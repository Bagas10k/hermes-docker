# Account lifecycle management

Use for an administrator-managed account directory in an application that already has users, sessions, roles, and business records. Reuse those primitives; do not replace the identity system merely to add an account screen.

## 1. Trace the current identity contract

Read the user model, login/logout controller, central authenticated middleware, role resolver, session schema/driver, route registration, and test login helper. Identify which grants protect both HTTP and direct-service operations. Distinguish employee master records from login accounts. Define exact create/edit fields and the approved roles before writing a form.

Use the same effective-access predicate at login and on protected requests: the stored account must be active and its role must be explicitly allowed. Refresh the user from storage instead of trusting a cached guard model. Inspect every caller of a shared role resolver before changing it so selectors, documents, and mutations remain consistent.

## 2. Make an additive schema transition

For a boolean active flag, preserve existing accounts with an explicit enabled default. For versioned session revocation, add a monotonically increasing integer authentication version with a documented initial value. Add a small audit table only when needed; record actor ID, target ID, action, changed field names, role/status transitions, and time, not credential material.

Deploy schema before code that requires new columns while ingress is held. Rehearse the exact named migration on a disposable copy of the current target engine. Hash an explicit ordered selection of pre-existing user columns before and after; hashing SELECT * would falsely flag the newly added defaults as a credential change. Preserve separate financial-table hashes and counts.

## 3. Serialize account changes at the invariant boundary

Validate scalar name/email/role/status/password fields and allowlist write columns. Normalize email consistently before duplicate lookup and persistence, retain the database unique constraint, and translate only a confirmed duplicate-key error into a duplicate-email validation response; SQLSTATE 23000 also covers unrelated integrity failures.

For a small account directory, locking the existing role rows in stable user-ID order provides a simple serialization point. After acquiring it, lock/re-read actor and target, then check authorization and the last-active-admin invariant before any change. Evaluate both demotion and deactivation, including concurrent changes. Never let an earlier request-level check stand in for this transactional check.

Reject self-disable/self-demotion. Before changing the role or disabling a shift owner, check unresolved operational responsibility such as an open cashier shift; do not orphan an open cash drawer. Do not silently broaden this guard to unrelated profile/password changes. Keep account edits, role writes, audit insertion, and session revocation atomic.

On create, require a confirmed password under the agreed policy and hash it using the framework. On edit, an absent/empty password means unchanged. Return explicit safe fields, never a raw model/hash/token/authentication version; mark account listings private/no-store.

## 4. Bind sessions to both identity and version

At successful login, regenerate the session and save a tuple such as [user_id, auth_version]. On each authenticated request, fetch the current account and compare the tuple; logout, invalidate the session, and regenerate CSRF state when the account is disabled or the tuple is stale.

For role/status/password changes, advance the stored version, rotate the remember token, and remove persisted sessions for the target. Define the migration compatibility policy for pre-version sessions narrowly: permit and stamp only an authorized initial-version session, or require reauthentication. Do not adopt an arbitrary newer version for a session missing its stamp, because that can revive stale access. Handle framework-validated remember-me restoration explicitly and test it if supported.

## 5. Integrate the Admin surface

Provide a list with labelled add/edit popups, known role options, and active status. For account editing, leave password blank and explain the unchanged meaning. Disable self-demotion/deactivation controls for clarity, but retain server enforcement. Clear secrets after save/close. Handle save errors in the same form rather than closing on failure. Read back the saved account through the authorized API and update the list.

Attach lazy loading to the application's actual navigation state, including deep links and keyboard navigation; a click-only loader misses arrow-key panel selection. Reuse dialog behavior with scoped listeners so adding account popups does not register duplicate Escape/cancel handlers on payment dialogs.

## 6. Verify without modifying real accounts

1. Guard the disposable database before RefreshDatabase or fixtures run.
2. Exercise actual registered routes: guest denial, cashier GET/POST/PUT denial, Admin list/create/edit, duplicate email, invalid role, weak/mismatched password, and a safe response field allowlist.
3. Assert hashing using the framework verifier, then prove that empty edit-password retains the prior hash. Check audit content contains no submitted credentials or personal strings.
4. Test self-lockout, the last-active-admin invariant, and open-shift restrictions. Test session deletion, version advancement, stored inactive-login denial, and a valid session becoming invalid on its next request.
5. When using actingAs, stamp the selected identity/version in the test helper; deliberately avoid refreshing that helper in stale-session tests. Never weaken production middleware to make role-switching fixtures pass.
6. In a real isolated browser, edit a synthetic non-secret field, read back the HTTP result, inspect role/status controls and focus restoration, and verify narrow/wide form bounds. Credentials must use the approved vault/masked path when a login or password form is exercised.
7. After authorized deployment, verify effective config, source manifest, named migration status, unchanged pre-existing account/financial values, and public guest denial. A controller render or login HTTP 200 is not authenticated public-browser coverage; disclose that gate independently.
