# Identity Rescue

[Live public demo](https://shoryamishra61.github.io/handover29c/) · [Public source snapshot](https://github.com/Shoryamishra61/handover29c/tree/identity-rescue-pivot) · [118-second narrated submission video](https://github.com/Shoryamishra61/handover29c/raw/refs/heads/identity-rescue-pivot/output/video/identity-rescue-final-submission.mp4)

Identity Rescue is an independent, browser-based hackathon prototype that helps a citizen understand which cross-service record inconsistency actually blocks a selected public-service task—and which visible differences should **not** be changed.

Choose a service goal and fictional demo profile, describe what happened in your own words, and run a privacy-safe pre-flight diagnosis. The app then shows the exact records, causal rule, provenance, correction alternatives, deterministic minimum-impact plan, reversible simulation, and official next action.

> Independent hackathon prototype · Fictional data · No government connection

## Why it is more than a mismatch checker

- It begins with the citizen’s goal, not a universal identity score.
- Every finding carries original facts, rule ID/version, evidence status, and source IDs.
- A visible mismatch is not automatically causal: the EPFO case proves a name-only change does not resolve its service-history blocker.
- The planner searches only allowlisted fictional actions with explicit costs; an LLM never selects readiness or the plan.
- Simulation recomputes the whole case and states that no official record changed.

## Three working golden journeys

1. **DigiLocker / Driving Licence:** a narrow issuer-record correction beats a broader upstream change.
2. **EPFO pre-flight:** the visible name variation is non-blocking; the fictional service-history condition is causal.
3. **Life-event reconciliation:** one targeted name correction resolves the selected goal while PAN and address differences remain visible and unchanged.

All profiles are bundled synthetic fixtures. There are no fields for real Aadhaar, PAN, UAN, OTP, payment, biometrics, or identity documents, and no live government API is called.

The editable intake note stays in browser session storage and is never sent to the diagnostic engine. ID- or OTP-like number sequences are rejected before the journey can start.

## Architecture

```text
fictional case
  → evidence-preserving record model
  → conservative normalization
  → versioned deterministic rules
  → causal finding + readiness
  → minimum-cost action search
  → reversible simulation
  → source-backed official handoff
```

The optional OpenAI explanation layer is credential-gated and non-authoritative. The complete P0 flow currently uses static bilingual templates and works with AI disabled.

The public demo is a generated, deterministic static export of the same engine outputs, so it needs no credentials or hosted API. Docker serves the full FastAPI implementation locally. Both modes use fictional fixtures and make zero government-system calls.

## Run

Docker is the shortest path:

```powershell
docker compose up --build
```

Open <http://127.0.0.1:8000>. The container runs as a non-root user and serves the SPA and API from one origin.

Local development:

```powershell
cd apps\web
npm ci
npm run build

cd ..\api
python -m pip install -r requirements-dev.txt
cd ..\..
python scripts\run_local.py --port 8129
```

## Verify

```powershell
powershell -ExecutionPolicy Bypass -File scripts\verify.ps1
```

The focused gate covers deterministic rules/planning, mutation rejection, source allowlisting, security headers, English/Hindi completeness, axe, keyboard/dialog focus, deep-link refresh, all three browser journeys, the generated static deployment, 320 CSS px, and 200% zoom.

Generate and inspect the final narrated video with `npm run record:final`, `npm run mux:final`, `npm run encode:final`, and `npm run inspect:final` from `apps/web`. The published MP4 is 118 seconds, 1280×720, and contains one audio and one video track.

## API

- `GET /api/v1/identity/scenarios`
- `POST /api/v1/identity/scenarios/{scenario_id}/analyze`
- `POST /api/v1/identity/scenarios/{scenario_id}/simulate`
- `GET /api/v1/identity/sources`
- `GET /healthz`

The former vehicle-transfer implementation is retained only as quarantined historical research and is absent from the default OpenAPI/runtime.

## Evidence and limits

- [Frozen product package](docs/identity-rescue/README.md)
- [Migration map](docs/identity-rescue/MIGRATION_MAP.md)
- [Acceptance ledger](COMPLETION_AUDIT.md)
- [Current build status](BUILD_STATUS.md)
- [Two-minute demo script](DEMO_SCRIPT.md)
- [Submission copy](SUBMISSION.md)
- In-product `/sources` and `/privacy` pages

Official processes can change. The linked authority source must be checked before acting; exact fixture predicates are labeled when they are prototype simulations.
