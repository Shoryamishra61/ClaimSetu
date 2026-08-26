from __future__ import annotations

from time import perf_counter

import pytest

from app.identity_rescue.adapters import ADAPTERS, load_fixture_records
from app.identity_rescue.engine import IdentityRescueEngine
from app.identity_rescue.fixtures import RULES, SCENARIOS
from app.identity_rescue.models import ReadinessState
from app.identity_rescue.normalization import (
    ComparisonResult,
    compare_iso_dates,
    compare_names,
    name_tokens,
)


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        ("ANANYA  R   KRISHNAN", "ANANYA R KRISHNAN", ComparisonResult.EXACT),
        ("ANANYA R. KRISHNAN", "ANANYA R KRISHNAN", ComparisonResult.EXACT),
        ("PRIYA", "PRIYA", ComparisonResult.EXACT),
        ("ANANYA ROY CHOUDHARY", "ANANYA ROY CHOUDHARY", ComparisonResult.EXACT),
        ("PRIYA MENON", "PRIYA MEHRA", ComparisonResult.MISMATCH),
        ("1990-08-07", "1990-07-08", ComparisonResult.MISMATCH),
    ],
)
def test_exact_and_genuine_difference_matrix(
    left: str, right: str, expected: ComparisonResult
) -> None:
    if left[0].isdigit():
        assert compare_iso_dates(left, right) is expected
    else:
        assert compare_names(left, right) is expected


def test_initials_require_an_explicit_fixture_relation() -> None:
    assert (
        compare_names("ANANYA R KRISHNAN", "ANANYA RAMESH KRISHNAN")
        is ComparisonResult.REVIEW
    )
    assert (
        compare_names(
            "ANANYA R KRISHNAN",
            "ANANYA RAMESH KRISHNAN",
            controlled_relations={"R": "RAMESH"},
        )
        is ComparisonResult.RULE_COMPATIBLE
    )


def test_token_order_is_rule_scoped_not_global() -> None:
    left = "KRISHNAN ANANYA RAMESH"
    right = "ANANYA RAMESH KRISHNAN"
    assert compare_names(left, right) is ComparisonResult.MISMATCH
    assert (
        compare_names(left, right, allow_token_reorder=True)
        is ComparisonResult.RULE_COMPATIBLE
    )


def test_local_script_requires_a_controlled_transliteration_pair() -> None:
    tamil = "மீரா நாயர்"
    latin = "MEERA NAIR"
    assert compare_names(tamil, latin) is ComparisonResult.REVIEW
    assert (
        compare_names(
            tamil,
            latin,
            controlled_transliterations={(tamil, latin)},
        )
        is ComparisonResult.RULE_COMPATIBLE
    )


def test_name_model_does_not_invent_surname_structure() -> None:
    assert name_tokens("PRIYA") == ("priya",)
    assert name_tokens("ANANYA ROY CHOUDHARY") == (
        "ananya",
        "roy",
        "choudhary",
    )


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        ("1990-08-07", "1990-08-07", ComparisonResult.EXACT),
        ("07/08/1990", "1990-08-07", ComparisonResult.REVIEW),
        (None, "1990-08-07", ComparisonResult.MISSING),
        ("1990-13-01", "1990-13-01", ComparisonResult.REVIEW),
    ],
)
def test_dates_are_never_reinterpreted(
    left: str | None, right: str | None, expected: ComparisonResult
) -> None:
    assert compare_iso_dates(left, right) is expected


def test_mock_adapters_are_deterministic_isolated_and_network_free() -> None:
    for fixture in SCENARIOS.values():
        loaded_once = load_fixture_records(fixture)
        loaded_twice = load_fixture_records(fixture)
        assert loaded_once == loaded_twice
        assert loaded_once is not loaded_twice
        assert [record.record_id for record in loaded_once] == [
            record.record_id for record in fixture.records
        ]
        for record in loaded_once:
            adapter = ADAPTERS[record.authority]
            assert adapter.list_capabilities() == ("GET_SYNTHETIC_RECORD",)


def test_fixture_expectations_are_separate_and_match_engine_results() -> None:
    engine = IdentityRescueEngine()
    for scenario_id, fixture in SCENARIOS.items():
        initial = engine.analyze(scenario_id)
        expected = fixture.golden_expectations
        assert initial.readiness.value == expected["initial_readiness"]
        assert initial.recommended_plan is not None
        assert initial.recommended_plan.action_ids == expected["recommended_actions"]
        for action_id, readiness in expected["after_actions"].items():
            assert engine.simulate(scenario_id, action_id).readiness.value == readiness


def test_rule_registry_covers_every_trace_and_has_current_provenance() -> None:
    engine = IdentityRescueEngine()
    sources = {source.source_id for source in engine.list_sources()}
    for rule in RULES.values():
        assert rule.version
        assert rule.input_fields
        assert rule.predicate_code
        assert rule.last_checked_at >= "2026-08-22"
        assert set(rule.source_ids) <= sources
    for fixture in SCENARIOS.values():
        for finding in engine.analyze(fixture.summary.scenario_id).findings:
            rule = RULES[finding.rule_id]
            assert finding.rule_version == rule.version
            assert finding.evidence_status is rule.evidence_status
            assert finding.source_ids == rule.source_ids


def test_actions_have_complete_bounded_metadata() -> None:
    source_ids = {source.source_id for source in IdentityRescueEngine().list_sources()}
    for fixture in SCENARIOS.values():
        record_ids = {record.record_id for record in fixture.records}
        for action in fixture.actions:
            assert action.target_record_id in record_ids
            assert set(action.affected_record_ids) <= record_ids
            assert action.affected_goals
            assert action.risk_key
            assert action.uncertainty_key
            assert set(action.source_ids) <= source_ids
            assert action.cost >= 0


def test_simulation_event_journal_is_deterministic_and_replayable() -> None:
    engine = IdentityRescueEngine()
    first = engine.simulate("digilocker-dl", "ACT-A1")
    second = engine.simulate("digilocker-dl", "ACT-A1")
    assert first.simulation_events == second.simulation_events
    assert len(first.simulation_events) == 1
    event = first.simulation_events[0]
    assert event.event_id == "SIM-digilocker-dl-1-ACT-A1"
    assert event.readiness_before is ReadinessState.BLOCKED
    assert event.readiness_after is ReadinessState.READY_SIMULATION
    assert "ANANYA" not in event.model_dump_json()


def test_deterministic_analysis_is_well_inside_300ms_target() -> None:
    engine = IdentityRescueEngine()
    durations: list[float] = []
    for scenario_id in SCENARIOS:
        for _ in range(20):
            started = perf_counter()
            engine.analyze(scenario_id)
            durations.append(perf_counter() - started)
    assert max(durations) < 0.3
