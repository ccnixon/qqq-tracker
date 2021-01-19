from typing import List, Dict
from pymongo import MongoClient, operations
client = MongoClient()

mongo = client.stocks
class DB:
  table = mongo.stocks
  def update(self, stocks: List[Dict]):
    requests = []
    for stock in stocks:
      request = operations.UpdateOne({ 'ticker': stock['ticker'] }, { '$set': stock }, upsert=True)
      requests.append(request)
    self.table.bulk_write(requests)
  
  def get_all(self):
    results = []
    stocks = self.table.find({})
    for stock in stocks:
      del stock['_id']
      results.append(stock)
    return results
