# Judge access — ClaimSetu

## Live URL

<https://shoryamishra61.github.io/ClaimSetu/>

## Credentials

**None required.** The product has no login, signup, OTP, or any identifier input by design. A judge reaches the full golden journey from the landing page with one click. This is a deliberate decision: authentication is not part of the citizen problem being demonstrated, and removing it removes the largest judge-friction risk.

## What a judge should never enter anywhere

Aadhaar, PAN, UAN, OTP, passwords, or real case documents. The app does not accept them; the sandbox rejects unknown fields and names containing digits. Only the fictional sample JSON shipped with the app is a valid sandbox input.

## Hero flow

See `submission/04_DEMO_WALKTHROUGH.md` — under 60 seconds, two clicks to the core insight.

## Mock-data disclosure

All citizen records, names, dates, balances, rule outcomes and the "prerequisite met" result are fictional and labelled as such on every screen. The only real elements are the outbound links to official EPFO/UMANG pages and the EPFO FAQ reference that documents the Date of Exit prerequisite. ClaimSetu never reads or writes a government record.
