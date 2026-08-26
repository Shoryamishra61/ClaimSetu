# ClaimPath build status

`DETERMINISTIC_CORE_COMPLETE=true`

`PUBLICATION_VERIFIED=true`

Last updated: 2026-08-27

The current source of truth is `docs/final-night/03_IMPLEMENTATION_AND_TEST_REPORT.md`.

## Implemented

- One focused EPFO old-balance transfer-prerequisite journey with two primary actions: diagnose and simulate.
- Fictional Ravi Kumar profile with Aadhaar-linked, PAN, EPFO, and service-history records.
- Causal diagnosis: the controlled `K -> KUMAR` name relation is non-blocking; missing Date of Exit is the modeled blocker.
- Deterministic minimum-action simulation using `ACT-B1`, full recomputation, before/after evidence, and undo.
- Source-backed EPFO Mark Exit guidance and Member Portal handoff checked on 2026-08-27.
- English/Hindi UI, keyboard-first semantics, responsive layouts, disclosure, privacy, and sources routes.
- Static GitHub Pages export and full same-origin FastAPI/Docker runtime.

## Verified in this build

| Gate | Result |
|---|---|
| Backend | 40 tests pass; Ruff passes |
| Frontend | 5 component/i18n tests pass |
| Build | TypeScript and Vite production/Pages builds pass |
| Dependencies | npm audit reports 0 vulnerabilities |
| Docker | rebuilt successfully; root returns ClaimPath; health is `ok`; container user is `identityrescue` |
| API journey | missing Date of Exit blocks the transfer prerequisite; `ACT-B1` reaches `READY_SIMULATION` |
| Static fixture | regenerated from the same rule engine with `DEMO-RAVI-01` |
| Public deployment | GitHub Pages build `4388d06` completed; live bundle and static data contain the EPFO Member Portal and UMANG fallback |

## Unclaimed external checks

- Automated Playwright replay, screenshots, axe checks and 320 px reflow pass locally. An in-app browser was unavailable, so an independent manual browser and native screen-reader pass remain unclaimed.
- Native screen-reader and fluent-human Hindi review require human confirmation.
- Devpost submission has not been performed.

Live demo target: <https://shoryamishra61.github.io/handover29c/>

Public source target: <https://github.com/Shoryamishra61/handover29c/tree/final-night-epfo-transfer>
