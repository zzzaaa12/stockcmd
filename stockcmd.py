#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import csv
import json
import requests
import re
import time
import os
import urllib
from datetime import datetime
from datetime import timedelta
from HTMLParser import HTMLParser

# User Setting1: Default output format
SIMPLE_OUTPUT = False
COLORFUL_OUTPUT = False
SHOW_TWSE_INDEX = False
SHOW_WORLD_INDEX = False
ADD_USER_STOCK_LIST = False
AUTO_UPDATE_SECOND = 20

# User Setting2: Stock list and file path
TW_STOCK_LIST = ['2330', '2317', '3008', '00631L', '00632R']
TSE_FILE = 'tse.csv'
OTC_FILE = 'otc.csv'

# Server Setting:
TWSE_SERVER = '220.229.103.179'
TWSE_URL = 'http://' + TWSE_SERVER + '/stock/api/getStockInfo.jsp?ex_ch='
GOOGLE_URL = 'http://www.google.com/finance/info?q='
INDEX_LIST = [['TPE:TAIEX'        , 'TAIEX' , +8, '加權指數'], # Format: google finance id, nickname, timezone, name
              ['INDEXDJX:.DJI'    , 'DOW'   , -4, '道瓊指數'], # FIXME: Daylight saving time
              ['INDEXNASDAQ:.IXIC', 'NASDAQ', -4, '那斯達克'],
              ['INDEXNASDAQ:SOX'  , 'PHLX'  , -4, '費半PHLX'],
              ['INDEXDB:DAX'      , 'DAX'   , +2, '德國DAX'],
              ['INDEXFTSE:UKX'    , 'FTSE'  , +1, '英國FTSE'],
              ['INDEXNIKKEI:NI225', 'N225'  , +9, '日本指數'],
              ['KRX:KOSPI'        , 'KOSPI' , +9, '韓國指數'],
              ['SHA:000001'       , 'SHCOMP', +8, '上證指數'],
              ['INDEXHANGSENG:HSI', 'HK'    , +8, '香港恆生']]

# ALL_RESULT includes all result data we need: [id, name, price, changes, percent, volume, time, type]
#   ex: ['00632R', 'T50反1', '19.75', '-0.15', '-0.75%', '88403', '13:30:00 (05/20)']
ALL_RESULT  = []

# Color Setting
color_print = False
RED = '\033[1;31;40m'
GREEN = '\033[1;32;40m'
YELLOW = '\033[1;33;40m'
WHITE = '\033[1;37;40m'
COLOR_END = '\033[0m'


def usage():
    print 'stockcmd - get stock information for TWSE'
    print ''
    print 'Usage:'
    print '    stockcmd.py [Options] [stock numbers]'
    print ''
    print 'Options:'
    print '    -a: list all stock infomation (include TSE, OTC, other stock)'
    print '    -s: list information with simple format'
    print '    -i: list include TSE index and OTC index'
    print '    -w: list International Stock Indexes'
    print '    -q: list the stocks predefined'
    print '    -c: list with color'
    print '    -d: continue update information every 20 seconds'
    print '    -h: show this page'
    print ''
    print 'Example:'
    print '    stockcmd.py -i'
    print '    stockcmd.py -w'
    print '    stockcmd.py -q'
    print '    stockcmd.py 2330 2317 3008'
    print ''


class future_parser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.data = []
        self.item_limit = 15
        self.item_index = 0
    def handle_starttag(self, tag, attrs):
        if tag == 'td':
            for attr in attrs:
                if attr[1] == 'bu13':
                    self.item_index = self.item_index + 1
                    break
    def handle_data(self, data):
        if self.item_index == 3 or self.item_index == 4:
            if self.item_limit and len(data) < 14:
                self.item_limit = self.item_limit - 1
                self.data.append(data)


def search_stock(stock_no, filename):
    ret = False

    f = open(filename,'r')
    for row in csv.reader(f):
        if row[0] == str(stock_no):
            ret = True
            break
    f.close()
    return ret


def remove_special_char(string):
    return re.sub(r'[^\x00-\x7F]','', string)


