#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import csv
import json
import requests
import re
import time
import os
import urllib
import select
from datetime import datetime
from datetime import timedelta
from HTMLParser import HTMLParser

# User Setting1: Default output format
SIMPLE_OUTPUT = False
COLORFUL_OUTPUT = False
SHOW_TWSE_INDEX = False
SHOW_WORLD_INDEX = False
ADD_USER_STOCK_LIST = False
AUTO_UPDATE_SECOND = 20

# User Setting2: Stock list and file path
USER_STOCK_LIST = ['2330', '2317', '3008', '00631L', '00632R']
TW_STOCK_QUERY_LIST = []
TSE_FILE = 'tse.csv'
OTC_FILE = 'otc.csv'

# Server Setting:
TWSE_SERVER = '220.229.103.179'
TWSE_URL = 'http://' + TWSE_SERVER + '/stock/api/getStockInfo.jsp?ex_ch='
GOOGLE_URL = 'http://www.google.com/finance/info?q='
INDEX_LIST = [['TPE:TAIEX'        , 'TAIEX' , '加權指數'], # Format: google finance id, short id, name
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

# ALL_RESULT includes all result data we need: [id, name, price, changes, percent, volume, time, type]
#   ex: ['00632R', 'T50反1', '19.75', '-0.15', '-0.75%', '88403', '13:30:00 (05/20)']
ALL_RESULT  = []

# Color Setting
color_print = False
RED = '\033[1;31;40m'
GREEN = '\033[1;32;40m'
YELLOW = '\033[1;33;40m'
WHITE = '\033[1;37;40m'
COLOR_END = '\033[0m'


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


class future_parser(HTMLParser):
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


def search_stock(stock_no):
    stock_str = ''

    f = open(TSE_FILE,'r')
    for row in csv.reader(f):
        if row[0] == str(stock_no):
            stock_str = 'tse_' + stock_no + '.tw|'
            break
    f.close()

    if len(stock_str) == 0:
        f = open(OTC_FILE,'r')
        for row in csv.reader(f):
            if row[0] == str(stock_no):
                stock_str = 'otc_' + stock_no + '.tw|'
                break
        f.close()

    return stock_str


def remove_special_char(string):
    return re.sub(r'[^\x00-\x7F]','', string)


def print_result(show_simple, auto_update, hide_closed_index):

    if auto_update:
        os.system('clear || cls')

    # when all index need be hidden, we will hide the titles
    index_count = 0;
    if hide_closed_index:
        for i in range(len(ALL_RESULT)):
            if ALL_RESULT[i]['type'] == 'index' and ALL_RESULT[i]['time'].find('(') == -1:
                index_count = index_count + 1

    for i in range(len(ALL_RESULT)):
        type = ALL_RESULT[i]['type']
        last_type = ALL_RESULT[i-1]['type']

        title_color = ''
        item_color = ''
        color_end = ''

        if color_print:
            title_color = YELLOW
            color_end = COLOR_END
            change = ALL_RESULT[i]['change'].replace(',','')
            if float(change) > 0:
                item_color = RED
            elif float(change) < 0:
                item_color = GREEN
            else:
                item_color = WHITE

        if show_simple:
            if type == 'stock' and last_type != 'stock':
                print '--------------------------------------'
            print item_color + ' ' + \
                  '{0:s}\t  '.format(ALL_RESULT[i]['id']) + \
                  '{0:>9s}'  .format(ALL_RESULT[i]['price']) + \
                  '{0:>9s}   {1:s}%'.format(ALL_RESULT[i]['change'], ALL_RESULT[i]['ratio']) + color_end

        elif type == 'index':
            if i == 0 and (not hide_closed_index or (hide_closed_index and index_count > 0)):
                print '\n' + title_color + ' 代號      指數          點數         漲跌     百分比    資料時間' + color_end
                print '---------------------------------------------------------------------------'

            # print all data
            if hide_closed_index == True and ALL_RESULT[i]['time'].find('(') != -1:
                continue;

            print item_color + ' ' + \
                  '{0:8s}'  .format(ALL_RESULT[i]['id']) + \
                  '{0:<10s}'.format(ALL_RESULT[i]['name']) + \
                  '{0:>13s}'.format(ALL_RESULT[i]['price']) + ' ' + \
                  '{0:>11s}'.format(ALL_RESULT[i]['change']) + ' ' + \
                  '{0:>9s}%'.format(ALL_RESULT[i]['ratio']) + ' ' + \
                  '{0:>19s}'.format(ALL_RESULT[i]['time']) + color_end

        elif type == 'stock':
            if (i == 0 or last_type != 'stock'):
                print '\n' + title_color + ' 股號     股名     成交價     漲跌    百分比   成交量    資料時間 & 狀態' + color_end
                print '---------------------------------------------------------------------------------'

            # print all data
            print item_color + ' ' + \
                  '{0:s}'   .format(ALL_RESULT[i]['id']) + '\t ' + ALL_RESULT[i]['name'] + '\t' + \
                  '{0:>9s}' .format(ALL_RESULT[i]['price']) + ' ' + \
                  '{0:>8s}' .format(ALL_RESULT[i]['change']) + ' ' + \
                  '{0:>8s}%'.format(ALL_RESULT[i]['ratio']) + ' ' + \
                  '{0:>8s}' .format(ALL_RESULT[i]['volume']) + ' ' + \
                  '   ' + ALL_RESULT[i]['time'] + color_end

    if show_simple == False:
        if auto_update:
            print datetime.now().strftime('\nLast updated: %Y.%m.%d %H:%M:%S')
        else:
            print ''


def get_tw_future():
    sign = ''
    future = future_parser()
    future.feed(urllib.urlopen("http://info512.taifex.com.tw/Future/FusaQuote_Norl.aspx").read())
    future.close()

    if (future.data[1] == '收盤'):
        price   = float(future.data[6].replace(',',''))
        change  = float(future.data[7])
        volume  = future.data[9].replace(',','')
        time_str = future.data[14] + ' (close)'
        last_day_price = float(future.data[13].replace(',',''))
        ratio   = '{0:.02f}'.format(change / last_day_price * 100)
        highest = float(future.data[11].replace(',',''))
        lowest = float(future.data[12].replace(',',''))
    else:
        price   = float(future.data[5].replace(',',''))
        change  = float(future.data[6])
        volume  = future.data[8].replace(',','')
        time_str = future.data[13]
        last_day_price = float(future.data[12].replace(',',''))
        ratio   = '{0:.02f}'.format(change / last_day_price * 100)
        highest = float(future.data[10].replace(',',''))
        lowest = float(future.data[11].replace(',',''))

    if change > 0:
        sign = '+'
    else:
        sign = ''

    status = ''
    if price == highest:
        status = u' 最高'
    elif price == lowest:
        status = u' 最低'

    change_str = sign + '{0:.0f} '.format(change)
    ratio_str = sign + ratio

    result = {'id':'', 'name':'', 'price':'', 'change':'', 'ratio':'', 'volume':'', 'time': '', 'type':''}
    result['id']     = 'WTX'
    result['name']   = '台指期'
    result['price']  = '{0:.0f} '.format(price)
    result['change'] = change_str
    result['ratio']  = ratio_str
    result['volume'] = volume
    result['time']   = time_str + status
    result['type']   = 'stock'
    ALL_RESULT.append(result)


def timezone_diff(timezone):
    gmt = timezone.find('GMT')
    if gmt != -1:
        return 8 - int(timezone[gmt + 3:])
    elif timezone.find('EDT') != -1:
        return 8 - (-4)
    else:
        print 'unknown timezone: ' + timezone
        return 0

def add_result_to_list(json_str, stock_type):
    # read json data
    json_data = json.loads(json_str)
    now = datetime.now()

    if stock_type == 'world':
        for i in range(len(INDEX_LIST)):
            result = []
            j = json_data[i]
            id = INDEX_LIST[i][1]

            ratio = j["cp"]
            if ratio.find('-'):
                ratio = '+' + ratio

            result_time = datetime.strptime(j["lt_dts"], '%Y-%m-%dT%H:%M:%SZ') + timedelta(hours = timezone_diff(j['lt']))

            if (now-result_time).total_seconds() < 1800:
                time_str = str(result_time.strftime('%H:%M:%S        '))
            elif now.month == result_time.month and now.day == result_time.day:
                time_str = str(result_time.strftime('%H:%M:%S (today)'))
            else:
                time_str = str(result_time.strftime('%H:%M:%S (%m/%d)'))

            result = {'id':'', 'name':'', 'price':'', 'change':'', 'ratio':'', 'volume':'', 'time': '', 'type':''}
            result['id']     = id
            result['name']   = INDEX_LIST[i][2]
            result['price']  = j["l"].replace(',','')
            result['change'] = j["c"]
            result['ratio']  = ratio
            result['volume'] = ' '
            result['time']   = time_str
            result['type']   = 'index'
            ALL_RESULT.append(result)

    elif stock_type == 'tw':
        # FIXME: console sometimes show "KeyError: 'msgArray'"
        for i in range(len(json_data['msgArray'])):
            h_limit = -1
            l_limit = -1
            highest = -1
            lowest = -1
            status = ''

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
            name = j["n"]
            volume = j["v"]

            highest = float(j['h'])
            lowest = float(j['l'])

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

            # FIXME: To avoid stock name too long
            if len(name) > 4:
                name = stock_no

            result = {'id':'', 'name':'', 'price':'', 'change':'', 'ratio':'', 'volume':'', 'time': '', 'type':''}
            result['id']     = stock_no
            result['name']   = name
            result['price']  = price
            result['change'] = change_str
            result['ratio']  = change_str_p
            result['volume'] = volume
            result['time']   = time_str + status
            result['type']   = 'stock'
            ALL_RESULT.append(result)


def add_tw_stock_to_query_list(stock_no):
    global TW_STOCK_QUERY_LIST

    for i in TW_STOCK_QUERY_LIST:
        if i == stock_no:
            return

    TW_STOCK_QUERY_LIST.append(stock_no)


def create_tw_query_list(add_stock_list, argv):
    global TW_STOCK_QUERY_LIST
    TW_STOCK_QUERY_LIST = []

    # add stocks in argv to stock list
    for i in argv:
        if i[:1] == '-':
            continue;
        USER_STOCK_LIST.append(i)

    # add stock list to query list
    if add_stock_list:
        for i in USER_STOCK_LIST:
            add_tw_stock_to_query_list(str(i).upper())


def create_tw_stock_url(add_twse):
    url = TWSE_URL
    if add_twse:
        url = url + 'tse_t00.tw|otc_o00.tw|'

    for i in TW_STOCK_QUERY_LIST:
        url = url + search_stock(i)

    return url


def create_world_index_url():
    url = GOOGLE_URL
    for item in INDEX_LIST:
        url = url + item[0] + ','

    return url


# query world index:
def get_world_index_info(url):
    result = requests.get(url)
    json_str = remove_special_char(result.content.replace('// ', '', 1))
    add_result_to_list(json_str, 'world')


# query taiwan stock:
def get_tw_stock_info(url):
    #   access the index first and then send request for stock list
    r = requests.session()
    r.get('http://' + TWSE_SERVER + '/stock/index.jsp', headers = {'Accept-Language':'zh-TW'}, timeout=5)
    result = r.get(url)

    json_str = result.content
    add_result_to_list(json_str, 'tw')


def main():
    argv = sys.argv
    count = 0
    add_world = False
    add_twse = False
    add_stock_list = False
    show_simple = False
    auto_update = False
    hidden_help = False
    hide_closed_index = False
    global color_print

    if len(argv) == 1 and \
       SHOW_TWSE_INDEX == False and \
       SHOW_WORLD_INDEX == False and \
       ADD_USER_STOCK_LIST == False:
        # no parameter, show usage()
        usage()
        exit()

    # remote program name
    del argv[0]

    # read parameters
    for x in argv:
        if str(x) == '-c':
            color_print = True
        elif str(x) == '-a':
            add_world = True
            add_twse = True
            add_stock_list = True
        elif str(x) == '-w':
            add_world = True
        elif str(x) == '-i':
            add_twse = True
        elif str(x) == '-q':
            add_stock_list = True
        elif str(x) == '-s':
            show_simple = True
            add_stock_list = True
        elif str(x) == '-d':
            auto_update = True
        elif str(x) == '-h' or str(x) == '--help':
            usage()
            exit()

    # load default setting
    if SIMPLE_OUTPUT:
        show_simple = True
    if COLORFUL_OUTPUT:
        color_print = True
    if SHOW_TWSE_INDEX:
        add_twse = True
    if SHOW_WORLD_INDEX:
        add_world = True
    if ADD_USER_STOCK_LIST:
        add_stock_list = True

    # generate query url
    create_tw_query_list(add_stock_list, argv)
    tw_url = create_tw_stock_url(add_twse)
    world_url = create_world_index_url()

    # show usage() if there is no index or stock
    if tw_url == TWSE_URL and add_world == False:
        usage()
        exit()

    while True:
        # access google finance for world index
        if add_world:
            get_world_index_info(world_url)

        if add_twse:
            get_tw_future()

        # access twse server for taiwan stock
        if tw_url != TWSE_URL:
            get_tw_stock_info(tw_url)

        print_result(show_simple, auto_update, hide_closed_index);

        if auto_update == False:
            break

        del ALL_RESULT[:]

        # receive input command to do something
        if not hidden_help:
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
                color_print = not color_print
            elif input == 'S':
                show_simple = not show_simple
            elif input == 'I':
                add_twse = not add_twse
            elif input == 'W':
                add_world = not add_world
            elif input == 'U':
                add_stock_list = not add_stock_list
            elif input == 'H':
                hidden_help = not hidden_help
            elif input == 'X':
                hide_closed_index = not hide_closed_index
            elif input[:1] == '+' and len(input) > 1:
                append_stock = True
                for i in USER_STOCK_LIST:
                    if i == input[1:]:
                           append_stock = False;
                if append_stock:
                    USER_STOCK_LIST.append(input[1:])

            elif input[:1] == '-' and len(input) > 1:
                for i in USER_STOCK_LIST:
                    if i == input[1:]:
                        USER_STOCK_LIST.remove(i)
                        break

            # update taiwan stock query list
            create_tw_query_list(add_stock_list, '')
            tw_url = create_tw_stock_url(add_twse)
            break

if __name__ == '__main__':
    main()