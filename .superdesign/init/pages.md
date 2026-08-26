# Page dependency trees

## `/` - custody handover (new target)

Entry: `apps/web/src/main.tsx` (missing; to be created)

Planned dependencies:

- `apps/web/src/App.tsx` (new journey UI)
  - `apps/web/src/custodyApi.ts` (new exact four-state client)
  - `apps/web/src/i18n/LangProvider.ts`
  - `apps/web/src/i18n/strings.ts`
- `apps/web/src/styles.css` (new tokens and responsive styles)

Existing older ACK-workflow infrastructure remains available but is not a rendered
page: `src/api/client.ts`, `src/api/types.ts`, `src/state/useCaseStream.ts`, and
`src/state/session.ts`.
