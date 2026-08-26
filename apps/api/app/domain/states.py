"""Case state machine for the Handover29C authorised-dealer handover journey.

Source of truth: 06_STATE_MACHINE_SERVICE_BLUEPRINT.md sections 2-4.

Two rules drive the shape of this module:

1.  The exposed enum deliberately does NOT encode every ordering permutation of
    the two actor confirmations. Blueprint section 2 requires confirmations to be
    stored as *actor facts*; only `SELLER_CONFIRMED` exists as a state. A case
    where the dealer confirmed first stays `REVIEW_READY` and surfaces the
    dealer's confirmation through a boolean on the case snapshot instead. This
    keeps the state graph small enough to reason about while letting the UI say
    something truthful to whichever party is still waiting.

2.  Transitions are validated here and nowhere else. Services call
    `assert_transition` inside the same DB transaction that writes the new state,
    so an illegal transition cannot be persisted even under concurrency.
"""

from __future__ import annotations

from enum import Enum


class JourneyType(str, Enum):
    """Which statutory route the citizen selected.

    Only `AUTHORISED_DEALER_HANDOFF` has a state machine in this prototype.
    `PRIVATE_BUYER_TRANSFER` exists so the route selector can name the thing it
    refuses to do (MV Act section 50 is a different journey) without silently
    dropping the user into the Form 29C flow. See INV-08.
    """

    AUTHORISED_DEALER_HANDOFF = "AUTHORISED_DEALER_HANDOFF"
    PRIVATE_BUYER_TRANSFER = "PRIVATE_BUYER_TRANSFER"


SUPPORTED_JOURNEY_TYPES: frozenset[JourneyType] = frozenset(
    {JourneyType.AUTHORISED_DEALER_HANDOFF}
)


class Actor(str, Enum):
    SELLER = "SELLER"
    DEALER = "DEALER"
    SYSTEM = "SYSTEM"


class CaseState(str, Enum):
    DRAFT = "DRAFT"
    VEHICLE_VERIFIED = "VEHICLE_VERIFIED"
    DEALER_VERIFIED = "DEALER_VERIFIED"
    DEALER_INVALID = "DEALER_INVALID"
    PREFLIGHT_PASSED = "PREFLIGHT_PASSED"
    PREFLIGHT_BLOCKED = "PREFLIGHT_BLOCKED"
    REVIEW_READY = "REVIEW_READY"
    SELLER_CONFIRMED = "SELLER_CONFIRMED"
    BOTH_CONFIRMED = "BOTH_CONFIRMED"
    SUBMITTING_29C = "SUBMITTING_29C"
    SUBMISSION_TEMPORARY_FAILURE = "SUBMISSION_TEMPORARY_FAILURE"
    SUBMISSION_UNKNOWN = "SUBMISSION_UNKNOWN"
    SUBMISSION_REJECTED = "SUBMISSION_REJECTED"
    HANDOFF_ACKNOWLEDGED = "HANDOFF_ACKNOWLEDGED"
    CANCELLED = "CANCELLED"


#: The single state that means "the simulated adapter returned a persisted ACK".
#: Nothing else may be rendered green. See INV-01.
ACKNOWLEDGED_STATE = CaseState.HANDOFF_ACKNOWLEDGED

TERMINAL_STATES: frozenset[CaseState] = frozenset(
    {CaseState.HANDOFF_ACKNOWLEDGED, CaseState.CANCELLED}
)

#: States in which the canonical payload may still change. Reaching any of these
#: from a confirmed state must clear confirmations (INV-03).
PRE_SUBMIT_MUTABLE_STATES: frozenset[CaseState] = frozenset(
    {
        CaseState.DRAFT,
        CaseState.VEHICLE_VERIFIED,
        CaseState.DEALER_VERIFIED,
        CaseState.DEALER_INVALID,
        CaseState.PREFLIGHT_PASSED,
        CaseState.PREFLIGHT_BLOCKED,
        CaseState.REVIEW_READY,
        CaseState.SELLER_CONFIRMED,
        CaseState.BOTH_CONFIRMED,
    }
)

#: Outcome states after a submission attempt where no acknowledgement exists.
#: Grouped so UI and tests can assert "none of these is success" in one place.
NON_ACK_SUBMISSION_OUTCOMES: frozenset[CaseState] = frozenset(
    {
        CaseState.SUBMISSION_REJECTED,
        CaseState.SUBMISSION_TEMPORARY_FAILURE,
        CaseState.SUBMISSION_UNKNOWN,
    }
)

