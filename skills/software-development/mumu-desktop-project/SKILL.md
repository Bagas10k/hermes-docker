---
name: mumu-desktop-project
description: Use when developing mumu Windows desktop companion.
---

# mumu desktop — project decisions

## Identity and continuity
- User chose exact lowercase name `mumu`. Continue improving existing prototype rather than discarding it or starting another project.
- Source workspace: `/home/ubuntu/coucou-desktop`; original web: `/home/ubuntu/coucou-companion-web`; upstream read-only reference: `/home/ubuntu/coucou/windows`.
- Planned download location remains https://www.jajandigital.web.id/coucou/; do not infer a route rename from rebranding.
- Target Windows 10/11. Floating standalone mascot with panel on click, not Dynamic Island for first release.
- User wants soft organic morphing animations: round, stretch, squash, expressive. Rigid diamond prototype is NOT approved final design.
- Create original identity/assets. Upstream code MIT does not grant redistribution rights to Coucou/Mochi names, character, icons or sounds; preserve notices. User selected original own assets. Similar animation technique is acceptable; do not assume permission to copy character.

## Approved behavior
- Control Hermes server and local Windows; local control only during an explicitly started session.
- Autostart companion at Windows login WITHOUT activating control.
- Ordinary authorized tasks automatic; dangerous actions require confirmation; never bypass UAC.
- Physical mouse/keyboard activity pauses automation; explicit Resume required.
- Disconnection stops new local instructions; reconnection requires explicit Resume. Do not indiscriminately kill already-running processes.
- Accept local-control instructions only from desktop application, not Telegram/WhatsApp.
- Visible Stop control during active session.
- One-time-code device pairing through authenticated owner approval; secure OS credential storage; revocable device access; no embedded server credentials in installer.
- Necessary screenshots may reach configured model provider only during active unpaused session; no default screenshot archive. Disclose provider retention separately.
- Approved server tasks may continue after laptop session ends; laptop-dependent steps wait.
- Updates download automatically, install only with consent outside active control and verified authenticity.

## Workflow and acceptance
- Interview one question at a time with structured choices when a real design decision is missing.
- Inspect upstream/native backend before replacing architecture; distinguish prototype policy tests from actual Windows integration.
- Keep live web/backend unchanged unless deployment scope is explicitly handled; isolate new development.
- Report verified artifacts/tests and exact blockers; never invent completion percentages. Never describe inactive workers as still running.
- Completion requires real Hermes integration, pairing, native automation, input-interruption checks, Windows installer/runtime validation and verified download publication; a packaged preview is not full control.
- Prefer finishing functional integration before further cosmetic prototype work. User accepts iterative prototype refinement, not abandonment or unexplained restarts.
- Check live files/tests for current status rather than treating this skill as a progress log.
