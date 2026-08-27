# Demo and submission

## Two-minute storyboard

| Time | Screen/action | Narration purpose |
|---|---|---|
| 0:00–0:05 | Entry: “Ravi cannot move his old PF balance.” | State the citizen task. |
| 0:05–0:13 | Show “Previous PF account not available to transfer” and the visible name difference. | Recreate the failure and likely wrong guess. |
| 0:13–0:25 | Click **Find what blocks the transfer**. | Let the product reveal cause. |
| 0:25–0:36 | “Date of Exit is missing”; “Do not change the name.” | Show causal diagnosis and harm avoided. |
| 0:36–0:45 | Open evidence: EPFO rule, fictional values, current source. | Establish trust and boundary. |
| 0:45–0:56 | Simulate; show `NOT_RECORDED → 2026-05-31`. | Show visible transformation. |
| 0:56–1:00 | Show Manage → Mark Exit and retry condition. | Complete the citizen journey. |
| 1:00–1:18 | Before/after process: search and guessing versus one prerequisite path. | Explain product judgment. |
| 1:18–1:35 | Versioned rule, fictional adapter, static fallback, official boundary. | Demonstrate backend/process thinking. |
| 1:35–1:47 | No AI in decision path; Codex audit/refactor/test role. | Explain truthful OpenAI involvement. |
| 1:47–1:56 | 320 px, Hindi, keyboard, no identifiers, no live integration. | Show India-first and safety choices. |
| 1:56–1:58 | Return to official handoff. | Close on citizen action, under two minutes. |

## Submission summary (194 words)

ClaimPath redesigns one EPFO dead end: a worker changes jobs, tries to transfer an old PF balance, and the previous account is unavailable. A visible name variation can send the worker toward the wrong correction, while the actual prerequisite may be hidden in service history.

The working prototype opens a fictional case, evaluates a small versioned rule set, and shows that Ravi's missing Date of Exit—not the visible name difference—blocks this transfer scenario. It traces the finding to current EPFO guidance, tells Ravi what not to change, simulates only the fictional exit-date correction, recomputes the case, and then gives the official Manage → Mark Exit path and retry condition.

The app accepts no Aadhaar, PAN, UAN, OTP, password or identity-document upload. An optional sandbox lets reviewers download, edit and upload a strict fictional JSON sample, run the FastAPI rule endpoint or labelled browser fallback, simulate the proposed correction and export the result. Unknown fields and numeric names are rejected. The core runs deterministically without an LLM.

All citizen records, the name relation, the simulated correction and the “prerequisite met” result are fictional. ClaimPath does not connect to EPFO, update an account or guarantee transfer eligibility. Codex was used to challenge the original cross-service thesis, verify sources, narrow the product, refactor the journey, update rules and tests, and prepare the evidence-linked submission.

## Reviewer instructions

No login. Open the public URL, click **Find what blocks the transfer**, optionally open evidence, then click **Simulate minimum fix**. The complete path takes under one minute.

For the production-shaped test, open `/test-case`, choose **Load sample now**, run the deterministic check, then test the proposed Date of Exit. Download/edit/re-upload the JSON to exercise review and waiting-period states.

## Limitations to disclose

- One fictional EPFO transfer case, not a general EPFO help system.
- No production incidence claim.
- No live government read/write, identity decision or approval prediction.
- Exceptional cases are handed back to current official guidance.
