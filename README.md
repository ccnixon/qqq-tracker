## QQQ Tracker
Service to track price and volume movements of the top ten stocks in the Invesco QQQ etf. The following stocks are tracked:

AAPL, MSFT, AMZN, TSLA, FB, GOOG, NFLX, NVDA, PYPL, ADBE

## Getting Started
### Requirements
You will need python 3 and docker-compose installed on your machine.

### Installation
```
git clone https://github.com/ccnixon/qqq-tracker && cd qqq-tracker
pip install -r requirements.txt
docker-compose up -d
```

If necessary, ensure your `PYTHONPATH` is set:
```
export PYTHONPATH="${PYTHONPATH}:${pwd}"
```

To run the worker:
```
python worker/main.py
```

To run the server, open a second terminal window and run:
```
python server/main.py
```
## Architecture
We are leveraging a batch/poll based architecture. This is a simple and straightforward solution. Potential options for more advanced approaches are explored later.

![image](https://user-images.githubusercontent.com/12958606/105150630-4a090000-5b05-11eb-980b-b2f0fb2cb790.png)

### Worker
The worker is responsible for polling the IEX Cloud financial data API every minute to gather information on the recent trading activity (ie. Candlesticks) of the stocks being tracked. With each new batch of data, it does the following:

1. Calculates the standard deviation of the price and volume changes over the past 24 hours.
2. Checks to see if the most recent price and/or volume values have increase by at least 3x from their trailing 60 min. averages. 
3. If such an increase has occurred, it triggers a notification to be sent out to users.
4. Writes the updated the price, volume, and standard deviation metrics to the database to be consumed by the server.

### Server
The server is responsible for handling incoming requests for data on the tracked stocks. The application runs two threads. The first (the API) is responsible for handling incoming http requests from clients. The second (the cache runner) runs in a loop and continuously updates an in-memory cache (used by the API) with new data from the database.

## API
### Get stock data
Retrieve the price/volume history for a given stock and the ranking of each tracked stock based on the standard deviation of either their price or volume. The value of the `metric` parameter must be either `volume` or `price`

**Request:**
```
GET `/<ticker>/volume|price`
```
**Response**
```
{
  prices|volume: Array
  rankings: Array
}
```

### Subscribe to stock notifications
Subscribe to notifications. An email will be sent whenever a stock exceeds the trailing 60 min average of your chosen metric by at least 3x.

**Request:**
```
POST `/subscribe`
{
  email: String
  metric: volume|price
  ticker: string
}
```

## Deployment and Scaling Strategy
The service is comprised of three separate entities (server, worker, and the db) so I'll address each separately.

### Server
The server would be deployed using a container management solution like Kubernetes or ECS. The server itself could scale easily to handle high volume.

### DB
MongoDB is being used as the database. Mongo provides scalability and performance at the expense of some consistency guarantees. This could be an issue depending on what this service is actually being used for so a decision would need to be made about what the underlying persistence layer long term should be. Potential alternatives are explored below.

### Worker
The worker does not really need to scale at all. It is simply polling an API for new data and is not exposed to any kind of external pressure that would require additional capacity. The easiest solution would be to deploy and run the worker using Lambda.

## Questions
**What would you change if you needed to track many metrics?**
At some point the speed of the worker process execution loop could could start to lag behind the frequency of updates being provided by the API. A more sophisticated approach to account for this could involve using some kind of data stream processing framework such as Kafka Streams, Spark, Flink, etc. This could potentially allow us to scale the worker horizontally.

I might look at [Faust](https://faust.readthedocs.io/en/latest/) as a starting point.

**What if you needed to sample them more frequently?**
Similar to the last question. The approach I would take is look into moving away from the poll based system we have now towards more of a stream processing architecture.

**What if you had many users accessing your dashboard to view metrics?**
Assuming we were running on something like Kubernetes or ECS then the server should be able to easily scale out to handle high usage. The database would also need to be scaled as well but Mongo is [capable of handling this quite well](https://www.mongodb.com/blog/post/crittercism-scaling-to-billions-of-requests-per).

**How would you track the health and uptime of your application?  What are the key metrics/events you would be alerting on?**
Besides the usual APM metrics (runtime errors, memory issues, CPU usage, etc.) we would likely want to monitor the following:
1. Server Latency - how quickly are we handling requests for stock data
2. Database latency - how fast are reads/writes happening
3. Data Integrity :) - has the data being generated by our worker node changed unexpectedly or become corrupted?
4. Worker execution speed - is our worker executing in sub 60 seconds?

**How would you extend testing for an application of this kind (beyond what you implemented)?**
1. Server endpoint integration tests
2. Testing for the notification feature
