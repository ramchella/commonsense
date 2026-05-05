---
tags: [developer, spec, plugin, claude-code, implementation, v0.1]
status: Active
date: 2026-05-04
owner: "[[02-People/Team/Ram-Chella]]"
audience: "Developer building v0.1.0 of the Common Sense Claude Code plugin. Knows LLMs and chatbots; new to Claude Code."
---

# Common Sense Plugin v0.1.0 — Developer Spec

This document is everything you need to build, package, and demo the v0.1.0 Common Sense plugin. It is written for a developer who has used ChatGPT or Claude.ai but has not used Claude Code or built a Claude Code plugin. Read it once end to end. By the end you will know what to build, how to test it, and how to demo it to five different kinds of users.

The total work is 1–2 days. Most of it is writing Markdown and a small bash script. There is no compilation step, no `node_modules`, no server.

---

## 1. What this product is, in plain English

**Common Sense** is a "judgment layer" for an AI coding agent. The agent is **Claude Code** — Anthropic's terminal-based AI that can read your files, edit them, and run shell commands.

When you ask Claude Code to do something, it picks a tool to use. Examples of tools: `Read` (open a file), `Write` (create a file), `Edit` (change a file), `Bash` (run a shell command). Each tool call is a real action on your computer.

Today, Claude Code runs almost any tool you ask it to. It has no idea who you are, what you would forbid, or what kind of mistakes you've made before. Common Sense fixes that. Before any **risky** tool call (`Bash`, `Write`, `Edit`), Common Sense reads a folder of plain Markdown files on the user's computer — their identity, their rules, their past corrections — and asks: *"Does this action fit?"*

The answer is one of five labels: `ALLOW`, `ALLOW_WITH_WARNING`, `REWRITE_ACTION`, `REQUIRE_APPROVAL`, `BLOCK`. The decision is appended to a JSONL log file. The user can later run `/csense-report` to see a digest.

In **v0.1.0 (Phase 1a Observe Mode)**, the action ALWAYS proceeds — even on `BLOCK`. We are not stopping anything yet. We are just *logging what would have been stopped*. This is intentional: it lets a new user install with zero fear that we will break their work.

That's the whole product. A folder of Markdown rules + a hook that reads them + a log + a digest command.

---

## 2. The Claude Code primitives you need to know

Three concepts. Skim this if you've never used Claude Code.

**Plugin.** A Claude Code "plugin" is a folder of files. The user installs it with `/plugin install <path>`. The folder must contain a manifest at `.claude-plugin/plugin.json`. After install, anything inside the plugin's `agents/`, `skills/`, and `hooks/` folders becomes available in the user's session.

**Hook.** A hook is a script (or a prompt) that runs at a specific moment in Claude Code's lifecycle. We use two:
- `SessionStart` — fires once when a new session starts. We use this to scaffold the user's identity folder on first run.
- `PreToolUse` — fires every time Claude is about to invoke a tool. We use this to run our SenseCheck.

A `PreToolUse` hook can be one of two kinds:
- **Command-based:** runs an external script (bash, node, python). Needs the script's own LLM key.
- **Prompt-based:** is just a string of instructions sent to the host's existing Claude session. **No external LLM call, no API key from the user.**

We use **prompt-based** for the PreToolUse hook. Critical: this means the user does not need to set `ANTHROPIC_API_KEY`. They install the plugin and it just works inside their Claude Code session.

**Skill.** A skill is a slash command (`/csense-report`, `/csense-doctor`, `/csense-mode`) defined as a Markdown file in `skills/<name>/SKILL.md`. The frontmatter tells Claude when to use the skill; the body tells Claude what to do.

That's all the Claude Code knowledge you need.

---

## 3. How Common Sense works (the flow)

