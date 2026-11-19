# ALAC（Apple Lossless Audio Codec）

> **一句話白話結論**：Apple 生態系專屬的無損壓縮技術，Apple Music 整個百萬無損曲庫皆採用它編碼，是蘋果用戶享受無損音質的核心基石。

## 概念說明
Apple 無損音訊編碼（ALAC，Apple Lossless Audio Codec，常簡稱為 Apple Lossless）是由 Apple 公司自行研發的無損壓縮格式，通常以 `.m4a` 檔案封裝呈現。ALAC 最初為封閉格式，後來 Apple 於 2011 年以開源的 Apache 授權條款釋出原始碼。

在功能上，ALAC 與 FLAC 完全同級：兩者皆能在不損失任何聲音訊號的前提下，將未壓縮的 PCM 音訊容量減少約 40%～50%（壓縮後體積約為原本的 50%～60%）。Apple Music 目前所提供的「無損音訊（Lossless）」與「高解析無損音訊（Hi-Res Lossless）」，全數使用 ALAC 格式進行編碼與傳輸。

## 重點整理
* **Apple 軟硬體深度原生整合**：
  * 在 iPhone、iPad、Mac、Apple TV、HomePod 等所有 Apple 裝置中享有最高的硬體解碼相容性與省電效率。
* **技術規格與涵蓋範圍**：
  * 支援 16-bit、20-bit、24-bit 與 32-bit 整數取樣深度，取樣率最高可支援至 384 kHz。
  * **Apple Music 中的 ALAC 檔位劃分**：
    * 官方支援文件明確將曲庫區分為「標準無損（Lossless）」與「高解析度無損（Hi-Res Lossless）」，並以「48 kHz」作為硬體輸出門檻（播放高於 48 kHz 音訊需搭配外接 DAC；14/16 吋 MacBook Pro 則原生支援至 96 kHz）。
    * > [!NOTE] [補充說明 / 待進一步文件確認]
      > 坊間常引用 Apple Music 標準無損為 24-bit / 48 kHz、高解析無損為 24-bit / 192 kHz（iZotope 文章亦提及現代串流服務能支援至 192 kHz），但在目前提供的 Apple 官方說明文件（raw/05）中，僅具體載明「高於 48 kHz」與「最高至 96 kHz」，並未直接出現 24-bit / 192 kHz 的文字規格，此部分細節先予標記保留。
* **與 FLAC 的生態區隔**：
  * 雖然 ALAC 已經開源，且在 Windows 與 Android 版 Apple Music App 中皆能順暢播放，但在一般獨立發燒硬體（如車載音響、非 Apple 播放器）與開放網頁平台的普及度上，社群仍普遍更偏好開放且免授權爭議的 FLAC。

## 生活類比
> [!NOTE] [補充說明] 生活類比
> ALAC 與 FLAC 的關係就像快充界的 **「Apple MagSafe 磁吸充電 vs. 通用 Qi2 無線充電」**：兩者底層充電功率與保真效率幾乎完全相同，但如果你全套使用 Apple 設備，使用原廠專屬的 ALAC/MagSafe 體驗最為天衣無縫；而走出 Apple 宇宙，開放的 FLAC 則是通行全球的通用規格。

## 實務應用與選擇建議
* **Apple 使用者與 iTunes/Music 收藏**：若主要在 macOS、iOS 裝置上管理個人本機無損音樂庫，轉換為 ALAC 能獲得最佳的系統與 AirPlay 相容度。
* **Apple Music 串流使用者**：只要訂閱 Apple Music，無需額外付費即可直接串流 ALAC 無損曲庫（但需注意播放端設備與耳機的硬體限制）。

## 關聯條目
* [FLAC 格式專頁](./flac.md) - 比較開放標準 FLAC 與 Apple ALAC 之異同
* [AAC 格式專頁](./aac.md) - Apple 生態系中的主力有損壓縮格式
* [Apple Music 無損音訊與播放設備指南](../comparisons/apple-music-lossless.md) - 深入了解 Apple 設備與耳機播放 ALAC 的硬體限制與必備條件
* [橫向對比：有損壓縮 vs 無損壓縮](../comparisons/lossy-vs-lossless.md) - 評估無損 ALAC 與有損串流的流量與音質代價

## 原始來源
* **文章標題**：[Web audio codec guide](https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Formats/Audio_codecs)
  * **原始檔案**：`raw/03-mdn-audio-codecs.md`
  * **對應章節/段落**：章節「ALAC (Apple Lossless Audio Codec)」
* **文章標題**：[About lossless audio in Apple Music](https://support.apple.com/en-us/118295)
  * **原始檔案**：`raw/05-apple-lossless-audio.md`
  * **對應章節/段落**：章節「About lossless audio in Apple Music」、「What you need to know about lossless in Apple Music」
