#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Wiki HTML: 靜態生成 11 篇 Wiki 的 HTML 閱讀頁面
將 wiki/ 目錄下的 Markdown 條目轉為延續專案暖白手繪質感的獨立靜態 HTML 網頁。
支援標題雙錨點（精確文字與 slug）、表格、清單、引用、補充說明警示框，並自動將內部 .md 相對連結轉為 .html。
完全使用 Python 標準函式庫，零外部套件與 CDN 依賴。
"""

import html
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
WIKI_DIR = ROOT_DIR / "wiki"

CATEGORY_NAMES = {
    "concepts": "核心概念（Concepts）",
    "formats": "音訊格式（Formats）",
    "comparisons": "橫向對比（Comparisons）",
    "myths": "迷思破解（Myths & FAQs）",
}

CSS_STYLE = """
:root {
  --bg-cream: #FAF8F5;
  --card-bg: #FFFFFF;
  --card-alt: #F6F3EE;
  --ink-black: #231F20;
  --ink-muted: #5C5550;
  --border-ink: #231F20;
  --border-subtle: #E2DDD5;
  --accent-warm: #EAD9C8;
  --accent-badge: #FBF0D9;
  --accent-callout: #FFF9ED;
  --accent-green: #E3EDE4;
  --accent-pink: #F5DCD5;
  --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", sans-serif;
  --code-font: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  background-color: var(--bg-cream);
  color: var(--ink-black);
  font-family: var(--font-family);
  line-height: 1.75;
  padding: 2rem 1.25rem 4rem;
}

.wiki-container {
  max-width: 860px;
  margin: 0 auto;
}

/* 頂部導航列 */
.top-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  background: var(--card-bg);
  border: 2px solid var(--border-ink);
  border-radius: 14px;
  padding: 0.85rem 1.25rem;
  box-shadow: 3px 3px 0px rgba(35, 31, 32, 0.9);
  margin-bottom: 2rem;
}

.breadcrumbs {
  font-size: 0.9rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--ink-muted);
}

.breadcrumbs a {
  color: var(--ink-black);
  text-decoration: none;
  border-bottom: 1px dashed var(--ink-muted);
}

.breadcrumbs a:hover {
  color: #8C4324;
  border-bottom-style: solid;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.nav-btn {
  font-size: 0.82rem;
  font-weight: 700;
  text-decoration: none;
  color: var(--ink-black);
  background: var(--card-alt);
  border: 1.5px solid var(--border-ink);
  padding: 0.35rem 0.8rem;
  border-radius: 8px;
  box-shadow: 2px 2px 0px rgba(35, 31, 32, 0.8);
  transition: all 0.12s ease;
}

.nav-btn:hover {
  transform: translate(-1px, -1px);
  box-shadow: 3px 3px 0px rgba(35, 31, 32, 0.9);
  background: var(--accent-warm);
}

.nav-btn.primary {
  background: var(--ink-black);
  color: #FAF8F5;
}

.nav-btn.primary:hover {
  background: #3B3436;
}

/* 主文章卡片 */
.article-card {
  background: var(--card-bg);
  border: 2px solid var(--border-ink);
  border-radius: 18px;
  padding: 2.5rem 2.2rem;
  box-shadow: 4px 5px 0px rgba(35, 31, 32, 0.9);
  margin-bottom: 2.5rem;
}

/* 標題與內文排版 */
h1.article-title {
  font-size: 2.1rem;
  font-weight: 900;
  line-height: 1.3;
  margin-bottom: 1.2rem;
  letter-spacing: -0.5px;
  color: var(--ink-black);
  border-bottom: 3px solid var(--border-ink);
  padding-bottom: 0.8rem;
}

h2 {
  font-size: 1.4rem;
  font-weight: 800;
  margin-top: 2.2rem;
  margin-bottom: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border-bottom: 1.5px solid var(--border-subtle);
  padding-bottom: 0.4rem;
}

h2::before {
  content: "";
  display: inline-block;
  width: 9px;
  height: 9px;
  background: var(--ink-black);
  border-radius: 50%;
}

h3 {
  font-size: 1.15rem;
  font-weight: 800;
  margin-top: 1.6rem;
  margin-bottom: 0.6rem;
  color: #2D2728;
}

p {
  margin-bottom: 1.1rem;
  font-size: 1.02rem;
}

/* 金句與引言 */
.quote-highlight {
  background: var(--card-alt);
  border-left: 5px solid var(--border-ink);
  border-radius: 0 12px 12px 0;
  padding: 1.1rem 1.4rem;
  margin: 1.4rem 0;
  font-size: 1.05rem;
  font-weight: 600;
  line-height: 1.7;
}

/* 補充說明 / Note Alert 區塊 */
.callout-note {
  background: var(--accent-callout);
  border: 1.8px solid var(--border-ink);
  border-radius: 12px;
  padding: 1.1rem 1.3rem;
  margin: 1.4rem 0;
  box-shadow: 2px 3px 0px rgba(35, 31, 32, 0.8);
}

.callout-note-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.78rem;
  font-weight: 800;
  background: var(--accent-badge);
  border: 1.2px solid var(--border-ink);
  padding: 0.15rem 0.6rem;
  border-radius: 6px;
  margin-bottom: 0.6rem;
}

