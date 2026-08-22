"""The product invariants, one test each.

These are the tests the acceptance gates point at. They are marked
``@pytest.mark.invariant`` so `pytest -m invariant` is a single command that
answers "does the thing still refuse to lie?".

Two rules shaped how they are written.

**They call services, not HTTP.** An invariant that only holds when you come in
through FastAPI is not an invariant -- it is a middleware. The API contract gets
its own suite; this one proves the rules hold for any caller.

**They assert the error code, not just that something raised.** Several guards in
this codebase are ordered, and the order is a deliberate decision. A test that
accepted any ``AppError`` would pass while the product told the user the wrong
thing, which for a prototype about honest status reporting would be a peculiar
failure to tolerate.
"""

from __future__ import annotations

import pytest

from app.adapters.mock_form29c_adapter import SubmissionOutcome
from app.clock import iso_plus_seconds
from app.db import repository as repo
from app.domain.policies import registry
from app.domain.states import (
    NON_ACK_SUBMISSION_OUTCOMES,
    Actor,
    CaseState,
    can_transition,
)
from app.errors import AppError
from app.services.case_service import CaseService, hash_token
from app.services.context import ServiceContext
from tests.conftest import DEFAULT_DEALER, Journey

pytestmark = pytest.mark.invariant


#: Fixtures chosen by what the adapter does with them, named here so a test reads
#: as intent rather than as a registration number.
VEHICLE_ACK = ("DEMO01AB1234", "12345")
VEHICLE_REJECTED = ("DEMO02CD5678", "56789")
VEHICLE_UNKNOWN = ("DEMO03EF9012", "90123")
VEHICLE_TEMPORARY = ("DEMO04GH3456", "34567")
VEHICLE_UNKNOWN_THEN_ACK = ("DEMO06KL2345", "23456")

DEALER_EXPIRED = "DEMO-29B-002"
DEALER_SUSPENDED = "DEMO-29B-003"
DEALER_REVALIDATION_FAILS = "DEMO-29B-005"


def expire_pair_codes(ctx: ServiceContext, case_id: str) -> None:
    """Push every pair code for a case into the past.

    Done with SQL rather than a clock override because ``expires_at`` is stored, not
    computed: moving the stored value is exactly what an expired code looks like to
    the service, and it does not require the production code to grow a seam that
    exists only for tests.
    """
    with ctx.db.write() as connection:
        connection.execute(
            "UPDATE pair_sessions SET expires_at = ? WHERE case_id = ?",
            (iso_plus_seconds(-60), case_id),
        )


# ---------------------------------------------------------------------------
# INV-08: the unsupported route is refused, not redirected
# ---------------------------------------------------------------------------


def test_private_buyer_route_cannot_start_a_case(journey: Journey) -> None:
    with pytest.raises(AppError) as raised:
        journey.create(journey_type="PRIVATE_BUYER_TRANSFER")
    assert raised.value.code == "UNSUPPORTED_JOURNEY"
    assert raised.value.detail == {"journey_type": "PRIVATE_BUYER_TRANSFER"}
    # 409 and not recoverable: the answer is a different statutory process (MV Act
    # section 50), not a retry of this one.
    assert raised.value.http_status == 409
    assert raised.value.spec.recoverable is False


def test_private_buyer_route_creates_no_row(journey: Journey) -> None:
    """The refusal happens before the INSERT.

    Stronger than checking the exception: if a row were created and then rejected
    downstream, a case in an unsupported journey would exist and something later
    could pick it up.
    """
    with pytest.raises(AppError):
        journey.create(journey_type="PRIVATE_BUYER_TRANSFER")
    with journey.ctx.db.read() as connection:
        count = connection.execute("SELECT COUNT(*) AS n FROM cases").fetchone()["n"]
    assert count == 0


def test_unknown_journey_type_is_also_refused(journey: Journey) -> None:
    """A string that is not a JourneyType at all must not fall through to the
    supported branch."""
    with pytest.raises(AppError) as raised:
        journey.create(journey_type="SOMETHING_ELSE")
    assert raised.value.code == "VALIDATION_ERROR"
    assert raised.value.detail == {"field": "journey_type"}


