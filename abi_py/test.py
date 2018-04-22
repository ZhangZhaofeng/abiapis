#!/usr/bin/python3


from tradingapis.bittrex_api import bittrex
from tradingapis.huobi_api import huobi
#from tradingapis.binance_api import client,exceptions
from tradingapis.bitflyer_api import pybitflyer
from tradingapis.bitbank_api import public_api

import apis
import private




from timeit import Timer
import time
import threading

def test_api_time():
    execute_list=['print_bittrex','print_huobi','print_bitflyer','print_bitbank']
    for i in execute_list:
        from_str = 'from __main__ import %s'%(i)
        execute_str = '%s()'%(i)

        t1 = Timer(execute_str, from_str)
        print(t1.timeit(1))

def get_bid_ask_huobi(product_pair):
    if product_pair == '':
        product_pair = 'BTC_USDT'
    elif product_pair =='BTC_ETH':
        product_pair = 'ethbtc'
    elif product_pair =='BTC_LTC':
        product_pair = 'ltcbtc'
    jsons_dict = huobi.get_ticker(product_pair)
    bid = jsons_dict['tick']['bid'][0]
    ask = jsons_dict['tick']['ask'][0]
    return([bid,ask])

def get_bid_ask_bittrex(product_pair):
    if product_pair == '':
        product_pair = 'BTC_USDT'
    elif product_pair =='BTC_ETH':
        product_pair = 'BTC-ETH'
    elif product_pair =='BTC_LTC':
        product_pair = 'BTC-LTC'
    bittrex_api = bittrex.Bittrex('', '')
    #jsons_dict = bittrex_api.get_markets()
    jsons_dict = bittrex_api.get_ticker(product_pair)
    bid = jsons_dict['result']['Bid']
    ask = jsons_dict['result']['Ask']
    return([bid,ask])

#def ask_huobi():
 #   huobi.get_ticker()

def get_bid_ask_bitbank(product_pair):
    if product_pair == 'BTC_JPY':
        product_pair = 'btc_jpy'
    elif product_pair =='BTC_ETH':
        product_pair = 'eth_btc'
    bitbank_api = public_api.bitbankcc_public()
    jsons_dict = bitbank_api.get_ticker(product_pair)
    ask = float(jsons_dict['sell'])
    bid = float(jsons_dict['buy'])
    return ([bid, ask])

def get_bid_ask_bitflyer(product_pair):
    if product_pair == '':
        product_pair = 'BTC_JPY'
    elif product_pair =='BTC_ETH':
        product_pair = 'ETH_BTC'
    elif product_pair =='BTC_LTC':
        product_pair = 'LTC_BTC'
    bitflyer_api = pybitflyer.API()
    jsons_dict = bitflyer_api.ticker(product_code='%s'%(product_pair))
    bid = jsons_dict['best_bid']
    ask = jsons_dict['best_ask']
    return ([bid, ask])


def calculate_rate(result_bid_ask1,result_bid_ask2):

    direction = 0
    # if 1's sell bigger than 2's buy
    if result_bid_ask1[0] > result_bid_ask2[1]:
        sell = result_bid_ask1[0]
        buy = result_bid_ask2[1]
        direction = 2 # buy at 2 sell at 1
    # if 2's sell bigger than 1's buy
    elif result_bid_ask2[1] > result_bid_ask1[0]:
        sell = result_bid_ask1[1]
        buy = result_bid_ask2[0]
        direction = 1 # buy at 1 sell at 2
    else:
        return (0,0)

    return((sell-buy)/sell*100,direction)


def trading_fees(rate, market):

    if market == 'bittrex':
        fees = 0.25
    elif market =='bitflyer':
        fees = 0.13
    else:
        fees = 0
    return(rate - fees)


if __name__=='__main__':
    #btcbox_api = '3r8mg-q4ez1-8puq6-9vbhg-twbr5-aqeah-cd8jz'
    #btcbox_secret = 'Vn78n-7s(*3-af%AU-ukNR$-X(Uai-fCMz3-LarSh'
    #from tradingapis.btcbox_api import apis
    #aps = apis.API(btcbox_api, btcbox_secret)
    #print(aps.ticker())
    #print(aps.balance())

    #print(apis.get_bid_ask_btcbox(''))
    au = private.AutoTrading()

    print(au.get_bank_personal_info('btcbox'))
    print(au.judge_tradable('btcbox','sell',0.13))
