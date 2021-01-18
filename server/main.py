import os
import sys
import threading
import pika
import json
from flask import Flask

from server.cache import Cache

app = Flask(__name__)
cache = Cache()

"""
Return the price and trading volume history for a give ticker.
Also return each of the tracked tickers ranked by the standard deviations of their price or volume specifed by the <metric> param
"""
@app.route('/history/<ticker>/<metric>')
def get_asset(ticker, metric):
    quotes = cache.get_ticker_history(ticker.upper())
    ranks = []
    if metric == 'volume':
      ranks = cache.std_dev_vol_ranks
    if metric == 'price':
      ranks = cache.std_dev_price_ranks
    
    return json.dumps({
      'history': quotes,
      'rankings': ranks
    }), 200, { 'Content-Type': 'application/json' }


def poll_queue():
    credentials = pika.PlainCredentials(username="user", password="bitnami")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost', credentials=credentials))
    channel = connection.channel()

    channel.queue_declare(queue='price-updates')

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)
        cache.update_cache(json.loads(body))

    channel.basic_consume(
        queue='price-updates', on_message_callback=callback, auto_ack=True)

    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == "__main__":
    try:
      thread = threading.Thread(target=poll_queue)
      thread.start()
      app.run()
    except KeyboardInterrupt:
      print('Interrupted')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
