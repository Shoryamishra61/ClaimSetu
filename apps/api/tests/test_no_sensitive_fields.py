"""The absence of a personal-data field, asserted rather than promised.

``app/api/schemas.py`` claims it: "No request model has a name, address, phone,
Aadhaar, PAN, OTP, password or payment field, because the product has no use for
one." This file is what makes that claim checkable, and it checks four surfaces,
because "we do not collect that" is only true if it is true at every one of them:

1.  **What the API accepts.** Every request body is a ``StrictModel``, so an
    invented field is a 422 rather than a silently ignored key.
2.  **What the route signatures accept.** A body parameter that is not a model
    escapes ``extra="forbid"`` entirely -- ``Body(embed=True)`` on a bare scalar
    accepts and discards any sibling key. There is exactly one way in.
3.  **What the generated OpenAPI document advertises.** The published input surface
    and the code cannot drift, because this is generated from that code.
4.  **What the database can hold.** The strongest of the four: a column that does
    not exist cannot be filled in later by a well-meaning patch.

**Why identifiers and not text.** A ``grep`` for "aadhaar" over this codebase hits
seven lines, and every one of them is a docstring or a user-facing warning saying
the product refuses it -- including the warning copy in ``app/copy.py`` that
``tests/test_copy_lint.py`` requires to exist. A text scan would therefore flag the
evidence that the property holds. So this file scans *names*: model fields, handler
parameters, OpenAPI properties, SQL columns. Prose is left to the copy lint.

**The one exception, stated plainly.** The product displays one personal-shaped
value: ``registered_owner_name``. It is output only -- it comes from
``fixtures/vehicles.json``, where every value is suffixed ``(fictional)``, no route
accepts it, and there is no column for it. Section E pins all three of those.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel

from app.api import schemas
from app.config import REPO_ROOT, Settings
from app.main import create_app

APP_ROOT = REPO_ROOT / "apps" / "api" / "app"
SCHEMA_SQL = APP_ROOT / "db" / "schema.sql"
FIXTURE_ROOT = REPO_ROOT / "fixtures"
API_PREFIX = "/api/v1"

#: Identifier fragments that would mean the product had started handling personal
#: or credential data. Word-bounded where the bare word is a common substring:
#: ``pan`` matches "panel" and "expand", ``dob`` matches nothing here but would
#: match "dobule" in a typo, and a lint that cries wolf gets deleted.
#:
#: Deliberately *not* on this list: ``name``. ``business_name`` and ``make_model``
#: are how a vehicle and a dealership are described, and banning the word would
#: force worse names. The personal-name forms are banned individually instead.
SENSITIVE_IDENTIFIER = re.compile(
    r"""
    aadhaar | aadhar | \buid\b | uidai
    | \bpan\b | pan_no | pan_number
    | \botp\b | passw | \bpin\b | pin_code | pincode
    | \bdl_no\b | driving_licen
    | first_name | last_name | full_name | middle_name | father | applicant_name
    | \bphone\b | mobile_no | \bmobile\b | contact_no | \bemail\b | whatsapp
    | \baddress\b | address_ | _address | street | locality | \bdistrict\b
    | \bdob\b | date_of_birth | \bage\b | \bgender\b
    | biometric | fingerprint | \bface\b | selfie | liveness | \bphoto\b
    | latitude | longitude | \bgps\b | geoloc | \bcoords?\b | accuracy_m
    | \bupi\b | upi_ | _upi | \bifsc\b | account_no | card_no | \bcvv\b | \biban\b
    | amount_paid | \bprice\b | \bpayment\b | payment_ | _payment | \bescrow\b
    """,
    re.VERBOSE | re.IGNORECASE,
)

#: Annotations a route handler may carry that are not request bodies: the framework
#: objects, path parameters (always ``str`` here), and the header aliases.
FRAMEWORK_ANNOTATIONS = frozenset(
    {"Request", "Response", "WebSocket", "str", "PartyToken", "ServiceContext"}
)


def request_models() -> dict[str, type[BaseModel]]:
    """Every concrete request model, by class name."""
    return {
        name: obj
        for name, obj in vars(schemas).items()
        if isinstance(obj, type)
        and issubclass(obj, BaseModel)
        and obj not in (BaseModel, schemas.StrictModel)
    }


MODELS = request_models()
MODEL_NAMES = frozenset(MODELS)


# ---------------------------------------------------------------------------
# A. what the API accepts
# ---------------------------------------------------------------------------


def test_there_are_models_to_check() -> None:
    """A scan that found nothing would pass every test below it."""
    assert len(MODELS) >= 6, f"only found {sorted(MODELS)}"


def test_the_module_exports_exactly_what_it_defines() -> None:
    """``__all__`` drifting from the module is how a model escapes review.

    Every model is listed, and nothing is listed that does not exist -- so the
    parametrised tests below genuinely cover the whole request surface.
    """
    exported = set(schemas.__all__)
    assert exported == MODEL_NAMES | {"StrictModel"}, (
        f"__all__ says {sorted(exported)}; module defines {sorted(MODEL_NAMES)}"
    )


@pytest.mark.parametrize("name", sorted(MODEL_NAMES))
def test_every_request_model_is_strict(name: str) -> None:
    """Inheriting ``StrictModel`` is the whole mechanism, so it is not optional.

    A plain ``BaseModel`` would accept and ignore any extra key, which is exactly
    how a field nobody agreed to ends up being sent for months before anyone reads
    the server code and finds it was never stored.
    """
    model = MODELS[name]
    assert issubclass(model, schemas.StrictModel), f"{name} is not a StrictModel"
    assert model.model_config.get("extra") == "forbid", (
        f"{name} does not forbid unknown keys"
    )


@pytest.mark.invariant
@pytest.mark.parametrize("name", sorted(MODEL_NAMES))
def test_no_request_field_names_personal_data(name: str) -> None:
    offences = [
        field for field in MODELS[name].model_fields if SENSITIVE_IDENTIFIER.search(field)
    ]
    assert offences == [], f"{name} accepts {offences}"


def test_the_pattern_would_actually_catch_something() -> None:
    """Pins the guard itself.

    A regex with a stray character class can quietly stop matching, and an absence
    test that cannot fail is worse than no test: it reports a property nobody
    checked. The negative cases are the real field names in this codebase, so a
    future tightening of the pattern cannot pass by banning them.
    """
    for bad in (
        "aadhaar_no",
        "pan",
        "otp",
        "password",
        "applicant_full_name",
        "phone",
        "address_line1",
        "latitude",
        "upi_id",
        "payment_ref",
        "selfie",
    ):
        assert SENSITIVE_IDENTIFIER.search(bad), f"pattern missed {bad}"

    for good in (
        "registration_no",
        "chassis_suffix",
        "authorisation_no",
        "business_name",
        "registered_owner_name",
        "make_model",
        "payload_hash",
        "token_hash",
        "acknowledgement_no",
        "idempotency_key",
        "policy_version",
        "handover_local_time",
        "expand_panel",
        "company",
    ):
        assert not SENSITIVE_IDENTIFIER.search(good), f"pattern false-positives on {good}"


# ---------------------------------------------------------------------------
# B. what the route signatures accept
# ---------------------------------------------------------------------------


def route_handlers(path: Path) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    """Decorated handlers only -- helpers are not part of the input surface."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    handlers: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            target = decorator.func if isinstance(decorator, ast.Call) else decorator
            if (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id.endswith("router")
            ):
                handlers.append(node)
                break
    return handlers


