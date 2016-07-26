# -*- coding: utf-8 -*-
import csv
import urllib
import json
import requests
from datetime import datetime
from HTMLParser import HTMLParser

# files in this project
from common import COLOR

class TaiwanStock:
    def __init__(self, argv):
        self.user_stock_list = ['00632r','4127','2330','2317']
        self.stock_list = []
        self.stock_query_str = ''
        self.data = []
        self.twse_url = 'http://220.229.103.179/stock/api/getStockInfo.jsp?ex_ch='
        self.json_data = ''
        self.argv = argv


    def append_stock(self, stock_no):
        if stock_no.upper() not in self.user_stock_list and stock_no.lower() not in self.user_stock_list:
            self.user_stock_list.append(stock_no.upper())


    def remove_stock(self, stock_no):
        if stock_no.upper() in self.user_stock_list:
            self.user_stock_list.remove(stock_no.upper())
        if stock_no.lower() in self.user_stock_list:
            self.user_stock_list.remove(stock_no.lower())


    def create_stock_list(self, show_user_list):
        self.stock_list = []

        if show_user_list:
            # add stock in user_stock_list
            for x in self.user_stock_list:
                if x.upper() not in self.stock_list:
                    self.stock_list.append(x.upper())
            # add stock in argv
            for x in self.argv:
                if x.find('-') == -1 and x not in self.stock_list:
                    self.stock_list.append(x.upper())


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
        color_print = profile['color_print']
        show_index = profile['show_twse']
        show_simple = profile['show_simple']

        if color_print:
            color = COLOR['yellow']
            color_end = COLOR['end']
        else:
            color = ''
            color_end = ''

        if not show_simple:
            print color + ' 股號     股名     成交價     漲跌    百分比   成交量    資料時間 & 狀態' + color_end
            print '--------------------------------------------------------------------------------'

        for stock in self.data:
            if not show_index:
                if stock['id'] == 'TWSE' or stock['id'] == 'OTC' or stock['id'] == 'WTX':
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
                print (color + ' {0:s}'   .format(stock['id']) + '\t '
                      + '{0:>8s}' .format(stock['price'])
                      + '{0:>10s}' .format(stock['change'])
                      + '{0:>10s}%'.format(stock['ratio']) + color_end)
            else:
                print (color + ' {0:s}'   .format(stock['id']) + '\t '
                      + stock['name'] + '\t'
                      + '{0:>9s}' .format(stock['price'])
                      + '{0:>9s}' .format(stock['change'])
                      + '{0:>9s}%'.format(stock['ratio'])
                      + '{0:>9s}' .format(stock['volume'])
                      + '    ' + stock['time'] + ' ' + stock['status'] + color_end)
        print ''


    def add_tw_future(self):
        tw_future = TaiwanFuture()
        self.data.append(tw_future.get_data())

    def get_data(self, profile):
        self.data = []
        self.add_tw_future()
        self.create_stock_list(profile['show_user_list'])
        self.create_query_url()
        self.query_stock_info()
        self.parse_json_data()


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
        self.feed(urllib.urlopen("http://info512.taifex.com.tw/Future/FusaQuote_Norl.aspx").read())
        self.close()
        return self.read_data()
