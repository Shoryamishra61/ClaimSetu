from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

from .models import (
    CorrectionAction,
    EvidenceStatus,
    FieldValue,
    Goal,
    OfficialHandoff,
    ReadinessState,
    RuleDefinition,
    ScenarioSummary,
    SourceReference,
    SyntheticProfile,
    SyntheticRecord,
)

SOURCES: dict[str, SourceReference] = {
    "SRC-DIGI-001": SourceReference(
        source_id="SRC-DIGI-001",
        title="DigiLocker FAQs",
        publisher="DigiLocker / NeGD",
        url="https://www.digilocker.gov.in/web/about/faq",
        proposition=(
            "DigiLocker says the Aadhaar name should match the name in the DL/RC "
            "database for retrieval and that issued documents are fetched from issuer sources."
        ),
        last_checked_at="2026-08-22",
    ),
    "SRC-UIDAI-001": SourceReference(
        source_id="SRC-UIDAI-001",
        title="Aadhaar Handbook 2026",
        publisher="UIDAI",
        url="https://uidai.gov.in/images/LR_Aadhaar_Handbook_2026.pdf",
        proposition=(
            "UIDAI documents demographic name updates and regional-language handling. "
            "The initial expansion used here is an explicit fictional profile relation, not a UIDAI match decision."
        ),
        last_checked_at="2026-08-22",
    ),
    "SRC-EPFO-001": SourceReference(
        source_id="SRC-EPFO-001",
        title="EPFO Unified Member Portal",
        publisher="Employees' Provident Fund Organisation",
        url="https://unifiedportal-mem.epfindia.gov.in/memberinterface/",
        proposition=(
            "Official destination for EPFO member services, including the Mark Exit workflow."
        ),
        last_checked_at="2026-08-27",
    ),
    "SRC-EPFO-FAQ-001": SourceReference(
        source_id="SRC-EPFO-FAQ-001",
        title="EPFO FAQ — transfer and Date of Exit",
        publisher="Employees' Provident Fund Organisation",
        url="https://www.epfindia.gov.in/site_en/FAQ.php",
        proposition=(
            "EPFO states that Date of Exit for the previous employment is mandatory for an online transfer, "
            "and documents the member self-service Mark Exit route after two months."
        ),
        last_checked_at="2026-08-27",
    ),
    "SRC-UMANG-001": SourceReference(
        source_id="SRC-UMANG-001",
        title="UMANG EPFO services",
        publisher="UMANG / NeGD",
        url="https://web.umang.gov.in/landing/department/epfo.html",
        proposition=(
            "UMANG provides an alternate official access point for EPFO member services "
            "when an EPFO web endpoint is slow or unavailable."
        ),
        last_checked_at="2026-08-23",
    ),
}


