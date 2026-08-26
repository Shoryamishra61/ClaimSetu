# 02 — Software Requirements Specification (SRS)

## Identity Rescue

**Version:** 1.0  
**Normative language:** MUST / MUST NOT / SHOULD / MAY  
**Requirement prefixes:** `FR` functional, `NFR` non-functional, `DR` data, `AR` AI, `SEC` security, `ACC` accessibility, `OBS` observability.

---

# 1. System purpose and boundary

Identity Rescue is a browser-accessible prototype that evaluates **fictional** records against a small, versioned set of service-specific compatibility rules and simulates correction sequences. It does not authenticate real residents, query government databases, write to official systems, or determine legal identity.

## 1.1 Logical components

1. **Citizen UI** — goal selection, diagnosis, evidence, correction comparison, simulation, handoff.
2. **Scenario Store** — synthetic profiles and initial states.
3. **Mock Adapters** — agency-shaped interfaces that return synthetic records.
4. **Normalizer** — conservative representation transformations.
5. **Rule Engine** — deterministic evaluation of service requirements.
6. **Readiness Evaluator** — combines findings into service state.
7. **Correction Planner** — searches allowed synthetic actions.
8. **Simulation Engine** — applies reversible changes to in-memory/session state and recalculates.
9. **Evidence Store** — source/provenance metadata.
10. **Explanation Service** — template-first; optional bounded OpenAI call.
11. **Event Journal** — local/app persistence of demo actions for deterministic replay/debugging.

---

# 2. Functional requirements

## 2.1 Session and navigation

### FR-001 — Anonymous entry
The system MUST allow a reviewer to enter the primary citizen journey without account creation.

### FR-002 — Persistent prototype disclosure
Every route in the citizen experience MUST display or expose in the global shell the statement that this is an independent hackathon prototype using fictional data and no government connection.

### FR-003 — Goal selection
The home route MUST present exactly the three P0 golden journeys before any optional content.

### FR-004 — Deep linking
Each golden journey SHOULD have a stable route suitable for demo/reviewer access.

### FR-005 — Reset
The user MUST be able to reset the current synthetic case and clear session-local mutations from every scenario.

### FR-006 — Back navigation
Browser Back MUST not corrupt the scenario state. Returning to a previous step MUST either restore the prior deterministic state or clearly re-evaluate it.

## 2.2 Scenario loading

### FR-010 — Synthetic-only fixtures
The system MUST load P0 cases from pre-seeded fictional profiles.

### FR-011 — Demo identifiers
Synthetic identifiers MUST be visibly non-real (`DEMO-*`, masked placeholders, UUID-like internal keys) and MUST NOT be valid Aadhaar/PAN/UAN formats.

### FR-012 — Relevant data minimization
The UI MUST initially load/display only fields relevant to the selected goal. Additional records MAY be available through progressive disclosure.

### FR-013 — Fixture integrity
Each golden fixture MUST have an expected outcome encoded separately from implementation logic so tests can detect accidental rule drift.

## 2.3 Mock adapter interface

### FR-020 — Adapter contract
Each mock authority adapter MUST implement equivalent behavior to:

```ts
interface MockRecordAdapter {
  authority: AuthorityCode;
  getRecord(profileId: string): Promise<SyntheticRecord | null>;
  listCapabilities(): AdapterCapability[];
}
```

Actual language/framework MAY differ while preserving the contract.

### FR-021 — No live endpoints
P0 adapters MUST NOT call live UIDAI, Income Tax, DigiLocker, EPFO, Passport Seva, Parivahan or other government endpoints.

### FR-022 — Deterministic response
Given the same fixture version and profile ID, an adapter MUST return the same base record.

### FR-023 — Failure simulation
Adapters MAY expose explicit fixture-driven latency/error states for resilience testing, but these MUST be labeled simulation states.

## 2.4 Canonical record representation

### FR-030 — Original preservation
The system MUST retain the original synthetic field value separately from all derived representations.

### FR-031 — Field provenance
Every field used in a finding MUST be traceable to authority, record ID, field name and fixture version.

### FR-032 — Full-name-first model
The canonical identity model MUST support a `full_name_original` representation without requiring first/middle/last decomposition.

