export type ReadinessState =
  | "READY_SIMULATION"
  | "BLOCKED"
  | "NEEDS_REVIEW"
  | "NOT_IDENTITY_ISSUE";
export type FindingState =
  | "MATCH_EXACT"
  | "MATCH_RULE_COMPATIBLE"
  | "VARIANT_NON_BLOCKING"
  | "MISMATCH_BLOCKING"
  | "MISMATCH_REVIEW"
  | "MISSING_REQUIRED"
  | "NON_IDENTITY_BLOCKER"
  | "UNKNOWN";

export interface FieldValue {
  original: string | boolean | null;
  normalized: string | null;
  script: string | null;
  locale: string | null;
  derived_label: string | null;
}
export interface SyntheticRecord {
  record_id: string;
  authority: string;
  label: string;
  fixture_version: string;
  fields: Record<string, FieldValue>;
}
export interface SyntheticProfile {
  profile_id: string;
  display_name: string;
  fictional: boolean;
  preferred_locale: string;
  scenario_note: string;
}
export interface SourceReference {
  source_id: string;
  title: string;
  publisher: string;
  url: string;
  proposition: string;
  last_checked_at: string;
}
export interface EvidenceInput {
  record_id: string;
  authority: string;
  field: string;
  label: string;
  original_value: string | boolean | null;
}
export interface Finding {
  finding_id: string;
  rule_id: string;
  rule_version: string;
  state: FindingState;
  title_key: string;
  explanation_key: string;
  causal: boolean;
  evidence_status: string;
  inputs: EvidenceInput[];
  source_ids: string[];
  uncertainty_key: string | null;
}
export interface CorrectionAction {
  action_id: string;
  title_key: string;
  target_record_id: string;
  target_field: string;
  from_value: string | boolean | null;
  to_value: string | boolean | null;
  effort_key: string;
  effect_key: string;
  impact_key: string;
  prerequisite_keys: string[];
  affected_goals: string[];
  affected_record_ids: string[];
  risk_key: string;
  uncertainty_key: string;
  reversible: boolean;
  evidence_status: string;
  source_ids: string[];
  cost: number;
}
export interface PlanResult {
  action_ids: string[];
  total_cost: number;
  reason_codes: string[];
  equivalent_plan_count: number;
}
export interface OfficialHandoff {
  title_key: string;
  step_keys: string[];
  official_url: string;
  official_label: string;
  source_id: string;
  caveat_key: string;
}
export interface BeforeAfter {
  action_id: string;
  record_label: string;
  field_label: string;
  before: string | boolean | null;
  after: string | boolean | null;
}
export interface SimulationEvent {
  event_id: string;
  sequence: number;
  scenario_id: string;
  fixture_version: string;
  action_id: string;
  readiness_before: ReadinessState;
  readiness_after: ReadinessState;
}
export interface ScenarioSummary {
  scenario_id: string;
  goal: string;
  card_title_key: string;
  card_body_key: string;
  recommended_demo: boolean;
}
export interface ScenarioAnalysis {
  scenario_id: string;
  fixture_version: string;
  goal: string;
  profile: SyntheticProfile;
  readiness: ReadinessState;
  headline_key: string;
  explanation_key: string;
  next_best_action_key: string;
  records: SyntheticRecord[];
  findings: Finding[];
  dependency_trail_keys: string[];
  actions: CorrectionAction[];
  recommended_plan: PlanResult | null;
  applied_action_ids: string[];
  before_after: BeforeAfter[];
  simulation_events: SimulationEvent[];
  official_handoff: OfficialHandoff;
  source_ids: string[];
  deterministic: boolean;
  government_systems_contacted: number;
}

export interface FictionalTestCase {
  schema_version: "claimpath-test-case.v1";
  fictional: true;
  aadhaar_linked_name: string;
  epfo_name: string;
  name_relation_confirmed: boolean;
  date_of_exit: string | null;
  proposed_exit_date: string;
  mark_exit_waiting_period_met: boolean;
}

export type TestCaseStatus =
  | "BLOCKED_DATE_OF_EXIT"
  | "WAITING_PERIOD_NOT_MET"
  | "NEEDS_REVIEW"
  | "PREREQUISITE_MET";

export interface TestCaseResult {
  schema_version: "claimpath-test-result.v1";
  status: TestCaseStatus;
  blocker: string | null;
  date_of_exit_before: string | null;
  date_of_exit_after: string | null;
  name_change_recommended: false;
  next_action: string;
  traces: Array<{
    rule_id: string;
    status: "PASS" | "BLOCK" | "REVIEW";
    message: string;
    source_id: string;
  }>;
  deterministic: true;
  fictional: true;
  government_systems_contacted: 0;
  execution_mode:
    | "FASTAPI_DETERMINISTIC_ENGINE"
    | "BROWSER_DETERMINISTIC_FALLBACK";
}

