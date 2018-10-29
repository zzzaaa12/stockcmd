#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import select
import time
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
    print '    -a: show all stock infomation (include TSE, OTC, other stock)'
    print '    -s: show information with simple format'
    print '    -i: show TWSE index, TWSE Future and OTC index'
    print '    -t: show TWSE stocks (includes user list)'
    print '    -w: show International Stock Indexes'
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


def monitor_help():
    print ''
    print ' Commands: Q->Exit, C->Color, S->Simple, I->TWSE, W->World, U->User\'s List'
    print '      X->Hide closed index, +-[stock] -> add or remove stock'


def elapsed_time(time_diff, last):
    print ''
    print ' Elapsed time: {0:.2f}s'.format(time_diff)
    print ' Last updated: ' + last


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
            profile['show_tw_stock'] = True
        elif str(x) == '-w':
            profile['show_world_index'] = True
        elif str(x) == '-i':
            profile['show_twse_index'] = True
        elif str(x) == '-t':
            profile['show_tw_stock'] = True
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
        elif input == 'T':
            profile['show_tw_stock'] = not profile['show_tw_stock']
            refresh = True
        elif input == 'W':
            profile['show_world_index'] = not profile['show_world_index']
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

    # create objects
    world = WorldIndex()
    world_result = False
    tw_stock = TaiwanStock(argv)

    # if it is not monitor mode, just run once
    while True:
        start_time = time.time()
        time_diff = 0

        # read data
        if profile['show_world_index']:
            world_result = world.get_data()

        tw_result = tw_stock.get_data(profile)

        # show usage page when no stock or index
        if tw_result == False and world_result == False:
            usage()
            exit()

        # clear monitor
        if profile['monitor_mode']:
            system('clear')

        # print world index
        if profile['show_world_index'] and world_result:
            world.print_stock_info(profile)

        # print tw stock
        if tw_result:
            tw_stock.print_stock_info(profile)

        last_update_time = datetime.now().strftime('%Y.%m.%d %H:%M:%S')
        time_diff = time.time() - start_time
        elapsed_time(time_diff, last_update_time)

        # motitor mode
        if not profile['monitor_mode']:
            exit()

        if profile['monitor_help']:
            monitor_help()

        # renew profile
        update = update_profile(profile, AUTO_UPDATE_SECOND)
        update_count = update['count']
        renew_now = False
        while update_count < AUTO_UPDATE_SECOND:
            if update['refresh']:

                if profile['show_world_index'] and world_result == False:
                    renew_now = True
                elif len(profile['append_stock']):
                    tw_stock.append_stock(profile['append_stock'])
                    profile['append_stock'] = ''
                    renew_now = True
                elif len(profile['remove_stock']):
                    tw_stock.remove_stock(profile['remove_stock'])
                    profile['remove_stock'] = ''
                    renew_now = True
                elif profile['show_twse_index']:
                    renew_now = True
                elif profile['show_tw_stock']:
                    renew_now = True

                if renew_now:
                    print 'Updating.....'
                    break

                system('clear')
                if profile['show_world_index'] and world_result:
                    world.print_stock_info(profile)

                if tw_result:
                    # show old data within AUTO_UPDATE_SECOND
                    tw_stock.print_stock_info(profile)

                if profile['monitor_help']:
                    monitor_help()

            else:
                print 'The setting will apply after ' + str(AUTO_UPDATE_SECOND - update_count) + ' secs'

            update = update_profile(profile, AUTO_UPDATE_SECOND - update_count)
            update_count = update_count + update['count']


if __name__ == '__main__':
    main()