def print_result(show_simple, auto_update):

    if auto_update:
        os.system('clear || cls')

    for i in range(len(ALL_RESULT)):
        type = ALL_RESULT[i][6]
        last_type = ALL_RESULT[i-1][6]

        title_color = ''
        item_color = ''
        color_end = ''

        if color_print:
            title_color = YELLOW
            color_end = COLOR_END
            change = ALL_RESULT[i][3]
            if float(change) > 0:
                item_color = RED
            elif float(change) < 0:
                item_color = GREEN
            else:
                item_color = WHITE

        if show_simple:
            print item_color + ' ' + \
                  '{0:s}\t  '.format(ALL_RESULT[i][0]) + \
                  '{0:>9s}'.format(ALL_RESULT[i][2]) + \
                  '{0:>9s}   {1:s}%'.format(ALL_RESULT[i][3], ALL_RESULT[i][4]) + color_end

        elif type == 'index':
            if i == 0:
                print '\n' + title_color + ' 代號      指數          點數         漲跌     百分比         資料時間' + color_end
                print '-----------------------------------------------------------------------'

            # print all data
            print item_color + ' ' + \
                  '{0:8s}'.format(ALL_RESULT[i][0]) + \
                  '{0:<10s}'.format(ALL_RESULT[i][1]) + \
                  '{0:>14s}'.format(ALL_RESULT[i][2]) + ' ' + \
                  '{0:>10s}'.format(ALL_RESULT[i][3]) + ' ' + \
                  '{0:>9s}%'.format(ALL_RESULT[i][4]) + ' ' + \
                  '{0:>20s}'.format(ALL_RESULT[i][7]) + color_end

        elif type == 'stock':
            if (i == 0 or last_type != 'stock'):
                print '\n' + title_color + ' 股號     股名     成交價     漲跌    百分比   成交量         資料時間' + color_end
                print '-------------------------------------------------------------------------'

            # print all data
            print item_color + ' ' + \
                  '{0:s}'.format(ALL_RESULT[i][0]) + '\t ' + \
                  ALL_RESULT[i][1] + '\t' + \
                  '{0:>9s}'.format(ALL_RESULT[i][2]) + ' ' + \
                  '{0:>8s}'.format(ALL_RESULT[i][3]) + ' ' + \
                  '{0:>8s}%'.format(ALL_RESULT[i][4]) + ' ' + \
                  '{0:>8s}'.format(ALL_RESULT[i][5]) + ' ' + \
                  '{0:>20s}'.format(ALL_RESULT[i][7]) + color_end

    if show_simple == False:
        print datetime.now().strftime('\nLast updated: %Y.%m.%d %H:%M:%S\n')


def get_tw_future():
    sign = ''
    future = future_parser()
    future.feed(urllib.urlopen("http://info512.taifex.com.tw/Future/FusaQuote_Norl.aspx").read())
    future.close()

    change = float(future.data[7])
    if change > 0:
        sign = '+'
    elif change < 0:
        sign = '-'

    result = []
    result.append("WTX")
    result.append("台指期")
    result.append(future.data[6].replace(',',''))
    result.append(sign + future.data[7])
    result.append(sign + future.data[8])
    result.append(future.data[9].replace(',',''))
    result.append("stock")

    if (future.data[1] == '收盤'):
        result.append(future.data[14] + ' (close)')
    else:
        result.append(future.data[14] + '        ')

    ALL_RESULT.append(result)


def add_result_to_list(json_str, stock_type):
    # read json data
    json_data = json.loads(json_str)
    now = datetime.now()

    if stock_type == 'world':
        for i in range(len(INDEX_LIST)):
            result = []
            j = json_data[i]
            id = INDEX_LIST[i][1]

            ratio = j["cp"]
            if ratio.find('-'):
                ratio = '+' + ratio

            timezone = int(INDEX_LIST[i][2])
            result_time = datetime.strptime(j["lt_dts"], '%Y-%m-%dT%H:%M:%SZ') + timedelta(hours = 8-timezone)

            if (now-result_time).total_seconds() < 1800:
                time_str = str(result_time.strftime('%H:%M:%S        '))
            elif now.month == result_time.month and now.day == result_time.day:
                time_str = str(result_time.strftime('%H:%M:%S (today)'))
            else:
                time_str = str(result_time.strftime('%H:%M:%S (%m/%d)'))

            result.append(id)
            result.append(INDEX_LIST[i][3])
            result.append(j["l"])
            result.append(j["c"])
            result.append(ratio)
            result.append(' ')
            result.append("index")
            result.append(time_str)
            ALL_RESULT.append(result)

    elif stock_type == 'tw':
        for i in range(len(json_data['msgArray'])):
            result = []
            j = json_data['msgArray'][i]
            diff = float(j["z"]) - float(j["y"])

            if diff > 0:
                sign = '+'
            elif diff < 0:
                sign = ''
            else:
                sign = ' '

            change_str = sign + str(diff)
            change_str_p = sign + '{0:.2f}'.format(diff / float(j["y"]) *100)

            stock_no = j["c"]
            name = j["n"]

            # fix too long name.....
            if stock_no == 't00':
                name = u'上市'
            elif stock_no == 'o00':
                name = u'上櫃'

            date = datetime.strptime(j["d"], '%Y%m%d')

            result_time_str = j["d"] + ' ' + j["t"]
            result_time = datetime.strptime(result_time_str, '%Y%m%d %H:%M:%S')

            if (now-result_time).total_seconds() < 300:
                time_str = j["t"] + '        '
            elif now.month == date.month and now.day == date.day:
                time_str = j["t"] + ' (today)'
            else:
                time_str = j["t"] + date.strftime(' (%m/%d)')

            result.append(stock_no)
            result.append(name)
            result.append(j["z"])
            result.append(change_str)
            result.append(change_str_p)
            result.append(j["v"])
            result.append("stock")
            result.append(time_str)
            ALL_RESULT.append(result)


