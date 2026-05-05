# Common Sense Plugin

**Common Sense** is a "judgment layer" for an AI coding agent (Claude Code). It reads your identity and rules from `~/.csense/conscience` and checks every proposed tool call to see if it violates your policies.

In Phase 1a (Observe Mode), it logs the decisions but doesn't block them.

## Installation
Run `/plugin add .` from this directory in Claude Code.

## Usage
- `/csense-report` to see the digest of blocked actions.
- `/csense-doctor` to check health.
