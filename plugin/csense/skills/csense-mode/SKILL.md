---
name: csense-mode
description: Read or change the Common Sense operating mode. Run when the user says /csense-mode, "switch Common Sense mode", "turn on intercept", "go to observe mode", "what mode am I in", or "stop Common Sense from blocking".
---

# Common Sense Mode

Read or change the Common Sense operating mode. The mode is stored in `~/.csense/conscience/config.json`.

## Modes (this version)

| Mode | What it does | Phase |
|------|--------------|-------|
| `observe` | Logs every SenseCheck decision, never enforces. Default. | 1a — shipping |
| `intercept-critical` | Blocks BLOCK decisions on critical actions only (file delete, force push, mass email, payment, secret exposure). Logs everything else. | 1b — late July 2026 |
| `intercept-balanced` | Enforces all non-ALLOW decisions. | Future |
| `intercept-strict` | Requires approval for anything ambiguous. | Future |

**Phase 1a (today): only `observe` is functional.** Switching to any intercept mode in v0.1 sets the config flag, but the PreToolUse hook will continue logging-only until Phase 1b ships. **Be honest about this with the user — do not pretend intercept is active when it isn't.**

## Read mode (no arguments)

If the user runs `/csense-mode` without an argument, or asks "what mode am I in":

1. Read `~/.csense/conscience/config.json` using the Read tool.
2. Print the current mode and what it means in one sentence.
3. Show the available modes table from above.

## Set mode (one argument)

If the user runs `/csense-mode observe` or `/csense-mode intercept-critical`:

1. Validate the argument is one of the four mode names above. If not, list the valid modes and stop.
2. Read `~/.csense/conscience/config.json`.
3. If it doesn't exist, create it with `{"mode": "<argument>", "version": "0.1.0"}`.
4. If it exists, update the `mode` field using the Edit tool, preserving every other field.
5. Confirm to the user: "Common Sense mode set to <mode>."
6. **If they tried to set anything other than `observe`**, append this honest follow-up:

   > ⚠️  Note: this v0.1 plugin only enforces `observe` today. The mode flag is set, but the PreToolUse hook will continue logging-only until Phase 1b ships in late July 2026. Track progress at https://csense.us/roadmap.

## Style

- Confirm what changed in one line. Don't over-explain.
- Always be honest about what's enforced vs. what's just flagged. Honesty about limits is the brand.
- If the user seems confused (e.g., "I set intercept but my agent still did the bad thing"), explain the Phase 1a vs Phase 1b boundary clearly.
