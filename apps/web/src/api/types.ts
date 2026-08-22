/**
 * TypeScript mirrors of `app/api/serialisers.py`.
 *
 * Hand-written, like the serialisers themselves, and for the same reason: the
 * property that matters is that the client renders only fields the server chose to
 * publish. A generated type would follow whatever the server started sending; a
 * hand-written one makes an unexpected field a compile error at the point someone
 * tries to read it.
 *
 * Two fields carry the product invariant and are typed so that misreading them is
 * awkward:
 *
 * -  `is_acknowledged` is the *only* success signal. It is a server-computed
 *    boolean that requires both the terminal state and a persisted acknowledgement
 *    row. Nothing in this client may infer success from `state`, from an HTTP
 *    status, or from a WebSocket message.
 * -  `payload_hash` is transport, not display. It is echoed back on confirm and
 *    submit and is shown to a human only inside the source drawer.
 */

export type Lang = "en" | "hi";

/** Every bilingual string the API sends has this shape. */
export interface Bilingual {
  en: string;
  hi: string;
}

export type CaseState =
  | "DRAFT"
  | "VEHICLE_VERIFIED"
  | "DEALER_VERIFIED"
  | "DEALER_INVALID"
  | "PREFLIGHT_PASSED"
  | "PREFLIGHT_BLOCKED"
  | "REVIEW_READY"
  | "SELLER_CONFIRMED"
  | "BOTH_CONFIRMED"
  | "SUBMITTING_29C"
  | "SUBMISSION_TEMPORARY_FAILURE"
  | "SUBMISSION_UNKNOWN"
  | "SUBMISSION_REJECTED"
  | "HANDOFF_ACKNOWLEDGED"
  | "CANCELLED";

export type Role = "SELLER" | "DEALER";

export type JourneyType = "AUTHORISED_DEALER_HANDOFF" | "PRIVATE_BUYER_TRANSFER";

export type SourceType =
  | "SIMULATED_CHECK"
  | "USER_DECLARATION"
  | "SIMULATED_CHECK_WITH_DECLARATION"
  | "INFORMATIONAL";

export type ItemResult = "PASS" | "PENDING" | "FAIL" | "INFO";

export type BlockingStage = "PREFLIGHT" | "SUBMIT" | "NONE";

export type DealerStatus = "ACTIVE" | "EXPIRED" | "SUSPENDED" | "NOT_FOUND";

export type AttemptStatus =
  | "ACK"
  | "REJECTED"
  | "TEMPORARY_FAILURE"
  | "UNKNOWN"
  | "IN_FLIGHT";

export interface Vehicle {
  simulation: true;
  id: string;
  registration_no: string;
  chassis_suffix: string;
  make_model: string;
  registered_owner_name: string;
  document_flags: Record<string, boolean>;
  submission_scenario: string;
  is_default_demo: boolean;
  demo_label: Bilingual;
}

export interface Dealer {
  simulation: true;
  id: string;
  authorisation_no: string;
  business_name: string;
  status: DealerStatus;
  status_text: Bilingual;
  can_continue: boolean;
  valid_from: string | null;
  valid_until: string | null;
  is_default_demo: boolean;
  demo_label: Bilingual;
}

export interface EvaluatedItem {
  code: string;
  label: Bilingual;
  help: Bilingual;
  source_type: SourceType;
  responsible: "SELLER" | "DEALER" | "SYSTEM";
  source_id: string;
  source_locator: string;
  blocking_stage: BlockingStage;
  blocking: boolean;
  result: ItemResult;
}

export interface PolicyEvaluation {
  policy_version: string;
  stage: "PREFLIGHT" | "SUBMIT";
  passed: boolean;
  items: EvaluatedItem[];
  blocking_failures: string[];
  pending_codes: string[];
}

export interface CanonicalPayload {
  schema_version: string;
  policy_version: string;
  case_id: string;
  vehicle: { registration_no: string; chassis_suffix: string };
  registered_owner_name: string;
  dealer: { authorisation_no: string; business_name: string };
  declarations: Array<{ code: string; value: boolean }>;
  handover_local_time: string;
}

