# Web Agent Chat Architecture Recipe

Practical implementation patterns for Express backends and vanilla/reactive frontends.

## 1. Backend Route Contract (Express.js)

```javascript
const router = require('express').Router();
const fs = require('fs');

const CHAT_STATE_FILE = '/path/to/state/chat_history.json';

function getChatHistory() {
  try {
    return JSON.parse(fs.readFileSync(CHAT_STATE_FILE, 'utf8'));
  } catch {
    return [];
  }
}

function saveChatHistory(history) {
  fs.writeFileSync(CHAT_STATE_FILE, JSON.stringify(history.slice(-100), null, 2));
}

// Inbound User Turn Dispatcher
router.post('/chat', async (req, res) => {
  try {
    const { message, agent = 'Hermes Core' } = req.body || {};
    if (!message || !message.trim()) return res.status(400).json({ ok: false, error: 'Empty message' });

    const now = new Date();
    const timeStr = now.toTimeString().split(' ')[0];

    const userMessage = {
      id: Date.now(),
      role: 'user',
      sender: 'Bagas Cihuy',
      content: message.trim(),
      time: timeStr
    };

    const history = getChatHistory();
    history.push(userMessage);

    // Call Local Inference (e.g. 9router / completions)
    const aiResponse = await fetch('http://127.0.0.1:20128/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: 'bk',
        messages: [
          { role: 'system', content: `You are ${agent}, responding directly to user instructions.` },
          ...history.slice(-6).map(h => ({ role: h.role, content: h.content })),
          { role: 'user', content: message.trim() }
        ],
        stream: false
      })
    });

    const data = await aiResponse.json();
    const replyText = data.choices?.[0]?.message?.content || 'No response generated.';

    const assistantMessage = {
      id: Date.now() + 1,
      role: 'assistant',
      sender: agent,
      content: replyText,
      time: timeStr
    };

    history.push(assistantMessage);
    saveChatHistory(history);

    res.json({ ok: true, userMessage, assistantMessage });
  } catch (err) {
    res.status(500).json({ ok: false, error: err.message });
  }
});
```

## 2. Frontend Dock Anti-Bleed CSS Structure

```css
/* Scroll container must pad bottom strictly greater than dock height */
.chat-scroll-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px 20px 170px; /* 170px = dock height (120px) + margin (50px) */
  scroll-behavior: smooth;
}

/* Floating dock container with accelerated opacity ramp */
.floating-dock-container {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 20px 20px;
  background: linear-gradient(180deg, 
    rgba(250, 248, 245, 0) 0%, 
    rgba(250, 248, 245, 0.85) 15%, 
    #faf8f5 40%, 
    #faf8f5 100%
  );
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  z-index: 30;
}
```

## 3. Local Storage Prompt Preset Cache

```javascript
function saveCustomPrompt(name, promptText) {
  const existing = JSON.parse(localStorage.getItem('hermes_custom_prompts') || '[]');
  existing.unshift({ id: Date.now(), name, prompt: promptText });
  localStorage.setItem('hermes_custom_prompts', JSON.stringify(existing.slice(0, 50)));
}

function loadCustomPrompts() {
  return JSON.parse(localStorage.getItem('hermes_custom_prompts') || '[]');
}
```

## 4. Mobile-First Responsive Suite & Auto-Expanding Input (iOS/Android)

```css
@media (max-width: 640px) {
  /* Prevent bounce & lock viewport */
  html, body {
    width: 100vw;
    max-width: 100vw;
    height: 100dvh;
    overflow: hidden;
    position: fixed;
    inset: 0;
  }

  /* Header compacting */
  header {
    height: 52px;
    padding: 0 10px;
    max-width: 100vw;
    overflow: hidden;
  }
  .brand-subtitle { display: none !important; }
  .btn-header-label { display: none !important; }
  .btn-action-header {
    min-width: 36px;
    min-height: 36px;
  }

  /* Chat feed clearance */
  #chat-stream {
    padding: 12px 10px calc(195px + env(safe-area-inset-bottom, 0px));
  }

  /* Floating Dock & Capsule */
  .dock-container {
    padding: 6px 10px calc(10px + env(safe-area-inset-bottom, 0px));
  }
  .dock-toolbar {
    padding-right: 24px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  .input-capsule {
    min-height: 44px;
    padding: 6px 8px 6px 14px;
  }

  /* Single-line ellipsis placeholder preventing vertical truncation */
  #chat-input {
    font-size: 14px;
    line-height: 22px;
    min-height: 22px;
    height: 22px;
    padding: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}
```

### Auto-Expanding Textarea Logic (Vanilla JS)

```javascript
const chatInput = document.getElementById('chat-input');

chatInput.addEventListener('input', function() {
  if (!this.value.trim()) {
    this.style.whiteSpace = 'nowrap';
    this.style.height = '22px';
  } else {
    this.style.whiteSpace = 'normal';
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 130) + 'px';
  }
});

// Reset on send
function resetInputAfterSend() {
  chatInput.value = '';
  chatInput.style.whiteSpace = 'nowrap';
  chatInput.style.height = '22px';
}
```

## 5. Mobile Bottom-Sheet Modal Pattern

```css
@media (max-width: 640px) {
  .modal-overlay {
    padding: 0;
    align-items: flex-end;
  }
  .modal-card {
    max-width: 100vw;
    width: 100vw;
    border-radius: 22px 22px 0 0;
    max-height: 90dvh;
    display: flex;
    flex-direction: column;
  }
  .modal-drag-bar {
    display: block;
    width: 38px;
    height: 4px;
    border-radius: 999px;
    background: var(--border-strong);
    margin: 10px auto 4px;
  }
  .modal-body {
    padding: 14px 16px calc(90px + env(safe-area-inset-bottom, 0px));
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
  }
  .modal-footer {
    position: sticky;
    bottom: 0;
    padding: 10px 16px calc(12px + env(safe-area-inset-bottom, 0px));
    background: var(--bg-card);
    border-top: 1px solid var(--border-subtle);
  }
  .btn-modal-cancel {
    display: none !important; /* Rely on top-right close icon or backdrop dismiss */
  }
}
```

## 6. Robust Lightweight Markdown & Numbered List Tokenizer

