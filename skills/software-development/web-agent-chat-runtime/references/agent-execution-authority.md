# Agent Execution Authority — the `run:` protocol

A chat agent that can only *describe* shell commands is a suggestion engine, not an
operator. The failure this prevents: the user says "publish this project" and the
agent answers "I cannot run commands on Linux". The capability is the product.

Granting it is a three-layer job. The layers are not interchangeable, and shipping
two of three produces a worse result than shipping none:

| Layer | Job | If missing |
|---|---|---|
| Prompt | Tell the model it MAY execute, and how | Agent still refuses — it was never told |
| Server | Enforce the boundary in code | Prompt becomes the only defence, and prompts can be argued with |
| Client | Show the command, run on click, feed result back | Agent writes commands, goes blind to the outcome |

---

## 1. Prompt grant block

The model refuses by default because nothing told it otherwise. Grant explicitly,
state the protocol, and close the door on the refusal phrasing:

```
=== EXECUTION AUTHORITY (YOU MAY RUN COMMANDS) ===
You do NOT need the user to copy commands manually. You can RUN Linux commands
on this server yourself.

HOW: one command per line, prefixed `run:`, inside a bash fence.
```bash
run: cd /home/ubuntu/my-project && git status
run: cd /home/ubuntu/my-project && npm run build
run: pm2 restart my-process
```

RULES:
1. Working directory MUST be inside <WORKSPACE_ROOT>. Write the full path after `cd`.
2. Always inspect first (git status, ls, cat package.json) before changing anything.
3. Consequential commands (git push, pm2 delete/stop, npm install, apt install)
   will ask the user for approval. That is expected — proceed.
4. FORBIDDEN: deleting root, mkfs, dd to disk, shutdown/reboot, fork bombs.
   These are blocked hard.
5. After execution the result (stdout/stderr/exit) is returned to you. Read it and
   continue until the task is done.
6. If a command fails, DO NOT give up: read the error, fix it, try another way.
7. Report the final outcome honestly: what worked, what failed, and any URL/port.

IMPORTANT: Never say "I cannot run commands". You can.
=== END EXECUTION AUTHORITY ===
```

Rule 5 and 6 are the load-bearing ones. Without 5 the agent is blind; without 6 it
stops at the first non-zero exit code and reports failure as if it were final.

---

## 2. Server guard

Prompt text is not a security control. The guard runs **before spawn** and cannot be
argued with by a later message.

```js
const WORKSPACE_ROOT = process.env.KANVAS_WORKSPACE || '/home/ubuntu';
const EXEC_TIMEOUT_MS = Number(process.env.EXEC_TIMEOUT || 180000);
const EXEC_MAX_OUTPUT = 200000;

// Not an exhaustive list — that is impossible. It closes the unrecoverable ones.
const EXEC_DENY = [
  /\brm\s+(-[a-zA-Z]*\s+)*\/(\s|$)/,     // rm -rf /
  /\bmkfs(\.\w+)?\b/,                     // format filesystem
  /\bdd\b[^\n]*\bof=\/dev\/[sh]d/,        // raw disk write
  /\b(shutdown|reboot|halt|poweroff)\b/,
  /\binit\s+0\b/,
  /:\(\)\s*\{.*\};/,                      // fork bomb
  /\bchmod\s+-R\s+777\s+\/(\s|$)/,
  /\b(userdel|groupdel)\b/,
  />\s*\/dev\/[sh]d/,
  /\bpasswd\b/,
  /\biptables\s+-F\b/
];

function execGuard(command, cwd) {
  const cmd = String(command || '').trim();
  if (!cmd) return 'Empty command';
  if (cmd.length > 4000) return 'Command too long';
  for (const re of EXEC_DENY) if (re.test(cmd)) return `Denied by guard: ${re}`;
  const resolved = path.resolve(cwd || WORKSPACE_ROOT);
  if (!resolved.startsWith(WORKSPACE_ROOT)) return `cwd outside workspace: ${resolved}`;
  return null;
}
```

### Two tiers, not one

A single blocklist forces a bad trade: block too little and one typo is fatal, block
too much and the agent cannot do its job. Split by **reversibility**:

- **Deny hard** — unrecoverable from inside the session: filesystem format, raw disk
  write, root deletion, power state, fork bomb, credential/account destruction.
- **Require approval** — consequential but recoverable: publishing, process
  lifecycle, dependency install, piping a remote script into a shell.

```js
const risky = /\b(git\s+push|pm2\s+(delete|kill|stop)|npm\s+(install|ci)
              |apt(-get)?\s+install|curl[^\n]*\|\s*(ba)?sh|docker\s+(rm|down))\b/i;
if (risky.test(command) && !approved) {
  return res.json({ success: false, needsApproval: true, command,
                    reason: 'This command changes the system. Approve to run it.' });
}
```

The client turns `needsApproval` into a confirm dialog showing the exact command, then
re-posts with `approved: true`. Approval is per-invocation, never sticky.

### Execution, timeout, output cap

```js
const { stdout, stderr } = await execAsync(command, {
  cwd: path.resolve(cwd || WORKSPACE_ROOT),
  timeout: EXEC_TIMEOUT_MS,
  maxBuffer: EXEC_MAX_OUTPUT,
  shell: '/bin/bash'
});
```

