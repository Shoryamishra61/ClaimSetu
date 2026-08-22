"""Domain objects -> JSON, by explicit allow-list.

Written by hand rather than generated from the dataclasses, for one reason: the
security requirement is that a case snapshot contains no secrets (SRS section 6,
threat T04). An allow-list serialiser fails closed -- a new field on ``CaseRow`` is
invisible until someone adds it here. Reflection over ``__dataclass_fields__``
would fail open, and the field it leaked would be the one nobody thought about.

Two consequences worth stating:

*   No token, token hash, or party session id appears in any function here.
*   ``payload_hash`` *is* returned, because the client must echo it back on confirm
    and submit. The UX bar keeps it out of the visible UI; that is the frontend's
    job, not a reason to withhold it from the API.
"""

from __future__ import annotations

from ..adapters.mock_dealer_registry import (
    STATUS_TEXT_EN,
    STATUS_TEXT_HI,
    DealerRecord,
    DealerStatus,
)
from ..adapters.mock_form29c_adapter import REASON_TEXT_EN, REASON_TEXT_HI, ReasonCode
from ..adapters.mock_vehicle_registry import VehicleRecord
from ..db import repository as repo
from ..domain.canonical import CANONICAL_SCHEMA_VERSION, CanonicalPayload
from ..domain.policy_types import ItemResult, PolicyEvaluation
from ..domain.states import (
    NON_ACK_SUBMISSION_OUTCOMES,
    Actor,
    CaseState,
)
from ..services.projection import CaseView


def serialise_vehicle(record: VehicleRecord) -> dict[str, object]:
    return {
        **record.envelope(),
        "id": record.id,
        "registration_no": record.registration_no,
        "chassis_suffix": record.chassis_suffix,
        "make_model": record.make_model,
        "registered_owner_name": record.registered_owner_name,
        "document_flags": dict(record.document_flags),
        # Named openly. A judge choosing the UNKNOWN vehicle should know that is
        # what they picked; a hidden scenario switch would be the dishonest option.
        "submission_scenario": record.submission_scenario,
        "is_default_demo": record.is_default_demo,
        "demo_label": {"en": record.demo_label_en, "hi": record.demo_label_hi},
    }


def serialise_dealer(record: DealerRecord) -> dict[str, object]:
    return {
        **record.envelope(),
        "id": record.id,
        "authorisation_no": record.authorisation_no,
        "business_name": record.business_name,
        "status": record.status.value,
        "status_text": {
            "en": STATUS_TEXT_EN[record.status],
            "hi": STATUS_TEXT_HI[record.status],
        },
        "can_continue": record.can_continue,
        "valid_from": record.valid_from,
        "valid_until": record.valid_until,
        "is_default_demo": record.is_default_demo,
        "demo_label": {"en": record.demo_label_en, "hi": record.demo_label_hi},
    }


def serialise_evaluation(evaluation: PolicyEvaluation) -> dict[str, object]:
    return {
        "policy_version": evaluation.policy_version,
        "stage": evaluation.stage.value,
        "passed": evaluation.passed,
        "items": [
            {
                "code": item.code,
                "label": {"en": item.label_en, "hi": item.label_hi},
                "help": {"en": item.help_en, "hi": item.help_hi},
                # Provenance per row, so the UI can badge "we checked this against a
                # simulated fixture" separately from "you told us this".
                "source_type": item.source_type.value,
                "responsible": item.responsible.value,
                "source_id": item.source_id,
                "source_locator": item.source_locator,
                "blocking_stage": item.blocking_stage.value,
                "blocking": item.blocking,
                "result": item.result.value,
            }
            for item in evaluation.items
        ],
        "blocking_failures": [i.code for i in evaluation.blocking_failures],
        "pending_codes": [
            i.code for i in evaluation.items if i.result is ItemResult.PENDING
        ],
    }


