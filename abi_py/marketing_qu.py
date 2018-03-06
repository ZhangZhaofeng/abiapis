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

    def onTrick(self, depth , type ='buysell', amount = 0.001):
        mean = 20
        # print(depth['bids'])
        buysell_pairs = get_price(depth)
        order_pirce = buysell_pairs
        orderbuy = ''
        ordersell = ''
        if buysell_pairs[1] - buysell_pairs[0] < mean:
            order_pirce[0] = buysell_pairs[0] - 10
            order_pirce[1] = buysell_pairs[1] + 10
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
        return(order['models'])

    def get_orderbyid(self, id):
        order = self.quoinex_api.get_order(id)
        return(order['models'])

    def cancle_order(self,id):
        order = self.quoinex_api.cancel_order(id)
        return(order)

    def cancel_exception(self, id, oldjpy, oldbtc, buysell):
        time.sleep(3)
        #autotrading = auto_arb.MyAutoTrading()
        possible_market = ['quoinex']
        self.calculate_captial(possible_market)
        self.calculate_all_captial()
        cur_btc = self.currency2[0]
        cur_jpy = self.currency1[0]

        times = 2
        while oldbtc != cur_btc and times > 0:
            times -= 1
            try:
                print('Try to cancel operation again')
                checkid = self.cancle_order(id)
                deal_amount = float(checkid['quantity'])-float(checkid['filled_quantity'])
                if  deal_amount > 0.0:
                    return (buysell, '%f'%deal_amount)
                else:
                    return ('buysell', '')
            except Exception:
                print('Something wrong, try to cancel operation again')
            finally:
                time.sleep(3)
                self.calculate_captial(possible_market)
                self.calculate_all_captial()
                cur_btc = self.currency2[0]
        print('cur : %f, old :  %f' % (cur_btc, oldbtc))
        if cur_btc > oldbtc:
            amount = cur_btc - oldbtc
            return ('sell', ('%f')%amount)
        elif cur_btc < oldbtc:
            amount = oldbtc - cur_btc
            return ('buy', ('%f') % amount)
        else:
            return ('buysell','')


    def return_deal_amount(self, buysell, amount):
        if amount < 0.001:
            print('last %f wait to %s'%(amount, buysell))
            return('sleep', '%f'%amount)
        else:
            return (buysell, '%f'% amount)

    def judge_order(self, past_orderids, oldbtc, oldjpy):
        #past_orderids = [buy ,sell]
        orders = self.get_orders()
        curr_orderids = []
        for i in orders:
            curr_orderids.append(i['id'])

        if (past_orderids[0] not in curr_orderids) and (past_orderids[1] not in curr_orderids):
            possible_market = ['quoinex']
            self.calculate_captial(possible_market)
            self.calculate_all_captial()
            cur_btc = self.currency2[0]
            cur_jpy = self.currency1[0]
            if cur_btc > oldbtc:
                amount = cur_btc - oldbtc
                return (self.return_deal_amount('sell', amount))
            elif cur_btc < oldbtc:
                amount = oldbtc - cur_btc
                return (self.return_deal_amount('buy', amount))
            else:
                return ('buysell', '0')

        elif (past_orderids[0] in curr_orderids) and (past_orderids[1] not in curr_orderids):
            orderid = past_orderids[0]
            try:
                checkid = self.cancle_order(orderid)
                amount = float(checkid['quantity'])-float(checkid['filled_quantity'])
                return (self.return_deal_amount('buy', amount))
            except Exception:
                str, amount = self.cancel_exception(orderid, oldjpy ,oldbtc, 'buy')
                return (self.return_deal_amount(str, amount))

        elif (past_orderids[0] not in curr_orderids) and (past_orderids[1] in curr_orderids):
            orderid = past_orderids[1]
            try:
                checkid = self.cancle_order(orderid)
                amount = float(checkid['quantity']) - float(checkid['filled_quantity'])
                return (self.return_deal_amount('sell', amount))
            except Exception:
                str, amount = self.cancel_exception(orderid, oldjpy, oldbtc, 'sell')
                return (self.return_deal_amount(str, amount))

        elif (past_orderids[0] in curr_orderids) and (past_orderids[1] in curr_orderids):
            return('sleep','')

    def get_depth(self):
        depth =self.quoinex_api.get_order_book(product_id=5)
        return(depth)

    def get_last_executions(self):
        executions = self.quoinex_api.get_executions(product_id=5,limit=50)
        return(executions['models'])

    def get_last_price(self, executions):
        last_buy_price = []
        last_sell_price = []
        last_price = []
        last_buy_amount = []
        last_sell_amount = []
        for i in executions:
            if i['taker_side'] == 'buy':
                last_buy_price.append(float(i['price']))
                last_buy_amount.append(float(i['quantity']))
            elif i['taker_side'] == 'sell':
                last_sell_price.append(float(i['price']))
                last_sell_amount.append(float(i['quantity']))
            last_price.append(float(i['price']))

        return [last_price, last_buy_price, last_sell_price, last_buy_amount, last_sell_amount]

    def judge_market(self):

        #1. judge if bull or bear

        mid_price, sell_depth, buy_depth = get_price(self.get_depth(), if123 = True)
        margin1 = mid_price * 0.00005
        bull = False
        bear = False

        buyselllastprice = self.get_last_price(self.get_last_executions())

        lastprice = buyselllastprice[0][0:20]

        if mid_price > max(lastprice[0:]) + margin1 and mid_price > lastprice[1]:
            print('bull')
            bull = True
        elif mid_price < min(lastprice[0:]) - margin1 and mid_price < lastprice[1]:
            print('bear')
            bear = True

        # 2. judge if over buy or over sell
        last_buy_amount = sum(buyselllastprice[3])
        if last_buy_amount == 0:
            last_buy_amount = 0.001
        last_sell_amount = sum(buyselllastprice[4])
        if last_sell_amount == 0:
            last_sell_amount = 0.001
        passedbuy = False
        passedsell = False

        futurebuy = False
        futuresell = False


        margin2 = 2.5
        if last_buy_amount/last_sell_amount > margin2:
            print('Passedbuy')
            passedbuy = True
        elif last_sell_amount/last_buy_amount > margin2:
            print('Passedsell')
            passedsell = True

        if sell_depth/buy_depth > 1.4:
            print('Futurebuy')
            futurebuy = True
        elif buy_depth/sell_depth > 1.4:
            print('Futuresell')
            futuresell = True

        if passedbuy and futurebuy :
            passedbuy = False
            futurebuy = False
        elif passedsell and futuresell :
            passedsell = False
            futuresell = False

        # 3. judge if big difference of last price
        margin3 = mid_price * 0.002
        faraway = False
        if abs(mid_price - lastprice[0]*0.7 - lastprice[1]*0.2 - lastprice[2]*0.1) > margin3:
            print('Faraway')
            faraway = True

        if bull or bear or passedbuy or passedsell or futurebuy or futuresell or faraway:
            return False
        else:
            return True


