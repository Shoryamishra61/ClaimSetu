"""Contract and invariant tests for the exact four-state custody slice."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import statistics
import time
from dataclasses import replace
from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfReader

from app.config import Settings
from app.custody import initialise_custody_schema
from app.main import create_app
from app.services.context import ServiceContext

DEMO_VEHICLE = {
    "vehicle_no": "DL-1CA-1234",
    "chassis_suffix": "56789",
    "seller_id": "seller-01",
}
DEMO_DEALER = {
    "dealer_id": "dealer-01",
    "gstin": "07AAAAA1111A1Z1",
}


@pytest.fixture(autouse=True)
def _custody_schema_for_service_tests(ctx: ServiceContext) -> None:
    """Direct-context tests opt into the slice initialized by the ASGI lifespan."""
    initialise_custody_schema(ctx.db)


def _initiate(api: TestClient) -> str:
    response = api.post("/api/v1/case/initiate", json=DEMO_VEHICLE)
    assert response.status_code == 201, response.text
    return str(response.json()["case_id"])


def _select_dealer(api: TestClient, case_id: str) -> None:
    response = api.patch(
        f"/api/v1/cases/{case_id}/state",
        json={"state": "DEALER_SELECTED", "dealer_id": DEMO_DEALER["dealer_id"]},
    )
    assert response.status_code == 200, response.text


def test_default_runtime_exposes_only_the_definitive_custody_contract(
    settings: Settings, tmp_path: Path
) -> None:
    clean_settings = replace(
        settings,
        database_path=str(tmp_path / "definitive-custody.sqlite3"),
        enable_historical_blueprint=False,
    )
    with TestClient(create_app(clean_settings)) as client:
        assert set(client.get("/openapi.json").json()["paths"]) == {
            "/healthz",
            "/api/v1/vehicle/verify",
            "/api/v1/case/initiate",
            "/api/v1/dealer/verify",
            "/api/v1/cases/{case_id}/custody",
            "/api/v1/cases/{case_id}/state",
            "/api/v1/cases/{case_id}/transitions",
            "/api/v1/cases/{case_id}/form29c.pdf",
        }
        with client.app.state.custody_db.read() as connection:
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
    assert tables == {
        "Citizen",
        "AuthorizedDealer",
        "VehicleFixture",
        "HandoverCase",
        "StateTransitionLog",
        "Form29CDocument",
    }


def test_schema_seeds_exactly_ten_fictional_rows_and_enables_sqlite_guards(
    ctx: ServiceContext,
) -> None:
    with ctx.db.read() as connection:
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert connection.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"
        assert {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in ("Citizen", "AuthorizedDealer", "VehicleFixture")
        } == {"Citizen": 10, "AuthorizedDealer": 10, "VehicleFixture": 10}
        assert connection.execute(
            "SELECT COUNT(*) FROM Citizen WHERE Is_Fictional=1"
        ).fetchone()[0] == 10


@pytest.mark.parametrize(
    ("seller_id", "dealer_id"),
    (("missing-seller", None), ("seller-01", "missing-dealer")),
)
def test_db_constraints(
    ctx: ServiceContext, seller_id: str, dealer_id: str | None
) -> None:
    with pytest.raises(sqlite3.IntegrityError), ctx.db.write() as connection:
        connection.execute(
            """
            INSERT INTO HandoverCase
              (Case_ID, Vehicle_No, Chassis_Suffix, Seller_ID, Dealer_ID,
               Current_State, Created_At, Updated_At)
            VALUES ('orphan', 'DEMO', '12345', ?, ?, 'DRAFT', 'now', 'now')
            """,
            (seller_id, dealer_id),
        )


def test_multirow_failure_rolls_back_the_entire_write(ctx: ServiceContext) -> None:
    with pytest.raises(sqlite3.IntegrityError), ctx.db.write() as connection:
        connection.execute(
            """
            INSERT INTO HandoverCase
              (Case_ID, Vehicle_No, Chassis_Suffix, Seller_ID, Current_State,
               Created_At, Updated_At)
            VALUES ('rollback-case', 'DEMO', '12345', 'seller-01', 'DRAFT', 'now', 'now')
            """
        )
        connection.execute(
            """
            INSERT INTO StateTransitionLog
              (Transition_ID, Case_ID, From_State, To_State, Transition_Timestamp,
               System_Integrity_Chaining_Hash)
            VALUES ('bad-transition', 'missing-case', 'DRAFT', 'INITIATED', 'now', 'hash')
            """
        )
    with ctx.db.read() as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM HandoverCase WHERE Case_ID='rollback-case'"
        ).fetchone()[0] == 0


@pytest.mark.parametrize(
    "gstin",
    ["1234567890", "not-a-gstin", "07AAAAA1111A1Z", "07aaaaa1111a1z1x"],
)
def test_gstin_format_enforcement(api: TestClient, gstin: str) -> None:
    response = api.post("/api/v1/dealer/verify", json={"gstin": gstin})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_GSTIN"
    assert response.json()["error"]["message"] == "Invalid GSTIN format structure."


def test_state_transition_protection(api: TestClient, ctx: ServiceContext) -> None:
    case_id = "draft-transition-protection"
    with ctx.db.write() as connection:
        connection.execute(
            """
            INSERT INTO HandoverCase
              (Case_ID, Vehicle_No, Chassis_Suffix, Seller_ID, Current_State,
               Created_At, Updated_At)
            VALUES (?, ?, ?, ?, 'DRAFT', 'now', 'now')
            """,
            (
                case_id,
                DEMO_VEHICLE["vehicle_no"],
                DEMO_VEHICLE["chassis_suffix"],
                DEMO_VEHICLE["seller_id"],
            ),
        )
    response = api.patch(
        f"/api/v1/cases/{case_id}/state",
        json={
            "state": "CUSTODY_TRANSFERRED",
            "odometer_reading": 1,
            "seller_confirmed": True,
            "dealer_confirmed": True,
        },
    )
    assert response.status_code == 422
    snapshot = api.get(f"/api/v1/cases/{case_id}/custody")
    assert snapshot.json()["case"]["state"] == "DRAFT"


@pytest.mark.parametrize("odometer", [None, 0, -1])
def test_nonpositive_or_missing_odometer_is_rejected(
    api: TestClient, odometer: int | None
) -> None:
    case_id = _initiate(api)
    _select_dealer(api, case_id)
    response = api.patch(
        f"/api/v1/cases/{case_id}/state",
        json={
            "state": "CUSTODY_TRANSFERRED",
            "odometer_reading": odometer,
            "seller_confirmed": True,
            "dealer_confirmed": True,
        },
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_ODOMETER"


def test_document_is_unavailable_before_transfer(api: TestClient) -> None:
    case_id = _initiate(api)
    response = api.get(f"/api/v1/cases/{case_id}/form29c.pdf")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "FORM_NOT_READY"


def test_complete_workflow_pdf_and_integrity_chain(api: TestClient) -> None:
    vehicle = api.get("/api/v1/vehicle/verify", params=DEMO_VEHICLE)
    assert vehicle.status_code == 200
    assert vehicle.json()["data"]["fictional"] is True

    dealer = api.post("/api/v1/dealer/verify", json={"gstin": DEMO_DEALER["gstin"]})
    assert dealer.status_code == 200
    assert dealer.json()["data"]["status"] == "ACTIVE"

    case_id = _initiate(api)
    _select_dealer(api, case_id)
    transfer = api.patch(
        f"/api/v1/cases/{case_id}/state",
        json={
            "state": "CUSTODY_TRANSFERRED",
            "odometer_reading": 12_345,
            "seller_confirmed": True,
            "dealer_confirmed": True,
        },
    )
    assert transfer.status_code == 200, transfer.text
    case = transfer.json()["case"]
    assert case["state"] == "CUSTODY_TRANSFERRED"
    assert case["is_government_acknowledgement"] is False

    document = api.get(case["form_29c_storage_url"])
    assert document.status_code == 200
    assert document.headers["x-prototype-document"] == "simulated-not-government-submission"
    assert hashlib.sha256(document.content).hexdigest() == document.headers[
        "x-document-sha256"
    ]
    reader = PdfReader(BytesIO(document.content))
    assert len(reader.pages) == 2
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    for exact_value in (
        "DL-1CA-1234",
        "Demo Seller 01 (fictional)",
        "Demo address 01, Fictional City",
        "Registering Authority DL-01 (fictional)",
        "Aster 110 Demo Scooter",
        "DEMOCHASSIS56789",
        "DEMOENGINE00001",
        "Demo dealer address 01, Fictional City",
        "29B-DEMO-0001",
        "Registering Authority DL-14 (fictional)",
        "2030-12-31",
        "07AAAAA1111A1Z1",
        "NOT SUBMITTED TO GOVERNMENT",
        "There is no e-signature captured by this prototype",
    ):
        assert exact_value in text

    log = api.get(f"/api/v1/cases/{case_id}/transitions").json()["transitions"]
    assert [(event["From_State"], event["To_State"]) for event in log] == [
        ("DRAFT", "INITIATED"),
        ("INITIATED", "DEALER_SELECTED"),
        ("DEALER_SELECTED", "CUSTODY_TRANSFERRED"),
    ]
    previous = ""
    for event in log:
        canonical = json.dumps(
            {
                "case_id": case_id,
                "from_state": event["From_State"],
                "to_state": event["To_State"],
                "timestamp": event["Transition_Timestamp"],
                "transition_id": event["Transition_ID"],
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        assert event["Previous_Transition_Hash"] == (previous or None)
        assert event["System_Integrity_Chaining_Hash"] == hashlib.sha256(
            (previous + canonical).encode()
        ).hexdigest()
        previous = event["System_Integrity_Chaining_Hash"]


def test_mock_lookup_p95_is_below_50_ms(api: TestClient) -> None:
    lookups = {
        "vehicle": lambda: api.get(
            "/api/v1/vehicle/verify", params=DEMO_VEHICLE
        ),
        "dealer": lambda: api.post(
            "/api/v1/dealer/verify", json={"gstin": DEMO_DEALER["gstin"]}
        ),
    }
    for label, lookup in lookups.items():
        for _ in range(10):
            assert lookup().status_code == 200
        timings: list[float] = []
        for _ in range(100):
            started = time.perf_counter()
            response = lookup()
            timings.append(time.perf_counter() - started)
            assert response.status_code == 200
        p95 = statistics.quantiles(timings, n=100, method="inclusive")[94]
        assert p95 < 0.050, f"{label} lookup p95 was {p95 * 1000:.2f} ms"
