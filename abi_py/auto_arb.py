
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
    market_number = 4
    currency1 = [0.0] * market_number
    currency2 = [0.0] * market_number
    allcurrency1 = 0
    allcurrency2 = 0
    initlize = [0] * market_number


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
        trytimes = 20
        i = 0
        while i< trytimes:
            i += 1
            print('Try to %s @ %s @ %d time'%(action, bankname, i))
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

    def get_asset(self,market):
        if market == 'zaif':
            return(self.get_asset_zaif())
        elif market == 'quoinex':
            return(self.get_asset_quoinex())
        elif market == 'bitbank':
            return(self.get_asset_bitbank())
        elif market == 'bitflyer':
            return(self.get_asset_bitflyer())
        else:
            print('Error, specific a market')
            return([.0,.0])


    def calculate_captial(self, possible_market):

        for i in range(0, len(possible_market)):
            try_times = 20
            while try_times > 0:
                try:
                    temp = self.get_asset(possible_market[i])
                    self.currency1[i] = temp[0]
                    self.currency2[i] = temp[1]
                    break
                except Exception:
                    print ('Exception occured during ask captial @ %s, try last %d time'%(possible_market[i],try_times))
                    try_times -= 1




    def calculate_all_captial(self):
        self.allcurrency1 = 0.0
        self.allcurrency2 = 0.0
        for i in range(0,self.market_number):
            self.allcurrency1 += self.currency1[i]
            self.allcurrency2 += self.currency2[i]

class MyArbitrage(private.Arbitrage):
    def __init__(self):
        print("Initializing Arbitrage"
              ""
              "")
        self.autotrade = MyAutoTrading()
        self.DIFF_PRICE_SHELHOLD=-10000

    def arbitrage_once(self, buy_bankname, sell_bankname, if_judge_tradable, amount=0.001, ):

        if if_judge_tradable:
            print("Judge if it can trade once")
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
        else:
            print('Start to balance once')

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

    def arb_trade(self, buy, sell, amount, if_judge_tradable=True):
        result = self.arbitrage_once(buy, sell,if_judge_tradable, amount)

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

    # find the largest buy sell able amount
    def plan_max_mount(self, buy_asset, sell_asset , buy, sell, market_price, market_list):
        floating_mount = 0.95
        max_amount = 0.0
        buy_index = market_list.index(buy)
        #sell_index = market_list.index(sell)
        buy_price = market_price[buy_index][1]
        canbuy = (buy_asset[0] / buy_price) * floating_mount
        cansell = sell_asset[1]
        if canbuy < cansell:
            return canbuy
        else:
            return cansell

    def offset_trade(self, buy, sell,market_price, market_list, amount = -1.0):
        offset_mount = 1

        print("Judge the amount to offset once")
        trytimes = 20
        result1 = ['.0','.0']
        result2 = ['.0','.0']
        t = 0
        while t < trytimes:
            t += 1
            try:
                result1 = self.autotrade.get_asset(buy)
                result2 = self.autotrade.get_asset(sell)
                if amount == -1.0:
                    amount = self.plan_max_mount(result1, result2, buy, sell, market_price, market_list)
                amount = offset_mount * amount
                break
            except Exception:
                print("Exception catched while judging asset, trying again.")
            continue

        if result1 == ['.0','.0'] or result2 == ['.0', '.0'] :
            return 1


        result = self.arb_trade(self, buy, sell, amount, False)
        #result = 0
        return result
        # return 0 succeed
        # return 1 both failed since cannot get statues
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


def get_arb_cost(offset, offset_pairs, buy, sell):
    for i in range(0,len(offset_pairs)):
        if offset_pairs[i] == [buy, sell]:
            return offset[i]
    return -1





