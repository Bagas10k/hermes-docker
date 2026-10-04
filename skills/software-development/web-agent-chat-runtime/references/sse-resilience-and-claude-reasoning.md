# SSE Streaming Resiliency & Claude-Style Reasoning Architecture

Guidelines for engineering resilient Server-Sent Events (SSE) AI chat runtimes and structured reasoning loops.

## 1. High TTFT & Mobile Socket Resiliency (Anti-Failed to fetch)

When an agent performs deep reasoning (e.g. "Think" mode or large prompt compilation), Time-to-First-Token (TTFT) can reach 3–10 seconds. On mobile devices with battery saver active or fluctuating cellular connections (4G/3G drops), zero-byte idle sockets trigger browser network errors (`Failed to fetch`).

### Backend Handshake & Heartbeat Protocol

1. **Immediate SSE Handshake (<50ms)**:
   Flush HTTP 200 headers and initial comment/event immediately upon accepting the connection before awaiting model completion:
   ```javascript
   res.setHeader('Content-Type', 'text/event-stream; charset=utf-8');
   res.setHeader('Cache-Control', 'no-cache, no-transform');
   res.setHeader('Connection', 'keep-alive');
   res.setHeader('X-Accel-Buffering', 'no');
   res.flushHeaders?.();

   // Instant byte flush locks the socket in 'connected' state
   res.write(': keep-alive\n\n');
   res.write(`data: ${JSON.stringify({ status: 'connected', sender: agentName })}\n\n`);
   ```

2. **Heartbeat Keep-Alive Interval (3–4s)**:
   Send an SSE comment (`: heartbeat\n\n`) periodically while the reasoning engine is generating tokens:
   ```javascript
   const heartbeat = setInterval(() => {
     if (!res.writableEnded) res.write(': heartbeat\n\n');
   }, 3500);
   if (heartbeat.unref) heartbeat.unref();

   res.on('close', () => clearInterval(heartbeat));
   ```
   *Pitfall*: Clear heartbeat timers in both `onDone`, `onError`, and `res.on('close')`; un-cleared intervals cause timer leaks and crash PM2 worker processes under load.

3. **Frontend Transparent Auto-Retry**:
   Wrap client-side `fetch()` with a 1-retry loop with a short backoff (500–800ms) for transient network hiccups:
   ```javascript
   let res = null;
   for (let attempt = 0; attempt < 2; attempt++) {
     try {
       res = await fetch('/api/.../chat/stream', { ...opts, signal: abortController.signal });
       if (res.ok) break;
       if ([400, 401, 402, 429].includes(res.status)) throw new Error(`HTTP ${res.status}`);
     } catch (err) {
       if (abortController.signal.aborted || attempt === 1) throw err;
       await new Promise(r => setTimeout(r, 600));
     }
   }
   ```

---

## 2. Claude-Style Reasoning Architecture & Prompt Partitioning

Structure prompt contexts using unambiguous XML-like block delimiters to preserve instruction hierarchy and eliminate context bleeding:

```
<system_instructions>
Core operational rules, zero-fluff requirements, and formatting bounds.
</system_instructions>

<reasoning_mindset>
- Causal analysis: isolate mechanisms before concluding.
- Grounded attribution: treat attached documents as single source of truth.
- Zero emojis: enforce professional SVG/symbolic interfaces.
</reasoning_mindset>

<attached_documents>
[Extracted plain text or structured extracts of user-uploaded files]
</attached_documents>

<user_memories>
Persistent profile and cross-session constraints.
</user_memories>

<current_query>
User input prompt.
</current_query>
```

### Deterministic `stop_reason` State Machine

Normalize model gateway completion statuses into standard lifecycle signals:
- `end_turn`: Natural response completion; persist conversation turn and deduct quota.
- `tool_use`: Model requests external tool invocation; dispatch to permission gateway and stream progress.
- `max_tokens`: Context or token budget ceiling hit; signal truncation or trigger continuation.

---

## 3. Gateway Model Alias Mapping (Zero 404 Round-Trips)

