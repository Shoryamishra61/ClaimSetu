# 04 — Citizen Scenarios & Deterministic Rulebook

## Purpose

This document defines the synthetic profiles, rule semantics and correction planner behavior that make Identity Rescue credible. It is not a representation of undocumented government matching algorithms. Where a current official source establishes a dependency or correction requirement, the rule is marked `OFFICIAL_SOURCE_DERIVED`. Where the prototype must choose concrete simulation semantics beyond the public source, that portion is marked `PROTOTYPE_SIMULATION`.

---

# 1. Rule-authoring principles

1. **A difference is not a blocker until a service rule says it matters.**
2. **A string similarity score is evidence, not identity.**
3. **Never normalize away information silently.**
4. **Never infer an initial expansion unless the fixture explicitly provides it.**
5. **Never assume token order means first/middle/last across Indian names.**
6. **Never treat Hindi/Latin transliteration as authoritative equivalence.**
7. **Never invent a correction document or official route to make the demo complete.**
8. **If public guidance is broad, make the simulated detail explicit.**
9. **Rules are goal-specific.** A record can be compatible for one service and problematic for another.
10. **Unknown is a valid result.**

---

# 2. Evidence status taxonomy

## OFFICIAL_SOURCE_DERIVED
The public official source directly supports the citizen-facing dependency or action.

Example: DigiLocker FAQ states that the Aadhaar name should match the name in DL/RC database for retrieval.

## OFFICIAL_SOURCE_INTERPRETED
The official source supports the principle but the prototype translates it into a simplified deterministic predicate for demonstration.

## PROTOTYPE_SIMULATION
No claim is made that this exact predicate or path is the authority's production logic. It exists to demonstrate a safer UX/system concept.

## NEEDS_AUTHORITY_VALIDATION
Useful post-hackathon concept not safe to present as current fact.

P0 blockers should prefer the first two statuses and must disclose any simulated part.

---

# 3. Canonical synthetic data model

## 3.1 `SyntheticProfile`

```json
{
  "profile_id": "DEMO-ANANYA-01",
  "display_name": "Ananya R. Krishnan",
  "fictional": true,
  "preferred_locale": "en-IN",
  "known_name_relations": [],
  "records": [],
  "allowed_actions": [],
  "golden_expectations": {}
}
```

## 3.2 `SyntheticRecord`

```json
{
  "record_id": "REC-AADHAAR-ANANYA",
  "authority": "AADHAAR_DEMO",
  "label": "Aadhaar demo record",
  "fields": {
    "name": {
      "original": "ANANYA R KRISHNAN",
      "script": "Latn",
      "locale": "en-IN"
    },
    "dob": { "original": "1998-02-14" }
  },
  "fixture_version": "1.0"
}
```

Use obvious demo labels and identifiers. Do not create realistic Aadhaar/PAN/UAN numbers.

---

# 4. Name comparison model

## 4.1 Derived representations

For comparison only, the engine may derive:

- Unicode-normalized form;
- case-folded form;
- whitespace-collapsed form;
- punctuation-separated tokens;
- honorific-stripped form when source/rule permits;
- token multiset/order;
- initial tokens;
- controlled expansion mapping;
- controlled transliteration mapping.

The UI always retains the original value.

## 4.2 Example classification

Given:

`A: ANANYA R KRISHNAN`  
`B: ANANYA RAMESH KRISHNAN`

The engine must **not** automatically assert equivalence. It can classify:

- if fixture says `R -> RAMESH`: `MATCH_RULE_COMPATIBLE` only if selected rule permits initial/full-name relation;
- if no expansion metadata: `MISMATCH_REVIEW`;
- if rule requires literal reconciliation: `MISMATCH_BLOCKING`.

## 4.3 Indian-specific structures to cover in tests

- `V VIJAYAN` ↔ `VENKATRAMAN VIJAYAN`;
- `R K SRIVASTAVA` ↔ `RAMESH KUMAR SRIVASTAVA`;
- no surname at all;
- two-word surname such as `ROY CHOUDHARY`;
- patronymic/father-name initial before given name;
- family name first vs last;
- punctuation/no punctuation in initials;
- repeated whitespace;
- honorific mistakenly present;
- Latin/local-script pair with controlled transliteration;
- a genuinely different token that should not be normalized away.

These are test categories, not claims that one normalization rule is valid for every service.

---

# 5. Golden Profile A — Ananya R. Krishnan

## 5.1 Citizen goal

`DIGILOCKER_FETCH_DL`

## 5.2 Narrative

