"""WebSocket channel for case updates.

Kept separate from ``routes.py`` because the failure model is different. An HTTP
route that raises owes the client an error contract; a socket that fails owes the
client nothing, because the client is already polling REST every two seconds as its
fallback (SRS section 6).

The rule that makes this safe: **every message is a full authoritative snapshot
read from the database.** The socket never carries a delta, never carries a
"success" signal of its own, and is never the reason the UI turns green. If this
whole module were deleted the product would still be correct, only slower -- which
is the test for whether a realtime layer has been given too much authority.
"""

from __future__ import annotations

import asyncio
import contextlib

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_in_threadpool

from ..errors import AppError
from ..services.case_service import CaseService
from ..services.context import ServiceContext
from .serialisers import serialise_case

ws_router = APIRouter()

#: Seconds between server-initiated pings. Well under the 60-second idle timeout
#: that most proxies apply, so a quiet case does not look like a dead socket.
PING_INTERVAL_SECONDS = 20.0


async def _send_snapshot(
    websocket: WebSocket, ctx: ServiceContext, case_id: str
) -> bool:
    """Send the current snapshot. Returns False if the case is gone."""
    try:
        view = await run_in_threadpool(CaseService(ctx).snapshot, case_id=case_id)
    except AppError:
        return False
    await websocket.send_json(
        {"type": "CASE_SNAPSHOT", "case": serialise_case(view, actor=None)}
    )
    return True


@ws_router.websocket("/ws/cases/{case_id}")
async def case_socket(websocket: WebSocket, case_id: str) -> None:
    ctx: ServiceContext = websocket.app.state.ctx
    await websocket.accept()

    # An immediate snapshot on connect, so a client that reconnects after a network
    # blip is correct straight away rather than correct at the next mutation.
    if not await _send_snapshot(websocket, ctx, case_id):
        await websocket.close(code=4404, reason="Case not found")
        return

    subscription = ctx.events.subscribe(case_id)
    try:
        while True:
            try:
                message = await asyncio.wait_for(
                    subscription.queue.get(), timeout=PING_INTERVAL_SECONDS
                )
            except asyncio.TimeoutError:
                # Keepalive. Carries no state: a client must never learn anything
                # from a ping.
                await websocket.send_json({"type": "PING"})
                continue
            await websocket.send_json(message)
    except WebSocketDisconnect:
        pass
    except RuntimeError:
        # Raised when the socket is already closing underneath us. Nothing to
        # report: the client is gone and the REST fallback covers whatever it
        # missed.
        pass
    finally:
        ctx.events.unsubscribe(subscription)
        with contextlib.suppress(RuntimeError):
            await websocket.close()


__all__ = ["PING_INTERVAL_SECONDS", "ws_router"]