# ---------------------------------------------------------------------------
# INV-04: dealer authorisation must be active, at preflight and again at submit
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("authorisation_no", "expected_status"),
    [(DEALER_EXPIRED, "EXPIRED"), (DEALER_SUSPENDED, "SUSPENDED")],
)
def test_inactive_dealer_lands_in_dealer_invalid(
    journey: Journey, authorisation_no: str, expected_status: str
) -> None:
    journey.create()
    journey.verify_vehicle()
    view = journey.verify_dealer(authorisation_no)
    assert view.state is CaseState.DEALER_INVALID
    assert view.dealer is not None
    assert view.dealer.status.value == expected_status


def test_inactive_dealer_blocks_pairing(journey: Journey) -> None:
    """The block is not cosmetic: the next step in the journey refuses to run.

    DEALER_INVALID is deliberately absent from PAIRING_ALLOWED_STATES, so a seller
    cannot invite a dealer whose authorisation the simulated registry has already
    said is not active.
    """
    journey.create()
    journey.verify_vehicle()
    journey.verify_dealer(DEALER_EXPIRED)
    with pytest.raises(AppError) as raised:
        journey.pair()
    assert raised.value.code == "INVALID_STATE"
    assert raised.value.detail == {"state": "DEALER_INVALID"}


def test_inactive_dealer_cannot_be_worked_around_by_declarations(
    journey: Journey,
) -> None:
    """Ticking every box does not promote a case past an inactive dealer."""
    journey.create()
    journey.verify_vehicle()
    journey.verify_dealer(DEALER_SUSPENDED)
    view = journey.seller_declarations()
    assert view.state is CaseState.DEALER_INVALID


def test_dealer_revalidation_at_submit_blocks_and_sticks(journey: Journey) -> None:
    """A dealer active at preflight but not at submit stops the submission.

    Two assertions, and the second is the one that matters. Refusing the submit is
    obvious. Committing DEALER_INVALID *despite* raising is the subtle part: if the
    revalidation transaction rolled back to keep the error clean, the UI would go on
    showing a verified dealer while every submit mysteriously failed.
    """
    journey.to_both_confirmed(dealer=DEALER_REVALIDATION_FAILS)
    with pytest.raises(AppError) as raised:
        journey.submit()
    assert raised.value.code == "DEALER_NOT_ACTIVE"
    assert raised.value.detail is not None
    assert raised.value.detail["stage"] == "SUBMIT"
    assert raised.value.detail["simulated"] is True

    assert journey.view().state is CaseState.DEALER_INVALID


def test_dealer_revalidation_failure_leaves_no_attempt_row(journey: Journey) -> None:
    """Nothing reached the adapter, so nothing may look like an attempt."""
    journey.to_both_confirmed(dealer=DEALER_REVALIDATION_FAILS)
    with pytest.raises(AppError):
        journey.submit()
    with journey.ctx.db.read() as connection:
        assert repo.count_attempts(connection, journey.case_id) == 0


# ---------------------------------------------------------------------------
# Pairing: one code, one use, one lifetime
# ---------------------------------------------------------------------------


def test_pair_code_is_single_use(journey: Journey) -> None:
    journey.to_preflight_passed()
    code = journey.pair()
    journey.join(code)
    with pytest.raises(AppError) as raised:
        journey.join(code, client_key="second-device")
    assert raised.value.code == "PAIR_CODE_ALREADY_USED"


def test_pair_code_expires(journey: Journey) -> None:
    journey.to_preflight_passed()
    code = journey.pair()
    expire_pair_codes(journey.ctx, journey.case_id)
    with pytest.raises(AppError) as raised:
        journey.join(code)
    assert raised.value.code == "PAIR_CODE_EXPIRED"


def test_issuing_a_new_code_burns_the_old_one(journey: Journey) -> None:
    """A code on an earlier screenshot must not still work.

    The distinct ``SUPERSEDED`` reason exists so the dealer's screen can say "the
    seller generated a new code" instead of the misleading "already used".
    """
    journey.to_preflight_passed()
    first = journey.pair()
    second = journey.pair()
    assert first != second

    with pytest.raises(AppError) as raised:
        journey.join(first)
    assert raised.value.code == "PAIR_CODE_EXPIRED"
    assert raised.value.detail == {"reason": "SUPERSEDED"}

    # And the replacement still works, so superseding is not a foot-gun.
    assert journey.join(second).dealer_joined is True


def test_unknown_pair_code_is_never_described_as_expired(journey: Journey) -> None:
    journey.to_preflight_passed()
    journey.pair()
    with pytest.raises(AppError) as raised:
        journey.join("not-a-real-code")
    assert raised.value.code == "PAIR_CODE_INVALID"


