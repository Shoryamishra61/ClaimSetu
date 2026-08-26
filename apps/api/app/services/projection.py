"""Assembling and re-deriving the authoritative view of a case.

Every mutating service ends by calling :func:`refresh`, which:

1.  rebuilds the canonical payload from the stored facts;
2.  if the payload hash moved, clears both confirmations (INV-03);
3.  re-derives the state from the facts (``domain.derivation``);
4.  writes the transition through the compare-and-set in ``repository``;
5.  appends one audit event describing what changed.

All five happen inside the caller's transaction, so a case can never be left with
a hash that does not match its confirmations, or a state that does not match its
facts.

:func:`load_view` is the read-only counterpart. Reads deliberately do not
re-derive: GET must be side-effect free so that a browser back-button or a refresh
cannot change anything (SRS section 14).
"""

from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass

from ..adapters.mock_dealer_registry import DealerRecord, DealerStatus, LookupPurpose
from ..adapters.mock_vehicle_registry import VehicleRecord
from ..db import repository as repo
from ..domain.canonical import (
    CanonicalDealer,
    CanonicalDeclaration,
    CanonicalPayload,
    CanonicalVehicle,
    payload_hash,
)
from ..domain.derivation import derive_case_state
from ..domain.policy_types import PolicyContext, PolicyEvaluation, PolicyStage
from ..domain.states import Actor, CaseState
from .context import ServiceContext


@dataclass(frozen=True, slots=True)
class CaseView:
    """Everything the API needs to describe a case, gathered once."""

    case: repo.CaseRow
    vehicle: VehicleRecord | None
    dealer: DealerRecord | None
    dealer_joined: bool
    declarations: dict[str, bool]
    preflight: PolicyEvaluation
    submit: PolicyEvaluation
    payload: CanonicalPayload | None
    latest_attempt: repo.SubmissionAttemptRow | None
    acknowledgement: repo.SubmissionAttemptRow | None

    @property
    def state(self) -> CaseState:
        return self.case.current_state

    @property
    def is_acknowledged(self) -> bool:
        """INV-01, expressed in one place.

        Both halves are required: the state says acknowledged *and* a persisted
        attempt row carries an acknowledgement number. A state flag on its own is
        never treated as success, so a stray write to ``current_state`` cannot make
        the UI go green.
        """
        return (
            self.case.current_state is CaseState.HANDOFF_ACKNOWLEDGED
            and self.acknowledgement is not None
            and bool(self.acknowledgement.acknowledgement_no)
        )


def dealer_has_joined(connection: sqlite3.Connection, case_id: str) -> bool:
    """True once some dealer device has redeemed a pairing code for this case."""
    return repo.has_party_session(
        connection, case_id=case_id, actor=Actor.DEALER.value
    )


def resolve_vehicle(
    ctx: ServiceContext, case_row: repo.CaseRow
) -> VehicleRecord | None:
    if case_row.vehicle_id is None:
        return None
    return ctx.vehicles.by_id(case_row.vehicle_id)


def resolve_dealer(
    ctx: ServiceContext,
    case_row: repo.CaseRow,
    *,
    purpose: LookupPurpose = LookupPurpose.VERIFICATION,
) -> DealerRecord | None:
    """Look the dealer up again from the simulated registry.

    Deliberately a fresh lookup rather than a read of ``cases.dealer_id``'s cached
    status: the stored ``dealer_status_at_verify`` is a historical record, and
    treating it as current is exactly the mistake INV-04 exists to prevent.
    """
    if case_row.dealer_id is None:
        return None
    record = ctx.dealers.lookup(
        authorisation_no=case_row.dealer_id, purpose=purpose
    )
    return record if isinstance(record, DealerRecord) else None


def build_policy_context(
    *,
    vehicle: VehicleRecord | None,
    dealer: DealerRecord | None,
    declarations: Mapping[str, bool],
    dealer_joined: bool,
) -> PolicyContext:
    return PolicyContext(
        vehicle_loaded=vehicle is not None,
        dealer_status=dealer.status.value if dealer is not None else None,
        vehicle_document_flags=dict(vehicle.document_flags) if vehicle else {},
        declarations=dict(declarations),
        dealer_joined=dealer_joined,
    )


def build_canonical_payload(
    ctx: ServiceContext,
    case_row: repo.CaseRow,
    *,
    vehicle: VehicleRecord | None,
    dealer: DealerRecord | None,
    declarations: Mapping[str, bool],
) -> CanonicalPayload | None:
    """The exact set of facts the two parties will confirm.

    Returns None until both a vehicle and a dealer are chosen, because there is
    nothing meaningful to agree to before then.

    Every settable declaration code appears, including the ones still False. That
    is on purpose: if only ticked boxes were included, un-ticking one after
    confirmation would produce a payload whose hash the confirmation still
    matched, and INV-03 would silently not fire.
    """
    if vehicle is None or dealer is None or case_row.handover_local_time is None:
        return None
    codes = sorted(ctx.policy.declaration_codes())
    return CanonicalPayload(
        case_id=case_row.id,
        policy_version=case_row.policy_version,
        vehicle=CanonicalVehicle(
            registration_no=vehicle.registration_no,
            chassis_suffix=vehicle.chassis_suffix,
        ),
        dealer=CanonicalDealer(
            authorisation_no=dealer.authorisation_no,
            business_name=dealer.business_name,
        ),
        declarations=tuple(
            CanonicalDeclaration(code=code, value=bool(declarations.get(code, False)))
            for code in codes
        ),
        handover_local_time=case_row.handover_local_time,
        registered_owner_name=vehicle.registered_owner_name,
    )


