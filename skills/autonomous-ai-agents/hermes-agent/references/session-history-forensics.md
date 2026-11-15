# Session-history forensics: recovering past work

Use when the user refers to something "we built before" that is no longer on disk, in pm2, or on its port, or when you must prove where and when an artifact existed. Iteration budgets are finite: go from high-signal to broad, and print small targeted output.

## Order of search (highest signal first)

1. **Architecture notes in the vault.** Grep `~/otak-koding/BUKU_CATATAN/` (and any bundle copies such as `~/hermes-genesis-portable/otak_koding_bundle/`) for the product noun and its likely names. These notes usually record the path, port, pm2 name, update rate, palette, fonts and component list — often enough to rebuild without the code.
2. **Live state, one batched command.** `ls <path>`, pm2 names, `ss -ltnp | grep <port>`, `curl -s -o /dev/null -w '%{http_code}' 127.0.0.1:<port>`. Combine into one call; separate probes waste iterations.
3. **`session_search`** for the product name and for a distinctive file path. It returns session ids and matching message ids to target in SQL.
4. **Read-only SQL on `$HERMES_HOME/state.db`** (and `profiles/*/state.db` if the work might have run under another profile).
5. **Reconstruct or rebuild** (below).

Only then fall back to broad scans of archives/backups.

## state.db query recipe

```python
import sqlite3
db = sqlite3.connect('file:/home/ubuntu/.hermes/state.db?mode=ro', uri=True)  # never open read-write
print(db.execute('PRAGMA table_info(messages)').fetchall())                 # confirm columns first
CUR = '<current session id>'
q = '%server-monitor%'
rows = db.execute("""
  SELECT id, session_id, role, timestamp, substr(coalesce(content,''),1,160)
  FROM messages
  WHERE session_id != ?
    AND (content LIKE ? OR tool_calls LIKE ?)
    AND coalesce(content,'') NOT LIKE '[CONTEXT COMPACTION%'
  ORDER BY timestamp LIMIT 30""", (CUR, q, q)).fetchall()
for r in rows: print(r)
```

Pitfalls:

- Exclude the current session — your own searches and tool output match every pattern.
- Exclude compaction handoff blocks — they are user-role messages that quote earlier work, so they match LIKE queries and look like evidence while adding nothing.
- Print counts and short slices, never whole rows; very long output gets collapsed and the result is lost along with the iteration.
- Distinguish the build session from consumer sessions: a session that edited a client of the old service (fetching its port) is not where the service was written. Check whether the matched session issued `write_file` for the target path.
- Cron/autopilot sessions that ran `find`/`ls` are timestamped proof the file still existed then; use them to bound when it disappeared.

## Reconstructing files from tool calls

`tool_calls` holds JSON with each call's `function.name` and `function.arguments` (itself JSON). For `write_file`, the arguments contain `path` and `content`. Replay later `patch` calls on that path in timestamp order to reach the final version. Write results into `$HERMES_HOME/cache/scratch/<name>_recover/`, never over a live path. Then list the directory and run or render the file before relying on it. Until that check, treat the reconstruction as unverified.

## When the source is gone

Report three facts separately: what the note specifies, what is missing (path, pm2 entry, port), and what currently serves the role. Propose rebuilding the recorded design on the current backend. If two similarly named surfaces exist (for example a PM2/cron status tab and a system-metrics telemetry page), ask one question naming both, with your recommendation first.
