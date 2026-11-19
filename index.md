# 數位音樂與音質知識庫（Digital Audio & Sound Quality Wiki）

歡迎來到數位音樂與音質結構化知識庫。本 Wiki 依據 Andrej Karpathy 的 LLM Wiki 構想構建，旨在以直覺、通俗、生活化的方式，系統化梳理數位音訊核心原理、常見格式、音質對比與大眾迷思。

本知識庫亦作為未來製作「教學型 HTML 簡報」的單一事實來源（Single Source of Truth）。

---

## 🗺️ 建議閱讀順序（Recommended Reading Path）

> 針對無技術背景的讀者，建議依照以下學習路徑閱讀，建立由淺入深的直覺概念：

1. **第一站：音訊數位化基礎**
   * [取樣率（Sampling Rate）](./wiki/concepts/sample-rate.md) — 聲音每秒拍幾次照？最高能記錄到多高頻率？
   * [位元深度（Bit Depth）](./wiki/concepts/bit-depth.md) — 測量聲音大小聲的刻度有多細？底噪與動態範圍的真相。
   * [位元率（Bitrate）與檔案大小](./wiki/concepts/bitrate.md) — 每秒吃掉多少資料量？未壓縮檔案為什麼這麼大？
2. **第二站：壓縮的魔法與代價**
   * [音訊壓縮原理與心理聲學](./wiki/concepts/compression-basics.md) — 聲音難以直接壓縮，如何靠人耳聽覺盲點神奇瘦身 20 倍？
3. **第三站：常見格式家族**
   * [MP3（MPEG-1 Audio Layer III）](./wiki/formats/mp3.md) — 數位音樂普及的最大功臣，跨時代的相容性之王。
   * [AAC（進階音訊編碼）](./wiki/formats/aac.md) — 現代網路串流與大眾藍牙耳機的主力有損格式。
   * [FLAC（自由無損音訊編碼）](./wiki/formats/flac.md) — 開源無專利的音訊真空袋，發燒友與典藏的最佳無損選擇。
   * [ALAC（Apple 無損音訊編碼）](./wiki/formats/alac.md) — Apple 生態系專用無損格式，Apple Music 高音質串流的底層支柱。
4. **第四站：實用比較與決策**
   * [橫向對比：有損壓縮 vs 無損壓縮](./wiki/comparisons/lossy-vs-lossless.md) — 保留全部細節 vs 節省九成空間，生活情境該怎麼選？
   * [實務指南：Apple Music 無損音訊與播放設備限制](./wiki/comparisons/apple-music-lossless.md) — 戴 AirPods 真的能聽無損嗎？解密藍牙傳輸與外接 DAC 限制。
5. **第五站：常見迷思破解**
   * [迷思破解：取樣率與位元深度越高，音質就一定越好嗎？](./wiki/myths/higher-sample-rate-and-bit-depth.md) — 破解 Hi-Res 24/192 神話與不存在的階梯鋸齒波形。

---

## 📚 條目分類目錄（Taxonomy & Pages）

### 1. 核心概念（Concepts）
* [取樣率（Sampling Rate）](./wiki/concepts/sample-rate.md)
* [位元深度（Bit Depth）](./wiki/concepts/bit-depth.md)
* [位元率（Bitrate）與檔案大小](./wiki/concepts/bitrate.md)
* [音訊壓縮原理與心理聲學](./wiki/concepts/compression-basics.md)

### 2. 音訊格式（Formats）
* [MP3（MPEG-1 Audio Layer III）](./wiki/formats/mp3.md)
* [AAC（進階音訊編碼）](./wiki/formats/aac.md)
* [FLAC（自由無損音訊編碼）](./wiki/formats/flac.md)
* [ALAC（Apple 無損音訊編碼）](./wiki/formats/alac.md)

### 3. 橫向對比（Comparisons）
* [橫向對比：有損壓縮 vs 無損壓縮](./wiki/comparisons/lossy-vs-lossless.md)
* [實務指南：Apple Music 無損音訊與播放設備限制](./wiki/comparisons/apple-music-lossless.md)

### 4. 迷思破解（Myths & FAQs）
* [迷思破解：取樣率與位元深度越高，音質就一定越好嗎？](./wiki/myths/higher-sample-rate-and-bit-depth.md)

---

## 🛠️ 維護與來源資訊
* **Wiki 維護規範**：請參閱 [AGENTS.md](./AGENTS.md)
* **變更紀錄日誌**：請參閱 [log.md](./log.md)
* **原始資料庫存**：請參閱 [raw/](./raw/)
