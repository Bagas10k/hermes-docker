# Same-Host Multi-Profile Gateways and Bot Mode

Use this procedure when several Hermes profiles on one machine must share messaging ingress or collaborate as durable named Bots.

## 1. Lock the layer and acceptance contract

Distinguish the requested behavior before editing anything:

| Layer | Mechanism | What success means |
|---|---|---|
| Persistent identity | Profile | Separate config, model, memory, skills, credentials, sessions, and `state.db` |
| Messaging transport | Gateway multiplex | One host gateway serves all eligible profiles without duplicate polling or port ownership |
| Durable profile collaboration | Bot Mode `message_agent` | One profile dispatches to another profile's canonical `Bot Chat`; receipt reaches `settled` |
| Ephemeral task work | `delegate_task` | A fresh child conversation completes a bounded subtask; it is not another profile |

Never substitute one layer's evidence for another. In particular, `gateway.multiplex_profiles=true` proves routing consolidation, not Bot-to-Bot reasoning.

Binary gates for a full rollout:

1. One host gateway process is active; profile-specific gateway units are inactive/uninstalled.
2. Multiplex is enabled and every intended profile is discovered.
3. Each intended messaging credential is unique and accepted by its platform.
4. Logs contain no duplicate polling conflict, auth rejection, or crash loop during a fixed soak.
5. Each intended bot passes inbound and outbound tests under its own profile identity.
6. A Bot Mode handoff reaches `settled`, not merely `queued`.
7. A separate `delegate_task` probe passes if ephemeral orchestration is part of the claim.

## 2. Inventory without leaking credentials

```bash
hermes profile list
systemctl --user is-active hermes-gateway.service
systemctl --user list-unit-files 'hermes-gateway*'
hermes config get gateway.multiplex_profiles
```

For each profile, verify the token exists and compare a short SHA-256 fingerprint; never print the token. Treat `HTTP 200` from `getMe` as accepted, `HTTP 401` as an invalid/revoked credential, and timeouts as network evidence—not authentication evidence.

List every profile that has a messaging credential before migration. A multiplexer rescans profile homes and may activate a dormant bot whose token is still present, so obtain the user's decision about that expanded roster first.

## 2A. Rename a live profile and attach a Telegram bot

Use this path when the user wants an existing specialist profile to keep its model, SOUL, skills, memory, and sessions under a shorter public identity.

1. Identify the source profile from its live `SOUL.md`/`profile.yaml`; do not create a blank replacement when the requested expertise already exists.
2. Export a rollback archive to a mode-`0700` local directory and treat the archive as secret-bearing because it may include `.env`:
   ```bash
   hermes profile export <old> -o <protected-dir>/<old>-before-rename.tar.gz
   ```
3. Rename only through the supported command:
   ```bash
   hermes profile rename <old> <new>
   ```
   Never `mv` a live profile directory: the CLI first unserves the old adapter, migrates routing identity and aliases, records `previous_names`, then asks the multiplexer to reconcile. A filesystem-only move can resurrect a ghost profile or strand persisted routing.
4. Search live, nonhistorical files across all profiles for the old slug and absolute path. Update `SOUL.md`, `profile.yaml` descriptions, collaborator routing instructions, topical references, and pending durable-memory payloads. Do **not** rewrite session dumps, caches, backups, or `previous_names`; those are historical provenance, not active routing.
5. Validate the Telegram credential with `getMe` before binding it and require the returned username to equal the intended bot username. Keep the token out of command arguments and printed URLs; report only HTTP status, `ok`, `is_bot`, display name, and username.
6. Configure the renamed profile through its scoped setup (`hermes -p <new> gateway setup`) or an equivalent secret-aware writer to `<profile-home>/.env`. Require mode `0600`. Use numeric Telegram IDs for `TELEGRAM_ALLOWED_USERS`; when setup originates from an authenticated Telegram turn, `HERMES_SESSION_USER_ID` is the correct default for that user, never their `@username`.
7. Let the live multiplexer hot-rescan the profile signature before restarting anything. Wait one bounded rescan interval, then require `gateway_state.json` to contain `<new>:telegram` as `connected`, with no error and the current gateway writer PID; require `<old>:telegram` to be absent. Restart only if the bounded rescan fails and logs identify a startup-only setting or stuck adapter.
8. Test the scoped transport:
   ```bash
   hermes -p <new> send --to telegram:<numeric-chat-id> --json '<synthetic probe>'
   ```
   Require `success: true` and a real `message_id`. Then require the user to send a fresh message to the new bot and verify that the inbound turn/session is owned by `<new>`; outbound delivery is not evidence of inbound routing or agent response.
9. Run a fixed post-cutover soak. Judge errors after the adapter's connected timestamp; a one-off handoff warning is not a veto unless it recurs after reconciliation.

## 3. Preflight and migrate through the official path

```bash
hermes gateway migrate --multiplex --dry-run
```

