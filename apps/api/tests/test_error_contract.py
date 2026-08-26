"""The error contract, asserted end to end.

``app/errors.py`` says of ``AppError.detail``: "It must never contain a pair token, a
session token, or a stack trace; ``tests/test_error_contract.py`` asserts the shape."
This is that file, and it asserts four things rather than one:

1.  **The catalogue is internally consistent** -- key matches code, status is a real
    HTTP status, both languages are present.
2.  **The wire shape is fixed.** One envelope, one key set. The frontend has a single
    parser (SRS section 12), and that is only true if nothing invents a second shape.
3.  **Every code is reachable, and every raised code exists.** Both directions. A
    catalogue entry with no raise site is a documented behaviour the product does not
    have; a raised code with no entry is a ``KeyError`` waiting for a user to find.
    The first direction is not hypothetical -- it is what removed ``NOT_PAIRED``,
    which had a message, a translation, and no code path.
4.  **Nothing sensitive leaks.** Checked statically on ``detail`` keys and then
    behaviourally, by provoking real failures through the services and inspecting
    the serialised body for the tokens involved.

The static scans work on the AST rather than on ``grep`` because three quarters of
the raise sites in this codebase span multiple lines; a line-oriented scan finds most
of them, which is the worst possible outcome for a completeness check.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app.config import REPO_ROOT
from app.domain.states import Actor
from app.errors import ERROR_CATALOGUE, AppError
from app.services.case_service import hash_token
from tests.conftest import Journey

APP_ROOT = REPO_ROOT / "apps" / "api" / "app"

#: The two places that legitimately pass a non-literal code, by enclosing function.
#:
#: ``error_response`` is the single funnel every handler routes through, and
#: ``handle_app_error`` re-raises a code that was already validated when the
#: ``AppError`` was constructed. Anywhere else, a computed code would defeat the
#: reachability scan below, so it is a failure rather than an exemption.
DYNAMIC_CODE_CALLERS = {"error_response", "handle_app_error"}


# ---------------------------------------------------------------------------
# the catalogue itself
# ---------------------------------------------------------------------------


def test_catalogue_is_not_empty() -> None:
    assert len(ERROR_CATALOGUE) >= 15


@pytest.mark.parametrize("code", sorted(ERROR_CATALOGUE))
def test_catalogue_entry_is_self_consistent(code: str) -> None:
    spec = ERROR_CATALOGUE[code]
    assert spec.code == code, "the dict key and the spec disagree"
    assert 400 <= spec.http_status <= 599, spec.http_status
    assert isinstance(spec.recoverable, bool)
    assert spec.message_en.strip()
    assert spec.message_hi.strip()


@pytest.mark.parametrize("code", sorted(ERROR_CATALOGUE))
def test_message_has_no_unfilled_placeholder(code: str) -> None:
    """Messages are static text, not templates.

    A ``{state}`` that never gets formatted would reach a user verbatim. The
    machine-readable part of an error lives in ``detail``, which is why the message
    never needs interpolation.
    """
    spec = ERROR_CATALOGUE[code]
    for message in (spec.message_en, spec.message_hi):
        assert "{" not in message, message
        assert "%s" not in message, message


def test_only_internal_error_is_a_server_error() -> None:
    """Everything else is the caller's situation, not the server falling over.

    Worth pinning: a 500 tells a client "retry, this was not your fault", and using
    it for a domain refusal would send exactly the wrong signal.
    """
    server_errors = {
        code for code, spec in ERROR_CATALOGUE.items() if spec.http_status >= 500
    }
    assert server_errors == {"INTERNAL_ERROR"}


def test_internal_error_leaks_nothing_and_reassures() -> None:
    """The generic handler's message is the one a real crash produces."""
    message = ERROR_CATALOGUE["INTERNAL_ERROR"].message_en
    assert "Nothing was submitted" in message
    for leak in ("Traceback", "File \"", ".py", "Exception", "sqlite", "app."):
        assert leak not in message, message


