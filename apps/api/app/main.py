"""Application factory, middleware and error handling.

Three things here are product requirements rather than boilerplate:

1.  **The error contract is total.** ``AppError`` maps to its catalogue entry;
    everything else becomes ``INTERNAL_ERROR`` with a fixed bilingual message. No
    stack trace, no exception text, no SQL fragment reaches a client. A leaked
    internal message is how a demo audience learns your table names.

2.  **Security headers are set here, not in a proxy.** The deployment target is a
    single container that may sit behind a platform router nobody configures, so the
    headers travel with the app. ``frame-ancestors 'none'`` matters specifically:
    this prototype must not be embeddable inside a page that dresses it up as an
    official service.

3.  **Domain exceptions are translated, never leaked.** ``IllegalTransition`` and
    ``ConcurrentModification`` are internal vocabulary; a client sees
    ``INVALID_STATE`` and ``SUBMISSION_IN_PROGRESS``.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from .api.routes import router
from .api.websocket import ws_router
from .config import Settings, load_settings
from .custody.routes import router as custody_router
from .custody.schema import initialise_custody_schema
from .db import Database
from .db.repository import ConcurrentModification
from .domain.policies import registry
from .domain.states import IllegalTransition
from .errors import AppError
from .services.context import ServiceContext
from .services.events import EventBus
from .services.pairing_service import PairingService

logger = logging.getLogger("handover29c")

#: No inline script, no external origin, nothing embeddable. ``style-src`` allows
#: inline styles because the Vite build inlines critical CSS; scripts do not get the
#: same latitude.
CONTENT_SECURITY_POLICY = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; "
    "font-src 'self' data:; "
    "connect-src 'self' ws: wss:; "
    "frame-ancestors 'none'; "
    "base-uri 'self'; "
    "form-action 'none'; "
    "object-src 'none'"
)

SECURITY_HEADERS = {
    "Content-Security-Policy": CONTENT_SECURITY_POLICY,
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Permissions-Policy": (
        # Named explicitly rather than left to defaults. The product does not use
        # location, camera or microphone, and saying so in a header is a claim a
        # reviewer can verify without reading the source.
        "geolocation=(), camera=(), microphone=(), payment=(), usb=()"
    ),
    # This prototype has no login, so there is nothing to keep out of a cache for
    # confidentiality; the concern is a stale case state being shown as current.
    "Cache-Control": "no-store",
}


def error_response(code: str, *, detail: dict[str, object] | None = None) -> JSONResponse:
    """One place builds an error body.

    Routed through ``AppError.to_body`` even for failures that were not raised as
    an ``AppError``, so a validation error and a domain error are the same shape on
    the wire and the frontend has one parser.
    """
    error = AppError(code, detail=detail)
    return JSONResponse(status_code=error.http_status, content=error.to_body())


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    if settings.enable_historical_blueprint:
        ctx = ServiceContext.build(settings)
        app.state.ctx = ctx
        app.state.custody_db = ctx.db
        app.state.custody_events = ctx.events
        # This service belongs only to the quarantined research controller.
        app.state.pairing = PairingService(ctx)
    else:
        app.state.custody_db = Database(settings.database_path)
        app.state.custody_events = EventBus()
    initialise_custody_schema(app.state.custody_db)
    logger.info(
        "handover29c started: build=%s policy=%s db=%s",
        settings.build_label,
        registry.get(settings.policy_version).version,
        settings.database_path,
    )
    yield


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or load_settings()
    app = FastAPI(
        title="Handover29C prototype API",
        # Stated in the OpenAPI description too, so even a machine-readable view of
        # this API carries the disclosure.
        description=(
            "Independent hackathon prototype. Simulated government integrations, "
            "fictional data. Does not connect to any government system and produces "
            "nothing with legal effect."
        ),
        version="1.0.2",
        lifespan=lifespan,
    )
    app.state.settings = resolved

    if resolved.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(resolved.cors_origins),
            allow_credentials=False,
            allow_methods=["GET", "POST", "PATCH"],
            allow_headers=["Content-Type", "Idempotency-Key", "X-Party-Token"],
        )

    @app.middleware("http")
    async def security_headers(request: Request, call_next):  # type: ignore[no-untyped-def]
        response = await call_next(request)
        for header, value in SECURITY_HEADERS.items():
            response.headers.setdefault(header, value)
        return response

    @app.exception_handler(AppError)
    async def handle_app_error(_request: Request, exc: AppError) -> JSONResponse:
        return error_response(exc.code, detail=exc.detail)

    @app.exception_handler(IllegalTransition)
    async def handle_illegal_transition(
        _request: Request, exc: IllegalTransition
    ) -> JSONResponse:
        # Logged with the edge because it means a service tried something the state
        # graph forbids -- a bug worth seeing in the logs, not just a 409.
        logger.warning("illegal transition %s -> %s", exc.source.value, exc.target.value)
        return error_response("INVALID_STATE", detail={"state": exc.source.value})

    @app.exception_handler(ConcurrentModification)
    async def handle_concurrent(
        _request: Request, _exc: ConcurrentModification
    ) -> JSONResponse:
        return error_response("INVALID_STATE", detail={"reason": "CONCURRENT_UPDATE"})

    @app.exception_handler(RequestValidationError)
    async def handle_validation(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # Field names only. Pydantic's messages can echo submitted values, and even
        # in a prototype that refuses personal data, reflecting input back is a habit
        # worth not having.
        fields = sorted(
            {".".join(str(p) for p in err["loc"][1:]) or "body" for err in exc.errors()}
        )
        return error_response("VALIDATION_ERROR", detail={"fields": fields})

    @app.exception_handler(StarletteHTTPException)
    async def handle_http(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
        if exc.status_code == 404:
            return error_response("CASE_NOT_FOUND", detail={"reason": "NO_SUCH_ROUTE"})
        if exc.status_code == 405:
            return error_response("VALIDATION_ERROR", detail={"reason": "BAD_METHOD"})
        return error_response("INTERNAL_ERROR")

    @app.exception_handler(Exception)
    async def handle_unexpected(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled error", exc_info=exc)
        return error_response("INTERNAL_ERROR")

    @app.get("/healthz")
    async def healthz(request: Request) -> dict[str, object]:
        """Liveness plus the facts a reviewer needs to trust the running build.

        ``policy_in_force`` is here so a deployment evaluating draft rules would be
        visible from outside the process rather than only in a log line.
        """
        settings: Settings = request.app.state.settings
        policy = registry.get(settings.policy_version)
        return {
            "status": "ok",
            "simulation": True,
            "build_label": settings.build_label,
            "policy_version": policy.version,
            "policy_in_force": policy.in_force,
            "live_government_integrations": 0,
        }

    if resolved.enable_historical_blueprint:
        app.include_router(router, prefix="/api/v1")
        app.include_router(ws_router)
    app.include_router(custody_router, prefix="/api/v1")

    if resolved.serve_frontend and resolved.frontend_dist.is_dir():
        # Mounted last so it cannot shadow /api or /ws. html=True serves index.html
        # for unknown paths, which is what makes a hard refresh on a deep link work
        # -- a requirement, since refresh-safety is a gate.
        app.mount(
            "/",
            StaticFiles(directory=resolved.frontend_dist, html=True),
            name="spa",
        )

    return app


app = create_app()

__all__ = ["CONTENT_SECURITY_POLICY", "SECURITY_HEADERS", "app", "create_app", "error_response"]
