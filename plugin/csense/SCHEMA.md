# Common Sense JSONL Schema (v0.1.0)

Every line in `~/.csense/conscience/logs/action-log.jsonl` is one
JSON object on one line. The PreToolUse hook emits records matching this.
The /csense-report skill parses records matching this. They MUST agree.

## Required fields

| Field          | Type             | Example                                          |
|----------------|------------------|--------------------------------------------------|
| timestamp      | ISO-8601 string  | "2026-05-04T14:32:18Z"                           |
| tool           | string           | "Bash" / "Write" / "Edit"                        |
| decision       | enum             | "ALLOW", "ALLOW_WITH_WARNING", "REWRITE_ACTION", "REQUIRE_APPROVAL", "BLOCK" |
| riskLevel      | enum             | "low", "medium", "high", "critical"              |
| confidence     | number 0..1      | 0.94                                             |
| reasoning      | string           | "Force-push to protected branch (main)."         |
| citedSources   | array of strings | ["governor/rules.md#rule-4"]                     |
| actionSummary  | string           | "git push --force origin main"                   |
| mode           | enum             | "observe", "intercept-critical", "intercept-balanced", "intercept-strict" |
| enforced       | boolean          | false (always false in Phase 1a)                 |

## Optional fields

| Field         | Type    | Notes                                       |
|---------------|---------|---------------------------------------------|
| suggested     | string  | Suggested rewrite (only for REWRITE_ACTION) |
| archetypeId   | string  | "founder", "marketing", etc. — for demos    |

## One full example

{"timestamp":"2026-05-04T14:32:18Z","tool":"Bash","decision":"BLOCK","riskLevel":"high","confidence":0.94,"reasoning":"Destructive recursive delete on src/ with uncommitted changes. Violates Governor Rule 3.","citedSources":["governor/rules.md#rule-3"],"actionSummary":"rm -rf src/legacy/ src/","mode":"observe","enforced":false}