def serialise_payload(payload: CanonicalPayload | None, payload_hash: str | None) -> dict[str, object] | None:
    """The exact object both parties confirm, plus its digest.

    ``canonical`` is the serialised form the hash is taken over, returned so a
    reviewer can recompute the digest themselves rather than take the app's word.
    """
    if payload is None:
        return None
    return {
        "schema_version": CANONICAL_SCHEMA_VERSION,
        "canonical": payload.to_canonical_dict(),
        "payload_hash": payload_hash,
    }


def serialise_attempt(attempt: repo.SubmissionAttemptRow | None) -> dict[str, object] | None:
    if attempt is None:
        return None
    reason = ReasonCode(attempt.reason_code) if attempt.reason_code else None
    return {
        "simulation": True,
        "attempt_number": attempt.attempt_number,
        "status": attempt.status,
        "acknowledgement_no": attempt.acknowledgement_no,
        "reason_code": attempt.reason_code,
        "reason_text": (
            {"en": REASON_TEXT_EN[reason], "hi": REASON_TEXT_HI[reason]}
            if reason is not None
            else None
        ),
        "created_at": attempt.created_at,
        "completed_at": attempt.completed_at,
    }


def serialise_event(event: repo.AuditEventRow) -> dict[str, object]:
    """One audit row for the source drawer.

    ``event_hash`` and ``prev_hash`` are included because the drawer's purpose is
    to let a reviewer verify the chain. This is tamper-evidence for a demo, not a
    cryptographic audit guarantee, and the drawer copy says so.
    """
    return {
        "sequence": event.id,
        "event_type": event.event_type,
        "actor": event.actor,
        "state_before": event.state_before,
        "state_after": event.state_after,
        "detail": event.detail,
        "created_at": event.created_at,
        "event_hash": event.event_hash,
        "previous_event_hash": event.previous_event_hash,
    }


def serialise_case(view: CaseView, *, actor: Actor | None) -> dict[str, object]:
    """The full safe snapshot. Contains no token and no session identifier.

    ``is_acknowledged`` is computed by :class:`CaseView`, which requires both the
    terminal state and a persisted acknowledgement row. The frontend renders green
    on this flag alone, so there is one definition of success and it lives on the
    server (INV-01).
    """
    case = view.case
    return {
        "simulation": True,
        "id": case.id,
        "journey_type": case.journey_type,
        "policy_version": case.policy_version,
        "state": case.current_state.value,
        # Deliberately explicit rather than left to the client to infer from the
        # state string. A client that string-matches states will eventually match
        # the wrong one.
        "is_acknowledged": view.is_acknowledged,
        "is_terminal": case.current_state
        in (CaseState.HANDOFF_ACKNOWLEDGED, CaseState.CANCELLED),
        "is_failed_outcome": case.current_state in NON_ACK_SUBMISSION_OUTCOMES,
        "your_role": actor.value if actor is not None else None,
        "seller_confirmed": case.seller_confirmed,
        "dealer_confirmed": case.dealer_confirmed,
        "dealer_joined": view.dealer_joined,
        "handover_local_time": case.handover_local_time,
        "vehicle": serialise_vehicle(view.vehicle) if view.vehicle else None,
        "dealer": serialise_dealer(view.dealer) if view.dealer else None,
        "declarations": view.declarations,
        "preflight": serialise_evaluation(view.preflight),
        "submit_checks": serialise_evaluation(view.submit),
        "review": serialise_payload(view.payload, case.payload_hash),
        "latest_attempt": serialise_attempt(view.latest_attempt),
        "acknowledgement": serialise_attempt(view.acknowledgement),
        "created_at": case.created_at,
        "updated_at": case.updated_at,
    }


def serialise_dealer_status(status: DealerStatus) -> dict[str, object]:
    return {
        "simulation": True,
        "status": status.value,
        "status_text": {"en": STATUS_TEXT_EN[status], "hi": STATUS_TEXT_HI[status]},
    }


__all__ = [
    "serialise_attempt",
    "serialise_case",
    "serialise_dealer",
    "serialise_dealer_status",
    "serialise_evaluation",
    "serialise_event",
    "serialise_payload",
    "serialise_vehicle",
]
