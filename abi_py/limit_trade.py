#!/usr/bin/python3
# coding=utf-8

import private


if __name__ == '__main__':
    print("limit_trade")
    mytrade = private.AutoTrading()
    # print(mytrade.get_asset_quoinex())
    mytrade.execute_trade("quoinex", "buy", 0.027)