---
name: motion-agent-training-kit
description: "Use when building motion workflow training videos."
---
# Production and teaching
Workflow attribution: Bagas Cihuy. Hermes Agent product: Nous Research.

Project: `/home/ubuntu/theory-motion`. Read `training-kit/README.md`, `training-kit/lesson.json`, `src/compositions/AgentWorkflowLesson.tsx`, `output/agent-workflow-lesson-storyboard.json`, and `output/motion-training-audit.md`. Reference provenance: `output/motion-training-reference/provenance.json`.

1. Storyboard before final rendering: question → source → action → consequence. Timeline records intentional reading holds. User reference and rated-7 direction are not final approval of subsequent drafts.
2. Preserve object identity; use geometry transforms, not fades alone. Major transitions 60–90 frames at 60fps. Meaningful stagger during holds, no decoration to disguise inactivity. Current example: button becomes node at 600–675; overview details at 1620–1740. Initial storyboard may predate these improvements; reconcile source and manifest.
3. Run `node training-kit/build.mjs --check --manifest training-kit/lesson.json`; then `node training-kit/build.mjs --manifest training-kit/lesson.json --out output/training-kit/NEW-ID`. Never overwrite evidence runs. Long render: background terminal with completion notification. Timeout with no MP4 is failure, not success; correct stale rendering status.
4. Inspect actual render before delivery: full-resolution key frames plus adjacent transition samples, cursor targeting, source/result agreement, geometry and reading holds. Contact sheet alone cannot prove temporal smoothness. Tests/ffprobe never prove aesthetic quality.
5. Fix observed defects and render again. Teach from before/after evidence: abrupt conditional green-to-white change needs color interpolation. Preserve negative candidate separately.
6. Deliver video plus source, manifests, runnable tool, evidence and honest review. Bundle excludes node_modules and third-party reference footage. Over-15MB Telegram files must be split.

Example is 1920x1080 60fps 30s, silent vector illustration, not live execution. It demonstrates a button-to-node morph and persistent layout, not every possible morph or VO synchronization. Label limitations; do not claim gold standard, reference parity or user acceptance. This trains agent procedure through skills/examples, not model weights.
