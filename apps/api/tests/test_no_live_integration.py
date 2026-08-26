"""No live integration exists, and this is where that is proven.

``app/config.py`` states the rule it is asserting: "There is no configuration key for
a government endpoint, API key, or credential, because there is no code path that
would use one. The absence is deliberate and is asserted by
``tests/test_no_live_integration.py``."

Absence is the hardest property to test, because nothing fails when it holds. So
this file attacks it from five directions, each of which would independently have to
be defeated for a live call to appear:

1.  **No outbound client is imported.** A module that cannot reach the network
    cannot call a government system by accident.
2.  **No URL is written down.** Not in a constant, not in a fixture, not in a
    default. A simulated adapter with a base URL is one code change away from being
    a real one.
3.  **No configuration key would carry one.** No endpoint, host, key, secret or
    credential field on ``Settings``; no environment variable named like one.
4.  **No HTTP client is a runtime dependency.** ``httpx`` is in
    requirements-dev.txt for ``TestClient`` and is deliberately absent from the
    runtime file, so the deployed image cannot make one.
5.  **The running process says so.** ``/healthz`` reports
    ``live_government_integrations: 0``, which is a claim a reviewer can check from
    outside the process without reading any of this.

The honesty requirement this serves is not a nice-to-have: "Never call a live
government system" is one of the non-negotiables, and a hackathon prototype that
merely *intends* not to is indistinguishable from one that does until it does.
"""

from __future__ import annotations

import ast
import re
from dataclasses import fields
from pathlib import Path

import pytest

from app.config import REPO_ROOT, Settings, load_settings

API_ROOT = REPO_ROOT / "apps" / "api"
APP_ROOT = API_ROOT / "app"
FIXTURE_ROOT = REPO_ROOT / "fixtures"

#: Import paths that can open a connection. Matched as dotted prefixes, so
#: ``urllib.parse`` (pure string handling) stays legal while ``urllib.request`` does
#: not, and ``from http import HTTPStatus`` stays legal while ``http.client`` does not.
FORBIDDEN_IMPORT_PREFIXES: tuple[str, ...] = (
    "requests",
    "httpx",
    "aiohttp",
    "urllib3",
    "urllib.request",
    "urllib.error",
    "http.client",
    "socket",
    "socketserver",
    "ssl",
    "ftplib",
    "smtplib",
    "poplib",
    "imaplib",
    "telnetlib",
    "xmlrpc",
    "websockets",
    "websocket",
    "paramiko",
    "boto3",
    "botocore",
    "grpc",
    "pycurl",
    "pika",
    "kafka",
    "redis",
    "pymongo",
    "psycopg",
    "psycopg2",
    "asyncpg",
    "MySQLdb",
    "pymysql",
)

#: Substrings that would betray a credential- or endpoint-shaped name.
#:
#: ``TOKEN`` is deliberately absent: ``pair_token_ttl_seconds`` and
#: ``pair_token_bytes`` are the *local* pairing token's parameters, which have nothing
#: to do with an upstream credential. Banning the word would ban the honest use.
CREDENTIAL_SHAPED = (
    "api_key",
    "apikey",
    "secret",
    "password",
    "passwd",
    "credential",
    "endpoint",
    "base_url",
    "upstream",
    "gateway",
    "client_id",
    "certificate",
    "private_key",
)


def source_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.py") if "__pycache__" not in p.parts)


APP_FILES = source_files(APP_ROOT)