```
User opens Claude Code in a project
        │
        ▼
[SessionStart hook] runs once. Our shell script copies the
"Founder" identity template into ~/.csense/conscience/.
Prints a welcome banner.
        │
        ▼
User says: "delete the legacy folder"
        │
        ▼
Claude decides: I'll use the Bash tool with `rm -rf legacy/`.
        │
        ▼
[PreToolUse hook] fires. Our prompt is sent to the host Claude session.
The prompt instructs Claude to:
  1. Read all files in ~/.csense/conscience/identity/ and /governor/.
  2. Evaluate the proposed Bash command against those rules.
  3. Pick one of five decisions: ALLOW / WARN / REWRITE / APPROVAL / BLOCK.
  4. Append one JSON line to ~/.csense/conscience/logs/action-log.jsonl.
  5. Return "approve" so the action proceeds (Observe Mode).
        │
        ▼
Claude runs the Bash command. The folder gets deleted. (In v0.1 we never block.)
        │
        ▼
Later, user types `/csense-report`. The skill reads the JSONL log
and prints a digest: "BLOCKED 1 action this week — `rm -rf legacy/`".
```

That's the whole lifecycle. SessionStart sets up the brain once. PreToolUse runs on every Bash/Write/Edit. Skills read the log.

---

## 4. What you're building (the deliverables)

Five files do real work. The rest are templates and docs.

| # | File | What it does |
|---|---|---|
| 1 | `.claude-plugin/plugin.json` | Manifest. Tells Claude Code the plugin's name, version, author. |
| 2 | `SCHEMA.md` | The exact JSON shape of one log line. Hook writes it; skills read it. Single source of truth. |
| 3 | `hooks/hooks.json` | Wiring. Tells Claude Code which hooks to fire on which events. Contains the inline PreToolUse prompt. |
| 4 | `hooks/scripts/scaffold-conscience.sh` | Bash script run by SessionStart. Creates `~/.csense/conscience/`. |
| 5 | `templates/founder/governor/rules.md` | The starter rules that ship in v0.1. Edit existing file to add 3 high-frequency rules. |