When frontends or agent selectors send abstract persona identifiers (e.g. `agent: 'mumu'`, `agent: 'sputarai'`), never pass the raw unmapped identifier directly to upstream model gateways (e.g. 9Router or OpenAI-compatible backends).
- **Pitfall**: An unmapped model string immediately triggers an upstream HTTP 404, incurring a 2–3 second delay while waiting for fallback retry loops on every turn.
- **Rule**: Maintain an explicit, synchronous `MODEL_ALIASES` resolution table at the entry of `streamCompletion()` before issuing requests:
  ```javascript
  const MODEL_ALIASES = {
    'mumu': 'bk',
    'mumu-ai': 'bk',
    'sputarai': 'bk',
    'claude': 'ag/claude-sonnet-4-6',
    'claude-thinking': 'ag/claude-opus-4-6-thinking',
    'gpt': 'cx/gpt-5.6-terra',
    'gemini': 'ag/gemini-3.8-flash-low'
  };
  const resolvedModel = MODEL_ALIASES[preferredModel] || preferredModel;
  ```

---

## 4. Reasoning Token Isolation (Anti-Thinking Bleed)

When modern reasoning models emit internal thoughts (`delta.reasoning_content` or `<think>...</think>`), never append reasoning tokens directly into the user message accumulator (`streamedText`).
- **Pitfall**: Raw internal reasoning generated in a foreign language (e.g. English analysis of an Indonesian prompt) will pollute the primary chat bubble before the actual answer starts.
- **Rule**:
  1. Backend must flag reasoning chunks explicitly: `{ chunk: delta, isThinking: true }`.
  2. Frontend must route `isThinking: true` to a status label (*"Mumu sedang menalar..."*) or a collapsible accordion; only `isThinking: false` chunks may be concatenated to the assistant's visible response.
  3. System prompts must enforce language consistency: *"Seluruh penalaran dan respons akhir WAJIB disajikan dalam Bahasa Indonesia."*

---

## 5. Single-Process Graceful Reload & Socket Protection

On single-process Node.js backends managed by PM2 (`fork_mode`), executing `pm2 restart` violently kills the active process and immediately severs all active TCP sockets, triggering client-side `Failed to fetch`.
- **Rule**: Implement graceful shutdown hooks in `server.js` listening for `SIGINT` and `SIGTERM` to close HTTP listeners cleanly, and execute `pm2 reload` instead of `pm2 restart` to avoid connection resets.
- **Always provide a non-streaming fallback endpoint**: Register `POST /api/.../chat` alongside `/stream`. If the client-side streaming reader aborts or fails to mount a row, the client's fallback request must not return HTTP 404.

---

## 6. Actionable Error Recovery & Document Export UX

1. **Interactive Retry Card (No Dead Red Errors)**:
   Never render cold, dead errors like `Terjadi kendala jaringan: Failed to fetch`. Render an actionable recovery card with an inline `[Kirim Ulang]` button that preserves the user's prompt and allows immediate 1-tap re-transmission.
2. **Instant Document Export Action**:
   When users request documents (poems, reports, essays, structured code), provide a 1-click **[Unduh Dokumen]** button on the assistant action bar. Generate a clean client-side Blob (`application/msword;charset=utf-8` formatted HTML as `.doc`) allowing users to download their deliverable without leaving the page.

---

## 7. Context History Turn Invariants (Anti-Prompt Duplication)

When persisting user messages to SQLite/Postgres *before* feeding context to the model:
- **Pitfall**: Querying `getConversationMessages(convId, limit)` right after `saveMessage()` returns an array that already terminates with the current prompt. If the context builder subsequently appends `{ role: 'user', content: currentUserPrompt }`, the LLM receives two consecutive, identical user messages (`user => X`, `user => X`). This violates strict alternating-turn API schemas (e.g. Anthropic Claude), wastes token quota, and degrades instruction adherence.
- **Rule**:
  1. Slice off the current prompt when feeding history into `buildContext`: `recentMessages: recentMessages.slice(0, -1)`.
  2. In `buildContext()`, enforce a deduplication guard: if `recentMessages[recentMessages.length - 1]?.content === currentUserPrompt`, pop it before composing `modelMessages`.

---

## 8. Aborted Stream Accounting & State Preservation

