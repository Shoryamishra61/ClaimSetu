"""Transactional domain service for the exact four-state custody lifecycle."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from dataclasses import dataclass

from .. import clock
from ..db.connection import Database
from ..errors import AppError
from .models import CustodyState
from .pdf_service import Form29CFields, generate_form29c

GSTIN_PATTERN = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$")

ALLOWED_TRANSITIONS: dict[CustodyState, CustodyState] = {
    CustodyState.DRAFT: CustodyState.INITIATED,
    CustodyState.INITIATED: CustodyState.DEALER_SELECTED,
    CustodyState.DEALER_SELECTED: CustodyState.CUSTODY_TRANSFERRED,
}


@dataclass(frozen=True, slots=True)
class CustodyCase:
    case_id: str
    vehicle_no: str
    chassis_suffix: str
    seller_id: str
    seller_name: str
    seller_address: str
    vehicle_make: str
    chassis_no: str
    engine_or_motor_no: str
    rto_jurisdiction: str
    dealer_id: str | None
    dealer_name: str | None
    dealer_gstin: str | None
    trade_certificate_no: str | None
    dealer_business_address: str | None
    authorisation_certificate_no: str | None
    authorisation_issued_by: str | None
    authorisation_valid_until: str | None
    state: CustodyState
    odometer_reading: int | None
    delivery_timestamp: str | None
    form_29c_storage_url: str | None
    created_at: str
    updated_at: str


def _normalise(value: str) -> str:
    return "".join(value.split()).upper()


def _case_from_row(row: sqlite3.Row) -> CustodyCase:
    return CustodyCase(
        case_id=row["Case_ID"],
        vehicle_no=row["Vehicle_No"],
        chassis_suffix=row["Chassis_Suffix"],
        seller_id=row["Seller_ID"],
        seller_name=row["Full_Name"],
        seller_address=row["Address"],
        vehicle_make=row["Make_Model"],
        chassis_no=row["Chassis_No"],
        engine_or_motor_no=row["Engine_Or_Motor_No"],
        rto_jurisdiction=row["RTO_Jurisdiction"],
        dealer_id=row["Dealer_ID"],
        dealer_name=row["Business_Name"],
        dealer_gstin=row["GSTIN"],
        trade_certificate_no=row["Trade_Certificate_No"],
        dealer_business_address=row["Business_Address"],
        authorisation_certificate_no=row["Authorisation_Certificate_No"],
        authorisation_issued_by=row["Authorisation_Issued_By"],
        authorisation_valid_until=row["Authorisation_Valid_Until"],
        state=CustodyState(row["Current_State"]),
        odometer_reading=row["Odometer_Reading"],
        delivery_timestamp=row["Delivery_Timestamp"],
        form_29c_storage_url=row["Form_29C_Storage_URL"],
        created_at=row["Created_At"],
        updated_at=row["Updated_At"],
    )


class CustodyService:
    def __init__(self, database: Database) -> None:
        self.database = database

    def verify_vehicle(self, *, vehicle_no: str, chassis_suffix: str) -> dict[str, object]:
        with self.database.read() as connection:
            row = connection.execute(
                """
                SELECT v.*, c.Full_Name, c.Address
                FROM VehicleFixture v JOIN Citizen c ON c.Resident_ID=v.Seller_ID
                WHERE UPPER(REPLACE(v.Vehicle_No, ' ', ''))=?
                  AND UPPER(REPLACE(v.Chassis_Suffix, ' ', ''))=?
                """,
                (_normalise(vehicle_no), _normalise(chassis_suffix)),
            ).fetchone()
        if row is None:
            raise AppError("VEHICLE_NOT_FOUND")
        return {
            "simulation": True,
            "fictional": True,
            "vehicle_id": row["Vehicle_ID"],
            "vehicle_no": row["Vehicle_No"],
            "chassis_suffix": row["Chassis_Suffix"],
            "seller_id": row["Seller_ID"],
            "owner_name": row["Full_Name"],
            "owner_address": row["Address"],
            "model": row["Make_Model"],
            "chassis_no": row["Chassis_No"],
            "engine_or_motor_no": row["Engine_Or_Motor_No"],
            "rto_jurisdiction": row["RTO_Jurisdiction"],
            "hypothecation_active": bool(row["Hypothecation_Active"]),
        }

    def verify_dealer(
        self, *, gstin: str | None, trade_certificate_no: str | None
    ) -> dict[str, object]:
        normal_gstin = _normalise(gstin or "")
        normal_trade = _normalise(trade_certificate_no or "")
        if not normal_gstin and not normal_trade:
            raise AppError("DEALER_IDENTIFIER_REQUIRED")
        if normal_gstin and GSTIN_PATTERN.fullmatch(normal_gstin) is None:
            raise AppError("INVALID_GSTIN")
        with self.database.read() as connection:
            row = connection.execute(
                """
                SELECT * FROM AuthorizedDealer
                WHERE (? <> '' AND GSTIN = ?)
                   OR (? <> '' AND UPPER(REPLACE(Trade_Certificate_No, ' ', '')) = ?)
                """,
                (normal_gstin, normal_gstin, normal_trade, normal_trade),
            ).fetchone()
        if row is None:
            raise AppError("DEALER_NOT_FOUND")
        return {
            "simulation": True,
            "fictional": True,
            "dealer_id": row["Dealer_ID"],
            "trade_certificate_no": row["Trade_Certificate_No"],
            "gstin": row["GSTIN"],
            "business_name": row["Business_Name"],
            "rto_jurisdiction_code": row["RTO_Jurisdiction_Code"],
            "business_address": row["Business_Address"],
            "authorisation_certificate_no": row["Authorisation_Certificate_No"],
            "authorisation_issued_by": row["Authorisation_Issued_By"],
            "authorisation_valid_until": row["Authorisation_Valid_Until"],
            "status": row["Status"],
            "can_continue": row["Status"] == "ACTIVE",
        }

    def initiate(
        self, *, vehicle_no: str, chassis_suffix: str, seller_id: str
    ) -> CustodyCase:
        verified = self.verify_vehicle(
            vehicle_no=vehicle_no, chassis_suffix=chassis_suffix
        )
        if verified["seller_id"] != seller_id:
            raise AppError("SELLER_NOT_FOUND")
        case_id = f"case-{clock.new_id()}"
        now = clock.utc_now_iso()
        with self.database.write() as connection:
            connection.execute(
                """
                INSERT INTO HandoverCase
                  (Case_ID, Vehicle_No, Chassis_Suffix, Seller_ID, Current_State,
                   Created_At, Updated_At)
                VALUES (?, ?, ?, ?, 'DRAFT', ?, ?)
                """,
                (case_id, verified["vehicle_no"], verified["chassis_suffix"], seller_id, now, now),
            )
            self._transition_in_transaction(
                connection, case_id=case_id, source=CustodyState.DRAFT,
                target=CustodyState.INITIATED
            )
        return self.get_case(case_id)

    def transition(
        self,
        *,
        case_id: str,
        target: CustodyState,
        dealer_id: str | None = None,
        odometer_reading: int | None = None,
        seller_confirmed: bool = False,
        dealer_confirmed: bool = False,
    ) -> CustodyCase:
        with self.database.write() as connection:
            current = self._get_case(connection, case_id)
            expected = ALLOWED_TRANSITIONS.get(current.state)
            if expected is not target:
                raise AppError(
                    "CUSTODY_INVALID_TRANSITION",
                    detail={"from_state": current.state.value, "to_state": target.value},
                )

            fields: dict[str, object] = {}
            if target is CustodyState.DEALER_SELECTED:
                if not dealer_id:
                    raise AppError("DEALER_IDENTIFIER_REQUIRED")
                dealer = connection.execute(
                    "SELECT * FROM AuthorizedDealer WHERE Dealer_ID=?", (dealer_id,)
                ).fetchone()
                if dealer is None:
                    raise AppError("DEALER_NOT_FOUND")
                if dealer["Status"] != "ACTIVE":
                    raise AppError("DEALER_NOT_ACTIVE")
                fields["Dealer_ID"] = dealer_id

            if target is CustodyState.CUSTODY_TRANSFERRED:
                if odometer_reading is None or odometer_reading <= 0:
                    raise AppError("INVALID_ODOMETER")
                if not seller_confirmed or not dealer_confirmed:
                    raise AppError("CONFIRMATIONS_INCOMPLETE")
                if current.dealer_id is None:
                    raise AppError("DEALER_IDENTIFIER_REQUIRED")
                fields["Odometer_Reading"] = odometer_reading
                fields["Delivery_Timestamp"] = clock.utc_now_iso()
                generated = generate_form29c(
                    Form29CFields(
                        case_id=current.case_id,
                        vehicle_no=current.vehicle_no,
                        chassis_suffix=current.chassis_suffix,
                        seller_name=current.seller_name,
                        seller_address=current.seller_address,
                        vehicle_make=current.vehicle_make,
                        chassis_no=current.chassis_no,
                        engine_or_motor_no=current.engine_or_motor_no,
                        rto_jurisdiction=current.rto_jurisdiction,
                        dealer_name=current.dealer_name or "",
                        dealer_gstin=current.dealer_gstin or "",
                        trade_certificate_no=current.trade_certificate_no or "",
                        dealer_business_address=current.dealer_business_address or "",
                        authorisation_certificate_no=(
                            current.authorisation_certificate_no or ""
                        ),
                        authorisation_issued_by=current.authorisation_issued_by or "",
                        authorisation_valid_until=(
                            current.authorisation_valid_until or ""
                        ),
                        odometer_reading=odometer_reading,
                        delivery_timestamp=str(fields["Delivery_Timestamp"]),
                    )
                )
                storage_url = f"/api/v1/cases/{case_id}/form29c.pdf"
                fields["Form_29C_Storage_URL"] = storage_url
                connection.execute(
                    """
                    INSERT INTO Form29CDocument (Case_ID, Pdf_Bytes, Sha256, Generated_At)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(Case_ID) DO UPDATE SET
                      Pdf_Bytes=excluded.Pdf_Bytes, Sha256=excluded.Sha256,
                      Generated_At=excluded.Generated_At
                    """,
                    (case_id, generated.content, generated.sha256, clock.utc_now_iso()),
                )

            self._transition_in_transaction(
                connection,
                case_id=case_id,
                source=current.state,
                target=target,
                fields=fields,
            )
        return self.get_case(case_id)

    def get_case(self, case_id: str) -> CustodyCase:
        with self.database.read() as connection:
            return self._get_case(connection, case_id)

    def get_document(self, case_id: str) -> tuple[bytes, str]:
        with self.database.read() as connection:
            row = connection.execute(
                "SELECT Pdf_Bytes, Sha256 FROM Form29CDocument WHERE Case_ID=?",
                (case_id,),
            ).fetchone()
        if row is None:
            raise AppError("FORM_NOT_READY")
        return bytes(row["Pdf_Bytes"]), str(row["Sha256"])

    def transition_log(self, case_id: str) -> list[dict[str, object]]:
        with self.database.read() as connection:
            rows = connection.execute(
                "SELECT * FROM StateTransitionLog WHERE Case_ID=? ORDER BY rowid",
                (case_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def _get_case(self, connection: sqlite3.Connection, case_id: str) -> CustodyCase:
        row = connection.execute(
            """
            SELECT h.*, c.Full_Name, c.Address,
                   v.Make_Model, v.Chassis_No, v.Engine_Or_Motor_No,
                   v.RTO_Jurisdiction,
                   d.Business_Name, d.GSTIN, d.Trade_Certificate_No,
                   d.Business_Address, d.Authorisation_Certificate_No,
                   d.Authorisation_Issued_By, d.Authorisation_Valid_Until
            FROM HandoverCase h
            JOIN Citizen c ON c.Resident_ID=h.Seller_ID
            JOIN VehicleFixture v
              ON v.Vehicle_No=h.Vehicle_No AND v.Seller_ID=h.Seller_ID
            LEFT JOIN AuthorizedDealer d ON d.Dealer_ID=h.Dealer_ID
            WHERE h.Case_ID=?
            """,
            (case_id,),
        ).fetchone()
        if row is None:
            raise AppError("CASE_NOT_FOUND")
        return _case_from_row(row)

    def _transition_in_transaction(
        self,
        connection: sqlite3.Connection,
        *,
        case_id: str,
        source: CustodyState,
        target: CustodyState,
        fields: dict[str, object] | None = None,
    ) -> None:
        assignments = {**(fields or {}), "Current_State": target.value, "Updated_At": clock.utc_now_iso()}
        set_clause = ", ".join(f"{name}=?" for name in assignments)
        cursor = connection.execute(
            f"UPDATE HandoverCase SET {set_clause} WHERE Case_ID=? AND Current_State=?",
            (*assignments.values(), case_id, source.value),
        )
        if cursor.rowcount != 1:
            raise AppError(
                "CUSTODY_INVALID_TRANSITION",
                detail={"from_state": source.value, "to_state": target.value},
            )
        previous = connection.execute(
            """
            SELECT System_Integrity_Chaining_Hash FROM StateTransitionLog
            WHERE Case_ID=? ORDER BY rowid DESC LIMIT 1
            """,
            (case_id,),
        ).fetchone()
        previous_hash = str(previous[0]) if previous else ""
        transition_id = clock.new_id()
        timestamp = clock.utc_now_iso()
        canonical = json.dumps(
            {
                "case_id": case_id,
                "from_state": source.value,
                "to_state": target.value,
                "timestamp": timestamp,
                "transition_id": transition_id,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        event_hash = hashlib.sha256((previous_hash + canonical).encode()).hexdigest()
        connection.execute(
            """
            INSERT INTO StateTransitionLog
              (Transition_ID, Case_ID, From_State, To_State, Transition_Timestamp,
               System_Integrity_Chaining_Hash, Previous_Transition_Hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (transition_id, case_id, source.value, target.value, timestamp, event_hash, previous_hash or None),
        )