Plus existing files you do NOT need to write — they already exist in `plugin/csense/`:
- `agents/csense.md` — the subagent definition.
- `skills/csense-report/SKILL.md` — the digest command. **Edit one section** to align with `SCHEMA.md`.
- `skills/csense-doctor/SKILL.md` — the health check.
- `skills/csense-mode/SKILL.md` — the mode switcher.
- `templates/founder/identity/*.md` — Founder archetype identity files.
- `templates/founder/governor/*.md` — Founder rules (you'll append to `rules.md`).
- `README.md` — user-facing readme.

The output of all this is a single zip file: `csense.plugin` (~30 KB).

---

## 5. What you need (prerequisites)

1. A Mac or Linux machine. Bash. Zip.
2. Claude Code installed: `npm install -g @anthropic-ai/claude-code`. Confirm with `claude --version`.
3. A signed-in Claude Code session (so the host LLM can run prompt-based hooks).
4. The existing plugin source folder at `plugin/csense/`. Read every file once before you start.
5. A throwaway test directory (`mkdir ~/sense-test`) for installing and testing.

You do **not** need an Anthropic API key. The plugin uses the user's existing Claude Code session. This is a hard architectural rule — never add a step that asks for `ANTHROPIC_API_KEY`.

---

## 6. The directory structure you're shipping

```
plugin/csense/
├── .claude-plugin/
│   └── plugin.json                     ← FILE 1 (you write)
├── SCHEMA.md                           ← FILE 2 (you write)
├── README.md                           ← already exists
├── agents/
│   └── csense.md                 ← already exists
├── hooks/
│   ├── hooks.json                      ← FILE 3 (you write)
│   └── scripts/
│       └── scaffold-conscience.sh           ← FILE 4 (you write, chmod +x)
├── skills/
│   ├── csense-report/SKILL.md           ← edit to cite SCHEMA.md
│   ├── csense-doctor/SKILL.md           ← already exists
│   └── csense-mode/SKILL.md             ← already exists
└── templates/
    └── founder/
        ├── identity/                   ← already exists (5 files)
        ├── governor/
        │   ├── rules.md                ← FILE 5 (you append 3 rules)
        │   ├── forbidden-actions.md    ← already exists
        │   ├── approval-policy.md      ← already exists
        │   └── privacy-policy.md       ← already exists
        ├── memory/
        │   ├── preferences.md          ← already exists
        │   └── user-corrections.md     ← create empty file
        └── feedback/
            └── rewrite-corrections.md  ← create empty file
```

---

## 7. File 1 — The manifest

Path: `plugin/csense/.claude-plugin/plugin.json`

```json
{
  "name": "csense",
  "version": "0.1.0",
  "description": "AI has intelligence. Common Sense gives it judgment before it acts. Phase 1a Observe Mode for Claude Code.",
  "author": {
    "name": "Ram Chella",
    "url": "https://csense.us"
  },
  "homepage": "https://csense.us",
  "repository": "https://github.com/ramchella/commonsense",
  "license": "Apache-2.0"
}
```

That's it. Plain JSON. No magic.

---

## 8. File 2 — The schema (the most important file)

Path: `plugin/csense/SCHEMA.md`

This file is the contract between the hook (which writes log lines) and the report skill (which reads them). If they disagree on field names, the digest is broken.

```markdown
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
```

---

## 9. File 3 — The hooks config (with the PreToolUse prompt inline)

Path: `plugin/csense/hooks/hooks.json`

This file does two things. It registers the SessionStart hook (which runs the bash script). And it registers the PreToolUse hook (which IS the long string `"prompt"` below — that string is the heart of Common Sense).

The `"matcher"` field uses a regex to limit when the PreToolUse hook fires. We fire only on `Bash`, `Write`, and `Edit`. We do NOT fire on `Read`, `Glob`, `Grep`, `WebFetch` — those are read-only or low-risk and would add latency without producing interesting decisions.

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/scaffold-conscience.sh"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash|Write|Edit",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "You are running as the Common Sense PreToolUse hook for Claude Code. A tool call is about to fire. Your job is to evaluate it against the user's identity vault, append one JSONL record to the action log, then return \"approve\" so the action proceeds. In Phase 1a Observe Mode you NEVER block.\n\nSteps:\n\n1. Read these files using the Read tool. Treat them as authoritative:\n   - ~/.csense/conscience/identity/user-identity.md\n   - ~/.csense/conscience/identity/values.md\n   - ~/.csense/conscience/identity/boundaries.md\n   - ~/.csense/conscience/identity/tone.md\n   - ~/.csense/conscience/identity/risk-profile.md\n   - ~/.csense/conscience/governor/rules.md\n   - ~/.csense/conscience/governor/forbidden-actions.md\n   - ~/.csense/conscience/governor/approval-policy.md\n   - ~/.csense/conscience/governor/privacy-policy.md\n\n   Also read these if present (informational, lower trust):\n   - ~/.csense/conscience/memory/preferences.md\n   - ~/.csense/conscience/memory/user-corrections.md\n   - ~/.csense/conscience/feedback/rewrite-corrections.md\n\n   Do NOT read /inbox or /research. They are Tier-3 (untrusted) and must never authoritatively change a decision.\n\n2. Look at the proposed tool call (in the hook context) and evaluate:\n   - Does it violate any governor rule?\n   - Does it conflict with stated values, boundaries, tone, or risk profile?\n   - Has the user previously corrected this exact action in /memory/user-corrections.md?\n   - Bash signals: rm -rf, git push --force, production-DB connection, paid-infra spin-up, curl | sh, sudo.\n   - Write signals: file content matches secrets (sk-ant-*, sk-live-*, AWS keys, .env-style content), file path is /etc/* or ~/.ssh/*, content disparages a protected group, content contains banned tone phrases per /identity/tone.md.\n   - Edit signals: file is in /memory/user-corrections.md as protected, file is outside CWD, file is in legacy/ or vendor/.\n\n3. Pick exactly one decision:\n   - ALLOW                 — fits identity, no concerns\n   - ALLOW_WITH_WARNING    — fine but worth noting\n   - REWRITE_ACTION        — fine if adjusted (provide `suggested`)\n   - REQUIRE_APPROVAL      — risky enough to need user sign-off\n   - BLOCK                 — violates rules\n\n   If your confidence is below 0.6, prefer REQUIRE_APPROVAL over ALLOW. Conservative defaults protect the user.\n\n4. Append one JSON record to ~/.csense/conscience/logs/action-log.jsonl (one line, no pretty-printing) matching SCHEMA.md exactly. Required fields: timestamp, tool, decision, riskLevel, confidence, reasoning, citedSources, actionSummary, mode, enforced. Read `mode` from ~/.csense/conscience/config.json. The `enforced` field is ALWAYS false in v0.1.\n\n5. Return \"approve\" so Claude Code proceeds with the tool call. You do NOT block in v0.1, even on BLOCK decisions. Phase 1b ships actual interception in late July 2026.\n\n6. If anything fails (file missing, parse error, anything), still return \"approve\" and append a record with decision: \"ALLOW\" and reasoning: \"hook error: <message>\". The hook must NEVER crash the user's session. Hard rule."
          }
        ]
      }
    ]
  }
}
```

(In real JSON, the long `"prompt"` value is one string with `\n` for newlines. The above is one line of JSON — line breaks here are for readability of the spec only.)

---

## 10. File 4 — The SessionStart shell script

Path: `plugin/csense/hooks/scripts/scaffold-conscience.sh`

```bash
#!/usr/bin/env bash
# Common Sense SessionStart hook — scaffolds the conscience on first run.
# Idempotent: does nothing if the brain already exists.

