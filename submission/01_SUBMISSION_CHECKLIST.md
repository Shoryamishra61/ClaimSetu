# Submission checklist — ClaimSetu

Current submission-form deadline: **29 August 2026, 10:00 PM IST**. The form supersedes the older public brief deadline. Freeze rule: after final verification, only genuine bugs get fixed.

## Verified before freeze (28 Aug 2026)

- [x] Live URL works: <https://shoryamishra61.github.io/ClaimSetu/> (HTTP 200)
- [x] HTTPS enabled (GitHub Pages)
- [x] Fresh automated Chromium journey tested with no local state
- [x] Login tested — no login exists; nothing blocks judge access
- [x] Credentials: not applicable (no auth in the product)
- [x] Golden flow complete end-to-end on production: Diagnose → evidence → Simulate → official handoff → Undo → Restart
- [x] Mock data disclosed on every screen ("Independent prototype · Bundled fictional data · No government connection")
- [x] Production console clean: zero JS errors / unhandled rejections across a full interaction pass
- [x] No failed network requests on production load
- [x] Desktop tested (1280×720)
- [x] Narrow viewport tested (320 px: full journey usable; horizontal overflow fixed in final build)
- [x] /test-case sandbox verified on production (load sample → schema validated → deterministic check → proposed fix → PASS/PASS → export)
- [x] Typed citizen flow verified on production (type names/dates → Build my case → same deterministic result; REVIEW, BLOCK→FIX, WAITING and invalid-input states all exercised; zero JS errors)
- [x] Hindi toggle verified on production (no leaked keys, per e2e + manual)
- [x] Refresh test verified (returns to deterministic landing state; no stuck state)
- [x] Backend: 42 pytest tests pass; ruff clean (verified 28 Aug 2026)
- [x] Frontend: 7 vitest tests pass; tsc clean; 6 Playwright e2e tests pass
- [x] Production build + Pages build pass

## Final form actions

- [ ] Use or replace the generated 1:56 video (script: `submission/03_TWO_MINUTE_VIDEO_SCRIPT.md`; keep under 2:00)
- [ ] Paste the 250-word summary (`submission/02_SUBMISSION_SUMMARY_250_WORDS.md`) into the form — copy only the summary body, exactly as written
- [ ] Confirm the registered email is `shoryamishra65@gmail.com`
- [ ] Paste each reviewed value from `submission/08_FORM_FIELDS.md`
- [ ] Submit before 10:00 PM IST on 29 August 2026
