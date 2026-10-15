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
1. Trace the actual production page, API routes, and runtime event producer before redesigning. Identify which fields are live, static defaults, inferred, or delayed; preserve a working access path to old controls during an in-place replacement. Inventory the measurement sources that already exist before writing any new instrumentation: behavioral metrics usually live somewhere already (a capability/evidence table in a monitoring service, tool-call traces in the session store, a mutation ledger on disk). Query each with bounded reads and reuse it — a second collector for data that is already recorded creates two sources of truth that will disagree.
2. Inspect real payloads with bounded queries. Correlate event, tool, verification, and task records by trace/session ID. Treat `ACTIVE` database state or a recent message as insufficient evidence of a running agent when no recent runtime event exists.
3. Design the first viewport around four questions: what task is observed, what action just occurred and when, what evidence proves the result, and what remains unknown. Show source and freshness on each relevant status. On fetch failure or stale event, downgrade to `unknown`, not `online`.
4. Render untrusted summaries using `textContent`, not interpolated `innerHTML`; cap line length and sample sizes. Do not expose raw tool arguments, payload JSON, secrets, or private messages on a public dashboard. A page showing behavioral metrics (correction rate, typo rate, working habits) is private data even when it looks like a neutral dashboard: bind the service to `127.0.0.1`, not `0.0.0.0`, and proxy it through the existing authenticated path. "Put it on my domain" is not authorization to publish it — verify with an unauthenticated request that returns 401/303, not 200.
5. Label measurements precisely: tool success is not code correctness; tool p95 is not code efficiency; RAM usage is not token spend; recorded verification for another trace is not proof for the current task. If alignment with the user's request is not assessed against explicit criteria, say `belum dapat dinilai`. A capability with no supporting evidence is rendered `INSUFFICIENT DATA`, never a score: one fabricated number discredits every other number on the page. A high count of unmeasured capabilities is itself a useful finding about how deeply the system has been exercised.
6. Verify the public URL in a browser at desktop and mobile widths after the asynchronous data load completes; inspect populated fields, connection state, and horizontal overflow. A 200 response or syntax check alone does not prove the dashboard works. Exercise stale/disconnected rendering and preserve a path to underlying evidence.
7. Render charts server-side as inline SVG. It needs no chart library, survives a dead CDN, and works with JavaScript disabled — for an internal dashboard this outlasts pulling in a rendering library. Assert in the chart tests that every generated coordinate falls inside the `viewBox`, and cover the cases that break a naive renderer: a flat series (division by zero), an out-of-range value (clamp to the axis bound), and fewer points than the chart needs (emit a message, not a malformed path). When such a test fails, check the assertion before the renderer — a bar at maximum value legitimately equals the canvas width, and editing the code to satisfy a wrong assertion introduces a real bug.

Prefer existing runtime endpoints and a bounded refresh mechanism over a new polling service. Measure before claiming lower token use, latency, or improved developer visibility. Summarize what is verified and what the instrumentation still cannot see in a few weighted points, not a feature tour.