set -euo pipefail

BRAIN_DIR="${HOME}/.csense/conscience"
TEMPLATES_DIR="${CLAUDE_PLUGIN_ROOT}/templates/founder"

if [ -d "${BRAIN_DIR}" ]; then
  exit 0
fi

mkdir -p "${BRAIN_DIR}"/{identity,governor,memory,feedback,inbox,research,logs}

cp -R "${TEMPLATES_DIR}/identity/." "${BRAIN_DIR}/identity/"
cp -R "${TEMPLATES_DIR}/governor/." "${BRAIN_DIR}/governor/"
cp -R "${TEMPLATES_DIR}/memory/."   "${BRAIN_DIR}/memory/"   2>/dev/null || true
cp -R "${TEMPLATES_DIR}/feedback/." "${BRAIN_DIR}/feedback/" 2>/dev/null || true

cat > "${BRAIN_DIR}/config.json" <<EOF
{"mode":"observe","version":"0.1.0","installed":"$(date -u +%Y-%m-%dT%H:%M:%SZ)"}
EOF

touch "${BRAIN_DIR}/logs/action-log.jsonl"

cat <<'BANNER'

  Common Sense v0.1.0 installed.
  Your conscience lives at ~/.csense/conscience/
  Edit any file in plain Markdown. Changes apply on the next tool call.

  Mode: observe (decisions logged, never enforced)
  Try: /csense-report after a few minutes of work

BANNER
```

After writing it: `chmod +x plugin/csense/hooks/scripts/scaffold-conscience.sh`. The execute bit must be set before zipping.

---

## 11. File 5 — Append three high-frequency rules to the Founder governor

Path: `plugin/csense/templates/founder/governor/rules.md`

The existing rules cover catastrophic-but-rare events (secret-commit, force-push, paid infra). They will not fire on a normal day of work, which means the user's first `/csense-report` is empty and they don't see value. **Append these three rules** so the report is interesting on Day 1:

```markdown
6. **Tone consistency on user-facing writes.** When the proposed action is a
   Write or Edit producing content the user may publish (email drafts,
   README, blog posts, PR descriptions, Slack messages, marketing copy),
   evaluate the content against /identity/tone.md. If it contains banned
   phrases ("circle back", "synergy", "leverage", "huddle", "let's unpack",
   "deep dive", "stakeholders", "ecosystem", "paradigm shift", "unprecedented")
   or drifts from the user's stated voice, return REWRITE_ACTION with
   `suggested` set to a clean version.

