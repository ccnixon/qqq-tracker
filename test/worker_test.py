import unittest
from worker.store import Store

class StoreUnitTests(unittest.TestCase):
    def test_update(self):
        store = Store(['AAPL'])
        test_data = {'AAPL': {'intraday-prices': [{'date': '2021-01-15', 'minute': '15:59', 'label': '3:59 PM', 'high': 127.33, 'low': 127.06,
                                                   'open': 127.18, 'close': 127.33, 'average': 127.145, 'volume': 17552, 'notional': 2231643.15, 'numberOfTrades': 155}]}}
        store.update(test_data)
        stock = store.get_stock('AAPL')
        self.assertEqual(len(stock.volume), 1)
        self.assertEqual(len(stock.prices.history), 1)

if __name__ == '__main__':
    unittest.main()
