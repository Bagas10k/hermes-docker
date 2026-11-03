### 5. Dynamic Island ("Rumah si Agent"), Bottom User Tools & Multimodal Engine
- **Dynamic Island as the "Agent's Home" (*Rumahnya si Agent*)**:
  - The Dynamic Island is hidden during idle zen mode; it appears only after chat/work begins.
  - It is the active agent's residence, cognitive status beacon, and compact configuration hub—not a duplicate mascot container.
  - In collapsed state, show only live presence/status and the morph chevron:
    * **Siaga di Rumah**: `[Agent] • Di Rumah` (sub: `Siaga menanti instruksi...` with emerald pulse dot).
    * **Berpikir di Rumah**: `[Agent] • Berpikir di Rumah` (sub: `Menganalisis instruksi...` with amber glow pulse and integrated progress bar).
    * **Merespons**: `[Agent] • Menulis Respon` (sub: `Mengalirkan jawaban ke kartu...`).
    * **Menganalisis Berkas**: `[Agent] • Menganalisis Berkas` (sub: `[nama berkas]`).
  - In expanded state, morph in-place and reveal: AI agent squad selection, response mode config (`Kausal 3-Mindset`, `Ringkas & Cepat`, `Kreatif`), and compact telemetry (CPU/RAM/latency). Keep broad session actions (`+ Baru`, `Riwayat`) near the bottom prompt unless the user asks to move them.
- **Bottom User Controls & Keyboard-Safe Prompt Zone (*Tools User di Bagian Bawah*)**:
  - Put broad session actions beside the prompt as compact icon buttons, not text-heavy pills. Use icon-only `+`/new-chat and history buttons styled like the utility dock, close enough for thumb reach but never overlapping the input field.
  - On mobile keyboard focus, move only the prompt/control block above the virtual keyboard; do not translate the whole page or disturb the zero-scroll canvas. Anchor the command wrapper with fixed positioning and safe-area/keyboard inset handling.
  - `+ Baru`: archives the current thread to `localStorage`, plays a 1–2 second "wrap into history" morph animation, then collapses the chat card and returns to a fresh prompt.
  - `Riwayat`: opens a DI-like compact history panel showing simple conversation titles/snippets.
  - `Mode Respon`: keep active reasoning mode available either in the expanded Dynamic Island or a compact bottom control; avoid duplicating it in multiple places unless the user requests both.
- **Per-Character Monotonic Streaming Engine ("Animasi Ketikan Mengalir Per Huruf")**:
  - Rather than jumping word-by-word or executing full markdown regular expressions on every animation tick (which causes layout thrashing and noticeable freeze/stutter as the response lengthens), use a **Text Node Walker** strategy:
    * Pre-render the full structured Markdown HTML into the chat container once with all styling tags intact (`<p>`, `<strong>`, `<ul>`, `<code>`).
    * Walk the DOM tree using `document.createTreeWalker(container, NodeFilter.SHOW_TEXT)` to collect all text nodes and cache their complete string contents.
    * Temporarily clear each text node's `nodeValue = ''`.
    * Run a monotonic frame loop via `requestAnimationFrame(tick)` with `performance.now()`.
    * Stream characters sequentially across the DOM nodes at calibrated human typing speed (~85–130 chars/sec) with gentle micro-pauses at punctuation marks (`.` `,` `!` `?`), and position a blinking amber cursor (`▌`).
    * Anchor each newly submitted turn once at the top of the internal message viewport, then keep `scrollTop` unchanged while characters stream. Never chase `scrollHeight` during typing—the response must grow downward while the user retains manual control of reading position.
  - Rich accessories such as link cards and file download cards may animate in only after typing completes. Do not append unsolicited follow-up-question chips or recommended replies; they add clutter and undermine the direct conversational flow.
