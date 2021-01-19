from typing import List, Dict
from worker.stock import Stock
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
