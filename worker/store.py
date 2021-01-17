import json
from typing import List, Optional

import pika

from worker.quote import Quote
from worker.stock import Stock

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='price-updates')


class Store:
    latest_quote_time: Optional[str] = None

    def __init__(self, tickers: list) -> None:
        super().__init__()
        self._cache = {}
        for ticker in tickers:
            self._cache[ticker] = Stock(ticker)

    def get_stock(self, ticker) -> Stock:
        if ticker not in self._cache:
            raise AssertionError(f'{ticker} not valid')
        return self._cache[ticker]

    def update(self, quotes: List[Quote], quote_time: str) -> None:
        message_body = []
        
        # Check to see if the data is fresh to ensure we are not duplicating quotes when markets are closed.
        if self.latest_quote_time is not None:
            if (self.latest_quote_time == quote_time):
                print("Duplicate quote detected, skipping")
                return
        else:
            self.latest_quote_time = quote_time
        
        for quote in quotes:
            stock = self.get_stock(quote.ticker)
            stock.update(quote.volume, quote.price)
            message_body.append({
                'ticker': quote.ticker,
                'time': quote.timestamp,
                'volume': quote.volume,
                'price': quote.price,
                'std_dev_vol': stock.std_dev_vol(),
                'std_dev_price': stock.std_dev_price()
            })
        print("Publishing record")
        channel.basic_publish(exchange='',
                              routing_key='price-updates',
                              body=json.dumps(message_body))
        print("Record inserted successfully")
        connection.close()
