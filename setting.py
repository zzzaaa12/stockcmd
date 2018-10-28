# -*- coding: utf-8 -*-

# taiwan stock setting
USER_STOCK_LIST = ['2330','2317','3008','6142','00664R','00632R']
TWSE_SERVER = 'http://220.229.103.179' # mis.twse.com.tw
TW_FUTURE_URL = 'http://60.250.19.181/Future/FusaQuote_Norl.aspx' # info512.taifex.com.tw


# world index setting
WORLD_INDEX_URL = 'https://www.wantgoo.com/global/api/getglobaldefault'

INDEX_LIST = [ \
              ['0000',      'TWSE',      '加權指數'], \
              ['WTXM',      'WTX',       '台指期全'], \
              ['USDTWD',    'TWD',       '台幣匯率'], \
              ['USDINDEX',  'DXY',       '美元指數'], \
              ['B1YM',      'DOWF',      '小道瓊期'], \
              ['NKI',       'JAPAN',     '日經指數'], \
              ['KOR',       'KOREA',     '韓國指數'], \
              ['A50F',      'A50',       'A50期貨 '], \
              ['VIX',       'VIX',       'SP500VIX'], \
              ['VIXTWN',    'TW-VIX',    '台指VIX '], \
              ['WGD',       'Gold',      '黃金期貨'], \
              ['OIL',       'Oil',       '紐約原油'], \
#              ['NAS',       'NASDAQ',    '那斯達克'], \
#              ['SPS',       'S&P500',    'S&P 500 '], \
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
