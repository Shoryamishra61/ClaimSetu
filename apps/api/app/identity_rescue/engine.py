from __future__ import annotations

from itertools import combinations

from .adapters import load_fixture_records
from .fixtures import RULES, SCENARIOS, SOURCES, ScenarioFixture, scenario_copy
from .models import (
    BeforeAfter,
    CorrectionAction,
    EvidenceInput,
    EvidenceStatus,
    Finding,
    FindingState,
    PlanResult,
    ReadinessState,
    RuleDefinition,
    ScenarioAnalysis,
    ScenarioSummary,
    SimulationEvent,
    SourceReference,
    SyntheticRecord,
)
from .normalization import (
    ComparisonResult,
    compare_iso_dates,
    compare_names,
    normalize_text,
)


class ScenarioNotFound(KeyError):
    pass


class InvalidSimulationAction(ValueError):
    pass


def _field(record: SyntheticRecord, field: str) -> str | bool | None:
    value = record.fields.get(field)
    return value.original if value else None


def _record(records: list[SyntheticRecord], record_id: str) -> SyntheticRecord:
    return next(record for record in records if record.record_id == record_id)


def _input(record: SyntheticRecord, field: str, label: str) -> EvidenceInput:
    return EvidenceInput(
        record_id=record.record_id,
        authority=record.authority,
        field=field,
        label=label,
        original_value=_field(record, field),
    )


