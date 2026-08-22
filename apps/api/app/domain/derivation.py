"""Deriving the case state from the facts, rather than trusting a caller.

The API has no "set state" operation. Every mutating endpoint writes facts --
which vehicle, which dealer, which declarations, which confirmations -- and then
this function decides what state those facts add up to. That inversion is what
makes "the client cannot navigate to success" true at the domain level rather than
only at the routing level: there is no argument a client can send that selects a
state.

Two distinctions this function encodes, both of which exist so the UI can say
something true:

*   **PENDING is not FAIL.** A readiness item the seller has not filled in yet
    leaves the case in `DEALER_VERIFIED` ("finish the checklist"). An item the
    simulated fixtures say is actively wrong moves it to `PREFLIGHT_BLOCKED`
    ("this cannot proceed until it is fixed"). Collapsing both into "blocked"
    would tell a seller something is broken when they have simply not started.

*   **Waiting on the dealer is not being blocked.** Once the seller's own items
    pass, an outstanding dealer declaration leaves the case in
    `PREFLIGHT_PASSED`, which is the state where pairing happens. See the
    `BlockingStage` docstring for why the dealer's item is staged at SUBMIT.
"""

from __future__ import annotations

from .policy_types import ItemResult, PolicyEvaluation
from .states import CaseState, derive_confirmation_state

#: States only the submission service may leave, because leaving them requires
#: knowing what the simulated adapter said -- which is not derivable from the
#: facts this function can see.
_ADAPTER_OWNED_STATES: frozenset[CaseState] = frozenset(
    {CaseState.SUBMITTING_29C, CaseState.SUBMISSION_UNKNOWN}
)

#: Outcome states that persist until something actually changes. A rejected case
#: must keep saying "rejected" while the parties read the reason; it must not
#: silently reset itself to "ready to confirm" on the next read.
_STICKY_OUTCOME_STATES: frozenset[CaseState] = frozenset(
    {CaseState.SUBMISSION_REJECTED, CaseState.SUBMISSION_TEMPORARY_FAILURE}
)


def _has_blocking_failure(evaluation: PolicyEvaluation) -> bool:
    return any(
        item.blocking and item.result is ItemResult.FAIL for item in evaluation.items
    )


def derive_case_state(
    *,
    current: CaseState,
    vehicle_loaded: bool,
    dealer_loaded: bool,
    dealer_can_continue: bool,
    preflight: PolicyEvaluation,
    submit: PolicyEvaluation,
    seller_confirmed: bool,
    dealer_confirmed: bool,
    payload_changed: bool,
) -> CaseState:
    """The state these facts imply.

    ``payload_changed`` is True only when the canonical payload hash actually
    moved. It is what lets a rejected or temporarily-failed case stay put on an
    ordinary refresh while still re-deriving once a party edits something.
    """
    # Terminal means terminal. HANDOFF_ACKNOWLEDGED in particular can never be
    # re-derived away, and nothing can be re-derived into it -- only
    # SubmissionService writes it, and only against a persisted ACK row.
    if current in (CaseState.HANDOFF_ACKNOWLEDGED, CaseState.CANCELLED):
        return current
    if current in _ADAPTER_OWNED_STATES:
        return current
    if current in _STICKY_OUTCOME_STATES and not payload_changed:
        return current

    if not vehicle_loaded:
        return CaseState.DRAFT
    if not dealer_loaded:
        return CaseState.VEHICLE_VERIFIED
    if not dealer_can_continue:
        return CaseState.DEALER_INVALID

    # A fixture-backed check that is actively negative is a real blocker at either
    # stage, and is reported as such even if it is the dealer's row.
    if _has_blocking_failure(preflight) or _has_blocking_failure(submit):
        return CaseState.PREFLIGHT_BLOCKED
    if not preflight.passed:
        return CaseState.DEALER_VERIFIED
    if not submit.passed:
        return CaseState.PREFLIGHT_PASSED

    return derive_confirmation_state(
        seller_confirmed=seller_confirmed, dealer_confirmed=dealer_confirmed
    )
