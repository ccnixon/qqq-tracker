import statistics
from typing import List, Dict, Optional
from worker.notifier import Notifier
from lib.db import DB


class Stock:
    ticker: str
    volume: List[int]
    prices: List[float]
    std_dev_vol: float
    std_dev_price: float
    notifier: Notifier

    def __init__(self, ticker: str, notifier: Notifier) -> None:
        self.ticker = ticker
        self.volume = []
        self.prices = []
        self.std_dev_price = 0
        self.std_dev_vol = 0
        self.notifier = notifier

    """Check to see if the stock's price and/or volume have exceeded 3x their average from the past 60 min"""

    def check_for_average_deviation(self, current_price, current_volume) -> None:
        prices = self.prices
        volume = self.volume

        # Only check for average deviation if we have at least an hour of price data.
        if (len(prices) < 60):
            return

        avg_price = statistics.median(prices)
        avg_volume = statistics.median(volume)

        if (current_price > (3*avg_price)):
            self.notifier.send_notifications('price', self.ticker)
        if (avg_volume > (3*current_volume)):
            self.notifier.send_notifications('volume', self.ticker)

    """Update the stock volume and price history and calulate the standard deviation"""

    def update(self, price: Optional[float], volume: int):
        self.check_for_average_deviation(price, volume)
        vol = self.volume
        prices = self.prices
        vol.append(volume)
        if price is not None:
            prices.append(price)

        if len(prices) > 1:
            self.std_dev_price = statistics.stdev(prices)

        if len(vol) > 1:
            self.std_dev_vol = statistics.stdev(vol)

        # Only keep the last 24h worth of history in memory
        if (len(prices) > (60*24)):
            prices.pop(0)
        
        if (len(vol) > (60*24)):
            vol.pop(0)

    def snapshot(self) -> Dict:
        return {
            'ticker': self.ticker,
            'price': self.prices,
            'volume': self.volume,
            'std_dev_vol': self.std_dev_vol,
            'std_dev_price': self.std_dev_price
        }
