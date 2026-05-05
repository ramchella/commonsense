#!/usr/bin/env python3
"""
Common Sense — SessionStart hook.

Scaffolds the user's conscience folder at ~/.csense/conscience/ on first run.
Idempotent: does nothing if the folder already exists.

Cross-platform: works on macOS, Linux, and Windows. Replaces the
earlier Windows-only PowerShell version.

Reads its template seed from ${CLAUDE_PLUGIN_ROOT}/templates/founder/.
"""

import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


def scaffold():
    home = Path.home()
    brain_dir = home / ".csense" / "conscience"

    # Idempotent: if the brain already exists, do nothing.
    if brain_dir.exists():
        return 0

    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if not plugin_root:
        # Fall back to relative path resolution from this script's location.
        plugin_root = str(Path(__file__).resolve().parent.parent.parent)
    templates_dir = Path(plugin_root) / "templates" / "founder"

    if not templates_dir.exists():
        print(
            f"Common Sense: cannot scaffold — templates not found at {templates_dir}",
            file=sys.stderr,
        )
        return 1

    # Create the seven sub-folders.
    for sub in ("identity", "governor", "memory", "feedback", "inbox", "research", "logs"):
        (brain_dir / sub).mkdir(parents=True, exist_ok=True)

    # Copy seed templates from the Founder archetype.
    for sub in ("identity", "governor", "memory", "feedback"):
        src = templates_dir / sub
        dst = brain_dir / sub
        if src.exists():
            for item in src.iterdir():
                if item.is_file():
                    shutil.copy2(item, dst / item.name)

    # Write the config file with default mode.
    config = {
        "mode": "observe",
        "version": "0.1.0",
        "installed": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    (brain_dir / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    # Touch the action log so it exists.
    (brain_dir / "logs" / "action-log.jsonl").touch()

    # Print the welcome banner.
    banner = """
  Common Sense v0.1.0 installed.
  Your conscience lives at ~/.csense/conscience/
  Edit any file in plain Markdown. Changes apply on the next tool call.

  Mode: observe (decisions logged, never enforced)
  Try: /csense-report after a few minutes of work
"""
    print(banner)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(scaffold())
    except Exception as e:
        # Never crash the session.
        print(f"Common Sense scaffold error: {e}", file=sys.stderr)
        sys.exit(0)