```javascript
function escapeHtml(str) {
  return (str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function formatMarkdown(text) {
  if (!text) return '';

  // 1. Stash fenced code blocks
  const codeBlocks = [];
  let raw = text.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, (match, lang, code) => {
    const idx = codeBlocks.length;
    codeBlocks.push(`<pre><code class="language-${lang || 'text'}">${escapeHtml(code.trim())}</code></pre>`);
    return `@@CODEBLOCK_${idx}@@`;
  });
  raw = raw.replace(/```([\s\S]*?)```/g, (match, code) => {
    const idx = codeBlocks.length;
    codeBlocks.push(`<pre><code>${escapeHtml(code.trim())}</code></pre>`);
    return `@@CODEBLOCK_${idx}@@`;
  });

  let out = escapeHtml(raw);

  // 2. Inline elements
  out = out.replace(/`([^`]+)`/g, '<code>$1</code>');
  out = out.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  out = out.replace(/(^|[\s(])(https?:\/\/[^\s<)]+)/g, '$1<a href="$2" target="_blank" rel="noopener">$2</a>');
  out = out.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  out = out.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  out = out.replace(/__([^_]+)__/g, '<strong>$1</strong>');
  out = out.replace(/~~([^~]+)~~/g, '<del>$1</del>');
  out = out.replace(/^### (.*$)/gim, '<h3>$1</h3>');
  out = out.replace(/^## (.*$)/gim, '<h2>$1</h2>');
  out = out.replace(/^# (.*$)/gim, '<h1>$1</h1>');
  out = out.replace(/^---$/gim, '<hr>');

  // 3. Tokenize lines into Paragraphs, Numbered Lists (<ol>), and Bullet Lists (<ul>)
  const lines = out.split('\n');
  const tokens = [];
  let currentList = null;
  let currentParagraph = [];

  function flushParagraph() {
    if (currentParagraph.length > 0) {
      tokens.push({ type: 'p', content: currentParagraph.join('<br>') });
      currentParagraph = [];
    }
  }

  function flushList() {
    if (currentList) {
      tokens.push(currentList);
      currentList = null;
    }
  }

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    if (!trimmed) {
      flushParagraph();
      continue;
    }

    if (/^@@CODEBLOCK_\d+@@$/.test(trimmed) || /^<(?:h[1-6]|hr|blockquote)/i.test(trimmed)) {
      flushParagraph();
      flushList();
      tokens.push({ type: 'raw', content: trimmed });
      continue;
    }

    // Numbered list item: "1. ", "2. ", "1) ", "a. "
    const numMatch = line.match(/^(\s*)(?:\d+[\.\)]|[a-zA-Z][\.\)])\s+(.*)$/);
    if (numMatch) {
      flushParagraph();
      if (!currentList || currentList.type !== 'ol') {
        flushList();
        currentList = { type: 'ol', items: [] };
      }
      currentList.items.push([numMatch[2]]);
      continue;
    }

    // Bullet list item: "- ", "* ", "• ", "+ "
    const bulletMatch = line.match(/^(\s*)[•\-\*\+]\s+(.*)$/);
    if (bulletMatch) {
      flushParagraph();
      if (!currentList || currentList.type !== 'ul') {
        flushList();
        currentList = { type: 'ul', items: [] };
      }
      currentList.items.push([bulletMatch[2]]);
      continue;
    }

    // List item continuation (indented text or sub-sentences)
    if (currentList && (/^\s{2,}/.test(line) || (!line.startsWith('#') && currentList.items.length > 0 && lines[i - 1].trim().length > 0))) {
      currentList.items[currentList.items.length - 1].push(trimmed);
      continue;
    }

    flushList();
    currentParagraph.push(trimmed);
  }

  flushParagraph();
  flushList();

  // 4. Assemble HTML parts
  const htmlParts = tokens.map(tok => {
    if (tok.type === 'raw') return tok.content;
    if (tok.type === 'p') return `<p>${tok.content}</p>`;
    if (tok.type === 'ol') {
      const lis = tok.items.map(arr => `<li>${arr.join('<br>')}</li>`).join('\n');
      return `<ol class="md-numbered-list">\n${lis}\n</ol>`;
    }
    if (tok.type === 'ul') {
      const lis = tok.items.map(arr => `<li>${arr.join('<br>')}</li>`).join('\n');
      return `<ul class="md-bullet-list">\n${lis}\n</ul>`;
    }
    return '';
  });

  let result = htmlParts.join('\n');

  // 5. Restore code blocks
  result = result.replace(/@@CODEBLOCK_(\d+)@@/g, (m, idx) => codeBlocks[parseInt(idx, 10)] || '');
  return result;
}
```

## 7. Deterministic Dirty-Checked Polling Engine (Anti-Flicker)

```javascript
let lastRenderedChatSignature = '';
let isFetchingChat = false;
let isWaitingForResponse = false;

function computeChatSignature(messages) {
  if (!messages || messages.length === 0) return 'empty';
  const last = messages[messages.length - 1];
  return `${messages.length}:${last.time || ''}:${(last.content || '').length}`;
}

async function fetchStudioChat() {
  if (isFetchingChat || isWaitingForResponse) return;
  isFetchingChat = true;

  try {
    const res = await fetch('/api/studio/chat');
    if (!res.ok) return;
    const data = await res.json();

    if (data && Array.isArray(data.messages)) {
      const sig = computeChatSignature(data.messages);
      // STRICT DIRTY CHECK: If signature unchanged, NEVER touch the DOM!
      if (sig !== lastRenderedChatSignature) {
        lastRenderedChatSignature = sig;
        renderMessages(data.messages);
      }
    }
  } catch (err) {
    // quiet background sync
  } finally {
    isFetchingChat = false;
  }
}

// Smart Poller: Pauses when tab is hidden or waiting for LLM completion
setInterval(() => {
  if (!document.hidden && !isWaitingForResponse) {
    fetchStudioChat();
  }
}, 7000);
```

## 8. Persistent Living Companion & Flex Sibling Layout

Preventing the mascot from disappearing when chatting or scrolling:

```html
<!-- Main Container -->
<main>
  <!-- 1. Sibling Stage: Anchored outside scroll stream -->
  <div id="mumu-companion-zone" class="hero-mode">
    <div class="mumu-stage-wrap">
      <div class="mumu-stage" id="mumu-stage" onclick="reactMumu()">
        <!-- 3D Mascot Rig / Canvas / SVG -->
      </div>
      <div class="mumu-status-pill">
        <span class="mumu-status-dot"></span>
        <span id="pill-label">Companion • Ready</span>
      </div>
    </div>
  </div>

  <!-- 2. Sibling Stream: Dedicated scroll container -->
  <div id="chat-stream">
    <div class="chat-inner">
      <!-- Welcome headline and prompt cards (hidden when chat active) -->
      <div class="hero-welcome" id="hero-welcome-block">...</div>

      <!-- Messages Stream -->
      <div id="chat-messages-container"></div>
    </div>
  </div>
