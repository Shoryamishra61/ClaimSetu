# Demo walkthrough — ClaimPath golden flow (under 60 seconds)

Backup path if the video is unavailable or a judge asks for the fastest route.

## Product journey (~35 seconds)

1. Open <https://shoryamishra61.github.io/handover29c/>
2. Click **Find what blocks the transfer**
   → "The name is not the blocker. The service history is." / "Date of Exit is missing" / "Do not change the name for this blocker"
3. Click **View technical evidence**
   → rule EPFO-003 v1.0, fictional values, link to the EPFO FAQ that documents the prerequisite
4. Click **Simulate minimum fix**
   → Before "—" / After "2026-05-31" · "The transfer prerequisite is now met." · official **Manage → Mark Exit** steps + retry condition + UMANG fallback
5. Optional: click **Undo last simulation** to show determinism, then **Restart ClaimPath** to reset

## Engine sandbox (~25 seconds)

1. Open <https://shoryamishra61.github.io/handover29c/test-case>
2. Click **Load sample now** → "Schema validated · fictional boundary confirmed"
3. Click **Run deterministic check** → PASS EPFO-001 / BLOCK EPFO-003, both citing SRC-EPFO-FAQ-001
4. Click **Test proposed Date of Exit** → PASS / PASS · **Download result JSON** available

## Edge cases a judge can try safely

- **Refresh** anywhere → returns to the deterministic landing state; nothing breaks
- **हिन्दी** toggle in the header → complete journey in Hindi
- Edit the sample JSON (e.g., remove the name relation or set `date_of_exit`) and re-upload in the sandbox → rules respond deterministically; unknown fields and names containing digits are rejected

## Always true on every screen

"Independent prototype · Bundled fictional data · No government connection · No official record is read or changed."
