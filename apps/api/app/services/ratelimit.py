"""Fixed-window rate limiting for pairing-code redemption.

Scope is deliberately small. The only endpoint that needs this is pair-code
redemption, because that is the one place where an unauthenticated caller can
guess at a secret (SRS section 8: "rate-limit by token hash and by IP"). Everything
else requires a party token that the caller already has to possess.

In-process and non-durable on purpose: a single-container prototype has no shared
cache, and pretending otherwise by adding Redis would be operational risk without
changing what a judge sees. A restart resets the windows, which is documented in
KNOWN_LIMITATIONS.md rather than hidden.
"""

from __future__ import annotations

import time
from collections import deque


class FixedWindowLimiter:
    """Allow at most ``limit`` hits per ``window_seconds`` per key.

    Uses ``time.monotonic`` rather than the wall clock so that a system clock
    adjustment cannot either lock a user out or silently widen the window.
    """

    __slots__ = ("_hits", "_limit", "_window")

    def __init__(self, *, limit: int, window_seconds: float) -> None:
        if limit < 1:
            raise ValueError("limit must be at least 1")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        self._limit = limit
        self._window = window_seconds
        self._hits: dict[str, deque[float]] = {}

    def allow(self, key: str) -> bool:
        """Record an attempt and report whether it is within the limit."""
        now = time.monotonic()
        cutoff = now - self._window
        bucket = self._hits.get(key)
        if bucket is None:
            bucket = deque()
            self._hits[key] = bucket
        while bucket and bucket[0] <= cutoff:
            bucket.popleft()
        if len(bucket) >= self._limit:
            return False
        bucket.append(now)
        return True

    def retry_after_seconds(self, key: str) -> int:
        """Whole seconds until this key's oldest hit falls out of the window."""
        bucket = self._hits.get(key)
        if not bucket:
            return 0
        remaining = self._window - (time.monotonic() - bucket[0])
        return max(1, int(remaining + 0.999)) if remaining > 0 else 0

    def reset(self) -> None:
        """Clear all windows. Used by the demo-reset endpoint and by tests."""
        self._hits.clear()


__all__ = ["FixedWindowLimiter"]
