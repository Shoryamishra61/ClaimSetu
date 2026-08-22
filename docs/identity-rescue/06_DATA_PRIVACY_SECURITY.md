# 06 — Data, Privacy, Security & Trust Requirements

## Scope

Identity Rescue is a hackathon prototype involving identity-like data. That makes **trust design** more important, not less, even though all P0 records are fictional.

The strongest security posture is not “we encrypted everything.” It is **we never ask for the dangerous data in the first place**.

---

# 1. Data policy

## 1.1 P0 data inventory

Allowed:

- fictional profile IDs;
- fictional names/DOBs/addresses crafted for scenarios;
- non-valid demo authority identifiers;
- rule/source metadata;
- simulation action IDs;
- anonymous technical telemetry.

Not allowed:

- real Aadhaar numbers;
- real PAN;
- real UAN/member IDs;
- OTPs;
- bank/payment details;
- passwords;
- biometric data;
- real scanned documents;
- health information;
- real grievance text containing personal identifiers;
- user-uploaded identity documents.

## 1.2 UI enforcement

P0 should offer **profile selection**, not real identity-data entry.

Do not show a realistic input labelled `Enter your Aadhaar number` even if the backend never transmits it. That trains the judge/user to trust the prototype with data the brief explicitly forbids.

---

# 2. Data classification

| Class | Example | Storage |
|---|---|---|
| PUBLIC | source titles, product copy | bundled/repository |
| SYNTHETIC-DEMO | fictional records | fixture store / local DB |
| INTERNAL-CONFIG | rule weights, feature flags | config/repo |
| SECRET | OpenAI/API credentials | environment/secret manager only |
| REAL-SENSITIVE | real IDs/OTPs/biometrics | **prohibited in P0** |

---

# 3. Privacy-by-design requirements

## PRIV-001 — Data minimization
Only load/display fields needed for the selected goal.

## PRIV-002 — Purpose visibility
The citizen should understand why each displayed field is relevant through `Why are we checking this?` or equivalent evidence UI.

## PRIV-003 — No secondary use
No synthetic/person-like data is used for advertising, profiling or unrelated analytics.

## PRIV-004 — Session clear
`Reset demo` clears mutations. If localStorage/sessionStorage is used, expose `Clear this device` and avoid indefinite stale cases.

## PRIV-005 — No hidden tracking dependency
The app must remain functional with analytics blocked.

## PRIV-006 — AI data minimization
Send only the evidence packet necessary for explanation, never entire synthetic profile if only two fields are needed.

## PRIV-007 — Human-readable privacy notice
A one-page notice explains:

- prototype status;
- fictional-data design;
- what technical telemetry is collected, if any;
- AI usage;
- external links;
- how to clear local state.

---

# 4. DPDP positioning

The Digital Personal Data Protection Rules, 2025 were notified with phased commencement. As of this package date, not every substantive rule is simultaneously in force. Therefore the product must **not** market itself as “DPDP certified/compliant” without legal review.

Correct positioning:

> `The prototype follows privacy-by-design principles such as data minimization, clear purpose, synthetic data and limited logging, and is designed with India's DPDP framework in mind.`

Avoid:

> `100% DPDP compliant.`

For a production deployment, legal counsel and the relevant authority would need to assess data-fiduciary roles, notice/consent, security safeguards, retention, rights handling, children’s data if applicable, breach response and any government-specific exemptions/obligations.

---

# 5. Threat model

## 5.1 Assets

- integrity of rule results;
- trust/provenance metadata;
- API secrets;
- deployment availability;
- source code;
- user confidence that simulation is not real government action.

## 5.2 Threat actors

- casual internet abuse/bots;
- malicious user attempting to inject instructions into AI text;
- attacker seeking exposed API credentials;
- accidental developer leakage;
- misleading UI that causes user to believe a real update occurred;
- stale/incorrect rule content (integrity threat rather than hacker).

## 5.3 STRIDE-style summary

### Spoofing
Risk: site appears official or external link spoofing.  
Controls: independent-prototype label, verified official URLs in local registry, no government branding impersonation.

### Tampering
Risk: rule/fixture changed without tests.  
Controls: version control, golden tests, optional rule hash/version display in debug mode.

### Repudiation
Risk: hard to reproduce simulation result.  
Controls: non-sensitive event journal with fixture/rule versions.

### Information disclosure
Risk: secrets or pasted personal data.  
Controls: no real inputs; server-side secrets; redaction if P1 text input exists; sanitized logs.

### Denial of service
Risk: public AI endpoint abuse.  
Controls: rate limit, timeout, circuit breaker/fallback, core works without AI.

### Elevation of privilege
P0 has no meaningful privileged citizen roles. Avoid adding admin auth unless necessary for development; do not ship hidden mutable policy UI publicly.