/* 清單樣式 */
ul, ol {
  margin: 0.8rem 0 1.2rem 1.8rem;
  font-size: 1rem;
}

li {
  margin-bottom: 0.5rem;
}

li strong {
  color: var(--ink-black);
}

/* 表格樣式 */
.table-wrapper {
  overflow-x: auto;
  margin: 1.5rem 0 2rem;
  border: 2px solid var(--border-ink);
  border-radius: 12px;
  box-shadow: 3px 3px 0px rgba(35, 31, 32, 0.85);
  background: #FFFFFF;
}

table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.95rem;
}

th, td {
  padding: 0.85rem 1.1rem;
  border-bottom: 1px solid var(--border-subtle);
  border-right: 1px solid var(--border-subtle);
}

th:last-child, td:last-child {
  border-right: none;
}

tr:last-child td {
  border-bottom: none;
}

th {
  background: var(--card-alt);
  font-weight: 800;
  color: var(--ink-black);
  border-bottom: 2px solid var(--border-ink);
}

tr:nth-child(even) td {
  background: #FCFBF9;
}

/* 行內代碼與標記 */
code {
  font-family: var(--code-font);
  font-size: 0.88em;
  background: var(--card-alt);
  border: 1px solid var(--border-subtle);
  padding: 0.15em 0.45em;
  border-radius: 5px;
  color: #7A331A;
}

/* 連結樣式 */
a {
  color: #1A5FA8;
  text-decoration: underline;
  text-underline-offset: 3px;
  font-weight: 600;
}

a:hover {
  color: #A33A18;
}

hr.wiki-divider {
  border: none;
  border-top: 1.5px dashed var(--border-subtle);
  margin: 2.2rem 0;
}

/* 頁尾導航 */
.footer-nav {
  text-align: center;
  padding: 2rem 0;
  font-size: 0.9rem;
  color: var(--ink-muted);
}

.footer-nav a {
  margin: 0 0.5rem;
  color: var(--ink-black);
}

