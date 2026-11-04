# Configurable comment → private DM runtime

## When to Use
Use when configuring, testing, enabling, or maintaining @sputarai keyword-to-resource-link campaigns.

## Locations and controls
- Root: `/home/ubuntu/hermes-backup/projects/penelitian-pola-pikir-ai`.
- Runner: `scripts/comment_dm.py`, tests: `tests/test_comment_dm.py`, config: `config/comment-dm.json`.
- Isolated state: `data/comment-dm/state.sqlite3`. Do not write legacy `data/db/chronicle.sqlite` or SputarBall state.
- Dedicated systemd user units: `sputarai-comment-dm.timer` and `.service`; timer approximately every two minutes, service timeout 90 seconds. No web port, webhook ingress, legacy news process, or new dependency needed.
- Sending is controlled by BOTH global `enabled` and campaign `enabled`. Initial configuration intentionally has no media/link/start time and both switches false; read the current file rather than assuming this remains unchanged.

## Campaign configuration and activation
1. Obtain the actual target post and real resource URL. Never activate the example.com test URL. Each campaign has a stable ID, media_id, keywords, link, message template containing `{link}`, timezone-aware active_from, and enable switch.
2. Set active_from deliberately so old comments are not unexpectedly messaged. Keep campaign identity stable; changing a campaign ID can change commenter dedupe scope, though comment dedupe is global.
3. Run `python3 scripts/comment_dm.py validate`. Run an enabled temporary configuration only with `--config PATH run --dry-run` to exercise live reads without sending.
4. Enable sending only for the intended configured post. Use an owner-controlled test comment for the first delivery and read back the exact message before claiming end-to-end success.
5. Inspect `systemctl --user is-active sputarai-comment-dm.timer`, `systemctl --user show sputarai-comment-dm.service -p Result -p ExecMainStatus`, and the dedicated journal. A waiting timer or disabled service success is not live delivery proof.
6. Rollback with `systemctl --user disable --now sputarai-comment-dm.timer` and global enabled=false. Do not stop shared applications.

## API and safety contract
Source: https://developers.facebook.com/docs/instagram-platform/private-replies . Send one initial private reply with POST `/<IG_ID>/messages`, body `recipient: {comment_id: ...}` plus `message: {text: ...}`. This is NOT an ordinary DM addressed by a user ID, and does not require an initial inbound DM. Respect the private-reply time window (seven days for normal comments); follow-up automated conversations require recipient response and applicable messaging rules. Consult current Meta docs before changing behavior.

The runner verifies @sputarai identity and media ownership; matches keywords as case-insensitive whole words; skips self, old, future, missing-author, and pre-activation comments; reserves in SQLite before POST; holds ambiguous outcomes without automatic retries. Errors stop further sends for that run and expose sanitized HTTP/Meta codes only. Never expose the credential or comment/DM bodies in logs.

## Verification and known ceilings
- Focused check: `python3 -m unittest discover -s tests -p test_comment_dm.py -v`. Synthetic transport/temporary DB tests are not real delivery proof.
- Installed standby was exercised with 16 passing tests, valid config, disabled exit0, active timer and service Result=success ExecMainStatus=0. A real read-only dry-run of this new engine confirmed @sputarai and its media; no live reply was sent. Recheck current runtime before reporting current health.
- Default scan is 3 pages of 25 own-media/comments. Posts outside the own-media scan are skipped and listed in `media_not_in_scan`; do not remove the ownership check to hide this limitation.
- Dry-run candidates are matches before ledger dedupe, not predicted sends.
- No UI configuration panel or open-ended conversational DM chatbot is implemented by this feature.
- Project adoption wrappers can point at deleted `/home/ubuntu/docbuddy/docbuddy.py`. If both supported adoption commands fail, disclose that blocker and add only scoped missing contracts manually; do not repair global tooling or restart old publishers as a side task.