Ananya tries to fetch a Driving Licence in DigiLocker and sees a generic issuer-data mismatch. The prototype demonstrates that the Aadhaar-linked name representation and DL source representation do not reconcile under the **simulated retrieval predicate derived from DigiLocker’s public requirement that names match**.

## 5.3 Synthetic records

### Aadhaar demo

- Name: `ANANYA R KRISHNAN`
- DOB: `1998-02-14`
- Address locality: `CHENNAI`

### DL source demo

- Name: `KRISHNAN ANANYA RAMESH`
- DOB: `1998-02-14`
- Record present in mock National Register: `true`

### PAN demo — secondary downstream record

- Name: `ANANYA RAMESH KRISHNAN`
- DOB: `1998-02-14`

## 5.4 Known synthetic relation

For this fictional profile only:

`R` is a documented initial corresponding to `RAMESH`.

This relation may support explanation/planning. It does not prove that all real records using `R` belong to the same person.

## 5.5 Rules

### RULE DL-001 — issuer record must exist

**Evidence status:** OFFICIAL_SOURCE_DERIVED  
**Public basis:** DigiLocker explains that DL/RC retrieval depends on the record existing in the National Register.

Predicate:

`DL.record_present == true`

Pass: continue.  
Fail: `NON_IDENTITY_BLOCKER` with `record not available in modeled issuer source`.

### RULE DL-002 — name reconciliation required

**Evidence status:** OFFICIAL_SOURCE_INTERPRETED  
**Public basis:** DigiLocker says the Aadhaar name should match the DL/RC database name for retrieval.

Prototype predicate for this scenario:

- exact normalized token sequence: pass;
- controlled initial expansion with same semantic token order after rule-specific canonicalization: pass;
- family-name-first reordering **is not automatically accepted in this mock rule** unless the correction action aligns the issuer display representation;
- otherwise block.

Initial state: `MISMATCH_BLOCKING`.

### RULE DL-003 — DOB

**Evidence status:** PROTOTYPE_SIMULATION  
Predicate: exact ISO date equality for demo.

Initial state: pass.

## 5.6 Findings at start

1. Record existence: exact/pass.
2. DOB: exact/pass.
3. Name: blocking because token representation/order does not pass the configured retrieval rule.

Overall: `BLOCKED`.

## 5.7 Correction actions

### ACT-A1 — simulate aligning DL source representation

From: `KRISHNAN ANANYA RAMESH`  
To: `ANANYA RAMESH KRISHNAN`

- Effort class: `ISSUER / OFFICIAL RECORD CORRECTION`
- Reversible in demo: yes
- Evidence status: `PROTOTYPE_SIMULATION` for exact action mechanics
- Downstream modeled effect: PAN remains compatible; DigiLocker/DL rule passes.
- Planner cost: low-to-medium.

### ACT-A2 — simulate changing Aadhaar representation

From: `ANANYA R KRISHNAN`  
To: `ANANYA RAMESH KRISHNAN`

- Effort class: `AADHAAR UPDATE / REVIEW`
- Reversible in demo: yes
- Public basis: UIDAI supports demographic name update but actual eligibility/document route depends on circumstances.
- Downstream modeled effect: may create a new mismatch with another fictional record in expanded scenario.
- Planner cost: higher because Aadhaar is upstream and broadly reused.

## 5.8 Recommended plan

For the locked fixture, the planner recommends `ACT-A1` because it resolves the selected target with a single modeled change and introduces no new modeled conflict, whereas `ACT-A2` changes the more broadly reused upstream record.

**Critical disclosure:** This is a prototype recommendation based on modeled dependencies; it is not a universal official instruction to change DL rather than Aadhaar.

## 5.9 Expected final state

After `ACT-A1`:

- DL-001 pass
- DL-002 pass
- DL-003 pass
- readiness: `READY_SIMULATION`

Citizen copy:

> `This fictional case now passes the rules we model for DL retrieval. No government record was changed.`

---

# 6. Golden Profile B — Arvind N. Iyer

## 6.1 Citizen goal

`EPFO_KYC_PREFLIGHT`

## 6.2 Narrative

Arvind sees a visible variation across Aadhaar/PAN/PF name representations and assumes that must be why the PF task fails. The real simulated blocker is a service-history condition. The product proves it can reject an attractive but wrong explanation.

## 6.3 Synthetic records

### Aadhaar demo

- Name: `ARVIND N IYER`
- DOB: `1989-07-11`

### PAN demo

- Name: `ARVIND NARAYAN IYER`
- DOB: `1989-07-11`

