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
from setting import WORLD_INDEX_URL


class WorldIndex:
    def __init__(self):
        self.query_url = WORLD_INDEX_URL
        self.json_data = []
        self.data = []


    def query_stock_info(self):
        headers = requests.utils.default_headers()
        headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
                })

        r = requests.get(self.query_url, headers=headers, timeout=10)
        if r.status_code != 200 or len(r.text) < 10000:
            print 'HTTP Status: ' + r.status_code
            print 'Data Length: ' + len(r.text)
            print 'query failed!!!'
            return False

        self.json_data = json.loads(r.text)
        return True


    def parse_json_data(self):
        query_list = []
        parsed_items = []

        for x in INDEX_LIST:
            # save json data
            for j in self.json_data:
                j['stockNo'] = j['stockNo'].replace('&','')

                if j['stockNo'] in parsed_items:
                    continue

                # get specific entry
                if j['stockNo'] == x[0]:
                    result = {'id': '', 'name': '', 'price': '', 'change': '', 'percent': '', 'date_time': '', 'time': ''}
                    result['id'] = x[1]
                    result['name'] = x[2]
                    result['price'] = j['Deal']
                    result['change'] = j['Change']
                    result['percent'] = j['Percent']
                    result['date_time'] = j['dt']
                    result['time'] = j['dt2']
                    self.data.append(result)
                    parsed_items.append(j['stockNo'])

        # rewrite saved data
        for x in self.data:
            # replace stock id to nick name
            for index in INDEX_LIST:
                if x['id'] == index[0]:
                    x['id'] = index[1]
                    x['name'] = index[2]
                    break

            # round to 2 decimal places
            if x['price'] < 10:
                x['price'] = '{0:.4f}'.format(float(x['price']))
                x['change'] = '{0:.4f}'.format(float(x['change']))
            else:
                x['price'] = '{0:.2f}'.format(float(x['price']))
                x['change'] = '{0:.2f}'.format(float(x['change']))
            x['percent'] = '{0:.2f}'.format(float(x['percent']))

            # sing of change and percent
            if float(x['change']) == 0:
                x['change'] = ' ' + x['change']
                x['percent'] = ' ' + x['percent']
            elif float(x['change']) > 0:
                x['change'] = '+' + x['change']
                x['percent'] = '+' + x['percent']



    def print_stock_info(self, profile):
        if len(self.data) == 0:
            return

        hide_closed = profile['hide_closed_index']
        show_simple = profile['show_simple']
        color_print = profile['color_print']
        color_attrs = ['bold']

        if color_print:
            color = 'yellow'
        else:
            color = 'white'

        print ''

        if not show_simple:
            print colored(' 代號        指數          點數        漲跌      百分比', color, attrs = color_attrs)
            print '-----------------------------------------------------------'

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
                print colored(' {0:8s}'.format(stock['id'])
                       + '{0:>10s}'.format(stock['price'])
                       + '{0:>10s}'.format(stock['change'])
                       + '{0:>9s}%'.format(stock['percent']), color, attrs = color_attrs)
            else:
                print colored(' {0:8s}  '.format(stock['id'])
                       + stock['name']
                       + '{0:>13s}'.format(stock['price'])
                       + '{0:>12s}'.format(stock['change'])
                       + '{0:>10s}%'.format(stock['percent']), color, attrs = color_attrs)


    def get_data(self):
        self.data = []
        try:
            if self.query_stock_info() == False:
                return False
            self.parse_json_data()
        except:
            traceback.print_exc()
            return False
        return True
