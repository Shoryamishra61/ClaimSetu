# 01 — Product Requirements Document (PRD)

## Identity Rescue

**Version:** 1.0 product freeze  
**Audience:** product, design, frontend, backend, AI, QA, demo/submission  
**Primary reference:** `00_MASTER_SPEC.md`

---

# 1. Executive summary

Identity Rescue is an independent citizen-facing hackathon prototype for diagnosing cross-service identity-data conflicts in Indian public-service journeys. The citizen chooses what they are trying to accomplish, loads a fictional profile, sees the exact record-level conflict or non-identity blocker, understands why that issue affects the selected service, compares correction routes, simulates a correction, and receives the minimum next-action plan for the official channel.

The product intentionally does **not** connect to live government systems and does not process real Aadhaar/PAN/UAN/OTP data. The demo value comes from a realistic model of the coordination failure between systems, not from unauthorized integration.

---

# 2. Research-backed problem evidence

The product thesis is supported by current official service behavior:

- The Income Tax Department's Link Aadhaar guidance says that if Aadhaar/PAN linking fails because name/phone/DOB do not match, the citizen must correct details in PAN or Aadhaar so they match.
- DigiLocker states that Aadhaar name should match the Driving Licence/Registration Certificate record for retrieval and exposes generic “details did not match issuer data” errors.
- DigiLocker’s published expert guidance also discusses inability to fetch documents when name order differs between Aadhaar and degree certificates.
- UIDAI enrolment/update guidance explicitly warns about initials vs expanded full names, variation across documentary proofs, regional-language transliteration, and the need to verify full names carefully.
- Passport Seva instructions require initials to be expanded and separately handle citizens who do not use a surname, demonstrating that name structure cannot be reduced to a universal first/last-name schema.
- EPFO guidance states that the name as per Aadhaar and PAN must align appropriately with PF records for KYC, and documents name/DOB mismatch errors in pension workflows.

The product does not claim these agencies share one universal matching algorithm. It demonstrates the citizen problem created when **service-specific matching rules and record representations differ**.

---

# 3. Product objective

## 3.1 User outcome

At the end of the journey, a citizen should be able to answer:

1. What is blocking my chosen task?
2. Which records disagree, if any?
3. Does that disagreement actually matter for this task?
4. Why does the service care about that field?
5. What are my plausible correction routes?
6. Which route is the least disruptive in this fictional case?
7. What would happen if I made that correction?
8. What official channel should I use next?
9. What should I **not** change unnecessarily?

## 3.2 Judge outcome

Within the first minute, a reviewer should observe a complete transformation rather than a feature tour:

`confusion → diagnosis → evidence → choice → simulation → readiness → next action`.

---

# 4. User needs / Jobs to be Done

## JTBD-01 — Diagnose a cryptic failure

**When** a public-service journey says my details do not match,  
**I want** to know exactly which fields and records are involved,  
**so that** I do not blindly edit official records.

## JTBD-02 — Establish causality

**When** several records differ,  
**I want** to know which difference actually blocks my target service,  
**so that** I do not spend time fixing irrelevant inconsistencies.

## JTBD-03 — Sequence corrections

**When** changing one record could affect other services,  
**I want** to compare correction paths and downstream impact,  
**so that** I can choose the smallest safe sequence.

## JTBD-04 — Understand government language

**When** I encounter an error code or procedural rule,  
**I want** a plain-language explanation tied to evidence,  
**so that** I can act without relying on a broker or random forum answer.

## JTBD-05 — Preserve dignity and control

**When** I am confused by a public-service failure,  
**I want** the product to explain the system without treating me as careless or incapable,  
**so that** I remain in control of the decision.

## JTBD-06 — Use the service in my actual context

**When** I use a mobile phone, regional language, screen reader, shared device, or unstable network,  
**I want** the core diagnosis to remain usable,  
**so that** the redesign is not limited to high-end desktop users.

---

# 5. Personas as contexts, not stereotypes

Personas are behavioral/access contexts. Do not infer income, education, competence or language from age, geography, gender or occupation.

## 5.1 Fast self-service user

Needs quick scan, immediate cause, minimal explanation by default, detailed evidence on demand.

## 5.2 Explanation-first user

Needs one concept per step, examples, plain-language terms, visible progress and no unexplained abbreviations.

## 5.3 Regional-language-first user

Needs meaningful translation, local-script rendering, no Latin-only identity assumptions, and ability to compare the source value exactly as stored.

## 5.4 Assisted user

May be sitting with a family member or service helper. Needs a “show me what to do” summary that can be discussed without exposing unnecessary IDs.

