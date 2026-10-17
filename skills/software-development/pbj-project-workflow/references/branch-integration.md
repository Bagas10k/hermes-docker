# Collaborator-branch comparison and selective integration

Use when reviewing incoming PBJ changes against a locally hardened, possibly dirty worktree. Preserve the owner's stated conflict priority; do not convert audit permission into a merge or runtime migration.

## 1. Freeze the versions and protect local work

1. In the verified repository, run `git status --short --branch`, `git remote -v`, and `git fetch origin --prune`. Discover exact ref spelling before selecting it.
2. Pin `git rev-parse HEAD origin/<branch>` and `git merge-base HEAD origin/<branch>`. Use these fixed object IDs throughout the review so a moving remote cannot silently change the target.
3. Enumerate local tracked changes with `git diff --name-only` and relevant untracked source with `git ls-files --others --exclude-standard`. Save a private source snapshot plus SHA-256 manifest outside the repository. Include tests, routes, views and services; exclude secrets, sessions and runtime storage.
4. Enumerate incoming files with `git diff --name-status <base> <incoming>`. Record separately: incoming changes, files changed on both sides, and actual text conflicts. Do not infer conflict count from the number of overlapping filenames.

## 2. Simulate without touching the worktree

For each incoming path, export `git show <base>:<path>` and `git show <incoming>:<path>` to a private scratch directory, and copy the ACTUAL working file as the local side. Treat an absent base or new file explicitly rather than mistaking an expected missing path for a failed audit.

Run `git merge-file -p <ours-snapshot> <base-snapshot> <incoming-snapshot>` and save its stdout as a preview, never as the live file. Interpret positive conflict results separately from command errors. Do not use checkout/reset/stash or blanket `-X ours` to manufacture a clean workspace: those operations can hide or discard the very changes the owner prioritized.

Inspect semantic conflicts even when text merges cleanly: middleware exemptions, posting dates, reversal ownership, historical filtering and schema prerequisites can change behavior on distant lines.

## 3. Assign bounded audit ownership

Split independent concerns into small principal-file scopes, typically three files: financial lifecycle, driver/master schema, or shipment/form payloads. Give each worker the pinned refs, current-worktree priority, no-write boundaries and an exact report path. Dependencies may be read, but do not let two workers own the same edits. Keep a financial QC reviewer separate from implementation.

The parent owns aggregation, conflict decisions and serialized disposable tests. Worker reports are hypotheses until checked against the pinned code and real execution. Do not claim all incoming files were reviewed merely because a few scopes or probes passed.

## 4. Probe dangerous behavior before adoption

- Inspect helpers named `has*`, `memiliki*`, scopes and page-load synchronizers for DDL/DML before treating them as reads. On disposable target MySQL, call the real helper and compare schema nullability, columns and source rows before/after; record executed ALTER statements. Keep schema changes in explicit migrations, not hidden in page visits.
- Trace migration calls into application models. A migration invoking a mutable synchronizer may rename IDs, reclassify employees or clear document links instead of merely adding schema. Reject hard-coded legacy-code transformations and silent exception swallowing from automatic adoption; require approved mappings, atomicity, preserved evidence and separate rehearsal.
- Preserve historical employee receivables, payroll and ritase when introducing internal/partner categories. Current ownership filters must not make already-posted debt or evidence disappear. Never infer ownership solely from an old code or matching name.
- Audit route additions together with every global-middleware exemption. Drive anonymous HTTP requests through the real kernel and check the exact schema column names. A 500 after an authentication bypass is not a successful authorization rejection, but also does not establish successful data disclosure when the query failed. Report those findings separately.
- Treat foreign-key disabling and broad relationship rewrites as integrity risks, not proof of a safe identity migration. Check every referencing domain and historical audit/source reference before considering a mapping.

Use only guarded disposable databases and frozen source snapshots for mutating probes. Keep live runtime, historical data and credentials outside the review.

## 5. Adopt selectively and prove preservation

Classify each change as retain-local, adapt, safe-to-adopt, owner-decision, or unverified. Apply only a bounded approved adaptation with a failing reproduction and a distinct hardening pass; do not import unrelated migrations or debug endpoints along with useful UI work.

