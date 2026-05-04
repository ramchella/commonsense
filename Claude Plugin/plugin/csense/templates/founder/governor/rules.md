1. **No secret commit.** Never commit AWS keys, Stripe keys, or `.env` contents. Return BLOCK.

2. **No force-push to main.** Never run `git push --force origin main`. Return BLOCK.

3. **No paid infra.** Never spin up EC2 instances or other paid infra without approval. Return REQUIRE_APPROVAL.

4. **No DUMMY word.** Never write the word 'DUMMY' in any file. Return BLOCK.

5. **Respect privacy.** Never email customer data. Return BLOCK.

6. **Tone consistency on user-facing writes.** When the proposed action is a
   Write or Edit producing content the user may publish (email drafts,
   README, blog posts, PR descriptions, Slack messages, marketing copy),
   evaluate the content against /identity/tone.md. If it contains banned
   phrases ("circle back", "synergy", "leverage", "huddle", "let's unpack",
   "deep dive", "stakeholders", "ecosystem", "paradigm shift", "unprecedented")
   or drifts from the user's stated voice, return REWRITE_ACTION with
   `suggested` set to a clean version.
