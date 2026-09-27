---
name: supabase-selfhosted-ops
description: Supabase Self-Hosted ops, Envoy ingress, and RLS security.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [supabase, postgres, docker, rls, database-ops, envoy]
    related_skills: [database-design-migrations, application-auth-security]
---

# Supabase Self-Hosted Ops & RLS Security

Operational management, health telemetry, Envoy ingress routing, Row Level Security (RLS) enforcement, and automated backup for self-hosted Supabase Docker clusters.

## When to Use

- Inspecting self-hosted Supabase containers, Envoy gateway, and PostgREST connectivity.
- Auditing public database tables for missing RLS policies or permissive leaks.
- Diagnosing PostgREST 401/403/42501 errors, RBAC access denied, and JWT authentication.
- Creating verified backups and dumping PostgreSQL schemas before migrations.
- Don't use for: Supabase Cloud hosted projects (use official Supabase CLI/Management API).

## Prerequisites

- Local Docker daemon running with Supabase Compose cluster (`supabase-db`, `supabase-envoy`, `supabase-rest`, `supabase-auth`, `supabase-storage`, `supabase-studio`).
- Cluster configuration located at `~/supabase/.env` with defined `KONG_HTTP_PORT`, `ANON_KEY`, `SERVICE_ROLE_KEY`, and `DASHBOARD_PASSWORD`.
- Python 3.8+ on the host for running diagnostic automation.

## Quick Reference

Flat commands via terminal and Python helper:

```bash
# Cluster health check & ingress test
python3 ~/.hermes/skills/software-development/supabase-selfhosted-ops/scripts/supabase_ops.py status

# Audit all public tables for RLS enablement and active policies
python3 ~/.hermes/skills/software-development/supabase-selfhosted-ops/scripts/supabase_ops.py audit-rls

# Test PostgREST API connectivity using anon key
python3 ~/.hermes/skills/software-development/supabase-selfhosted-ops/scripts/supabase_ops.py test-api --table drive_folders

# Run safe PostgreSQL schema dump
python3 ~/.hermes/skills/software-development/supabase-selfhosted-ops/scripts/supabase_ops.py backup --output /tmp/supabase_public_schema.sql
```

## Procedure

### Step 1: Health & Ingress Inspection
1. Run `python3 ~/.hermes/skills/software-development/supabase-selfhosted-ops/scripts/supabase_ops.py status`.
2. Verify all 10 core containers report `Up (healthy)`.
3. Completion criterion: `all_containers_healthy: true` and `gateway_http_live: true`.

### Step 2: Row Level Security (RLS) Audit
1. Run `python3 ~/.hermes/skills/software-development/supabase-selfhosted-ops/scripts/supabase_ops.py audit-rls`.
2. Inspect `unprotected_tables` list.
3. Tables with `rowsecurity = true` but 0 policies are in DEFAULT-DENY mode (blocking anon/authenticated inserts).
4. Completion criterion: Every public table has an explicit, tested policy or is documented as intentionally private.

### Step 3: API Endpoint Verification
1. Run `python3 ~/.hermes/skills/software-development/supabase-selfhosted-ops/scripts/supabase_ops.py test-api --table <table_name>`.
2. Confirm anonymous requests pass through Envoy to PostgREST and receive HTTP 200 with scoped JSON payloads.
3. Completion criterion: HTTP status 200 returned for both anon query and service role OpenAPI metadata.

### Step 4: Schema Backup
1. Run `python3 ~/.hermes/skills/software-development/supabase-selfhosted-ops/scripts/supabase_ops.py backup --output <path>`.
2. Completion criterion: Output file exists, is non-empty, and contains valid PostgreSQL DDL statements.

## Pitfalls

1. **Envoy RBAC on Root Schema `/rest/v1/`**: Anonymous keys querying `/rest/v1/` directly encounter `RBAC: access denied`. Querying specific tables (e.g. `/rest/v1/table_name`) or `/rest/v1/rpc/` works as intended.
2. **Case Sensitivity in Table Names**: Tables created with PascalCase (e.g. `"Halo"`) require double quotes in SQL queries. Without quotes, PostgreSQL defaults to lowercase and fails with `relation does not exist`.
3. **Studio Dashboard Basic Auth**: Supabase Studio is protected by HTTP Basic Auth (`DASHBOARD_USERNAME` & `DASHBOARD_PASSWORD`). Requests without credentials return HTTP 401.
4. **Service Role Key Exposure**: Never embed `SERVICE_ROLE_KEY` in frontend bundles; it bypasses RLS completely.

## Verification

Run the verification test suite:

```bash
python3 ~/.hermes/skills/software-development/supabase-selfhosted-ops/scripts/supabase_ops.py status
python3 ~/.hermes/skills/software-development/supabase-selfhosted-ops/scripts/supabase_ops.py audit-rls
```

Success is verified when the status JSON returns `all_containers_healthy: true` and the table audit classifies each relation deterministically.
