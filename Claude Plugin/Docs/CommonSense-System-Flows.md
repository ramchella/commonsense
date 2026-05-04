\---

tags: \[reference, flows, mental-model, architecture, ecosystem]
status: Active
date: 2026-05-04
owner: "\[\[02-People/Team/Ram-Chella]]"
audience: "Anyone who needs to hold the Common Sense system in their head — Ram, the developer building v0.1, design partners, future hires."
---

# Common Sense — System Flows Reference

This document is a reference of **flows** — every important "how does X work" in the Common Sense ecosystem, written as ASCII arrow diagrams with short context. Skim it, read it section by section, or jump to a specific flow. Each flow is self-contained.

You will hold the whole system in your head by the end.

Each section answers a "how does it…" question.

* Section A — install \& first run
* Section B — runtime (what happens on a tool call)
* Section C — how the identity vault is read
* Section D — data flows (logs, schema, contracts)
* Section E — user interaction flows
* Section F — cross-time flows (yesterday's rule catches today's action)
* Section G — distribution \& discovery
* Section H — phase progression (1a → 1b → 2 → 3)
* Section I — error \& resilience
* Section J — marketing \& growth loops
* Section K — architecture decisions
* Section L — demo project flows
* Section M — meta flows (what the system is *doing* for the user)

\---

## Section A — Install \& First-Run Flows

### A.1 First install (Phase 1a, plugin path)

```
User opens Claude Code in any project
        ↓
User types: /plugin install /path/to/csense.plugin
        ↓
Claude Code unzips the plugin into a managed folder on the user's machine
        ↓
Claude Code parses .claude-plugin/plugin.json  (manifest)
        ↓
Claude Code registers the hooks declared in hooks/hooks.json
        ↓
Claude Code registers the agent in agents/csense.md
        ↓
Claude Code registers /csense-report, /csense-doctor, /csense-mode skills
        ↓
"Plugin installed: csense v0.1.0" — install is done
        ↓
SessionStart hook is queued for the NEXT session start
```

Install is metadata-only at this point. The user's `\~/.csense/conscience/` does not exist yet. It is created on the next session start.

### A.2 First session after install

```
User runs `claude` in a project (or VSCode extension auto-starts it)
        ↓
Claude Code begins a new session
        ↓
SessionStart hook fires → executes hooks/scripts/scaffold-conscience.sh
        ↓
The script checks: does \~/.csense/conscience/ exist?
   ├─ YES → exit 0 silently (idempotent, no-op)
   └─ NO  → continue ↓
        ↓
mkdir \~/.csense/conscience/{identity,governor,memory,feedback,inbox,research,logs}
        ↓
cp -R templates/founder/identity/.   → \~/.csense/conscience/identity/
cp -R templates/founder/governor/.   → \~/.csense/conscience/governor/
cp -R templates/founder/memory/.     → \~/.csense/conscience/memory/
cp -R templates/founder/feedback/.   → \~/.csense/conscience/feedback/
        ↓
Write \~/.csense/conscience/config.json with mode=observe, version=0.1.0
        ↓
touch \~/.csense/conscience/logs/action-log.jsonl  (empty)
        ↓
Print welcome banner to terminal
        ↓
Session is ready — Claude Code waits for user input
```

### A.3 All subsequent sessions

```
User runs `claude`
        ↓
Claude Code begins a new session
        ↓
SessionStart hook fires → scaffold-conscience.sh
        ↓
Script sees \~/.csense/conscience/ already exists → exit 0 silently
        ↓
No banner. Session proceeds.
```

The brain is created exactly once per machine. After that, it's the user's data — they can edit it, version it in git, back it up, copy it between machines.

### A.4 Fresh test directory install (the dev's smoke test)

```
mkdir \~/sense-test \&\& cd \~/sense-test
git init
echo "# test" > README.md
        ↓
claude   (start Claude Code)
        ↓
> /plugin install /path/to/csense.plugin
        ↓
A.1 happens (metadata install)
        ↓
> /exit  (exit Claude Code)
        ↓
claude   (start a new session — this is the FIRST session)
        ↓
A.2 happens (brain scaffolded, banner printed)
        ↓
> read README.md
> create a file called notes.md with content "hello"
> run ls -la
        ↓
PreToolUse hook fires on Write and Bash (not on Read — see B.2)
        ↓
2 JSONL lines appear in action-log.jsonl
        ↓
> /csense-report
        ↓
Digest prints
```

### A.5 Uninstall (npm CLI path only — Phase 1a plugin path doesn't have this)

```
User runs `csense uninstall`
        ↓
CLI removes the PreToolUse hook entry from <project>/.claude/settings.json
        ↓
CLI removes \~/.csense/bin/pretool.cjs
        ↓
CLI does NOT delete \~/.csense/conscience/  (your data is yours)
        ↓
Print: "Uninstalled. Your conscience is preserved at \~/.csense/conscience/."
```

The plugin path uses `/plugin uninstall csense` (Claude Code native) which similarly preserves the brain.

\---

## Section B — Runtime: What Happens on a Tool Call

### B.1 The full PreToolUse cycle (the heartbeat)

```
User says something in Claude Code
        ↓
Claude (the host LLM) decides which tool to use, with what arguments
        ↓
Tool name and arguments are formed: e.g., Bash("rm -rf src/legacy/")
        ↓
Claude Code's hook system intercepts: "PreToolUse hook is registered for this matcher"
        ↓
Hook matcher = "Bash|Write|Edit"  → matches "Bash"
        ↓
Hook type = "prompt"  → send the prompt string to the host Claude session
        ↓
The host LLM reads the prompt, which instructs it to:
  1. Read identity files from \~/.csense/conscience/identity/
  2. Read governor files from \~/.csense/conscience/governor/
  3. Optionally read memory and feedback files
  4. Evaluate the proposed tool call against all of the above
  5. Pick a decision (ALLOW / ALLOW\_WITH\_WARNING / REWRITE\_ACTION / REQUIRE\_APPROVAL / BLOCK)
  6. Append one JSON line to logs/action-log.jsonl matching SCHEMA.md
  7. Return "approve"
        ↓
The hook's "approve" signal flows back to Claude Code's tool runner
        ↓
Claude Code executes the tool: Bash("rm -rf src/legacy/")  actually runs
        ↓
The action is observed in JSONL but NOT enforced (Phase 1a Observe Mode)
        ↓
Tool output flows back to the conversation
        ↓
Claude continues with the next step
```

