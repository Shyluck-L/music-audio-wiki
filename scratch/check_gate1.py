#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gate 1: 程式化結構與路徑檢驗腳本
檢核 scratch/evidence-cards.json 的結構完整性、路徑有效性與基本欄位規範。
"""

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
CARDS_FILE = ROOT_DIR / "scratch" / "evidence-cards.json"


def verify_gate1():
    print("=" * 60)
    print("🔍 執行 Gate 1 程式化檢核 (Evidence Cards Verification)...")
    print("=" * 60)

    if not CARDS_FILE.exists():
        print(f"❌ 錯誤：找不到檔案 {CARDS_FILE}")
        return False

    try:
        data = json.loads(CARDS_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"❌ JSON 解析失敗：{e}")
        return False

    errors = []
    warnings = []

    total_slides = data.get("total_slides", 0)
    cards = data.get("evidence_cards", [])

    if total_slides != 12:
        errors.append(f"投影片總數應為 12，目前記錄為 {total_slides}")

    if len(cards) != 12:
        errors.append(f"證據卡數量應為 12，實際有 {len(cards)} 張")

    for i, card in enumerate(cards, 1):
        sid = card.get("slide_id")
        if sid != i:
            errors.append(f"卡片編號不匹配：預期 {i}，得到 {sid}")

        title = card.get("title", "")
        if not title:
            errors.append(f"第 {i} 頁缺少標題")

        claims = card.get("claims", [])
        if not claims or len(claims) < 2:
            errors.append(f"第 {i} 頁的主張（claims）過少或為空")

        # 檢驗 Wiki 來源真實路徑與錨點
        wiki_sources = card.get("wiki_sources", [])
        if not wiki_sources:
            errors.append(f"第 {i} 頁缺少 wiki_sources")
        for ws in wiki_sources:
            wiki_fn = ws.split("#")[0].strip()
            wpath = ROOT_DIR / wiki_fn
            if not wpath.exists():
                errors.append(f"第 {i} 頁的 Wiki 來源檔案不存在：{wiki_fn}")
            elif "#" in ws:
                anchor = ws.split("#", 1)[1].strip()
                content = wpath.read_text(encoding="utf-8")
                anchor_clean = anchor.replace("-", " ")
                if anchor not in content and anchor_clean not in content:
                    warnings.append(f"第 {i} 頁的 Wiki 錨點段落未在內文中直接找到精確標題：{wiki_fn} -> #{anchor}")

        # 檢驗 Raw 來源檔案
        raw_sources = card.get("raw_sources", [])
        if not raw_sources:
            errors.append(f"第 {i} 頁缺少 raw_sources")
        for rs in raw_sources:
            raw_fn = rs.split(" ")[0].strip()
            rpath = ROOT_DIR / raw_fn
            if not rpath.exists():
                errors.append(f"第 {i} 頁的 Raw 來源檔案不存在：{raw_fn}")

        # 檢驗視覺規劃欄位
        if not card.get("visual_plan"):
            warnings.append(f"第 {i} 頁缺少 visual_plan")

    # 特殊檢驗
    if len(cards) >= 6:
        c6_conflict = cards[5].get("conflict_notes", "")
        if "MDN" not in c6_conflict and "衝突" not in c6_conflict:
            errors.append("第 6 頁必須在 conflict_notes 記錄 MDN 兩篇文獻之壓縮比衝突保留")

    if len(cards) >= 12:
        c12_claims = " ".join(cards[11].get("claims", []))
        if "70%" in c12_claims or "20%" in c12_claims:
            errors.append("第 12 頁不可含有未接地之 70%/20% 百分比數據")

    print(f"📊 檢驗結果：發現 {len(errors)} 個錯誤，{len(warnings)} 個提示")
    if warnings:
        for w in warnings:
            print(f"  ⚠️ {w}")
    if errors:
        for e in errors:
            print(f"  ❌ {e}")
        print("=" * 60)
        return False

    print("✅ Gate 1 程式化檢核全部通過！")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = verify_gate1()
    sys.exit(0 if success else 1)