</main>
```

```css
main {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

/* Hero Mode (Empty Chat) */
#mumu-companion-zone.hero-mode {
  padding: 16px 20px 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}

/* Chat Mode (Active Conversation - Corner Living Mascot with Soft Radial Gradient) */
#mumu-companion-zone.chat-mode {
  padding: 6px 16px 8px 12px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  background: radial-gradient(ellipse 260px 100px at 45px 50%, rgba(255, 255, 255, 0.95) 0%, rgba(237, 244, 249, 0.7) 40%, rgba(237, 244, 249, 0) 100%);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: none !important;
  border-bottom: none !important;
  box-shadow: none !important;
  width: 100%;
  flex-shrink: 0;
  z-index: 15;
}

#mumu-companion-zone.chat-mode .mumu-stage {
  width: 86px;
  min-width: 86px;
  height: 92px;
  min-height: 92px;
  perspective: 600px;
  background: transparent;
  border: none;
  box-shadow: none;
  overflow: visible;
}

/* Omit status text pill during active chat */
#mumu-companion-zone.chat-mode .mumu-status-pill {
  display: none !important;
}

#chat-stream {
  flex: 1;
  overflow-y: auto;
  /* Top padding (22px) strictly exceeds mask fade distance (14px) */
  padding: 22px 20px 170px;
}
```

## 9. Pre-Decoded Audio Engine with Fallback (0ms Latency)

```javascript
class CompanionSoundEngine {
  constructor(soundNames = []) {
    this.soundNames = soundNames;
    this.buffers = {};
    this.ctx = null;
    this.idleTimer = null;
  }

  ensureContext() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioCtx();
    }
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
    clearTimeout(this.idleTimer);
    this.idleTimer = setTimeout(() => {
      if (this.ctx && this.ctx.state === 'running') this.ctx.suspend();
    }, 2000);
  }

  async preloadAll() {
    this.ensureContext();
    await Promise.all(this.soundNames.map(async name => {
      try {
        const res = await fetch(`/sounds/${name}.wav`);
        if (!res.ok) return;
        const arrayBuf = await res.arrayBuffer();
        this.buffers[name] = await this.ctx.decodeAudioData(arrayBuf);
      } catch (e) {
        // Fallback to oscillator if file unavailable
      }
    }));
  }

  play(name, volume = 0.4) {
    this.ensureContext();
    if (this.buffers[name]) {
      const src = this.ctx.createBufferSource();
      const gain = this.ctx.createGain();
      src.buffer = this.buffers[name];
      gain.gain.value = volume;
      src.connect(gain);
      gain.connect(this.ctx.destination);
      src.start(0);
    } else {
      // Zero-asset fallback synthesizer
      this.playSyntheticBeep(name);
    }
  }

  playSyntheticBeep(type) {
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(460, this.ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(780, this.ctx.currentTime + 0.12);
    gain.gain.setValueAtTime(0.15, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.14);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start();
    osc.stop(this.ctx.currentTime + 0.15);
  }
}

## 10. Kinematics-to-CSS Scale Synchronization & Silk Fade Scroll Mask

### A. Kinematics Scale Matrix (Preventing Scale Clashing)
When using dynamic 60 FPS head-tracking or squash/stretch in JavaScript, inline transforms override CSS class scales every frame. Calculate the active base scale directly in the animation step:

```javascript
function updateCompanionKinematics() {
  const isChatMode = companionZone.classList.contains('chat-mode');
  const isMobile = window.innerWidth <= 640;
  
  // Base scale matrix driven by UI state: Keep large & tactile in corner
  const baseScale = isChatMode ? (isMobile ? 0.62 : 0.68) : 1.0;
  
  // Constrain dynamic tilt/squash deltas when compressed
  const maxFloatDelta = isChatMode ? 3.0 : 8.0;
  const floatOffset = Math.sin(Date.now() / 450) * maxFloatDelta;
  
  // Apply combined transform
  mascotRig.style.transform = `translate3d(0, ${floatOffset}px, 0) scale(${baseScale})`;
  
  requestAnimationFrame(updateCompanionKinematics);
}
```

### B. Silk Fade Scroll Mask (CSS Mask-Image)
Prevent harsh visual clipping when long chat logs scroll under sticky headers or sibling companion bars:

```css
#chat-stream {
  flex: 1;
  overflow-y: auto;
  /* Top padding (22px) strictly exceeds mask fade distance (14px) to prevent initial message clipping */
  padding: 22px 20px 170px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  scroll-behavior: smooth;
  
  /* Silk fade gradient mask on top and bottom edges */
  -webkit-mask-image: linear-gradient(
    to bottom,
    transparent 0px,
    black 14px,
    black calc(100% - 20px),
    transparent 100%
  );
  mask-image: linear-gradient(
    to bottom,
    transparent 0px,
    black 14px,
    black calc(100% - 20px),
    transparent 100%
  );
}
```

## 11. Living Mascot Body Container & Claymorphic Appendage Recipe

Architecture for immersive mascot-as-container UIs (e.g. Purrweb Living Body paradigm):

