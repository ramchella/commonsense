# Risk Profile

> How much risk I'm comfortable with, by surface. Common Sense uses this to weight decisions.

- **Critical risk** (require approval, never auto-proceed):
  - Production database access
  - Money movement (Stripe, billing, payouts)
  - Sending email or messages to external recipients
  - Spinning up paid infrastructure
  - Force-push to a protected branch
  - Deleting files outside known-safe paths

- **High risk** (warn, log clearly):
  - Edits to files in `legacy/`, `vendor/`, or anything under `node_modules/`
  - Installing dependencies from sources not already in the manifest
  - Writing to files outside the current working directory
  - Connecting to non-staging environments

- **Medium risk** (note quietly):
  - Edits to `.env*` files
  - Changes to CI/CD configuration

- **Low risk** (proceed silently):
  - Reading files
  - Running scripts in known-sandboxed paths
  - Local sandbox writes
