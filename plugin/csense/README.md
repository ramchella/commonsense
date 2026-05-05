# csense — Common Sense plugin (developer reference)

This is the implementation layer. For the marketing pitch, install instructions, and roadmap, see the [root README](../../README.md).

## What this folder contains

```
plugin/csense/
├── .claude-plugin/
│   └── plugin.json              Plugin manifest (Claude Code reads this first)
├── README.md                    You are here
├── SCHEMA.md                    JSONL contract — emitted by the hook, parsed by /csense-report
├── hooks.json                   Hook registration (SessionStart + PreToolUse)
├── hooks/scripts/
│   ├── scaffold-conscience.py   Cross-platform: creates ~/.csense/conscience/ on first session
│   └── sense-check.py           Cross-platform: runs the SenseCheck on every Bash/Write/Edit
├── skills/
│   ├── csense-report/SKILL.md   /csense-report — digest of catches
│   ├── csense-doctor/SKILL.md   /csense-doctor — five-check health verification
│   └── csense-mode/SKILL.md     /csense-mode — read or change operating mode
└── templates/
    └── founder/                 Founder archetype seed (copied to ~/.csense/conscience/ on install)
```

## How to install for development

From the repo root:

```bash
cd /path/to/commonsense
# In Claude Code:
/plugin install ./plugin/csense
```

(End users use `/plugin install ramchella/csense` once the marketplace flips public on 2026-06-16.)

## Lifecycle

1. **First session:** the `SessionStart` hook runs `scaffold-conscience.py`, which creates `~/.csense/conscience/` and copies the Founder archetype templates.
2. **Every Bash/Write/Edit tool call:** the `PreToolUse` hook runs `sense-check.py`, which evaluates the action and appends a JSON line to `~/.csense/conscience/logs/action-log.jsonl`.
3. **User-invoked:** `/csense-report`, `/csense-doctor`, `/csense-mode` slash commands.

## Contract

`sense-check.py` writes JSON records matching `SCHEMA.md`. `csense-report` parses records matching `SCHEMA.md`. **They must agree.** Any change to one half requires a matching change to the other.

## What's enforced today (v0.1.0)

- Rule-based pattern matching in `sense-check.py`. Catches: force-push to main, paid-infra spin-up keywords, banned tone phrases, secret-bearing patterns, destructive `rm -rf`.
- Observe Mode only — decisions are logged, never enforced.

## What's coming (v0.1.1)

- LLM-powered SenseCheck that reads every file in `~/.csense/conscience/identity/` and `~/.csense/conscience/governor/` per call.
- Cross-session memory: reading `~/.csense/conscience/memory/user-corrections.md` and treating each line as a hard rule.
- Eval harness in `/eval/cases.json` to prevent prompt regressions.

## Contributing

See the root [README's Contribute section](../../README.md#contribute) and (eventually) [CONTRIBUTING.md](../../CONTRIBUTING.md). The fastest way to help: add a new archetype under `templates/`.
