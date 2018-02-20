#!/usr/bin/python3
# coding=utf-8


from tradingapis.bittrex_api import bittrex
from tradingapis.huobi_api import huobi
from tradingapis.bitflyer_api import pybitflyer
from tradingapis.bitbank_api import public_api
from tradingapis.zaif_api.impl import ZaifPublicApi, ZaifTradeApi
from tradingapis.quoine_api import client

from timeit import Timer
import time

import threading
#import json


def print_quoine():
    quoine_api = client.Quoine()
    print(quoine_api.get_product(5))


def print_zaif():
    zaif_api = ZaifPublicApi()
    print(zaif_api.ticker('btc_jpy'))


def print_bittrex():
    bittrex_api = bittrex.Bittrex('', '')
    print(bittrex_api.get_markets())


def print_huobi():
    print(huobi.get_ticker('btcusdt'))


def print_bitflyer():
    bitflyer_api = pybitflyer.API()
    print(bitflyer_api.ticker(product_code="BTC_JPY"))


def print_bitbank():
    bitbank_api = public_api.bitbankcc_public()
    print(bitbank_api.get_ticker('eth_btc'))
    print(bitbank_api.get_depth('eth_btc'))


def test_api_time():
    execute_list = ['print_bittrex', 'print_huobi', 'print_bitflyer', 'print_bitbank']
    for i in execute_list:
        from_str = 'from __main__ import %s' % (i)
        execute_str = '%s()' % (i)

        t1 = Timer(execute_str, from_str)
        print(t1.timeit(1))


def get_bid_ask_huobi(product_pair):
    if product_pair == '':
        product_pair = 'BTC_USDT'
    elif product_pair == 'BTC_ETH':
        product_pair = 'ethbtc'
    elif product_pair == 'BTC_LTC':
        product_pair = 'ltcbtc'
    jsons_dict = huobi.get_ticker(product_pair)
    bid = jsons_dict['tick']['bid'][0]
    ask = jsons_dict['tick']['ask'][0]
    return [bid, ask]


def get_bid_ask_bittrex(product_pair):
    if product_pair == '':
        product_pair = 'BTC_USDT'
    elif product_pair == 'BTC_ETH':
        product_pair = 'BTC-ETH'
    elif product_pair == 'BTC_LTC':
        product_pair = 'BTC-LTC'
    bittrex_api = bittrex.Bittrex('', '')
    # jsons_dict = bittrex_api.get_markets()
    jsons_dict = bittrex_api.get_ticker(product_pair)
    bid = jsons_dict['result']['Bid']
    ask = jsons_dict['result']['Ask']
    return [bid, ask]


# def ask_huobi():
#   huobi.get_ticker()

def get_bid_ask_bitbank(product_pair):
    if product_pair == 'BTC_JPY':
        product_pair = 'btc_jpy'
    elif product_pair == 'BTC_ETH':
        product_pair = 'eth_btc'
    bitbank_api = public_api.bitbankcc_public()
    jsons_dict = bitbank_api.get_ticker(product_pair)
    ask = float(jsons_dict['sell'])
    bid = float(jsons_dict['buy'])
    return [bid, ask]


def get_bid_ask_bitflyer(product_pair):
    if product_pair == '':
        product_pair = 'BTC_JPY'
    elif product_pair == 'BTC_ETH':
        product_pair = 'ETH_BTC'
    elif product_pair == 'BTC_LTC':
        product_pair = 'LTC_BTC'
    bitflyer_api = pybitflyer.API()
    jsons_dict = bitflyer_api.ticker(product_code='%s' % (product_pair))
    bid = jsons_dict['best_bid']
    ask = jsons_dict['best_ask']
    return [bid, ask]

def get_bid_ask_zaif(product_pair):
    if product_pair == 'BTC_JPY':
        product_pair = 'btc_jpy'
    else:
        product_pair = ''
    zaif_api =ZaifPublicApi()
    jsons_dict = zaif_api.ticker(product_pair)
    bid = jsons_dict['bid']
    ask = jsons_dict['ask']
    return ([bid, ask])
#TODO
#def get_bid_ask_quoine():

def get_bid_ask_quoine(product_pair):
    if product_pair == 'BTC_JPY':
        product_pair = 5
    else:
        product_pair = ''

    quoine_api = client.Quoine()
    jsons_dict = quoine_api.get_product(product_pair)
    bid = jsons_dict['market_bid']
    ask = jsons_dict['market_ask']
    return([bid, ask])


def get_bid_ask_zaif(product_pair):
    if product_pair == 'BTC_JPY':
        product_pair = 'btc_jpy'
    zaif_api = ZaifPublicApi()
    ticker = zaif_api.ticker(product_pair)
    bid = float(ticker['bid'])
    ask = float(ticker['ask'])
    return [bid, ask]


