import unittest
from unittest import mock
from worker.notifier import Notifier

from flask import wrappers
from worker.store import Store
from lib.db import DB
from pymongo.mongo_client import MongoClient
from worker.stock import Stock

db = DB(client=MongoClient())

class StoreUnitTests(unittest.TestCase):
    def test_update(self):
        store = Store(['AAPL'], db)
        test_data = {'AAPL': {'intraday-prices': [{'date': '2021-01-15', 'minute': '15:59', 'label': '3:59 PM', 'high': 127.33, 'low': 127.06,
                                                   'open': 127.18, 'close': 127.33, 'average': 127.145, 'volume': 17552, 'notional': 2231643.15, 'numberOfTrades': 155}]}}
        store.update(test_data)
        stock = store.get_stock('AAPL')
        self.assertEqual(len(stock.volume), 1)
        self.assertEqual(len(stock.prices), 1)

    def test_duplicate(self):
        store = Store(['AAPL'], db)
        test_data = {'AAPL': {'intraday-prices': [{'date': '2021-01-15', 'minute': '15:59', 'label': '3:59 PM', 'high': 127.33, 'low': 127.06,
                                                   'open': 127.18, 'close': 127.33, 'average': 127.145, 'volume': 17552, 'notional': 2231643.15, 'numberOfTrades': 155}]}}
        store.update(test_data)
        with mock.patch.object(db, 'update_stocks', wraps=db.update_stocks) as monkey:
            store.update(test_data)
            monkey.assert_not_called()

class StockUnitTests(unittest.TestCase):
    def test_update(self):
        stock = Stock('AAPL', Notifier(db))
        stock.update(50, 100)
        self.assertEqual(len(stock.volume), 1)
        self.assertEqual(len(stock.prices), 1)
        self.assertEqual(stock.volume[0], 100)
        self.assertEqual(stock.prices[0], 50)


if __name__ == '__main__':
    unittest.main()
