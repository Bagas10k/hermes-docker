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

Hidden buttons, client-side route guards, unpredictable IDs, and a working login screen do not constitute authorization. A permissive CORS policy does not grant safe access control. Never call a system secure merely because a scanner reported no findings.

For Telegram portal login, derive authorization from an explicit numeric owner/allowlist, never a home-channel ID or username. Read-only `getMe` can verify the bot identity without interfering with gateway updates/webhooks. Keep bot credentials server-side outside public roots. The legacy widget requires BotFather `/setdomain`; a real `Bot domain invalid` response must leave login fail-closed until the user links the domain. Its signature does not bind an application nonce: combine browser-bound single-use challenges, CSRF, freshness and global proof replay protection, and document that OIDC nonce/PKCE provides stronger binding. Strip portal session cookies before forwarding to native upstream apps, and recheck long-lived WebSocket sessions after revocation.

## Verification
Run the permission matrix against a local/test system using distinct test identities. Report tested paths and residual risks; only test remote environments within the user's authorized scope.
