# Handover29C completion audit

Audit date: 2026-08-22

This ledger maps the definitive TDD brief to current executable evidence. The
active product is the four-state custody workflow; `newguidelines.md` is retained
only as explicitly quarantined historical input.

## Requirement matrix

| Requirement | Current evidence | Result |
|---|---|---|
| SQLite foreign keys and WAL | Application connection reports `foreign_keys=1`, `journal_mode=wal`; focused schema test repeats both checks. | PASS |
| Atomic multi-row writes and rollback | `Database.write()` uses `BEGIN IMMEDIATE`/commit/rollback; seed, initiation, transition log and PDF write use it; injected child-row failure leaves no case row. | PASS |
| Exact state progression | Transition map contains only `DRAFT -> INITIATED -> DEALER_SELECTED -> CUSTODY_TRANSFERRED`; extracted Docker log contains those three edges. | PASS |
| Out-of-order HTTP 422 without mutation | `test_state_transition_protection` inserts a `DRAFT` case, attempts direct transfer, receives 422, and re-reads `DRAFT`. | PASS |
| Exact GSTIN structure and HTTP 400 | Anchored required regex; `test_gstin_format_enforcement[1234567890]` asserts 400 and exact message. | PASS |
| Positive odometer | Missing, zero, and negative values all return `INVALID_ODOMETER` HTTP 400. | PASS |
| Mock lookup p95 under 50ms | 100-request warmed container measurement: vehicle 8.20ms; dealer 7.47ms. Focused TestClient gate independently times both. | PASS |
| PDF parsing | `pypdf` verifies two pages and exact plate, seller, GSTIN, vehicle, dealer authorisation, boundary, and signature-outstanding text. | PASS |
| Mandatory schema and seed cardinality | Fresh Docker volume contains only Citizen, AuthorizedDealer, VehicleFixture, HandoverCase, StateTransitionLog and Form29CDocument; fixture counts are 10/10/10. | PASS |
| Working versus simulated boundary | SQLite/state/PDF are local working logic; vehicle/dealer registries are fictional fixtures; health reports zero live government integrations. | PASS |
| Default shipped API scope | OpenAPI contains exactly `/healthz` plus seven custody HTTP routes; the custody WebSocket is `/api/v1/sync/{case_id}`. | PASS |
| Accessible frontend | 3 component and 3 Playwright tests pass; axe serious/critical count 0; keyboard, 320px and 200% zoom gates pass. | PASS |
| Container | Python 3.12 multi-stage image runs as UID 100, reports healthy, and completes the full mutation/PDF path. | PASS |

## Exact executable matrix

- `test_db_constraints`: two parameterized foreign-key failures.
- `test_state_transition_protection`: direct `DRAFT` skip returns 422 and preserves state.
- `test_gstin_format_enforcement`: four malformed values including `1234567890`.
- `test_mock_lookup_p95_is_below_50_ms`: 100 measured vehicle requests and 100 dealer requests after warm-up.
- `test_complete_workflow_pdf_and_integrity_chain`: PDF extraction and three-edge hash chain.

The focused module collects 16 passing tests. The full backend suite collects 797
passing tests. `scripts/verify.ps1` also passes Ruff, compileall, npm audit, Vitest,
Vite and Playwright.

## Document boundary

Final notification G.S.R. 901(E) requires Form 29C to be submitted electronically
on the portal, signed by both parties, after which the portal generates an
acknowledgement. The generated two-page artifact is therefore labeled a pre-fill
worksheet. It cannot be presented as a filed form, signature, acknowledgement,
ownership transfer, or change in liability.

Authoritative format reference:
[G.S.R. 901(E), 22 December 2022](https://transport.jharkhand.gov.in/pdf/GSR901%28E%29-22December-2022-Sale-purchase-of-registered-vehicles-through-authorised-dealers.pdf).

## External submission handoff

The verified implementation is complete. Public source, release, PDF, screenshots,
and video were published under `Shoryamishra61/handover29c`; the released PDF was
downloaded again and matched locally by SHA-256. Durable application hosting and
fluent-human Hindi review still require an authenticated host or person and remain
explicitly unclaimed in `BUILD_STATUS.md`.

GitHub rejected workflow-file activation because the available OAuth token lacks
the `workflow` scope and rejected GHCR publication without `write:packages`. The
locally actionlint-validated workflow bundle is attached to release `v1.0.2` so the
missing hosted state remains auditable rather than hidden.
