"""Row-level persistence operations.

Every function takes an open ``sqlite3.Connection`` so the caller owns the
transaction boundary. That is deliberate: a state transition, the declaration
writes that caused it, and the audit event that records it must all land or all
roll back, and that is only expressible if the service decides the boundary.

The single most important function here is ``transition_state``. It is the only
way ``cases.current_state`` changes, and it does so with a compare-and-set against
the states the caller believed were current. Two concurrent submits therefore
cannot both proceed: the loser's UPDATE matches zero rows and it raises.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass

from .. import clock
from ..domain.states import CaseState, IllegalTransition, assert_transition


class ConcurrentModification(Exception):
    """The row changed between read and write; the caller must re-read and retry."""


class DuplicateIdempotencyKey(Exception):
    """``(case_id, idempotency_key)`` already exists. Not an error by itself --
    ``SubmissionService`` treats it as "return the stored result"."""


# ---------------------------------------------------------------------------
# cases
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CaseRow:
    id: str
    journey_type: str
    current_state: CaseState
    policy_version: str
    vehicle_id: str | None
    dealer_id: str | None
    dealer_status_at_verify: str | None
    handover_local_time: str | None
    payload_hash: str | None
    seller_confirmed_hash: str | None
    dealer_confirmed_hash: str | None
    created_at: str
    updated_at: str

    @property
    def seller_confirmed(self) -> bool:
        """A confirmation counts only while it still matches the current payload."""
        return (
            self.payload_hash is not None
            and self.seller_confirmed_hash == self.payload_hash
        )

    @property
    def dealer_confirmed(self) -> bool:
        return (
            self.payload_hash is not None
            and self.dealer_confirmed_hash == self.payload_hash
        )


def _to_case(row: sqlite3.Row) -> CaseRow:
    return CaseRow(
        id=row["id"],
        journey_type=row["journey_type"],
        current_state=CaseState(row["current_state"]),
        policy_version=row["policy_version"],
        vehicle_id=row["vehicle_id"],
        dealer_id=row["dealer_id"],
        dealer_status_at_verify=row["dealer_status_at_verify"],
        handover_local_time=row["handover_local_time"],
        payload_hash=row["payload_hash"],
        seller_confirmed_hash=row["seller_confirmed_hash"],
        dealer_confirmed_hash=row["dealer_confirmed_hash"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def insert_case(
    connection: sqlite3.Connection,
    *,
    case_id: str,
    journey_type: str,
    policy_version: str,
    state: CaseState,
) -> CaseRow:
    now = clock.utc_now_iso()
    connection.execute(
        """
        INSERT INTO cases (id, journey_type, current_state, policy_version,
                           created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (case_id, journey_type, state.value, policy_version, now, now),
    )
    fetched = get_case(connection, case_id)
    assert fetched is not None  # just inserted inside this transaction
    return fetched


def get_case(connection: sqlite3.Connection, case_id: str) -> CaseRow | None:
    row = connection.execute(
        "SELECT * FROM cases WHERE id = ?", (case_id,)
    ).fetchone()
    return _to_case(row) if row is not None else None


#: Columns a caller may change through ``update_case``. Anything outside this set
#: is either immutable (id, journey_type, created_at) or has a dedicated function
#: with its own guard (current_state).
_UPDATABLE_CASE_COLUMNS = frozenset(
    {
        "vehicle_id",
        "dealer_id",
        "dealer_status_at_verify",
        "handover_local_time",
        "payload_hash",
        "seller_confirmed_hash",
        "dealer_confirmed_hash",
    }
)


def update_case(
    connection: sqlite3.Connection, case_id: str, **fields: object
) -> None:
    unknown = set(fields) - _UPDATABLE_CASE_COLUMNS
    if unknown:
        raise KeyError(
            f"Cannot update {sorted(unknown)} through update_case. "
            f"Allowed: {sorted(_UPDATABLE_CASE_COLUMNS)}"
        )
    if not fields:
        return
    assignments = ", ".join(f"{name} = ?" for name in fields)
    connection.execute(
        f"UPDATE cases SET {assignments}, updated_at = ? WHERE id = ?",
        (*fields.values(), clock.utc_now_iso(), case_id),
    )


