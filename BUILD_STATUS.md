# Identity Rescue build status

`DETERMINISTIC_P0_COMPLETE=true`

`SHIP_READY=false`

Last updated: 2026-08-22

## Completed

- Root URL is the citizen-first Identity Rescue shell; the vehicle-transfer UI/API is not reachable in the default product.
- Three fictional golden journeys work end to end.
- Findings preserve rule ID/version, original evidence, evidence status, source IDs, and uncertainty.
- Planner is deterministic, goal-conditioned, costed, and searched over an action allowlist.
- Scenario B proves a name-only correction does not resolve a causal non-identity blocker.
- English/Hindi core UI, persistent disclosure, privacy page, and sources/limits page are implemented.
- Simulation is reversible, re-evaluates readiness, announces the state change, and never implies an official write.
- Container serves exactly five default HTTP paths, runs as UID 100, and supports deep-link refresh.

## Current verified gates

| Gate | Result |
|---|---|
| Backend acceptance | 20 tests pass; Ruff passes |
| Frontend components/i18n | 4 tests pass |
| Production build | Vite/TypeScript pass; 195.05 kB JS and 12.64 kB CSS before gzip |
| Browser E2E | 6 Playwright tests pass across all golden journeys |
| Accessibility | axe serious/critical = 0; skip link and dialog focus-return pass |
| Reflow | complete Scenario A at 320 px; 200% zoom; <=1 px overflow |
| Security | CSP, HSTS, frame denial, no-sniff, no-referrer, permissions policy asserted |
| Dependencies | npm audit and pip-audit report no known vulnerabilities; tracked/built secret-pattern scans pass |
| Official sources | DigiLocker, UIDAI, and EPFO official sources rechecked 2026-08-22 |
| Docker | root/deep route 200, Identity Rescue-only OpenAPI, non-root UID 100 |
| Demo capture | 23.88-second automated working-feature walkthrough generated and frame-checked |
| Public source | Identity Rescue branch and working walkthrough return HTTP 200 without authentication |

## Remaining P0 / external gates

1. Optional OpenAI explanation is paused at the mandatory credential decision; deterministic fallback is the current complete behavior.
2. A permanent HTTPS deployment must be published and tested logged out/incognito.
3. Native NVDA smoke testing and fluent-human Hindi review require external human/environment confirmation.
4. Public-link smoke and the narrated final recording/submission checks remain.

No missing external result is represented as completed.

Public source: <https://github.com/Shoryamishra61/handover29c/tree/identity-rescue-pivot>