### FR-033 — Optional structured name metadata
The model MAY include known synthetic components (`given`, `family`, `patronymic`, `initial_expansions`) where the fixture explicitly provides them. The system MUST NOT infer such structure as authoritative merely from token position.

### FR-034 — Script metadata
A field MAY include script/locale metadata and controlled transliterations; any generated transliteration MUST be labeled derived.

## 2.5 Normalization

### FR-040 — Conservative normalization
The normalizer MUST support Unicode normalization, whitespace normalization and explicitly configured punctuation/honorific handling.

### FR-041 — No destructive overwrite
Normalization MUST never replace the stored original.

### FR-042 — Initial handling
The normalizer MUST identify likely initials but MUST NOT expand them unless the synthetic profile/rulebook provides the expansion relationship.

### FR-043 — Token reordering
Token-order equivalence MUST be rule-specific. It MUST NOT be globally assumed.

### FR-044 — Transliteration
Transliteration similarity MAY generate a `REVIEW` finding but MUST NOT alone establish identity equivalence.

### FR-045 — Similarity score limitation
A scalar fuzzy-string score MUST NOT directly determine `READY` or `BLOCKED` status.

## 2.6 Rule engine

### FR-050 — Versioned rules
Every service rule MUST have stable ID and version.

### FR-051 — Rule schema
At minimum a rule MUST provide:

```json
{
  "id": "DL_FETCH_NAME_001",
  "version": "1.0",
  "goal": "DIGILOCKER_FETCH_DL",
  "inputs": ["AADHAAR.name", "DL.name"],
  "predicate": "...deterministic comparator...",
  "on_pass": "MATCH_RULE_COMPATIBLE",
  "on_fail": "MISMATCH_BLOCKING",
  "source_ids": ["SRC-DIGILOCKER-FAQ"],
  "evidence_status": "OFFICIAL_SOURCE_DERIVED",
  "last_checked": "2026-08-22"
}
```

### FR-052 — Rule provenance
No P0 blocking rule may exist without source or explicit `PROTOTYPE_SIMULATION` status.

### FR-053 — Unknown handling
If required evidence is absent or rule semantics are not modeled, the engine MUST return `UNKNOWN`/`NEEDS_REVIEW`, not guess.

### FR-054 — Multiple findings
The engine MUST preserve multiple simultaneous findings and identify which are causal for the selected goal.

### FR-055 — Non-identity blocker
The engine MUST support `NON_IDENTITY_BLOCKER` so Scenario 2 can explicitly reject the false premise that every service failure is an identity mismatch.

### FR-056 — Explainable trace
For every finding the engine MUST expose input facts, comparator/rule ID, outcome and source IDs.

## 2.7 Readiness evaluator

### FR-060 — Categorical readiness
The evaluator MUST output one of:

- `READY_SIMULATION`
- `BLOCKED`
- `NEEDS_REVIEW`
- `NOT_IDENTITY_ISSUE`

### FR-061 — Blocking precedence
Any unresolved mandatory blocking rule MUST prevent `READY_SIMULATION`.

### FR-062 — Unknown precedence
If no blocker exists but a mandatory rule is `UNKNOWN`, the state MUST be `NEEDS_REVIEW` rather than `READY_SIMULATION`.

### FR-063 — No fake score
The P0 citizen UI MUST NOT represent readiness as an arbitrary percentage.

## 2.8 Correction actions

### FR-070 — Allowed-action catalogue
All simulation actions MUST be explicitly declared in the scenario/rulebook. Users may not arbitrarily mutate official-looking fields.

### FR-071 — Action metadata
Each action MUST contain:

- `action_id`
- target mock authority/record/field
- from/to synthetic values
- prerequisites
- effort class
- reversibility
- source/evidence status
- affected goals/records
- risk/uncertainty note

### FR-072 — Action preview
Before simulation, the UI MUST state that the change is fictional and list modeled downstream effects.

## 2.9 Correction planner

### FR-080 — Goal-conditioned planning
The planner MUST optimize relative to the selected citizen goal, not global visual consistency.

### FR-081 — Deterministic cost
The planner MUST use explicit configured costs; it MUST NOT use an LLM to rank actions.