def test_pair_code_is_never_written_to_the_audit_trail(journey: Journey) -> None:
    """The trail records that a code was issued, never the code or its hash."""
    journey.to_preflight_passed()
    code = journey.pair()
    with journey.ctx.db.read() as connection:
        events = repo.list_events(connection, journey.case_id)
    issued = [e for e in events if e.event_type == "PAIR_CODE_ISSUED"]
    assert issued, "expected a PAIR_CODE_ISSUED event"
    serialised = repr([e.detail for e in issued])
    assert code not in serialised
    assert hash_token(code) not in serialised


# ---------------------------------------------------------------------------
# INV-02 / INV-03: confirmations are about one exact payload
# ---------------------------------------------------------------------------


def test_one_party_confirmation_cannot_submit(journey: Journey) -> None:
    """Seller alone is not enough.

    The code asserted is ``INVALID_STATE`` rather than ``CONFIRMATIONS_INCOMPLETE``
    on purpose: SELLER_CONFIRMED is not in SUBMITTABLE_STATES, and that guard runs
    before the confirmation recount. CONFIRMATIONS_INCOMPLETE is reserved for the
    narrow race where a withdrawal lands mid-submit.
    """
    journey.to_review_ready()
    view = journey.confirm(Actor.SELLER)
    assert view.state is CaseState.SELLER_CONFIRMED
    with pytest.raises(AppError) as raised:
        journey.submit()
    assert raised.value.code == "INVALID_STATE"
    assert raised.value.detail == {"state": "SELLER_CONFIRMED"}


def test_stale_payload_hash_is_refused_at_confirmation(journey: Journey) -> None:
    journey.to_review_ready()
    stale = journey.payload_hash()
    assert stale
    # Change the vehicle rather than a declaration, so the case stays REVIEW_READY
    # and the test is about the hash rather than about preflight failing.
    journey.verify_vehicle(*VEHICLE_TEMPORARY)
    assert journey.payload_hash() != stale

    with pytest.raises(AppError) as raised:
        journey.confirm(Actor.SELLER, payload_hash=stale)
    assert raised.value.code == "STALE_PAYLOAD"
    assert raised.value.detail == {"reason": "PAYLOAD_CHANGED"}


def test_stale_payload_hash_is_refused_at_submit(journey: Journey) -> None:
    journey.to_both_confirmed()
    stale = journey.payload_hash()
    journey.verify_vehicle(*VEHICLE_TEMPORARY)
    with pytest.raises(AppError) as raised:
        journey.submit(payload_hash=stale)
    assert raised.value.code in {"STALE_PAYLOAD", "INVALID_STATE"}


def test_mutation_clears_both_confirmations(journey: Journey) -> None:
    """INV-03. The confirmations do not merely stop counting -- they are erased."""
    journey.to_both_confirmed()
    before = journey.view()
    assert before.state is CaseState.BOTH_CONFIRMED
    assert before.case.seller_confirmed and before.case.dealer_confirmed

    after = journey.verify_vehicle(*VEHICLE_TEMPORARY)
    assert after.case.seller_confirmed is False
    assert after.case.dealer_confirmed is False
    assert after.case.seller_confirmed_hash is None
    assert after.case.dealer_confirmed_hash is None
    assert after.state is CaseState.REVIEW_READY

    # The trail explains *why* they disappeared, so a party asking "where did my
    # confirmation go?" has an answer that is not "no idea".
    with journey.ctx.db.read() as connection:
        events = repo.list_events(connection, journey.case_id)
    assert any(e.detail.get("confirmations_cleared") is True for e in events)


def test_confirmation_of_a_changed_payload_requires_the_new_hash(
    journey: Journey,
) -> None:
    """After a mutation both parties must confirm again, against the new payload."""
    journey.to_both_confirmed()
    journey.verify_vehicle(*VEHICLE_TEMPORARY)
    journey.confirm(Actor.SELLER)
    view = journey.confirm(Actor.DEALER)
    assert view.state is CaseState.BOTH_CONFIRMED
    assert view.case.payload_hash == journey.payload_hash()


def test_withdrawn_confirmation_drops_the_case_out_of_submittable(
    journey: Journey,
) -> None:
    journey.to_both_confirmed()
    view = journey.withdraw(Actor.DEALER)
    assert view.state is CaseState.SELLER_CONFIRMED
    with pytest.raises(AppError) as raised:
        journey.submit()
    assert raised.value.code == "INVALID_STATE"


