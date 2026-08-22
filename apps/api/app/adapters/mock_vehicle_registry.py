"""Simulated vehicle registry.

Reads ``fixtures/vehicles.json``. There is no network call, no cache warming and
no upstream. The only thing this adapter knows how to do is match a fictional
registration number plus chassis suffix against a small seeded list.

Lookup is case-insensitive and whitespace-tolerant on the registration number
because a citizen typing a plate is not performing an exact-match exercise; the
chassis suffix is compared the same way. This is input hygiene, not fuzzy
matching -- there is deliberately no similarity scoring anywhere in this project.
"""

from __future__ import annotations

from dataclasses import dataclass

from .fixture_loader import load
from .simulation import SimulatedResponse, TruthLabel


@dataclass(frozen=True, slots=True)
class VehicleRecord(SimulatedResponse):
    id: str
    registration_no: str
    chassis_suffix: str
    make_model: str
    registered_owner_name: str
    document_flags: dict[str, bool]
    submission_scenario: str
    is_default_demo: bool
    demo_label_en: str
    demo_label_hi: str


def _normalise(value: str) -> str:
    return "".join(value.split()).upper()


class MockVehicleRegistry:
    def __init__(self) -> None:
        self._records: tuple[VehicleRecord, ...] = tuple(
            VehicleRecord(
                truth_label=TruthLabel.FICTIONAL_VEHICLE_DATA,
                id=row["id"],
                registration_no=row["registration_no"],
                chassis_suffix=row["chassis_suffix"],
                make_model=row["make_model"],
                registered_owner_name=row["registered_owner_name"],
                document_flags=dict(row["document_flags"]),
                submission_scenario=row["submission_scenario"],
                is_default_demo=bool(row["is_default_demo"]),
                demo_label_en=row["demo_label_en"],
                demo_label_hi=row["demo_label_hi"],
            )
            for row in load("vehicles.json")["vehicles"]
        )

    def all(self) -> tuple[VehicleRecord, ...]:
        return self._records

    def default_demo(self) -> VehicleRecord:
        for record in self._records:
            if record.is_default_demo:
                return record
        raise RuntimeError(
            "vehicles.json must mark exactly one record as is_default_demo"
        )

    def by_id(self, vehicle_id: str) -> VehicleRecord | None:
        for record in self._records:
            if record.id == vehicle_id:
                return record
        return None

    def lookup(
        self, *, registration_no: str, chassis_suffix: str
    ) -> VehicleRecord | None:
        """Both fields must match. Returns None rather than raising.

        A miss is an ordinary, recoverable user outcome -- the caller turns it
        into an inline field error and leaves case state untouched (test T03).
        """
        wanted_reg = _normalise(registration_no)
        wanted_chassis = _normalise(chassis_suffix)
        for record in self._records:
            if (
                _normalise(record.registration_no) == wanted_reg
                and _normalise(record.chassis_suffix) == wanted_chassis
            ):
                return record
        return None
