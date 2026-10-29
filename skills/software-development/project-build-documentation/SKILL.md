---
name: project-build-documentation
description: "Use when building projects. Keep build docs current."
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [project, documentation, build, reproducibility, maintenance]
    related_skills: [structured-project-execution, long-horizon-app-building, ui-ux-execution-standard]
---

# Project Build Documentation

## When to Use

Use when creating a project, adding a substantial feature, changing build/setup/test workflows, or handing a codebase to another developer/agent.

## Habit

1. **Lock the project contract before coding.** During discovery, inspect whether the repository has both `AGENTS.md` and `.onefreq/`. If either is missing, run `docbuddy-adopt .` from the repository root before source edits. This wrapper only adopts missing templates and preserves existing files; then read `AGENTS.md` and relevant `.onefreq/` contracts. If the wrapper is unavailable, use `docbuddy adopt .` for the same non-overwriting bootstrap. Neither adoption command enriches existing architecture/verification docs; run `docbuddy propose`, inspect its diff and scope, and use `docbuddy apply` only after explicit approval. Read README/docs, build scripts, manifests, CI workflows, and trackers; reuse canonical documents.
2. **Build the working docs before implementation.** Every project needs a discoverable canonical README or equivalent covering purpose, prerequisites, setup, run/build, tests, and configuration, alongside `.onefreq/` contracts. Create or complete those documents and initialize the task tracker during setup; treat this as a Stage 1 exit gate before the implementation sprint. Include only commands verified in this repository/environment and mark unverified steps. Update canonical docs and `.onefreq/CURRENT_STATE.md` at milestones when facts/status change; do not defer this to handoff.
3. **Add architecture notes when they remove real onboarding cost.** For multi-service, multi-domain, or non-obvious data flows, record major components, boundaries, important contracts, and where implementation lives. Label claims as observed in code, verified at runtime, approved requirement, assumption, or recommendation; source inspection does not prove ingress exposure, auth behavior, or the state of another DB connection. Capture a decision only when future maintainers would otherwise rediscover its rationale. Prefer links from README over duplicated prose.
4. **Keep state separate from durable documentation.** Use the repository's existing tracker for multi-step work. If none exists and work spans milestones/context, create a small build tracker with scope, criteria, statuses, evidence, and known blockers. Do not turn trackers into permanent architecture docs or overwrite another task's tracker.
5. **Update docs in the same change as the system.** When a change alters setup/build/test commands, APIs, routes, schemas, operational behavior, or an important constraint, update the canonical doc in the same work slice. For implementation-only changes that do not affect how someone builds or operates the project, avoid documentation churn.
6. **Write for execution, not ceremony.** Give exact paths, commands, prerequisites, expected outcomes, and recovery/limitations where useful. Keep pages concise, use headings and links, and remove stale instructions instead of appending contradictions.
7. **Protect private data.** Never put credentials, tokens, personal details, private client/business records, or production data into project documentation. Use synthetic examples and environment-variable names; secret values belong in the approved secret store, never README or tracker.
8. **Verify the documentation.** Run documented commands when safely possible; check referenced paths/links and JSON/YAML syntax for trackers. For requirement/feature traceability, inspect the validator's extraction grammar first: if IDs only occur in Markdown tables while it reads headings/frontmatter, a link-check PASS does not prove ID coverage. Compare declared-ID count with the requirements actually authored; fix extraction or markup before claiming traceability is validated. Rerun validation after the final edit, not only before it. Report what was run and what remains unverified. A successful doc edit is not proof that the documented build works.

## Minimal documentation set

- **Small project:** README with setup/run/build/test and configuration basics; no extra documents unless a real need appears.
- **Growing or multi-step project:** README plus the existing tracker and one focused architecture/operations document if component boundaries or recovery steps are not obvious.
- **Complex service/business system:** README, focused architecture/data-flow notes, operational runbook when required, and current task tracker for active long-horizon work. Avoid duplicate policy files; link to the canonical source.

## Completion gate

A contributor unfamiliar with the latest change should be able to find the supported build/test path, understand relevant contracts, and distinguish verified steps from assumptions. Keep the change set minimal and preserve user-owned dirty files.

Skipped: documentation for its own sake. Add a document only when it reduces real build, maintenance, or recovery effort.

## Related skills

Use `structured-project-execution` and `long-horizon-app-building` for milestone planning and runtime proof; use `ui-ux-execution-standard` when changes affect user interfaces.