# ClaimPath

[Live public demo](https://shoryamishra61.github.io/handover29c/) · [Public source](https://github.com/Shoryamishra61/handover29c/tree/identity-rescue-pivot)

ClaimPath is an independent, browser-based hackathon prototype that explains why a fictional EPFO transfer claim is blocked, separates a visible but non-causal name variation from the actual modeled blocker, and simulates the minimum correction before handing the citizen to official EPFO guidance.

> Fictional demo · Not EPFO · No government connection · No official record is changed

## The four-click journey

1. **Load Ravi's fictional case** — inspect the bundled Aadhaar, PAN, and EPFO facts; optionally describe what happened in a browser-only note.
2. **Run claim pre-flight** — deterministic, versioned rules show that `RAVI K` versus `RAVI KUMAR` is not the blocker and that the missing Date of Exit is causal in this model.
3. **Simulate minimum fix** — apply only an allowlisted fictional Date of Exit correction and recompute every modeled check.
4. **Continue to official EPFO guidance** — leave the prototype through a registry-backed official link with a process-change warning.

## What makes it substantive

- Goal-specific causal diagnosis, not a universal identity score or cosmetic mismatch list.
- Original facts, source IDs, evidence status, rule ID/version, and uncertainty remain inspectable.
- A counterfactual simulation proves a name-only correction does not resolve this case.
- A minimum-cost planner searches only allowlisted fictional actions.
- The complete path works without AI, credentials, live government APIs, or sensitive data.
- English/Hindi UI, keyboard navigation, responsive layout, static hosting, and a non-root Docker runtime.

The editable note stays in `sessionStorage`, never enters the API payload, and rejects long ID-like digit sequences. All records are bundled synthetic fixtures.

## Architecture

```text
fictional records
  -> evidence-preserving comparison
  -> versioned deterministic rules
  -> causal blocker + non-causal differences
  -> minimum-cost allowlisted action
  -> full counterfactual recomputation
  -> official source handoff
```

## Run and verify

```powershell
docker compose up --build
```

Open <http://127.0.0.1:8000> locally.

```powershell
powershell -ExecutionPolicy Bypass -File scripts\verify.ps1
```

Core API contracts:

- `GET /api/v1/identity/scenarios`
- `POST /api/v1/identity/scenarios/{scenario_id}/analyze`
- `POST /api/v1/identity/scenarios/{scenario_id}/simulate`
- `GET /api/v1/identity/sources`
- `GET /healthz`

## Evidence and limits

- [Current product decision](docs/claimpath/00_PRODUCT_DECISION.md)
- [Build status](BUILD_STATUS.md)
- [Completion audit](COMPLETION_AUDIT.md)
- [Submission copy](SUBMISSION.md)
- [Preserved Identity Rescue foundation](docs/identity-rescue/README.md)

The exact Date of Exit predicate and outcome are prototype simulation logic. Official EPFO processes can change; verify the linked official guidance before acting.