#: States in which a party may still change the transaction.
#:
#: `SUBMISSION_UNKNOWN` is deliberately excluded even though it is not terminal.
#: While the outcome of a submission is genuinely unknown, editing and resubmitting
#: risks producing a second Form 29C record for the same handover, which is the
#: exact harm INV-05/INV-06 exist to prevent. The only ways out of UNKNOWN are
#: reconciliation and cancellation.
MUTABLE_STATES: frozenset[CaseState] = PRE_SUBMIT_MUTABLE_STATES | frozenset(
    {CaseState.SUBMISSION_REJECTED, CaseState.SUBMISSION_TEMPORARY_FAILURE}
)


# Explicit adjacency list. Anything absent is illegal by construction rather
# than by omission of a check somewhere in a service.
_ALLOWED: dict[CaseState, frozenset[CaseState]] = {
    CaseState.DRAFT: frozenset(
        {CaseState.VEHICLE_VERIFIED, CaseState.CANCELLED}
    ),
    # Re-verifying a different vehicle keeps the case in VEHICLE_VERIFIED, hence
    # the self-transition; it still recomputes the payload hash and clears
    # confirmations via the mutation path.
    CaseState.VEHICLE_VERIFIED: frozenset(
        {
            CaseState.VEHICLE_VERIFIED,
            CaseState.DEALER_VERIFIED,
            CaseState.DEALER_INVALID,
            CaseState.CANCELLED,
        }
    ),
    CaseState.DEALER_VERIFIED: frozenset(
        {
            CaseState.VEHICLE_VERIFIED,
            CaseState.DEALER_VERIFIED,
            CaseState.DEALER_INVALID,
            CaseState.PREFLIGHT_PASSED,
            CaseState.PREFLIGHT_BLOCKED,
            CaseState.REVIEW_READY,
            CaseState.CANCELLED,
        }
    ),
    CaseState.DEALER_INVALID: frozenset(
        {
            CaseState.VEHICLE_VERIFIED,
            CaseState.DEALER_VERIFIED,
            CaseState.DEALER_INVALID,
            CaseState.PREFLIGHT_PASSED,
            CaseState.PREFLIGHT_BLOCKED,
            CaseState.REVIEW_READY,
            CaseState.CANCELLED,
        }
    ),
    CaseState.PREFLIGHT_BLOCKED: frozenset(
        {
            CaseState.VEHICLE_VERIFIED,
            CaseState.DEALER_VERIFIED,
            CaseState.DEALER_INVALID,
            CaseState.PREFLIGHT_PASSED,
            CaseState.PREFLIGHT_BLOCKED,
            CaseState.REVIEW_READY,
            CaseState.CANCELLED,
        }
    ),
    CaseState.PREFLIGHT_PASSED: frozenset(
        {
            CaseState.VEHICLE_VERIFIED,
            CaseState.DEALER_VERIFIED,
            CaseState.DEALER_INVALID,
            CaseState.PREFLIGHT_PASSED,
            CaseState.PREFLIGHT_BLOCKED,
            CaseState.REVIEW_READY,
            CaseState.CANCELLED,
        }
    ),
    CaseState.REVIEW_READY: frozenset(
        {
            CaseState.VEHICLE_VERIFIED,
            CaseState.DEALER_VERIFIED,
            CaseState.DEALER_INVALID,
            CaseState.PREFLIGHT_BLOCKED,
            CaseState.PREFLIGHT_PASSED,
            CaseState.REVIEW_READY,
            CaseState.SELLER_CONFIRMED,
            CaseState.BOTH_CONFIRMED,
            CaseState.CANCELLED,
        }
    ),
    CaseState.SELLER_CONFIRMED: frozenset(
        {
            CaseState.DEALER_VERIFIED,
            CaseState.DEALER_INVALID,
            CaseState.PREFLIGHT_BLOCKED,
            CaseState.PREFLIGHT_PASSED,
            CaseState.REVIEW_READY,
            CaseState.BOTH_CONFIRMED,
            CaseState.CANCELLED,
        }
    ),
    CaseState.BOTH_CONFIRMED: frozenset(
        {
            CaseState.DEALER_VERIFIED,
            CaseState.DEALER_INVALID,
            CaseState.PREFLIGHT_BLOCKED,
            CaseState.PREFLIGHT_PASSED,
            CaseState.REVIEW_READY,
            CaseState.SELLER_CONFIRMED,
            CaseState.SUBMITTING_29C,
            CaseState.CANCELLED,
        }
    ),
    # Only the adapter result may move a case out of SUBMITTING_29C. There is
    # deliberately no path back to a mutable state and no path to CANCELLED: a
    # request is in flight and its outcome must be recorded, not discarded.
    CaseState.SUBMITTING_29C: frozenset(
        {
            CaseState.HANDOFF_ACKNOWLEDGED,
            CaseState.SUBMISSION_REJECTED,
            CaseState.SUBMISSION_TEMPORARY_FAILURE,
            CaseState.SUBMISSION_UNKNOWN,
        }
    ),
    # A definitive rejection sends the parties back to review to fix the cause.
    # It may NOT go straight to SUBMITTING_29C: the payload has to be reviewed
    # and re-confirmed by both parties first.
    CaseState.SUBMISSION_REJECTED: frozenset(
        {
            CaseState.REVIEW_READY,
            CaseState.DEALER_VERIFIED,
            CaseState.DEALER_INVALID,
            CaseState.PREFLIGHT_BLOCKED,
            CaseState.PREFLIGHT_PASSED,
            CaseState.CANCELLED,
        }
    ),
    # Transient failure: confirmations are still valid, so retry is allowed
    # without re-confirmation. The retry reuses the idempotency envelope.
    CaseState.SUBMISSION_TEMPORARY_FAILURE: frozenset(
        {
            CaseState.SUBMITTING_29C,
            CaseState.REVIEW_READY,
            CaseState.SELLER_CONFIRMED,
            CaseState.BOTH_CONFIRMED,
            CaseState.DEALER_VERIFIED,
            CaseState.DEALER_INVALID,
            CaseState.PREFLIGHT_BLOCKED,
            CaseState.PREFLIGHT_PASSED,
            CaseState.CANCELLED,
        }
    ),
    # UNKNOWN may only be resolved by status reconciliation that reads a
    # persisted attempt. There is no timer, and `assert_transition` cannot tell
    # the difference -- so SubmissionService additionally requires a persisted
    # ACK row before writing HANDOFF_ACKNOWLEDGED. See INV-01/INV-06.
    CaseState.SUBMISSION_UNKNOWN: frozenset(
        {
            CaseState.HANDOFF_ACKNOWLEDGED,
            CaseState.SUBMISSION_REJECTED,
            CaseState.SUBMISSION_UNKNOWN,
            CaseState.CANCELLED,
        }
    ),
    CaseState.HANDOFF_ACKNOWLEDGED: frozenset(),
    CaseState.CANCELLED: frozenset(),
}