def transition_state(
    connection: sqlite3.Connection,
    case_id: str,
    *,
    expected: Iterable[CaseState],
    new_state: CaseState,
) -> CaseState:
    """Move the case to ``new_state``, but only from one of ``expected``.

    Two layers of protection, and both are load-bearing:

    1.  ``assert_transition`` checks the state graph, so a caller cannot invent an
        edge that the product does not allow (for example straight to
        HANDOFF_ACKNOWLEDGED).
    2.  The ``WHERE current_state IN (...)`` clause makes the write conditional on
        the state still being what the caller read. Under ``BEGIN IMMEDIATE`` this
        is a genuine compare-and-set.

    Returns the state actually written. Raises ``ConcurrentModification`` if the
    row moved underneath the caller, and ``IllegalTransition`` if the edge does
    not exist.
    """
    expected_states = tuple(expected)
    if not expected_states:
        raise ValueError("transition_state requires at least one expected state")
    for state in expected_states:
        assert_transition(state, new_state)

    placeholders = ", ".join("?" for _ in expected_states)
    cursor = connection.execute(
        f"""
        UPDATE cases SET current_state = ?, updated_at = ?
        WHERE id = ? AND current_state IN ({placeholders})
        """,
        (
            new_state.value,
            clock.utc_now_iso(),
            case_id,
            *(state.value for state in expected_states),
        ),
    )
    if cursor.rowcount != 1:
        current = get_case(connection, case_id)
        raise ConcurrentModification(
            f"Case {case_id} is in "
            f"{current.current_state.value if current else 'MISSING'}, expected one "
            f"of {[s.value for s in expected_states]}"
        )
    return new_state


def transition_if_needed(
    connection: sqlite3.Connection,
    case_row: CaseRow,
    *,
    new_state: CaseState,
) -> CaseState:
    """``transition_state`` that tolerates the case already being there.

    Used where an operation is naturally idempotent -- re-verifying the same
    vehicle, or re-deriving REVIEW_READY after a no-op declaration write.
    """
    if case_row.current_state is new_state:
        return new_state
    return transition_state(
        connection,
        case_row.id,
        expected=(case_row.current_state,),
        new_state=new_state,
    )


# ---------------------------------------------------------------------------
# declarations
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class DeclarationRow:
    code: str
    value: bool
    source_type: str
    policy_version: str
    actor: str
    updated_at: str


def get_declarations(
    connection: sqlite3.Connection, case_id: str
) -> dict[str, DeclarationRow]:
    rows = connection.execute(
        "SELECT * FROM declarations WHERE case_id = ? ORDER BY code", (case_id,)
    ).fetchall()
    return {
        row["code"]: DeclarationRow(
            code=row["code"],
            value=bool(row["value"]),
            source_type=row["source_type"],
            policy_version=row["policy_version"],
            actor=row["actor"],
            updated_at=row["updated_at"],
        )
        for row in rows
    }


def declaration_values(connection: sqlite3.Connection, case_id: str) -> dict[str, bool]:
    return {
        code: row.value for code, row in get_declarations(connection, case_id).items()
    }


def upsert_declarations(
    connection: sqlite3.Connection,
    case_id: str,
    *,
    values: Mapping[str, bool],
    source_types: Mapping[str, str],
    policy_version: str,
    actor: str,
) -> None:
    now = clock.utc_now_iso()
    connection.executemany(
        """
        INSERT INTO declarations (case_id, code, value, source_type, policy_version,
                                  actor, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(case_id, code) DO UPDATE SET
            value = excluded.value,
            source_type = excluded.source_type,
            policy_version = excluded.policy_version,
            actor = excluded.actor,
            updated_at = excluded.updated_at
        """,
        [
            (
                case_id,
                code,
                1 if value else 0,
                source_types[code],
                policy_version,
                actor,
                now,
            )
            for code, value in values.items()
        ],
    )


def clear_confirmations(connection: sqlite3.Connection, case_id: str) -> None:
    """INV-03: any mutation of canonical fields drops both confirmations.

    Setting the columns to NULL rather than comparing hashes at read time means a
    later bug in hash comparison cannot resurrect a confirmation that should have
    been invalidated.
    """
    connection.execute(
        """
        UPDATE cases
        SET seller_confirmed_hash = NULL, dealer_confirmed_hash = NULL,
            updated_at = ?
        WHERE id = ?
        """,
        (clock.utc_now_iso(), case_id),
    )


# ---------------------------------------------------------------------------
# pair sessions
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class PairSessionRow:
    id: str
    case_id: str
    expires_at: str
    consumed_at: str | None
    dealer_session_id: str | None
    created_at: str


def _to_pair(row: sqlite3.Row) -> PairSessionRow:
    return PairSessionRow(
        id=row["id"],
        case_id=row["case_id"],
        expires_at=row["expires_at"],
        consumed_at=row["consumed_at"],
        dealer_session_id=row["dealer_session_id"],
        created_at=row["created_at"],
    )


