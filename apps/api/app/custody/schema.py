"""Schema initialization for the isolated four-state custody tables."""

from __future__ import annotations

from pathlib import Path

from ..db.connection import Database
from .seed_data import seed_reference_data

SCHEMA_PATH = Path(__file__).with_name("schema.sql")

ADDITIVE_COLUMNS: dict[str, dict[str, str]] = {
    "Citizen": {
        "Address": "TEXT NOT NULL DEFAULT 'Fictional address pending seed'",
    },
    "AuthorizedDealer": {
        "Business_Address": "TEXT NOT NULL DEFAULT 'Fictional address pending seed'",
        "Authorisation_Certificate_No": "TEXT NOT NULL DEFAULT ''",
        "Authorisation_Issued_By": "TEXT NOT NULL DEFAULT 'Fictional authority'",
        "Authorisation_Valid_Until": "TEXT NOT NULL DEFAULT '2030-12-31'",
    },
    "VehicleFixture": {
        "Chassis_No": "TEXT NOT NULL DEFAULT 'FICTIONAL-CHASSIS'",
        "Engine_Or_Motor_No": "TEXT NOT NULL DEFAULT 'FICTIONAL-ENGINE'",
        "RTO_Jurisdiction": "TEXT NOT NULL DEFAULT 'Fictional registering authority'",
    },
}


def _apply_additive_migrations(database: Database) -> None:
    """Upgrade pre-release demo volumes without deleting their local records."""
    with database.write() as connection:
        for table, columns in ADDITIVE_COLUMNS.items():
            existing = {
                row[1] for row in connection.execute(f'PRAGMA table_info("{table}")')
            }
            for column, declaration in columns.items():
                if column not in existing:
                    connection.execute(
                        f'ALTER TABLE "{table}" ADD COLUMN "{column}" {declaration}'
                    )


def initialise_custody_schema(database: Database) -> None:
    database.apply_schema(SCHEMA_PATH)
    _apply_additive_migrations(database)
    seed_reference_data(database)
    with database.write() as connection:
        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
              idx_authorized_dealer_authorisation_certificate
            ON AuthorizedDealer(Authorisation_Certificate_No)
            """
        )


__all__ = ["initialise_custody_schema"]
