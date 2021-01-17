import os
import sys
import threading
from typing import Dict, List

import pika


def sort_quotes(quotes: List[Dict], metric: str) -> List[str]:
    quotes.sort(key=lambda x: x[metric], reverse=True)
    ranks = map(lambda x: x['ticker'], quotes)
    return list(ranks)


class Cache:
    quotes: Dict[str, List[Dict]] = {}
    std_dev_vol_ranks = []
    std_dev_price_ranks = []

    def get_ticker_history(self, ticker: str):
      print(self.quotes)
      if ticker in self.quotes:
        return self.quotes[ticker]
      else:
        return []

    def update_cache(self, quotes: List[Dict]) -> None:
        for quote in quotes:
            ticker = quote['ticker']
            if ticker in self.quotes:
                self.quotes[ticker].append(quote)
            else:
              self.quotes[ticker] = [quote]
            self.std_dev_price_ranks = sort_quotes(quotes, 'std_dev_price')
            self.std_dev_vol_ranks = sort_quotes(quotes, 'std_dev_vol')