- **DI-Style Simple Morphing History List & Multi-Device Central Sync ("Daftar Simple Morphi Riwayat & Riwayat Tetap Satu")**:
  - **Server-Backed Unified History Across All Devices**: Past conversations must never be trapped exclusively in client-side `localStorage`. In multi-device ecosystems (mobile phone, laptop, tablet), store and synchronize sessions centrally on the server (`GET /coucou/api/sessions`, `POST /coucou/api/sessions`, `DELETE /coucou/api/sessions/:id`, `DELETE /coucou/api/sessions` writing atomically to a state store such as `sessions.json` or SQLite). `localStorage` acts solely as an optimistic cache. Whenever the companion boots or the history sheet opens, sync from the server so a thread started on mobile can be instantly resumed or inspected on desktop with zero fragmentation.
  - Present history as a compact Dynamic-Island-like panel rather than a heavy page. Show simple conversation titles/snippets first; detail can load after selection.
  - Render an ultra-sleek, minimalist list inside the slide-up G2 squircle sheet (`.history-sheet`):
    * **Opening Morph**: Sheet opens with spring physics scaling (`transform: translateY(105%) scale(0.96) -> translateY(0) scale(1); opacity: 0 -> 1;`).
    * **Minimalist Row Layout (`.history-item-simple`)**:
      - Left: Frosted squircle icon with amber chat bubble (`width: 34px; height: 34px; border-radius: 11px;`).
      - Center: Bold single-line session title + subtle timestamp on top; single-line truncated preview snippet below with clean CSS ellipsis.
      - Right: Minimalist delete icon (`✕`) with hover red tint that syncs deletion immediately to the server.
    * **Tactile Spring Squash Feedback**: Tapping an item triggers an instant spring squash (`transform: scale(0.97)`), momentary amber glow border, audio pop, smooth sheet dismissal, and instant thread restoration into the main chat card.
    * Bottom bar: Clean and unobtrusive "Bersihkan Semua Riwayat" action that clears server and local caches simultaneously.
- **File Attachment with Physical Mascot Reaction**:
  - Mount an attach button (`.cmd-attach-btn`) beside the prompt input wired to a hidden file picker.
  - When a file is selected, an emerald preview pill (`.attached-file-pill`) slides in above the command bar with filename, formatted size, and a remove (`✕`) trigger.
  - **Mascot Physical Reaction**: The living mascot immediately reacts physically to the file selection:
    * Eyes tilt downward to look directly at the attachment (`lookY = 1.0`).
    * Body squashes and bounces with surprised delight (`state = 'surprised'; squash(0.55)`).
    * Audio chime `pop` fires.
    * Dynamic Island updates status to `Coucou Menerima Berkas`.
    * Vocal speech bubble asks: *"Wah, ada berkas baru: [filename]! Mau aku analisis apa?"*.
  - When the message is submitted, the attachment metadata is bundled into the API payload so the AI acknowledges and dissects the file with high intellectual curiosity.
- **High Intellectual Curiosity Persona**: The companion AI may explore root causes and propose hypotheses inside the answer, but it must not render separate recommended-response or follow-up-question chips unless explicitly requested.
- **Link Cards**: Structured preview cards with SVG external-link icons, title, and direct URL.
- **File Attachment Cards**: Emerald-tinted file cards (`.chat-file-card`) displaying filename, description, and size. Clicking the download button dynamically synthesizes a `Blob` (`URL.createObjectURL`) for instant, reliable local file download.
- **Reactive Speech & Thought Bubble**:
  - Floats dynamically directly above the mascot's head during casual interactions with a soft pointing tail and spring scale-in animation.
  - Multi-line formatting (`white-space: normal; width: max-content; min-width: 140px; max-width: min(85vw, 320px); word-break: break-word; line-height: 1.4;`). Never apply `white-space: nowrap` or `text-overflow: ellipsis`.
  - Proactive greeting on load (500ms) and playful reactions upon tapping the mascot directly.

