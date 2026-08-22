"""Canonical review payload construction and hashing.

Purpose (07_ARCHITECTURE_DATA_MODEL.md section 6): detect mutation of the
transaction between the moment a party reviewed it and the moment they confirmed
it. That is the *whole* claim. This hash does not prove human identity, does not
constitute a statutory signature, and is not offered as evidence of anything.

The serialisation routine is locked and covered by a committed test vector
(`tests/test_canonical.py`, class `TestLockedVector`). Changing it is a breaking
change: existing confirmations would stop matching. If it ever must change, bump
`CANONICAL_SCHEMA_VERSION` so old and new hashes cannot be confused.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

CANONICAL_SCHEMA_VERSION = "29c-prototype-1"


@dataclass(frozen=True, slots=True)
class CanonicalVehicle:
    registration_no: str
    chassis_suffix: str


@dataclass(frozen=True, slots=True)
class CanonicalDealer:
    authorisation_no: str
    business_name: str


@dataclass(frozen=True, slots=True)
class CanonicalDeclaration:
    code: str
    value: bool


@dataclass(frozen=True, slots=True)
class CanonicalPayload:
    """The exact set of fields both parties are agreeing to.

    Presentation-only data (labels, translations, badge text, formatted dates)
    is deliberately excluded: re-wording a label must not invalidate a
    confirmation, and translating the UI must not change the hash.
    """

    case_id: str
    policy_version: str
    vehicle: CanonicalVehicle
    dealer: CanonicalDealer
    declarations: tuple[CanonicalDeclaration, ...]
    handover_local_time: str
    registered_owner_name: str

    def to_canonical_dict(self) -> dict[str, Any]:
        # Declarations are sorted by code so that the order the user happened to
        # tick them in cannot change the hash.
        declarations = sorted(self.declarations, key=lambda d: d.code)
        return {
            "schema_version": CANONICAL_SCHEMA_VERSION,
            "policy_version": self.policy_version,
            "case_id": self.case_id,
            "vehicle": {
                "registration_no": self.vehicle.registration_no,
                "chassis_suffix": self.vehicle.chassis_suffix,
            },
            "registered_owner_name": self.registered_owner_name,
            "dealer": {
                "authorisation_no": self.dealer.authorisation_no,
                "business_name": self.dealer.business_name,
            },
            "declarations": [
                {"code": d.code, "value": d.value} for d in declarations
            ],
            "handover_local_time": self.handover_local_time,
        }


def canonical_json(payload: CanonicalPayload) -> str:
    """Serialise deterministically.

    - `sort_keys=True` removes dict-ordering as a variable.
    - `separators` without spaces removes whitespace as a variable.
    - `ensure_ascii=False` keeps real UTF-8 so a Devanagari business name hashes
      as its own bytes rather than as escape sequences.
    - `allow_nan=False` because NaN/Infinity are not valid JSON and would make
      the vector unreproducible across languages.
    """
    return json.dumps(
        payload.to_canonical_dict(),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def payload_hash(payload: CanonicalPayload) -> str:
    """SHA-256 of the canonical serialisation, lowercase hex."""
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
