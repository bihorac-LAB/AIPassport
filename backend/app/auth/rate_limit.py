"""In-process sliding-window rate limiter.

Keyed by ``(scope, identity)`` where identity is the user UUID when authenticated and the client IP
otherwise. One class, one method — swap ``_hits`` for Redis to make it multi-instance.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque

from fastapi import Request

from app.core.errors import RateLimited
from app.core.logging import get_logger

log = get_logger("aipassport.ratelimit")


class RateLimiter:
    def __init__(self) -> None:
        self._hits: dict[tuple[str, str], deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, scope: str, identity: str, *, limit: int, window_seconds: int) -> None:
        """Record a hit and raise :class:`RateLimited` when the window budget is exhausted."""
        if limit <= 0:
            return
        now = time.monotonic()
        cutoff = now - window_seconds
        key = (scope, identity)
        with self._lock:
            bucket = self._hits[key]
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            if len(bucket) >= limit:
                retry_after = max(1, int(window_seconds - (now - bucket[0])))
                log.info("rate_limited", scope=scope, limit=limit, window=window_seconds)
                raise RateLimited(
                    "Too many requests. Please wait before trying again.",
                    headers={"Retry-After": str(retry_after)},
                )
            bucket.append(now)

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


limiter = RateLimiter()


def client_ip(request: Request) -> str:
    """Trust ``X-Forwarded-For`` only for its left-most entry, which our proxy sets."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
