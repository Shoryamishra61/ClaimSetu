# Identity Rescue completion audit

Audit date: 2026-08-22

The frozen package under `docs/identity-rescue/` has precedence. This ledger distinguishes executable evidence from pending human or hosted checks.

| P0 item | Implementation evidence | Verification | Status |
|---|---|---|---|
| Goal-first shell | Three citizen problem cards, one-click entry, persistent disclosure | component + browser | PASS |
| Scenario A | DL name reconciliation, two routes, ACT-A1 minimum plan | unit + desktop/mobile E2E | PASS |
| Scenario B | compatible name variant plus causal service-history finding | anti-error unit + E2E | PASS |
| Scenario C | ACT-C1 only; PAN/address retained as non-blocking | planner unit + E2E | PASS |
| Deterministic rules | conservative normalization; explicit relation expansion only | backend tests | PASS |
| Evidence/provenance | original facts, rule/version, source/evidence status, uncertainty | API tests + evidence drawer E2E | PASS |
| Simulation | allowlisted mutation, before/after, recomputation, undo | backend + E2E | PASS |
| Official handoff | registry-backed HTTPS URL and process-change caveat | allowlist test + UI | PASS |
| Privacy/trust | synthetic-only controls, no real-data field, no government call | source inspection + health/API assertions | PASS |
| English/Hindi | every registered key has both locales; one Hindi flow | component + E2E | PASS automated; human review pending |
| Accessibility/reflow | semantic landmarks, dialog, focus return, live status, reduced motion CSS | axe/keyboard/320px/200% E2E | PASS automated; NVDA pending |
| AI fallback | complete static-template path; health declares `ai_required=false` | all golden E2E | PASS |
| Optional AI generation | credential-gated, schema-grounded endpoint | not implemented without credential authorization | PENDING OPTIONAL |
| Container | non-root, same-origin SPA/API, deep-link fallback | Docker smoke | PASS |
| Public deployment | permanent HTTPS, logged-out/incognito | no destination currently verified | PENDING EXTERNAL |
| Submission assets | 235-word summary, <=2-minute script, 23.88-second working capture | word/duration/frame checks | PASS local; narrated/public upload pending |

## Key invariants proved

- Scenario A: `ACT-A1` costs 45 and beats broader `ACT-A2` cost 100.
- Scenario B: `ACT-B-NAME` retains `NOT_IDENTITY_ISSUE`; `ACT-B1` reaches `READY_SIMULATION`.
- Scenario C: the minimum plan is only `ACT-C1`; address is not changed.
- Unknown/review findings cannot become ready.
- Arbitrary and oversized action mutations return 422.
- Every official handoff URL exactly equals an entry in the allowlisted source registry.
- Default OpenAPI contains only the Identity Rescue scenario, simulation, source, and health contracts.

## Product-question audit

A reviewer can understand the pain from the H1, see the causal blocker immediately, compare why the narrow recommendation is safer, watch the blocked-to-ready transformation, and reach an official next action before any architecture explanation. Scenario B is the clearest proof that this is causal debugging rather than a cosmetic PDF or fuzzy matcher.
