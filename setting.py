# -*- coding: utf-8 -*-

# taiwan stock setting
USER_STOCK_LIST = ['2330','2317','3008','6142','00664R','00632R']
TWSE_SERVER = 'http://220.229.103.179' # mis.twse.com.tw
TW_FUTURE_URL = 'http://info512.taifex.com.tw/Future/FusaQuote_Norl.aspx'


# world index setting
INDEX_LIST = [
    ['TPE:TAIEX'        , 'TAIEX' , '加權指數'],
    ['INDEXDJX:.DJI'    , 'DOW'   , '道瓊指數'],
    ['INDEXNASDAQ:.IXIC', 'NASDAQ', '那斯達克'],
    ['INDEXNASDAQ:SOX'  , 'PHLX'  , '費半PHLX'],
    ['INDEXDB:DAX'      , 'DAX'   , '德國DAX'],
    ['INDEXFTSE:UKX'    , 'FTSE'  , '英國FTSE'],
    ['INDEXEURO:PX1'    , 'CAC40' , '法國指數'],
    ['INDEXNIKKEI:NI225', 'N225'  , '日本指數'],
    ['KRX:KOSPI'        , 'KOSPI' , '韓國指數'],
    ['SHA:000001'       , 'SHCOMP', '上證指數'],
    ['INDEXHANGSENG:HSI', 'HK'    , '香港恆生']
]


# global setting
AUTO_UPDATE_SECOND = 20

DEFAULT_PROFILE = {
    'color_print'         : False,
    'show_twse_index'     : False,
    'show_world_index'    : False,
    'show_simple'         : False,
    'monitor_mode'        : False,
    'monitor_help'        : True,
    'hide_closed_index'   : False,
    'append_stock': '',
    'remove_stock': ''
}
