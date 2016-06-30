#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import csv
import json
import requests
import urllib
import re
from datetime import datetime
from datetime import timedelta
from HTMLParser import HTMLParser

# TODO:
#      ( ) monitor mode
#      ( ) cmd of monitor mode
#      ( ) colorful print
#      ( ) important status change
#      ( ) limit up/down print

class world_index:
    def __init__(self):
        self.google_url = 'http://www.google.com/finance/info?q='
        self.index_list = [['TPE:TAIEX'        , 'TAIEX' , '加權指數'], # Format: google finance id, nickname, timezone, name
                           ['INDEXDJX:.DJI'    , 'DOW'   , '道瓊指數'],
                           ['INDEXNASDAQ:.IXIC', 'NASDAQ', '那斯達克'],
                           ['INDEXNASDAQ:SOX'  , 'PHLX'  , '費半PHLX'],
                           ['INDEXDB:DAX'      , 'DAX'   , '德國DAX'],
                           ['INDEXFTSE:UKX'    , 'FTSE'  , '英國FTSE'],
                           ['INDEXEURO:PX1'    , 'CAC40' , '法國指數'],
                           ['INDEXNIKKEI:NI225', 'N225'  , '日本指數'],
                           ['KRX:KOSPI'        , 'KOSPI' , '韓國指數'],
                           ['SHA:000001'       , 'SHCOMP', '上證指數'],
                           ['INDEXHANGSENG:HSI', 'HK'    , '香港恆生']]
        self.json_data = ''
        self.query_url = ''
        self.data = []

    def create_query_url(self):
        stock_str = self.google_url
        for index in self.index_list:
            stock_str = stock_str + index[0] + ','
        self.query_url = stock_str

    def query_stock_info(self):
        result = requests.get(self.query_url)
        # remove '//' and other special char in json data
        self.json_data = re.sub(r'[^\x00-\x7F]','', result.content.replace('// ', '', 1))

    def parse_json_data(self):
        now = datetime.now()
        json_data = json.loads(self.json_data)
        for i in range(len(self.index_list)):
            result = []
            j = json_data[i]
            id = self.index_list[i][1]

            ratio = j["cp"]
            if ratio.find('-'):
                ratio = '+' + ratio

            result_time = datetime.strptime(j["lt_dts"], '%Y-%m-%dT%H:%M:%SZ') + timedelta(hours = self.timezone_diff(j['lt'][15:]))
            if (now-result_time).total_seconds() < 1800:
                time_str = str(result_time.strftime('%H:%M:%S        '))
            elif now.month == result_time.month and now.day == result_time.day:
                time_str = str(result_time.strftime('%H:%M:%S (today)'))
            else:
                time_str = str(result_time.strftime('%H:%M:%S (%m/%d)'))

            result = {'id':'', 'name':'', 'price':'', 'change':'', 'ratio':'', 'time': ''}
            result['id']     = id
            result['name']   = self.index_list[i][2]
            result['price']  = j["l"].replace(',','')
            result['change'] = j["c"]
            result['ratio']  = ratio
            result['time']   = time_str
            self.data.append(result)

    def timezone_diff(self, timezone):
        timezone = timezone.replace(' ', '')
        if timezone[:3] == 'GMT':
            return 8 - int(timezone[3:])
        elif timezone[:3] == 'EDT':
            return 8 - (-4)
        else:
            print 'unknown timezone: ' + timezone
            return 0

    def print_stock_info(self):
        print ' 代號      指數          點數         漲跌     百分比    資料時間' 
        print '---------------------------------------------------------------------------'

        for stock in self.data:
            print ' {0:8s}' .format(stock['id']) + \
                  '{0:<10s}'.format(stock['name']) + \
                  '{0:>13s}'.format(stock['price']) + ' ' + \
                  '{0:>11s}'.format(stock['change']) + ' ' + \
                  '{0:>9s}%'.format(stock['ratio']) + ' ' + \
                  '{0:>19s}'.format(stock['time'])

    def run(self):
        self.create_query_url()
        self.query_stock_info()
        self.parse_json_data()
        self.print_stock_info()


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

        # we need access the website before query data
        r.get('http://220.229.103.179/')

        # query data
        self.json_data = r.get(query_url).content

    def parse_json_data(self):
        now = datetime.now()
        json_data = json.loads(self.json_data)

        for i in range(len(json_data['msgArray'])):
            j = json_data['msgArray'][i]
            status = ''
            price = j["z"]
            stock_no = j["c"]
            name     = j["n"]
            volume   = j["v"]
            highest = float(j['h'])
            lowest = float(j['l'])

            diff = float(j["z"]) - float(j["y"])
            if diff > 0:
                sign = '+'
            elif diff < 0:
                sign = ''
            else:
                sign = ' '

            change_str = sign + '{0:.2f}'.format(diff)
            change_str_p = sign + '{0:.2f}'.format(diff / float(j["y"]) *100)

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

            # status
            if (float(price) == highest):
                status = u' 最高'
            elif (float(price) == lowest):
                status = u' 最低'

            if stock_no != 'TWSE' and stock_no != 'OTC':
                h_limit = float(j['u'])
                l_limit = float(j['w'])
                if (float(price) == h_limit):
                    status = u' 漲停！'
                elif (float(price) == l_limit):
                    status = u' 跌停！'

            # check data time
            date = datetime.strptime(j["d"], '%Y%m%d')
            result_time_str = j["d"] + ' ' + j["t"]
            result_time = datetime.strptime(result_time_str, '%Y%m%d %H:%M:%S')

            if now.month == date.month and now.day == date.day:
                if (now.hour > 13) or (now.hour == 13 and now.minute > 30):
                    time_str = j["t"] + ' (today)'
                else:
                    time_str = j["t"]
            else:
                time_str = j["t"] + date.strftime(' (%m/%d)')

            # save to self.data
            result = {'id':'', 'name':'', 'price':'', 'change':'', 'ratio':'', 'volume':'', 'time': '', 'status': ''}
            result['id']     = stock_no
            result['name']   = name
            result['price']  = price
            result['change'] = change_str
            result['ratio']  = change_str_p
            result['volume'] = volume
            result['time']   = time_str
            result['status']   = status
            self.data.append(result)

    def print_stock_info(self):
        print ' 股號     股名     成交價     漲跌    百分比   成交量    資料時間'
        print '---------------------------------------------------------------------------'

        for stock in self.data:
            print ' ' + '{0:s}'   .format(stock['id']) + \
                  '\t ' + stock['name'] + '\t' + \
                  '{0:>9s}' .format(stock['price']) + ' ' + \
                  '{0:>8s}' .format(stock['change']) + ' ' + \
                  '{0:>8s}%'.format(stock['ratio']) + ' ' + \
                  '{0:>8s}' .format(stock['volume']) + ' ' + \
                  '   {0:19s}'.format(stock['time']) + ' ' + \
                  stock['status']

    def add_tw_future(self):
        tw_future = taiwan_future()
        self.data.append(tw_future.get_data())

    def run(self):
        self.add_tw_future()
        self.create_stock_list()
        self.create_query_url()
        self.query_stock_info()
        self.parse_json_data()
        self.print_stock_info()