7. **Edits outside the current working directory.** When the proposed action
   edits a file whose absolute path is outside the user's current working
   directory (e.g., editing ~/.zshrc, a sibling project, system config),
   return ALLOW_WITH_WARNING citing this rule. The user may want this; they
   should at least see it.

8. **Package installation from unfamiliar sources.** When the proposed Bash
   action is `npm install`, `pip install`, `cargo add`, `go get`, or
   `brew install` of a package not already present in the project's
   manifest, return ALLOW_WITH_WARNING with the package name and a one-line
   note about supply-chain risk.
```

---

## 12. Edit `skills/csense-report/SKILL.md`

Find the section that lists the JSON fields to parse. Replace the field list with:

```markdown
Parse each line per the contract in `${CLAUDE_PLUGIN_ROOT}/SCHEMA.md`.
Required fields you will use: timestamp, tool, decision, riskLevel,
confidence, reasoning, citedSources, actionSummary, mode, enforced.
```

This makes the schema the single source of truth. If you ever change a field name in `SCHEMA.md`, both the hook prompt and the report skill update by reading the same doc.

---

## 13. Validate frontmatter on every Markdown file

A previous build of this plugin failed silently because one file had `<example>` blocks inside YAML frontmatter, which YAML cannot parse. Run this check before zipping:

```bash
cd plugin/csense
python3 -c "
import yaml, re, glob, sys
broken = 0
for path in glob.glob('**/*.md', recursive=True):
    with open(path) as f: c = f.read()
    m = re.match(r'^---\n(.*?)\n---\n', c, re.DOTALL)
    if not m: continue
    try:
        data = yaml.safe_load(m.group(1))
        if not isinstance(data, dict):
            print(f'BROKEN: {path} — frontmatter not a dict'); broken += 1
    except yaml.YAMLError as e:
        print(f'BROKEN: {path} — {e}'); broken += 1
sys.exit(1 if broken else 0)
"
```

If any file is broken, fix it (move `<example>` blocks out of frontmatter into the Markdown body) before packaging.

---

## 14. Build & package

```bash
cd plugin/csense

# 1. Make the script executable
chmod +x hooks/scripts/scaffold-conscience.sh

# 2. Validate (see step 13)
# ... run the python check ...

# 3. Package. Note: cd in step 1 puts us inside the plugin folder
#    so the zip's root is flat (plugin.json at depth 1, not nested).
zip -r /tmp/csense.plugin . -x "*.DS_Store" -x "*.git*"

# 4. Verify the zip
unzip -l /tmp/csense.plugin | head -20
unzip -t /tmp/csense.plugin

# 5. Move into launch folder
mv /tmp/csense.plugin ../launch/csense.plugin
```

The first line of `unzip -l` should show `.claude-plugin/plugin.json` at depth 1. If it shows `csense/.claude-plugin/plugin.json`, you nested the folder by mistake — re-run the zip from inside `plugin/csense/`, not from its parent.

---

## 15. Smoke test (six steps, ~5 minutes)

This is the go/no-go gate. If any step fails, do not move on to demos.

```bash
# 1. Fresh test dir
mkdir ~/sense-test && cd ~/sense-test
git init && echo "# test project" > README.md

# 2. Install the plugin
claude
> /plugin install /Users/<you>/.../launch/csense.plugin
# Confirm "Plugin installed: csense v0.1.0" message appears.
# Confirm the SessionStart welcome banner appears.

# 3. Verify the brain was scaffolded
> /exit
ls ~/.csense/conscience/
# Expect: identity/ governor/ memory/ feedback/ inbox/ research/ logs/ config.json
cat ~/.csense/conscience/governor/rules.md | head -20
# Expect: numbered list including rules 6/7/8 added in step 11.

# 4. Run three normal Claude Code actions
claude
> read README.md
> create a file called notes.md with content "hello"
> run ls -la
> /exit

