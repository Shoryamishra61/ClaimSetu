# Identity Rescue — Product Freeze Package

**Hackathon:** Build What Moves India  
**Product working title:** Identity Rescue  
**Freeze date:** 22 August 2026  
**Submission deadline used by this package:** 28 August 2026, 8:00 PM IST (official Builder Brief/FAQ as checked on 22 August 2026)  
**Status:** BUILD SOURCE OF TRUTH — do not broaden scope without replacing an explicit requirement.

## 1. What this package is

This package converts the pivot from Handover29C into a buildable, testable citizen product. It is deliberately biased toward the criteria the hackathon actually evaluates: real problem severity, a complete citizen journey, usability, product thinking, end-to-end engineering, and honesty about mocks and dependencies.

Identity Rescue is **not** a government identity system, identity-proofing service, Aadhaar/PAN matcher, grievance portal, or general AI assistant. It is an independent hackathon prototype that uses **only fictional/synthetic data** to demonstrate how a citizen could diagnose cross-service identity-data conflicts, understand the causal blocker, compare safe correction paths, simulate a correction, and leave with the exact official next action.

## 2. Locked product thesis

> Indian citizens are often forced to reconcile inconsistent identity representations across public-service systems themselves. A name expansion, token order, stale address, date-of-birth discrepancy, issuer mismatch, or downstream record dependency can block a service while each portal only reports its local failure. Identity Rescue reconstructs a synthetic cross-service identity graph, identifies the blocker for a chosen citizen goal, explains the evidence in plain language, compares correction paths, and simulates the minimum safe sequence before the citizen acts on official portals.

The product is best understood as a **pre-flight debugger for a citizen journey**.

## 3. Source-of-truth order

When documents disagree, use this order:

1. `00_MASTER_SPEC.md` — locked product boundary and non-negotiables.
2. `01_PRD.md` — user value, scope, journeys, priorities.
3. `02_SRS.md` — implementable functional/non-functional requirements.
4. `03_UX_UI_DESIGN_SYSTEM.md` — screen, component, content, accessibility behavior.
5. `04_CITIZEN_SCENARIOS_RULEBOOK.md` — synthetic profiles, deterministic rules, planner behavior.
6. `05_AI_SAFETY_GROUNDING.md` — what AI may and may not do.
7. `06_DATA_PRIVACY_SECURITY.md` — data, privacy, trust, threat controls.
8. `07_TESTING_ACCEPTANCE.md` — objective definition of done.
9. `08_DEMO_SUBMISSION.md` — reviewer path, video, summary, submission gates.
10. `09_IMPLEMENTATION_BACKLOG.md` — execution sequence and scope cuts.
11. `10_MASTER_AGENT_PROMPT.md` — loop prompt for the coding agent.
12. `SOURCES.md` — research basis and evidence status.

## 4. Three golden journeys — P0 only

The demo build must make these three journeys excellent before adding anything else:

1. **DigiLocker / Driving Licence fetch mismatch** — citizen sees which exact representation conflict blocks retrieval, why it matters, and the safest mock correction path.
2. **EPFO KYC / claim pre-flight** — system distinguishes an identity mismatch from a non-identity service-history blocker instead of falsely blaming the name.
3. **Life-event reconciliation** — citizen has legitimately changed name/address and needs to understand which synthetic record should be updated first and what downstream services may be affected.

These journeys cover: direct identity mismatch, causal disambiguation, and correction sequencing.

## 5. Non-negotiables

- The first useful result must be reachable in **under 20 seconds** from landing page using a demo profile.
- A reviewer must be able to complete one entire journey without creating an account, entering any real ID, or reading documentation.
- Every citizen-facing diagnosis must show **evidence**, **effect**, **recommended action**, and **what remains uncertain**.
- Deterministic rules decide blockers and correction consequences. AI may explain; AI must not decide identity equivalence, eligibility, or legal correctness.
- Every government interaction is mocked or linked out. No private/undocumented government API use.
- Never request or store real Aadhaar, PAN, UAN, OTP, payment, or sensitive personal data.
- Do not present the product as government-authorized. Persistent independent-prototype disclosure is required.
- No dashboard-first design. No admin panel. No vanity analytics in the main journey.
- Mobile is first-class, not a responsive afterthought. Core flow works at 320 CSS px width with no two-dimensional scrolling for normal content.
- Accessibility target: WCAG 2.1 AA / GIGW 3.0-aligned interaction behavior.
- English and simple Hindi are P0. The information architecture must not assume Hindi is universal; all copy and components must remain locale-ready for other Indian languages/scripts.
- No architecture pattern is included merely because it is sophisticated. SQLite/local persistence is acceptable for the prototype if it preserves deterministic behavior and replayability.
- The core demo must remain functional if an OpenAI runtime call is unavailable. AI failure degrades explanation quality, never the underlying diagnosis.

## 6. Package philosophy

The previous build over-optimized invisible engineering. This package reverses the ratio:

**Citizen value first → product logic second → evidence and safety third → implementation sophistication only where it improves those three.**

The retained engineering foundation is useful only if it accelerates the new journey: accessibility primitives, bilingual infrastructure, deterministic test harnesses, Docker/deployment, mock-data discipline, and stable persistence.

## 7. Research corrections applied

The supporting research file correctly emphasizes progressive disclosure, plain-language errors, accessibility, modular boundaries, and privacy-by-design. This package deliberately does **not** make Saga, Kafka, SEDA, microservices, transactional outbox, or hash-chain infrastructure mandatory. For a six-day independent prototype with simulated integrations, those patterns are unjustified unless the existing repository already uses them and keeping them is cheaper than removal.

The package also treats DPDP compliance carefully: the Digital Personal Data Protection Rules, 2025 have a phased commencement schedule. We design for data minimization and transparent notice, but do not make false legal-compliance claims.

## 8. Build command for humans and agents

Before coding anything:

1. Read `00_MASTER_SPEC.md` through `07_TESTING_ACCEPTANCE.md`.
2. Audit the existing Handover29C repository for reusable infrastructure.
3. Delete/quarantine vehicle-transfer domain logic from citizen routes.
4. Implement the three golden journeys in the exact P0 order.
5. Run acceptance gates after every vertical slice.
6. Do not start P1 until every P0 gate passes.

## 9. Definition of success

A judge should understand the problem in one sentence, see a specific blocker within seconds, change one synthetic fact, watch the downstream state recompute, understand why the recommendation is safe, and know exactly what the citizen would do next on an official channel.

If the demo instead requires explanation of the architecture before the value is visible, the product is not done.
