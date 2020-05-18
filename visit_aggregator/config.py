import os
from dataclasses import dataclass


@dataclass
class Configuration:
    """
    Configuration for visit_aggregator
    """

    # The Kafka Broker URL.
    broker: str = os.getenv("KAFKA_BROKER", default="kafka://localhost:9092")

    # The backend for table storage.
    store: str = os.getenv("STORE", "memory://")

    # Size of Tumbling Window in seconds, used to aggregate visits.
    window_size: float = float(os.getenv("WINDOW_SIZE", "60"))

    # Expiration time of Tumbling Window after close. Controls how often the
    # aggregation callback function is called.
    window_expires: float = float(os.getenv("WINDOW_EXPIRES", "10"))

    # Default number of partitions for new topics.
    topic_partitions: int = int(os.getenv("TOPIC_PARITIONS", "4"))
