---
name: synthetic-sse-screenshot
description: Use when capturing dashboards without live telemetry.
---

Serve the unchanged frontend assets on an ephemeral port bound to 127.0.0.1. Implement the production SSE wire shape in a separate fixture with explicit demo identifiers and a visible synthetic-data label. Do not import or run the real sampler, and keep the fixture outside the publication tree unless explicitly requested.

Route the Playwright context through an origin-and-path allowlist and block service workers, so links or dependencies cannot pull in production data. Wait for SSE-driven content and local fonts, then verify populated canvases and tables; `networkidle` is not a suitable readiness gate for a persistent event stream. Probe desktop and mobile document widths, console/page errors, HTTP failures, and a real sorting interaction before saving a full-page PNG. Inspect the exact final PNG after the last regeneration, not an earlier capture: check that the complete dashboard and footer are visible, the synthetic-data label is readable, and no real host, user, service, path, or network identifiers are visible. Review the allowed request log alongside the image; visual inspection alone cannot establish that no live endpoint was contacted.