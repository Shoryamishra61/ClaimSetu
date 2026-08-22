# 07 — Testing, Acceptance & Quality Gates

## Objective

The previous system accumulated hundreds of tests around the wrong citizen outcome. Identity Rescue needs fewer tests with higher product leverage. Test the **invariants that make the concept trustworthy**: causality, conservative matching, correction consequences, accessibility, synthetic-data boundaries and end-to-end completion.

A large test count is not a success metric.

---

# 1. Test strategy

## Layer A — domain unit tests

Highest volume. Pure, deterministic, fast.

Test:

- normalization;
- name token handling;
- controlled initial expansion;
- transliteration-review behavior;
- rule evaluation;
- readiness precedence;
- planner cost/constraints;
- simulation recomputation;
- source/provenance resolution.

## Layer B — contract/integration tests

Test:

- fixture ↔ adapter contract;
- rule registry ↔ source registry;
- backend/API ↔ UI DTOs if server exists;
- AI schema/fallback boundary;
- locale completeness.

## Layer C — component/accessibility tests

Test:

- semantic status;
- focus behavior;
- dialog/drawer behavior;
- diff accessibility;
- language switch;
- error messaging.

## Layer D — golden E2E tests

At minimum one complete test per locked scenario on desktop + mobile viewport.

## Layer E — manual/reviewer tests

Screen reader, keyboard, slow network, visual comprehension, Hindi copy, deployed links, two-minute recording run.

---

# 2. Recommended test budget

Do not optimize for an arbitrary number. A likely healthy P0 distribution is approximately:

- 50–80 domain unit/property tests;
- 15–25 integration/contract tests;
- 15–25 component/accessibility tests;
- 6–12 E2E tests;
- manual quality gates.

Roughly 90–140 high-value tests may be enough. If the retained infrastructure brings more tests at near-zero maintenance cost, keep them, but do not rewrite hundreds of vehicle-domain tests.

---

# 3. Domain test matrix

## 3.1 Normalization

### T-NAME-001
`ANANYA  R   KRISHNAN` normalizes whitespace but original is preserved.

### T-NAME-002
Punctuation in `R.` may be normalized for configured comparison without rewriting original.

### T-NAME-003
`R` does not expand to `RAMESH` without profile relation.

### T-NAME-004
With explicit `R -> RAMESH`, comparator can expose relation.

### T-NAME-005
Token reorder does not globally pass unless the selected rule permits it.

### T-NAME-006
No-surname fixture remains valid and does not synthesize a family name.

### T-NAME-007
Multi-token surname remains represented without destructive splitting.

### T-NAME-008
`PRIYA MENON` vs `PRIYA MEHRA` must not pass due to fuzzy similarity.

### T-NAME-009
Controlled local-script ↔ Latin pair produces at most configured compatible/review state.

### T-NAME-010
Uncontrolled transliteration produces `REVIEW`, not exact identity.

## 3.2 Dates

- ISO-equivalent exact values pass.
- ambiguous string formats are never guessed after parse failure.
- date inversion near-miss fails/reviews.
- missing mandatory date → `MISSING_REQUIRED`.

## 3.3 Rule engine

For each rule:

- pass fixture;
- fail fixture;
- missing input;
- source exists;
- version exists;
- citizen explanation key exists;
- unknown does not become ready.

## 3.4 Readiness

- blocking finding wins over passes;
- mandatory unknown → needs review;
- no identity blocker + causal non-identity blocker does not become `READY`;
- all mandatory passes → `READY_SIMULATION`;
- unrelated non-blocking finding does not prevent ready.

## 3.5 Planner

- minimum known route selected for Scenario A;
- upstream broader-impact alternative costs more when configured;
- Scenario B name-only action does not resolve target;
- Scenario C planner excludes address change for name-only target;
- action causing new modeled blocker is rejected/penalized;
- equal-cost plans surface ambiguity;
- no viable plan returns `NO_PLAN/NEEDS_REVIEW`, not fabricated route.

---

# 4. Golden E2E acceptance cases

## E2E-GJ01 — DL mismatch, desktop

**Given** clean browser, 1280px viewport  
**When** reviewer selects `I can't fetch my Driving Licence`  
**Then** fictional-data disclosure appears  
**And** initial analysis is `BLOCKED`  
**And** exact name values are visible  
**And** evidence drawer cites DigiLocker source  
**When** reviewer opens correction comparison  
**Then** recommended simulation explains modeled impact  
**When** reviewer confirms simulation  
**Then** state becomes `READY IN THIS SIMULATION`  
**And** before/after is visible  
**And** official next-action link appears  
**And** UI states no real record changed.

## E2E-GJ01-M — same at 360x800

No horizontal overflow for normal content; graph defaults to dependency trail.

## E2E-GJ02 — EPFO causal disambiguation

**Given** Arvind fixture  
**Then** the name variation is shown but marked non-blocking  
**And** service-history condition is primary blocker  
**When** a name-only simulated action is attempted (through test/debug path or alternative card)  
**Then** readiness remains blocked  
**When** causal action is simulated  
**Then** readiness updates correctly.

