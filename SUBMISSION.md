# Submission copy

## Title

ClaimPath — Fix the record that actually blocks the claim

## Summary

When a provident-fund claim is blocked, a citizen may see several differences across records but cannot tell which one matters. ClaimPath is an independent prototype that turns that confusion into one focused pre-flight journey.

Using Ravi Kumar's bundled fictional case, ClaimPath compares Aadhaar-linked, PAN, EPFO, and service-history facts while preserving their original values and provenance. Its deterministic rules prove that `RAVI K` versus `RAVI KUMAR` is visible but non-causal in this case. The modeled blocker is the missing Date of Exit. A minimum-cost planner selects only that allowlisted correction, then a counterfactual simulation recomputes the entire case and shows the modeled checks moving from blocked to pass.

The editable problem note stays in the browser and cannot influence the result. Long ID-like number sequences are rejected before analysis. No real Aadhaar, PAN, UAN, OTP, payment, document, government API, or official record write is used. Every result distinguishes official-source-derived guidance from prototype simulation logic, and the final state says explicitly that passing modeled checks does not guarantee EPFO approval.

The experience is English/Hindi, responsive, keyboard-oriented, statically deployable, and backed by a versioned FastAPI rules engine. AI is not required and cannot select readiness or a correction.

## Links

- Live app: <https://shoryamishra61.github.io/handover29c/>
- Source: <https://github.com/Shoryamishra61/handover29c/tree/identity-rescue-pivot>