Audit the integration boundary separately from each file's internal correctness. For a new Blade partial, trace the host view's option variables, controller `compact` payload, Alpine state/watchers/handlers and canonical hidden form fields. A partial can pass scoped QC and still break its host because its companion files are missing. Do not hide the dependency by supplying empty arrays that make partner selection unusable. Freeze the compatible companion set, exercise actual render, dropdown interaction and submit/readback on disposable data, then adopt the set together. A dependency-free refinement may ship separately only when its exact source and behavior are independently verified.

Recheck the protected-file manifest after read-only auditing. After intentional edits, review exact diffs, rerun affected and combined financial tests, then check role enforcement, browser payloads, exports and visual evidence where relevant. Verify packaged code matches the tested hashes.

Consolidate business impact, evidence limits and adoption decisions in the existing readable PBJ status document. Distinguish reviewed, reproduced, corrected, integrated and deployed; a successful probe proving a defect is not a completed correction.

## 6. Publish only the approved branch slice

1. Fetch the target branch and compare local/remote ancestry before staging. Do not resolve remote drift with an automatic rebase, merge or force push on a dirty collaborator workspace.
2. Build an explicit manifest of selected app, route, view, migration, test and documentation files. Leave quarantined candidates and their exploratory RED-only scenarios outside the release. Preserve those scenarios privately rather than weakening or deleting the material assertions that already pass.
3. Audit release notes and run commands against the selected tree. Tell readers to use the disposable env-gated runner; a bare fixture command can otherwise bootstrap an active application's database. Describe migrations as rehearsed, not live-applied.
4. Re-run the affected and combined suites. When extracting a passing test subset from exploratory work, verify the retained branches are unchanged and execute the release subset again.
5. Stage explicit paths, then inspect `git diff --cached --name-only` and `git diff --cached --check`. A failed `git add` may already have staged other arguments, so inspect the index before retrying. Normalize whitespace without changing semantics; preserve Markdown hard breaks explicitly. Do not force-add ignored logs broadly: only include exact, scrubbed synthetic evidence files when the release needs them.
6. Compare index blobs to the manifest, check reviewed hashes remain current, and commit only the selected set. If whitespace normalization changes an audited hash, record that difference instead of claiming byte-identical QC.
7. Push with an explicit destination such as `git push origin HEAD:refs/heads/sandbox`, without force. Read back `git ls-remote --heads origin refs/heads/sandbox` and the GitHub branch SHA; require both to equal the local commit before reporting success. State test execution and deployment separately, and do not call absent remote checks a green CI run.

## 7. Assess migration safety before an approved release

1. Enumerate the target database's migration history and ENTIRE pending set read-only before recommending execution. Laravel `php artisan migrate` applies every pending file, not merely the new driver migration; historical cleanup or identity-renumber migrations can rewrite live data. Do not mark old migrations applied just to skip their effects.
2. Compare the target's actual column lengths, nullability, defaults, indexes and engine/version with the rehearsed schema. A nullable `change()` that also fixes a varchar length can narrow a divergent schema; an additive design does not promise zero ALTER TABLE blocking.
3. Rehearse the pending upgrade on a representative isolated copy of the target version, verifying existing IDs, document links, role references and financial rows before/after. Distinguish a fresh install, rerun and real prior-version upgrade.
4. State irreversible `down()` behavior before deployment and verify a logical backup restore or forward-fix recovery path. A code `git revert` does not undo schema changes, and an intentionally rejected `migrate:rollback` is not a completed recovery plan.
5. Report separately: what the migration changes, what preservation was exercised, and what remains unverified on the VPS. A push never establishes that a migration ran or that the live database is safe to migrate.

## 8. Preflight a public-sandbox runtime publication

