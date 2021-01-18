## QQQ Tracker
Service to track price and volume movements of the top ten stocks in the Invesco QQQ etf. The following stocks are tracked:

AAPL, MSFT, AMZN, TSLA, FB, GOOG, NFLX, NVDA, PYPL, ADBE

## Project Overview
This service is composed of two independent service, a `server` and a `worker`.

### Worker
The worker is responsible for polling the IEX Cloud financial data API every minute to gather information on the recent trading activity of the stocks being tracked. With each new batch of data, it does the following:

1. Calculates the standard deviation of the price and volume changes over the past 24 hours and ranks each stock in descending order based on each value.
2. Checks to see if the most recent price and/or volume values have increase by at least 3x from their averages over the past hour. If such an increase has occurred, it triggers a notification to be sent out to users.
3. Publishes the price, volume, and standard deviation metrics to RabbitMQ to be consumed by the server.

### Server
The server is responsible for handling incoming requests for data on the tracked stocks. The service runs two threads. The first is responsible for handling incoming http requests from clients. The second runs in a loop and listens for updates published by the worker to RabbitMQ. When updates arrive, it loads it into an in-memory cache with the data for the http handler to use.

## API
Retrieve the price/volume history for a given stock and the ranking of each tracked stock based on the standard deviation of either their price or volume. The value of the `metric` parameter must be either `volume` or `price`

**Request:**
```
GET `/history/<ticker>/<volume|price>`
```
**Response**
```
{
  history: Array
  rankings: Array
}
```

## Getting Started
### Requirements
You will need python3 and docker-compose installed on your machine.

### Installation
```
git clone https://github.com/ccnixon/qqq-tracker && cd qqq-tracker
pip install -r requirements.txt
docker-compose up -d
```

To run the worker:
```
python worker/main.py
```

To run the server, open a second terminal window and run:
```
pythong server/main.py
```

