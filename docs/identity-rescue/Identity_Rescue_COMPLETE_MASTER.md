# Identity Rescue — Complete Master Specification

**Generated:** 22 August 2026

> This file concatenates the entire product-freeze package for one-shot ingestion by an implementation agent. Individual files remain authoritative according to README precedence.


---

<!-- BEGIN README.md -->
# Identity Rescue — Product Freeze Package

**Hackathon:** Build What Moves India  
**Product working title:** Identity Rescue  
**Freeze date:** 22 August 2026  
**Submission deadline used by this package:** 28 August 2026, 8:00 PM IST (official Builder Brief/FAQ as checked on 22 August 2026)  
**Status:** BUILD SOURCE OF TRUTH — do not broaden scope without replacing an explicit requirement.

## 1. What this package is

This package converts the pivot from Handover29C into a buildable, testable citizen product. It is deliberately biased toward the criteria the hackathon actually evaluates: real problem severity, a complete citizen journey, usability, product thinking, end-to-end engineering, and honesty about mocks and dependencies.

Identity Rescue is **not** a government identity system, identity-proofing service, Aadhaar/PAN matcher, grievance portal, or general AI assistant. It is an independent hackathon prototype that uses **only fictional/synthetic data** to demonstrate how a citizen could diagnose cross-service identity-data conflicts, understand the causal blocker, compare safe correction paths, simulate a correction, and leave with the exact official next action.

## 2. Locked product thesis

> Indian citizens are often forced to reconcile inconsistent identity representations across public-service systems themselves. A name expansion, token order, stale address, date-of-birth discrepancy, issuer mismatch, or downstream record dependency can block a service while each portal only reports its local failure. Identity Rescue reconstructs a synthetic cross-service identity graph, identifies the blocker for a chosen citizen goal, explains the evidence in plain language, compares correction paths, and simulates the minimum safe sequence before the citizen acts on official portals.

The product is best understood as a **pre-flight debugger for a citizen journey**.

## 3. Source-of-truth order

When documents disagree, use this order:

1. `00_MASTER_SPEC.md` — locked product boundary and non-negotiables.
2. `01_PRD.md` — user value, scope, journeys, priorities.
3. `02_SRS.md` — implementable functional/non-functional requirements.
4. `03_UX_UI_DESIGN_SYSTEM.md` — screen, component, content, accessibility behavior.
5. `04_CITIZEN_SCENARIOS_RULEBOOK.md` — synthetic profiles, deterministic rules, planner behavior.
6. `05_AI_SAFETY_GROUNDING.md` — what AI may and may not do.
7. `06_DATA_PRIVACY_SECURITY.md` — data, privacy, trust, threat controls.
8. `07_TESTING_ACCEPTANCE.md` — objective definition of done.
9. `08_DEMO_SUBMISSION.md` — reviewer path, video, summary, submission gates.
10. `09_IMPLEMENTATION_BACKLOG.md` — execution sequence and scope cuts.
11. `10_MASTER_AGENT_PROMPT.md` — loop prompt for the coding agent.
12. `SOURCES.md` — research basis and evidence status.

## 4. Three golden journeys — P0 only

The demo build must make these three journeys excellent before adding anything else:

1. **DigiLocker / Driving Licence fetch mismatch** — citizen sees which exact representation conflict blocks retrieval, why it matters, and the safest mock correction path.
2. **EPFO KYC / claim pre-flight** — system distinguishes an identity mismatch from a non-identity service-history blocker instead of falsely blaming the name.
3. **Life-event reconciliation** — citizen has legitimately changed name/address and needs to understand which synthetic record should be updated first and what downstream services may be affected.

These journeys cover: direct identity mismatch, causal disambiguation, and correction sequencing.

## 5. Non-negotiables

- The first useful result must be reachable in **under 20 seconds** from landing page using a demo profile.
- A reviewer must be able to complete one entire journey without creating an account, entering any real ID, or reading documentation.
- Every citizen-facing diagnosis must show **evidence**, **effect**, **recommended action**, and **what remains uncertain**.
- Deterministic rules decide blockers and correction consequences. AI may explain; AI must not decide identity equivalence, eligibility, or legal correctness.
- Every government interaction is mocked or linked out. No private/undocumented government API use.
- Never request or store real Aadhaar, PAN, UAN, OTP, payment, or sensitive personal data.
- Do not present the product as government-authorized. Persistent independent-prototype disclosure is required.
- No dashboard-first design. No admin panel. No vanity analytics in the main journey.
- Mobile is first-class, not a responsive afterthought. Core flow works at 320 CSS px width with no two-dimensional scrolling for normal content.
- Accessibility target: WCAG 2.1 AA / GIGW 3.0-aligned interaction behavior.
- English and simple Hindi are P0. The information architecture must not assume Hindi is universal; all copy and components must remain locale-ready for other Indian languages/scripts.
- No architecture pattern is included merely because it is sophisticated. SQLite/local persistence is acceptable for the prototype if it preserves deterministic behavior and replayability.
- The core demo must remain functional if an OpenAI runtime call is unavailable. AI failure degrades explanation quality, never the underlying diagnosis.

## 6. Package philosophy

The previous build over-optimized invisible engineering. This package reverses the ratio:

**Citizen value first → product logic second → evidence and safety third → implementation sophistication only where it improves those three.**

The retained engineering foundation is useful only if it accelerates the new journey: accessibility primitives, bilingual infrastructure, deterministic test harnesses, Docker/deployment, mock-data discipline, and stable persistence.

## 7. Research corrections applied

The supporting research file correctly emphasizes progressive disclosure, plain-language errors, accessibility, modular boundaries, and privacy-by-design. This package deliberately does **not** make Saga, Kafka, SEDA, microservices, transactional outbox, or hash-chain infrastructure mandatory. For a six-day independent prototype with simulated integrations, those patterns are unjustified unless the existing repository already uses them and keeping them is cheaper than removal.

The package also treats DPDP compliance carefully: the Digital Personal Data Protection Rules, 2025 have a phased commencement schedule. We design for data minimization and transparent notice, but do not make false legal-compliance claims.

## 8. Build command for humans and agents

Before coding anything:

1. Read `00_MASTER_SPEC.md` through `07_TESTING_ACCEPTANCE.md`.
2. Audit the existing Handover29C repository for reusable infrastructure.
3. Delete/quarantine vehicle-transfer domain logic from citizen routes.
4. Implement the three golden journeys in the exact P0 order.
5. Run acceptance gates after every vertical slice.
6. Do not start P1 until every P0 gate passes.

## 9. Definition of success

A judge should understand the problem in one sentence, see a specific blocker within seconds, change one synthetic fact, watch the downstream state recompute, understand why the recommendation is safe, and know exactly what the citizen would do next on an official channel.

If the demo instead requires explanation of the architecture before the value is visible, the product is not done.

<!-- END README.md -->

---

<!-- BEGIN 00_MASTER_SPEC.md -->
# 00 — Identity Rescue Master Product Specification

## Document status

**Authority:** Highest.  
**Purpose:** Freeze the product, citizen outcome, system boundary, safety boundary, and quality bar.  
**Change rule:** Any change that alters the core problem, golden journeys, data policy, or deterministic/AI boundary must be recorded as an explicit product decision. Do not silently broaden the product.

---

# 1. Product thesis

## 1.1 Problem statement

Indian public-service journeys frequently depend on citizen attributes stored in multiple systems. Those systems may represent the same human-readable fact differently: initials versus expanded names, different token order, stale address, local-language transliteration, a missing surname, historical records, or a legitimate life-event update. The citizen encounters the failure at the final service but is often told only that the details do not match.

The citizen therefore has to answer three hard questions without a system-level view:

1. **What exactly is inconsistent?**
2. **Is that inconsistency actually causing the service failure?**
3. **What should I correct first without creating another downstream mismatch?**

Identity Rescue demonstrates a better public-service interaction: diagnose the goal-specific blocker, show the evidence, explain the dependency, compare correction routes, simulate the consequences, and hand the citizen a precise next-action plan.

## 1.2 One-line pitch

> **Every portal tells you what failed. Identity Rescue tells you what to fix first.**

## 1.3 Product category

Citizen-facing diagnostic and pre-flight decision-support prototype for cross-service identity-data reconciliation.

## 1.4 What makes this different

This is not “better forms” and not “chat with government FAQs.” The product introduces a visible computational model:

**Citizen goal → relevant records → field-level evidence → service rule → causal blocker → correction options → downstream impact → simulated readiness → official next action.**

The innovation is the correction planner and causal explanation, not the mere detection of string differences.

---

# 2. Hackathon alignment

The official Builder Brief requires one real problem, a complete citizen journey, improved usability, accommodation of real Indian users including mobile/slower connections/limited digital experience, synthetic data for sensitive dependencies, and clear disclosure of mocks. Reviewers test the citizen experience rather than an admin panel.

Identity Rescue optimizes directly for those requirements:

| Judging axis | Product response |
|---|---|
| Problem | Cross-system identity-data mismatches and opaque resolution are documented by official Indian services. |
| Working build | Three deterministic end-to-end synthetic journeys. |
| Usability | Goal-first flow, progressive disclosure, plain language, evidence cards, simulation. |
| Product thinking | Distinguishes correlation from causation and optimizes correction order, not only similarity score. |
| End-to-end thinking | Models issuer/service dependencies, rule provenance, adapters, planner and official handoff. |
| Honesty | Persistent prototype badge, synthetic profiles, no live government connections, evidence provenance. |

---

# 3. Product principles

## P-01 — Goal before documents

Never begin by asking the citizen to inventory IDs. Begin with **“What are you trying to do?”** The target service determines which records and rules matter.

## P-02 — Cause before correction

A visible mismatch is not automatically a blocker. The product must identify whether it is causal for the selected journey.

## P-03 — Minimum necessary correction

Recommend the smallest change set that resolves the target service while minimizing downstream disruption, citizen effort, irreversible actions and uncertainty.

## P-04 — Evidence, not authority theatre

Every conclusion must trace to synthetic record values plus a locally stored rule/evidence object. Never phrase a recommendation as an official government determination.

## P-05 — Indian identity semantics, not Western name assumptions

Do not hard-code first-name/last-name logic as universal. Indian records can use initials, expanded initials, patronymics, matronymics, multi-token surnames, no surname, different token ordering, local scripts and transliteration. UIDAI and Passport Seva themselves document such cases.

## P-06 — Language is a user setting, not a nationality assumption

English and simple Hindi ship first because of hackathon time. The system must not treat Hindi as “the Indian language.” Locale architecture, text expansion and Indic-script typography must be ready for additional languages.

## P-07 — Accessible by construction

Semantic HTML, keyboard operation, focus visibility, screen-reader labels, reflow, contrast, status announcements and reduced-motion behavior are acceptance criteria, not polish.

## P-08 — Low-bandwidth by default

No hero video, heavy illustrations, large graph libraries or blocking AI call on the critical path. Core bundle, cached synthetic data and deterministic rules should allow meaningful use on unstable networks.

## P-09 — AI is subordinate to rules

The model may extract, rewrite, translate, summarize or explain evidence. It may not establish that two identities are the same person, decide a legal entitlement, fabricate a government requirement, or override deterministic rule outcomes.

## P-10 — The prototype must refuse the wrong problem

If a chosen service is blocked by a non-identity cause, Identity Rescue must say so. A correct “this is not an identity-data issue” is more trustworthy than forcing every failure into the product thesis.

## P-11 — No government impersonation

No Ashoka emblem, ministry/agency logos, official color mimicry intended to imply endorsement, or copy such as “Government of India service.” The product is visibly independent.

## P-12 — No real sensitive data

The main build has no input path requiring real Aadhaar/PAN/UAN/OTP/payment data. Demo scenarios use fictional profiles only.

---

# 4. Primary users and Indian usage contexts

There is no single “Indian user.” The product must work across contexts rather than demographic caricatures.

## UC-A — Self-service mobile citizen

- Comfortable with UPI/app-style flows but not government terminology.
- Uses Android/mobile browser.
- Wants a quick explanation and direct next step.

## UC-B — Regional-language-first citizen

- May understand the concept better in a regional language than in English.
- Names/addresses may appear in local script and Latin transliteration.
- Needs terminology translated by meaning, not word-for-word bureaucratic transliteration.

## UC-C — Assisted citizen

- A family member, CSC-like helper, employer HR representative or trusted person may sit beside the citizen.
- UI must make it possible to explain the issue without exposing unnecessary identifiers.
- “Show why” and “What to carry/do” are more important than hidden scoring.

## UC-D — Older or low-digital-literacy citizen

- Benefits from one decision per screen, persistent progress, concrete verbs, no jargon, forgiving back navigation and no loss of state.

## UC-E — Citizen using assistive technology

- Requires screen-reader structure, full keyboard operation, status announcements, non-color cues and magnification/reflow.

## UC-F — Citizen with unstable connectivity/shared device

- Needs small payloads, deterministic local/synthetic data, restartable flow, explicit session reset, no sensitive residue.

## UC-G — Citizen with non-canonical name structure

- Initials, expanded initials, no surname, multi-part surname, name order variation, patronymic conventions or local-script representation must not be scored as “wrong” merely because the token pattern differs.

---

# 5. Locked P0 journeys

## GJ-01 — DigiLocker Driving Licence fetch mismatch

**Citizen goal:** “I cannot fetch my Driving Licence in DigiLocker.”

**Synthetic evidence:** Aadhaar-name representation differs from National Register/DL representation in a way the selected mock retrieval rule treats as blocking.

**Outcome:**

1. Product shows relevant records only.
2. Highlights exact conflicting tokens/representation.
3. Explains the retrieval dependency.
4. Shows at least two mock correction paths.
5. Warns against changing a stable upstream record unnecessarily.
6. Simulates chosen correction.
7. Recomputes retrieval readiness.
8. Ends with exact official channel/action guidance sourced from the rulebook.

## GJ-02 — EPFO pre-flight with causal disambiguation

**Citizen goal:** “Why is my PF/KYC or claim still blocked?”

**Synthetic evidence:** Profile intentionally contains both a name variation and a service-history/exit-date problem.

**Required product behavior:** The system must demonstrate that **not every mismatch is causal**. Depending on the configured scenario, the service-history rule remains the blocker even after a cosmetic/acceptable name variation is normalized.

**Outcome:**

- Identity state: compatible / needs review / blocking.
- Non-identity service-history state: blocking.
- Product says: “Changing your name record would not fix this simulated claim.”
- Exact next route focuses on the causal blocker.

## GJ-03 — Life-event correction sequencing

**Citizen goal:** “My name/address changed. What should I update first?”

**Synthetic evidence:** At least four mock records have old/new variants and two target services depend on them differently.

**Outcome:**

- Citizen selects desired target outcome.
- Planner shows the smallest safe sequence.
- Each step includes effort, channel, required synthetic evidence and downstream effects.
- Simulation updates the graph step-by-step.

---

# 6. Explicit non-goals

The product must not become any of the following before submission:

1. Universal identity verification or KYC engine.
2. Biometric matching service.
3. Live Aadhaar/PAN/UAN lookup tool.
4. Government data aggregator.
5. Legal-advice engine.
6. Autonomous form submission bot.
7. Grievance filing automation.
8. OCR-based personal-document ingestion.
9. General government chatbot.
10. Admin dashboard/agency case-management product.
11. “AI agent swarm.”
12. Blockchain/audit-chain showcase.
13. Full India-wide policy ontology.
14. Real-time synchronization with government systems.
15. Replacement for official portals.

---

# 7. Core information model

## 7.1 Goal

A citizen-intent object such as `DIGILOCKER_FETCH_DL`, `EPFO_KYC_PREFLIGHT`, `LIFE_EVENT_NAME_RECONCILIATION`.

## 7.2 Synthetic citizen profile

Contains fictional stable profile ID, locale preference, synthetic records, scenario tags and expected golden outcome.

## 7.3 Record

A representation of citizen attributes held by a mock authority/issuer. Fields are not treated as globally authoritative; they have provenance, update route, last-synthetic-update date and source label.

## 7.4 Field observation

Value as seen in a particular record, e.g. name string, DOB, address fragment, mobile-status flag. Store original plus derived normalized forms.

## 7.5 Rule

Deterministic policy/compatibility rule with:

- rule ID;
- service/goal;
- required fields;
- comparison semantics;
- severity;
- evidence source title/date;
- mock/official-derived status;
- citizen explanation template;
- correction routes;
- uncertainty note.

## 7.6 Finding

A computed mismatch, compatibility observation or non-identity blocker. A finding is not a recommendation.

## 7.7 Blocker

A finding determined by the selected service rule to prevent the simulated goal.

