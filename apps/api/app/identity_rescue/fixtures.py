from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

from .models import (
    CorrectionAction,
    EvidenceStatus,
    FieldValue,
    Goal,
    OfficialHandoff,
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
        title="Enrolment and Update FAQ",
        publisher="UIDAI",
        url="https://uidai.gov.in/en/295-faqs/enrolment-update.html",
        proposition=(
            "UIDAI guidance discusses full names, initials and variation across documentary proofs."
        ),
        last_checked_at="2026-08-22",
    ),
    "SRC-EPFO-001": SourceReference(
        source_id="SRC-EPFO-001",
        title="FAQ on UAN and KYC",
        publisher="Employees' Provident Fund Organisation",
        url="https://www.epfindia.gov.in/site_docs/PDFs/Circulars/Y2020-2021/FAQUANKYC.pdf",
        proposition=(
            "EPFO guidance describes name alignment for KYC and date-of-exit workflows. "
            "The exact service-history predicate in this demo remains a prototype simulation."
        ),
        last_checked_at="2026-08-22",
    ),
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
)


ARVIND = ScenarioFixture(
    summary=ScenarioSummary(
        scenario_id="epfo-preflight",
        goal=Goal.EPFO_KYC_PREFLIGHT,
        card_title_key="scenario.epfo.title",
        card_body_key="scenario.epfo.body",
    ),
    fixture_version="1.0",
    profile=SyntheticProfile(
        profile_id="DEMO-ARVIND-01",
        display_name="Arvind N. Iyer",
        preferred_locale="en-IN",
        scenario_note="profile.arvind.note",
    ),
    records=(
        SyntheticRecord(
            record_id="REC-AADHAAR-ARVIND",
            authority="AADHAAR_DEMO",
            label="Aadhaar demo record",
            fixture_version="1.0",
            fields={
                "name": FieldValue(original="ARVIND N IYER", script="Latn", locale="en-IN"),
                "dob": FieldValue(original="1989-07-11"),
            },
        ),
        SyntheticRecord(
            record_id="REC-PAN-ARVIND",
            authority="PAN_DEMO",
            label="PAN demo record",
            fixture_version="1.0",
            fields={
                "name": FieldValue(
                    original="ARVIND NARAYAN IYER", script="Latn", locale="en-IN"
                ),
                "dob": FieldValue(original="1989-07-11"),
            },
        ),
        SyntheticRecord(
            record_id="REC-EPFO-ARVIND",
            authority="EPFO_DEMO",
            label="EPFO member demo record",
            fixture_version="1.0",
            fields={
                "name": FieldValue(original="ARVIND N IYER", script="Latn", locale="en-IN"),
                "dob": FieldValue(original="1989-07-11"),
                "aadhaar_linked": FieldValue(original=True),
                "pan_linked": FieldValue(original=True),
                "date_of_exit": FieldValue(original="2026-08-31"),
                "last_contribution_month": FieldValue(original="2026-07"),
                "claim_attempt_date": FieldValue(original="2026-08-20"),
            },
        ),
    ),
    known_name_relations={"N": "NARAYAN"},
    actions=(
        CorrectionAction(
            action_id="ACT-B-NAME",
            title_key="action.b_name.title",
            target_record_id="REC-PAN-ARVIND",
            target_field="name",
            from_value="ARVIND NARAYAN IYER",
            to_value="ARVIND N IYER",
            effort_key="effort.review",
            effect_key="action.b_name.effect",
            impact_key="action.b_name.impact",
            reversible=True,
            evidence_status=EvidenceStatus.PROTOTYPE_SIMULATION,
            source_ids=["SRC-EPFO-001"],
            cost=30,
        ),
        CorrectionAction(
            action_id="ACT-B1",
            title_key="action.b1.title",
            target_record_id="REC-EPFO-ARVIND",
            target_field="date_of_exit",
            from_value="2026-08-31",
            to_value="2026-07-31",
            effort_key="effort.employer",
            effect_key="action.b1.effect",
            impact_key="action.b1.impact",
            reversible=True,
            evidence_status=EvidenceStatus.PROTOTYPE_SIMULATION,
            source_ids=["SRC-EPFO-001"],
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
        official_url="https://www.epfindia.gov.in/site_docs/PDFs/Circulars/Y2020-2021/FAQUANKYC.pdf",
        official_label="EPFO official UAN and KYC FAQ",
        source_id="SRC-EPFO-001",
    ),
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
)


SCENARIOS: dict[str, ScenarioFixture] = {
    fixture.summary.scenario_id: fixture for fixture in (ANANYA, ARVIND, MEERA)
}


def scenario_copy(scenario_id: str) -> ScenarioFixture:
    return deepcopy(SCENARIOS[scenario_id])
