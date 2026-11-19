# 位元深度（Bit Depth）

> **一句話白話結論**：位元深度代表電腦測量聲音強弱（振幅）時所使用的精細位元數，它決定了系統的「底噪有多低」以及「動態範圍有多大」。

## 概念說明
當類比聲波被轉換成數位訊號時，系統除了要決定每秒取樣幾次（取樣率），還必須量測每一次取樣時聲波的電壓強度（振幅，Amplitude）。然而，電腦無法儲存無限連續的小數，因此必須將電壓數值四捨五入到最近的離散階梯數值，這個過程稱為「量化（Quantization）」。

用來記錄每個取樣點數值的二進位位元數，就稱為「位元深度（Bit Depth）」，有時也被稱為字長（Word Length）或解析度（Resolution）。位元深度越高，能表示的階梯數目呈指數成長，可記錄的音量強弱對比（動態範圍）就越寬廣，背景底噪就越微弱。

## 重點整理
* **音量測量的刻度精細度（階梯數）**：
  * 電腦以二進位儲存資料，每增加 1 個位元，可表達的振幅階梯數就呈倍數翻倍（$2^X$）。
  * **16-bit**：擁有 65,536 個音量階梯。
  * **24-bit**：高達 1,677 萬個音量階梯（精細度是 16-bit 的 256 倍）。
* **動態範圍與底噪（每增加 1 位元約拓展 6 dB）**：
  * **動態範圍（Dynamic Range）**：指系統能記錄的「最大音量」與「最小背景雜音（底噪）」之間的落差。
  * **16-bit**：提供約 96 dB 的動態範圍（底噪極微弱，約 -96 dBFS）。
  * **24-bit**：提供約 144 dB 的動態範圍（底噪降至約 -144 dBFS，幾乎是物理測量極限）。
* **量化誤差與抖動技術（Dither）**：
  * 將連續音量四捨五入成整數時產生的微小偏差稱為「量化誤差」。
  * 在音訊領域中，工程師會刻意加入極微弱的隨機雜訊（稱為「抖動，Dither」），巧妙破除數位顆粒感，將其轉化為均勻平順、人耳難以察覺的平穩底噪。
* **定點數 vs. 浮點數（32-bit Float）**：
  * 播放檔案多採用 16-bit 或 24-bit 定點數。
  * 專業音訊編輯軟體（DAW）內部運算廣泛採用 **32-bit 浮點數**，擁有超過 1,500 dB 的超大動態範圍，讓音樂人在後製混音時即便瞬間音量過大爆表，也不會直接產生破音（Clipping）。

## 生活類比
> [!NOTE] [補充說明] 生活類比
> 可以將位元深度想像成一把「尺的刻度精細度」：16-bit 的尺刻度已經細如毫釐，而 24-bit 的刻度更達到奈米級。刻度越細，測量聲音高低起伏時就不需要大幅四捨五入，背景雜音（測量誤差）就越小。

## 實務應用與選擇建議
* **最終聆聽與發行（CD / 串流播放）**：
  * **16-bit**：對於一般消費者在居家或耳機聆聽環境，96 dB 的動態範圍已遠超過環境底噪與人耳正常忍受範圍，完全足以提供乾淨無噪的音樂體驗。
* **錄音與音樂製作階段**：
  * **24-bit**：錄音時強烈建議採用 24-bit。因為底噪極低（-144 dB），錄音師可以故意保留充裕的安全空間（稱為動態餘裕，Headroom），避免瞬間大動態造成破音（Clipping），後續混音調整彈性極大。
  * **32-bit Float**：在軟體內部匯出分軌（Stems）、中間混音檔時非常適合，避免任何處理過程中的數位削波與多次抖動損失。

## 常見迷思與 FAQ
* **Q：位元深度較低時，波形會像階梯一樣鋸齒狀不滑順嗎？**
  * A：不會。鋸齒階梯只是圖解量化概念時的視覺簡化。在實際數位音訊中，配合抖動（Dither）與 DAC 濾波重組，輸出的是平滑連續的波形，位元深度影響的是「底噪的音量大小」，而不是波形邊緣是否鋸齒。

## 關聯條目
* [取樣率（Sampling Rate）](./sample-rate.md) - 取樣率決定頻率上限，位元深度決定動態範圍與底噪
* [位元率（Bitrate）與檔案大小](./bitrate.md) - 位元深度直接影響未壓縮音訊的資料傳輸率
* [常見迷思：取樣率與位元深度越高越好嗎？](../myths/higher-sample-rate-and-bit-depth.md) - 深入探討人耳是否能分辨 16-bit 與 24-bit

## 原始來源
* **文章標題**：[Digital audio basics: audio sample rate and bit depth](https://www.izotope.com/community/blog/digital-audio-basics-sample-rate-and-bit-depth)
  * **原始檔案**：`raw/01-izotope-digital-audio-basics.md`
  * **對應章節/段落**：章節「What is bit depth in audio?」、「Can you hear the difference between audio bit depths?」、「What should my sample rate and bit depth be?」
* **文章標題**：[Digital audio concepts](https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Formats/Audio_concepts)
  * **原始檔案**：`raw/02-mdn-digital-audio-concepts.md`
  * **對應章節/段落**：章節「Sampling audio (Resolution)」、「Samples」
