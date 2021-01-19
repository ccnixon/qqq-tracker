from typing import List
import pika
import json

credentials = pika.PlainCredentials(username="user", password="bitnami")
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', credentials=credentials))
channel = connection.channel()
channel.queue_declare(queue='price-updates')


class Queue:
    payload: List
    topic: str
    def __init__(self, topic: str) -> None:
        super().__init__()
        self.payload = []
        self.topic = topic

    def push(self, data) -> None:
        self.payload.append(data)

    def flush(self) -> None:
        channel.basic_publish(exchange='', routing_key=self.topic, body=json.dumps(self.payload))
        self.payload = []
