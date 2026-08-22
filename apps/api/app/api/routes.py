"""HTTP surface. Thin by design.

Every route here does four things and no more: parse input, call one service
method, publish the resulting snapshot to the WebSocket bus, return the serialised
snapshot. There is no business rule in this file -- no state check, no hash
comparison, no policy evaluation. That is the point: if a rule lived here it would
be enforced only for callers who came through HTTP, and the invariant tests drive
the services directly.

Notable consequences:

*   **There is no endpoint that sets a state.** The client can submit facts and
    that is all. This is what makes "a client cannot navigate to success" true at
    the API level and not merely in the router.
*   **The WebSocket publish is fire-and-forget.** A delivery failure never affects
    the HTTP response, because the socket is an accelerator and the REST poll is
    the fallback (SRS section 6).
*   **``Idempotency-Key`` is read from the header**, not the body, so a retry made
    by an HTTP layer that replays the request unchanged is automatically safe.
"""

from __future__ import annotations

import asyncio
from typing import Annotated

from fastapi import APIRouter, Header, Request, Response, status
from fastapi.concurrency import run_in_threadpool

from .. import copy as disclosure
from ..copy import meta_payload
from ..db import repository as repo
from ..domain.policy_types import PolicyContext, PolicyStage
from ..domain.states import CaseState
from ..errors import AppError
from ..services.case_service import CaseService
from ..services.confirmation_service import ConfirmationService
from ..services.context import ServiceContext
from ..services.pairing_service import PairingService
from ..services.projection import CaseView
from ..services.submission_service import SubmissionResult, SubmissionService
from .schemas import (
    ConfirmRequest,
    CreateCaseRequest,
    DealerVerifyRequest,
    DeclarationsRequest,
    JoinPairRequest,
    SubmitRequest,
    VehicleVerifyRequest,
)
from .serialisers import (
    serialise_attempt,
    serialise_case,
    serialise_dealer,
    serialise_evaluation,
    serialise_event,
    serialise_payload,
    serialise_vehicle,
)

router = APIRouter()

#: Header the SPA uses to present a party token. Not a cookie: the dealer and the
#: seller are frequently the same browser during a demo on one laptop, and cookies
#: would make them share an identity.
TOKEN_HEADER = "X-Party-Token"

PartyToken = Annotated[str | None, Header(alias=TOKEN_HEADER)]


def ctx_of(request: Request) -> ServiceContext:
    return request.app.state.ctx


def client_key(request: Request) -> str:
    """Rate-limit bucket for an unauthenticated caller.

    Falls back to a constant when the client address is unavailable, which is the
    conservative choice: an unknown caller shares a bucket rather than escaping the
    limit entirely.
    """
    return request.client.host if request.client else "unknown"


def publish(ctx: ServiceContext, view: CaseView, *, actor_hint: str | None = None) -> None:
    """Push a full authoritative snapshot to this case's listeners.

    A snapshot rather than a diff, deliberately. A client that rebuilt state from a
    stream of deltas could drift from the server after a dropped message, and the
    one thing the realtime layer must never do is disagree with the database about
    whether a handover was acknowledged.
    """
    ctx.events.publish(
        view.case.id,
        {
            "type": "CASE_SNAPSHOT",
            # ``your_role`` is intentionally None on the socket: one broadcast goes
            # to both parties, so it cannot be personalised. The client already
            # knows its own role from the response that gave it its token.
            "case": serialise_case(view, actor=None),
            "actor_hint": actor_hint,
        },
    )


# ---------------------------------------------------------------------------
# metadata, fixtures, policy -- everything a reviewer needs to check our claims
# ---------------------------------------------------------------------------


@router.get("/meta")
async def get_meta(request: Request) -> dict[str, object]:
    ctx = ctx_of(request)
    return meta_payload(
        build_label=ctx.settings.build_label,
        policy_version=ctx.policy.version,
        poll_interval_seconds=ctx.settings.poll_interval_seconds,
    )


@router.get("/fixtures")
async def get_fixtures(request: Request) -> dict[str, object]:
    """The demo cast list.

    Exposed because a demo that requires the presenter to know magic strings is a
    demo that breaks on stage. Every fictional record is listed with its scenario,
    so a judge can pick the rejection or the unknown-outcome case on purpose.
    """
    ctx = ctx_of(request)
    return {
        "simulation": True,
        "vehicles": [serialise_vehicle(v) for v in ctx.vehicles.all()],
        "dealers": [serialise_dealer(d) for d in ctx.dealers.all()],
    }