### 6. Enlarged Living Agent Folder Container ("Kontainer Pembungkus Agen Hidup")
- **Mobile OS-Style Squircle Folder Architecture**:
  - Wrap the entire multi-agent roster into an **Enlarged Frosted Squircle Folder** inspired by smartphone home screen app folders (HyperOS/iOS/ColorOS).
  - Container box:
    ```css
    .agent-folder-box {
      width: 290px;
      background: rgba(255, 255, 255, 0.12);
      backdrop-filter: blur(36px) saturate(190%);
      -webkit-backdrop-filter: blur(36px) saturate(190%);
      border: 1.5px solid rgba(255, 255, 255, 0.22);
      border-radius: 36px;
      padding: 22px 18px 20px 18px;
      box-shadow: 0 24px 60px rgba(0, 0, 0, 0.75), 0 0 32px rgba(245, 158, 11, 0.12);
    }
    ```
  - Symmetry label: Place the text `"Folder"` (or squad name) directly beneath the container (`font-size: 15px; font-weight: 500; color: #FFFFFF; text-shadow: 0 2px 6px rgba(0, 0, 0, 0.85);`) with clean sans-serif typography.
- **Living Mascot Canvases Inside the Grid ("Agent Tetap Hidup Sesuai Status")**:
  - Inside the grid (e.g. 2x2), **never use static icons or dead illustrations**.
  - Mount an independent 60 FPS micro-canvas (`width: 60px; height: 60px;`) for each agent tile:
    * **Hermes**: White body, glowing amber antenna, focused blush expression, `:80` red badge (*Otak Kognitif*).
    * **Bekagent**: Ice cyan body, curious tilted head, `2` red badge (*Obsidian Vault*).
    * **SputarAI**: Lavender violet body, radar scanning expression, `11` red badge (*Media Radar*).
    * **SputarBall**: Emerald green body, energetic smiling eyes, `:30` red badge (*Portal Skor*).
  - Every micro-mascot runs its own physical loop: blinking independently, breathing, and looking toward pointer interaction.
- **Red Notification Badges ("Lencana Notifikasi Merah")**:
  - Replicate mobile app notification pills mounted at the top-right of each icon wrap (`position: absolute; top: -5px; right: -5px;`):
    ```css
    .agent-noti-badge {
      background: #EF4444;
      color: #FFFFFF;
      font-size: 10px;
      font-weight: 800;
      min-width: 18px;
      height: 18px;
      padding: 0 5px;
      border-radius: 9px;
      border: 1.5px solid #0D1117;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 2px 8px rgba(239, 68, 68, 0.65);
    }
    ```
- **Tactile Pop-in & Two-Tier Glass Peek Interaction**:
  - **Prune Loose Outer Buttons ("Yang di Luar Hapus, Yang di Dalam Dilihat dari Luar")**: Avoid scattering individual agent buttons across the dock alongside a separate folder button. Remove all loose outer agent buttons and consolidate them into a single **Glass Peek Dock Folder** (`.dock-folder-glass`, ~52x52px).
  - **Visible From Outside**: The dock folder features a frosted translucent glass container revealing a 2x2 grid of mini living Coucous directly from the outside, complete with animated eye blinks, signature body colors, active selection ring, and a red notification badge (`4`).
  - **Two-Tier Interaction Architecture**:
    * Direct Quick Switch: Clicking a mini Coucou directly inside the dock folder preview switches the active agent immediately without opening the modal.
    * Modal Expansion: Clicking the surrounding glass container smoothly pops open the full **Enlarged Living Folder Modal** (`@keyframes folderSpringOpen`), displaying large living canvases and complete status diagnostics.
  - Tapping an agent tile triggers tactile squash (`scale(0.92)`), plays that agent's chime signature, smoothly closes the folder, and morphs the main hero mascot to the selected agent.