On failure return `{ success:false, exitCode, stdout, stderr, error }` — the agent
needs stderr far more than it needs a friendly message.

### Audit ring

Keep the last N entries in memory and expose `GET /api/exec/audit`, plus a one-line
`console.log` per run. An execution surface with no audit trail is undebuggable
after the fact — you cannot reconstruct what the agent actually did.

---

## 3. Client: parse, show, run, feed back

Parse `run:` from bash fences (and from bare lines as a fallback), de-duplicate, and
render one row per command with an explicit run button. **Never auto-execute** — the
user sees the command before it touches the machine.

```js
function extractRunCommands(text) {
  const cmds = [];
  for (const f of String(text||'').matchAll(/```(?:bash|sh|shell)?[ \t]*\r?\n([\s\S]*?)```/gi)) {
    for (const line of f[1].split('\n')) {
      const m = line.match(/^\s*run:\s*(.+)$/i);
      if (m && m[1].trim()) cmds.push(m[1].trim());
    }
  }
  if (!cmds.length) { /* same scan over bare lines */ }
  return [...new Set(cmds)];
}
```

### The feedback loop (the part that makes it an operator)

After execution, post the result back into the conversation as a **machine message**,
not as a user bubble:

```js
async function feedbackToHermes(command, data) {
  const msg = [
    '[AUTOMATIC EXECUTION RESULT]',
    'Command: ' + command,
    'Status: ' + (data.blocked ? 'BLOCKED BY GUARD'
                 : data.success ? 'SUCCESS' : 'FAILED'),
    'Exit code: ' + (data.exitCode ?? (data.success ? 0 : '?')),
    'Output:', '```', (data.stdout + data.stderr).trim().slice(0, 4000) || '(none)', '```',
    'Continue until the task is done. If it failed, read the error above and fix it.'
  ].join('\n');
  await sendMessage(msg, { silent: true });   // silent = do not echo as user turn
}
```

Guard against re-entry: a busy flag so a multi-command run does not spawn overlapping
turns.

---

## Verification matrix

Run all four before claiming the feature works. The last one is the only real proof.

| Check | Command | Expect |
|---|---|---|
| Guard blocks | `rm -rf /`, `mkfs.ext4 /dev/sda1`, `shutdown now` | `blocked: true` |
| Guard passes | `echo ok`, `ls <root> \| head -3` | `success: true` |
| Approval gate | `pm2 stop <svc>`, `git push origin main` | `needsApproval: true` |
| **End to end** | Ask the agent in natural language to inspect a project | It emits `run:` lines, the panel renders, clicking runs it, the result returns to the conversation and the agent continues |

The first three are table stakes. Only the fourth distinguishes "wired up" from
"works". A guard that blocks everything also passes the first three.

---

## Pitfalls

- **The Prompt-Only Permission Trap.** Telling the model "you may run commands"
  without a server guard does not make it safe — it makes the prompt the only defence,
  and prompt text can be argued with by the next message. Building the guard without
  the prompt grant leaves the agent still refusing. Both layers, or neither.
- **The Blind Operator Trap.** Showing execution output only to the user leaves the
  agent unable to react to its own failures. It writes a command, gets an error nobody
  routed back, and stops. Every result must be fed back into the conversation, and
  must not be echoed as a user bubble.
- **The Triplicated Command Trap.** Rendering the raw bash fence, the parsed command
  panel, and the run button at once shows the same command three times within three
  centimetres. When every line of a fence is a `run:` line, hide the fence and keep
  only the panel. A "run all" control only earns its place above one command.
- **The Fake-Progress Approval.** Making approval sticky ("always allow") turns a
  per-command gate into a session-wide grant, which is the same as no gate. Approve
  per invocation.
- **The Silent Exit-Code Drop.** Returning only `stdout` and a human sentence throws
  away the one signal the agent reasons with. Always return the numeric exit code.

---

## Companion rendering pitfalls (same surface, different layer)

These bit the same feature and are easy to reintroduce:

- **The Parent-Measures-the-Artifact Trap.** A sandboxed iframe without
  `allow-same-origin` has an opaque origin, so `frame.contentDocument` is `null` and
  the parent can never measure the document. Height logic that reads the frame from
  outside silently falls back to a fixed height and clips the page behind a scrollbar
  the user never notices. Inject a reporter into the `srcdoc`; let the document
  `postMessage` its own content height, and answer an explicit `{__askHeight:1}` ping.
  Cap generously (e.g. 1400px) — a hard ceiling clips anything taller.
- **The `vh` Inside an Embedded Artifact Trap.** A document written for a full browser
  window (`min-height:100vh`) resolves those units against the *frame* height when
  embedded, so the layout stretches and leaves a large dead region with the real
  content pushed to one edge. Neutralise viewport units inside the artifact
  (`html,body{min-height:0!important;height:auto!important}`) so content is honestly
  content-sized and the reporter measures something real.
- **The Chrome Budget Creep Trap.** Chat chrome that grows one strip at a time (mode
  tabs, agent header, quick chips, target bar, settings row, bottom dock) can silently
  consume more of a phone screen than the conversation does. Measure per element —
  `sum(rect.height of each chrome bar) / innerHeight` — and hold the conversation above
  roughly half the viewport. Collapse configuration rows (model, tone, bot) behind one
  toggle; they are configuration, not conversation.
