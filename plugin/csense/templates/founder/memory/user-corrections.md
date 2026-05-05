# User Corrections

> Things the user has explicitly told the agent NOT to do, captured across conversations.
>
> The Common Sense LLM-powered evaluator (v0.1.1+) reads this file every SenseCheck and treats each entry as a hard rule. The rule-based v0.1.0 does not yet read this file; cross-session memory lands in v0.1.1.
>
> Format: one rule per line, prefixed with the date you set it. Append-only. Never delete — strike through with `~~text~~` if you want to retire a rule.

<!-- Examples (delete these and add your own as you go):

- 2026-05-04 — Don't touch `legacy/auth.ts`. Regulatory code, do not refactor without my explicit permission.
- 2026-05-04 — When drafting investor emails, never include specific MRR numbers. Use ranges.
- 2026-05-04 — Don't run `npm install` against the workspace root. Always cd into the specific package first.

-->
