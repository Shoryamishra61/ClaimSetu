"""State machine invariants.

These read as requirements on purpose. Each test names the invariant or the
acceptance-gate row it defends.
"""

from __future__ import annotations

import pytest

from app.domain.states import (
    ACKNOWLEDGED_STATE,
    NON_ACK_SUBMISSION_OUTCOMES,
    SUPPORTED_JOURNEY_TYPES,
    Actor,
    CaseState,
    IllegalTransition,
    JourneyType,
    allowed_transitions,
    assert_transition,
    can_transition,
    derive_confirmation_state,
    is_terminal,
)


class TestGraphIntegrity:
    def test_every_state_has_an_entry_in_the_transition_table(self) -> None:
        # Guards against adding an enum member and forgetting the adjacency row,
        # which would make `allowed_transitions` raise KeyError at runtime.
        for state in CaseState:
            assert isinstance(allowed_transitions(state), frozenset)

    def test_only_acknowledged_and_cancelled_are_terminal(self) -> None:
        terminal = {s for s in CaseState if is_terminal(s)}
        assert terminal == {CaseState.HANDOFF_ACKNOWLEDGED, CaseState.CANCELLED}

    def test_terminal_states_have_no_outgoing_transitions(self) -> None:
        for state in CaseState:
            if is_terminal(state):
                assert allowed_transitions(state) == frozenset()

    def test_every_state_can_reach_a_terminal_state(self) -> None:
        # A state with no path to terminal would be a trap the citizen cannot
        # leave. Breadth-first over the graph from each state.
        for start in CaseState:
            seen: set[CaseState] = set()
            frontier = [start]
            while frontier:
                node = frontier.pop()
                if node in seen:
                    continue
                seen.add(node)
                frontier.extend(allowed_transitions(node))
            assert seen & {
                CaseState.HANDOFF_ACKNOWLEDGED,
                CaseState.CANCELLED,
            }, f"{start.value} cannot reach any terminal state"


class TestAcknowledgementGate:
    """INV-01 / gate G5: ACK is the only door into the green state."""

    def test_only_submitting_and_unknown_can_reach_acknowledged(self) -> None:
        sources = {
            state
            for state in CaseState
            if ACKNOWLEDGED_STATE in allowed_transitions(state)
        }
        assert sources == {
            CaseState.SUBMITTING_29C,
            CaseState.SUBMISSION_UNKNOWN,
        }

    def test_confirmed_states_cannot_jump_straight_to_acknowledged(self) -> None:
        # Confirmation is not submission; submission is not acknowledgement.
        for state in (
            CaseState.REVIEW_READY,
            CaseState.SELLER_CONFIRMED,
            CaseState.BOTH_CONFIRMED,
        ):
            assert not can_transition(state, ACKNOWLEDGED_STATE)

    def test_rejected_and_temporary_failure_cannot_reach_acknowledged(self) -> None:
        # A definitive rejection or a transient failure must go back through
        # review and a fresh submission; neither may become success in place.
        for state in (
            CaseState.SUBMISSION_REJECTED,
            CaseState.SUBMISSION_TEMPORARY_FAILURE,
        ):
            assert not can_transition(state, ACKNOWLEDGED_STATE)

    def test_no_non_ack_outcome_is_the_acknowledged_state(self) -> None:
        assert ACKNOWLEDGED_STATE not in NON_ACK_SUBMISSION_OUTCOMES


class TestSubmissionInFlight:
    def test_submitting_may_only_move_to_an_adapter_outcome(self) -> None:
        assert allowed_transitions(CaseState.SUBMITTING_29C) == frozenset(
            {
                CaseState.HANDOFF_ACKNOWLEDGED,
                CaseState.SUBMISSION_REJECTED,
                CaseState.SUBMISSION_TEMPORARY_FAILURE,
                CaseState.SUBMISSION_UNKNOWN,
            }
        )

    def test_submitting_cannot_be_cancelled(self) -> None:
        # A request is in flight; its outcome must be recorded, not discarded,
        # otherwise the citizen is left not knowing whether it landed.
        assert not can_transition(CaseState.SUBMITTING_29C, CaseState.CANCELLED)

    def test_submitting_cannot_return_to_a_mutable_state(self) -> None:
        assert not can_transition(CaseState.SUBMITTING_29C, CaseState.REVIEW_READY)


