---
name: agent-knowledge-portability
description: Use when moving agent knowledge between devices.
---
# Agent knowledge portability

## Decide the target before copying
- Distinguish one agent accessed from many devices, an independent knowledge clone, and a full runtime move. A remote Desktop connection is not a clone; a profile distribution is not a conversation backup.
- For a knowledge clone, inventory skills, memory documents, persona, configuration, and external knowledge vaults separately. Do not assume a profile export or existing GitHub repo contains vault notes, session databases, or credentials.

## Discover existing backups first
1. Inspect the live backup schedule (`hermes cron list`), the script it actually runs, and its called scripts. Trace source paths, exclusions, staging paths, and actual `git push` target. A green cron run proves the script exited successfully, not that every intended source was included; scripts may silently skip missing files.
2. Check local and remote independently: `git -C <repo> remote -v`, `git -C <repo> status -sb`, `git -C <repo> ls-tree -r --name-only HEAD`, `gh repo view <owner/repo> --json isPrivate,pushedAt,defaultBranchRef`, and `gh api repos/<owner>/<repo>/commits/<branch> --jq .sha`. Compare remote SHA with local HEAD; count included source categories programmatically. Do not say “already backed up” from a job name or success marker alone.
3. If an external vault is not itself a Git repo, count its files and compare representative anchor paths against the backup tree. A partial copy of one subdirectory is not a vault backup.

## Privacy and upload gate
- Inspect repo visibility before any stage, commit, or push. Private is the default for personal knowledge; never widen an existing public repository just because it already contains some agent files.
- Stage only an explicit allowlist in a clean directory, excluding `.env`, `auth.json`, tokens, session DBs/history, logs, raw business/customer data, and runtime caches. Scan both filenames and contents before commit; `.gitignore` does not protect previously tracked files. Human review is required for ambiguous personal notes. A private repository still needs filtering.
- Compare the staged manifest with required knowledge anchors (especially indexes and retrieval instructions) before calling it portable. A keyword filter can exclude exactly the documents that make the copied notes navigable; either review/redact those privately or label the snapshot incomplete. Run the privacy scan again on the staged tree, not only the source tree, because file paths and filtering behavior can differ.
- When the user requests an immediate backup, bound the audit and continue through commit, push, and remote readback in the same workstream once the gate passes. A newly created private repository or prepared staging tree is progress, not completion; if the gate fails, report the blocker and preserved staging state plainly.
- If personal content is already tracked publicly, flag it without repeating values. Changing visibility does not revoke copies or purge commit history; handle remediation separately rather than pretending a new private backup fixes past exposure.

## Verify and explain the result
- After a push, read back the exact remote branch/commit and representative paths, then compare counts and hashes with the approved manifest. A created empty repo is not a completed backup.
- Give a short inventory: included knowledge, excluded runtime/secrets, last verified remote commit, and restoration procedure. State that independent clones do not auto-sync memories or conversations, and configure credentials separately on each device.
- For a full runtime move, plan a separate private state transfer and stop the old messaging gateway before activating the same bot token elsewhere; a GitHub knowledge repo alone does not relocate the running agent.

## Restore path
- For a curated Hermes profile distribution, use `hermes profile install <private-repo>` then `hermes profile update <name>` on subsequent revisions. For a one-off handoff use `hermes profile export <name> -o <archive>` / `hermes profile import <archive> --name <new-name>`, but inspect the archive: exports omit `.env` and `auth.json` while they may include personal memory and sessions. Verify external vault files separately.
- Treat a custom knowledge-only GitHub repo as source material, not automatically an installable profile distribution; restoration must place approved files into appropriate profile/vault paths and verify Hermes loads them.
