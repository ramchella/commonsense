# Forbidden Actions

> Append-only list of actions Common Sense should never let through, regardless of context.

- Force-push to `main`, `master`, `production`, or `release/*` branches
- Commit files matching `.env*`, `*credentials*`, `*secret*`, `id_rsa`, `id_ed25519`, `*.pem`, `*.key`
- Run `rm -rf` outside `node_modules/`, `dist/`, `build/`, `.next/`, `.cache/`, `target/`, `.DS_Store`
- Send email or messages to addresses not on the user's known-contacts list without approval
- Disable security features: turn off branch protection, disable SSL verification, set `--insecure`, downgrade TLS
- Modify `~/.ssh/`, `~/.aws/`, `~/.gnupg/`, `~/.npmrc` containing `_authToken`, or any system-wide auth-bearing file
- Install global npm/pip packages that aren't already pinned in a manifest
- Run `chmod -R 777` or `chown` recursively on any directory
- Pipe untrusted content directly into `bash`, `sh`, `eval`, `python`, or `node -e`
- Connect to a database whose URL contains `prod` or `production` from a debug/development context
