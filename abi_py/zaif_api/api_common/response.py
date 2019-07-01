import json
import requests
from tradingapis.zaif_api.api_error import ZaifServerException


def get_response(url, params=None, headers=None):
    response = requests.post(url, data=params, headers=headers)
    if response.status_code != 200:
        raise ZaifServerException('return status code is {}'.format(response.status_code))
    return json.loads(response.text)