## 7.8 Correction action

Synthetic change with target record, field, route, effort level, prerequisites, reversibility, uncertainty and downstream impact edges.

## 7.9 Plan

Ordered correction actions generated by deterministic search against the target readiness condition.

## 7.10 Evidence citation

Human-readable source label and URL/date stored with rule metadata. The UI may show short source labels; detailed references live in “Why this?” drawer.

---

# 8. Deterministic reasoning model

## 8.1 Matching is multi-stage

1. Preserve originals.
2. Unicode normalization.
3. Script/language tagging where known.
4. Conservative whitespace/punctuation normalization.
5. Tokenization.
6. Optional honorific removal for comparison only where rule permits.
7. Initial detection without automatic expansion.
8. Known synthetic alias/expansion relationships from the profile, not guessed globally.
9. Token-order comparison where rule permits.
10. Transliteration relationship only when source metadata provides both representations or a controlled synthetic mapping.
11. Rule-specific compatibility decision.

A single Levenshtein/Jaro score is never sufficient to label a record “same person.”

## 8.2 Finding states

- `MATCH_EXACT`
- `MATCH_RULE_COMPATIBLE`
- `VARIANT_NON_BLOCKING`
- `MISMATCH_BLOCKING`
- `MISMATCH_REVIEW`
- `MISSING_REQUIRED`
- `NON_IDENTITY_BLOCKER`
- `UNKNOWN`

## 8.3 Correction planner objective

Minimize a weighted cost:

`total_cost = citizen_effort + downstream_breakage_risk + uncertainty_penalty + irreversible_action_penalty + number_of_steps`

subject to:

- selected target service becomes `READY`;
- no P0-critical dependent service becomes `BLOCKED` unless explicitly acknowledged;
- only allowed synthetic actions may be chosen;
- unknown rules cannot be converted into false certainty.

Weights are product configuration, not learned from user data.

---

# 9. Experience architecture

## 9.1 Landing

Single primary question: **“What are you trying to do?”**

Three visible demo cards, each phrased as a citizen problem, not an agency category.

Primary CTA: `Try a fictional case`.

Secondary: `How this prototype works`.

Persistent banner: `Independent hackathon prototype · Uses fictional data · Does not connect to government systems`.

## 9.2 Scenario setup

Show fictional profile card with a prominent `DEMO DATA` badge. Never present synthetic Aadhaar/PAN numbers formatted to look convincingly real; use masked/non-valid placeholders such as `AADHAAR-DEMO-01`.

## 9.3 Diagnosis

Above the fold:

- target goal;
- readiness state;
- one-sentence cause;
- next best action.

Then progressive disclosure:

- `Show the mismatch`;
- `Why does this block me?`;
- `Compare ways to fix it`;
- `See official source`.

## 9.4 Identity/dependency map

Graph is supportive, not primary. On mobile it becomes a vertical dependency trail. Every visual edge has a text equivalent.

## 9.5 Correction comparison

Each option card shows:

- what changes;
- what it fixes;
- what else may be affected;
- effort;
- confidence;
- official route;
- whether simulation is reversible.

## 9.6 Simulation

Never use language like “Updated Aadhaar.” Use:

`Simulate this correction` → `Fictional record changed for this demo only`.

Then animate/reannounce recalculation and show before/after.

## 9.7 Handoff

Final screen:

- `What to do next` numbered steps;
- `What not to change` where useful;
- documents/evidence if source-backed;
- official service link;
- caveat: process can change; verify on linked official portal;
- reset demo.

---

# 10. Design language

## 10.1 Tone

Calm, competent, non-accusatory. The system should not say “your Aadhaar is wrong” or “EPFO made an error” when it only knows records differ.

Preferred:

> “These two records represent your name differently, and this simulated service requires the values to reconcile.”

Avoid:

> “Government database mismatch detected!”

## 10.2 Visual hierarchy

- neutral background;
- strong text contrast;
- one primary action per state;
- red reserved for blocking status, not decoration;
- amber for review/uncertainty;
- green for simulated readiness;
- every color paired with icon + text label;
- no glassmorphism, neon gradients, animated particles, “AI sparkle” motifs or fake government styling.

## 10.3 Typography

Use Noto Sans family or an equivalently tested family with Indic-script coverage. Avoid narrow display fonts and all-caps body copy.

---

# 11. AI boundary

Runtime AI is optional to the deterministic journey but can strengthen the demo if implemented safely.

## Allowed

- convert a synthetic bureaucratic error remark into structured candidate fields;
- rewrite a deterministic finding into plain English/Hindi;
- produce a concise explanation constrained to cited rule facts;
- translate controlled UI explanatory text;
- answer a narrow “Why?” question using only the current finding/evidence packet.

## Forbidden

- decide that two records belong to the same real person;
- decide actual Aadhaar/PAN/EPFO eligibility;
- infer missing legal facts;
- recommend document fabrication/alteration;
- submit anything to a government service;
- claim official approval;
- use open-web retrieval at runtime for an uncited policy decision;
- alter deterministic blocker state.

---

# 12. Data boundary

## P0 data policy

- 100% synthetic profiles.
- No real user account required.
- No text field labelled “Enter Aadhaar/PAN/UAN.”
- If a free-text synthetic rejection demo exists, display a warning not to paste real personal data and redact common ID-like patterns before logging or model calls.
- Analytics, if used, record only anonymous product events such as scenario ID and completion stage.
- Logs must never contain synthetic “realistic-looking” sensitive numbers either; use stable demo IDs.

---

# 13. Architecture boundary

## Required components

1. Citizen web UI.
2. Scenario/profile fixture store.
3. Mock service adapter interface.
4. Deterministic normalization/comparison library.
5. Rule engine.
6. Readiness evaluator.
7. Correction planner.
8. Evidence/provenance store.
9. Optional bounded OpenAI explanation service.
10. Local audit/event journal sufficient to replay simulation state.

## Not required

Kafka, microservices, distributed transactions, real OAuth, real biometrics, external event bus, vector database, multi-agent orchestration, Kubernetes.

If the existing code already has infrastructure that is stable and does not slow the pivot, it may remain behind interfaces. It must not appear as a citizen-facing feature merely to justify its existence.

---

# 14. Performance and resilience targets

- Critical interaction usable on current Chromium, Firefox, Safari and Android Chromium-class browsers.
- First meaningful content target <= 2.5 s on a simulated mid-tier mobile/slow 4G profile after deploy optimization.
- Deterministic diagnosis after scenario selection target <= 300 ms client-observed excluding animation.
- Core route should not wait on AI.
- Core app usable if AI endpoint returns timeout/5xx.
- No routine horizontal scroll at 320 CSS px.
- Avoid payload-heavy network visualization library if a lightweight SVG/DOM implementation suffices.
- Persist in-progress demo locally only if it does not create confusing stale state; provide obvious Reset.

---

# 15. Accessibility targets

At minimum:

- WCAG 2.1 AA-aligned implementation;
- semantic landmarks and one clear H1 per screen;
- skip link;
- visible focus;
- keyboard complete;
- 44x44 px-equivalent touch targets where practical;
- text zoom/reflow without content loss;
- contrast >= 4.5:1 for normal text unless applicable WCAG exception;
- live-region announcements for recalculation/status changes;
- graph has linear text alternative;
- form errors are linked to fields and described in text;
- motion respects `prefers-reduced-motion`;
- no timeout-dependent citizen task in demo;
- language attribute changes with locale;
- local-language labels are real localized strings, not images.

---

# 16. P0 feature inventory

| ID | Feature | P0 outcome |
|---|---|---|
| F-01 | Goal-first landing | Judge chooses a problem in one click. |
| F-02 | Fictional profile loader | No real sensitive input. |
| F-03 | Record comparison | Relevant fields shown side-by-side. |
| F-04 | Causal blocker engine | Identifies blocker vs non-blocking difference. |
| F-05 | Evidence explanation | Shows source-backed “why.” |
| F-06 | Dependency trail/graph | Makes cross-system consequence visible. |
| F-07 | Correction option comparison | Shows trade-offs. |
| F-08 | Deterministic correction planner | Recommends minimum safe sequence. |
| F-09 | Simulation | Before/after readiness changes visibly. |
| F-10 | Exact official handoff | Citizen knows next action. |
| F-11 | EN/HI toggle | Core copy available in English/simple Hindi. |
| F-12 | Accessibility controls | Essential accessibility is native; optional UX4G-like controls may supplement. |
| F-13 | Offline/AI degradation | Diagnosis remains usable without AI. |
| F-14 | Prototype/synthetic disclosure | Persistent and unambiguous. |

---

# 17. P1 only after P0 passes

- additional language pack;
- “paste a synthetic rejection remark” parser;
- voice read-out of explanation;
- downloadable/shareable action summary without identifiers;
- more mock issuers;
- richer correction cost settings;
- optional user testing instrumentation.

# 18. P2 / post-hackathon

- approved public sandboxes;
- consent-based data imports;
- assisted-service mode;
- policy administration tooling;
- continuous source-change monitoring;
- formal graph optimization;
- production identity assurance architecture;
- legal/compliance review;
- government co-design.

---

# 19. Critical failure conditions

The build is **not submission-ready** if any is true:

1. Reviewer must enter real-looking personal numbers.
2. Main result depends on an LLM response.
3. Product calls a visible mismatch “the cause” without a service rule.
4. Simulation looks like a real government write.
5. Graph is unreadable on mobile or inaccessible without vision.
6. A correction recommendation has no provenance or uncertainty state.
7. Hindi copy is machine-like or the UI assumes Hindi represents all Indian languages.
8. Any feature shown in the video is non-functional.
9. Government logo/branding implies endorsement.
10. Main journey takes longer than the first demo minute.
11. User can complete the flow but still does not know the official next action.
12. Architecture explanation occupies product UI space better used for citizen clarity.

---

# 20. North-star demo moment

The central visual transformation is:

**BLOCKED → explain exact causal edge → simulate one safe correction → recompute → READY, with “no new conflicts detected” and the official next step.**

Everything in the product exists to make that transformation credible, fast and understandable.

<!-- END 00_MASTER_SPEC.md -->

---

<!-- BEGIN 01_PRD.md -->
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

<!-- END 01_PRD.md -->

---

<!-- BEGIN 02_SRS.md -->
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

<!-- END 02_SRS.md -->

---

<!-- BEGIN 03_UX_UI_DESIGN_SYSTEM.md -->
# 03 — UX/UI Design System & Screen Specification

## Identity Rescue

**Objective:** Make the citizen transformation obvious without turning the product into a dashboard, chatbot, or government-site imitation.

---

# 1. Design thesis

The interface should feel like a **calm diagnostic conversation with visible evidence**, not a government form and not an AI showcase.

The citizen must always know:

1. **What am I trying to do?**
2. **What is blocking it?**
3. **Why do you think that?**
4. **What can I do?**
5. **What happens if I do it?**
6. **Where do I go officially?**

Any component that does not improve one of those questions is suspect.

---

# 2. Anti-slop rules

MUST NOT use:

- generic “AI-powered” hero text;
- glowing orbs, neural-network backgrounds, sparkles around every AI output;
- gradient-heavy SaaS aesthetic;
- 3D India maps;
- random glassmorphism;
- “Welcome back, citizen!” dashboard greetings;
- arbitrary readiness percentages;
- huge KPI cards like `4 mismatches`, `78% identity health` as primary value;
- chatbot as the only navigation;
- fake testimonials;
- stock photos of Indian families;
- cartoon bureaucrats;
- patriotic ornamentation unrelated to usability;
- tricolour palette as default branding;
- Ashoka emblem/government logos implying officiality;
- dense enterprise graph visible before the diagnosis;
- motion that delays task completion.

The product should look designed for India because of **language, naming semantics, mobile behavior, accessibility, content and service context**, not decorative nationalism.

---

# 3. Visual system

## 3.1 Brand character

- trustworthy;
- independent;
- legible;
- restrained;
- modern but not startup-theatrical;
- warm enough to reduce anxiety, not playful about serious citizen problems.

## 3.2 Palette semantics

Define tokens rather than hard-coding agency colors.

- `surface/base` — neutral light background.
- `surface/elevated` — cards.
- `text/primary` — near-black.
- `text/secondary` — muted but WCAG-compliant.
- `status/blocking` — dark red family.
- `status/review` — amber/brown family.
- `status/ready` — green family.
- `status/info` — blue family.
- `border/subtle` — neutral.
- `focus` — high-contrast dedicated ring.

Every status includes text and icon. Do not encode meaning through color alone.

Dark mode is P1 unless already essentially free in the existing design system. Do not sacrifice P0 contrast/testing for it.

## 3.3 Typography

Recommended: **Noto Sans** family with tested Indic-script fallbacks. Rationale: broad Indic support and alignment with UX4G guidance.

Suggested scale:

- Display/hero: 32–40 px desktop, 28–32 mobile; used sparingly.
- H1: 28–32 desktop, 24–28 mobile.
- H2: 22–24.
- H3: 18–20.
- Body: 16–18, line-height 1.5–1.65.
- Supporting: >= 14.
- Avoid all-caps labels for long text/Indic scripts.

Text must survive 200% zoom and longer translated strings.

## 3.4 Spacing

Use 4/8 px base. Preferred content width 720–960 px for reading flows; comparison views can expand to ~1120 px desktop.

Mobile page side padding: 16–20 px.

Do not make cards unnecessarily dense. Critical status sections need whitespace around them.

## 3.5 Radius and elevation

Moderate radii (8–14 px). Use borders more than shadows. Avoid floating-card overload.

---

# 4. Global shell

## Header

Left: simple wordmark `Identity Rescue` or final chosen name.  
Right: language selector + `Sources & limits` + accessibility/settings icon if needed.

Below/within header: compact trust strip:

> **Independent hackathon prototype · Fictional data · No government connection**

On mobile this may collapse to `Demo prototype · Fictional data` with accessible expansion.

## Footer

- About the prototype
- Sources & limitations
- Privacy
- Reset demo
- Built for Build What Moves India (text only; no false partner endorsement beyond accurate hackathon disclosure)

---

# 5. Screen map

```text
/
├─ /case/digilocker-dl
│  ├─ diagnosis
│  ├─ evidence
│  ├─ options
│  ├─ simulation
│  └─ next-action
├─ /case/epfo-preflight
│  └─ same state model
├─ /case/life-event
│  └─ same state model
├─ /sources
├─ /privacy
└─ /about
```

States may be route segments or one stateful route. Browser back/refresh behavior must remain deterministic.

---

# 6. Home screen specification

## Purpose

Get the judge/citizen into meaningful diagnosis with one click.

## Above-the-fold order

1. Independent prototype label.
2. H1:
   **When one government record says one thing and another says something else, what should you fix first?**
3. Short supporting line:
   `Choose a fictional case. We’ll show the blocker, why it matters, and what a safer correction sequence could look like.`
4. Three scenario cards.
5. Small reassurance:
   `No real Aadhaar, PAN, UAN or OTP required.`

## Scenario card anatomy

Icon (descriptive, not agency logo)  
Citizen statement  
One-line value  
Badge: `FICTIONAL CASE`  
CTA: `Try this case`

### Card A
**I can't fetch my Driving Licence**  
`Trace a name mismatch across a mock Aadhaar and DL record.`

### Card B
**My PF/KYC issue isn't getting resolved**  
`See how the system separates an identity difference from the real blocker.`

### Card C
**My name or address changed**  
`Compare which fictional record to update first and what it could affect.`

## What NOT to put on home

- sign-up;
- giant explainer diagram;
- list of supported agencies;
- architecture metrics;
- AI chat input;
- testimonial carousel;
- “identity score.”

---

# 7. Case header

Once inside a case, display:

- breadcrumb/back: `All demo cases`;
- case title as H1;
- one-line citizen goal;
- fictional profile chip;
- current state chip: `Blocked`, `Needs review`, `Ready in simulation`;
- step indicator using meaningful labels rather than `Step 2 of 7` alone.

Suggested labels:

`Understand → Compare → Simulate → Next action`

On mobile use an accessible compact progress list.

---

# 8. Diagnosis screen

This is the most important screen.

## 8.1 First viewport

### Status eyebrow
`SIMULATED PREFLIGHT RESULT`

### H1/result
**Blocked by one record mismatch**

or in EPFO scenario:

**The visible name difference is not the blocker**

### Explanation
Maximum ~2 short sentences before disclosure controls.

Example:

> `The mock Aadhaar record says “ANANYA R KRISHNAN” while the mock DL source says “ANANYA KRISHNAN RAMESH”. This demo retrieval rule requires those name records to reconcile before the document can be fetched.`