RULES: dict[str, RuleDefinition] = {
    rule.rule_id: rule
    for rule in (
        RuleDefinition(
            rule_id="DL-001",
            version="1.0",
            goal=Goal.DIGILOCKER_FETCH_DL,
            input_fields=["DL_SOURCE_DEMO.record_present"],
            predicate_code="RECORD_PRESENT",
            evidence_status=EvidenceStatus.OFFICIAL_SOURCE_DERIVED,
            source_ids=["SRC-DIGI-001"],
            last_checked_at="2026-08-22",
        ),
        RuleDefinition(
            rule_id="DL-002",
            version="1.0",
            goal=Goal.DIGILOCKER_FETCH_DL,
            input_fields=["AADHAAR_DEMO.name", "DL_SOURCE_DEMO.name"],
            predicate_code="CONTROLLED_FULL_NAME_EQUAL",
            evidence_status=EvidenceStatus.OFFICIAL_SOURCE_INTERPRETED,
            source_ids=["SRC-DIGI-001", "SRC-UIDAI-001"],
            last_checked_at="2026-08-22",
        ),
        RuleDefinition(
            rule_id="DL-003",
            version="1.0",
            goal=Goal.DIGILOCKER_FETCH_DL,
            input_fields=["AADHAAR_DEMO.dob", "DL_SOURCE_DEMO.dob"],
            predicate_code="ISO_DATE_EQUAL",
            evidence_status=EvidenceStatus.PROTOTYPE_SIMULATION,
            source_ids=[],
            last_checked_at="2026-08-22",
        ),
        RuleDefinition(
            rule_id="EPFO-001",
            version="1.0",
            goal=Goal.EPFO_KYC_PREFLIGHT,
            input_fields=[
                "AADHAAR_DEMO.name",
                "PAN_DEMO.name",
                "EPFO_DEMO.name",
            ],
            predicate_code="CONTROLLED_FULL_NAME_COMPATIBILITY",
            evidence_status=EvidenceStatus.OFFICIAL_SOURCE_INTERPRETED,
            source_ids=["SRC-EPFO-FAQ-001"],
            last_checked_at="2026-08-22",
        ),
        RuleDefinition(
            rule_id="EPFO-002",
            version="1.0",
            goal=Goal.EPFO_KYC_PREFLIGHT,
            input_fields=[
                "AADHAAR_DEMO.dob",
                "PAN_DEMO.dob",
                "EPFO_DEMO.dob",
            ],
            predicate_code="ISO_DATE_EQUAL",
            evidence_status=EvidenceStatus.OFFICIAL_SOURCE_INTERPRETED,
            source_ids=["SRC-EPFO-FAQ-001"],
            last_checked_at="2026-08-22",
        ),
        RuleDefinition(
            rule_id="EPFO-003",
            version="1.0",
            goal=Goal.EPFO_KYC_PREFLIGHT,
            input_fields=[
                "EPFO_DEMO.date_of_exit",
                "EPFO_DEMO.last_contribution_month",
                "EPFO_DEMO.claim_attempt_date",
            ],
            predicate_code="DATE_OF_EXIT_PRESENT_FOR_TRANSFER",
            evidence_status=EvidenceStatus.OFFICIAL_SOURCE_DERIVED,
            source_ids=["SRC-EPFO-FAQ-001"],
            last_checked_at="2026-08-27",
        ),
        RuleDefinition(
            rule_id="LIFE-001",
            version="1.0",
            goal=Goal.LIFE_EVENT_RECONCILIATION,
            input_fields=["PAN_DEMO.name", "AADHAAR_DEMO.name"],
            predicate_code="NON_BLOCKING_REMAINING_NAME_VARIANT",
            evidence_status=EvidenceStatus.PROTOTYPE_SIMULATION,
            source_ids=[],
            last_checked_at="2026-08-22",
        ),
        RuleDefinition(
            rule_id="LIFE-002",
            version="1.0",
            goal=Goal.LIFE_EVENT_RECONCILIATION,
            input_fields=["AADHAAR_DEMO.name", "DL_SOURCE_DEMO.name"],
            predicate_code="CHOSEN_NAME_TARGET_EQUAL",
            evidence_status=EvidenceStatus.OFFICIAL_SOURCE_INTERPRETED,
            source_ids=["SRC-DIGI-001"],
            last_checked_at="2026-08-22",
        ),
        RuleDefinition(
            rule_id="LIFE-003",
            version="1.0",
            goal=Goal.LIFE_EVENT_RECONCILIATION,
            input_fields=["AADHAAR_DEMO.address", "DL_SOURCE_DEMO.address"],
            predicate_code="UNRELATED_ADDRESS_NON_BLOCKING",
            evidence_status=EvidenceStatus.PROTOTYPE_SIMULATION,
            source_ids=[],
            last_checked_at="2026-08-22",
        ),
    )
}


@dataclass(frozen=True, slots=True)
class ScenarioFixture:
    summary: ScenarioSummary
    fixture_version: str
    profile: SyntheticProfile
    records: tuple[SyntheticRecord, ...]
    known_name_relations: dict[str, str]
    actions: tuple[CorrectionAction, ...]
    dependency_trail_keys: tuple[str, ...]
    official_handoff: OfficialHandoff
    golden_expectations: dict[str, object]


