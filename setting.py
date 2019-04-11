# -*- coding: utf-8 -*-

# taiwan stock setting
USER_STOCK_LIST = ['2330','2317','3008','6142','00632R','00664R','00659R', '00677U','00662', '2441']
TWSE_SERVER = 'http://220.229.103.179' # mis.twse.com.tw
TW_FUTURE_URL = 'http://info512.taifex.com.tw/Future/FusaQuote_Norl.aspx' # info512.taifex.com.tw


# world index setting
WORLD_INDEX_URL = 'https://www.wantgoo.com/global/api/getglobaldefault'

INDEX_LIST = [ \
              ['0000',      'TWSE',      '加權指數'], \
              ['WTXM',      'WTX-All',   '台指期全'], \
              ['USDTWD',    'TWD',       '台幣匯率'], \
              ['B1YM',      'DOW-F',     '小道瓊期'], \
              ['M1NQ',      'NAS-F',     'NASDAQ期'], \
              ['NKI',       'JAPAN',     '日經指數'], \
              ['KOR',       'KOREA',     '韓國指數'], \
              ['SHI',       'SHI',       '上證指數'], \
              ['A50F',      'A50',       'A50期貨 '], \
              ['HSI',       'HSI',       '恆生指數'], \
              ['VIX',       'VIX',       'SP500VIX'], \
              ['DAX',       'DAX',       '德國指數'], \
              ['USDINDEX',  'DXY',       '美元指數'], \
              ['US10-YR',   'US10-YR',   '十年美債'], \
              ['GOLD',      'Gold',      '黃金現貨'], \
              ['OIL',       'Oil',       '紐約原油'], \
              ['bitcoin',   'BTC',       '比特幣  '], \
              ['ethereum',  'ETH',       '以太幣  '], \
#              ['NAS',       'NASDAQ',    '那斯達克'], \
#              ['SPS',       'S&P500',    'S&P 500 '], \
            ]

# global setting
AUTO_UPDATE_SECOND = 20

DEFAULT_PROFILE = {
    'color_print'         : False,
    'show_tw_stock'       : False,
    'show_twse_index'     : False,
    'show_world_index'    : False,
    'show_simple'         : False,
    'monitor_mode'        : False,
    'monitor_help'        : True,
    'hide_closed_index'   : False,
    'refresh_now'         : False,
    'append_stock': '',
    'remove_stock': ''
}