### EPFO member demo

- Name: `ARVIND N IYER`
- DOB: `1989-07-11`
- Aadhaar-linked: `true`
- PAN-linked: `true`
- Date of exit: `2026-08-31`
- Last contribution month: `2026-07`
- Target claim attempt date: `2026-08-20`

## 6.4 Known synthetic relation

`N -> NARAYAN` for this fictional profile.

## 6.5 Rules

### RULE EPFO-001 — KYC name compatibility

**Evidence status:** OFFICIAL_SOURCE_INTERPRETED  
**Public basis:** EPFO FAQ says name as per Aadhaar/PAN should align appropriately with PF records for KYC.

Prototype predicate:

- exact name or controlled initial expansion relation passes;
- genuine unmatched token causes review/block depending fixture.

Initial state: `MATCH_RULE_COMPATIBLE`.

### RULE EPFO-002 — DOB compatibility

**Evidence status:** OFFICIAL_SOURCE_INTERPRETED  
Initial state: exact pass.

### RULE EPFO-003 — service-history readiness

**Evidence status:** PROTOTYPE_SIMULATION, conceptually informed by EPFO service-history/date-of-exit workflows.  
For this fixture, a future/invalid exit date relative to target attempt prevents the selected simulated readiness condition.

Initial state: `NON_IDENTITY_BLOCKER` / blocking.

## 6.6 Initial findings

- Aadhaar vs PAN name: visibly different but controlled relation → `VARIANT_NON_BLOCKING`.
- PF vs Aadhaar name: exact → pass.
- Service history: blocker.

Overall: `NOT_IDENTITY_ISSUE` or `BLOCKED` with primary cause category `NON_IDENTITY_BLOCKER` depending UI state model.

Recommended citizen wording:

> `The name variation is not what blocks this fictional case. The service-history date is the condition that fails.`

## 6.7 Deliberate anti-error test

If user simulates a name-only alignment action, readiness MUST remain blocked. This test protects the product from “identity mismatch tunnel vision.”

## 6.8 Correct simulation action

`ACT-B1` — set the fictional date-of-exit condition to a valid scenario value.

After action, all modeled conditions pass → `READY_SIMULATION`.

## 6.9 Why this scenario matters

This case is critical to judge trust: the product proves it diagnoses the goal, not merely highlights string differences.

---

# 7. Golden Profile C — Meera Nair

## 7.1 Citizen goal

`LIFE_EVENT_RECONCILIATION`

## 7.2 Narrative

Meera has deliberately completed a legal name change and moved residence. Some fictional records reflect the new details, others still contain the old representation. She wants to know the smallest sequence needed for a selected target service.

The scenario must never imply that marriage or any other life event obligates a person to change name. The user has already chosen/completed the change.

## 7.3 Synthetic records

### Aadhaar demo

- Name: `MEERA NAIR`
- Address: `BENGALURU, KARNATAKA`

### PAN demo

- Name: `MEERA MENON`
- Address field not modeled for selected goal.

### DL demo

- Name: `MEERA MENON`
- Address: `KOCHI, KERALA`

### EPFO demo

- Name: `MEERA NAIR`
- KYC status: `pending review` in fixture

### Supporting synthetic legal-change evidence

- `name_change_evidence_present: true`
- This is a demo metadata flag, not a simulated real gazette number.

## 7.4 Target sub-goal for P0

To keep the demo bounded, P0 selects:

`Make the fictional DL retrieval path consistent with the new chosen name while minimizing other changes.`

## 7.5 Rules

### RULE LIFE-001 — chosen canonical direction

The citizen explicitly declares that `MEERA NAIR` is the desired current legal name in the fictional case. This is user intent, not inferred by the system.

### RULE LIFE-002 — target DL retrieval dependency

Uses the same public-derived DigiLocker/DL reconciliation principle as Scenario A.

### RULE LIFE-003 — planner should not update unrelated address for name-only target

**Evidence status:** PROTOTYPE_PRODUCT_RULE.  
If the selected goal depends only on name, planner should not add an address change merely for global consistency.

This is a key data-minimization/product-thinking rule.

## 7.6 Actions

### ACT-C1 — simulate DL name update to chosen current name

- resolves target name dependency;
- leaves old DL address unchanged because not required for selected target;
- medium effort.

### ACT-C2 — simulate PAN name update

- may be useful for broader reconciliation but not required to satisfy P0 DL target after C1;
- therefore not part of minimum plan.

### ACT-C3 — simulate DL address update

- not required for the P0 goal;
- planner rejects from minimum sequence.

