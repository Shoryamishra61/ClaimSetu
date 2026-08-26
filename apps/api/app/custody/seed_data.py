"""Deterministic fictional reference data for the custody-record slice."""

from __future__ import annotations

from collections.abc import Sequence

from ..db.connection import Database

CitizenSeed = tuple[str, str, str, str]
DealerSeed = tuple[str, str, str, str, str, str, str, str, str, str]
VehicleSeed = tuple[str, str, str, str, str, str, str, str, int]

CITIZENS: tuple[CitizenSeed, ...] = tuple(
    (
        f"seller-{index:02d}",
        f"Demo Seller {index:02d} (fictional)",
        f"00000000{index:02d}",
        f"Demo address {index:02d}, Fictional City",
    )
    for index in range(1, 11)
)

DEALERS: tuple[DealerSeed, ...] = tuple(
    (
        dealer_id,
        trade_certificate,
        gstin,
        business_name,
        jurisdiction,
        status,
        f"Demo dealer address {index:02d}, Fictional City",
        f"29B-DEMO-{index:04d}",
        f"Registering Authority {jurisdiction} (fictional)",
        "2030-12-31" if status == "ACTIVE" else "2025-12-31",
    )
    for index, (
        dealer_id,
        trade_certificate,
        gstin,
        business_name,
        jurisdiction,
        status,
    ) in enumerate(
        (
            ("dealer-01", "TC-DEL-9988", "07AAAAA1111A1Z1", "Suresh Auto (fictional)", "DL-14", "ACTIVE"),
            ("dealer-02", "TC-MH-2202", "27BBBBB2222B2Z2", "Asha Motors (fictional)", "MH-02", "ACTIVE"),
            ("dealer-03", "TC-KA-3303", "29CCCCC3333C3Z3", "Namma Wheels (fictional)", "KA-03", "ACTIVE"),
            ("dealer-04", "TC-UP-4404", "09DDDDD4444D4Z4", "Ganga Autos (fictional)", "UP-04", "ACTIVE"),
            ("dealer-05", "TC-WB-5505", "19EEEEE5555E5Z5", "Howrah Cars (fictional)", "WB-05", "ACTIVE"),
            ("dealer-06", "TC-TN-6606", "33FFFFF6666F6Z6", "Kaveri Mobility (fictional)", "TN-06", "ACTIVE"),
            ("dealer-07", "TC-GJ-7707", "24GGGGG7777G7Z7", "Sabarmati Auto (fictional)", "GJ-07", "ACTIVE"),
            ("dealer-08", "TC-HR-8808", "06HHHHH8888H8Z8", "Aravali Motors (fictional)", "HR-08", "ACTIVE"),
            ("dealer-09", "TC-TS-9909", "36IIIII9999I9Z9", "Deccan Cars (fictional)", "TS-09", "EXPIRED"),
            ("dealer-10", "TC-KL-1010", "32JJJJJ1010JAZA", "Malabar Auto (fictional)", "KL-10", "SUSPENDED"),
        ),
        start=1,
    )
)

VEHICLES: tuple[VehicleSeed, ...] = tuple(
    (
        vehicle_id,
        vehicle_no,
        chassis_suffix,
        f"DEMOCHASSIS{chassis_suffix}",
        f"DEMOENGINE{index:05d}",
        seller_id,
        make_model,
        f"Registering Authority {vehicle_no[:2]}-01 (fictional)",
        hypothecation_active,
    )
    for index, (
        vehicle_id,
        vehicle_no,
        chassis_suffix,
        seller_id,
        make_model,
        hypothecation_active,
    ) in enumerate(
        (
            ("vehicle-01", "DL-1CA-1234", "56789", "seller-01", "Aster 110 Demo Scooter", 0),
            ("vehicle-02", "DEMO01AB1234", "12345", "seller-02", "WagonR Demo", 0),
            ("vehicle-03", "DEMO02CD5678", "56789", "seller-03", "i20 Demo", 0),
            ("vehicle-04", "DEMO03EF9012", "90123", "seller-04", "Nexon Demo", 0),
            ("vehicle-05", "DEMO04GH3456", "34567", "seller-05", "Activa Demo", 0),
            ("vehicle-06", "DEMO05IJ7890", "78901", "seller-06", "Bolero Demo", 1),
            ("vehicle-07", "DEMO06KL2345", "23456", "seller-07", "Eeco Demo", 0),
            ("vehicle-08", "DEMO07MN6789", "67890", "seller-08", "Tiago Demo", 0),
            ("vehicle-09", "DEMO08PQ0123", "01234", "seller-09", "Celerio Demo", 0),
            ("vehicle-10", "DEMO09RS4567", "45678", "seller-10", "Amaze Demo", 0),
        ),
        start=1,
    )
)


