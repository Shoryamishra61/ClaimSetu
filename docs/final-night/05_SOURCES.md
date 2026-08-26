# Source registry

Checked 27 August 2026.

| ID | Classification | Source | What it supports | Product rule? |
|---|---|---|---|---|
| HACK-01 | PRIMARY-OFFICIAL | [Build What Moves India — Builder Brief](https://buildwhatmovesindia.com/brief) | Challenge, build, submission and judging requirements; deadline | Scope only |
| HACK-02 | PRIMARY-OFFICIAL | [Build What Moves India — FAQ](https://buildwhatmovesindia.com/faq) | Working-feature, mock-data, live-system and Codex requirements | Scope only |
| EPFO-01 | PRIMARY-OFFICIAL | [EPFO FAQ](https://www.epfindia.gov.in/site_en/FAQ.php) | FAQs 185, 186, 230, 250 and 253: transfer prerequisite, Mark Exit, two-month condition, unavailable prior Member ID | `EPFO-003` |
| EPFO-02 | PRIMARY-OFFICIAL | [EPFO transfer-claim FAQ](https://www.epfindia.gov.in/site_docs/PDFs/Circulars/Y2020-2021/faq_transfer_claim.pdf) | Transfer prerequisites and missing Date of Exit guidance; older corroboration | Supporting |
| EPFO-03 | PRIMARY-OFFICIAL | [EPFO Member Portal](https://unifiedportal-mem.epfindia.gov.in/memberinterface/) | Official handoff destination | Handoff |
| UMANG-01 | PRIMARY-OFFICIAL | [UMANG EPFO services](https://web.umang.gov.in/landing/department/epfo.html) | Alternate official access surface | Fallback handoff |
| USER-01 | PRIMARY-USER | [Old account, missing Date of Exit, closed employer](https://www.reddit.com/r/EPFO/comments/1vn5l2u/old_pf_account_noida_jurisdiction_date_of_exit/) | Current stuck behavior, distance/employer/escalation cost | No |
| USER-02 | PRIMARY-USER | [Previous PF transfer unavailable](https://www.reddit.com/r/EPFO/comments/1vo14wn/not_able_to_transfer_funds_from_one_account_to/) | Current transfer symptom and correction discussion | No |
| DIGI-01 | PRIMARY-OFFICIAL | [DigiLocker FAQ](https://www.digilocker.gov.in/web/about/faq) | Disconfirmed comparator: name matching, issuer absence and generic mismatch guidance already exist | No |
| DIGI-USER-01 | COMMUNITY-ANECDOTE | [DL addition on DigiLocker](https://www.reddit.com/r/hyderabad/comments/1mb5lb6/dl_addition_on_digilocker/) | Multiple causes and workaround behavior; also disconfirms name mismatch as universal cause | No |
| GIGW-01 | PRIMARY-OFFICIAL | [GIGW accessibility guidance](https://guidelines.india.gov.in/accessibility-guidelines-and-attributes/) | Accessibility and reflow direction | Accessibility |

## Source-use rules

- Official sources define rules; user reports establish pain only.
- A source stating a prerequisite does not prove incidence.
- Product copy paraphrases; it does not present ClaimPath as EPFO.
- Any stale, unreachable or contradictory rule must fail closed and be rechecked before a future release.
