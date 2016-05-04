#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import csv
import json
import requests
import re

TWSE_SERVER = '220.229.103.179'
TWSE_URL = 'http://' + TWSE_SERVER + '/stock/api/getStockInfo.jsp?ex_ch='
TSE_FILE = 'tse.csv'
OTC_FILE = 'otc.csv'
GOOGLE_URL = 'http://www.google.com/finance/info?q='
INDEX_LIST = [['TPE:TAIEX', 'TAIEX'],
              ['INDEXDJX:.DJI', 'DOW'],
              ['INDEXNASDAQ:.IXIC', 'NASDAQ'],
              ['INDEXNASDAQ:SOX', 'PHLX'],
              ['INDEXDB:DAX', 'DAX'],
              ['INDEXFTSE:UKX', 'FTSE'],
              ['INDEXNIKKEI:NI225', 'N225'],
              ['KRX:KOSPI', 'KOSPI'],
              ['SHA:000001', 'SHCOMP'],
              ['INDEXHANGSENG:HSI', 'HK']]
TW_STOCK_LIST = [2330, 2317, 3008] # you can define the default stock list!!


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
    # read json data
    json_data = json.loads(json_str)

    if stock_type == 'world':
        print u'  指數            點數             漲跌         百分比'
        for i in range(0, len(INDEX_LIST), 1):
            j = json_data[i]
            ratio = j["cp"]
            if ratio.find('-'):
                ratio = '+' + ratio
            name = INDEX_LIST[i][1]
            print ' ' + '{0:13s}'.format(name) + '{0:>10s}'.format(j["l"]) + '{0:>15s}'.format(j["c"]) + '{0:>14s}%'.format(ratio)

    elif stock_type == 'tw':
        print u' 股號     股名      成交價       漲跌      百分比     成交量     資料時間'

        for i in range(0, len(json_data['msgArray']), 1):
            j = json_data['msgArray'][i]
            diff = float(j["z"]) - float(j["y"])

            if diff > 0:
                sign = '+'
            else:
                sign = ''

            change_str = sign + str(diff)
            change_str_p = sign + '{0:.2f}'.format(diff / float(j["y"]) *100)

            stock_no = j["c"]
            name = j["n"]

            # fix too long name.....
            if stock_no == 't00':
                name = u'上市'
            elif stock_no == 'o00':
                name = u'上櫃'

            print ' ' + '{0:8s}'.format(j["c"]) \
                      + name + '\t    {0:7s}'.format(j["z"]) \
                      + '     {0:11s}'.format(change_str) +  change_str_p + '%'\
                      + '    {0:>7s}'.format(j["v"]) + '     ' + j["t"]
    print ''


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
        if str(x) == '-a':
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

main()
