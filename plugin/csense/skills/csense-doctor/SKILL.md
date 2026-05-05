---
name: csense-doctor
description: Health check for the Common Sense install. Run when the user says /csense-doctor, "is Common Sense working", "verify the install", "diagnose Common Sense", or "why isn't Common Sense catching anything".
---

# Common Sense Doctor

Verify the Common Sense install is healthy. Five checks, each green or red, with a one-line fix if red.

## Steps

Run all five checks in order. For each check, use the Read tool or run a Bash test (`test -e`, `test -f`) to verify existence.

### Check 1 — Conscience folder exists

- Path: `~/.csense/conscience/`
- Sub-folders that must exist: `identity/`, `governor/`, `memory/`, `feedback/`, `logs/`
- **Red fix:** "Run `/exit` and reopen Claude Code — the SessionStart hook will scaffold the conscience folder. If that doesn't work, reinstall the plugin."

### Check 2 — Identity files present

- At minimum: `~/.csense/conscience/identity/user-identity.md` must exist and be non-empty.
- **Red fix:** "Conscience folder exists but identity is missing. Reinstall the plugin or restore from `${CLAUDE_PLUGIN_ROOT}/templates/founder/identity/`."

### Check 3 — Governor rules present

- At minimum: `~/.csense/conscience/governor/rules.md` must exist and contain at least one numbered rule.
- **Red fix:** "Governor rules missing. Without rules, Common Sense has nothing to enforce. Restore from the Founder template at `${CLAUDE_PLUGIN_ROOT}/templates/founder/governor/`."

### Check 4 — Action log exists and is appendable

- File: `~/.csense/conscience/logs/action-log.jsonl`
- If the file doesn't exist, that's fine — it'll be created on the first SenseCheck. Show as **green** with the note `(empty — no SenseChecks logged yet, that's normal on a fresh install)`.
- If it exists, validate the last line parses as JSON. If not, **red** with fix: "Last log line is malformed. Truncate the file or restore from backup."

### Check 5 — Config file readable

- File: `~/.csense/conscience/config.json`
- Must parse as JSON and contain a `mode` field whose value is one of: `observe`, `intercept-critical`, `intercept-balanced`, `intercept-strict`.
- **Red fix:** `"Config missing or corrupt. Reset with: echo '{\"mode\":\"observe\",\"version\":\"0.1.0\"}' > ~/.csense/conscience/config.json"`

## Output format

```
Common Sense Doctor
===================

✓ Check 1 — Conscience folder exists
✓ Check 2 — Identity files present (5 files)
✓ Check 3 — Governor rules present (6 rules loaded)
✓ Check 4 — Action log: 47 entries logged, last entry valid
✓ Check 5 — Config: mode=observe, version=0.1.0

5/5 checks passed. Common Sense is healthy.

Mode: observe (decisions logged, never enforced)
Conscience: ~/.csense/conscience/
Plugin: csense v0.1.0

Next: run /csense-report to see what your agent has been up to.
```

If any check is red, mark it with `✗` and put the fix line directly under it. Stop after the first red and ask the user to apply the fix before re-running.

## Style

- Concise. The user wants a yes/no signal.
- If everything is green: 5 lines of summary, then stop.
- If something is red: lead with the fix, then the diagnostic detail.
- Never run a check that requires the user's input mid-flow.
