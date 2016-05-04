#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import csv
import json
import requests
import re

server = '220.229.103.179'
url = 'http://' + server + '/stock/api/getStockInfo.jsp?ex_ch='
argv = sys.argv
count = 0
tse_file = 'tse.csv'
otc_file = 'otc.csv'
stock_list = 'stock_list.txt'

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
    print ''
    print 'Example:'
    print '    stockcmd.py -i'
    print '    stockcmd.py -w'
    print '    stockcmd.py -i 2330 2317 3008'
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
    url = 'http://www.google.com/finance/info?q='
    list = [['TPE:TAIEX', 'TAIEX'],
           ['INDEXDJX:.DJI', 'DOW'],
           ['INDEXNASDAQ:.IXIC', 'NASDAQ'],
           ['INDEXNASDAQ:SOX', 'PHLX'],
           ['INDEXDB:DAX', 'DAX'],
           ['INDEXFTSE:UKX', 'FTSE'],
           ['INDEXNIKKEI:NI225', 'N225'],
           ['KRX:KOSPI', 'KOSPI'],
           ['SHA:000001', 'SHCOMP'],
           ['INDEXHANGSENG:HSI', 'HK']]

    for index in list:
        url = url + index[0] + ','

    result = requests.get(url)
    json_str = remove_special_char(result.content.replace('// ', '', 1))

    # read json data
    json_data = json.loads(json_str)

    print u'  指數          點數             漲跌         百分比'
    for i in range(0, len(list), 1):
        j = json_data[i]
        ratio = j["cp"]
        if ratio.find('-'):
            ratio = '+' + ratio

        print ' ' + '{0:13s}'.format(list[i][1]) + '{0:18s}'.format(j["l"]) + '{0:14s}'.format(j["c"]) + ratio + '%'
    print ''


if len(argv) == 1:
    # no parameter, show usage()
    usage()
    exit()

del argv[0]
i = 0
add_world = False
add_twse = False

# read parameters
for x in argv:
    if str(x) == '-a':
        add_world = True;
        add_twse = True;
    elif str(x) == '-w':
        add_world = True;
    elif str(x) == '-i':
        add_twse = True;
    elif str(x) == '-h' or str(x) == '--help':
        usage()
        exit()

if add_world:
    world_index()

if add_twse:
    url = url + 'tse_t00.tw|otc_o00.tw|'
    count += 2

# determine stock is in tse or otc and add it to list
for x in argv:
    if search_stock(str(x), otc_file):
        url = url + 'otc_' + str(x) + '.tw|'
    elif search_stock(str(x), tse_file):
        url = url + 'tse_' + str(x) + '.tw|'
    else:
        continue
    count += 1

if count > 0:
    # access the index first and then send request for stock list
    r = requests.session()
    r.get('http://' + server + '/stock/index.jsp', headers = {'Accept-Language':'zh-TW'}, timeout=2)
    result = r.get(url)

    # read json data
    json_data = json.loads(result.content)
    print u' 股號    股名    成交價      漲跌     百分比     成交量     資料時間'

    for i in range(0, count, 1):
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
                  + name + '    {0:10s}'.format(j["z"]) \
                  + ' {0:10s}'.format(change_str) +  change_str_p + '%'\
                  + '    {0:>7s}'.format(j["v"]) + '     ' + j["t"]
    print ''
