from typing import Dict, List
from lib.db import DB

db = DB()

def generate_ranks(quotes: List[Dict], metric: str) -> List[str]:
    quotes.sort(key=lambda x: x[metric], reverse=True)
    ranks = map(lambda x: x['ticker'], quotes)
    return list(ranks)


class Cache:
    stocks: Dict[str, List[Dict]] = {}
    std_dev_vol_ranks = []
    std_dev_price_ranks = []

    def get_stock(self, ticker: str):
        print(self.stocks[ticker])
        if ticker in self.stocks:
            return self.stocks[ticker]
        else:
            return {}

    def update_cache(self) -> None:
        stocks = db.get_all()
        for stock in stocks:
            print(stock)
            ticker = stock['ticker']
            self.stocks[ticker] = stock
        self.std_dev_price_ranks = generate_ranks(stocks, 'std_dev_price')
        self.std_dev_vol_ranks = generate_ranks(stocks, 'std_dev_vol')
