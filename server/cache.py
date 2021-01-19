from typing import Dict, List, Optional
from lib.db import DB
from pymongo import MongoClient

def generate_ranks(quotes: List[Dict], metric: str) -> List[str]:
    quotes.sort(key=lambda x: x[metric], reverse=True)
    ranks = map(lambda x: x['ticker'], quotes)
    return list(ranks)


class Cache:
    db: DB
    stocks: Dict[str, List[Dict]] = {}
    std_dev_vol_ranks = []
    std_dev_price_ranks = []

    def __init__(self, db: DB) -> None:
        super().__init__()
        self.db = db

    def get_stock(self, ticker: str) -> Optional[Dict]:
        if ticker in self.stocks:
            return self.stocks[ticker]
        else:
            return None

    def update_cache(self) -> None:
        stocks = self.db.get_stocks()
        for stock in stocks:
            print(stock)
            ticker = stock['ticker']
            self.stocks[ticker] = stock
        self.std_dev_price_ranks = generate_ranks(stocks, 'std_dev_price')
        self.std_dev_vol_ranks = generate_ranks(stocks, 'std_dev_vol')
