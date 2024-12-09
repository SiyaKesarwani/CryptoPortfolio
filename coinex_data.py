# -*- coding: utf-8 -*-
import hashlib
import re
import time
import hmac
from urllib.parse import urlparse, urlencode
from dotenv import load_dotenv
import os
from decimal import Decimal

import requests

from tabulate import tabulate

# Load environment variables from .env file
load_dotenv()
# Access variables
access_id = os.getenv('ACCESS_ID')
secret_key = os.getenv('SECRET_KEY')

COINEX_API_URL = "https://api.coinex.com/v1/market/ticker/all"

class RequestsClient(object):
    HEADERS = {
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
        "X-COINEX-KEY": "",
        "X-COINEX-SIGN": "",
        "X-COINEX-TIMESTAMP": "",
    }

    def __init__(self):
        self.access_id = access_id
        self.secret_key = secret_key
        self.url = "https://api.coinex.com/v2"
        self.headers = self.HEADERS.copy()

    # Generate your signature string
    def gen_sign(self, method, request_path, body, timestamp):
        prepared_str = f"{method}{request_path}{body}{timestamp}"
        signature = hmac.new(
            bytes(self.secret_key, 'latin-1'),
            msg=bytes(prepared_str, 'latin-1'),
            digestmod=hashlib.sha256
        ).hexdigest().lower()
        return signature

    def get_common_headers(self, signed_str, timestamp):
        headers = self.HEADERS.copy()
        headers["X-COINEX-KEY"] = self.access_id
        headers["X-COINEX-SIGN"] = signed_str
        headers["X-COINEX-TIMESTAMP"] = timestamp
        headers["Content-Type"] = "application/json; charset=utf-8"
        return headers

    def request(self, method, url, params={}, data=""):
        req = urlparse(url)
        request_path = req.path

        timestamp = str(int(time.time() * 1000))
        if method.upper() == "GET":
            # If params exist, query string needs to be added to the request path
            if params:
                for item in params:
                    if params[item] is None:
                        del params[item]
                        continue
                request_path = request_path + "?" + urlencode(params)

            signed_str = self.gen_sign(
                method, request_path, body="", timestamp=timestamp
            )
            response = requests.get(
                url,
                params=params,
                headers=self.get_common_headers(signed_str, timestamp),
            )

        else:
            signed_str = self.gen_sign(
                method, request_path, body=data, timestamp=timestamp
            )
            response = requests.post(
                url, data, headers=self.get_common_headers(signed_str, timestamp)
            )

        if response.status_code != 200:
            raise ValueError(response.text)
        return response


request_client = RequestsClient()

def fetch_prices(symbols):
    try:
        # Make the GET request
        response = requests.get(COINEX_API_URL)
        response.raise_for_status()  # Raise an error for bad status codes

        # Parse the JSON response
        data = response.json()

        prices = {}

        if data["code"] == 0:
            markets = data["data"]["ticker"]

            # Print cryptocurrency prices
            print("Cryptocurrency Prices on CoinEx:")
            for symbol in symbols:
                if symbol in markets:
                    price = markets[symbol]['last']
                    prices[symbol[0:len(symbol)-4]] = price
                    # print(f"{market}: Last Price = {markets[market]['last']}")
                else:
                    print(f"{symbol} not found on CoinEx.")
            # for market, details in markets.items():
            #     print(f"{market}: Last Price = {details['last']}")
        else:
            print(f"Error: {data['message']}")
        return prices
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return {}

def get_spot_market():
    request_path = "/assets/spot/balance"
    params = {}
    response = request_client.request(
        "GET",
        "{url}{request_path}".format(url=request_client.url, request_path=request_path),
        params=params,
    )
    return response


def run_code():
    try:
        response = get_spot_market().json()
        response_data = response['data']

        symbols = []
        for data in response_data:
            if data['ccy'] != "USDT":
                symbols.append(data['ccy']+"USDT")

        token_prices = fetch_prices(symbols)

        for token_detail in response_data:
            if token_detail['ccy'] in token_prices:
                token_detail.update({'price':Decimal(token_prices[token_detail['ccy']])})
            else:
                token_detail.update({'price':0})

        # Convert data to tabular format
        headers = ["Currency", "Price (USD)", "Current Value (USD)"]
        rows = [(entry['ccy'], entry['price'],  entry['price'] * Decimal(entry['available'])) for entry in response_data]

        # Print table
        print(tabulate(rows, headers=headers, tablefmt="grid"))

    except Exception as e:
        print("Error:" + str(e))
        time.sleep(3)
        run_code()


if __name__ == "__main__":
    run_code()
    # fetch_prices()