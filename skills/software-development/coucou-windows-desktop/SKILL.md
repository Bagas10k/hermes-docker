---
name: coucou-windows-desktop
description: Use when building or reviewing Coucou Windows desktop.
---

# Coucou Windows Desktop

## Approved product requirements
- Target Windows 10/11 and reuse Coucou identity and mascot. Attribute user project design to Bagas Cihuy.
- Use a freely floating mascot for the first version, NOT Dynamic Island. Clicking opens chat/settings. The later Dynamic Island discussion did not approve changing this design.
- Start the companion at Windows login without granting laptop control.
- Distribute the verified installer at https://www.jajandigital.web.id/coucou/. Downloading alone does not install it.
- Support Hermes/server management plus Windows screen, mouse, keyboard, files, and terminal. Clearly distinguish server and laptop execution targets.

## Approved security boundaries
- Require explicit local start for laptop control; keep stop visible.
- Accept laptop instructions only through desktop Coucou, never Telegram/WhatsApp.
- Physical user input pauses automation; require explicit resume.
- Connection loss rejects new local actions; reconnection requires explicit resume. Do not forcibly kill already-running processes indiscriminately.
- Ordinary work executes automatically; risky/destructive actions require confirmation. Never bypass Windows UAC.
- Pair once via a one-time code approved through authenticated administration. Store revocable device credentials securely in Windows. Never ship server secrets in the installer.
- Send screenshots to the model provider only when necessary during active, unpaused control; no screenshot archive by default. Provider retention is separate.
- Previously authorized server work continues after laptop control ends; laptop-dependent steps wait for a new session.
- Download updates automatically; verify authenticity and install only with consent outside active control.

## Workflow and verification
- Preserve live Coucou web while implementing desktop in isolation.
- Discover actual repository and backend; do not assume a frontend directory is a Git checkout.
- Separate policy unit tests, Electron launch, installer build, and actual Windows end-to-end control gates. Passing one never proves the others.
- Verify published downloads before claiming availability. Report concrete progress and blockers, not invented completion percentages.
- Ask design questions one at a time with structured choices and recommendation first.
