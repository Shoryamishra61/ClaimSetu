# 03 — UX/UI Design System & Screen Specification

## Identity Rescue

**Objective:** Make the citizen transformation obvious without turning the product into a dashboard, chatbot, or government-site imitation.

---

# 1. Design thesis

The interface should feel like a **calm diagnostic conversation with visible evidence**, not a government form and not an AI showcase.

The citizen must always know:

1. **What am I trying to do?**
2. **What is blocking it?**
3. **Why do you think that?**
4. **What can I do?**
5. **What happens if I do it?**
6. **Where do I go officially?**

Any component that does not improve one of those questions is suspect.

---

# 2. Anti-slop rules

MUST NOT use:

- generic “AI-powered” hero text;
- glowing orbs, neural-network backgrounds, sparkles around every AI output;
- gradient-heavy SaaS aesthetic;
- 3D India maps;
- random glassmorphism;
- “Welcome back, citizen!” dashboard greetings;
- arbitrary readiness percentages;
- huge KPI cards like `4 mismatches`, `78% identity health` as primary value;
- chatbot as the only navigation;
- fake testimonials;
- stock photos of Indian families;
- cartoon bureaucrats;
- patriotic ornamentation unrelated to usability;
- tricolour palette as default branding;
- Ashoka emblem/government logos implying officiality;
- dense enterprise graph visible before the diagnosis;
- motion that delays task completion.

The product should look designed for India because of **language, naming semantics, mobile behavior, accessibility, content and service context**, not decorative nationalism.

---

# 3. Visual system

## 3.1 Brand character

- trustworthy;
- independent;
- legible;
- restrained;
- modern but not startup-theatrical;
- warm enough to reduce anxiety, not playful about serious citizen problems.

## 3.2 Palette semantics

Define tokens rather than hard-coding agency colors.

- `surface/base` — neutral light background.
- `surface/elevated` — cards.
- `text/primary` — near-black.
- `text/secondary` — muted but WCAG-compliant.
- `status/blocking` — dark red family.
- `status/review` — amber/brown family.
- `status/ready` — green family.
- `status/info` — blue family.
- `border/subtle` — neutral.
- `focus` — high-contrast dedicated ring.

Every status includes text and icon. Do not encode meaning through color alone.

Dark mode is P1 unless already essentially free in the existing design system. Do not sacrifice P0 contrast/testing for it.

## 3.3 Typography

Recommended: **Noto Sans** family with tested Indic-script fallbacks. Rationale: broad Indic support and alignment with UX4G guidance.

Suggested scale:

- Display/hero: 32–40 px desktop, 28–32 mobile; used sparingly.
- H1: 28–32 desktop, 24–28 mobile.
- H2: 22–24.
- H3: 18–20.
- Body: 16–18, line-height 1.5–1.65.
- Supporting: >= 14.
- Avoid all-caps labels for long text/Indic scripts.

Text must survive 200% zoom and longer translated strings.

## 3.4 Spacing

Use 4/8 px base. Preferred content width 720–960 px for reading flows; comparison views can expand to ~1120 px desktop.

Mobile page side padding: 16–20 px.

Do not make cards unnecessarily dense. Critical status sections need whitespace around them.

## 3.5 Radius and elevation

Moderate radii (8–14 px). Use borders more than shadows. Avoid floating-card overload.

---

# 4. Global shell

## Header

Left: simple wordmark `Identity Rescue` or final chosen name.  
Right: language selector + `Sources & limits` + accessibility/settings icon if needed.

Below/within header: compact trust strip:

> **Independent hackathon prototype · Fictional data · No government connection**

On mobile this may collapse to `Demo prototype · Fictional data` with accessible expansion.

## Footer

- About the prototype
- Sources & limitations
- Privacy
- Reset demo
- Built for Build What Moves India (text only; no false partner endorsement beyond accurate hackathon disclosure)

---

# 5. Screen map

```text
/
├─ /case/digilocker-dl
│  ├─ diagnosis
│  ├─ evidence
│  ├─ options
│  ├─ simulation
│  └─ next-action
├─ /case/epfo-preflight
│  └─ same state model
├─ /case/life-event
│  └─ same state model
├─ /sources
├─ /privacy
└─ /about
```