### FR-082 — Search
For P0, breadth-first / Dijkstra / A* / exhaustive search MAY be used because the action space is small. The result MUST be deterministic for a fixture version.

### FR-083 — Constraints
A plan MUST NOT include an action marked prohibited/unsupported. A plan that introduces a new modeled P0-critical blocker MUST either be rejected or explicitly surface the trade-off.

### FR-084 — Tie behavior
If multiple plans have equivalent cost, the UI MUST state that more than one route is viable rather than fabricate certainty.

### FR-085 — Explanation
Planner output MUST expose a reason based on steps, effort, impact and uncertainty.

## 2.10 Simulation

### FR-090 — Isolated session state
Simulation mutations MUST affect only the current demo session/profile copy.

### FR-091 — Re-evaluation
Every simulation action MUST trigger recomputation of all dependent findings and readiness states.

### FR-092 — Undo/reset
User MUST be able to revert the most recent change or reset the entire case.

### FR-093 — Before/after
The UI MUST make the modified field and readiness delta inspectable.

### FR-094 — Audit event
Each simulation action SHOULD append a local event with scenario ID, action ID and timestamp for debugging/replay; it MUST NOT contain real identifiers.

## 2.11 Evidence and official handoff

### FR-100 — Source registry
Rules MUST resolve source IDs against a local source registry.

### FR-101 — Citizen evidence
The citizen UI MUST expose source title, agency/publisher, last-checked date and official URL for important P0 conclusions.

### FR-102 — Official link separation
External official links MUST be visibly identified as leaving the prototype.

### FR-103 — Process-change caveat
The final handoff MUST say that official processes can change and the linked official source is authoritative.

## 2.12 Localization

### FR-110 — Locale keys
No P0 citizen-facing sentence may be embedded only inside business logic; UI copy MUST be localizable.

### FR-111 — P0 languages
English and Hindi MUST cover every P0 screen, validation, error, disclosure and fallback message.

### FR-112 — User-controlled switch
Language MUST be user-selectable. Locale detection MAY suggest but MUST NOT silently force Hindi or any regional language.

### FR-113 — Source value preservation
Changing UI locale MUST NOT alter the original displayed synthetic record value unless user explicitly selects a derived transliteration view.

## 2.13 AI explanation

### FR-120 — Non-critical path
AI MUST NOT be required to calculate findings/readiness/plans.

### FR-121 — Evidence packet
Any model request MUST receive a bounded structured packet containing only synthetic values, current deterministic findings and approved source snippets/metadata.

### FR-122 — Structured response
Model output SHOULD use a validated schema rather than arbitrary HTML/Markdown.

### FR-123 — Template fallback
If AI is disabled, times out, violates schema or fails grounding checks, the system MUST render deterministic templates.

### FR-124 — No hidden policy retrieval
The model MUST NOT browse or retrieve new web policy at runtime in P0.

### FR-125 — Explanation labeling
The UI MAY label generated text as AI-assisted explanation; source citations remain those of the deterministic evidence, not “AI says.”

---

# 3. Data requirements

## DR-001 — No real sensitive data
The application MUST NOT require real Aadhaar, PAN, UAN, OTP, payment or health data.

## DR-002 — Fixture classes
The system SHOULD separate:

- `source_fixtures` — immutable synthetic base records;
- `scenario_state` — per-session mutation overlay;
- `rules` — deterministic logic/config;
- `sources` — provenance registry;
- `events` — non-sensitive simulation journal.

## DR-003 — Suggested entities

```text
SyntheticProfile
SyntheticRecord
FieldValue
Goal
Rule
Finding
CorrectionAction
CorrectionPlan
SourceReference
SimulationEvent
LocaleString
```

## DR-004 — Schema evolution
Fixture/rule versions MUST be explicit so recordings/tests can pin known behavior.

## DR-005 — No realistic number generation
Test factories MUST avoid accidentally generating syntactically valid Aadhaar/PAN/UAN values.

---

# 4. External interface requirements

## 4.1 Browser

### NFR-UI-001
The app MUST be deployable as a public browser URL; no mobile installation required.

### NFR-UI-002
P0 MUST work on current stable Chromium-class desktop/mobile and should work on current Firefox/Safari.

