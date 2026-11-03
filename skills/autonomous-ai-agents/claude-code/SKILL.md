---
name: claude-code
description: Delegate coding to Claude Code CLI (features, PRs).
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [coding, delegation, claude, subagent, orchestration]
---

# Claude Code CLI Orchestration

Delegate bounded coding, refactoring, and code review tasks to Anthropic's Claude Code CLI.

## Supporting References
- `references/unabridged-claude-code.md`: Full unabridged orchestration reference.
- `references/claude-cli-reference.md`: Complete CLI flags reference, slash commands, shortcuts, hooks, and MCP configuration.

---

## Prerequisites
- Claude Code CLI installed: `npm install -g @anthropic-ai/claude-code`
- Authenticated via `claude login` or `ANTHROPIC_API_KEY` set in environment.

## Orchestration Modes

### Mode 1: One-Shot / Non-Interactive (Print Mode `-p`)
Best for bounded refactoring, test fixes, and automated PR reviews.
```bash
# Direct task execution
claude -p "Fix the failing test in tests/test_auth.py"

# Piping context into Claude
git diff | claude -p "Review this diff for security flaws and performance regressions"

# Output structured JSON
claude -p "List all exported functions in src/index.ts" --output-format json
```

### Mode 2: Interactive Session (PTY Mode)
Best for long-horizon multi-step tasks requiring REPL interaction.
- Launch via `terminal(command="claude", pty=True, background=True)`.
- Drive via `process_manage` (`action="write"`, `action="read"`).

## Critical PTY Dialog Handling
- **Trust Dialog**: First run in a new directory asks to trust the folder. Detect prompt and submit `y\n` or `Enter`.
- **Permission Prompts**: When Claude Code requests bash tool execution, approve via `y\n` or launch with `--dangerously-skip-permissions` in isolated sandboxes.
- **Escape / Cancel**: Send `\x03` (Ctrl+C) to interrupt runaway loops.

## Rules for Hermes Agents
1. **Prefer Print Mode (`-p`)**: Use `-p` for 90% of tasks; avoid interactive PTY overhead unless conversational back-and-forth is required.
2. **Always Check Diffs**: After Claude finishes, run `git diff` or `git status --short` to independently verify changes before reporting.
3. **Bound Task Context**: Provide specific filenames and line numbers in the prompt; never ask Claude to "fix the whole project" blindly.
