---
name: fullstack-delivery
description: Use when testing or releasing full-stack applications.
version: 0.1.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ci, cd, docker, testing, deployment, observability]
---

# Full-stack verification and delivery

## When to Use
Preparing CI, Docker/Compose development environments, release workflows, staging verification, or operational readiness for stateful applications.

## Prerequisites
Discover actual package scripts, lockfiles, CI provider, runtime versions, infrastructure manifests, and existing deployment docs. Use `terminal` for actual commands; do not assume npm, a hosting provider, Docker engine readiness, or production credentials.

## Procedure
1. Define gates from the repository: reproducible dependency install, lint, typecheck, domain tests, API/database integration tests, production build, and end-to-end smoke tests. Match tools already in use. Label new proposed tooling rather than pretending it exists.
2. Test business rules with focused unit tests and persistence/authorization with real integration boundaries. Use disposable test data. For browser tests use accessible locators, deterministic setup, observable waits, and retain failure traces/screenshots. Avoid arbitrary sleeps and retries that conceal regressions.
3. Exercise a core scenario through the UI and server: authenticate, perform an authorized mutation, reload, assert stored state, then assert an unauthorized identity cannot access it. Verify failure/empty/loading states relevant to the change.
4. If containers are requested, use multi-stage builds, a non-root runtime where feasible, locked dependencies, a .dockerignore, and explicit runtime config. Keep secrets out of images/build args. Bind development ports to loopback by default. Health checks must reflect meaningful readiness, not just a running process.
5. For Compose, validate with `docker compose config --quiet` without dumping resolved secrets; verify the engine with `docker info`. Wait for actual health endpoints. Preserve named database volumes; never use `down -v` or prune as routine troubleshooting. Explicitly confirm destructive cleanup scope.
6. Build CI with minimal permissions, explicit service dependencies, lockfile-based installs, and protected secrets. Do not expose deployment credentials to untrusted pull requests. Record required checks and produce useful failure artifacts without secrets/PII.
7. Prepare a release runbook: immutable artifact identity, configuration variable names, migration sequencing, health checks, smoke tests, monitoring, rollback/forward-fix conditions, and accountable target environment. Database rollback needs its own plan.
8. Configure useful structured logs and request IDs; identify error, latency, and resource signals. Include background-job failures, retry limits, idempotency, and shutdown behavior when those components exist. Do not add infrastructure that the application does not need.
9. Deploy only when the target and authorization are explicit. After a deployment, read back its actual status and exercise the target health/smoke paths. A successful CLI exit is not sufficient evidence of a working release.

## Pitfalls
- Built, unit-tested, browser-tested, deployed, and production-ready are different claims.
- Mocks are suitable at controlled external boundaries, not proof that the real integration works.
- Never modify the running Hermes installation's dependencies as part of an application's setup.
- Package managers, DB runtimes, and MCP connectors should be installed for a concrete project need, not to inflate the skill catalog.

## Verification
List exact executed commands and their results; distinguish pre-existing failures from regressions. State which services were real, mocked, or unavailable. End with changed behavior, evidence, and remaining risks rather than a replay of the process.
