# Handover29C

[Public release v1.0.2](https://github.com/Shoryamishra61/handover29c/releases/tag/v1.0.2)
| [Demo video](https://github.com/Shoryamishra61/handover29c/releases/download/v1.0.2/handover29c-demo.webm)
| [Verified PDF](https://github.com/Shoryamishra61/handover29c/releases/download/v1.0.2/handover29c-demo-form29c.pdf)

Handover29C is an independent hackathon prototype for preparing a fictional
vehicle-custody record for transfer to an authorised dealer. It implements the
four-state workflow `DRAFT -> INITIATED -> DEALER_SELECTED ->
CUSTODY_TRANSFERRED`, validates relational integrity in SQLite WAL mode, and
generates a text-extractable Form 29C pre-fill worksheet.

It is not a government portal. Every person, vehicle, dealer, and registry result
is fictional. Nothing is submitted to VAHAN or any government system, and no
output is represented as an official acknowledgement, e-signature, ownership
transfer, or change in legal liability.

## Why this shape

The project deliberately removes the earlier GPS, Aadhaar, WebCrypto,
phonetic-name matching, and private Section 65B certificate concepts. Its research
question is narrower: can a low-latency, accessible prototype model the custody
handover facts and state transitions without inventing a parallel legal process?

## Run locally

Requirements: Python 3.10+ and Node.js 22.12+ (Node 24 is used by the container).

```powershell
cd apps\web
npm ci
npm run build

cd ..\api
python -m pip install -r requirements.txt
cd ..\..
python scripts\run_local.py --port 8129
```

Open `http://127.0.0.1:8129`. Use the visible demo buttons; do not enter real data.

Container run:

```powershell
docker compose up --build
```

The container runs as a non-root user and persists SQLite data in a named volume.

## Verify

```powershell
cd apps\api
python -m pip install -r requirements-dev.txt
python -m ruff check app tests
python -m pytest -q

cd ..\web
npm ci
npm audit --audit-level=high
npm test
npm run build
npx playwright install chromium
npm run e2e
```

Generate the stable PDF review artifact:

```powershell
python scripts\generate_demo_form29c.py
```

## Definitive API

- `GET /api/v1/vehicle/verify`
- `POST /api/v1/case/initiate`
- `POST /api/v1/dealer/verify`
- `PATCH /api/v1/cases/{case_id}/state`
- `GET /api/v1/cases/{case_id}/custody`
- `GET /api/v1/cases/{case_id}/transitions`
- `GET /api/v1/cases/{case_id}/form29c.pdf`
- `WS /api/v1/sync/{case_id}`

The repository retains a superseded ACK-only research controller solely for its
regression evidence. It is disabled by default, absent from the shipped Docker
OpenAPI surface and database, and enabled only by an explicit test-fixture flag.
The active PDF is visibly marked as locally generated and unsubmitted.

## Regulatory boundary

The worksheet field structure was checked against final notification G.S.R.
901(E), dated 22 December 2022. Rule 55B requires electronic portal submission,
both parties' signatures, and a portal-generated acknowledgement. This prototype
does none of those things; its output is only a preparation aid. See the
[government-hosted Gazette copy](https://transport.jharkhand.gov.in/pdf/GSR901%28E%29-22December-2022-Sale-purchase-of-registered-vehicles-through-authorised-dealers.pdf).

## Evidence

- [BUILD_STATUS.md](BUILD_STATUS.md) is the current gate ledger.
- [COMPLETION_AUDIT.md](COMPLETION_AUDIT.md) maps the TDD matrix to executable evidence.
- [CODEX_BUILD_LOG.md](CODEX_BUILD_LOG.md) records implementation and verification.
- [DEMO_SCRIPT.md](DEMO_SCRIPT.md) is the <=120-second recording plan.
- [SUBMISSION.md](SUBMISSION.md) contains the <250-word submission copy.
- `output/pdf/`, `output/screenshots/`, and `output/video/` hold generated review
  artifacts, including the 10.00-second local walkthrough.

The source/evidence precedence in the final specification package remains the
authority for legal and product claims.

## Publication status

The public `v1.0.2` release contains the PDF, video, responsive screenshots, and
locally validated CI/release workflow bundle. GitHub would not activate the
workflow files or accept GHCR publication because the available OAuth token lacks
the separately required `workflow` and `write:packages` scopes. This limitation is
reported rather than presenting local verification as hosted CI.