class IllegalTransition(Exception):
    """Raised when a caller attempts a transition absent from the state graph."""

    def __init__(self, source: CaseState, target: CaseState) -> None:
        self.source = source
        self.target = target
        super().__init__(
            f"Illegal case transition {source.value} -> {target.value}"
        )


def allowed_transitions(source: CaseState) -> frozenset[CaseState]:
    return _ALLOWED[source]


def can_transition(source: CaseState, target: CaseState) -> bool:
    return target in _ALLOWED[source]


def assert_transition(source: CaseState, target: CaseState) -> None:
    if not can_transition(source, target):
        raise IllegalTransition(source, target)


def is_terminal(state: CaseState) -> bool:
    return state in TERMINAL_STATES


def derive_confirmation_state(
    *, seller_confirmed: bool, dealer_confirmed: bool
) -> CaseState:
    """Map the two actor facts onto the reduced exposed enum.

    Dealer-confirmed-first stays `REVIEW_READY` on purpose (blueprint section 2).
    The snapshot carries `dealer_confirmed` separately so the dealer's screen can
    still say "you confirmed, waiting for the seller" without the state graph
    growing a `DEALER_CONFIRMED` member.
    """
    if seller_confirmed and dealer_confirmed:
        return CaseState.BOTH_CONFIRMED
    if seller_confirmed:
        return CaseState.SELLER_CONFIRMED
    return CaseState.REVIEW_READY