def insert_pair_session(
    connection: sqlite3.Connection,
    *,
    pair_id: str,
    case_id: str,
    token_hash: str,
    expires_at: str,
) -> PairSessionRow:
    connection.execute(
        """
        INSERT INTO pair_sessions (id, case_id, token_hash, expires_at, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (pair_id, case_id, token_hash, expires_at, clock.utc_now_iso()),
    )
    row = connection.execute(
        "SELECT * FROM pair_sessions WHERE id = ?", (pair_id,)
    ).fetchone()
    return _to_pair(row)


def find_pair_session_by_hash(
    connection: sqlite3.Connection, token_hash: str
) -> PairSessionRow | None:
    row = connection.execute(
        "SELECT * FROM pair_sessions WHERE token_hash = ?", (token_hash,)
    ).fetchone()
    return _to_pair(row) if row is not None else None


def latest_pair_session(
    connection: sqlite3.Connection, case_id: str
) -> PairSessionRow | None:
    row = connection.execute(
        """
        SELECT * FROM pair_sessions WHERE case_id = ?
        ORDER BY created_at DESC, rowid DESC LIMIT 1
        """,
        (case_id,),
    ).fetchone()
    return _to_pair(row) if row is not None else None


def consume_pair_session(
    connection: sqlite3.Connection,
    *,
    pair_id: str,
    dealer_session_id: str,
) -> None:
    """Mark the code used, conditional on it not already being used.

    The ``consumed_at IS NULL`` predicate is what makes one-time use real. Checking
    in Python first and updating second would leave a race in which two dealers
    both redeem the same code.
    """
    cursor = connection.execute(
        """
        UPDATE pair_sessions
        SET consumed_at = ?, dealer_session_id = ?
        WHERE id = ? AND consumed_at IS NULL
        """,
        (clock.utc_now_iso(), dealer_session_id, pair_id),
    )
    if cursor.rowcount != 1:
        raise ConcurrentModification(f"Pair session {pair_id} was already consumed")


def invalidate_pair_sessions(connection: sqlite3.Connection, case_id: str) -> None:
    """Burn every unused code for a case.

    Called when a new code is issued, so "generate a new code" cannot leave an
    older, still-valid code floating around on a screenshot.
    """
    connection.execute(
        """
        UPDATE pair_sessions SET consumed_at = ?
        WHERE case_id = ? AND consumed_at IS NULL
        """,
        (clock.utc_now_iso(), case_id),
    )


# ---------------------------------------------------------------------------
# party sessions
# ---------------------------------------------------------------------------


def insert_party_session(
    connection: sqlite3.Connection,
    *,
    session_id: str,
    case_id: str,
    actor: str,
    token_hash: str,
) -> None:
    connection.execute(
        """
        INSERT INTO party_sessions (id, case_id, actor, token_hash, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (session_id, case_id, actor, token_hash, clock.utc_now_iso()),
    )


def find_party_session(
    connection: sqlite3.Connection, *, case_id: str, token_hash: str
) -> str | None:
    """Return the actor this token authorises for the case, or None."""
    row = connection.execute(
        "SELECT actor FROM party_sessions WHERE case_id = ? AND token_hash = ?",
        (case_id, token_hash),
    ).fetchone()
    return row["actor"] if row is not None else None


def has_party_session(
    connection: sqlite3.Connection, *, case_id: str, actor: str
) -> bool:
    row = connection.execute(
        "SELECT 1 FROM party_sessions WHERE case_id = ? AND actor = ? LIMIT 1",
        (case_id, actor),
    ).fetchone()
    return row is not None


# ---------------------------------------------------------------------------
# submission attempts
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SubmissionAttemptRow:
    id: str
    case_id: str
    idempotency_key: str
    request_hash: str
    attempt_number: int
    status: str | None
    acknowledgement_no: str | None
    reason_code: str | None
    created_at: str
    completed_at: str | None


def _to_attempt(row: sqlite3.Row) -> SubmissionAttemptRow:
    return SubmissionAttemptRow(
        id=row["id"],
        case_id=row["case_id"],
        idempotency_key=row["idempotency_key"],
        request_hash=row["request_hash"],
        attempt_number=row["attempt_number"],
        status=row["status"],
        acknowledgement_no=row["acknowledgement_no"],
        reason_code=row["reason_code"],
        created_at=row["created_at"],
        completed_at=row["completed_at"],
    )


def insert_attempt(
    connection: sqlite3.Connection,
    *,
    attempt_id: str,
    case_id: str,
    idempotency_key: str,
    request_hash: str,
    attempt_number: int,
) -> SubmissionAttemptRow:
    """Claim an idempotency key.

    Raises ``DuplicateIdempotencyKey`` if the key is already claimed. This is the
    real enforcement point for INV-05: the UNIQUE index decides, so two requests
    racing with the same key cannot both create an attempt no matter how the
    application code is scheduled.
    """
    try:
        connection.execute(
            """
            INSERT INTO submission_attempts (id, case_id, idempotency_key,
                                             request_hash, attempt_number, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                attempt_id,
                case_id,
                idempotency_key,
                request_hash,
                attempt_number,
                clock.utc_now_iso(),
            ),
        )
    except sqlite3.IntegrityError as exc:
        raise DuplicateIdempotencyKey(
            f"Idempotency key already used for case {case_id}"
        ) from exc
    row = connection.execute(
        "SELECT * FROM submission_attempts WHERE id = ?", (attempt_id,)
    ).fetchone()
    return _to_attempt(row)


def find_attempt_by_key(
    connection: sqlite3.Connection, *, case_id: str, idempotency_key: str
) -> SubmissionAttemptRow | None:
    row = connection.execute(
        """
        SELECT * FROM submission_attempts
        WHERE case_id = ? AND idempotency_key = ?
        """,
        (case_id, idempotency_key),
    ).fetchone()
    return _to_attempt(row) if row is not None else None


def complete_attempt(
    connection: sqlite3.Connection,
    *,
    attempt_id: str,
    status: str,
    acknowledgement_no: str | None,
    reason_code: str | None,
) -> None:
    """Record the adapter's answer, once.

    ``completed_at IS NULL`` in the predicate makes the write single-shot: a
    recorded outcome can never be overwritten, so an UNKNOWN cannot be quietly
    rewritten as an ACK by a second code path. Reconciliation creates a new
    attempt row instead.
    """
    cursor = connection.execute(
        """
        UPDATE submission_attempts
        SET status = ?, acknowledgement_no = ?, reason_code = ?, completed_at = ?
        WHERE id = ? AND completed_at IS NULL
        """,
        (status, acknowledgement_no, reason_code, clock.utc_now_iso(), attempt_id),
    )
    if cursor.rowcount != 1:
        raise ConcurrentModification(
            f"Submission attempt {attempt_id} already has a recorded outcome"
        )


def latest_attempt(
    connection: sqlite3.Connection, case_id: str
) -> SubmissionAttemptRow | None:
    row = connection.execute(
        """
        SELECT * FROM submission_attempts WHERE case_id = ?
        ORDER BY attempt_number DESC, rowid DESC LIMIT 1
        """,
        (case_id,),
    ).fetchone()
    return _to_attempt(row) if row is not None else None


def list_attempts(
    connection: sqlite3.Connection, case_id: str
) -> list[SubmissionAttemptRow]:
    rows = connection.execute(
        """
        SELECT * FROM submission_attempts WHERE case_id = ?
        ORDER BY attempt_number ASC, rowid ASC
        """,
        (case_id,),
    ).fetchall()
    return [_to_attempt(row) for row in rows]


def count_attempts(connection: sqlite3.Connection, case_id: str) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS n FROM submission_attempts WHERE case_id = ?", (case_id,)
    ).fetchone()
    return int(row["n"])


def acknowledged_attempt(
    connection: sqlite3.Connection, case_id: str
) -> SubmissionAttemptRow | None:
    """The ACK attempt for this case, if one exists.

    ``SubmissionService`` uses this as the sole authority for INV-01. The green
    terminal state is derived from a row here, never from a state flag alone.
    """
    row = connection.execute(
        """
        SELECT * FROM submission_attempts
        WHERE case_id = ? AND status = 'ACK' AND acknowledgement_no IS NOT NULL
        ORDER BY attempt_number ASC LIMIT 1
        """,
        (case_id,),
    ).fetchone()
    return _to_attempt(row) if row is not None else None


# ---------------------------------------------------------------------------
# audit events
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AuditEventRow:
    id: int
    case_id: str
    event_type: str
    actor: str
    state_before: str | None
    state_after: str | None
    payload_digest: str | None
    detail: dict[str, object]
    created_at: str
    previous_event_hash: str | None
    event_hash: str


def _to_event(row: sqlite3.Row) -> AuditEventRow:
    return AuditEventRow(
        id=int(row["id"]),
        case_id=row["case_id"],
        event_type=row["event_type"],
        actor=row["actor"],
        state_before=row["state_before"],
        state_after=row["state_after"],
        payload_digest=row["payload_digest"],
        detail=json.loads(row["detail"]) if row["detail"] else {},
        created_at=row["created_at"],
        previous_event_hash=row["previous_event_hash"],
        event_hash=row["event_hash"],
    )


def _event_hash(
    *,
    previous_event_hash: str | None,
    case_id: str,
    event_type: str,
    actor: str,
    state_before: str | None,
    state_after: str | None,
    payload_digest: str | None,
    detail_json: str,
    created_at: str,
) -> str:
    material = json.dumps(
        {
            "previous_event_hash": previous_event_hash,
            "case_id": case_id,
            "event_type": event_type,
            "actor": actor,
            "state_before": state_before,
            "state_after": state_after,
            "payload_digest": payload_digest,
            "detail": detail_json,
            "created_at": created_at,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def append_event(
    connection: sqlite3.Connection,
    *,
    case_id: str,
    event_type: str,
    actor: str,
    state_before: CaseState | None = None,
    state_after: CaseState | None = None,
    payload_digest: str | None = None,
    detail: Mapping[str, object] | None = None,
) -> AuditEventRow:
    """Append one link to the case's audit chain.

    Runs inside the caller's transaction, so an event cannot be recorded for a
    state change that rolled back, and a state change cannot happen without its
    event.
    """
    previous = connection.execute(
        "SELECT event_hash FROM audit_events WHERE case_id = ? ORDER BY id DESC LIMIT 1",
        (case_id,),
    ).fetchone()
    previous_hash = previous["event_hash"] if previous is not None else None
    created_at = clock.utc_now_iso()
    detail_json = json.dumps(
        dict(detail or {}), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    before = state_before.value if state_before is not None else None
    after = state_after.value if state_after is not None else None
    digest = _event_hash(
        previous_event_hash=previous_hash,
        case_id=case_id,
        event_type=event_type,
        actor=actor,
        state_before=before,
        state_after=after,
        payload_digest=payload_digest,
        detail_json=detail_json,
        created_at=created_at,
    )
    cursor = connection.execute(
        """
        INSERT INTO audit_events (case_id, event_type, actor, state_before,
                                  state_after, payload_digest, detail, created_at,
                                  previous_event_hash, event_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            case_id,
            event_type,
            actor,
            before,
            after,
            payload_digest,
            detail_json,
            created_at,
            previous_hash,
            digest,
        ),
    )
    row = connection.execute(
        "SELECT * FROM audit_events WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    return _to_event(row)


def list_events(connection: sqlite3.Connection, case_id: str) -> list[AuditEventRow]:
    rows = connection.execute(
        "SELECT * FROM audit_events WHERE case_id = ? ORDER BY id ASC", (case_id,)
    ).fetchall()
    return [_to_event(row) for row in rows]


def verify_chain(events: Sequence[AuditEventRow]) -> bool:
    """Recompute every link. False means a row was edited or removed."""
    previous_hash: str | None = None
    for event in events:
        if event.previous_event_hash != previous_hash:
            return False
        expected = _event_hash(
            previous_event_hash=previous_hash,
            case_id=event.case_id,
            event_type=event.event_type,
            actor=event.actor,
            state_before=event.state_before,
            state_after=event.state_after,
            payload_digest=event.payload_digest,
            detail_json=json.dumps(
                event.detail, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            ),
            created_at=event.created_at,
        )
        if expected != event.event_hash:
            return False
        previous_hash = event.event_hash
    return True


__all__ = [
    "AuditEventRow",
    "CaseRow",
    "ConcurrentModification",
    "DeclarationRow",
    "DuplicateIdempotencyKey",
    "IllegalTransition",
    "PairSessionRow",
    "SubmissionAttemptRow",
    "acknowledged_attempt",
    "append_event",
    "clear_confirmations",
    "complete_attempt",
    "consume_pair_session",
    "count_attempts",
    "declaration_values",
    "find_attempt_by_key",
    "find_pair_session_by_hash",
    "find_party_session",
    "get_case",
    "get_declarations",
    "has_party_session",
    "insert_attempt",
    "insert_case",
    "insert_pair_session",
    "insert_party_session",
    "invalidate_pair_sessions",
    "latest_attempt",
    "latest_pair_session",
    "list_attempts",
    "list_events",
    "transition_if_needed",
    "transition_state",
    "update_case",
    "upsert_declarations",
    "verify_chain",
]
