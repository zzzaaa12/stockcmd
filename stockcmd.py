#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import csv
import json
import requests

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
    print '    -a: list include TSE index and OTC index'
    print ''
    print 'Example:'
    print '    stockcmd.py -a 2330 2317 3008'
    print ''

def search_stock (stock_no, filename):
    ret = False

    f = open(filename,'r')
    for row in csv.reader(f):
        if row[0] == str(stock_no):
            ret = True
            break
    f.close()
    return ret


if len(argv) == 1:
    usage()
    exit()

elif len(argv) > 1:
    del argv[0]
    i = 0

    for x in argv:
        if str(x) == '-h' or str(x) == '--help':
            usage()
            exit()

        if str(x) == '-a':
            url = url + 'tse_t00.tw|otc_o00.tw|'
            count += 2
            del argv[i]
        i += 1

    for x in argv:
        if search_stock(str(x), otc_file):
            url = url + 'otc_' + str(x) + '.tw|'
        elif search_stock(str(x), tse_file):
            url = url + 'tse_' + str(x) + '.tw|'
        else:
            print str(x) + ': wrong parameter'
            continue
        count += 1

# access the index first and then send request for stock list
r = requests.session()
r.get('http://' + server + '/stock/index.jsp', headers = {'Accept-Language':'zh-TW'}, timeout=2)
result = r.get(url)

# read json data
json_data = json.loads(result.content)
print u'股號\t股名\t成交價\t漲跌\t百分比\t成交量\t資料時間'

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

    print j["c"] + '\t' + name + '\t' + j["z"] + '\t' + change_str + '\t' + change_str_p + '%\t' + j["v"] + '\t' + j["t"]
