# Final product specification — ClaimPath

## Product thesis

A worker changing jobs needs to transfer an old PF balance, but an unavailable previous account forces them to search across service history, FAQs and employer channels. ClaimPath connects that symptom to the documented Date of Exit prerequisite, shows the correction that is not needed, and hands the citizen to the official Mark Exit route before they retry.

## Evidence summary

EPFO FAQ 185 establishes Date of Exit as mandatory for the selected online transfer. FAQs 186, 230, 250 and 253 establish the self-service route, waiting condition and link between a missing previous account and Date of Exit. Citizen reports corroborate the dead end and escalation burden. Incidence remains unknown.

## User and job

The P0 user is a worker with a previous EPFO employment record who wants to transfer the old balance into the current account. They need to know why the previous account is unavailable and what official step comes before retrying.

## Before journey

Transfer attempt → previous account unavailable → inspect several records → suspect visible name difference → search FAQ/web or contact employer → discover Date of Exit dependency → find Mark Exit route → correct official history → retry.

## Redesigned journey

Recognizable failure → run fictional prerequisite check → see exact causal blocker and non-cause → inspect official evidence → simulate only Date of Exit → see the prerequisite change from blocked to met → follow official Mark Exit steps → retry transfer after the update appears.

## Hero interaction

`Previous PF account unavailable` → `Date of Exit is missing` → `Do not change the name for this blocker` → `simulate adding the fictional exit date` → `transfer prerequisite met` → `Manage → Mark Exit`.

## Information architecture

- `/`: complete three-state citizen journey.
- `/test-case`: optional fictional integration sandbox with sample download, strict upload validation, deterministic analysis and result export.
- `/sources`: current P0 official sources and propositions.
- `/privacy`: synthetic-only, no-live-data boundary.
- No scenario catalogue, admin surface, marketing landing page or chatbot.

## Screen behavior

### 1. Failure and intent

- H1 names the citizen outcome: move an old PF balance.
- A red-bordered failure object shows the current symptom.
- Fictional profile and three relevant record rows are visible.
- One action: **Find what blocks the transfer**.
- No text input and no identifiers.

### 2. Causal diagnosis

- H1 states that name is not the blocker; service history is.
- Primary finding states Date of Exit is absent.
- Secondary finding says not to change the name for this fixture.
- Evidence disclosure includes rule ID, values, source and the boundary between official requirement and fictional evaluation.
- One action: **Simulate minimum fix**.

### 3. Result and handoff

- Shows `NOT_RECORDED → 2026-05-31` for the fictional record.
- States that the transfer prerequisite is met in the model, not that a transfer is approved.
- Lists waiting-condition check, official Mark Exit path and retry condition.
- Provides official Member Portal and UMANG links plus undo.

## States and recovery

- `case`: useful content renders without a request.
- `busy`: primary action disables and retains its accessible name/context.
- `diagnosed`: documented blocker plus evidence.
- `result`: reversible simulated record change.
- `load_error`: plain-language retry state; existing screen remains usable.
- Static Pages fallback completes the same deterministic journey if the API is absent.
- Test-case results expose whether they ran through the FastAPI engine or browser fallback.
- Unknown fields, numeric names and unsupported situations are rejected; the product never generalizes a file to a real account.

## Edge cases

- Fewer than two months since last contribution: do not suggest self-marking yet.
- Wrong Date of Exit, contribution after exit, missing contribution, closed employer or unavailable Mark Exit: direct the citizen to current EPFO guidance/grievance route; do not fabricate a fix.
- Name relation unknown: return `needs official review`, never infer identity equivalence.
- Official link unavailable: retain source title and path text so the citizen can find it later.

## Accessibility and mobile

- Semantic headings, buttons, links, lists and `details`.
- Skip link, visible focus, keyboard-complete flow and live status/error announcements.
- No color-only meaning; icons are supplemental.
- 44+ px touch targets and 320 px reflow without horizontal scrolling.
- `lang` switches between `en-IN` and `hi-IN`; Hindi is user-controlled and does not claim pan-India language coverage.
- Reduced-motion rules remain; no fake processing delay.

## Deterministic rule

`EPFO-003 v1.0`: for this online-transfer fixture, `date_of_exit` must be present. Source: current EPFO FAQ. The app does not reproduce undisclosed EPFO eligibility logic. The fixture uses a last-contribution month of May 2026 and a fictional exit date within that month; the user must use their real records in the official portal.

## AI boundary

No AI is used in the citizen path. It is unnecessary for a published binary prerequisite and would add latency and hallucination risk. Codex was materially used to audit the evidence, narrow the product, refactor the interaction, implement tests and prepare the submission evidence.

## Backstage and institutional boundary

Working: versioned rules, source registry, fictional adapters, deterministic analysis, reversible simulation, strict `claimpath-test-case.v1` request contract, FastAPI test endpoint, result export, static fallback, localized frontend and tests.

Simulated: EPFO records, name relation, exit date, readiness recomputation and official handoff result.

Requires EPFO: authentication, real service history, validation of entered date/reason, OTP, official update, transfer eligibility and processing.

Production needs: authority-owned adapter, rule owner and review date, stale-rule fail-closed behavior, consent and minimization, case audit without identifiers, retry/availability handling, assisted channel, escalation ownership and observability.

## Privacy

The main route accepts no input. The optional sandbox accepts only a strict fictional JSON object containing names, dates and booleans; extra fields and names containing digits are rejected. It never accepts Aadhaar, PAN, UAN, OTP, password, bank data or identity documents. No live government integration exists.

## Acceptance tests

1. The first viewport names the transfer goal and recognizable failure.
2. One action reaches the exact blocker.
3. The diagnosis identifies Date of Exit and says not to change the name.
4. Evidence links to current EPFO guidance.
5. Simulation changes only the fictional Date of Exit and recomputes.
6. Result never says a real transfer was submitted or approved.
7. Official steps include the two-month condition and Manage → Mark Exit.
8. English/Hindi, keyboard, 320 px, reset, undo, static fallback and error state work.
9. No real identifiers can be entered.
10. A reviewer can download the sample JSON, load or upload it, run the backend rule, simulate the proposed correction and download the result.
11. Static deployment completes the same test through a visibly labelled browser fallback.

## Demo path

Open → click **Find what blocks the transfer** → open evidence → click **Simulate minimum fix** → show prerequisite met and official steps. Target: under 55 seconds without narration-dependent context.

## Cut list

- Broad cross-service scenario selector.
- Free-text rejection intake.
- Separate “load case” step.
- AI explanation layer.
- Withdrawal approval language.
- Universal correction-planner claims.
- Additional scenarios on the judged route.