@media (max-width: 640px) {
  body {
    padding: 1rem 0.75rem 3rem;
  }
  .article-card {
    padding: 1.5rem 1.1rem;
  }
  h1.article-title {
    font-size: 1.65rem;
  }
  .top-nav {
    flex-direction: column;
    align-items: flex-start;
  }
}
"""


def slugify(text: str) -> str:
    """產生 URL slug 錨點"""
    clean = re.sub(r"[^\w\u4e00-\u9fff\- ]", "", text).strip()
    return clean.replace(" ", "-")


def format_inline(text: str, current_file: Path) -> str:
    """行內格式解析：粗體、行內代碼、超連結替換 (.md -> .html)"""
    # 1. 處理行內代碼，保護免於格式被粗體干擾
    code_tokens = []
    def code_repl(m):
        code_tokens.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"__CODE_TOKEN_{len(code_tokens)-1}__"
    text = re.sub(r"`([^`]+)`", code_repl, text)

    # 2. 處理粗體 **text**
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)

    # 3. 處理數學式 $f$ 轉為 code 標籤
    text = re.sub(r"\$([^$]+)\$", r"<code>\1</code>", text)

    # 4. 處理 Markdown 連結 [text](url)
    def link_repl(m):
        label = m.group(1)
        url = m.group(2).strip()

        # 外部連結
        if url.startswith(("http://", "https://", "mailto:")):
            return f'<a href="{url}" target="_blank" rel="noopener">{label}</a>'

        # 內部相對連結：若指向 .md 且位於 wiki 內部，改為 .html
        if ".md" in url:
            parts = url.split("#", 1)
            path_part = parts[0]
            anchor_part = f"#{parts[1]}" if len(parts) > 1 else ""

            # 只要不是指向 raw/ 的原始文獻，皆轉為 .html
            if "raw/" not in path_part:
                path_part = re.sub(r"\.md$", ".html", path_part)
            new_url = path_part + anchor_part
            return f'<a href="{new_url}">{label}</a>'

        return f'<a href="{url}">{label}</a>'

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_repl, text)

    # 5. 還原代碼 token
    for i, tok in enumerate(code_tokens):
        text = text.replace(f"__CODE_TOKEN_{i}__", tok)

    return text


def render_markdown_to_html(md_text: str, current_file: Path) -> tuple:
    """將 Markdown 文字轉換為結構化 HTML 片段"""
    lines = md_text.splitlines()
    body_parts = []
    title = current_file.stem

    i = 0
    n = len(lines)

    while i < n:
        raw_line = lines[i]
        line = raw_line.rstrip()

        # 空行
        if not line:
            i += 1
            continue

        # 一級標題 (文章主標題)
        if line.startswith("# "):
            title = line[2:].strip()
            i += 1
            continue

        # 分隔線 (--- 或 ***)
        if re.match(r"^(\-{3,}|\*{3,})$", line.strip()):
            body_parts.append('<hr class="wiki-divider"/>')
            i += 1
            continue

        # 二級標題 (同時建立文字錨點與 slug 錨點)
        if line.startswith("## "):
            h_text = line[3:].strip()
            slug = slugify(h_text)
            body_parts.append(
                f'<h2 id="{html.escape(h_text)}"><span id="{slug}"></span>{format_inline(h_text, current_file)}</h2>'
            )
            i += 1
            continue

        # 三級標題
        if line.startswith("### "):
            h_text = line[4:].strip()
            slug = slugify(h_text)
            body_parts.append(
                f'<h3 id="{html.escape(h_text)}"><span id="{slug}"></span>{format_inline(h_text, current_file)}</h3>'
            )
            i += 1
            continue

        # 四級標題
        if line.startswith("#### "):
            h_text = line[5:].strip()
            body_parts.append(f'<h4>{format_inline(h_text, current_file)}</h4>')
            i += 1
            continue

        # 補充說明 Callout: > [!NOTE] [補充說明]
        if line.startswith("> [!NOTE]"):
            callout_lines = []
            badge_title = line.replace("> [!NOTE]", "").strip() or "補充說明"
            i += 1
            while i < n and lines[i].startswith(">"):
                c_line = lines[i].lstrip(">").strip()
                if c_line:
                    callout_lines.append(c_line)
                i += 1

            c_content = " ".join(callout_lines)
            c_html = format_inline(c_content, current_file)
            body_parts.append(
                f'<div class="callout-note">\n'
                f'  <div class="callout-note-badge">💡 {html.escape(badge_title)}</div>\n'
                f'  <p>{c_html}</p>\n'
                f'</div>'
            )
            continue

        # 一般引言 / 金句: > ...
        if line.startswith(">"):
            quote_lines = []
            while i < n and lines[i].startswith(">"):
                q_line = lines[i].lstrip(">").strip()
                if q_line:
                    quote_lines.append(q_line)
                i += 1
            q_content = " ".join(quote_lines)
            q_html = format_inline(q_content, current_file)
            body_parts.append(f'<div class="quote-highlight">{q_html}</div>')
            continue

        # 表格檢測 (| ... |)
        if line.startswith("|") and line.endswith("|"):
            table_lines = []
            while i < n and lines[i].startswith("|") and lines[i].endswith("|"):
                table_lines.append(lines[i].strip())
                i += 1

            if len(table_lines) >= 2:
                header_cells = [c.strip() for c in table_lines[0].strip("|").split("|")]
                rows = []
                for r in table_lines[2:]:
                    cells = [c.strip() for c in r.strip("|").split("|")]
                    rows.append(cells)

                t_html = ['<div class="table-wrapper">', '<table>', '  <thead>', '    <tr>']
                for hc in header_cells:
                    t_html.append(f'      <th>{format_inline(hc, current_file)}</th>')
                t_html.extend(['    </tr>', '  </thead>', '  <tbody>'])

                for row in rows:
                    t_html.append('    <tr>')
                    for cell in row:
                        t_html.append(f'      <td>{format_inline(cell, current_file)}</td>')
                    t_html.append('    </tr>')

                t_html.extend(['  </tbody>', '</table>', '</div>'])
                body_parts.append("\n".join(t_html))
            continue

        # 清單處理 (支援二層縮排清單)
        if re.match(r"^\s*[*-]\s+", line):
            list_lines = []
            while i < n and (re.match(r"^\s*[*-]\s+", lines[i]) or (lines[i].startswith("  ") and lines[i].strip())):
                list_lines.append(lines[i])
                i += 1

            ul_html = ["<ul>"]
            in_sub = False
            for ll in list_lines:
                m_sub = re.match(r"^\s{2,}[*-]\s+(.+)$", ll)
                m_top = re.match(r"^\s*[*-]\s+(.+)$", ll)
                if m_sub:
                    if not in_sub:
                        ul_html.append("  <ul>")
                        in_sub = True
                    ul_html.append(f"    <li>{format_inline(m_sub.group(1).strip(), current_file)}</li>")
                elif m_top:
                    if in_sub:
                        ul_html.append("  </ul>")
                        in_sub = False
                    ul_html.append(f"  <li>{format_inline(m_top.group(1).strip(), current_file)}</li>")
            if in_sub:
                ul_html.append("  </ul>")
            ul_html.append("</ul>")
            body_parts.append("\n".join(ul_html))
            continue

        # 有序清單 (1. 2.)
        if re.match(r"^\d+\.\s+", line):
            ol_items = []
            while i < n and re.match(r"^\d+\.\s+", lines[i]):
                m = re.match(r"^\d+\.\s+(.+)$", lines[i])
                if m:
                    ol_items.append(m.group(1).strip())
                i += 1
            ol_html = ["<ol>"]
            for item in ol_items:
                ol_html.append(f'  <li>{format_inline(item, current_file)}</li>')
            ol_html.append("</ol>")
            body_parts.append("\n".join(ol_html))
            continue

        # 一般段落 (連續行合併)
        para_lines = []
        while i < n and lines[i].strip() and not lines[i].startswith(("#", ">", "|", "*", "-")) and not re.match(r"^\d+\.", lines[i]):
            para_lines.append(lines[i].strip())
            i += 1

        if para_lines:
            p_content = " ".join(para_lines)
            body_parts.append(f'<p>{format_inline(p_content, current_file)}</p>')
        else:
            # 安全防呆：若未被任何規則匹配，保證指標推進，杜絕無窮迴圈
            if i < n:
                fallback_str = lines[i].strip()
                if fallback_str:
                    body_parts.append(f'<p>{format_inline(fallback_str, current_file)}</p>')
                i += 1

    return title, "\n".join(body_parts)


def build_page_html(md_file: Path) -> str:
    category = md_file.parent.name
    category_label = CATEGORY_NAMES.get(category, category)
    rel_to_root = "../../"

    md_content = md_file.read_text(encoding="utf-8")
    title, body_html = render_markdown_to_html(md_content, md_file)

    page_html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)} - 數位音樂與音質知識庫</title>
  <style>
{CSS_STYLE}
  </style>
</head>
<body>
  <div class="wiki-container">
    <!-- 頂部導航列 -->
    <nav class="top-nav">
      <div class="breadcrumbs">
        <a href="{rel_to_root}index.html">🏠 首頁</a>
        <span>/</span>
        <a href="{rel_to_root}index.html#wiki-catalog">📚 Wiki 導覽</a>
        <span>/</span>
        <span>{html.escape(category_label)}</span>
      </div>
      <div class="nav-actions">
        <a href="{rel_to_root}presentation/index.html" class="nav-btn primary">▶ 開啟教學簡報</a>
        <a href="{rel_to_root}index.html" class="nav-btn">← 回首頁</a>
        <a href="./{md_file.name}" target="_blank" class="nav-btn" title="查看原始 Markdown 文本">📄 Markdown 原文</a>
      </div>
    </nav>

    <!-- 文章本體 -->
    <article class="article-card">
      <h1 class="article-title">{format_inline(title, md_file)}</h1>
      <div class="article-body">
{body_html}
      </div>
    </article>

    <!-- 底部導航 -->
    <footer class="footer-nav">
      <p>數位音樂與音質結構化知識庫 ｜ 依據 Andrej Karpathy LLM Wiki 構想建立</p>
      <p style="margin-top: 0.5rem;">
        <a href="{rel_to_root}index.html">專案首頁</a> •
        <a href="{rel_to_root}presentation/index.html">12 頁手繪簡報</a> •
        <a href="{rel_to_root}index.md">Wiki 目錄 (index.md)</a> •
        <a href="./{md_file.name}">本篇 Markdown 原文</a>
      </p>
    </footer>
  </div>
</body>
</html>
"""
    return page_html


def main():
    print("=" * 60)
    print("🚀 啟動 Wiki Markdown → HTML 靜態生成器...")
    print("=" * 60)

    md_files = sorted(list(WIKI_DIR.rglob("*.md")))
    if not md_files:
        print("❌ 未在 wiki/ 目錄下找到任何 .md 檔案！")
        return False

    generated_count = 0
    for md_path in md_files:
        html_content = build_page_html(md_path)
        out_html_path = md_path.with_suffix(".html")
        out_html_path.write_text(html_content, encoding="utf-8")
        rel_path = out_html_path.relative_to(ROOT_DIR).as_posix()
        print(f"  ✅ 已生成：{rel_path}")
        generated_count += 1

    print("-" * 60)
    print(f"🎉 成功生成 {generated_count} 篇 Wiki 靜態 HTML 閱讀頁面！")
    print("=" * 60)
    return True


if __name__ == "__main__":
    main()
