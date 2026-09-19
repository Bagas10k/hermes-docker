---
name: fullstack-systems
description: Use when building full-stack business systems.
version: 0.1.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [fullstack, architecture, backend, frontend, business-systems]
---

# Full-stack business systems

Build working business workflows, not a landing page that resembles an application. This is a stack-neutral procedure; use the actual repository and its documentation as the source of truth.

## When to Use
- Building or extending dashboards, SaaS, admin systems, inventory, approvals, booking, CRM, ERP, or other stateful applications.
- Planning a feature spanning UI, API, persistence, and permissions.
- Do not impose this workflow on an explicitly requested static mockup.

## Prerequisites
Use `search_files`, `read_file`, and `terminal` to discover the repository, project instructions, git status, manifests, lockfiles, existing routes, schema, tests, and CI. Ask for the repository path if none is provided or discoverable. Never treat the home directory as the application repository.

## Procedure
1. Identify actors, the core use case, state transitions, ownership, permission boundaries, and failure cases. For an existing system, trace one comparable feature first. Ask only about choices that materially change implementation, scope, or external effects.
2. Write concise acceptance criteria for the requested feature. Include success, invalid input, denied access, and persisted state. Distinguish confirmed requirements from assumptions.
3. Preserve the established stack and package manager. For a new system, propose the simplest maintainable architecture consistent with requirements; prefer a modular monolith unless independent deployment or scaling is justified. Do not introduce microservices, queues, caching, or a new framework solely for appearance.
4. Define the data model and API contract before parallel implementation: types, validation, identifiers, error shape, pagination, authorization, and transaction boundaries. Separate transport handlers from domain rules and persistence without gratuitous abstraction. Record consequential tradeoffs in a short ADR when useful.
5. Implement a vertical slice: migration -> domain behavior -> server endpoint -> real UI -> integration test. Add a failing regression/behavior test before changing behavior. Load `test-driven-development`; use `systematic-debugging` for unexplained failures.
6. Enforce business invariants on the server and with database constraints where appropriate. Test concurrent writes for inventory, booking, balances, and quotas. Use decimal or integer minor units for money and explicit timezone semantics for dates.
7. Connect UI to real endpoints. Include loading, empty, error, validation, forbidden, and success states. Make forms and tables keyboard accessible, preserve user input on failures, and handle pagination/filtering consistently. Never pass fixture arrays, localStorage, hidden buttons, or mocked HTTP as production persistence or access control.
8. Run the repository's lint, type checks, relevant tests, and production build using discovered commands. Exercise a critical workflow in a browser against a real local backend and development database; verify the change survives reload. Use external-service mocks only at explicit boundaries and report their limits.
9. Review the diff for scope, security, accidental secrets, migration compatibility, and regressions. Do not auto-commit, push, publish, or deploy unless authorized. Record exact commands and outcomes, including blocked checks.

## Delivery
Report what works, verification evidence, and remaining limitations in concise Indonesian unless the user requests another language. Do not label a local build production-ready without deployment and operational verification. Keep project-specific setup commands and architecture facts in the project's existing documentation, not global memory.

## Pitfalls
- A screenshot proves rendering, not business correctness.
- A successful HTTP status proves neither authorization nor persistence.
- A skill is procedural guidance, not an installed runtime or a test result.
- On Windows Git Bash use native forward-slash paths for native executables; use `node.exe` for noninteractive checks when `node` is a winpty alias.
- Reuse the project lockfile and toolchain; do not globally install competing package managers unnecessarily.

## Verification
Every acceptance criterion maps to a real test or documented manual check. Identify checks not executed; never replace unavailable integrations with fabricated evidence.
