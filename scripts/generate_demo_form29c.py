#!/usr/bin/env python3
"""Generate the stable fictional Form 29C demonstration artifact."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_ROOT = ROOT / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.custody.pdf_service import Form29CFields, generate_form29c  # noqa: E402


def main() -> int:
    output = ROOT / "output" / "pdf" / "handover29c-demo-form29c.pdf"
    output.parent.mkdir(parents=True, exist_ok=True)
    generated = generate_form29c(
        Form29CFields(
            case_id="case-demo-review",
            vehicle_no="DL-1CA-1234",
            chassis_suffix="56789",
            seller_name="Demo Seller 01 (fictional)",
            seller_address="Demo address 01, Fictional City",
            vehicle_make="Aster 110 Demo Scooter",
            chassis_no="DEMOCHASSIS56789",
            engine_or_motor_no="DEMOENGINE00001",
            rto_jurisdiction="Registering Authority DL-01 (fictional)",
            dealer_name="Suresh Auto (fictional)",
            dealer_gstin="07AAAAA1111A1Z1",
            trade_certificate_no="TC-DEL-9988",
            dealer_business_address="Demo dealer address 01, Fictional City",
            authorisation_certificate_no="29B-DEMO-0001",
            authorisation_issued_by="Registering Authority DL-14 (fictional)",
            authorisation_valid_until="2030-12-31",
            odometer_reading=12_345,
            delivery_timestamp="2026-08-22T10:00:00Z",
        )
    )
    output.write_bytes(generated.content)
    print(f"generated={output}")
    print(f"sha256={generated.sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
