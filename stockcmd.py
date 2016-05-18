#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import csv
import json
import requests
import re
from datetime import datetime
from datetime import timedelta

TWSE_SERVER = '220.229.103.179'
TWSE_URL = 'http://' + TWSE_SERVER + '/stock/api/getStockInfo.jsp?ex_ch='
TSE_FILE = 'tse.csv'
OTC_FILE = 'otc.csv'
GOOGLE_URL = 'http://www.google.com/finance/info?q='
INDEX_LIST = [['TPE:TAIEX'        , 'TAIEX' , +8], # Format: index name, id, timezone
              ['INDEXDJX:.DJI'    , 'DOW'   , -4], # FIXME: Daylight saving time
              ['INDEXNASDAQ:.IXIC', 'NASDAQ', -4],
              ['INDEXNASDAQ:SOX'  , 'PHLX'  , -4],
              ['INDEXDB:DAX'      , 'DAX'   , +2],
              ['INDEXFTSE:UKX'    , 'FTSE'  , +1],
              ['INDEXNIKKEI:NI225', 'N225'  , +9],
              ['KRX:KOSPI'        , 'KOSPI' , +9],
              ['SHA:000001'       , 'SHCOMP', +8],
              ['INDEXHANGSENG:HSI', 'HK'    , +8]]
TW_STOCK_LIST = ['2330', '2317', '3008', '00631L', '00632R'] # you can define the default stock list!!
color_print = False

# [id, name, price, changes, percent, volume, time, type]
ALL_RESULT  = []

def usage():
    print 'stockcmd - get stock information for TWSE'
    print ''
    print 'Usage:'
    print '    stockcmd.py [Options] [stock numbers]'
    print ''
    print 'Options:'
    print '    -a: list all stock infomation (include TSE, OTC, other stock)'
    print '    -i: list include TSE index and OTC index'
    print '    -w: list International Stock Indexes'
    print '    -q: list the stocks predefined'
    print '    -c: colorful print result'
    print '    -h: show this page'
    print ''
    print 'Example:'
    print '    stockcmd.py -i'
    print '    stockcmd.py -w'
    print '    stockcmd.py -q'
    print '    stockcmd.py 2330 2317 3008'
    print ''


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


def world_index():
    url = GOOGLE_URL
    for item in INDEX_LIST:
        url = url + item[0] + ','

    result = requests.get(url)
    json_str = remove_special_char(result.content.replace('// ', '', 1))

    print_result(json_str, 'world')


def print_result(json_str, stock_type):
    red = '\033[1;31;40m'
    green = '\033[1;32;40m'
    yellow = '\033[1;33;40m'
    white = '\033[1;37;40m'
    title_color = ''
    item_color = ''

    if color_print == True:
        title_color = yellow
    else:
        red = ''
        green = ''
        yellow = ''
        white = ''

    # read json data
    json_data = json.loads(json_str)

    if stock_type == 'world':
        for i in range(0, len(INDEX_LIST), 1):
            result = []
            j = json_data[i]
            id = INDEX_LIST[i][1]

            ratio = j["cp"]
            if ratio.find('-'):
                ratio = '+' + ratio
                item_color = red
            else:
                item_color = green

            if float(j["c"]) == 0:
                item_color = white

            timezone = int(INDEX_LIST[i][2])
            last_time = datetime.strptime(j["lt_dts"], '%Y-%m-%dT%H:%M:%SZ') + timedelta(hours = 8-timezone)
            time_str = str(last_time.strftime('%H:%M:%S (%m/%d)'))

            result.append(id)
            result.append(id)
            result.append(j["l"])
            result.append(j["c"])
            result.append(j["cp"])
            result.append(' ')
            result.append(time_str)
            result.append("index")
            ALL_RESULT.append(result)

    elif stock_type == 'tw':

        for i in range(0, len(json_data['msgArray']), 1):
            result = []
            j = json_data['msgArray'][i]
            diff = float(j["z"]) - float(j["y"])

            if diff > 0:
                sign = '+'
                item_color = red
            elif diff < 0:
                sign = ''
                item_color = green
            else:
                sign = ' '
                item_color = white

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

            time_str = j["t"] + date.strftime(' (%m/%d)')
            result.append(stock_no)
            result.append(name)
            result.append(j["z"])
            result.append(change_str)
            result.append(change_str_p)
            result.append(j["v"])
            result.append(time_str)
            result.append("stock")
            ALL_RESULT.append(result)


