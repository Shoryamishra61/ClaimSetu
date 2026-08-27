# ClaimPath completion audit

Audit date: 2026-08-27

The current public-product decision is [docs/final-night/01_PROBLEM_VERDICT.md](docs/final-night/01_PROBLEM_VERDICT.md). The broader Identity Rescue documents remain historical research, not the judged scope.

| Requirement | Evidence | Status |
|---|---|---|
| Focused citizen journey | Three visible states and two primary actions | PASS in component and Playwright tests |
| Sensitive-data minimization | No free-text or identifier intake | PASS |
| Fictional integration test | Sample download/upload, strict schema, backend/browser execution, recomputation and result export | PASS |
| Causal diagnosis | EPFO-001 name condition passes; EPFO-002 Date of Exit condition fails | PASS |
| Minimum fix | planner selects only `ACT-B1` | PASS |
| Counterfactual proof | name-only action remains non-ready; Date of Exit action reaches modeled-ready | PASS |
| Evidence/provenance | original value, rule/version, evidence status, sources, uncertainty | PASS |
| Official handoff | primary EPFO Member Portal plus official UMANG fallback; process-change caveat shown | PASS locally and live |
| Honest result | UI says modeled checks pass and does not guarantee approval | PASS |
| English/Hindi | every registered key has both locales | PASS automated; human review pending |
| Container | same-origin SPA/API, health endpoint, non-root user | PASS |
| Visual/browser QA | desktop and 320 px Playwright screenshots inspected; axe and overflow checks pass | PASS automated; manual browser and native screen-reader checks remain unclaimed |

## Key invariants

- The fictional name difference is visible but not causal for this modeled goal.
- The missing Date of Exit is represented as `NOT_RECORDED`, never fabricated as null evidence.
- Only allowlisted actions can be simulated; arbitrary or oversized mutations return 422.
- Simulation changes bundled fictional state only and recomputes all rules.
- The judged path collects no citizen-entered identity data.
- The optional sandbox accepts only bounded fictional names, dates and booleans; unknown fields and digit-bearing names are rejected.
- No government API, real identifier, OTP, payment, biometric, upload, or official write is used.