class IdentityApiUnavailable extends Error {}

interface StaticBundle {
  fixture_version: string;
  generated_from: string;
  deterministic: true;
  government_systems_contacted: 0;
  sources: SourceReference[];
  analyses: Record<string, ScenarioAnalysis>;
}

let staticBundle: Promise<StaticBundle> | null = null;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(path, {
      ...init,
      headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    });
  } catch {
    throw new IdentityApiUnavailable("IDENTITY_API_NETWORK");
  }
  if (response.status === 404 || response.status === 405) {
    throw new IdentityApiUnavailable(`IDENTITY_API_${response.status}`);
  }
  if (!response.ok) throw new Error(`IDENTITY_API_${response.status}`);
  return response.json() as Promise<T>;
}

function loadStaticBundle(): Promise<StaticBundle> {
  staticBundle ??= fetch(`${import.meta.env.BASE_URL}identity-rescue-static.json`)
    .then((response) => {
      if (!response.ok) throw new Error(`STATIC_FIXTURE_${response.status}`);
      return response.json() as Promise<StaticBundle>;
    })
    .then((bundle) => {
      if (
        bundle.generated_from !== "IdentityRescueEngine" ||
        bundle.deterministic !== true ||
        bundle.government_systems_contacted !== 0
      ) {
        throw new Error("STATIC_FIXTURE_TRUST_BOUNDARY");
      }
      return bundle;
    });
  return staticBundle;
}

async function withStaticFallback<T>(
  live: () => Promise<T>,
  fallback: (bundle: StaticBundle) => T,
): Promise<T> {
  try {
    return await live();
  } catch (error) {
    if (!(error instanceof IdentityApiUnavailable)) throw error;
    return fallback(await loadStaticBundle());
  }
}

function staticAnalysis(
  bundle: StaticBundle,
  scenarioId: string,
  appliedActionIds: string[],
): ScenarioAnalysis {
  const key = `${scenarioId}|${appliedActionIds.join(",")}`;
  const result = bundle.analyses[key];
  if (!result) throw new Error("STATIC_FIXTURE_ACTION_NOT_ALLOWED");
  return structuredClone(result);
}

export function analyzeScenario(
  scenarioId: string,
  appliedActionIds: string[] = [],
): Promise<ScenarioAnalysis> {
  return withStaticFallback(
    () =>
      request(
        `/api/v1/identity/scenarios/${encodeURIComponent(scenarioId)}/analyze`,
        {
          method: "POST",
          body: JSON.stringify({ applied_action_ids: appliedActionIds }),
        },
      ),
    (bundle) => staticAnalysis(bundle, scenarioId, appliedActionIds),
  );
}

export function simulateScenario(
  scenarioId: string,
  actionId: string,
  appliedActionIds: string[],
): Promise<ScenarioAnalysis> {
  const nextActionIds = appliedActionIds.includes(actionId)
    ? appliedActionIds
    : [...appliedActionIds, actionId];
  return withStaticFallback(
    () =>
      request(
        `/api/v1/identity/scenarios/${encodeURIComponent(scenarioId)}/simulate`,
        {
          method: "POST",
          body: JSON.stringify({
            action_id: actionId,
            applied_action_ids: appliedActionIds,
          }),
        },
      ),
    (bundle) => staticAnalysis(bundle, scenarioId, nextActionIds),
  );
}

export function getSources(): Promise<SourceReference[]> {
  return withStaticFallback(
    () => request("/api/v1/identity/sources"),
    (bundle) => structuredClone(bundle.sources),
  );
}

const TEST_CASE_KEYS = new Set([
  "schema_version",
  "fictional",
  "aadhaar_linked_name",
  "epfo_name",
  "name_relation_confirmed",
  "date_of_exit",
  "proposed_exit_date",
  "mark_exit_waiting_period_met",
]);

const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/;