def test_seller_cannot_make_the_dealers_declaration(journey: Journey) -> None:
    """A party may only assert things about itself.

    Without this the app could record that the dealer confirmed possession when the
    dealer never did -- the app asserting something on a party's behalf, which is
    the one thing an acknowledgement-gated product must not do.
    """
    journey.to_preflight_passed()
    with pytest.raises(AppError) as raised:
        journey.cases.set_declarations(
            case_id=journey.case_id,
            token=journey.seller_token,
            values={"DEALER_POSSESSION_CONFIRM": True},
        )
    assert raised.value.code == "UNAUTHORISED_ACTOR"
    assert raised.value.detail == {"codes": ["DEALER_POSSESSION_CONFIRM"]}


# ---------------------------------------------------------------------------
# INV-05: one idempotency key, one submission
# ---------------------------------------------------------------------------


def test_duplicate_submit_replays_instead_of_resubmitting(journey: Journey) -> None:
    journey.to_both_confirmed()
    first = journey.submit(idempotency_key="dup-key")
    second = journey.submit(idempotency_key="dup-key")

    assert first.replayed is False
    assert second.replayed is True
    assert second.attempt.id == first.attempt.id
    assert second.acknowledgement_no == first.acknowledgement_no
    with journey.ctx.db.read() as connection:
        assert repo.count_attempts(connection, journey.case_id) == 1


def test_same_key_with_a_different_payload_is_refused(journey: Journey) -> None:
    """Reusing a key for different details is a client bug, and is named as one."""
    journey.to_both_confirmed()
    journey.submit(idempotency_key="reuse-key")
    with pytest.raises(AppError) as raised:
        journey.submissions.submit(
            case_id=journey.case_id,
            token=journey.seller_token,
            payload_hash_claim="0" * 64,
            idempotency_key="reuse-key",
        )
    assert raised.value.code == "IDEMPOTENCY_KEY_REUSED"
    assert raised.value.detail == {"reason": "DIFFERENT_PAYLOAD"}


def test_missing_idempotency_key_is_refused(journey: Journey) -> None:
    journey.to_both_confirmed()
    with pytest.raises(AppError) as raised:
        journey.submit(idempotency_key="")
    assert raised.value.code == "IDEMPOTENCY_KEY_REQUIRED"


def test_submitting_an_acknowledged_case_with_a_new_key_is_refused(
    journey: Journey,
) -> None:
    journey.to_both_confirmed()
    journey.submit(idempotency_key="first")
    with pytest.raises(AppError) as raised:
        journey.submit(idempotency_key="second")
    assert raised.value.code == "ALREADY_ACKNOWLEDGED"
    with journey.ctx.db.read() as connection:
        assert repo.count_attempts(connection, journey.case_id) == 1


# ---------------------------------------------------------------------------
# INV-01: green requires a persisted acknowledgement
# ---------------------------------------------------------------------------


def test_acknowledgement_is_the_only_green_terminal_state(journey: Journey) -> None:
    journey.to_both_confirmed()
    result = journey.submit()
    view = result.view

    assert view.state is CaseState.HANDOFF_ACKNOWLEDGED
    assert view.is_acknowledged is True
    assert view.acknowledgement is not None
    assert view.acknowledgement.acknowledgement_no
    assert view.acknowledgement.acknowledgement_no.startswith("SIM29C-")
    assert result.acknowledgement_no == view.acknowledgement.acknowledgement_no


def test_state_flag_alone_is_not_treated_as_success(journey: Journey) -> None:
    """The strongest form of INV-01.

    Writes HANDOFF_ACKNOWLEDGED straight into the row -- the thing a forged client,
    a bad migration or a careless future patch would do -- and asserts the view
    still reports "not acknowledged", because no attempt row carries a number.
    Success is a consequence of evidence, not of a string in a column.
    """
    journey.to_both_confirmed()
    with journey.ctx.db.write() as connection:
        connection.execute(
            "UPDATE cases SET current_state = ? WHERE id = ?",
            (CaseState.HANDOFF_ACKNOWLEDGED.value, journey.case_id),
        )
    view = journey.view()
    assert view.state is CaseState.HANDOFF_ACKNOWLEDGED
    assert view.acknowledgement is None
    assert view.is_acknowledged is False


