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
