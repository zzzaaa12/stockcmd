#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import select
from os import system as system
from time import sleep as sleep
from datetime import datetime

# files in this project
from world_index import WorldIndex
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
    print '    -w: list International Stock Indexes'
    print '    -u: list stocks predefined in "setting.py"'
    print '    -c: list with color'
    print '    -d: continue update information every ' + str(AUTO_UPDATE_SECOND) + ' seconds'
    print '    -h: show this page'
    print ''
    print 'Example:'
    print '    stockcmd.py -i'
    print '    stockcmd.py -w'
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
            profile['show_world_index'] = True
            profile['show_twse_index'] = True
            profile['show_user_list'] = True
        elif str(x) == '-w':
            profile['show_world_index'] = True
        elif str(x) == '-i':
            profile['show_twse_index'] = True
        elif str(x) == '-u':
            profile['show_user_list'] = True
        elif str(x) == '-s':
            profile['show_simple'] = True
        elif str(x) == '-d':
            profile['monitor_mode'] = True
        elif str(x) == '-h' or str(x) == '--help':
            usage()
            exit()

    return profile


def update_profile(profile):

    if profile['monitor_help']:
            print ' Commands: Q->Exit, C->Color, S->Simple, I->TWSE, W->World, U->User\'s List'
            print '           X->Hide closed index,  +-[stock] -> add or remove stock'

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
            profile['show_twse_index'] = not profile['show_twse_index']
        elif input == 'W':
            profile['show_world_index'] = not profile['show_world_index']
        elif input == 'U':
            profile['show_user_list'] = not profile['show_user_list']
        elif input == 'H':
            profile['monitor_help'] = not profile['monitor_help']
        elif input == 'X':
            profile['hide_closed_index'] = not profile['hide_closed_index']
        elif input[:1] == '+' and len(input) > 1:
            profile['append_stock'] = input[1:]
        elif input[:1] == '-' and len(input) > 1:
            profile['remove_stock'] = input[1:]
        break


def main():
    argv = sys.argv
    # remove program name
    del argv[0]
    profile = read_option(argv)

    # create objects
    world = WorldIndex()
    tw_stock = TaiwanStock(argv)

    # if it is not monitor mode, just run once
    while True:
        # read data
        if profile['show_world_index']:
            world.get_data()
        tw_result = tw_stock.get_data(profile)

        # show usage page when no stock or index
        if tw_result == False and profile['show_world_index'] == False:
            usage()
            exit()

        # clear monitor
        if profile['monitor_mode']:
            system('clear')
            print ''

        # print world index
        if profile['show_world_index']:
            world.print_stock_info(profile)

        # print tw stock
        if tw_result:
            tw_stock.print_stock_info(profile)

        if not profile['monitor_mode']:
            exit()

        print datetime.now().strftime(' Last updated: %Y.%m.%d %H:%M:%S')

        # renew profile
        update_profile(profile)

        # append or remove stock
        if len(profile['append_stock']):
            tw_stock.append_stock(profile['append_stock'])
            profile['append_stock'] = ''
        elif len(profile['remove_stock']):
            tw_stock.remove_stock(profile['remove_stock'])
            profile['remove_stock'] = ''


if __name__ == '__main__':
    main()
