#!/usr/bin/python3
# coding=utf-8

from tradingapis.bitflyer_api import pybitflyer
from tradingapis.bitbank_api import public_api, private_api
from tradingapis.zaif_api.impl import ZaifPublicApi, ZaifTradeApi
from tradingapis.zaif_api.api_error import *
from tradingapis.quoine_api import client
import apis
import my_secret as ks
import time
import copy


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
            order = self.bitflyer_api.sendchildorder(product_code="BTC_JPY",
                                                     child_order_type="MARKET",
                                                     side="BUY",
                                                     size=amount,
                                                     minute_to_expire=10000,
                                                     time_in_force="GTC"
                                                     )
        elif type == "SELL" or type == "sell":
            order = self.bitflyer_api.sendchildorder(product_code="BTC_JPY",
                                                     child_order_type="MARKET",
                                                     side="SELL",
                                                     size=amount,
                                                     minute_to_expire=10000,
                                                     time_in_force="GTC"
                                                     )
        else:
            print("error!")
        print(order)

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

        print(order)

    def trade_zaif(self, type, amount=0.001):
        print("trade_zaif")

        margin_ratio = 0.05
        # [bid, ask] = apis.get_bid_ask_zaif('btc_jpy')
        # bid = float(bid)
        # ask = float(ask)
        zaifpublic = ZaifPublicApi()
        last_price = round(zaifpublic.last_price(currency_pair='btc_jpy')["last_price"], 1)

        if type == "BUY" or type == "buy":
            price = int(last_price * (1 + margin_ratio))
            order = self.zaif_api.trade(
                currency_pair='btc_jpy',
                action='bid',
                price=price,
                amount=amount
            )
        elif type == "SELL" or type == "sell":
            price = int(last_price * (1 - margin_ratio))
            order = self.zaif_api.trade(
                currency_pair='btc_jpy',
                action='ask',
                price=price,
                amount=amount
            )
        else:
            print("error!")
        print(order)

    def trade_bitbank(self, type, amount=0.001):
        print("trade_bitbank")
        margin_ratio = 0.05
        [bid, ask] = apis.get_bid_ask_bitbank('btc_jpy')
        if type == "BUY" or type == "buy":
            order = self.bitbank_api.order(pair='btc_jpy',
                                           price=str(ask * (1 + margin_ratio)),
                                           amount=str(amount),
                                           side='buy',
                                           order_type="market")
        elif type == "SELL" or type == "sell":
            order = self.bitbank_api.order(pair='btc_jpy',
                                           price=str(bid * (1 - margin_ratio)),
                                           amount=str(amount),
                                           side='sell',
                                           order_type='market')
        else:
            print("error!")

        print(order)

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

    def get_asset_from_bank(self, bankname):
        if bankname == "zaif":
            [jpy_avai, btc_avai] = self.get_asset_zaif()
        elif bankname == "quoinex":
            [jpy_avai, btc_avai] = self.get_asset_quoinex()
        elif bankname == "bitflyer":
            [jpy_avai, btc_avai] = self.get_asset_bitflyer()
        elif bankname == "bitbank":
            [jpy_avai, btc_avai] = self.get_asset_bitbank()
        else:
            print("Bankname error")
            [jpy_avai, btc_avai] = [0., 0.]
        return [jpy_avai, btc_avai]

    def judge_asset_change(self, bankname, original_asset, trade_type):
        [current_jpy_avai, current_btc_avai] = self.get_asset_from_bank(bankname)
        [original_jpy_avai, original_btc_avai] = original_asset

        if trade_type == "buy" or trade_type == "BUY":
            if current_jpy_avai < original_jpy_avai:
                return True
        elif trade_type == "sell" or trade_type == "SELL":
            if current_btc_avai < original_btc_avai:
                return True

        return False

    def get_bank_personal_info(self, bankname):
        [jpy_avai, btc_avai] = [0., 0.]
        [bid, ask] = [0., 0.]
        [buyable_btc, sell_btc] = [0., 0.]
        margin_ratio = 0.05  # increasing the value to prevent trading failure
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

        buyable_btc = jpy_avai / ask * (1 - margin_ratio)
        if buyable_btc < 0.001:
            buyable_btc = 0.
        sellable_btc = btc_avai * (1 - margin_ratio)
        if sellable_btc < 0.001:
            sellable_btc = 0.

        return [bid, ask, jpy_avai, btc_avai, buyable_btc, sellable_btc, bankname]

    def execute_trade(self, bankname, action, amount):
        print("execute_trade")

        trytimes = 100
        i = 0
        while i < trytimes:
            i += 1
            print('Try to %s at %s @ %d time' % (action, bankname, i))
            try:
                if bankname == "quoinex":
                    self.trade_quoinex(action, amount)
                elif bankname == "bitbank":
                    self.trade_bitbank(action, amount)
                elif bankname == "bitflyer":
                    self.trade_bitflyer(action, amount)
                elif bankname == "zaif":
                    self.trade_zaif(action, amount)

                print('%s %f @%s orded' % (action, amount, bankname))
                return True
            except ZaifServerException:
                print("ZaifServerException catched while trading, trying again.")
                time.sleep(0.5)
                continue
            except Exception:
                print("Other exception catched while trading, trying again.")
                time.sleep(0.5)
                continue
        return False

    def judge_tradable(self, bankname, action, amount):
        if not (self.check(bankname, action, amount)):
            return False

        bankinfo = self.get_bank_personal_info(bankname)

        if action == "buy" or action == "BUY":
            if amount > bankinfo[4]:
                print("Buy power is not enough!")
                return False
        elif action == "sell" or action == "SELL":
            if amount > bankinfo[5]:
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
    def __init__(self, _buybankinfo, _sellbankinfo, _tradable_percent=1.0):
        self.buybankinfo = _buybankinfo
        self.sellbankinfo = _sellbankinfo
        assert (_tradable_percent >= 0. and _tradable_percent <= 1.)
        self.tradable_percent = _tradable_percent