### Primary CTA
`Compare ways to fix this`

### Secondary
`Show the evidence`

Do not force the citizen to inspect raw data before understanding the conclusion.

## 8.2 Record comparison component

Desktop: two or three vertical cards, not a dense 10-column table.  
Mobile: stacked records with a sticky field label.

Each record card:

- authority/service name in plain text;
- `FICTIONAL RECORD` badge;
- exact source value;
- field status label;
- expandable details.

Token emphasis must remain readable by screen readers. Visual token highlights are supplemental; accessible text says what differs.

## 8.3 Mismatch language

Use semantic labels:

- `Exact match`
- `Different, but compatible here`
- `Blocks this task`
- `Needs review`
- `Missing required detail`
- `Not related to this failure`

Never use `bad data`, `invalid person`, `wrong identity` unless the source itself establishes invalidity.

---

# 9. Evidence drawer / “Why?”

## Trigger

`Why does this block the task?`

## Drawer content order

1. **Rule in plain language**
2. **Evidence used**
3. **What the product concluded**
4. **Official-source basis**
5. **Prototype limitation**

Example:

**Rule**  
`For this fictional DL retrieval, the name from the Aadhaar-linked DigiLocker profile must reconcile with the issuer record.`

**Evidence**  
`Aadhaar demo name: …`  
`DL demo name: …`

**Source basis**  
`DigiLocker FAQ — Driving Licence / RC retrieval guidance. Checked 22 Aug 2026.`

**Limit**  
`The actual issuer may apply additional checks that this prototype does not model.`

Use an external-link icon/text for official source.

---

# 10. Dependency visualization

## Principle

The graph is a **proof mechanism**, not visual entertainment.

### Desktop

Maximum 4–6 nodes in a P0 view. Example:

`Your goal` → `DigiLocker fetch` → `DL issuer record`  
                    ↑  
             `Aadhaar name`

Red edge = blocking; green = satisfied; amber = review.

### Mobile/text equivalent

Render:

1. `You want to fetch your DL.`
2. `DigiLocker asks the issuer for the record.`
3. `This retrieval uses your Aadhaar-linked name.`
4. `The issuer record represents the name differently.`
5. `In this demo rule, that difference blocks retrieval.`

A screen-reader user should lose zero explanatory meaning by never encountering the SVG visually.

---

# 11. Correction comparison screen

## H1
`Two ways this fictional case could be resolved`

## Recommended card

Use `Recommended in this simulation`, never `Officially recommended`.

Fields:

- **Change:** what record/field;
- **Why:** target service effect;
- **Effort:** Online / Centre / Issuer action / Employer action / Review;
- **Downstream:** e.g. `No new conflicts in the records modeled here`;
- **Confidence:** `High within this demo rule` / `Needs official confirmation`;
- **Source basis:** link/drawer;
- CTA `Simulate this route`.

## Alternative card

Same anatomy. If an alternative would create modeled downstream conflicts, surface them prominently.

## Trade-off wording

Prefer concrete trade-offs:

> `This route changes one downstream record.`

rather than:

> `Risk score: 32%`.

---

# 12. Simulation interaction

## Confirmation copy

**Simulate this correction?**  
`This changes only the fictional case in your browser. No government record will be contacted or updated.`

Actions:

- `Simulate correction` primary
- `Cancel` secondary

## Animation

150–250 ms state transition. With reduced motion, immediate state replacement.

During recompute:

`Rechecking the records in this demo…`

Do not mimic official “processing” with fake multi-second delays.

## Success result

### State
`READY IN THIS SIMULATION`

### Copy
`The blocking rule now passes, and this demo found no new conflict for the selected goal.`

### Proof
`Changed: DL name representation`  
`Resolved: DigiLocker/DL reconciliation blocker`  
`Still different: EPFO display name — not relevant to this selected goal`

This “still different but not relevant” line demonstrates causal thinking.

---

# 13. Official next-action screen

## H1
`What you would do next`

A short ordered list, each step with verb-first copy.

Example structure:

1. `Open the official service for the record that needs correction.`
2. `Use the source-backed update route shown below.`
3. `After the official record changes, retry the target service.`

Include requirements/documents only if directly sourced for that scenario.

## Safety footer

`Processes and document requirements can change. Verify the linked official service before acting.`

## CTAs

- `Open official service` (external)
- `See why this route was chosen`
- `Reset demo`

No PDF download as the primary outcome. A shareable summary is P1.

---

# 14. EPFO scenario special UX

The signature moment is a **false lead crossed out by evidence**.

## Finding stack

### Finding 1
`Name looks different`  
Status: `Not the blocker in this simulation`

### Finding 2
`Date of exit is inconsistent with this demo service-history rule`  
Status: `Blocks the target`

Primary explanation:

> `Fixing the visible name difference would not make this fictional claim ready. The service-history condition is the causal blocker.`

This is a product-thinking proof. Do not dilute it with five additional findings.

---

# 15. Life-event scenario special UX

Use a **sequence**, not a spaghetti graph.

## Timeline/plan

`Now` → `Update A` → `Recheck B` → `Update C only if target requires it`

For each step show:

- why now;
- what becomes unblocked;
- what stays unchanged;
- whether official confirmation is needed.

The system must not imply that marriage or another life event requires a person to change name. The scenario is explicitly for a citizen who **has chosen / legally completed** a change and now wants records reconciled.

---

# 16. Hindi content guidance

Hindi should be simple and functional, not bureaucratic Sanskrit-heavy translation.

Examples:

| English | Simple Hindi |
|---|---|
| What are you trying to do? | आप क्या करना चाहते हैं? |
| This is blocking the task | इसी वजह से यह काम रुक रहा है |
| Different, but not the blocker | जानकारी अलग दिखती है, लेकिन इस काम को नहीं रोक रही |
| Show the evidence | वजह और रिकॉर्ड देखें |
| Compare ways to fix this | सुधार के विकल्प देखें |
| Simulate this correction | इस सुधार को डेमो में आज़माएँ |
| No government record will be changed | किसी सरकारी रिकॉर्ड में बदलाव नहीं होगा |
| Ready in this simulation | इस डेमो में अब प्रक्रिया तैयार है |
| What to do next | अब आगे क्या करें |

Agency/legal terminology that citizens recognize may remain in English alongside Hindi, e.g. `PAN`, `Aadhaar`, `UAN`, `Driving Licence`.

Do not transliterate every English UX word into Devanagari if a clearer Hindi phrase exists.

---

# 17. Form and input rules

P0 has almost no free-form sensitive input.

If any input exists:

- label above field, not placeholder-only;
- clear example marked fictional;
- validation on blur/submit, not every keystroke where distracting;
- retain user-entered synthetic value after errors;
- error text adjacent + programmatic association;
- never auto-format into a valid government ID.

---

# 18. Loading, empty and failure states

## Scenario loading
Because fixtures are local/small, use skeleton only if actual delay exists. Do not fake 3-second “AI analysis.”

## Rule unknown

**We can’t confirm this step from the rules in this prototype.**  
`The available evidence is incomplete, so we won’t guess. You can still see the records and the official source.`

## AI unavailable

**The AI explanation is unavailable.**  
`Your diagnosis is unchanged because it was calculated from the demo rules.`

## Source link unavailable

`The official link could not be opened from this device. The source title is shown below so you can find it independently.`

---

# 19. Responsive behavior

## 320–479 px

- single column;
- full-width primary actions;
- record compare stacks;
- dependency graph replaced/defaulted to trail;
- sticky bottom CTA allowed if it does not obscure content;
- no horizontal table.

## 480–767 px

- single column with larger cards;
- optional compact two-card comparisons only if each remains readable.

## 768–1199 px

- two-column comparison regions;
- side evidence drawer.

## 1200+ px

- max content width; do not stretch text across screen;
- graph/options can use extra horizontal room.

---

# 20. Accessibility interaction details

- Skip link target `main`.
- Route changes update document title and move/announce H1 appropriately.
- Dialogs use native/accessible semantics and escape-close where safe.
- Focus order follows DOM order; never reorder with CSS in a way that confuses keyboard users.
- Status icon has hidden text or combined accessible label.
- Diff spans must expose a plain-language summary such as `Record A includes RAMESH; Record B uses initial R`.
- SVG nodes/edges are `aria-hidden` if the full text trail immediately represents them; avoid duplicate verbose screen-reader content.
- `aria-live="polite"` for readiness recomputation; `assertive` only for critical blocking validation.
- Tooltips cannot contain exclusive information.
- Target size and spacing are tested on touch.

---

# 21. Content review checklist

Every screen must pass:

- Can a citizen understand it without knowing what a “canonical identity graph” is?
- Does the first sentence communicate outcome rather than implementation?
- Is any claim stronger than the evidence?
- Are we blaming a citizen or agency without proof?
- Is any text implying the prototype changed an official record?
- Is Hindi natural enough for a human reviewer?
- Would the flow work if the graph were removed?
- Would the flow work if AI were removed?
- Is the next action visible?

---

# 22. Suggested component inventory

Keep the UI kit intentionally small:

- `PrototypeDisclosure`
- `LanguageSwitcher`
- `ScenarioCard`
- `DemoProfileCard`
- `ReadinessBanner`
- `FindingCard`
- `RecordValueCard`
- `DiffSummary`
- `EvidenceDrawer`
- `DependencyTrail`
- `DependencyGraph`
- `CorrectionOptionCard`
- `ImpactList`
- `SimulationConfirmDialog`
- `BeforeAfterPanel`
- `NextActionSteps`
- `OfficialLink`
- `SourceBadge`
- `UncertaintyCallout`
- `ResetCaseButton`

Avoid building a generic 80-component enterprise design system before the three flows are complete.

<!-- END 03_UX_UI_DESIGN_SYSTEM.md -->

---

<!-- BEGIN 04_CITIZEN_SCENARIOS_RULEBOOK.md -->
# 04 — Citizen Scenarios & Deterministic Rulebook

## Purpose

This document defines the synthetic profiles, rule semantics and correction planner behavior that make Identity Rescue credible. It is not a representation of undocumented government matching algorithms. Where a current official source establishes a dependency or correction requirement, the rule is marked `OFFICIAL_SOURCE_DERIVED`. Where the prototype must choose concrete simulation semantics beyond the public source, that portion is marked `PROTOTYPE_SIMULATION`.

---

# 1. Rule-authoring principles

1. **A difference is not a blocker until a service rule says it matters.**
2. **A string similarity score is evidence, not identity.**
3. **Never normalize away information silently.**
4. **Never infer an initial expansion unless the fixture explicitly provides it.**
5. **Never assume token order means first/middle/last across Indian names.**
6. **Never treat Hindi/Latin transliteration as authoritative equivalence.**
7. **Never invent a correction document or official route to make the demo complete.**
8. **If public guidance is broad, make the simulated detail explicit.**
9. **Rules are goal-specific.** A record can be compatible for one service and problematic for another.
10. **Unknown is a valid result.**

---

# 2. Evidence status taxonomy

## OFFICIAL_SOURCE_DERIVED
The public official source directly supports the citizen-facing dependency or action.

Example: DigiLocker FAQ states that the Aadhaar name should match the name in DL/RC database for retrieval.

## OFFICIAL_SOURCE_INTERPRETED
The official source supports the principle but the prototype translates it into a simplified deterministic predicate for demonstration.

## PROTOTYPE_SIMULATION
No claim is made that this exact predicate or path is the authority's production logic. It exists to demonstrate a safer UX/system concept.

## NEEDS_AUTHORITY_VALIDATION
Useful post-hackathon concept not safe to present as current fact.

P0 blockers should prefer the first two statuses and must disclose any simulated part.

---

# 3. Canonical synthetic data model

## 3.1 `SyntheticProfile`

```json
{
  "profile_id": "DEMO-ANANYA-01",
  "display_name": "Ananya R. Krishnan",
  "fictional": true,
  "preferred_locale": "en-IN",
  "known_name_relations": [],
  "records": [],
  "allowed_actions": [],
  "golden_expectations": {}
}
```

## 3.2 `SyntheticRecord`

```json
{
  "record_id": "REC-AADHAAR-ANANYA",
  "authority": "AADHAAR_DEMO",
  "label": "Aadhaar demo record",
  "fields": {
    "name": {
      "original": "ANANYA R KRISHNAN",
      "script": "Latn",
      "locale": "en-IN"
    },
    "dob": { "original": "1998-02-14" }
  },
  "fixture_version": "1.0"
}
```

Use obvious demo labels and identifiers. Do not create realistic Aadhaar/PAN/UAN numbers.

---

# 4. Name comparison model

## 4.1 Derived representations

For comparison only, the engine may derive:

- Unicode-normalized form;
- case-folded form;
- whitespace-collapsed form;
- punctuation-separated tokens;
- honorific-stripped form when source/rule permits;
- token multiset/order;
- initial tokens;
- controlled expansion mapping;
- controlled transliteration mapping.

The UI always retains the original value.

## 4.2 Example classification

Given:

`A: ANANYA R KRISHNAN`  
`B: ANANYA RAMESH KRISHNAN`

The engine must **not** automatically assert equivalence. It can classify:

- if fixture says `R -> RAMESH`: `MATCH_RULE_COMPATIBLE` only if selected rule permits initial/full-name relation;
- if no expansion metadata: `MISMATCH_REVIEW`;
- if rule requires literal reconciliation: `MISMATCH_BLOCKING`.

## 4.3 Indian-specific structures to cover in tests

- `V VIJAYAN` ↔ `VENKATRAMAN VIJAYAN`;
- `R K SRIVASTAVA` ↔ `RAMESH KUMAR SRIVASTAVA`;
- no surname at all;
- two-word surname such as `ROY CHOUDHARY`;
- patronymic/father-name initial before given name;
- family name first vs last;
- punctuation/no punctuation in initials;
- repeated whitespace;
- honorific mistakenly present;
- Latin/local-script pair with controlled transliteration;
- a genuinely different token that should not be normalized away.

These are test categories, not claims that one normalization rule is valid for every service.

---

# 5. Golden Profile A — Ananya R. Krishnan

## 5.1 Citizen goal

`DIGILOCKER_FETCH_DL`

## 5.2 Narrative

Ananya tries to fetch a Driving Licence in DigiLocker and sees a generic issuer-data mismatch. The prototype demonstrates that the Aadhaar-linked name representation and DL source representation do not reconcile under the **simulated retrieval predicate derived from DigiLocker’s public requirement that names match**.

## 5.3 Synthetic records

### Aadhaar demo

- Name: `ANANYA R KRISHNAN`
- DOB: `1998-02-14`
- Address locality: `CHENNAI`

### DL source demo

- Name: `KRISHNAN ANANYA RAMESH`
- DOB: `1998-02-14`
- Record present in mock National Register: `true`

### PAN demo — secondary downstream record

- Name: `ANANYA RAMESH KRISHNAN`
- DOB: `1998-02-14`

## 5.4 Known synthetic relation

For this fictional profile only:

`R` is a documented initial corresponding to `RAMESH`.

This relation may support explanation/planning. It does not prove that all real records using `R` belong to the same person.

## 5.5 Rules

### RULE DL-001 — issuer record must exist

**Evidence status:** OFFICIAL_SOURCE_DERIVED  
**Public basis:** DigiLocker explains that DL/RC retrieval depends on the record existing in the National Register.

Predicate:

`DL.record_present == true`

Pass: continue.  
Fail: `NON_IDENTITY_BLOCKER` with `record not available in modeled issuer source`.

### RULE DL-002 — name reconciliation required

**Evidence status:** OFFICIAL_SOURCE_INTERPRETED  
**Public basis:** DigiLocker says the Aadhaar name should match the DL/RC database name for retrieval.

Prototype predicate for this scenario:

- exact normalized token sequence: pass;
- controlled initial expansion with same semantic token order after rule-specific canonicalization: pass;
- family-name-first reordering **is not automatically accepted in this mock rule** unless the correction action aligns the issuer display representation;
- otherwise block.

Initial state: `MISMATCH_BLOCKING`.

### RULE DL-003 — DOB

**Evidence status:** PROTOTYPE_SIMULATION  
Predicate: exact ISO date equality for demo.

Initial state: pass.

## 5.6 Findings at start

1. Record existence: exact/pass.
2. DOB: exact/pass.
3. Name: blocking because token representation/order does not pass the configured retrieval rule.

Overall: `BLOCKED`.

## 5.7 Correction actions

### ACT-A1 — simulate aligning DL source representation

From: `KRISHNAN ANANYA RAMESH`  
To: `ANANYA RAMESH KRISHNAN`

