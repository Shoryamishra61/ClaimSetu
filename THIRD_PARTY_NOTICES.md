# Third-party notices

Identity Rescue contains no copied government branding or proprietary source code.
The direct libraries below remain under their respective upstream licences; this
notice does not replace those licence texts in installed distributions.

## Runtime

| Package | Use | Licence |
|---|---|---|
| FastAPI | HTTP and WebSocket application framework | MIT |
| Pydantic | Request validation and typed models | MIT |
| Uvicorn | ASGI server | BSD-3-Clause |
| ReportLab | Text-extractable PDF generation | BSD-3-Clause |
| React / React DOM | Browser interface | MIT |

## Development and verification

| Package | Use | Licence |
|---|---|---|
| pytest | Python tests | MIT |
| httpx | API test client | BSD-3-Clause |
| pypdf | PDF text verification | BSD-3-Clause |
| Ruff | Python linting | MIT |
| Vite | Browser build | MIT |
| TypeScript | Static type checking | Apache-2.0 |
| Vitest | Component tests | MIT |
| Playwright | End-to-end browser tests | Apache-2.0 |
| axe-core / @axe-core/playwright | Automated accessibility checks | MPL-2.0 |
| Testing Library packages | DOM/React interaction tests | MIT |
| jsdom | Test DOM implementation | MIT |

Exact JavaScript versions and transitive packages are locked in
`apps/web/package-lock.json`. Python version ranges are recorded in
`apps/api/requirements*.txt`; the final verification report records the resolved
environment.
