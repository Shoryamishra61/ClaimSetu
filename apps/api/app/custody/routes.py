"""FastAPI transport for the four-state custody-record slice."""

from __future__ import annotations

from fastapi import APIRouter, Query, Request, Response, WebSocket, WebSocketDisconnect, status
from fastapi.concurrency import run_in_threadpool

from .models import DealerLookupRequest, InitiateCaseRequest, StateTransitionRequest
from .service import CustodyService, serialise_case

router = APIRouter()


def _service(request: Request) -> CustodyService:
    return CustodyService(request.app.state.custody_db)


@router.get("/vehicle/verify")
async def verify_vehicle(
    request: Request,
    vehicle_no: str = Query(min_length=4, max_length=32),
    chassis_suffix: str = Query(min_length=3, max_length=32),
) -> dict[str, object]:
    data = await run_in_threadpool(
        _service(request).verify_vehicle,
        vehicle_no=vehicle_no,
        chassis_suffix=chassis_suffix,
    )
    return {"status": "success", "simulation": True, "data": data}


@router.post("/case/initiate", status_code=status.HTTP_201_CREATED)
async def initiate_case(
    request: Request, body: InitiateCaseRequest
) -> dict[str, object]:
    created = await run_in_threadpool(
        _service(request).initiate,
        vehicle_no=body.vehicle_no,
        chassis_suffix=body.chassis_suffix,
        seller_id=body.seller_id,
    )
    return {
        "status": "success",
        "simulation": True,
        "case": serialise_case(created),
        "case_id": created.case_id,
        "websocket_sync_url": f"/api/v1/sync/{created.case_id}",
    }


@router.post("/dealer/verify")
async def verify_dealer(
    request: Request, body: DealerLookupRequest
) -> dict[str, object]:
    data = await run_in_threadpool(
        _service(request).verify_dealer,
        gstin=body.gstin,
        trade_certificate_no=body.trade_certificate_no,
    )
    return {"status": "success", "simulation": True, "data": data}


@router.get("/cases/{case_id}/custody")
async def get_custody_case(request: Request, case_id: str) -> dict[str, object]:
    case = await run_in_threadpool(_service(request).get_case, case_id)
    return {"status": "success", "simulation": True, "case": serialise_case(case)}


@router.patch("/cases/{case_id}/state")
async def transition_state(
    request: Request, case_id: str, body: StateTransitionRequest
) -> dict[str, object]:
    case = await run_in_threadpool(
        CustodyService(request.app.state.custody_db).transition,
        case_id=case_id,
        target=body.state,
        dealer_id=body.dealer_id,
        odometer_reading=body.odometer_reading,
        seller_confirmed=body.seller_confirmed,
        dealer_confirmed=body.dealer_confirmed,
    )
    payload = {"type": "CUSTODY_CASE_SNAPSHOT", "case": serialise_case(case)}
    request.app.state.custody_events.publish(case_id, payload)
    return {"status": "success", "simulation": True, "case": serialise_case(case)}


@router.get("/cases/{case_id}/transitions")
async def transition_log(request: Request, case_id: str) -> dict[str, object]:
    events = await run_in_threadpool(_service(request).transition_log, case_id)
    return {"status": "success", "simulation": True, "transitions": events}


@router.get("/cases/{case_id}/form29c.pdf")
async def download_form29c(request: Request, case_id: str) -> Response:
    content, digest = await run_in_threadpool(_service(request).get_document, case_id)
    return Response(
        content=content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="handover29c-{case_id}.pdf"',
            "X-Document-SHA256": digest,
            "X-Prototype-Document": "simulated-not-government-submission",
        },
    )


@router.websocket("/sync/{case_id}")
async def custody_sync(websocket: WebSocket, case_id: str) -> None:
    await websocket.accept()
    service = CustodyService(websocket.app.state.custody_db)
    try:
        case = await run_in_threadpool(service.get_case, case_id)
        await websocket.send_json(
            {"type": "CUSTODY_CASE_SNAPSHOT", "case": serialise_case(case)}
        )
        async with websocket.app.state.custody_events.subscribe(case_id) as subscription:
            while True:
                await websocket.send_json(await subscription.queue.get())
    except WebSocketDisconnect:
        return
    except Exception:
        await websocket.close(code=4404, reason="Custody case not found")


__all__ = ["router"]
