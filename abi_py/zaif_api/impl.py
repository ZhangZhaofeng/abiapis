# Importing from this module is deprecated
# This module will be removed in the future

_MAX_COUNT = 1000
_MIN_WAIT_TIME_SEC = 1

from tradingapis.zaif_api.exchange_api.public import (
    ZaifPublicStreamApi,
    ZaifPublicApi,
    ZaifFuturesPublicApi,
)
from tradingapis.zaif_api.exchange_api.trade import (
    ZaifTradeApi,
    ZaifLeverageTradeApi,
    ZaifTokenTradeApi,
)

from tradingapis.zaif_api.oauth import ZaifTokenApi

__all__ = [
    'ZaifTradeApi',
    'ZaifLeverageTradeApi',
    'ZaifTokenTradeApi',
    'ZaifPublicStreamApi',
    'ZaifPublicApi',
    'ZaifFuturesPublicApi',
    'ZaifTokenApi'
]
