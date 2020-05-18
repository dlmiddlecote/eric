import hashlib
import logging
from datetime import datetime
from typing import Tuple, List

import aiohttp
import faust
from faust.types import TopicT, StreamT

from visit_aggregator.app import app, config
from visit_aggregator.models import Visit, ActiveVisitors

logger: logging.Logger = logging.getLogger("visit_aggregator")

# Topic that receives visits.
visit_topic: TopicT = app.topic("visits", value_type=Visit, internal=True)

# Topic that receives active visitor counts.
active_visitors_topic: TopicT = app.topic("active-visitors", value_type=ActiveVisitors, partitions=1, internal=True)


def process_window(key: Tuple, visits: List[Visit]) -> None:
    """
    Process a window of visits, and publish an aggregated `ActiveVisitors` to
    the correct topic.
    """

    # Unpack the key
    (account_id, store_id), (start, end) = key

    # We add 0.1 since Faust defines the window range as (start, start + size - 0.1)
    # See: https://github.com/robinhood/faust/blob/master/faust/types/windows.py#L16
    window = (start, end + 0.1)

    active_visitors = ActiveVisitors(account_id=account_id, store_id=store_id, window=window, count=len(visits))

    active_visitors_topic.send_soon(value=active_visitors)

    logger.info(f"Aggregated visits for account {account_id}'s store {store_id}")


# Table that persists visits to be aggregated.
# `process_window` is called whenever a window expires.
table = (
    app.Table(
        "visitors-tumbling-window",
        default=list,
        on_window_close=process_window,
        help=f"Persist visits from visits topic in windows of {config.window_size}s.",
    )
    .tumbling(size=config.window_size, expires=config.window_expires)
    .relative_to_field(Visit.timestamp)
)


def partition_by_account_store(visit: Visit) -> str:
    """
    Compute partition key for visit.
    """

    key = f"{visit.account_id}:{visit.store_id}"
    hsh = int(hashlib.sha1(key.encode("utf-8")).hexdigest(), 16) % config.topic_partitions
    return str(hsh)


@app.agent(visit_topic)
async def process_visits(stream: StreamT) -> None:
    """
    Update the tumbling window with incoming visits.
    """
    async for visit in stream.group_by(
        partition_by_account_store, name="account_store", partitions=config.topic_partitions
    ):
        key = (visit.account_id, visit.store_id)
        visits = set(table[key].value())
        visits.add(visit.id)
        table[key] = list(visits)


# Channel to use for sending active visitors over websocket connection.
active_visitors_channel = app.channel(value_type=ActiveVisitors)


@app.agent(active_visitors_topic)
async def process_active_visitors(stream: StreamT) -> None:
    """
    Display active visitors aggregate.
    """
    async for av in stream:
        from_timestamp, to_timestamp = av.window
        dt_from = datetime.fromtimestamp(from_timestamp)
        dt_to = datetime.fromtimestamp(to_timestamp)
        logger.info(
            f"(Account {av.account_id}, Store {av.store_id}): {av.count} visits in window <{dt_from} => {dt_to}>"
        )

        await active_visitors_channel.send(value=av)


@app.page("/ws")
async def websocket_handler(self, request):
    """
    Push new active visitor counts to websocket.
    """

    # Prepare request for websocket
    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)

    async for event in active_visitors_channel:
        av = event.value
        await ws.send_json(
            {
                "account_id": av.account_id,
                "store_id": av.store_id,
                "ts_from": av.window[0],
                "ts_to": av.window[1],
                "count": av.count,
            }
        )
