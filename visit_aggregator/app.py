from typing import Optional

import faust

from visit_aggregator.config import Configuration


def create_app(config: Optional[Configuration] = None) -> faust.App:
    """
    Create and configure the Faust application.
    """

    config = config if config else Configuration()

    app = faust.App(
        id="visitor-aggregator",
        broker=config.broker,
        store=config.store,
        autodiscover=True,
        origin="visit_aggregator",
        topic_partitions=config.topic_partitions,
    )

    return app


# Default configuration
config: Configuration = Configuration()


# App with default configuration
app: faust.App = create_app(config)