```css
/* Ambient Drifting Glow Mesh Orbs */
.ambient-glass-orb {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  filter: blur(55px);
  z-index: 1;
  opacity: 0.65;
  animation: orbFloat 14s ease-in-out infinite alternate;
}
.orb-cyan {
  width: 320px;
  height: 320px;
  top: 40px;
  right: -40px;
  background: radial-gradient(circle, rgba(0, 229, 255, 0.45) 0%, rgba(0, 229, 255, 0) 70%);
}
.orb-purple {
  width: 340px;
  height: 340px;
  bottom: 40px;
  left: -60px;
  background: radial-gradient(circle, rgba(168, 85, 247, 0.4) 0%, rgba(168, 85, 247, 0) 70%);
}
@keyframes orbFloat {
  0% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(30px, -25px) scale(1.08); }
  100% { transform: translate(-25px, 30px) scale(0.92); }
}

/* 1. Parent living body container card: Frosted Morphic Glass with Positive Headroom */
#mumu-living-container {
  position: absolute;
  top: 76px; /* Desktop: 76px. Mobile: 84px to maintain >=32px positive headroom below 52px navbar */
  bottom: 0;
  left: 16px;
  right: 16px;
  max-width: 820px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.76);
  backdrop-filter: blur(28px) saturate(200%);
  -webkit-backdrop-filter: blur(28px) saturate(200%);
  border-radius: 40px 40px 0 0;
  box-shadow: 
    0 30px 80px rgba(14, 27, 49, 0.12),
    0 10px 30px rgba(14, 27, 49, 0.05),
    inset 0 2px 6px rgba(255, 255, 255, 0.95),
    inset 0 -2px 6px rgba(0, 229, 255, 0.08);
  border: 1.5px solid rgba(255, 255, 255, 0.85);
  display: flex;
  flex-direction: column;
  overflow: visible; /* CRITICAL: Enables ears & antenna to peek over top rim unclipped */
  z-index: 5;
  transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* 2. Stationary Face Apex: Frosted Glass, elevation, anchored at top */
#hero-mumu-zone.mumu-container-face {
  position: relative;
  width: 100%;
  height: 88px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.55);
  border-radius: 40px 40px 0 0;
  z-index: 25;
}

/* 3. Arched Smiling Crescent Eyes (^ ^) */
#hero-mumu-zone.happy .mumu-eye {
  width: 15px !important;
  height: 8px !important;
  border-radius: 14px 14px 0 0 !important;
  background: transparent !important;
  border-top: 3.5px solid #00e5ff !important;
  border-left: 2px solid #00e5ff !important;
  border-right: 2px solid #00e5ff !important;
  border-bottom: none !important;
  box-shadow: 0 -2px 12px #00e5ff, 0 0 24px rgba(0, 229, 255, 0.9) !important;
  transform: translateY(-2px);
}

/* 4. 3D Volumetric Sculpted Claymorphic Ears with Inset Conch */
.mumu-head-ear {
  position: absolute;
  top: -20px;
  width: 30px;
  height: 42px;
  border-radius: 16px 16px 8px 8px;
  background: linear-gradient(180deg, #ffffff 0%, #e0ecfa 100%);
  border: 2.5px solid #ffffff;
  box-shadow: 
    0 8px 20px rgba(28, 38, 92, 0.18),
    0 2px 6px rgba(0, 229, 255, 0.2),
    inset 0 2px 4px rgba(255, 255, 255, 0.95);
  pointer-events: none;
  z-index: 15;
  transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.mumu-head-ear::after {
  content: '';
  position: absolute;
  top: 6px;
  left: 5px;
  right: 5px;
  bottom: 7px;
  border-radius: 10px 10px 4px 4px;
  background: linear-gradient(180deg, #dceaff 0%, #b8d9fc 100%);
  box-shadow: inset 0 2px 4px rgba(12, 28, 56, 0.15);
}
.mumu-head-ear.left { left: calc(50% - 72px); transform: rotate(-18deg); }
.mumu-head-ear.right { right: calc(50% - 72px); transform: rotate(18deg); }

/* 5. Glowing Jewel Antenna */
.mumu-head-antenna {
  position: absolute;
  top: -26px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  pointer-events: none;
  z-index: 25;
}
.mumu-antenna-ball {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #ffffff 0%, #00e5ff 55%, #0088b3 100%);
  box-shadow: 0 0 18px #00e5ff, 0 0 36px rgba(0, 229, 255, 0.95);
  border: 2.5px solid #ffffff;
}

/* 6. Independent Inner Scroll Stream */
#chat-stream {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 18px 22px 140px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

## 12. Mobile Software Keyboard Pinning via visualViewport

Anchor floating prompt docks reliably above the iOS and Android virtual keyboard:

```javascript
if (window.visualViewport) {
  const updateKeyboardOffset = () => {
    // Calculate keyboard displacement including visual viewport scroll offset
    const offsetFromBottom = window.innerHeight - (window.visualViewport.height + (window.visualViewport.offsetTop || 0));
    const dockWrap = document.querySelector('.input-dock-wrap');
    if (dockWrap) {
      dockWrap.style.bottom = offsetFromBottom > 40 
        ? `${Math.max(offsetFromBottom, 0) + 10}px` 
        : 'calc(14px + var(--safe-bottom))';
    }
  };
  
  // Listen to both resize and scroll for iOS Safari compatibility
  window.visualViewport.addEventListener('resize', updateKeyboardOffset);
  window.visualViewport.addEventListener('scroll', updateKeyboardOffset);
}
```

```html
<!-- Pair with interactive-widget in viewport meta tag -->
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover, interactive-widget=resizes-content">
```

## 13. In-Dock Model & Thinking Depth Pill Selectors Alongside Execution Button

Mount agent runtime, thinking pills, and the execution button on the action row directly beneath the auto-growing textarea:

```html
<div class="input-dock">
  <!-- Top: Expanding Textarea -->
  <div class="dock-input-row">
    <textarea id="chat-input" class="chat-textarea" rows="1" placeholder="Kirim pesan ke Mumu..."></textarea>
  </div>

  <!-- Bottom: Action Bar with Attachment on left, Pills + Execution Button on right -->
  <div class="dock-action-bar">
    <button class="btn-dock-icon" onclick="triggerAttachFile()" aria-label="Lampirkan berkas">
      <!-- Paperclip SVG -->
    </button>

    <div class="dock-right-actions">
      <!-- Model Pill (Frosted White Blur) -->
      <div style="position: relative;">
        <button class="dock-pill-btn" id="btn-dock-model" onclick="toggleDockPopover('model')">
          <span id="label-dock-model">Mumu bk</span>
          <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
        </button>
        <div class="dock-popover" id="popover-model">
          <button class="dock-popover-item active" onclick="selectModel('bk', 'Mumu bk')">Mumu bk (Default)</button>
          <button class="dock-popover-item" onclick="selectModel('architect', 'Architect')">Architect</button>
        </div>
      </div>

      <!-- Thinking Effort Controller (Frosted White Blur) -->
      <div style="position: relative;">
        <button class="dock-pill-btn" id="btn-dock-thinking" onclick="toggleDockPopover('thinking')">
          <span id="label-dock-thinking">Think: Standar</span>
          <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
        </button>
        <div class="dock-popover" id="popover-thinking">
          <button class="dock-popover-item" onclick="selectThinking('off', 'Think: Off')">Off (Cepat)</button>
          <button class="dock-popover-item active" onclick="selectThinking('standard', 'Think: Standar')">Standar (Penalaran Ringan)</button>
          <button class="dock-popover-item" onclick="selectThinking('deep', 'Think: Mendalam')">Mendalam (Tiga Mindset Penuh)</button>
        </div>
      </div>

      <!-- Execution Button (Luminous Blue Gradient) -->
      <button id="btn-send-chat" class="btn-send" onclick="handleSendOrStop()" aria-label="Kirim Pesan">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 19V5M5 12l7-7 7 7"/></svg>
      </button>
    </div>
  </div>
