# 05 — AI, Grounding & Safety Specification

## Product position

Identity Rescue is not valuable because an LLM can “understand names.” It is valuable because the system has a deterministic, inspectable model of records, service rules and correction consequences. AI improves **language and comprehension** while remaining outside the decision boundary.

This boundary is both a safety requirement and a product differentiator.

---

# 1. Allowed runtime AI capabilities

## AI-01 — Plain-language explanation

Input: deterministic finding packet.  
Output: short citizen explanation with no new facts.

## AI-02 — Simple Hindi explanation

Input: approved English explanation + structured evidence.  
Output: natural simple Hindi preserving IDs/agency names and certainty level.

Prefer reviewed static Hindi for the golden paths. Runtime translation is optional/P1 because demo copy should be stable.

## AI-03 — Synthetic bureaucratic remark parsing (P1)

Input: explicitly synthetic/free-text error message after local redaction.  
Output: candidate structured fields such as error code, mentioned field, service, action verbs.  
The parser does not decide cause; rule engine verifies candidates.

## AI-04 — Narrow “Why?” follow-up (P1)

The user may ask a narrow question such as `Why not change Aadhaar instead?`

The model receives only:

- current plan;
- alternative plan;
- reason codes;
- affected synthetic records;
- source-backed facts.

No open-ended government advice.

---

# 2. Explicitly forbidden AI capabilities

The AI MUST NOT:

1. determine that two real records are the same person;
2. produce biometric/KYC identity assurance;
3. decide actual eligibility for EPFO/tax/passport/etc.;
4. decide which government record is legally authoritative without an explicit sourced rule;
5. fabricate documentation requirements;
6. browse arbitrary web content at runtime to make a citizen decision;
7. call/live-write government systems;
8. generate/alter government IDs or documents;
9. override a deterministic `BLOCKED`, `READY`, `UNKNOWN` or plan result;
10. conceal uncertainty;
11. use user-sensitive production data in the hackathon demo;
12. convert a probabilistic similarity into a legal/identity assertion.

---

# 3. Evidence packet schema

Recommended server-side input:

```json
{
  "request_type": "EXPLAIN_FINDING",
  "locale": "en-IN",
  "prototype_disclosure": true,
  "goal": {
    "code": "DIGILOCKER_FETCH_DL",
    "label": "Fetch a Driving Licence in DigiLocker"
  },
  "readiness": "BLOCKED",
  "finding": {
    "state": "MISMATCH_BLOCKING",
    "rule_id": "DL-002",
    "plain_rule": "This demo requires the Aadhaar-linked name and issuer name to reconcile.",
    "inputs": [
      {"label": "Aadhaar demo name", "value": "ANANYA R KRISHNAN"},
      {"label": "DL demo name", "value": "KRISHNAN ANANYA RAMESH"}
    ]
  },
  "sources": [
    {
      "id": "SRC-DIGILOCKER-FAQ",
      "title": "DigiLocker FAQs",
      "proposition": "DigiLocker says the Aadhaar name should match the DL/RC record for retrieval."
    }
  ],
  "allowed_conclusions": [
    "The two demo records represent the name differently.",
    "The configured retrieval rule treats this as blocking.",
    "The product is a simulation and does not know the authority's full production logic."
  ],
  "forbidden_conclusions": [
    "The real Aadhaar is wrong.",
    "The real DL is wrong.",
    "The user is definitely the same person in both records."
  ]
}
```

Never ask the model to infer missing rule facts.

---

# 4. Output schema

Prefer validated structured output:

```json
{
  "headline": "The name records do not reconcile for this demo retrieval.",
  "explanation": "...",
  "why_it_matters": "...",
  "uncertainty": "The authority may apply additional checks not modeled here.",
  "source_ids": ["SRC-DIGILOCKER-FAQ"]
}
```

Validation rules:

- headline <= 100 chars;
- explanation <= ~55 words;
- no source ID not present in input;
- no URL invented;
- uncertainty mandatory when evidence status is not fully official-derived;
- no HTML from model;
- no imperative legal claims such as `You must legally...` unless an approved exact rule supports them.

