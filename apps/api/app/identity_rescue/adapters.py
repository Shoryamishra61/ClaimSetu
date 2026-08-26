from __future__ import annotations

from dataclasses import dataclass

from .fixtures import SCENARIOS, ScenarioFixture
from .models import SyntheticRecord


@dataclass(frozen=True, slots=True)
class MockRecordAdapter:
    """Deterministic, in-process substitute for one fictional record authority."""

    authority: str
    records_by_profile: dict[str, SyntheticRecord]

    def get_record(self, profile_id: str) -> SyntheticRecord | None:
        record = self.records_by_profile.get(profile_id)
        return record.model_copy(deep=True) if record else None

    def list_capabilities(self) -> tuple[str, ...]:
        return ("GET_SYNTHETIC_RECORD",)


def _build_adapters() -> dict[str, MockRecordAdapter]:
    records: dict[str, dict[str, SyntheticRecord]] = {}
    for fixture in SCENARIOS.values():
        for record in fixture.records:
            records.setdefault(record.authority, {})[fixture.profile.profile_id] = record
    return {
        authority: MockRecordAdapter(authority, profile_records)
        for authority, profile_records in records.items()
    }


ADAPTERS = _build_adapters()


def load_fixture_records(fixture: ScenarioFixture) -> list[SyntheticRecord]:
    loaded: list[SyntheticRecord] = []
    for expected in fixture.records:
        adapter = ADAPTERS[expected.authority]
        record = adapter.get_record(fixture.profile.profile_id)
        if record is None or record.record_id != expected.record_id:
            raise LookupError(
                f"Synthetic adapter record unavailable: {expected.authority}/{expected.record_id}"
            )
        loaded.append(record)
    return loaded
