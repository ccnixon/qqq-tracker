from typing import Collection, List, Dict
from pymongo import MongoClient, operations
from pymongo.database import Database
class DB:
  client: MongoClient
  _db: Database
  stocks_table: Collection
  subscriptions_table: Collection

  def __init__(self, client: MongoClient) -> None:
      super().__init__()
      self.client = client
      self._db = self.client.market_tracker
      self.stocks_table = self._db.stocks
      self.subscriptions_table = self._db.subscriptions
  
  def update_stocks(self, stocks: List[Dict]):
    requests = []
    for stock in stocks:
      print(stock)
      request = operations.UpdateOne({ 'ticker': stock['ticker'] }, { '$set': stock }, upsert=True)
      requests.append(request)
    self.stocks_table.bulk_write(requests)
  
  def get_stocks(self):
    results = []
    stocks = self.stocks_table.find({})
    for stock in stocks:
      del stock['_id']
      results.append(stock)
    return results

  def add_subscription(self, ticker: str, email: str, metric: str) -> None:
    self.subscriptions_table.update({ 'ticker': ticker }, { '$push': { metric: email } }, upsert=True)
  
  def get_subscriptions(self, ticker: str) -> List[str]:
    subscriptions = self.subscriptions_table.find({ 'ticker': ticker })
    return list(subscriptions)
