/**
 * The only place this app talks to the server.
 *
 * Three rules are enforced here rather than left to call sites:
 *
 * 1.  **Every response is either typed data or an `ApiError`.** The server's error
 *     envelope is total (`app/errors.py`), so a call site never has to guess what a
 *     failure looks like or invent user-facing wording for one.
 * 2.  **The party token travels in a header, never in a URL.** A token in a query
 *     string ends up in browser history, in a screenshot of the address bar, and in
 *     any proxy log between here and the server.
 * 3.  **Idempotency keys are minted per user action, not per HTTP request.** See
 *     `submitCase` -- this is subtle enough that getting it wrong looks like it
 *     works.
 */

import type {
  AuditResponse,
  CaseResponse,
  ConfirmResponse,
  CreateCaseResponse,
  FixturesPayload,
  JoinPairResponse,
  JourneyType,
  MetaPayload,
  PairResponse,
  PolicyPayload,
  ReviewResponse,
  SubmissionResponse,
  SubmissionStatusResponse,
} from "./types";

const BASE = "/api/v1";

/**
 * A failure with the server's own bilingual wording attached.
 *
 * `recoverable` comes from the server so the UI can choose between "fix this and
 * try again" and "this journey cannot continue" without string-matching a code.
 */
export class ApiError extends Error {
  readonly code: string;
  readonly messageEn: string;
  readonly messageHi: string;
  readonly recoverable: boolean;
  readonly detail: Record<string, unknown>;
  readonly httpStatus: number;

  constructor(init: {
    code: string;
    messageEn: string;
    messageHi: string;
    recoverable: boolean;
    detail?: Record<string, unknown>;
    httpStatus: number;
  }) {
    super(`${init.code}: ${init.messageEn}`);
    this.name = "ApiError";
    this.code = init.code;
    this.messageEn = init.messageEn;
    this.messageHi = init.messageHi;
    this.recoverable = init.recoverable;
    this.detail = init.detail ?? {};
    this.httpStatus = init.httpStatus;
  }
}

/**
 * The one failure the server cannot describe, because it never received the
 * request. Given its own code so the UI can say "we could not reach the prototype"
 * instead of implying the server rejected something.
 */
export const TRANSPORT_ERROR = "TRANSPORT_ERROR";

function transportError(): ApiError {
  return new ApiError({
    code: TRANSPORT_ERROR,
    messageEn:
      "Could not reach the prototype server. Nothing was sent. Check your connection and try again.",
    messageHi:
      "प्रोटोटाइप सर्वर तक नहीं पहुँच सके। कुछ भी नहीं भेजा गया। कनेक्शन जाँचकर पुनः प्रयास करें।",
    recoverable: true,
    httpStatus: 0,
  });
}

function isErrorBody(value: unknown): value is {
  error: {
    code: string;
    message: string;
    message_hi: string;
    recoverable: boolean;
    detail?: Record<string, unknown>;
  };
} {
  if (typeof value !== "object" || value === null) return false;
  const candidate = (value as { error?: unknown }).error;
  if (typeof candidate !== "object" || candidate === null) return false;
  return typeof (candidate as { code?: unknown }).code === "string";
}

interface RequestOptions {
  method?: "GET" | "POST";
  body?: unknown;
  token?: string | null;
  idempotencyKey?: string;
  signal?: AbortSignal;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = { Accept: "application/json" };
  if (options.body !== undefined) headers["Content-Type"] = "application/json";
  if (options.token) headers["X-Party-Token"] = options.token;
  if (options.idempotencyKey) headers["Idempotency-Key"] = options.idempotencyKey;

  let response: Response;
  try {
    response = await fetch(`${BASE}${path}`, {
      method: options.method ?? "GET",
      headers,
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
      // No cookies anywhere in this product: identity is possession of a party
      // token, and `omit` makes that structural rather than incidental.
      credentials: "omit",
      cache: "no-store",
      ...(options.signal ? { signal: options.signal } : {}),
    });
  } catch {
    throw transportError();
  }

  if (response.status === 204) return undefined as T;

  let parsed: unknown = null;
  const text = await response.text();
  if (text) {
    try {
      parsed = JSON.parse(text) as unknown;
    } catch {
      parsed = null;
    }
  }

  if (!response.ok) {
    if (isErrorBody(parsed)) {
      throw new ApiError({
        code: parsed.error.code,
        messageEn: parsed.error.message,
        messageHi: parsed.error.message_hi,
        recoverable: parsed.error.recoverable,
        ...(parsed.error.detail ? { detail: parsed.error.detail } : {}),
        httpStatus: response.status,
      });
    }
    // A non-JSON error body means something in front of the app answered -- a
    // platform router, a proxy. Report it as transport rather than pretending the
    // application said it.
    throw transportError();
  }

  return parsed as T;
}

/**
 * A fresh idempotency key.
 *
 * `crypto.randomUUID` where available, otherwise random bytes. Not a security
 * boundary: the key only has to be unique per user-initiated submission so the
 * server's `UNIQUE (case_id, idempotency_key)` index can do its job.
 */