TRANSPORT_FILES = [APP_ROOT / "api" / "routes.py", APP_ROOT / "api" / "websocket.py"]
HANDLERS = [(path, node) for path in TRANSPORT_FILES for node in route_handlers(path)]


def test_the_handler_scan_found_the_routes() -> None:
    assert len(HANDLERS) >= 20, f"found only {len(HANDLERS)} decorated handlers"


@pytest.mark.invariant
@pytest.mark.parametrize(("path", "node"), HANDLERS, ids=lambda v: v.name)
def test_every_handler_body_is_a_strict_model(
    path: Path, node: ast.FunctionDef | ast.AsyncFunctionDef
) -> None:
    """The one way in.

    A parameter annotated with a bare class name is either a framework object, a
    path parameter, or a request body. If it is a request body it must be one of
    the strict models, because that is the only annotation that carries
    ``extra="forbid"``.
    """
    offences: list[str] = []
    for argument in [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]:
        annotation = argument.annotation
        if not isinstance(annotation, ast.Name):
            # Annotated[...] -- a header or query alias, checked below.
            continue
        if annotation.id in FRAMEWORK_ANNOTATIONS or annotation.id in MODEL_NAMES:
            continue
        offences.append(f"{node.name}({argument.arg}: {annotation.id})")
    assert offences == [], (
        f"{path.name}: unrecognised parameter type(s) {offences}. A request body must "
        f"be one of {sorted(MODEL_NAMES)}."
    )