When a user clicks "Stop" or a mobile device drops connection mid-stream:
- **Pitfall**: Relying exclusively on `onDone` to save the assistant's message and deduct quota leaves the database with an orphaned user prompt without a reply. Furthermore, users can stream large responses and abort right before completion, bypassing token usage accounting.
- **Rule**:
  1. Maintain an `accumulatedContent` variable across `onChunk` events.
  2. In `res.on('close')`, check `if (!res.writableEnded && accumulatedContent.trim().length > 0)`.
  3. Persist the partial response tagged with `[Dihentikan oleh pengguna]` and atomically deduct tokens proportional to `accumulatedContent.length`.

---

## 9. Mobile Input & IME Composition Safety

Virtual keyboards on Android/iOS behave differently from physical desktop keyboards:
- **Pitfall**: Listening for `keydown Enter` without checking `e.isComposing` triggers premature message transmission during IME predictive word selection, voice input transcription, or Japanese/Chinese character conversion. Furthermore, virtual keyboard "Return" keys have `shiftKey: false`, causing accidental sends when users simply want a line break.
- **Rule**:
  ```javascript
  chatInput.addEventListener('keydown', (e) => {
    if (e.isComposing || e.keyCode === 229) return;
    const isMobile = window.matchMedia('(max-width: 768px)').matches || ('ontouchstart' in window);
    if (e.key === 'Enter' && !e.shiftKey) {
      if (isMobile) {
        // Allow default newline insertion on mobile touchscreens
        return;
      }
      e.preventDefault();
      handleSendOrStop();
    }
  });
  ```

---

## 10. Cross-Session Stream Isolation (Race Condition Prevention)

When users navigate between conversation sessions in a sidebar or click "New Chat" while a response is streaming:
- **Pitfall**: Leaving the SSE reader running causes arriving tokens from the previous session to be injected into the newly mounted chat DOM, corrupting conversation history.
- **Rule**: In `loadSessionHistory(newId)` and `startNewConversation()`, unconditionally check `if (abortController) abortController.abort()` and reset `isGenerating = false` before clearing or repopulating `messagesContainer`.

---

## 11. Response Regeneration & History Clean Slate

When the user triggers "Regenerate / Buat Ulang":
- **Pitfall**: Sending the prompt again with the same `conversationId` without special flags causes the backend to append a second identical user prompt to SQLite and leaves the stale assistant message in the sliding history window. The model sees its prior failed answer and wastes context tokens.
- **Rule**:
  1. Frontend must pass `isRegenerate: true` in the request payload.
  2. Backend must check `if (isRegenerate)`: atomically delete the latest assistant message for that conversation (`DELETE FROM messages WHERE id = (SELECT id FROM messages WHERE conversation_id = ? AND role = 'assistant' ORDER BY created_at DESC LIMIT 1)`) and skip inserting a duplicate user message.

---

## 12. Streaming Render Throttling via requestAnimationFrame (60 FPS)

When high-speed LLMs stream 30–60 chunks per second:
- **Pitfall**: Executing a full `bubble.innerHTML = formatMarkdown(fullText)` on every individual token chunk triggers severe DOM thrashing, destroys text selection highlights mid-read, causes UI frame drops, and drains mobile batteries.
- **Rule**: Buffer incoming tokens in `pendingText` and schedule DOM updates via `requestAnimationFrame`. Only paint once per browser refresh frame (~16ms), and cancel pending frames on completion or abort.

---

## 13. Syntax Highlighting Attribute Sanitization

Custom code block syntax highlighters that isolate HTML/XML tags and attributes:
- **Pitfall**: Replacing attribute names with colored spans without first passing `attrs` through `escapeHtml()` permits raw attribute strings to be re-injected unescaped into innerHTML, creating XSS or broken tag injection risks if the LLM emits malformed HTML examples.
- **Rule**: Always run `escapeHtml(attrs)` before running attribute-name matching regexes.

---

## 14. Drag-and-Drop Browser Navigation Hijack Prevention

Desktop web chat views:
- **Pitfall**: Dropping files onto the browser window triggers default browser navigation to the file URL (`file://` or blob), terminating the active session and losing unsaved prompt state.
- **Rule**: Register global `dragover` and `drop` event listeners calling `e.preventDefault()`, extract `e.dataTransfer.files`, and route them directly to the attachment ingestion pipeline.

---

## 15. Attachment ObjectURL Lifecycle & Drafting Disambiguation

