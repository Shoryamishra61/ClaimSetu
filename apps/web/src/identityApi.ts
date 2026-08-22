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
  official_handoff: OfficialHandoff;
  source_ids: string[];
  deterministic: boolean;
  government_systems_contacted: number;
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