def test_rejection_is_never_green(journey: Journey) -> None:
    journey.to_both_confirmed(vehicle=VEHICLE_REJECTED)
    result = journey.submit()

    assert result.view.state is CaseState.SUBMISSION_REJECTED
    assert result.view.state in NON_ACK_SUBMISSION_OUTCOMES
    assert result.view.is_acknowledged is False
    assert result.view.acknowledgement is None
    assert result.acknowledgement_no is None
    assert result.attempt.acknowledgement_no is None
    assert result.attempt.reason_code == "VALIDATION_ERROR"


def test_rejected_case_cannot_resubmit_without_re_confirmation(
    journey: Journey,
) -> None:
    """SUBMISSION_REJECTED has no edge to SUBMITTING_29C.

    A rejection means the details were wrong, so both parties go back through
    review rather than retrying the same payload with a new key.
    """
    journey.to_both_confirmed(vehicle=VEHICLE_REJECTED)
    journey.submit(idempotency_key="rejected-1")
    assert can_transition(
        CaseState.SUBMISSION_REJECTED, CaseState.SUBMITTING_29C
    ) is False
    with pytest.raises(AppError) as raised:
        journey.submit(idempotency_key="rejected-2")
    assert raised.value.code == "INVALID_STATE"


def test_unknown_is_never_promoted_to_success(journey: Journey) -> None:
    journey.to_both_confirmed(vehicle=VEHICLE_UNKNOWN)
    result = journey.submit()

    assert result.view.state is CaseState.SUBMISSION_UNKNOWN
    assert result.view.is_acknowledged is False
    assert result.attempt.status == SubmissionOutcome.UNKNOWN.value
    assert result.attempt.acknowledgement_no is None

    # Reading the case again must not change it. There is no timer that ages an
    # unknown into a success, and a GET is side-effect free.
    assert journey.view().state is CaseState.SUBMISSION_UNKNOWN
    assert journey.view().is_acknowledged is False


def test_unknown_stays_unknown_when_reconciliation_learns_nothing(
    journey: Journey,
) -> None:
    """The UNKNOWN fixture answers UNKNOWN forever, and the case does not drift."""
    journey.to_both_confirmed(vehicle=VEHICLE_UNKNOWN)
    journey.submit()
    result = journey.reconcile()
    assert result.view.state is CaseState.SUBMISSION_UNKNOWN
    assert result.view.is_acknowledged is False


def test_reconciliation_can_resolve_an_unknown_into_an_acknowledgement(
    journey: Journey,
) -> None:
    """The recovery path, proven end to end.

    A new attempt row is written rather than the unknown one amended, because
    ``complete_attempt`` is single-shot so that an UNKNOWN can never be rewritten
    as an ACK.
    """
    journey.to_both_confirmed(vehicle=VEHICLE_UNKNOWN_THEN_ACK)
    first = journey.submit()
    assert first.view.state is CaseState.SUBMISSION_UNKNOWN

    resolved = journey.reconcile()
    assert resolved.view.state is CaseState.HANDOFF_ACKNOWLEDGED
    assert resolved.view.is_acknowledged is True
    assert resolved.acknowledgement_no

    with journey.ctx.db.read() as connection:
        attempts = repo.list_attempts(connection, journey.case_id)
    assert len(attempts) == 2
    assert attempts[0].status == SubmissionOutcome.UNKNOWN.value
    assert attempts[0].acknowledgement_no is None
    assert "SUBMISSION_RECONCILED" in journey.audit_types()


def test_reconciliation_is_refused_outside_unknown(journey: Journey) -> None:
    journey.to_both_confirmed(vehicle=VEHICLE_REJECTED)
    journey.submit()
    with pytest.raises(AppError) as raised:
        journey.reconcile()
    assert raised.value.code == "INVALID_STATE"


def test_temporary_failure_allows_retry_without_re_confirmation(
    journey: Journey,
) -> None:
    """A transient failure keeps confirmations valid, but needs a fresh key.

    The fresh key is not a detail the frontend may skip: reusing the key replays the
    stored failure rather than retrying, so the retry button must mint a new one.
    """
    journey.to_both_confirmed(vehicle=VEHICLE_TEMPORARY)
    first = journey.submit(idempotency_key="attempt-1")
    assert first.view.state is CaseState.SUBMISSION_TEMPORARY_FAILURE
    assert first.view.is_acknowledged is False
    assert first.view.case.seller_confirmed and first.view.case.dealer_confirmed

    replay = journey.submit(idempotency_key="attempt-1")
    assert replay.replayed is True
    assert replay.view.state is CaseState.SUBMISSION_TEMPORARY_FAILURE

    # The TEMPORARY_FAILURE fixture keeps failing, which is the point: the retry is
    # allowed to start, and still does not go green.
    retried = journey.submit(idempotency_key="attempt-2")
    assert retried.view.is_acknowledged is False
    with journey.ctx.db.read() as connection:
        assert repo.count_attempts(connection, journey.case_id) == 2


