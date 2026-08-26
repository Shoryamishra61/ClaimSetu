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
