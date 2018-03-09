#!/usr/bin/python3
# coding=utf-8


import auto_arb

#import json





if __name__=='__main__':
    autotrading = auto_arb.MyAutoTrading()
    logfile = './profit_log'
    possible_market = ['zaif', 'bitbank', 'bitflyer', 'quoinex']
    print(possible_market)
    autotrading.calculate_captial(possible_market)
    autotrading.calculate_all_captial()
    auto_arb.print_and_write(autotrading.currency1, logfile)
    auto_arb.print_and_write(autotrading.currency2, logfile)
    auto_arb.print_and_write(autotrading.allcurrency1, logfile)
    auto_arb.print_and_write(autotrading.allcurrency2, logfile)