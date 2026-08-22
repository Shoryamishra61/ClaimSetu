# ClaimPath product decision

Date: 2026-08-23

## Decision

The public product is now **ClaimPath**, a focused EPFO transfer-claim pre-flight. It replaces the prior multi-scenario dashboard shell with one complete citizen journey:

1. Load Ravi Kumar's fictional case.
2. Diagnose the modeled claim blocker.
3. Simulate the minimum correction.
4. Continue to official EPFO guidance.

The Identity Rescue rule engine, provenance model, action allowlist, privacy controls, bilingual support, and deterministic static export remain the technical foundation. DigiLocker and life-event fixtures remain research/test assets but are not promoted in the root citizen journey.

## Problem and research question

People can see several differences across EPFO, PAN, and Aadhaar records but cannot tell which one actually prevents a task. ClaimPath asks: can a goal-specific, evidence-preserving rules engine distinguish a visible but non-causal name variation from the service-history field that blocks a modeled transfer claim?

## Demonstrated result

For the fictional Ravi case, the controlled `K -> KUMAR` relation makes the displayed name difference non-blocking. The modeled Date of Exit predicate fails because the value is explicitly `NOT_RECORDED`. Simulating only the allowlisted Date of Exit correction recomputes the case and makes the modeled checks pass. This is a simulation, not an EPFO decision or write.

## Safety boundary

- Fictional bundled records only; no Aadhaar, PAN, UAN, OTP, payment, document upload, or government API.
- Free-text context stays in session storage and long ID-like sequences are rejected before analysis.
- Readiness and the minimum action are deterministic; AI cannot choose either.
- Every official link comes from the backend source registry and the UI warns that official processes can change.

This decision supersedes the public-shell and three-equal-journey requirements in `docs/identity-rescue/`; those documents remain the preserved foundation and research record.
