# Claude Plugin — Common Sense

A judgment layer for [Claude Code](https://claude.ai/code) that enforces your identity, values, and risk policies on every tool call the agent attempts.

## What it does

Common Sense sits between Claude and its tools. Before any action is taken, it checks the proposed call against your conscience files — a set of rules you define once and the agent respects automatically. The synergy between your declared values and the agent's capabilities means you get the full power of AI-assisted coding without giving up control over what it can and cannot do.

## Project layout

```
plugin/csense/          # Plugin source
  plugin.json           # Plugin manifest
  hooks/scripts/        # Hook scripts (sense-check, scaffold)
  templates/founder/    # Default conscience templates
  skills/               # Slash commands (csense-report, csense-doctor, csense-mode)
Docs/                   # Developer spec and system flow diagrams
```

## Getting started

1. Open this directory in Claude Code.
2. Run `/plugin add .` to install the plugin.
3. Follow the scaffold prompts to populate your conscience files under `~/.csense/conscience/`.
4. Run `/csense-doctor` to confirm everything is wired up.

## Key commands

| Command | Purpose |
|---|---|
| `/csense-report` | Digest of recent blocked or flagged actions |
| `/csense-doctor` | Health check for the plugin installation |
| `/csense-mode` | Show the current operating mode (Observe / Enforce) |

## Modes

- **Observe** — logs policy decisions without blocking. Good for initial calibration.
- **Enforce** — blocks tool calls that violate your rules.
