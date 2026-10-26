---
name: long-horizon-app-building
description: Execute long-horizon app building with honest verification.
version: 0.1.0
author: Hermes
license: MIT
related_skills:
  - structured-project-execution
  - subagent-lifecycle-management
  - test-driven-development
  - fullstack-systems
metadata:
  hermes:
    tags:
      - LongHorizon
      - AppBuilding
      - Integrity
      - AntiABS
      - Execution
---

# Long-Horizon App Building & Radical Truthfulness

Guide autonomous agents in executing multi-hour, multi-step application builds from inception to final production delivery. Enforces state persistence, honest error reporting, incremental milestone verification, and radical truthfulness (Anti-ABS) where every claimed feature is backed by empirical runtime proof.

## When to Use
- User asks to "bangun aplikasi dari awal sampai akhir", "eksekusi proyek jangka panjang", or "build full-stack app secara konsisten dan jujur".
- Developing multi-tier applications (database, backend API, frontend UI, authentication, and reverse proxy wiring).
- Projects requiring multiple consecutive turns without losing architectural context or deviating from core specs.

## Prerequisites
- Target runtime environment (Node.js, PHP/Laravel, Python, or Go).
- Database only when the product actually needs persistence; browser-local prototypes do not require one.
- State tracking file at `workspace/build_tracker.json` or `.hermes/state.json` to persist execution milestones across context compactions.

## How to Run
Orchestrate long-horizon milestones through Hermes tools:
- Initialize project repositories and run test suites via the `terminal` tool.
- Inspect and modify codebases incrementally with `read_file`, `write_file`, and `patch`.
- Verify runtime UI and visual layout using `browser_navigate` and `vision_analyze`.
- Track progress and milestones through `todo_list` or persistent tracker files.

## Quick Reference
- **The Golden Rule of Radical Truthfulness (Anti-ABS):** Match each feature claim to evidence at its own boundary: build exit code proves compilation, HTTP 200 proves a response, a screenshot proves visible layout, and an exercised user journey proves behavior. None substitutes for another.
- **Epistemic Classification:**
  - `KNOWN`: Empirically tested and confirmed via runtime command.
  - `LIKELY`: Follows standard documentation but pending runtime verification.
  - `UNCERTAIN`: Multiple potential root causes; requires diagnostic probe.
  - `UNKNOWN`: Unchecked assumption; never state as fact.
- **The 5 Invariant Milestones:**
  1. *Foundation:* Schema migrations, seeders, environment configuration.
  2. *Core Engine:* Business logic, invariants, API endpoints.
  3. *Client Interface:* Responsive UI, form validation, error states.
  4. *Ingress & Wiring:* Subpath reverse proxy, cookie isolation, CORS.
  5. *Live Verification:* End-to-end curl assertions, smoke tests, zero regression.

## Procedure

1. **Lock the Product Contract Before Scaffolding:**
   - Translate the user's reference product into the primary user journey and acceptance check (e.g. online music discovery → licensed catalog result → playable audio), plus secondary features. Separate feasibility questions from the user's actual requirement.
   - Probe upstream data/API rights, terms, uptime, browser support, and media playback early. If the defining journey cannot be implemented responsibly, explain the blocker and ask permission for a changed scope before building a materially different product. A local-file player is not a substitute for an online-streaming player.
   - If the user has named a visual vibe, carry it through the functional phase; do not ask for it again.

2. **Establish Build Documentation and Persistent Tracker:**
   Follow `project-build-documentation`: read existing docs first, reuse their canonical entry points, and keep setup/build/test/architecture notes accurate as the implementation changes. Do not create duplicate or ceremonial docs. Never rely solely on volatile conversational context. Write a persistent plan:
   ```json
   {
     "project_name": "app-name",
     "current_phase": 1,
     "milestones": [
       {"id": 1, "name": "Foundation & DB", "status": "pending"},
       {"id": 2, "name": "Backend API", "status": "pending"},
       {"id": 3, "name": "Frontend Interface", "status": "pending"},
       {"id": 4, "name": "Reverse Proxy Ingress", "status": "pending"},
       {"id": 5, "name": "E2E Verification", "status": "pending"}
     ]
   }
   ```
   Save via `write_file` and update status as each milestone is empirically proven.