def serialise_case(case: CustodyCase) -> dict[str, object]:
    return {
        "simulation": True,
        "fictional": True,
        "case_id": case.case_id,
        "vehicle_no": case.vehicle_no,
        "chassis_suffix": case.chassis_suffix,
        "seller_id": case.seller_id,
        "seller_name": case.seller_name,
        "seller_address": case.seller_address,
        "vehicle_make": case.vehicle_make,
        "chassis_no": case.chassis_no,
        "engine_or_motor_no": case.engine_or_motor_no,
        "rto_jurisdiction": case.rto_jurisdiction,
        "dealer_id": case.dealer_id,
        "dealer_name": case.dealer_name,
        "dealer_gstin": case.dealer_gstin,
        "trade_certificate_no": case.trade_certificate_no,
        "dealer_business_address": case.dealer_business_address,
        "authorisation_certificate_no": case.authorisation_certificate_no,
        "authorisation_issued_by": case.authorisation_issued_by,
        "authorisation_valid_until": case.authorisation_valid_until,
        "state": case.state.value,
        "odometer_reading": case.odometer_reading,
        "delivery_timestamp": case.delivery_timestamp,
        "form_29c_storage_url": case.form_29c_storage_url,
        "is_government_acknowledgement": False,
        "created_at": case.created_at,
        "updated_at": case.updated_at,
    }


__all__ = [
    "ALLOWED_TRANSITIONS",
    "GSTIN_PATTERN",
    "CustodyCase",
    "CustodyService",
    "serialise_case",
]