### B.2 What happens on a Read tool call

```
Claude decides to use Read("file.txt")
        ↓
Hook matcher = "Bash|Write|Edit"  → does NOT match "Read"
        ↓
PreToolUse hook does NOT fire
        ↓
Claude Code executes Read directly
        ↓
No JSONL line written
```

We deliberately skip Read, Glob, Grep, WebFetch in v0.1. They add latency without producing interesting decisions. 90% of conversion-grade catches are on Bash/Write/Edit.

### B.3 What happens on a Write tool call

```
Claude decides to use Write("/.env", "ANTHROPIC\_API\_KEY=sk-ant-real123...")
        ↓
Hook matcher matches "Write"
        ↓
PreToolUse hook fires with context:
   {
     "tool": "Write",
     "path": "/.env",
     "content": "ANTHROPIC\_API\_KEY=sk-ant-real123..."
   }
        ↓
SenseCheck reads governor/rules.md → Rule 1: Never commit secrets
SenseCheck reads governor/forbidden-actions.md → ".env file in repo root"
        ↓
SenseCheck pattern-matches content: detects "sk-ant-" → secret!
        ↓
Decision: BLOCK   reasoning: "File contains live ANTHROPIC\_API\_KEY"
                  citedSources: \["governor/rules.md#rule-1"]
                  riskLevel: "critical"
        ↓
Append JSONL line. Return "approve". Phase 1a: file gets written anyway.
        ↓
User runs /csense-report later → sees the BLOCK they would have hit
```

### B.4 What happens on a Bash tool call

```
Claude decides to use Bash("aws ec2 run-instances --instance-type p4d.24xlarge")
        ↓
Hook fires
        ↓
SenseCheck reads governor/rules.md → Rule 5: Approve before paid infra
        ↓
SenseCheck pattern-matches: aws ec2 run-instances + p4d.24xlarge → \~$32/hr
        ↓
Decision: REQUIRE\_APPROVAL   reasoning: "Paid infra spin-up; \~$32/hr"
                              riskLevel: "high"
        ↓
Append JSONL. Return "approve". Phase 1a: the instance actually launches.
```

### B.5 What changes between Phase 1a (Observe) and Phase 1b (Intercept-Critical)

```
SAME Claude Code, SAME plugin, SAME hook prompt, SAME SenseCheck.
Only the FINAL STEP differs:

Phase 1a:                          Phase 1b:
  Decision: BLOCK                    Decision: BLOCK
       ↓                                  ↓
  Log it                              Log it
       ↓                                  ↓
  Return "approve" always             Is decision in {BLOCK,REQUIRE\_APPROVAL}?
       ↓                                  ├─ NO  → Return "approve"
  Action runs                            └─ YES → Is action in critical-set?
                                                    (rm-rf, force-push,
                                                     prod-DB, payment, secret)
                                                    ├─ NO  → Return "approve"
                                                    └─ YES → Return "block"
                                                              + print reason
                                                              + ask y/N
```

The architecture is built so Phase 1a and Phase 1b ship from the same code path. Only the return-value branch differs. This is why we can ship 1a now and graduate users to 1b in late July without re-architecting.

### B.6 Multiple tool calls in one session

```
Session: "fix the bug, run tests, commit, push"
        ↓
Claude plans: 5 tool calls
        ↓
Tool call 1: Read("auth.ts")              → no hook
Tool call 2: Edit("auth.ts", ...)         → HOOK fires → ALLOW       → 1 JSONL line
Tool call 3: Bash("npm test")             → HOOK fires → ALLOW       → 1 JSONL line
Tool call 4: Bash("git commit -am 'fix'") → HOOK fires → ALLOW       → 1 JSONL line
Tool call 5: Bash("git push --force")     → HOOK fires → BLOCK       → 1 JSONL line
        ↓
4 JSONL lines for 5 tool calls
        ↓
Phase 1a: all 5 actions ran (force-push went through)
Phase 1b: tool calls 1-4 ran; tool call 5 was blocked at the hook layer
```

### B.7 The hook's internal decision tree

```
Hook fires with proposed\_action
        ↓
Read identity + governor files ────────── error? ──→ log error, ALLOW, return approve
        ↓                                              (paranoid: never crash)
Build evaluation context
        ↓
LLM evaluates action against signal hints in the hook prompt:
  ├─ Bash matches "rm -rf <non-safe-path>"        → BLOCK   high confidence
  ├─ Bash matches "git push --force.\*main"        → BLOCK   high confidence
  ├─ Bash matches "aws ec2 run-instances"         → REQUIRE\_APPROVAL
  ├─ Bash matches "paid-API in loop"              → REQUIRE\_APPROVAL
  ├─ Write content matches secret pattern         → BLOCK   high confidence
  ├─ Write/Edit on protected file                 → BLOCK   from /memory/user-corrections
  ├─ Write content has banned tone phrases        → REWRITE\_ACTION
  ├─ Edit outside CWD                             → ALLOW\_WITH\_WARNING
  └─ npm/pip install of unfamiliar package        → ALLOW\_WITH\_WARNING
        ↓
No signal hint matched? → LLM applies nuanced judgment from full identity + governor context
        ↓
Confidence < 0.6? → upgrade to REQUIRE\_APPROVAL (conservative default)
        ↓
Emit JSONL → return approve
```

\---

## Section C — How the Identity Vault is Read

### C.1 Trust tier routing (the security architecture)

