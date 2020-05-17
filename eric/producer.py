import os
import json
import logging
import time
from random import randint
from kafka import KafkaProducer

logger = logging.getLogger(__name__)

# Which Kafka should we connect to?
KAFKA_BROKER = os.getenv("KAFKA_BROKER", default="localhost:9092")


def main():
    kafka_producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)

    p = 0
    while True:
        message = {
            "index": randint(0, 10000),
            "name": "Rincewind",
        }

        key = bytes("key", encoding="utf-8")
        value = bytes(json.dumps(message), encoding="utf-8")

        kafka_producer.send("msgs", key=key, value=value)
        kafka_producer.flush()

        logger.info("Sent message.")

        time.sleep(2)

        p += 1


if __name__ == "__main__":
    main()