@router.get("/policy")
async def get_policy(request: Request) -> dict[str, object]:
    """The rule set the running instance evaluates, with per-item provenance.

    ``in_force`` is included so the source drawer can state plainly that the draft
    2026 amendment is not what is being applied.
    """
    ctx = ctx_of(request)
    policy = ctx.policy
    return {
        "version": policy.version,
        "title": policy.title,
        "source_id": policy.source_id,
        "source_locator": policy.source_locator,
        "in_force": policy.in_force,
        "anchor_text": {
            "en": disclosure.POLICY_ANCHOR_EN,
            "hi": disclosure.POLICY_ANCHOR_HI,
        },
        "items": serialise_evaluation(
            # An empty context: this endpoint documents the rules, it does not
            # evaluate a case. The frontend reads only labels and provenance from
            # it, never the results.
            policy.evaluate(
                PolicyContext(vehicle_loaded=False, dealer_status=None),
                PolicyStage.SUBMIT,
            )
        )["items"],
    }


# ---------------------------------------------------------------------------
# case lifecycle
# ---------------------------------------------------------------------------


@router.post("/cases", status_code=status.HTTP_201_CREATED)
async def create_case(
    request: Request, body: CreateCaseRequest
) -> dict[str, object]:
    ctx = ctx_of(request)
    created = await run_in_threadpool(
        CaseService(ctx).create_case, journey_type=body.journey_type
    )
    return {
        "case": serialise_case(created.view, actor=None),
        # Returned exactly once. The client stores it for the session; the server
        # keeps only its SHA-256.
        "party_token": created.seller_token,
        "your_role": "SELLER",
    }


@router.get("/cases/{case_id}")
async def get_case(
    request: Request, case_id: str, token: PartyToken = None
) -> dict[str, object]:
    ctx = ctx_of(request)
    service = CaseService(ctx)
    view = await run_in_threadpool(service.snapshot, case_id=case_id)
    actor = await run_in_threadpool(service.actor_for, case_id=case_id, token=token)
    return {"case": serialise_case(view, actor=actor)}


@router.post("/cases/{case_id}/vehicle/verify")
async def verify_vehicle(
    request: Request,
    case_id: str,
    body: VehicleVerifyRequest,
    token: PartyToken = None,
) -> dict[str, object]:
    ctx = ctx_of(request)
    view = await run_in_threadpool(
        CaseService(ctx).verify_vehicle,
        case_id=case_id,
        token=token,
        registration_no=body.registration_no,
        chassis_suffix=body.chassis_suffix,
    )
    publish(ctx, view, actor_hint="SELLER")
    return {"case": serialise_case(view, actor=None)}


@router.post("/cases/{case_id}/dealer/verify")
async def verify_dealer(
    request: Request,
    case_id: str,
    body: DealerVerifyRequest,
    token: PartyToken = None,
) -> dict[str, object]:
    ctx = ctx_of(request)
    view = await run_in_threadpool(
        CaseService(ctx).verify_dealer,
        case_id=case_id,
        token=token,
        authorisation_no=body.authorisation_no,
    )
    publish(ctx, view, actor_hint="SELLER")
    return {"case": serialise_case(view, actor=None)}


@router.get("/cases/{case_id}/preflight")
async def get_preflight(request: Request, case_id: str) -> dict[str, object]:
    ctx = ctx_of(request)
    view = await run_in_threadpool(CaseService(ctx).snapshot, case_id=case_id)
    return {
        "preflight": serialise_evaluation(view.preflight),
        "submit_checks": serialise_evaluation(view.submit),
        "state": view.state.value,
    }


@router.post("/cases/{case_id}/declarations")
async def set_declarations(
    request: Request,
    case_id: str,
    body: DeclarationsRequest,
    token: PartyToken = None,
) -> dict[str, object]:
    ctx = ctx_of(request)
    view = await run_in_threadpool(
        CaseService(ctx).set_declarations,
        case_id=case_id,
        token=token,
        values=body.values,
    )
    publish(ctx, view)
    return {"case": serialise_case(view, actor=None)}


@router.post("/cases/{case_id}/cancel")
async def cancel_case(
    request: Request, case_id: str, token: PartyToken = None
) -> dict[str, object]:
    ctx = ctx_of(request)
    view = await run_in_threadpool(
        CaseService(ctx).cancel, case_id=case_id, token=token
    )
    publish(ctx, view, actor_hint="SELLER")
    return {"case": serialise_case(view, actor=None)}


