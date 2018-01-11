# -*- coding: utf-8 -*-
import requests
import re
import json
import traceback
from datetime import datetime
from datetime import timedelta
from termcolor import colored

# files in this project
from setting import INDEX_LIST


class WorldIndex:
    def __init__(self):
        self.google_url = 'http://finance.google.com/finance?q='
        self.index_list = INDEX_LIST
        self.json_data = []
        self.query_url = []
        self.data = []


    def create_query_url_list(self):
        self.query_url = []
        for index in self.index_list:
            stock_str = self.google_url + index[0] + '&output=json'
            self.query_url.append(stock_str)


    def query_stock_info(self):
        self.json_data = []
        for x in self.query_url:
            result = requests.get(x)
            # remove '//' and other special char in json data
            json_str = re.sub(r'[^\x00-\x7F]','', result.content.replace('// ', '', 1))
            self.json_data.append(json_str)


    def parse_json_data(self):
        now = datetime.now()
        self.data = []
        for js in self.json_data:
            json_data = json.loads(js)
            j = json_data[0]
            item = j['exchange'] + ':' + j['symbol']
            for x in self.index_list:
                if x[0] == item:
                    id = x[1]
                    name = x[2]

            ratio = j["cp"]
            if ratio.find('-'):
                ratio = '+' + ratio

            result = {'id':'', 'name':'', 'price':'', 'change':'', 'ratio':'', 'high':'', 'low':''}
            result['id']     = id
            result['name']   = name
            result['price']  = j["l"].replace(',','')
            result['change'] = j["c"]
            result['ratio']  = ratio
            result['high']   = j['hi'].replace(',','')
            result['low']    = j['lo'].replace(',','')
            self.data.append(result)


    def print_stock_info(self, profile):
        hide_closed = profile['hide_closed_index']
        show_simple = profile['show_simple']
        color_print = profile['color_print']
        color_attrs = ['bold']

        if color_print:
            color = 'yellow'
        else:
            color = 'white'

        if not show_simple:
            print colored(' 代號      指數          點數        漲跌      百分比           區間', color, attrs = color_attrs)
            print '-------------------------------------------------------------------------------'

        for stock in self.data:
            if color_print:
                change = float(stock['change'])
                if change > 0:
                    color = 'red'
                elif change < 0:
                    color = 'green'
                else:
                    color = 'white'

            if show_simple:
                print colored(' {0:8s}' .format(stock['id'])
                       + '{0:>9s}'.format(stock['price'])
                       + '{0:>10s}'.format(stock['change'])
                       + '{0:>9s}%'.format(stock['ratio']), color, attrs = color_attrs)
            else:
                print colored(' {0:8s}' .format(stock['id'])
                       + '{0:<10s}'.format(stock['name'])
                       + '{0:>13s}'.format(stock['price'])
                       + '{0:>12s}'.format(stock['change'])
                       + '{0:>10s}%'.format(stock['ratio'])
                       + '{0:>12s}'.format(stock['low']) + ' ~ '
                       + '{0:<10s}'.format(stock['high']), color, attrs = color_attrs)
        print ''


    def get_data(self):
        self.data = []
        self.create_query_url_list()
        try:
            self.query_stock_info()
            self.parse_json_data()
        except:
            traceback.print_exc()
            return False
        return True