## E2E-GJ03 — life-event sequence

**Given** Meera fixture  
**Then** planner recommends only the required target correction  
**And** unrelated address change is not included  
**When** plan simulated  
**Then** target becomes ready  
**And** remaining old values are transparently listed as non-blocking for selected goal.

## E2E-AI-OFF

Disable/mock AI endpoint failure. All three golden journeys complete with template explanations.

## E2E-HI

Switch to Hindi before entering a case. Complete one full flow; no missing keys/English-only safety states except stable agency/product names intentionally preserved.

---

# 5. Accessibility acceptance

## Automated

Use axe or equivalent on each primary state. Zero critical/serious violations accepted without documented false-positive rationale.

## Keyboard

For each golden flow:

- skip link works;
- all controls reachable;
- visible focus always present;
- no keyboard trap;
- drawer/dialog opens/closes and returns focus;
- simulation can be completed;
- external official link reachable;
- reset reachable.

## Screen reader smoke test

At least NVDA + Chromium/Firefox on Windows if available.

Verify:

- page title/H1;
- prototype disclosure;
- scenario cards;
- readiness change;
- record comparison summary;
- mismatch state is clear without color;
- dependency trail;
- evidence drawer;
- confirmation dialog;
- final next-action steps.

## Reflow/zoom

- 320 CSS px equivalent;
- 200% zoom;
- no lost action/content;
- no horizontal scroll except explicitly exempt 2D visual that has text alternative.

## Contrast

Check all normal text, status badges, focus rings, disabled controls and charts. Do not validate only primary buttons.

## Reduced motion

With OS/browser reduced motion enabled, simulation and graph transitions should not animate materially.

---

# 6. Localization acceptance

- no raw i18n keys in production;
- no clipped Hindi buttons;
- 30–60% copy expansion tolerance;
- line breaks do not separate critical labels from values;
- `lang` attribute updates;
- screen reader pronounces Hindi content under Hindi language context;
- names/source values remain unchanged unless explicitly showing derived transliteration;
- Hindi microcopy manually reviewed for the golden path.

---

# 7. Low-network/performance acceptance

Use browser throttling / Lighthouse-like lab profile.

Target:

- LCP <= 2.5 s where hosting allows;
- no giant background images/videos;
- no blocking AI call before diagnosis;
- lazy-load non-critical source/graph modules;
- deterministic fixture analysis immediate after app data available;
- on AI timeout, fallback appears <= configured timeout and flow continues;
- retry does not duplicate simulation actions.

If targets cannot be met due to host variance, report actual numbers honestly and fix major bundle bottlenecks.

---

# 8. Security acceptance

- inspect built JS for secrets;
- run secret scan;
- run dependency vulnerability scan;
- verify no live government host used as an API endpoint;
- verify external URLs originate only from source registry;
- attempt arbitrary action ID mutation → rejected;
- attempt XSS-like synthetic text → rendered inert;
- AI endpoint rejects oversize/invalid request type;
- production logs inspected for names/free text/secrets;
- reset clears local mutations.

---

# 9. Source/provenance acceptance

Before final recording, manually click/verify every P0 official source.

For each P0 rule confirm:

- official source still exists;
- current page still supports proposition;
- source publisher is correct;
- `last_checked_at` = current verification date;
- citizen copy does not strengthen the source beyond support;
- any simulated predicate is labeled as such.

---

# 10. Visual/UI acceptance

Ask five questions on every screen:

1. What is the primary action?
2. What is the current status?
3. What is the evidence?
4. What happens next?
5. Is anything decorative competing with those answers?

Reject screen if:

- more than one primary CTA competes;
- five+ status cards appear before the cause;
- graph dominates mobile viewport;
- copy uses internal jargon;
- the user must interpret a numerical score;
- prototype disclosure is hidden;
- source/uncertainty is inaccessible;
- success implies real government update.

---

# 11. Demo-readiness gate

Run the following from an incognito browser on the deployed URL:

1. Open URL.
2. Understand problem without narration.
3. Start Scenario A in one click.
4. Reach diagnosis.
5. Show evidence.
6. Compare corrections.
7. Simulate.
8. Reach next action.
9. Reset.
10. Switch Hindi.
11. Open Scenario B and show “name is not blocker.”
12. Disable AI/network endpoint and confirm core still works.

If any manual recovery/devtools intervention is required, it is not ready.

---

# 12. Submission stop-ship defects

- core scenario broken;
- any demo feature is fake/nonfunctional;
- live government API interaction;
- real sensitive data required;
- AI determines readiness;
- source-backed claim is materially wrong/stale;
- mobile flow unusable;
- keyboard cannot finish flow;
- deployed link requires permission;
- demo implies official partnership;
- external official link is broken/misdirected;
- video exceeds 2 minutes;
- project summary exceeds 250 words;
- missing clear mock/limitations disclosure.
