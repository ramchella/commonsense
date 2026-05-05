# Preferences

> Quirks, conventions, and opinions Common Sense should remember about how I work. Edit freely.

## Code

- TypeScript over JavaScript. Python over Bash for non-trivial scripts.
- Functional style over class-heavy. Pure functions where reasonable.
- Small commits. One concept per commit. Conventional Commits format if the repo uses it.
- Tests live next to the code they test (`foo.test.ts` next to `foo.ts`).

## Editor

- VSCode with Claude Code as the primary working surface.
- Prefer Markdown over rich text for any working document.
- Date format: ISO 8601 (`2026-05-04`) — never `05/04/2026`.

## Communication

- Email sign-off: first name only. No "Best regards" / "Cheers."
- Slack: short messages. No greetings ("Hey team," is fine; longer is too much).
- PR descriptions: 3 sections — what, why, test plan. Skip the "I bring you this PR with great pleasure" preamble.

## Files

- Never auto-format files I haven't asked to format.
- Always write a final newline. Lint warnings about trailing whitespace are acceptable; missing final newlines are not.

## Tools I use

- **Editor:** VSCode + Claude Code
- **Repo host:** GitHub
- **Cloud:** AWS (sandbox account aliased `sandbox`); production is `prod-us-east`
- **Database:** Postgres (staging at `$DATABASE_URL_STAGING`, prod at `$DATABASE_URL_PRODUCTION`)
- **Email:** Gmail
- **Calendar:** Google Calendar
- **Notes:** Markdown files in iCloud Drive; never proprietary apps
