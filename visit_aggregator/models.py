from typing import Optional, Tuple

import faust


class Visit(faust.Record, serializer="json"):
    """Visit Message"""

    id: str
    account_id: int
    store_id: Optional[str]
    timestamp: float


class ActiveVisitors(faust.Record, serializer="json"):
    """Aggregate number of visitors in time window"""

    account_id: int
    store_id: Optional[str]
    window: Tuple[float, float]
    count: int
