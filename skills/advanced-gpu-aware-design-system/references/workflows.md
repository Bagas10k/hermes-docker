# Input workflows

## Brief -> design system + production UI
1. Extract business objective, audience, density, branding, motion, browser targets.
2. Create 2-3 visual directions as concise descriptions; choose one aligned with requirements.
3. Specify tokens, page grid, components, interaction states and acceptance checks.
4. Build exemplar screen and library; validate before expanding.
5. Deliver files, demo route, tests and limitations.

## Screenshot -> implementation
1. Inventory visible regions, alignment, proportions, typography, surfaces, icons, and state.
2. Separate observed facts from estimates; ask for missing assets only if blocking.
3. Implement responsive intent rather than pixel-for-pixel hardcoding.
4. Capture target viewport screenshots and compare; document unavoidable deviations.
5. Verify keyboard, zoom, small screen, long content, and reduced motion.

## Existing repo -> safe modernization
1. Capture git status, dependency versions, routes, baseline screenshots and current test results.
2. Map component duplication and token drift; prioritize one route as pilot.
3. Introduce tokens/compatibility layers; migrate components incrementally.
4. Preserve data bindings and behaviors; run regression tests.
5. Summarize file changes, tests, rollback, and remaining debt.

## Parallel agent work
Coordinator owns contract and integration. Design agent owns token specification (not application code). UI agents each own non-overlapping component folders. GPU agent owns isolated effects modules. QA agent independently verifies integrated output. Merge in dependency order; no concurrent edits to the same file.
