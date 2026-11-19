#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Digital Audio & Sound Quality Wiki - Lint Inspection Script
自動檢查 Wiki 知識庫規範：
1. 來源追溯（是否包含文章標題、網址、原始檔案路徑與段落）
2. 內部相對連結有效性（無死連結）
3. 全域目錄完整性（index.md 是否收錄所有 wiki 頁面，無孤立頁面）
4. 日誌完整性（log.md 是否存在並有記錄）
5. 補充說明標籤（生活類比等額外內容是否標記 [補充說明]）
"""

import os
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
WIKI_DIR = ROOT_DIR / "wiki"
RAW_DIR = ROOT_DIR / "raw"
INDEX_FILE = ROOT_DIR / "index.md"
LOG_FILE = ROOT_DIR / "log.md"

LINK_REGEX = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def check_log_file(errors, warnings):
    if not LOG_FILE.exists():
        errors.append("❌ 缺少 log.md 檔案")
        return
    content = LOG_FILE.read_text(encoding="utf-8")
    if not content.strip() or "## " not in content:
        warnings.append("⚠️ log.md 內容過少或缺少條目章節紀錄")


def check_index_completeness(wiki_files, errors, warnings):
    if not INDEX_FILE.exists():
        errors.append("❌ 缺少 index.md 檔案")
        return
    index_content = INDEX_FILE.read_text(encoding="utf-8")
    
    # 檢查 wiki 檔案是否都被 index.md 引用
    for wf in wiki_files:
        rel_to_root = wf.relative_to(ROOT_DIR).as_posix()
        # 只要 index.md 內有出現該路徑或檔名
        if rel_to_root not in index_content and wf.name not in index_content:
            errors.append(f"❌ 孤立頁面：{rel_to_root} 未在 index.md 中被引用")


def check_markdown_links(file_path, content, errors):
    file_dir = file_path.parent
    links = LINK_REGEX.findall(content)
    for text, url in links:
        url = url.strip()
        # 忽略外部連結與錨點
        if url.startswith(("http://", "https://", "mailto:")):
            continue
        if url.startswith("#"):
            continue
        # 去除 url 內的錨點
        path_part = url.split("#")[0]
        if not path_part:
            continue
        target_path = (file_dir / path_part).resolve()
        if not target_path.exists():
            rel_file = file_path.relative_to(ROOT_DIR)
            errors.append(f"❌ 死連結：{rel_file} 中的連結 [{text}]({url}) 指向不存在的路徑")


def check_wiki_page_structure(file_path, errors, warnings):
    content = file_path.read_text(encoding="utf-8")
    rel_path = file_path.relative_to(ROOT_DIR).as_posix()

    # 1. 檢查標題
    if not content.startswith("# "):
        errors.append(f"❌ 格式錯誤：{rel_path} 頂部應為一級標題 (# 標題)")

    # 2. 檢查原始來源區塊
    if "## 原始來源" not in content:
        errors.append(f"❌ 缺少來源：{rel_path} 必須包含 '## 原始來源' 區塊")
    else:
        source_part = content.split("## 原始來源", 1)[1]
        if "文章標題" not in source_part:
            warnings.append(f"⚠️ 來源資訊不完整：{rel_path} 的 '## 原始來源' 建議包含文章標題")
        if "原始檔案" not in source_part and "raw/" not in source_part:
            warnings.append(f"⚠️ 來源資訊不完整：{rel_path} 的 '## 原始來源' 未標註 raw 檔案路徑")
        if "對應章節" not in source_part and "段落" not in source_part:
            warnings.append(f"⚠️ 來源資訊不完整：{rel_path} 的 '## 原始來源' 建議包含對應章節或段落")

    # 3. 檢查生活類比是否有 [補充說明] 標註
    if "## 生活類比" in content:
        analogy_part = content.split("## 生活類比", 1)[1].split("##", 1)[0]
        if "[補充說明]" not in analogy_part:
            warnings.append(f"⚠️ 標籤提示：{rel_path} 的 '## 生活類比' 若為額外補充，請標記 [補充說明]")

    # 4. 檢查內部相對連結
    check_markdown_links(file_path, content, errors)


def run_lint():
    print("=" * 60)
    print("🔍 執行 Digital Audio Wiki 品質檢測 (Lint)...")
    print("=" * 60)

    errors = []
    warnings = []

    # 檢查 log.md
    check_log_file(errors, warnings)

    # 檢查 index.md 中的連結
    if INDEX_FILE.exists():
        index_content = INDEX_FILE.read_text(encoding="utf-8")
        check_markdown_links(INDEX_FILE, index_content, errors)

    # 取得所有 wiki 頁面
    wiki_files = list(WIKI_DIR.rglob("*.md")) if WIKI_DIR.exists() else []

    # 檢查 index 孤立頁面
    check_index_completeness(wiki_files, errors, warnings)

    # 檢查每個 wiki 頁面結構
    for wf in wiki_files:
        check_wiki_page_structure(wf, errors, warnings)

    print(f"📊 檢查統計：")
    print(f"  - 發現 Wiki 頁面數：{len(wiki_files)} 篇")
    print(f"  - 發現問題（Errors）：{len(errors)} 個")
    print(f"  - 提示建議（Warnings）：{len(warnings)} 個")
    print("-" * 60)

    if warnings:
        print("💡 建議改善項目（Warnings）：")
        for w in warnings:
            print(f"  {w}")
        print("-" * 60)

    if errors:
        print("🚨 檢測未通過（Errors）：")
        for e in errors:
            print(f"  {e}")
        print("=" * 60)
        return False
    else:
        print("✅ 恭喜！所有 Lint 檢測規則均已通過。")
        print("=" * 60)
        return True


if __name__ == "__main__":
    success = run_lint()
    sys.exit(0 if success else 1)
