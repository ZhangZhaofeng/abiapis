#!/usr/bin/python3
# coding=utf-8

import private


if __name__ == '__main__':
    print("limit_trade")
    mytrade = private.AutoTrading()
    # print(mytrade.get_asset_quoinex())
    mytrade.execute_trade("zaif", "buy", 0.003)

    banklist = ["zaif", "quoinex", "bitflyer", "bitbank"]
    myarbitrage = private.Arbitrage(banklist)
    banks_info = myarbitrage.get_all_bankinfo()
    myarbitrage.print_total_asset(banks_info)