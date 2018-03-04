from tradingapis.quoine_api import client
import auto_arb
import time

class AutoTradingForMarketing_quoine(auto_arb.MyAutoTrading):
    def trade_quoine_limit(self, type, buysellprice ,amount):
        print("trade_quoine")

        if type == 'BUY' or type == 'buy':
            order = self.quoinex_api.create_limit_buy(product_id=5, quantity=str(amount), price=str(buysellprice))
        elif type == "SELL" or type == "sell":
            order = self.quoinex_api.create_limit_sell(product_id=5, quantity=str(amount), price=str(buysellprice))
        else:
            print("error!")

        return(order)

    def onTrick(self, depth , type ='buysell', amount = 0.01):
        mean = 150
        # print(depth['bids'])
        buysell_pairs = get_price(depth)
        order_pirce = buysell_pairs
        orderbuy = ''
        ordersell = ''
        if buysell_pairs[1] - buysell_pairs[0] < mean:
            order_pirce[0] = buysell_pairs[0] - 50
            order_pirce[1] = buysell_pairs[1] + 50
        if type == 'buy':
            orderbuy = self.trade_quoine_limit('buy' , order_pirce[0], amount)
            return(orderbuy)
        elif type == 'sell':
            ordersell = self.trade_quoine_limit('sell', order_pirce[1], amount)
            return(ordersell)
        elif type == 'buysell':
            orderbuy = self.trade_quoine_limit('buy', order_pirce[0], amount)
            ordersell = self.trade_quoine_limit('sell', order_pirce[1], amount)
            return([orderbuy,ordersell])
        else:
            return ([orderbuy, ordersell])


    def get_orders(self):
        order = self.quoinex_api.get_orders(status='live')
        return(order)

    def get_orderbyid(self, id):
        order = self.quoinex_api.get_order(id)
        return(order)

    def cancle_order(self,id):
        order = self.quoinex_api.cancel_order(id)
        return(order)

    def cancel_exception(self, id, oldjpy, oldbtc, buysell):
        time.sleep(3)
        autotrading = auto_arb.MyAutoTrading()
        possible_market = ['quoine']
        autotrading.calculate_captial(possible_market)
        autotrading.calculate_all_captial()
        cur_btc = autotrading.currency2[0]
        cur_jpy = autotrading.currency1[0]

        times = 2
        while oldbtc != cur_btc and times > 0:
            times -= 1
            try:
                print('Try to cancel operation again')
                checkid = self.cancle_order(id)
                if float(checkid['disc_quantity']) > 0.0:
                    return (buysell, checkid['disc_quantity'])
                else:
                    return ('buysell', '')
            except Exception:
                print('Something wrong, try to cancel operation again')
            finally:
                time.sleep(3)
                autotrading.calculate_captial(possible_market)
                autotrading.calculate_all_captial()
                cur_btc = autotrading.currency2[0]
        print('cur : %f, old :  %f' % (cur_btc, oldbtc))
        if cur_btc > oldbtc:
            amount = cur_btc - oldbtc
            return ('sell', ('%f')%amount)
        elif cur_btc < oldbtc:
            amount = oldbtc - cur_btc
            return ('buy', ('%f') % amount)
        else:
            return ('buysell','')


    def judge_order(self, past_orderids, oldbtc, oldjpy):
        #past_orderids = [buy ,sell]
        orders = self.get_orders()
        curr_orderids = []
        for i in orders['orders']:
            curr_orderids.append(i['order_id'])

        if (past_orderids[0] not in curr_orderids) and (past_orderids[1] not in curr_orderids):
            return ('buysell','')
        elif (past_orderids[0] in curr_orderids) and (past_orderids[1] not in curr_orderids):
            orderid = past_orderids[0]
            try:
                checkid = self.cancle_order(orderid)
                return ('buy', checkid['disc_quantity'])
            except Exception:
                str, amount = self.cancel_exception(orderid, oldjpy ,oldbtc, 'buy')
                return (str, amount)

        elif (past_orderids[0] not in curr_orderids) and (past_orderids[1] in curr_orderids):
            orderid = past_orderids[1]
            try:
                checkid = self.cancle_order(orderid)
                return ('sell', checkid['disc_quantity'])
            except Exception:
                str, amount = self.cancel_exception(orderid, oldjpy, oldbtc, 'sell')
                return (str, amount)

        elif (past_orderids[0] in curr_orderids) and (past_orderids[1] in curr_orderids):
            return('sleep','')

    def get_depth(self):
        product_id = 5
        depth =self.quoinex_api.get_order_book(product_id)
        return(depth)

