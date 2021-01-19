from datetime import datetime
from typing import Dict, List, Optional
from worker.stock import Stock
from lib.db import DB

db = DB()
class Store:
    cache: Dict[str, Stock]
    last_quote_time: Optional[str] = None
    def __init__(self, tickers: List[str]) -> None:
        self.cache = {}
        self.last_quote_time = None
        for ticker in tickers:
            self.cache[ticker] = Stock(ticker)

    def get_stock(self, ticker) -> Stock:
        if ticker not in self.cache:
            raise AssertionError(f'{ticker} not valid')
        return self.cache[ticker]

    def get_quote_time(self, prices: Dict) -> str:
        data = prices['AAPL']['intraday-prices'][0]
        timestamp = datetime.strptime("{} {}".format(data['date'], data['minute']), '%Y-%m-%d %H:%M')
        return timestamp.strftime('%Y-%m-%d %H:%M')
    
    def update(self, prices: Dict) -> None:
        quote_time = self.get_quote_time(prices)
        
        if (self.last_quote_time is not None and quote_time == self.last_quote_time):
            print("Duplicate quote detected, skipping")
            return
        else:
            self.last_quote_time = quote_time
        
        updates = []
        for ticker in prices:
            data = prices[ticker]['intraday-prices'].pop()
            avg_price = data['average']
            volume = data['volume']
            stock = self.get_stock(ticker)
            stock.update(avg_price, volume)
            updates.append(stock.snapshot())
        
        print("Persisting stock updates")
        db.update_stocks(updates)
        print("Updates saved successfully")
