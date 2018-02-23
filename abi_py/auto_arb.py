
#!/usr/bin/python3

import observer,private,keysecret

from tradingapis.bitflyer_api import pybitflyer
from tradingapis.bitbank_api import public_api, private_api
from tradingapis.zaif_api.impl import ZaifPublicApi, ZaifTradeApi
from tradingapis.zaif_api.api_error import *
from tradingapis.quoine_api import client
import apis
import keysecret as ks
import memcache
import time


class MyAutoTrading(private.AutoTrading):
    currency1 = [0.0] * 4
    currency2 = [0.0] * 4
    allcurrency1 = 0
    allcurrency2 = 0
    initlize = [0] * 4


    def __init__(self):

        print("Initializing API")
        try:
            self.zaif_api = ZaifTradeApi(key=str(ks.zaif_api), secret=str(ks.zaif_secret))
        except Exception:
            print('Cant initialize Zaif API')
            self.initlize[0] = 1
        try:
            self.quoinex_api = client.Quoinex(api_token_id=str(ks.quoinex_api), api_secret=(ks.quoinex_secret))
        except Exception:
            print('Cant initialize Quoinex API')
            self.initlize[1] = 1

        try:
            self.bitbank_api = private_api.bitbankcc_private(api_key=str(ks.bitbank_api),
                                                             api_secret=str(ks.bitbank_secret))
        except Exception:
            print('Cant initialize Bitbank API')
            self.initlize[2] = 1

        try:
            self.bitflyer_api = pybitflyer.API(api_key=str(ks.bitflyer_api), api_secret=str(ks.bitflyer_secret))
        except Exception:
            print('Cant initialize bitflyer API')
            self.initlize[3] = 1

    def execute_trade(self, bankname, action, amount):
        print("execute_trade")

        trytimes = 20
        i = 0
        while i< trytimes:
            i += 1
            print('Try to %s at %s @ %d time'%(action, bankname, i))
            try:
                if bankname == "quoinex":
                    self.trade_quoinex(action, amount)
                elif bankname == "bitbank":
                    self.trade_bitbank(action, amount)
                elif bankname == "bitflyer":
                    self.trade_bitflyer(action, amount)
                elif bankname == "zaif":
                    self.trade_zaif(action, amount)

                print('%s %f @%s orded'%(action, amount, bankname))
                return 0
            except ZaifServerException:
                print("ZaifServerException catched while trading, trying again.")
                time.sleep(0.5)
                continue
            except Exception:
                print("Other exception catched while trading, trying again.")
                time.sleep(0.5)
                continue
        return 1

    def calculate_captial(self, possible_market):
        for i in possible_market:
            if i == 'zaif':
                temp = self.get_asset_zaif()
                self.currency1[0] = temp[0]
                self.currency2[0] = temp[1]
            elif i== 'quoinex':
                temp = self.get_asset_quoinex()
                self.currency1[1] = temp[0]
                self.currency2[1] = temp[1]
            elif i == 'bitbank':
                temp = self.get_asset_bitbank()
                self.currency1[2] = temp[0]
                self.currency2[2] = temp[1]
            elif i == 'bitflyer':
                temp = self.get_asset_bitflyer()
                self.currency1[3] = temp[0]
                self.currency2[3] = temp[1]

    def calculate_all_captial(self):
        len_market = len(self.currency1)
        self.allcurrency1 = 0.0
        self.allcurrency2 = 0.0
        for i in range(0,len_market):
            self.allcurrency1 += self.currency1[i]
            self.allcurrency2 += self.currency2[i]

