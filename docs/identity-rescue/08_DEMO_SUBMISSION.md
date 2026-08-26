# 08 — Demo, Storytelling & Submission Package

## Official constraints used

Checked against the Build What Moves India Builder Brief/FAQ on 22 August 2026:

- submission deadline: **28 August 2026, 8:00 PM IST**;
- live public browser link;
- one video, **no longer than two minutes**;
- first minute: citizen demo;
- second minute: how it was built and why choices were made;
- project summary under 250 words;
- use synthetic/mock data for sensitive/government dependencies;
- Codex must be meaningfully involved;
- reviewers test citizen experience, not an admin panel.

Recheck the official site immediately before submission in case rules change.

---

# 1. Reviewer landing strategy

The deployed root URL should be the product, not a developer README or login wall.

Above fold:

> **Every portal tells you what failed. See what to fix first.**

Then 3 fictional case cards.

Recommended small reviewer cue:

`For the 60-second demo, start with “I can’t fetch my Driving Licence.”`

Do not force it if that feels artificial; the first card can naturally be the preferred path.

---

# 2. Two-minute video script — timing blueprint

Do not memorize every word. Memorize the transitions and citizen outcome.

## 0:00–0:10 — premise + enter

Voice:

> `In India, the same person's name can be represented differently across Aadhaar, PAN, DigiLocker, DL or PF records. When a service says “details don't match,” the citizen has to figure out which record actually matters. This is Identity Rescue.`

Action: click `I can't fetch my Driving Licence`.

## 0:10–0:22 — diagnosis

Show fictional profile and immediate result.

Voice:

> `This is entirely fictional data. The pre-flight shows one blocking edge: the Aadhaar-linked name and the mock DL issuer record don't reconcile for this retrieval rule.`

Click `Show evidence` briefly.

## 0:22–0:36 — why/correction comparison

Voice:

> `Instead of a generic mismatch error, it shows exactly what differs, why this service cares, and the source behind that rule. More importantly, it compares correction paths rather than telling the citizen to randomly edit Aadhaar.`

Click comparison.

## 0:36–0:50 — simulation “aha”

Voice:

> `For this fictional case, the minimum-impact route is this issuer-record correction. I can simulate it before doing anything real.`

Click simulate. Show blocked → ready.

## 0:50–0:59 — handoff

Voice:

> `The system rechecks downstream dependencies, shows what is now ready, what still differs but doesn't matter, and gives the exact official next action. No government system was contacted.`

Transition.

## 1:00–1:14 — product-thinking proof

Open Scenario B or show prepared split-screen/code only if navigation is instant.

Voice:

> `The core is not fuzzy name matching. In our EPFO case, a visible name difference is deliberately *not* the blocker—the service-history condition is. That prevents the product from giving confident but wrong identity advice.`

## 1:14–1:32 — architecture

Show concise architecture diagram/code view:

`synthetic adapters → normalization → deterministic rules → correction planner → simulation → evidence`.

Voice:

> `All decisions are deterministic and source-traceable. The planner minimizes citizen effort, downstream breakage and uncertainty. Government integrations are simulated behind adapters, so the prototype is safe and testable.`

## 1:32–1:45 — OpenAI/Codex

Voice:

> `Codex was used throughout the pivot to refactor the existing foundation, implement the rule engine, tests and accessible UI. An OpenAI model is bounded to plain-language explanation: it receives the deterministic evidence packet, cannot change readiness, and falls back to static copy if unavailable.`

Show evidence schema/test rather than chat UI.

## 1:45–1:57 — India-first UX

Voice:

> `The experience is mobile-first, English and simple Hindi, WCAG/GIGW-aligned, and built for Indian name structures—initials, expanded names, token order, no-surname cases and local-script transliteration without pretending fuzzy similarity proves identity.`

## 1:57–2:00 — close

> `Every portal sees one record. Identity Rescue helps the citizen see the journey.`

Stop before 2:00. Aim recording around 1:55–1:58 to avoid platform rounding.

---

# 3. What not to show in the video

- test count;
- Docker terminal unless it proves something essential;
- long architecture poster;
- database schema scroll;
- admin tooling;
- AI chat conversation;
- every scenario end-to-end;
- every accessibility setting;
- repo folder tour;
- speculative future integrations.

The first minute must remain a citizen transformation.

---

# 4. Project summary — under 250 words

## Submission-ready draft

**Identity Rescue** is an independent prototype for a common failure across Indian public services: the same citizen detail can be represented differently across Aadhaar, PAN, DigiLocker, Driving Licence, EPFO and other records, while the final portal only says that the details do not match.

Instead of asking citizens to guess which database to edit, Identity Rescue starts with their goal. Using fictional records, it reconstructs only the dependencies relevant to that task, identifies the causal blocker, shows the exact evidence and source behind the rule, compares correction paths, and lets the citizen simulate the minimum-impact change before taking any real action. It can also identify when a visible identity difference is *not* the reason a service is blocked.

The prototype uses deterministic, versioned rules for compatibility, readiness and correction planning. An OpenAI model is bounded to plain-language explanation and cannot change the underlying decision; the complete journey still works if AI is unavailable. Government systems and sensitive data are fully mocked—no real Aadhaar, PAN, UAN, OTP or private API is used.

The interface is mobile-first, accessible, English/Hindi-ready, and designed around Indian naming realities such as initials, expanded names, token ordering, absent surnames and transliteration. The result is not another government dashboard: it is a pre-flight debugger that tells citizens what actually blocks their task, what not to change, and where to go next officially.

---

# 5. Architecture slide/view for minute two

Keep to six boxes:

```text
[Fictional Citizen Case]
          ↓
[Synthetic Service Adapters]
          ↓
[Normalizer + Evidence-Preserving Record Model]
          ↓
[Deterministic Rules + Readiness]
          ↓
[Correction Planner + Simulation]
          ↓
[Citizen Explanation + Official Handoff]

Optional sidecar:
[OpenAI Explanation Layer]
  reads evidence only; cannot mutate decisions
```

Do not show Kafka/Saga/outbox if not used by the visible product.

---

# 6. README/reviewer section recommended in repository

Include:

1. One-sentence problem.
2. Live demo URL.
3. `Use fictional case A first`.
4. Prototype limitations.
5. No live government integration.
6. OpenAI/Codex usage.
7. Architecture.
8. How to run locally.
9. How to run tests.
10. Official source list.

---

# 7. Submission checklist

## Live link

- [ ] public/incognito works;
- [ ] no auth permission screen;
- [ ] HTTPS;
- [ ] mobile works;
- [ ] all golden scenarios load;
- [ ] official external links work;
- [ ] no dev banners/errors;
- [ ] no real secrets in bundle.

## Video

- [ ] <= 2:00;
- [ ] first minute citizen journey;
- [ ] second minute build/product choices;
- [ ] Codex/OpenAI role clearly stated;
- [ ] mocks/limitations stated;
- [ ] captions if possible;
- [ ] cursor/zoom readable;
- [ ] no dead time;
- [ ] public link works without permission.

## Summary

- [ ] < 250 words;
- [ ] explains real problem;
- [ ] explains why solution is better;
- [ ] synthetic/mock disclosure;
- [ ] OpenAI role;
- [ ] no unsupported scale/impact claim.

## Final rules

- [ ] official brief/FAQ rechecked same day;
- [ ] submission email correct;
- [ ] teammate email correct if applicable;
- [ ] every submitted link tested from logged-out/incognito session;
- [ ] submit well before 8:00 PM IST.
