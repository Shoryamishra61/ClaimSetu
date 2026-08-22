# 120-second demo script

Target runtime: 105-115 seconds. Use only the fictional demo controls.

| Time | Visual | Narration |
|---|---|---|
| 0-8s | Open on the route-choice screen and point to the disclosure. | "Handover29C is an independent prototype for preparing a vehicle-custody record. Every record in this demo is fictional, and no government system is connected." |
| 8-18s | Select Private buyer, show the out-of-scope stop, then return. | "The product begins with the legal route. A private sale is a different process, so the Form 29C journey stops instead of guessing." |
| 18-35s | Select authorised dealer, use the demo vehicle, verify. | "For the supported route, the seller uses a fictional vehicle fixture. The lookup runs against local SQLite data; no real registration or identity information is requested." |
| 35-50s | Enter an invalid GSTIN once, show the inline error, then use the demo dealer. | "Malformed dealer identifiers fail with a precise, recoverable error. The active fictional dealer then advances the server-owned state." |
| 50-72s | Enter odometer 12345 and tick both confirmations. | "The handover requires a positive odometer reading and explicit confirmation from both fictional parties. These confirmations are prototype records, not electronic signatures." |
| 72-86s | Confirm and show the Record screen. | "The database moves atomically to Custody Transferred and appends a hash-chained transition event. Refresh and WebSocket loss cannot invent a later state; REST polling restores the authoritative snapshot." |
| 86-100s | Download and open both worksheet pages. | "The pre-fill worksheet mirrors the notified preparation fields and preserves our test values as extractable text. It also shows that portal declarations, both signatures, submission, and the acknowledgement are still outstanding." |
| 100-112s | Show terminal with tests/audit summary and the boundary drawer. | "The build is backed by backend, component, browser, accessibility, latency, PDF, dependency, and container checks. The product closes where evidence closes: it prepares a transparent fictional record and claims nothing beyond that." |

Do not say: liability severed, legally binding, official filing completed,
government verified, biometric verified, cryptographically signed, or Section 65B
certified.
