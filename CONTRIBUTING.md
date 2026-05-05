# Contributing to Common Sense

Thanks for considering a contribution. Common Sense is an open-source Claude Code plugin that gives AI agents a conscience — a layer of identity-aware judgment before they act. The project is small, intentional, and shipping in public.

This document is short on purpose. The bar is not "match a complex contributor framework" — it's "read this once, then ship."

## Three ways to help

### 1. Add an archetype *(highest leverage, marked `good first issue`)*

The Founder archetype ships in v0.1.0. Four more land in Phase 1b. The fastest way to make Common Sense useful for someone the project doesn't yet cover is to add an archetype for a role you understand: Lawyer, Teacher, Doctor, Indie Hacker, DevRel, Therapist, Journalist, Marketing Operator, Sales Engineer.

**How:**

1. Copy `plugin/csense/templates/founder/` to `plugin/csense/templates/<your-archetype>/`.
2. Rewrite the contents of every file in `identity/`, `governor/`, `memory/`, `feedback/` for the role you're covering. Use plain English. Keep each file short.
3. Open a PR. In the PR description, include one paragraph on who this archetype is for and what kind of catches it would generate.

### 2. Improve the SenseCheck

The single most important file in the codebase is [`plugin/csense/hooks/scripts/sense-check.py`](plugin/csense/hooks/scripts/sense-check.py). If you can make it produce *better* decisions on the same inputs, that's pure value.

**Guardrails:**

- Don't add latency. Median SenseCheck must stay under 500ms.
- Don't introduce dependencies. Python stdlib only for v0.1.x.
- Add an entry to `eval/cases.json` (coming in v0.1.1) for any new pattern you add. PRs without an eval case will be asked to add one.

### 3. Tell us what your agent almost did

Open a [discussion](https://github.com/ramchella/commonsense/discussions) or DM [@ramchella](https://x.com/ramchella). Every real flag — anonymized — becomes a story we share, a rule we add, and a lesson the prompt learns from.

## How we work

- **Single maintainer (Ram Chella).** PR responses within 48 hours during weekdays.
- **Conventional Commits.** `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`. PR titles use the same.
- **Small PRs win.** One concept per PR. PRs over ~300 lines get split before review.
- **Plain English.** README and docs follow the brand voice in [`plugin/csense/templates/founder/identity/tone.md`](plugin/csense/templates/founder/identity/tone.md). No corporate jargon.

## Code of conduct

By participating you agree to follow [our code of conduct](CODE_OF_CONDUCT.md) (Contributor Covenant 2.1). The short version: be respectful, assume good faith, and don't be the reason someone stops contributing.

## Contributor License Agreement

We use [CLA Assistant](https://cla-assistant.io/). On your first PR, the bot will guide you through signing a one-page CLA that gives the project the right to relicense your contribution if needed (e.g., to a stricter source-available license in a future major version). This is standard for OSS-funded projects and protects long-term project health.

## Security

If you find a security issue (prompt-injection bypass, hook-evasion, data exfiltration via Tier 3 contamination, etc.), **do not open a public issue.** Email security@csense.us with the details. See [SECURITY.md](SECURITY.md).

## Releases

`main` is the release branch. We tag releases as `v0.MAJOR.MINOR-{alpha,beta,rc,stable}` per the roadmap. v0.1.0-alpha is the current public release.

## Questions

DM [@ramchella](https://x.com/ramchella) on X or open a [discussion](https://github.com/ramchella/commonsense/discussions). Email is the slowest channel; X DMs are fastest.
