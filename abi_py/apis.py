
#!/usr/bin/python3


from treadingapis.bittrex_api import bittrex
from treadingapis.huobi_api import huobi
from treadingapis.binance_api import client,exceptions
from treadingapis.bitflyer_api import pybitflyer

if __name__ == '__main__':
    bittrex_api = bittrex.Bittrex('', '')
    print(bittrex_api.get_markets())
    print(huobi.get_symbols())