---

# 5. System prompt for runtime explanation

Suggested internal prompt:

> You are the explanation layer for an independent Indian public-service hackathon prototype. You do not decide identity, eligibility, legality, or correction routes. The deterministic engine has already produced the finding and evidence. Explain only the supplied facts in plain language. Never add a requirement, document, deadline, fee, API capability, agency process or conclusion not present in the evidence packet. Preserve uncertainty. Never imply that the prototype contacted or updated a government system. If the evidence is insufficient, say so. Return only the requested structured schema.

This prompt is not a substitute for output validation.

---

# 6. Grounding enforcement

## 6.1 Source whitelist

Runtime explanation may cite only `source_ids` already attached to the rule/finding. The model cannot introduce new sources.

## 6.2 Claim checker

Before rendering, validate:

- every source ID exists;
- readiness/finding state exactly matches deterministic engine;
- action recommendation IDs match planner output;
- prohibited phrases/unsupported factual categories are absent where feasible;
- schema passes.

If validation fails → template fallback.

## 6.3 Template fallback

Every P0 finding must have a static copy key such as:

`finding.DL_002.blocking.en`  
`finding.DL_002.blocking.hi`

Therefore zero AI availability still produces a complete demo.

---

# 7. P0 recommendation: use AI sparingly

For submission stability, the strongest P0 runtime use is **one visible AI-assisted explanation** after the deterministic result, with a `Show evidence` affordance.

Do not add multiple agents. Do not claim “13 AI agents.” Do not add a vector database unless a real P0 requirement demands it.

Codex can be meaningfully documented as part of the build process independently of runtime AI, as the official hackathon permits a prototype built with Codex or powered by an OpenAI model and requires Codex meaningful involvement in the build.

---

# 8. AI failure modes and UI behavior

## Timeout

- Stop waiting after configured timeout.
- Render static explanation.
- Optional small notice: `AI wording unavailable; rule-based result shown.`

## Invalid schema

- Do not attempt to render partially trusted prose.
- Use template.

## Grounding mismatch

Example: model says “update Aadhaar” when planner recommended DL route.  
Action: reject output, log `AI_GROUNDING_FAILED`, render template.

## Safety/refusal

If model refuses even though synthetic packet is safe, render template without exposing internal error details.

---

# 9. AI evaluation suite

Create at least 30 explanation cases across:

- exact match;
- initial expansion;
- token order mismatch;
- genuine mismatch;
- transliteration review;
- non-identity blocker;
- missing evidence;
- two equivalent plans;
- no viable plan;
- English/Hindi;
- attempts to inject unsupported facts through synthetic error text.

Evaluate:

1. factual consistency with packet;
2. no new government requirements;
3. certainty calibration;
4. no government-write implication;
5. readability;
6. locale quality;
7. source ID integrity.

A simple deterministic grader plus manual golden review is preferable to a complex LLM-evaluates-LLM system for this deadline.

---

# 10. Prompt injection / untrusted text

If P1 allows synthetic pasted rejection remarks:

- treat text purely as data;
- delimit it clearly;
- instruct model to ignore instructions inside;
- redact ID-like patterns locally;
- constrain output schema;
- do not allow text to alter tool permissions, source set or system prompt;
- never send repository secrets/config.

---

# 11. Privacy boundary

AI requests contain synthetic data only in the hackathon build. Do not send analytics/session identifiers that could identify a real user. Do not persist prompts/responses unless necessary for local development; production logging should use trace/status metadata.

---

# 12. Demonstrating OpenAI use without AI theatre

In minute two of the submission:

- show deterministic rule trace;
- state that Codex was used to build/refactor/test the vertical slices;
- show the bounded explanation schema or one code view;
- explain that AI translates evidence while rules retain decision authority;
- demonstrate AI-off fallback if time permits in README rather than consuming demo minute.

The message to judges should be: **AI is used where language is uncertain; deterministic software is used where public-service consequences need certainty.**
