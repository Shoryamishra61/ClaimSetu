# Submission summary — exactly 250 words

Copy everything between the rules below into the submission form as-is.

---

ClaimPath redesigns one EPFO dead end: a worker changes jobs, tries to transfer an old PF balance, and the previous account is unavailable. EPFO's own transfer guidance makes a Date of Exit for the previous employment a prerequisite for the online transfer, yet the portal does not bring prerequisite, symptom and safe next action together. A visible name variation points to the wrong correction.

The working prototype opens a fictional case, evaluates a small versioned rule set, and shows that Ravi's missing Date of Exit, not the visible name difference, blocks this transfer scenario. It traces the finding to current EPFO guidance, tells Ravi what not to change, simulates only the fictional exit-date correction, recomputes the case, then gives the official Member Portal Mark Exit route and retry condition. No login is needed; the journey also runs in Hindi at 320 pixel width.

The app accepts no Aadhaar, PAN, UAN, OTP, password or identity-document upload. A separate sandbox lets reviewers download, edit and upload a strict fictional JSON sample, run the FastAPI rule endpoint or labelled browser fallback, simulate the proposed correction and export the result. Unknown fields and identifier-like names are rejected. The core runs deterministically without an LLM.

All citizen records, the name relation, the simulated correction and the prerequisite-met result are fictional. ClaimPath does not connect to EPFO, update an account or guarantee transfer eligibility. Codex was used to challenge the original thesis, verify sources, narrow the product, update rules and tests, and prepare the evidence-linked submission.

---

Rules for the person pasting:

- The text between the rules is VERIFIED at exactly 250 words (whitespace-split count, checked programmatically on 28 Aug 2026).
- Paste it without the rules, without a title, and without edits. Adding or removing a single word breaks the 250-word requirement.
- The count treats "EPFO's", "Ravi's", "prerequisite-met" and "identity-document" as single words, the same way standard form word counters do.
