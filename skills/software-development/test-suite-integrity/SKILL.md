---
name: test-suite-integrity
description: Use when a test suite touches live state or copies logic.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [testing, isolation, production-safety, verification, data-integrity]
---

# Test Suite Integrity

A green suite is only evidence if the suite is honest. Three failure modes make a
passing suite worse than no suite: it mutates production, it asserts on a copy of
the logic, or it leaves data nothing can ever read again.

## When to Use

- Writing or repairing tests that run against a live instance (HTTP, DB, or UI).
- A suite passes but the app behaves differently afterwards.
- Reviewing an assertion that "can never fail".
- Deleting or cascading records, profiles, tenants, or workspaces.

## Procedure

### 1. Isolate writes before asserting anything

Identify the actual target connection and every side effect before setup. Inspect helpers,
query scopes and page-load synchronizers before classifying a test as read-only: a method
named as a schema check can execute ALTER TABLE or rewrite source identities. Exercise
uncertain paths only in a disposable instance and compare schema AND source rows before
and after, because unchanged ledger counts do not exclude destructive master-data writes.
Run financial, ledger, migration, destructive, and cross-module write tests in a disposable
database or instance of the target engine/version, never in a live application with a
promise to restore it afterwards. For an explicitly authorized, non-financial live test, use a
**throwaway record** and snapshot any live configuration before changing it. Register
cleanup immediately after setup; `atexit` handles normal interpreter shutdown and many
handled failures, not SIGKILL, power loss, or every crash. Isolation must remain safe
when cleanup never runs.

```python
def setup():
    s = state()
    _ORIG["profile"] = s["active_profile"]
    created = post_json("/api/profile", {"action": "create", "name": "suite-scratch"})
    _ORIG["test_id"] = created["active_profile"]

setup()
atexit.register(teardown)   # best-effort shutdown cleanup; not a crash-safety boundary
```

Why it matters: a suite that pointed `base_url` at a local mock **on the live
profile** turned every green run into a silent production reconfiguration. The app
kept answering, but from a dead endpoint, and the failure surfaced later as "the AI
stopped replying" rather than as a test bug.

Pass disposable paths to every stateful constructor, including secondary asset/auth stores created by a router; overriding only the primary database leaves default storage writes outside the sandbox. Seed persisted authentication fixtures before constructing an in-memory auth provider, or use its supported store API: editing its file afterwards does not update the provider's already-loaded sessions.

Check it: snapshot the live record before the run and diff it after. If it changed,
the suite is destructive.

### 2. Never re-implement the logic under test

Copying the handler's body into the assertion passes even when the handler is
broken — it only proves you can copy code. Drive the real path:

- an HTTP call to the running server, or
- a call into the actual exported function or framework HTTP kernel.

Label the boundary exercised: a direct controller call proves controller behavior,
not route authorization; an in-process HTTP kernel request exercises middleware but
is not a network or browser test. For role probes, provision real synthetic accounts
in the disposable database, retain authentication/session/CSRF middleware, and compare
HTTP response plus persisted before/after state. Resolve every probe URL from the actual
named route before testing: a 404 on an invented write URL does not measure the role guard.
Pair an unauthorized role with an authorized-role control and a missing-CSRF control;
a 419 measures CSRF, and a 302 alone does not distinguish successful mutation from an
error redirect. For redirected reads, assert both status and the intended destination.

A test that duplicates a branch is a **vacuous test**. Delete it and write one that
fails when the branch is removed.

Construct control-character negatives with actual bytes, such as `String.fromCharCode(10)`, and assert their code points before invoking the real boundary; a string containing backslash-plus-n tests a different input. Compare fixtures with captured wire shapes before changing production: `text` versus `content`, top-level versus nested fields, and native identifier names are contract differences, not reasons to weaken assertions.

Await the observable asynchronous effect before inspecting it. A queued/admitted response can precede the native call; use an event/promise or a bounded event-loop checkpoint in deterministic component tests, then assert the exact call count and parameters. Do not add fixture-specific synchronous behavior to production just to satisfy an immediate assertion.