def test_unrecoverable_codes_are_the_dead_ends() -> None:
    """``recoverable`` is what the UI branches on, so it is pinned rather than assumed.

    These are the codes where "fix it and try again" is false: the journey is out of
    scope, the case does not exist for this client, the dealer cannot support the
    flow, this device is not a party, or the case is already finished.
    """
    unrecoverable = {
        code for code, spec in ERROR_CATALOGUE.items() if not spec.recoverable
    }
    assert unrecoverable == {
        "UNSUPPORTED_JOURNEY",
        "CASE_NOT_FOUND",
        "DEALER_NOT_ACTIVE",
        "UNAUTHORISED_ACTOR",
        "ALREADY_ACKNOWLEDGED",
    }


# ---------------------------------------------------------------------------
# the wire shape
# ---------------------------------------------------------------------------


def test_body_shape_without_detail() -> None:
    body = AppError("PREFLIGHT_BLOCKED").to_body()
    assert set(body) == {"error"}
    assert set(body["error"]) == {"code", "message", "message_hi", "recoverable"}
    assert body["error"]["code"] == "PREFLIGHT_BLOCKED"
    assert body["error"]["recoverable"] is True


def test_body_omits_detail_when_empty() -> None:
    """An empty ``detail`` is absent rather than ``{}``.

    So a client can test for presence instead of for emptiness, and the payload does
    not carry a key that means nothing.
    """
    assert "detail" not in AppError("INVALID_STATE").to_body()["error"]
    assert "detail" not in AppError("INVALID_STATE", detail={}).to_body()["error"]


def test_body_includes_detail_when_present() -> None:
    body = AppError("INVALID_STATE", detail={"state": "REVIEW_READY"}).to_body()
    assert body["error"]["detail"] == {"state": "REVIEW_READY"}
    assert set(body["error"]) == {
        "code", "message", "message_hi", "recoverable", "detail",
    }


def test_detail_defaults_to_a_dict_not_none() -> None:
    """``detail`` is always a mapping, so callers never branch on None."""
    assert AppError("RATE_LIMITED").detail == {}


def test_properties_delegate_to_the_spec() -> None:
    error = AppError("PAIR_CODE_EXPIRED")
    assert error.code == "PAIR_CODE_EXPIRED"
    assert error.http_status == 410
    assert error.spec.recoverable is True


def test_unknown_code_fails_loudly_with_guidance() -> None:
    """Not a silent fallback to INTERNAL_ERROR.

    A typo'd code is a programming error; converting it into a generic 500 would
    hide it in production and in the test suite alike.
    """
    with pytest.raises(KeyError, match="bilingual copy"):
        AppError("NO_SUCH_CODE_AT_ALL")


def test_str_of_an_apperror_carries_the_code() -> None:
    """Log lines need to identify the failure without a custom formatter."""
    assert "PAIR_CODE_INVALID" in str(AppError("PAIR_CODE_INVALID"))


# ---------------------------------------------------------------------------
# reachability, in both directions
# ---------------------------------------------------------------------------


