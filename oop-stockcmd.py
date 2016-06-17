#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import csv
import json
import requests
from datetime import datetime
from datetime import timedelta

class taiwan_stock:
    def __init__(self):
        self.user_stock_list = ['00632r','4127','2330','2317']
        self.stock_list = []
        self.stock_query_str = ''
        self.data = []
        self.twse_url = 'http://220.229.103.179/stock/api/getStockInfo.jsp?ex_ch='
        self.json_data = ''

    def create_stock_list(self):
        self.stock_list = []
        tmp_list = []

        # add stock in user list
        for i in self.user_stock_list:
            tmp_list.append(str(i).upper())

        # add stock in argv
        for i in sys.argv:
            if i.find('-') == -1:
                tmp_list.append(i.upper())

        # check duplicate and create stock `list
        seen = set()
        for i in tmp_list:
            if i not in seen:
                self.stock_list.append(i)
                seen.add(i)


    def create_query_url(self):
        stock_str = 'tse_t00.tw|otc_o00.tw|'

        for stock_no in self.stock_list:
            found = False

            f = open('tse.csv','r')
            for row in csv.reader(f):
                if not found and row[0] == str(stock_no):
                    stock_str = stock_str + 'tse_' + stock_no + '.tw|'
                    found = True
            f.close()

            f = open('otc.csv','r')
            for row in csv.reader(f):
                if not found and row[0] == str(stock_no):
                    stock_str = stock_str + 'otc_' + stock_no + '.tw|'
                    found = True
            f.close()

        self.stock_query_str = stock_str


    def query_stock_info(self):
        query_url = self.twse_url + self.stock_query_str
        r = requests.session()
        r.get('http://220.229.103.179/')
        result = r.get(query_url)

        self.json_data = result.content


    def parse_json_data(self):

        now = datetime.now()
        json_data = json.loads(self.json_data)

        for i in range(len(json_data['msgArray'])):
            j = json_data['msgArray'][i]
            price = j["z"]
            diff = float(j["z"]) - float(j["y"])

            if diff > 0:
                sign = '+'
            elif diff < 0:
                sign = ''
            else:
                sign = ' '

            change_str = sign + '{0:.2f}'.format(diff)
            change_str_p = sign + '{0:.2f}'.format(diff / float(j["y"]) *100)

            stock_no = j["c"]
            name     = j["n"]
            volume   = j["v"]

            # fix too long name
            if stock_no == 't00':
                stock_no = 'TWSE'
                name = u'上市'
                price = '{0:.0f} '.format(float(price))
                change_str = sign + '{0:.0f} '.format(diff)
                volume = '{0:d}'.format(int(volume)/100)
            elif stock_no == 'o00':
                stock_no = 'OTC'
                name = u'上櫃'
                volume = '{0:d}'.format(int(volume)/100)

            date = datetime.strptime(j["d"], '%Y%m%d')
            result_time_str = j["d"] + ' ' + j["t"]
            result_time = datetime.strptime(result_time_str, '%Y%m%d %H:%M:%S')

            if now.month == date.month and now.day == date.day:
                if (now.hour > 13) or (now.hour == 13 and now.minute > 30):
                    time_str = j["t"] + ' (today)'
                else:
                    time_str = j["t"] + '        '
            else:
                time_str = j["t"] + date.strftime(' (%m/%d)')

            result = {'id':'', 'name':'', 'price':'', 'change':'', 'ratio':'', 'volume':'', 'time': '', 'type':''}
            result['id']     = stock_no
            result['name']   = name
            result['price']  = price
            result['change'] = change_str
            result['ratio']  = change_str_p
            result['volume'] = volume
            result['time']   = time_str
            result['type']   = 'stock'
            self.data.append(result)


    def print_tw_stock_info(self):
        print ' 股號     股名     成交價     漲跌    百分比   成交量    資料時間'
        print '---------------------------------------------------------------------------'

        for stock in self.data:
            print ' ' + '{0:s}'   .format(stock['id']) + \
                  '\t ' + stock['name'] + '\t' + \
                  '{0:>9s}' .format(stock['price']) + ' ' + \
                  '{0:>8s}' .format(stock['change']) + ' ' + \
                  '{0:>8s}%'.format(stock['ratio']) + ' ' + \
                  '{0:>8s}' .format(stock['volume']) + ' ' + \
                  '{0:>19s}'.format(stock['time'])


    def run(self):
        self.create_stock_list()
        self.create_query_url()
        self.query_stock_info()
        self.parse_json_data()
        self.print_tw_stock_info()


def main():
    # remote program name
    argv = sys.argv
    del argv[0]

    # read parameters
    for x in argv:
        if str(x) == '-c':
            color_print = True
        elif str(x) == '-a':
            show_world = True
            show_twse = True
            show_stock_list = True
        elif str(x) == '-w':
            show_world = True
        elif str(x) == '-i':
            show_twse = True
        elif str(x) == '-q':
            show_stock_list = True
        elif str(x) == '-s':
            show_simple = True
            show_stock_list = True
        elif str(x) == '-d':
            monitor_mode = True
        elif str(x) == '-h' or str(x) == '--help':
            usage()
            exit()

    tw_stock = taiwan_stock()
    tw_stock.run()


if __name__ == '__main__':
    main()