States may be route segments or one stateful route. Browser back/refresh behavior must remain deterministic.

---

# 6. Home screen specification

## Purpose

Get the judge/citizen into meaningful diagnosis with one click.

## Above-the-fold order

1. Independent prototype label.
2. H1:
   **When one government record says one thing and another says something else, what should you fix first?**
3. Short supporting line:
   `Choose a fictional case. We’ll show the blocker, why it matters, and what a safer correction sequence could look like.`
4. Three scenario cards.
5. Small reassurance:
   `No real Aadhaar, PAN, UAN or OTP required.`

## Scenario card anatomy

Icon (descriptive, not agency logo)  
Citizen statement  
One-line value  
Badge: `FICTIONAL CASE`  
CTA: `Try this case`

### Card A
**I can't fetch my Driving Licence**  
`Trace a name mismatch across a mock Aadhaar and DL record.`

### Card B
**My PF/KYC issue isn't getting resolved**  
`See how the system separates an identity difference from the real blocker.`

### Card C
**My name or address changed**  
`Compare which fictional record to update first and what it could affect.`

## What NOT to put on home

- sign-up;
- giant explainer diagram;
- list of supported agencies;
- architecture metrics;
- AI chat input;
- testimonial carousel;
- “identity score.”

---

# 7. Case header

Once inside a case, display:

- breadcrumb/back: `All demo cases`;
- case title as H1;
- one-line citizen goal;
- fictional profile chip;
- current state chip: `Blocked`, `Needs review`, `Ready in simulation`;
- step indicator using meaningful labels rather than `Step 2 of 7` alone.

Suggested labels:

`Understand → Compare → Simulate → Next action`

On mobile use an accessible compact progress list.

---

# 8. Diagnosis screen

This is the most important screen.

## 8.1 First viewport

### Status eyebrow
`SIMULATED PREFLIGHT RESULT`

### H1/result
**Blocked by one record mismatch**

or in EPFO scenario:

**The visible name difference is not the blocker**

### Explanation
Maximum ~2 short sentences before disclosure controls.

Example:

> `The mock Aadhaar record says “ANANYA R KRISHNAN” while the mock DL source says “ANANYA KRISHNAN RAMESH”. This demo retrieval rule requires those name records to reconcile before the document can be fetched.`

### Primary CTA
`Compare ways to fix this`

### Secondary
`Show the evidence`

Do not force the citizen to inspect raw data before understanding the conclusion.

## 8.2 Record comparison component

Desktop: two or three vertical cards, not a dense 10-column table.  
Mobile: stacked records with a sticky field label.

Each record card:

- authority/service name in plain text;
- `FICTIONAL RECORD` badge;
- exact source value;
- field status label;
- expandable details.

Token emphasis must remain readable by screen readers. Visual token highlights are supplemental; accessible text says what differs.

## 8.3 Mismatch language

Use semantic labels:

- `Exact match`
- `Different, but compatible here`
- `Blocks this task`
- `Needs review`
- `Missing required detail`
- `Not related to this failure`

Never use `bad data`, `invalid person`, `wrong identity` unless the source itself establishes invalidity.

---

# 9. Evidence drawer / “Why?”

## Trigger

`Why does this block the task?`

## Drawer content order

1. **Rule in plain language**
2. **Evidence used**
3. **What the product concluded**
4. **Official-source basis**
5. **Prototype limitation**

Example:

**Rule**  
`For this fictional DL retrieval, the name from the Aadhaar-linked DigiLocker profile must reconcile with the issuer record.`

**Evidence**  
`Aadhaar demo name: …`  
`DL demo name: …`

**Source basis**  
`DigiLocker FAQ — Driving Licence / RC retrieval guidance. Checked 22 Aug 2026.`

**Limit**  
`The actual issuer may apply additional checks that this prototype does not model.`

Use an external-link icon/text for official source.

---

# 10. Dependency visualization

## Principle

The graph is a **proof mechanism**, not visual entertainment.