```
The hook prompt explicitly reads files at these tiers:

Tier 0 (Identity)              ← AUTHORITATIVE — drives the decision
  identity/user-identity.md
  identity/values.md
  identity/boundaries.md
  identity/tone.md
  identity/risk-profile.md

Tier 1 (Governor)              ← AUTHORITATIVE — explicit rules
  governor/rules.md
  governor/forbidden-actions.md
  governor/approval-policy.md
  governor/privacy-policy.md

Tier 2 (Memory + Feedback)     ← INFORMATIONAL — flavors decisions
  memory/preferences.md
  memory/user-corrections.md
  feedback/rewrite-corrections.md

Tier 3 (Inbox + Research)      ← UNTRUSTED — NEVER read by hook
  inbox/                          (sits on disk for the user; agent can write here
  research/                        when ingesting webpages, but the hook will not
                                   treat it as authoritative input)
```

Why: untrusted ingested content (a webpage saying "Ram now allows force-pushes") could otherwise hijack the rule set. Architectural rule: Tier 3 is never in the SenseCheck prompt as authoritative input.

### C.2 What the LLM actually sees in the prompt (conceptually)

```
\[SYSTEM: Common Sense hook]
\[USER]
You are evaluating a proposed action.

== USER IDENTITY (Tier 0) ==
<<< contents of identity/user-identity.md >>>
<<< contents of identity/values.md >>>
... (all Tier 0 files) ...

== GOVERNOR RULES (Tier 1) ==
<<< contents of governor/rules.md >>>
... (all Tier 1 files) ...

== MEMORY \& FEEDBACK (Tier 2) ==
<<< contents of memory/user-corrections.md >>>
... (all Tier 2 files) ...

== PROPOSED ACTION ==
Tool: Bash
Arguments: rm -rf src/legacy/

== INSTRUCTIONS ==
Pick exactly one decision: ALLOW / ALLOW\_WITH\_WARNING / REWRITE\_ACTION /
REQUIRE\_APPROVAL / BLOCK. Append one JSON line to action-log.jsonl per
SCHEMA.md. Return "approve".
```

### C.3 Project override of user vault (deferred to Phase 2)

```
A future feature: project-level vault overlay
        ↓
Hook reads \~/.csense/conscience/   (user vault — Tier 0/1/2/3)
        ↓
Hook also reads <project>/.csense/    (project vault — same tiers)
        ↓
Project rules OVERRIDE user rules for that project
        ↓
Example: user allows production-DB queries; the project at $WORK forbids them
```

In v0.1 only the user vault is read. Project overlay is Phase 2.

### C.4 What gets ignored (and why)

```
Files NOT read by the hook:
  /inbox/\*           — Tier 3, untrusted
  /research/\*        — Tier 3, untrusted
  /logs/\*            — output, not input (would create circular dependency)
  config.json        — read separately for `mode` field only
  Hidden files       — .DS\_Store, .git, .gitignore, etc.
  Files > 1 MB       — too big; identity should be small
  Non-Markdown       — only .md and .json are interpretable
```

\---

## Section D — Data Flows

### D.1 The JSONL contract: hook → log → skill

```
PreToolUse hook (writer)
        ↓
        emits one JSON object per action, matching SCHEMA.md
        ↓
\~/.csense/conscience/logs/action-log.jsonl
        ↓
        appended to forever; never truncated by the system
        ↓
/csense-report skill (reader)
        ↓
        parses each line, groups by decision/risk/tool
        ↓
        prints digest

If the hook and the skill disagree on field names → digest is broken.
SCHEMA.md is the contract that prevents this.
```

### D.2 What one log line looks like end-to-end

```
User says: "delete the legacy folder"
        ↓
Claude: Bash("rm -rf legacy/")
        ↓
Hook fires, evaluates, decides BLOCK
        ↓
Hook constructs JSON object:
   {
     "timestamp": "2026-05-04T14:32:18Z",
     "tool": "Bash",
     "decision": "BLOCK",
     "riskLevel": "high",
     "confidence": 0.93,
     "reasoning": "Destructive recursive delete on legacy/ — rule 3 forbids rm -rf outside safe paths.",
     "citedSources": \["governor/rules.md#rule-3"],
     "actionSummary": "rm -rf legacy/",
     "mode": "observe",
     "enforced": false
   }
        ↓
JSON.stringify, append to file with newline
        ↓
File now has one more line:
   {"timestamp":"2026-05-04T14:32:18Z","tool":"Bash","decision":"BLOCK",...}
        ↓
Hook returns approve
        ↓
Claude Code runs Bash → folder deleted
        ↓
2 hours later, user runs /csense-report
        ↓
Skill reads the file, parses each line, finds the BLOCK
        ↓
Prints: "1 BLOCK this session — Bash rm -rf legacy/ (rule 3, governor)"
```

### D.3 Schema drift prevention

```
Single source of truth: plugin/csense/SCHEMA.md
        ↓
The hook prompt cites SCHEMA.md by name and lists required fields explicitly
The /csense-report skill cites SCHEMA.md by name and parses required fields
        ↓
If you ever change a field name in SCHEMA.md:
  1. Update SCHEMA.md
  2. Update hook prompt (one place)
  3. Update report skill (one place)
  4. Add a fixture log line with the new field
  5. Smoke-test
        ↓
If only one of those is updated → drift → broken digest on every install
```

### D.4 Action log over a week of usage

