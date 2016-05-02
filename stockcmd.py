#!/usr/bin/python
import sys
import csv
import json
import requests

server = '220.229.103.179'
url = 'http://' + server + '/stock/api/getStockInfo.jsp?ex_ch='
argv = sys.argv
index = 0
tse_file = 'tse.csv'
otc_file = 'otc.csv'
stock_list = 'stocl_list.txt'

def search_number (stock_no, filename):
    ret = 0

    f = open(filename,'r')
    for row in csv.reader(f):
        if row[0] == str(stock_no):
            ret = 1
            break
    f.close()
    return ret


if len(argv) == 1:
    url = url + 'tse_t00.tw|otc_o00.tw'
    index += 2

elif len(argv) > 1:
    del argv[0]

    for x in (argv):
        if search_number(str(x), otc_file) == 1:
            url = url + 'otc_' + str(x) + '.tw|'
        elif search_number(str(x), tse_file) == 1:
            url = url + 'tse_' + str(x) + '.tw|'
        else:
            print 'Error: Cannot find stock ' + str(x) + ' name in files'
            continue
        index += 1

# access the index first and then send request for stock list
r = requests.session()
r.get('http://' + server + '/stock/index.jsp', headers = {'Accept-Language':'zh-TW'}, timeout=2)
result = r.get(url)

# read json data
json_data = json.loads(result.content)
print 'No.\tName\tPrice\tChange\t   %\tVolume\t  Time'

for i in range(0, index, 1):
    j = json_data['msgArray'][i]

    diff = float(j["z"]) - float(j["y"])
    if diff > 0:
        sign = '+'
    else:
        sign = ''

    change_str = sign + str(diff)
    change_str_p = sign + '{0:.2f}'.format(diff / float(j["y"]) *100)

    print j["c"] + '\t' + j["n"] + '\t' + j["z"] + '\t' + change_str + '\t' + change_str_p + '%\t' + j["v"] + '\t' + j["t"]