def error_call_sites(path: Path) -> tuple[list[str], list[str]]:
    """(literal codes, offending non-literal call descriptions) for one module.

    Walks with the enclosing function name in hand so the two legitimate dynamic
    callers can be recognised without hard-coding line numbers.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    literals: list[str] = []
    dynamic: list[str] = []

    def visit(node: ast.AST, enclosing: str) -> None:
        current = enclosing
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            current = node.name
        if isinstance(node, ast.Call):
            target = node.func
            name = (
                target.id
                if isinstance(target, ast.Name)
                else target.attr
                if isinstance(target, ast.Attribute)
                else ""
            )
            if name in {"AppError", "error_response"}:
                first = node.args[0] if node.args else None
                if isinstance(first, ast.Constant) and isinstance(first.value, str):
                    literals.append(first.value)
                elif current not in DYNAMIC_CODE_CALLERS:
                    dynamic.append(
                        f"{path.name}:{node.lineno} {name}(...) in {current or '<module>'}() "
                        "does not pass a literal code"
                    )
        for child in ast.iter_child_nodes(node):
            visit(child, current)

    visit(tree, "")
    return literals, dynamic


APP_FILES = sorted(p for p in APP_ROOT.rglob("*.py") if "__pycache__" not in p.parts)
RAISED_CODES: set[str] = set()
DYNAMIC_OFFENCES: list[str] = []
for _path in APP_FILES:
    _literals, _dynamic = error_call_sites(_path)
    RAISED_CODES.update(_literals)
    DYNAMIC_OFFENCES.extend(_dynamic)


def test_the_scan_found_call_sites() -> None:
    assert len(RAISED_CODES) >= 15, sorted(RAISED_CODES)


def test_every_raised_code_exists_in_the_catalogue() -> None:
    """A typo here is a KeyError in front of a user, so it is caught at test time."""
    unknown = sorted(RAISED_CODES - set(ERROR_CATALOGUE))
    assert unknown == [], f"raised but not defined: {unknown}"


@pytest.mark.invariant
def test_every_catalogue_code_is_actually_reachable() -> None:
    """No documented error the product cannot produce.

    This is the direction that finds real drift: an error message is easy to add and
    easy to orphan, and an orphaned one is a claim about behaviour that does not
    exist. ``NOT_PAIRED`` was removed because of this test.
    """
    orphaned = sorted(set(ERROR_CATALOGUE) - RAISED_CODES)
    assert orphaned == [], (
        f"defined but never raised: {orphaned}. Either raise them where they belong "
        "or delete them; a message with no code path is documentation of a behaviour "
        "the product does not have."
    )


def test_no_module_passes_a_computed_error_code() -> None:
    """Otherwise the reachability scan above would be quietly incomplete."""
    assert DYNAMIC_OFFENCES == [], "\n".join(DYNAMIC_OFFENCES)


# ---------------------------------------------------------------------------
# nothing sensitive in detail
# ---------------------------------------------------------------------------

#: Substrings that must not appear as a ``detail`` key. Checked on keys only, because
#: a value's *expression* legitimately mentions a token -- the rate limiter computes
#: ``retry_after_seconds`` from a token hash while returning only an integer. The
#: behavioural tests below are what cover values.
#:
#: The scan matches every ``detail=`` keyword, which also catches the audit-event
#: details passed to ``refresh(...)``. That is deliberate: an audit row must not carry
#: a credential either, and the two share a key name and a JSON serialiser.
FORBIDDEN_DETAIL_KEYS = ("token", "secret", "password", "credential", "traceback")


def detail_keys(path: Path) -> list[tuple[int, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for keyword in node.keywords:
            if keyword.arg != "detail" or not isinstance(keyword.value, ast.Dict):
                continue
            for key in keyword.value.keys:
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    found.append((node.lineno, key.value))
    return found


@pytest.mark.invariant
@pytest.mark.parametrize("path", APP_FILES, ids=lambda p: p.name)
def test_no_detail_key_names_a_secret(path: Path) -> None:
    offences = [
        f"{path.name}:{lineno} detail key {key!r} contains {shape!r}"
        for lineno, key in detail_keys(path)
        for shape in FORBIDDEN_DETAIL_KEYS
        if shape in key.lower()
    ]
    assert offences == [], "\n".join(offences)


def serialised(error: AppError) -> str:
    import json

    return json.dumps(error.to_body(), ensure_ascii=False)


@pytest.mark.invariant
def test_an_unauthorised_actor_error_does_not_echo_the_token(journey: Journey) -> None:
    """The one error whose cause *is* a token, so the obvious mistake is to include it."""
    journey.to_review_ready()
    with pytest.raises(AppError) as caught:
        journey.confirmations.confirm(
            case_id=journey.case_id,
            token="not-a-real-token",
            payload_hash_claim=journey.payload_hash(),
        )

    body = serialised(caught.value)
    assert caught.value.code == "UNAUTHORISED_ACTOR"
    # Bare, not "expected <hash>": an unrecognised bearer token has nothing to say
    # back to whoever presented it, and a hint would only help someone guessing.
    assert caught.value.detail == {}
    assert "not-a-real-token" not in body
    assert hash_token("not-a-real-token") not in body
    assert journey.seller_token not in body
    assert journey.dealer_token not in body


@pytest.mark.invariant
def test_a_rate_limit_error_does_not_echo_the_pair_code(journey: Journey) -> None:
    """``RATE_LIMITED`` is keyed on a hashed code, and must return only a delay."""
    journey.to_preflight_passed()
    code = journey.pair()

    caught: AppError | None = None
    for _ in range(40):
        try:
            journey.pairing.redeem(code="000000", client_key="flooder")
        except AppError as error:
            if error.code == "RATE_LIMITED":
                caught = error
                break

    assert caught is not None, "the limiter never engaged; has the window changed?"
    body = serialised(caught)
    assert code not in body
    assert hash_token(code) not in body
    assert set(caught.detail) == {"retry_after_seconds"}
    assert isinstance(caught.detail["retry_after_seconds"], int)


@pytest.mark.invariant
def test_a_stale_payload_error_does_not_disclose_the_expected_hash(
    journey: Journey,
) -> None:
    """The client already has the current hash from the review payload.

    Echoing the expected value in an error would turn a mismatch report into an
    oracle, and it would put an internal hash on a user's screen -- which the UX bar
    forbids outside the developer drawer.
    """
    journey.to_review_ready()
    current = journey.payload_hash()

    with pytest.raises(AppError) as caught:
        journey.confirm(Actor.SELLER, payload_hash="0" * 64)

    assert caught.value.code == "STALE_PAYLOAD"
    assert current not in serialised(caught.value)


@pytest.mark.invariant
def test_an_unknown_dealer_echoes_nothing_and_credits_the_simulated_registry(
    journey: Journey,
) -> None:
    """Two properties in one place, because they fail together.

    The lookup miss carries no detail -- there is nothing about an unrecognised
    authorisation number worth reflecting back. And the message attributes the answer
    to the *simulated* registry, which is the sentence that keeps this prototype
    honest: no government system was asked anything.
    """
    journey.create()
    journey.verify_vehicle()
    with pytest.raises(AppError) as caught:
        journey.verify_dealer("DEMO-29B-999")

    assert caught.value.code == "DEALER_NOT_FOUND"
    assert caught.value.detail == {}
    body = serialised(caught.value)
    assert "simulated dealer registry" in body
    assert "sqlite" not in body.lower()
    assert "Traceback" not in body


# ---------------------------------------------------------------------------
# the same contract over HTTP
# ---------------------------------------------------------------------------


@pytest.mark.invariant
def test_an_unknown_route_uses_the_same_envelope(api) -> None:
    """Even a 404 from the framework comes back in the product's own shape."""
    response = api.get("/api/v1/no-such-thing")
    assert response.status_code == 404
    body = response.json()
    assert set(body) == {"error"}
    assert body["error"]["code"] == "CASE_NOT_FOUND"
    assert body["error"]["detail"] == {"reason": "NO_SUCH_ROUTE"}
    assert body["error"]["message_hi"]