def load_view(
    ctx: ServiceContext,
    connection: sqlite3.Connection,
    case_row: repo.CaseRow,
    *,
    dealer_purpose: LookupPurpose = LookupPurpose.VERIFICATION,
) -> CaseView:
    """Read-only snapshot. Performs no writes and no state derivation."""
    vehicle = resolve_vehicle(ctx, case_row)
    dealer = resolve_dealer(ctx, case_row, purpose=dealer_purpose)
    declarations = repo.declaration_values(connection, case_row.id)
    joined = dealer_has_joined(connection, case_row.id)
    policy_context = build_policy_context(
        vehicle=vehicle,
        dealer=dealer,
        declarations=declarations,
        dealer_joined=joined,
    )
    return CaseView(
        case=case_row,
        vehicle=vehicle,
        dealer=dealer,
        dealer_joined=joined,
        declarations=declarations,
        preflight=ctx.policy.evaluate(policy_context, PolicyStage.PREFLIGHT),
        submit=ctx.policy.evaluate(policy_context, PolicyStage.SUBMIT),
        payload=build_canonical_payload(
            ctx,
            case_row,
            vehicle=vehicle,
            dealer=dealer,
            declarations=declarations,
        ),
        latest_attempt=repo.latest_attempt(connection, case_row.id),
        acknowledgement=repo.acknowledged_attempt(connection, case_row.id),
    )


def refresh(
    ctx: ServiceContext,
    connection: sqlite3.Connection,
    case_row: repo.CaseRow,
    *,
    actor: Actor,
    event_type: str,
    detail: Mapping[str, object] | None = None,
    dealer_purpose: LookupPurpose = LookupPurpose.VERIFICATION,
) -> CaseView:
    """Recompute the payload hash and state after a fact changed.

    Called by every mutating service. The order matters: hash first, then
    confirmation invalidation, then state derivation -- deriving before
    invalidating would briefly compute a state from confirmations that were about
    to be dropped.

    ``dealer_purpose`` is REVALIDATION only on the submit path (INV-04). Note that
    a revalidated status can move the case to DEALER_INVALID without touching the
    canonical payload, because the payload records *which* dealer, not their
    current authorisation status -- so confirmations survive a status change, and
    it is the state, not the hash, that stops the submission.
    """
    vehicle = resolve_vehicle(ctx, case_row)
    dealer = resolve_dealer(ctx, case_row, purpose=dealer_purpose)
    declarations = repo.declaration_values(connection, case_row.id)
    joined = dealer_has_joined(connection, case_row.id)

    payload = build_canonical_payload(
        ctx,
        case_row,
        vehicle=vehicle,
        dealer=dealer,
        declarations=declarations,
    )
    new_hash = payload_hash(payload) if payload is not None else None
    payload_changed = new_hash != case_row.payload_hash

    if payload_changed:
        repo.update_case(connection, case_row.id, payload_hash=new_hash)
        # INV-03. Unconditional: a confirmation is a statement about one exact set
        # of details, so any change to those details ends it.
        repo.clear_confirmations(connection, case_row.id)

    reloaded = repo.get_case(connection, case_row.id)
    assert reloaded is not None  # same transaction; the row cannot vanish

    policy_context = build_policy_context(
        vehicle=vehicle,
        dealer=dealer,
        declarations=declarations,
        dealer_joined=joined,
    )
    preflight = ctx.policy.evaluate(policy_context, PolicyStage.PREFLIGHT)
    submit = ctx.policy.evaluate(policy_context, PolicyStage.SUBMIT)

    target = derive_case_state(
        current=reloaded.current_state,
        vehicle_loaded=vehicle is not None,
        dealer_loaded=dealer is not None,
        dealer_can_continue=dealer is not None and dealer.can_continue,
        preflight=preflight,
        submit=submit,
        seller_confirmed=reloaded.seller_confirmed,
        dealer_confirmed=reloaded.dealer_confirmed,
        payload_changed=payload_changed,
    )

    state_before = reloaded.current_state
    if target is not state_before:
        repo.transition_state(
            connection, reloaded.id, expected=(state_before,), new_state=target
        )
        reloaded = repo.get_case(connection, reloaded.id)
        assert reloaded is not None

    event_detail: dict[str, object] = dict(detail or {})
    event_detail["payload_changed"] = payload_changed
    if payload_changed and case_row.payload_hash is not None:
        # Recorded so the audit trail explains why confirmations disappeared.
        event_detail["confirmations_cleared"] = True
    repo.append_event(
        connection,
        case_id=reloaded.id,
        event_type=event_type,
        actor=actor.value,
        state_before=state_before,
        state_after=reloaded.current_state,
        payload_digest=reloaded.payload_hash,
        detail=event_detail,
    )

    return CaseView(
        case=reloaded,
        vehicle=vehicle,
        dealer=dealer,
        dealer_joined=joined,
        declarations=declarations,
        preflight=preflight,
        submit=submit,
        payload=payload,
        latest_attempt=repo.latest_attempt(connection, reloaded.id),
        acknowledgement=repo.acknowledged_attempt(connection, reloaded.id),
    )


__all__ = [
    "CaseView",
    "DealerStatus",
    "LookupPurpose",
    "build_canonical_payload",
    "build_policy_context",
    "dealer_has_joined",
    "load_view",
    "payload_hash",
    "refresh",
    "resolve_dealer",
    "resolve_vehicle",
]