ANANYA = ScenarioFixture(
    summary=ScenarioSummary(
        scenario_id="digilocker-dl",
        goal=Goal.DIGILOCKER_FETCH_DL,
        card_title_key="scenario.dl.title",
        card_body_key="scenario.dl.body",
        recommended_demo=True,
    ),
    fixture_version="1.0",
    profile=SyntheticProfile(
        profile_id="DEMO-ANANYA-01",
        display_name="Ananya R. Krishnan",
        preferred_locale="en-IN",
        scenario_note="profile.ananya.note",
    ),
    records=(
        SyntheticRecord(
            record_id="REC-AADHAAR-ANANYA",
            authority="AADHAAR_DEMO",
            label="Aadhaar demo record",
            fixture_version="1.0",
            fields={
                "name": FieldValue(
                    original="ANANYA R KRISHNAN", script="Latn", locale="en-IN"
                ),
                "dob": FieldValue(original="1998-02-14"),
            },
        ),
        SyntheticRecord(
            record_id="REC-DL-ANANYA",
            authority="DL_SOURCE_DEMO",
            label="Driving Licence source demo record",
            fixture_version="1.0",
            fields={
                "name": FieldValue(
                    original="KRISHNAN ANANYA RAMESH", script="Latn", locale="en-IN"
                ),
                "dob": FieldValue(original="1998-02-14"),
                "record_present": FieldValue(original=True),
            },
        ),
        SyntheticRecord(
            record_id="REC-PAN-ANANYA",
            authority="PAN_DEMO",
            label="PAN demo record",
            fixture_version="1.0",
            fields={
                "name": FieldValue(
                    original="ANANYA RAMESH KRISHNAN", script="Latn", locale="en-IN"
                ),
                "dob": FieldValue(original="1998-02-14"),
            },
        ),
    ),
    known_name_relations={"R": "RAMESH"},
    actions=(
        CorrectionAction(
            action_id="ACT-A1",
            title_key="action.a1.title",
            target_record_id="REC-DL-ANANYA",
            target_field="name",
            from_value="KRISHNAN ANANYA RAMESH",
            to_value="ANANYA RAMESH KRISHNAN",
            effort_key="effort.issuer",
            effect_key="action.a1.effect",
            impact_key="action.a1.impact",
            prerequisite_keys=[],
            affected_goals=[Goal.DIGILOCKER_FETCH_DL],
            affected_record_ids=["REC-DL-ANANYA", "REC-AADHAAR-ANANYA"],
            risk_key="action.a1.impact",
            uncertainty_key="finding.dl.name.uncertainty",
            reversible=True,
            evidence_status=EvidenceStatus.PROTOTYPE_SIMULATION,
            source_ids=["SRC-DIGI-001"],
            cost=45,
        ),
        CorrectionAction(
            action_id="ACT-A2",
            title_key="action.a2.title",
            target_record_id="REC-AADHAAR-ANANYA",
            target_field="name",
            from_value="ANANYA R KRISHNAN",
            to_value="ANANYA RAMESH KRISHNAN",
            effort_key="effort.review",
            effect_key="action.a2.effect",
            impact_key="action.a2.impact",
            prerequisite_keys=[],
            affected_goals=[Goal.DIGILOCKER_FETCH_DL],
            affected_record_ids=["REC-AADHAAR-ANANYA", "REC-DL-ANANYA"],
            risk_key="action.a2.impact",
            uncertainty_key="finding.dl.name.uncertainty",
            reversible=True,
            evidence_status=EvidenceStatus.NEEDS_AUTHORITY_VALIDATION,
            source_ids=["SRC-UIDAI-001", "SRC-DIGI-001"],
            cost=100,
        ),
    ),
    dependency_trail_keys=(
        "trail.dl.1",
        "trail.dl.2",
        "trail.dl.3",
        "trail.dl.4",
        "trail.dl.5",
    ),
    official_handoff=OfficialHandoff(
        title_key="handoff.dl.title",
        step_keys=["handoff.dl.step1", "handoff.dl.step2", "handoff.dl.step3"],
        official_url="https://www.digilocker.gov.in/web/about/faq",
        official_label="DigiLocker official FAQ",
        source_id="SRC-DIGI-001",
    ),
    golden_expectations={
        "initial_readiness": ReadinessState.BLOCKED.value,
        "recommended_actions": ["ACT-A1"],
        "after_actions": {"ACT-A1": ReadinessState.READY_SIMULATION.value},
    },
)


