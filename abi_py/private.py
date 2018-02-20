#!/usr/bin/python3
# coding=utf-8

from tradingapis.bitflyer_api import pybitflyer
from tradingapis.bitbank_api import public_api, private_api
from tradingapis.zaif_api.impl import ZaifPublicApi, ZaifTradeApi
from tradingapis.zaif_api.api_error import *
from tradingapis.quoine_api import client
import apis
import keysecret as ks


class AutoTrading:
    def __init__(self):
        print("Initializing API")
        self.bitflyer_api = pybitflyer.API(api_key=str(ks.bitflyer_api), api_secret=str(ks.bitflyer_secret))
        self.zaif_api = ZaifTradeApi(key=str(ks.zaif_api), secret=str(ks.zaif_secret))
        self.quoinex_api = client.Quoinex(api_token_id=str(ks.quoinex_api), api_secret=(ks.quoinex_secret))
        self.bitbank_api = private_api.bitbankcc_private(api_key=str(ks.bitbank_api), api_secret=str(ks.bitbank_secret))

    def trade_bitflyer(self, type, amount=0.001):
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
                                             size=amount,
                                             minute_to_expire=10000,
                                             time_in_force="GTC"
                                             )
        else:
            print("error!")

    def trade_quoinex(self, type, amount=0.001):
        print("trade_quoniex")
        products = self.quoinex_api.get_products()
        pid = 5
        for product in products:
            # print(product['currency_pair_code'])
            if product['currency_pair_code'] == 'BTCJPY':
                pid = int(product['id'])

        if type == "BUY" or type == "buy":
            order = self.quoinex_api.create_market_buy(
                product_id=pid,
                quantity=str(amount))
        elif type == "SELL" or type == "sell":
            order = self.quoinex_api.create_market_sell(
                product_id=pid,
                quantity=str(amount))
        else:
            print("error!")

    def trade_zaif(self, type, amount=0.001):
        print("trade_zaif")

        margin_ratio = 0.05
        # [bid, ask] = apis.get_bid_ask_zaif('btc_jpy')
        # bid = float(bid)
        # ask = float(ask)
        zaifpublic = ZaifPublicApi()
        last_price = int(zaifpublic.last_price(currency_pair='btc_jpy')["last_price"])

        if type == "BUY" or type == "buy":
            price = int(last_price * (1 + margin_ratio))
            self.zaif_api.trade(
                currency_pair='btc_jpy',
                action='bid',
                price=price,
                amount=amount
            )
        elif type == "SELL" or type == "sell":
            price = int(last_price * (1 - margin_ratio))
            self.zaif_api.trade(
                currency_pair='btc_jpy',
                action='ask',
                price=price,
                amount=amount
            )
        else:
            print("error!")

    def trade_bitbank(self, type, amount=0.001):
        print("trade_bitbank")
        margin_ratio = 0.05
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

    def get_asset_bitbank(self):
        balances = self.bitbank_api.get_asset()
        jpy_avai = 0.0
        btc_avai = 0.0
        for balance in balances['assets']:
            if balance['asset'] == 'jpy':
                jpy_avai = float(balance['onhand_amount'])
            if balance['asset'] == 'btc':
                btc_avai = float(balance['onhand_amount'])
        return ([jpy_avai, btc_avai])

    def get_asset_bitflyer(self):
        balances = self.bitflyer_api.getbalance(product_code="BTC_JPY")
        jpy_avai = 0.0
        btc_avai = 0.0
        for balance in balances:
            if balance['currency_code'] == 'JPY':
                jpy_avai = float(balance['available'])
            elif balance['currency_code'] == 'BTC':
                btc_avai = float(balance['available'])
        return ([jpy_avai, btc_avai])

    def get_asset_quoinex(self):
        balances = self.quoinex_api.get_account_balances()
        jpy_avai = 0.0
        btc_avai = 0.0
        for balance in balances:
            if balance['currency'] == 'BTC':
                btc_avai = float(balance['balance'])
            elif balance['currency'] == 'JPY':
                jpy_avai = float(balance['balance'])

        return ([jpy_avai, btc_avai])

    def get_asset_zaif(self):
        infos = self.zaif_api.get_info()
        btc_avai = float(infos['funds']['btc'])
        jpy_avai = float(infos['funds']['jpy'])
        return ([jpy_avai, btc_avai])

    def get_bank_info(self, bankname):
        [jpy_avai, btc_avai] = [0., 0.]
        [bid, ask] = [0., 0.]
        if bankname == "quoinex":
            [jpy_avai, btc_avai] = self.get_asset_quoinex()
            [bid, ask] = apis.get_bid_ask_quoinex('BTC_JPY')
        elif bankname == "bitbank":
            [jpy_avai, btc_avai] = self.get_asset_bitbank()
            [bid, ask] = apis.get_bid_ask_bitbank('BTC_JPY')
        elif bankname == "bitflyer":
            [jpy_avai, btc_avai] = self.get_asset_bitflyer()
            [bid, ask] = apis.get_bid_ask_bitflyer('BTC_JPY')
        elif bankname == "zaif":
            [jpy_avai, btc_avai] = self.get_asset_zaif()
            [bid, ask] = apis.get_bid_ask_zaif('BTC_JPY')

        return [bid, ask, jpy_avai, btc_avai]

    def execute_trade(self, bankname, action, amount):
        print("execute_trade")

        while 1:
            try:
                if bankname == "quoinex":
                    self.trade_quoinex(action, amount)
                elif bankname == "bitbank":
                    self.trade_bitbank(action, amount)
                elif bankname == "bitflyer":
                    self.trade_bitflyer(action, amount)
                elif bankname == "zaif":
                    self.trade_zaif(action, amount)

                print(bankname, action, "orded.")
                break
            except ZaifServerException:
                print("ZaifServerException catched while trading, trying again.")
                continue
            except Exception:
                print("Other exception catched while trading, trying again.")
                continue

        return True

    def judge_asset(self, bankname, action, amount):
        if not (self.check(bankname, action, amount)):
            return False

        [bid, ask, jpy_avai, btc_avai] = self.get_bank_info(bankname)

        if action == "buy" or action == "BUY":
            if amount * ask > jpy_avai * 1.01:
                print("Buy power is not enough!")
                return False
        elif action == "sell" or action == "SELL":
            if amount > btc_avai or amount < 0.001:
                print("Sell power is not enough!")
                return False

        return True

    def check(self, bankname, action, amount):
        if action != "buy" and action != "sell" and action != "BUY" and action != "SELL":
            print("Action invalid!")
            return False

        if bankname != "quoinex" and bankname != "zaif" and bankname != "bitbank" and bankname != "bitflyer":
            print("Bankname invalid!")
            return False

        if amount < 0.001:
            print("Amount invalid!")
            return False

        return True