- **Memory Leak Pitfall**: Generating `URL.createObjectURL(file)` for image thumbnails without pairing it with `URL.revokeObjectURL(url)` in `removeAttachment()` retains Blob memory in browser RAM indefinitely across long sessions.
- **Drafting vs Abort Pitfall**: When Enter is pressed while `isGenerating === true`, never call `stopGeneration()` if the input textarea contains non-empty drafted text. Only treat Enter as Stop when the input is empty; otherwise users trying to draft their next thought will accidentally kill active generation.

---

## 16. Text Deliverable Integrity: Plain Text vs Code Artifact Misconception (Anti-HTML Wrapping)

When users prompt the agent to "bikin/buatkan file/dokumen berisi [karya tulis / puisi / artikel / cerpen / laporan]" (e.g. "bikin sebuah file yang berisi 20 puisi"):
- **Pitfall (Artifact Misconception)**: Coding-focused or Claude-style LLMs reflexively interpret the word "file" or "dokumen" as a web artifact, wrapping human literature/prose into an HTML code block (````html <!DOCTYPE html> ... ````). In the UI, this renders as an unreadable code snippet or iframe sandbox requiring users to preview web code rather than reading their poems/documents as natural text.
- **Rule (Text First, Never Wrap in HTML)**:
  1. **Prompt Isolation**: System instructions must explicitly forbid wrapping written works into HTML/CSS code blocks:
     *"HARAM membuat kode HTML (<!DOCTYPE html>, <html>, tag CSS/div) jika pengguna meminta file puisi, dokumen teks, karya sastra, cerpen, atau artikel bacaan. Pengguna menginginkan teks biasa (.txt / Markdown), BUKAN kodingan web. Blok kode (```) HANYA untuk instruksi pemrograman teknis."*
  2. **Format Standar**: Deliver written works directly as structured Markdown (headers `#`, numbered items `1..N`, poetic stanzas with clean line breaks).
  3. **Dual Export UX ([Unduh TXT] & [Unduh Dokumen])**: Chat action bars must provide both **[Unduh TXT]** (`text/plain` Blob `.txt`) and **[Unduh Dokumen]** (`application/msword` `.doc`), giving users immediate 1-click access to download clean text files to their local disk without manual copy-pasting.

---

## 17. User Intent Understanding Engine & Direct Live Visual Rendering (Anti-Raw Code Slop)