## 5.5 Screen-reader/keyboard user

Needs all meaning available outside graph/color, predictable focus, semantic headings and announced dynamic results.

## 5.6 Low-bandwidth/shared-device user

Needs small initial load, no mandatory media, recoverable state and clear `Reset demo` / `Clear this device` controls.

---

# 6. Scope priorities

## 6.1 P0 — must ship

### PRD-F01 Goal-first home

User can choose exactly one of the three golden tasks. No agency directory wall.

**Acceptance intent:** first CTA is visible without scrolling on common mobile/desktop sizes.

### PRD-F02 Fictional profile preview

Each task opens with a pre-seeded fictional citizen card.

Must show:

- fictional name;
- scenario description;
- `DEMO / FICTIONAL DATA` badge;
- no valid-looking government number;
- one-line privacy statement.

### PRD-F03 Relevant-record view

Show only records relevant to the selected goal initially. Additional records can be disclosed through `See other affected records`.

### PRD-F04 Difference highlighting

For a selected field, visually distinguish:

- exact same;
- compatible representation;
- blocking mismatch;
- needs review;
- missing required field.

Never rely on color alone.

### PRD-F05 Causal diagnosis

A “difference” becomes a “blocker” only when the selected service rule requires it.

UI must distinguish:

- `This is blocking the task.`
- `This looks different but is allowed in this simulated rule.`
- `This is not an identity issue.`
- `We cannot determine this from the available evidence.`

### PRD-F06 Evidence drawer

Every blocker has `Why?` with:

- records/fields used;
- rule statement in plain language;
- source title;
- source date/checked date;
- official-derived vs prototype assumption label;
- uncertainty note.

### PRD-F07 Dependency trail

Show citizen-readable chain such as:

`Your goal → DigiLocker request → DL issuer record → Name reconciliation`.

Desktop can show graph; mobile uses vertical trail. The trail is primary for accessibility.

### PRD-F08 Correction options

At least two options when legitimate alternatives exist. If only one source-backed route exists, do not invent a second option to make the UI look sophisticated.

Each option includes:

- target record;
- simulated change;
- what it fixes;
- what it may affect;
- effort class: `Online`, `Centre/office`, `Employer/issuer action`, `Review required`;
- evidence/doc requirements only when sourced;
- confidence;
- `Simulate` CTA.

### PRD-F09 Correction planner

The planner recommends one route with explanation such as:

> “Recommended because it resolves this target with one simulated change and does not introduce a new conflict in the records we model.”

Never say `best` without scope: the recommendation is best **within the synthetic rule set and modeled dependencies**.

### PRD-F10 Simulation

After simulation:

- state change is obvious;
- before/after is available;
- system re-runs all affected rules;
- status is announced to assistive technology;
- user can undo/reset;
- UI says no live government system was changed.

### PRD-F11 Readiness result

Use categorical state rather than fake precision:

- `READY IN THIS SIMULATION`
- `BLOCKED`
- `NEEDS REVIEW`
- `NOT AN IDENTITY-DATA ISSUE`

Avoid 87% “readiness scores” unless mathematically and semantically justified.

### PRD-F12 Official handoff

Final card lists exact next actions and official external destination. External link opens clearly as official site and is visually separate from the prototype.

### PRD-F13 English / Hindi

Core flow and all error/safety text exist in English and simple Hindi. Translation must preserve meaning of technical terms; agency names/IDs remain recognizable.

### PRD-F14 Accessibility

All P0 screens meet requirements in `03_UX_UI_DESIGN_SYSTEM.md` and `07_TESTING_ACCEPTANCE.md`.

### PRD-F15 Low-network behavior

Core deterministic flow has no critical network dependency beyond app delivery. AI explanation has loading timeout and local fallback copy.

### PRD-F16 Independent prototype disclosure

Persistent but non-obstructive. Minimum text:

> `Independent hackathon prototype · Fictional data · No government connection`

### PRD-F17 Source/provenance page

A small “Sources & limits” route lists the official sources behind rules and clearly identifies prototype assumptions.

### PRD-F18 Reset/clear

One control clears the current synthetic scenario and any local state. Shared-device users can confidently leave the app clean.

---

# 7. P0 journey detail

## 7.1 Journey A — DL fetch mismatch

### Entry copy

**Card:** `I can't fetch my Driving Licence`  
**Subcopy:** `See why a fictional DigiLocker retrieval fails and which record is causing it.`

### Flow

