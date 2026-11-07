"""In-process pub/sub keyed by paper id. Safe to publish from worker threads."""
from __future__ import annotations

import asyncio
import threading
from typing import Any


class EventBus:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._subs: dict[str, list[tuple[asyncio.AbstractEventLoop, asyncio.Queue]]] = {}

    def subscribe(self, paper_id: str) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=1000)
        loop = asyncio.get_running_loop()
        with self._lock:
            self._subs.setdefault(paper_id, []).append((loop, q))
        return q

    def unsubscribe(self, paper_id: str, q: asyncio.Queue) -> None:
        with self._lock:
            subs = self._subs.get(paper_id, [])
            self._subs[paper_id] = [s for s in subs if s[1] is not q]

    def publish(self, paper_id: str, event: dict[str, Any]) -> None:
        with self._lock:
            subs = list(self._subs.get(paper_id, []))
        for loop, q in subs:
            try:
                loop.call_soon_threadsafe(_put, q, event)
            except RuntimeError:  # loop closed
                pass


def _put(q: asyncio.Queue, event: dict) -> None:
    try:
        q.put_nowait(event)
    except asyncio.QueueFull:
        pass


bus = EventBus()