# ---------------------------------------------------------------------------
# Refresh, resume and the absence of a client-selectable state
# ---------------------------------------------------------------------------


def test_state_survives_a_process_restart(journey: Journey, settings) -> None:
    """Refresh-safety, proven the hard way.

    A brand-new ServiceContext over the same file is what a restarted process sees.
    Nothing about the case may be held in memory: the acknowledgement has to be
    readable from disk, or "refresh does not lose your handover" is a promise about
    the current process rather than about the product.
    """
    journey.to_both_confirmed()
    result = journey.submit()
    ack_no = result.acknowledgement_no
    assert ack_no

    reopened = CaseService(ServiceContext.build(settings))
    view = reopened.snapshot(case_id=journey.case_id)
    assert view.state is CaseState.HANDOFF_ACKNOWLEDGED
    assert view.is_acknowledged is True
    assert view.acknowledgement is not None
    assert view.acknowledgement.acknowledgement_no == ack_no


def test_mid_journey_state_survives_a_process_restart(
    journey: Journey, settings
) -> None:
    journey.to_review_ready()
    journey.confirm(Actor.SELLER)
    hash_before = journey.payload_hash()

    reopened = CaseService(ServiceContext.build(settings))
    view = reopened.snapshot(case_id=journey.case_id)
    assert view.state is CaseState.SELLER_CONFIRMED
    assert view.case.seller_confirmed is True
    assert view.case.dealer_confirmed is False
    assert view.case.payload_hash == hash_before
    assert view.dealer_joined is True


def test_no_service_accepts_a_target_state(journey: Journey) -> None:
    """There is no "set state" surface for a client to aim at.

    State is derived from stored facts, so the reason a client cannot navigate to
    success is not that a check refuses it -- it is that no parameter exists.
    Asserted by introspection so that adding one later fails this test.
    """
    import inspect

    services = (journey.cases, journey.confirmations, journey.submissions, journey.pairing)
    offenders: list[str] = []
    for service in services:
        for name, member in inspect.getmembers(service, inspect.ismethod):
            if name.startswith("_"):
                continue
            params = set(inspect.signature(member).parameters)
            for banned in ("state", "new_state", "current_state", "target_state"):
                if banned in params:
                    offenders.append(f"{type(service).__name__}.{name}({banned})")
    assert offenders == []


def test_success_is_not_reachable_from_a_confirmed_state(journey: Journey) -> None:
    """Only the adapter's outcome may write the green state."""
    for source in (
        CaseState.REVIEW_READY,
        CaseState.SELLER_CONFIRMED,
        CaseState.BOTH_CONFIRMED,
        CaseState.SUBMISSION_REJECTED,
        CaseState.SUBMISSION_TEMPORARY_FAILURE,
    ):
        assert can_transition(source, CaseState.HANDOFF_ACKNOWLEDGED) is False
    assert can_transition(CaseState.SUBMITTING_29C, CaseState.HANDOFF_ACKNOWLEDGED)
    assert can_transition(CaseState.SUBMISSION_UNKNOWN, CaseState.HANDOFF_ACKNOWLEDGED)


def test_a_stranger_cannot_act_on_a_case(journey: Journey) -> None:
    """Possession of a case id is not authority to change it."""
    journey.to_review_ready()
    with pytest.raises(AppError) as raised:
        journey.confirmations.confirm(
            case_id=journey.case_id,
            token="not-a-real-token",
            payload_hash_claim=journey.payload_hash(),
        )
    assert raised.value.code == "UNAUTHORISED_ACTOR"


def test_a_missing_token_cannot_act_on_a_case(journey: Journey) -> None:
    journey.to_review_ready()
    with pytest.raises(AppError) as raised:
        journey.confirmations.confirm(
            case_id=journey.case_id, token=None, payload_hash_claim=journey.payload_hash()
        )
    assert raised.value.code == "UNAUTHORISED_ACTOR"


