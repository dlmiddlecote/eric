import os
import json
from random import random
from kafka import KafkaProducer

# Which Kafka should we connect to?
KAFKA_BROKER = os.getenv("KAFKA_BROKER", default="kafka://localhost:9092")
TOPIC = 'test'
KEY = 'test'


def publish_message(producer_instance, topic_name, key, value):
    try:
        key_bytes = bytes(key, encoding='utf-8')
        value_bytes = bytes(value, encoding='utf-8')
        producer_instance.send(topic_name, key=key_bytes, value=value_bytes)
        producer_instance.flush()
        print('Message published successfully.')
    except Exception as ex:
        print('Exception in publishing message')
        print(ex)


def connect_kafka_producer():
    _producer = None
    try:
        # host.docker.internal is how a docker container connects to the local
        # machine.
        # Don't use in production, this only works with Docker for Mac in
        # development
        _producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER])
    except Exception as ex:
        print('Exception while connecting Kafka')
        print(ex)
    return _producer


if __name__ == '__main__':
    kafka_producer = connect_kafka_producer()
    index = 0
    while True:
        message = {
            'index': index % 8,
            'name': 'Rincewind',
        }
        publish_message(kafka_producer, TOPIC, KEY, json.dumps(message))
        index += 1

    if kafka_producer is not None:
        kafka_producer.close()