@pytest.mark.invariant
@pytest.mark.parametrize("path", TRANSPORT_FILES, ids=lambda p: p.name)
def test_no_route_takes_an_embedded_scalar_body(path: Path) -> None:
    """``Body(embed=True)`` is the loophole in the rule above.

    ``authorisation_no: Annotated[str, Body(embed=True)]`` produces the same wire
    shape as a one-field model -- and accepts, then discards, any other key sent
    alongside it, because there is no model to forbid extras. It was written that
    way once in this codebase and replaced with ``DealerVerifyRequest`` for exactly
    this reason.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    offences = [
        f"{path.name}:{node.lineno} uses Body(...)"
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "Body"
    ]
    assert offences == [], "\n".join(offences)


@pytest.mark.parametrize(("path", "node"), HANDLERS, ids=lambda v: v.name)
def test_no_handler_parameter_names_personal_data(
    path: Path, node: ast.FunctionDef | ast.AsyncFunctionDef
) -> None:
    """Covers header and query parameters, which no model validates."""
    offences = [
        argument.arg
        for argument in [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
        if SENSITIVE_IDENTIFIER.search(argument.arg)
    ]
    assert offences == [], f"{path.name}:{node.name} takes {offences}"


# ---------------------------------------------------------------------------
# C. what the generated document advertises
# ---------------------------------------------------------------------------


@pytest.fixture
def openapi(settings: Settings) -> dict[str, Any]:
    """The published input surface, generated from the code that serves it.

    Worth checking separately from the models: this is what a client library is
    generated from, so a field that appears here has effectively been published
    whether or not any handler reads it. No lifespan needed -- schema generation
    touches neither the database nor an adapter.
    """
    return create_app(settings).openapi()


def collect_property_names(node: Any, found: set[str]) -> None:
    """Every key under every ``properties`` object, at any depth."""
    if isinstance(node, dict):
        properties = node.get("properties")
        if isinstance(properties, dict):
            found.update(properties)
        for value in node.values():
            collect_property_names(value, found)
    elif isinstance(node, list):
        for value in node:
            collect_property_names(value, found)


@pytest.mark.invariant
def test_the_published_input_surface_names_no_personal_data(
    openapi: dict[str, Any],
) -> None:
    names: set[str] = set()
    collect_property_names(openapi, names)
    assert names, "no properties found in the OpenAPI document"
    offences = sorted(name for name in names if SENSITIVE_IDENTIFIER.search(name))
    assert offences == [], f"OpenAPI advertises {offences}"


def test_every_published_body_schema_forbids_extra_properties(
    openapi: dict[str, Any],
) -> None:
    """``extra="forbid"`` is expected to reach the document, not just the runtime.

    If it stops appearing here, a generated client will happily send the extra key
    and the 422 will look like a server bug to whoever hits it.
    """
    components = openapi.get("components", {}).get("schemas", {})
    published = {name: schema for name, schema in components.items() if name in MODEL_NAMES}
    assert published, f"none of {sorted(MODEL_NAMES)} reached the document"
    lax = sorted(
        name
        for name, schema in published.items()
        if schema.get("additionalProperties") is not False
    )
    assert lax == [], f"these schemas accept extra properties: {lax}"


def test_the_document_publishes_every_model() -> None:
    """Guards the test above against passing on a subset.

    Asserted against the route signatures rather than the document, so a model that
    is defined but wired to nothing is caught here instead of silently reducing the
    coverage of the check above.
    """
    referenced = {
        annotation.id
        for _path, node in HANDLERS
        for argument in [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
        if isinstance((annotation := argument.annotation), ast.Name)
        and annotation.id in MODEL_NAMES
    }
    assert referenced == MODEL_NAMES, (
        f"defined but never accepted by any route: {sorted(MODEL_NAMES - referenced)}"
    )


# ---------------------------------------------------------------------------
# D. what the database can hold
# ---------------------------------------------------------------------------

COLUMN = re.compile(r"^\s+([a-z_][a-z0-9_]*)\s+(TEXT|INTEGER|REAL|BLOB|NUMERIC)\b")
TABLE = re.compile(r"CREATE TABLE IF NOT EXISTS (\w+)")


def schema_columns() -> dict[str, list[str]]:
    """Table name -> column names, parsed from the DDL."""
    tables: dict[str, list[str]] = {}
    current = ""
    for line in SCHEMA_SQL.read_text(encoding="utf-8").splitlines():
        if match := TABLE.search(line):
            current = match.group(1)
            tables[current] = []
            continue
        if not current or line.lstrip().startswith("--"):
            continue
        if match := COLUMN.match(line):
            tables[current].append(match.group(1))
        if line.startswith(")"):
            current = ""
    return tables


COLUMNS = schema_columns()


def test_the_ddl_parser_found_the_tables() -> None:
    assert set(COLUMNS) == {
        "cases",
        "declarations",
        "pair_sessions",
        "party_sessions",
        "submission_attempts",
        "audit_events",
    }, sorted(COLUMNS)
    for table, columns in COLUMNS.items():
        assert columns, f"parsed no columns for {table}"


@pytest.mark.invariant
@pytest.mark.parametrize("table", sorted(COLUMNS))
def test_no_column_can_hold_personal_data(table: str) -> None:
    """The strongest of the four surfaces.

    An API field can be added in one line; a column has to be migrated, which means
    someone has to notice. The prototype stores a fixture *id* and reads the
    fictional record through the registry adapter on every request, so there is no
    row anywhere that a real person's details could be written into.
    """
    offences = [c for c in COLUMNS[table] if SENSITIVE_IDENTIFIER.search(c)]
    assert offences == [], f"{table} has column(s) {offences}"


@pytest.mark.invariant
def test_no_credential_is_stored_in_the_clear() -> None:
    """Pair codes and party tokens exist only as SHA-256 digests.

    A column literally named ``token`` or ``code`` on a session table would mean the
    database held a usable credential, which is the one thing the hashing in
    ``case_service.hash_token`` exists to prevent.
    """
    for table in ("pair_sessions", "party_sessions"):
        columns = COLUMNS[table]
        assert "token_hash" in columns, f"{table} does not store a hash"
        for forbidden in ("token", "code", "secret", "plaintext"):
            assert forbidden not in columns, f"{table} stores a raw {forbidden}"


def test_the_case_row_holds_no_name_at_all() -> None:
    """Not even the fictional one.

    ``registered_owner_name`` is resolved from the vehicle fixture at read time. A
    stored copy would be a second source of truth for a value the fixture already
    owns, and the first thing anyone would do with it is put a real name there.
    """
    assert [c for c in COLUMNS["cases"] if c.endswith("_name")] == []
    assert "vehicle_id" in COLUMNS["cases"], "the case must reference the fixture by id"


# ---------------------------------------------------------------------------
# E. the one personal-shaped value that does exist
# ---------------------------------------------------------------------------


def test_every_owner_name_in_the_fixture_says_it_is_fictional() -> None:
    """The mitigation for displaying a name at all.

    ``test_copy_lint.py`` already requires every registration to start ``DEMO`` and
    every authorisation ``DEMO-``. The owner name is the remaining field that could
    be mistaken for a real person's, and it is the one field on screen that looks
    like personal data, so it says so in the value itself.
    """
    vehicles = json.loads((FIXTURE_ROOT / "vehicles.json").read_text(encoding="utf-8"))
    names = [record["registered_owner_name"] for record in vehicles["vehicles"]]
    assert names, "no vehicle fixtures found"
    for name in names:
        assert name.endswith("(fictional)"), name


def test_the_owner_name_cannot_be_supplied_by_a_client() -> None:
    """Output only, asserted against all three input surfaces at once."""
    for model in MODELS.values():
        assert "registered_owner_name" not in model.model_fields
    for _path, node in HANDLERS:
        arguments = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
        assert all("owner" not in a.arg for a in arguments), node.name
    for columns in COLUMNS.values():
        assert "registered_owner_name" not in columns


# ---------------------------------------------------------------------------
# F. the refusal, over HTTP
# ---------------------------------------------------------------------------


def create_case(api: Any) -> tuple[str, str]:
    response = api.post(
        f"{API_PREFIX}/cases", json={"journey_type": "AUTHORISED_DEALER_HANDOFF"}
    )
    assert response.status_code == 201, response.text
    body = response.json()
    return body["case"]["id"], body["party_token"]


def test_an_invented_field_is_refused_not_ignored(api: Any) -> None:
    """The behaviour ``extra="forbid"`` buys, checked end to end.

    422 rather than 201 matters: a client that gets a 201 back concludes the field
    was accepted, and nobody discovers otherwise until the data is missing.
    """
    response = api.post(
        f"{API_PREFIX}/cases",
        json={"journey_type": "AUTHORISED_DEALER_HANDOFF", "aadhaar": "1234"},
    )
    assert response.status_code == 422, response.text
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_personal_data_cannot_ride_along_with_the_dealer_lookup(api: Any) -> None:
    """The route that used to take an embedded scalar.

    Before ``DealerVerifyRequest`` existed this request would have returned 200 and
    quietly dropped the extra key, which is the failure mode section B guards
    against. Kept as a runtime test because the AST check alone cannot show what a
    client would actually receive.
    """
    case_id, token = create_case(api)
    response = api.post(
        f"{API_PREFIX}/cases/{case_id}/dealer/verify",
        json={"authorisation_no": "DEMO-29B-001", "pan": "ABCDE1234F"},
        headers={"X-Party-Token": token},
    )
    assert response.status_code == 422, response.text
    fields = response.json()["error"]["detail"]["fields"]
    assert any("pan" in field for field in fields), fields


def test_the_validation_error_names_the_field_and_nothing_else(api: Any) -> None:
    """A rejection must not echo the value back.

    If someone does paste a real Aadhaar number into a field that does not exist,
    the refusal is the moment it could get written to a log. So the error carries
    field names only -- which is also asserted from the other direction in
    ``tests/test_error_contract.py``.
    """
    secret = "999988887777"
    response = api.post(
        f"{API_PREFIX}/cases",
        json={"journey_type": "AUTHORISED_DEALER_HANDOFF", "aadhaar": secret},
    )
    assert response.status_code == 422
    assert secret not in response.text, "the refusal echoed the value it refused"


def test_the_no_real_data_warning_reaches_the_client(api: Any) -> None:
    """The human half of the same property.

    Refusing the data technically is not enough if the screen never says so; the
    wording itself is ``test_copy_lint.py``'s subject, and this asserts only that it
    is actually delivered by the endpoint the SPA reads at startup.
    """
    response = api.get(f"{API_PREFIX}/meta")
    assert response.status_code == 200
    warning = response.json()["no_real_data"]
    assert "Aadhaar" in warning["en"]
    assert warning["hi"].strip(), "the Hindi warning is empty"