class taiwan_future(HTMLParser):
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

    def read_data(self):
        if (self.data[1] == '收盤'):
            i = 6
            time_str = self.data[i+8] + ' (close)'
        else:
            i = 5
            time_str = self.data[i+8] + '        '

        price   = float(self.data[i].replace(',',''))
        change  = float(self.data[i+1])
        volume  = self.data[i+3].replace(',','')
        last_day_price = float(self.data[i+7].replace(',',''))
        ratio   = '{0:.02f}'.format(change / last_day_price * 100)
        highest = float(self.data[i+5].replace(',',''))
        lowest = float(self.data[i+6].replace(',',''))

        status = ''
        if price == highest:
            status = u' 最高'
        elif price == lowest:
            status = u' 最低'

        if change > 0:
            sign = '+'
        else:
            sign = ''

        change_str = sign + '{0:.0f} '.format(change)
        ratio_str = sign + ratio
        result = {'id':'', 'name':'', 'price':'', 'change':'', 'ratio':'', 'volume':'', 'time': '', 'status': ''}
        result['id']     = 'WTX'
        result['name']   = '台指期'
        result['price']  = '{0:.0f} '.format(price)
        result['change'] = change_str
        result['ratio']  = ratio_str
        result['volume'] = volume
        result['time']   = time_str
        result['status'] = status
        return result

    def get_data(self):
        self.feed(urllib.urlopen("http://info512.taifex.com.tw/Future/FusaQuote_Norl.aspx").read())
        self.close()
        return self.read_data()


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

    world = world_index()
    world.run()
    print ''
    tw_stock = taiwan_stock()
    tw_stock.run()

if __name__ == '__main__':
    main()