- Effort class: `ISSUER / OFFICIAL RECORD CORRECTION`
- Reversible in demo: yes
- Evidence status: `PROTOTYPE_SIMULATION` for exact action mechanics
- Downstream modeled effect: PAN remains compatible; DigiLocker/DL rule passes.
- Planner cost: low-to-medium.

### ACT-A2 — simulate changing Aadhaar representation

From: `ANANYA R KRISHNAN`  
To: `ANANYA RAMESH KRISHNAN`

- Effort class: `AADHAAR UPDATE / REVIEW`
- Reversible in demo: yes
- Public basis: UIDAI supports demographic name update but actual eligibility/document route depends on circumstances.
- Downstream modeled effect: may create a new mismatch with another fictional record in expanded scenario.
- Planner cost: higher because Aadhaar is upstream and broadly reused.

## 5.8 Recommended plan

For the locked fixture, the planner recommends `ACT-A1` because it resolves the selected target with a single modeled change and introduces no new modeled conflict, whereas `ACT-A2` changes the more broadly reused upstream record.

**Critical disclosure:** This is a prototype recommendation based on modeled dependencies; it is not a universal official instruction to change DL rather than Aadhaar.

## 5.9 Expected final state

After `ACT-A1`:

- DL-001 pass
- DL-002 pass
- DL-003 pass
- readiness: `READY_SIMULATION`

Citizen copy:

> `This fictional case now passes the rules we model for DL retrieval. No government record was changed.`

---

# 6. Golden Profile B — Arvind N. Iyer

## 6.1 Citizen goal

`EPFO_KYC_PREFLIGHT`

## 6.2 Narrative

Arvind sees a visible variation across Aadhaar/PAN/PF name representations and assumes that must be why the PF task fails. The real simulated blocker is a service-history condition. The product proves it can reject an attractive but wrong explanation.

## 6.3 Synthetic records

### Aadhaar demo

- Name: `ARVIND N IYER`
- DOB: `1989-07-11`

### PAN demo

- Name: `ARVIND NARAYAN IYER`
- DOB: `1989-07-11`

### EPFO member demo

- Name: `ARVIND N IYER`
- DOB: `1989-07-11`
- Aadhaar-linked: `true`
- PAN-linked: `true`
- Date of exit: `2026-08-31`
- Last contribution month: `2026-07`
- Target claim attempt date: `2026-08-20`

## 6.4 Known synthetic relation

`N -> NARAYAN` for this fictional profile.

## 6.5 Rules

### RULE EPFO-001 — KYC name compatibility

**Evidence status:** OFFICIAL_SOURCE_INTERPRETED  
**Public basis:** EPFO FAQ says name as per Aadhaar/PAN should align appropriately with PF records for KYC.

Prototype predicate:

- exact name or controlled initial expansion relation passes;
- genuine unmatched token causes review/block depending fixture.

Initial state: `MATCH_RULE_COMPATIBLE`.

### RULE EPFO-002 — DOB compatibility

**Evidence status:** OFFICIAL_SOURCE_INTERPRETED  
Initial state: exact pass.

### RULE EPFO-003 — service-history readiness

**Evidence status:** PROTOTYPE_SIMULATION, conceptually informed by EPFO service-history/date-of-exit workflows.  
For this fixture, a future/invalid exit date relative to target attempt prevents the selected simulated readiness condition.

Initial state: `NON_IDENTITY_BLOCKER` / blocking.

## 6.6 Initial findings

- Aadhaar vs PAN name: visibly different but controlled relation → `VARIANT_NON_BLOCKING`.
- PF vs Aadhaar name: exact → pass.
- Service history: blocker.

Overall: `NOT_IDENTITY_ISSUE` or `BLOCKED` with primary cause category `NON_IDENTITY_BLOCKER` depending UI state model.

Recommended citizen wording:

> `The name variation is not what blocks this fictional case. The service-history date is the condition that fails.`

## 6.7 Deliberate anti-error test

If user simulates a name-only alignment action, readiness MUST remain blocked. This test protects the product from “identity mismatch tunnel vision.”

## 6.8 Correct simulation action

`ACT-B1` — set the fictional date-of-exit condition to a valid scenario value.

After action, all modeled conditions pass → `READY_SIMULATION`.

## 6.9 Why this scenario matters

This case is critical to judge trust: the product proves it diagnoses the goal, not merely highlights string differences.

---

# 7. Golden Profile C — Meera Nair

## 7.1 Citizen goal

`LIFE_EVENT_RECONCILIATION`

## 7.2 Narrative

Meera has deliberately completed a legal name change and moved residence. Some fictional records reflect the new details, others still contain the old representation. She wants to know the smallest sequence needed for a selected target service.

The scenario must never imply that marriage or any other life event obligates a person to change name. The user has already chosen/completed the change.

## 7.3 Synthetic records

### Aadhaar demo

- Name: `MEERA NAIR`
- Address: `BENGALURU, KARNATAKA`

### PAN demo

- Name: `MEERA MENON`
- Address field not modeled for selected goal.

### DL demo

- Name: `MEERA MENON`
- Address: `KOCHI, KERALA`

### EPFO demo

- Name: `MEERA NAIR`
- KYC status: `pending review` in fixture

### Supporting synthetic legal-change evidence

- `name_change_evidence_present: true`
- This is a demo metadata flag, not a simulated real gazette number.

## 7.4 Target sub-goal for P0

To keep the demo bounded, P0 selects:

`Make the fictional DL retrieval path consistent with the new chosen name while minimizing other changes.`

## 7.5 Rules

### RULE LIFE-001 — chosen canonical direction

The citizen explicitly declares that `MEERA NAIR` is the desired current legal name in the fictional case. This is user intent, not inferred by the system.

### RULE LIFE-002 — target DL retrieval dependency

Uses the same public-derived DigiLocker/DL reconciliation principle as Scenario A.

### RULE LIFE-003 — planner should not update unrelated address for name-only target

**Evidence status:** PROTOTYPE_PRODUCT_RULE.  
If the selected goal depends only on name, planner should not add an address change merely for global consistency.

This is a key data-minimization/product-thinking rule.

## 7.6 Actions

### ACT-C1 — simulate DL name update to chosen current name

- resolves target name dependency;
- leaves old DL address unchanged because not required for selected target;
- medium effort.

### ACT-C2 — simulate PAN name update

- may be useful for broader reconciliation but not required to satisfy P0 DL target after C1;
- therefore not part of minimum plan.

### ACT-C3 — simulate DL address update

- not required for the P0 goal;
- planner rejects from minimum sequence.

## 7.7 Expected recommendation

Plan: `ACT-C1` only for selected target.

Then final screen says:

> `Your fictional PAN still uses the earlier name and the DL still has the previous address. They are not part of this selected retrieval blocker, so the minimum plan does not change them automatically.`

This explicitly demonstrates **minimum necessary correction**, not “make every database identical.”

---

# 8. Secondary edge fixtures for tests (not primary demo)

## EDGE-01 — No surname

Passport-style name structure where all name content is a given name. Ensure parser does not invent surname.

## EDGE-02 — Multi-token surname

`ANANYA ROY CHOUDHARY` remains intact; no automatic split assumption.

## EDGE-03 — Initial ambiguity

`K S RAVI` has no known expansion metadata. Result must be `REVIEW`, not guessed expansion.

## EDGE-04 — Genuine mismatch

`PRIYA MENON` vs `PRIYA MEHRA`; fuzzy similarity must not mark compatible.

## EDGE-05 — Local script / Latin

Controlled fixture includes `மீரா நாயர்` and `MEERA NAIR` with explicit fixture relation. System may present derived transliteration but labels it.

## EDGE-06 — Transliteration ambiguity

Two plausible Latin transliterations exist. Result = `REVIEW`.

## EDGE-07 — DOB near miss

`1990-08-07` vs `1990-07-08`; never silently interpret locale formatting once canonical dates are parsed from fixtures.

## EDGE-08 — Missing record

No DL record in mock issuer. Diagnose `NON_IDENTITY_BLOCKER`, not name mismatch.

## EDGE-09 — Unknown rule

A new mock agency appears with no rule. Product must say it cannot determine compatibility.

---

# 9. Planner cost model

P0 recommended weights (tunable but versioned):

| Factor | Weight | Meaning |
|---|---:|---|
| Step count | 10 | Penalize unnecessary corrections. |
| Online self-service | 10 | Low effort. |
| Centre/office visit | 30 | Higher citizen effort. |
| Employer/issuer dependency | 35 | External coordination. |
| Uncertain/authority validation needed | 40 | Avoid false certainty. |
| Downstream new blocker | 100 | Strongly avoid. |
| Upstream high-reuse record change | 20 | Prefer narrower changes when equally valid. |
| Irreversible/legally significant action | 100+ | Not recommended without explicit source/validation. |

These weights demonstrate product logic; they are not empirical welfare values.

## 9.1 Planner pseudo-code

```text
input: current synthetic state S, target goal G, allowed actions A
queue <- [S, []]
best <- none

while queue not empty:
  state, plan <- lowest_cost_state(queue)
  evaluation <- evaluate(state, G)

  if evaluation == READY_SIMULATION:
     best <- plan
     break

  for action in allowed_actions(state):
     next <- simulate(state, action)
     if violates_safety_constraint(next): continue
     push(next, plan + action, configured_cost)

return best or NO_PLAN / NEEDS_REVIEW
```

## 9.2 Planner explanation contract

Return structured reasons:

```json
{
  "reason_codes": [
    "RESOLVES_TARGET",
    "ONE_STEP",
    "NO_NEW_MODELED_BLOCKERS",
    "LOWER_UPSTREAM_IMPACT"
  ]
}
```

The UI translates these codes into plain language. AI may improve phrasing but not change reason codes.

---

# 10. Evidence registry requirements

Each source record contains:

- stable source ID;
- title;
- publisher/authority;
- official URL;
- relevant proposition;
- publication/update date if known;
- `last_checked_at`;
- extraction/paraphrase note;
- rules that cite it.

If a source changes materially before submission, affected tests/rules must be reviewed.

---

# 11. Prohibited rule shortcuts

Do not implement any of the following:

- `if similarity > 0.8 => same person`;
- `last token = surname`;
- `first token = first name`;
- `single-letter token => automatically expand from another record`;
- `all dates normalized by guessing DD/MM vs MM/DD`;
- `regional script transliteration => exact identity`;
- `more matching records => majority record is legally correct`;
- `Aadhaar is always the record that should be changed`;
- `Aadhaar is always the record that should never be changed`;
- `AI chooses authoritative record`;
- `all differences should be fixed`.

---

# 12. Citizen-facing confidence model

Avoid numeric confidence unless tied to explicit evidence measurement.

Use:

- **Clear in this demo** — all required rule inputs present and deterministic rule directly fires.
- **Needs official confirmation** — route/process detail not fully supported.
- **Cannot determine** — missing rule/input.

Never use `99% sure this is you`.

<!-- END 04_CITIZEN_SCENARIOS_RULEBOOK.md -->

---

<!-- BEGIN 05_AI_SAFETY_GROUNDING.md -->
# 05 — AI, Grounding & Safety Specification

## Product position

Identity Rescue is not valuable because an LLM can “understand names.” It is valuable because the system has a deterministic, inspectable model of records, service rules and correction consequences. AI improves **language and comprehension** while remaining outside the decision boundary.

This boundary is both a safety requirement and a product differentiator.

---

# 1. Allowed runtime AI capabilities

## AI-01 — Plain-language explanation

Input: deterministic finding packet.  
Output: short citizen explanation with no new facts.

## AI-02 — Simple Hindi explanation

Input: approved English explanation + structured evidence.  
Output: natural simple Hindi preserving IDs/agency names and certainty level.

Prefer reviewed static Hindi for the golden paths. Runtime translation is optional/P1 because demo copy should be stable.

## AI-03 — Synthetic bureaucratic remark parsing (P1)

Input: explicitly synthetic/free-text error message after local redaction.  
Output: candidate structured fields such as error code, mentioned field, service, action verbs.  
The parser does not decide cause; rule engine verifies candidates.

## AI-04 — Narrow “Why?” follow-up (P1)

The user may ask a narrow question such as `Why not change Aadhaar instead?`

The model receives only:

- current plan;
- alternative plan;
- reason codes;
- affected synthetic records;
- source-backed facts.

No open-ended government advice.

---

# 2. Explicitly forbidden AI capabilities

The AI MUST NOT:

1. determine that two real records are the same person;
2. produce biometric/KYC identity assurance;
3. decide actual eligibility for EPFO/tax/passport/etc.;
4. decide which government record is legally authoritative without an explicit sourced rule;
5. fabricate documentation requirements;
6. browse arbitrary web content at runtime to make a citizen decision;
7. call/live-write government systems;
8. generate/alter government IDs or documents;
9. override a deterministic `BLOCKED`, `READY`, `UNKNOWN` or plan result;
10. conceal uncertainty;
11. use user-sensitive production data in the hackathon demo;
12. convert a probabilistic similarity into a legal/identity assertion.

---

# 3. Evidence packet schema

Recommended server-side input:

```json
{
  "request_type": "EXPLAIN_FINDING",
  "locale": "en-IN",
  "prototype_disclosure": true,
  "goal": {
    "code": "DIGILOCKER_FETCH_DL",
    "label": "Fetch a Driving Licence in DigiLocker"
  },
  "readiness": "BLOCKED",
  "finding": {
    "state": "MISMATCH_BLOCKING",
    "rule_id": "DL-002",
    "plain_rule": "This demo requires the Aadhaar-linked name and issuer name to reconcile.",
    "inputs": [
      {"label": "Aadhaar demo name", "value": "ANANYA R KRISHNAN"},
      {"label": "DL demo name", "value": "KRISHNAN ANANYA RAMESH"}
    ]
  },
  "sources": [
    {
      "id": "SRC-DIGILOCKER-FAQ",
      "title": "DigiLocker FAQs",
      "proposition": "DigiLocker says the Aadhaar name should match the DL/RC record for retrieval."
    }
  ],
  "allowed_conclusions": [
    "The two demo records represent the name differently.",
    "The configured retrieval rule treats this as blocking.",
    "The product is a simulation and does not know the authority's full production logic."
  ],
  "forbidden_conclusions": [
    "The real Aadhaar is wrong.",
    "The real DL is wrong.",
    "The user is definitely the same person in both records."
  ]
}
```

Never ask the model to infer missing rule facts.

---

# 4. Output schema

Prefer validated structured output:

```json
{
  "headline": "The name records do not reconcile for this demo retrieval.",
  "explanation": "...",
  "why_it_matters": "...",
  "uncertainty": "The authority may apply additional checks not modeled here.",
  "source_ids": ["SRC-DIGILOCKER-FAQ"]
}
```

Validation rules:

- headline <= 100 chars;
- explanation <= ~55 words;
- no source ID not present in input;
- no URL invented;
- uncertainty mandatory when evidence status is not fully official-derived;
- no HTML from model;
- no imperative legal claims such as `You must legally...` unless an approved exact rule supports them.

---

# 5. System prompt for runtime explanation

Suggested internal prompt:

> You are the explanation layer for an independent Indian public-service hackathon prototype. You do not decide identity, eligibility, legality, or correction routes. The deterministic engine has already produced the finding and evidence. Explain only the supplied facts in plain language. Never add a requirement, document, deadline, fee, API capability, agency process or conclusion not present in the evidence packet. Preserve uncertainty. Never imply that the prototype contacted or updated a government system. If the evidence is insufficient, say so. Return only the requested structured schema.

This prompt is not a substitute for output validation.

---

# 6. Grounding enforcement

## 6.1 Source whitelist

Runtime explanation may cite only `source_ids` already attached to the rule/finding. The model cannot introduce new sources.

## 6.2 Claim checker

Before rendering, validate:

- every source ID exists;
- readiness/finding state exactly matches deterministic engine;
- action recommendation IDs match planner output;
- prohibited phrases/unsupported factual categories are absent where feasible;
- schema passes.

If validation fails → template fallback.

## 6.3 Template fallback

Every P0 finding must have a static copy key such as:

`finding.DL_002.blocking.en`  
`finding.DL_002.blocking.hi`

Therefore zero AI availability still produces a complete demo.

---

# 7. P0 recommendation: use AI sparingly

For submission stability, the strongest P0 runtime use is **one visible AI-assisted explanation** after the deterministic result, with a `Show evidence` affordance.

Do not add multiple agents. Do not claim “13 AI agents.” Do not add a vector database unless a real P0 requirement demands it.

Codex can be meaningfully documented as part of the build process independently of runtime AI, as the official hackathon permits a prototype built with Codex or powered by an OpenAI model and requires Codex meaningful involvement in the build.

---