class MyArbitrage(private.Arbitrage):
    def __init__(self):
        print("Initializing Arbitrage"
              ""
              "")
        self.autotrade = MyAutoTrading()
        self.DIFF_PRICE_SHELHOLD=-10000

    def arbitrage_once(self, buy_bankname, sell_bankname, amount=0.001):
        print("arbitrage_once")
        trytimes = 20
        i = 0
        while i < trytimes:
            i += 1
            try:
                result1 = self.autotrade.judge_tradable(buy_bankname, "buy", amount)
                result2 = self.autotrade.judge_tradable(sell_bankname, "sell", amount)
                break
            except Exception:
                print("Exception catched while judging asset, trying again.")
                continue

        if not (result1 and result2):
            return 2

        print("Both banks asset OK")

        if buy_bankname == "zaif":
            trading_flag1 = self.autotrade.execute_trade(buy_bankname, "buy", amount)
            if trading_flag1 == 0:
                trading_flag2 = self.autotrade.execute_trade(sell_bankname, "sell", amount)
                if trading_flag2 == 0:
                    return 0
                else:
                    return 4
            else:
                return 5
        else:
            trading_flag1 = self.autotrade.execute_trade(sell_bankname, "sell", amount)
            if trading_flag1 == 0:
                trading_flag2 = self.autotrade.execute_trade(buy_bankname, "buy", amount)
                if trading_flag2 == 0:
                    return 0
                else:
                    return 3
            else:
                return 5
        return 6

    def arb_trade(self, buy, sell, amount):
        result = self.arbitrage_once(buy, sell, amount)

        if result == 3: # if failed to buy at buy side.  buy at sell side now
            print('Sold at %s but Failed to buy at %s. Try to buy at %s now' % (sell ,buy, sell))
            trytimes = 20
            i = 0
            result2 = False
            while i < trytimes:
                i += 1
                try:
                    result2 = self.autotrade.judge_tradable(sell, 'buy', amount)
                    break
                except Exception:
                    print("Exception catched while judging asset, trying again.")
                    continue
            if not result2:
                return 3
            result3 = self.autotrade.execute_trade(sell, "buy", amount)
            if result3 == 1:
                return 3
            else:
                return 7

        elif result == 4: # if failed to sell at sell side. sell at buy side now
            print('Bought at %s but Failed to sell at %s. Try to sell at %s now'%(buy ,sell, buy))
            trytimes = 20
            i = 0
            result2 = False
            while i < trytimes:
                i += 1
                try:
                    result2 = self.autotrade.judge_tradable(buy, 'sell', amount)
                    break
                except Exception:
                    print("Exception catched while judging asset, trying again.")
                    continue
            if not result2:
                return 4
            result3 = self.autotrade.execute_trade(buy, 'sell' , amount)
            if result3 == 1:
                return 4
            else:
                return 7

        else:
            return result
        # return 0 succeed and can do it again
        # return 1 succeed but need offset
        # return 2 both failed since no money need offset
        # return 3 only buy failed since connection problem
        # return 4 only sell failed since connection problem
        # return 5 both failed since connection problem
        # return 6 both failed since unknown problem
        # return 7 only buy failed and buy at sell side
        # return 8 only sell failed and sell at buy side

    def offset_trade(self, buy, sell):
        return 0
        # return 0 succeed
        # return 2 both failed since no money
        # return 2 both failed since connection problem
        # return 3 buy failed since connection problem
        # return 4 sell failed
        # return 5 others
        # return 7 only buy failed and buy at sell side
        # return 8 only sell failed and sell at buy side


#def simulate_arbtriage(arb_chance, offset_chance):

def find_market_index(buy_sell_pairs, trading_pairs):
    index = -1
    for i in trading_pairs:
        index += 1
        if buy_sell_pairs == i:
            return index
    return -1






if __name__ == '__main__':
    autotrading = MyAutoTrading()
    arbobject = MyArbitrage()
    possible_market = ['zaif', 'bitbank', 'bitflyer']

    trading_pairs = observer.get_offset_pairs(possible_market, True)
    pairs_number = len(trading_pairs)

    # all pairs has a arb label at first time for 0:arb  for 1:offset  for 2:initial
    arb_label = [2]*pairs_number
    arb_poss_label = [0]*pairs_number
    setoff_poss_label = [0]*pairs_number

    check_balance =1
    if check_balance:
        autotrading.calculate_captial(possible_market)
        autotrading.calculate_all_captial()
        print(autotrading.currency1)
        print(autotrading.currency2)
        print(autotrading.allcurrency1)
        print(autotrading.allcurrency2)


    #zaif2 = autotrading.get_asset_zaif()

    shared = memcache.Client(['127.0.0.1:11211'], debug=0)


    if_arb = 0

    while if_arb:
        arb_chance = shared.get('arb_chance')
        offset_chance = shared.get('offset_chance')

        print(arb_chance)
        print(offset_chance)

    # find arb chance
        for i in arb_chance:
            buy_sell_pairs = [i[0],i[2]]
            index=find_market_index(buy_sell_pairs, trading_pairs)
            if index > -1:
                arb_poss_label[index] = 1
        print(arb_poss_label)

    # find offset chance
        for j in offset_chance:
            buy_sell_pairs = [j[0], j[2]]
            index = find_market_index(buy_sell_pairs, trading_pairs)
            if index > -1:
                setoff_poss_label[index] = 1
        print(setoff_poss_label)


        for i in range(0,pairs_number):
            # if there is profit in this arb and we can arb, do it after that mark it as offsetable
            if arb_poss_label[i]==1 and (arb_label[i] == 2 or arb_label[i] == 1):
                print('It is good time to preform arb to buy @ %s and sell @ %s '%(trading_pairs[i][0],trading_pairs[i][1] ))
                #TODO banzhuan
                arb_result = arbobject.arb_trade(trading_pairs[i][0], trading_pairs[i][1], amount=0.02)
                if arb_result == 0:
                    print('Arb succeed, sleep 5 seconds')
                    time.sleep(5)
                else:
                    print('Arb failed code %d'%arb_result)
                    break


            # if there is a pair need to offset and it is possible, do it
            #if setoff_poss_label[i] == 1 and arb_label[i] == 0:
                #TODO pingcang
            #    if succeed(pingcang):
            #    arb_label[i] = 1