def main():
    argv = sys.argv
    count = 0
    add_world = False
    add_twse = False
    add_stock_list = False
    url = TWSE_URL

    if len(argv) == 1:
        # no parameter, show usage()
        usage()
        exit()

    # remote program name
    del argv[0]

    # read parameters
    for x in argv:
        if str(x) == '-c':
            global color_print
            color_print = True
        elif str(x) == '-a':
            add_world = True;
            add_twse = True
            add_stock_list = True
        elif str(x) == '-w':
            add_world = True
        elif str(x) == '-i':
            add_twse = True
        elif str(x) == '-q':
            add_stock_list = True
        elif str(x) == '-h':
            usage()
            exit()

    if add_world:
        world_index()

    if add_twse:
        url = url + 'tse_t00.tw|otc_o00.tw|'
        count += 2

    # add user predefined stock list
    # search_stock() is use to determine stock is in tse or otc
    if add_stock_list:
        for x in TW_STOCK_LIST:
            if search_stock(str(x), OTC_FILE):
                url = url + 'otc_' + str(x) + '.tw|'
            elif search_stock(str(x), TSE_FILE):
                url = url + 'tse_' + str(x) + '.tw|'
            else:
                continue
            count += 1

    # search stock number from input
    for x in argv:
        if search_stock(str(x), OTC_FILE):
            url = url + 'otc_' + str(x) + '.tw|'
        elif search_stock(str(x), TSE_FILE):
            url = url + 'tse_' + str(x) + '.tw|'
        else:
            continue
        count += 1

    if count == 0 and add_world == False and add_twse == False and add_stock_list == False:
        usage()
        exit()

    elif count > 0:
        # access the index first and then send request for stock list
        r = requests.session()
        r.get('http://' + TWSE_SERVER + '/stock/index.jsp', headers = {'Accept-Language':'zh-TW'}, timeout=2)
        result = r.get(url)

        json_str = result.content
        print_result(json_str, 'tw')


if __name__ == '__main__':
	main()

for i in range(len(ALL_RESULT)):

    red = '\033[1;31;40m'
    green = '\033[1;32;40m'
    yellow = '\033[1;33;40m'
    title_color = ''
    item_color = ''

    if color_print == True:
        title_color = yellow
    else:
        red = ''
        green = ''
        yellow = ''

    type = ALL_RESULT[i][7]
    change = ALL_RESULT[i][3]

    if float(change) > 0:
        item_color = red
    elif float(change) < 0:
        item_color = green

    if (i == 0) or (type == 'stock' and ALL_RESULT[i-1][7] != 'stock'):
        if i > 0:
            print ''
        print title_color + ' 股號     股名       成交價      漲跌      百分比     成交量         資料時間'
        print '----------------------------------------------------------------------------------'

    # for tw stock
    print item_color + ' ' + \
          '{0:s}'.format(ALL_RESULT[i][0]) + '\t ' + \
          ALL_RESULT[i][1] + '\t' + \
          '{0:>12s}'.format(ALL_RESULT[i][2]) + ' ' + \
          '{0:>10s}'.format(ALL_RESULT[i][3]) + ' ' + \
          '{0:>9s}%'.format(ALL_RESULT[i][4]) + ' ' + \
          '{0:>9s}'.format(ALL_RESULT[i][5]) + ' ' + \
          '{0:>21s}'.format(ALL_RESULT[i][6])
print ''
