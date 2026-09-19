---
name: database-design-migrations
description: Use when designing schemas or database migrations.
version: 0.1.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [database, sql, migrations, transactions, performance]
---

# Database design and safe migrations

## When to Use
Designing relational data models, changing ORM schemas, writing migrations, diagnosing queries, or protecting consistency in business systems.

## Prerequisites
Read existing migrations, ORM configuration, database engine/version declarations, and relevant queries with `read_file` and `search_files`. Identify the target environment without printing connection secrets. Confirm a disposable development/test database before any migration execution; production data changes require explicit approval.

## Procedure
1. Model entities, cardinality, ownership/tenant boundaries, lifecycle, and business invariants. Define primary and foreign keys, nullability, unique constraints, deletion behavior, money precision, and time semantics. Avoid soft-delete unless recovery/audit requirements justify its query complexity.
2. Put invariants in database constraints as well as server validation. For multi-tenancy, ensure uniqueness and relations cannot silently cross tenants. Consider composite keys or equivalent enforced checks where suitable.
3. Design indexes from actual filters, joins, ordering, and cardinality. Inspect query plans on representative non-sensitive data using engine-appropriate EXPLAIN; remember EXPLAIN ANALYZE executes its query. Measure before and after; do not invent performance numbers.
4. Define transaction boundaries and isolation needed for concurrent operations. Use atomic updates, conditional writes, row locking, or optimistic version checks as appropriate. Test competing booking/inventory/balance requests rather than relying on a read-then-write check.
5. Generate migrations with the project's existing tool. Inspect generated SQL. For live compatibility use expand -> backfill in bounded resumable batches -> validate -> switch readers/writers -> contract in a later approved release. Analyze locks and table rewrites for the actual engine/version.
6. Rehearse both an empty-database install and an upgrade from a representative prior schema in disposable databases. Assert old records remain intact, new constraints work, and the application can read/write after upgrade. Do not run destructive ORM reset or schema push on shared data.
7. Plan backup/restore or forward-fix recovery; rollback code does not automatically reverse data changes. Verify restoration separately before claiming backups are recoverable. Document irreversible steps and compatibility window.
8. Check query count, N+1 behavior, bounded pagination, connection pool sizing, and timeout behavior on affected paths. Keep raw query parameters bound, not interpolated.

## Pitfalls
- Successful schema generation is not a successfully applied migration.
- SQLite-only tests cannot prove PostgreSQL/MySQL locking, enum, or index behavior.
- ORM validation cannot replace uniqueness under concurrent requests.
- Docker CLI availability does not imply a running engine. Verify `docker info` through `terminal`; if unavailable, report the blocker or use an approved existing local database. Never silently change the production database choice.
- Do not log connection strings, dump production data into fixtures, or delete volumes to fix a connection error.

## Verification
Report actual migration targets, test commands, integrity checks, query-plan findings, and any untested recovery or concurrency behavior. Preserve migration history already applied to shared environments; add a new migration rather than rewriting it.
