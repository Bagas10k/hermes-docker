---
name: dialogue-regression-replay
description: Use when checking repeated user-intent failures.
---
# Dialogue regression replay
Convert one real correction into a synthetic action invariant; do not copy private conversation or secrets. JSON cases contain `id`, `actions`, `required_actions`, `forbidden_actions`, and `claims`. Wrong-route actions and unverified claims must fail first. Run `terminal(command="python3 /home/ubuntu/agent-quality/replay_eval.py <cases.json>")` against the corrected trajectory. This is an offline replay smoke test, not automatic interception: independently check real UI/browser behavior.