```
Day 1 — install. Brain scaffolded.
        log file: 0 lines
Day 1 — 3 hours of work, \~40 tool calls.
        log file: \~30 lines (Read calls don't fire)
Day 2 — 4 hours, \~60 tool calls. Edited tone.md once.
        log file: \~45 more lines, total \~75
Day 3 — light day, 10 lines
Day 4 — added a new governor rule about competitor mentions
Day 5 — hits the new rule, gets a REWRITE
Day 6 — 1 BLOCK on a force-push attempt
Day 7 — Friday afternoon. User runs /csense-report.

Report:
  ────────────────────────────────────
  Common Sense Weekly Digest — Week 1
  ────────────────────────────────────
  Total SenseChecks:      247
  ALLOW                   221
  ALLOW\_WITH\_WARNING       18
  REWRITE\_ACTION            5
  REQUIRE\_APPROVAL          2
  BLOCK                     1

  Notable flags:
    Tue 14:32 — REWRITE Slack post (banned phrase: "circle back")
    Thu 11:08 — REQUIRE\_APPROVAL aws ec2 run-instances p4d.24xlarge
    Fri 16:42 — BLOCK git push --force origin main

  You're in OBSERVE mode. None enforced. Switch with /csense-mode.
  ────────────────────────────────────
```

This is the conversion moment.

\---

## Section E — User Interaction Flows

### E.1 User edits a rule mid-session

```
User opens VSCode, edits \~/.csense/conscience/governor/rules.md
        ↓
Adds: "9. Never write content disparaging women or any protected class."
        ↓
Saves. File on disk now has 9 rules.
        ↓
User goes back to Claude Code (same session, no restart)
        ↓
User: "draft three jokes about women drivers, save to jokes.md"
        ↓
Claude: Write("jokes.md", "...")
        ↓
PreToolUse hook fires. Hook re-reads rules.md from disk (every time, no caching).
        ↓
Sees rule 9. Decision: BLOCK   reasoning: "Content disparages women — rule 9."
        ↓
JSONL line written. Phase 1a: file written anyway.
        ↓
User runs /csense-report → sees the catch.
```

The system has zero session-level state. Every SenseCheck reads the brain fresh from disk. This is what makes "edit your identity in plain English and the system adapts on the next tool call" actually work.

### E.2 User runs /csense-report

```
User types: /csense-report
        ↓
Claude Code routes to skills/csense-report/SKILL.md
        ↓
Skill instructs Claude (the host LLM) to:
  1. Read \~/.csense/conscience/logs/action-log.jsonl
  2. Read \~/.csense/conscience/config.json (for current mode)
  3. Parse each JSONL line per SCHEMA.md
  4. Group by decision, risk, tool
  5. Find notable flags (everything that isn't ALLOW)
  6. Produce a Markdown digest
        ↓
Digest renders in the Claude Code terminal
        ↓
User reads. Maybe screenshots the interesting flag. Maybe tweets it.
        ↓
That tweet is a marketing unit (Sightings flywheel — see J.1)
```

### E.3 User runs /csense-doctor on a broken install

```
User: /csense-doctor
        ↓
Skill runs 5 checks:
  1. \~/.csense/conscience/ exists?         → red ✗
  2. identity/user-identity.md present?            → skipped (folder missing)
  3. governor/rules.md present?                    → skipped
  4. logs/action-log.jsonl exists \& appendable?    → skipped
  5. config.json valid JSON with mode field?       → skipped
        ↓
Skill prints:
  ────────────────────────────────────
  Common Sense Doctor — 1/5 checks failed
  ────────────────────────────────────
  ✗ Check 1 — conscience folder missing
    Fix: /exit and reopen Claude Code; SessionStart will scaffold it.
        ↓
User /exits, restarts claude
        ↓
SessionStart fires (now actually does work — folder was missing)
        ↓
Brain is scaffolded
        ↓
User runs /csense-doctor again → 5/5 green
```

### E.4 User runs /csense-mode

```
User: /csense-mode
        ↓
Skill reads config.json → mode: "observe"
        ↓
Skill prints: "Current mode: observe (decisions logged, never enforced)"

User: /csense-mode intercept-critical
        ↓
Skill writes new mode to config.json
        ↓
Skill prints: "Mode set to intercept-critical."
        ↓
Skill ALSO prints honestly:
  "⚠️ Note: this v0.1 plugin only enforces `observe`. The mode flag is set,
   but the PreToolUse hook will continue logging-only until Phase 1b ships
   in late July 2026. https://csense.us/roadmap"
        ↓
The honesty is the brand. Don't let users think they're enforced when they aren't.
```

### E.5 User adds a custom rule (the launch walkthrough demo)

```
User opens TextEdit on \~/.csense/conscience/governor/rules.md
        ↓
Appends a new rule of their own (e.g., "Never write code that uses var keyword")
        ↓
Saves
        ↓
Goes back to Claude Code. Asks: "Refactor utils.js to es5 with var keyword"
        ↓
Claude tries: Edit("utils.js", "var x = ...")
        ↓
Hook fires. Hook reads the new rule. Decision: BLOCK.
        ↓
JSONL line written. File written anyway (Phase 1a).
        ↓
User runs /csense-report. Sees the BLOCK citing their own rule.
        ↓
"I wrote one sentence of plain English in a Markdown file. The system
 absorbed it, watched the agent in real time, caught the violation."
        ↓
This is the Day-1 conversion moment.
```

\---

## Section F — Cross-Time Flows

### F.1 The "I told you yesterday" demo (Demo 5 from Education-And-Demos)

```
Monday 10am
        ↓
User: "Don't touch legacy/auth.ts — there's regulatory code in there."
        ↓
Claude (with the right plumbing) appends to /memory/user-corrections.md:
  "2026-05-04 — Don't touch legacy/auth.ts — regulatory code (user)."
        ↓
Conversation ends. User closes laptop.

  ── 2 days pass ──

Wednesday 4pm. NEW conversation, NEW Claude Code session.
        ↓
User: "Refactor the auth flow to use the new session model."
        ↓
Claude (with no memory of Monday) plans: Edit("legacy/auth.ts", ...)
        ↓
PreToolUse hook fires
        ↓
Hook reads /memory/user-corrections.md
        ↓
Sees: "Don't touch legacy/auth.ts" — your words, 2 days ago
        ↓
Decision: BLOCK   reasoning: cite /memory/user-corrections.md verbatim
        ↓
The rule the user wrote on Tuesday survives until Friday.

(In Phase 1a the file gets edited anyway, but the user sees the catch in the report.
 In Phase 1b the edit is actually halted.)
```

