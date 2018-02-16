#!/usr/bin/python3
# coding=utf-8

from tradingapis.bitflyer_api import pybitflyer
from tradingapis.bitbank_api import public_api, private_api
from tradingapis.zaif_api.impl import ZaifPublicApi, ZaifTradeApi
from tradingapis.quoine_api import client
import apis


class AutoTrading:
    def __init__(self):
        print("Initializing API")
        self.bitflyer_api = pybitflyer.API(api_key="xxx...", api_secret="yyy...")
        self.zaif_api = ZaifTradeApi(key="xxx...", secret="yyy...")
        self.quoinex_api = client.Quoinex(api_token_id="xxx...", api_secret="yyy...")
        self.bitbank_api = private_api.bitbankcc_private(api_key="xxx...", api_secret="yyy...")

    def trade_bitflyer(self, type, amount=0.01):
        print("trade bitflyer")
        if type == "BUY" or type == "buy":
            self.bitflyer_api.sendchildorder(product_code="BTC_JPY",
                                             child_order_type="MARKET",
                                             side="BUY",
                                             size=amount,
                                             minute_to_expire=10000,
                                             time_in_force="GTC"
                                             )
        elif type == "SELL" or type == "sell":
            self.bitflyer_api.sendchildorder(product_code="BTC_JPY",
                                             child_order_type="MARKET",
                                             side="SELL",
                                             size=0.01,
                                             minute_to_expire=10000,
                                             time_in_force="GTC"
                                             )
        else:
            print("error!")

    def trade_quoniex(self, type, amount=0.01):
        print("trade_quoniex")
        products = self.quoinex_api.get_products()

        if type == "BUY" or type == "buy":
            order = self.quoinex_api.create_market_buy(
                product_id=products[5]['id'],
                quantity=str(amount))
        elif type == "SELL" or type == "sell":
            order = self.quoinex_api.create_market_sell(
                product_id=products[5]['id'],
                quantity=str(amount))
        else:
            print("error!")

    def trade_zaif(self, type, amount=0.01):
        print("trade_zaif")

        margin_ratio = 0.1
        [bid, ask] = apis.get_bid_ask_zaif('btc_jpy')

        if type == "BUY" or type == "buy":
            self.zaif_api.trade(
                currency_pair='btc_jpy',
                action='ask',
                price=ask * (1 + margin_ratio),
                amount=amount
            )
        elif type == "SELL" or type == "sell":
            self.zaif_api.trade(
                currency_pair='btc_jpy',
                action='bid',
                price=bid * (1 - margin_ratio),
                amount=amount
            )
        else:
            print("error!")

    def trade_bitbank(self, type, amount=0.01):
        print("trade_bitbank")
        margin_ratio = 0.1
        [bid, ask] = apis.get_bid_ask_bitbank('btc_jpy')
        if type == "BUY" or type == "buy":
            self.bitbank_api.order(pair='btc_jpy',
                                   price=str(ask * (1 + margin_ratio)),
                                   amount=str(amount),
                                   side='buy',
                                   order_type="market")
        elif type == "SELL" or type == "sell":
            self.bitbank_api.order(pair='btc_jpy',
                                   price=str(bid * (1 - margin_ratio)),
                                   amount=str(amount),
                                   side='sell',
                                   order_type='market')
        else:
            print("error!")


if __name__ == '__main__':
    print("Shooting")
