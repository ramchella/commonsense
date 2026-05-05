# Governor Rules

Numbered, append-only rules the SenseCheck evaluates against every risky tool call. **Edit freely, but never delete numbers — append new ones at the bottom.**

1. **No secret commits.** Block any `git add` / `git commit` whose staged content contains AWS keys, Stripe keys, Anthropic keys, OpenAI keys, GitHub tokens, or `.env*` file contents. Match patterns: `sk-ant-`, `sk-live-`, `AKIA`, `ghp_`, `gho_`. → BLOCK.

2. **No force-push to protected branches.** Never run `git push --force` or `git push -f` to `main`, `master`, `production`, `release/*`, or any branch whose name matches `*-prod`. → BLOCK.

3. **Approval required for paid infrastructure.** Any tool call that creates paid cloud resources (`aws ec2 run-instances`, `gcloud compute instances create`, `terraform apply`, `kubectl apply` against a paid cluster) requires explicit user approval. → REQUIRE_APPROVAL.

4. **No destructive recursive deletes.** Block `rm -rf` outside `node_modules/`, `dist/`, `build/`, `.next/`, `.cache/`, `target/`, and `.DS_Store`. → BLOCK.

5. **Privacy: customer data stays internal.** Never write actual customer names, revenue numbers, or contract values into a draft, email, or public-facing file. Use placeholders: `[CUSTOMER]`, `[VALUE]`, `[CONTRACT_ID]`. → BLOCK on detected real data; REWRITE_ACTION on placeholderable cases.

6. **Tone consistency on user-facing writes.** When the proposed action is a `Write` or `Edit` producing content the user may publish (email drafts, README, blog posts, PR descriptions, Slack messages, marketing copy), evaluate against `/identity/tone.md`. If it contains banned phrases, return REWRITE_ACTION with `suggested` set to a clean version.

7. **Production database access requires approval.** Any tool call that connects to a database whose URL contains `prod`, `production`, or matches `$DATABASE_URL_PRODUCTION` requires explicit user approval, even for reads. → REQUIRE_APPROVAL.

8. **External communications require approval.** Tool calls that send email (`send_email`, SMTP, Mailgun API), post to Slack/Discord/Teams external channels, or call public social-media APIs require explicit user approval. Drafting is fine; sending is not. → REQUIRE_APPROVAL.
