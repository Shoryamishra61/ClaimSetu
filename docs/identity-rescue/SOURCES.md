# Research Sources & Evidence Registry

**Checked:** 22 August 2026 unless noted.  
**Policy:** Prefer current official sources for normative product claims. Community sources may support problem discovery but do not define rules. Recheck P0 official pages before final recording/submission.

---

# A. Hackathon — normative

## SRC-HACK-001 — Builder Brief

**Publisher:** Build What Moves India  
**URL:** https://buildwhatmovesindia.com/brief  
**Relevant propositions:**

- choose one real problem on an Indian public-service website/digital service;
- build a simpler, clearer, more useful complete citizen journey;
- reviewers test citizen experience, not admin panel;
- design for mobile, slower connections and limited digital experience;
- use mock/synthetic data for personal information/OTPs/payments/government systems;
- do not access live systems/private APIs;
- disclose what works vs what is mocked;
- judging: problem, working build, usability, product thinking, end-to-end thinking, honesty;
- submission deadline shown: 28 Aug 2026, 8:00 PM IST;
- video <= 2 minutes; first minute citizen, second minute build/choices;
- project summary <250 words.

**Used by:** master scope, demo/submission requirements.

## SRC-HACK-002 — FAQ

**Publisher:** Build What Moves India  
**URL:** https://buildwhatmovesindia.com/faq  
**Relevant propositions:**

- can solve one specific problem within a public-service website or digital journey;
- main journey must be working prototype;
- every feature demoed must work;
- Codex meaningful involvement required;
- no live government connection unless approved sandbox;
- no real sensitive user data;
- do not use official logos to imply endorsement;
- deadline/submission details.

---

# B. Indian government UX/accessibility

## SRC-GIGW-001 — GIGW 3.0 Scope and Objective

**Publisher:** Guidelines for Indian Government Websites and Apps / NIC-MeitY ecosystem  
**URL:** https://guidelines.india.gov.in/scope-and-objective/  
**Relevant propositions:**

- Indian government websites/apps should be user-centric, user-friendly and secure;
- focus on usability, user-centricity and universal accessibility;
- GIGW references WCAG 2.1, RPwD Act and Indian web realities.

## SRC-GIGW-002 — New Features of GIGW 3.0

**URL:** https://guidelines.india.gov.in/new-features-of-gigw-3-0/  
**Relevant proposition:** GIGW 3.0 incorporates WCAG 2.1 Level AA and additional mobile/cognitive/low-vision accessibility requirements; cybersecurity chapter included.

## SRC-GIGW-003 — Accessibility Guidelines and Attributes

**URL:** https://guidelines.india.gov.in/accessibility-guidelines-and-attributes/  
**Relevant propositions:**

- reflow at width equivalent to 320 CSS px for normal content;
- programmatically determinable UI names/roles/states;
- contrast guidance;
- accessible structure and controls.

## SRC-UX4G-001 — UX4G Handbook

**Publisher:** UX4G  
**URL:** https://www.ux4g.gov.in/assets/img/pdf/UX4G-Handbook.pdf  
**Relevant propositions:** Noto Sans/Indic-script suitability, reusable design tokens and public-service design-system guidance.

## SRC-UX4G-002 — UX4G Brochure / Accessibility Widget

**URL:** https://www.ux4g.gov.in/assets/img/pdf/UX4G-Brochure.pdf  
**Relevant propositions:** accessibility tooling includes text sizing/spacing, dyslexia/ADHD-oriented modes, saturation, text-to-speech, pause animation and other options.

**Product interpretation:** Native semantic accessibility remains mandatory; an accessibility widget is supplemental, not a substitute for accessible implementation.

---

# C. Aadhaar / UIDAI — identity representation

## SRC-UIDAI-001 — Aadhaar Handbook 2026

**Publisher:** UIDAI  
**URL:** https://uidai.gov.in/images/LR_Aadhaar_Handbook_2026.pdf
**Relevant propositions:**

- demographic name updates are supported through documented, proof-dependent processes;
- Aadhaar supports regional-language demographic representations;
- the handbook distinguishes update channels and supporting-document requirements.

**Used by:** demographic-update context and regional-language uncertainty. The exact initial relation in the golden fixture is explicitly synthetic and never inferred from this source.

## SRC-UIDAI-002 — Updating Data on Aadhaar

**URL:** https://uidai.gov.in/en/my-aadhaar/about-your-aadhaar/updating-data-on-aadhaar.html  
**Relevant propositions:** demographic details can require update after life events; authentication failures/false rejects may occur; update modes depend on field/process.

## SRC-UIDAI-003 — Aadhaar Authentication History / Error Codes

**URL:** https://uidai.gov.in/en/contact-support/have-any-question/305-english-uk/faqs/aadhaar-online-services/aadhaar-authentication-history.html  
**Relevant propositions:** error codes include demographic mismatch, address mismatch, biometric mismatch, locked biometrics, invalid OTP and technical conditions.

**Used by:** product principle that “failure” has different causal classes and should not be reduced to identity string mismatch.

## SRC-UIDAI-004 — Local-language address update

**URL:** https://uidai.gov.in/en/922-faqs/aadhaar-online-services/online-address-update-process/11613-can-i-update-my-address-in-my-local-language.html  
**Relevant proposition:** English input may be transliterated to selected regional language, with correction of transliteration available.

