# Final-night evidence ledger

Checked 27 August 2026. Incidence is unknown unless explicitly stated; platform reach is not treated as affected population.

| Claim | Evidence | Source type | Date | Confidence | Used in product? | Used in demo? |
|---|---|---|---|---|---|---|
| The challenge requires one real public-service problem, a complete working citizen journey, mobile/slow-network consideration, synthetic data, and explicit mock boundaries. | [Builder Brief](https://buildwhatmovesindia.com/brief), lines/sections “What we want you to build” through “How builds will be judged” | PRIMARY-OFFICIAL | 2026-08-27 | HIGH | Yes | Yes |
| Deadline is 28 Aug 2026, 8:00 PM IST; video is at most two minutes; summary is under 250 words. | [Builder Brief](https://buildwhatmovesindia.com/brief), [FAQ](https://buildwhatmovesindia.com/faq) | PRIMARY-OFFICIAL | 2026-08-27 | HIGH | No | Yes |
| Date of Exit for the previous employment is mandatory for an online PF transfer. | [EPFO FAQ](https://www.epfindia.gov.in/site_en/FAQ.php), FAQ 185 | PRIMARY-OFFICIAL | 2026-08-27 | HIGH | Yes | Yes |
| A member can use Manage → Mark Exit after the required waiting period; EPFO documents OTP, consent and update steps. | [EPFO FAQ](https://www.epfindia.gov.in/site_en/FAQ.php), FAQs 186, 230 and 250 | PRIMARY-OFFICIAL | 2026-08-27 | HIGH | Yes | Yes |
| If the previous Member ID does not appear, missing Date of Exit is one documented cause; after updating it the member retries Form 13. | [EPFO FAQ](https://www.epfindia.gov.in/site_en/FAQ.php), FAQ 253 | PRIMARY-OFFICIAL | 2026-08-27 | HIGH | Yes | Yes |
| Citizens still report being unable to transfer old balances when Date of Exit is absent, including cases where employer closure or portal errors make the normal route fail. | [Recent EPFO user report](https://www.reddit.com/r/EPFO/comments/1vn5l2u/old_pf_account_noida_jurisdiction_date_of_exit/), [recent transfer report](https://www.reddit.com/r/EPFO/comments/1vo14wn/not_able_to_transfer_funds_from_one_account_to/) | PRIMARY-USER | 2026-08-13/14 | MEDIUM | Yes | No |
| Current official help already explains Mark Exit; the residual failure is not absence of instructions, but failure to connect the transfer symptom to the prerequisite and safe next action in one place. | [EPFO FAQ](https://www.epfindia.gov.in/site_en/FAQ.php) plus current product-flow inference | PRIMARY-OFFICIAL + INFERENCE | 2026-08-27 | MEDIUM | Yes | Yes |
| A visible name difference can be irrelevant in the bundled fictional case; the K → Kumar relation is fixture knowledge, not a government rule. | Bundled fictional record relation and deterministic test | ENGINEERING_NECESSITY | 2026-08-27 | HIGH within fixture only | Yes | Yes |
| The prototype does not inspect or alter a real EPFO account and cannot promise transfer approval. | Code boundary, static fixtures, no live adapter tests | ENGINEERING_NECESSITY | 2026-08-27 | HIGH | Yes | Yes |
| GIGW 3.0 incorporates WCAG 2.1 AA direction including mobile accessibility and 320 CSS px reflow. | [GIGW accessibility guidance](https://guidelines.india.gov.in/accessibility-guidelines-and-attributes/) | PRIMARY-OFFICIAL | 2026-08-27 | HIGH | Yes | No |
| DigiLocker mismatch is real, but official help already identifies name matching and issuer-record absence while a safe independent prototype cannot know the live cause without records. | [DigiLocker FAQ](https://www.digilocker.gov.in/web/about/faq) and feasibility analysis | PRIMARY-OFFICIAL + INFERENCE | 2026-08-27 | HIGH/MEDIUM | No | No |

## Judge objective function

1. Make one real citizen failure recognizable without a pitch.
2. Complete the citizen path from failure to a safer next action.
3. Be clearer, more accessible and more useful than the current fragmented experience.
4. Show backend/process thinking through a source-versioned deterministic rule and explicit institutional boundary.
5. Make fictional data, simulation and unverified production outcomes unmistakable.

## Evidence gaps

- No authoritative incidence rate was found for missing Date of Exit blocking PF transfers. Affected population is therefore **unknown**.
- The authenticated Member Portal could not be safely exercised with a real account. The current-screen representation is based on official FAQ descriptions and public user reports, not a live authenticated capture.
- Community reports establish pain and workarounds, not policy.
