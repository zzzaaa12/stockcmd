#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import select
import time
from os import system as system
from time import sleep as sleep
from datetime import datetime

# files in this project
from taiwan_stock import TaiwanStock
from setting import AUTO_UPDATE_SECOND
from setting import DEFAULT_PROFILE


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
    print '    -c: list with color'
    print '    -d: continue update information every ' + str(AUTO_UPDATE_SECOND) + ' seconds'
    print '    -h: show this page'
    print ''
    print 'Example:'
    print '    stockcmd.py -i'
    print '    stockcmd.py -u'
    print '    stockcmd.py 2330 2317 3008'
    print ''


def read_option(opt):
    if len(opt) == 0:
        usage()
        exit()

    profile = DEFAULT_PROFILE

    for x in opt:
        if str(x) == '-c':
            profile['color_print'] = True
        elif str(x) == '-a':
            profile['show_twse_index'] = True
        elif str(x) == '-i':
            profile['show_twse_index'] = True
        elif str(x) == '-s':
            profile['show_simple'] = True
            profile['monitor_help'] = False
        elif str(x) == '-d':
            profile['monitor_mode'] = True
        elif str(x) == '-h' or str(x) == '--help':
            usage()
            exit()

    return profile


def update_profile(profile, interval):

    count = 0
    for x in range(0, interval):
        count = count + 1
        refresh = False;
        input_cmd = ''
        i, o, e = select.select([sys.stdin], [], [], 1)
        if not i:
            continue
        input = sys.stdin.readline().strip().upper()
        if input == 'Q':
            print 'Exit? (Y/N)'
            ans = sys.stdin.readline().strip().upper()
            if ans == 'Y' or ans == 'Q':
                exit()
        elif input == 'C':
            profile['color_print'] = not profile['color_print']
            refresh = True
        elif input == 'S':
            profile['show_simple'] = not profile['show_simple']
            profile['monitor_help'] = not profile['show_simple']
            refresh = True
        elif input == 'H':
            profile['monitor_help'] = not profile['monitor_help']
            refresh = True
        elif input == 'I':
            profile['show_twse_index'] = not profile['show_twse_index']
            refresh = True
        elif input[:1] == '+' and len(input) > 1:
            profile['append_stock'] = input[1:]
            refresh = True
        elif input[:1] == '-' and len(input) > 1:
            profile['remove_stock'] = input[1:]
            refresh = True
        break

    return {'count':count, 'refresh':refresh}


def main():
    argv = sys.argv
    # remove program name
    del argv[0]
    profile = read_option(argv)
    tw_stock = TaiwanStock(argv)

    # if it is not monitor mode, just run once
    while True:
        start_time = time.time()

        # read data
        tw_result = tw_stock.get_data(profile)

        # show usage page when no stock or index
        if tw_result == False:
            usage()
            exit()

        # clear monitor
        if profile['monitor_mode']:
            system('clear')

        # print tw stock
        if tw_result:
            tw_stock.print_stock_info(profile)

        if not profile['monitor_mode']:
            exit()

        last_update_time = datetime.now().strftime('%Y.%m.%d %H:%M:%S')
        print ' Elapsed time: {0:.2f}s'.format(time.time()-start_time)
        print ' Last updated: ' + last_update_time
        if profile['monitor_help']:
                print ' Commands: Q->Exit, C->Color, S->Simple, I->TWSE, U->User\'s List,'
                print '           +-[stock] -> add or remove stock'

        # renew profile
        update = update_profile(profile, AUTO_UPDATE_SECOND)
        update_count = update['count']
        while update_count < AUTO_UPDATE_SECOND:
            if update['refresh']:
                system('clear')
                if tw_result:
                    # show old data within AUTO_UPDATE_SECOND
                    tw_stock.print_stock_info(profile)
                print ' Updating.....'
                print ' Last updated: ' + str(last_update_time)
                if profile['monitor_help']:
                        print ' Commands: Q->Exit, C->Color, S->Simple, I->TWSE, U->User\'s List,'
                        print '           +-[stock] -> add or remove stock'

            else:
                print 'The setting will apply after ' + str(AUTO_UPDATE_SECOND - update_count) + ' secs'

            update = update_profile(profile, AUTO_UPDATE_SECOND - update_count)
            update_count = update_count + update['count']

        # append or remove stock
        if len(profile['append_stock']):
            tw_stock.append_stock(profile['append_stock'])
            profile['append_stock'] = ''
        elif len(profile['remove_stock']):
            tw_stock.remove_stock(profile['remove_stock'])
            profile['remove_stock'] = ''

if __name__ == '__main__':
    main()