# ---------------------------------------------------------------------------
# INV-07: everything government-shaped says it is simulated
# ---------------------------------------------------------------------------


def test_every_adapter_scenario_is_labelled_simulated(adapter) -> None:
    scenarios = adapter.known_scenarios()
    assert scenarios, "the adapter must expose its scenarios for this test to mean anything"
    for scenario in sorted(scenarios):
        for attempt in (1, 2, 3):
            response = adapter.submit(
                scenario=scenario,
                case_id="case-under-test",
                payload_hash="a" * 64,
                attempt_number=attempt,
            )
            assert response.simulation is True, scenario
            assert response.truth_label.value.startswith("SIMULATED"), scenario
            assert response.envelope()["simulation"] is True, scenario
            # No response may carry both an acknowledgement and a failure reason.
            if response.status is SubmissionOutcome.ACK:
                assert response.acknowledgement_no
                assert response.reason_code is None
            else:
                assert response.acknowledgement_no is None


def test_simulation_flag_cannot_be_switched_off(adapter) -> None:
    """``simulation`` is a property, not a field with a default.

    A field could be constructed as False by a future caller; a property cannot.
    """
    response = adapter.submit(
        scenario="ACK", case_id="c", payload_hash="b" * 64, attempt_number=1
    )
    with pytest.raises((AttributeError, TypeError)):
        response.simulation = False  # type: ignore[misc]


def test_registry_lookups_are_labelled_simulated(vehicles, dealers) -> None:
    vehicle = vehicles.lookup(registration_no=VEHICLE_ACK[0], chassis_suffix=VEHICLE_ACK[1])
    assert vehicle is not None
    assert vehicle.simulation is True
    assert vehicle.truth_label.value.startswith(("SIMULATED", "FICTIONAL"))

    record = dealers.lookup(authorisation_no=DEFAULT_DEALER)
    assert record.simulation is True
    assert record.truth_label.value.startswith("SIMULATED")

    # A miss is still a registry answer, so it still carries the label. Otherwise
    # "not found" would be the one response that escaped the disclosure.
    miss = dealers.lookup(authorisation_no="DEMO-29B-NOPE")
    assert miss.simulation is True
    assert miss.can_continue is False


# ---------------------------------------------------------------------------
# Policy: the current rules execute, the draft cannot
# ---------------------------------------------------------------------------


def test_running_policy_is_in_force(ctx: ServiceContext) -> None:
    """The policy the services actually hold, not the one the registry advertises."""
    assert ctx.policy.in_force is True
    assert ctx.policy.version == registry.CURRENT_POLICY_VERSION
    assert "DRAFT" not in ctx.policy.version.upper()


def test_a_case_records_the_in_force_policy_version(journey: Journey) -> None:
    """The version is stamped on the row, so a case cannot be silently re-judged
    under different rules later."""
    view = journey.create()
    assert view.case.policy_version == registry.CURRENT_POLICY_VERSION


def test_settings_refuse_a_draft_policy_version(settings) -> None:
    """The config seam, which ``test_policy_draft_inert`` does not cover.

    ``registry.get`` refusing the draft only helps if nothing can construct a
    Settings object pointing at it. ``Settings.__post_init__`` validates through the
    registry, so a bad H29C_POLICY_VERSION fails at startup rather than producing a
    process that quietly evaluates a proposal as law.
    """
    from dataclasses import replace

    # Imported inside the test on purpose: the draft module must not appear in any
    # import graph that production code walks.
    from app.domain.policies.draft.gsr_649e_2026_draft import POLICY_VERSION as DRAFT

    with pytest.raises(registry.PolicyNotSelectable):
        replace(settings, policy_version=DRAFT)

    with pytest.raises(registry.PolicyNotSelectable):
        replace(settings, policy_version="NO_SUCH_POLICY")


def test_no_service_context_can_be_built_on_a_draft_policy(settings) -> None:
    """Belt and braces: even bypassing Settings validation, the context refuses."""
    import dataclasses

    from app.domain.policies.draft.gsr_649e_2026_draft import POLICY_VERSION as DRAFT

    # object.__setattr__ past the frozen dataclass, i.e. the worst case a future
    # patch could create.
    forged = dataclasses.replace(settings)
    object.__setattr__(forged, "policy_version", DRAFT)
    with pytest.raises(registry.PolicyNotSelectable):
        ServiceContext.build(forged)