if __name__ == '__main__':
    autotrading = MyAutoTrading()
    arbobject = MyArbitrage()
    #market_list = ['zaif', 'quoinex', 'bitbank', 'bitflyer']
    possible_market = ['zaif', 'bitbank', 'bitflyer']

    trading_pairs = observer.get_offset_pairs(possible_market, True)
    pairs_number = len(trading_pairs)

    # all pairs has a arb label at first time for 0:arb  for 1:offset  for 2:initial
    arb_label = [2]*pairs_number
    arb_poss_label = [0]*pairs_number
    setoff_poss_label = [0]*pairs_number

    check_balance = 0
    if check_balance:
        autotrading.calculate_captial(possible_market)
        autotrading.calculate_all_captial()
        print(autotrading.currency1)
        print(autotrading.currency2)
        print(autotrading.allcurrency1)
        print(autotrading.allcurrency2)

    #zaif2 = autotrading.get_asset_zaif()

    shared = memcache.Client(['127.0.0.1:11211'], debug=0)
    market_price = shared.get('market_price')
    print(market_price)
    market_list = shared.get('market_list')
    print(market_list)

    if_arb = 1

    while if_arb:
        arb_chance = shared.get('arb_chance')
        offset_chance = shared.get('offset_chance')
        all_offsets = shared.get('offset')
        all_offset_pairs = shared.get('offset_pairs')
        #print(arb_chance)
        #print(offset_chance)
    # find arb chance
        for i in arb_chance:
            buy_sell_pairs = [i[0],i[2]]
            index=find_market_index(buy_sell_pairs, trading_pairs)
            if index > -1:
                arb_poss_label[index] = 1
        #print(arb_poss_label)
    # find offset chance
        for j in offset_chance:
            buy_sell_pairs = [j[0], j[2]]
            index = find_market_index(buy_sell_pairs, trading_pairs)
            if index > -1:
                setoff_poss_label[index] = 1
        #print(setoff_poss_label)

#TODO add judje largest arb pairs

        for i in range(0,pairs_number):
            # if there is profit in this arb and we can arb, do it after that mark it as offsetable
            if arb_poss_label[i]==1 and arb_label[i] == 2:
                cost = get_arb_cost(all_offsets, all_offset_pairs, trading_pairs[i][0], trading_pairs[i][1])
                print('It is good time to preform arb to buy @ %s and sell @ %s. Profit is %f '%(trading_pairs[i][0],trading_pairs[i][1],-cost ))
                #TODO banzhuan
                arb_result = arbobject.arb_trade(trading_pairs[i][0], trading_pairs[i][1], amount=0.01)
                # for test
                if arb_result == 0:
                    print('Arb succeed, sleep 5 seconds')
                else:
                    # if no money find a chance to offset
                    if arb_result == 2:
                        arb_label[i] = 0
                        if (i%2) == 0:
                            arb_label[i + 1] = 1
                        else:
                            arb_label[i - 1] = 1
                        print('Change to offset mode')
                        #print(setoff_poss_label)
                        #print(arb_label)
                    print('Arb failed code %d'%arb_result)
            break

# TODO add judje largest setoff pairs

        for i in range(0, pairs_number):
            # if there is a pair need to offset and it is possible, do it
            if setoff_poss_label[i] == 1 and arb_label[i] == 1:
                cost = get_arb_cost(all_offsets, all_offset_pairs, trading_pairs[i][0], trading_pairs[i][1])
                print('It is good time to preform offset to buy @ %s and sell @ %s. Cost is' % (
                trading_pairs[i][0], trading_pairs[i][1],cost))
                arb_result = arbobject.offset_trade(trading_pairs[i][0], trading_pairs[i][1], market_price, market_list, amount = -1.0)
                if arb_result == 0:
                    print('Offset succeed. Set pairs to begin')
                    arb_label[i] = 2
                    if (i % 2) == 0:
                        arb_label[i + 1] = 2
                    else:
                        arb_label[i - 1] = 2
                else:
                    print('Offset failed code %d'%arb_result)
                break
            elif setoff_poss_label[i] == 0 and arb_label[i] == 1:
                cost = get_arb_cost(all_offsets, all_offset_pairs, trading_pairs[i][0], trading_pairs[i][1])
                print('We need offset to buy @ %s and sell @ %s, But the cost is too high. The cost is %f' % (
                    trading_pairs[i][0], trading_pairs[i][1], cost))

        time.sleep(5)

            #if setoff_poss_label[i] == 1 and arb_label[i] == 0:
                #TODO pingcang
            #    if succeed(pingcang):
            #    arb_label[i] = 1