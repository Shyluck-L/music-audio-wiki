#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Workflow Controller: 數位音樂與音質教學簡報 Graph / Loop 工作流控制器
職責：
1. 管理 Node 0 至 Node 7 之狀態推進與狀態持久化 (scratch/workflow-state.json)。
2. 執行 Gate 1、Gate 2、Gate 3 與 Lint 之自動化檢查。
3. 嚴格落實人機協同職責邊界（Python 控制器負責狀態/門禁/日誌，Agent 負責實質修改檔案）。
4. 嚴格執行自動重試上限（MAX_RETRIES = 2 次），超限強制中斷 (CRITICAL_HALT)。
5. 每次重要事件（PASS/FAIL/退回/修訂/重試重置/核准）即時追加至 log.md。
6. human-approve 前置檢查守衛（禁止在未過審、未通過全部 Gate 或有未解決退回時放行）。
7. check-all 防覆寫與舊版 HTML 過期檢核守衛（禁止以舊版 HTML 掩蓋人工退回或偽通過）。
"""

import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
STATE_FILE = ROOT_DIR / "scratch" / "workflow-state.json"
LOG_FILE = ROOT_DIR / "log.md"
PYTHON_EXE = sys.executable

MAX_RETRIES = 2

NODE_MAP = {
    0: ("Node 0: 設計規格確認", "scratch/design-specs.json"),
    1: ("Node 1: Wiki 檢索與接地", "wiki/ 及 raw/ 條目"),
    2: ("Node 2: 證據卡與大綱建立 (Gate 1)", "scratch/evidence-cards.json & slide-outline.md"),
    3: ("Node 3: 逐頁簡報文字稿起草", "scratch/slide-scripts.md"),
    4: ("Node 4: 內容與事實檢查 (Gate 2)", "scratch/check_gate2.py"),
    5: ("Node 5: HTML 簡報生成", "presentation/index.html"),
    6: ("Node 6: 瀏覽器畫面與功能檢核 (Gate 3)", "scratch/run_gate3_browser_test.py"),
    7: ("Node 7: 最終交付與歸檔", "正式交付成果"),
}

GATE_SCRIPTS = {
    1: (ROOT_DIR / "scratch" / "check_gate1.py", "route_a_gate1_fallback", 2, "Node 2: 證據卡與大綱建立", "scratch/evidence-cards.json"),
    2: (ROOT_DIR / "scratch" / "check_gate2.py", "route_b_gate2_fallback", 3, "Node 3: 逐頁簡報文字稿起草", "scratch/slide-scripts.md"),
    3: (ROOT_DIR / "scratch" / "run_gate3_browser_test.py", "route_c_gate3_fallback", 5, "Node 5: HTML 簡報生成", "presentation/index.html"),
}


def load_state():
    if not STATE_FILE.exists():
        return {
            "project": "Digital Audio & Sound Quality Presentation Workflow",
            "version": "1.1",
            "current_node": 6,
            "current_node_name": "Node 6: 瀏覽器畫面與功能檢核 (Gate 3)",
            "node_status": "GATE_3_PASSED_PENDING_HUMAN_ACCEPTANCE",
            "human_acceptance_status": "PENDING_REVIEW",
            "max_automatic_retries": MAX_RETRIES,
            "retry_counters": {
                "route_a_gate1_fallback": 0,
                "route_b_gate2_fallback": 0,
                "route_c_gate3_fallback": 0,
            },
            "gate_results": {
                "gate_1": "PASS",
                "gate_2": "PASS",
                "gate_3": "PASS",
            },
            "pending_revision": None,
            "last_updated": datetime.datetime.now().isoformat(),
            "history": [],
        }
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"⚠️ 讀取狀態檔失敗，使用預設值：{e}")
        return {}


def save_state(state):
    state["last_updated"] = datetime.datetime.now().isoformat()
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def append_log(title, lines):
    """即時追加結構化日誌至既有 log.md，嚴禁覆蓋或偽造舊記錄"""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n\n### [{now_str}] Workflow 執行紀錄：{title}\n"
    for line in lines:
        entry += f"* {line}\n"

    try:
        current_log = LOG_FILE.read_text(encoding="utf-8")
        LOG_FILE.write_text(current_log + entry, encoding="utf-8")
        print(f"📝 日誌已追加至 log.md")
    except Exception as e:
        print(f"⚠️ 追加 log.md 失敗：{e}")


def check_artifact_staleness():
    """檢核工件新鮮度：判斷是否有待修訂項目，或 HTML 是否晚於文字稿生成（依實體檔案修改時間判定）"""
    state = load_state()
    pending = state.get("pending_revision")
    html_path = ROOT_DIR / "presentation" / "index.html"
    scripts_path = ROOT_DIR / "scratch" / "slide-scripts.md"

    warnings = []
    is_stale = False

    if pending and not pending.get("resolved", False):
        warnings.append(
            f"尚有待完成修訂：[{pending.get('type')}] 目標節點 Node {pending.get('target_node')}（原因：{pending.get('details', '未詳述')}）"
        )
        is_stale = True

    # 以實體工件檔案修改時間（st_mtime）判定時序，避免字串秒數比對造成之競態落差
    if scripts_path.exists() and html_path.exists():
        # 若文字稿有變更，HTML 的修改時間不可早於文字稿（給予 0.5 秒容差）
        if html_path.stat().st_mtime < (scripts_path.stat().st_mtime - 0.5):
            if pending and pending.get("target_node") in [1, 2, 3]:
                scripts_time = datetime.datetime.fromtimestamp(scripts_path.stat().st_mtime).isoformat()
                html_time = datetime.datetime.fromtimestamp(html_path.stat().st_mtime).isoformat()
                warnings.append(
                    f"HTML 工件已過期：文字稿 (slide-scripts.md, {scripts_time}) 的修改時間晚於 HTML (index.html, {html_time})，尚未重新生成！"
                )
                is_stale = True

    return is_stale, warnings


def show_status():
    state = load_state()
    print("=" * 70)
    print("📊 數位音樂簡報 Workflow 當前狀態")
    print("=" * 70)
    c_node = state.get("current_node", 0)
    c_name = state.get("current_node_name", "未指定")
    n_status = state.get("node_status", "UNKNOWN")
    h_status = state.get("human_acceptance_status", "PENDING_REVIEW")
    retries = state.get("retry_counters", {})
    gates = state.get("gate_results", {})
    pending = state.get("pending_revision")

    print(f"📍 當前節點：{c_name} (Node {c_node})")
    print(f"🏷️ 節點狀態：{n_status}")
    print(f"👤 人工驗收狀態：{h_status}")

    if pending:
        resolved_str = "已由 Agent 完成標記，待 Gate 檢驗" if pending.get("resolved") else "❌ 尚未解決（待修訂）"
        print(f"\n⚠️ 待處理修訂請求 (Pending Revision)：")
        print(f"   • 類型：{pending.get('type')}")
        print(f"   • 目標節點：Node {pending.get('target_node')}")
        print(f"   • 詳情備註：{pending.get('details')}")
        print(f"   • 處理狀態：{resolved_str}")

    print("\n🔍 各 Gate 檢驗狀態：")
    print(f"   • Gate 1 (資料完整性與來源路徑)：{gates.get('gate_1', '未檢驗')}")
    print(f"   • Gate 2 (事實正確性與文字稿檢核)：{gates.get('gate_2', '未檢驗')}")
    print(f"   • Gate 3 (多解析度瀏覽器檢驗)：{gates.get('gate_3', '未檢驗')}")

    print("\n🔁 自動重試計數器（上限 2 次）：")
    for r_num, (s_path, r_key, f_node, f_name, f_file) in GATE_SCRIPTS.items():
        cnt = retries.get(r_key, 0)
        flag = "🛑 超限鎖定" if cnt >= MAX_RETRIES else ("⚠️ 已重試" if cnt > 0 else "✅ 正常")
        print(f"   • Gate {r_num} -> {f_name}：{cnt} / {MAX_RETRIES} 次 ({flag})")

    is_stale, warnings = check_artifact_staleness()
    print("\n📦 工件新鮮度檢驗：")
    if is_stale:
        for w in warnings:
            print(f"   ❌ {w}")
    else:
        print("   ✅ 現存工件狀態一致，無過期未生成情況。")

    print("\n📁 節點與負責檔案對應：")
    for n_id, (n_desc, n_file) in NODE_MAP.items():
        marker = "👉" if n_id == c_node else "  "
        print(f" {marker} [{n_id}] {n_desc} -> {n_file}")

    print("=" * 70)


def run_gate(gate_num):
    state = load_state()
    retries = state.setdefault("retry_counters", {})

    if gate_num not in GATE_SCRIPTS:
        print(f"❌ 無效的 Gate 編號：{gate_num}（有效值為 1, 2, 3）")
        return False

    script_path, retry_key, fallback_node, fallback_name, fallback_file = GATE_SCRIPTS[gate_num]
    current_retry = retries.get(retry_key, 0)

    # 停止條件檢查：超過上限不得繼續自動修正
    if current_retry >= MAX_RETRIES:
        print("=" * 70)
        print(f"🛑 [CRITICAL_HALT] Gate {gate_num} 自動重試次數已達上限 ({MAX_RETRIES} 次)！")
        print("=" * 70)
        print(f"• 目標節點：{fallback_name}")
        print(f"• 失敗計數：{current_retry} / {MAX_RETRIES}")
        print("• 工作流強制鎖定中斷，禁止繼續自動退回修正，防止進入無效死循環。")
        print("• 處置要求：請人工介入審查根本問題，手動修正後執行以下指令重置鎖定：")
        print("    python scripts/workflow.py reset-retries")
        print("=" * 70)

        state["node_status"] = f"GATE_{gate_num}_MAX_RETRIES_EXCEEDED"
        save_state(state)
        append_log(
            f"Gate {gate_num} 達到重試上限強制中斷",
            [
                f"關卡：Gate {gate_num}",
                f"累計重試次數：{current_retry} 次（已達上限 {MAX_RETRIES} 次）",
                "處置：工作流進入 CRITICAL_HALT，等待人工介入審查與重置",
            ],
        )
        return False

    # 若為 Gate 3，檢核工件新鮮度（避免測試過期的舊 HTML）
    if gate_num == 3:
        is_stale, warnings = check_artifact_staleness()
        if is_stale:
            print("=" * 70)
            print("❌ [STALE_ARTIFACT_BLOCKED] Gate 3 拒絕檢驗過期工件！")
            print("=" * 70)
            for w in warnings:
                print(f" • {w}")
            print("處置指引：請 Agent 重新執行 Node 5 生成最新 HTML，再行執行 Gate 3 檢驗。")
            print("=" * 70)
            return False

    print(f"🚀 執行 Gate {gate_num} 檢驗（目前重試計數：{current_retry}/{MAX_RETRIES}）...")
    res = subprocess.run([PYTHON_EXE, str(script_path)])
    passed = (res.returncode == 0)

    if passed:
        state["gate_results"][f"gate_{gate_num}"] = "PASS"
        # 若當前解決了 pending_revision，將其清除
        if state.get("pending_revision") and state["pending_revision"].get("gate") == gate_num:
            state["pending_revision"] = None

        print(f"✅ Gate {gate_num} 檢驗通過！")
        append_log(
            f"Gate {gate_num} 檢驗通過",
            [
                f"關卡：Gate {gate_num}（{script_path.name}）",
                f"檢驗結果：PASS",
                f"目前重試計數維持：{current_retry} / {MAX_RETRIES}",
            ],
        )
        save_state(state)
        return True
    else:
        state["gate_results"][f"gate_{gate_num}"] = "FAIL"
        new_retry = current_retry + 1
        retries[retry_key] = new_retry
        state["current_node"] = fallback_node
        state["current_node_name"] = fallback_name
        state["node_status"] = f"GATE_{gate_num}_FAILED_FALLBACK"

        state["pending_revision"] = {
            "type": "GATE_FAILURE",
            "gate": gate_num,
            "target_node": fallback_node,
            "target_file": fallback_file,
            "retry_count": new_retry,
            "timestamp": datetime.datetime.now().isoformat(),
            "resolved": False,
        }

        save_state(state)

        append_log(
            f"Gate {gate_num} 自動檢查失敗退回",
            [
                f"失敗關卡：Gate {gate_num}",
                f"退回節點：{fallback_name}",
                f"負責工件：{fallback_file}",
                f"自動重試次數：第 {new_retry} 次（上限 {MAX_RETRIES} 次）",
                "原因：程式化或瀏覽器檢核未通過",
            ],
        )

        # 輸出高能見度之人機職責協同訊號合約
        print("\n" + "=" * 70)
        print(f"❌ Gate {gate_num} 檢驗未通過！已啟動自動退回 -> {fallback_name}")
        print("=" * 70)
        print("📢 [AGENT_ACTION_REQUIRED] 需由 Antigravity Agent 執行實質檔案修訂：")
        print(f" • 失敗關卡：Gate {gate_num}")
        print(f" • 退回目標節點：{fallback_name}")
        print(f" • 負責工件：{fallback_file}")
        print(f" • 重試計數：第 {new_retry} 次（上限 {MAX_RETRIES} 次）")
        print(" • Agent 執行指南：")
        print(f"   1. 檢視 Gate {gate_num} 之報錯細節，使用檔案編輯工具修改實質工件 ({fallback_file})。")
        print(f"   2. 修改完成後，執行：python scripts/workflow.py mark-revised {fallback_node} \"<修訂說明>\"")
        print(f"   3. 重新執行檢驗：python scripts/workflow.py run-gate {gate_num}")
        print("=" * 70 + "\n")

        if new_retry >= MAX_RETRIES:
            print(f"🛑 警告：重試計數已達上限 ({MAX_RETRIES} 次)！下次執行將強制鎖定，請謹慎修訂。")

        return False


def mark_revised(node_num, note="Agent 已完成實質檔案修訂"):
    """由 Antigravity Agent 在實質修改檔案後調用，標記該修訂完成並記錄日誌"""
    state = load_state()
    pending = state.get("pending_revision")

    state["current_node"] = node_num
    state["current_node_name"] = NODE_MAP.get(node_num, (f"Node {node_num}", ""))[0]

    if not pending:
        print(f"ℹ️ 目前並無記錄中的待修訂項目，直接更新節點 {node_num} 修訂狀態。")
        state["pending_revision"] = {
            "type": "MANUAL_REVISION",
            "target_node": node_num,
            "details": note,
            "timestamp": datetime.datetime.now().isoformat(),
            "resolved": True,
            "resolved_at": datetime.datetime.now().isoformat(),
        }
    else:
        pending["resolved"] = True
        pending["resolved_at"] = datetime.datetime.now().isoformat()
        pending["resolution_note"] = note
        # 若是 Node 5 完成 HTML，代表來自 Node 1~3 的變更已成功傳遞至展示層
        if node_num == 5:
            pending["target_node"] = 5

    if node_num == 3:
        state["node_status"] = "SCRIPTS_REVISED_PENDING_GATE2"
    elif node_num == 5:
        state["node_status"] = "HTML_GENERATED_PENDING_GATE3"
    else:
        state["node_status"] = "REVISION_COMPLETED_PENDING_GATE_CHECK"

    save_state(state)

    print(f"✅ 已成功標記 Node {node_num} 完成實質修訂：{note}")
    append_log(
        f"Agent 完成 Node {node_num} 實質工件修訂",
        [
            f"修訂節點：Node {node_num}",
            f"修訂說明：{note}",
            "當前狀態：修訂完成，待執行對應 Gate 重新檢驗",
        ],
    )


def run_check_all():
    print("=" * 70)
    print("🔍 執行全流程自動檢驗清單 (Lint + Gate 1 + Gate 2 + Gate 3)...")
    print("=" * 70)

    state = load_state()

    # 檢核是否處於未解決之人身退回狀態，嚴禁覆寫
    h_status = state.get("human_acceptance_status", "")
    n_status = state.get("node_status", "")
    pending = state.get("pending_revision")

    if h_status.startswith("REJECTED_") or n_status == "HUMAN_REVISION_REQUESTED":
        if pending and not pending.get("resolved", False):
            print("=" * 70)
            print("⚠️ [CHECK_ALL_ABORTED] 工作流目前處於人工退回待修訂狀態！")
            print("=" * 70)
            print(f"• 人工驗收狀態：{h_status}")
            print(f"• 退回節點：Node {pending.get('target_node')}（原因：{pending.get('details')}）")
            print("• 禁止直接執行 check-all 覆寫狀態或以舊版成果偽通過！")
            print("• 處置方式：請 Agent 先完成實質修訂並標記 mark-revised，再重新檢驗。")
            print("=" * 70)
            return False

    # 檢核工件新鮮度
    is_stale, warnings = check_artifact_staleness()
    if is_stale:
        print("=" * 70)
        print("❌ [STALE_ARTIFACT_BLOCKED] 全流程檢驗中止：存在過期或未同步之工件！")
        print("=" * 70)
        for w in warnings:
            print(f" • {w}")
        print("處置方式：請確保各階段工件已依序重新生成，再執行全流程檢驗。")
        print("=" * 70)
        return False

    checks = [
        ("Wiki 規格檢測 (scripts/lint.py)", ROOT_DIR / "scripts" / "lint.py"),
        ("Gate 1: 證據卡與路徑檢核 (scratch/check_gate1.py)", ROOT_DIR / "scratch" / "check_gate1.py"),
        ("Gate 2: 事實與文字稿檢核 (scratch/check_gate2.py)", ROOT_DIR / "scratch" / "check_gate2.py"),
        ("Gate 3: 多解析度瀏覽器檢核 (scratch/run_gate3_browser_test.py)", ROOT_DIR / "scratch" / "run_gate3_browser_test.py"),
    ]

    all_passed = True
    for name, script in checks:
        print(f"\n▶ 執行：{name}")
        res = subprocess.run([PYTHON_EXE, str(script)])
        if res.returncode != 0:
            print(f"❌ 項目未通過：{name}")
            all_passed = False
            break
        else:
            print(f"✅ 通過：{name}")

    state = load_state()
    if all_passed:
        state["gate_results"] = {"gate_1": "PASS", "gate_2": "PASS", "gate_3": "PASS"}
        state["pending_revision"] = None

        # 若原先已正式驗收交付 (APPROVED / OFFICIALLY_DELIVERED)，保持交付狀態
        if h_status == "APPROVED" and state.get("node_status") == "OFFICIALLY_DELIVERED":
            print("\n🎉 全流程自動檢核全部通過！專案維持正式交付歸檔狀態 (Node 7 / OFFICIALLY_DELIVERED)。")
        # 若原先為人工退回，通過後進入「修訂完成待人工複審」，不直接抹除人工意見
        elif h_status.startswith("REJECTED_"):
            state["node_status"] = "GATE_3_PASSED_PENDING_HUMAN_ACCEPTANCE"
            state["human_acceptance_status"] = "REVISED_PENDING_HUMAN_REVIEW"
            state["current_node"] = 6
            state["current_node_name"] = "Node 6: 瀏覽器畫面與功能檢核 (Gate 3)"
            print("\n🎉 全流程檢核通過！已將修訂成果送交人工複審 (REVISED_PENDING_HUMAN_REVIEW)。")
        else:
            state["node_status"] = "GATE_3_PASSED_PENDING_HUMAN_ACCEPTANCE"
            state["human_acceptance_status"] = "PENDING_REVIEW"
            state["current_node"] = 6
            state["current_node_name"] = "Node 6: 瀏覽器畫面與功能檢核 (Gate 3)"
            print("\n🎉 全流程自動檢核全部通過！當前狀態：待人工視覺驗收 (Node 6 -> Node 7 Gate)")

        save_state(state)
        append_log(
            "全流程自動檢核 (check-all) 通過",
            [
                "執行檢核：Lint, Gate 1, Gate 2, Gate 3",
                "檢核結果：ALL PASS",
                f"當前節點狀態：{state['node_status']}",
                f"人工驗收狀態：{state['human_acceptance_status']}",
            ],
        )
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("❌ 全流程檢核中斷，請依據上述錯誤修正對應節點。")
        print("=" * 70)

    return all_passed


def human_reject(reason_type, details):
    state = load_state()
    # 人工退回重置自動重試次數（人工提出之修改不與自動重試混算）
    state["retry_counters"] = {
        "route_a_gate1_fallback": 0,
        "route_b_gate2_fallback": 0,
        "route_c_gate3_fallback": 0,
    }

    if reason_type == "content":
        target_node = 3
        target_name = "Node 3: 逐頁簡報文字稿起草"
        target_file = "scratch/slide-scripts.md"
        desc = "文字稿起草、教學重點或文案精簡"
    elif reason_type == "style":
        target_node = 5
        target_name = "Node 5: HTML 簡報生成"
        target_file = "presentation/index.html"
        desc = "版面構圖、插圖大小、邊距或排版視覺微調"
    elif reason_type in ["tech", "claims"]:
        target_node = 1
        target_name = "Node 1: Wiki 檢索與接地"
        target_file = "wiki/ 及 raw/ 條目"
        desc = "技術主張、規格依據或來源檢索查核"
    elif reason_type == "spec":
        target_node = 0
        target_name = "Node 0: 設計規格確認"
        target_file = "scratch/design-specs.json"
        desc = "整體設計規格、風格大綱或調性變更"
    else:
        print(f"❌ 未知的人工退回類型：{reason_type}（可選：content, style, tech, spec）")
        return False

    state["current_node"] = target_node
    state["current_node_name"] = target_name
    state["node_status"] = "HUMAN_REVISION_REQUESTED"
    state["human_acceptance_status"] = f"REJECTED_{reason_type.upper()}"

    state["pending_revision"] = {
        "type": "HUMAN_REJECTION",
        "category": reason_type,
        "target_node": target_node,
        "target_file": target_file,
        "details": details,
        "timestamp": datetime.datetime.now().isoformat(),
        "resolved": False,
    }

    save_state(state)

    print("=" * 70)
    print(f"🔄 人工退回受理成功！")
    print("=" * 70)
    print(f"   • 退回類別：{reason_type} ({desc})")
    print(f"   • 轉入節點：{target_name}")
    print(f"   • 負責檔案：{target_file}")
    print(f"   • 意見詳情：{details}")
    print(f"   • 自動重試次數已重置為 0（獨立計算新一輪修訂）")
    print("=" * 70)
    print("📢 [AGENT_ACTION_REQUIRED] 需由 Antigravity Agent 執行修訂：")
    print(f"   1. 請 Agent 依據退回意見修改 {target_file}。")
    print(f"   2. 修改完成後執行：python scripts/workflow.py mark-revised {target_node} \"<修訂摘要>\"")
    print("   3. 推進後續 Gate 檢驗。")
    print("=" * 70)

    append_log(
        f"人工驗收退回（{reason_type}）",
        [
            f"退回類型：{reason_type}（{desc}）",
            f"轉入節點：{target_name}",
            f"負責工件：{target_file}",
            f"退回原因與指導意見：{details}",
            "處置：自動重試計數器已重置為 0，建立待修訂項目 (Pending Revision)",
        ],
    )
    return True


def human_approve(sign_off_note="人工視覺驗收確認無誤，同意交付"):
    state = load_state()
    n_status = state.get("node_status")
    h_status = state.get("human_acceptance_status")
    gates = state.get("gate_results", {})
    pending = state.get("pending_revision")

    # 守衛條件 1：必須處於待人工驗收或人工複審狀態
    allowed_statuses = ["GATE_3_PASSED_PENDING_HUMAN_ACCEPTANCE"]
    allowed_h_statuses = ["PENDING_REVIEW", "REVISED_PENDING_HUMAN_REVIEW"]

    blocking_reasons = []

    if n_status not in allowed_statuses:
        blocking_reasons.append(f"當前節點狀態為 '{n_status}'（必須為 GATE_3_PASSED_PENDING_HUMAN_ACCEPTANCE）")

    if h_status not in allowed_h_statuses:
        blocking_reasons.append(f"人工驗收狀態為 '{h_status}'（必須為 PENDING_REVIEW 或 REVISED_PENDING_HUMAN_REVIEW）")

    # 守衛條件 2：三大 Gate 必須全部為 PASS
    for g_id in [1, 2, 3]:
        if gates.get(f"gate_{g_id}") != "PASS":
            blocking_reasons.append(f"Gate {g_id} 尚未通過（目前狀態：{gates.get(f'gate_{g_id}', '未檢驗')}）")

    # 守衛條件 3：不得有未解決之修訂項目
    if pending and not pending.get("resolved", False):
        blocking_reasons.append(f"尚有未完成之修訂：[{pending.get('type')}] Node {pending.get('target_node')}（{pending.get('details')}）")

    # 守衛條件 4：檢核工件新鮮度
    is_stale, warnings = check_artifact_staleness()
    if is_stale:
        blocking_reasons.extend(warnings)

    # 守衛條件 5：確認成品 HTML 實體存在
    html_path = ROOT_DIR / "presentation" / "index.html"
    if not html_path.exists():
        blocking_reasons.append("成果檔案 presentation/index.html 不存在")

    if blocking_reasons:
        print("=" * 70)
        print("❌ 拒絕核准 (Human Approval Blocked)：未滿足正式交付條件！")
        print("=" * 70)
        for r in blocking_reasons:
            print(f" • 阻斷原因：{r}")
        print("處置指引：必須先修復上述問題並通過全部 Gate 檢驗後，方可執行核准。")
        print("=" * 70)
        return False

    state["current_node"] = 7
    state["current_node_name"] = "Node 7: 最終交付與歸檔"
    state["node_status"] = "OFFICIALLY_DELIVERED"
    state["human_acceptance_status"] = "APPROVED"
    state["pending_revision"] = None
    save_state(state)

    print("=" * 70)
    print("🎉 人工驗收審核通過！工作流正式推進至 Node 7（正式交付與歸檔完成）！")
    print("=" * 70)
    print(f" • 驗收備註：{sign_off_note}")
    print(f" • 交付成品：presentation/index.html")
    print("=" * 70)

    append_log(
        "人工驗收通過暨正式交付完成",
        [
            "驗收結果：APPROVED",
            f"驗收備註：{sign_off_note}",
            "當前節點：Node 7（正式交付與歸檔完成）",
            "交付檔案：presentation/index.html",
        ],
    )
    return True


def reset_retries():
    state = load_state()
    old_retries = dict(state.get("retry_counters", {}))
    state["retry_counters"] = {
        "route_a_gate1_fallback": 0,
        "route_b_gate2_fallback": 0,
        "route_c_gate3_fallback": 0,
    }
    # 若先前因超限被鎖定，解除鎖定狀態
    if "MAX_RETRIES_EXCEEDED" in state.get("node_status", ""):
        state["node_status"] = "RETRIES_RESET_PENDING_GATE_CHECK"

    save_state(state)
    print("🔄 自動重試計數器已重置為 0，超限鎖定已解除。")
    append_log(
        "手動重置自動重試計數器與解除超限鎖定",
        [
            f"原重試計數：{old_retries}",
            "處置：所有 Route 計數歸零，工作流鎖定已解除",
        ],
    )


def main():
    if len(sys.argv) < 2:
        show_status()
        print("\n可用指令：")
        print("  python scripts/workflow.py status                                    # 檢視目前狀態、工件新鮮度與重試計數")
        print("  python scripts/workflow.py check-all                                 # 執行全流程自動檢驗 (Lint+Gate1+Gate2+Gate3，具過期防護)")
        print("  python scripts/workflow.py run-gate <1|2|3>                          # 執行指定 Gate 檢驗並處理自動退回與重試上限")
        print("  python scripts/workflow.py mark-revised <node> \"<修訂說明>\"           # [Agent專用] 標記節點完成實質修訂")
        print("  python scripts/workflow.py human-reject <content|style|claims> <說明> # 人工驗收退回分流（重置重試計數）")
        print("  python scripts/workflow.py human-approve [驗收備註]                    # 人工驗收核准（具嚴格守衛條件）")
        print("  python scripts/workflow.py reset-retries                             # 重置自動重試計數器並解除超限鎖定")
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd == "status":
        show_status()
    elif cmd == "check-all":
        success = run_check_all()
        sys.exit(0 if success else 1)
    elif cmd == "run-gate":
        if len(sys.argv) < 3:
            print("請指定 Gate 編號，例如：python scripts/workflow.py run-gate 1")
            sys.exit(1)
        try:
            g_num = int(sys.argv[2])
        except ValueError:
            print("Gate 編號必須為整數 (1, 2, 3)")
            sys.exit(1)
        success = run_gate(g_num)
        sys.exit(0 if success else 1)
    elif cmd == "mark-revised":
        if len(sys.argv) < 3:
            print("請指定修訂節點編號，例如：python scripts/workflow.py mark-revised 3 '已微調投影片文字'")
            sys.exit(1)
        try:
            n_num = int(sys.argv[2])
        except ValueError:
            print("節點編號必須為整數 (0~7)")
            sys.exit(1)
        note = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else "已完成修訂"
        mark_revised(n_num, note)
    elif cmd == "human-reject":
        if len(sys.argv) < 4:
            print("請提供退回類型與說明，例如：python scripts/workflow.py human-reject content '文字過多需簡化'")
            sys.exit(1)
        rtype = sys.argv[2].lower()
        details = " ".join(sys.argv[3:])
        success = human_reject(rtype, details)
        sys.exit(0 if success else 1)
    elif cmd == "human-approve":
        note = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "人工視覺驗收確認無誤，同意交付"
        success = human_approve(note)
        sys.exit(0 if success else 1)
    elif cmd == "reset-retries":
        reset_retries()
    else:
        print(f"❌ 未知指令：{cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
