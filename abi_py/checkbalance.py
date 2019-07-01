#!/usr/bin/python3
# coding=utf-8


import auto_arb_no_offset





if __name__=='__main__':
    autotrading = auto_arb_no_offset.MyAutoTrading()
    logfile = './profit_log'
    possible_market = ['zaif', 'bitbank', 'bitflyer', 'quoinex', 'btcbox', 'coincheck']
    print(possible_market)
    autotrading.calculate_captial(possible_market)
    autotrading.calculate_all_captial()
    auto_arb_no_offset.print_and_write(autotrading.currency1, logfile)
    auto_arb_no_offset.print_and_write(autotrading.currency2, logfile)
    auto_arb_no_offset.print_and_write(autotrading.allcurrency1, logfile)
    auto_arb_no_offset.print_and_write(autotrading.allcurrency2, logfile)