## 4.2 Government links

### NFR-EXT-001
Only documented public webpages/official destinations may be linked. The app MUST not imply API integration.

## 4.3 Optional OpenAI service

### AR-001
OpenAI credentials, if used, MUST remain server-side and never ship to the browser bundle.

### AR-002
The runtime model identifier MUST be configuration, not hard-coded throughout business logic.

### AR-003
AI requests MUST contain synthetic/demo data only.

---

# 5. Non-functional requirements

## 5.1 Performance

### NFR-PERF-001
Target First Contentful Paint <= 2.0 s and Largest Contentful Paint <= 2.5 s on an optimized mid-tier mobile / slow-4G test profile for the production build, subject to host variance.

### NFR-PERF-002
Deterministic analysis after fixture data is available SHOULD complete <= 300 ms for P0 cases.

### NFR-PERF-003
UI input response SHOULD remain < 100 ms for normal interactions.

### NFR-PERF-004
AI explanation timeout SHOULD be <= 4 s before displaying fallback; the user may continue immediately without waiting.

### NFR-PERF-005
Avoid loading graph/AI/admin code on the initial route unless required.

## 5.2 Reliability

### NFR-REL-001
A refresh on any golden route MUST either restore a known fixture state or restart cleanly with explicit notice; it MUST NOT produce a corrupt partial case.

### NFR-REL-002
AI or telemetry failure MUST NOT fail the primary journey.

### NFR-REL-003
Invalid fixture/rule references MUST fail closed to `NEEDS_REVIEW` and log a developer-visible error.

## 5.3 Maintainability

### NFR-MNT-001
Rules, source metadata and UI copy SHOULD be data/config driven where practical, separated from rendering code.

### NFR-MNT-002
Business logic MUST be unit-testable without a browser or network.

### NFR-MNT-003
No component should contain hard-coded agency-specific decision logic if the same logic can live in the rule engine.

## 5.4 Deployment

### NFR-DEP-001
Production build MUST have one-command documented deployment from repository state.

### NFR-DEP-002
A health/readiness endpoint MAY exist for host diagnostics but MUST not expose sensitive configuration.

### NFR-DEP-003
Docker MAY be retained if already stable, but containerization is not a citizen feature and should not block a simpler deployment.

---

# 6. Accessibility requirements

## ACC-001
The implementation MUST target WCAG 2.1 AA / GIGW 3.0-aligned requirements applicable to the prototype.

## ACC-002
Every screen MUST have a unique, meaningful H1.

## ACC-003
All interactive controls MUST have programmatically determinable names, roles and states.

## ACC-004
Normal content MUST reflow at 320 CSS px without two-dimensional scrolling, except true two-dimensional artifacts; the graph MUST have a non-2D alternative.

## ACC-005
Normal text/background contrast MUST be at least 4.5:1 except valid standard exceptions.

## ACC-006
Focus indication MUST be visible and keyboard operation MUST cover all P0 functionality.

## ACC-007
Dynamic readiness/status changes MUST be available to assistive technology via appropriate live region/status semantics.

## ACC-008
Color MUST NOT be the only means of conveying readiness/mismatch state.

## ACC-009
At 200% zoom, no P0 information/action may become unavailable.

## ACC-010
Motion MUST respect `prefers-reduced-motion`.

## ACC-011
Language metadata MUST match the selected locale.

## ACC-012
Touch targets for primary actions SHOULD be at least 44x44 CSS px where feasible.

---

# 7. Security requirements

## SEC-001
The public application MUST serve over HTTPS in deployed environment.

## SEC-002
If a backend exists, it MUST apply secure headers appropriate to framework/host, including CSP where practical, HSTS on production, frame restrictions and MIME sniffing protection.

## SEC-003
No API key or private credential may be committed or exposed client-side.

## SEC-004
The app MUST not log raw free text sent to an AI endpoint unless explicitly required for debugging in local development; production should log only request outcome/trace IDs.

## SEC-005
If a synthetic free-text parser is P1, common Indian identifier patterns MUST be locally redacted/rejected before any network call.

## SEC-006
External official links MUST use safe rel attributes when opened in a new tab/window.