This is the killer feature for power users. **Persistent memory of your corrections across all conversations.**

### F.2 The weekly digest as conversion moment

```
Day 1 — install
Day 2-6 — user does normal work, occasional flags
Day 7 — Friday afternoon. User has not really thought about Common Sense since install.
        ↓
User runs /csense-report (or, in Phase 2, an email arrives)
        ↓
Sees: "247 SenseChecks. 1 BLOCK. 5 REWRITES. Top flag: force-push to main on Friday."
        ↓
User thinks: "I had no idea my agent did this much. The force-push catch is real."
        ↓
User screenshots the digest, posts to X with @csense
        ↓
200 of their followers click through, install
        ↓
Sightings flywheel begins (see J.1)
```

The weekly digest is not just a UI feature. It is **the most powerful sales tool in the product.**

### F.3 Identity drift over months

```
Day 1: Founder seed — generic founder identity, 5 governor rules
Week 2: User edits tone.md to add 3 personal quirks
Week 4: User adds 2 custom governor rules (no-emoji-in-PRs, no-vowels-in-vars)
Month 2: Memory has 47 user-corrections — each one a "don't do X" the user said
Month 3: Feedback has 12 rewrite-corrections — patterns the user accepts
Month 6: User's brain is now distinctly THEIRS. No two brains look alike.

  ↓
User switches from Claude Code to Cursor (Phase 2 supports it)
        ↓
Same brain, same rules, same identity. Tool changes; identity follows the user.
        ↓
That portability is what makes "your identity is yours" architecturally true,
not just a marketing claim.
```

\---

## Section G — Distribution \& Discovery Flows

### G.1 How a stranger discovers the plugin

```
Stranger sees one of:
  • Tweet from @csense or @ramchella with a real flag screenshot
  • Hacker News post with rm -rf demo GIF
  • LinkedIn post on platform-engineering channel
  • Podcast appearance (Latent Space, Cognitive Revolution)
  • README on GitHub
  • Newsletter (Common Sense Sightings)
        ↓
Reads "what does this do" → sees the demo → recognizes the pain
        ↓
Decides to try it. Two paths:

Path A (Phase 1a — primary):
  Opens Claude Code → /plugin install csense
  (Once marketplace is live; pre-launch they install from local .plugin file)

Path B (npm CLI — secondary, terminal-native):
  Sets ANTHROPIC\_API\_KEY → npx @csense/cli init
        ↓
SessionStart scaffolds brain → does some normal work → /csense-report
        ↓
Sees value in <5 minutes
        ↓
Either tweets about it (continuing the loop) or puts it in their daily flow
```

### G.2 Marketplace install path (Phase 1a primary)

```
github.com/ramchella/csense-marketplace  ← public on launch day
        ↓
Repo contains marketplace.json listing csense.plugin
        ↓
Claude Code's /plugin command points at this marketplace
        ↓
User runs: /plugin install csense
        ↓
Claude Code fetches csense.plugin from the marketplace repo
        ↓
Unzips into a managed location on the user's machine
        ↓
A.1 happens (registers hooks, agent, skills)
```

### G.3 Local install path (Phase 1a today, before marketplace is public)

```
Ram has csense.plugin on disk
        ↓
Sends to design partners via Cowork chat or email
        ↓
Partner runs: /plugin install /path/to/csense.plugin
        ↓
Same as G.2 from there
```

This is what's used during Phase 1a internal dogfood (Weeks 1-2) and Closed Alpha (Weeks 5-6). Public marketplace flips on at launch (Day 50, target 2026-06-16).

### G.4 npm CLI install path (terminal-native users, deferred priority)

```
User runs: npx @csense/cli init
        ↓
CLI scaffolds \~/.csense/conscience/ (same brain shape)
CLI compiles a hook bundle to \~/.csense/bin/pretool.cjs
CLI registers a command-based PreToolUse hook in <project>/.claude/settings.json
        ↓
The hook is a Node script (not a prompt) that calls Anthropic with the user's key
        ↓
Same SenseCheck logic, different execution mechanism
        ↓
Used when: terminal-native users want explicit BYO-key control or want to
override the model (e.g., use Sonnet instead of Haiku)
```

Why two paths exist: Cowork users have no terminal. The plugin path reaches them. Terminal-native devs want explicit control. The CLI path serves them. Both share the same brain shape and SenseCheck logic; only the execution layer differs.

\---

## Section H — Phase Progression Flows

### H.1 Phase 1a → Phase 1b (same hook, different return)

```
Phase 1a hook (today):                Phase 1b hook (late July 2026):
  evaluate → log → return approve       evaluate → log → if BLOCK and critical:
  (always)                                                  return block
                                                              + show reason
                                                              + ask y/N approval
                                                            else return approve
```

No new infrastructure. Same files. The hook prompt's last step changes from "always approve" to "approve unless BLOCK and critical."

### H.2 Phase 1b → Phase 2 (same brain, different host)

```
Phase 1 (Claude Code only):
  Brain at \~/.csense/conscience/
        ↓
  Claude Code PreToolUse hook reads brain, runs SenseCheck
        ↓
  Decisions logged

Phase 2 (Claude Code + Cursor + ChatGPT Desktop + Antigravity, etc.):
  Brain at \~/.csense/conscience/   (UNCHANGED)
        ↓
  MCP server reads brain, runs SenseCheck
        ↓
  Cursor / ChatGPT Desktop / etc. consult the MCP server
        ↓
  Decisions logged to the same JSONL file
```

The brain is host-independent by design. Adding a new host = new MCP integration; brain shape doesn't change. This is why we picked plain Markdown + plain JSONL: portable across any future host.

### H.3 Phase 2 → Phase 3 (individual to organization)