## 7.7 Expected recommendation

Plan: `ACT-C1` only for selected target.

Then final screen says:

> `Your fictional PAN still uses the earlier name and the DL still has the previous address. They are not part of this selected retrieval blocker, so the minimum plan does not change them automatically.`

This explicitly demonstrates **minimum necessary correction**, not “make every database identical.”

---

# 8. Secondary edge fixtures for tests (not primary demo)

## EDGE-01 — No surname

Passport-style name structure where all name content is a given name. Ensure parser does not invent surname.

## EDGE-02 — Multi-token surname

`ANANYA ROY CHOUDHARY` remains intact; no automatic split assumption.

## EDGE-03 — Initial ambiguity

`K S RAVI` has no known expansion metadata. Result must be `REVIEW`, not guessed expansion.

## EDGE-04 — Genuine mismatch

`PRIYA MENON` vs `PRIYA MEHRA`; fuzzy similarity must not mark compatible.

## EDGE-05 — Local script / Latin

Controlled fixture includes `மீரா நாயர்` and `MEERA NAIR` with explicit fixture relation. System may present derived transliteration but labels it.

## EDGE-06 — Transliteration ambiguity

Two plausible Latin transliterations exist. Result = `REVIEW`.

## EDGE-07 — DOB near miss

`1990-08-07` vs `1990-07-08`; never silently interpret locale formatting once canonical dates are parsed from fixtures.

## EDGE-08 — Missing record

No DL record in mock issuer. Diagnose `NON_IDENTITY_BLOCKER`, not name mismatch.

## EDGE-09 — Unknown rule

A new mock agency appears with no rule. Product must say it cannot determine compatibility.

---

# 9. Planner cost model

P0 recommended weights (tunable but versioned):

| Factor | Weight | Meaning |
|---|---:|---|
| Step count | 10 | Penalize unnecessary corrections. |
| Online self-service | 10 | Low effort. |
| Centre/office visit | 30 | Higher citizen effort. |
| Employer/issuer dependency | 35 | External coordination. |
| Uncertain/authority validation needed | 40 | Avoid false certainty. |
| Downstream new blocker | 100 | Strongly avoid. |
| Upstream high-reuse record change | 20 | Prefer narrower changes when equally valid. |
| Irreversible/legally significant action | 100+ | Not recommended without explicit source/validation. |

These weights demonstrate product logic; they are not empirical welfare values.

## 9.1 Planner pseudo-code

```text
input: current synthetic state S, target goal G, allowed actions A
queue <- [S, []]
best <- none

while queue not empty:
  state, plan <- lowest_cost_state(queue)
  evaluation <- evaluate(state, G)

  if evaluation == READY_SIMULATION:
     best <- plan
     break

  for action in allowed_actions(state):
     next <- simulate(state, action)
     if violates_safety_constraint(next): continue
     push(next, plan + action, configured_cost)

return best or NO_PLAN / NEEDS_REVIEW
```

## 9.2 Planner explanation contract

Return structured reasons:

```json
{
  "reason_codes": [
    "RESOLVES_TARGET",
    "ONE_STEP",
    "NO_NEW_MODELED_BLOCKERS",
    "LOWER_UPSTREAM_IMPACT"
  ]
}
```

The UI translates these codes into plain language. AI may improve phrasing but not change reason codes.

---

# 10. Evidence registry requirements

Each source record contains:

- stable source ID;
- title;
- publisher/authority;
- official URL;
- relevant proposition;
- publication/update date if known;
- `last_checked_at`;
- extraction/paraphrase note;
- rules that cite it.

If a source changes materially before submission, affected tests/rules must be reviewed.

---

# 11. Prohibited rule shortcuts

Do not implement any of the following:

- `if similarity > 0.8 => same person`;
- `last token = surname`;
- `first token = first name`;
- `single-letter token => automatically expand from another record`;
- `all dates normalized by guessing DD/MM vs MM/DD`;
- `regional script transliteration => exact identity`;
- `more matching records => majority record is legally correct`;
- `Aadhaar is always the record that should be changed`;
- `Aadhaar is always the record that should never be changed`;
- `AI chooses authoritative record`;
- `all differences should be fixed`.

---

# 12. Citizen-facing confidence model

Avoid numeric confidence unless tied to explicit evidence measurement.

Use:

- **Clear in this demo** — all required rule inputs present and deterministic rule directly fires.
- **Needs official confirmation** — route/process detail not fully supported.
- **Cannot determine** — missing rule/input.

Never use `99% sure this is you`.
