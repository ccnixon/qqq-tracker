from typing import List, Dict
from pymongo import MongoClient, operations
client = MongoClient()

mongo = client.stocks
class DB:
  stocks_table = mongo.stocks
  subscriptions_table = mongo.subscriptions
  def update_stocks(self, stocks: List[Dict]):
    requests = []
    for stock in stocks:
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
