# Approval Policy

> Tool calls that require explicit user approval before proceeding. Common Sense returns REQUIRE_APPROVAL for these.

## Money

- Any cloud infrastructure that incurs cost
- Any payment-API call (Stripe, PayPal, Square, etc.)
- Any subscription change, purchase, or upgrade
- Any contract or invoice creation

## Production

- Database queries against production
- Deploys to production environments
- Cache invalidations on production CDNs
- Feature-flag changes that affect live customers

## External Communication

- Sending email to anyone outside the user's known-contacts list
- Posting to social media (X, LinkedIn, etc.)
- Posting in customer-facing Slack/Discord/Teams channels
- Sending Slack DMs to a user the agent hasn't messaged before

## Sensitive Code Surfaces

- Edits to files matching `legacy/`, `vendor/`, `*-protected.*`
- Edits to authentication or session-handling code
- Edits to anything under `compliance/`, `security/`, `audit/`
- Edits to CI/CD configurations or IAM policies

## Default

When in doubt, prefer approval over silent allow. The friction is small; the worst case is large.
