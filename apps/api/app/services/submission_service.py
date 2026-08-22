"""Submission to the simulated Form 29C boundary, and the acknowledgement gate.

This module carries the product invariant, so it is worth being explicit about the
three separate things it keeps apart:

*   **Confirmation** is two parties agreeing to one set of details. Handled in
    ``confirmation_service``. It reaches BOTH_CONFIRMED and stops.
*   **Submission** is this module sending that payload to the simulated adapter.
    It produces SUBMITTING_29C, which is a real, observable, non-green state.
*   **Acknowledgement** is a persisted attempt row carrying an acknowledgement
    number. Only that writes HANDOFF_ACKNOWLEDGED.

Nothing here can shortcut from the second to the third. The ACK transition is
guarded on re-reading ``acknowledged_attempt`` *after* the outcome is written, so
the green state is a consequence of a committed row rather than of the branch the
code happened to take (INV-01).

The split into :meth:`begin` and :meth:`complete` is not incidental. It exists so
that SUBMITTING_29C is committed and visible to the other party's device before the
adapter is consulted, which is what makes the in-flight state honest rather than a
spinner the frontend invents.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..adapters.mock_form29c_adapter import (
    Form29CSubmissionResponse,
    ReasonCode,
    SubmissionOutcome,
)
from ..clock import new_id
from ..db import repository as repo
from ..db.repository import ConcurrentModification, DuplicateIdempotencyKey
from ..domain.canonical import payload_hash
from ..domain.states import Actor, CaseState
from ..errors import AppError
from .case_service import authorise_actor, load_case
from .context import ServiceContext
from .projection import CaseView, LookupPurpose, load_view, refresh

#: States from which a submission may start.
#:
#: SUBMISSION_TEMPORARY_FAILURE is included because a transient failure leaves the
#: confirmations intact and valid -- the payload never changed, so asking both
#: parties to re-confirm would be theatre. SUBMISSION_REJECTED is deliberately
#: excluded: a definitive rejection means the details were wrong, so the parties go
#: back through review.
SUBMITTABLE_STATES: frozenset[CaseState] = frozenset(
    {
        CaseState.BOTH_CONFIRMED,
        CaseState.SUBMISSION_TEMPORARY_FAILURE,
    }
)

#: Which state each non-ACK outcome lands in.
_OUTCOME_STATE: dict[SubmissionOutcome, CaseState] = {
    SubmissionOutcome.REJECTED: CaseState.SUBMISSION_REJECTED,
    SubmissionOutcome.TEMPORARY_FAILURE: CaseState.SUBMISSION_TEMPORARY_FAILURE,
    SubmissionOutcome.UNKNOWN: CaseState.SUBMISSION_UNKNOWN,
}


@dataclass(frozen=True, slots=True)
class BeganSubmission:
    """The case is now in SUBMITTING_29C and this attempt row owns the outcome."""

    view: CaseView
    attempt_id: str
    attempt_number: int
    scenario: str
    request_hash: str


@dataclass(frozen=True, slots=True)
class SubmissionResult:
    view: CaseView
    attempt: repo.SubmissionAttemptRow
    #: True when no adapter call happened because this idempotency key already had
    #: a recorded outcome. The client sees the original answer (INV-05).
    replayed: bool

    @property
    def acknowledgement_no(self) -> str | None:
        """Never derived from ``status`` alone.

        Reads the acknowledgement off the view's persisted ACK row, so a response
        object cannot report a number the database does not hold.
        """
        ack = self.view.acknowledgement
        return ack.acknowledgement_no if ack is not None else None


class SubmissionService:
    def __init__(self, ctx: ServiceContext) -> None:
        self.ctx = ctx

    # -- phase 1: claim the attempt and enter SUBMITTING_29C --------------------

    def begin(
        self,
        *,
        case_id: str,
        token: str | None,
        payload_hash_claim: str,
        idempotency_key: str,
    ) -> BeganSubmission | SubmissionResult:
        """Guard, revalidate, claim the idempotency key, enter SUBMITTING_29C.

        Returns a :class:`SubmissionResult` instead when the key already carries a
        recorded outcome: that is a replay, and it must not reach the adapter.
        """
        if not idempotency_key:
            raise AppError("IDEMPOTENCY_KEY_REQUIRED")
        if not payload_hash_claim:
            raise AppError("VALIDATION_ERROR", detail={"field": "payload_hash"})

        # -- authorise, and answer replays before doing anything expensive -----
        with self.ctx.db.read() as connection:
            case_row = load_case(connection, case_id)
            authorise_actor(connection, case_id=case_id, token=token)
            existing = repo.find_attempt_by_key(
                connection, case_id=case_id, idempotency_key=idempotency_key
            )
            if existing is not None:
                if existing.completed_at is None:
                    # Same key, no outcome yet: a request with this key is in
                    # flight. Refusing is the only answer that cannot produce two
                    # submissions for one key.
                    raise AppError("SUBMISSION_IN_PROGRESS")
                if existing.request_hash != payload_hash_claim:
                    raise AppError(
                        "IDEMPOTENCY_KEY_REUSED",
                        detail={"reason": "DIFFERENT_PAYLOAD"},
                    )
                return SubmissionResult(
                    view=load_view(self.ctx, connection, case_row),
                    attempt=existing,
                    replayed=True,
                )
            if case_row.current_state is CaseState.HANDOFF_ACKNOWLEDGED:
                # A new key against an acknowledged case is a genuinely new
                # submission request, and there is nothing left to submit.
                raise AppError("ALREADY_ACKNOWLEDGED")

        # -- INV-04: revalidate the dealer at submit time -----------------------
        #
        # In its own transaction, which commits before any refusal is raised. If
        # revalidation finds the authorisation is no longer active, the case must
        # *stay* in DEALER_INVALID -- rolling that back to satisfy a raise would
        # leave the UI claiming the dealer is fine while the submission mysteriously
        # keeps failing.
        with self.ctx.db.write() as connection:
            case_row = load_case(connection, case_id)
            if case_row.current_state not in SUBMITTABLE_STATES:
                raise AppError(
                    "INVALID_STATE", detail={"state": case_row.current_state.value}
                )
            view = refresh(
                self.ctx,
                connection,
                case_row,
                actor=Actor.SYSTEM,
                event_type="SUBMIT_REVALIDATION",
                detail={"purpose": LookupPurpose.REVALIDATION.value, "simulated": True},
                dealer_purpose=LookupPurpose.REVALIDATION,
            )

        self._raise_for_revalidation(view)

        # -- claim the key and enter the in-flight state ------------------------
        with self.ctx.db.write() as connection:
            case_row = load_case(connection, case_id)
            if case_row.current_state not in SUBMITTABLE_STATES:
                raise AppError(
                    "INVALID_STATE", detail={"state": case_row.current_state.value}
                )
            view = load_view(self.ctx, connection, case_row)
            if view.payload is None or view.vehicle is None:
                raise AppError(
                    "INVALID_STATE", detail={"state": case_row.current_state.value}
                )
            current_hash = payload_hash(view.payload)
            if (
                payload_hash_claim != current_hash
                or current_hash != case_row.payload_hash
            ):
                raise AppError("STALE_PAYLOAD", detail={"reason": "PAYLOAD_CHANGED"})
            if not (case_row.seller_confirmed and case_row.dealer_confirmed):
                # Reachable if a confirmation was withdrawn between the guard above
                # and this transaction. Checked again rather than assumed from the
                # state, because the state was read a moment ago.
                raise AppError("CONFIRMATIONS_INCOMPLETE")

            attempt_id = new_id()
            attempt_number = repo.count_attempts(connection, case_id) + 1
            try:
                attempt = repo.insert_attempt(
                    connection,
                    attempt_id=attempt_id,
                    case_id=case_id,
                    idempotency_key=idempotency_key,
                    request_hash=current_hash,
                    attempt_number=attempt_number,
                )
            except DuplicateIdempotencyKey:
                # Lost the race with a concurrent request carrying the same key.
                # The UNIQUE index is the arbiter (INV-05); this branch only
                # translates it into the client contract.
                raise AppError("SUBMISSION_IN_PROGRESS") from None

            state_before = case_row.current_state
            try:
                repo.transition_state(
                    connection,
                    case_id,
                    expected=tuple(SUBMITTABLE_STATES),
                    new_state=CaseState.SUBMITTING_29C,
                )
            except ConcurrentModification:
                raise AppError("SUBMISSION_IN_PROGRESS") from None
            repo.append_event(
                connection,
                case_id=case_id,
                event_type="SUBMISSION_STARTED",
                actor=Actor.SYSTEM.value,
                state_before=state_before,
                state_after=CaseState.SUBMITTING_29C,
                payload_digest=current_hash,
                detail={
                    "attempt_number": attempt_number,
                    "simulated": True,
                },
            )
            case_row = load_case(connection, case_id)
            view = load_view(self.ctx, connection, case_row)

        return BeganSubmission(
            view=view,
            attempt_id=attempt.id,
            attempt_number=attempt.attempt_number,
            scenario=view.vehicle.submission_scenario if view.vehicle else "ACK",
            request_hash=attempt.request_hash,
        )

    # -- phase 2: consult the adapter and record what it said ------------------

    def complete(self, began: BeganSubmission) -> SubmissionResult:
        """Ask the simulated adapter, then record the answer exactly once."""
        # Called outside any transaction. The adapter is a pure function today, but
        # holding SQLite's write lock across a call to something that is *shaped
        # like* a network boundary is a habit worth not forming.
        response = self.ctx.adapter.submit(
            scenario=began.scenario,
            case_id=began.view.case.id,
            payload_hash=began.request_hash,
            attempt_number=began.attempt_number,
        )
        return self._record(
            case_id=began.view.case.id,
            attempt_id=began.attempt_id,
            response=response,
            event_type="SUBMISSION_OUTCOME",
        )

    def submit(
        self,
        *,
        case_id: str,
        token: str | None,
        payload_hash_claim: str,
        idempotency_key: str,
    ) -> SubmissionResult:
        """begin + complete with no delay between them.

        The API route uses the two halves separately so it can await the simulated
        latency; tests and the reconciliation path use this.
        """
        began = self.begin(
            case_id=case_id,
            token=token,
            payload_hash_claim=payload_hash_claim,
            idempotency_key=idempotency_key,
        )
        if isinstance(began, SubmissionResult):
            return began
        return self.complete(began)

    # -- resolving an unknown outcome ------------------------------------------

    def reconcile(self, *, case_id: str, token: str | None) -> SubmissionResult:
        """Re-check a submission whose outcome was never learned.

        This is the only way out of SUBMISSION_UNKNOWN other than cancelling, and
        it is manual by design: there is no timer that promotes an unknown to a
        success, because no amount of elapsed time is evidence of acknowledgement.

        A *new* attempt row is written rather than the unknown one being amended.
        ``complete_attempt`` is single-shot precisely so an UNKNOWN cannot be
        rewritten as an ACK, and reconciliation must not be the exception to that.
        """
        with self.ctx.db.read() as connection:
            case_row = load_case(connection, case_id)
            authorise_actor(connection, case_id=case_id, token=token)
            if case_row.current_state is CaseState.HANDOFF_ACKNOWLEDGED:
                view = load_view(self.ctx, connection, case_row)
                attempt = view.acknowledgement
                assert attempt is not None  # is_acknowledged guarantees the row
                return SubmissionResult(view=view, attempt=attempt, replayed=True)
            if case_row.current_state is not CaseState.SUBMISSION_UNKNOWN:
                raise AppError(
                    "INVALID_STATE", detail={"state": case_row.current_state.value}
                )
            view = load_view(self.ctx, connection, case_row)
            if view.vehicle is None or case_row.payload_hash is None:
                raise AppError("INVALID_STATE", detail={"state": case_row.current_state.value})
            scenario = view.vehicle.submission_scenario
            request_hash = case_row.payload_hash
            attempt_number = repo.count_attempts(connection, case_id) + 1

        response = self.ctx.adapter.submit(
            scenario=scenario,
            case_id=case_id,
            payload_hash=request_hash,
            attempt_number=attempt_number,
        )

        with self.ctx.db.write() as connection:
            attempt_id = new_id()
            repo.insert_attempt(
                connection,
                attempt_id=attempt_id,
                case_id=case_id,
                # Deterministic and distinct from the original submit key, so a
                # reconciliation can never collide with, or replay, a submission.
                idempotency_key=f"reconcile:{case_id}:{attempt_number}",
                request_hash=request_hash,
                attempt_number=attempt_number,
            )

        return self._record(
            case_id=case_id,
            attempt_id=attempt_id,
            response=response,
            event_type="SUBMISSION_RECONCILED",
        )

    # -- internals -------------------------------------------------------------

    def _raise_for_revalidation(self, view: CaseView) -> None:
        """Translate a committed revalidation failure into the client contract."""
        if view.state is CaseState.DEALER_INVALID:
            raise AppError(
                "DEALER_NOT_ACTIVE",
                detail={
                    "status": view.dealer.status.value if view.dealer else "NOT_FOUND",
                    "stage": "SUBMIT",
                    "simulated": True,
                },
            )
        if view.state is CaseState.PREFLIGHT_BLOCKED:
            raise AppError("PREFLIGHT_BLOCKED")
        if view.state not in SUBMITTABLE_STATES:
            # Catch-all so a future policy item that re-derives the case somewhere
            # unexpected cannot fall through into a submission.
            raise AppError("INVALID_STATE", detail={"state": view.state.value})

    def _record(
        self,
        *,
        case_id: str,
        attempt_id: str,
        response: Form29CSubmissionResponse,
        event_type: str,
    ) -> SubmissionResult:
        """Write the outcome and move the case, in one transaction.

        The ACK branch does not trust ``response.status``. It writes the row, then
        re-reads ``acknowledged_attempt`` and only transitions if that read returns
        something. So HANDOFF_ACKNOWLEDGED is impossible without a committed row
        holding an acknowledgement number -- which is INV-01, enforced rather than
        promised.
        """
        with self.ctx.db.write() as connection:
            case_row = load_case(connection, case_id)
            state_before = case_row.current_state
            try:
                repo.complete_attempt(
                    connection,
                    attempt_id=attempt_id,
                    status=response.status.value,
                    acknowledgement_no=response.acknowledgement_no,
                    reason_code=(
                        response.reason_code.value
                        if response.reason_code is not None
                        else None
                    ),
                )
            except ConcurrentModification:
                raise AppError("SUBMISSION_IN_PROGRESS") from None

            if response.status is SubmissionOutcome.ACK:
                ack = repo.acknowledged_attempt(connection, case_id)
                if ack is None:  # pragma: no cover - defensive; the row was just written
                    raise AppError("INTERNAL_ERROR")
                target = CaseState.HANDOFF_ACKNOWLEDGED
            else:
                target = _OUTCOME_STATE[response.status]
                # UNKNOWN has no edge to TEMPORARY_FAILURE: once the outcome of a
                # submission is genuinely unknown, a later transient failure does
                # not make it less unknown, so the case stays put.
                if (
                    state_before is CaseState.SUBMISSION_UNKNOWN
                    and target is CaseState.SUBMISSION_TEMPORARY_FAILURE
                ):
                    target = CaseState.SUBMISSION_UNKNOWN

            if target is not state_before:
                try:
                    repo.transition_state(
                        connection,
                        case_id,
                        expected=(state_before,),
                        new_state=target,
                    )
                except ConcurrentModification:
                    raise AppError("SUBMISSION_IN_PROGRESS") from None

            repo.append_event(
                connection,
                case_id=case_id,
                event_type=event_type,
                actor=Actor.SYSTEM.value,
                state_before=state_before,
                state_after=target,
                payload_digest=case_row.payload_hash,
                detail={
                    "status": response.status.value,
                    "reason_code": (
                        response.reason_code.value
                        if response.reason_code is not None
                        else None
                    ),
                    # The acknowledgement number is recorded because it is the
                    # evidence for the terminal state. It is fictional and prefixed
                    # SIM29C, so there is nothing sensitive in the trail.
                    "acknowledgement_no": response.acknowledgement_no,
                    "simulated": True,
                    "truth_label": response.truth_label.value,
                },
            )
            case_row = load_case(connection, case_id)
            view = load_view(self.ctx, connection, case_row)
            attempt = next(
                (a for a in repo.list_attempts(connection, case_id) if a.id == attempt_id),
                None,
            )
            assert attempt is not None  # written in this transaction

        return SubmissionResult(view=view, attempt=attempt, replayed=False)


__all__ = [
    "SUBMITTABLE_STATES",
    "BeganSubmission",
    "ReasonCode",
    "SubmissionOutcome",
    "SubmissionResult",
    "SubmissionService",
]
