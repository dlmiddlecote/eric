from collections import defaultdict
from typing import List, MutableMapping, Set

from visit_aggregator.app import app
from visit_aggregator.agents import active_visitors_channel

import aiohttp
from faust import web
from faust.types.tuples import TP


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


def group_topics(assignment: Set[TP]) -> MutableMapping[str, List[int]]:
    tps: MutableMapping[str, List[int]] = defaultdict(list)
    for tp in sorted(assignment):
        tps[tp.topic].append(tp.partition)
    return dict(tps)


@app.page("/ready")
async def ready(self, request: web.Request) -> web.Response:
    """Return OK if app can serve websocket."""

    topics = group_topics(self.app.assignor.assigned_actives())
    if "active-visitors" in topics:
        return self.json({"status": "OK"}, status=200)
    else:
        return self.json({"status": "NOT READY"}, status=503)