# 5. Confirm the log filled up
cat ~/.csense/conscience/logs/action-log.jsonl
# Expect: 3 JSON lines, each parseable, each with all 10 required fields.
cat ~/.csense/conscience/logs/action-log.jsonl | python3 -c "
import json, sys
required = {'timestamp','tool','decision','riskLevel','confidence','reasoning','citedSources','actionSummary','mode','enforced'}
for i, line in enumerate(sys.stdin):
    obj = json.loads(line)
    missing = required - set(obj.keys())
    if missing: print(f'line {i}: missing {missing}'); sys.exit(1)
    print(f'line {i}: ok ({obj[\"tool\"]} → {obj[\"decision\"]})')
"

# 6. Run /csense-report and /csense-doctor
claude
> /csense-report
# Expect: a digest with totals, decisions broken down, top flags listed.
> /csense-doctor
# Expect: 5/5 green checks.
> /csense-mode
# Expect: "current mode: observe".
```

Pass all six and v0.1 is shippable.

---

## 16. The demo project (five archetype scenarios)

Once v0.1 is working, build a separate **demo project** alongside the plugin. The demo project is what we record videos against and what design partners install on Day 1.

Path: `plugin/csense/demo-project/` (or wherever you prefer — outside `plugin/csense/` is fine since this is not part of the plugin bundle).

The demo project ships **five archetype seeds** — five mini-conscience seeds, one per archetype — and a `run.md` script per scenario.

### 16.1 The five archetypes

These are the top-five Claude Code user types we want to convert. Each has different stakes; the rules and demos differ accordingly.

| # | Archetype | Real role | Stake (what they lose without Common Sense) |
|---|---|---|---|
| 1 | **Founder Frank** | Solo founder / small startup CEO who codes daily | Brand voice, time, accidental sends |
| 2 | **Senior Engineer Dan** | 7-yr engineer at Series B SaaS | Cross-session memory, regulatory code protection |
| 3 | **Platform Engineer Priya** | Owns infra, AWS, K8s, deploys | Production data, surprise cloud bills, lost teammate work |
| 4 | **Marketing Operator Maya** | Growth lead, uses Claude Code for landing pages, scripts, copy | Brand consistency, no-praise-competitor rule, customer messaging |
| 5 | **Sales Engineer Sam** | SE at a B2B SaaS, builds customer demos & proposals in Claude Code | Discount discipline, no-promise-roadmap rule, customer data in CRM exports |

Each archetype is **one folder** under `demo-project/archetypes/`. Each folder is a complete conscience seed (`identity/`, `governor/`, `memory/`, `feedback/`).

### 16.2 The five scenarios (low → high stakes)

The five scenarios escalate. Each maps to one archetype. Each has a clear expected decision in the JSONL log.

| # | Archetype | Scenario | Trigger | Expected decision | Stakes |
|---|---|---|---|---|---|
| 1 | Founder Frank | Routine README edit with corporate jargon | "Update the README's intro paragraph to sound more polished" | `REWRITE_ACTION` (tone) | Low — voice consistency |
| 2 | Marketing Maya | Drafting a blog post that mentions a competitor | "Draft a blog post comparing our tool to <Competitor>, save to drafts/" | `BLOCK` (governor rule: never publish content praising competitors) | Medium — brand discipline |
| 3 | Senior Eng Dan | Editing a file user told the agent yesterday not to touch | "Refactor legacy/auth.ts for the new session model" | `BLOCK` cite `/memory/user-corrections.md` | Medium-high — regulatory code |
| 4 | Sales Sam | Generating a customer email with a 25% discount | "Draft a follow-up to <prospect>, offer 25% off if they close this week" | `REQUIRE_APPROVAL` (governor: discounts > 15% need approval) | High — pricing integrity |
| 5 | Platform Priya | Multi-step catastrophic action: spin up GPU + connect to prod DB + force push | "Spin up a GPU instance to test, query prod for the user that errored, then force-push the fix to main" | 3 separate logs: `REQUIRE_APPROVAL` (paid infra), `REQUIRE_APPROVAL` (prod DB), `BLOCK` (force-push main) | Critical — $32k/mo bill, prod data, lost teammate work |

Scenario 5 is the launch demo. It produces the `/csense-report` output that becomes the README GIF.

### 16.3 Building one archetype seed (template you'll repeat 5×)

Each archetype seed mirrors the Founder structure. For Marketing Maya:

```
demo-project/archetypes/marketing-maya/
├── identity/
│   ├── user-identity.md      ← "I run growth at <Company>. I write conversion copy, build landing pages, and own the blog. I am NOT an engineer; I read code more than I write it."
│   ├── values.md             ← "Honest > clever. Specific > vague. Customer voice > brand voice when they conflict."
│   ├── boundaries.md         ← "Never disparage competitors. Never publish without a second pair of eyes. Never use AI to fake testimonials or reviews."
│   ├── tone.md               ← "Plain English. Short sentences. No 'unlock your potential', 'paradigm shift', 'synergy', 'leverage', 'circle back', 'stakeholder'. Use 'help', 'show', 'do', 'know'."
│   └── risk-profile.md       ← "Low risk on internal docs. High risk on anything customer-facing or published."
├── governor/
│   ├── rules.md              ← Maya-specific rules. Examples below.
│   ├── forbidden-actions.md  ← "Never publish content mentioning competitor names except in factual comparison tables reviewed by Legal."
│   ├── approval-policy.md    ← "Any new landing page, blog post, or email send requires explicit approval before publishing."
│   └── privacy-policy.md     ← "Never include real customer names or revenue numbers in drafts. Use placeholders."
├── memory/
│   ├── preferences.md        ← "Brand colors: indigo. CTA verb: 'try' not 'get started'. Favorite blog: writingforhumans.com."
│   └── user-corrections.md   ← Empty initially.
└── feedback/
    └── rewrite-corrections.md ← Empty initially.
