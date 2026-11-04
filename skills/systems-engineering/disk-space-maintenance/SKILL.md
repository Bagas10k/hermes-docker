---
name: disk-space-maintenance
description: Use when reclaiming Linux disk space safely.
---

# Disk-space maintenance

## Inspect, classify, decide
1. Measure pressure with `df -h <mount>` and identify large directories with `du -sh <candidates>`. List large regular files with a bounded Python `os.walk`/heap scan; disclose excluded trees such as `.git` or `node_modules` so the ranking is not mistaken for exhaustive coverage.
2. Before calling a project or virtual environment unused, check active process command lines (`ps -eo pid,args`), PM2 metadata (`pm2 jlist`, especially `pm_exec_path` and `pm_cwd`), user services, and references from deployed entrypoints. A venv outside a project's tree may supply several live services; folder age and name are not evidence of disuse.
3. Separate cache/build artifacts, source trees, published assets, and live runtime dependencies. For deletions that break services or public downloads, state the concrete impact and ask for a decision if the user has not explicitly accepted it. If a user authorizes several targets but one is live, remove independently safe targets and hold the live one; do not silently trade service availability for recovered space.
4. When pruning containerized environments:
   - Run `docker system df` to break down reclaimable capacity across images, containers, local volumes, and build cache.
   - Stopped containers (`docker container prune -f`) and build cache (`docker builder prune -f`) reclaim build clutter, but anonymous volumes (`docker volume prune -f`) often hold gigabytes of orphaned database state left behind by test/candidate containers.
5. Delete only explicit, canonicalized targets; reject symlinks and ambiguous prefix/glob matches. For a generic cache directory, confirm its scope first: deleting browser binaries/models may force downloads or restart work even if currently idle.
6. Handle container mount permissions: Directories populated by root/www-data inside containers (e.g. framework storage trees, testing caches) will fail user-level deletion (`shutil.rmtree` / `rm -rf`) with Permission Denied. Isolate and elevate (`sudo rm -rf`) only those explicitly confirmed abandoned targets.
7. Recheck `df -h`, existence of targets, and affected service/URL health:
   - Verify HTTP status codes on local endpoints (e.g. `curl -i http://127.0.0.1:<port>/`).
   - If a local check returns 302 redirecting to an absolute public domain, testing with `curl -L` may fail with 502/DNS loopback errors if tunnels or public DNS resolve externally; test the target relative route (e.g. `/login`) directly on the local port.
   - Report reclaimed capacity, exceptions, and surviving endpoints plainly.

## Pitfalls
- Check reverse-proxy/static-route references before removing a web build; an idle build folder can still be the only source for a live URL.
- Do not infer that a running Python process proves an environment is fully functional after partial deletion; preserve its executable and dependencies, then verify the service separately.
- Do not delete a working project's entire source tree merely because compiled artifacts are large; choose artifact-level cleanup when the user intends to keep the product.
- Do not rely solely on `docker image prune`; anonymous Docker volumes (`docker volume prune`) frequently hold the bulk of disk bloat from ephemeral database testing containers.
- Do not misinterpret a `curl -L` failure as a service crash when an application returns a 302 redirect to a public domain that cannot loop back to localhost; inspect headers directly with `curl -i`.
