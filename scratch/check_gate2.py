#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gate 2: 程式化事實與文字稿結構檢驗腳本
檢核 scratch/slide-scripts.md 的結構完整性、關鍵技術條件、來源路徑與禁止項目。
"""

import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_FILE = ROOT_DIR / "scratch" / "slide-scripts.md"


def verify_gate2():
    print("=" * 60)
    print("🔍 執行 Gate 2 程式化檢核 (Slide Scripts Verification)...")
    print("=" * 60)

    if not SCRIPTS_FILE.exists():
        print(f"❌ 錯誤：找不到文字稿檔案 {SCRIPTS_FILE}")
        return False

    content = SCRIPTS_FILE.read_text(encoding="utf-8")
    errors = []
    warnings = []

    # 1. 檢驗 12 頁是否齊全
    slide_sections = re.findall(r"### 第 (\d+) 頁｜([^\n]+)", content)
    found_slide_nums = [int(s[0]) for s in slide_sections]

    if len(found_slide_nums) != 12 or found_slide_nums != list(range(1, 13)):
        errors.append(f"投影片頁數不完整：預期 1～12 頁，實際找到：{found_slide_nums}")

    # 分割各頁內容
    raw_slides = re.split(r"### 第 \d+ 頁｜", content)[1:]

    for i, slide_text in enumerate(raw_slides, 1):
        # 檢查必要段落
        if "* **白話核心金句**：" not in slide_text:
            errors.append(f"第 {i} 頁缺少「白話核心金句」")
        if "* **條列解析**：" not in slide_text:
            errors.append(f"第 {i} 頁缺少「條列解析」")
        if "* **生活類比圖卡**：" not in slide_text:
            errors.append(f"第 {i} 頁缺少「生活類比圖卡」")
        elif "[補充說明]" not in slide_text:
            errors.append(f"第 {i} 頁生活類比圖卡未標註「[補充說明]」")
        if "* **視覺佈局指引**：" not in slide_text:
            errors.append(f"第 {i} 頁缺少「視覺佈局指引」")
        if "* **來源憑據與段落定位**：" not in slide_text:
            errors.append(f"第 {i} 頁缺少「來源憑據與段落定位」")

        # 檢驗 Wiki 相對連結有效性
        links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", slide_text)
        for link_text, link_path in links:
            if link_path.startswith("http"):
                continue
            path_part = link_path.split("#")[0].strip()
            # 相對路徑轉換（文字稿位於 scratch/，故 ../wiki/... 指向 root/wiki/...）
            target_path = (SCRIPTS_FILE.parent / path_part).resolve()
            if not target_path.exists():
                errors.append(f"第 {i} 頁相對連結目標不存在：{link_path} -> {target_path}")

    # 2. 特殊關鍵事實檢驗
    if len(raw_slides) >= 2:
        s2 = raw_slides[1]
        if "藍牙標準 48 kHz" in s2 or "藍牙標準" in s2 and "48 kHz" in s2 and "常見" not in s2:
            errors.append("第 2 頁避免將 48 kHz 直接稱為藍牙標準")

    if len(raw_slides) >= 4:
        s4 = raw_slides[3]
        if "48 kHz" not in s4 or "16-bit" not in s4 or "雙聲道" not in s4 and "2 聲道" not in s4:
            errors.append("第 4 頁計算前提不完整（需包含 48 kHz, 16-bit, 雙聲道/2聲道）")
        if "34.56 MB" not in s4 and "34.5 MB" not in s4:
            errors.append("第 4 頁未明確呈現 34.56 MB（或 34.5 MB）計算結論")

    if len(raw_slides) >= 6:
        s6 = raw_slides[5]
        if "raw/02" not in s6 or "raw/03" not in s6:
            errors.append("第 6 頁必須在來源與內文中並陳 MDN raw/02 與 raw/03 兩種壓縮比描述")
        if "40%" not in s6 or "50%" not in s6:
            errors.append("第 6 頁缺少 40%～50% 壓縮比例說明")
        if "兩者皆表明無損壓縮約可節省一半左右的空間" in s6:
            errors.append("第 6 頁應移除將兩篇 MDN 文獻視為同一數據的統合結論")

    if len(raw_slides) >= 7:
        s7 = raw_slides[6]
        if "256k AAC 必勝" in s7 or "256 kbps AAC 必勝" in s7:
            errors.append("第 7 頁不可出現未接地之「256k AAC 必勝 320k MP3」絕對論調")

    if len(raw_slides) >= 9:
        s9 = raw_slides[8]
        if "絕對必須" in s9:
            errors.append("第 9 頁專業後製建議應避免使用「絕對必須」等過度絕對語氣")

    if len(raw_slides) >= 10:
        s10 = raw_slides[9]
        if "Clipping" not in s10 and "破音" not in s10:
            errors.append("第 10 頁缺少 Clipping / 破音說明")
        if "Headroom" not in s10 and "安全餘裕" not in s10:
            errors.append("第 10 頁缺少動態安全餘裕（Headroom）說明")

    if len(raw_slides) >= 11:
        s11 = raw_slides[10]
        if "Bluetooth connections aren't lossless" not in s11:
            errors.append("第 11 頁缺少 Apple 官方「Bluetooth connections aren't lossless」引用")
        if "AirPods Max" not in s11 or "USB-C" not in s11:
            errors.append("第 11 頁缺少 AirPods Max (USB-C) 有線例外說明")
        if "Vision Pro" not in s11:
            errors.append("第 11 頁缺少 Vision Pro 專有協定例外說明")
        if "DAC" not in s11:
            errors.append("第 11 頁缺少高於 48 kHz 需外接 DAC 說明")
        if "所有透過標準藍牙連線的無線耳機" in s11 and "皆採用有損 Apple AAC" in s11:
            errors.append("第 11 頁避免過度概括宣稱所有標準藍牙耳機均使用 Apple AAC")

    if len(raw_slides) >= 12:
        s12 = raw_slides[11]
        for bad_pct in ["70%", "20%", "10%"]:
            if bad_pct in s12:
                errors.append(f"第 12 頁不可包含未接地之比例數據：{bad_pct}")
        if "金字塔" in s12:
            errors.append("第 12 頁視覺圖解應避免金字塔階層暗示固定影響力排名")
        if "Mastering" not in s12:
            errors.append("第 12 頁缺少母帶製作（Mastering）維度")
        if "Transducers" not in s12:
            errors.append("第 12 頁缺少耳機揚聲器硬體（Transducers）維度")

    print(f"📊 檢驗結果：發現 {len(errors)} 個錯誤，{len(warnings)} 個提示")
    if warnings:
        for w in warnings:
            print(f"  ⚠️ {w}")
    if errors:
        for e in errors:
            print(f"  ❌ {e}")
        print("=" * 60)
        return False

    print("✅ Gate 2 程式化檢核全部通過！")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = verify_gate2()
    sys.exit(0 if success else 1)
