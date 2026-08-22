# Identity Rescue migration map

Baseline: `d80c11e`, tagged `handover29c-baseline-2026-08-22`.

## KEEP

- React 18, TypeScript, Vite, Vitest, Testing Library, Playwright and axe tooling.
- FastAPI application factory, total error boundary, same-origin SPA serving and security headers.
- English/Hindi language-provider primitive and responsive/accessibility CSS foundations.
- Multi-stage non-root Docker build, Compose smoke path, CI/release scaffolding and verification scripts.
- Synthetic-fixture discipline, dependency audit tooling and static asset delivery.

## ADAPT

- Root React shell, routes, copy and tests -> Identity Rescue goal-first experience.
- FastAPI metadata/health -> Identity Rescue identity and explicit zero-government-integration boundary.
- Existing deterministic service patterns -> evidence-preserving normalization, rule evaluation,
  readiness, correction planning and session simulation.
- Existing i18n dictionaries -> complete `en-IN` and `hi-IN` P0 strings.
- Existing CSS tokens/components -> restrained record cards, findings, evidence disclosure,
  correction comparison, simulation and official handoff.
- Existing Docker/environment names -> product-neutral Identity Rescue names while accepting the old
  variables temporarily where doing so avoids deployment breakage.

## DELETE OR QUARANTINE

- Vehicle/dealer verification and Form 29C routes from the default runtime.
- Vehicle-transfer state machine, WebSocket synchronization and PDF generation from the citizen path.
- Checkbox handover flow, custody API client and vehicle-domain browser tests.
- Vehicle-specific database schema/fixtures and historical controller tests from the new P0 gate.
- Vehicle-domain README, demo and submission claims from active documentation.

Old code may remain temporarily in source history or an explicitly disabled compatibility namespace;
it must not be reachable from the shipped root experience or default OpenAPI surface.

## UNKNOWN / VERIFY DURING SLICES

- Whether SQLite adds value to the P0 session journal after the deterministic API is implemented.
- Whether the optional OpenAI explanation endpoint can run with an available server-side credential;
  deterministic fallback remains mandatory either way.
- Permanent hosting destination and human Hindi/screen-reader review availability.

## Baseline evidence

- Backend: Ruff passed; 797 inherited tests passed.
- Frontend: 3 inherited component tests passed; production Vite build passed.
- Docker: inherited container was healthy before the pivot.

These results prove the inherited foundation only. They do not count as Identity Rescue acceptance
evidence.
