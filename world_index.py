# -*- coding: utf-8 -*-
import requests
import re
import json
from datetime import datetime
from datetime import timedelta

# files in this project
from common import COLOR

class WorldIndex:
    def __init__(self):
        self.google_url = 'http://www.google.com/finance/info?q='
        self.index_list = [
            ['TPE:TAIEX'        , 'TAIEX' , '加權指數'], # Format: google finance id, nickname, timezone, name
            ['INDEXDJX:.DJI'    , 'DOW'   , '道瓊指數'],
            ['INDEXNASDAQ:.IXIC', 'NASDAQ', '那斯達克'],
            ['INDEXNASDAQ:SOX'  , 'PHLX'  , '費半PHLX'],
            ['INDEXDB:DAX'      , 'DAX'   , '德國DAX'],
            ['INDEXFTSE:UKX'    , 'FTSE'  , '英國FTSE'],
            ['INDEXEURO:PX1'    , 'CAC40' , '法國指數'],
            ['INDEXNIKKEI:NI225', 'N225'  , '日本指數'],
            ['KRX:KOSPI'        , 'KOSPI' , '韓國指數'],
            ['SHA:000001'       , 'SHCOMP', '上證指數'],
            ['INDEXHANGSENG:HSI', 'HK'    , '香港恆生']
        ]
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

            result_time = datetime.strptime(j["lt_dts"], '%Y-%m-%dT%H:%M:%SZ') + timedelta(hours = self.timezone_diff(j['lt']))
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
        gmt = timezone.find('GMT')
        if gmt != -1:
            return 8 - int(timezone[gmt + 3:])
        elif timezone.find('EDT') != -1:
            return 8 - (-4)
        else:
            print 'unknown timezone: ' + timezone
            return 0

    def print_stock_info(self, profile):
        color_print = profile['color_print']
        hide_closed = profile['hide_closed_index']
        show_simple = profile['show_simple']

        if color_print:
            color = COLOR['yellow']
            color_end = COLOR['end']
        else:
            color = ''
            color_end = ''

        if hide_closed:
            # search closed data
            closed_count = 0
            for stock in self.data:
                if stock['time'].find('(') != -1:
                    closed_count = closed_count + 1

            # skip when all index closed
            if closed_count == len(self.data):
                return

        if not show_simple:
            print color + ' 代號      指數          點數        漲跌      百分比    資料時間' + color_end
            print '---------------------------------------------------------------------------'

        for stock in self.data:
            if hide_closed and stock['time'].find('(') != -1:
                continue

            if color_print:
                change = float(stock['change'])
                if change > 0:
                    color = COLOR['red']
                elif change < 0:
                    color = COLOR['green']
                else:
                    color = COLOR['white']

            if show_simple:
                print (color + ' {0:8s}' .format(stock['id'])
                       + '{0:>9s}'.format(stock['price'])
                       + '{0:>10s}'.format(stock['change'])
                       + '{0:>9s}%'.format(stock['ratio']) + color_end)
            else:
                print (color + ' {0:8s}' .format(stock['id'])
                       + '{0:<10s}'.format(stock['name'])
                       + '{0:>13s}'.format(stock['price'])
                       + '{0:>12s}'.format(stock['change'])
                       + '{0:>10s}%'.format(stock['ratio'])
                       + '{0:>20s}'.format(stock['time']) + color_end)
        print''


    def get_data(self):
        self.data = []
        self.create_query_url()
        self.query_stock_info()
        self.parse_json_data()
