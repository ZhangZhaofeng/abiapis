from tradingapis.zaif_api import Utils

def get_trade(symbol):
    params = {'symbol': symbol}

    url = Utils.MARKET_URL + '/market/trade'
    return Utils.http_get_request(url, params)


def send_order(amount, source, symbol, _type, price=0):
    """
    :param amount:
    :param symbol: treading pair
    :param _type: 可选值 {buy-market：市价买, sell-market：市价卖, buy-limit：限价买, sell-limit：限价卖}
    :param price:
    :return:
    """

    params = {"method": 'active_orders',
              "nonce": 123,
              "currency_pairs": symbol #'btc_jpy',
              }

    url = '/v1/order/orders/place'
    return Utils.api_key_post(params)