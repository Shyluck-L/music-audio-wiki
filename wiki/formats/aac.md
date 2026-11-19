# AAC（Advanced Audio Coding）

> **一句話白話結論**：MP3 的全方位升級版接班人，在更低位元率下能提供更出色的音質，是 Apple 串流、YouTube 與大眾藍牙耳機的核心有損格式。

## 概念說明
進階音訊編碼（AAC，Advanced Audio Coding）是由 MPEG 組織（包含杜比、Fraunhofer 等機構）共同制定的有損音訊壓縮技術，屬於 MPEG-4（Part 3）與 MPEG-2（Part 7）標準的一部分。其誕生目標就是為了解決 MP3 壓縮效率較低與高頻衰減的問題，在相同甚至更小的檔案大小下提供更優秀的聲音細節。

AAC 具備多種針對不同場景特化的設定檔（Profiles），廣泛應用於現代串流影音（如 YouTube）、智慧型手機以及 Apple 生態系統（Apple Music 預設有損串流格式）。

## 重點整理
* **顯著躍升的壓縮效率**：
  * 相較於 MP3，AAC 採用了更先進的轉換演算法與心理聲學模型。
  * **立體聲建議起點**：AAC 僅需約 **96 kbps** 即可呈現良好的立體聲聽感（MP3 通常需要 128 kbps 以上）。
  * 業界普遍評估，**256 kbps 的 AAC** 在聽感還原度上已能媲美甚至超越 320 kbps 的 MP3。
* **豐富的規格支援度**：
  * 支援取樣率由 8 kHz 至 96 kHz。
  * 位元率可自由設定，最高支援至 512 kbps，並完整支援固定位元率（CBR）與可變位元率（VBR）。
* **Apple 生態系與藍牙無線傳輸的核心**：
  * Apple 旗下裝置（iPhone、iPad、Mac）與無線耳機（AirPods 全系列、Beats 系列）在進行藍牙傳輸時，均預設採用 **Apple AAC 藍牙編碼**，確保在有限頻寬下提供穩定的高音質無線聆聽體驗。
* **專利授權考量**：
  * 與 MP3 專利全面過期不同，AAC 仍屬於受專利保護的格式，因此在開源瀏覽器或特殊系統中，通常依賴作業系統底層隨附的解碼模組來提供播放支援。

## 生活類比
> [!NOTE] [補充說明] 生活類比
> 如果 MP3 像是經典的大排氣量自然進氣引擎，AAC 就好比現代的「渦輪增壓油電引擎」：消耗更少的油料（佔用更低位元率），卻能迸發出相同的馬力與平順行路質感（呈現更豐富的高頻與動態細節）。

## 實務應用與選擇建議
* **現代網路串流與行動下載**：日常聽音樂若考量手機容量與行動網路流量，**256 kbps AAC** 是兼顧高保真度與順暢載入的甜蜜點首選。
* **無線耳機聆聽**：在 Apple 裝置上搭配 AirPods 進行常規藍牙播放時，不論音源是無損還是有損，藍牙傳輸端最終都會轉為 AAC 傳輸（Apple Vision Pro 之專有無線協定等少數情境除外）。

## 關聯條目
* [MP3 格式專頁](./mp3.md) - 比較 AAC 與其前身 MP3 的演進與差異
* [ALAC 格式專頁](./alac.md) - Apple 生態系中的無損音訊格式對應方案
* [Apple Music 無損音訊與播放設備指南](../comparisons/apple-music-lossless.md) - 了解 Apple 藍牙設備為何受限於 AAC 傳輸
* [橫向對比：有損壓縮 vs 無損壓縮](../comparisons/lossy-vs-lossless.md) - 評估高碼率有損與無損音訊之實質差別

## 原始來源
* **文章標題**：[Web audio codec guide](https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Formats/Audio_codecs)
  * **原始檔案**：`raw/03-mdn-audio-codecs.md`
  * **對應章節/段落**：章節「AAC (Advanced Audio Coding)」
* **文章標題**：[About lossless audio in Apple Music](https://support.apple.com/en-us/118295)
  * **原始檔案**：`raw/05-apple-lossless-audio.md`
  * **對應章節/段落**：章節「About lossless audio with Apple and Beats headphones」
