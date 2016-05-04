stockcmd
===================

本專案由 Python 撰寫，提供一個快速在 terminal 上取得台股報價的功能！

---------
**格式：**  

    stockcmd.py [Options] [Stock_No]

**參數：**  

    -a: 列出所有資訊 (國外股市、台灣上市櫃指數、個股報價)
    -i: 增加上市&上櫃指數的報價
    -w: 顯示國外股市行情
    -q: 只顯示存在 List 中的股票清單 (不需輸入股號)
    -h: 顯示說明頁面

**使用範例：** 

    $ ./stockcmd.py -a 2330 2317 3008
    股號    股名     成交價   漲跌    百分比  成交量   資料時間
    t00     上市    8294.12 -83.78  -1.00%  78227   13:33:00
    o00     上櫃    124.01  -0.73   -0.59%  16525   13:33:00
    2330    台積電  147.50  -2.5    -1.67%  68550   13:30:00
    2317    鴻海    75.60   -1.5    -1.95%  31299   13:30:00
    3008    大立光  2295.00 +25.0   +1.10%  888     13:30:00

    $ ./stockcmd.py 2330 2317 3008
    股號    股名     成交價   漲跌    百分比  成交量   資料時間
    2330    台積電  147.50  -2.5    -1.67%  68550   13:30:00
    2317    鴻海    75.60   -1.5    -1.95%  31299   13:30:00
    3008    大立光  2295.00 +25.0   +1.10%  888     13:30:00

    $ ./stockcmd.py -w
    指數            點數            漲跌            百分比
    TAIEX           8,294.12        -83.78          -1.00%
    DOW             17,891.16       +117.52         0.66%
    NASDAQ          4,817.59        +42.24          0.88%
    DAX             9,934.56        -188.71         -1.86%
    NI225           16,147.38       -518.67         -3.11%
    KOSPI           1,986.41        +8.26           0.42%
    SHCOMP          2,992.64        +54.32          1.85%
    HK             20,676.94       -390.11         -1.85%

**即將新增功能：**  
- 自訂股票清單(OK)  
- 顯色彩色文字  
