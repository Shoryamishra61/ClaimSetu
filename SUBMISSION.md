# Submission copy

## Title

Identity Rescue — See what to fix first

## Project summary (235 words)

Identity Rescue is an independent prototype for a common failure across Indian public services: the same citizen detail can be represented differently across records, while the final portal only says that details do not match.

Instead of asking citizens to guess which database to edit, Identity Rescue starts with their goal. Using only bundled fictional records, it reconstructs the dependencies relevant to that task, identifies the causal blocker, shows the exact evidence and source behind the rule, compares correction paths, and lets the citizen simulate the minimum-impact change before taking any real action. It can also prove when a visible identity difference is not the reason a service is blocked.

Three working journeys cover a DigiLocker/Driving Licence name-reconciliation failure, an EPFO pre-flight whose causal blocker is service history rather than the visible name variation, and a life-event case where unrelated address data is deliberately left unchanged.

The prototype uses deterministic, versioned rules for compatibility, readiness, planning, and simulation. The complete journey works with AI disabled; any future OpenAI explanation is explicitly non-authoritative and cannot change the decision. Government systems and sensitive data are fully mocked—no real Aadhaar, PAN, UAN, OTP, payment data, private API, or official write is used.

The interface is mobile-first, keyboard accessible, English/Hindi, and designed around Indian naming realities such as initials, token ordering, absent surnames, and multiple-token names. Codex was used throughout specification migration, implementation, testing, accessibility hardening, and Docker verification.

## Links

- Live app: <https://shoryamishra61.github.io/handover29c/>
- Source: <https://github.com/Shoryamishra61/handover29c/tree/identity-rescue-pivot>
- Narrated final video (118 seconds): <https://github.com/Shoryamishra61/handover29c/raw/refs/heads/identity-rescue-pivot/output/video/identity-rescue-final-submission.mp4>
- Supplemental silent walkthrough: <https://github.com/Shoryamishra61/handover29c/raw/refs/heads/identity-rescue-pivot/output/video/identity-rescue-demo.webm>
