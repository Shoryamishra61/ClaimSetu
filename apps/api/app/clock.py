"""Time and identifier generation, isolated so tests can control them.

Both live here rather than being called inline because determinism is a product
requirement (09_QA_TEST_DEMO_RELIABILITY.md section 6). A test that needs a fixed
acknowledgement time or a predictable case id overrides the provider rather than
monkeypatching ``datetime`` globally.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

#: India Standard Time. The backend stores UTC and only converts for display, so
#: this exists for presentation and for the canonical ``handover_local_time``.
IST = timezone(timedelta(hours=5, minutes=30))


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    return utc_now().isoformat()


def to_ist_iso(moment: datetime) -> str:
    return moment.astimezone(IST).isoformat()


def iso_plus_seconds(seconds: int) -> str:
    return (utc_now() + timedelta(seconds=seconds)).isoformat()


def parse_iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        # Stored timestamps are always tz-aware; a naive value means data written
        # by something other than this module, so fail loudly rather than guess.
        raise ValueError(f"Timestamp {value!r} has no timezone")
    return parsed


def is_expired(expires_at: str, *, now: datetime | None = None) -> bool:
    return (now or utc_now()) >= parse_iso(expires_at)


def new_id() -> str:
    return str(uuid.uuid4())
