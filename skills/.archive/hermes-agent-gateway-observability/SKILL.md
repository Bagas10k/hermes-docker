---
name: hermes-agent-gateway-observability
description: "Use when Telegram shows silent loading or lacks tool logs."
version: 1.0.0
author: Bagas Cihuy
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [telegram, gateway, observability, verbose, progress]
---

# Gateway & Platform Observability Troubleshooting

## Telegram "Silent Working Bubble" / No Progress or Error Visible
By default, the Telegram adapter configures `display_overrides={"tool_progress": "off", "busy_ack_detail": False}` to keep mobile notifications quiet. This causes Hermes to appear stuck on a silent "Working / Sedang bekerja" indicator with zero tool execution details, zero arguments, and no visible error trace if a command hangs or fails.

### Resolution Steps
Configure display settings in `~/.hermes/config.yaml`:
```bash
hermes config set display.platforms.telegram.tool_progress verbose
hermes config set display.platforms.telegram.tool_preview_length 160
hermes config set display.platforms.telegram.streaming true
hermes config set display.platforms.telegram.cleanup_progress false
```

- `tool_progress: verbose`: Reports every tool invocation and status instead of suppressing it or waiting for tool switches (`new`).
- `tool_preview_length: 160`: Shows the actual command/target argument instead of an empty or truncated preview.
- `cleanup_progress: false`: Preserves progress messages so error breadcrumbs are not deleted upon failure.
- In-session toggle: `/verbose` in chat cycles display modes (`off` -> `new` -> `all` -> `verbose`).
- Reasoning visibility: `/reasoning show` unhides streaming thought process.

## Gateway Process Self-Restart Restriction
The gateway process blocks self-restart (`systemctl --user restart hermes-gateway` or `hermes gateway restart`) from within tool-execution sessions to prevent deadlocks and broken connections. Instruct the user to run `systemctl --user restart hermes-gateway` from an external terminal or SSH session outside the running gateway.
