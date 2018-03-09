#!/usr/bin/python3
# coding=utf-8

import private
import marketing_qu
from tradingapis.bitbank_api import public_api


def get_depth():
    bitbank_api = public_api.bitbankcc_public()
    product_pair = 'btc_jpy'
    depth = bitbank_api.get_depth(product_pair)
    return(depth)


if __name__ == '__main__':
    # print("limit_trade")
    # mytrade = private.AutoTrading()
    # # print(mytrade.get_asset_quoinex())
    # mytrade.execute_trade("bitbank", "buy", 0.01)
    #
    # banklist = ["zaif", "quoinex", "bitflyer", "bitbank"]
    # myarbitrage = private.Arbitrage(banklist)
    # banks_info = myarbitrage.get_all_bankinfo()
    # myarbitrage.print_total_asset(banks_info)
    trade_class = marketing_qu.AutoTradingForMarketing_quoine()


    e = trade_class.get_last_executions()
    print(e)
    e = trade_class.get_orders()
    print(e)
    e = get_depth()
    print(e['bids'][1])
    #e = trade_class.cancle_order(224852585)
    #e = trade_class.cancle_order(224829082)
    #trade_class.trade_zaif_limit('sell', 935100, 0.1)
    #trade_class.trade_quoine_limit('buy', '935000' ,'0.1')
    #trade_class.trade_bitbank_limit('buy', )
    trade_class.trade_bitbank_limit('buy', '929800', '0.15')
