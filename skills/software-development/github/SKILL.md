---
name: github
description: "GitHub via gh CLI: PRs, issues, reviews, repos, auth."
version: 2.0.0
author: Ben Barclay (benbarclay), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [github, gh, git, pull-requests, issues, code-review, repos, auth, ci]
    category: software-development
    related_skills: [codebase-inspection, requesting-code-review]
---

# GitHub

Work GitHub end to end with the `gh` CLI (REST fallback where noted): auth,
issues, the PR lifecycle, issue-to-PR delivery, code review, and repo
management. This skill consolidates six former skills; each workflow lives
complete in its reference file — ALWAYS read the matching reference before
starting that workflow, the body below only routes.

## Routing

| Task | Read first |
|---|---|
| Auth broken / new machine / token or SSH setup / gh login | `references/auth.md` |
| Create, triage, label, assign, close issues | `references/issues.md` |
| Branch, commit, open PR, watch CI, merge | `references/pr-workflow.md` |
| Carry an ISSUE to a verified PR (full delivery loop) | `references/issue-to-pr.md` |
| Review someone's PR: diffs, inline comments, verdict | `references/code-review.md` |
| Clone/create/fork repos, remotes, releases | `references/repo-management.md` |

Supporting assets: `scripts/gh-env.sh` + `scripts/git-credential-token.py`
(auth helpers), `templates/` (PR bodies, bug report, feature request),
`references/ci-troubleshooting.md`, `references/conventional-commits.md`,
`references/github-api-cheatsheet.md`, `references/review-output-template.md`.

## Core discipline (applies to every workflow)

- Preflight once per session: `gh auth status` — if it fails, go to
  `references/auth.md` before anything else.
- For an explicit repository visibility change, verify the exact owner/repo and
  current visibility, apply it immediately with `gh repo edit <owner/repo>
  --visibility public|private`, then read back `gh repo view <owner/repo>
  --json nameWithOwner,isPrivate,url`. Do not turn a simple authorized toggle
  into a broad history audit or rewrite Git history; that is a separate,
  high-impact operation. If a concrete credential leak is already known, state
  the specific risk briefly and ask before proceeding; report other privacy
  concerns separately without blocking the requested change.
- Large files & initial push safeguard: scan files >= 50MB and > 95MB before initial
  push (`find . -type f -size +95M`). Files >= 100MB are hard rejected by GitHub unless
  tracked with Git LFS (`git lfs track "<pattern>"`). On an unborn branch / root commit,
  if large files were committed before LFS tracking, reset via `git update-ref -d HEAD`
  (never `git reset --soft HEAD~1` as no parent exists), add `.gitattributes`, and re-commit.
- Prefer `gh` over raw REST; drop to `gh api` only for endpoints the
  porcelain lacks (the cheatsheet lists them).
- Never report CI green without checking `gh pr checks` yourself; never
  claim merged without verifying `state,mergedAt`.
- Read full context before writing: `gh issue view --comments` /
  `gh pr view --comments` — decisions live in threads, not titles.
- Sweep for duplicates before creating anything:
  `gh pr list --search` / `gh issue list --search`.

## Verification

- The workflow's own reference file defines done for that task.
- Cross-cutting: every claim about remote state (CI, merge, release,
  issue state) is backed by a fresh `gh` read, never memory.
- When publishing a source snapshot of a running app, keep production untouched: review and commit an explicit allowlist in separate staging. Verify the exact owner/repo and intended visibility before the first source push; create the empty private repo separately from the push when privacy is required, because a combined create-and-push leaves no verification gate. `gh repo view <owner/repo> --json nameWithOwner,isPrivate,url` checks remote privacy; `package.json` does not.
- For a reusable snapshot of a production frontend, prefer the smallest standalone package that serves the approved scope. Preserve the URL base path (or update all links and assets consistently), include local startup steps and a short code map, and document omitted integrations. Disable production-bound forms, chat, or other API actions visibly unless a separately configured backend is in scope. Before pushing, start the staged package, exercise the affected routes and actions in a browser, and inspect network requests for accidental calls to production; a successful page load alone does not catch those calls. For public repos, verify the expected commit is readable without authentication.
- For a requested README preview, commit an image of the actual UI rendered against wholly synthetic data, never a live operational capture, even in a private repo. Follow `references/repo-management.md` and deliver the verified repository link, visibility, and README preview result. Read back the pushed SHA and compare remote README and image bytes at that SHA (`gh api -H 'Accept: application/vnd.github.raw+json' ... | cmp - <local-file>`). If browser access is unavailable, fetch `repos/<owner>/<repo>/readme?ref=<sha>` with `Accept: application/vnd.github.html+json` and check the expected image tag; report this as rendered HTML verification, not a visual browser check.
- If a read-back command fails after a write, query the exact remote target before retrying the write; failure to verify does not mean the write failed. In the final report, distinguish publication evidence from local test scope: a syntax-only test is not a startup or integration test, and production health is not proof of publication.