def get_price(depth):
    asks = depth['asks']
    bids = depth['bids']

    sell_price = float(asks[0][1])
    buy_price = float(bids[-1][1])
    amount_asks = 0.0
    amount_bids = 0.0
    largest_diff = 500
    float_amount_buy = 0.01
    float_amount_sell = 0.01
    len_a = len(asks)
    for i in range(0, len_a):
        amount_asks += float(asks[i][1])
        if amount_asks > float_amount_sell:
            sell_price = float(asks[i][0]) - 3.0
            break

    len_b = len(bids)
    for i in range(0 , len_b):
        amount_bids += float(bids[i][1])
        if amount_bids > float_amount_buy:
            buy_price = float(bids[i][0]) + 3.0
            break

    mid_price = (sell_price + buy_price)/2
    if sell_price - mid_price > largest_diff:
        sell_price = mid_price + largest_diff
    if mid_price -buy_price > largest_diff:
        buy_price = mid_price - largest_diff

    return([buy_price, sell_price ])





if __name__=='__main__':
    autoTradingForMarketing_Tset = AutoTradingForMarketing_quoine()
    autotrading = auto_arb.MyAutoTrading()
    log_file = '/home/zhang/marketing_log'

    possible_market = ['quoine']
    autotrading.calculate_captial(possible_market)
    autotrading.calculate_all_captial()
    start_jpy = autotrading.currency1[0]
    start_btc = autotrading.currency2[0]
    loss_cut = 100
    loss_cut_btc = 0.02
    #
    cur_jpy = start_jpy
    cur_btc = start_btc

    print(autoTradingForMarketing_Tset.get_orders())

    try_times = 200
    while try_times> 0:
        auto_arb.print_and_write(cur_jpy, log_file)
        auto_arb.print_and_write(cur_btc, log_file)
        auto_arb.print_and_write('profit: %f'%(cur_jpy - start_jpy), log_file)
        depth = autoTradingForMarketing_Tset.get_depth()
        results = autoTradingForMarketing_Tset.onTrick(depth)
        orderid_buy = results[0]['id']
        orderid_sell = results[1]['id']
        auto_arb.print_and_write('Orders placed! buy: %s sell: %s, wait 10s'%(results[0]['price'],results[1]['price']), log_file)
        #auto_arb.print_and_write(results, log_file)
        time.sleep(10)
        flag = 1
        while flag:
            judgeresult, unslove_part = autoTradingForMarketing_Tset.judge_order([orderid_buy, orderid_sell], cur_btc, cur_jpy)
            if judgeresult == 'buysell' :
                auto_arb.print_and_write('All order are at a deal, try next time', log_file)
                flag = 0
                time.sleep(5)
            elif judgeresult == 'buy' or judgeresult == 'sell' :
                depth = autoTradingForMarketing_Tset.get_depth()
                part_flag = True
                if judgeresult == 'buy':
                    results = autoTradingForMarketing_Tset.onTrick(depth, 'buy', float(unslove_part))
                    orderid_buy = results['id']
                elif judgeresult == 'sell':
                    results = autoTradingForMarketing_Tset.onTrick(depth, 'sell', float(unslove_part))
                    orderid_sell = results['id']
                auto_arb.print_and_write(
                    'order is not full filled, try %s %s @ %s again!' % ( judgeresult, unslove_part, results['price']), log_file)
                # auto_arb.print_and_write(results, log_file)
                time.sleep(5)
            elif judgeresult == 'sleep' :
                auto_arb.print_and_write('Orders are not at deals, wait 3 seconds', log_file)
                time.sleep(3)

        autotrading.calculate_captial(possible_market)
        autotrading.calculate_all_captial()
        cur_jpy = autotrading.currency1[0]
        cur_btc = autotrading.currency2[0]
        if start_jpy - cur_jpy > loss_cut:
            try_times = 0
            auto_arb.print_and_write('Triggered loss cut, stop', log_file)
        elif start_btc - cur_btc > loss_cut_btc:
            try_times = 0
            auto_arb.print_and_write('Something wrong, only one side approved, stop', log_file)
        else:
            try_times -= 1
    #print(results)

    #time.sleep(3)


    #print(len(orders['orders']))
    #print(get_price(depth))

    #onTrick(depth)