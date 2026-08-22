"""Runtime configuration.

Two rules shape this module:

1.  Nothing here can select the draft 2026 policy. ``policy_version`` is read
    through ``app.domain.policies.registry``, which refuses anything not in force,
    so even a bad environment variable cannot make draft rules execute.
2.  There is no configuration key for a government endpoint, API key, or
    credential, because there is no code path that would use one. The absence is
    deliberate and is asserted by ``tests/test_no_live_integration.py``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .domain.policies import registry

#: Repository root, derived by walking up from this file (apps/api/app/config.py).
REPO_ROOT = Path(__file__).resolve().parents[3]


def _env_str(name: str, default: str) -> str:
    value = os.environ.get(name, "").strip()
    return value or default


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError as exc:  # pragma: no cover - configuration error
        raise ValueError(f"{name} must be an integer, got {raw!r}") from exc


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default
    if raw in {"1", "true", "yes", "on"}:
        return True
    if raw in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be a boolean-ish value, got {raw!r}")


def _env_list(name: str, default: tuple[str, ...]) -> tuple[str, ...]:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    return tuple(part.strip() for part in raw.split(",") if part.strip())


@dataclass(frozen=True, slots=True)
class Settings:
    #: SQLite file. ``":memory:"`` is rejected by ``Database.__init__``, including in
    #: tests: that module opens a connection per transaction, so an in-memory
    #: database would be empty on every call. Tests use a tmp_path file, which also
    #: exercises the refresh-safety the product promises across a process restart.
    database_path: str

    #: Policy version the running instance evaluates against. Validated in
    #: __post_init__ via the registry, which only knows in-force policies.
    policy_version: str

    #: Pair-token lifetime. SRS section 8 sets the default at 5 minutes.
    pair_token_ttl_seconds: int

    #: Bytes of OS entropy per pair token. SRS section 8 requires >= 16 (128 bits)
    #: and prefers more; 32 bytes = 256 bits.
    pair_token_bytes: int

    #: Origins allowed to call the API. Empty tuple means same-origin only, which
    #: is the deployed configuration (the SPA is served by this app).
    cors_origins: tuple[str, ...]

    #: Emitted in the health payload and the source drawer so a reviewer can see
    #: which build they are looking at.
    build_label: str

    #: Seconds the client should wait between REST polls when the WebSocket is
    #: unavailable. Sent to the client so the fallback interval is server-owned.
    poll_interval_seconds: float

    #: When true the API serves the built SPA from apps/web/dist.
    serve_frontend: bool

    #: Artificial latency for the simulated adapter, in milliseconds. Exists so
    #: the "submitting" state is visible in a demo; it is not a network call.
    simulated_adapter_latency_ms: int

    #: Keeps the superseded ACK-only research controller available to its
    #: regression suite without exposing it from the shipped application.
    #: Production/default runtime must present only the four-state custody API.
    enable_historical_blueprint: bool = False

    def __post_init__(self) -> None:
        # Raises PolicyNotSelectable for an unknown or not-in-force version. This
        # runs at import time of the app, so a misconfigured deployment fails to
        # start rather than silently evaluating the wrong rules.
        if self.enable_historical_blueprint:
            registry.get(self.policy_version)
        if self.pair_token_bytes < 16:
            raise ValueError(
                "pair_token_bytes must be at least 16 (128 bits) per SRS section 8"
            )
        if self.pair_token_ttl_seconds <= 0:
            raise ValueError("pair_token_ttl_seconds must be positive")

    @property
    def frontend_dist(self) -> Path:
        return REPO_ROOT / "apps" / "web" / "dist"


def load_settings() -> Settings:
    default_db = str(REPO_ROOT / "var" / "identity-rescue.sqlite3")
    return Settings(
        database_path=_env_str("IR_DATABASE_PATH", default_db),
        policy_version=_env_str("H29C_POLICY_VERSION", registry.CURRENT_POLICY_VERSION),
        pair_token_ttl_seconds=_env_int("H29C_PAIR_TOKEN_TTL_SECONDS", 300),
        pair_token_bytes=_env_int("H29C_PAIR_TOKEN_BYTES", 32),
        cors_origins=_env_list("IR_CORS_ORIGINS", ()),
        build_label=_env_str("IR_BUILD_LABEL", "dev"),
        poll_interval_seconds=float(_env_int("H29C_POLL_INTERVAL_MS", 2000)) / 1000.0,
        serve_frontend=_env_bool("IR_SERVE_FRONTEND", False),
        simulated_adapter_latency_ms=_env_int("H29C_SIM_LATENCY_MS", 600),
    )