</div>
```

```css
.dock-pill-btn {
  background: rgba(255, 255, 255, 0.76);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 0.5px solid rgba(255, 255, 255, 0.95);
  border-radius: 9999px;
  padding: 4px 10px;
  font-size: 11.5px;
  font-weight: 700;
  color: #1e293b;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(14, 27, 49, 0.04), inset 0 1px 2px rgba(255, 255, 255, 0.95);
}

.btn-send {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2b7fff 0%, #0059f7 50%, #0047d4 100%);
  border: 0.5px solid rgba(255, 255, 255, 0.45);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(0, 89, 247, 0.32);
}
```

## 14. Continuous Liquid Opacity Gradient Blur Masks

Eliminate sharp, abrupt cutoff seams on backdrop-filter glass layers:

```css
/* Sticky top navbar: feathers out into pure transparent canvas at bottom */
.top-navbar-wrap {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 54px;
  background: rgba(255, 255, 255, 0.55);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  -webkit-mask-image: linear-gradient(to bottom, rgba(0,0,0,1) 70%, rgba(0,0,0,0) 100%);
  mask-image: linear-gradient(to bottom, rgba(0,0,0,1) 70%, rgba(0,0,0,0) 100%);
}

/* Floating bottom dock blur backing: feathers out towards the top */
.dock-blur-backing {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 120px;
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  -webkit-mask-image: linear-gradient(to top, rgba(0,0,0,1) 75%, rgba(0,0,0,0) 100%);
  mask-image: linear-gradient(to top, rgba(0,0,0,1) 75%, rgba(0,0,0,0) 100%);
}
```

## 15. Harmonious Multi-Stop Blue Gradient Prompt Bubble (Apple iMessage Standard)

Luminous user message bubble with specular rim lighting and squircle anchoring:

```css
.message-row.user {
  display: flex;
  width: 100%;
  justify-content: flex-end;
  align-items: flex-end;
}

