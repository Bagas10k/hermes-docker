---
name: task-surface-contract
description: Use when matching user intent to a delivery surface.
---
# Task-surface contract
Record target, requested surface/route, source kind and completion criteria before a UI change. Inspect existing flow. Do not replace main route with test route or URL input with local upload. Map the public hostname to its actual gateway and upstream before selecting a deployment folder; a local static route on another service does not establish the public route. For a public, self-contained artifact behind a default-private gateway, allow only the exact reviewed GET/HEAD paths and serve the existing source file; preserve sibling/private routes and verify negative access checks. Test the exact route in a browser; attach non-sensitive evidence. Run `/home/ubuntu/agent-quality/quality_gate.py <record.json>` before reporting completion.
