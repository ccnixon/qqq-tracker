import os
import sys
import threading
import json
from flask import Flask, request, Response
from lib.db import DB
from server.cache import Cache
from lib.constants import SUPPORTED_TICKERS, SUPPORTED_METRICS
import schedule
import time
from flask_expects_json import expects_json

app = Flask(__name__)
cache = Cache()
db = DB()

"""
Return the price and trading volume history for a give ticker.
Also return each of the tracked tickers ranked by the standard deviations of their price or volume specifed by the <metric> param
"""
@app.route('/<ticker>/<metric>')
def get_asset(ticker, metric):    
    if metric not in SUPPORTED_METRICS:
      return 'Invalid Metric', 400
    
    stock = cache.get_stock(ticker.upper())
    history = []
    ranks = []
    
    if stock is None:
      return 'No info found for ticker', 404
    
    if metric == 'volume':
      ranks = cache.std_dev_vol_ranks
      history = stock['volume']
    if metric == 'price':
      ranks = cache.std_dev_price_ranks
      history = stock['prices']
    
    return json.dumps({
      metric: history,
      'rankings': ranks
    }), 200, { 'Content-Type': 'application/json' }

@app.route('/subscribe/', methods=['POST'])
@expects_json({
  'type': 'object',
  'properties': {
      'ticker': {'type': 'string' },
      'email': {'type': 'string'},
      'metric': {'type': 'string', 'enum': SUPPORTED_METRICS }
  },
  'required': ['email', 'ticker', 'metric']
})
def add_subscription():
  body = request.get_json()
  ticker = body['ticker']
  email = body['email']
  metric = body['metric']
  
  if ticker.upper() not in SUPPORTED_TICKERS:
      return Response(400, 'Invalid Ticker')
  
  db.add_subscription(ticker, email, metric)
  return Response(status=201)


def update_cache():
  schedule.every(1).minute.do(cache.update_cache).run()
  while True:
    schedule.run_pending()
    time.sleep(1)


if __name__ == "__main__":
    try:
      thread = threading.Thread(target=update_cache)
      thread.start()
      app.run()
    except KeyboardInterrupt:
      print('Interrupted')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
