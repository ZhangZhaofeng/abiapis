
# -*- coding:utf-8 -*-
import hashlib
import requests
import time
import urllib
import hmac
from collections import OrderedDict
from hashlib import sha256
from . import error_code

# coin
public_key = 'xxxx'
private_key = 'xxxx'


class API(object):

    def __init__(self, api_key=public_key, api_secret=private_key, timeout=None):
        self.api_url = 'https://www.btcbox.co.jp/api/v1/'
        self.api_key = api_key
        self.api_secret = api_secret
        self.timeout = timeout

# send requests
    def request(self, method, params):
        Od = OrderedDict()
        Od['key'] = self.api_key
        Od['nonce'] = int(time.time())

        for i in params:
            Od[i] = params[i]

        Od['signature'] = self.signature(Od)
        response = requests.post(self.api_url + method, data=Od)
        if response.status_code == 200:
            #print(response.text)
            error_code.error_parser(response.json())
            return(response.json())
        else:
            message = response.status_code
            raise Exception(message)


# create signature
    def signature(self, params):
        payload = urllib.parse.urlencode(params)
        md5prikey = hashlib.md5(self.api_secret.encode()).hexdigest()
        h = hmac.new(bytearray(md5prikey, 'utf8'), bytearray(payload, 'utf8'), sha256).hexdigest()
        sign = urllib.parse.quote(h)
        return sign


    def ticker(self, coin='btc'):
        return(self.request('ticker',{'coin': str(coin)}))


# get balance
    def balance(self, coin='btc'):
        return(self.request('balance', {'coin': str(coin)}))

    def trade(self, price, amount, side, coin='btc'):
        if side == 'sell' or side == 'SELL':
            return(self.request('trade_add',{'price': str(price), 'amount' : str(amount),'type': 'sell' ,'coin': str(coin)}))
        elif side == 'buy' or side == 'BUY':
            return (self.request('trade_add', {'price': str(price), 'amount' : str(amount), 'type': 'buy', 'coin': str(coin)}))

# get wallet address
    def wallet(self, coin='btc'):
        return (self.request('wallet', {'coin': str(coin)}))


# select orders
    def orders(self, coin='btc'):
        return (self.request('orders', {'coin': str(coin), 'type': 'open'}))

