# BUILD_STATUS.md - Handover29C

`IMPLEMENTATION_COMPLETE=true`

`SHIP_READY=false`

Last updated: 2026-08-22 (session 4 - definitive-scope completion audit)

`SHIP_READY` remains false only for two external submission prerequisites: a
permanent application host and human Hindi-copy review. The source repository,
release, PDF, screenshots, and video now have durable public GitHub URLs. No host
or review outcome is fabricated.

## Verified implementation

- Exact custody path: `DRAFT -> INITIATED -> DEALER_SELECTED -> CUSTODY_TRANSFERRED`.
- Mandatory relational tables, SQLite WAL/foreign keys, atomic rollback, deterministic
  10/10/10 fictional reference fixtures, and hash-chained transition history.
- Exact vehicle/dealer/initiate/state endpoints, GSTIN HTTP 400 contract, positive
  odometer enforcement, REST reads, WebSocket synchronization, and polling fallback.
- Two-page, text-extractable Form 29C pre-fill worksheet aligned to the notified
  field structure, with portal signatures and acknowledgement visibly outstanding.
- Responsive English/Hindi React UI with private-buyer route block, 48px controls,
  3px amber focus, semantic status, 320px layout, and 200% zoom support.
- Non-root multi-stage container, Compose file, CI workflow, third-party notices,
  submission copy, demo script, screenshots, and local demo video.

## Verification summary

| Check | Result | Evidence |
|---|---|---|
| Backend tests | PASS | 797 tests collected and passed. |
| Python lint/compile | PASS | Ruff and `compileall` passed. |
| Four-state/PDF/latency tests | PASS | 16 focused tests; container p95 vehicle `8.20ms`, dealer `7.47ms` (both `<50ms`). |
| React interaction tests | PASS | 3 Vitest tests. |
| Production web build | PASS | Vite 8 build; 190.69kB JS / 9.75kB CSS before gzip. |
| Browser E2E | PASS | 3 Playwright tests against real API and fresh DB. |
| Accessibility | PASS | axe serious/critical count 0; keyboard skip-link path passed. |
| Responsive/zoom | PASS | 320px and 200% checks show <=1px horizontal overflow. |
| JavaScript dependency audit | PASS | npm audit: 0 vulnerabilities. |
| Python dependency audit | PASS | Isolated Python 3.12 `pip-audit`: no known vulnerabilities. |
| PDF extraction/render | PASS | Two 1191x1684 pages visually clean; expanded field set and boundaries extracted. |
| Container | PASS | Healthy UID 100 runtime; exact 8-path OpenAPI, six-table schema, full mutation/PDF smoke passed. |
| Demo video | PASS (local) | `output/video/handover29c-demo.webm`, 10.00 seconds, frame-checked. |
| Public smoke | TEMP PASS | HTTPS quick-tunnel UI and `/healthz` returned 200 on 2026-08-22; no uptime guarantee. |
| Public source/release | PASS | Public repository and `v1.0.2` release; five assets uploaded and PDF SHA-256 re-downloaded/verified. |
| CI/package publication | BLOCKED EXTERNAL | Workflows pass local `actionlint`, but GitHub rejected activation because OAuth lacks `workflow`; GHCR rejected the token without `write:packages`. |

## Acceptance gate ledger

| Gate | Status | Evidence / remaining limitation |
|---|---|---|
| G0 source and claims boundary | PASS | Runtime has no GPS, Aadhaar, WebCrypto, phonetic matching, Section 65B certification, or liability-severed claims. |
| G1 browser deployment | PARTIAL | Local/container and temporary HTTPS smoke pass; durable hosting account destination remains external. |
| G2 route/fixture/dealer validation | PASS | UI/E2E and backend active/inactive/not-found coverage. |
| G3 provenance and blocking checks | PASS | Historical controller is test-only; default Docker/OpenAPI/database expose only the definitive custody workflow. |
| G4 bilateral custody invariants | PASS | Seller and dealer confirmations are required and explicitly are not portal signatures. |
| G5 portal-boundary integrity | PASS | PDF/UI state `is_government_acknowledgement=false`; signatures and portal acknowledgement remain outstanding. |
| G6 refresh/socket/polling | PASS | SQLite persistence plus browser WebSocket and REST polling implementation. |
| G7 accessibility/localization | PARTIAL | Automated keyboard, focus, zoom, mobile, axe, bilingual-copy gates pass; native human Hindi review remains. |
| G8 security/dependencies | PASS | Headers, redaction, role/state checks, npm audit, pip-audit, and non-root container. |
| G9 demo integrity | PASS (local) | 10.00s working-feature recording includes failure and visible disclosure; script is source-aligned. |
| G10 Codex evidence | PASS | Build log, tests, Superdesign state, artifacts, local history, public source, and public release. |
| G11 submission package | PARTIAL | 188-word summary, notices, public source/release/video/PDF URLs; only a permanent live-app URL remains external. |

## Artifact index

- `output/pdf/handover29c-demo-form29c.pdf`
- `output/screenshots/handover29c-mobile-320.png`
- `output/screenshots/handover29c-desktop-200pct.png`
- `output/video/handover29c-demo.webm`
- `apps/web/playwright-report/` (generated locally, ignored by git)
- `SUBMISSION.md`, `DEMO_SCRIPT.md`, `THIRD_PARTY_NOTICES.md`
- `COMPLETION_AUDIT.md`

## External handoff only

1. Deploy the already-verified container to a host with a persistent volume and HTTPS.
2. Have a fluent Hindi reviewer sign off critical copy.
3. Grant GitHub OAuth `workflow` and `write:packages` scopes if hosted Actions/GHCR
   publication is desired; the validated workflow bundle is attached to the release.
4. Replace the temporary app-review URL and rerun public smoke tests.

## Durable public links

- Repository: <https://github.com/Shoryamishra61/handover29c>
- Release: <https://github.com/Shoryamishra61/handover29c/releases/tag/v1.0.2>
- Demo video: <https://github.com/Shoryamishra61/handover29c/releases/download/v1.0.2/handover29c-demo.webm>
- PDF: <https://github.com/Shoryamishra61/handover29c/releases/download/v1.0.2/handover29c-demo-form29c.pdf>