### Desktop

Maximum 4–6 nodes in a P0 view. Example:

`Your goal` → `DigiLocker fetch` → `DL issuer record`  
                    ↑  
             `Aadhaar name`

Red edge = blocking; green = satisfied; amber = review.

### Mobile/text equivalent

Render:

1. `You want to fetch your DL.`
2. `DigiLocker asks the issuer for the record.`
3. `This retrieval uses your Aadhaar-linked name.`
4. `The issuer record represents the name differently.`
5. `In this demo rule, that difference blocks retrieval.`

A screen-reader user should lose zero explanatory meaning by never encountering the SVG visually.

---

# 11. Correction comparison screen

## H1
`Two ways this fictional case could be resolved`

## Recommended card

Use `Recommended in this simulation`, never `Officially recommended`.

Fields:

- **Change:** what record/field;
- **Why:** target service effect;
- **Effort:** Online / Centre / Issuer action / Employer action / Review;
- **Downstream:** e.g. `No new conflicts in the records modeled here`;
- **Confidence:** `High within this demo rule` / `Needs official confirmation`;
- **Source basis:** link/drawer;
- CTA `Simulate this route`.

## Alternative card

Same anatomy. If an alternative would create modeled downstream conflicts, surface them prominently.

## Trade-off wording

Prefer concrete trade-offs:

> `This route changes one downstream record.`

rather than:

> `Risk score: 32%`.

---

# 12. Simulation interaction

## Confirmation copy

**Simulate this correction?**  
`This changes only the fictional case in your browser. No government record will be contacted or updated.`

Actions:

- `Simulate correction` primary
- `Cancel` secondary

## Animation

150–250 ms state transition. With reduced motion, immediate state replacement.

During recompute:

`Rechecking the records in this demo…`

Do not mimic official “processing” with fake multi-second delays.

## Success result

### State
`READY IN THIS SIMULATION`

### Copy
`The blocking rule now passes, and this demo found no new conflict for the selected goal.`

### Proof
`Changed: DL name representation`  
`Resolved: DigiLocker/DL reconciliation blocker`  
`Still different: EPFO display name — not relevant to this selected goal`

This “still different but not relevant” line demonstrates causal thinking.

---

# 13. Official next-action screen

## H1
`What you would do next`

A short ordered list, each step with verb-first copy.

Example structure:

1. `Open the official service for the record that needs correction.`
2. `Use the source-backed update route shown below.`
3. `After the official record changes, retry the target service.`

Include requirements/documents only if directly sourced for that scenario.

## Safety footer

`Processes and document requirements can change. Verify the linked official service before acting.`

## CTAs

- `Open official service` (external)
- `See why this route was chosen`
- `Reset demo`

No PDF download as the primary outcome. A shareable summary is P1.

---

# 14. EPFO scenario special UX

The signature moment is a **false lead crossed out by evidence**.

## Finding stack

### Finding 1
`Name looks different`  
Status: `Not the blocker in this simulation`

### Finding 2
`Date of exit is inconsistent with this demo service-history rule`  
Status: `Blocks the target`

Primary explanation:

> `Fixing the visible name difference would not make this fictional claim ready. The service-history condition is the causal blocker.`

This is a product-thinking proof. Do not dilute it with five additional findings.

---

# 15. Life-event scenario special UX

Use a **sequence**, not a spaghetti graph.

## Timeline/plan

`Now` → `Update A` → `Recheck B` → `Update C only if target requires it`

For each step show:

- why now;
- what becomes unblocked;
- what stays unchanged;
- whether official confirmation is needed.

The system must not imply that marriage or another life event requires a person to change name. The scenario is explicitly for a citizen who **has chosen / legally completed** a change and now wants records reconciled.

---

# 16. Hindi content guidance

Hindi should be simple and functional, not bureaucratic Sanskrit-heavy translation.

Examples:

| English | Simple Hindi |
|---|---|
| What are you trying to do? | आप क्या करना चाहते हैं? |
| This is blocking the task | इसी वजह से यह काम रुक रहा है |
| Different, but not the blocker | जानकारी अलग दिखती है, लेकिन इस काम को नहीं रोक रही |
| Show the evidence | वजह और रिकॉर्ड देखें |
| Compare ways to fix this | सुधार के विकल्प देखें |
| Simulate this correction | इस सुधार को डेमो में आज़माएँ |
| No government record will be changed | किसी सरकारी रिकॉर्ड में बदलाव नहीं होगा |
| Ready in this simulation | इस डेमो में अब प्रक्रिया तैयार है |
| What to do next | अब आगे क्या करें |

Agency/legal terminology that citizens recognize may remain in English alongside Hindi, e.g. `PAN`, `Aadhaar`, `UAN`, `Driving Licence`.

Do not transliterate every English UX word into Devanagari if a clearer Hindi phrase exists.

---

# 17. Form and input rules

P0 has almost no free-form sensitive input.

If any input exists:

- label above field, not placeholder-only;
- clear example marked fictional;
- validation on blur/submit, not every keystroke where distracting;
- retain user-entered synthetic value after errors;
- error text adjacent + programmatic association;
- never auto-format into a valid government ID.

---

# 18. Loading, empty and failure states

## Scenario loading
Because fixtures are local/small, use skeleton only if actual delay exists. Do not fake 3-second “AI analysis.”

## Rule unknown

**We can’t confirm this step from the rules in this prototype.**  
`The available evidence is incomplete, so we won’t guess. You can still see the records and the official source.`

## AI unavailable

**The AI explanation is unavailable.**  
`Your diagnosis is unchanged because it was calculated from the demo rules.`

## Source link unavailable

`The official link could not be opened from this device. The source title is shown below so you can find it independently.`

---

# 19. Responsive behavior

## 320–479 px

- single column;
- full-width primary actions;
- record compare stacks;
- dependency graph replaced/defaulted to trail;
- sticky bottom CTA allowed if it does not obscure content;
- no horizontal table.

## 480–767 px

- single column with larger cards;
- optional compact two-card comparisons only if each remains readable.

## 768–1199 px

- two-column comparison regions;
- side evidence drawer.

## 1200+ px

- max content width; do not stretch text across screen;
- graph/options can use extra horizontal room.

---

# 20. Accessibility interaction details

- Skip link target `main`.
- Route changes update document title and move/announce H1 appropriately.
- Dialogs use native/accessible semantics and escape-close where safe.
- Focus order follows DOM order; never reorder with CSS in a way that confuses keyboard users.
- Status icon has hidden text or combined accessible label.
- Diff spans must expose a plain-language summary such as `Record A includes RAMESH; Record B uses initial R`.
- SVG nodes/edges are `aria-hidden` if the full text trail immediately represents them; avoid duplicate verbose screen-reader content.
- `aria-live="polite"` for readiness recomputation; `assertive` only for critical blocking validation.
- Tooltips cannot contain exclusive information.
- Target size and spacing are tested on touch.

---

# 21. Content review checklist

Every screen must pass:

- Can a citizen understand it without knowing what a “canonical identity graph” is?
- Does the first sentence communicate outcome rather than implementation?
- Is any claim stronger than the evidence?
- Are we blaming a citizen or agency without proof?
- Is any text implying the prototype changed an official record?
- Is Hindi natural enough for a human reviewer?
- Would the flow work if the graph were removed?
- Would the flow work if AI were removed?
- Is the next action visible?

---

# 22. Suggested component inventory

Keep the UI kit intentionally small:

- `PrototypeDisclosure`
- `LanguageSwitcher`
- `ScenarioCard`
- `DemoProfileCard`
- `ReadinessBanner`
- `FindingCard`
- `RecordValueCard`
- `DiffSummary`
- `EvidenceDrawer`
- `DependencyTrail`
- `DependencyGraph`
- `CorrectionOptionCard`
- `ImpactList`
- `SimulationConfirmDialog`
- `BeforeAfterPanel`
- `NextActionSteps`
- `OfficialLink`
- `SourceBadge`
- `UncertaintyCallout`
- `ResetCaseButton`

Avoid building a generic 80-component enterprise design system before the three flows are complete.