@router.get("/cases/{case_id}/audit")
async def get_audit(request: Request, case_id: str) -> dict[str, object]:
    """The hash-chained event log, for the source drawer.

    ``chain_valid`` is recomputed on read rather than stored. This is
    tamper-evidence for a prototype -- it shows the log has not been edited in
    place. It is not an independent audit guarantee, and the drawer says so.
    """
    ctx = ctx_of(request)
    events = await run_in_threadpool(CaseService(ctx).audit_trail, case_id=case_id)
    return {
        "events": [serialise_event(e) for e in events],
        "chain_valid": repo.verify_chain(events),
    }


# ---------------------------------------------------------------------------
# pairing
# ---------------------------------------------------------------------------


@router.post("/cases/{case_id}/pair")
async def create_pair_code(
    request: Request, case_id: str, token: PartyToken = None
) -> dict[str, object]:
    ctx = ctx_of(request)
    issued = await run_in_threadpool(
        PairingService(ctx).issue_code, case_id=case_id, token=token
    )
    publish(ctx, issued.view, actor_hint="SELLER")
    return {
        "case": serialise_case(issued.view, actor=None),
        # Shown once, as a code and a QR. Only its hash reaches the database.
        "pair_code": issued.code,
        "expires_at": issued.expires_at,
        "expires_in_seconds": issued.expires_in_seconds,
    }


@router.post("/pair/join")
async def join_pair(
    request: Request, body: JoinPairRequest
) -> dict[str, object]:
    ctx = ctx_of(request)
    # Rate limiting lives in the service, keyed by both the code hash and this
    # client key, so the limit applies however the caller reaches it.
    redeemed = await run_in_threadpool(
        request.app.state.pairing.redeem,
        code=body.code,
        client_key=client_key(request),
    )
    publish(ctx, redeemed.view, actor_hint="DEALER")
    return {
        "case": serialise_case(redeemed.view, actor=None),
        "case_id": redeemed.case_id,
        "party_token": redeemed.dealer_token,
        "your_role": "DEALER",
    }


# ---------------------------------------------------------------------------
# review and confirmation
# ---------------------------------------------------------------------------


@router.get("/cases/{case_id}/review")
async def get_review(request: Request, case_id: str) -> dict[str, object]:
    ctx = ctx_of(request)
    view = await run_in_threadpool(CaseService(ctx).snapshot, case_id=case_id)
    return {
        "review": serialise_payload(view.payload, view.case.payload_hash),
        "seller_confirmed": view.case.seller_confirmed,
        "dealer_confirmed": view.case.dealer_confirmed,
        "state": view.state.value,
        "meaning": {
            "en": disclosure.CONFIRMATION_MEANING_EN,
            "hi": disclosure.CONFIRMATION_MEANING_HI,
        },
    }


@router.post("/cases/{case_id}/confirm")
async def confirm(
    request: Request,
    case_id: str,
    body: ConfirmRequest,
    token: PartyToken = None,
) -> dict[str, object]:
    ctx = ctx_of(request)
    result = await run_in_threadpool(
        ConfirmationService(ctx).confirm,
        case_id=case_id,
        token=token,
        payload_hash_claim=body.payload_hash,
    )
    publish(ctx, result.view, actor_hint=result.actor.value)
    return {
        "case": serialise_case(result.view, actor=result.actor),
        "already_confirmed": result.already_confirmed,
    }


@router.post("/cases/{case_id}/withdraw-confirmation")
async def withdraw_confirmation(
    request: Request, case_id: str, token: PartyToken = None
) -> dict[str, object]:
    ctx = ctx_of(request)
    result = await run_in_threadpool(
        ConfirmationService(ctx).withdraw, case_id=case_id, token=token
    )
    publish(ctx, result.view, actor_hint=result.actor.value)
    return {"case": serialise_case(result.view, actor=result.actor)}


# ---------------------------------------------------------------------------
# submission
# ---------------------------------------------------------------------------