def imported_modules(path: Path) -> list[tuple[int, str]]:
    """Every module path a file imports, as (line, dotted name).

    ``from x.y import z`` yields both ``x.y`` and ``x.y.z``: the first catches
    ``from urllib import request``-style access to a forbidden submodule, the second
    catches ``from urllib.request import urlopen``.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend((node.lineno, alias.name) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:  # relative import, cannot be a third-party client
                continue
            module = node.module or ""
            found.append((node.lineno, module))
            found.extend(
                (node.lineno, f"{module}.{alias.name}") for alias in node.names
            )
    return found


def forbidden(dotted: str) -> str | None:
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        if dotted == prefix or dotted.startswith(prefix + "."):
            return prefix
    return None


# ---------------------------------------------------------------------------
# 1. nothing can reach the network
# ---------------------------------------------------------------------------


def test_there_are_files_to_check() -> None:
    assert len(APP_FILES) >= 20, f"only found {len(APP_FILES)} modules under {APP_ROOT}"


@pytest.mark.invariant
@pytest.mark.parametrize("path", APP_FILES, ids=lambda p: p.name)
def test_module_imports_no_outbound_client(path: Path) -> None:
    offences = [
        f"{path.name}:{lineno} imports {dotted} (matches forbidden prefix {hit!r})"
        for lineno, dotted in imported_modules(path)
        if (hit := forbidden(dotted))
    ]
    assert offences == [], "\n".join(offences)


@pytest.mark.invariant
def test_the_import_scanner_bites(tmp_path: Path) -> None:
    """Proves the check is capable of failing before trusting that it passed."""
    probe = tmp_path / "probe.py"
    probe.write_text(
        "import httpx\n"
        "from urllib.request import urlopen\n"
        "from urllib.parse import quote\n"
        "from http import HTTPStatus\n",
        encoding="utf-8",
    )
    hits = {dotted for _, dotted in imported_modules(probe) if forbidden(dotted)}
    assert "httpx" in hits
    assert any(h.startswith("urllib.request") for h in hits)
    # The legal neighbours must not be caught, or the rule is unusable.
    assert not any(h.startswith("urllib.parse") for h in hits)
    assert "http.HTTPStatus" not in hits


@pytest.mark.invariant
def test_the_simulated_adapter_is_the_only_submission_path() -> None:
    """The adapter is where a live call would be tempting, so it is named directly.

    Asserted as a property of the module rather than of the class: an import that
    could reach a government system is a defect even on a code path nobody calls.
    """
    adapter = APP_ROOT / "adapters" / "mock_form29c_adapter.py"
    assert adapter.is_file(), adapter
    offences = [
        f"{lineno}: {dotted}"
        for lineno, dotted in imported_modules(adapter)
        if forbidden(dotted)
    ]
    assert offences == [], "\n".join(offences)


# ---------------------------------------------------------------------------
# 2. no URL is written down
# ---------------------------------------------------------------------------

#: URL-ish text that is legitimate: loopback for a local dev server, and the two
#: schemes as bare words inside prose. Anything else is a host somebody could call.
ALLOWED_URL_SUBSTRINGS = ("http://localhost", "http://127.0.0.1")


def non_docstring_strings(path: Path) -> list[tuple[int, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(
            node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            body = getattr(node, "body", None)
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                docstrings.add(id(body[0].value))
    return [
        (node.lineno, node.value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in docstrings
    ]


@pytest.mark.invariant
@pytest.mark.parametrize("path", APP_FILES, ids=lambda p: p.name)
def test_no_remote_url_in_source(path: Path) -> None:
    offences: list[str] = []
    for lineno, text in non_docstring_strings(path):
        for match in re.finditer(r"https?://[^\s'\"]*", text):
            url = match.group(0)
            if any(url.startswith(allowed) for allowed in ALLOWED_URL_SUBSTRINGS):
                continue
            offences.append(f"{path.name}:{lineno} contains {url!r}")
    assert offences == [], "\n".join(offences)


@pytest.mark.invariant
def test_no_remote_url_in_fixtures() -> None:
    """Fixtures are the other place a "source URL" field tends to appear."""
    offences = [
        f"{path.name}:{lineno} contains {match.group(0)!r}"
        for path in sorted(FIXTURE_ROOT.glob("*.json"))
        for lineno, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        )
        for match in re.finditer(r"https?://[^\s'\"]*", line)
    ]
    assert offences == [], "\n".join(offences)


# ---------------------------------------------------------------------------
# 3. no configuration key would carry one
# ---------------------------------------------------------------------------


@pytest.mark.invariant
def test_settings_has_no_credential_or_endpoint_field() -> None:
    names = [f.name for f in fields(Settings)]
    offences = [
        f"Settings.{name} looks like {shape!r}"
        for name in names
        for shape in CREDENTIAL_SHAPED
        if shape in name.lower()
    ]
    assert offences == [], "\n".join(offences)


@pytest.mark.invariant
def test_settings_field_set_is_the_documented_one() -> None:
    """Pins the shape, so a new field is a deliberate decision with a failing test.

    Without this the previous test only forbids *badly named* additions; a field
    called ``partner_ref`` holding a URL would sail through.
    """
    assert {f.name for f in fields(Settings)} == {
        "database_path",
        "policy_version",
        "pair_token_ttl_seconds",
        "pair_token_bytes",
        "cors_origins",
        "build_label",
        "poll_interval_seconds",
        "serve_frontend",
        "simulated_adapter_latency_ms",
        "enable_historical_blueprint",
    }


@pytest.mark.invariant
def test_environment_variables_are_namespaced_and_harmless() -> None:
    """Every env var the app reads, extracted from the source of config.py.

    Read the literal names passed to the module's typed environment helpers. The
    helpers intentionally call ``os.environ.get(name)`` with a variable, so
    looking only for literals on the low-level call would always find nothing.
    """
    config_source = APP_ROOT / "config.py"
    tree = ast.parse(config_source.read_text(encoding="utf-8"))

    read_names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        target = node.func
        if not isinstance(target, ast.Name) or target.id not in {
            "_env_str",
            "_env_int",
            "_env_bool",
            "_env_list",
        }:
            continue
        if node.args and isinstance(node.args[0], ast.Constant):
            value = node.args[0].value
            if isinstance(value, str):
                read_names.add(value)

    assert read_names, "no literal environment-helper call found; has config.py changed?"

    banned = ("URL", "ENDPOINT", "HOST", "API_KEY", "SECRET", "PASSWORD",
              "CREDENTIAL", "CERT", "AADHAAR", "PAN")
    for name in sorted(read_names):
        assert name.startswith("H29C_"), f"{name} is not namespaced"
        for shape in banned:
            assert shape not in name, f"{name} contains {shape}"


@pytest.mark.invariant
def test_default_settings_are_local_and_same_origin(monkeypatch: pytest.MonkeyPatch) -> None:
    """With a clean environment the app is local-only.

    CORS defaults to same-origin rather than ``*``: the deployed SPA is served by
    this app, so a permissive default would buy nothing and widen the surface.
    """
    for name in (
        "H29C_DATABASE_PATH",
        "H29C_POLICY_VERSION",
        "H29C_PAIR_TOKEN_TTL_SECONDS",
        "H29C_PAIR_TOKEN_BYTES",
        "H29C_CORS_ORIGINS",
        "H29C_BUILD_LABEL",
        "H29C_POLL_INTERVAL_MS",
        "H29C_SERVE_FRONTEND",
        "H29C_SIM_LATENCY_MS",
    ):
        monkeypatch.delenv(name, raising=False)

    settings = load_settings()
    assert settings.cors_origins == ()
    assert "*" not in settings.cors_origins
    assert not settings.database_path.startswith(("http", "postgres", "mysql"))
    assert Path(settings.database_path).is_absolute()


# ---------------------------------------------------------------------------
# 4. the runtime dependency set cannot make a call
# ---------------------------------------------------------------------------

#: Packages that exist to make outbound requests. ``httpx`` belongs to the dev file
#: only, because Starlette's TestClient needs it; shipping it would put a working
#: HTTP client inside the deployed image for no runtime reason.
HTTP_CLIENT_PACKAGES = ("requests", "httpx", "aiohttp", "urllib3", "pycurl", "grpcio")


def requirement_names(path: Path) -> list[str]:
    names: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        names.append(re.split(r"[<>=!\[~;]", line, maxsplit=1)[0].strip().lower())
    return names


@pytest.mark.invariant
def test_runtime_requirements_contain_no_http_client() -> None:
    runtime = requirement_names(API_ROOT / "requirements.txt")
    assert runtime, "requirements.txt parsed to nothing"
    offences = [name for name in runtime if name in HTTP_CLIENT_PACKAGES]
    assert offences == [], (
        f"{offences} would put an outbound HTTP client in the deployed image"
    )


@pytest.mark.invariant
def test_runtime_dependency_set_is_the_documented_four() -> None:
    """The runtime surface stays limited to the four documented dependencies."""
    assert set(requirement_names(API_ROOT / "requirements.txt")) == {
        "fastapi",
        "pydantic",
        "reportlab",
        "uvicorn",
    }


@pytest.mark.invariant
def test_the_test_client_dependency_is_dev_only() -> None:
    """Confirms the split is real rather than accidental.

    If httpx ever migrates into requirements.txt, the previous test fails and this
    one explains why it was there.
    """
    dev = requirement_names(API_ROOT / "requirements-dev.txt")
    assert "httpx" in dev, "TestClient needs httpx; it must be declared somewhere"
    assert "httpx" not in requirement_names(API_ROOT / "requirements.txt")


# ---------------------------------------------------------------------------
# 5. the running process says so
# ---------------------------------------------------------------------------


@pytest.mark.invariant
def test_health_endpoint_declares_zero_live_integrations(api) -> None:
    """The externally checkable version of everything above."""
    response = api.get("/healthz")
    assert response.status_code == 200
    body = response.json()
    assert body["live_government_integrations"] == 0
    assert body["simulation"] is True
    assert body["policy_in_force"] is True


@pytest.mark.invariant
def test_meta_endpoint_declares_simulation(api) -> None:
    response = api.get("/api/v1/meta")
    assert response.status_code == 200
    assert response.json()["simulation"] is True


@pytest.mark.invariant
def test_security_headers_disable_the_capabilities_we_do_not_use(api) -> None:
    """Location, camera and microphone are switched off in a header.

    Relevant here because "no GPS" is a product claim: a Permissions-Policy that
    denies geolocation is the version of that claim a reviewer can verify with curl.
    """
    response = api.get("/healthz")
    policy = response.headers["permissions-policy"]
    for capability in ("geolocation", "camera", "microphone", "payment"):
        assert f"{capability}=()" in policy, policy
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["referrer-policy"] == "no-referrer"
