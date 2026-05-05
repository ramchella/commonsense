---
name: csense-report
description: Generates a digest of Common Sense decisions from the action log.
---

# Common Sense Report Skill

When the user runs `/csense-report`, you will read the action log at `~/.csense/conscience/logs/action-log.jsonl` and present a summarized digest.

## Instructions

1. Read the JSONL file at `~/.csense/conscience/logs/action-log.jsonl`.
2. Parse each line per the contract in `${CLAUDE_PLUGIN_ROOT}/SCHEMA.md`.
3. Required fields you will use: timestamp, tool, decision, riskLevel, confidence, reasoning, citedSources, actionSummary, mode, enforced.
4. Calculate totals for each decision type (ALLOW, BLOCK, etc.) and risk level.
5. Present the data in a clean, formatted table.
6. Highlight any BLOCK or REQUIRE_APPROVAL decisions with extra detail.
7. If the log is empty, report "No actions logged yet."

## Example Output Format

---
Common Sense Report — [Date]

Total decisions logged: [Count]

┌──────────┬───────┐
│ Decision │ Count │
├──────────┼───────┤
│ ALLOW    │ [X]   │
│ BLOCK    │ [Y]   │
└──────────┴───────┘

...
