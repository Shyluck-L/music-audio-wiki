#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gate 3: 瀏覽器實際畫面渲染、尺寸溢出與導航功能測試執行腳本
透過本機 Headless Chrome 載入自我檢測的簡報頁面，精確檢核 12 頁畫面佈局與互動功能。
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT_DIR / "presentation" / "index.html"
TEST_HTML_PATH = ROOT_DIR / "scratch" / "test_presentation.html"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

TEST_INJECTION = """
<div id="test-results" style="display:none;"></div>
<script>
(function() {
  function executeGate3Verification() {
    const slides = document.querySelectorAll('.slide');
    const results = {
      status: 'SUCCESS',
      total_slides: slides.length,
      slides_data: [],
      navigation_tests: {},
      overflow_issues: []
    };

    if (slides.length !== 12) {
      results.status = 'FAIL';
      results.overflow_issues.push('預期 12 頁，實際找到 ' + slides.length + ' 頁');
    }

    // 逐頁檢查畫面與溢出
    for (let i = 0; i < slides.length; i++) {
      // 強制切換該頁 active 進行渲染尺寸量測
      slides.forEach((s, idx) => {
        if (idx === i) s.classList.add('active');
        else s.classList.remove('active');
      });

      const slide = slides[i];
      const scrollH = slide.scrollHeight;
      const clientH = slide.clientHeight;
      const scrollW = slide.scrollWidth;
      const clientW = slide.clientWidth;

      // 檢查是否有垂直或水平溢出 (容許 2px 浮點渲染公差)
      const hasVerticalOverflow = scrollH > clientH + 2;
      const hasHorizontalOverflow = scrollW > clientW + 2;

      const titleEl = slide.querySelector('.slide-title');
      const titleText = titleEl ? titleEl.textContent.trim() : '';

      results.slides_data.push({
        slide_index: i + 1,
        title: titleText,
        clientHeight: clientH,
        scrollHeight: scrollH,
        clientWidth: clientW,
        scrollWidth: scrollW,
        vertical_overflow: hasVerticalOverflow,
        horizontal_overflow: hasHorizontalOverflow
      });

      if (hasVerticalOverflow) {
        results.overflow_issues.push('第 ' + (i + 1) + ' 頁垂直溢出: scrollH=' + scrollH + ', clientH=' + clientH);
      }
      if (hasHorizontalOverflow) {
        results.overflow_issues.push('第 ' + (i + 1) + ' 頁水平溢出: scrollW=' + scrollW + ', clientW=' + clientW);
      }
    }

    // 專項 SVG 文字邊界檢核：第 8 頁下方說明標籤
    // 驗證標籤文字邊界 getBBox() 是否完全包含在外框 rect 內，且具備充足內距（>= 8px）
    slides.forEach((s, idx) => {
      if (idx === 7) s.classList.add('active');
      else s.classList.remove('active');
    });

    results.svg_boundary_tests = {};
    const s8Rect = document.getElementById('slide8-badge-rect');
    const s8Text = document.getElementById('slide8-badge-text');

    if (!s8Rect || !s8Text) {
      results.status = 'FAIL';
      results.svg_boundary_tests.slide8_badge = {
        passed: false,
        details: '找不到 slide8-badge-rect 或 slide8-badge-text 元素'
      };
      results.overflow_issues.push('第 8 頁找不到 SVG 標籤元素');
    } else {
      try {
        const rBBox = s8Rect.getBBox();
        const tBBox = s8Text.getBBox();

        const leftPadding = tBBox.x - rBBox.x;
        const rightPadding = (rBBox.x + rBBox.width) - (tBBox.x + tBBox.width);
        const topPadding = tBBox.y - rBBox.y;
        const bottomPadding = (rBBox.y + rBBox.height) - (tBBox.y + tBBox.height);

        // 判定標準：左右內距至少各 8px (避免貼邊)，上下內距至少各 2px
        const isHorizontallyContained = (leftPadding >= 8) && (rightPadding >= 8);
        const isVerticallyContained = (topPadding >= 2) && (bottomPadding >= 2);
        const isContained = isHorizontallyContained && isVerticallyContained;

        results.svg_boundary_tests.slide8_badge = {
          passed: isContained,
          rect: { x: rBBox.x, y: rBBox.y, width: rBBox.width, height: rBBox.height },
          text: { x: tBBox.x, y: tBBox.y, width: tBBox.width, height: tBBox.height },
          text_content: s8Text.textContent.trim(),
          padding: {
            left: Math.round(leftPadding * 10) / 10,
            right: Math.round(rightPadding * 10) / 10,
            top: Math.round(topPadding * 10) / 10,
            bottom: Math.round(bottomPadding * 10) / 10
          },
          details: isContained
            ? `文字「${s8Text.textContent.trim()}」完全位於外框內 (左邊距: ${Math.round(leftPadding)}px, 右邊距: ${Math.round(rightPadding)}px, 上邊距: ${Math.round(topPadding)}px, 下邊距: ${Math.round(bottomPadding)}px)`
            : `文字超出外框或內距不足 (左邊距: ${Math.round(leftPadding)}px, 右邊距: ${Math.round(rightPadding)}px)`
        };

        if (!isContained) {
          results.status = 'FAIL';
          results.overflow_issues.push('第 8 頁 SVG 標籤文字超出或貼邊: ' + results.svg_boundary_tests.slide8_badge.details);
        }
      } catch (err) {
        results.status = 'FAIL';
        results.svg_boundary_tests.slide8_badge = {
          passed: false,
          details: '計算 getBBox 異常: ' + err.message
        };
        results.overflow_issues.push('第 8 頁 SVG getBBox 異常: ' + err.message);
      }
    }

    // 導航按鈕與快捷鍵功能測試
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Home' }));
    const homeCounter = document.getElementById('current-slide-num').textContent.trim();
    const prevDisabled = document.getElementById('prev-btn').disabled;
    results.navigation_tests.home_key_and_prev_disabled = (homeCounter === '01' && prevDisabled === true);

    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'End' }));
    const endCounter = document.getElementById('current-slide-num').textContent.trim();
    const nextDisabled = document.getElementById('next-btn').disabled;
    results.navigation_tests.end_key_and_next_disabled = (endCounter === '12' && nextDisabled === true);

    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Home' }));
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight' }));
    const step2 = document.getElementById('current-slide-num').textContent.trim();
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowLeft' }));
    const step1 = document.getElementById('current-slide-num').textContent.trim();
    results.navigation_tests.arrow_step_navigation = (step2 === '02' && step1 === '01');

    const progressBar = document.getElementById('progress-bar');
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'End' }));
    results.navigation_tests.progress_bar_100pct = (progressBar.style.width === '100%');

    // 導航點擊測試 (點選第 5 點跳轉第 5 頁)
    const dots = document.querySelectorAll('.dot');
    if (dots.length === 12) {
      dots[4].click();
      const dot5Counter = document.getElementById('current-slide-num').textContent.trim();
      results.navigation_tests.dot_click_jump = (dot5Counter === '05');
    }

    const allPass = Object.values(results.navigation_tests).every(v => v === true);
    if (!allPass || results.overflow_issues.length > 0) {
      results.status = 'FAIL';
    }

    const resEl = document.getElementById('test-results');
    resEl.textContent = JSON.stringify(results);
    resEl.style.display = 'block';
  }

  // 立即執行檢驗
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', executeGate3Verification);
  } else {
    executeGate3Verification();
  }
})();
</script>
"""


