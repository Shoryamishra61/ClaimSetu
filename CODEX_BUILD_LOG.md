# CODEX BUILD LOG — Handover29C

## Entry 2026-08-22 — Stabilize and verify the FastAPI case controller

**Goal:** Make the existing backend executable and verify the complete P0 controller
contract rather than creating a competing `/initiate` API.

**Spec/gate:** SRS INV-01–INV-08; Gates G0–G6 and G8 backend clauses.

**Prompt/task summary:** Audit the supplied handover package and existing FastAPI
implementation, repair persistence/test failures, verify case initiation, vehicle/dealer
checks, pairing, canonical review, bilateral confirmation, idempotent simulated
submission, and explicit ACK/reject/temporary/unknown outcomes.

**Files inspected:**

- Final package Markdown, OpenAPI, schema, policies, and fixtures.
- `apps/api/app/` domain, adapters, services, routes, persistence, and transport code.
- All backend test modules.

**Files changed:**

- `apps/api/app/db/connection.py`
- `apps/api/app/adapters/fixture_loader.py`
- `apps/api/app/adapters/mock_form29c_adapter.py`
- `apps/api/app/errors.py`
- `apps/api/app/main.py`
- `apps/api/app/services/case_service.py`
- `apps/api/app/services/events.py`
- `apps/api/app/services/pairing_service.py`
- `apps/api/app/services/ratelimit.py`
- `apps/api/app/services/submission_service.py`
- `apps/api/pyproject.toml`
- Backend lint/introspection tests
- `apps/api/tests/vectors/canonical_v1.json`
- `BUILD_STATUS.md`

**Tests added/changed:**

- Locked canonical serialization vector.
- Corrected environment-helper AST coverage and sensitive-identifier guard coverage.
- Existing controller, API, policy, state, security, and layering tests retained.

**Commands/tests run:**

- `python -m pytest -q` — 705 collected tests passed.
- `python -m ruff check app tests` — passed.
- `python -m compileall -q app tests` — passed.

**Result:** PASS for the backend slice; overall product remains PARTIAL pending UI,
accessibility, deployment, and demo gates.

**Bugs or risks Codex found:**

- `sqlite3.executescript()` implicitly ended the manually opened transaction, so every
  fresh-database API fixture failed at startup.
- The canonical payload vector had not been generated.
- Two guard tests no longer matched their helper/identifier shapes and could not prove
  the intended property.
- The user's latest summary mentions a pre-filled Form 29C PDF, but the governing final
  package scopes P0 to a simulated portal adapter and explicitly avoids presenting a
  private/generated document as an official filing artifact.

**Human/source corrections:** The final claims ledger and current Gazette source remain
authoritative. Codex implemented their declared behavior; it did not make legal decisions.

**Commit:** `UNAVAILABLE — workspace is not a git repository`

**Next gate:** Complete the frontend and resilience/accessibility E2E loop.

## Entry 2026-08-22 - Four-state compatibility slice and complete browser flow

**Goal:** Implement the new master specification's exact custody controller, PDF,
accessible UI, and reproducible deployment package without reviving rejected legal-tech
concepts.

**Spec/gate:** `handover29c-master-spec.md`; new attachment; final package claims ledger;
four-state transition, relational, latency, PDF, accessibility, security, and container
gates.

**Prompt/task summary:** Finish the implementation without further permission prompts,
while referring to `newguidelines.md` and every Markdown file in the supplied package.

**Major implementation:**

- Added the isolated `app/custody/` FastAPI slice and mandatory SQLite tables.
- Added deterministic 10-citizen, 10-dealer, and 10-vehicle fictional seed data.
- Enforced exact transition order, relational rollback, GSTIN structure, positive
  odometer, bilateral confirmation, and hash-chained transition logs.
- Added a ReportLab PDF with extractable plate, seller, GSTIN, and an explicit
  simulated/unsubmitted boundary.
- Designed the new focused journey on Superdesign, then implemented React screens,
  bilingual critical copy, persistence, WebSocket updates, and REST polling fallback.
- Added Docker, Compose, CI, notices, reproducible scripts, screenshots, demo copy,
  and a stable PDF review artifact.

**Evidence:**

- Backend: full legacy-plus-new suite passed; Ruff and compileall passed.
- Frontend: 3 Vitest interaction tests and production build passed.
- Browser: 3 Playwright tests passed; axe serious/critical count 0; real PDF download;
  320px and 200% zoom overflow checks passed.
- Dependencies: npm audit found 0 vulnerabilities; isolated Python 3.12 `pip-audit`
  found no known vulnerabilities.
- Container: image built; Docker health `healthy`; SPA 200; process UID 100 non-root;
  containerized full mutation path and PDF response passed.
- PDF: pypdf extraction passed and a 1191x1684 page render was visually inspected with
  no clipping, overlap, or misleading official presentation.
- Demo recording: the refreshed WebM is 10.00 seconds and representative frames were
  visually inspected.

**Bugs or risks Codex found:**

- The older guideline document still promotes rejected GPS, Aadhaar, phonetic matching,
  WebCrypto, Section 65B, and liability-severed claims. The master specification and
  claims ledger override it; none entered runtime code or current demo copy.
- The in-app browser backend was unavailable, so rendered QA used the repository's
  pinned Playwright Chromium runner instead.
- A durable public host and public video upload require external account destinations;
  local container and artifact gates are complete, but those URLs are not fabricated.

**Human/source corrections:** Codex preserved the supplied evidence precedence and
implemented explicit simulation boundaries; it did not make legal decisions.

## Entry 2026-08-22 - Definitive runtime and notified-form completion audit

**Goal:** Prove the pasted TDD matrix requirement by requirement and remove the
superseded controller from the shipped runtime surface.

**Corrections and evidence:**

- Default runtime now exposes exactly eight HTTP paths and only the six custody
  tables. The superseded controller is available solely through an explicit
  regression-test setting.
- The named executable matrix now literally includes `test_db_constraints`,
  `test_state_transition_protection`, and `test_gstin_format_enforcement`, including
  the supplied `1234567890` example and a real `DRAFT` rollback assertion.
- Both vehicle and dealer lookup p95 were measured through the container at 8.20ms
  and 7.47ms respectively, below the 50ms target.
- Final G.S.R. 901(E) was checked from a government-hosted Gazette copy. The PDF was
  expanded to a two-page, field-aligned pre-fill worksheet and now makes portal
  declarations, signatures, submission, and acknowledgement visibly outstanding.
- The stable PDF was extracted programmatically and both 1191x1684 page renders were
  inspected without clipping or overlap.
- Full verification passed: 797 backend tests, Ruff, compileall, 3 Vitest tests,
  production build, 3 Playwright tests, accessibility/responsive gates, and zero
  npm audit findings.
- Rebuilt Docker evidence: healthy non-root process, FK=1, WAL, exact 10/10/10 seed
  counts, exact transition chain, two-page PDF parse, and clean custody-only volume.

**Result:** The implementation requirements are complete locally and in Docker.
Durable public hosting, public video upload, and human Hindi review remain external
submission handoff items and are not represented as completed.
