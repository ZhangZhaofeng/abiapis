#!/usr/bin/python3
# coding=utf-8

import private


if __name__ == '__main__':
    print("Arb")
    mytrade = private.AutoTrading()
    # print(mytrade.get_asset_quoinex())
    # mytrade.execute_trade("quoinex", "buy", 0.027)
    # arb info example
    banklist=["zaif", "quoinex","bitflyer","bitbank"]
    # banklist = ["quoinex", "bitflyer", "bitbank"]
    myarbitrage = private.Arbitrage(banklist)

    # myarbitrage.run()

    banks_info=myarbitrage.get_all_bankinfo()
    myarbitrage.print_all_plan_eval(banks_info)
    myarbitrage.print_total_asset(banks_info)