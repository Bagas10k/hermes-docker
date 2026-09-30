# Conversational Companion UI

Use this recipe when maintaining a mobile, character-led AI chat surface with streaming responses, multiple agents, a Dynamic Island/status surface, and messaging-platform integration.

## Procedure

1. **Separate reading position from generation progress.**
   - When a user sends a message, position that new turn at the top of the internal reading viewport once.
   - During typewriter/streaming updates, never assign `scrollTop = scrollHeight` and never repeatedly call `scrollIntoView()`; repeated writes steal the user's reading position.
   - Keep the message pane independently scrollable with `overscroll-behavior: contain` and use top/bottom alpha masks to indicate additional content without enclosing the transcript in an opaque card.

2. **Render assistant output as semantic content, not a dense container.**
   - Keep the outer transcript surface transparent; reserve bubbles for user turns and special artifacts such as code, links, or files.
   - Support escaped Markdown for headings, bold, italic, strikethrough, lists, blockquotes, links, inline code, and fenced code blocks. Extract fenced blocks before inline transforms so code contents are not modified as Markdown.
   - Do not append suggested follow-up questions unless explicitly requested; they visually compete with the conversation and make the assistant feel scripted.

3. **Attach provenance and actions to every assistant response.**
   - Return the actual successful model identifier from the backend, including fallback selection, and render it in each response footer.
   - Give each assistant turn its own copy button; copy the raw response text rather than DOM-decorated text and expose a deterministic copied state for testing and accessibility.
   - Do not rely only on a global copy button because it becomes ambiguous once multiple responses are visible.

4. **Make response cancellation control the entire pipeline.**
   - Replace the send control with a stop control while generation is active.
   - Use one generation token plus `AbortController` for the network request and retain the active `requestAnimationFrame` ID for typewriter rendering.
   - On stop: increment/invalidate the generation token, abort the request, cancel the frame, clear progress timers, restore composer controls, and show a neutral `Dihentikan` state. Treat `AbortError` as intentional cancellation, not a connection failure.
   - Write a failing end-to-end test first that delays the response, clicks Stop, asserts cancellation state, then verifies a subsequent response still renders model metadata and copy actions.

5. **Use the status island for real work, never decorative fake progress.**
   - Publish bounded activity records from each real ingress path (web chat, Telegram private, Telegram group, worker) into one server-side activity channel with `source`, `agent`, `stage`, `summary`, `status`, and timestamp.
   - Feed that channel to the UI through SSE or the existing real-time transport; expire stale activity client-side so old work is not shown as current.
   - Distinguish group roles such as analyzer and executor only when those stages are emitted by the real handler. Never infer bot activity from animation timers alone.
   - Keep secrets, chat identifiers, and full message bodies out of the activity feed; bound summaries before persistence.

6. **Implement hold-drag agent switching with stable geometry.**
   - On long press, reveal large living agent characters beside and behind the selected character, allowing outer characters to extend beyond the frame when needed.
   - Show every agent name below its character and make the previewed agent move forward smoothly.
   - Capture each candidate's center point once when the selector opens and select the nearest fixed anchor while dragging. Do not recompute hit geometry after the preview character scales or moves; moving hit targets cause oscillation and vibration near boundaries.
   - Preserve pointer capture through drag, support `pointercancel`, and reset tilt/state to idle after commit or cancellation so gaze tracking continues.

7. **Keep mobile chrome product-native.**
   - Remove simulated phone status chrome such as clocks, battery, Wi-Fi, and signal indicators from a real mobile web page.
   - Keep the bottom dock limited to primary navigation such as New Chat, History, and Settings. Move audio, diagnostics, and low-frequency utilities into Settings.
   - When the virtual keyboard opens, move only the composer according to `visualViewport`; keep the page and transcript stable.
   - Use a centered warm-orange ambient gradient with a persisted dimming control rather than baking brightness into multiple component colors.

## Verification gates

- Build the production bundle and deploy the exact built assets before browser QA.
- Run the full existing E2E suite plus focused tests for: no auto-scroll during streaming, Stop/Abort, per-response model/copy, fixed-anchor hold-drag switching, zero simulated status bar, manual transcript scrolling, and keyboard composer isolation.
- Audit source files for forbidden emoji when the project has a zero-emoji invariant.
- After restarting production processes, allow readiness time, then verify both loopback and public URLs; an immediate post-restart connection refusal is not a final health result.
- Use screenshot/vision review to catch Dynamic Island overlap with transcript headers and to confirm transparent surfaces remain readable.
