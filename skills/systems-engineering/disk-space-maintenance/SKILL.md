---
name: disk-space-maintenance
description: Use when reclaiming Linux disk space safely.
---

# Disk-space maintenance

## Inspect, classify, decide
1. Measure pressure with `df -h <mount>` and identify large directories with `du -sh <candidates>`. List large regular files with a bounded Python `os.walk`/heap scan; disclose excluded trees such as `.git` or `node_modules` so the ranking is not mistaken for exhaustive coverage.
2. Before calling a project or virtual environment unused, check active process command lines (`ps -eo pid,args`), PM2 metadata (`pm2 jlist`, especially `pm_exec_path` and `pm_cwd`), user services, and references from deployed entrypoints. A venv outside a project's tree may supply several live services; folder age and name are not evidence of disuse.
3. Separate cache/build artifacts, source trees, published assets, and live runtime dependencies. For deletions that break services or public downloads, state the concrete impact and ask for a decision if the user has not explicitly accepted it. If a user authorizes several targets but one is live, remove independently safe targets and hold the live one; do not silently trade service availability for recovered space.
4. Delete only explicit, canonicalized targets; reject symlinks and ambiguous prefix/glob matches. For a generic cache directory, confirm its scope first: deleting browser binaries/models may force downloads or restart work even if currently idle.
5. Recheck `df -h`, existence of targets, and affected service/URL health. Report reclaimed capacity, exceptions, and broken endpoints plainly; do not claim cleanup is complete if a live dependency was intentionally retained.

## Pitfalls
- Check reverse-proxy/static-route references before removing a web build; an idle build folder can still be the only source for a live URL.
- Do not infer that a running Python process proves an environment is fully functional after partial deletion; preserve its executable and dependencies, then verify the service separately.
- Do not delete a working project's entire source tree merely because compiled artifacts are large; choose artifact-level cleanup when the user intends to keep the product.
