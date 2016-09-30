# -*- coding: utf-8 -*-
import urllib
import json
import requests
import traceback
from datetime import datetime
from HTMLParser import HTMLParser
from termcolor import colored

# files in this project
from setting import USER_STOCK_LIST
from setting import TWSE_SERVER
from setting import TW_FUTURE_URL


class TaiwanStock:
    def __init__(self, argv):
        self.user_stock_list = USER_STOCK_LIST
        self.stock_list = []
        self.stock_query_str = ''
        self.data = []
        self.twse_url = TWSE_SERVER + '/stock/api/getStockInfo.jsp?ex_ch='
        self.json_data = ''
        self.argv = argv

    # append stock in monitor mode
    def append_stock(self, stock_no):
        if self.check_stock_no(stock_no) == False:
            return
        if stock_no.upper() not in self.user_stock_list and stock_no.lower() not in self.user_stock_list:
            self.user_stock_list.append(stock_no.upper())

    # remove stock in monitor mode
    def remove_stock(self, stock_no):
        if self.check_stock_no(stock_no) == False:
            return
        if stock_no.upper() in self.user_stock_list:
            self.user_stock_list.remove(stock_no.upper())
        if stock_no.lower() in self.user_stock_list:
            self.user_stock_list.remove(stock_no.lower())

    # check format of stock number
    def check_stock_no(self, stock_no):
        if len(stock_no) > 6 or len(stock_no) < 4 or stock_no[0:1].isdigit() == False:
            return False
        return True

    def create_stock_list(self, show_user_list):
        self.stock_list = []

        if show_user_list:
            # add stock in user_stock_list
            for x in self.user_stock_list:
                if x.upper() not in self.stock_list:
                    self.stock_list.append(x.upper())
        # add stock in argv
        for x in self.argv:
            if self.check_stock_no(x) == False:
                continue
            if x.find('-') == -1 and x.upper() not in self.stock_list:
                self.stock_list.append(x.upper())


    def create_query_url(self, show_twse_index):
        if show_twse_index:
            stock_str = 'tse_t00.tw|otc_o00.tw|'
        else:
            stock_str = ''

        for stock_no in self.stock_list:
            stock_str = stock_str + 'tse_' + stock_no + '.tw|otc_' + stock_no + '.tw|'

        self.stock_query_str = stock_str


    def query_stock_info(self):
        query_url = self.twse_url + self.stock_query_str
        r = requests.session()

        # we need access the website before query data
        r.get(TWSE_SERVER)

        # query data
        self.json_data = r.get(query_url).content


    def parse_json_data(self):
        now = datetime.now()
        json_data = json.loads(self.json_data)

        for i in range(len(json_data['msgArray'])):
            j = json_data['msgArray'][i]
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

            # status
            status = ''
            if (float(price) == highest):
                status = u'最高'
            elif (float(price) == lowest):
                status = u'最低'

            if stock_no != 't00' and stock_no != 'o00':
                h_limit = float(j['u'])
                l_limit = float(j['w'])
                if (float(price) == h_limit):
                    status = u'漲停！'
                elif (float(price) == l_limit):
                    status = u'跌停！'

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

            # FIXME: To avoid too long stock name
            if len(name) > 4:
                name = stock_no

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


    def print_stock_info(self, profile):
        show_twse_index = profile['show_twse_index']
        show_simple = profile['show_simple']
        color_print = profile['color_print']
        color_attrs = ['bold']

        if color_print:
            color = 'yellow'
        else:
            color = 'white'

        if not show_simple:
            print colored(' 股號     股名     成交價     漲跌    百分比   成交量    資料時間 & 狀態', color, attrs = color_attrs)
            print '--------------------------------------------------------------------------------'

        for stock in self.data:
            if not show_twse_index:
                if stock['id'] == 'TWSE' or stock['id'] == 'OTC' or stock['id'] == 'WTX':
                    continue

            if color_print:
                change = float(stock['change'])
                color_attrs = ['bold']
                if stock['status'].find(u'停') > -1:
                    color_attrs = ['reverse', 'blink']
                if change > 0:
                    color = 'red'
                elif change < 0:
                    color = 'green'
                else:
                    color = 'white'

            if show_simple:
                print colored(' {0:8s}'.format(stock['id'])
                      + '{0:>8s}' .format(stock['price'])
                      + '{0:>10s}' .format(stock['change'])
                      + '{0:>10s}%'.format(stock['ratio'])
                      + '{0:>9s}' .format(stock['volume'])
                      + '    ' + stock['status'], color, attrs = color_attrs)
            else:
                print colored(' {0:8s}'.format(stock['id'])
                      + stock['name'] + '\t'
                      + '{0:>9s}' .format(stock['price'])
                      + '{0:>9s}' .format(stock['change'])
                      + '{0:>9s}%'.format(stock['ratio'])
                      + '{0:>9s}' .format(stock['volume'])
                      + '    ' + stock['time'] + ' ' + stock['status'], color, attrs = color_attrs)
        print ''


    def add_tw_future(self):
        tw_future = TaiwanFuture()
        self.data.append(tw_future.get_data())


    def get_data(self, profile):
        self.data = []
        if profile['show_twse_index']:
            self.add_tw_future()

        self.create_stock_list(profile['show_user_list'])
        self.create_query_url(profile['show_twse_index'])

        if len(self.stock_query_str):
            try:
                self.query_stock_info()
                self.parse_json_data()
            except:
                traceback.print_exc()
                return False
            return True

        return False


class TaiwanFuture(HTMLParser):
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
            time_str = self.data[i+8]

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
        self.feed(urllib.urlopen(TW_FUTURE_URL).read())
        self.close()
        return self.read_data()