When users prompt the assistant for visual components, interfaces, or interactive tools (e.g. "bikin tampilan login", "buatkan kalkulator mini", "desain landing page", "bikin kartu profil"):
- **Pitfall (Raw Code Barrier)**: Presenting hundreds of lines of raw HTML/CSS boilerplate in a dark code block with a tiny secondary "Pratinjau" button alienates non-technical users. Users asking for a UI desire to **see, interact with, and test the visual design immediately**, not read markup tags.
- **Rule (Intent Resolution Engine)**:
  1. **Context-Level Intent Classification (`<user_intent_understanding_engine>`)**:
     Train the reasoning engine to categorize prompts before generating output:
     - **Visual & UI Intent**: Self-contained HTML/CSS/JS in ```html blocks ready for instant live rendering.
     - **Prose & Document Intent**: Natural Markdown text without HTML wrapping (see Section 16).
     - **Engineering Code Intent**: Isolated script syntax (Python, SQL, Bash) with causal mechanisms.
  2. **Default Active Live Canvas (Inline Sandboxed Iframe)**:
     The Markdown renderer must convert ````html```` blocks directly into an interactive visual card:
     - Active view by default: Sandboxed `<iframe>` with `srcdoc` rendering the live interactive component.
     - Tab Switcher: **[Tampilan Langsung]** (active) vs **[Kode Sumber]** (hidden by default, togglable for developers).
     - Header Actions: **[Layar Penuh]** (expands to device-toggleable modal), **[Unduh]** (.html), and **[Salin]**.
  3. **Inline SVG Vector Rendering**:
     Convert ````svg```` blocks directly into inline vector canvases (`<div class="inline-svg-preview">...</div>`) so icons, flowcharts, and architecture diagrams appear as crisp graphics rather than raw XML markup.

---

## 18. Mobile Scroll Performance & GPU Compositor Decoupling (Anti-Scroll Stutter & Tile Starvation)

When long chat messages (tables, complex markdown) are rendered in a scrollable container (`overflow-y: auto`):
- **Pitfall (Mask-Image Compositor Stutter)**: Applying CSS `mask-image` or `-webkit-mask-image` (e.g. for top/bottom edge gradient fades) on a scrolling container forces the mobile Chromium/WebKit GPU compositor to discard cached bitmap tiles and re-composite the alpha mask across the entire scrolling layer on every touch move. On Android mid-range GPUs, this drops framerates from 60 FPS down to 5–15 FPS ("patah-patah") and causes giant blank/white rectangular tile dropouts.
- **Rule (Hardware Scroll Invariants)**:
  1. **Strictly Forbid `mask-image` on Scroll Containers**: Use lightweight, pointer-events-none gradient overlays or borders instead of alpha masks on scrolling DOM nodes.
  2. **Enable Hardware Layer Isolation**: Apply `contain: layout;`, `will-change: scroll-position;`, `-webkit-overflow-scrolling: touch;`, and `overscroll-behavior-y: contain;` on `#chat-stream`.
  3. **Zero-Vibration Scroll Pinning Architecture (Anti-Jitter Autoscroll Fight)**:
     - **Pitfall (Rapid 60Hz Jitter / Getar-Getar)**: Relying on generous distance-from-bottom heuristics (e.g. `< 120px` or `< 220px`) or touch-end timers to decide autoscroll causes violent screen vibration when users try to scroll up to read earlier text while the AI is writing. The user's thumb moves the scroll up 30–80px, but the RAF loop evaluates `< 120px` as true and pulls `scrollTop = scrollHeight` back down 60 times/sec, locking the user in a rapid fluttering tug-of-war.
     - **Rule (Binary Sticky Pinning State)**:
       - Maintain an explicit state boolean: `let isUserPinnedToBottom = true;`.
       - In the `scroll` event listener:
         ```javascript
         const distFromBottom = chatStream.scrollHeight - chatStream.scrollTop - chatStream.clientHeight;
         // The moment user scrolls up even slightly (> 20px), instantly unpin!
         if (distFromBottom > 20) {
           isUserPinnedToBottom = false;
         } else if (distFromBottom <= 15) {
           // Only re-pin when user is at the absolute bottom edge
           isUserPinnedToBottom = true;
         }
         ```
       - In the streaming/typewriter loop:
         ```javascript
         // STRICT INVARIANT: If user is unpinned, NEVER touch scrollTop! Zero programmatic scroll.
         if (isUserPinnedToBottom) {
           chatStream.scrollTop = chatStream.scrollHeight;
         }
         ```
       - Floating Jump-to-Bottom button: clicking `#btn-scroll-bottom` sets `isUserPinnedToBottom = true;` and smoothly scrolls to bottom.

---

## 19. Action Bar Minimalism & 3-Dots Action Popover (Anti-Button Clutter)

When assistant messages provide multiple post-generation actions (Copy, Regenerate, Download DOC, Download TXT, Export Markdown, Token Badge):
- **Pitfall (Mobile Horizontal Clutter)**: Exposing 4+ text buttons side-by-side (`[Salin] [Buat Ulang] [Unduh TXT] [Unduh Dokumen]`) on narrow mobile viewports (<400px width) forces buttons to wrap into multiple clumsy lines or push the token usage badge off-screen.
- **Rule (3-Dots Popover Hierarchy)**:
  1. **Keep Only Primary Actions Inline**: Show only `[ Salin ]`, `[ Buat Ulang ]`, the 3-dots trigger button (`btn-msg-more`), and the `<span class="token-badge">`.
  2. **Wrap Secondary File Actions into a 3-Dots Popover**:
     ```html
     <div class="msg-more-wrap">
       <button class="btn-msg-action btn-msg-more" onclick="toggleMsgMoreMenu(this, event)" title="Menu opsi lainnya">
         <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
           <circle cx="12" cy="5" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="12" cy="19" r="2"/>
         </svg>
       </button>
       <div class="msg-more-popover" style="display: none;">
         <button class="msg-popover-item" onclick="handlePopoverDownloadDoc(this)">Unduh Dokumen (.doc)</button>
         <button class="msg-popover-item" onclick="handlePopoverDownloadTxt(this)">Unduh Berkas Teks (.txt)</button>
       </div>
     </div>
     ```
  3. **Clean Dismissal**: Automatically close the popover on option click or global document tap outside `.msg-more-wrap`.