For browser interaction claims, observe the external effect rather than an event flag:
assert prompt request counts and retained draft text for Enter/IME behavior, not only
`defaultPrevented`. Change the relevant geometry before testing keyboard overlap;
dispatching `resize` at an unchanged viewport height cannot prove keyboard handling.
Label injected viewport measurements as simulation rather than physical-device evidence.
Treat source-only accessibility findings as hypotheses until the browser reproduces them,
because native controls may already provide the claimed missing behavior.
For reconnect claims, force the real stream to disconnect/reopen or switch away and back, require a fresh stream request/snapshot plus at least one existing tool row, then verify row identity/count. Dispatching an unhandled custom browser event and observing unchanged rows proves no recovery behavior. Missing runtimes, hidden controls, or absent prompts must fail or remain untested, never pass privacy/approval assertions by default.

### 3. Test the domain's deletion policy, not a blanket cascade

Determine whether deletion should remove owned children, be rejected, or preserve
historical evidence before writing the assertion. For disposable ownership records,
exercise `create parent → create child → delete parent` and assert permitted children
are removed and active/current pointers are repaired. For posted financial documents,
used accounts, and depreciated assets, prefer the approved rejection or reversal path;
cascading their history can destroy the evidence the suite is meant to protect.

Count references to missing parents and inspect each relation: an orphan signals an
integrity gap, but it does not prove cascading deletion is the correct repair. Verify
rejected deletion leaves both parent and children unchanged.

### 4. Verify the implementation and assertion runtime before testing

Inspect an automatically detected verification recipe before treating its green result as acceptance. Require the commands to execute the intended suite and readiness to probe the intended application route with the expected status; an unrelated listener or a login response can satisfy a generic reachability check. Name the candidate suite separately when the recipe still covers an older surface; repeatedly rerunning the older recipe does not close the missing candidate or visual gate. Save an authorized project-specific recipe with a disposable verification host when necessary, then verify teardown. If a recipe write is refused or its approval expires, leave it unchanged and run the scoped checks separately instead of writing through another tool. Keep local startup evidence distinct from public deployment and genuine external-client acceptance.

When an application image contains baked code, synchronize the entry point and all
called services/controllers/views/routes into the disposable instance before testing.
Verify critical source hashes; refresh route/view caches after copying, because a test
can otherwise pass against an older implementation. Prefer one shared synchronization
preflight over divergent dependency lists in each scenario branch.

Inspect the initial schema phase before choosing the image: a candidate that already
runs all migrations at startup cannot satisfy a premigration assertion. Keep the real
premigration check on a deliberately old isolated baseline, then test the candidate's
upgrade/rerun separately; do not weaken the assertion or call the phase mismatch an
application regression.

Separate environment-dependent security and browser suites when their contracts differ.
Laravel's testing environment can bypass CSRF by design, so run missing-token/authorization
checks with CSRF enabled and run the browser fixture under its required testing setup.
Require both runs to pass and retain shared-source hash parity; do not change an expected
419 to success merely to combine incompatible harness modes.

Verify lint output names the intended source files. Pass shell-loop filenames through
positional arguments when invoking a container from another shell, because premature
expansion of `$file` can leave `php -l` checking empty standard input and returning a
misleading success.

