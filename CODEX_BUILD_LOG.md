# Codex build log — Identity Rescue pivot

## 2026-08-22

- Tagged the pre-pivot repository as `handover29c-baseline-2026-08-22` and created `identity-rescue-pivot`.
- Copied the complete frozen Identity Rescue package into `docs/identity-rescue/` and recorded `MIGRATION_MAP.md`.
- Replaced the default citizen product and OpenAPI surface; the former vehicle domain remains quarantined behind an explicit historical flag.
- Implemented exact synthetic profiles, evidence-preserving records, conservative normalization, multi-state findings, versioned deterministic rules, explicit-cost plan search, reversible simulation, and source-backed handoff.
- Implemented three complete React journeys, English/Hindi localization, privacy/source pages, persistent disclosure, evidence drawers, accessible simulation dialog, readiness live region, reset/undo, deep-link routing, mobile reflow, and reduced-motion styling.
- Added focused rule/planner/source/security tests and Playwright golden journeys, including the Scenario B anti-error proof.
- Reworked the Docker/Compose runtime as Identity Rescue, removed default persistence requirements, kept it non-root, and verified same-origin deep-link refresh.

## Verified commands

- `uv run ruff check app tests_identity_rescue`
- `uv run pytest` — 20 passed
- `npm test -- --run` — 4 passed
- `npm run build`
- `npm run e2e` — 6 passed
- `npm audit --audit-level=high` — 0 vulnerabilities
- Docker build/runtime smoke — five-path OpenAPI, root/deep-route 200, UID 100
- `uvx pip-audit -r requirements.txt` — no known vulnerabilities
- automated demo capture — 23.88 seconds, four sampled frames visually checked

## Honest boundary

The optional OpenAI explanation layer is paused pending the required credential decision. It is not needed for any deterministic journey. Permanent public deployment, native screen-reader smoke testing, human Hindi review, and final video recording remain unclaimed.

The verified source snapshot and 23.88-second working capture were published to the public `identity-rescue-pivot` branch. Corrected workflow files remain local because the GitHub OAuth token lacks the separately required `workflow` scope; hosted CI is therefore not claimed.