# 8. AI failure modes and UI behavior

## Timeout

- Stop waiting after configured timeout.
- Render static explanation.
- Optional small notice: `AI wording unavailable; rule-based result shown.`

## Invalid schema

- Do not attempt to render partially trusted prose.
- Use template.

## Grounding mismatch

Example: model says “update Aadhaar” when planner recommended DL route.  
Action: reject output, log `AI_GROUNDING_FAILED`, render template.

## Safety/refusal

If model refuses even though synthetic packet is safe, render template without exposing internal error details.

---

# 9. AI evaluation suite

Create at least 30 explanation cases across:

- exact match;
- initial expansion;
- token order mismatch;
- genuine mismatch;
- transliteration review;
- non-identity blocker;
- missing evidence;
- two equivalent plans;
- no viable plan;
- English/Hindi;
- attempts to inject unsupported facts through synthetic error text.

Evaluate:

1. factual consistency with packet;
2. no new government requirements;
3. certainty calibration;
4. no government-write implication;
5. readability;
6. locale quality;
7. source ID integrity.

A simple deterministic grader plus manual golden review is preferable to a complex LLM-evaluates-LLM system for this deadline.

---

# 10. Prompt injection / untrusted text

If P1 allows synthetic pasted rejection remarks:

- treat text purely as data;
- delimit it clearly;
- instruct model to ignore instructions inside;
- redact ID-like patterns locally;
- constrain output schema;
- do not allow text to alter tool permissions, source set or system prompt;
- never send repository secrets/config.

---

# 11. Privacy boundary

AI requests contain synthetic data only in the hackathon build. Do not send analytics/session identifiers that could identify a real user. Do not persist prompts/responses unless necessary for local development; production logging should use trace/status metadata.

---

# 12. Demonstrating OpenAI use without AI theatre

In minute two of the submission:

- show deterministic rule trace;
- state that Codex was used to build/refactor/test the vertical slices;
- show the bounded explanation schema or one code view;
- explain that AI translates evidence while rules retain decision authority;
- demonstrate AI-off fallback if time permits in README rather than consuming demo minute.

The message to judges should be: **AI is used where language is uncertain; deterministic software is used where public-service consequences need certainty.**

<!-- END 05_AI_SAFETY_GROUNDING.md -->

---

<!-- BEGIN 06_DATA_PRIVACY_SECURITY.md -->
# 06 — Data, Privacy, Security & Trust Requirements

## Scope

Identity Rescue is a hackathon prototype involving identity-like data. That makes **trust design** more important, not less, even though all P0 records are fictional.

The strongest security posture is not “we encrypted everything.” It is **we never ask for the dangerous data in the first place**.

---

# 1. Data policy

## 1.1 P0 data inventory

Allowed:

- fictional profile IDs;
- fictional names/DOBs/addresses crafted for scenarios;
- non-valid demo authority identifiers;
- rule/source metadata;
- simulation action IDs;
- anonymous technical telemetry.

Not allowed:

- real Aadhaar numbers;
- real PAN;
- real UAN/member IDs;
- OTPs;
- bank/payment details;
- passwords;
- biometric data;
- real scanned documents;
- health information;
- real grievance text containing personal identifiers;
- user-uploaded identity documents.

## 1.2 UI enforcement

P0 should offer **profile selection**, not real identity-data entry.

Do not show a realistic input labelled `Enter your Aadhaar number` even if the backend never transmits it. That trains the judge/user to trust the prototype with data the brief explicitly forbids.

---

# 2. Data classification

| Class | Example | Storage |
|---|---|---|
| PUBLIC | source titles, product copy | bundled/repository |
| SYNTHETIC-DEMO | fictional records | fixture store / local DB |
| INTERNAL-CONFIG | rule weights, feature flags | config/repo |
| SECRET | OpenAI/API credentials | environment/secret manager only |
| REAL-SENSITIVE | real IDs/OTPs/biometrics | **prohibited in P0** |

---

# 3. Privacy-by-design requirements

## PRIV-001 — Data minimization
Only load/display fields needed for the selected goal.

## PRIV-002 — Purpose visibility
The citizen should understand why each displayed field is relevant through `Why are we checking this?` or equivalent evidence UI.

## PRIV-003 — No secondary use
No synthetic/person-like data is used for advertising, profiling or unrelated analytics.

## PRIV-004 — Session clear
`Reset demo` clears mutations. If localStorage/sessionStorage is used, expose `Clear this device` and avoid indefinite stale cases.

## PRIV-005 — No hidden tracking dependency
The app must remain functional with analytics blocked.

## PRIV-006 — AI data minimization
Send only the evidence packet necessary for explanation, never entire synthetic profile if only two fields are needed.

## PRIV-007 — Human-readable privacy notice
A one-page notice explains:

- prototype status;
- fictional-data design;
- what technical telemetry is collected, if any;
- AI usage;
- external links;
- how to clear local state.

---

# 4. DPDP positioning

The Digital Personal Data Protection Rules, 2025 were notified with phased commencement. As of this package date, not every substantive rule is simultaneously in force. Therefore the product must **not** market itself as “DPDP certified/compliant” without legal review.

Correct positioning:

> `The prototype follows privacy-by-design principles such as data minimization, clear purpose, synthetic data and limited logging, and is designed with India's DPDP framework in mind.`

Avoid:

> `100% DPDP compliant.`

For a production deployment, legal counsel and the relevant authority would need to assess data-fiduciary roles, notice/consent, security safeguards, retention, rights handling, children’s data if applicable, breach response and any government-specific exemptions/obligations.

---

# 5. Threat model

## 5.1 Assets

- integrity of rule results;
- trust/provenance metadata;
- API secrets;
- deployment availability;
- source code;
- user confidence that simulation is not real government action.

## 5.2 Threat actors

- casual internet abuse/bots;
- malicious user attempting to inject instructions into AI text;
- attacker seeking exposed API credentials;
- accidental developer leakage;
- misleading UI that causes user to believe a real update occurred;
- stale/incorrect rule content (integrity threat rather than hacker).

## 5.3 STRIDE-style summary

### Spoofing
Risk: site appears official or external link spoofing.  
Controls: independent-prototype label, verified official URLs in local registry, no government branding impersonation.

### Tampering
Risk: rule/fixture changed without tests.  
Controls: version control, golden tests, optional rule hash/version display in debug mode.

### Repudiation
Risk: hard to reproduce simulation result.  
Controls: non-sensitive event journal with fixture/rule versions.

### Information disclosure
Risk: secrets or pasted personal data.  
Controls: no real inputs; server-side secrets; redaction if P1 text input exists; sanitized logs.

### Denial of service
Risk: public AI endpoint abuse.  
Controls: rate limit, timeout, circuit breaker/fallback, core works without AI.

### Elevation of privilege
P0 has no meaningful privileged citizen roles. Avoid adding admin auth unless necessary for development; do not ship hidden mutable policy UI publicly.

---

# 6. Web application controls

## SEC-WEB-001
Production must use HTTPS.

## SEC-WEB-002
Use framework/host security headers. Strong baseline where compatible:

- Content-Security-Policy;
- Strict-Transport-Security;
- X-Content-Type-Options;
- Referrer-Policy;
- frame-ancestors / equivalent clickjacking protection;
- Permissions-Policy as appropriate.

## SEC-WEB-003
Never interpolate model/user text as raw HTML. Render escaped text or sanitized allowed markup.

## SEC-WEB-004
No secrets in client bundles or source maps.

## SEC-WEB-005
Pin/lock dependencies and scan for reachable critical/high vulnerabilities before submission.

## SEC-WEB-006
External official links use an allowlisted source registry rather than arbitrary model-generated URL.

## SEC-WEB-007
If a server endpoint accepts scenario/action IDs, validate against allowlisted fixtures/actions. Do not trust arbitrary mutation payloads.

---

# 7. AI endpoint security

- server-side credential;
- request body size limits;
- schema validation;
- allowlisted request types;
- synthetic-data assertion;
- rate limit by IP/session as reasonable;
- timeout and max-output limit;
- no tool permissions to call government websites;
- no arbitrary URL fetch tool;
- no prompt/response logs with content in production unless explicitly needed and safe.

---

# 8. Real-data guardrails

P0 strongest control: **there is nowhere to enter it.**

If P1 free text is added:

1. Place inline warning before the input: `Use the fictional sample only. Do not paste real IDs or personal details.`
2. Client-side pattern scan for likely Aadhaar/PAN/UAN/phone/bank-like data.
3. If matched, block submission and offer to load a sample remark.
4. Do not attempt to “mask and continue” automatically for highly sensitive patterns unless thoroughly tested; safest demo behavior is refusal.
5. Server repeats validation because client controls can be bypassed.

---

# 9. Source integrity / policy staleness

A wrong rule can be more harmful than a code bug.

Every source-backed rule includes:

- source ID;
- official publisher;
- URL;
- last checked date;
- proposition used;
- evidence status;
- rule version.

Before recording/submission:

- click every official link;
- verify wording/process has not materially changed;
- if it changed, update rule/test/copy together;
- never silently keep a stale correction recommendation.

---

# 10. Accessibility as trust/security

Accessibility failures can cause citizens to misread a blocker or action. Treat these as correctness issues:

- status must not be color-only;
- focus must not jump during simulation;
- external link must be announced;
- dialog confirmation must state `simulation only`;
- screen-reader text must distinguish original vs derived/transliterated values;
- errors must not disappear before they can be read.

---

# 11. Logging policy

## Production log allowlist

Allowed examples:

```text
scenario_started {scenario_id}
analysis_completed {scenario_id, rule_version, readiness}
simulation_applied {scenario_id, action_id}
ai_explanation_status {success|timeout|schema_fail|grounding_fail}
client_error {error_code, route, build_sha}
```

Not allowed:

- full synthetic name strings unless strictly local debug;
- free-form rejection text;
- secrets;
- real user identifiers;
- browser storage dumps.

Even synthetic person data should not become a lazy logging habit.

---

# 12. Authentication and authorization

P0 citizen experience SHOULD NOT require login.

If existing app architecture forces a login, replace with obvious mock persona access or bypass for reviewer routes. The official brief allows mock consumer credentials but reviewer friction should be minimized.

Do not build Entra/OAuth/government SSO for this prototype merely to show security sophistication.

---

# 13. Persistence choice

SQLite/local persistence is sufficient for:

- source/rule registry;
- fixtures;
- event journal;
- deterministic replay.

A transactional outbox/event broker is not required because P0 has no distributed production write workflow. If an existing outbox is already stable, it may remain internal; do not spend pivot time integrating Kafka.

---

# 14. Trust disclosures — exact minimum copy

## Global

`Independent hackathon prototype · Fictional data · Does not connect to government systems`

## Simulation

`This changes only the fictional case in this demo. No official record will be updated.`

## Final action

`Processes can change. Check the linked official service before acting.`

## AI

`AI may help explain the result. The blocker and correction simulation are calculated from deterministic demo rules.`

---

# 15. Security release gate

Before submission:

- [ ] no real-sensitive input path;
- [ ] no exposed API keys;
- [ ] no live government API call;
- [ ] official external URLs verified;
- [ ] CSP/headers reviewed;
- [ ] dependency security scan reviewed;
- [ ] AI endpoint rate/size/time limits configured;
- [ ] production logs inspected for content leakage;
- [ ] reset clears local scenario state;
- [ ] prototype disclosure visible on every relevant route;
- [ ] simulation language cannot reasonably be mistaken for a real government update.

<!-- END 06_DATA_PRIVACY_SECURITY.md -->

---

<!-- BEGIN 07_TESTING_ACCEPTANCE.md -->
# 07 — Testing, Acceptance & Quality Gates

## Objective

The previous system accumulated hundreds of tests around the wrong citizen outcome. Identity Rescue needs fewer tests with higher product leverage. Test the **invariants that make the concept trustworthy**: causality, conservative matching, correction consequences, accessibility, synthetic-data boundaries and end-to-end completion.

A large test count is not a success metric.

---

# 1. Test strategy

## Layer A — domain unit tests

Highest volume. Pure, deterministic, fast.

Test:

- normalization;
- name token handling;
- controlled initial expansion;
- transliteration-review behavior;
- rule evaluation;
- readiness precedence;
- planner cost/constraints;
- simulation recomputation;
- source/provenance resolution.

## Layer B — contract/integration tests

Test:

- fixture ↔ adapter contract;
- rule registry ↔ source registry;
- backend/API ↔ UI DTOs if server exists;
- AI schema/fallback boundary;
- locale completeness.

## Layer C — component/accessibility tests

Test:

- semantic status;
- focus behavior;
- dialog/drawer behavior;
- diff accessibility;
- language switch;
- error messaging.

## Layer D — golden E2E tests

At minimum one complete test per locked scenario on desktop + mobile viewport.

## Layer E — manual/reviewer tests

Screen reader, keyboard, slow network, visual comprehension, Hindi copy, deployed links, two-minute recording run.

---

# 2. Recommended test budget

Do not optimize for an arbitrary number. A likely healthy P0 distribution is approximately:

- 50–80 domain unit/property tests;
- 15–25 integration/contract tests;
- 15–25 component/accessibility tests;
- 6–12 E2E tests;
- manual quality gates.

Roughly 90–140 high-value tests may be enough. If the retained infrastructure brings more tests at near-zero maintenance cost, keep them, but do not rewrite hundreds of vehicle-domain tests.

---

# 3. Domain test matrix

## 3.1 Normalization

### T-NAME-001
`ANANYA  R   KRISHNAN` normalizes whitespace but original is preserved.

### T-NAME-002
Punctuation in `R.` may be normalized for configured comparison without rewriting original.

### T-NAME-003
`R` does not expand to `RAMESH` without profile relation.

### T-NAME-004
With explicit `R -> RAMESH`, comparator can expose relation.

### T-NAME-005
Token reorder does not globally pass unless the selected rule permits it.

### T-NAME-006
No-surname fixture remains valid and does not synthesize a family name.

### T-NAME-007
Multi-token surname remains represented without destructive splitting.

### T-NAME-008
`PRIYA MENON` vs `PRIYA MEHRA` must not pass due to fuzzy similarity.

### T-NAME-009
Controlled local-script ↔ Latin pair produces at most configured compatible/review state.

### T-NAME-010
Uncontrolled transliteration produces `REVIEW`, not exact identity.

## 3.2 Dates

- ISO-equivalent exact values pass.
- ambiguous string formats are never guessed after parse failure.
- date inversion near-miss fails/reviews.
- missing mandatory date → `MISSING_REQUIRED`.

## 3.3 Rule engine

For each rule:

- pass fixture;
- fail fixture;
- missing input;
- source exists;
- version exists;
- citizen explanation key exists;
- unknown does not become ready.

## 3.4 Readiness

- blocking finding wins over passes;
- mandatory unknown → needs review;
- no identity blocker + causal non-identity blocker does not become `READY`;
- all mandatory passes → `READY_SIMULATION`;
- unrelated non-blocking finding does not prevent ready.

## 3.5 Planner

- minimum known route selected for Scenario A;
- upstream broader-impact alternative costs more when configured;
- Scenario B name-only action does not resolve target;
- Scenario C planner excludes address change for name-only target;
- action causing new modeled blocker is rejected/penalized;
- equal-cost plans surface ambiguity;
- no viable plan returns `NO_PLAN/NEEDS_REVIEW`, not fabricated route.

---

# 4. Golden E2E acceptance cases

## E2E-GJ01 — DL mismatch, desktop

**Given** clean browser, 1280px viewport  
**When** reviewer selects `I can't fetch my Driving Licence`  
**Then** fictional-data disclosure appears  
**And** initial analysis is `BLOCKED`  
**And** exact name values are visible  
**And** evidence drawer cites DigiLocker source  
**When** reviewer opens correction comparison  
**Then** recommended simulation explains modeled impact  
**When** reviewer confirms simulation  
**Then** state becomes `READY IN THIS SIMULATION`  
**And** before/after is visible  
**And** official next-action link appears  
**And** UI states no real record changed.

## E2E-GJ01-M — same at 360x800

No horizontal overflow for normal content; graph defaults to dependency trail.

## E2E-GJ02 — EPFO causal disambiguation

**Given** Arvind fixture  
**Then** the name variation is shown but marked non-blocking  
**And** service-history condition is primary blocker  
**When** a name-only simulated action is attempted (through test/debug path or alternative card)  
**Then** readiness remains blocked  
**When** causal action is simulated  
**Then** readiness updates correctly.

## E2E-GJ03 — life-event sequence

**Given** Meera fixture  
**Then** planner recommends only the required target correction  
**And** unrelated address change is not included  
**When** plan simulated  
**Then** target becomes ready  
**And** remaining old values are transparently listed as non-blocking for selected goal.