1. Select card.
2. Show fictional profile `Ananya R. Krishnan`.
3. `Run pre-flight` (or run automatically after 500 ms with explicit status).
4. Result: `Blocked — name representation does not reconcile for this mock retrieval rule.`
5. Show Aadhaar vs DL value with token-level emphasis.
6. `Why this matters` explains that DigiLocker states Aadhaar name should match the DL/RC source for retrieval.
7. Compare mock correction actions.
8. Planner recommends minimum-impact action.
9. User simulates.
10. Recompute: `Ready in this simulation`.
11. Show official next action and `What we did NOT do` disclosure.

### Emotional target

The citizen feels: **“Now I understand what the error actually means.”**

## 7.2 Journey B — EPFO causal disambiguation

### Entry copy

`My PF/KYC issue isn't getting resolved`

### Flow

1. Synthetic profile includes a visible name variation plus a missing/invalid simulated date-of-exit condition.
2. Analysis reports two findings.
3. Name finding marked `Compatible / non-blocking under this scenario` or `Review`, depending rule fixture.
4. Service-history finding marked `Actual blocker in this simulation`.
5. UI explicitly says: `Changing the name would not resolve this simulated claim.`
6. Show source-backed next route for the blocker.
7. Simulate service-history correction.
8. Recompute ready state.

### Product-thinking target

The judge sees that the system does not equate “things look different” with “this caused the failure.”

## 7.3 Journey C — Life-event sequence

### Entry copy

`My name or address changed — what should I update first?`

### Flow

1. Synthetic profile `Meera Nair` has a legitimate new-name/new-address state plus old values in selected records.
2. Citizen chooses the immediate goal: e.g. `fetch DL`, `complete PF KYC`, or `make records consistent` (P0 can preselect one for demo).
3. Planner maps dependencies.
4. Show Plan A vs alternative, with side effects.
5. User advances through simulated corrections.
6. Readiness after each step updates.
7. Final summary says which records still retain old value and whether they currently block the selected goal.

### Emotional target

The citizen feels: **“I know the order; I don't have to randomly update everything.”**

---

# 8. Content requirements

## 8.1 Vocabulary

Prefer:

- `record` over `database entry` in citizen copy;
- `doesn't match` over `validation exception`;
- `what to do next` over `resolution workflow`;
- `official site` over `upstream authority interface`;
- `needs review` over fake certainty;
- `simulated change` over `update` when referring to the prototype.

Use acronyms only after expansion where space permits.

## 8.2 Error format

Every error should answer:

1. What happened?
2. What did not happen?
3. Can the user continue?
4. What should they do?

Example AI timeout:

> **The plain-language explanation could not load.** Your diagnosis is unchanged because it was calculated locally from the demo rules. You can continue with the evidence view.

## 8.3 Safety copy

On every scenario:

> `This is fictional demo data. Do not enter real Aadhaar, PAN, UAN, OTP or payment details.`

---

# 9. Localization requirements

## 9.1 P0 locales

- `en-IN`
- `hi-IN`

## 9.2 Architecture

All visible copy must be keys, not hard-coded strings in components. Locale files must support pluralization and variable ordering.

## 9.3 Indic UI constraints

- Allow 30–60% text expansion without layout breakage.
- Avoid fixed-width buttons based on English labels.
- Use fonts with tested Devanagari and broader Indic support.
- Never place critical text inside raster images.
- Preserve source-record value exactly alongside any transliteration.
- Do not auto-transliterate a citizen's name and then present the generated result as authoritative.

## 9.4 Future-ready locales

Architecture should support, but P0 need not translate: Bengali, Tamil, Telugu, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Odia, Assamese, Urdu and others.

---

# 10. Accessibility product requirements

- No interaction is graph-only.
- “Blocked/ready” state contains text and icon, not color alone.
- Dynamic diagnosis result receives programmatic focus or polite live announcement without stealing focus unexpectedly.
- Screen-reader reading order mirrors visual priority.
- Compare table becomes cards/definition list on narrow widths.
- All drawers/modals trap focus correctly and return it to trigger.
- No hover-only explanation.
- Touch target minimum target 44 px in primary flow.
- Motion is functional and under 300 ms; reduced-motion mode removes graph transitions.
- All user actions remain possible at 200% browser zoom and 320 CSS px viewport width.

---

# 11. Trust requirements

## 11.1 Provenance labels

Every rule has one of:

- `OFFICIAL-SOURCE-DERIVED`
- `PROTOTYPE-SIMULATION`
- `ASSUMPTION / NEEDS AUTHORITY VALIDATION`

The citizen UI uses friendlier copy; developer/debug view may show exact tag.

## 11.2 No false officiality

The app must not use:

