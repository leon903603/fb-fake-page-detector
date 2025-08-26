# 假粉專偵測系統 Fake Facebook Page Detector

自動化系統，用於偵測與追蹤假冒 Facebook 粉絲專頁，特別著重於 **廣告行為分析**，因為投放廣告的粉專大概率與詐騙相關，可作為檢舉依據。  
Automated system to detect and track fake Facebook pages, focusing on advertisement activity analysis as a strong indicator of potential fraud.  

---

## 📌 功能 Features
- 🔍 關鍵字搜尋並爬取粉專資訊  
  Scrapes Facebook fan pages by keyword search.  
- 🖼️ 收集粉專基本資料（名稱、ID、網址）  
  Collects page metadata (name, ID, URL, profile picture).  
- 📢 偵測並追蹤粉專廣告活動，作為詐騙判斷依據  
  Tracks and analyzes ad activity as a fraud indicator.  
- 📊 將結果輸出為 Excel 供進一步調查  
  Exports results into Excel for further investigation.  

---

## 📂 專案結構 Project Structure
```
project_root/
│── main.py # 主程式入口 / Main controller
│── config.py # 設定檔 / Configuration file
│── facebook_scraper.py # Facebook 爬蟲模組 / Facebook crawler module
│── excel_utils.py # Excel 匯出工具 / Excel export utilities
│── fb_pages.xlsx # 結果輸出 / Output result file
└── README.md # 專案說明文件 / Project documentation
```
---

## 🚀 快速開始 Getting Started
### 1. 複製專案 Clone the Repository
```bash
git clone https://github.com/yourusername/fake-fb-detector.git
cd fake-fb-detector
2. 安裝套件 Install Requirements
bash
pip install -r requirements.txt
3. 執行程式 Run the Program
bash
python main.py
📊 輸出範例 Output Example
結果將存成 fb_pages.xlsx，包含：
Results will be saved to fb_pages.xlsx, including:

偵測日期 Detection Date

粉專名稱 Page Name

粉專 ID Page ID

網站網域 Website Domain

廣告活動狀態 Ad Activity Status

是否下架 Removal Status