def prepare_test_html():
    raw_html = HTML_PATH.read_text(encoding="utf-8")
    injected = raw_html.replace("</body>", TEST_INJECTION + "\n</body>")
    TEST_HTML_PATH.write_text(injected, encoding="utf-8")


def run_gate3_test():
    print("=" * 60)
    print("🔍 執行 Gate 3 瀏覽器實際畫面檢核 (Browser Render Verification)...")
    print("=" * 60)

    if not Path(CHROME_PATH).exists():
        print(f"❌ 找不到 Chrome 瀏覽器：{CHROME_PATH}")
        return False

    prepare_test_html()
    file_url = f"file:///{TEST_HTML_PATH.as_posix()}"
    print(f"🌐 啟動 Headless Chrome 載入測試頁面：{file_url}")

    resolutions = [
        ("1280,720", "標準 16:9 (720p)"),
        ("1920,1080", "Full HD 16:9 (1080p)"),
        ("1366,768", "常見筆電解析度")
    ]

    all_resolutions_pass = True

    for res_size, res_label in resolutions:
        print(f"\n🖥️ 測試解析度：{res_label} ({res_size})")
        cmd = [
            CHROME_PATH,
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            f"--window-size={res_size}",
            "--dump-dom",
            file_url,
        ]

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        except Exception as e:
            print(f"❌ 執行 Chrome 失敗：{e}")
            return False

        dom_output = proc.stdout
        match = re.search(r'<div id="test-results"[^>]*>(.*?)</div>', dom_output, re.DOTALL)
        if not match or not match.group(1).strip():
            print("❌ 未在 DOM 中提取到測試結果")
            return False

        raw_json = match.group(1).strip()
        try:
            data = json.loads(raw_json)
        except Exception as e:
            print(f"❌ JSON 解析測試結果失敗：{e}")
            return False

        status = data.get("status")
        total_slides = data.get("total_slides", 0)
        overflow_issues = data.get("overflow_issues", [])
        nav_tests = data.get("navigation_tests", {})

        nav_passed = bool(nav_tests) and all(nav_tests.values())
        print(f"   • 頁數：{total_slides} / 12 頁 | 導航測試：{'全部通過' if nav_passed else '部分失敗'}")

        # SVG 專項文字邊界結果
        svg_tests = data.get("svg_boundary_tests", {})
        slide8_svg = svg_tests.get("slide8_badge", {})
        svg_passed = slide8_svg.get("passed", False)
        if svg_passed:
            pad = slide8_svg.get("padding", {})
            rect_w = slide8_svg.get("rect", {}).get("width", 0)
            text_w = round(slide8_svg.get("text", {}).get("width", 0), 1)
            text_str = slide8_svg.get("text_content", "")
            print(f"   • SVG 邊界檢核：✅ 第 8 頁標籤「{text_str}」完全包覆於外框內 (字寬: {text_w}px / 框寬: {rect_w}px，左邊距: {pad.get('left')}px，右邊距: {pad.get('right')}px)")
        else:
            print(f"   • SVG 邊界檢核：❌ 第 8 頁標籤邊界異常：{slide8_svg.get('details', '未通過')}")

        has_failure = False
        if total_slides != 12:
            print(f"   ❌ 投影片總數異常：預期 12 頁，實際為 {total_slides} 頁")
            has_failure = True

        if not nav_passed:
            print(f"   ❌ 導航測試未全數通過：")
            for tname, tpass in nav_tests.items():
                if not tpass:
                    print(f"      - {tname}: 失敗")
            has_failure = True

        if not svg_passed:
            print(f"   ❌ 第 8 頁 SVG 標籤文字超出或貼邊")
            has_failure = True

        if overflow_issues:
            print(f"   ❌ 發現溢出問題 ({len(overflow_issues)} 項)：")
            for issue in overflow_issues[:3]:
                print(f"      - {issue}")
            has_failure = True

        if status != "SUCCESS":
            has_failure = True

        if has_failure:
            all_resolutions_pass = False
        else:
            print(f"   ✅ 12 頁全部尺寸正常、SVG 標籤文字內距充裕、無任何溢出截斷且導航測試全數通過")

    print("\n" + "=" * 60)
    if all_resolutions_pass:
        print("🎉 Gate 3 多解析度瀏覽器實際畫面與功能檢核全部通過！")
        print("=" * 60)
        return True
    else:
        print("❌ Gate 3 檢驗失敗，需進行 Route C 展示層修正！")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = run_gate3_test()
    sys.exit(0 if success else 1)
