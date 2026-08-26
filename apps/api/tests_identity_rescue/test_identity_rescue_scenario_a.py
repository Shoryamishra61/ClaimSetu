from __future__ import annotations

from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from app.config import load_settings
from app.identity_rescue.engine import IdentityRescueEngine, InvalidSimulationAction
from app.identity_rescue.models import FindingState, ReadinessState
from app.identity_rescue.normalization import (
    expand_controlled_tokens,
    name_tokens,
    normalize_text,
)
from app.main import create_app


def test_normalization_preserves_original_and_is_conservative() -> None:
    original = "ANANYA  R.   KRISHNAN"
    assert normalize_text(original) == "ananya r krishnan"
    assert original == "ANANYA  R.   KRISHNAN"


def test_initial_never_expands_without_fixture_relation() -> None:
    tokens = name_tokens("ANANYA R KRISHNAN")
    assert expand_controlled_tokens(tokens, {}) == ("ananya", "r", "krishnan")
    assert expand_controlled_tokens(tokens, {"R": "RAMESH"}) == (
        "ananya",
        "ramesh",
        "krishnan",
    )


def test_scenario_a_starts_blocked_with_traceable_causal_name_finding() -> None:
    result = IdentityRescueEngine().analyze("digilocker-dl")
    assert result.readiness is ReadinessState.BLOCKED
    name = next(finding for finding in result.findings if finding.rule_id == "DL-002")
    assert name.state is FindingState.MISMATCH_BLOCKING
    assert name.causal is True
    assert {item.original_value for item in name.inputs} == {
        "ANANYA R KRISHNAN",
        "KRISHNAN ANANYA RAMESH",
    }
    assert name.source_ids == ["SRC-DIGI-001", "SRC-UIDAI-001"]


def test_scenario_a_planner_selects_narrow_issuer_change() -> None:
    result = IdentityRescueEngine().analyze("digilocker-dl")
    assert result.recommended_plan is not None
    assert result.recommended_plan.action_ids == ["ACT-A1"]
    assert result.recommended_plan.total_cost == 45
    assert "LOWER_UPSTREAM_IMPACT" in result.recommended_plan.reason_codes


def test_scenario_a_simulation_recomputes_to_ready_and_preserves_before_after() -> None:
    result = IdentityRescueEngine().simulate("digilocker-dl", "ACT-A1")
    assert result.readiness is ReadinessState.READY_SIMULATION
    assert result.government_systems_contacted == 0
    assert result.applied_action_ids == ["ACT-A1"]
    assert result.before_after[0].before == "KRISHNAN ANANYA RAMESH"
    assert result.before_after[0].after == "ANANYA RAMESH KRISHNAN"


def test_broad_upstream_change_does_not_create_false_readiness() -> None:
    result = IdentityRescueEngine().simulate("digilocker-dl", "ACT-A2")
    assert result.readiness is ReadinessState.BLOCKED


def test_arbitrary_or_duplicate_actions_fail_closed() -> None:
    engine = IdentityRescueEngine()
    with pytest.raises(InvalidSimulationAction):
        engine.simulate("digilocker-dl", "ACT-NOT-ALLOWED")
    with pytest.raises(InvalidSimulationAction):
        engine.analyze("digilocker-dl", ["ACT-A1", "ACT-A1"])


def test_default_openapi_is_identity_rescue_only() -> None:
    identity_settings = replace(load_settings(), enable_historical_blueprint=False)
    with TestClient(create_app(identity_settings)) as client:
        paths = set(client.get("/openapi.json").json()["paths"])
        assert paths == {
            "/healthz",
            "/api/v1/identity/scenarios",
            "/api/v1/identity/scenarios/{scenario_id}/analyze",
            "/api/v1/identity/scenarios/{scenario_id}/simulate",
            "/api/v1/identity/sources",
        }
        result = client.post(
            "/api/v1/identity/scenarios/digilocker-dl/analyze",
            json={"applied_action_ids": []},
        )
        assert result.status_code == 200
        assert result.json()["readiness"] == "BLOCKED"
        health = client.get("/healthz").json()
        assert health["product"] == "Identity Rescue"
        assert health["live_government_integrations"] == 0