class Arbitrage:
    def __init__(self):
        print("Initializing Arbitrage"
              ""
              "")
        self.autotrade = AutoTrading()
        self.DIFF_PRICE_SHELHOLD = 1000

    def arbitrage_once(self, buy_bankname, sell_bankname, amount=0.001):
        print("arbitrage_once")
        while 1:
            try:
                result1 = self.autotrade.judge_tradable(buy_bankname, "buy", amount)
                result2 = self.autotrade.judge_tradable(sell_bankname, "sell", amount)
                break
            except Exception:
                print("Exception catched while judging asset, trying again.")
                continue

        if not (result1 and result2):
            return False

        print("Both banks asset OK")

        if buy_bankname == "zaif":
            self.autotrade.execute_trade(buy_bankname, "buy", amount)
            self.autotrade.execute_trade(sell_bankname, "sell", amount)
        elif sell_bankname == "zaif":
            self.autotrade.execute_trade(sell_bankname, "sell", amount)
            self.autotrade.execute_trade(buy_bankname, "buy", amount)
        else:
            self.autotrade.execute_trade(sell_bankname, "sell", amount)
            self.autotrade.execute_trade(buy_bankname, "buy", amount)

        return True

    def execute_plan_trade(self, plan):
        buy_bank = plan.buybankinfo[6]
        sell_bank = plan.sellbankinfo[6]
        print("execute_plan_trade. BUY:", buy_bank, "SELL:", sell_bank)
        percent = plan.tradable_percent
        assert (percent > 0.0 and percent <= 1.0)
        amount = percent * min([plan.buybankinfo[4], plan.sellbankinfo[5]])

        amount = round(amount, 3)
        print(amount)

        if amount < 0.001:
            print("Amount not enough")
            return False

        if buy_bank == "zaif":
            if self.autotrade.execute_trade(buy_bank, "buy", amount):
                self.autotrade.execute_trade(sell_bank, "sell", amount)
        elif sell_bank == "zaif":
            if self.autotrade.execute_trade(sell_bank, "sell", amount):
                self.autotrade.execute_trade(buy_bank, "buy", amount)
        else:
            if self.autotrade.execute_trade(buy_bank, "buy", amount):
                self.autotrade.execute_trade(sell_bank, "sell", amount)

        return True

    def judge_arb_order_success(self, plan):
        buy_bank = plan.buybankinfo[6]
        sell_bank = plan.sellbankinfo[6]

        original_buybank_asset = [plan.buybankinfo[2], plan.buybankinfo[3]]
        original_sellbank_asset = [plan.sellbankinfo[2], plan.sellbankinfo[3]]

        if self.autotrade.judge_asset_change(buy_bank, original_buybank_asset, "buy"):
            print(buy_bank, "buy order verified")
        if self.autotrade.judge_asset_change(sell_bank, original_sellbank_asset, "sell"):
            print(sell_bank, "sell order verified")

    def get_plan_eval(self, plan):
        buybankinfo = plan.buybankinfo
        sellbankinfo = plan.sellbankinfo
        percentage = plan.tradable_percent

        tradable_btc = min([buybankinfo[4],
                            sellbankinfo[5]])

        price_diff = sellbankinfo[0] - buybankinfo[1]
        estm_profit = price_diff * tradable_btc * percentage

        return [price_diff, tradable_btc, estm_profit]

    def get_all_bankinfo(self):
        banks_info = []
        while 1:
            try:
                zaifinfo = self.autotrade.get_bank_personal_info("zaif")
                quoinexinfo = self.autotrade.get_bank_personal_info("quoinex")
                bitflyerinfo = self.autotrade.get_bank_personal_info("bitflyer")
                bitbankinfo = self.autotrade.get_bank_personal_info("bitbank")
                banks_info = [zaifinfo, quoinexinfo, bitflyerinfo, bitbankinfo]
                break
            except ZaifServerException:
                print("ZaifServerException while reading info, trying again.")
                time.sleep(1)
                continue
            except Exception:
                print("Error.")
                time.sleep(1)
                continue

        return banks_info

    def print_all_plan_eval(self, banks_info):
        for buy_bank_info in banks_info:
            for sell_bank_info in banks_info:
                if buy_bank_info != sell_bank_info:
                    plan = Plan(buy_bank_info, sell_bank_info)
                    print("BUY:", buy_bank_info[6], "SELL:", sell_bank_info[6])
                    print(self.get_plan_eval(plan))

        print(" ")

    def print_total_asset(self, banks_info):
        total_btc = 0.0
        total_jpy = 0.0
        for each_bank_info in banks_info:
            total_jpy += each_bank_info[2]
            total_btc += each_bank_info[3]

        print("total_btc:", total_btc)
        print("total_jpy:", total_jpy)

    def run_stragedy(self, banks_info):
        max_price_diff = 0.
        for buy_bank_info in banks_info:
            for sell_bank_info in banks_info:
                if buy_bank_info != sell_bank_info:
                    plan = Plan(buy_bank_info, sell_bank_info, 1.0)
                    [price_diff, tradable_btc, estm_profit] = self.get_plan_eval(plan)
                    if price_diff > max_price_diff and tradable_btc * plan.tradable_percent > 0.001:
                        max_price_diff = price_diff
                        best_plan = copy.deepcopy(plan)

        if max_price_diff > self.DIFF_PRICE_SHELHOLD and max_price_diff != 0.:
            if self.execute_plan_trade(best_plan):
                print("One stragedy executed")

    def run(self):
        print("Start!")

        while 1:
            banks_info = self.get_all_bankinfo()
            self.print_all_plan_eval(banks_info)
            self.print_total_asset(banks_info)
            self.run_stragedy(banks_info)  # real-trading
            time.sleep(1)


if __name__ == '__main__':
    print("Arb")
    mytrade = AutoTrading()
    # mytrade.execute_trade("bitflyer", "buy", 0.0000001)
    # arb info example
    myarbitrage = Arbitrage()

    myarbitrage.run()

    # myarbitrage.arbitrage_once("zaif","quoinex",0.045)
