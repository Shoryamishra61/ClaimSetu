# Two-minute video script — ClaimPath

Target length: ~1:50. Record at desktop width (1280×720 or larger). Every cue below names the exact click. No segment lists the tech stack.

## 0:00–0:10 — Problem

Screen: <https://shoryamishra61.github.io/handover29c/> (do not scroll past the first screen).

> "A worker changes jobs and tries to move his old PF balance. The portal says: previous PF account not available to transfer. The only visible clue is a name variation — and it points to the wrong fix. This is ClaimPath, a pre-flight check for one EPFO transfer dead end."

## 0:10–0:30 — Diagnose

Click: **Find what blocks the transfer**.

> "One click runs a versioned rule set over the case. The result: the name is not the blocker — the service history is. The previous employment has no Date of Exit, which EPFO's own guidance requires before an online transfer. ClaimPath also says what NOT to change, so the worker doesn't waste a correction cycle on the name."

## 0:30–0:40 — Evidence

Click: **View technical evidence**.

> "Every determination is traceable: the rule ID, the fictional values it used, and the EPFO FAQ that documents the prerequisite. Nothing is inferred silently."

## 0:40–0:55 — Simulate

Click: **Simulate minimum fix**.

> "The worker can test the minimum correction before touching the real portal. Only the fictional exit date changes — the name stays untouched — and the case recomputes to: prerequisite met. Then ClaimPath hands over to the real journey: the official Member Portal Mark Exit route, the two-month condition, and when to retry the transfer."

Point at: **Manage → Mark Exit** list item and the UMANG fallback link (do not click away from the app).

## 0:55–1:05 — The core insight

Return to the diagnosis screen (click **Undo last simulation**, then narrate over it).

> "The current portal reports a status. ClaimPath reports the gap between 'case closed' and 'the thing the citizen asked for actually became possible' — and makes the next action explicit. That is the whole product."

## 1:05–1:35 — Technical decisions

Open in the same tab: <https://shoryamishra61.github.io/handover29c/test-case>

Click: **Load sample now**, then **Run deterministic check**, then **Test proposed Date of Exit**.

> "The same rule engine is exposed as a sandbox: reviewers download a documented fictional JSON contract, edit it, and run the check. On the hosted build it runs through a labelled browser fallback; the same rules ship behind a FastAPI endpoint. The engine is deterministic — no LLM in the decision path — so every reviewer sees identical evidence. Unknown fields and identifier-like names are rejected: the app accepts no Aadhaar, PAN, UAN, OTP or document upload. All records are fictional and labelled as such on every screen; nothing claims an EPFO connection."

## 1:35–1:50 — Closing

Return to <https://shoryamishra61.github.io/handover29c/>.

> "We took one documented EPFO transfer failure — a missing Date of Exit hiding behind a misleading name difference — and made the cause, the non-cause, the evidence and the official next step one path instead of a search problem. The journey runs in Hindi, works at 320 pixels, and needs no login. ClaimPath: check what actually blocks the transfer, before you correct the wrong thing."

## Recording checklist

- [ ] Total length under 2:00 (aim 1:50)
- [ ] No government seals, logos, or wordmarks visible other than the app's own "CP" mark
- [ ] Every click lands on the first try (rehearse once)
- [ ] Cursor visible and deliberate
- [ ] Audio: no background music over narration