---

# D. Income Tax — PAN/Aadhaar mismatch

## SRC-ITD-001 — Link Aadhaar guidance

**Publisher:** Income Tax Department  
**URL:** https://www.incometax.gov.in/iec/foportal/help/all-topics/e-filing-services/link-aadhaar  
**Relevant proposition:** when Aadhaar/PAN linking fails because of mismatch in name/phone/DOB, the citizen is directed to correct details in PAN or Aadhaar so they match.

**Used by:** core problem evidence; correction-routing motivation.

---

# E. DigiLocker — issuer reconciliation

## SRC-DIGI-001 — DigiLocker FAQs

**Publisher:** DigiLocker / NeGD  
**URL:** https://www.digilocker.gov.in/web/about/faq  
**Relevant propositions:**

- issued documents are fetched from issuer sources;
- for DL/RC retrieval, Aadhaar name should match the name in the DL/RC database / National Register;
- generic errors include details not matching issuer data;
- if the DL/RC record does not exist in the National Register, DigiLocker cannot fetch it;
- DigiLocker profile name/DOB derive from Aadhaar in the described flow.

**Used by:** Scenario A rules; non-identity “record absent” edge case.

## SRC-DIGI-002 — DigiLocker Ask Our Experts

**URL:** https://www.digilocker.gov.in/assets/DIGILOCKER%20ASK%20EXPERT.pdf  
**Relevant proposition:** published guidance discusses name-order mismatch between Aadhaar and degree certificates and states document retrieval can fail when names do not match.

**Used by:** evidence that ordering/representation differences are a citizen-facing interoperability issue.

---

# F. EPFO — KYC / multiple blockers

## SRC-EPFO-001 — FAQ on UAN & KYC

**Publisher:** EPFO  
**URL:** https://www.epfindia.gov.in/site_docs/PDFs/Circulars/Y2020-2021/FAQUANKYC.pdf  
**Relevant propositions:**

- name as per Aadhaar and PAN must align appropriately with PF records for KYC;
- name change request can be raised in mismatch situations;
- EPFO workflows include date-of-exit handling and employer/portal actions.

**Used by:** Scenario B identity rule and broader process model.

## SRC-EPFO-002 — Higher Pension FAQ / error table

**URL:** https://www.epfindia.gov.in/site_docs/PDFs/MiscPDFs/Higher_Pension_FAQs_Eng.pdf  
**Relevant propositions:** EPFO documents errors involving names as per UAN/PPO, DOB/name mismatch and member-ID details.

**Used by:** evidence that multiple record relationships can generate distinct failure classes.

**Important prototype note:** Scenario B’s exact service-history predicate is `PROTOTYPE_SIMULATION`; do not present it as EPFO’s undocumented production claim engine.

---

# G. Passport Seva — name structures

## SRC-PASS-001 — Passport Application Form Instructions

**Publisher:** Passport Seva / Ministry of External Affairs  
**URL:** https://passportindia.gov.in/AppOnlineProject/pdf/ApplicationformInstructionBooklet-V3.0.pdf  
**Relevant propositions:**

- citizens without surname can leave surname blank and put full name in given name;
- initials should be expanded in passport application;
- surnames may contain multiple words;
- titles/honorifics should not be part of the name.

**Used by:** name data model must not enforce first/last structure.

## SRC-PASS-002 — Passport Manual

**URL:** https://www.passportindia.gov.in/AppOnlineProject/pdf/Passport_Manual_16_Chapters_to_be_disclosed.pdf  
**Relevant proposition:** manual recognizes regional name practices involving father-name initials/last-name patterns and treats name changes with context-specific procedures.

---

# H. Privacy / DPDP

## SRC-DPDP-001 — Digital Personal Data Protection Rules, 2025

**Publisher:** MeitY  
**Landing page:** https://www.meity.gov.in/documents/act-and-policies/digital-personal-data-protection-rules-2025-gDOxUjMtQWa  
**Gazette PDF:** https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf  
**Relevant proposition:** final Rules were notified 14 Nov 2025 with phased commencement; not all substantive rules came into force simultaneously.

**Used by:** do not make blanket “DPDP compliant” claims; design with data minimization/transparency principles and obtain legal review for production.

---

# I. Supporting uploaded research

The supplied project research note is valuable for:

- DPI modularity / thin interfaces;
- progressive disclosure;
- plain-language error handling;
- system-status visibility;
- GIGW/UX4G accessibility direction;
- privacy-by-design concepts.

This product package intentionally rejects its implication that Saga, transactional outbox, idempotent messaging, SEDA/microservices are automatically necessary for this prototype. Those are valid architectural patterns in distributed systems but would be premature here without a distributed production workflow.

---

# J. Evidence-writing rules

When adding a source:

1. Use official page/PDF if available.
2. Record exact proposition used, not a broad summary.
3. Do not quote long passages in product UI.
4. Record checked date.
5. Link the rule IDs that depend on it.
6. If source only establishes a general dependency, label the exact demo predicate as interpreted/simulated.
7. If a current source contradicts an older source, prefer current official guidance and update fixtures/tests.
8. Community posts can inform UX/problem discovery, never silently become normative requirements.