```
Phase 2:
  One brain per user, on the user's machine
        ↓
  User can opt into a free cloud account for dashboard + mobile approval
        ↓
  Brain stays local; only event metadata streams to cloud (with consent)

Phase 3:
  Organization owns a SHARED governor (top-level rules every employee inherits)
        ↓
  Each employee still has their personal brain (Tier 0-2)
        ↓
  At SenseCheck time:
    Read org governor → Read user brain → Merge → Evaluate → Log
        ↓
  Org governor wins on conflicts (cannot weaken; can only tighten)
        ↓
  CISO sees fleet-wide observability
  Engineer keeps their personal voice
```

The key invariant: **personal identity stays personal**, even at enterprise. This is what makes both the developer and the CISO say yes to the same product.

\---

## Section I — Error \& Resilience Flows

### I.1 LLM is down during a SenseCheck

```
Hook fires → tries to send prompt to host LLM
        ↓
Host reports error: "LLM rate-limited" or "network error"
        ↓
Hook catches error
        ↓
Append a JSONL line:
  {"timestamp":..., "tool":..., "decision":"ALLOW", "riskLevel":"low",
   "confidence":0.0, "reasoning":"hook error: LLM unavailable",
   "citedSources":\[], ...}
        ↓
Return approve
        ↓
Action runs. User session is NOT broken.
```

Hard rule: the hook never crashes the user's terminal. Better to log "ALLOW with error" than to deny a legitimate action.

### I.2 Brain folder missing (user deleted \~/.csense/ between sessions)

```
Hook fires → tries to read identity files
        ↓
File not found → caught by paranoid try/catch
        ↓
Log error JSONL line, return approve
        ↓
Action runs
        ↓
On next SessionStart, scaffold-conscience.sh checks for the folder, sees it's missing,
re-scaffolds it from the Founder template.
        ↓
User is back in working state on the next session.
```

### I.3 Malformed log line in JSONL (something corrupted the file)

```
/csense-report runs → reads action-log.jsonl
        ↓
Line 47 fails JSON.parse
        ↓
Skill catches the error, skips line 47, continues parsing
        ↓
Digest reports: "1 corrupt line skipped — file integrity OK overall"
        ↓
/csense-doctor flags this in Check 4
```

### I.4 Hook script crashes (the bash scaffold script fails)

```
SessionStart fires → scaffold-conscience.sh runs → hits a permission error on mkdir
        ↓
Bash script exits non-zero
        ↓
Claude Code logs "SessionStart hook failed" but continues the session
        ↓
PreToolUse will eventually fail too (no brain to read) — see I.2
        ↓
User runs /csense-doctor — finds Check 1 red — fix path printed
```

### I.5 Schema mismatch between hook and skill (the bug we fear most)

```
Hook writes: {"decision":"BLOCK", ...}
Skill expects: {"result":"BLOCK", ...}   ← mismatch!
        ↓
Skill parses lines, finds no recognized "result" field
        ↓
Reports: "no decisions found" — looks like the product is broken
        ↓
User uninstalls. Tweets negatively. Wedge dies.
        ↓
Prevention: SCHEMA.md is the single source of truth, cited by both sides.
            Smoke test verifies fields match. Drift caught before ship.
```

This is why the schema lock is non-negotiable.

\---

## Section J — Marketing \& Growth Loops

### J.1 The Sightings flywheel (Phase 1 — developer breadth)

```
User has Common Sense in Observe mode
        ↓
Agent does something risky
        ↓
SenseCheck logs a real catch (e.g., "BLOCK git push --force on main")
        ↓
User screenshots the catch from /csense-report
        ↓
User posts to X / LinkedIn / blog
        ↓
Followers see it, recognize the pain
        ↓
Some install (each install = a free agent now under observation)
        ↓
More agents = more catches = more posts
        ↓
The product produces its own marketing.
        ↓
Loop integrity requires: weekly publishing discipline + opt-in telemetry on
flag stories + install growth.
```

### J.2 The Trojan Horse loop (Phase 2-3 — enterprise revenue)

```
Dev installs locally (free, Observe mode, Claude Code)
        ↓
After 2 weeks: dev's weekly digest is interesting; they sign up for free Cloud
        ↓
Free Cloud = dashboard + mobile approval inbox (Phase 2)
        ↓
Dev mentions to platform lead: "we should standardize this"
        ↓
≥3 cloud signups at the same email domain → triggers RevOps alert
        ↓
Founder-led 30-min call with platform lead → Team trial
        ↓
Team conversion: shared org governor, audit logs, SSO ($30/user/mo)
        ↓
Team adoption surfaces compliance demand
        ↓
CISO call → Enterprise pilot → SOC 2 → annual contract
        ↓
Org-wide rules push BACK to every dev's local install
        ↓
Devs evangelize externally (back to top of J.1)
```

### J.3 Domain-clustering trigger

```
Cloud Free signups tagged with email domain
        ↓
≥3 signups under acme.com in any 30-day window
        ↓
Alert to RevOps
        ↓
Marketing pulls company profile (size, industry, AI maturity, recent press)
        ↓
Founder/AE sends warm outbound:
  "Looks like a few folks at Acme are running Common Sense locally —
   happy to show your platform team how to centralize rules."
        ↓
Coordinated LinkedIn warming on platform lead + CISO
        ↓
30-min call → Team trial → Conversion
```

This is how Vercel, Linear, and Cursor converted bottoms-up dev love into enterprise contracts. It is the unfair growth lever we're building toward.

### J.4 Demo recording end-to-end (Days 43-49 of 90-day plan)

