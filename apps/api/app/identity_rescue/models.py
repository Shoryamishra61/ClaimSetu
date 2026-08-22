from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Goal(str, Enum):
    DIGILOCKER_FETCH_DL = "DIGILOCKER_FETCH_DL"
    EPFO_KYC_PREFLIGHT = "EPFO_KYC_PREFLIGHT"
    LIFE_EVENT_RECONCILIATION = "LIFE_EVENT_RECONCILIATION"


class FindingState(str, Enum):
    MATCH_EXACT = "MATCH_EXACT"
    MATCH_RULE_COMPATIBLE = "MATCH_RULE_COMPATIBLE"
    VARIANT_NON_BLOCKING = "VARIANT_NON_BLOCKING"
    MISMATCH_BLOCKING = "MISMATCH_BLOCKING"
    MISMATCH_REVIEW = "MISMATCH_REVIEW"
    MISSING_REQUIRED = "MISSING_REQUIRED"
    NON_IDENTITY_BLOCKER = "NON_IDENTITY_BLOCKER"
    UNKNOWN = "UNKNOWN"


class ReadinessState(str, Enum):
    READY_SIMULATION = "READY_SIMULATION"
    BLOCKED = "BLOCKED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    NOT_IDENTITY_ISSUE = "NOT_IDENTITY_ISSUE"


class EvidenceStatus(str, Enum):
    OFFICIAL_SOURCE_DERIVED = "OFFICIAL_SOURCE_DERIVED"
    OFFICIAL_SOURCE_INTERPRETED = "OFFICIAL_SOURCE_INTERPRETED"
    PROTOTYPE_SIMULATION = "PROTOTYPE_SIMULATION"
    NEEDS_AUTHORITY_VALIDATION = "NEEDS_AUTHORITY_VALIDATION"


class FieldValue(StrictModel):
    original: str | bool | None
    normalized: str | None = None
    script: str | None = None
    locale: str | None = None
    derived_label: str | None = None


class SyntheticRecord(StrictModel):
    record_id: str
    authority: str
    label: str
    fixture_version: str
    fields: dict[str, FieldValue]


class SyntheticProfile(StrictModel):
    profile_id: str
    display_name: str
    fictional: bool = True
    preferred_locale: str
    scenario_note: str


class SourceReference(StrictModel):
    source_id: str
    title: str
    publisher: str
    url: str
    proposition: str
    last_checked_at: str


class RuleDefinition(StrictModel):
    rule_id: str
    version: str
    goal: Goal
    input_fields: list[str]
    predicate_code: str
    evidence_status: EvidenceStatus
    source_ids: list[str]
    last_checked_at: str


class EvidenceInput(StrictModel):
    record_id: str
    authority: str
    field: str
    label: str
    original_value: str | bool | None


class Finding(StrictModel):
    finding_id: str
    rule_id: str
    rule_version: str
    state: FindingState
    title_key: str
    explanation_key: str
    causal: bool
    evidence_status: EvidenceStatus
    inputs: list[EvidenceInput]
    source_ids: list[str]
    uncertainty_key: str | None = None


class CorrectionAction(StrictModel):
    action_id: str
    title_key: str
    target_record_id: str
    target_field: str
    from_value: str | bool | None
    to_value: str | bool | None
    effort_key: str
    effect_key: str
    impact_key: str
    prerequisite_keys: list[str]
    affected_goals: list[Goal]
    affected_record_ids: list[str]
    risk_key: str
    uncertainty_key: str
    reversible: bool
    evidence_status: EvidenceStatus
    source_ids: list[str]
    cost: int = Field(ge=0)


class PlanResult(StrictModel):
    action_ids: list[str]
    total_cost: int
    reason_codes: list[str]
    equivalent_plan_count: int = Field(ge=1)


class OfficialHandoff(StrictModel):
    title_key: str
    step_keys: list[str]
    official_url: str
    official_label: str
    source_id: str
    caveat_key: str = "handoff.processes_change"


class BeforeAfter(StrictModel):
    action_id: str
    record_label: str
    field_label: str
    before: str | bool | None
    after: str | bool | None


class SimulationEvent(StrictModel):
    event_id: str
    sequence: int = Field(ge=1)
    scenario_id: str
    fixture_version: str
    action_id: str
    readiness_before: ReadinessState
    readiness_after: ReadinessState


class ScenarioSummary(StrictModel):
    scenario_id: str
    goal: Goal
    card_title_key: str
    card_body_key: str
    recommended_demo: bool = False


class ScenarioAnalysis(StrictModel):
    scenario_id: str
    fixture_version: str
    goal: Goal
    profile: SyntheticProfile
    readiness: ReadinessState
    headline_key: str
    explanation_key: str
    next_best_action_key: str
    records: list[SyntheticRecord]
    findings: list[Finding]
    dependency_trail_keys: list[str]
    actions: list[CorrectionAction]
    recommended_plan: PlanResult | None
    applied_action_ids: list[str]
    before_after: list[BeforeAfter]
    simulation_events: list[SimulationEvent]
    official_handoff: OfficialHandoff
    source_ids: list[str]
    deterministic: bool = True
    government_systems_contacted: int = 0


class AnalyzeRequest(StrictModel):
    applied_action_ids: list[str] = Field(default_factory=list, max_length=10)


class SimulateRequest(AnalyzeRequest):
    action_id: str = Field(min_length=1, max_length=80)