## E2E-AI-OFF

Disable/mock AI endpoint failure. All three golden journeys complete with template explanations.

## E2E-HI

Switch to Hindi before entering a case. Complete one full flow; no missing keys/English-only safety states except stable agency/product names intentionally preserved.

---

# 5. Accessibility acceptance

## Automated

Use axe or equivalent on each primary state. Zero critical/serious violations accepted without documented false-positive rationale.

## Keyboard

For each golden flow:

- skip link works;
- all controls reachable;
- visible focus always present;
- no keyboard trap;
- drawer/dialog opens/closes and returns focus;
- simulation can be completed;
- external official link reachable;
- reset reachable.

## Screen reader smoke test

At least NVDA + Chromium/Firefox on Windows if available.

Verify:

- page title/H1;
- prototype disclosure;
- scenario cards;
- readiness change;
- record comparison summary;
- mismatch state is clear without color;
- dependency trail;
- evidence drawer;
- confirmation dialog;
- final next-action steps.

## Reflow/zoom

- 320 CSS px equivalent;
- 200% zoom;
- no lost action/content;
- no horizontal scroll except explicitly exempt 2D visual that has text alternative.

## Contrast

Check all normal text, status badges, focus rings, disabled controls and charts. Do not validate only primary buttons.

## Reduced motion

With OS/browser reduced motion enabled, simulation and graph transitions should not animate materially.

---

# 6. Localization acceptance

- no raw i18n keys in production;
- no clipped Hindi buttons;
- 30–60% copy expansion tolerance;
- line breaks do not separate critical labels from values;
- `lang` attribute updates;
- screen reader pronounces Hindi content under Hindi language context;
- names/source values remain unchanged unless explicitly showing derived transliteration;
- Hindi microcopy manually reviewed for the golden path.

---

# 7. Low-network/performance acceptance

Use browser throttling / Lighthouse-like lab profile.

Target:

- LCP <= 2.5 s where hosting allows;
- no giant background images/videos;
- no blocking AI call before diagnosis;
- lazy-load non-critical source/graph modules;
- deterministic fixture analysis immediate after app data available;
- on AI timeout, fallback appears <= configured timeout and flow continues;
- retry does not duplicate simulation actions.

If targets cannot be met due to host variance, report actual numbers honestly and fix major bundle bottlenecks.

---

# 8. Security acceptance

- inspect built JS for secrets;
- run secret scan;
- run dependency vulnerability scan;
- verify no live government host used as an API endpoint;
- verify external URLs originate only from source registry;
- attempt arbitrary action ID mutation → rejected;
- attempt XSS-like synthetic text → rendered inert;
- AI endpoint rejects oversize/invalid request type;
- production logs inspected for names/free text/secrets;
- reset clears local mutations.

---

# 9. Source/provenance acceptance

Before final recording, manually click/verify every P0 official source.

For each P0 rule confirm:

- official source still exists;
- current page still supports proposition;
- source publisher is correct;
- `last_checked_at` = current verification date;
- citizen copy does not strengthen the source beyond support;
- any simulated predicate is labeled as such.

---

# 10. Visual/UI acceptance

Ask five questions on every screen:

1. What is the primary action?
2. What is the current status?
3. What is the evidence?
4. What happens next?
5. Is anything decorative competing with those answers?

Reject screen if:

- more than one primary CTA competes;
- five+ status cards appear before the cause;
- graph dominates mobile viewport;
- copy uses internal jargon;
- the user must interpret a numerical score;
- prototype disclosure is hidden;
- source/uncertainty is inaccessible;
- success implies real government update.

---

# 11. Demo-readiness gate

Run the following from an incognito browser on the deployed URL:

1. Open URL.
2. Understand problem without narration.
3. Start Scenario A in one click.
4. Reach diagnosis.
5. Show evidence.
6. Compare corrections.
7. Simulate.
8. Reach next action.
9. Reset.
10. Switch Hindi.
11. Open Scenario B and show “name is not blocker.”
12. Disable AI/network endpoint and confirm core still works.

If any manual recovery/devtools intervention is required, it is not ready.

---

# 12. Submission stop-ship defects

- core scenario broken;
- any demo feature is fake/nonfunctional;
- live government API interaction;
- real sensitive data required;
- AI determines readiness;
- source-backed claim is materially wrong/stale;
- mobile flow unusable;
- keyboard cannot finish flow;
- deployed link requires permission;
- demo implies official partnership;
- external official link is broken/misdirected;
- video exceeds 2 minutes;
- project summary exceeds 250 words;
- missing clear mock/limitations disclosure.

<!-- END 07_TESTING_ACCEPTANCE.md -->

---

<!-- BEGIN 08_DEMO_SUBMISSION.md -->
# 08 — Demo, Storytelling & Submission Package

## Official constraints used

Checked against the Build What Moves India Builder Brief/FAQ on 22 August 2026:

- submission deadline: **28 August 2026, 8:00 PM IST**;
- live public browser link;
- one video, **no longer than two minutes**;
- first minute: citizen demo;
- second minute: how it was built and why choices were made;
- project summary under 250 words;
- use synthetic/mock data for sensitive/government dependencies;
- Codex must be meaningfully involved;
- reviewers test citizen experience, not an admin panel.

Recheck the official site immediately before submission in case rules change.

---

# 1. Reviewer landing strategy

The deployed root URL should be the product, not a developer README or login wall.

Above fold:

> **Every portal tells you what failed. See what to fix first.**

Then 3 fictional case cards.

Recommended small reviewer cue:

`For the 60-second demo, start with “I can’t fetch my Driving Licence.”`

Do not force it if that feels artificial; the first card can naturally be the preferred path.

---

# 2. Two-minute video script — timing blueprint

Do not memorize every word. Memorize the transitions and citizen outcome.

## 0:00–0:10 — premise + enter

Voice:

> `In India, the same person's name can be represented differently across Aadhaar, PAN, DigiLocker, DL or PF records. When a service says “details don't match,” the citizen has to figure out which record actually matters. This is Identity Rescue.`

Action: click `I can't fetch my Driving Licence`.

## 0:10–0:22 — diagnosis

Show fictional profile and immediate result.

Voice:

> `This is entirely fictional data. The pre-flight shows one blocking edge: the Aadhaar-linked name and the mock DL issuer record don't reconcile for this retrieval rule.`

Click `Show evidence` briefly.

## 0:22–0:36 — why/correction comparison

Voice:

> `Instead of a generic mismatch error, it shows exactly what differs, why this service cares, and the source behind that rule. More importantly, it compares correction paths rather than telling the citizen to randomly edit Aadhaar.`

Click comparison.

## 0:36–0:50 — simulation “aha”

Voice:

> `For this fictional case, the minimum-impact route is this issuer-record correction. I can simulate it before doing anything real.`

Click simulate. Show blocked → ready.

## 0:50–0:59 — handoff

Voice:

> `The system rechecks downstream dependencies, shows what is now ready, what still differs but doesn't matter, and gives the exact official next action. No government system was contacted.`

Transition.

## 1:00–1:14 — product-thinking proof

Open Scenario B or show prepared split-screen/code only if navigation is instant.

Voice:

> `The core is not fuzzy name matching. In our EPFO case, a visible name difference is deliberately *not* the blocker—the service-history condition is. That prevents the product from giving confident but wrong identity advice.`

## 1:14–1:32 — architecture

Show concise architecture diagram/code view:

`synthetic adapters → normalization → deterministic rules → correction planner → simulation → evidence`.

Voice:

> `All decisions are deterministic and source-traceable. The planner minimizes citizen effort, downstream breakage and uncertainty. Government integrations are simulated behind adapters, so the prototype is safe and testable.`

## 1:32–1:45 — OpenAI/Codex

Voice:

> `Codex was used throughout the pivot to refactor the existing foundation, implement the rule engine, tests and accessible UI. An OpenAI model is bounded to plain-language explanation: it receives the deterministic evidence packet, cannot change readiness, and falls back to static copy if unavailable.`

Show evidence schema/test rather than chat UI.

## 1:45–1:57 — India-first UX

Voice:

> `The experience is mobile-first, English and simple Hindi, WCAG/GIGW-aligned, and built for Indian name structures—initials, expanded names, token order, no-surname cases and local-script transliteration without pretending fuzzy similarity proves identity.`

## 1:57–2:00 — close

> `Every portal sees one record. Identity Rescue helps the citizen see the journey.`

Stop before 2:00. Aim recording around 1:55–1:58 to avoid platform rounding.

---

# 3. What not to show in the video

- test count;
- Docker terminal unless it proves something essential;
- long architecture poster;
- database schema scroll;
- admin tooling;
- AI chat conversation;
- every scenario end-to-end;
- every accessibility setting;
- repo folder tour;
- speculative future integrations.

The first minute must remain a citizen transformation.

---

# 4. Project summary — under 250 words

## Submission-ready draft

**Identity Rescue** is an independent prototype for a common failure across Indian public services: the same citizen detail can be represented differently across Aadhaar, PAN, DigiLocker, Driving Licence, EPFO and other records, while the final portal only says that the details do not match.

Instead of asking citizens to guess which database to edit, Identity Rescue starts with their goal. Using fictional records, it reconstructs only the dependencies relevant to that task, identifies the causal blocker, shows the exact evidence and source behind the rule, compares correction paths, and lets the citizen simulate the minimum-impact change before taking any real action. It can also identify when a visible identity difference is *not* the reason a service is blocked.

The prototype uses deterministic, versioned rules for compatibility, readiness and correction planning. An OpenAI model is bounded to plain-language explanation and cannot change the underlying decision; the complete journey still works if AI is unavailable. Government systems and sensitive data are fully mocked—no real Aadhaar, PAN, UAN, OTP or private API is used.

The interface is mobile-first, accessible, English/Hindi-ready, and designed around Indian naming realities such as initials, expanded names, token ordering, absent surnames and transliteration. The result is not another government dashboard: it is a pre-flight debugger that tells citizens what actually blocks their task, what not to change, and where to go next officially.

---

# 5. Architecture slide/view for minute two

Keep to six boxes:

```text
[Fictional Citizen Case]
          ↓
[Synthetic Service Adapters]
          ↓
[Normalizer + Evidence-Preserving Record Model]
          ↓
[Deterministic Rules + Readiness]
          ↓
[Correction Planner + Simulation]
          ↓
[Citizen Explanation + Official Handoff]

Optional sidecar:
[OpenAI Explanation Layer]
  reads evidence only; cannot mutate decisions
```

Do not show Kafka/Saga/outbox if not used by the visible product.

---

# 6. README/reviewer section recommended in repository

Include:

1. One-sentence problem.
2. Live demo URL.
3. `Use fictional case A first`.
4. Prototype limitations.
5. No live government integration.
6. OpenAI/Codex usage.
7. Architecture.
8. How to run locally.
9. How to run tests.
10. Official source list.

---

# 7. Submission checklist

## Live link

- [ ] public/incognito works;
- [ ] no auth permission screen;
- [ ] HTTPS;
- [ ] mobile works;
- [ ] all golden scenarios load;
- [ ] official external links work;
- [ ] no dev banners/errors;
- [ ] no real secrets in bundle.

## Video

- [ ] <= 2:00;
- [ ] first minute citizen journey;
- [ ] second minute build/product choices;
- [ ] Codex/OpenAI role clearly stated;
- [ ] mocks/limitations stated;
- [ ] captions if possible;
- [ ] cursor/zoom readable;
- [ ] no dead time;
- [ ] public link works without permission.

## Summary

- [ ] < 250 words;
- [ ] explains real problem;
- [ ] explains why solution is better;
- [ ] synthetic/mock disclosure;
- [ ] OpenAI role;
- [ ] no unsupported scale/impact claim.

## Final rules

- [ ] official brief/FAQ rechecked same day;
- [ ] submission email correct;
- [ ] teammate email correct if applicable;
- [ ] every submitted link tested from logged-out/incognito session;
- [ ] submit well before 8:00 PM IST.

<!-- END 08_DEMO_SUBMISSION.md -->

---

<!-- BEGIN 09_IMPLEMENTATION_BACKLOG.md -->
# 09 — Implementation Backlog, Pivot Sequence & Scope Control

## Objective

Convert the existing Handover29C engineering foundation into Identity Rescue without a ground-up rewrite unless the repository audit proves reuse is more expensive than replacement.

The execution unit is a **vertical citizen slice**, not infrastructure layer completion.

---

# 1. Reuse audit

## Keep by default if stable

- routing/app shell;
- TypeScript/build configuration;
- accessible primitive components;
- i18n plumbing;
- design tokens that meet new visual direction;
- error boundary;
- test runner and CI;
- deployment config;
- Docker only if it is already useful;
- SQLite/local persistence primitives;
- fixture utilities;
- logging abstraction;
- security headers;
- existing responsive utilities.

## Replace/quarantine

- vehicle verification domain models;
- dealer verification;
- statutory Form 29C logic;
- checkbox-centric citizen flow;
- vehicle-transfer copy;
- PDF-as-primary-outcome screens;
- unused WebSocket flows;
- test suites whose only value is the abandoned domain;
- admin/architecture UI irrelevant to new citizen flow.

## Keep only if zero-cost

- hash-chain audit infrastructure;
- transactional/event machinery;
- elaborate container orchestration.

Do not spend time surfacing these to justify prior work.

---

# 2. Vertical-slice build order

## Slice 0 — product shell

Definition of done:

- root landing with three scenario cards;
- global prototype disclosure;
- English/Hindi switch plumbing;
- mobile shell;
- sources/limits page placeholder;
- no vehicle copy remains on citizen route.

## Slice 1 — Scenario A end-to-end

Implement **before** Scenario B/C:

1. Ananya fixture.
2. Aadhaar/DL/PAN mock adapters.
3. record model.
4. conservative normalizer.
5. DL rules.
6. readiness evaluator.
7. diagnosis UI.
8. evidence drawer.
9. correction actions.
10. planner.
11. simulation/undo.
12. final official handoff.
13. E2E test desktop/mobile.

When Slice 1 works, you already have a submission-shaped product.

## Slice 2 — Scenario B causal disambiguation

Reuse engine, add:

- Arvind fixture;
- EPFO adapter;
- name compatibility rule;
- non-identity service-history rule;
- finding stack UI if needed;
- anti-error test that name correction does not unblock case.

## Slice 3 — Scenario C sequencing

Reuse planner, add:

- Meera fixture;
- life-event goal;
- chosen-current-name intent;
- alternative correction actions;
- minimum-sequence UX.

## Slice 4 — bounded AI

Only after all three deterministic slices pass:

- explanation endpoint/service;
- structured evidence packet;
- output schema;
- fallback templates;
- grounding validator;
- AI-off E2E.

## Slice 5 — accessibility/localization/performance hardening

- Hindi golden-path review;
- screen reader;
- 320px reflow;
- keyboard;
- reduced motion;
- slow-network test;
- bundle trimming.

## Slice 6 — submission

- deployed production;
- source verification;
- video rehearsal;
- exact 2-min recording;
- <250 word summary;
- README;
- incognito link test.

---

# 3. Date plan

Current package date: 22 August 2026. Official deadline used: 28 August 2026 8:00 PM IST.

## Aug 22 — freeze + audit

- commit current Handover29C baseline/tag;
- create pivot branch;
- inventory reusable code;
- install package specs in repo `/docs/identity-rescue/`;
- remove old citizen routing from default entry;
- implement shell/scenario fixtures skeleton.

**Gate:** new root route clearly communicates Identity Rescue.

## Aug 23 — Scenario A

- domain model;
- normalizer;
- rules;
- evidence;
- planner;
- complete DL journey.

**Gate:** Scenario A works deployed end-to-end on mobile and desktop.

## Aug 24 — Scenario B + C

- EPFO disambiguation;
- life-event sequencing;
- unit/property tests;
- polish shared UI.

**Gate:** three deterministic journeys pass.

## Aug 25 — AI + Hindi + accessibility

- bounded explanation;
- fallback;
- full Hindi P0 strings;
- axe/keyboard/reflow.

**Gate:** AI-off still passes; no critical a11y issues.

## Aug 26 — product polish / no new conceptual features

- microcopy;
- visual hierarchy;
- mobile bugs;
- source drawer;
- privacy/sources pages;
- performance;
- final official-link registry.

**Feature freeze end of day.**

## Aug 27 — regression + deployment + recording rehearsals

- clean deploy from main/release branch;
- E2E regression;
- source verification;
- demo timing;
- README/submission summary;
- record candidate video.

## Aug 28 — submission safety day

No ambitious new features.