export function parseFictionalTestCase(value: unknown): FictionalTestCase {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("TEST_CASE_OBJECT_REQUIRED");
  }
  const input = value as Record<string, unknown>;
  if (Object.keys(input).some((key) => !TEST_CASE_KEYS.has(key))) {
    throw new Error("TEST_CASE_UNKNOWN_FIELD");
  }
  const validName = (name: unknown) =>
    typeof name === "string" &&
    name.trim().length >= 2 &&
    name.trim().length <= 80 &&
    !/\d/.test(name);
  if (
    input.schema_version !== "claimpath-test-case.v1" ||
    input.fictional !== true ||
    !validName(input.aadhaar_linked_name) ||
    !validName(input.epfo_name) ||
    typeof input.name_relation_confirmed !== "boolean" ||
    !(
      input.date_of_exit === null ||
      (typeof input.date_of_exit === "string" && ISO_DATE.test(input.date_of_exit))
    ) ||
    typeof input.proposed_exit_date !== "string" ||
    !ISO_DATE.test(input.proposed_exit_date) ||
    typeof input.mark_exit_waiting_period_met !== "boolean"
  ) {
    throw new Error("TEST_CASE_SCHEMA_INVALID");
  }
  return {
    schema_version: "claimpath-test-case.v1",
    fictional: true,
    aadhaar_linked_name: (input.aadhaar_linked_name as string).trim(),
    epfo_name: (input.epfo_name as string).trim(),
    name_relation_confirmed: input.name_relation_confirmed,
    date_of_exit: input.date_of_exit as string | null,
    proposed_exit_date: input.proposed_exit_date,
    mark_exit_waiting_period_met: input.mark_exit_waiting_period_met,
  };
}

function browserAnalyzeTestCase(
  input: FictionalTestCase,
  applySuggestedFix: boolean,
): TestCaseResult {
  const normalize = (name: string) => name.trim().toLocaleUpperCase("en-IN").replace(/\s+/g, " ");
  const namesDiffer = normalize(input.aadhaar_linked_name) !== normalize(input.epfo_name);
  const nameSafe = !namesDiffer || input.name_relation_confirmed;
  let status: TestCaseStatus;
  let blocker: string | null;
  let dateAfter = input.date_of_exit;
  let nextAction: string;
  if (!nameSafe) {
    status = "NEEDS_REVIEW";
    blocker = "NAME_RELATION_UNCONFIRMED";
    nextAction = "Do not infer identity equivalence or change a name from this file. Review the fictional evidence relation first.";
  } else if (input.date_of_exit !== null) {
    status = "PREREQUISITE_MET";
    blocker = null;
    nextAction = "The Date of Exit prerequisite is present in this fictional case.";
  } else if (!input.mark_exit_waiting_period_met) {
    status = "WAITING_PERIOD_NOT_MET";
    blocker = "MARK_EXIT_WAITING_PERIOD";
    nextAction = "The sample says the documented waiting condition is not yet met. Do not simulate Mark Exit yet.";
  } else if (applySuggestedFix) {
    dateAfter = input.proposed_exit_date;
    status = "PREREQUISITE_MET";
    blocker = null;
    nextAction = "The fictional Date of Exit was added and the prerequisite was recomputed.";
  } else {
    status = "BLOCKED_DATE_OF_EXIT";
    blocker = "DATE_OF_EXIT_MISSING";
    nextAction = "Test the proposed fictional Date of Exit, then recompute.";
  }
  return {
    schema_version: "claimpath-test-result.v1",
    status,
    blocker,
    date_of_exit_before: input.date_of_exit,
    date_of_exit_after: dateAfter,
    name_change_recommended: false,
    next_action: nextAction,
    traces: [
      {
        rule_id: "EPFO-001",
        status: nameSafe ? "PASS" : "REVIEW",
        message: nameSafe
          ? "Name relation is explicitly confirmed in the fictional file."
          : "Different names have no confirmed fictional relation.",
        source_id: "SRC-EPFO-FAQ-001",
      },
      {
        rule_id: "EPFO-003",
        status: dateAfter === null ? "BLOCK" : "PASS",
        message: dateAfter === null
          ? "Date of Exit is missing for the transfer prerequisite."
          : "Date of Exit is present for the transfer prerequisite.",
        source_id: "SRC-EPFO-FAQ-001",
      },
    ],
    deterministic: true,
    fictional: true,
    government_systems_contacted: 0,
    execution_mode: "BROWSER_DETERMINISTIC_FALLBACK",
  };
}

export function analyzeFictionalTestCase(
  input: FictionalTestCase,
  applySuggestedFix = false,
): Promise<TestCaseResult> {
  return withStaticFallback(
    () =>
      request("/api/v1/identity/test-case/analyze", {
        method: "POST",
        body: JSON.stringify({
          case: input,
          apply_suggested_fix: applySuggestedFix,
        }),
      }),
    () => browserAnalyzeTestCase(input, applySuggestedFix),
  );
}
