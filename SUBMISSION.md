# Submission copy

## Title

ClaimPath — Find what blocks an old PF transfer

## Summary

ClaimPath redesigns one EPFO dead end: a worker changes jobs, tries to transfer an old PF balance, and the previous account is unavailable. A visible name variation can send the worker toward the wrong correction, while the actual prerequisite may be hidden in service history.

The working prototype opens a fictional case, evaluates a small versioned rule set, and shows that Ravi's missing Date of Exit—not the visible name difference—blocks this transfer scenario. It traces the finding to current EPFO guidance, tells Ravi what not to change, simulates only the fictional exit-date correction, recomputes the case, and then gives the official Manage → Mark Exit path and retry condition.

The app accepts no Aadhaar, PAN, UAN, OTP, password or identity-document upload. A separate sandbox lets reviewers download, edit and upload a strict fictional JSON sample, run the FastAPI rule endpoint or labelled browser fallback, simulate the proposed correction and export the result. Unknown fields and identifier-like names are rejected. The core runs deterministically without an LLM.

All citizen records, the name relation, the simulated correction and the “prerequisite met” result are fictional. ClaimPath does not connect to EPFO, update an account or guarantee transfer eligibility. Codex was used to challenge the original cross-service thesis, verify sources, narrow the product, refactor the journey, update rules and tests, and prepare the evidence-linked submission.

## Links

- Live app: <https://shoryamishra61.github.io/handover29c/>
- Fictional-data sandbox: <https://shoryamishra61.github.io/handover29c/test-case>
- Source: <https://github.com/Shoryamishra61/handover29c/tree/final-night-epfo-transfer>
