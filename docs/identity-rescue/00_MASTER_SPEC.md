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
