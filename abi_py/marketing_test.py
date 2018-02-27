from tradingapis.bitbank_api import public_api
import auto_arb
import private
import observer
import time

class AutoTradingForMarketing_Tset(auto_arb.MyAutoTrading):
    def trade_bitbank_limit(self, type, buysellprice ,amount):
        print("trade_bitbank")
        if type == "BUY" or type == "buy":
            order = self.bitbank_api.order(pair='btc_jpy',
                                           price=str(buysellprice),
                                           amount=str(amount),
                                           side='buy',
                                           order_type="limit")
        elif type == "SELL" or type == "sell":
            order = self.bitbank_api.order(pair='btc_jpy',
                                           price=str(buysellprice),
                                           amount=str(amount),
                                           side='sell',
                                           order_type='limit')
        else:
            print("error!")

        return(order)

    def onTrick(self, depth):
        mean = 150
        amount = 0.01
        # print(depth['bids'])
        buysell_pairs = get_price(depth)
        order_pirce = buysell_pairs
        if buysell_pairs[1] - buysell_pairs[0] < mean:
            order_pirce[0] = buysell_pairs[0] - 50
            order_pirce[1] = buysell_pairs[1] + 50
        orderbuy = self.trade_bitbank_limit('buy' , order_pirce[0], amount)
        ordersell = self.trade_bitbank_limit('sell', order_pirce[1], amount)
        return([orderbuy,ordersell])

    def get_orders(self):
        order = self.bitbank_api.get_active_orders('btc_jpy')
        return(order)

def get_depth(market,product_pair):
    if market == 'bitbank':
        bitbank_api = public_api.bitbankcc_public()
        if product_pair == 'BTC_JPY':
            product_pair = 'btc_jpy'
            depth = bitbank_api.get_depth(product_pair)
            return(depth)

def get_price(depth):
    asks = depth['asks']
    bids = depth['bids']

    sell_price = float(asks[0][1])
    buy_price = float(bids[-1][1])
    amount_asks = 0.0
    amount_bids = 0.0
    float_amount_buy = 0.02
    float_amount_sell = 0.02
    len_a = len(asks)
    for i in range(0, len_a):
        amount_asks += float(asks[i][1])
        if amount_asks > float_amount_sell:
            sell_price = float(asks[i][0]) - 1.0
            break

    len_b = len(bids)
    for i in range(0 , len_b):
        amount_bids += float(bids[i][1])
        if amount_bids > float_amount_buy:
            buy_price = float(bids[i][0]) + 1.0
            break

    return([buy_price, sell_price ])





if __name__=='__main__':
    autoTradingForMarketing_Tset = AutoTradingForMarketing_Tset()

    #

    depth = get_depth('bitbank', 'BTC_JPY')
    #results = autoTradingForMarketing_Tset.onTrick(depth)

    #print(results)

    time.sleep(3)
    orders = autoTradingForMarketing_Tset.get_orders()
    print(len(orders))
    #print(get_price(depth))

    #onTrick(depth)