.message-row.user .message-bubble {
  /* 4-point continuous gradient avoiding banding artifacts */
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 32%, #1d4ed8 68%, #1e40af 100%);
  color: #ffffff;
  /* Asymmetric squircle anchoring lower-right edge to sender */
  border-radius: 20px 20px 4px 20px;
  padding: 12px 18px;
  font-size: 14px;
  line-height: 1.55;
  font-weight: 500;
  max-width: 82%;
  margin-left: auto;
  /* Diffuse colored ambient drop-shadow + specular rim highlight */
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.28), 
              inset 0 1px 1.5px rgba(255, 255, 255, 0.5), 
              inset 0 -1px 2px rgba(0, 0, 0, 0.12);
  border: 0.5px solid rgba(255, 255, 255, 0.35);
  word-break: break-word;
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.08);
}
```

## 16. Light-Blue Pastel Code Blocks & Multi-Language Syntax Highlighter

Render code blocks with soft pastel light-blue gradients, macOS window controls, and robust regex syntax highlighting across programming languages and markup:

```css
.code-block-wrapper {
  margin: 14px 0;
  border-radius: 14px;
  background: linear-gradient(145deg, #f0f7ff 0%, #e0f2fe 50%, #d6ebfd 100%);
  border: 1px solid rgba(147, 197, 253, 0.7);
  box-shadow: 0 6px 18px rgba(56, 189, 248, 0.12), 0 2px 6px rgba(0, 0, 0, 0.03);
  overflow: hidden;
}
.code-block-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 14px;
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(147, 197, 253, 0.5);
}
.code-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.mac-window-dots {
  display: flex;
  align-items: center;
  gap: 5px;
}
.mac-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
.mac-dot.red { background: #ff5f56; }
.mac-dot.yellow { background: #ffbd2e; }
.mac-dot.green { background: #27c93f; }

.code-lang-label {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  color: #0369a1;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.code-block-wrapper pre {
  padding: 14px 16px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  font-family: var(--font-mono);
  font-size: 12.5px;
  line-height: 1.6;
  color: #0f2b48;
  background: transparent;
  scrollbar-width: thin;
  scrollbar-color: rgba(14, 165, 233, 0.35) transparent;
}

/* Syntax Token Highlighting */
.tok-keyword { color: #4f46e5; font-weight: 700; }
.tok-string { color: #047857; font-weight: 600; }
.tok-number { color: #ea580c; font-weight: 600; }
.tok-comment { color: #64748b; font-style: italic; }
.tok-attr { color: #0284c7; font-weight: 600; }
```

```javascript
function highlightSyntax(rawCode) {
  const tokens = [];
  let code = rawCode;

  // 1. Comments (JS, Python, Shell, HTML/XML)
  code = code.replace(/(\/\/[^\n]*|#[^\n]*|<!--[\s\S]*?-->)/g, (m) => {
    tokens.push('<span class="tok-comment">' + escapeHtml(m) + '</span>');
    return '___TKN_' + (tokens.length - 1) + '_END___';
  });

  // 2. Strings
  code = code.replace(/(".*?"|'.*?'|`.*?`)/gs, (m) => {
    tokens.push('<span class="tok-string">' + escapeHtml(m) + '</span>');
    return '___TKN_' + (tokens.length - 1) + '_END___';
  });

  // 3. Doctype
  code = code.replace(/(<!DOCTYPE[\s\S]*?>)/gi, (m) => {
    tokens.push('<span class="tok-comment">' + escapeHtml(m) + '</span>');
    return '___TKN_' + (tokens.length - 1) + '_END___';
  });

  // 4. HTML/XML Tags & Attributes
  code = code.replace(/(<\/?[a-zA-Z0-9_\-]+)([\s\S]*?)(\/?>)/g, (match, tagStart, attrs, tagEnd) => {
    const coloredTag = '<span class="tok-keyword">' + escapeHtml(tagStart) + '</span>';
    const coloredAttrs = attrs.replace(/\b([a-zA-Z_\-:]+)(?=\s*=)/g, (m, attrName) => '<span class="tok-attr">' + attrName + '</span>');
    tokens.push(coloredTag + coloredAttrs + '<span class="tok-keyword">' + escapeHtml(tagEnd) + '</span>');
    return '___TKN_' + (tokens.length - 1) + '_END___';
  });

  // 5. Programming Keywords
  code = code.replace(/\b(const|let|var|function|return|if|else|for|while|class|import|export|from|async|await|def|try|catch|switch|case|break|continue|new|this|typeof|null|undefined|true|false)\b/g, (m) => {
    tokens.push('<span class="tok-keyword">' + m + '</span>');
    return '___TKN_' + (tokens.length - 1) + '_END___';
  });

  // 6. Numbers
  code = code.replace(/\b(\d+(?:\.\d+)?)\b/g, (m) => {
    tokens.push('<span class="tok-number">' + m + '</span>');
    return '___TKN_' + (tokens.length - 1) + '_END___';
  });

  code = escapeHtml(code);
  let safety = 0;
  while (code.includes('___TKN_') && safety < 10) {
    code = code.replace(/___TKN_(\d+)_END___/g, (match, idx) => tokens[parseInt(idx, 10)]);
    safety++;
  }
  return code;
}
```

## 17. Artifact Sandbox Modal & Cross-Origin Media Download Handler

```javascript
// Sandbox Live Preview Handler with Automatic SVG Boilerplate Wrapping
let currentPreviewHtml = '';

function openArtifactPreview(btn) {
  const wrapper = btn.closest('.code-block-wrapper');
  const codeEl = wrapper ? wrapper.querySelector('pre code') : null;
  if (!codeEl) return;

  currentPreviewHtml = codeEl.innerText || codeEl.textContent;
  const lang = (wrapper.dataset.lang || 'html').toLowerCase();
  const modal = document.getElementById('modal-artifact-preview');
  const iframe = document.getElementById('artifact-preview-iframe');
  const titleEl = document.getElementById('artifact-preview-title');
  
  if (titleEl) {
    titleEl.textContent = (lang === 'svg' || lang === 'xml') ? 'Pratinjau Grafis Vektor SVG' : 'Pratinjau Landing Page Mini';
  }

  if (modal && iframe) {
    if (lang === 'svg' || (!currentPreviewHtml.trim().toLowerCase().startsWith('<!doctype') && !currentPreviewHtml.trim().toLowerCase().startsWith('<html') && currentPreviewHtml.trim().startsWith('<svg'))) {
      iframe.srcdoc = '<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><style>body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:#f8fafc;padding:20px;box-sizing:border-box;}svg{max-width:100%;max-height:85vh;height:auto;box-shadow:0 8px 30px rgba(0,0,0,0.08);border-radius:12px;background:#ffffff;padding:16px;}</style></head><body>' + currentPreviewHtml + '</body></html>';
    } else {
      iframe.srcdoc = currentPreviewHtml;
    }
    modal.style.display = 'flex';
  }
}

// Cross-Origin Blob Download Handler (Bypasses Modern Browser Anchor Restrictions)
async function downloadImageFile(target, explicitName) {
  let url = '';
  let filename = (explicitName || 'mumu-visual').trim();
  if (typeof target === 'string') {
    url = target;
  } else if (target && target.dataset) {
    url = target.dataset.url || '';
    filename = (target.dataset.filename || filename).trim();
  }
  if (!url) return;

  if (!filename.toLowerCase().match(/\.(png|jpg|jpeg|webp|svg)$/)) {
    filename += '.png';
  }

  try {
    const resp = await fetch(url, { mode: 'cors' });
    if (!resp.ok) throw new Error('Fetch failed');
    const blob = await resp.blob();
    const blobUrl = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = blobUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(blobUrl);
  } catch (e) {
    // Fallback: Open in new tab if CORS prevents direct blob stream
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.target = '_blank';
    a.rel = 'noopener';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }
}

## 18. KaTeX LaTeX Mathematical Typesetting Pattern

Extract display and inline math into collision-free placeholders before HTML escaping:

```javascript
function formatMarkdownWithMath(str) {
  // 1. Display Math: $$ ... $$
  const mathBlocks = [];
  str = str.replace(/\$\$([\s\S]+?)\$\$/g, (match, formula) => {
    let rendered = match;
    if (window.katex) {
      try {
        rendered = `<div class="math-display">${window.katex.renderToString(formula.trim(), { displayMode: true, throwOnError: false })}</div>`;
      } catch (_) {
        rendered = `<div class="math-display">$$${escapeHtml(formula.trim())}$$</div>`;
      }
    }
    mathBlocks.push(rendered);
    return ` ___MATHBLOCK_${mathBlocks.length - 1}_END___ `;
  });

  // 2. Inline Math: $ ... $ (excluding simple currency numbers like $10 or $0.0015)
  const inlineMaths = [];
  str = str.replace(/(^|[^\$])\$([^\$\n]+?)\$(?!\$)/g, (match, prefix, formula) => {
    if (/^\d+(\.\d+)?$/.test(formula.trim())) return match;
    let rendered = `$${formula}$`;
    if (window.katex) {
      try {
        rendered = window.katex.renderToString(formula.trim(), { displayMode: false, throwOnError: false });
      } catch (_) {
        rendered = `$${escapeHtml(formula.trim())}$`;
      }
    }
    inlineMaths.push(rendered);
    return `${prefix}___INLINEMATH_${inlineMaths.length - 1}_END___`;
  });

  // Run general markdown parsing (headings, codeblocks, tables, paragraphs)...
  let finalHtml = parseMarkdownBody(str);

  // Re-inject compiled math blocks
  finalHtml = finalHtml.replace(/___MATHBLOCK_(\d+)_END___/g, (_, idx) => mathBlocks[parseInt(idx, 10)]);
  finalHtml = finalHtml.replace(/___INLINEMATH_(\d+)_END___/g, (_, idx) => inlineMaths[parseInt(idx, 10)]);
  return finalHtml;
}
```

## 19. Backend Thinking Effort Calibration & Token Usage Propagation

```javascript
router.post('/chat', async (req, res) => {
  const { message, agent = 'bk', thinking = 'standard' } = req.body || {};
  
  let maxTokens = 1500;
  let temperature = 0.7;
  let thinkingDirective = '';

  if (thinking === 'off') {
    maxTokens = 850;
    temperature = 0.4;
    thinkingDirective = '\n[MODA THINKING: OFF]: Berikan solusi langsung, ringkas, padat.';
  } else if (thinking === 'deep') {
    maxTokens = 2500;
    temperature = 0.7;
    thinkingDirective = '\n[MODA THINKING: MENDALAM]: Lakukan dekomposisi kausal formal, bounds matematis, dan evaluasi trade-off.';
  }

  const response = await fetch('http://127.0.0.1:20128/v1/chat/completions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${apiKey}` },
    body: JSON.stringify({
      model: 'bk',
      messages: [
        { role: 'system', content: basePersona + thinkingDirective },
        ...history,
        { role: 'user', content: message }
      ],
      max_tokens: maxTokens,
      temperature: temperature
    })
  });

  const data = await response.json();
  res.json({
    ok: true,
    reply: data.choices?.[0]?.message?.content,
    tokens: data.usage?.total_tokens || null
  });
});
```

## 20. Universal Clipboard Copy Fallback with Inline Feedback

```javascript
function copyMessageText(btn) {
  const bubble = btn.closest('.assistant-content-wrap').querySelector('.message-bubble');
  if (!bubble) return;
  const text = bubble.innerText;

  const onCopied = () => {
    const originalHtml = btn.innerHTML;
    btn.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg> <span style="color:#10b981;">Tersalin</span>`;
    setTimeout(() => { btn.innerHTML = originalHtml; }, 1800);
  };

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(onCopied).catch(() => {
      // Fallback: Programmatic Textarea for iframes, headless testing & non-secure contexts
      try {
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        onCopied();
      } catch (_) {}
    });
  } else {
    onCopied();
  }
}
```

## 21. Multi-Turn Session State, Clean Titles & Turn-Aware In-Place Regeneration

```javascript
let activeSessionId = null;

function saveCurrentSession(messages) {
  if (!messages || messages.length === 0) return;
  const sessions = JSON.parse(localStorage.getItem('chat_sessions') || '[]');
  
  if (!activeSessionId) {
    activeSessionId = Date.now().toString();
  }

  const firstUser = messages.find(m => m.role === 'user');
  let cleanTitle = 'Percakapan Mumu';
  if (firstUser && firstUser.content) {
    // Strip custom instructions or context tag prefix before slicing title
    const stripped = firstUser.content.replace(/^\[(?:Konteks|Gaya)[^\]]*\]\s*/gim, '').trim();
    cleanTitle = (stripped || firstUser.content).slice(0, 36);
  }

  const existingIdx = sessions.findIndex(s => s.id === activeSessionId);
  const sessionData = {
    id: activeSessionId,
    title: cleanTitle,
    messages: messages
  };

  if (existingIdx >= 0) {
    sessions[existingIdx] = sessionData;
  } else {
    sessions.unshift(sessionData);
  }
  localStorage.setItem('chat_sessions', JSON.stringify(sessions.slice(0, 25)));
}

// In-place turn-aware regeneration (ChatGPT & Claude standard)
async function regenerateResponse(btn) {
  if (isGenerating) return;

  let targetUserPrompt = '';
  if (btn) {
    const row = btn.closest('.message-row.assistant');
    if (row) {
      // Find the user turn immediately preceding this assistant card
      let prev = row.previousElementSibling;
      while (prev && !prev.classList.contains('user')) {
        prev = prev.previousElementSibling;
      }
      if (prev) {
        targetUserPrompt = prev.querySelector('.message-bubble')?.innerText || '';
        // Prune this assistant row and all downstream messages from DOM
        while (row.nextElementSibling) {
          messagesContainer.removeChild(row.nextElementSibling);
        }
        messagesContainer.removeChild(row);

        // Slice conversation state back to that user prompt
        const userIdx = currentConversation.findIndex(m => m.role === 'user' && m.content.trim() === targetUserPrompt.trim());
        if (userIdx !== -1) {
          currentConversation = currentConversation.slice(0, userIdx + 1);
        }
      }
    }
  }

  if (!targetUserPrompt) {
    const userMsgs = currentConversation.filter(m => m.role === 'user');
    if (userMsgs.length === 0) return;
    targetUserPrompt = userMsgs[userMsgs.length - 1].content;

    if (currentConversation.length > 0 && currentConversation[currentConversation.length - 1].role === 'assistant') {
      currentConversation.pop();
      if (messagesContainer.lastElementChild?.classList.contains('assistant')) {
        messagesContainer.removeChild(messagesContainer.lastElementChild);
      }
    }
  }

  await resendPrompt(targetUserPrompt);
}
```

## 22. Live Telemetry & Local Vault Grounding Engine (Express.js)

```javascript
const { execSync } = require('child_process');
const os = require('os');
const path = require('path');
const fs = require('fs');

function getLiveSystemTelemetry() {
  try {
    const totalMem = (os.totalmem() / (1024**3)).toFixed(1);
    const freeMem = (os.freemem() / (1024**3)).toFixed(1);
    const usedMem = (totalMem - freeMem).toFixed(1);
    const load = os.loadavg().map(l => l.toFixed(2)).join(', ');
    let pm2Summary = '';
    try {
      const raw = execSync('pm2 jlist', { encoding: 'utf8', timeout: 1500 });
      const list = JSON.parse(raw);
      const online = list.filter(p => p.pm2_env?.status === 'online').map(p => p.name).slice(0, 15);
      pm2Summary = `Layanan PM2 Online (${online.length}): ${online.join(', ')}`;
    } catch (_) {
      pm2Summary = 'PM2 status tidak dapat dibaca.';
    }
    return `\n[DATA TELEMETRI LIVE VPS SAAT INI (REAL TIME - KUTIP ANGKA INI SECARA AKURAT KE PENGGUNA)]:\n- RAM Fisik: Terpakai ${usedMem} GB / Bebas ${freeMem} GB (Total: ${totalMem} GB)\n- CPU Load Avg: ${load}\n- ${pm2Summary}\n`;
  } catch (_) {
    return '';
  }
}

function findVaultContext(query, vaultDirs = ['/path/to/vault/KNOWLEDGE', '/path/to/vault/BUKU_CATATAN']) {
  if (!query) return '';
  const qClean = query.toLowerCase().replace(/[^a-z0-9\s]/g, ' ').trim();
  const words = qClean.split(/\s+/).filter(w => w.length >= 3 && !['dan', 'yang', 'untuk', 'pada', 'apa', 'ini', 'itu'].includes(w));
  if (words.length === 0) return '';
  
  const matches = [];
  for (const d of vaultDirs) {
    try {
      if (!fs.existsSync(d)) continue;
      const files = fs.readdirSync(d);
      for (const f of files) {
        if (!f.endsWith('.md')) continue;
        const fLower = f.toLowerCase();
        let matchScore = 0;
        for (const w of words) {
          if (fLower.includes(w)) matchScore += 2;
        }
        if (matchScore > 0) {
          matches.push({ file: path.join(d, f), name: f, score: matchScore });
        }
      }
    } catch (_) {}
  }
  if (matches.length === 0) return '';
  matches.sort((a, b) => b.score - a.score);
  const top = matches[0];
  try {
    const content = fs.readFileSync(top.file, 'utf8');
    return `\n[RUJUKAN VAULT OTAK-KODING: ${top.name}]:\n${content.slice(0, 1200)}\n`;
  } catch (_) {
    return '';
  }
}
```

## 23. Multi-Turn Context Forwarding & Persona Normalization

```javascript
router.post('/chat', async (req, res) => {
  const { message, agent = 'bk', thinking = 'standard', context = [] } = req.body || {};

  const lower = (agent + ' ' + message).toLowerCase();
  let systemPersona = 'Kamu adalah asisten AI terpercaya...';

  // Telemetry grounding
  if (lower.includes('status') || lower.includes('ram') || lower.includes('server') || lower.includes('pm2')) {
    systemPersona += '\n' + getLiveSystemTelemetry();
  }

  // Vault knowledge grounding
  if (lower.includes('vault') || lower.includes('catatan') || lower.includes('buku') || lower.includes('knowledge')) {
    const snippet = findVaultContext(message);
    if (snippet) systemPersona += '\n' + snippet;
  }

  // Persona routing: accept both tag ID and @text prefix
  let senderName = 'Mumu';
  if (agent === 'architect' || lower.includes('@architect')) {
    senderName = 'Senior Systems Architect';
    systemPersona += '\nFokus: arsitektur sistem, zero-RAM waste, dan diagram alur.';
  } else if (agent === 'dev' || lower.includes('@dev')) {
    senderName = 'Lead Fullstack Engineer';
    systemPersona += '\nFokus: kode produksi nyata tanpa data mock.';
  }

  // Use caller session context if provided, else fallback to local log
  const history = Array.isArray(context) && context.length > 0 ? context.slice(-8) : getChatHistory().slice(-6);

  const messagesPayload = [
    { role: 'system', content: systemPersona },
    ...history.filter(h => h.role === 'user' || h.role === 'assistant').map(h => ({ role: h.role, content: h.content })),
    { role: 'user', content: message }
  ];

  // Dispatch to LLM...
});
```

## 24. Native Server-Sent Events (SSE) Streaming Pipeline (Express + Vanilla JS)

### A. Backend Route (Express.js)

```javascript
router.post('/chat/stream', express.json(), async (req, res) => {
  const { message, agent = 'bk', thinking = 'standard', context = [] } = req.body || {};
  if (!message || !message.trim()) return res.status(400).json({ ok: false, error: 'Empty message' });

  // 1. Set SSE Headers
  res.setHeader('Content-Type', 'text/event-stream; charset=utf-8');
  res.setHeader('Cache-Control', 'no-cache, no-transform');
  res.setHeader('Connection', 'keep-alive');
  res.setHeader('X-Accel-Buffering', 'no');
  res.flushHeaders?.();

  // 2. Build payload with system persona, grounding & caller context
  const messagesPayload = buildMessagesPayload({ message, agent, thinking, context });

  try {
    const upstreamRes = await fetch('http://127.0.0.1:20128/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
        'Accept': 'text/event-stream'
      },
      body: JSON.stringify({
        model: 'bk',
        stream: true,
        messages: messagesPayload,
        max_tokens: 1800,
        temperature: 0.7
      })
    });

    if (!upstreamRes.ok || !upstreamRes.body) throw new Error(`Upstream HTTP ${upstreamRes.status}`);

    let fullContent = '';
    const reader = upstreamRes.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop(); // keep trailing incomplete line

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || !trimmed.startsWith('data: ')) continue;
        const dataStr = trimmed.slice(6).trim();
        if (dataStr === '[DONE]') break;
        try {
          const parsed = JSON.parse(dataStr);
          const delta = parsed?.choices?.[0]?.delta?.content;
          if (delta) {
            fullContent += delta;
            res.write(`data: ${JSON.stringify({ chunk: delta, sender: 'Mumu' })}\n\n`);
          }
        } catch (_) {}
      }
    }

    const tokenEstimate = Math.max(30, Math.round(fullContent.length / 3.8));
    res.write(`data: ${JSON.stringify({ done: true, content: fullContent.trim(), tokens: tokenEstimate })}\n\n`);
    res.end();
  } catch (err) {
    res.write(`data: ${JSON.stringify({ error: err.message })}\n\n`);
    res.end();
  }
});
```

### B. Frontend Stream Consumer & Kinetic Cursor (Vanilla JS)

```javascript
function createStreamingAssistantRow(sender = 'Mumu') {
  const row = document.createElement('div');
  row.className = 'message-row assistant';
  row.innerHTML = `
    <div class="assistant-content-wrap">
      <div class="message-bubble"><span class="typing-cursor"></span></div>
      <div class="message-actions-bar" style="display: none;">
        <button class="btn-msg-action" onclick="copyMessageText(this)">Salin</button>
        <button class="btn-msg-action" onclick="regenerateLastResponse()">Buat Ulang</button>
        <span class="token-badge"></span>
      </div>
    </div>
  `;
  messagesContainer.appendChild(row);
  const bubble = row.querySelector('.message-bubble');
  const actionsBar = row.querySelector('.message-actions-bar');
  const tokenBadge = row.querySelector('.token-badge');

  return {
    update(text) {
      bubble.innerHTML = formatMarkdown(text) + '<span class="typing-cursor"></span>';
      chatStream.scrollTop = chatStream.scrollHeight;
    },
    finish(text, costInfo) {
      bubble.innerHTML = formatMarkdown(text);
      if (tokenBadge) tokenBadge.textContent = costInfo;
      if (actionsBar) actionsBar.style.display = 'flex';
      chatStream.scrollTop = chatStream.scrollHeight;
    }
  };
}

async function streamPrompt(promptText) {
  abortController = new AbortController();
  updateSendButtonState(true); // morphs send icon into stop button

  try {
    const res = await fetch('/api/studio/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      signal: abortController.signal,
      body: JSON.stringify({
        message: promptText,
        agent: currentModel,
        thinking: currentThinking,
        context: currentConversation.slice(-8)
      })
    });

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let streamedText = '';
    let streamingRow = null;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop();

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed.startsWith('data: ')) continue;
        const data = JSON.parse(trimmed.slice(6));
        if (data.chunk) {
          if (!streamingRow) streamingRow = createStreamingAssistantRow(data.sender);
          streamedText += data.chunk;
          streamingRow.update(streamedText);
        }
        if (data.done) break;
      }
    }

    if (streamingRow) {
      streamingRow.finish(streamedText, `${Math.round(streamedText.length / 4)} token`);
    }
  } catch (err) {
    if (err.name !== 'AbortError') console.error('...[truncated]
```
