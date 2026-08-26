# Implementation and test report

## What changed and why

- Narrowed the judged route from broad Identity Rescue to one EPFO old-balance transfer prerequisite.
- Replaced unsupported withdrawal-risk framing with the officially documented online-transfer dependency.
- Removed the unused free-text rejection box and redundant “load case” step. The product no longer invites sensitive identifiers into an input that did not affect diagnosis.
- Added a recognizable current-failure object to the entry screen.
- Updated `EPFO-003` from an invented date-order predicate to the documented presence of Date of Exit for the selected transfer case.
- Updated the fictional last-contribution/exit dates so the demo does not contradict EPFO's two-month self-service condition.
- Added current EPFO FAQ provenance and made the working/simulated boundary more precise.
- Forced Vitest to one fork on Windows after the default worker pool stalled during baseline verification.

## Deliberately retained

React/Vite routing, FastAPI boundary, source registry, deterministic fixture export, static Pages fallback, English/Hindi plumbing, accessible primitives, security headers, test setup and deployment workflows.

## Verification commands

```powershell
python scripts/export_static_identity_rescue.py
python -m pytest -q
npm --prefix apps/web test
npm --prefix apps/web run build
npm --prefix apps/web run build:pages
npm --prefix apps/web run e2e
npm --prefix apps/web run e2e:pages
```

Observed final results:

- Ruff: pass.
- Pytest: 40 passed; one third-party Starlette deprecation warning.
- Vitest: 5 passed.
- TypeScript and both Vite production builds: pass; main JavaScript 72.15 KB gzip.
- Playwright: 5 passed, including Axe serious/critical scan and 320 px no-overflow journey.
- Static GitHub Pages smoke: pass with no unexpected external request.

## Accessibility and responsive checks

- Automated DOM/component coverage: semantic controls, complete locale keys and no identifier input.
- Playwright/Axe coverage: serious/critical violations, keyboard skip link, complete hero path, 320 px overflow, Hindi route, supporting routes and static deployment.
- Automated Playwright screenshots were inspected at desktop and 320 px states. The in-app browser was unavailable, so an independent live-browser pass and native screen-reader behavior remain unclaimed.

## Mock boundaries

Fictional: Ravi, all records, names, balance, Member IDs, contribution month, exit date and recomputed result. Working: rule evaluation, trace, simulation, undo, static fallback, localization and handoff links. Official: only EPFO can read/update an account or decide a transfer.

## Known limitations and risks

- The authenticated EPFO flow was not exercised; no real data or credentials were used.
- Incidence is unknown.
- Cases involving wrong exit dates, post-exit contributions, closed employers or portal errors need a different official route and are not diagnosed here.
- Fluent-human Hindi review and native assistive-technology testing remain unverified.
- The pre-existing raw visual path was regenerated against the final production bundle and retained beside the 117.97-second encoded submission video.

## Screenshot-led flow audit

1. **Entry — strong.** Citizen goal, current failure, fictional boundary and one action are visible in the first viewport. [Screenshot](../../output/audit-final/01-entry.png)
2. **Diagnosis — strong.** The causal blocker and the explicit “do not change” guidance dominate; evidence remains optional. [Screenshot](../../output/audit-final/02-diagnosis.png)
3. **Result — strong.** Before/after, no-real-change boundary and official Mark Exit handoff form a clear terminal state. [Screenshot](../../output/audit-final/03-result.png)
4. **320 px result — strong with evidence limit.** All three stages and the full official handoff reflow without horizontal overflow. Native screen-reader and fluent-human Hindi review remain unverified. [Screenshot](../../output/screenshots/claimpath-mobile-320.png)

The audit caught and fixed a skip-link rendering leak in full-page captures and a stale four-column progress grid. Web-interface review also replaced action-styled navigation with links, added theme color/touch behavior/text balancing, and removed dead form CSS.

## Adversarial judge loop

| Lens | Score | Evidence | Largest defect | Fix/status |
|---|---:|---|---|---|
| Problem | 8 | Current EPFO prerequisite + recent user reports | Incidence unknown | No scale claim |
| Working build | 9 | 40 API, 5 component, 5 browser tests; static smoke | Authenticated EPFO cannot be tested | Explicit institutional boundary |
| Usability | 9 | Two actions, one dominant CTA per state | Official process still leaves the prototype | Handoff is the honest completion state |
| Product thinking | 9 | Removed broad thesis, unused intake and wrong withdrawal framing | One fixture only | Chosen depth over catalogue |
| End-to-end thinking | 8 | Rule provenance, fallback, correction ownership, exceptional-case boundary | No authority adapter | Production needs documented |
| Honesty | 10 | Fictional/no-government disclosure on every state | None found | Retain release tests |
| Instant recognition | 9 | Entry screenshot names task and failure | Synthetic profile adds some density | Kept because it proves record comparison |
| Transformation | 9 | Missing prerequisite → modeled pass → official action | No real record changes | Stated, not disguised |
| Memorability | 8 | “Do not change the name” is the insight | EPFO subject is visually restrained | Restraint retained |
| Restraint | 10 | No chatbot, AI dependency, scenario dashboard or data entry | None found | Freeze scope |

## Hostile-judge answers

- **Just an FAQ?** The official FAQ supplies rules; the product joins symptom, non-cause, prerequisite, reversible counterfactual and handoff in one executable path.
- **Fake because data is mocked?** The rule trace and transformation work; identity data and government actions are visibly fictional because the brief forbids live access.
- **Why not improve EPFO copy?** EPFO should. This prototype demonstrates the exact frontstage/backstage change EPFO could adopt.
- **How can diagnosis be correct?** Only within the bundled fixture and published prerequisite. Unknown real cases are not accepted or inferred.
- **Could advice cause harm?** The product says not to change a name based on appearance, requires real records for Mark Exit, states the waiting condition and never promises approval.
