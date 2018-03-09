from tradingapis.quoine_api import client
import auto_arb
import time
import observer
import marketing_qu

class AutoTradingForMarketing_quoine2(auto_arb.MyAutoTrading):
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

    def get_orders_bitbank(self):
        order = self.bitbank_api.get_active_orders('btc_jpy')
        return(order)

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

    def get_property(self):
        possible_market = ['quoinex']
        self.calculate_captial(possible_market)
        self.calculate_all_captial()
        cur_btc = self.currency2[0]
        cur_jpy = self.currency1[0]
        buysellpairs = observer.get_bid_ask_quoine('BTC_JPY')
        price = (buysellpairs[0] + buysellpairs[1])/2
        property = cur_jpy + cur_btc * price
        return(property, cur_jpy, cur_btc)

    def judge_order(self, past_orderids, oldbtc, oldjpy):
        #past_orderids = [buy ,sell]
        orders = self.get_orders()
        curr_orderids = []
        for i in orders:
            curr_orderids.append(i['id'])

        if (past_orderids[0] not in curr_orderids) and (past_orderids[1] not in curr_orderids):
            return ('buysell', '0')

        elif (past_orderids[0] in curr_orderids) or (past_orderids[1] in curr_orderids):
            # cancel all orders
            ids = []
            if past_orderids[0] in curr_orderids:
                ids.append(past_orderids[0]) # buy order id
            if past_orderids[1] in curr_orderids:
                ids.append(past_orderids[1]) # sell order id

            opflag = 1
            amount = 0
            for i in ids:
                while opflag:
                    try:
                        checkid = self.cancle_order(i)
                        amount += float(checkid['quantity'])-float(checkid['filled_quantity'])
                        opflag = 0
                    except Exception:
                        time.sleep(5)
                        order = self.get_orderbyid(i)
                        if order['status'] == 'filled':
                            amount += float(order['quantity'])-float(order['filled_quantity'])
                            print('Filled before cancelling')
                            opflag = 0
                        else:
                            continue


        return('canceled', '%f'%amount)


    def get_depth(self):
        product_id = 5
        depth =self.quoinex_api.get_order_book(product_id)
        return(depth)

def get_price(depth):
    asks = depth['sell_price_levels']
    bids = depth['buy_price_levels']

    sell_price = float(asks[0][0])
    buy_price = float(bids[0][0])
    amount_asks = 0.0
    amount_bids = 0.0
    largest_diff = 300
    float_amount_buy = 0.001
    float_amount_sell = 0.001
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

        sell_price = float('%.2f'%sell_price)
        buy_price = float('%.2f'%buy_price)

    return([buy_price, sell_price ])





if __name__=='__main__':
    autoTradingForMarketing_Tset = AutoTradingForMarketing_quoine2()
    #autotrading = auto_arb.MyAutoTrading()
    judge_flag_class = marketing_qu.AutoTradingForMarketing_quoine()

    log_file = './marketing_log'
    possible_market = ['quoinex']


    print(autoTradingForMarketing_Tset.get_orders())

    try_times = 1000
    while try_times> 0:
        [start_property, start_jpy, start_btc]=autoTradingForMarketing_Tset.get_property()
        loss_cut = 1000
        loss_cut_btc = 0.02
        #

        auto_arb.print_and_write(start_jpy, log_file)
        auto_arb.print_and_write(start_btc, log_file)


        if judge_flag_class.judge_market():
            depth = autoTradingForMarketing_Tset.get_depth()
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
        #time.sleep(20)
        flag = 1
        while flag:
            judgeresult, unslove_part = autoTradingForMarketing_Tset.judge_order([orderid_buy, orderid_sell], start_btc, start_jpy)
            if judgeresult == 'buysell' :
                auto_arb.print_and_write('All order are at a deal, try next time', log_file)
                flag = 0
                time.sleep(5)
            elif judgeresult == 'canceled' :
                flag = 0
                auto_arb.print_and_write('Orders are not at deals, cancel and try again, unslovepart: %s'%unslove_part, log_file)
                time.sleep(5)

        [cur_property, cur_jpy, cur_btc] = autoTradingForMarketing_Tset.get_property()


        if start_property - cur_property > loss_cut or abs(start_btc - cur_btc) > loss_cut_btc:
            try_times = 0
            auto_arb.print_and_write('Triggered loss cut, (loss: %f), stop'%(start_property - cur_property), log_file)
        else:
            try_times -= 1
        auto_arb.print_and_write('profit: %f' % (start_property - cur_property), log_file)
