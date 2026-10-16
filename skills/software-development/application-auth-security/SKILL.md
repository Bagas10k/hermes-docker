---
name: application-auth-security
description: Use when implementing auth, roles, or tenant access.
version: 0.1.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [security, authentication, authorization, rbac, tenancy]
---

# Application authentication and authorization

## When to Use
Login/session flows, role-based permissions, tenant isolation, protected APIs, uploads, webhooks, and security review of business applications. This is defensive application development, not permission to probe unrelated systems.

## Prerequisites
Read the project's auth middleware, session/storage strategy, trusted identity provider documentation, role model, and test setup. Use maintained libraries already adopted by the project. Never invent cryptography or expose credentials in tool output.

## Procedure
1. Map subjects, resources, actions, roles, ownership, and tenant boundaries. Write an explicit allow/deny matrix; default deny and check authorization on every server entry point, not just page navigation.
2. Reuse a maintained identity/session solution. For password authentication use its supported modern password hashing and reset flow. Ensure reset tokens are expiring and single-use. Avoid account enumeration in login/reset errors.
3. Verify session rotation after login/privilege change, expiration, revocation/logout, and secure cookie attributes. Set HttpOnly, Secure in HTTPS deployments, and appropriate SameSite. Apply CSRF protection to cookie-authenticated mutations; CORS is not authorization or a substitute for CSRF protection.
4. If using JWTs, verify signature with an algorithm allowlist, issuer, audience, expiry, and applicable not-before claims. Decoding a token does not validate it. Define refresh-token rotation/revocation rather than indefinitely trusting tokens after logout.
5. Derive identity and tenant scope from trusted server context. Ignore client-supplied ownership or role fields unless specifically authorized. Apply object-level access checks to lists, details, mutations, exports, background jobs, and file downloads.
6. Validate request shape and bound sizes. Use parameterized database access, output escaping, and deliberate rich-text sanitization. Restrict uploads by content/type/size and store outside executable paths. For outbound URL fetching, consider SSRF including redirects and private-network targets.
7. Add rate limits to abuse-sensitive flows. For webhooks verify provider signatures against the raw body, freshness where supported, and replay/idempotency behavior. Do not retry non-idempotent mutations blindly.
8. Write tests for unauthenticated access, wrong role, another user's ID, cross-tenant access, expired/revoked sessions, mass assignment, and direct endpoint access bypassing the UI. Include positive tests for permitted operations.
9. Review error responses, logs, audit records, dependency advisories, and secret handling. Audit relevant privileged changes without recording passwords, tokens, or unnecessary PII. Never run a bulk dependency fix without inspecting compatibility and the diff.

## Pitfalls
Disable automatic WebSocket upgrade subscriptions in reverse-proxy middleware when enforcing a central upgrade guard; otherwise an independently registered upgrade listener can bypass the HTTP authentication middleware. Explicitly dispatch only approved path prefixes after both session and Origin validation.

When reusing upstream session status, require an explicit authenticated result with authentication still enabled, reject upstream redirects/errors/timeouts, and forward only the intended session cookie. Test against an isolated status server and separately document any untested production login or upstream revocation limitations.

Repair obsolete Laravel role tests by explicitly authenticating an active role-owning model with `actingAs` (or a real super-account session ID), not by weakening middleware or globally converting every session into a login. Keep login metadata consistent with the selected identity; clear stale super-account session keys when switching staff identities. Seed FK parents before children, and allocate standby resources per positive logistics case rather than selecting the first driver, which may be busy from another case. Retain failed early-run evidence: a green default-order suite can hide empty-ledger defects after preceding tests create journals.

Hidden buttons, client-side route guards, unpredictable IDs, and a working login screen do not constitute authorization. A permissive CORS policy does not grant safe access control. Never call a system secure merely because a scanner reported no findings.

For Telegram portal login, derive authorization from an explicit numeric owner/allowlist, never a home-channel ID or username. Read-only `getMe` can verify the bot identity without interfering with gateway updates/webhooks. Keep bot credentials server-side outside public roots. The legacy widget requires BotFather `/setdomain`; a real `Bot domain invalid` response must leave login fail-closed until the user links the domain. Its signature does not bind an application nonce: combine browser-bound single-use challenges, CSRF, freshness and global proof replay protection, and document that OIDC nonce/PKCE provides stronger binding. Strip portal session cookies before forwarding to native upstream apps, and recheck long-lived WebSocket sessions after revocation.

## Segregation of Duties (ERP / finance paths)

Role checks are not internal control. When a system moves money, inventory, or approvals, enforce the separation of FOUR functions: otorisasi (approve), pencatatan (record), penyimpanan aset (hold the asset), rekonsiliasi (reconcile).

Forbidden combinations, enforced at ASSIGNMENT time not at transaction time:
- `O + S` and `P + S` within the same cycle (e.g. approving payments while holding cash; recording receipts while receiving goods).

Why assignment-time: if the dangerous combination can never be granted, the system can never enter a dangerous state. Granting is the choke point, not execution.

Implementation shape (see `erp-engineering-doctrine` for the full DDL and test suite):
- Model permissions as ATOMIC grants (`jurnal.buat`, `kas.keluarkan`), never as coarse roles. Adding a new role must not silently open a forbidden combination.
- Store the forbidden pairs in a table (`larangan_sod`) so the rule is data, reviewable and auditable, not buried in code.
- Enforce with an `AFTER INSERT` trigger on the grant table — it must check the state AFTER the new row lands, or it misses the case where the new grant itself is the second half of the forbidden pair.
- Four-eyes on the document: the approver must never be the document creator. Check it in the approval path, not the UI.
- Approval thresholds by amount (`matriks_persetujuan`) must cover `[0, infinity)` with no gaps. A gap means documents at that value cannot be approved — or worse, slip through as "no rule found".

Small-organisation compromise: you cannot separate four functions across three employees. Use COMPENSATING CONTROLS (owner reviews exception reports weekly, external accountant reconciles the bank, hard value thresholds) — never disable the SOD trigger because it is inconvenient. If the trigger is configurable per tenant, changing that configuration is itself an audited event.

Pitfalls specific to this area:
- A permissive `role` column with a single `WHERE` clause is not segregation of duties.
- Hiding the approve button for the creator is not four-eyes; the server must reject it.
- If the SOD matrix is not verified for gaps and consistency, it silently degrades as the org chart changes.

## Verification
When an application provider or container entrypoint automatically migrates on startup, bypass the entrypoint for regression runners and set the disposable DB configuration before providers boot. Seed only explicit test fixtures; disable schema self-healing through its existing test/cache switch without editing the provider. A network-isolated container with in-memory SQLite keeps permission tests away from live data, and an explicit exception handler must exit nonzero because a framework console renderer may otherwise mask a failed assertion.

When reusing a Docker image's Composer vendor tree, run the isolated checkout at the image's original application path (inside a disposable container), or regenerate its autoload map. Optimized Composer classmaps can otherwise silently load stale application classes from the image even when bootstrap/routes come from the checkout; verify source paths before trusting regression failures or passes.

Run the permission matrix against a local/test system using distinct test identities. Report tested paths and residual risks; only test remote environments within the user's authorized scope.
