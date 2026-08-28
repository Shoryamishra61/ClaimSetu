# Final release report — ClaimSetu

Date of freeze verification: 28 August 2026.

## Current product

ClaimSetu — an EPFO transfer pre-flight. One citizen job: find what actually blocks an old PF balance transfer when the previous account is unavailable, and what the minimum safe correction is.

- **Locked platform:** EPFO (recommended platform list)
- **Hero thesis:** the portal reports a status ("Previous PF account not available to transfer") but does not bring prerequisite, symptom and next action together; a visible name variation points to the wrong correction while the documented blocker — a missing Date of Exit — hides in service history. ClaimSetu makes cause, non-cause, evidence and the official next step one path.
- **Memorable result state:** "The name is not the blocker. The service history is." → simulate → "The transfer prerequisite is now met." → official Manage → Mark Exit handoff.

## Changes made in this release (28 Aug 2026)

1. **Fixed 320 px horizontal overflow (P1):** `body { min-width: 320px }` forced a 15 px horizontal scroll when a classic desktop scrollbar was present at a 320 px window. Changed to `min-width: min(320px, 100%)`. Verified: production Pages build rebuilt; all 6 Playwright e2e tests pass (including the 320 px reflow test); `scrollWidth == clientWidth` confirmed live at 320 px.
2. **Fixed 320 px step-label clipping (P2):** the three journey-step labels ("Diagnose", "Simulate", "Official next step") could not wrap in the 3-column grid at very narrow widths. Below 430 px the steps now stack vertically with full labels. Verified live at 320 px and by the full e2e suite.
3. **Submission summary corrected to exactly 250 words** (was 221 in `SUBMISSION.md`, 194 in the demo doc). Canonical copy: `submission/02_SUBMISSION_SUMMARY_250_WORDS.md`, whitespace-split count verified programmatically = 250.
4. **Created the `submission/` pack** (checklist, 250-word summary, video script, walkthrough, judge access, problem evidence, this report).
5. **Added a typed citizen flow to the sandbox** (after the initial freeze, on request): under "Answer a few questions. Get the same check.", a citizen types the two names, the Date of Exit, the waiting-period answer and the proposed exit date; the form builds the same validated `claimpath-test-case.v1` object and runs the identical deterministic engine, including the REVIEW state when a name relation is unconfirmed and rejection of names containing digits. No identifiers are accepted; answers stay in the browser tab. Verified locally across six states (REVIEW, BLOCK, FIX→met, direct MET, WAITING, invalid input) and on production in a fresh browser; full suites re-run (7 vitest, 6 e2e, static-pages smoke, tsc, build:pages).
6. No changes to the hero journey, rules, or existing pages' behaviour.

## Tests run (all pass, 28 Aug 2026)

| Gate | Result |
|---|---|
| Backend pytest | 42 passed |
| Backend ruff (app + tests_identity_rescue) | clean (one pre-existing lint note in the standalone `apps/api/seed_data.py` script, which the CI/verify gates do not include) |
| Frontend vitest | 7 passed |
| TypeScript (`tsc --noEmit`) | clean |
| `npm run build:pages` | pass |
| Playwright e2e (journey, Hindi, 320 px, sandbox, supporting routes) | 6 passed |

## Production verification (fresh browser, after deploy)

- Landing page, /sources, /privacy, /test-case, /samples JSON: all load (HTTP 200)
- Hero journey end-to-end: Diagnose → evidence disclosure → Simulate → prerequisite met → official handoff — all functional on the live URL
- Undo and Restart work; refresh returns to the deterministic landing state
- Sandbox: load sample → schema validated → deterministic check (PASS/BLOCK with source refs) → proposed fix recomputes to PASS/PASS → result export
- Hindi toggle: complete journey in Hindi, no leaked keys
- Zero JS errors / unhandled rejections across a full interaction pass; zero failed network requests

## Known non-critical limitations

- One fictional EPFO transfer case; not a general EPFO help system (disclosed in-app and in all docs).
- On the hosted Pages build the sandbox runs through an explicitly labelled browser fallback rather than the FastAPI endpoint; the container build serves the real endpoint.
- Native screen-reader and fluent-Hindi human review remain unclaimed (automated checks pass).
- Playwright's headless Chromium uses overlay scrollbars, so the 320 px fix is verified by e2e + code analysis rather than by a classic-scrollbar browser; the change only ever removes a forced minimum width.
- Devpost/form submission itself is a human step (see `submission/01_SUBMISSION_CHECKLIST.md`).

## Verdict

READY, pending the human steps: record the video, paste the summary and URL into the form, submit before 8:00 PM IST.