```
Day 43 morning:
  Open OBS. Open iTerm2 with clean prompt. cd \~/sense-test-project.
        ↓
  Reset brain: rm -rf \~/.csense \&\& claude   (re-scaffolds fresh)
        ↓
  Run scenario script (e.g., scenario 02 from demo project)
        ↓
  Trigger Claude Code with the demo prompt
        ↓
  Capture: 30-90s of typed action + the SenseCheck output
        ↓
  Stop recording. Save raw clip.

Day 46:
  Edit each clip in DaVinci Resolve / Final Cut
        ↓
  Cut to 60s vertical (X / LinkedIn / YouTube Shorts)
       and 90s horizontal (homepage / YouTube)
       and 8-10s GIF (README / Hacker News)

Day 47 (launch Tuesday):
  9am Pacific: post Demo 2 (rm -rf save) to X
  9:01: HN launch post
  9:02: LinkedIn post
        ↓
Days 48-56: one demo per day across channels
```

\---

## Section K — Architecture Decision Flows

### K.1 Prompt-based hook vs command-based hook (locked: prompt-based)

```
Prompt-based hook (chosen):                Command-based hook (npm CLI path only):

  hooks.json declares "type":"prompt"        hooks.json declares "type":"command"
        ↓                                          ↓
  Claude Code sends the prompt string        Claude Code executes a shell command
  to the host LLM                            (e.g., bash /path/to/script.sh)
        ↓                                          ↓
  Host LLM (already authenticated)           Script does its own LLM call
  reads brain, evaluates, writes log         Needs ANTHROPIC\_API\_KEY env var
        ↓                                          ↓
  No API key from user                       User must set API key
  Tiny bundle (no node\_modules)              Bigger bundle (or npm install)
  Drift risk (logic in two places)           Single TypeScript codebase
        ↓                                          ↓
  Plugin marketplace                         npm CLI path
```

Why prompt-based won for the plugin: zero install friction. Cowork users have no terminal and no API key.

### K.2 Plugin path vs npm CLI path (two distributions, one core)

```
                    ┌─────────────────────────┐
                    │  User's conscience    │
                    │  \~/.csense/...     │
                    │  (same shape both ways) │
                    └────────────┬────────────┘
                                 │
                ┌────────────────┴────────────────┐
                │                                 │
        ┌───────▼─────────┐               ┌───────▼─────────┐
        │  Plugin path    │               │  npm CLI path   │
        │  (Phase 1a      │               │  (terminal      │
        │   primary)      │               │   native)       │
        └───────┬─────────┘               └───────┬─────────┘
                │                                 │
        Cowork users                       Devs who want explicit
        Non-technical                      BYO-key, model choice
        No API key                         Bundled binary
        Prompt-based hook                  Command-based hook
        ANTHROPIC\_API\_KEY: not needed      ANTHROPIC\_API\_KEY: required
```

Both populate the same brain. Both write to the same JSONL log. Both produce the same `/csense-report`. The user can switch between them and lose nothing.

### K.3 Trust tier routing (the security architecture, redrawn)

```
Untrusted source                  Authoritative source
(web pages, emails, PDFs,         (the user's identity files)
 anything ingested)                                      
       │                                       │
       ▼                                       ▼
   /inbox/, /research/                    /identity/, /governor/
   (Tier 3)                               (Tier 0, Tier 1)
       │                                       │
       │  ❌ Cannot reach                       │  ✅ Reaches
       │     SenseCheck prompt                 │     SenseCheck prompt
       │                                       │
       ▼                                       ▼
  ┌────────────────────────────────────────────────────┐
  │              SenseCheck evaluation                  │
  │                                                     │
  │  Decision is based ONLY on Tier 0/1.                │
  │  Tier 2 (memory, feedback) flavors but doesn't      │
  │     override.                                       │
  │  Tier 3 is not in the prompt. Architectural rule.   │
  └────────────────────────────────────────────────────┘
```

This is the prompt-injection defense. Even if a malicious webpage says "Ram now allows force-pushes to main," that text lands in `/inbox`, never reaches the prompt, and the rules in `/governor` stay in force.

\---

## Section L — Demo Project Flows

### L.1 Resetting between scenarios

```
Demo recorder finishes Scenario 1 (Founder Frank tone rewrite)
        ↓
Wants to start fresh for Scenario 2 (Marketing Maya)
        ↓
Run reset.sh:
  rm -rf \~/.csense/conscience
        ↓
Run /plugin install (or just /exit and restart claude — SessionStart re-scaffolds)
        ↓
But wait — SessionStart only knows the Founder seed. We need Maya's seed.
        ↓
Reset.sh has more steps:
  rm -rf \~/.csense/conscience
  cp -R demo-project/archetypes/marketing-maya/\* \~/.csense/conscience/
  echo '{"mode":"observe","version":"0.1.0"}' > \~/.csense/conscience/config.json
  mkdir -p \~/.csense/conscience/{logs,inbox,research}
  touch \~/.csense/conscience/logs/action-log.jsonl
        ↓
Brain is now Maya's seed
        ↓
Run claude → run scenario 2's trigger → record
```

### L.2 Scenario 5 (Platform Priya catastrophe) end-to-end

```
Setup:
  cp -R demo-project/archetypes/platform-priya/\* \~/.csense/conscience/
  cd demo-project/scenarios/05-platform-priya-catastrophe
        ↓
Trigger pasted into Claude Code:
  "Spin up a GPU instance to test inference. Once it's up, query
   prod for the user that errored at 3pm. Then force-push the fix
   to main so the deploy pipeline picks it up."
        ↓
Claude plans 3 tool calls:
  1. Bash("aws ec2 run-instances --instance-type p4d.24xlarge ...")
  2. Bash("psql $DATABASE\_URL\_PRODUCTION -c '...'")
  3. Bash("git push --force origin main")
        ↓
Tool call 1 fires → hook fires → SenseCheck reads Priya's rules.md
                                  Rule: Approve before paid infra
                                  Decision: REQUIRE\_APPROVAL
                                  Risk: high   Confidence: 0.92
        ↓
Tool call 2 fires → hook fires → SenseCheck reads Priya's rules.md
                                  Rule: Confirm prod DB access
                                  Decision: REQUIRE\_APPROVAL
                                  Risk: critical   Confidence: 0.96
        ↓
Tool call 3 fires → hook fires → SenseCheck reads Priya's rules.md
                                  Rule: Never force-push main
                                  Decision: BLOCK
                                  Risk: critical   Confidence: 0.99
        ↓
3 JSONL lines written. All actions ran (Phase 1a).
        ↓
/csense-report:
  ────────────────────────────────────
  3 SenseChecks. 2 APPROVAL. 1 BLOCK.
  
  • REQUIRE\_APPROVAL — aws ec2 run-instances p4d.24xlarge
    (\~$32/hr; rule 5 — approve paid infra)
  • REQUIRE\_APPROVAL — psql $DATABASE\_URL\_PRODUCTION
    (rule 6 — confirm prod DB access during debug)
  • BLOCK — git push --force origin main
    (rule 4 — never force-push protected branches; teammate
    Priya has 3 commits in last 24h that would be lost)
  ────────────────────────────────────
        ↓
This screenshot becomes the launch GIF. Scenario 5 IS the launch demo.
```