def get_bid_ask_quoinex(product_pair):
    if product_pair == 'btc_jpy' or product_pair == 'BTC_JPY':
        product_pair = 'BTCJPY'
    quoinex_api = client.Quoinex()
    [bid, ask] = [0., 0.]
    products = quoinex_api.get_products()
    for product in products:
        # print(product['currency_pair_code'])
        if product['currency_pair_code'] == product_pair:
            id = int(product['id'])
            bid = int(product['market_bid'])
            ask = int(product['market_ask'])
    return [bid, ask]


def calculate_rate(result_bid_ask1, result_bid_ask2):
    direction = 0
    # if 1's sell bigger than 2's buy
    if result_bid_ask1[0] > result_bid_ask2[1]:
        sell = result_bid_ask1[0]
        buy = result_bid_ask2[1]
        direction = 2  # buy at 2 sell at 1
    # if 2's sell bigger than 1's buy
    elif result_bid_ask2[0] > result_bid_ask1[1]:
        sell = result_bid_ask2[0]
        buy = result_bid_ask1[1]
        direction = 1  # buy at 1 sell at 2
    else:
        return (0, 0)

    return ((sell - buy) / sell * 100, direction)


def trading_fees(rate, market):
    if market == 'bittrex':
        fees = 0.25
    elif market == 'bitflyer':
        fees = 0.13
    else:
        fees = 0
    return (rate - fees)


def write_record(fname, rate, direction, str1, str2):
    fid = open(fname, 'a')
    if direction == 1:
        buy = str1
        sell = str2
    else:
        buy = str2
        sell = str1

    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
    write_str = 'buy: %s, sell: %s, profit: %f %% time: %s \n' % (buy, sell, rate, time_str)
    fid.write(write_str)
    fid.close()

#def print_rate(result_bid_ask1, string1, result_bid_ask2, string2):


if __name__ == '__main__':
    #print_bitbank()

    product_pair = 'BTC_JPY'
    #print_huobi()

    class Mythread(threading.Thread):
        def __init__(self,target,args):
            super(Mythread,self).__init__()
            self.target = target
            self.args = args

        def run(self):
            self.result = self.target(*self.args)
        def get_result(self):
            try:
                return self.result
            except Exception:
                return None


    t_zaif = Mythread(target=get_bid_ask_zaif, args=(product_pair,))
    t_quoine = Mythread(target=get_bid_ask_quoine, args=(product_pair,))
    t_bitbank = Mythread(target=get_bid_ask_bitbank, args=(product_pair,))
    t_bitflyer = Mythread(target=get_bid_ask_bitflyer, args=(product_pair,))

    t_zaif.start()
    t_quoine.start()
    t_bitbank.start()
    t_bitflyer.start()

    while 1:
        try:
            t_zaif.run()
            t_quoine.run()
            t_bitbank.run()
            t_bitflyer.run()
            t_zaif.join(timeout=1)
            t_quoine.join(timeout=1)
            t_bitbank.join(timeout=1)
            t_bitflyer.join(timeout=1)
            print(t_zaif.get_result())
            print(t_quoine.get_result())
            print(t_bitbank.get_result())
            print(t_bitflyer.get_result())
        except Exception:
            print('Error')
        time.sleep(1)

    #print_zaif()
    #print_quoine()
    #results_zaif = get_bid_ask_zaif(product_pair)
    #results_bitflyer = get_bid_ask_bitflyer(product_pair)
    #[rate, direction]=calculate_rate(results_zaif, results_bitflyer)

    #try:
    #    try_error(x)
    #except:
    #    print('not_value')
    #product_pair = 'BTC_JPY'

    #print(time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime()))
    #fname1 = '/home/zhang/Templates/recording2.txt'
    #fname2 = '/home/zhang/Templates/recording4.txt'
    #fname3 = '/home/zhang/Templates/recording6.txt'

    #fid = open(fname1,'w')
    #fid.close()
    #fid = open(fname2, 'w')
    #fid.close()
    #fid = open(fname3, 'w')
    #fid.close()
    #threadhold1 = 2
    #threadhold2 = 4
    #threadhold3 = 6
    #str_bitflyer = 'bitflyer'
    #str_bittrex = 'bittrex'
    #str_huobi = 'huobi'
    #str_bitbank = 'bitbank'

    #while 1:
        #results_bitflyer = get_bid_ask_bitflyer(product_pair)
      #  results_bittrex = get_bid_ask_bittrex(product_pair)
      #  results_bitbank = get_bid_ask_bitbank(product_pair)
       # results_huobi = get_bid_ask_huobi(product_pair)
        #compute_and_record(results_bitflyer, results_bittrex, results_bitbank, results_huobi, threadhold1, fname1)
        #compute_and_record(results_bitflyer, results_bittrex, results_bitbank, results_huobi, threadhold2, fname2)
        #compute_and_record(results_bitflyer, results_bittrex, results_bitbank, results_huobi, threadhold3, fname3)
        #time.sleep(10)
