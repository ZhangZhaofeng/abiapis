#!/usr/bin/env python
# -*- coding:utf-8 -*-
import hashlib
import requests
import time
import urllib
import hmac
from collections import OrderedDict

# coin
coin = 'btc'
public_key = 'xxxx'
private_key = 'xxxx'


# send requests
def request(method, params):
    Od = OrderedDict()
    Od['coin'] = coin
    Od['key'] = public_key
    Od['nonce'] = int(time.time())

    for i in params:
        Od[i] = params[i]

    Od['signature'] = signature(Od)
    response = requests.post('https://www.btcbox.co.jp/api/v1/' + method, data=Od)
    if response.status_code == 200:
        print(response.text)


# create signature
def signature(params):
    payload = urllib.parse.urlencode(params)
    md5prikey = hashlib.md5(private_key.encode()).hexdigest()
    sign = urllib.parse.quote(hmac.new(b'md5prikey', payload.encode(), digestmod=hashlib.sha256).hexdigest())
    return sign


def ticker():
    request('ticker',{'coin':'btc'})

# get balance
def balance():
    request('balance', {})


# get wallet address
def wallet():
    request('wallet', {})


# select orders
def orders():
    request('orders', {'type': 'open'})


balance()