---

# 6. Web application controls

## SEC-WEB-001
Production must use HTTPS.

## SEC-WEB-002
Use framework/host security headers. Strong baseline where compatible:

- Content-Security-Policy;
- Strict-Transport-Security;
- X-Content-Type-Options;
- Referrer-Policy;
- frame-ancestors / equivalent clickjacking protection;
- Permissions-Policy as appropriate.

## SEC-WEB-003
Never interpolate model/user text as raw HTML. Render escaped text or sanitized allowed markup.

## SEC-WEB-004
No secrets in client bundles or source maps.

## SEC-WEB-005
Pin/lock dependencies and scan for reachable critical/high vulnerabilities before submission.

## SEC-WEB-006
External official links use an allowlisted source registry rather than arbitrary model-generated URL.

## SEC-WEB-007
If a server endpoint accepts scenario/action IDs, validate against allowlisted fixtures/actions. Do not trust arbitrary mutation payloads.

---

# 7. AI endpoint security

- server-side credential;
- request body size limits;
- schema validation;
- allowlisted request types;
- synthetic-data assertion;
- rate limit by IP/session as reasonable;
- timeout and max-output limit;
- no tool permissions to call government websites;
- no arbitrary URL fetch tool;
- no prompt/response logs with content in production unless explicitly needed and safe.

---

# 8. Real-data guardrails

P0 strongest control: **there is nowhere to enter it.**

If P1 free text is added:

1. Place inline warning before the input: `Use the fictional sample only. Do not paste real IDs or personal details.`
2. Client-side pattern scan for likely Aadhaar/PAN/UAN/phone/bank-like data.
3. If matched, block submission and offer to load a sample remark.
4. Do not attempt to “mask and continue” automatically for highly sensitive patterns unless thoroughly tested; safest demo behavior is refusal.
5. Server repeats validation because client controls can be bypassed.

---

# 9. Source integrity / policy staleness

A wrong rule can be more harmful than a code bug.

Every source-backed rule includes:

- source ID;
- official publisher;
- URL;
- last checked date;
- proposition used;
- evidence status;
- rule version.

Before recording/submission:

- click every official link;
- verify wording/process has not materially changed;
- if it changed, update rule/test/copy together;
- never silently keep a stale correction recommendation.

---

# 10. Accessibility as trust/security

Accessibility failures can cause citizens to misread a blocker or action. Treat these as correctness issues:

- status must not be color-only;
- focus must not jump during simulation;
- external link must be announced;
- dialog confirmation must state `simulation only`;
- screen-reader text must distinguish original vs derived/transliterated values;
- errors must not disappear before they can be read.

---

# 11. Logging policy

## Production log allowlist

Allowed examples:

```text
scenario_started {scenario_id}
analysis_completed {scenario_id, rule_version, readiness}
simulation_applied {scenario_id, action_id}
ai_explanation_status {success|timeout|schema_fail|grounding_fail}
client_error {error_code, route, build_sha}
```

Not allowed:

- full synthetic name strings unless strictly local debug;
- free-form rejection text;
- secrets;
- real user identifiers;
- browser storage dumps.

Even synthetic person data should not become a lazy logging habit.

---

# 12. Authentication and authorization

P0 citizen experience SHOULD NOT require login.

If existing app architecture forces a login, replace with obvious mock persona access or bypass for reviewer routes. The official brief allows mock consumer credentials but reviewer friction should be minimized.

Do not build Entra/OAuth/government SSO for this prototype merely to show security sophistication.

---

# 13. Persistence choice

SQLite/local persistence is sufficient for:

- source/rule registry;
- fixtures;
- event journal;
- deterministic replay.

A transactional outbox/event broker is not required because P0 has no distributed production write workflow. If an existing outbox is already stable, it may remain internal; do not spend pivot time integrating Kafka.

---

# 14. Trust disclosures — exact minimum copy

## Global

`Independent hackathon prototype · Fictional data · Does not connect to government systems`

## Simulation

`This changes only the fictional case in this demo. No official record will be updated.`

## Final action

`Processes can change. Check the linked official service before acting.`

## AI

`AI may help explain the result. The blocker and correction simulation are calculated from deterministic demo rules.`

---

# 15. Security release gate

Before submission:

- [ ] no real-sensitive input path;
- [ ] no exposed API keys;
- [ ] no live government API call;
- [ ] official external URLs verified;
- [ ] CSP/headers reviewed;
- [ ] dependency security scan reviewed;
- [ ] AI endpoint rate/size/time limits configured;
- [ ] production logs inspected for content leakage;
- [ ] reset clears local scenario state;
- [ ] prototype disclosure visible on every relevant route;
- [ ] simulation language cannot reasonably be mistaken for a real government update.