def get_price(depth, if123 = False):
    asks = depth['sell_price_levels']
    bids = depth['buy_price_levels']

    sell_price = float(asks[0][0])
    buy_price = float(bids[0][0])
    sell_price1 = sell_price
    buy_price1 = buy_price
    sell_price2 = float(asks[1][0])
    buy_price2 = float(bids[1][0])
    sell_price3 = float(asks[2][0])
    buy_price3 = float(bids[2][0])
    amount_asks = 0.0
    amount_bids = 0.0
    largest_diff = 500
    float_amount_buy = 0.01
    float_amount_sell = 0.01
    buy_depth = 0.0
    sell_depth = 0.0

    for i in range(0, 10):
        sell_depth += float(asks[i][1])
        buy_depth  += float(bids[i][1])

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


    ave_price = (sell_price1 + buy_price1)/2 *0.7 + (sell_price2 + buy_price2)/2 *0.2  + (sell_price3 + buy_price3)/2 *0.1
    mid_price =  (sell_price1 + buy_price1)/2
    if sell_price - mid_price > largest_diff:
        sell_price = mid_price + largest_diff
    if mid_price -buy_price > largest_diff:
        buy_price = mid_price - largest_diff

        sell_price = float('%.2f'%sell_price)
        buy_price = float('%.2f'%buy_price)

    if if123:
        return (ave_price, sell_depth, buy_depth)
    else:
        return([buy_price, sell_price ])





if __name__=='__main__':
    autoTradingForMarketing_Tset = AutoTradingForMarketing_quoine()
    #autotrading = auto_arb.MyAutoTrading()
    log_file = './marketing_log'

    possible_market = ['quoinex']
    autoTradingForMarketing_Tset.calculate_captial(possible_market)
    autoTradingForMarketing_Tset.calculate_all_captial()
    start_jpy = autoTradingForMarketing_Tset.currency1[0]
    start_btc = autoTradingForMarketing_Tset.currency2[0]
    loss_cut = 100
    loss_cut_btc = 0.02
    #
    cur_jpy = start_jpy
    cur_btc = start_btc

    print(autoTradingForMarketing_Tset.get_orders())
    prices = autoTradingForMarketing_Tset.judge_market()


    try_times = 1000

    while try_times> 0:
        auto_arb.print_and_write(cur_jpy, log_file)
        auto_arb.print_and_write(cur_btc, log_file)
        auto_arb.print_and_write('profit: %f'%(cur_jpy - start_jpy), log_file)
        depth = autoTradingForMarketing_Tset.get_depth()
        if autoTradingForMarketing_Tset.judge_market():
            results = autoTradingForMarketing_Tset.onTrick(depth)
            orderid_buy = results[0]['id']
            orderid_sell = results[1]['id']
            auto_arb.print_and_write('Orders placed! buy: %s sell: %s, wait 10s'%(results[0]['price'],results[1]['price']), log_file)
        #auto_arb.print_and_write(results, log_file)
            time.sleep(40)
        else:
            auto_arb.print_and_write(
                'Not good time to do it, try again')
            time.sleep(5)
            continue
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
                time.sleep(10)
            elif judgeresult == 'sleep' :
                auto_arb.print_and_write('Orders are not at deals, wait 3 seconds, unslovepart: %s'%unslove_part, log_file)
                time.sleep(3)

        autoTradingForMarketing_Tset.calculate_captial(possible_market)
        autoTradingForMarketing_Tset.calculate_all_captial()
        cur_jpy = autoTradingForMarketing_Tset.currency1[0]
        cur_btc = autoTradingForMarketing_Tset.currency2[0]
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