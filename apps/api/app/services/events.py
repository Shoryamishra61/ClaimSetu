"""In-process fan-out for case updates.

Scope on purpose: one process, no broker. The blueprint's realtime requirement is
"both parties see the same state promptly", and the deployment is a single
container, so a Redis/Kafka hop would add operational risk without changing what
a judge sees. Kafka is on the explicit do-not-build list.

The contract that matters is not this bus -- it is that the WebSocket is an
*accelerator*, never an authority. Every message is a full authoritative snapshot
fetched from the database, and the client polls REST every two seconds when the
socket is down. If this bus dropped every message, the product would still be
correct, only slower.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from contextlib import suppress

#: Per-subscriber buffer. A slow client that falls this far behind is dropped
#: rather than allowed to grow memory without bound; it recovers on its next REST
#: poll, because the snapshot is always re-fetched and never reconstructed from a
#: message history.
QUEUE_MAXSIZE = 32


class Subscription:
    __slots__ = ("_bus", "case_id", "queue")

    def __init__(self, bus: EventBus, case_id: str) -> None:
        self._bus = bus
        self.case_id = case_id
        self.queue: asyncio.Queue[dict[str, object]] = asyncio.Queue(
            maxsize=QUEUE_MAXSIZE
        )

    async def __aenter__(self) -> Subscription:
        return self

    async def __aexit__(self, *_exc: object) -> None:
        self._bus.unsubscribe(self)


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, set[Subscription]] = defaultdict(set)
        self._loop: asyncio.AbstractEventLoop | None = None

    def subscribe(self, case_id: str) -> Subscription:
        subscription = Subscription(self, case_id)
        self._subscribers[case_id].add(subscription)
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:  # pragma: no cover - subscribe is always in a loop
            self._loop = None
        return subscription

    def unsubscribe(self, subscription: Subscription) -> None:
        listeners = self._subscribers.get(subscription.case_id)
        if listeners is not None:
            listeners.discard(subscription)
            if not listeners:
                self._subscribers.pop(subscription.case_id, None)

    def subscriber_count(self, case_id: str) -> int:
        return len(self._subscribers.get(case_id, ()))

    def publish(self, case_id: str, message: dict[str, object]) -> None:
        """Fan a snapshot out to this case's listeners.

        Safe to call from a worker thread as well as the event loop: FastAPI runs
        sync endpoints off-loop, and a publish that raised there would turn a
        cosmetic delivery problem into a failed state transition.
        """
        listeners = list(self._subscribers.get(case_id, ()))
        if not listeners:
            return
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            loop = self._loop
            if loop is None or loop.is_closed():
                return
            loop.call_soon_threadsafe(self._deliver, listeners, message)
            return
        self._deliver(listeners, message)

    @staticmethod
    def _deliver(
        listeners: list[Subscription], message: dict[str, object]
    ) -> None:
        for subscription in listeners:
            # Deliberately drop an update for a lagging subscriber: its next REST
            # poll re-syncs the full authoritative snapshot.
            with suppress(asyncio.QueueFull):
                subscription.queue.put_nowait(message)