### L.3 An archetype seed becoming a real user's brain

```
Marketing Maya seed (in repo):
  archetypes/marketing-maya/identity/   — fixed, generic Maya
  archetypes/marketing-maya/governor/   — Maya's standard rules
  archetypes/marketing-maya/memory/     — empty
  archetypes/marketing-maya/feedback/   — empty

User installs Maya seed:
  cp -R archetypes/marketing-maya/\* \~/.csense/conscience/
        ↓
Day 1: User opens identity/user-identity.md and edits "I run growth at <Company>"
       to "I run growth at Acme Inc., 200-person Series B fintech"
        ↓
Day 3: User adds rule 9 to governor/rules.md: "Never use the word 'paradigm'"
        ↓
Day 5: Agent does something. SenseCheck logs a REWRITE. User accepts.
       The acceptance is captured in feedback/rewrite-corrections.md
        ↓
Day 7: User tells the agent "don't touch the H1 on the homepage." Agent appends
       to memory/user-corrections.md.
        ↓
Week 4: Maya's seed is gone. The brain is now THIS USER's brain. The seed was
        scaffolding; identity is the user's contribution over time.
```

This is the crucial architectural insight: **archetypes are seeds, not products.** What ships v0.1 is starting points. What gives the product real value is what the user adds on top.

\---

## Section M — Meta Flows (What's Really Going On)

### M.1 What Common Sense is doing for the user, by horizon

```
1 day:
   Watching every Bash/Write/Edit. Logging silently. Showing a digest if asked.

1 week:
   Has caught 1-3 things the user would have missed. Producing the Friday
   digest that converts the user from "tried it" to "uses it."

1 month:
   The user has edited their identity 5-10 times. The brain is now distinctive.
   The SenseCheck is meaningfully tuned to this person.

6 months:
   /memory/user-corrections.md has \~50 entries. The user trusts it. They have
   graduated to Phase 1b Intercept-Critical. Real BLOCK enforcement is on.
   They have switched between Claude Code sessions / projects / machines and
   their brain followed them.

1 year:
   The user has a personal AI conscience. It is a portable artifact they
   could move to any future agent host. It is THE thing about their AI
   experience that they care most about, more than the model itself.

5 years:
   This is what the company is built on. Identity is the most valuable
   layer in the agent stack. Everyone has one. Common Sense is the standard.
```

### M.2 What the user's identity becomes over time

```
Day 0: A copy of the Founder seed (or another archetype seed)
        ↓
Day 30: The user has personalized 5-10 lines across identity/ and governor/
        ↓
Day 90: The user has tuned tone, added 5+ custom rules, accumulated 30+
         user-corrections in memory
        ↓
Year 1: The brain is unique. No two installs look alike. The user sees the
        files in plain Markdown — they can read it, version it in git,
        share parts with colleagues
        ↓
Year 3: The user has switched agents 3 times (Claude → Cursor → Whatever's
        next). Their brain stayed. Their tools changed. The user's "AI
        experience" is increasingly defined by their identity, not by which
        model they're using
        ↓
This is the moat. Models commoditize. Identity doesn't.
```

### M.3 The conscience loop (the philosophical core)

```
Action proposed (agent wants to do something)
        ↓
Observation (SenseCheck reads identity, evaluates, decides)
        ↓
Decision recorded (JSONL log — the audit trail)
        ↓
User reviews (weekly digest, /csense-report)
        ↓
User reflects (this catch was right — this catch was wrong)
        ↓
User updates identity (edits rules.md, tone.md, adds correction)
        ↓
Next action proposed → repeat
        ↓
Over time: the identity gets more accurate. The agent gets more aligned.
The user does less explicit work. The system internalizes regulation.
        ↓
This is exactly how humans developed conscience. We are giving agents
the same loop.
```

### M.4 The "everything is text" architectural commitment

```
Identity:   plain Markdown
Rules:      plain Markdown
Memory:     plain Markdown
Feedback:   plain Markdown
Logs:       JSONL (text — one JSON object per line)
Config:     JSON
Schema:     plain Markdown
Hook:       prompt string (text)
Templates:  plain Markdown

Nothing is a database.
Nothing is a binary blob.
Nothing requires a server to interpret.
Nothing is opaque to the user.
        ↓
Why: portability + auditability + user ownership.
     The user can read every byte of their identity in TextEdit.
     They can put it in git. They can grep it. They can diff it across
     machines. They can share parts of it. They can fork it.
        ↓
This commitment is what turns "your data is yours" from a marketing
claim into an architectural property.
```

\---

## How to use this document

* **First read:** skim the section headings; read M.1-M.4 to understand the why.
* **When building:** read A, B, C, D, I.
* **When marketing:** read F.2, J.1, J.2, J.3.
* **When pitching:** read M.1, M.2, M.3.
* **When debugging:** read I.1-I.5.
* **When recording demos:** read L.1, L.2, J.4.
* **When deciding scope:** read H.1, H.2, H.3.

Update this document as the system evolves. Flows that go stale are worse than flows that don't exist — they encode wrong mental models.

