import time
import hmac
import hashlib
import requests
import simplejson as json
from tradingapis.coincheck_api.utils import *

"""
document: https://coincheck.com/documents/exchange/api
"""
class Order(object):

    def __init__(self,
                 access_key=None,
                 secret_key=None):
        self.access_key = access_key
        self.secret_key = secret_key

    def get_info(self):
        ''' show user information
        '''

        url = 'https://coincheck.com/api/accounts'
        headers = make_header(url,
                              access_key=self.access_key,
                              secret_key=self.secret_key)

        r = requests.get(url,
                         headers=headers)
        return json.loads(r.text)

    def get_balance(self):
        ''' confirm balance
        '''
        url = 'https://coincheck.com/api/accounts/balance'
        headers = make_header(url,
                              access_key=self.access_key,
                              secret_key=self.secret_key)
        r = requests.get(url,
                         headers=headers)
        return json.loads(r.text)


    def create(self,rate, amount, order_type, pair):
        ''' create new order function
        :param rate: float
        :param amount: float
        :param order_type: str; set 'buy' or 'sell'
        :param pair: str; set 'btc_jpy' 
        '''
        nonce = nounce()
        payload = { 'rate': rate,
                    'amount': amount,
                    'order_type': order_type,
                    'pair': pair
                    }
        url= 'https://coincheck.com/api/exchange/orders'
        body = 'rate={rate}&amount={amount}&order_type={order_type}&pair={pair}'.format(**payload)
        message = nonce + url + body
        signature = hmac.new(self.secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()
        headers = {
           'ACCESS-KEY'      : self.access_key,
           'ACCESS-NONCE'    : nonce,
           'ACCESS-SIGNATURE': signature
        }
        r = requests.post(url,headers=headers,data=body)
        return json.loads(r.text)
    
    def buy_btc_jpy(self, **kwargs):
        return self.create(order_type='buy', pair='btc_jpy',**kwargs) 
    
    def sell_btc_jpy(self, **kwargs):
        return self.create(order_type='sell', pair='btc_jpy',**kwargs) 
    
    def list(self):
        ''' list all open orders func
        '''
        url= 'https://coincheck.com/api/exchange/orders/opens'
        headers = make_header(url,access_key=self.access_key,secret_key=self.secret_key)
        r = requests.get(url,headers=headers)
        return json.loads(r.text)
    
    def cancel(self,order_id):
        ''' cancel the specified order
        :param order_id: order_id to be canceled
        '''
        url= 'https://coincheck.com/api/exchange/orders/' + order_id
        headers = make_header(url,access_key=self.access_key,secret_key=self.secret_key)
        r = requests.delete(url,headers=headers)
        return json.loads(r.text)
    
    def history(self):
        ''' show payment history
        '''
        url= 'https://coincheck.com/api/exchange/orders/transactions'
        headers = make_header(url,access_key=self.access_key,secret_key=self.secret_key)
        r = requests.get(url,headers=headers)
        return json.loads(r.text)