- final regression;
- incognito/mobile check;
- official rules recheck;
- final video/public permissions;
- submit before deadline with buffer.

---

# 4. P0 / P1 / cut rules

## P0 cannot be cut

- three golden cases;
- diagnosis/evidence;
- causal blocker distinction;
- correction planner;
- simulation;
- official handoff;
- synthetic disclosure;
- mobile;
- English/Hindi core;
- accessibility baseline;
- deterministic operation without AI.

## P1 cut first when behind

- free-text rejection parser;
- audio/read-aloud;
- downloadable summary;
- additional languages;
- dark mode if not already stable;
- additional agencies;
- advanced graph animation;
- analytics dashboard.

## Never add before submission unless a P0 defect demands it

- microservices decomposition;
- Kafka;
- event sourcing rewrite;
- blockchain;
- vector DB;
- OCR document upload;
- live government APIs;
- multi-agent orchestration;
- admin portal.

---

# 5. Engineering work packages

## WP-01 — domain types

Deliver:

- enums/types;
- fixture versioning;
- evidence types;
- action/plan types;
- validation schema.

## WP-02 — fixtures/adapters

Deliver:

- 3 golden profiles;
- edge fixtures;
- adapters;
- no-real-ID validation.

## WP-03 — normalizer

Deliver:

- Unicode/whitespace/punctuation transformations;
- initial detection;
- controlled relations;
- tests.

## WP-04 — rule engine

Deliver:

- rule registry;
- comparator functions;
- evidence trace;
- unknown behavior;
- tests.

## WP-05 — planner/simulation

Deliver:

- allowed action graph;
- cost function;
- deterministic search;
- state overlay;
- undo/reset;
- tests.

## WP-06 — UI vertical flow

Deliver:

- home;
- diagnosis;
- compare;
- simulation;
- next action;
- source drawer;
- responsive behavior.

## WP-07 — i18n/a11y

Deliver:

- locale keys;
- Hindi strings;
- semantic structure;
- focus/live regions;
- reflow.

## WP-08 — AI

Deliver:

- server-only endpoint;
- prompt/schema;
- grounding validation;
- fallback;
- tests.

## WP-09 — trust/security

Deliver:

- disclosure;
- privacy page;
- source registry;
- external link allowlist;
- secret/dependency scans;
- logs sanitized.

## WP-10 — submission

Deliver:

- production URL;
- README;
- architecture visual;
- demo recording;
- project summary;
- final checklist.

---

# 6. Pull-request / commit gate

Every meaningful change should answer:

- Which requirement ID does this implement/fix?
- Does it improve the citizen journey or protect its correctness?
- Is new scope P0, P1 or accidental?
- Does it change a rule/source? If yes, were provenance/tests updated?
- Does it add a new external dependency? Is it necessary?
- Does it keep AI outside the decision boundary?

Reject work that cannot answer those questions.

---

# 7. Agent loop

For an autonomous coding agent:

1. Inspect repo and current test/deploy health.
2. Read source-of-truth docs.
3. Select highest-priority failing P0 acceptance criterion.
4. Implement smallest vertical change.
5. Run targeted tests.
6. Run relevant integration/E2E.
7. Inspect rendered UI, especially mobile.
8. Update requirement coverage notes.
9. Commit only coherent passing work.
10. Repeat until all P0 gates pass.
11. Then and only then consider P1.

The agent must not “improve architecture” in parallel unless required by a failing P0 criterion.

<!-- END 09_IMPLEMENTATION_BACKLOG.md -->

---

<!-- BEGIN 10_MASTER_AGENT_PROMPT.md -->
# 10 — Master Agent Prompt: Handover29C → Identity Rescue

Copy this prompt into the coding agent together with this entire package and the repository.

---

## MASTER PROMPT

You are the principal product engineer, staff UX engineer, public-service systems designer, accessibility engineer, QA lead and evidence-grounded AI engineer responsible for completing a competition-grade pivot for **Build What Moves India**.

Your job is not to brainstorm. The product decision is frozen.

# PRODUCT TO BUILD

**Identity Rescue** — an independent browser-based hackathon prototype that helps a citizen understand which cross-service identity-data inconsistency actually blocks a selected Indian public-service task, why it matters, what correction routes exist, what the minimum-impact correction sequence is, what would happen if that correction were made, and what official action the citizen should take next.

The main conceptual pipeline is:

**citizen goal → relevant fictional records → evidence-preserving normalization → service-specific deterministic rules → causal blocker → correction alternatives → deterministic minimum-impact planner → simulation → re-evaluated readiness → official handoff**

This is **not** a universal identity verifier, Aadhaar/PAN matcher, government integration, KYC provider, chatbot, document generator or admin dashboard.

# ABSOLUTE SOURCE OF TRUTH

Read these files before changing code, in this precedence order:

1. `00_MASTER_SPEC.md`
2. `01_PRD.md`
3. `02_SRS.md`
4. `03_UX_UI_DESIGN_SYSTEM.md`
5. `04_CITIZEN_SCENARIOS_RULEBOOK.md`
6. `05_AI_SAFETY_GROUNDING.md`
7. `06_DATA_PRIVACY_SECURITY.md`
8. `07_TESTING_ACCEPTANCE.md`
9. `08_DEMO_SUBMISSION.md`
10. `09_IMPLEMENTATION_BACKLOG.md`
11. `SOURCES.md`

If the old repository conflicts with these documents, the old **domain behavior** loses. Preserve old infrastructure only where it accelerates the new product.

# FIRST ACTION — REPOSITORY AUDIT

Inspect the repository before refactoring. Establish:

- actual frontend/backend stack and versions;
- routing structure;
- database/persistence layer;
- current fixture/test infrastructure;
- accessibility/i18n primitives;
- deployment/Docker setup;
- security middleware/headers;
- vehicle-transfer-specific modules/routes/tests;
- reusable generic modules;
- current production build/test status.

Create a concise internal migration map:

**KEEP / ADAPT / DELETE-OR-QUARANTINE / UNKNOWN**.

Do not spend a cycle writing a huge audit report instead of coding. Audit enough to make safe changes, then execute.

# NON-NEGOTIABLE PRODUCT RULES

1. The root experience is citizen-first and goal-first.
2. The first useful diagnosis must appear within roughly 20 seconds of a reviewer entering a fictional case.
3. Three P0 golden journeys are mandatory:
   - DigiLocker / Driving Licence name-reconciliation failure;
   - EPFO pre-flight where the visible name difference is deliberately **not** the causal blocker;
   - life-event reconciliation showing a minimum correction sequence.
4. Every P0 case uses only fictional/synthetic records. Never request real Aadhaar, PAN, UAN, OTP, payment, biometric or identity documents.
5. Do not call live government APIs or reverse-engineer private systems.
6. Persistent disclosure: `Independent hackathon prototype · Fictional data · No government connection` or semantically equivalent copy.
7. Every blocker must be traceable to input facts + deterministic rule ID + source/provenance status.
8. A visible mismatch is not automatically a blocker.
9. `UNKNOWN` / `NEEDS REVIEW` is preferable to an invented answer.
10. Never infer legal identity from fuzzy string similarity.
11. Never assume universal Indian first/middle/last-name structure.
12. Initial expansion only occurs when the fictional profile explicitly encodes that relation.
13. Transliteration may support review/controlled fixture equivalence; it must not independently prove identity.
14. The correction planner is deterministic and goal-conditioned.
15. AI cannot change readiness, blocker classification or correction-plan selection.
16. The complete P0 journey works if AI is disabled.
17. Do not imply that simulation updated a real government record.
18. The final screen always provides a source-backed official next action or explicitly says official confirmation is required.
19. Mobile and accessibility are product correctness requirements, not later polish.
20. Do not create architecture theatre: no Kafka, microservices, vector DB, agent swarm, blockchain, WebSockets, event sourcing or other infrastructure unless the current repo already uses it and retaining it is objectively cheaper/safer than removing it for P0.

# INDIA-FIRST UX REQUIREMENTS

Do not make the interface “Indian” through tricolour gradients, monuments, stock photography, flag motifs or bureaucratic styling.

Make it India-first through actual interaction requirements:

- English + simple Hindi P0;
- language chosen by user, never assume Hindi is universal;
- locale architecture ready for additional Indian languages/scripts;
- Noto Sans/robust Indic typography or equivalent;
- names with initials, expanded initials, no surname, multiple-token surnames, patronymic structures, token-order differences and local-script/Latin representations;
- exact original values preserved beside any normalized/derived representation;
- mobile-first layout at 320 CSS px;
- slower-network tolerance;
- simple, verb-first microcopy;
- assisted-use friendliness;
- visible official source and next action;
- GIGW 3.0 / WCAG 2.1 AA-aligned semantics and reflow.

Do not use jargon like `canonicalization`, `entity resolution`, `graph edge` or `predicate` in primary citizen copy. Those terms are acceptable in developer architecture.

# UI / VISUAL QUALITY BAR

The interface must look deliberate and premium but restrained.

MUST:

- have one obvious primary action per state;
- use strong typography and whitespace;
- use status color only semantically and always with text/icon;
- show diagnosis before graph;
- show evidence through progressive disclosure;
- render record comparison as readable cards/definitions, not enterprise tables on mobile;
- render dependency graph as a small supporting visualization with a full text trail alternative;
- make the blocked → simulated correction → ready transformation visually unmistakable;
- preserve focus and announce readiness changes;
- respect reduced motion;
- maintain contrast;
- avoid fixed layouts that break Hindi/Indic text.

MUST NOT:

- open with a chatbot;
- create a dashboard of arbitrary metrics;
- create fake percentage “identity health/readiness”;
- use glassmorphism/neon/sparkles/AI gradients;
- use government logos/emblem as product branding;
- make the graph the homepage;
- surface old test counts/architecture as citizen value;
- make PDF export the climax;
- add a feature that exists only because it sounds advanced.

# REQUIRED P0 DATA / RULE MODEL

Implement semantics equivalent to:

- `SyntheticProfile`
- `SyntheticRecord`
- `FieldValue` preserving original + derived forms
- `Goal`
- `Rule` with ID/version/input/predicate/outcome/source IDs/evidence status/last checked
- `Finding`
- `ReadinessState`
- `CorrectionAction`
- `CorrectionPlan`
- `SourceReference`
- `SimulationEvent`

Use the exact golden profiles and invariants in `04_CITIZEN_SCENARIOS_RULEBOOK.md` unless the existing implementation needs minor syntactic adaptation. Do not change their conceptual outcomes.

# REQUIRED P0 ENGINE STATES

Finding states must preserve semantics equivalent to:

- exact match;
- rule-compatible;
- non-blocking variant;
- blocking mismatch;
- needs review;
- missing required;
- non-identity blocker;
- unknown.

Readiness states:

- `READY IN THIS SIMULATION`
- `BLOCKED`
- `NEEDS REVIEW`
- `NOT AN IDENTITY-DATA ISSUE` where appropriate.

Do not collapse everything to boolean match/no-match.

# CORRECTION PLANNER

Implement explicit costs and deterministic search over allowed synthetic actions.

Objective: minimum citizen effort + minimum number of changes + minimum downstream breakage + minimum uncertainty + penalty for broad upstream/irreversible actions.

Never ask an LLM to choose the plan.

The planner must demonstrate:

- Scenario A: a narrow correction route beats a broader upstream change in the configured fixture;
- Scenario B: changing the name does not resolve the real service-history blocker;
- Scenario C: the minimum plan does not update unrelated address data merely for global consistency.

# AI IMPLEMENTATION

Add runtime AI only after all deterministic golden journeys work.

Allowed AI task: rewrite supplied evidence into plain-language explanation and optionally bounded Hindi wording.

Input is a small structured evidence packet. The model has no government tools and no arbitrary web retrieval.

Output uses a validated schema. Validate that:

- readiness/finding state is unchanged;
- source IDs are a subset of provided IDs;
- no new action is invented;
- uncertainty is preserved;
- no official-write claim appears.

On timeout/schema/grounding failure: render static template and continue.

Credentials stay server-side. Do not hard-code model names throughout business logic; configure the chosen OpenAI model in one place based on what is currently available in the implementation environment.

# ACCESSIBILITY

Treat these as stop-ship:

- missing H1/landmarks;
- keyboard trap;
- invisible focus;
- inaccessible dialog;
- status conveyed only by color;
- graph with no text alternative;
- dynamic recalculation not announced;
- horizontal scroll for normal content at 320 CSS px;
- clipped content at 200% zoom;
- broken Hindi layout;
- motion ignoring reduced-motion setting.

Run automated accessibility tests plus keyboard/manual smoke tests.

# SECURITY / PRIVACY

Strongest P0 privacy control: never ask for real data.

- no real-ID fields;
- no live government endpoint;
- no secrets in browser;
- external official URLs from an allowlisted source registry;
- AI endpoint server-side, limited and schema validated;
- production logs contain event IDs/states, not identity-like data;
- reset clears scenario-local state;
- sanitized rendering;
- dependency/security scan before submission;
- safe security headers where supported.

Do not claim blanket DPDP compliance. Use privacy-by-design language only.

# SOURCE POLICY

Use `SOURCES.md` as the current source registry. For any government-process claim changed or added during implementation:

1. Prefer current official Government of India / authority source.
2. Record URL, title, relevant proposition and date checked.
3. Distinguish direct source support from prototype simulation.
4. Never use a Reddit/blog post as the normative rule when an official source is available.
5. Never fabricate a fee, deadline, form, document requirement, processing time or correction route.
6. If unable to verify, return `NEEDS REVIEW` and label the product limitation.

Recheck P0 official links immediately before the final recording.

# TEST STRATEGY

Do not chase the old 797-test number.

Prioritize:

- property/unit tests for conservative name normalization;
- rule pass/fail/unknown;
- planner invariants;
- anti-error test: EPFO name-only correction does not unblock scenario;
- source registry integrity;
- AI fallback/grounding;
- locale completeness;
- accessibility component tests;
- E2E on the three golden paths desktop/mobile;
- AI-disabled E2E.

Use `07_TESTING_ACCEPTANCE.md` as the stop-ship contract.

# EXECUTION ORDER

Follow this order unless the repository audit reveals a hard dependency:

1. Baseline/tag current working repo.
2. Install/copy this product package into repo docs.
3. Replace default citizen entry with Identity Rescue shell.
4. Implement Scenario A end-to-end.
5. Deploy/check Scenario A early.
6. Implement Scenario B.
7. Implement Scenario C.
8. Complete deterministic tests.
9. Add bounded AI + fallback.
10. Complete Hindi.
11. Accessibility/mobile/performance/security hardening.
12. Sources/limits/privacy pages.
13. Production deployment.
14. Final E2E/source verification.
15. Demo/readme/submission.

Do not build horizontal infrastructure for all agencies before Scenario A works in the browser.

# AUTONOMOUS LOOP BEHAVIOR

Continue working in iterative loops until all P0 acceptance gates pass or a genuine external blocker makes further progress impossible.

For each loop:

1. Identify the highest-priority failing P0 requirement.
2. Inspect only the relevant code/tests/docs.
3. Make the smallest coherent vertical change.
4. Run targeted tests.
5. Run related integration/E2E tests.
6. Inspect the rendered UI in mobile + desktop if UI changed.
7. Check accessibility if interaction changed.
8. Check source/provenance if rule/copy changed.
9. Remove dead/old domain code when safe.
10. Record what requirement IDs are now satisfied and what remains.
11. Immediately proceed to the next highest-priority P0 gap.

Do not stop merely to ask for preference on minor implementation choices. Use the product specs, evidence and simplest maintainable solution. Ask only if an external fact/credential/irreversible repository action is truly impossible to resolve safely; otherwise make the best grounded decision and proceed.

# STATUS OUTPUT AFTER EACH MAJOR LOOP

Keep it concise and factual:

- **Completed:** requirement IDs / vertical outcome.
- **Verified:** tests + UI/a11y/source checks.
- **Remaining P0:** next 1–3 blockers.
- **Risk:** only if real.
- **Next:** exact implementation target.

Do not produce motivational filler or long speculative reports.

# DEFINITION OF DONE

The pivot is complete only when all are true:

- root URL clearly presents Identity Rescue;
- no abandoned vehicle-transfer flow is reachable as the primary citizen product;
- three golden journeys work end-to-end;
- Scenario B proves causal disambiguation;
- correction planner and simulation are deterministic;
- evidence/provenance visible;
- official handoff visible;
- all P0 data is fictional;
- AI disabled does not break the journey;
- English/Hindi core complete;
- mobile/reflow/keyboard/screen-reader smoke tests pass;
- deployed link works incognito;
- no live government API/private integration;
- no false official endorsement;
- P0 source links reverified;
- video can be recorded in <= 2 minutes with the first minute entirely citizen-facing;
- project summary remains <250 words;
- all demoed features actually work.

