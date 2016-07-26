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
from common import AUTO_UPDATE_SECOND

# TODO:
#      (v) monitor mode
#      ( ) cmd of monitor mode
#      (v) colorful print
#      (v) important status change
#      (v) limit up/down print


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
    if len(opt) == 0:
        usage()
        exit()

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
    tw_stock = TaiwanStock(argv)

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
