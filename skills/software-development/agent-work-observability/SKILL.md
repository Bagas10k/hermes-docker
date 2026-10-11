---
name: agent-work-observability
description: Use when building dashboards for live agent work.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Live Agent Work Observability

Build operator dashboards that distinguish **observed execution**, **task alignment**, **verified correctness**, and **measured efficiency**. Never collapse these into an invented health score.

## Procedure
1. Trace the actual production page, API routes, and runtime event producer before redesigning. Identify which fields are live, static defaults, inferred, or delayed; preserve a working access path to old controls during an in-place replacement.
2. Inspect real payloads with bounded queries. Correlate event, tool, verification, and task records by trace/session ID. Treat `ACTIVE` database state or a recent message as insufficient evidence of a running agent when no recent runtime event exists.
3. Design the first viewport around four questions: what task is observed, what action just occurred and when, what evidence proves the result, and what remains unknown. Show source and freshness on each relevant status. On fetch failure or stale event, downgrade to `unknown`, not `online`.
4. Render untrusted summaries using `textContent`, not interpolated `innerHTML`; cap line length and sample sizes. Do not expose raw tool arguments, payload JSON, secrets, or private messages on a public dashboard.
5. Label measurements precisely: tool success is not code correctness; tool p95 is not code efficiency; RAM usage is not token spend; recorded verification for another trace is not proof for the current task. If alignment with the user's request is not assessed against explicit criteria, say `belum dapat dinilai`.
6. Verify the public URL in a browser at desktop and mobile widths after the asynchronous data load completes; inspect populated fields, connection state, and horizontal overflow. A 200 response or syntax check alone does not prove the dashboard works. Exercise stale/disconnected rendering and preserve a path to underlying evidence.

Prefer existing runtime endpoints and a bounded refresh mechanism over a new polling service. Measure before claiming lower token use, latency, or improved developer visibility. Summarize what is verified and what the instrumentation still cannot see in a few weighted points, not a feature tour.