### 10. Character-as-Container Architecture (The Purrweb Living Body Container)
- **The Living Body Chat Card Concept**:
  - Rather than isolating the mascot into a small corner avatar or letting it crowd the top headroom, the character's physical body forms the **main container card** of the entire chat viewport.
  - Outer Canvas: High-contrast pastel canvas (`#D3E5F6` to `#B7CFEB` light gradient, or dark space aura) framing the character's body.
  - Torso Card (`#mumu-living-container`): Pinned white squircle container (`position: absolute; top: 14px; bottom: 0; left: 16px; right: 16px; border-radius: 40px 40px 0 0;`) holding the conversation inside the character's belly/chest.
  - Stationary Head & Visor Anchor: Top apex of the body container houses the static character head (claymorphic ears, antenna over top border, obsidian visor with tracking OLED eyes and blush). It remains 100% stationary (`position: relative; z-index: 25; flex-shrink: 0;`).
  - Independent Inner Scroll Viewport (`#chat-stream`): Only the messages inside the body container scroll (`overflow-y: auto; flex: 1;`). The character's body and face never budge or translate vertically during scrolling ("waktu gilir ke atas atau bawah itu ngga ngikut tubuhnya").
  - Dual-Stop Upper Gradient Mask: Apply `-webkit-mask-image: linear-gradient(to bottom, transparent 0px, transparent 14px, black 38px, black calc(100% - 24px), transparent 100%)` to the chat stream so messages dissolve smoothly beneath the character's chin/visor without harsh clipping.
  - 2×2 Grid Mobile Welcome Cards: Format preset prompt cards in a compact 2×2 grid (`grid-template-columns: 1fr 1fr; gap: 8px;`) so all 4 core prompts stay visible above the fold on mobile viewports.

## Procedure

1. **Establish Fixed Viewport & Ambient Canvas**:
   - Set `100dvh` flex column, prevent browser default pull-to-refresh and rubberbanding.
   - Lay down an orange radial gradient centered above the content, and expose a persisted Settings control that adjusts its opacity/dimming without changing semantic foreground contrast.
2. **Mount Dual 60 FPS Canvas Objects**:
   - Render the micro-mascot inside the Dynamic Island and the hero living mascot in the central zen canvas.
   - Calculate 3D spherical eye gaze projection:
     $$\text{dx} = \frac{x_{\text{pointer}} - x_{\text{center}}}{w_{\text{window}}}, \quad \text{dy} = \frac{y_{\text{pointer}} - y_{\text{center}}}{h_{\text{window}}}$$
   - Apply spring physics damping for squash & stretch on touch/tap.
3. **Mount Gesture-Driven Living Agent Switcher**:
   - Keep one active hero mascot visible. On a ~500ms hold, reveal the other independently animated mascot canvases fanned behind and beside it; do not replace them with text pills or static icons.
   - Capture the pointer on press. While held, map pointer coordinates to immutable opening-time agent anchor points, preview the nearest agent continuously, then commit on release. Preserve a tap/click fallback and cancel cleanly on `pointercancel`.
   - During preview, suppress repetitive toast/audio, optionally provide a bounded haptic tick, and bring only the candidate mascot forward with spring scale/depth. On close, restore the hero to `idle`, explicitly zero current and target tilt, and retain gaze tracking so switching never leaves it permanently leaning or unable to look around.
4. **Implement Nested Settings Drawer**:
   - Hook settings open button to add `.open` class to drawer and backdrop overlay.
   - Allow dismissal via close button (`✕`), backdrop click, drag handle, or Escape key.
5. **Mount Spotlight Command Bar & Reactive Speech Bubble**:
   - Anchor the command bar directly above a minimal dock containing only session navigation and settings. Put audio, diagnostics/ping, ambient dimming, and other utilities inside Settings; do not expose unexplained utility icons in the primary dock.
   - Keep the interaction hint faint and terse (for example, `Sentuh Coucou untuk berinteraksi`) so it does not compete with the mascot.
   - Mount an absolute-positioned speech bubble container above the mascot canvas.
   - Wire submit event to trigger optimistic "thinking" state (upward eye tilt, work chime), call the backend command endpoint asynchronously, and render the vocalized reply with emotional animation.
6. **Verify Zero-Emoji & Accessibility**:
   - 100% SVG vector icons for every glyph.
   - Minimum 44px touch targets on mobile viewports.