RAVI = ScenarioFixture(
    summary=ScenarioSummary(
        scenario_id="epfo-preflight",
        goal=Goal.EPFO_KYC_PREFLIGHT,
        card_title_key="scenario.epfo.title",
        card_body_key="scenario.epfo.body",
    ),
    fixture_version="1.0",
    profile=SyntheticProfile(
        profile_id="DEMO-RAVI-01",
        display_name="Ravi Kumar",
        preferred_locale="en-IN",
        scenario_note="profile.ravi.note",
    ),
    records=(
        SyntheticRecord(
            record_id="REC-AADHAAR-RAVI",
            authority="AADHAAR_DEMO",
            label="Aadhaar demo record",
            fixture_version="1.0",
            fields={
                "name": FieldValue(original="RAVI KUMAR", script="Latn", locale="en-IN"),
                "dob": FieldValue(original="1998-04-18"),
            },
        ),
        SyntheticRecord(
            record_id="REC-PAN-RAVI",
            authority="PAN_DEMO",
            label="PAN demo record",
            fixture_version="1.0",
            fields={
                "name": FieldValue(
                    original="RAVI K", script="Latn", locale="en-IN"
                ),
                "dob": FieldValue(original="1998-04-18"),
            },
        ),
        SyntheticRecord(
            record_id="REC-EPFO-RAVI",
            authority="EPFO_DEMO",
            label="EPFO member demo record",
            fixture_version="1.0",
            fields={
                "name": FieldValue(original="RAVI K", script="Latn", locale="en-IN"),
                "dob": FieldValue(original="1998-04-18"),
                "aadhaar_linked": FieldValue(original=True),
                "pan_linked": FieldValue(original=True),
                "date_of_exit": FieldValue(original="NOT_RECORDED"),
                "last_contribution_month": FieldValue(original="2026-05"),
                "claim_attempt_date": FieldValue(original="2026-08-20"),
            },
        ),
    ),
    known_name_relations={"K": "KUMAR"},
    actions=(
        CorrectionAction(
            action_id="ACT-B-NAME",
            title_key="action.b_name.title",
            target_record_id="REC-PAN-RAVI",
            target_field="name",
            from_value="RAVI K",
            to_value="RAVI KUMAR",
            effort_key="effort.review",
            effect_key="action.b_name.effect",
            impact_key="action.b_name.impact",
            prerequisite_keys=[],
            affected_goals=[Goal.EPFO_KYC_PREFLIGHT],
            affected_record_ids=["REC-PAN-RAVI", "REC-EPFO-RAVI"],
            risk_key="action.b_name.impact",
            uncertainty_key="finding.epfo.name.uncertainty",
            reversible=True,
            evidence_status=EvidenceStatus.PROTOTYPE_SIMULATION,
            source_ids=["SRC-EPFO-001"],
            cost=30,
        ),
        CorrectionAction(
            action_id="ACT-B1",
            title_key="action.b1.title",
            target_record_id="REC-EPFO-RAVI",
            target_field="date_of_exit",
            from_value="NOT_RECORDED",
            to_value="2026-05-31",
            effort_key="effort.employer",
            effect_key="action.b1.effect",
            impact_key="action.b1.impact",
            prerequisite_keys=[],
            affected_goals=[Goal.EPFO_KYC_PREFLIGHT],
            affected_record_ids=["REC-EPFO-RAVI"],
            risk_key="action.b1.impact",
            uncertainty_key="finding.epfo.history.uncertainty",
            reversible=True,
            evidence_status=EvidenceStatus.OFFICIAL_SOURCE_DERIVED,
            source_ids=["SRC-EPFO-FAQ-001"],
            cost=45,
        ),
    ),
    dependency_trail_keys=(
        "trail.epfo.1",
        "trail.epfo.2",
        "trail.epfo.3",
        "trail.epfo.4",
    ),
    official_handoff=OfficialHandoff(
        title_key="handoff.epfo.title",
        step_keys=["handoff.epfo.step1", "handoff.epfo.step2", "handoff.epfo.step3"],
        official_url="https://unifiedportal-mem.epfindia.gov.in/memberinterface/",
        official_label="EPFO Unified Member Portal",
        source_id="SRC-EPFO-001",
    ),
    golden_expectations={
        "initial_readiness": ReadinessState.NOT_IDENTITY_ISSUE.value,
        "recommended_actions": ["ACT-B1"],
        "after_actions": {
            "ACT-B-NAME": ReadinessState.NOT_IDENTITY_ISSUE.value,
            "ACT-B1": ReadinessState.READY_SIMULATION.value,
        },
    },
)