Inspect delegated probe source and raw execution artifacts before accepting its
reported results. If a reviewer times out after writing a partial runner, inspect its
source and artifact once, correct only verified harness defects, then rerun the full
named suite yourself; a timeout or saved partial PASS is not a QC verdict. Preserve
runner stdout/stderr and exit status as execution logs; keep handwritten summaries
in reports, never as substitutes for captured logs. Keep raw HTTP probe output and
session cookies private; persist/share only aggregate results, failure names, and
source hashes, because diagnostic response objects can contain live session IDs.
If a completion summary conflicts with recorded failures or a broken aggregation runner, inspect which commands actually executed, fix the runner, and rerun the complete named set against one frozen revision. Save each subprocess return code separately; a semicolon chain's final exit status cannot prove earlier commands passed. Record expected/executed/passed suite counts programmatically and hash transitive helpers as well as the entry module, because an unchanged service file can load a changed filter or catalog.
Make candidate acceptance failure return nonzero even when the harness completed;
a baseline reproduction mode may record expected defects, but must label them as
reproduced failures rather than application PASS. Reject a PASS verdict that also
lists an unresolved security or correctness blocker; inspect the finding and rerun
the corrected revision instead of trusting the verdict word.
Separate a characterization probe from an acceptance test: an assertion that a private path remains exposed or a string flag becomes true proves the observed defect, not its acceptability. Convert confirmed unsafe behavior into a desired-boundary failing assertion before repairing it; do not downgrade a violated requirement to INFO merely because the probe exits zero.
Relabel expected HTTP codes or database changes as predictions when the worker only
authored the script; a completion summary is not runtime proof. Bind each QC verdict
to source and test hashes: a rejected earlier candidate is not a verdict on a later
revision, and a later edit invalidates byte-identical PASS claims until rechecked.
For a reproduction-only task, hash the application before and after, and report a
confirmed anomaly separately from a fix, deployment, or historical-data correction.
Archive baseline reports, raw logs, screenshots, and source hashes before a revised run
can overwrite them; observed RED is evidence worth preserving, not a stale output to erase.
Use a configurable candidate root and output directory to exercise the intended isolated
revision; do not overwrite an earlier approved candidate merely to satisfy hardcoded test
paths. Preserve assertions while adapting the harness, and compare enumerated check names
and totals programmatically before accepting its summary.

Enable the assertion runtime explicitly. For standalone PHP checks, use
`php -d zend.assertions=1 -d assert.exception=1 scripts/<scenario>.php` or explicit
exceptions; a PASS label after disabled `assert()` calls proves nothing. Require the
selected mode's exact terminal success marker as well as the process exit status:
a console bootstrap can render a caught exception and still exit zero, leaving later
assertions unexecuted. Reject unknown modes before setup, emit each mode's marker only
after its assertions, and never let a generic final PASS claim unselected modes ran.
Keep reproduction success separate from application correctness: an anomaly probe
succeeds when it demonstrates the defect, not when the application passes its invariant.
To claim RED→GREEN, run the desired-behavior assertion against the pre-fix implementation
and observe its specific failure; a successful probe that asserts the old defect is
reproduction evidence, not itself that failing acceptance test. Scope QC properties to
the observations: a few stored two-decimal cases do not prove universal freedom from
floating-point drift, and correct lock placement does not prove a simultaneous
multi-process outcome.

When inspecting failed Laravel SQL, do not interpret an empty `DB::listen` capture as
proof that no query was attempted: failed statements may never emit `QueryExecuted`.
Capture the real exception and inspect the exact schema; distinguish an authentication
rejection from a route that bypassed authorization but failed with a database 500. Do not
claim data disclosure unless a response actually returned the protected data.

### Reject fixture-aware production behavior

Never add production branches keyed to a fixture ID, test title, temporary-directory name, or compatibility flag merely to preserve a stale assertion. A worker must remain `stopping` until its actual child exit is observed, and a turn counter must use one definition for synthetic and real sessions. Correct the fixture expectation and await the real lifecycle instead; search implementation diffs for fixture names and `compatMode` before accepting delegated PASS claims. Such branches make tests exercise different behavior from production and invalidate the evidence.

### 5. Prove the assertion can fail, then test intersections

For a non-trivial new guard, disable it only in the disposable copy and confirm the
specific expected invariant turns red; distinguish that failure from fixture, syntax,
or dependency errors. Then restore and rerun. Run related scenarios separately and
together on the same current implementation. Scope counts to the records/references
owned by each scenario rather than assuming a globally empty table; otherwise an
earlier scenario's valid rows can look like duplicate posting. Keep fixture cleanup
scoped to those same identities; deleting every row with a shared production-style
prefix can erase an earlier scenario's evidence even in a disposable database.

