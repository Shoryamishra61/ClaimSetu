"""One-time seller -> dealer pairing.

The pairing code is the mechanism by which two devices come to be looking at the
same case. What it is *not*, and what the UI must never imply it is:

*   not proof that the two people are in the same place -- there is no GPS, no
    proximity check and no distance threshold anywhere in this project;
*   not identity verification of the dealer -- it proves possession of a code the
    seller showed, nothing more;
*   not a signature.

Its single security property is that it can be redeemed exactly once, within a
short window, and only for the case it was issued against. That property is
enforced by the database (``consume_pair_session``'s ``consumed_at IS NULL``
predicate), not by a check-then-write in Python.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass

from .. import clock
from ..db import repository as repo
from ..domain.states import Actor, CaseState
from ..errors import AppError
from .case_service import (
    authorise_actor,
    hash_token,
    issue_party_token,
    load_case,
)
from .context import ServiceContext
from .projection import CaseView, load_view, refresh
from .ratelimit import FixedWindowLimiter

#: States in which inviting the dealer makes sense.
#:
#: `PREFLIGHT_PASSED` is the normal entry point: the seller's own readiness items
#: are done, and the one remaining blocking item is the dealer's possession
#: declaration. Deliberately excludes `DEALER_VERIFIED` -- asking a dealer to join
#: a handover whose checklist is unfinished wastes their time.
PAIRING_ALLOWED_STATES: frozenset[CaseState] = frozenset(
    {
        CaseState.PREFLIGHT_PASSED,
        CaseState.REVIEW_READY,
        CaseState.SELLER_CONFIRMED,
        CaseState.BOTH_CONFIRMED,
        CaseState.SUBMISSION_REJECTED,
        CaseState.SUBMISSION_TEMPORARY_FAILURE,
    }
)

#: Redemption attempts allowed per window. Two limiters, as SRS section 8 requires:
#: one keyed by the hash of the submitted code (so guessing a *specific* code is
#: bounded) and one keyed by client address (so guessing *any* code is bounded).
REDEEM_LIMIT_PER_CODE = 5
REDEEM_LIMIT_PER_CLIENT = 20
REDEEM_WINDOW_SECONDS = 60.0


@dataclass(frozen=True, slots=True)
class IssuedPairCode:
    view: CaseView
    #: Returned exactly once, to the seller's screen. Only its SHA-256 is stored,
    #: and it is never written to an audit event or a log line.
    code: str
    expires_at: str
    expires_in_seconds: int


@dataclass(frozen=True, slots=True)
class RedeemedPairCode:
    view: CaseView
    case_id: str
    #: The dealer device's party token, returned once.
    dealer_token: str


class PairingService:
    def __init__(self, ctx: ServiceContext) -> None:
        self.ctx = ctx
        self._by_code = FixedWindowLimiter(
            limit=REDEEM_LIMIT_PER_CODE, window_seconds=REDEEM_WINDOW_SECONDS
        )
        self._by_client = FixedWindowLimiter(
            limit=REDEEM_LIMIT_PER_CLIENT, window_seconds=REDEEM_WINDOW_SECONDS
        )

    def reset_limits(self) -> None:
        self._by_code.reset()
        self._by_client.reset()

    # -- issue -----------------------------------------------------------------

    def issue_code(self, *, case_id: str, token: str | None) -> IssuedPairCode:
        """Mint a fresh code and burn any earlier unused one for this case.

        Superseding matters: without it, a code left visible on an earlier
        screenshot or a still-open tab would stay redeemable.
        """
        with self.ctx.db.write() as connection:
            case_row = load_case(connection, case_id)
            authorise_actor(
                connection, case_id=case_id, token=token, required=Actor.SELLER
            )
            if case_row.current_state is CaseState.HANDOFF_ACKNOWLEDGED:
                raise AppError("ALREADY_ACKNOWLEDGED")
            if case_row.current_state not in PAIRING_ALLOWED_STATES:
                raise AppError(
                    "INVALID_STATE", detail={"state": case_row.current_state.value}
                )

            repo.invalidate_pair_sessions(connection, case_id)
            code = secrets.token_urlsafe(self.ctx.settings.pair_token_bytes)
            ttl = self.ctx.settings.pair_token_ttl_seconds
            expires_at = clock.iso_plus_seconds(ttl)
            repo.insert_pair_session(
                connection,
                pair_id=clock.new_id(),
                case_id=case_id,
                token_hash=hash_token(code),
                expires_at=expires_at,
            )
            repo.append_event(
                connection,
                case_id=case_id,
                event_type="PAIR_CODE_ISSUED",
                actor=Actor.SELLER.value,
                state_after=case_row.current_state,
                # No code, and no code hash: an audit trail that recorded either
                # would turn a read-only trail into a credential store.
                detail={"expires_in_seconds": ttl},
            )
            view = load_view(self.ctx, connection, case_row)
        return IssuedPairCode(
            view=view, code=code, expires_at=expires_at, expires_in_seconds=ttl
        )

    def current_code_status(self, *, case_id: str) -> repo.PairSessionRow | None:
        """The latest pair session, for rendering "code expires in N seconds".

        Returns the row, which carries no token material -- only timestamps.
        """
        with self.ctx.db.read() as connection:
            return repo.latest_pair_session(connection, case_id)

    # -- redeem ----------------------------------------------------------------

    def redeem(self, *, code: str, client_key: str = "unknown") -> RedeemedPairCode:
        """Join a case as the dealer, consuming the code.

        Failure ordering is chosen so the message is the most accurate one
        available: an unrecognised code is never described as "expired", and a code
        that was genuinely redeemed by a dealer is never described as "replaced".
        """
        if not code:
            raise AppError("PAIR_CODE_INVALID")
        token_hash = hash_token(code)
        if not self._by_client.allow(client_key):
            raise AppError(
                "RATE_LIMITED",
                detail={"retry_after_seconds": self._by_client.retry_after_seconds(client_key)},
            )
        if not self._by_code.allow(token_hash):
            raise AppError(
                "RATE_LIMITED",
                detail={"retry_after_seconds": self._by_code.retry_after_seconds(token_hash)},
            )

        with self.ctx.db.write() as connection:
            session = repo.find_pair_session_by_hash(connection, token_hash)
            if session is None:
                raise AppError("PAIR_CODE_INVALID")
            if session.consumed_at is not None:
                # A session consumed *with* a dealer session id was really redeemed.
                # One consumed without is a code the seller superseded, which is a
                # different situation and gets the "ask for a new one" wording.
                if session.dealer_session_id is not None:
                    raise AppError("PAIR_CODE_ALREADY_USED")
                raise AppError("PAIR_CODE_EXPIRED", detail={"reason": "SUPERSEDED"})
            if clock.is_expired(session.expires_at):
                raise AppError("PAIR_CODE_EXPIRED")

            case_row = load_case(connection, session.case_id)
            if case_row.current_state is CaseState.HANDOFF_ACKNOWLEDGED:
                raise AppError("ALREADY_ACKNOWLEDGED")
            if case_row.current_state not in PAIRING_ALLOWED_STATES:
                raise AppError(
                    "INVALID_STATE", detail={"state": case_row.current_state.value}
                )

            dealer_session_id = clock.new_id()
            # The party session and the pair session share one id, so the audit
            # trail can tie "this code was redeemed" to "this device may act as the
            # dealer" without storing either credential.
            dealer_token = issue_party_token(
                connection,
                case_id=case_row.id,
                actor=Actor.DEALER,
                session_id=dealer_session_id,
            )
            # Consume last, and conditionally. If two dealers race, exactly one
            # UPDATE matches a row and the loser's whole transaction rolls back --
            # including the party session it had just written.
            repo.consume_pair_session(
                connection,
                pair_id=session.id,
                dealer_session_id=dealer_session_id,
            )
            case_row = load_case(connection, case_row.id)
            view = refresh(
                self.ctx,
                connection,
                case_row,
                actor=Actor.DEALER,
                event_type="DEALER_JOINED",
                detail={"pair_session_id": session.id},
            )
        return RedeemedPairCode(
            view=view, case_id=view.case.id, dealer_token=dealer_token
        )


__all__ = [
    "PAIRING_ALLOWED_STATES",
    "IssuedPairCode",
    "PairingService",
    "RedeemedPairCode",
]
