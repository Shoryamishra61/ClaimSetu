# ClaimPath

[Live public demo](https://shoryamishra61.github.io/handover29c/) · [Test with sample JSON](https://shoryamishra61.github.io/handover29c/test-case) · [Public source](https://github.com/Shoryamishra61/handover29c/tree/final-night-epfo-transfer)

ClaimPath redesigns one EPFO dead end: a worker tries to transfer an old PF balance, but the previous account is unavailable because the previous employment has no Date of Exit.

> Independent fictional demo · Not EPFO · No government connection · No official record is read or changed

## The two-action journey

1. **Find what blocks the transfer** — a versioned deterministic rule connects the visible failure to the missing Date of Exit and says not to change the distracting name variation in this fictional case.
2. **Simulate the minimum fix** — only the fictional exit date changes; the prerequisite is recomputed, and the citizen receives the official Manage → Mark Exit path and retry condition.

EPFO's current FAQ states that Date of Exit for the previous employment is mandatory for an online transfer and documents the member Mark Exit route. ClaimPath brings the symptom, causal prerequisite, non-cause, evidence and next action into one path. It does not reproduce undisclosed EPFO eligibility logic or promise transfer approval.

## What works

- Evidence-preserving fictional records and source-versioned rule trace.
- Deterministic analysis, allowlisted simulation, full recomputation and undo.
- Same journey through FastAPI or a generated static Pages fallback.
- Downloadable `claimpath-test-case.v1` sample, strict JSON upload validation, backend execution, browser fallback and result export.
- English/Hindi switching, keyboard navigation, 320 px reflow and explicit mock boundaries.
- No citizen identifiers, identity-document upload, login, live government API or LLM dependency. The sandbox rejects unknown fields and names containing digits.

## Test the engine with fictional data

Open `/test-case`, download or load the sample JSON, edit its bounded fictional fields, then run the check — or skip the file entirely and type the answers into the short built-in form ("Answer a few questions. Get the same check."); it builds the same validated case and runs the identical deterministic rules, including the review state when a name relation is unconfirmed. In the container build, the request reaches `POST /api/v1/identity/test-case/analyze`. On static GitHub Pages, the same rules run through an explicitly labelled browser fallback. The file contract contains only fictional names, dates and booleans; real identifiers are neither needed nor accepted.

## Run and verify

```powershell
docker compose up --build
powershell -ExecutionPolicy Bypass -File scripts\verify.ps1
```

Local app: `http://127.0.0.1:8000`

## Final evidence package

- [Evidence ledger](docs/final-night/00_EVIDENCE_LEDGER.md)
- [Problem verdict](docs/final-night/01_PROBLEM_VERDICT.md)
- [Final product specification](docs/final-night/02_FINAL_PRODUCT_SPEC.md)
- [Implementation and test report](docs/final-night/03_IMPLEMENTATION_AND_TEST_REPORT.md)
- [Demo and submission](docs/final-night/04_DEMO_AND_SUBMISSION.md)
- [Sources](docs/final-night/05_SOURCES.md)

The broad Identity Rescue research is preserved under `docs/identity-rescue/` as historical evidence, not the judged product scope.
