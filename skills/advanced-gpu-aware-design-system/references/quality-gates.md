# Quality gates and evidence

## Release criteria
- Function: no broken routes, API contracts, form submission, validation, or backend behavior.
- Responsive: check at 320, 375, 768, 1024, 1440 CSS pixels plus zoom/long-text cases where applicable.
- Accessibility: keyboard navigation, visible focus, labels, dialog semantics, meaningful alt text, no keyboard traps, WCAG 2.2 AA target (normal text 4.5:1, large text 3:1; UI non-text 3:1 where applicable). Automated audits do not replace manual testing.
- Motion: respect `prefers-reduced-motion`, pause decorative perpetual animation, avoid flashing effects.
- Performance: measure LCP <= 2.5s, INP <= 200ms, CLS <= 0.1 at p75 where real-user data is available; otherwise report lab metrics separately. Track JS payload, frame budget (~16.7ms at 60Hz), long tasks, and memory where measurable.
- Maintenance: consistent tokens, documented components, no unnecessary dependencies, clean teardown of visual resources.
- Security: no unsafe HTML insertion, CSP considerations, no embedded secrets, server-side authorization intact.

## Verification matrix
Run project-supported lint/typecheck/unit tests. Browser automation: critical route screenshots and interactions on mobile and desktop; use axe-core/Playwright accessibility checks when installed. Run `python scripts/token_audit.py path/to/tokens.json` and `python scripts/css_motion_audit.py path/to/styles` (warning-only static heuristics). Report tool availability, command, outcome, environment, and evidence location. Do not turn static warnings into proof of GPU behavior.

## Evidence format
| Gate | Command/method | Result PASS/FAIL/NOT RUN | Evidence | Risk |
| --- | --- | --- | --- | --- |
| Build | actual command | actual result | log path | impact |

Mark NOT RUN if no browser, no dependencies, or no real device. Do not fabricate screenshots or benchmark results. If gates fail, repair and rerun or block release with explicit residual risk.

## Spatial scene gates
For 3D designs, verify every clickable scene hotspot via keyboard and pointer, an equivalent 2D action, fallback when WebGL/WebGPU fails, scene pause on hidden/reduced-motion state, proper cleanup on route change, and measured load/interaction budgets on target devices. Distinguish artistic preview from implemented UI. Score against `spatial-3d-direction.md` rubric only with evidence.