class TestUnknownRecovery:
    """INV-06 / gate G5: unknown never auto-resolves to success."""

    def test_unknown_may_stay_unknown(self) -> None:
        # Repeated status checks that learn nothing new must be representable.
        assert can_transition(
            CaseState.SUBMISSION_UNKNOWN, CaseState.SUBMISSION_UNKNOWN
        )

    def test_unknown_cannot_become_a_transient_failure(self) -> None:
        # Downgrading "we do not know" to "it failed, retry" would be a lie:
        # the submission may have landed upstream.
        assert not can_transition(
            CaseState.SUBMISSION_UNKNOWN, CaseState.SUBMISSION_TEMPORARY_FAILURE
        )

    def test_unknown_cannot_re_enter_submission_directly(self) -> None:
        # Re-submitting while the outcome is unknown risks a second
        # acknowledgement. Reconciliation must resolve it first.
        assert not can_transition(
            CaseState.SUBMISSION_UNKNOWN, CaseState.SUBMITTING_29C
        )


class TestRejectionRecovery:
    def test_rejected_returns_to_review_not_to_submission(self) -> None:
        allowed = allowed_transitions(CaseState.SUBMISSION_REJECTED)
        assert CaseState.REVIEW_READY in allowed
        assert CaseState.SUBMITTING_29C not in allowed

    def test_temporary_failure_may_retry_submission(self) -> None:
        # Confirmations are still valid, so a retry needs no re-confirmation.
        assert can_transition(
            CaseState.SUBMISSION_TEMPORARY_FAILURE, CaseState.SUBMITTING_29C
        )


class TestGuardEnforcement:
    def test_assert_transition_accepts_a_legal_move(self) -> None:
        assert_transition(CaseState.DRAFT, CaseState.VEHICLE_VERIFIED)

    def test_assert_transition_rejects_an_illegal_move(self) -> None:
        with pytest.raises(IllegalTransition) as excinfo:
            assert_transition(CaseState.DRAFT, ACKNOWLEDGED_STATE)
        assert excinfo.value.source is CaseState.DRAFT
        assert excinfo.value.target is ACKNOWLEDGED_STATE

    def test_illegal_transition_message_names_both_states(self) -> None:
        # Errors must be actionable, not generic.
        with pytest.raises(IllegalTransition, match="DRAFT -> HANDOFF_ACKNOWLEDGED"):
            assert_transition(CaseState.DRAFT, ACKNOWLEDGED_STATE)


class TestJourneyGating:
    """INV-08 / gate G2: a private-buyer route can never create a 29C case."""

    def test_only_the_dealer_handoff_journey_is_supported(self) -> None:
        assert frozenset(
            {JourneyType.AUTHORISED_DEALER_HANDOFF}
        ) == SUPPORTED_JOURNEY_TYPES

    def test_private_buyer_transfer_is_not_supported(self) -> None:
        assert JourneyType.PRIVATE_BUYER_TRANSFER not in SUPPORTED_JOURNEY_TYPES

    def test_private_buyer_route_still_has_a_name(self) -> None:
        # It must exist as a value so the route selector can explain what it
        # refuses to do, rather than silently routing the user into Form 29C.
        assert JourneyType("PRIVATE_BUYER_TRANSFER")


class TestConfirmationStateDerivation:
    """Blueprint section 2: the enum does not encode ordering permutations."""

    def test_both_confirmed(self) -> None:
        assert (
            derive_confirmation_state(seller_confirmed=True, dealer_confirmed=True)
            is CaseState.BOTH_CONFIRMED
        )

    def test_seller_only(self) -> None:
        assert (
            derive_confirmation_state(seller_confirmed=True, dealer_confirmed=False)
            is CaseState.SELLER_CONFIRMED
        )

    def test_dealer_only_stays_review_ready(self) -> None:
        # Deliberate: there is no DEALER_CONFIRMED member. The dealer's own
        # confirmation surfaces through a boolean on the case snapshot.
        assert (
            derive_confirmation_state(seller_confirmed=False, dealer_confirmed=True)
            is CaseState.REVIEW_READY
        )

    def test_neither(self) -> None:
        assert (
            derive_confirmation_state(seller_confirmed=False, dealer_confirmed=False)
            is CaseState.REVIEW_READY
        )

    def test_no_dealer_confirmed_state_exists(self) -> None:
        assert not hasattr(CaseState, "DEALER_CONFIRMED")


class TestActors:
    def test_actor_set_is_closed(self) -> None:
        assert {a.value for a in Actor} == {"SELLER", "DEALER", "SYSTEM"}