Stop on any blocker: duplicate bot tokens, unsupported port-bound platforms, unclear service ownership, insufficient resources, or an unexpected profile in the plan.

Apply from outside the gateway's cgroup. A transient user unit survives the gateway restart:

```bash
unit="hermes-multiplex-migrate-$(date +%s)"
systemd-run --user --unit="$unit" --collect \
  --property=TimeoutStartSec=15min \
  "$HOME/.local/bin/hermes" gateway migrate --multiplex -y
```

Do not make a secondary gateway permanent with `gateway run --force`; that bypass is diagnostic and can leave split ownership. If a temporary `--force` drop-in existed, remove it after successful migration and run `systemctl --user daemon-reload`.

## 4. Verify the transport layer

```bash
hermes config get gateway.multiplex_profiles        # true
systemctl --user is-active hermes-gateway.service   # active
systemctl --user is-active hermes-gateway-<profile>.service  # inactive/not found
pgrep -af 'gateway run'
hermes profile list
```

Read `~/.hermes/gateway_state.json`. The launch profile appears as `telegram`; secondary adapters appear as `<profile>:telegram`. Require the expected state keys and current writer PID. `hermes profile list` showing a profile as running means the multiplexer serves the profile; it does not prove every platform adapter is authenticated.

Search the journal after the new PID's start time, not across old failures:

```bash
journalctl --user -u hermes-gateway.service --since '<start time>' --no-pager
```

Match Telegram conflicts precisely (`409`, `terminated by other getUpdates`, or the platform's conflict class). A generic word such as `conflict` may match unrelated session-route diagnostics and produce a false veto.

For each bot, verify platform authentication and a real send/receive. Scope secondary-profile delivery explicitly with `hermes -p <profile> send --to telegram:<numeric-chat-id> --json ...`; otherwise the default profile's credential can produce a false-positive transport test. Require `success: true` and a real `message_id`, then verify a fresh inbound message creates or resumes a session under that same profile. Process-active, adapter-connected, `getMe`, and outbound delivery are four separate gates; none alone proves end-to-end conversation. Use synthetic messages, never personal/business data.

## 5. Enable durable Bot Mode collaboration on a headless host

`agent.bot_mode_protocol` is the master switch and defaults on, but `message_agent` appears only when both Bot Mode gates are satisfied:

1. The session title is exactly `Bot Chat`.
2. At least one profile has a Bot Mode marker in `profile.yaml`:

```yaml
ui_meta:
  hermes-bots: {}
```

There is no CLI writer for the marker. Patch only this metadata block and preserve existing description/title metadata. Keep each profile's SOUL, memories, model, and credentials isolated.

Create or resume the canonical chats:

```bash
hermes chat -c 'Bot Chat' --create-if-missing
hermes -p <profile> chat -c 'Bot Chat' --create-if-missing
```

When the named session already exists, resume it without creation-policy overrides such as a different `--run-budget`; Hermes freezes launch policy per session and correctly rejects mismatched overrides.

Give every Bot a concise, non-overlapping role description:

```bash
hermes profile describe default --text 'General Manager: ...'
hermes profile describe <profile> --text 'Specialist role: ...'
```

Keep `profile.yaml` descriptions consistent with `SOUL.md`; contradictory labels make roster routing and prompts ambiguous.

## 6. Prove Bot-to-Bot delivery end to end

From the sender's canonical Bot Chat, request exactly one `message_agent(target="<profile>", message="<synthetic probe>")` call.

Interpret states strictly:

- `queued` + `delivery_id`: dispatch process accepted the request; not completion.
- `claimed`: target profile admitted the delivery; still not completion.
- `settled` + expected reply: end-to-end PASS.
- `failed`/typed reason: FAIL; diagnose that target/profile/provider layer.

The durable receipt is under the target profile's `runtime/bot_live_delivery/<delivery_id>.json`. Poll the same receipt to terminal state. Do not resend while the outcome is unknown because the first turn may still be running.

A slow target model can make transport look broken. Separate evidence: `claimed` proves routing/admission, while a long-running target turn points to model/provider/tool behavior. Bound probe turns and stop only the probe process if it runs away; do not restart the whole gateway.

## 7. Verify ephemeral orchestration separately

Run one minimal `delegate_task` child that returns an exact sentinel. This proves the active profile's subagent runtime after migration, not cross-profile Bot Mode. Record both gates independently in the final report.

## 8. Report and release

Report each gate as PASS/PARTIAL/FAIL with evidence. For a renamed messaging profile, include: old slug absent from the active roster, new slug/model/SOUL/skills preserved, old live cross-profile references removed, credential identity matched, exact adapter key connected, scoped outbound `message_id`, fresh inbound ownership, and a clean bounded soak. A valid partial release may have one-gateway transport and outbound delivery working while inbound remains untested, or one optional bot has an invalid credential; do not call the whole roster healthy until every required inbound/outbound path passes. Preserve a physical tracker for long work and include remaining user-supplied prerequisites explicitly.