@pytest.mark.invariant
def test_a_wrong_method_is_translated_rather_than_passed_through(api) -> None:
    """405 becomes the catalogue's VALIDATION_ERROR status, deliberately.

    One envelope and one status table beats mirroring every framework status: the
    client has a single parser, and ``detail.reason`` still says what happened.
    """
    response = api.get("/api/v1/cases")
    assert response.status_code == ERROR_CATALOGUE["VALIDATION_ERROR"].http_status
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["detail"] == {"reason": "BAD_METHOD"}


@pytest.mark.invariant
def test_a_validation_failure_reports_field_names_only(api) -> None:
    """Pydantic can echo submitted values; the handler reduces it to field names."""
    response = api.post("/api/v1/cases", json={"journey_type": 12345})
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "12345" not in response.text
    assert set(body["error"]["detail"]) == {"fields"}


@pytest.mark.invariant
def test_http_status_matches_the_catalogue_for_a_domain_refusal(api) -> None:
    """The private-buyer route, checked through the transport this time."""
    response = api.post(
        "/api/v1/cases", json={"journey_type": "PRIVATE_BUYER_TRANSFER"}
    )
    spec = ERROR_CATALOGUE["UNSUPPORTED_JOURNEY"]
    assert response.status_code == spec.http_status
    body = response.json()["error"]
    assert body["code"] == "UNSUPPORTED_JOURNEY"
    assert body["message"] == spec.message_en
    assert body["message_hi"] == spec.message_hi
    assert body["recoverable"] is False


@pytest.mark.invariant
def test_error_responses_are_not_cached(api) -> None:
    """A cached 409 would show a stale refusal after the user fixed the cause."""
    response = api.post(
        "/api/v1/cases", json={"journey_type": "PRIVATE_BUYER_TRANSFER"}
    )
    assert response.headers["cache-control"] == "no-store"
