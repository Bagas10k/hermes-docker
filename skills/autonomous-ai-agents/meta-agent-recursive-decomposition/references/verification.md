# Local verification evidence

Scope: synthetic offline plan validation only. No real agents, model invocations, plan-provided code execution, services, vault/state edits, or other-profile changes. Web retrieval was used only for research sources.

Actual command via `terminal`:

`python3 -m unittest discover -s /home/ubuntu/.hermes/skills/autonomous-ai-agents/meta-agent-recursive-decomposition/scripts -p 'test_*.py' -v`

Observed: `Ran 30 tests in 0.032s`, `OK`, exit 0. Cases include positive single-leaf and exact-boundary admission, parallel weighted critical path, duplicate IDs, unknown references, multiple parents, unreachable nodes, connected/disconnected tree cycles, depth/node/branching/edge/budget/path limits, dependency cycles/self-loops/nonleaf references/coverage/duplicates, missing contracts, nonfinite thresholds, boolean costs, negative durations, executable extra fields, literal-ID preservation, input nonmutation, duplicate JSON keys, byte cap, parser recursion, and malformed JSON.

An initial availability test was run before implementation and failed because the validator file did not exist. The broader suite was added after the initial implementation; do not claim a complete per-invariant red/green TDD history.

Valid-template CLI observed exit 0:

```json
{"admitted":true,"budget_unit":"tokens","critical_path":8,"critical_path_ids":["b","c"],"depth":1,"duration_unit":"seconds","edges":2,"evidence_scope":"offline structural validation; estimates, not execution","leaves":3,"nodes":4,"topological_order":["a","b","c"],"total_budget":10}
```

A temporary copy with a→c prerequisite (forming a dependency cycle with c requiring a) was tested through the CLI. Observed exit 2 and `{"admitted":false,"error":"dependency cycle"}`. Temporary data was cleaned up.

Frontmatter and required sections were checked programmatically: description length 51, ends with period; exact author `Bagas Cihuy & Hermes Agent`; all six required sections present.

Limitations: these tests do not establish semantic goal coverage, metric quality, actual budget enforcement, runtime latency, model success probability, or faithful aggregation. No production performance benchmark or Bayesian posterior was measured. No OS sandbox claim is made. The unavailable Exa CLI (`mcporter: command not found`) was bypassed using built-in web search and primary-source extraction; nothing was installed.
