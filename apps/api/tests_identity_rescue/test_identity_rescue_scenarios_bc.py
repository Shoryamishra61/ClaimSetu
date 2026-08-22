from __future__ import annotations

from app.identity_rescue.engine import IdentityRescueEngine
from app.identity_rescue.models import FindingState, ReadinessState


def test_epfo_visible_name_variation_is_not_the_causal_blocker() -> None:
    result = IdentityRescueEngine().analyze("epfo-preflight")
    assert result.readiness is ReadinessState.NOT_IDENTITY_ISSUE
    name = next(finding for finding in result.findings if finding.rule_id == "EPFO-001")
    history = next(finding for finding in result.findings if finding.rule_id == "EPFO-003")
    assert name.state is FindingState.VARIANT_NON_BLOCKING
    assert name.causal is False
    assert history.state is FindingState.NON_IDENTITY_BLOCKER
    assert history.causal is True
    assert result.recommended_plan is not None
    assert result.recommended_plan.action_ids == ["ACT-B1"]


def test_epfo_name_only_change_does_not_unblock_service_history() -> None:
    result = IdentityRescueEngine().simulate("epfo-preflight", "ACT-B-NAME")
    assert result.readiness is ReadinessState.NOT_IDENTITY_ISSUE
    assert any(
        finding.rule_id == "EPFO-003" and finding.causal for finding in result.findings
    )


def test_epfo_causal_service_history_action_recomputes_ready() -> None:
    result = IdentityRescueEngine().simulate("epfo-preflight", "ACT-B1")
    assert result.readiness is ReadinessState.READY_SIMULATION
    assert result.before_after[0].field_label == "date_of_exit"


def test_life_event_planner_selects_only_dl_name_for_selected_goal() -> None:
    result = IdentityRescueEngine().analyze("life-event")
    assert result.readiness is ReadinessState.BLOCKED
    assert result.recommended_plan is not None
    assert result.recommended_plan.action_ids == ["ACT-C1"]
    assert "ACT-C2" not in result.recommended_plan.action_ids
    assert "ACT-C3" not in result.recommended_plan.action_ids


def test_life_event_minimum_plan_leaves_unrelated_address_unchanged() -> None:
    result = IdentityRescueEngine().simulate("life-event", "ACT-C1")
    assert result.readiness is ReadinessState.READY_SIMULATION
    dl = next(record for record in result.records if record.record_id == "REC-DL-MEERA")
    assert dl.fields["name"].original == "MEERA NAIR"
    assert dl.fields["address"].original == "KOCHI, KERALA"
    address = next(finding for finding in result.findings if finding.rule_id == "LIFE-003")
    assert address.state is FindingState.VARIANT_NON_BLOCKING
    assert address.causal is False


def test_scenario_catalog_is_exactly_three_locked_goals() -> None:
    summaries = IdentityRescueEngine().list_scenarios()
    assert [summary.scenario_id for summary in summaries] == [
        "digilocker-dl",
        "epfo-preflight",
        "life-event",
    ]
