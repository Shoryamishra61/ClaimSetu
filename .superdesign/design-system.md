# Handover29C design system

## Product and job

Handover29C is an independent hackathon prototype that helps a vehicle owner and a
fictional authorised dealer prepare a Form 29C custody record. It never claims to
be a government portal, never claims submission or legal effect, and uses only
fictional fixtures. The core journey is Vehicle -> Dealer -> Handover -> Record.
Private-buyer transfers are visibly out of scope.

## Experience architecture

- A focused, one-task service journey; never a dashboard, admin shell, or analytics page.
- Persistent top disclosure: "Independent prototype - simulated government integrations - fictional data."
- Compact header with wordmark text, prototype badge, English/Hindi toggle, and a details drawer.
- Four-step progress indicator labeled Vehicle, Dealer, Handover, Record. It must
  use words/numbers as well as color and collapse gracefully at 320px.
- One primary card at a time, max 760px, with progressive disclosure and plain copy.
- Demo-fixture actions are explicit. Real personal information is neither requested nor implied.
- The terminal panel offers the generated prototype PDF and says it is not a portal acknowledgement.

## Visual language

Light-only, restrained, trustworthy, and human. Use generous white space and
subtle paper-like surfaces rather than gradients or glossy effects. Avoid official
seals, flags, government emblems, biometric motifs, shields, locks, maps, GPS,
cryptocurrency/crypto imagery, and celebratory legal-success visuals.

### Tokens

- Font stack: Inter, "Noto Sans Devanagari", "Segoe UI", system-ui, sans-serif.
- Canvas `#F4F7F3`; surface `#FFFFFF`; ink `#17211B`; muted `#526158`.
- Primary forest `#145C3A`; hover `#0E472C`; tint `#E8F3EC`.
- Amber notice text `#8A5200`, notice surface `#FFF5D6`.
- Error `#A8201A`, error surface `#FCECEA`; border `#C7D2CA`.
- Focus indicator is exactly 3px solid `#FFC107` with 2px offset.
- Spacing scale: 4, 8, 12, 16, 24, 32, 48, 64px.
- Controls radius 8px, cards 16px. Minimum target 48x48px.
- Only subtle card shadow: `0 10px 30px rgba(23,33,27,.08)`.

## Typography

- Page title 32/40, 700; section title 24/32, 700; card title 20/28, 650.
- Body 16/24; label 15/20, 650; helper 14/20; status 13/18, 700.
- Sentence case throughout. Technical identifiers use a system monospace stack.

## Components and states

- Primary button is solid forest with white text; secondary is white with forest border.
- Inputs have persistent labels, examples beneath, 48px minimum height, and inline errors.
- Status chips combine a short word and a simple CSS icon/check, never color alone.
- Notices have a vertical amber rule and explicit "Prototype boundary" heading.
- Loading uses button text changes and `aria-busy`; no blocking full-screen spinner.
- Errors appear next to the relevant field and in a polite `aria-live` summary.
- Completed details become compact read-only summary rows with a Change action.

## Responsive and accessibility

- Must work at 320px without critical horizontal scrolling and at 200% browser zoom.
- Desktop remains a centered single-column task flow; no second-column distraction.
- All interactive controls are keyboard reachable in DOM order and have visible focus.
- Use semantic headings, fieldsets/legends, native inputs/buttons, `aria-current=step`,
  `aria-live=polite`, and explicit PDF link purpose.
- Hindi copy can expand by 35% without clipping.
- Honor reduced motion and Windows high-contrast/forced-colors modes.

## Motion

Use 160ms ease-out for card/status opacity and a 4px vertical settle. Disable
nonessential motion under `prefers-reduced-motion`. No confetti, pulsing warnings,
or animations that imply official approval.

## Absolute content constraints

Never include Aadhaar, GPS/proximity, WebCrypto signatures, Jaro-Winkler name
matching, Section 65B certificates, liability-severed language, official RTO filing
success, or claims of government acknowledgement. Always preserve the simulation
disclosure and the exact four states DRAFT, INITIATED, DEALER_SELECTED, and
CUSTODY_TRANSFERRED in technical details.