---

## 20. Adaptive 60 FPS Character-by-Character Typewriter Streaming (Per-Huruf Smooth Flow)

When SSE streaming sends bursts of text (tokens or multi-word chunks arriving abruptly from backend gateways):
- **Pitfall (Jumpy Chunk Pops)**: Dumping chunks immediately into `innerHTML = formatMarkdown(accumulatedText)` causes jerky visual jumps and thrashes the DOM 30–60 times per second, dropping frames during active user reading.
- **Rule (Adaptive RAF Typewriter Queue)**:
  1. **Character Queue Buffer**: Push incoming SSE chunk text into `targetText` without directly touching the DOM.
  2. **Adaptive Step per Animation Frame**:
     ```javascript
     function typewriterLoop() {
       if (renderedCharCount < targetText.length) {
         const delta = targetText.length - renderedCharCount;
         // Natural ~60 chars/sec per-huruf flow for close deltas
         let step = 1;
         if (delta > 160) step = 8;
         else if (delta > 80) step = 4;
         else if (delta > 25) step = 2;
         else step = 1;

         renderedCharCount = Math.min(targetText.length, renderedCharCount + step);
         bubble.innerHTML = formatMarkdown(targetText.slice(0, renderedCharCount)) + '<span class="typing-cursor"></span>';
         if (isUserPinnedToBottom) chatStream.scrollTop = chatStream.scrollHeight;
         animId = requestAnimationFrame(typewriterLoop);
       } else if (isDone) {
         bubble.innerHTML = formatMarkdown(targetText);
         actionsBar.style.display = 'flex';
         if (isUserPinnedToBottom) chatStream.scrollTop = chatStream.scrollHeight;
       }
     }
     ```
  3. **Smooth Finish & Immediate Stop**: When `done: true` arrives, allow the loop to drain the remaining letters smoothly to completion. On user Stop, invoke `forceFinish()` to cancel the RAF loop and display the full text instantly without delay.
  4. **Cursor Subpixel Baseline Stabilization**:
     - **Pitfall**: Animating `transform: scaleY()` on an `inline-block` typing cursor (`.typing-cursor`) inside flowing text triggers continuous font baseline recalculations in mobile WebKit/Blink, causing text lines to visually tremble and jitter vertically during generation.
     - **Rule**: Animate blinking cursors using pure opacity fading (`opacity: 1` to `opacity: 0` without transform) so line heights and layout baselines remain strictly frozen and calm.

---

## 21. User-Centric Chat Typography & Responsive Font Sizing (Segmented Scale Control)

Reading comfort varies widely across mobile screen densities, distances, and user preferences.
- **Pitfall (Fixed Hardcoded Typography)**: Hardcoding font sizes (`font-size: 14.5px`) without runtime adjustment options forces users with differing visual preferences or high-DPI displays to struggle with text readability on long markdown tables, reports, and code blocks.
- **Rule (Dynamic Segmented Sizing Architecture)**:
  1. **CSS Root Custom Properties**: Declare global sizing variables:
     ```css
     :root {
       --chat-font-size: 14.5px;
       --user-font-size: 14px;
       --chat-line-height: 1.7;
     }
     ```
     Bind chat bubbles, tables, and lists to `var(--chat-font-size)` and `var(--chat-line-height)`.
  2. **Segmented Button Control**: In the Settings panel/popover under Preferences, provide an iOS-style segmented button group with 4 calibrated steps:
     - `Kecil`: `--chat-font-size: 13px; --user-font-size: 12.5px; --chat-line-height: 1.6;`
     - `Standar` (Default): `--chat-font-size: 14.5px; --user-font-size: 14px; --chat-line-height: 1.7;`
     - `Sedang`: `--chat-font-size: 16px; --user-font-size: 15.5px; --chat-line-height: 1.75;`
     - `Besar`: `--chat-font-size: 18px; --user-font-size: 17px; --chat-line-height: 1.8;`
  3. **Immediate Application & Local Persistence**: Updating the selection instantly applies properties via `document.documentElement.style.setProperty()` and stores the choice in `localStorage.setItem('mumu_chat_font_size', sizeKey)`. On initial page load, `initChatFontSize()` restores the saved preset before rendering.

