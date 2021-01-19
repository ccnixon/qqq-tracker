from lib.queue import Queue
from worker.store import Store
from worker.quote import Quote
from typing import List, Any, Dict, Optional
from datetime import datetime
import schedule
import requests
import time

queue = Queue('price-updates')

class Worker:
    tickers = ['AAPL', 'MSFT', 'AMZN', 'TSLA', 'FB',
               'GOOG', 'NFLX', 'NVDA', 'PYPL', 'ADBE']
    store = Store(tickers)
    last_quote_time: Optional[str] = None

    """
    Data is pulled using the IEX Cloud API: https://iexcloud.io/
    Data format looks like this: {'AAPL': {'intraday-prices': [{'date': '2021-01-15', 'minute': '15:59', 'label': '3:59 PM', 'high': 127.33, 'low': 127.06, 'open': 127.18, 'close': 127.33, 'average': 127.145, 'volume': 17552, 'notional': 2231643.15, 'numberOfTrades': 155}]}, 'MSFT': {'intraday-prices': [{'date': '2021-01-15', 'minute': '15:59', 'label': '3:59 PM', 'high': 212.935, 'low': 212.57, 'open': 212.785, 'close': 212.57, 'average': 212.722, 'volume': 10639, 'notional': 2263152.585, 'numberOfTrades': 129}]}, 'AMZN': {'intraday-prices': [{'date': '2021-01-15', 'minute': '15:59', 'label': '3:59 PM', 'high': 3108.42, 'low': 3104.05, 'open': 3105.725, 'close': 3106.39, 'average': 3105.845, 'volume': 1177, 'notional': 3655579.06, 'numberOfTrades': 35}]}, 'TSLA': {'intraday-prices': [{'date': '2021-01-15', 'minute': '15:59', 'label': '3:59 PM', 'high': 826.65, 'low': 825.785, 'open': 826.5, 'close': 826.03, 'average': 826.159, 'volume': 18498, 'notional': 15282298.615, 'numberOfTrades': 159}]}, 'FB': {'intraday-prices': [{'date': '2021-01-15', 'minute': '15:59', 'label': '3:59 PM', 'high': 251.66, 'low': 251.19, 'open': 251.5, 'close': 251.34, 'average': 251.355, 'volume': 5676, 'notional': 1426691.42, 'numberOfTrades': 86}]}, 'GOOG': {'intraday-prices': [{'date': '2021-01-15', 'minute': '15:59', 'label': '3:59 PM', 'high': 1737.42, 'low': 1735.12, 'open': 1736.09, 'close': 1736.59, 'average': 1735.759, 'volume': 1297, 'notional': 2251279.54, 'numberOfTrades': 33}]}, 'GOOGL': {'intraday-prices': [{'date': '2021-01-15', 'minute': '15:59', 'label': '3:59 PM', 'high': 1728.77, 'low': 1726.53, 'open': 1727.23, 'close': 1727.54, 'average': 1727.092, 'volume': 1402, 'notional': 2421383.785, 'numberOfTrades': 34}]}, 'NVDA': {'intraday-prices': [{'date': '2021-01-15', 'minute': '15:59', 'label': '3:59 PM', 'high': 514.88, 'low': 514.395, 'open': 514.685, 'close': 514.6, 'average': 514.628, 'volume': 2236, 'notional': 1150707.12, 'numberOfTrades': 42}]}, 'PYPL': {'intraday-prices': [{'date': '2021-01-15', 'minute': '15:59', 'label': '3:59 PM', 'high': 240.11, 'low': 239.76, 'open': 239.94, 'close': 239.77, 'average': 239.893, 'volume': 4505, 'notional': 1080720.21, 'numberOfTrades': 55}]}, 'ADBE': {'intraday-prices': [{'date': '2021-01-15', 'minute': '15:59', 'label': '3:59 PM', 'high': 458.285, 'low': 458.05, 'open': 458.175, 'close': 458.06, 'average': 458.173, 'volume': 3792, 'notional': 1737392.725, 'numberOfTrades': 62}]}}
    """
    def get_data(self) -> Dict:
        symbols = ','.join(self.tickers)
        request_url = f'https://cloud.iexapis.com/stable/stock/market/batch?symbols={symbols}&types=intraday-prices&token=sk_0412fe7872274a30956607284727a7b5&chartLast=1'
        res = requests.get(request_url)
        return res.json()

    def get_quote_time(self, data: Dict) -> str:
        data = data['AAPL']['intraday-prices'][0]
        timestamp = datetime.strptime("{} {}".format(data['date'], data['minute']), '%Y-%m-%d %H:%M')
        return timestamp.strftime('%Y-%m-%d %H:%M')

    def update_store(self) -> None:
        prices = self.get_data()
        quote_time = self.get_quote_time(prices)
        
        if (self.last_quote_time is not None and quote_time == self.last_quote_time):
            print("Duplicate quote detected, skipping")
            return
        else:
            self.last_quote_time = quote_time
        
        for ticker in prices:
            data = prices[ticker]['intraday-prices'].pop()
            avg_price = data['average']
            volume = data['volume']
            stock = self.store.get_stock(ticker)
            stock.update(avg_price, volume)
            queue.push(stock.snapshot())
        
        print("Publishing stock updates")
        queue.flush()
        print("Updates published successfully")


w = Worker()

"""Data is pulled every 1 minute in a loop"""
schedule.every(1).minute.do(w.update_store).run()
while True:
    schedule.run_pending()
    time.sleep(1)