def _submission_response(result: SubmissionResult) -> dict[str, object]:
    return {
        "case": serialise_case(result.view, actor=None),
        "attempt": serialise_attempt(result.attempt),
        "replayed": result.replayed,
        # Read off the persisted ACK row, never off the response status, so this
        # field cannot disagree with the database (INV-01).
        "acknowledgement_no": result.acknowledgement_no,
        "acknowledgement_caveat": {
            "en": disclosure.ACKNOWLEDGEMENT_CAVEAT_EN,
            "hi": disclosure.ACKNOWLEDGEMENT_CAVEAT_HI,
        },
    }


@router.post("/cases/{case_id}/submit")
async def submit(
    request: Request,
    case_id: str,
    body: SubmitRequest,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    token: PartyToken = None,
) -> dict[str, object]:
    """Two phases, so SUBMITTING_29C is genuinely observable.

    ``begin`` commits the in-flight state and broadcasts it before the adapter is
    consulted; the simulated latency is then awaited; ``complete`` records the
    outcome. The finishing half runs as a shielded task, so a client that closes
    the tab mid-submission still gets its outcome written -- otherwise a
    disconnect would strand the case in SUBMITTING_29C with nothing able to move it.
    """
    if not idempotency_key:
        raise AppError("IDEMPOTENCY_KEY_REQUIRED")
    ctx = ctx_of(request)
    service = SubmissionService(ctx)

    began = await run_in_threadpool(
        service.begin,
        case_id=case_id,
        token=token,
        payload_hash_claim=body.payload_hash,
        idempotency_key=idempotency_key,
    )
    if isinstance(began, SubmissionResult):
        # A replay. No adapter call, no delay, and the original answer verbatim.
        return _submission_response(began)

    publish(ctx, began.view)

    async def finish() -> SubmissionResult:
        latency = ctx.settings.simulated_adapter_latency_ms / 1000.0
        if latency > 0:
            await asyncio.sleep(latency)
        outcome = await run_in_threadpool(service.complete, began)
        publish(ctx, outcome.view)
        return outcome

    task = asyncio.create_task(finish())
    result = await asyncio.shield(task)
    return _submission_response(result)


@router.get("/cases/{case_id}/submission-status")
async def submission_status(request: Request, case_id: str) -> dict[str, object]:
    """What the last attempt said, for refresh and for unknown-outcome recovery.

    ``can_reconcile`` is server-decided rather than inferred by the client from the
    state string, so there is one place that knows when re-checking is meaningful.
    """
    ctx = ctx_of(request)
    view = await run_in_threadpool(CaseService(ctx).snapshot, case_id=case_id)
    return {
        "state": view.state.value,
        "is_acknowledged": view.is_acknowledged,
        "acknowledgement": serialise_attempt(view.acknowledgement),
        "latest_attempt": serialise_attempt(view.latest_attempt),
        "can_reconcile": view.state is CaseState.SUBMISSION_UNKNOWN,
        "can_retry": view.state is CaseState.SUBMISSION_TEMPORARY_FAILURE,
    }


@router.post("/cases/{case_id}/reconcile")
async def reconcile(
    request: Request, case_id: str, token: PartyToken = None
) -> dict[str, object]:
    ctx = ctx_of(request)
    result = await run_in_threadpool(
        SubmissionService(ctx).reconcile, case_id=case_id, token=token
    )
    publish(ctx, result.view)
    return _submission_response(result)


@router.get("/cases/{case_id}/dealer-revalidation")
async def dealer_revalidation(request: Request, case_id: str) -> dict[str, object]:
    """A read-only preview of what submit-time revalidation would find.

    Exists for the demo narrative around threat T06. It changes nothing: the
    authoritative recheck happens inside the submission service.
    """
    ctx = ctx_of(request)
    record = await run_in_threadpool(
        CaseService(ctx).dealer_revalidation, case_id=case_id
    )
    if record is None:
        return {"simulation": True, "dealer": None}
    return {"simulation": True, "dealer": serialise_dealer(record)}


# ---------------------------------------------------------------------------
# demo support
# ---------------------------------------------------------------------------


@router.post("/demo/reset", status_code=status.HTTP_204_NO_CONTENT)
async def demo_reset(request: Request) -> Response:
    """Wipe all case data so a demo can be re-run cleanly.

    Fixtures are files, not rows, so this cannot delete the demo cast. It also
    clears the rate-limit windows, because a presenter who has just demonstrated
    the pairing limit should not then be locked out of their own demo.
    """
    ctx = ctx_of(request)
    await run_in_threadpool(ctx.db.reset)
    request.app.state.pairing.reset_limits()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


__all__ = ["TOKEN_HEADER", "router"]
