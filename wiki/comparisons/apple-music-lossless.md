# 實務指南：Apple Music 無損音訊與播放設備限制（Apple Music Lossless Guide）

> **一句話白話結論**：Apple Music 雖然提供了 ALAC 無損曲庫，但標準藍牙連線並不支援無損；一般搭配 AirPods 藍牙聆聽時會自動轉為有損 AAC，要聽真無損主要需使用有線連接（特定專利協定如 Apple Vision Pro 為少數無線例外），若要播放高於 48 kHz 的音訊更需外接 DAC。

## 概念說明
Apple Music 提供「無損音訊（Lossless）」與「高解析度無損（Hi-Res Lossless）」兩種品質規格（採用 ALAC 編碼）。許多音樂愛好者開啟該設定後，誤以為戴上任何 AirPods 無線耳機就能享受無損音質。

然而，音訊播放鏈受制於「傳輸通道」與「終端解碼硬體」的物理限制。Apple 官方支援文件明確指出，一般的藍牙無線連線目前在技術上並不支援無損音訊傳輸。要真正聆聽到無損音質，必須滿足特定的設備搭配與連接條件。

## 重點整理：各設備播放條件與硬體限制

### 1. 標準藍牙耳機的限制：AirPods 藍牙傳輸「並非無損」
* **標準藍牙協定限制**：
  * **所有透過標準藍牙連線的耳機**（包含 AirPods 1/2/3/4、AirPods Pro 系列、無線狀態下的 AirPods Max）以及絕大多數 Beats 無線耳機，在藍牙傳輸時**一律採用有損的 Apple AAC 藍牙編碼**。
  * 就算 Apple Music 串流下載的是 ALAC 無損檔案，在透過藍牙發送到耳機的瞬間，手機依然必須將其重新壓縮成有損的 AAC 訊號。
* **例外與特殊支援情境**：
  * **有線例外（AirPods Max USB-C 版）**：在更新至最新韌體後，使用官方 **USB-C 對 USB-C 連接線**以有線方式連接 iPhone/iPad/Mac，即可實現真正的有線無損播放。
  * **無線例外（Apple Vision Pro 專有通訊協定）**：搭配 AirPods 4（或更新版本）、AirPods Pro 2（USB-C 版）或 Powerbeats Pro 2 時，能透過 Vision Pro 獨家研發的超低延遲專有無線音訊協定實現無線無損聆聽（非走常規標準藍牙）。

### 2. iPhone 與 iPad 的播放條件
* **標準無損（最高至 48 kHz）**：
  * 使用內建揚聲器，或透過有線耳機（如 3.5mm 或 Lightning/USB-C 轉接線）連接耳機或主動式喇叭。
* **高解析無損（Hi-Res Lossless，高於 48 kHz）**：
  * **必須外接數位類比轉換器（External DAC）**。iPhone 與 iPad 內部硬體無法原生輸出高於 48 kHz 的音訊訊號，需依賴外接 DAC 處理。
  * > [!NOTE] [補充說明 / 待進一步文件確認]
    > 關於 Apple Music 高解析無損的具體上限（坊間常稱最高支援至 24-bit / 192 kHz，iZotope 文章亦提及串流平台最高支援至 192 kHz），在目前的 Apple 官方說明文件（raw/05）中，僅具體載明「高於 48 kHz 的歌曲」與「Hi-Res Lossless」，並未直接列出明確的 24-bit/192 kHz 數值，此處忠實依官方文本標註。

### 3. Mac 電腦的播放條件
* **內建支援**：
  * 14 吋與 16 吋 MacBook Pro 原生支援高達 **96 kHz** 取樣率的耳機孔輸出。
* **其餘 Mac 機型**：
  * 若要播放高於 48 kHz 的高解析無損音訊，同樣必須外接 DAC。

### 4. Apple TV 4K、HomePod 與其他平台
* **Apple TV 4K**：必須透過 HDMI 連接線接駁至家庭劇院 AV 擴大機。此外，「高解析度無損（Hi-Res Lossless）」僅在 **Apple TV 4K（第 3 代或後續機型）** 提供。
* **HomePod / HomePod mini**：可於「家庭」App 的設定中開啟無損串流播放。
* **Windows PC 與 Android 裝置**：安裝 Apple Music App 後，以有線耳機連接即可播放無損；若欲播放高於 48 kHz 音訊，同樣需視電腦音效卡或手機硬體搭配外接 DAC。

## 生活類比
> [!NOTE] [補充說明] 生活類比
> 藍牙耳機聽無損，就像「**高山純淨山泉水遇到了裝有濾網的水龍頭**」：水庫（Apple Music 雲端伺服器）流出的水質毫無疑問是頂級純淨的 ALAC 無損原水，但在流進水龍頭接上藍牙耳機時，受限於藍牙水管的管徑容量，強制通過了細密濾網（AAC 有損編碼壓縮），最終倒進杯子（耳朵聽到）的水雖然依舊甘甜可口，但已不再是未經修飾的原裝山泉水。要喝到真正無損，必須接上寬口金屬硬水管（有線連接）。

## 實務應用與設定指南
* **如何開啟無損設定**：
  * **iOS / iPadOS**：進入「設定」$\to$「App」$\to$「音樂」$\to$「音質」，開啟「無損音訊」，並可針對行動網路、Wi-Fi 串流與下載分別指定品質。
  * **macOS**：開啟音樂 App $\to$「設定」$\to$「播放」標籤頁，勾選「無損音訊」。
* **流量與儲存空間警告**：
  * 官方明確提醒：串流無損音訊將**大幅增加行動網路流量消耗**；下載無損或高解析音訊更會**快速佔滿手機儲存容量**。若平時僅使用一般藍牙耳機通勤，建議串流設定維持「高品質（256 kbps AAC）」即可，既省流量又省空間。

## 關聯條目
* [ALAC 格式專頁](../formats/alac.md) - 解析 Apple Music 核心採用的 Apple 無損格式規格
* [AAC 格式專頁](../formats/aac.md) - 解密 AirPods 與 Apple 藍牙設備為何預設使用 AAC
* [橫向對比：有損壓縮 vs 無損壓縮](./lossy-vs-lossless.md) - 比較不同壓縮格式在檔案流量與音質還原上的差異
* [常見迷思：取樣率與位元深度越高越好嗎？](../myths/higher-sample-rate-and-bit-depth.md) - 探討 24/192 高解析音質在實際聆聽中的心理與物理盲點

## 原始來源
* **文章標題**：[About lossless audio in Apple Music](https://support.apple.com/en-us/118295)
  * **原始檔案**：`raw/05-apple-lossless-audio.md`
  * **對應章節/段落**：章節「What you need to know about lossless in Apple Music」、「About lossless audio with Apple and Beats headphones」、「How to listen to lossless on your iPhone or iPad」、「How to listen to lossless on your Mac」
* **文章標題**：[Web audio codec guide](https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Formats/Audio_codecs)
  * **原始檔案**：`raw/03-mdn-audio-codecs.md`
  * **對應章節/段落**：章節「ALAC (Apple Lossless Audio Codec)」、「AAC (Advanced Audio Coding)」
