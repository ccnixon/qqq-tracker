import json
import pika
from typing import List, Optional, Dict
from worker.quote import Quote
from worker.stock import Stock

credentials = pika.PlainCredentials(username="user", password="bitnami")
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', credentials=credentials))
channel = connection.channel()
channel.queue_declare(queue='price-updates')


class Store:
    cache: Dict[str, Stock]

    def __init__(self, tickers: List[str]) -> None:
        self.cache = {}
        for ticker in tickers:
            self.cache[ticker] = Stock(ticker)

    def get_stock(self, ticker) -> Stock:
        if ticker not in self.cache:
            raise AssertionError(f'{ticker} not valid')
        return self.cache[ticker]
