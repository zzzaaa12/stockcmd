#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import csv
import json
import requests
import urllib
import re
import select
from os import system as system
from time import sleep as sleep
from datetime import datetime
from datetime import timedelta
from HTMLParser import HTMLParser

# TODO:
#      (v) monitor mode
#      ( ) cmd of monitor mode
#      (v) colorful print
#      (v) important status change
#      (v) limit up/down print

AUTO_UPDATE_SECOND = 20

COLOR = {
    'red':'\033[1;31;40m',
    'green':'\033[1;32;40m',
    'yellow':'\033[1;33;40m',
    'white':'\033[1;37;40m',
    'end':'\033[0m'
}

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

    def print_stock_info(self, color_print, hide_closed):
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
                if stock['time'].find('('):
                    closed_count = closed_count + 1

            # skip when all index closed
            if closed_count == len(self.data):
                return

        print color + ' 代號      指數          點數        漲跌      百分比    資料時間' + color_end
        print '---------------------------------------------------------------------------'

        for stock in self.data:
            if hide_closed and stock['time'].find('('):
                continue

            if color_print:
                change = float(stock['change'])
                if change > 0:
                    color = COLOR['red']
                elif change < 0:
                    color = COLOR['green']
                else:
                    color = COLOR['white']

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


class TaiwanStock:
    def __init__(self):
        self.user_stock_list = ['00632r','4127','2330','2317']
        self.stock_list = []
        self.stock_query_str = ''
        self.data = []
        self.twse_url = 'http://220.229.103.179/stock/api/getStockInfo.jsp?ex_ch='
        self.json_data = ''


    def append_stock(self, stock_no):
        if stock_no.upper() not in self.user_stock_list:
            self.user_stock_list.append(stock_no.upper())


    def remove_stock(self, stock_no):
        if stock_no.upper() in self.user_stock_list:
            self.user_stock_list.remove(stock_no.upper())


    def create_stock_list(self, show_user_list):
        self.stock_list = []

        if show_user_list:
            for x in self.user_stock_list:
                if x.upper() not in self.stock_list:
                    self.stock_list.append(x.upper())

        # add stock in argv
        for x in sys.argv:
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


    def print_stock_info(self, color_print):
        if color_print:
            color = COLOR['yellow']
            color_end = COLOR['end']
        else:
            color = ''
            color_end = ''
        print color + ' 股號     股名     成交價     漲跌    百分比   成交量    資料時間 & 狀態' + color_end
        print '--------------------------------------------------------------------------------'
        for stock in self.data:
            if color_print:
                change = float(stock['change'])
                if change > 0:
                    color = COLOR['red']
                elif change < 0:
                    color = COLOR['green']
                else:
                    color = COLOR['white']

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


def usage():
    print 'stockcmd - get stock information for TWSE'
    print ''
    print 'Usage:'
    print '    stockcmd.py [Options] [stock numbers]'
    print ''
    print 'Options:'
    print '    -a: list all stock infomation (include TSE, OTC, other stock)'
    print '    -s: list information with simple format'
    print '    -i: list include TSE index and OTC index'
    print '    -w: list International Stock Indexes'
    print '    -q: list the stocks predefined'
    print '    -c: list with color'
    print '    -d: continue update information every 20 seconds'
    print '    -h: show this page'
    print ''
    print 'Example:'
    print '    stockcmd.py -i'
    print '    stockcmd.py -w'
    print '    stockcmd.py -q'
    print '    stockcmd.py 2330 2317 3008'
    print ''


def read_option(opt):
    profile = {
        'color_print'         : False,
        'show_twse'           : False,
        'show_world_index'    : False,
        'show_user_list'      : False,
        'monitor_mode'        : False,
        'monitor_help'        : True,
        'hide_closed_index'   : False,
        'monitor_append_stock': '',
        'monitor_remove_stock': ''
    }

    for x in opt:
        if str(x) == '-c':
            profile['color_print'] = True
        elif str(x) == '-a':
            profile['show_world_index'] = True
            profile['show_twse'] = True
            profile['show_user_list'] = True
        elif str(x) == '-w':
            profile['show_world_index'] = True
        elif str(x) == '-i':
            profile['show_twse'] = True
        elif str(x) == '-q':
            profile['show_user_list'] = True
        elif str(x) == '-s':
            profile['show_simple'] = True
            profile['show_user_list'] = True
        elif str(x) == '-d':
            profile['monitor_mode'] = True
        elif str(x) == '-h' or str(x) == '--help':
            usage()
            exit()

    return profile


def update_profile(profile):

    if profile['monitor_help']:
            print 'Commands: Q->Exit, C->Color, S->Simple, I->TWSE, W->World, U->User\'s List'
            print '          X->Hide closed index,  +-[stock] -> add or remove stock'

    for x in range(1, AUTO_UPDATE_SECOND, 1):
        input_cmd = ''
        i, o, e = select.select([sys.stdin], [], [], 1)
        if not i:
            continue
        input = sys.stdin.readline().strip().upper()
        if input == 'Q':
            exit()
        elif input == 'C':
            profile['color_print'] = not profile['color_print']
        elif input == 'S':
            profile['show_simple'] = not profile['show_simple']
        elif input == 'I':
            profile['show_twse'] = not profile['show_twse']
        elif input == 'W':
            profile['show_world_index'] = not profile['show_world_index']
        elif input == 'U':
            profile['show_user_list'] = not profile['show_user_list']
        elif input == 'H':
            profile['monitor_help'] = not profile['monitor_help']
        elif input == 'X':
            profile['hide_closed_index'] = not profile['hide_closed_index']
        elif input[:1] == '+' and len(input) > 1:
            profile['monitor_append_stock'] = input[1:]
        elif input[:1] == '-' and len(input) > 1:
            profile['monitor_remove_stock'] = input[1:]
        break

    return profile


def main():
    # remove program name
    argv = sys.argv
    del argv[0]

    profile = read_option(argv)

    # create objects
    world = WorldIndex()
    tw_stock = TaiwanStock()

    # read data from TWSE or Goolge Finance
    world.get_data()
    tw_stock.get_data(profile)

    # clear terminal in monitor mode
    if profile['monitor_mode']:
        system('clear')
        print ''

    # print data
    if profile['show_world_index']:
        world.print_stock_info(profile['color_print'], profile['hide_closed_index'])
    tw_stock.print_stock_info(profile['color_print'])

    # loop for monitor mode
    while profile['monitor_mode']:
        print datetime.now().strftime('Last updated: %Y.%m.%d %H:%M:%S')

        # renew profile
        update_profile(profile)

        # append or remove stock
        if len(profile['monitor_append_stock']):
            tw_stock.append_stock(profile['monitor_append_stock'])
            profile['monitor_append_stock'] = ''
        elif len(profile['monitor_remove_stock']):
            tw_stock.remove_stock(profile['monitor_remove_stock'])
            profile['monitor_remove_stock'] = ''

        # read data
        world.get_data()
        tw_stock.get_data(profile)

        # print result
        system('clear')
        print ''
        if profile['show_world_index']:
            world.print_stock_info(profile['color_print'], profile['hide_closed_index'])
        tw_stock.print_stock_info(profile['color_print'])

if __name__ == '__main__':
    main()