1. Resolve the requested surface before changing it: Git branch, public sandbox web, or destination VPS. Treat a publish request as permission for the named surface, not authorization to change its database engine, accounting policy or historical records.
2. Use `terminal` in the verified repository to inspect `docker ps`, then parse `docker inspect` through a field whitelist: image ID, command/entrypoint, state/health, mounts, ports and Compose labels. Do not print the full inspect object or expanded Compose configuration, which can expose environment secrets. Use `read_file` for the repository Dockerfile, Compose file and entrypoint, and compare them with the running source rather than assuming the repository describes the live deployment.
3. Establish the live engine/version and schema read-only. Inspect application boot providers before bootstrapping a read-only Laravel query, because boot hooks can themselves perform DDL/DML. Compare applied migration names with the entire workspace migration set and inspect required columns. Verify actual column types and allowed statuses even when migration history says the change ran: an already-recorded migration can coexist with an older enum that rejects the application's warehouse-loading status. Reproduce this on a restored copy, then add a narrowly scoped forward migration; do not rewrite applied history or mark a missing change as already satisfied.
4. Trace startup side effects before building, restarting or recreating a service. If app startup executes `php artisan migrate --force`, require approval for the identified pending set, a restored backup and upgrade rehearsal on the actual target engine/version before allowing startup. Do not bypass approval by restarting the old container, marking migrations applied, inventing an untested startup switch, or changing the database service to match Compose.
5. Freeze the compatible source set only after implementation owners and QC finish. Export the pinned base with `git archive <commit>` into a private build context, overlay only explicitly selected current files, and record hashes; keep secrets, runtime data, held candidates and unrelated untracked artifacts outside that context. If reusing the inspected runtime image as a dependency-preserving base, first compare `composer.json` and `composer.lock` against the selected source; matching locks are necessary, not a substitute for application tests. Build an immutable candidate, extract its source with `docker create` plus `docker cp`, and compare it to the manifest before allowing publication. A code-only subset is releasable only when its dependency closure works with the existing schema, not merely because its controller passed alone.
6. Preserve rollback from the running containers, not mutable image tags: obtain each exact image ID with `docker inspect --format '{{.Image}}' <container>` and tag that ID with `docker tag <image-id> <rollback-tag>`. Record the actual command, entrypoint, mounts, networks and healthcheck; recreating from a divergent workspace Compose file can change more than the image. Preserve any authorized source hotfixes made inside the current containers, because those files may differ from the underlying rollback image. Identify separately which public assets or documents are volume-backed; retagging an image does not restore a changed volume or undo a database migration.
7. After an authorized release, verify app/worker image identities, health, exact source hashes and public HTTP response, then perform authorized authenticated smoke checks. State separately what was published, whether schema changed, and which workflow checks remain unverified. Do not substitute login availability for financial acceptance.

### Rehearse a stateful upgrade against the target version

1. Create a restricted logical backup using the credentials resolved inside the target container, never printed in the transcript. Restore into a separate database container running the exact inspected engine image, on an internal network with no published database port or live data-volume attachment. Retain backups outside temporary directories when they are needed for recovery.
2. Start the candidate image with an explicit inert entrypoint for inspection, so normal startup cannot migrate before the before-state is recorded. Use an isolated database name/configuration and inspect any bootstrap hooks before treating a query as read-only.
3. Capture schema, row counts and a deterministic digest for each existing table. Canonicalize row representations and sort them before hashing; record the old column set so newly added default columns do not falsely appear to change historical values. Keep raw rows private. Declare expected changes to migration history or reference-role rows explicitly rather than exempting all master data.
4. Apply the exact expected pending set, compare old-column digests and counts, assert no unexpected table/value changes, then rerun migrations and require a no-op. Inspect the actual expanded schema as well as migration names. Exercise the candidate's real cache commands and startup/readiness behavior against that restored copy.
5. Run mutating regression fixtures in a separate guarded test schema on the same isolated server, not in the preserved upgrade copy. Require suite-specific final markers and exit status. Keep preservation evidence distinct from synthetic business-test results: matching historical hashes prove preservation, not correctness of the imported accounting balances.
6. Bind backup restoration, upgrade, source parity, business tests and QC to the immutable candidate identity. If a later schema correction or source edit changes that identity, repeat the affected gates and refresh the manifest rather than presenting earlier image results as final.

This rehearsal recipe does not establish that a live cutover occurred; runtime publication still requires the step-7 readback.