MEERA = ScenarioFixture(
    summary=ScenarioSummary(
        scenario_id="life-event",
        goal=Goal.LIFE_EVENT_RECONCILIATION,
        card_title_key="scenario.life.title",
        card_body_key="scenario.life.body",
    ),
    fixture_version="1.0",
    profile=SyntheticProfile(
        profile_id="DEMO-MEERA-01",
        display_name="Meera Nair",
        preferred_locale="en-IN",
        scenario_note="profile.meera.note",
    ),
    records=(
        SyntheticRecord(
            record_id="REC-AADHAAR-MEERA",
            authority="AADHAAR_DEMO",
            label="Aadhaar demo record",
            fixture_version="1.0",
            fields={
                "name": FieldValue(original="MEERA NAIR", script="Latn", locale="en-IN"),
                "address": FieldValue(original="BENGALURU, KARNATAKA"),
            },
        ),
        SyntheticRecord(
            record_id="REC-PAN-MEERA",
            authority="PAN_DEMO",
            label="PAN demo record",
            fixture_version="1.0",
            fields={"name": FieldValue(original="MEERA MENON", script="Latn", locale="en-IN")},
        ),
        SyntheticRecord(
            record_id="REC-DL-MEERA",
            authority="DL_SOURCE_DEMO",
            label="Driving Licence source demo record",
            fixture_version="1.0",
            fields={
                "name": FieldValue(original="MEERA MENON", script="Latn", locale="en-IN"),
                "address": FieldValue(original="KOCHI, KERALA"),
            },
        ),
        SyntheticRecord(
            record_id="REC-EPFO-MEERA",
            authority="EPFO_DEMO",
            label="EPFO demo record",
            fixture_version="1.0",
            fields={
                "name": FieldValue(original="MEERA NAIR", script="Latn", locale="en-IN"),
                "kyc_status": FieldValue(original="pending review"),
            },
        ),
    ),
    known_name_relations={},
    actions=(
        CorrectionAction(
            action_id="ACT-C1",
            title_key="action.c1.title",
            target_record_id="REC-DL-MEERA",
            target_field="name",
            from_value="MEERA MENON",
            to_value="MEERA NAIR",
            effort_key="effort.issuer",
            effect_key="action.c1.effect",
            impact_key="action.c1.impact",
            prerequisite_keys=[],
            affected_goals=[Goal.LIFE_EVENT_RECONCILIATION],
            affected_record_ids=["REC-DL-MEERA", "REC-AADHAAR-MEERA"],
            risk_key="action.c1.impact",
            uncertainty_key="finding.life.target.uncertainty",
            reversible=True,
            evidence_status=EvidenceStatus.PROTOTYPE_SIMULATION,
            source_ids=["SRC-DIGI-001"],
            cost=45,
        ),
        CorrectionAction(
            action_id="ACT-C2",
            title_key="action.c2.title",
            target_record_id="REC-PAN-MEERA",
            target_field="name",
            from_value="MEERA MENON",
            to_value="MEERA NAIR",
            effort_key="effort.review",
            effect_key="action.c2.effect",
            impact_key="action.c2.impact",
            prerequisite_keys=[],
            affected_goals=[Goal.LIFE_EVENT_RECONCILIATION],
            affected_record_ids=["REC-PAN-MEERA", "REC-AADHAAR-MEERA"],
            risk_key="action.c2.impact",
            uncertainty_key="finding.life.target.uncertainty",
            reversible=True,
            evidence_status=EvidenceStatus.NEEDS_AUTHORITY_VALIDATION,
            source_ids=[],
            cost=70,
        ),
        CorrectionAction(
            action_id="ACT-C3",
            title_key="action.c3.title",
            target_record_id="REC-DL-MEERA",
            target_field="address",
            from_value="KOCHI, KERALA",
            to_value="BENGALURU, KARNATAKA",
            effort_key="effort.issuer",
            effect_key="action.c3.effect",
            impact_key="action.c3.impact",
            prerequisite_keys=[],
            affected_goals=[Goal.LIFE_EVENT_RECONCILIATION],
            affected_record_ids=["REC-DL-MEERA", "REC-AADHAAR-MEERA"],
            risk_key="action.c3.impact",
            uncertainty_key="finding.life.target.uncertainty",
            reversible=True,
            evidence_status=EvidenceStatus.PROTOTYPE_SIMULATION,
            source_ids=[],
            cost=45,
        ),
    ),
    dependency_trail_keys=(
        "trail.life.1",
        "trail.life.2",
        "trail.life.3",
        "trail.life.4",
    ),
    official_handoff=OfficialHandoff(
        title_key="handoff.life.title",
        step_keys=["handoff.life.step1", "handoff.life.step2", "handoff.life.step3"],
        official_url="https://www.digilocker.gov.in/web/about/faq",
        official_label="DigiLocker official FAQ",
        source_id="SRC-DIGI-001",
    ),
    golden_expectations={
        "initial_readiness": ReadinessState.BLOCKED.value,
        "recommended_actions": ["ACT-C1"],
        "after_actions": {"ACT-C1": ReadinessState.READY_SIMULATION.value},
        "minimum_plan_excludes": ["ACT-C2", "ACT-C3"],
    },
)


SCENARIOS: dict[str, ScenarioFixture] = {
    fixture.summary.scenario_id: fixture for fixture in (ANANYA, RAVI, MEERA)
}


def scenario_copy(scenario_id: str) -> ScenarioFixture:
    return deepcopy(SCENARIOS[scenario_id])
