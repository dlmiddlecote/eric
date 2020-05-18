import asyncio
import logging
import random
import time
import uuid
from typing import Tuple

from faust.cli import AppCommand, option

from visit_aggregator.app import app
from visit_aggregator.models import Visit

logger: logging.Logger = logging.getLogger("visit_aggregator")


@app.command(
    option(
        "--frequency",
        type=float,
        default=1,
        help="The frequency in which messages are produced per second.",
        show_default=True,
    ),
    option(
        "--max-messages", type=int, default=300, help="The maximum number of messages to produce.", show_default=True,
    ),
    option(
        "--account-id", type=int, default=(352,), multiple=True, help="Account IDs to produce for.", show_default=True,
    ),
    option(
        "--store-id",
        type=str,
        default=("default",),
        multiple=True,
        help="Store IDs to produce for.",
        show_default=True,
    ),
)
async def produce(
    self: AppCommand, frequency: float, max_messages: int, account_id: Tuple[int], store_id: Tuple[int]
) -> None:
    """
    Produce visits for the visit-aggregator
    """

    visit_topic = app.topic("visits", value_type=Visit, internal=True)

    logger.warning(f"Producing {max_messages} messages to the visits topic at {frequency} per second.")

    for _ in range(max_messages):
        visit = Visit(
            id=str(uuid.uuid4()),
            account_id=random.choice(account_id),
            store_id=random.choice((None,) + store_id),
            timestamp=time.time(),
        )

        await visit_topic.send(value=visit)

        logger.warning("Message sent.")

        await asyncio.sleep(1 / frequency)

    logger.warning(f"Produced {max_messages} messages.")