def seed_reference_data(database: Database) -> None:
    """Upsert all reference rows in one transaction.

    A failure anywhere rolls back citizens, dealers, and vehicles together; there
    is never a half-seeded registry.
    """

    with database.write() as connection:
        connection.executemany(
            """
            INSERT INTO Citizen
              (Resident_ID, Full_Name, Mobile_Number, Address, Is_Fictional)
            VALUES (?, ?, ?, ?, 1)
            ON CONFLICT(Resident_ID) DO UPDATE SET
              Full_Name=excluded.Full_Name, Mobile_Number=excluded.Mobile_Number,
              Address=excluded.Address
            """,
            CITIZENS,
        )
        connection.executemany(
            """
            INSERT INTO AuthorizedDealer
              (Dealer_ID, Trade_Certificate_No, GSTIN, Business_Name,
               RTO_Jurisdiction_Code, Status, Business_Address,
               Authorisation_Certificate_No, Authorisation_Issued_By,
               Authorisation_Valid_Until, Is_Fictional)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            ON CONFLICT(Dealer_ID) DO UPDATE SET
              Trade_Certificate_No=excluded.Trade_Certificate_No,
              GSTIN=excluded.GSTIN, Business_Name=excluded.Business_Name,
              RTO_Jurisdiction_Code=excluded.RTO_Jurisdiction_Code,
              Status=excluded.Status,
              Business_Address=excluded.Business_Address,
              Authorisation_Certificate_No=excluded.Authorisation_Certificate_No,
              Authorisation_Issued_By=excluded.Authorisation_Issued_By,
              Authorisation_Valid_Until=excluded.Authorisation_Valid_Until
            """,
            DEALERS,
        )
        connection.executemany(
            """
            INSERT INTO VehicleFixture
              (Vehicle_ID, Vehicle_No, Chassis_Suffix, Chassis_No,
               Engine_Or_Motor_No, Seller_ID, Make_Model, RTO_Jurisdiction,
               Hypothecation_Active, Is_Fictional)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            ON CONFLICT(Vehicle_ID) DO UPDATE SET
              Vehicle_No=excluded.Vehicle_No,
              Chassis_Suffix=excluded.Chassis_Suffix,
              Chassis_No=excluded.Chassis_No,
              Engine_Or_Motor_No=excluded.Engine_Or_Motor_No,
              Seller_ID=excluded.Seller_ID,
              Make_Model=excluded.Make_Model,
              RTO_Jurisdiction=excluded.RTO_Jurisdiction,
              Hypothecation_Active=excluded.Hypothecation_Active
            """,
            VEHICLES,
        )


def counts(database: Database) -> dict[str, int]:
    with database.read() as connection:
        return {
            table: int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
            for table in ("Citizen", "AuthorizedDealer", "VehicleFixture")
        }


def _validate_count(label: str, rows: Sequence[object]) -> None:
    if len(rows) != 10:
        raise RuntimeError(f"{label} must contain exactly 10 deterministic fixtures")


for _label, _rows in (("citizens", CITIZENS), ("dealers", DEALERS), ("vehicles", VEHICLES)):
    _validate_count(_label, _rows)


__all__ = ["CITIZENS", "DEALERS", "VEHICLES", "counts", "seed_reference_data"]