export interface ReviewPayload {
  schema_version: string;
  canonical: CanonicalPayload;
  payload_hash: string | null;
}

export interface SubmissionAttempt {
  simulation: true;
  attempt_number: number;
  status: AttemptStatus;
  acknowledgement_no: string | null;
  reason_code: string | null;
  reason_text: Bilingual | null;
  created_at: string;
  completed_at: string | null;
}

export interface AuditEvent {
  sequence: number;
  event_type: string;
  actor: string | null;
  state_before: string | null;
  state_after: string | null;
  detail: string | null;
  created_at: string;
  event_hash: string;
  previous_event_hash: string | null;
}

export interface CaseSnapshot {
  simulation: true;
  id: string;
  journey_type: JourneyType;
  policy_version: string;
  state: CaseState;
  /**
   * The one success signal. True only when the simulated adapter returned a
   * persisted acknowledgement AND the case reached its terminal state. Never
   * derive success from anything else in this object.
   */
  is_acknowledged: boolean;
  is_terminal: boolean;
  is_failed_outcome: boolean;
  your_role: Role | null;
  seller_confirmed: boolean;
  dealer_confirmed: boolean;
  dealer_joined: boolean;
  handover_local_time: string | null;
  vehicle: Vehicle | null;
  dealer: Dealer | null;
  declarations: Record<string, boolean>;
  preflight: PolicyEvaluation;
  submit_checks: PolicyEvaluation;
  review: ReviewPayload | null;
  latest_attempt: SubmissionAttempt | null;
  acknowledgement: SubmissionAttempt | null;
  created_at: string;
  updated_at: string;
}

export interface MetaPayload {
  simulation: true;
  build_label: string;
  policy_version: string;
  poll_interval_seconds: number;
  disclosure: Bilingual;
  about: Bilingual;
  no_real_data: Bilingual;
  scope: Bilingual;
  confirmation_meaning: Bilingual;
  acknowledgement_caveat: Bilingual;
  policy_anchor: Bilingual;
}

export interface FixturesPayload {
  simulation: true;
  vehicles: Vehicle[];
  dealers: Dealer[];
}

export interface PolicyPayload {
  version: string;
  title: string;
  source_id: string;
  source_locator: string;
  in_force: boolean;
  anchor_text: Bilingual;
  items: EvaluatedItem[];
}

export interface CreateCaseResponse {
  case: CaseSnapshot;
  party_token: string;
  your_role: "SELLER";
}

export interface JoinPairResponse {
  case: CaseSnapshot;
  case_id: string;
  party_token: string;
  your_role: "DEALER";
}

export interface PairResponse {
  case: CaseSnapshot;
  pair_code: string;
  expires_at: string;
  expires_in_seconds: number;
}

export interface ReviewResponse {
  review: ReviewPayload | null;
  seller_confirmed: boolean;
  dealer_confirmed: boolean;
  state: CaseState;
  meaning: Bilingual;
}

export interface ConfirmResponse {
  case: CaseSnapshot;
  already_confirmed: boolean;
}

export interface SubmissionResponse {
  case: CaseSnapshot;
  attempt: SubmissionAttempt | null;
  replayed: boolean;
  acknowledgement_no: string | null;
  acknowledgement_caveat: Bilingual;
}

export interface SubmissionStatusResponse {
  state: CaseState;
  is_acknowledged: boolean;
  acknowledgement: SubmissionAttempt | null;
  latest_attempt: SubmissionAttempt | null;
  can_reconcile: boolean;
  can_retry: boolean;
}

export interface AuditResponse {
  events: AuditEvent[];
  chain_valid: boolean;
}

export interface CaseResponse {
  case: CaseSnapshot;
}

/** The error envelope from `app/errors.py`. Total: every failure is one of these. */
export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    message_hi: string;
    recoverable: boolean;
    detail?: Record<string, unknown>;
  };
}