class Plan:
    def __init__(self, _buybank, _sellbank, _tradable_percent=1.0):
        self.buybank = _buybank
        self.sellbank = _sellbank
        assert (_tradable_percent >= 0. and _tradable_percent <= 1.)
        self.tradable_percent = _tradable_percent


class Arbitrage:
    def __init__(self):
        print("Initializing Arbitrage"
              ""
              "")
        self.autotrade = AutoTrading()

    def arbitrage_once(self, buy_bankname, sell_bankname, amount=0.001):
        print("arbitrage_once")
        while 1:
            try:
                result1 = self.autotrade.judge_asset(buy_bankname, "buy", amount)
                result2 = self.autotrade.judge_asset(sell_bankname, "sell", amount)
                break
            except Exception:
                print("Exception catched while judging asset, trying again.")
                continue

        if not (result1 and result2):
            return False

        print("Both banks asset OK")

        self.autotrade.execute_trade(buy_bankname, "buy", amount)
        self.autotrade.execute_trade(sell_bankname, "sell", amount)
        return True

    def get_tradable_btc_amount(self, bankinfo, action):
        ratio = 0.98

        [bid, ask, jpy_avai, btc_avai] = bankinfo

        if action == "buy" or action == "BUY":
            return float(jpy_avai / ask * ratio)
        elif action == "sell" or action == "SELL":
            return float(btc_avai * ratio)

    def get_plan_eval(self, plan):
        buybankinfo = self.autotrade.get_bank_info(plan.buybank)
        sellbankinfo = self.autotrade.get_bank_info(plan.sellbank)
        percentage = plan.tradable_percent

        tradable_btc = min([self.get_tradable_btc_amount(buybankinfo, "buy"),
                            self.get_tradable_btc_amount(sellbankinfo, "sell")])

        price_diff = sellbankinfo[0] - buybankinfo[1]
        estm_profit = price_diff * tradable_btc * percentage

        print([price_diff, tradable_btc, estm_profit])
        return [price_diff, tradable_btc, estm_profit]


if __name__ == '__main__':
    print("Arb")
    mytrade = AutoTrading()
    # print(mytrade.get_asset_bitflyer())

    # trading example
    # mytrade.execute_trade(bankname="bitbank", action="sell", amount=0.001)

    # arb info example
    myarbitrage = Arbitrage()
    # plan = Plan(_buybank="zaif", _sellbank="bitflyer", _tradable_percent=1.0)
    # myarbitrage.get_plan_eval(plan)

    # arb trading example
    if myarbitrage.arbitrage_once("quoinex","zaif", 0.001) == True:
        print("Successfully Executed!")
