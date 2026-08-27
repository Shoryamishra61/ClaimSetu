from __future__ import annotations

from dataclasses import replace
from urllib.parse import urlparse

from fastapi.testclient import TestClient

from app.config import load_settings
from app.identity_rescue.engine import IdentityRescueEngine
from app.identity_rescue.models import (
    EvidenceStatus,
    Finding,
    FindingState,
    ReadinessState,
)
from app.identity_rescue.normalization import name_tokens, normalize_text
from app.main import create_app

EXPECTED_SOURCE_HOSTS = {
    "www.digilocker.gov.in",
    "uidai.gov.in",
    "www.epfindia.gov.in",
    "unifiedportal-mem.epfindia.gov.in",
    "web.umang.gov.in",
}


def _client() -> TestClient:
    settings = replace(
        load_settings(),
        serve_frontend=False,
        enable_historical_blueprint=False,
    )
    return TestClient(create_app(settings))


def test_normalization_never_infers_structure_or_fuzzy_identity() -> None:
    assert name_tokens("M. S. SUBBULAKSHMI") == ("m", "s", "subbulakshmi")
    assert name_tokens("PRIYA") == ("priya",)
    assert name_tokens("PRIYA DEVI SINGH") == ("priya", "devi", "singh")
    assert normalize_text("PRIYA MENON") != normalize_text("PRIYA MEHRA")
    assert name_tokens("KRISHNAN ANANYA RAMESH") != name_tokens(
        "ANANYA RAMESH KRISHNAN"
    )


def test_every_finding_is_traceable_and_preserves_original_values() -> None:
    engine = IdentityRescueEngine()
    source_ids = {source.source_id for source in engine.list_sources()}
    for summary in engine.list_scenarios():
        result = engine.analyze(summary.scenario_id)
        for record in result.records:
            for value in record.fields.values():
                if isinstance(value.original, str):
                    assert value.normalized is not None
        for finding in result.findings:
            assert finding.rule_id
            assert finding.rule_version
            assert finding.title_key
            assert finding.explanation_key
            assert set(finding.source_ids) <= source_ids
            assert all(item.original_value is not None for item in finding.inputs)


def test_unknown_or_review_finding_cannot_become_ready() -> None:
    finding = Finding(
        finding_id="FIND-TEST",
        rule_id="TEST-001",
        rule_version="1.0",
        state=FindingState.UNKNOWN,
        title_key="test.title",
        explanation_key="test.explanation",
        causal=False,
        evidence_status=EvidenceStatus.NEEDS_AUTHORITY_VALIDATION,
        inputs=[],
        source_ids=[],
    )
    assert IdentityRescueEngine._readiness([finding]) is ReadinessState.NEEDS_REVIEW


def test_official_links_are_registry_allowlisted_https_urls() -> None:
    engine = IdentityRescueEngine()
    sources = {source.source_id: source for source in engine.list_sources()}
    for source in sources.values():
        parsed = urlparse(source.url)
        assert parsed.scheme == "https"
        assert parsed.hostname in EXPECTED_SOURCE_HOSTS
        assert source.publisher
        assert source.proposition
        assert source.last_checked_at
    for scenario in engine.list_scenarios():
        handoff = engine.analyze(scenario.scenario_id).official_handoff
        assert handoff.source_id in sources
        assert handoff.official_url == sources[handoff.source_id].url


def test_api_rejects_unknown_mutations_and_oversized_action_lists() -> None:
    with _client() as client:
        unknown = client.post(
            "/api/v1/identity/scenarios/digilocker-dl/simulate",
            json={"action_id": "ACT-INJECTED", "applied_action_ids": []},
        )
        assert unknown.status_code == 422
        oversized = client.post(
            "/api/v1/identity/scenarios/digilocker-dl/analyze",
            json={"applied_action_ids": [f"ACT-{index}" for index in range(11)]},
        )
        assert oversized.status_code == 422


def test_security_headers_and_machine_readable_trust_boundary() -> None:
    with _client() as client:
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.headers["x-content-type-options"] == "nosniff"
        assert response.headers["x-frame-options"] == "DENY"
        assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
        assert response.headers["strict-transport-security"].startswith("max-age=")
        body = response.json()
        assert body["live_government_integrations"] == 0
        assert body["ai_required"] is False
        analysis = client.post(
            "/api/v1/identity/scenarios/digilocker-dl/analyze",
            json={"applied_action_ids": []},
        ).json()
        assert analysis["government_systems_contacted"] == 0
        missing = client.get("/not-a-real-route")
        assert missing.status_code == 404
        assert missing.json()["error"]["code"] == "ROUTE_NOT_FOUND"
        assert "handover" not in missing.text.casefold()


def test_fictional_test_case_contract_runs_and_recomputes_on_the_backend() -> None:
    sample = {
        "schema_version": "claimpath-test-case.v1",
        "fictional": True,
        "aadhaar_linked_name": "RAVI KUMAR",
        "epfo_name": "RAVI K",
        "name_relation_confirmed": True,
        "date_of_exit": None,
        "proposed_exit_date": "2026-05-31",
        "mark_exit_waiting_period_met": True,
    }
    with _client() as client:
        blocked = client.post(
            "/api/v1/identity/test-case/analyze",
            json={"case": sample, "apply_suggested_fix": False},
        )
        assert blocked.status_code == 200
        assert blocked.json()["status"] == "BLOCKED_DATE_OF_EXIT"
        assert blocked.json()["government_systems_contacted"] == 0
        assert blocked.json()["execution_mode"] == "FASTAPI_DETERMINISTIC_ENGINE"

        resolved = client.post(
            "/api/v1/identity/test-case/analyze",
            json={"case": sample, "apply_suggested_fix": True},
        )
        assert resolved.status_code == 200
        assert resolved.json()["status"] == "PREREQUISITE_MET"
        assert resolved.json()["date_of_exit_after"] == "2026-05-31"
        assert resolved.json()["name_change_recommended"] is False


def test_fictional_test_case_rejects_identifiers_and_unsafe_inference() -> None:
    sample = {
        "schema_version": "claimpath-test-case.v1",
        "fictional": True,
        "aadhaar_linked_name": "MEERA SHAH",
        "epfo_name": "MEERA S",
        "name_relation_confirmed": False,
        "date_of_exit": None,
        "proposed_exit_date": "2026-05-31",
        "mark_exit_waiting_period_met": True,
    }
    with _client() as client:
        review = client.post(
            "/api/v1/identity/test-case/analyze",
            json={"case": sample},
        )
        assert review.status_code == 200
        assert review.json()["status"] == "NEEDS_REVIEW"
        assert review.json()["name_change_recommended"] is False

        sample["uan"] = "100000000000"
        rejected = client.post(
            "/api/v1/identity/test-case/analyze",
            json={"case": sample},
        )
        assert rejected.status_code == 422

        del sample["uan"]
        sample["epfo_name"] = "100000000000"
        rejected_name = client.post(
            "/api/v1/identity/test-case/analyze",
            json={"case": sample},
        )
        assert rejected_name.status_code == 422
