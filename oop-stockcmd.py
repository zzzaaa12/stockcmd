#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys


#class world_index:
#    def __init__(self):
#    def create_url:

#class tool:
#    def get_unique_list
#
#

class taiwan_stock:
    def __init__(self):
        self.user_stock_list = ['00632r','4127','2330','2317']
        self.stock_list = []
        self.data = []
        self.twse_url = 'http://220.229.103.179/stock/api/getStockInfo.jsp?ex_ch='


    def create_stock_list(self):
        self.stock_list = []
        tmp_list = []

        # add stock in user list
        for i in self.user_stock_list:
            tmp_list.append(str(i).upper())

        # add stock in argv
        for i in sys.argv:
            if i.find('-') == -1:
                tmp_list.append(i.upper())

        # check duplicate and create stock `list
        seen = set()
        for i in tmp_list:
            if i not in seen:
                self.stock_list.append(i)
                seen.add(i)

        # XXX test
        print self.stock_list


    def create_query_url(self):
        print 'xx'

def main():
    # remote program name
    argv = sys.argv
    del argv[0]

    # read parameters
    for x in argv:
        if str(x) == '-c':
            color_print = True
        elif str(x) == '-a':
            show_world = True
            show_twse = True
            show_stock_list = True
        elif str(x) == '-w':
            show_world = True
        elif str(x) == '-i':
            show_twse = True
        elif str(x) == '-q':
            show_stock_list = True
        elif str(x) == '-s':
            show_simple = True
            show_stock_list = True
        elif str(x) == '-d':
            monitor_mode = True
        elif str(x) == '-h' or str(x) == '--help':
            usage()
            exit()

    # test
    print "main()"   
    tw_stock = taiwan_stock()
    tw_stock.create_stock_list() 


if __name__ == '__main__':
    main()