For rejection tests, isolate competing guards: a negative-nominal case that reuses a
busy driver can pass because availability rejected it before nominal validation.
Use unique fixture identities or retire only scenario-owned active assignments.
Clear old flash errors before each request, then require the expected HTTP status,
the specific rejection reason, and unchanged source/stock/bank/ledger snapshots.
Unchanged rows alone also result from a 419, 404 or 500; a stale error message proves
nothing about the current request. Pair the rejection with a successful authorized
operation through the same harness. For direct-controller checks, capture the actual
validation exception or fresh redirect error and label the missing middleware coverage.
When a combined run stops, mark later scenarios not executed, not passed. Preserve
exit status and raw output for each gate.

### 6. Test transitions and repeated side effects, not just enum values

1. List the persisted source status, required approval evidence, target status and
   side-effect owner before editing a quick-status endpoint. A valid target enum is
   not permission to move there from every source state.
2. Exercise draft → return, returned → active, and awaiting physical confirmation →
   active as negative cases where the domain requires approval or warehouse receipt.
   Test legitimate approved progress separately; do not preserve a bypass merely
   because an old dropdown offered it.
3. Evaluate transition guards against the freshly locked row inside the transaction
   held through commit. Locking again after checking a stale model leaves the decision
   unprotected; inspect that ordering and use a two-process test before claiming a
   concurrency result.
4. Repeat a terminal action and compare timestamps, driver/vehicle availability,
   stock and paid-payment fields, not just status. Require a no-op or explicit rejection:
   a repeated completion can keep `paid` while overwriting its amounts or finish time.
5. After confirming a stock count, introduce a later fixture stock movement and retry
   confirm, edit and delete. Preserve the later stock and confirmed document; repeating
   the original count must not reset today's inventory to the old snapshot.

## Pitfalls

- **Cleanup mistaken for isolation.** Register cleanup close to setup and preserve
  the primary exception, but assume abrupt termination can bypass both `finally`
  and `atexit`; disposable storage, not teardown, is the protection boundary.
- **A timeout race mistaken for cancellation.** `Promise.race` settles the caller but leaves its asynchronous work running. For disposable native probes, reject new operations after a deadline, close the owned client to reject pending RPC/start promises, await the main loop and timeout cleanup, then remove the temporary home. Test a forced short deadline and require nonzero probe status, a settled lifecycle, dead owned processes and removed state; a normal successful run does not exercise timeout safety.
- **Cleanup that masks the real failure.** Wrap teardown in its own `try/except`
  and log to stderr; never let a cleanup error replace the assertion error. Record
  exact container/network/volume IDs owned by the run and read those targets back
  after teardown; other resources sharing a prefix are neither yours to delete nor
  evidence that this run leaked. Report unremoved owned resources instead of treating
  runner exit zero as cleanup proof.
- **Fixture names leaking into production config.** A test that writes
  `model: "inspect"`, `base_url: http://127.0.0.1:8099` and never restores leaves
  the live app pointing at fixtures. Isolate (step 1) instead of trusting restore.
- **Scrubbed synthetic credentials becoming vacuous fixtures.** A tool/privacy hook can replace a secret-shaped literal with a redaction placeholder before the test reaches disk. Construct the recognized prefix and neutral synthetic value at runtime, assert the resulting input actually matches the intended credential shape, and pair absence checks with delivery of ordinary surrounding text. Inspect the saved fixture before accepting a redaction PASS; never disable production redaction or use real secrets for the test.
- **Counting assertions as coverage.** More assertions over a copied implementation
  is not more evidence. Check that at least one test drives the real path.

## Verification

Before reporting a suite as passing:

1. Live state unchanged by the run (diff before/after).
2. No scratch records left behind.
3. At least one test observed failing when the behaviour was deliberately broken.
4. The approved cascade, rejection, or reversal policy is exercised for each delete path.
5. The suite uses current source, enabled assertions, and both targeted and combined runs.