export function newIdempotencyKey(): string {
  const cryptoObject = globalThis.crypto;
  if (cryptoObject && typeof cryptoObject.randomUUID === "function") {
    return cryptoObject.randomUUID();
  }
  if (cryptoObject && typeof cryptoObject.getRandomValues === "function") {
    const bytes = cryptoObject.getRandomValues(new Uint8Array(16));
    return Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
  }
  // jsdom without browser entropy support, and nothing else. Still unique enough
  // for one test tab.
  return `k-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 12)}`;
}

// ---------------------------------------------------------------------------
// read-only, unauthenticated
// ---------------------------------------------------------------------------

export const getMeta = (): Promise<MetaPayload> => request<MetaPayload>("/meta");

export const getFixtures = (): Promise<FixturesPayload> =>
  request<FixturesPayload>("/fixtures");

export const getPolicy = (): Promise<PolicyPayload> => request<PolicyPayload>("/policy");

export const getCase = (caseId: string, token: string | null): Promise<CaseResponse> =>
  request<CaseResponse>(`/cases/${encodeURIComponent(caseId)}`, { token });

export const getReview = (caseId: string): Promise<ReviewResponse> =>
  request<ReviewResponse>(`/cases/${encodeURIComponent(caseId)}/review`);

export const getSubmissionStatus = (caseId: string): Promise<SubmissionStatusResponse> =>
  request<SubmissionStatusResponse>(
    `/cases/${encodeURIComponent(caseId)}/submission-status`,
  );

export const getAudit = (caseId: string): Promise<AuditResponse> =>
  request<AuditResponse>(`/cases/${encodeURIComponent(caseId)}/audit`);

// ---------------------------------------------------------------------------
// mutations
// ---------------------------------------------------------------------------

export const createCase = (journeyType: JourneyType): Promise<CreateCaseResponse> =>
  request<CreateCaseResponse>("/cases", {
    method: "POST",
    body: { journey_type: journeyType },
  });

export const verifyVehicle = (
  caseId: string,
  token: string | null,
  input: { registration_no: string; chassis_suffix: string },
): Promise<CaseResponse> =>
  request<CaseResponse>(`/cases/${encodeURIComponent(caseId)}/vehicle/verify`, {
    method: "POST",
    body: input,
    token,
  });

export const verifyDealer = (
  caseId: string,
  token: string | null,
  authorisationNo: string,
): Promise<CaseResponse> =>
  request<CaseResponse>(`/cases/${encodeURIComponent(caseId)}/dealer/verify`, {
    method: "POST",
    body: { authorisation_no: authorisationNo },
    token,
  });

export const setDeclarations = (
  caseId: string,
  token: string | null,
  values: Record<string, boolean>,
): Promise<CaseResponse> =>
  request<CaseResponse>(`/cases/${encodeURIComponent(caseId)}/declarations`, {
    method: "POST",
    body: { values },
    token,
  });

export const createPairCode = (
  caseId: string,
  token: string | null,
): Promise<PairResponse> =>
  request<PairResponse>(`/cases/${encodeURIComponent(caseId)}/pair`, {
    method: "POST",
    token,
  });

export const joinPair = (code: string): Promise<JoinPairResponse> =>
  request<JoinPairResponse>("/pair/join", { method: "POST", body: { code } });

export const confirmCase = (
  caseId: string,
  token: string | null,
  payloadHash: string,
): Promise<ConfirmResponse> =>
  request<ConfirmResponse>(`/cases/${encodeURIComponent(caseId)}/confirm`, {
    method: "POST",
    body: { payload_hash: payloadHash },
    token,
  });

export const withdrawConfirmation = (
  caseId: string,
  token: string | null,
): Promise<CaseResponse> =>
  request<CaseResponse>(`/cases/${encodeURIComponent(caseId)}/withdraw-confirmation`, {
    method: "POST",
    token,
  });

/**
 * Send the confirmed payload to the simulated adapter.
 *
 * `idempotencyKey` is a parameter rather than being minted here, and that is the
 * whole point. The server (`SubmissionService.begin`) treats a key it has already
 * completed as a *replay* and returns the recorded outcome without consulting the
 * adapter. So:
 *
 * -  A double-click, or an HTTP-level retry of one button press, must reuse the key.
 *    That is what makes a duplicate press produce one acknowledgement (INV-05).
 * -  A user pressing "Try again" after a temporary failure must send a **new** key.
 *    Reusing it would replay the failure forever and the retry button would appear
 *    to work while doing nothing.
 *
 * `useSubmission` owns that distinction; this function just carries the key.
 */
export const submitCase = (
  caseId: string,
  token: string | null,
  payloadHash: string,
  idempotencyKey: string,
): Promise<SubmissionResponse> =>
  request<SubmissionResponse>(`/cases/${encodeURIComponent(caseId)}/submit`, {
    method: "POST",
    body: { payload_hash: payloadHash },
    token,
    idempotencyKey,
  });

export const reconcileCase = (
  caseId: string,
  token: string | null,
): Promise<SubmissionResponse> =>
  request<SubmissionResponse>(`/cases/${encodeURIComponent(caseId)}/reconcile`, {
    method: "POST",
    token,
  });

export const cancelCase = (
  caseId: string,
  token: string | null,
): Promise<CaseResponse> =>
  request<CaseResponse>(`/cases/${encodeURIComponent(caseId)}/cancel`, {
    method: "POST",
    token,
  });

export const resetDemo = (): Promise<void> =>
  request<void>("/demo/reset", { method: "POST" });
