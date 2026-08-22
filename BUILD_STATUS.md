# ClaimPath build status

`DETERMINISTIC_CORE_COMPLETE=true`

`PUBLICATION_PENDING=true`

Last updated: 2026-08-23

## Implemented

- One focused EPFO transfer-claim pre-flight with four explicit actions: load, diagnose, simulate, official handoff.
- Editable browser-only problem note with long-ID rejection before analysis.
- Fictional Ravi Kumar profile with Aadhaar-linked, PAN, EPFO, and service-history records.
- Causal diagnosis: the controlled `K -> KUMAR` name relation is non-blocking; missing Date of Exit is the modeled blocker.
- Deterministic minimum-action simulation using `ACT-B1`, full recomputation, before/after evidence, and undo.
- Source-backed official EPFO FAQ handoff checked on 2026-08-23.
- English/Hindi UI, keyboard-first semantics, responsive layouts, disclosure, privacy, and sources routes.
- Static GitHub Pages export and full same-origin FastAPI/Docker runtime.

## Verified in this build

| Gate | Result |
|---|---|
| Backend | 40 tests pass; Ruff passes |
| Frontend | 7 component/i18n tests pass |
| Build | TypeScript and Vite production/Pages builds pass |
| Dependencies | npm audit reports 0 vulnerabilities |
| Docker | rebuilt successfully; root returns ClaimPath; health is `ok`; container user is `identityrescue` |
| API journey | initial `NOT_IDENTITY_ISSUE`; recommended plan `ACT-B1`; simulation reaches `READY_SIMULATION` |
| Static fixture | regenerated from the same rule engine with `DEMO-RAVI-01` |

## Unclaimed external checks

- Pixel-level comparison, axe/browser execution, 320 px browser reflow, and clickable live-journey replay are pending because no in-app browser is available in this session. The browser tests and selectors are updated but were not executed here.
- Native screen-reader and fluent-human Hindi review require human confirmation.
- Devpost submission has not been performed.

Live demo target: <https://shoryamishra61.github.io/handover29c/>

Public source target: <https://github.com/Shoryamishra61/handover29c/tree/identity-rescue-pivot>