# FINAL QUALITY TEST

Before declaring completion, ask one product question:

> If a judge knew nothing about our codebase, would they understand the citizen pain, see the causal blocker, understand why our recommendation is safer than trial-and-error, watch the state change, and know the official next action — all before caring about our architecture?

If not, the product is not done. Fix the citizen journey before adding anything else.

---

END MASTER PROMPT

<!-- END 10_MASTER_AGENT_PROMPT.md -->

---

<!-- BEGIN 11_REQUIREMENTS_TRACEABILITY.md -->
# 11 — Requirements Traceability & Judge-Rubric Matrix

## Purpose

Use this as the final “nothing important fell through the pivot” checklist. A requirement is not complete because code exists; it is complete when the citizen behavior, tests and demo evidence exist.

---

# 1. Product-to-implementation traceability

| Capability | PRD/SRS | Primary implementation | Acceptance evidence | Demo evidence |
|---|---|---|---|---|
| Goal-first entry | PRD-F01 / FR-003 | Home/scenario cards | E2E route start | 0:00–0:10 |
| Fictional-only cases | PRD-F02 / FR-010–013 / DR-001 | Fixture store/adapters | no-real-ID tests/manual | disclosure visible |
| Relevant record view | PRD-F03 / FR-012 | Record cards | responsive/component tests | 0:10–0:22 |
| Difference classification | PRD-F04 / FR-040–045 | Normalizer/comparators | domain tests | diagnosis view |
| Causal blocker | PRD-F05 / FR-050–063 | Rule/readiness engine | Scenario B anti-error test | 1:00–1:14 |
| Evidence/provenance | PRD-F06 / FR-056/100–103 | Source registry/evidence drawer | source integrity gate | 0:22–0:36 |
| Dependency trail | PRD-F07 | Trail/graph component | mobile/a11y test | brief visual proof |
| Correction comparison | PRD-F08 / FR-070–072 | Option cards | E2E | 0:22–0:36 |
| Deterministic planner | PRD-F09 / FR-080–085 | Planner | planner unit tests | minute-two architecture |
| Simulation | PRD-F10 / FR-090–094 | Session overlay/recompute | E2E + undo | 0:36–0:50 |
| Readiness result | PRD-F11 / FR-060–063 | Readiness banner | domain/E2E | blocked → ready |
| Official handoff | PRD-F12 / FR-100–103 | Next action/source link | external-link verification | 0:50–0:59 |
| English/Hindi | PRD-F13 / FR-110–113 | i18n locale files | locale completeness/E2E-HI | 1:45–1:57 mention |
| Accessibility | PRD-F14 / ACC-* | semantic UI | axe/keyboard/NVDA/reflow | design rationale |
| Slow-network resilience | PRD-F15 / NFR-PERF-* | small critical path/fallback | throttled test | architecture rationale |
| Prototype honesty | PRD-F16 / FR-002 | global disclosure | every-route manual | first minute visible |
| Sources & limits | PRD-F17 | `/sources` | manual | optional minute two |
| Reset/clear | PRD-F18 / FR-005 | session reset | E2E/manual | reviewer resilience |
| Bounded AI | FR-120–125 / AR-* | server explanation endpoint | AI-off/schema tests | 1:32–1:45 |
| Privacy/security | DR-* / SEC-* | architecture/config | security gate | limitations explanation |

---

# 2. Hackathon rubric mapping

## Problem — “Is this a real and important user problem?”

Evidence to show:

- official Income Tax mismatch guidance;
- DigiLocker name-match/retrieval guidance;
- UIDAI initials/transliteration guidance;
- EPFO KYC naming guidance;
- Passport name-structure guidance.

Do not overstate incidence if no authoritative prevalence number is available. The submission only needs to establish a real, understandable problem, not fabricate national frequency.

## Working build — “Does the main journey actually work?”

Evidence:

- Scenario A complete in first minute;
- three E2E golden paths;
- simulation truly changes state/recomputes rules;
- deployed URL incognito-tested.

## Usability — “Simpler, clearer, accessible?”

Evidence:

- one-click fictional case;
- progressive disclosure;
- plain-language cause;
- no arbitrary scores;
- mobile 320px flow;
- English/Hindi;
- keyboard/screen reader;
- AI not blocking.

## Product thinking — “Are choices thoughtful?”

Strongest proof:

- Scenario B visible mismatch is not causal;
- planner optimizes minimum necessary correction;
- Scenario C refuses unrelated address change;
- unknown/uncertainty retained;
- no universal “Aadhaar is source of truth” shortcut.

## End-to-end thinking — backend/infrastructure/process

Evidence:

- service adapters;
- rule/evidence registry;
- normalization semantics;
- planner;
- simulation state;
- source-backed official handoff;
- resilience/fallback;
- no need for admin dashboard.

## Honesty — mocks/limitations/dependencies

Evidence:

- persistent disclosure;
- obviously fictional IDs;
- no live government calls;
- source status tags;
- “ready in this simulation” wording;
- AI boundaries;
- sources/limits page.

---

# 3. Final P0 completeness table

Before feature freeze, mark every row PASS.

| P0 item | Code | Unit/contract | E2E | Mobile | A11y | Source checked | Demo-ready |
|---|---|---|---|---|---|---|---|
| Home/shell | ☐ | ☐ | ☐ | ☐ | ☐ | N/A | ☐ |
| Scenario A | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Scenario B | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Scenario C | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Planner | ☐ | ☐ | ☐ | ☐ | N/A | N/A | ☐ |
| Simulation | ☐ | ☐ | ☐ | ☐ | ☐ | N/A | ☐ |
| Evidence | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Hindi | ☐ | ☐ | ☐ | ☐ | ☐ | N/A | ☐ |
| AI + fallback | ☐ | ☐ | ☐ | ☐ | ☐ | N/A | ☐ |
| Privacy/trust | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Deployed build | ☐ | N/A | ☐ | ☐ | ☐ | ☐ | ☐ |
| Submission assets | ☐ | N/A | N/A | N/A | N/A | ☐ | ☐ |

<!-- END 11_REQUIREMENTS_TRACEABILITY.md -->

---

<!-- BEGIN SOURCES.md -->
# Research Sources & Evidence Registry

**Checked:** 22 August 2026 unless noted.  
**Policy:** Prefer current official sources for normative product claims. Community sources may support problem discovery but do not define rules. Recheck P0 official pages before final recording/submission.

---

# A. Hackathon — normative

## SRC-HACK-001 — Builder Brief

**Publisher:** Build What Moves India  
**URL:** https://buildwhatmovesindia.com/brief  
**Relevant propositions:**

- choose one real problem on an Indian public-service website/digital service;
- build a simpler, clearer, more useful complete citizen journey;
- reviewers test citizen experience, not admin panel;
- design for mobile, slower connections and limited digital experience;
- use mock/synthetic data for personal information/OTPs/payments/government systems;
- do not access live systems/private APIs;
- disclose what works vs what is mocked;
- judging: problem, working build, usability, product thinking, end-to-end thinking, honesty;
- submission deadline shown: 28 Aug 2026, 8:00 PM IST;
- video <= 2 minutes; first minute citizen, second minute build/choices;
- project summary <250 words.

**Used by:** master scope, demo/submission requirements.

## SRC-HACK-002 — FAQ

**Publisher:** Build What Moves India  
**URL:** https://buildwhatmovesindia.com/faq  
**Relevant propositions:**

- can solve one specific problem within a public-service website or digital journey;
- main journey must be working prototype;
- every feature demoed must work;
- Codex meaningful involvement required;
- no live government connection unless approved sandbox;
- no real sensitive user data;
- do not use official logos to imply endorsement;
- deadline/submission details.

---

# B. Indian government UX/accessibility

## SRC-GIGW-001 — GIGW 3.0 Scope and Objective

**Publisher:** Guidelines for Indian Government Websites and Apps / NIC-MeitY ecosystem  
**URL:** https://guidelines.india.gov.in/scope-and-objective/  
**Relevant propositions:**

- Indian government websites/apps should be user-centric, user-friendly and secure;
- focus on usability, user-centricity and universal accessibility;
- GIGW references WCAG 2.1, RPwD Act and Indian web realities.

## SRC-GIGW-002 — New Features of GIGW 3.0

**URL:** https://guidelines.india.gov.in/new-features-of-gigw-3-0/  
**Relevant proposition:** GIGW 3.0 incorporates WCAG 2.1 Level AA and additional mobile/cognitive/low-vision accessibility requirements; cybersecurity chapter included.

## SRC-GIGW-003 — Accessibility Guidelines and Attributes

**URL:** https://guidelines.india.gov.in/accessibility-guidelines-and-attributes/  
**Relevant propositions:**

- reflow at width equivalent to 320 CSS px for normal content;
- programmatically determinable UI names/roles/states;
- contrast guidance;
- accessible structure and controls.

## SRC-UX4G-001 — UX4G Handbook

**Publisher:** UX4G  
**URL:** https://www.ux4g.gov.in/assets/img/pdf/UX4G-Handbook.pdf  
**Relevant propositions:** Noto Sans/Indic-script suitability, reusable design tokens and public-service design-system guidance.

## SRC-UX4G-002 — UX4G Brochure / Accessibility Widget

**URL:** https://www.ux4g.gov.in/assets/img/pdf/UX4G-Brochure.pdf  
**Relevant propositions:** accessibility tooling includes text sizing/spacing, dyslexia/ADHD-oriented modes, saturation, text-to-speech, pause animation and other options.

**Product interpretation:** Native semantic accessibility remains mandatory; an accessibility widget is supplemental, not a substitute for accessible implementation.

---

# C. Aadhaar / UIDAI — identity representation

## SRC-UIDAI-001 — Enrolment & Update FAQ

**Publisher:** UIDAI  
**URL:** https://uidai.gov.in/en/295-faqs/enrolment-update.html  
**Relevant propositions:**

- names should be entered carefully and fully;
- UIDAI explicitly gives examples such as `V. Vijayan` → `Venkatraman Vijayan` and `R. K. Srivastava` → `Ramesh Kumar Srivastava`;
- where documentary proofs vary between initials and full name, full name should be recorded in the described enrolment context;
- Aadhaar supports multiple regional languages;
- transliteration can require user/operator correction and can produce errors.

**Used by:** Indian name semantics, controlled initial-expansion test fixtures, transliteration uncertainty.

## SRC-UIDAI-002 — Updating Data on Aadhaar

**URL:** https://uidai.gov.in/en/my-aadhaar/about-your-aadhaar/updating-data-on-aadhaar.html  
**Relevant propositions:** demographic details can require update after life events; authentication failures/false rejects may occur; update modes depend on field/process.

## SRC-UIDAI-003 — Aadhaar Authentication History / Error Codes

**URL:** https://uidai.gov.in/en/contact-support/have-any-question/305-english-uk/faqs/aadhaar-online-services/aadhaar-authentication-history.html  
**Relevant propositions:** error codes include demographic mismatch, address mismatch, biometric mismatch, locked biometrics, invalid OTP and technical conditions.

**Used by:** product principle that “failure” has different causal classes and should not be reduced to identity string mismatch.

## SRC-UIDAI-004 — Local-language address update

**URL:** https://uidai.gov.in/en/922-faqs/aadhaar-online-services/online-address-update-process/11613-can-i-update-my-address-in-my-local-language.html  
**Relevant proposition:** English input may be transliterated to selected regional language, with correction of transliteration available.

---

# D. Income Tax — PAN/Aadhaar mismatch

## SRC-ITD-001 — Link Aadhaar guidance

**Publisher:** Income Tax Department  
**URL:** https://www.incometax.gov.in/iec/foportal/help/all-topics/e-filing-services/link-aadhaar  
**Relevant proposition:** when Aadhaar/PAN linking fails because of mismatch in name/phone/DOB, the citizen is directed to correct details in PAN or Aadhaar so they match.

**Used by:** core problem evidence; correction-routing motivation.

---

# E. DigiLocker — issuer reconciliation

## SRC-DIGI-001 — DigiLocker FAQs

**Publisher:** DigiLocker / NeGD  
**URL:** https://www.digilocker.gov.in/web/about/faq  
**Relevant propositions:**

- issued documents are fetched from issuer sources;
- for DL/RC retrieval, Aadhaar name should match the name in the DL/RC database / National Register;
- generic errors include details not matching issuer data;
- if the DL/RC record does not exist in the National Register, DigiLocker cannot fetch it;
- DigiLocker profile name/DOB derive from Aadhaar in the described flow.

**Used by:** Scenario A rules; non-identity “record absent” edge case.

## SRC-DIGI-002 — DigiLocker Ask Our Experts

**URL:** https://www.digilocker.gov.in/assets/DIGILOCKER%20ASK%20EXPERT.pdf  
**Relevant proposition:** published guidance discusses name-order mismatch between Aadhaar and degree certificates and states document retrieval can fail when names do not match.

**Used by:** evidence that ordering/representation differences are a citizen-facing interoperability issue.

---

# F. EPFO — KYC / multiple blockers

## SRC-EPFO-001 — FAQ on UAN & KYC

**Publisher:** EPFO  
**URL:** https://www.epfindia.gov.in/site_docs/PDFs/Circulars/Y2020-2021/FAQUANKYC.pdf  
**Relevant propositions:**

- name as per Aadhaar and PAN must align appropriately with PF records for KYC;
- name change request can be raised in mismatch situations;
- EPFO workflows include date-of-exit handling and employer/portal actions.

**Used by:** Scenario B identity rule and broader process model.

## SRC-EPFO-002 — Higher Pension FAQ / error table

**URL:** https://www.epfindia.gov.in/site_docs/PDFs/MiscPDFs/Higher_Pension_FAQs_Eng.pdf  
**Relevant propositions:** EPFO documents errors involving names as per UAN/PPO, DOB/name mismatch and member-ID details.

**Used by:** evidence that multiple record relationships can generate distinct failure classes.

**Important prototype note:** Scenario B’s exact service-history predicate is `PROTOTYPE_SIMULATION`; do not present it as EPFO’s undocumented production claim engine.

---

# G. Passport Seva — name structures

## SRC-PASS-001 — Passport Application Form Instructions

**Publisher:** Passport Seva / Ministry of External Affairs  
**URL:** https://passportindia.gov.in/AppOnlineProject/pdf/ApplicationformInstructionBooklet-V3.0.pdf  
**Relevant propositions:**

- citizens without surname can leave surname blank and put full name in given name;
- initials should be expanded in passport application;
- surnames may contain multiple words;
- titles/honorifics should not be part of the name.

**Used by:** name data model must not enforce first/last structure.

## SRC-PASS-002 — Passport Manual

**URL:** https://www.passportindia.gov.in/AppOnlineProject/pdf/Passport_Manual_16_Chapters_to_be_disclosed.pdf  
**Relevant proposition:** manual recognizes regional name practices involving father-name initials/last-name patterns and treats name changes with context-specific procedures.

---

# H. Privacy / DPDP

## SRC-DPDP-001 — Digital Personal Data Protection Rules, 2025

**Publisher:** MeitY  
**Landing page:** https://www.meity.gov.in/documents/act-and-policies/digital-personal-data-protection-rules-2025-gDOxUjMtQWa  
**Gazette PDF:** https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf  
**Relevant proposition:** final Rules were notified 14 Nov 2025 with phased commencement; not all substantive rules came into force simultaneously.

**Used by:** do not make blanket “DPDP compliant” claims; design with data minimization/transparency principles and obtain legal review for production.

---

# I. Supporting uploaded research

The supplied project research note is valuable for:

- DPI modularity / thin interfaces;
- progressive disclosure;
- plain-language error handling;
- system-status visibility;
- GIGW/UX4G accessibility direction;
- privacy-by-design concepts.

This product package intentionally rejects its implication that Saga, transactional outbox, idempotent messaging, SEDA/microservices are automatically necessary for this prototype. Those are valid architectural patterns in distributed systems but would be premature here without a distributed production workflow.

---

# J. Evidence-writing rules

When adding a source:

1. Use official page/PDF if available.
2. Record exact proposition used, not a broad summary.
3. Do not quote long passages in product UI.
4. Record checked date.
5. Link the rule IDs that depend on it.
6. If source only establishes a general dependency, label the exact demo predicate as interpreted/simulated.
7. If a current source contradicts an older source, prefer current official guidance and update fixtures/tests.
8. Community posts can inform UX/problem discovery, never silently become normative requirements.

<!-- END SOURCES.md -->
