# Rich TUI integration and verification

- Extend `ui-tui/` Ink components and `tui_gateway/` contracts rather than replacing dashboard chat with a second renderer. Read the area's AGENTS.md first; preserve pre-existing dirty work.
- Build `ui-tui/packages/hermes-ink` with `npm run build:ink` before Vitest imports `@hermes/ink`; a missing dist/entry-exports.js is a build prerequisite, not a renderer bug.
- Derive tool outcome from structured `tool.complete.result`, never prose or the existence of a completion event. Carry safe outcome fields through session history projection too; raw error/output may contain credentials.
- Preserve terminal tool rows at end-of-history or before a new user turn, not just before assistant replies. Interrupted turns often end with a tool result.
- Test render fallback through real Ink mounting and a throwing child. Pure state tests do not establish that the composer survives a component error.
- Sanitize OSC/DCS/C1 and unterminated control strings before splitting streaming Markdown into stable blocks; a malicious control string may itself contain blank lines. Preserve supported SGR through the styled renderer.
- Run UI tests with bounded workers. If a wall-clock render test fails on an empty output after a fixed sleep, wait for the actual rendered assertion with a bounded timeout; do not weaken the expected content.
- Validate the bundled `dist/entry.js` in a real PTY under a temporary HERMES_HOME, without provider requests or credentials: startup, /help, narrow/wide resize, and a preserved draft. This is a functional smoke check, not visual-quality approval.
- Do not disable sessions.max_resume_messages globally to claim long-history support. Reading archive pages and resuming model context are distinct capabilities and require separate verification.
