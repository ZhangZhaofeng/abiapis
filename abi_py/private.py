#!/usr/bin/python3
# coding=utf-8

from tradingapis.bitflyer_api import pybitflyer

class AutoRun:

    def __init__(self):
        print("Initializing API")
        self.bitflyer_api=pybitflyer.API(api_key="xxx...", api_secret="yyy...")




if __name__ == '__main__':
    print("Shooting")