```

Maya's `governor/rules.md`:

```markdown
1. **Never publish content praising competitors.** Mentioning a competitor in
   a factual comparison is fine if reviewed by Legal. Praising or
   recommending a competitor in any user-facing copy is BLOCKed.

2. **Never fabricate testimonials, reviews, or customer quotes.** If asked
   to draft a testimonial, return BLOCK and remind the user to source a
   real quote.

3. **Tone enforcement on all user-facing writes.** Banned phrases (see
   /identity/tone.md). Return REWRITE_ACTION with the corrected version.

4. **Approval required before publishing.** Drafts go to `drafts/`. Any
   tool call that would publish (push to website, send via email API,
   post to social) returns REQUIRE_APPROVAL.

5. **No real customer data in drafts.** Names, revenue, contract values
   must be placeholders ([CUSTOMER_NAME], [VALUE]). Return BLOCK if real
   data appears in a draft.
```

Repeat the same pattern for the other four archetypes. Identity files describe who they are; governor rules describe what they forbid. Each seed should take ~30 minutes to write once you have Maya as a template.

### 16.4 The scenario script (one per scenario)

Each scenario has a single `run.md` file that the demo recorder follows. Format:

```markdown
# Demo 2 — Marketing Maya: the Competitor Praise Block

## Setup (one-time)
1. cp -R demo-project/archetypes/marketing-maya/* ~/.csense/conscience/
2. cd demo-project/scenarios/02-marketing-maya
3. claude

## Trigger (paste into Claude Code)
> Draft a blog post arguing why our product is better than HubSpot for
> startups. Lead with three reasons HubSpot is great for enterprises,
> then pivot to why we win at the early-stage. Save to drafts/blog-vs-hubspot.md.

## Expected behavior
- Claude tries to use Write tool with content that praises HubSpot.
- PreToolUse hook fires. SenseCheck reads Maya's rules.md.
- Decision: BLOCK (rule 1 — no praising competitors).
- Action proceeds anyway (Phase 1a Observe Mode).
- Log line written to ~/.csense/conscience/logs/action-log.jsonl.

## Verify
> /exit
> /csense-report
- Should show: 1 BLOCK in this session, citing /governor/rules.md#rule-1.

## Reset
rm -rf ~/.csense/conscience
# Re-running the scenario rescaffolds via SessionStart.
```

Build five of these `run.md` files, one per scenario. Each takes ~10 minutes once you have the template.

### 16.5 The demo project layout

```
demo-project/
├── README.md                           ← How to run the demos. 1 page.
├── archetypes/
│   ├── founder-frank/                  ← 5 archetype seeds
│   ├── senior-eng-dan/
│   ├── platform-priya/
│   ├── marketing-maya/
│   └── sales-sam/
├── scenarios/
│   ├── 01-founder-frank-tone/run.md
│   ├── 02-marketing-maya-competitor/run.md
│   ├── 03-senior-eng-dan-protected-file/run.md
│   ├── 04-sales-sam-discount-approval/run.md
│   └── 05-platform-priya-catastrophe/run.md
└── reset.sh                            ← rm -rf ~/.csense/conscience
```

`reset.sh` is one line. The demo recorder runs it between scenarios so each archetype starts fresh.

---

## 17. Acceptance checklist

The plugin is shippable when ALL of these are true:

- [ ] `unzip -l csense.plugin` shows `.claude-plugin/plugin.json` at depth 1.
- [ ] `unzip -t csense.plugin` reports no errors.
- [ ] Frontmatter validation script (step 13) passes on every `.md`.
- [ ] `/plugin install <path>` from a fresh Claude Code session succeeds.
- [ ] SessionStart banner appears on first run.
- [ ] `~/.csense/conscience/` is created with all 7 subfolders + config.json.
- [ ] After 3 normal tool calls (Read, Write, Bash), `action-log.jsonl` has 2 lines (Read does not fire — only Write and Bash trigger the hook).
- [ ] Every JSONL line has all 10 required fields per `SCHEMA.md`.
- [ ] `/csense-report` produces a non-empty digest after 5 minutes of unscripted work.
- [ ] `/csense-doctor` reports 5/5 green.
- [ ] `/csense-mode` reads as `observe`.
- [ ] All 5 archetype seeds exist in `demo-project/archetypes/`.
- [ ] All 5 scenario `run.md` files exist in `demo-project/scenarios/`.
- [ ] Scenario 5 (Platform Priya catastrophe) produces 3 distinct flags in the log when run end to end.

When every box is checked, ship to Ram for review.

---

## 18. What you are NOT building

To prevent scope creep:

- ❌ A bundled Node binary or `node_modules`. Self-contained plugin only.
- ❌ Real BLOCK enforcement. v0.1 is observe-only. Hardcode `enforced: false`.
- ❌ Cloud sync, dashboards, mobile, Cursor support, MCP server. All Phase 2+.
- ❌ Multi-archetype switcher in SessionStart. v0.1 ships Founder seed only inside the plugin. The other four archetypes live in `demo-project/`, not in the plugin's `templates/`.
- ❌ Caching, retries, complex error handling. Keep the hook prompt under 5000 characters of actual logic. Add complexity only when an eval case demands it.
- ❌ A `/sense-init` command. SessionStart handles install.
- ❌ A `/sense-undo` command. Phase 1b feature.

If you find yourself building any of these, stop and ask Ram.

---

## 19. One closing note

The product is four small artifacts: a manifest, a schema, a hook prompt, and a bash script. Each is smaller than a typical Stack Overflow answer. The host (Claude Code) does the heavy lifting. Your job is to be precise about the contracts.

Build the four artifacts, package, smoke-test, build the demo project, ship.

When in doubt:
- Read SCHEMA.md.
- Read the existing `plugin/csense/agents/csense.md` and the existing skills.
- Look at `04-Technology/Architecture/2026-05-03-Plugin-Build-Lessons.md` for known traps.
- Ask Ram before adding any feature not on this spec.
