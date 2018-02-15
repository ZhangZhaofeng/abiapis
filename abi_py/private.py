#!/usr/bin/python3
# coding=utf-8

from tradingapis.bittrex_api import bittrex
from tradingapis.huobi_api import huobi
from tradingapis.bitflyer_api import pybitflyer
from tradingapis.bitbank_api import public_api
from tradingapis.zaif_api.impl import ZaifPublicApi,ZaifTradeApi
from tradingapis.quoine_api import client
# from tradingapis.quoine_api.client import Quoinex
from tradingapis.quoine_api import client



class AutoTrading:

    def __init__(self):
        print("Initializing API")
        self.bitflyer_api=pybitflyer.API(api_key="xxx...", api_secret="yyy...")
        self.zaif_api = ZaifTradeApi(key="xxx...", secret="yyy...")
        self.quoinex_api = client.Quoinex(api_token_id="xxx...", api_secret="yyy...")


    def trade_bitflyer(self, type, size=0.01):
        print("trade bitflyer")
        if type == "BUY":
            self.bitflyer_api.sendchildorder(product_code="BTC_JPY",
                                             child_order_type="MARKET",
                                             side="BUY",
                                             size=0.01,
                                             minute_to_expire=10000,
                                             time_in_force="GTC"
                                             )
        elif type == "SELL":
            self.bitflyer_api.sendchildorder(product_code="BTC_JPY",
                                             child_order_type="MARKET",
                                             side="SELL",
                                             size=0.01,
                                             minute_to_expire=10000,
                                             time_in_force="GTC"
                                             )
        else:
            print("error!")


    def trade_quoniex(self,type, size=0.01):
        print("trade_quoniex")
        products = self.quoinex_api.get_products()

        if type=="BUY":
            order = self.quoinex_api.create_market_buy(
                product_id=products[5]['id'],
                quantity=str(size))
        elif type=="SELL":
            order = self.quoinex_api.create_market_sell(
                product_id=products[5]['id'],
                quantity=str(size))
        else:
            print("error!")


    def trade_zaif(self):
        print("trade_zaif")

        zaifpublicApi = ZaifPublicApi()
        # zaifpublicApi.last_price ('btc_jpy')

        jsons_dict = zaifpublicApi.ticker('btc_jpy')
        bid = jsons_dict['result']['Bid']
        ask = jsons_dict['result']['Ask']

        self.zaif_api.trade(
            currency_pair='btc_jpy',
            action='bid',
            price=500000,
            amount=0.8
        )

    def trade_bitbank(self):
        print("trade_bitbank")



if __name__ == '__main__':
    print("Shooting")



