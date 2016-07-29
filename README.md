stockcmd
===================

本專案由 Python 撰寫，主要功能如下：  
1. 在 terminal 上顯示台指期、大盤指數 & 報價  
2. 在 terminal 上顯示國際指數報價  
3. 可自己定義所需要的項目  
4. 可依據漲跌狀態標記顏色  
5. 支援即時監控：自動更新(預設為20秒)、可隨時切換顯示內容  
6. 簡易動態：漲停、跌停、最高價、最低價等狀態會顯示在最右邊

---------
**檔案說明：**  
 - stockcmd.py：主程式  
 - taiwan_stock.py：處理台股&台指期的code  
 - world_index.py：處理國際指數code  
 - setting.py：設定檔  
 
**格式：**  

    stockcmd.py [Options] [Stock_No]

**參數：**  

    -a: 列出所有資訊 (國際股市、台灣上市櫃指數、個股報價)
    -s: 列出簡易資訊 (代號、點數、漲跌、百分比)
    -i: 增加上市&上櫃指數的報價
    -w: 顯示國際股市行情
    -u: 只顯示存在 List 中的股票清單 (不需輸入股號)
    -c: 顯示彩色畫面
    -d: 監控模式 (每20秒更新一次資訊)
    -h: 顯示說明頁面

**自訂預設值：**  

使用者可直接修改下列在 setting.py 的預設參數，在查詢時省略上面的參數  
1. USER_STOCK_LIST：台股股號清單  
2. INDEX_LIST：國際股市清單  
3. AUTO_UPDATE_SECOND：monitor mode 的更新秒數  
4. DEFAULT_PROFILE：自訂預設值  
 - color_print：彩色顯示  
 - show_twse_index：顯示台指期&上市上櫃指數  
 - show_world_index：顯示國際指數  
 - show_user_list：顯示使用者定義在USER_STOCK_LIST的股票
 - show_simple：顯示簡易格式 (只有股號、成交價、漲跌、百分比)

  
**使用範例：**  

1. 自選股報價  
![Alt text](/screenshot/1.png "Snapshot")  

2. 自選股 + 上市上櫃指數  
![Alt text](/screenshot/2.png "Snapshot")  

3. 簡易模式  
![Alt text](/screenshot/3.png "Snapshot")  

4. 國際指數  
![Alt text](/screenshot/4.png "Snapshot")  

5. 列出所有資訊 (上市上櫃、國際股市、自訂清單)  
![Alt text](/screenshot/5.png "Snapshot")  

**規劃中功能：**  
- 自訂股票清單 - 已完成  
- 顯色彩色文字 - 已完成  
- 增加國際指數時間 - 已完成  
- 國際指數的時區轉換 - 已完成  
- 加入台指期資訊 - 已完成  
- 監控模式中更改顯示內容 - 已完成  
- 以OOP的方式改寫程式 - 已完成