def create_tw_stock_url(add_twse, add_stock_list, argv):
    url = TWSE_URL
    if add_twse:
        url = url + 'tse_t00.tw|otc_o00.tw|'

    # add user predefined stock list
    # search_stock() is use to determine stock is in tse or otc
    if add_stock_list:
        for i in TW_STOCK_LIST:
            if search_stock(str(i), OTC_FILE):
                url = url + 'otc_' + str(i) + '.tw|'
            elif search_stock(str(i), TSE_FILE):
                url = url + 'tse_' + str(i) + '.tw|'

    # search stock number from input
    for i in argv:
        if search_stock(str(i), OTC_FILE):
            url = url + 'otc_' + str(i) + '.tw|'
        elif search_stock(str(i), TSE_FILE):
            url = url + 'tse_' + str(i) + '.tw|'

    return url;


def create_world_index_url():
    url = GOOGLE_URL
    for item in INDEX_LIST:
        url = url + item[0] + ','

    return url


# query world index:
def get_world_index_info(url):
    result = requests.get(url)
    json_str = remove_special_char(result.content.replace('// ', '', 1))
    add_result_to_list(json_str, 'world')


# query taiwan stock:
def get_tw_stock_info(url):
    #   access the index first and then send request for stock list
    r = requests.session()
    r.get('http://' + TWSE_SERVER + '/stock/index.jsp', headers = {'Accept-Language':'zh-TW'}, timeout=2)
    result = r.get(url)

    json_str = result.content
    add_result_to_list(json_str, 'tw')


def main():
    argv = sys.argv
    count = 0
    add_world = False
    add_twse = False
    add_stock_list = False
    show_simple = False
    auto_update = False
    global color_print

    if len(argv) == 1 and \
       SHOW_TWSE_INDEX == False and \
       SHOW_WORLD_INDEX == False and \
       ADD_USER_STOCK_LIST == False:
        # no parameter, show usage()
        usage()
        exit()

    # remote program name
    del argv[0]

    # read parameters
    for x in argv:
        if str(x) == '-c':
            color_print = True
        elif str(x) == '-a':
            add_world = True
            add_twse = True
            add_stock_list = True
        elif str(x) == '-w':
            add_world = True
        elif str(x) == '-i':
            add_twse = True
        elif str(x) == '-q':
            add_stock_list = True
        elif str(x) == '-s':
            show_simple = True
            add_stock_list = True
        elif str(x) == '-d':
            auto_update = True
        elif str(x) == '-h' or str(x) == '--help':
            usage()
            exit()

    # load default setting
    if SIMPLE_OUTPUT:
        show_simple = True
    if COLORFUL_OUTPUT:
        color_print = True
    if SHOW_TWSE_INDEX:
        add_twse = True
    if SHOW_WORLD_INDEX:
        add_world = True
    if ADD_USER_STOCK_LIST:
        add_stock_list = True

    # generate query url
    tw_url = create_tw_stock_url(add_twse, add_stock_list, argv)
    world_url = create_world_index_url()

    # show usage() if there is no index or stock
    if tw_url == TWSE_URL and add_world == False:
        usage()
        exit()

    while True:
        # access google finance for world index
        if add_world:
            get_world_index_info(world_url)

        if add_twse:
            get_tw_future()

        # access twse server for taiwan stock
        if tw_url != TWSE_URL:
            get_tw_stock_info(tw_url)

        print_result(show_simple, auto_update);

        if auto_update == False:
            break

        del ALL_RESULT[:]
        time.sleep(AUTO_UPDATE_SECOND)

if __name__ == '__main__':
    main()
