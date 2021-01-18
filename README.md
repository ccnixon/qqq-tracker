## QQQ Tracker
Service to track price and volume movements of the top ten stocks in the Invesco QQQ etf. The following stocks are tracked:

AAPL, MSFT, AMZN, TSLA, FB, GOOG, NFLX, NVDA, PYPL, ADBE

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
python server/main.py
```
## Architecture
This service is composed of two independent services, a `server` and a `worker`.

### Worker
The worker is responsible for polling the IEX Cloud financial data API every minute to gather information on the recent trading activity of the stocks being tracked. With each new batch of data, it does the following:

1. Calculates the standard deviation of the price and volume changes over the past 24 hours and ranks each stock in descending order based on each value.
2. Checks to see if the most recent price and/or volume values have increase by at least 3x from their averages over the past hour. If such an increase has occurred, it triggers a notification to be sent out to users.
3. Publishes the price, volume, and standard deviation metrics to RabbitMQ to be consumed by the server.

### Server
The server is responsible for handling incoming requests for data on the tracked stocks. The application runs two threads. The first is responsible for handling incoming http requests from clients. The second runs in a loop and listens for updates published by the worker to RabbitMQ. When updates arrive, it loads them into an in-memory cache for the http handler to use.

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

## Deployment and Scaling Strategy
The service is comprised of three separate entities (server, worker, and queue) so I'll address each separately.

### Server
The server would be deployed using a container management solution like Kubernetes or ECS. 

The only constraint preventing the system from basically infinite scalability is the queue the service connects to. Depending on the underlying technology powering the queue, too many client connections could begin to strangle the queue cluster. This is addressed in the next section.

### Queue
This prototype uses RabbitMQ for the sake of simplicity but this **would not** be the right choice long term. RabbitMQ is a message queue however in our system, each node in the server cluster needs to receive its own copy of the data being published by the worker and this is not how message queues work. Instead, we will need a pubsub framework in order to scale beyond a single node. The main options for this would be either Kafka or Kinesis.

The cluster running the queue would need to be able to scale in tandem with the server cluster. As new nodes are added to the server, the queue would need to scale up to handle the increase in client connections.

### Worker
The worker does not really need to scale at all. It is simply polling an API for new data and is not exposed to any kind of external pressure that would require additional capacity. The easiest solution would be to deploy and run the worker using Lambda.

## Questions
**What would you change if you needed to track many metrics?**
Depending on how many metrics we decide to track, the service could start running into memory issues as it currently stores the past 24 hours of data for each stock in memory. To handle this, we would likely need to look into inserting a persistence layer somewhere. The tradeoff would be the overall speed of the system.

**What if you needed to sample them more frequently?**
The frequency at which we could sample data would be bound by the speed at which our worker process could execute updates as we would need to ensure each execution finished before starting a new one. That being said, the worker would probably be able to handle a high fairly high frequency as it is performing very little I/O.

The bigger bottleneck might be the server nodes. Too many updates to the queue consumer on each node could starve resources. In this situation we might need to move away from the push based architecture and instead have each consumer pull data lazily (at request time) or on a loop either from a persistent queue or from an alternative persistence mechanism (likely a high performant DB). 

Depending on the approach we take, the tradeoff is that our request latency might suffer or our data might be lagging a bit.

**What if you had many users accessing your dashboard to view metrics?**
This should not be an issue. The server cluster could easily scale assuming we were using a cluster management tool as proposed above.

**How would you track the health and uptime of your application?  What are the key metrics/events you would be alerting on?**
Besides the usual APM metrics (runtime errors, memory issues, CPU usage, etc.) we would likely want to monitor the following:
1. Server Latency - how quickly are we handling requests for stock data
2. Consumer Lag - are our server nodes struggling to keep up with the data being published by our Worker node?
3. Data Integrity :) - has the data being published by our worker node changed unexpectedly or become corrupted?
4. Worker execution speed - we would need to ensure our worker was executing within the expected time window to prevent potentially missing data

**How would you extend testing for an application of this kind (beyond what you implemented)?**
1. More integration tests between the worker and server
2. Server endpoint integration tests
3. Testing for the notification feature