## SEC-007
Dependency audit MUST have no unresolved critical/high vulnerabilities in reachable P0 code unless documented with compensating rationale.

## SEC-008
Rate limiting SHOULD protect any public AI endpoint from abuse.

---

# 8. Observability requirements

## OBS-001
Errors MUST include a stable code suitable for debugging while citizen copy remains plain language.

## OBS-002
At minimum collect locally/server-side:

- route/scenario entered;
- deterministic analysis success/failure;
- AI fallback invoked;
- simulation action ID;
- external official link clicked;
- fatal client error.

No real identity data.

## OBS-003
Production telemetry MUST be optional/minimal. The demo must function with analytics disabled.

## OBS-004
A developer debug panel MAY expose fixture/rule IDs behind a query flag, but MUST NOT clutter citizen mode or be shown in the first demo minute.

---

# 9. Error/state taxonomy

Every engine boundary must map technical failures to one of:

- `SOURCE_FIXTURE_UNAVAILABLE`
- `RULE_NOT_FOUND`
- `RULE_INPUT_MISSING`
- `ANALYSIS_UNKNOWN`
- `PLAN_NOT_FOUND`
- `SIMULATION_INVALID_ACTION`
- `AI_TIMEOUT`
- `AI_SCHEMA_INVALID`
- `AI_GROUNDING_FAILED`
- `LOCALE_MISSING_KEY`
- `EXTERNAL_LINK_UNAVAILABLE` (if preflight checked)

Citizen copy must state what they can still do.

---

# 10. Golden scenario invariants

## GS-01 DL mismatch

- Initial state = `BLOCKED`.
- At least one official-source-derived name reconciliation rule fires.
- One permitted correction action changes the blocking field representation.
- After simulation = `READY_SIMULATION`.
- No unmodeled live call occurs.

## GS-02 EPFO disambiguation

- Initial profile has >= 2 findings.
- At least one name-related difference exists.
- The causal blocker is non-identity in the selected fixture state.
- Simulating a name-only change does **not** incorrectly make the target ready.
- Simulating the permitted causal correction changes readiness as expected.

## GS-03 Life-event sequencing

- Initial state has >= 3 affected mock records.
- Planner yields >= 1 viable sequence.
- Recommended sequence has lower configured cost than at least one alternative.
- Each step recomputes affected goals.
- Final state communicates remaining non-blocking differences.

---

# 11. Required interfaces — suggested types

```ts
type ReadinessState =
  | 'READY_SIMULATION'
  | 'BLOCKED'
  | 'NEEDS_REVIEW'
  | 'NOT_IDENTITY_ISSUE';

type FindingState =
  | 'MATCH_EXACT'
  | 'MATCH_RULE_COMPATIBLE'
  | 'VARIANT_NON_BLOCKING'
  | 'MISMATCH_BLOCKING'
  | 'MISMATCH_REVIEW'
  | 'MISSING_REQUIRED'
  | 'NON_IDENTITY_BLOCKER'
  | 'UNKNOWN';

interface EvidenceTrace {
  findingId: string;
  ruleId: string;
  inputs: Array<{
    recordId: string;
    authority: string;
    field: string;
    originalValue: string | null;
  }>;
  state: FindingState;
  sourceIds: string[];
  explanationKey: string;
}

interface PlanResult {
  goal: string;
  actions: CorrectionAction[];
  totalCost: number;
  affectedGoals: Array<{ goal: string; before: ReadinessState; after: ReadinessState }>;
  uncertainty: string[];
}
```

These are normative in semantics, not exact syntax.

---

# 12. Traceability summary

| Product requirement | Software requirements |
|---|---|
| Goal-first flow | FR-003, FR-004 |
| Synthetic-only | FR-010–013, DR-001–005 |
| Exact blocker | FR-040–063 |
| Compare corrections | FR-070–085 |
| Simulation | FR-090–094 |
| Evidence | FR-100–103 |
| Indian language support | FR-110–113 |
| Bounded AI | FR-120–125, AR-001–003 |
| Mobile/slow network | NFR-PERF-*; ACC-004 |
| Accessible | ACC-001–012 |
| Honest/safe | FR-002, FR-021, SEC-* |
