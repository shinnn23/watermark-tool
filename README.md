# 🌊 極速批量圖片浮水印工具 | Batch Image Watermarker

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://watermark-tool-iynuk47b5nuq8anatqzens.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **最強大的免費線上圖片處理工具！一鍵為 100+ 張圖片添加浮水印，支援自定義字體、全版鋪滿防盜模式。**
> *The most powerful free online batch watermarking tool. Secure, fast, and no installation required.*

## 🚀 線上試用 (Live Demo)

👉 **[點擊這裡立即使用 (Click Here to Start)](https://watermark-tool-iynuk47b5nuq8anatqzens.streamlit.app/)**

---

## ✨ 核心功能 (Key Features)

這款工具是為了電商賣家、攝影師、社群小編量身打造的，解決「一張張修圖」的痛苦：

* **⚡ 極速批量處理**：同時上傳 50+ 張圖片，秒速處理並打包 ZIP 下載。
* **🔒 隱私安全第一**：基於 Streamlit 運行，圖片處理完即焚，不會永久儲存在伺服器。
* **🛡️ 全版防盜模式 (Tiled Mode)**：支援浮水印「鋪滿整張圖」，透明度可調，有效防止盜圖。
* **🎨 豐富字體庫**：
    * 內建 **Google Noto Sans (思源黑體)**、**Noto Serif (思源宋體)**。
    * 支援英文時尚字體 **Montserrat**、**Playfair Display**。
    * 支援手寫簽名風格 **Dancing Script**、**Great Vibes**。
* **🎛️ 高度客製化**：可調整旋轉角度、透明度 (Opacity)、字體大小、顏色與間距。

---

## 🛠️ 技術棧 (Tech Stack)

本專案適合 Python 初學者參考，使用了以下技術：

* **[Streamlit](https://streamlit.io/)** - 快速構建 Data Apps 的最強框架。
* **[Pillow (PIL)](https://python-pillow.org/)** - 強大的 Python 圖像處理庫。
* **Python 3.9+** - 核心語言。

---

## 💻 如何在本地運行 (How to Run Locally)

如果您是開發者，想要在自己的電腦上運行或修改此專案：

1. **克隆專案 (Clone Repo)**
   
   ```bash
   git clone https://github.com/shinnn23/watermark-tool
   cd watermark-tool
   pip install -r requirements.txt
   streamlit run app.py
   ```

---

## 📂 專案結構 (Project Structure)

```text
watermark-tool/
├── app.py              # 主程式邏輯 (Main Logic)
├── requirements.txt    # 套件依賴清單
├── fonts/              # 字體資源庫 (Font Assets)
│   ├── NotoSansTC-Regular.ttf
│   ├── Montserrat-Bold.ttf
│   └── ...
└── README.md           # 專案說明文件
```

---

## 📝 授權 (License)

```text
本專案採用 MIT License 開源授權，您可以免費使用、修改或用於商業用途。
Made with ❤️ by Astrid | 讓工作自動化，把時間留給生活。
```