class IdentityRescueEngine:
    """Pure, deterministic engine. No network, database, clock or model dependency."""

    def list_scenarios(self) -> list[ScenarioSummary]:
        return [fixture.summary for fixture in SCENARIOS.values()]

    def list_sources(self) -> list[SourceReference]:
        return list(SOURCES.values())

    def list_rules(self) -> list[RuleDefinition]:
        return list(RULES.values())

    def analyze(
        self, scenario_id: str, applied_action_ids: list[str] | None = None
    ) -> ScenarioAnalysis:
        try:
            fixture = scenario_copy(scenario_id)
        except KeyError as exc:
            raise ScenarioNotFound(scenario_id) from exc
        action_ids = applied_action_ids or []
        records, before_after = self._apply_actions(fixture, action_ids)
        findings = self._evaluate(fixture, records)
        self._validate_rule_traces(fixture, findings)
        readiness = self._readiness(findings)
        simulation_events = self._simulation_events(fixture, action_ids)
        plan = None if readiness is ReadinessState.READY_SIMULATION else self._plan(fixture, action_ids)
        ready = readiness is ReadinessState.READY_SIMULATION
        prefix = {
            "digilocker-dl": "dl",
            "epfo-preflight": "epfo",
            "life-event": "life",
        }[scenario_id]
        return ScenarioAnalysis(
            scenario_id=scenario_id,
            fixture_version=fixture.fixture_version,
            goal=fixture.summary.goal,
            profile=fixture.profile,
            readiness=readiness,
            headline_key=f"diagnosis.{prefix}.ready" if ready else f"diagnosis.{prefix}.blocked",
            explanation_key=(
                f"diagnosis.{prefix}.ready_explanation"
                if ready
                else f"diagnosis.{prefix}.blocked_explanation"
            ),
            next_best_action_key=(
                "diagnosis.next.official" if ready else "diagnosis.next.compare"
            ),
            records=records,
            findings=findings,
            dependency_trail_keys=list(fixture.dependency_trail_keys),
            actions=list(fixture.actions),
            recommended_plan=plan,
            applied_action_ids=action_ids,
            before_after=before_after,
            simulation_events=simulation_events,
            official_handoff=fixture.official_handoff,
            source_ids=sorted({source for finding in findings for source in finding.source_ids}),
        )

    @staticmethod
    def _validate_rule_traces(
        fixture: ScenarioFixture, findings: list[Finding]
    ) -> None:
        for finding in findings:
            rule = RULES.get(finding.rule_id)
            if rule is None:
                raise LookupError(f"Rule not found: {finding.rule_id}")
            if (
                rule.goal is not fixture.summary.goal
                or finding.rule_version != rule.version
                or finding.evidence_status is not rule.evidence_status
                or finding.source_ids != rule.source_ids
            ):
                raise ValueError(f"Rule trace drift: {finding.rule_id}")

    def simulate(
        self, scenario_id: str, action_id: str, applied_action_ids: list[str] | None = None
    ) -> ScenarioAnalysis:
        fixture = self._fixture(scenario_id)
        allowed = {action.action_id for action in fixture.actions}
        if action_id not in allowed:
            raise InvalidSimulationAction(action_id)
        current = list(applied_action_ids or [])
        if action_id not in current:
            current.append(action_id)
        return self.analyze(scenario_id, current)

    def _fixture(self, scenario_id: str) -> ScenarioFixture:
        try:
            return SCENARIOS[scenario_id]
        except KeyError as exc:
            raise ScenarioNotFound(scenario_id) from exc

    def _apply_actions(
        self, fixture: ScenarioFixture, action_ids: list[str]
    ) -> tuple[list[SyntheticRecord], list[BeforeAfter]]:
        action_map = {action.action_id: action for action in fixture.actions}
        if len(action_ids) != len(set(action_ids)):
            raise InvalidSimulationAction("duplicate action")
        unknown = set(action_ids) - action_map.keys()
        if unknown:
            raise InvalidSimulationAction(sorted(unknown)[0])
        records = load_fixture_records(fixture)
        changes: list[BeforeAfter] = []
        for action_id in action_ids:
            action = action_map[action_id]
            record = _record(records, action.target_record_id)
            field = record.fields[action.target_field]
            before = field.original
            if before != action.from_value:
                raise InvalidSimulationAction(action_id)
            field.original = action.to_value
            changes.append(
                BeforeAfter(
                    action_id=action_id,
                    record_label=record.label,
                    field_label=action.target_field,
                    before=before,
                    after=action.to_value,
                )
            )
        for record in records:
            for value in record.fields.values():
                if isinstance(value.original, str):
                    value.normalized = normalize_text(value.original)
                    value.derived_label = "Comparison form"
        return records, changes

    def _simulation_events(
        self, fixture: ScenarioFixture, action_ids: list[str]
    ) -> list[SimulationEvent]:
        events: list[SimulationEvent] = []
        for index, action_id in enumerate(action_ids, start=1):
            before_records, _ = self._apply_actions(fixture, action_ids[: index - 1])
            after_records, _ = self._apply_actions(fixture, action_ids[:index])
            events.append(
                SimulationEvent(
                    event_id=f"SIM-{fixture.summary.scenario_id}-{index}-{action_id}",
                    sequence=index,
                    scenario_id=fixture.summary.scenario_id,
                    fixture_version=fixture.fixture_version,
                    action_id=action_id,
                    readiness_before=self._readiness(
                        self._evaluate(fixture, before_records)
                    ),
                    readiness_after=self._readiness(
                        self._evaluate(fixture, after_records)
                    ),
                )
            )
        return events

    def _evaluate(
        self, fixture: ScenarioFixture, records: list[SyntheticRecord]
    ) -> list[Finding]:
        if fixture.summary.goal.value == "DIGILOCKER_FETCH_DL":
            return self._evaluate_ananya(fixture, records)
        if fixture.summary.goal.value == "EPFO_KYC_PREFLIGHT":
            return self._evaluate_ravi(fixture, records)
        if fixture.summary.goal.value == "LIFE_EVENT_RECONCILIATION":
            return self._evaluate_meera(records)
        return []

    def _evaluate_ananya(
        self, fixture: ScenarioFixture, records: list[SyntheticRecord]
    ) -> list[Finding]:
        aadhaar = _record(records, "REC-AADHAAR-ANANYA")
        dl = _record(records, "REC-DL-ANANYA")
        record_present = _field(dl, "record_present") is True
        existence = Finding(
            finding_id="FIND-DL-001",
            rule_id="DL-001",
            rule_version="1.0",
            state=(
                FindingState.MATCH_EXACT if record_present else FindingState.NON_IDENTITY_BLOCKER
            ),
            title_key="finding.dl.record_present.title",
            explanation_key="finding.dl.record_present.pass",
            causal=not record_present,
            evidence_status=EvidenceStatus.OFFICIAL_SOURCE_DERIVED,
            inputs=[_input(dl, "record_present", "DL record present in demo issuer source")],
            source_ids=["SRC-DIGI-001"],
        )

        aadhaar_name = str(_field(aadhaar, "name") or "")
        dl_name = str(_field(dl, "name") or "")
        name_result = compare_names(
            aadhaar_name,
            dl_name,
            controlled_relations=fixture.known_name_relations,
        )
        name_passes = name_result in {
            ComparisonResult.EXACT,
            ComparisonResult.RULE_COMPATIBLE,
        }
        name = Finding(
            finding_id="FIND-DL-002",
            rule_id="DL-002",
            rule_version="1.0",
            state=(
                FindingState.MATCH_RULE_COMPATIBLE
                if name_passes
                else FindingState.MISMATCH_BLOCKING
            ),
            title_key=(
                "finding.dl.name.pass_title"
                if name_passes
                else "finding.dl.name.block_title"
            ),
            explanation_key=(
                "finding.dl.name.pass" if name_passes else "finding.dl.name.block"
            ),
            causal=not name_passes,
            evidence_status=EvidenceStatus.OFFICIAL_SOURCE_INTERPRETED,
            inputs=[
                _input(aadhaar, "name", "Aadhaar demo name"),
                _input(dl, "name", "Driving Licence source demo name"),
            ],
            source_ids=["SRC-DIGI-001", "SRC-UIDAI-001"],
            uncertainty_key="finding.dl.name.uncertainty",
        )

        dob_result = compare_iso_dates(
            str(_field(aadhaar, "dob") or ""), str(_field(dl, "dob") or "")
        )
        dob_passes = dob_result is ComparisonResult.EXACT
        dob_state = {
            ComparisonResult.EXACT: FindingState.MATCH_EXACT,
            ComparisonResult.MISSING: FindingState.MISSING_REQUIRED,
            ComparisonResult.REVIEW: FindingState.MISMATCH_REVIEW,
            ComparisonResult.MISMATCH: FindingState.MISMATCH_BLOCKING,
            ComparisonResult.RULE_COMPATIBLE: FindingState.MATCH_RULE_COMPATIBLE,
        }[dob_result]
        dob = Finding(
            finding_id="FIND-DL-003",
            rule_id="DL-003",
            rule_version="1.0",
            state=dob_state,
            title_key="finding.dl.dob.title",
            explanation_key=("finding.dl.dob.pass" if dob_passes else "finding.dl.dob.block"),
            causal=not dob_passes,
            evidence_status=EvidenceStatus.PROTOTYPE_SIMULATION,
            inputs=[
                _input(aadhaar, "dob", "Aadhaar demo date of birth"),
                _input(dl, "dob", "Driving Licence demo date of birth"),
            ],
            source_ids=[],
            uncertainty_key="finding.dl.dob.uncertainty",
        )
        return [existence, name, dob]

    def _evaluate_ravi(
        self, fixture: ScenarioFixture, records: list[SyntheticRecord]
    ) -> list[Finding]:
        aadhaar = _record(records, "REC-AADHAAR-RAVI")
        pan = _record(records, "REC-PAN-RAVI")
        epfo = _record(records, "REC-EPFO-RAVI")
        aadhaar_name = str(_field(aadhaar, "name") or "")
        names_compatible = all(
            compare_names(
                aadhaar_name,
                str(_field(record, "name") or ""),
                controlled_relations=fixture.known_name_relations,
            )
            in {ComparisonResult.EXACT, ComparisonResult.RULE_COMPATIBLE}
            for record in (pan, epfo)
        )
        name = Finding(
            finding_id="FIND-EPFO-001",
            rule_id="EPFO-001",
            rule_version="1.0",
            state=(
                FindingState.VARIANT_NON_BLOCKING
                if names_compatible
                else FindingState.MISMATCH_REVIEW
            ),
            title_key="finding.epfo.name.title",
            explanation_key=(
                "finding.epfo.name.nonblocking"
                if names_compatible
                else "finding.epfo.name.review"
            ),
            causal=False,
            evidence_status=EvidenceStatus.OFFICIAL_SOURCE_INTERPRETED,
            inputs=[
                _input(aadhaar, "name", "Aadhaar demo name"),
                _input(pan, "name", "PAN demo name"),
                _input(epfo, "name", "EPFO demo name"),
            ],
            source_ids=["SRC-EPFO-FAQ-001"],
            uncertainty_key="finding.epfo.name.uncertainty",
        )
        dob_results = [
            compare_iso_dates(
                str(_field(aadhaar, "dob") or ""), str(_field(record, "dob") or "")
            )
            for record in (pan, epfo)
        ]
        dob_passes = all(result is ComparisonResult.EXACT for result in dob_results)
        dob_state = (
            FindingState.MATCH_EXACT
            if dob_passes
            else (
                FindingState.MISSING_REQUIRED
                if ComparisonResult.MISSING in dob_results
                else FindingState.MISMATCH_REVIEW
            )
        )
        dob = Finding(
            finding_id="FIND-EPFO-002",
            rule_id="EPFO-002",
            rule_version="1.0",
            state=dob_state,
            title_key="finding.epfo.dob.title",
            explanation_key="finding.epfo.dob.pass",
            causal=not dob_passes,
            evidence_status=EvidenceStatus.OFFICIAL_SOURCE_INTERPRETED,
            inputs=[_input(record, "dob", f"{record.label} date of birth") for record in (aadhaar, pan, epfo)],
            source_ids=["SRC-EPFO-FAQ-001"],
        )
        exit_date = str(_field(epfo, "date_of_exit") or "")
        service_history_passes = bool(exit_date and exit_date != "NOT_RECORDED")
        service_history = Finding(
            finding_id="FIND-EPFO-003",
            rule_id="EPFO-003",
            rule_version="1.0",
            state=(
                FindingState.MATCH_EXACT
                if service_history_passes
                else FindingState.NON_IDENTITY_BLOCKER
            ),
            title_key=(
                "finding.epfo.history.pass_title"
                if service_history_passes
                else "finding.epfo.history.block_title"
            ),
            explanation_key=(
                "finding.epfo.history.pass"
                if service_history_passes
                else "finding.epfo.history.block"
            ),
            causal=not service_history_passes,
            evidence_status=EvidenceStatus.OFFICIAL_SOURCE_DERIVED,
            inputs=[
                _input(epfo, "date_of_exit", "Fictional date of exit"),
                _input(epfo, "last_contribution_month", "Fictional last contribution month"),
                _input(epfo, "claim_attempt_date", "Fictional transfer attempt date"),
            ],
            source_ids=["SRC-EPFO-FAQ-001"],
            uncertainty_key="finding.epfo.history.uncertainty",
        )
        return [name, service_history, dob]

    def _evaluate_meera(self, records: list[SyntheticRecord]) -> list[Finding]:
        aadhaar = _record(records, "REC-AADHAAR-MEERA")
        pan = _record(records, "REC-PAN-MEERA")
        dl = _record(records, "REC-DL-MEERA")
        chosen_name = str(_field(aadhaar, "name") or "")
        dl_name = str(_field(dl, "name") or "")
        target_passes = (
            compare_names(chosen_name, dl_name) is ComparisonResult.EXACT
        )
        target = Finding(
            finding_id="FIND-LIFE-002",
            rule_id="LIFE-002",
            rule_version="1.0",
            state=(
                FindingState.MATCH_EXACT if target_passes else FindingState.MISMATCH_BLOCKING
            ),
            title_key=(
                "finding.life.target.pass_title"
                if target_passes
                else "finding.life.target.block_title"
            ),
            explanation_key=(
                "finding.life.target.pass"
                if target_passes
                else "finding.life.target.block"
            ),
            causal=not target_passes,
            evidence_status=EvidenceStatus.OFFICIAL_SOURCE_INTERPRETED,
            inputs=[
                _input(aadhaar, "name", "Chosen current name in Aadhaar demo record"),
                _input(dl, "name", "Driving Licence source demo name"),
            ],
            source_ids=["SRC-DIGI-001"],
            uncertainty_key="finding.life.target.uncertainty",
        )
        pan_differs = normalize_text(str(_field(pan, "name") or "")) != normalize_text(chosen_name)
        pan_finding = Finding(
            finding_id="FIND-LIFE-PAN",
            rule_id="LIFE-001",
            rule_version="1.0",
            state=(
                FindingState.VARIANT_NON_BLOCKING if pan_differs else FindingState.MATCH_EXACT
            ),
            title_key="finding.life.pan.title",
            explanation_key="finding.life.pan.nonblocking",
            causal=False,
            evidence_status=EvidenceStatus.PROTOTYPE_SIMULATION,
            inputs=[_input(pan, "name", "PAN demo name")],
            source_ids=[],
        )
        address_differs = normalize_text(str(_field(aadhaar, "address") or "")) != normalize_text(
            str(_field(dl, "address") or "")
        )
        address = Finding(
            finding_id="FIND-LIFE-003",
            rule_id="LIFE-003",
            rule_version="1.0",
            state=(
                FindingState.VARIANT_NON_BLOCKING
                if address_differs
                else FindingState.MATCH_EXACT
            ),
            title_key="finding.life.address.title",
            explanation_key="finding.life.address.nonblocking",
            causal=False,
            evidence_status=EvidenceStatus.PROTOTYPE_SIMULATION,
            inputs=[
                _input(aadhaar, "address", "Aadhaar demo address"),
                _input(dl, "address", "Driving Licence demo address"),
            ],
            source_ids=[],
        )
        return [target, pan_finding, address]

    @staticmethod
    def _readiness(findings: list[Finding]) -> ReadinessState:
        if any(finding.causal and finding.state is FindingState.NON_IDENTITY_BLOCKER for finding in findings):
            return ReadinessState.NOT_IDENTITY_ISSUE
        if any(
            finding.causal
            and finding.state
            in {
                FindingState.MISMATCH_BLOCKING,
                FindingState.MISSING_REQUIRED,
            }
            for finding in findings
        ):
            return ReadinessState.BLOCKED
        if any(
            finding.state in {FindingState.MISMATCH_REVIEW, FindingState.UNKNOWN}
            for finding in findings
        ):
            return ReadinessState.NEEDS_REVIEW
        return ReadinessState.READY_SIMULATION

    def _plan(self, fixture: ScenarioFixture, already_applied: list[str]) -> PlanResult | None:
        remaining = [
            action for action in fixture.actions if action.action_id not in already_applied
        ]
        candidates: list[tuple[int, tuple[CorrectionAction, ...]]] = []
        for length in range(1, len(remaining) + 1):
            for actions in combinations(remaining, length):
                ids = [*already_applied, *(action.action_id for action in actions)]
                try:
                    records, _ = self._apply_actions(fixture, ids)
                except InvalidSimulationAction:
                    continue
                if self._readiness(self._evaluate(fixture, records)) is ReadinessState.READY_SIMULATION:
                    candidates.append((sum(action.cost for action in actions), actions))
        if not candidates:
            return None
        candidates.sort(key=lambda item: (item[0], tuple(action.action_id for action in item[1])))
        best_cost, best_actions = candidates[0]
        equivalent = sum(1 for cost, _ in candidates if cost == best_cost)
        reasons = ["RESOLVES_TARGET"]
        if len(best_actions) == 1:
            reasons.append("ONE_STEP")
        reasons.extend(["NO_NEW_MODELED_BLOCKERS", "LOWER_UPSTREAM_IMPACT"])
        return PlanResult(
            action_ids=[action.action_id for action in best_actions],
            total_cost=best_cost,
            reason_codes=reasons,
            equivalent_plan_count=equivalent,
        )
