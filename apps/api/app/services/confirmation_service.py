"""Two-party confirmation of one exact payload.

The rule this module exists to enforce (INV-02/INV-03): a confirmation is a
statement about a specific set of details, so it is recorded *as* that set of
details -- the hash of the canonical payload the party was shown -- and not as a
bare boolean. Two consequences follow automatically rather than by remembering to
check:

*   A confirmation carrying a hash that is no longer current is refused, because
    the party confirmed something that has since changed (INV-02).
*   A confirmation already on file stops counting the moment the payload moves,
    because ``CaseRow.seller_confirmed`` compares the stored hash to the current
    one and ``refresh`` nulls both columns on any change (INV-03).

Neither confirmation is an electronic signature, and the UI must not describe it
as one. It is a recorded agreement between two parties inside a prototype.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..db import repository as repo
from ..domain.canonical import payload_hash
from ..domain.states import Actor, CaseState
from ..errors import AppError
from .case_service import authorise_actor, load_case
from .context import ServiceContext
from .projection import CaseView, load_view, refresh

#: States in which a party may confirm.
#:
#: All three require ``submit`` to have passed, which is what makes REVIEW_READY
#: mean "both parties can act now" rather than "one of you is still waiting on the
#: other". `SELLER_CONFIRMED` and `BOTH_CONFIRMED` are included so re-sending the
#: same confirmation is harmless and so the second party can act.
CONFIRMABLE_STATES: frozenset[CaseState] = frozenset(
    {
        CaseState.REVIEW_READY,
        CaseState.SELLER_CONFIRMED,
        CaseState.BOTH_CONFIRMED,
    }
)


@dataclass(frozen=True, slots=True)
class ConfirmationResult:
    view: CaseView
    actor: Actor
    #: True when this actor's confirmation was already on file for this exact
    #: payload. The endpoint still returns 200: repeating a confirmation is not an
    #: error, and treating a double-tap as a failure would be worse UX than
    #: treating it as a no-op.
    already_confirmed: bool


class ConfirmationService:
    def __init__(self, ctx: ServiceContext) -> None:
        self.ctx = ctx

    def confirm(
        self, *, case_id: str, token: str | None, payload_hash_claim: str
    ) -> ConfirmationResult:
        if not payload_hash_claim:
            raise AppError("VALIDATION_ERROR", detail={"field": "payload_hash"})

        with self.ctx.db.write() as connection:
            case_row = load_case(connection, case_id)
            actor = authorise_actor(connection, case_id=case_id, token=token)
            if actor is Actor.SYSTEM:  # pragma: no cover - never issued to a device
                raise AppError("UNAUTHORISED_ACTOR")

            if case_row.current_state is CaseState.HANDOFF_ACKNOWLEDGED:
                raise AppError("ALREADY_ACKNOWLEDGED")
            if case_row.current_state is CaseState.SUBMITTING_29C:
                raise AppError("SUBMISSION_IN_PROGRESS")
            if case_row.current_state not in CONFIRMABLE_STATES:
                raise AppError(
                    "INVALID_STATE", detail={"state": case_row.current_state.value}
                )

            # Recomputed here rather than trusted from the cases row. The stored
            # hash and the recomputed one agree on every code path that exists
            # today; recomputing means that if they ever disagreed, the outcome
            # would be a refused confirmation rather than an accepted one against
            # a payload nobody had seen.
            view = load_view(self.ctx, connection, case_row)
            if view.payload is None:
                raise AppError(
                    "INVALID_STATE", detail={"state": case_row.current_state.value}
                )
            current_hash = payload_hash(view.payload)
            if (
                payload_hash_claim != current_hash
                or current_hash != case_row.payload_hash
            ):
                # No hash in the detail: the UX bar keeps digests out of the normal
                # UI, and the client's recovery path is to re-read the case anyway.
                raise AppError("STALE_PAYLOAD", detail={"reason": "PAYLOAD_CHANGED"})

            already = (
                case_row.seller_confirmed
                if actor is Actor.SELLER
                else case_row.dealer_confirmed
            )
            column = (
                "seller_confirmed_hash"
                if actor is Actor.SELLER
                else "dealer_confirmed_hash"
            )
            repo.update_case(connection, case_id, **{column: current_hash})

            case_row = load_case(connection, case_id)
            refreshed = refresh(
                self.ctx,
                connection,
                case_row,
                actor=actor,
                event_type=(
                    "SELLER_CONFIRMED"
                    if actor is Actor.SELLER
                    else "DEALER_CONFIRMED"
                ),
                detail={"repeat": already},
            )
        return ConfirmationResult(
            view=refreshed, actor=actor, already_confirmed=already
        )

    def withdraw(self, *, case_id: str, token: str | None) -> ConfirmationResult:
        """Take back this party's confirmation before submission.

        Included because the alternative -- a party who has spotted a problem but
        can only either submit or abandon the case -- is worse than letting them
        step back. Not available once a submission is in flight or acknowledged,
        for the same reason a submission cannot be cancelled mid-flight.
        """
        with self.ctx.db.write() as connection:
            case_row = load_case(connection, case_id)
            actor = authorise_actor(connection, case_id=case_id, token=token)

            if case_row.current_state is CaseState.HANDOFF_ACKNOWLEDGED:
                raise AppError("ALREADY_ACKNOWLEDGED")
            if case_row.current_state is CaseState.SUBMITTING_29C:
                raise AppError("SUBMISSION_IN_PROGRESS")
            if case_row.current_state not in CONFIRMABLE_STATES:
                raise AppError(
                    "INVALID_STATE", detail={"state": case_row.current_state.value}
                )

            column = (
                "seller_confirmed_hash"
                if actor is Actor.SELLER
                else "dealer_confirmed_hash"
            )
            repo.update_case(connection, case_id, **{column: None})
            case_row = load_case(connection, case_id)
            refreshed = refresh(
                self.ctx,
                connection,
                case_row,
                actor=actor,
                event_type="CONFIRMATION_WITHDRAWN",
            )
        return ConfirmationResult(view=refreshed, actor=actor, already_confirmed=False)


__all__ = ["CONFIRMABLE_STATES", "ConfirmationResult", "ConfirmationService"]