- national emblem;
- government department logos as app branding;
- `.gov.in`-like domain tricks;
- copy implying access to real government records.

Agency names can be used descriptively in text/cards to explain the journey.

## 11.3 Uncertainty

When a rule is incomplete, the system should say:

> `We can show the likely dependency in this prototype, but the official authority must confirm the actual correction route.`

Do not replace uncertainty with an LLM guess.

---

# 12. AI product requirements

## 12.1 P0 role

AI can generate a short plain-language explanation from a deterministic evidence packet and optionally Hindi translation.

## 12.2 AI must be visibly bounded

“AI explained this” is secondary. The result view must provide `Show evidence` so the judge can see the deterministic logic underneath.

## 12.3 No chatbot homepage

Do not open with “How can I help you today?” The product's structured goal selection is faster and safer.

## 12.4 Degraded mode

If the AI service fails, use pre-authored explanation templates. No journey becomes blocked.

---

# 13. Metrics

For the hackathon build, metrics are primarily acceptance metrics rather than growth metrics.

## North-star test metric

**Time to Correct Understanding (TCU):** median time from scenario entry to the citizen correctly identifying the causal blocker in moderated testing.

Target for golden demo profile: <= 25 seconds.

## Supporting metrics

- core journey completion <= 60 seconds for trained demo presenter;
- <= 5 primary interactions from scenario selection to first diagnosis;
- 100% P0 findings show provenance;
- 100% simulation actions reversible/resettable;
- 0 real sensitive IDs required;
- 0 critical WCAG blockers;
- 0 P0 routes requiring AI to determine state;
- all three golden E2E scenarios pass on desktop and mobile viewport.

Avoid vanity metrics such as total rules, total agents, number of database tables, or test count in the citizen pitch.

---

# 14. P1 opportunities

Only after P0 is fully stable:

1. Synthetic rejection-message parser.
2. Read-aloud explanation using browser speech / approved TTS.
3. Shareable action plan with no identifiers.
4. Third language chosen based on tester availability, not national assumptions.
5. Additional mock documents such as education certificate/passport.
6. Rule-change “last checked” indicators.

---

# 15. Product risks and mitigations

| Risk | Failure | Mitigation |
|---|---|---|
| Overclaiming | Product implies universal Indian matching rules. | Rule-specific scope; provenance; mock labels. |
| AI hallucination | Model invents correction route. | Structured evidence only; deterministic state; template fallback. |
| Scope explosion | Adds every government service. | Three golden journeys locked. |
| UI spectacle | Graph becomes product instead of explanation. | Goal/result first; graph is secondary. |
| Hindi-centric design | Treats Hindi as default India. | Explicit locale architecture; user choice; no auto-switch. |
| Name-model bias | Assumes surname/family structure. | Full-name field model + tokens/aliases; no automatic identity equivalence. |
| Real data misuse | Reviewer enters actual ID. | No real-ID fields; fictional profiles only. |
| Policy staleness | Official process changes. | Source dates, `last_checked_at`, limitations page. |
| Fake precision | Similarity/readiness score misleads. | Categorical states and evidence. |
| Rebuild risk | Pivot destroys stable deployment. | Reuse shell/tooling, replace domain vertical slice by slice. |

---

# 16. Release criteria

P0 can be called complete only when:

1. all three journeys work from clean browser state;
2. every state is usable on mobile;
3. English and Hindi core flows have no untranslated keys;
4. screen-reader smoke test completes one journey;
5. AI disabled test completes every journey;
6. all external official links are current and open in a safe new context;
7. synthetic/demo disclosure is always visible;
8. no government write is implied;
9. reviewer can access without login or can use clearly supplied fictional credentials;
10. the 2-minute demo can be recorded without cutting around failures.

---

# 17. Product decision log — locked

- **Decision:** hard pivot away from Handover29C domain.  
  **Reason:** previous journey lacked citizen transformation and instant problem recognition.

- **Decision:** Identity Rescue over generic EPFO Claim Rescue.  
  **Reason:** broader recognizability while preserving EPFO as a strong scenario; more differentiated systems insight.

- **Decision:** deterministic compatibility rules, AI explanation only.  
  **Reason:** identity and public-service decisions require traceability and must not depend on probabilistic output.

- **Decision:** three deep scenarios, not many shallow integrations.  
  **Reason:** hackathon evaluates complete functioning journey.

- **Decision:** no mandatory microservices/event-bus architecture.  
  **Reason:** prototype scale does not justify distributed complexity; engineering must serve visible citizen value.

- **Decision:** no dashboard-first interface.  
  **Reason:** goal-oriented citizen task completion is the product.