2. **Phase 1 — Scaffold Foundation & Database:**
   - Inspect existing ports and containers to prevent collisions.
   - Run migrations and seeders via `terminal`. Confirm tables exist.
   - Verify database constraints (`NUMERIC` precision, foreign keys, uniqueness).

3. **Phase 2 — Implement Backend & Business Invariants:**
   - Write controllers, models, and routes.
   - Enforce domain invariants (e.g. debit equals credit, positive quantities, role checks).
   - Test endpoints via `terminal` with direct HTTP requests.

4. **Phase 3 — Construct User Interface (The 2-Phase Engineering Protocol):**
   - **Phase 3a (Barebones Grid & Functional Engine):** Do not attempt full visual styling immediately. Focus 100% on container grid hierarchy (CSS Grid/Flexbox), component layout, form inputs, and wiring real CRUD state. Keep aesthetics clean and barebones (functional wireframe).
   - **Checkpoint (Vibe & Theme Confirmation):** Once core functionality works on screen, ask what vibe is desired only if the user has not already specified one. Preserve a previously chosen vibe rather than asking again.
   - **Phase 3b (Aesthetic Craftsmanship & Upnormal Styling):** Query live references matching the chosen vibe, filter through the 5 Hermes Taste Lenses (WCAG AAA >= 7:1, 60 FPS in-place morphing, custom anti-native dialogs/select/date, direct text branding), and polish without touching verified logic.
   - Handle edge states: loading spinners, empty states, network failure fallbacks.
   - Verify layout via `browser_navigate` and inspect DOM elements.

5. **Phase 4 — Configure Production Ingress & Ingress Routing:**
   - Wire reverse proxy (Nginx, Express, or Traefik) to internal application port.
   - Enforce subpath prefix locks (e.g. `SESSION_PATH` and asset prefixes) to prevent path leaks.
   - Place proxy declarations before body-parser middleware to avoid consuming POST streams.

6. **Phase 5 — Honest Verification & Delivery Report:**
   - Execute smoke tests and curl assertions, then exercise the product's defining user journey; a working UI without its core capability is a prototype, not fulfillment.
   - If an error occurs, report exact error output honestly. Never fabricate success.
   - When the user expects to try a web app, provide a verified user-accessible HTTPS link in the first delivery, not only a loopback URL or source archive. Identify temporary preview tunnels as temporary; do not mistake a 200 response for the app's core action working.
   - Report: (a) what was built, (b) verified runtime proof, (c) known limitations or remaining risks.

## Pitfalls
- **Premature Visual Polishing:** Attempting full artistic styling before the underlying grid and CRUD logic operate correctly. Dividing the build into barebones functional wireframe first, then asking for vibe confirmation, prevents cognitive overload and broken state.
- **The "Looks Done" Illusion:** Assuming code works just because it compiled without syntax errors. Always test the running process.
- **Silent Rabbit Holes:** Spending >60 seconds debugging an obscure error without alerting the user. Provide timely progress pulses.
- **Context Drift:** Forgetting earlier constraints after multiple turns. Re-read the build tracker file at each milestone transition.
- **Fabricated Certainty:** Claiming "fitur sudah siap digunakan" when it was never executed in terminal. Categorize unverified work as `LIKELY` or `PENDING TEST`.

## Verification
Execute live smoke testing via `terminal`:
`curl -s -o /dev/null -w "%{http_code}" https://<target-domain>/<app-path>/login`
An HTTP `200` or `302` confirms routing only. Exercise the primary action and verify its effect (including browser media events/output for media products) before declaring end-to-end readiness; report any unverified acceptance criterion separately.
