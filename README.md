stockcmd
===================

本專案由 Python 撰寫，主要功能如下：  
1. 在 terminal 上顯示台指數 & 報價  
2. 在 terminal 上顯示國際指數報價  
3. 可自己定義所需要的項目  
4. 可依據漲跌狀態標記顏色  

---------
**檔案說明：**  
 - stockcmd.py：主程式  
 - otc.csv & tse.csv：台股上市&上櫃股票清單  
 
**格式：**  

    stockcmd.py [Options] [Stock_No]

**參數：**  

    -a: 列出所有資訊 (國際股市、台灣上市櫃指數、個股報價)
    -s: 列出簡易資訊 (代號、點數、漲跌、百分比)
    -i: 增加上市&上櫃指數的報價
    -w: 顯示國際股市行情
    -q: 只顯示存在 List 中的股票清單 (不需輸入股號)
    -c: 顯示彩色畫面
    -d: 持續顯示 (每20秒更新一次資訊)
    -h: 顯示說明頁面

**自訂預設值：**  
使用者可直接修改下列在 stockcmd.py 的預設參數，在查詢時省略上面的參數  
1. SIMPLE_OUTPUT - 預設為簡易模式 (只有股號、股價、漲跌、百分比)  
2. COLORFUL_OUTPUT - 預設輸出彩色文字  
3. SHOW_TWSE_INDEX - 加入上市上櫃指數  
4. SHOW_WORLD_INDEX - 加入國外指數  
5. ADD_USER_STOCK_LIST - 加入使用者自定義股票  
  
**使用範例：**  

1. 自選股報價  
![Alt text](/screenshot/1.png "Snapshot")  

2. 自選股 + 上市上櫃指數  
![Alt text](/screenshot/2.png "Snapshot")  

3. 自選股 (簡易模式)  
![Alt text](/screenshot/3.png "Snapshot")  

4. 國際指數  
![Alt text](/screenshot/4.png "Snapshot")  

5. 列出所有資訊 (股票清單、上市上櫃、國際股市)  
![Alt text](/screenshot/5.png "Snapshot")  

**規劃中功能：**  
- 自訂股票清單 - 已完成  
- 顯色彩色文字 - 已完成  
- 增加國際指數時間 - 已完成  
- 國際指數的時區轉換 - 已完成 (但沒有日光節約時間)  
- 加入台指期資訊
