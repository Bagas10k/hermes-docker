# UI/UX motion, keyframes, and WebGPU

Motion is a core quality requirement, not decoration to cut for convenience. Use existing `motion-visual-systems`, `motion-principles`, `creative-motion-lab`, and UI/UX skills for their actual expertise. Optimize duplicated work and unnecessary dependencies, not requested experience quality. Complexity is justified when needed; use the simplest structure that meets the FULL outcome.

## 1. Specify the experience before the renderer

Write a motion contract: object identity, initial/intermediate/final composition, triggering input, path/occlusion, focus hierarchy, timing/easing, stable reading states, interruption/replay, and accessibility. Four beats below are an example for an approval workflow, not a mandatory state machine for every interface:

- **Queued:** a single recognizable document at source A; user can start.
- **Processing:** the SAME document moves A -> B while relevant references become apparent.
- **Review:** the draft moves B -> human gate C and STOPS. Readable status explains why.
- **Approved:** only explicit user approval changes the outcome; the result persists at C.

Keep the same object across transitions. Do not mistake replacing cards or moving arbitrary particles for an explanation of work. Announce stable state changes once, never every frame. A decorative demo must say it is synthetic; animation completion is not evidence that real AI, a payment, or an approval actually happened.

A supplied reference may use motion as a material/navigation system rather than a process diagram. For example, an inspected Shader Index reference coordinated a large capability list, selected-row emphasis, explanation, and a liquid shader accent. Adapt that relationship with original code and task-specific content; do not assume its canvas is WebGPU or copy a Pro component without a license. Hover must have keyboard/tap equivalents and inactive options must stay readable. Reference: https://useplanes.com/components/shader-index (observed 2026-10-20; linked by the user's Threads share).

Before a long build, render a short animatic or real interactive slice and inspect before/mid/after keyframes. Then inspect a short clip: still frames alone cannot establish continuity or pacing. Check static composition, actual movement, and usable interaction as three separate acceptance gates. No arbitrary beauty scores.

## 2. DOM semantics and graphics are separate

Keep headings, essential information, status and native buttons in DOM. Use valid selected/toggle semantics and visible focus. Decorative canvas: `aria-hidden="true"`, no focus, pointer-events none. A genuinely interactive canvas needs accessible equivalent controls; hiding it is not a substitute for equivalence.

Render a useful DOM/SVG baseline before hydration. Gate controls on their own controller readiness, not on unrelated scripts. Canvas stays hidden until a valid render has actually been submitted successfully; API presence and shader compilation alone are not a rendered scene. If init fails, allow the complete interaction through the fallback, rather than revealing dead buttons.

WebGPU is required when explicitly requested, but is not automatically needed for every page or faster than CSS. Deliver and exercise the actual API branch, plus fallback for unsupported devices. Never relabel CSS, Canvas 2D, or a mocked device as WebGPU.

## 3. Real WebGPU lifecycle checklist

Implement actual `requestAdapter()` -> `requestDevice()` -> WGSL shader -> pipeline/bindings -> render pass -> `queue.submit()`. Check secure context and `navigator.gpu`; requestAdapter may return null. Catch requests/pipeline failures. Read `getCompilationInfo()` where available and triage errors; collect validation/uncaptured errors as evidence.

- **Fallback tier is first-class design:** The 2D/SVG fallback must look polished, intentional, and pleasant to look at on mobile from pass 1—never leave fallback as bare wireframes or raw unstyled geometry while polishing only the WebGPU path.
- **Cache hygiene on deploy:** Always append version query strings (e.g. `?v=YYYYMMDD_HHMM`) to CSS and JS imports in HTML so client mobile browsers do not serve stale cached assets.
- Use at most one pending frame per scene. Draw on state changes and during finite transitions; stable idle/review/approved states schedule no perpetual loop.
- Time motion from timestamps, not frame counts. Interruptions invalidate pending callbacks so replay/reset cannot later complete an obsolete transition.
- Cap pixel ratio and bitmap size to a documented starting budget; tune for actual content/device instead of treating DPR2 or a layer count as a standard.
- Resize from container size without recursive CSS sizing. Preserve last semantic state across resize and renderer changes.
- Handle `device.lost`: stop rendering, hide failed canvas, release owned resources, and retain working DOM/SVG. Bound retries if any. Intentional destruction or unmount must not trigger reinitialization.
- Dispose idempotently: cancel frame, disconnect observers/listeners, unconfigure canvas, destroy owned buffers/textures/device as appropriate. Do not destroy externally shared resources.
- Guard asynchronous initialization with lifetime/generation state or cancellation. A late adapter/device result after unmount must be disposed, not attached to a dead view.

This is a lifecycle contract, not a copy-paste initializer with undefined helper functions. Adapt it to the actual project and leave one runnable check for nontrivial logic.

## 4. Accessibility and interruption

Reduced motion changes animation intensity, not user control or information. Use immediate stable transitions where appropriate; never bypass human review. Respect startup preference and changes, and avoid switching on motion the user never requested.

On hidden tab or offscreen scene, cancel/suspend pending work. Resume without jumping into an unrequested final state. Keep pause/replay/reset usable where relevant and preserve state when selecting 2D fallback. Do not blank essential headings for entrance effects.

WCAG SC2.3.3 is Level AAA and concerns suppressing nonessential interaction-triggered animation. Other criteria, including qualifying automatic animation under SC2.2.2, still need separate evaluation.

## 5. Evidence before claims

Exercise real native keyboard/pointer start -> review (hold) -> explicit approval, reset mid-transition, reduced motion, hidden/offscreen, resize and dispose. Test unsupported API/null adapter/initialization error/device loss without hiding failures. Repeat homepage regression for unrelated controls.

Shader success requires more than `navigator.gpu` truthiness: verify compilation, pipeline, submission and nontrivial pixel output. A GPU texture readback proves that shader output, not that browser composition displayed it correctly. Inspect actual scene screenshots/clip as a separate test. Never ship a blank canvas with a 'WebGPU active' claim.

Record adapter/backend. SwiftShader/software Vulkan is real API execution but NOT physical hardware acceleration. Browser headless mode alone does not determine backend. Report hardware FPS, mobile thermals, battery, field INP and speedup as NOT RUN unless measured appropriately. Zero-jank/zero-allocation claims need evidence, not optimistic code comments.

## Sources checked 2026-10-20

- [MDN WebGPU API](https://developer.mozilla.org/en-US/docs/Web/API/WebGPU_API): secure context, adapter/device and programmable graphics/compute.
- [MDN getCompilationInfo](https://developer.mozilla.org/en-US/docs/Web/API/GPUShaderModule/getCompilationInfo): actual shader diagnostics.
- [MDN GPUDevice.lost](https://developer.mozilla.org/en-US/docs/Web/API/GPUDevice/lost): loss and invalid resource lifecycle.
- [MDN Page Visibility](https://developer.mozilla.org/en-US/docs/Web/API/Page_Visibility_API): visibility state; test actual scheduling.
- [MDN requestAnimationFrame](https://developer.mozilla.org/en-US/docs/Web/API/Window/requestAnimationFrame): one-shot callbacks/timestamps, not guaranteed FPS.
- [W3C SC2.3.3](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html): interaction motion can be disabled unless essential.
