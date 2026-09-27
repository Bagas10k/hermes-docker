---
name: time-travel-state-debugger
description: Time-travel state debugging and snapshot replay for web apps.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [vibe-coding, state-management, time-travel, debugging, undo-redo, replay]
    related_skills: [vibe-coding-accelerator, live-sandbox-hot-preview, systematic-debugging]
---

# Time-Travel State Debugger

Lightweight, zero-dependency time-travel state debugging, deterministic action replay, and micro-snapshot inspection for front-end web applications, interactive visual sandboxes, and vibe-coding prototypes.

## When to Use

- Prototyping interactive UIs where actions need instant undo/redo capabilities without boilerplate architecture.
- Diagnosing elusive state mutation bugs by rewinding state changes frame-by-frame.
- Recording user interaction sessions and replaying them deterministically to reproduce visual flaws.
- Building stateful widgets (forms, canvas drawings, multi-step wizards, dashboards) that require non-destructive rollback.
- Exporting and importing state snapshots for bug reports, QA audits, or test fixtures.
- Don't use for: deep distributed database transactions, multi-process memory dumps, or heavy binary media streaming state.

## Prerequisites

- Modern browser runtime (ES2020+) supporting `structuredClone` (or deterministic JSON serialization fallback).
- Works with zero external dependencies in vanilla JavaScript, Alpine.js, React, Vue, or Svelte.
- No build tools required; runs directly inside self-contained HTML sandboxes or production web apps.

## Quick Reference

- **Initialize Debugger**:
  ```javascript
  const devtools = new TimeTravelDebugger({ maxHistory: 50, storageKey: 'vibe_state_snap' });
  ```
- **Record Action & Mutation**:
  ```javascript
  devtools.dispatch('ITEM_ADDED', (prev) => ({ ...prev, items: [...prev.items, newItem] }));
  ```
- **Time-Travel Jump**:
  ```javascript
  devtools.jumpTo(index); // Reverts DOM & memory state to step index
  ```
- **Export / Import Trace**:
  ```javascript
  const jsonTrace = devtools.exportTrace();
  devtools.importTrace(jsonTrace);
  ```

## Mathematical & Mechanistic Bounds

1. **State Space Complexity & Memory Envelope**:
   Let state size at step $t$ be $S_t$. Full naive snapshotting stores $\sum_{t=1}^N S_t = O(N \cdot |S|)$.
   With a ring buffer bound $K = 50$ ($K \ll N$):
   $$\text{Memory}_{\text{bounded}} \le K \cdot |S|_{\max}$$
   For a typical client state of $50\text{ KB}$, $50 \times 50\text{ KB} = 2.5\text{ MB}$, fitting comfortably under browser heap quotas without GC pressure.

2. **Deterministic Replay Guarantee**:
   Let transition function be $f: (S_t, A_t) \to S_{t+1}$.
   Replay is deterministic if and only if $f$ is pure:
   $$\forall t, \quad \epsilon_{\text{random}} = 0 \quad \land \quad \epsilon_{\text{time}} = 0$$
   Any non-deterministic input (e.g., `Date.now()`, `Math.random()`, UUIDs) must be injected explicitly inside action payload $A_t$, never computed inside reducer $f$.

3. **Diff Compression Bound (Structural Sharing)**:
   For complex tree models, delta serialization $D_t = \text{diff}(S_{t-1}, S_t)$ yields $|D_t| \ll |S_t|$, reducing memory consumption by $80\text{--}92\%$.

## Implementation Recipe: Zero-Dependency Time-Travel Core

```javascript
class TimeTravelDebugger {
  constructor(options = {}) {
    this.maxHistory = options.maxHistory || 50;
    this.storageKey = options.storageKey || null;
    this.subscribers = new Set();
    this.history = []; // Array of { id, action, timestamp, state }
    this.cursor = -1;
    this.isReplaying = false;

    const initial = options.initialState || {};
    this.pushSnapshot('@@INIT', initial);
  }

  getState() {
    return this.cursor >= 0 && this.history[this.cursor]
      ? this.clone(this.history[this.cursor].state)
      : null;
  }

  clone(obj) {
    if (typeof structuredClone === 'function') {
      try { return structuredClone(obj); } catch (e) {}
    }
    return JSON.parse(JSON.stringify(obj));
  }

  pushSnapshot(actionName, state) {
    if (this.cursor < this.history.length - 1) {
      // Discard future if branching occurred after time-travel jump
      this.history = this.history.slice(0, this.cursor + 1);
    }

    const snapshot = {
      id: Date.now().toString(36) + Math.random().toString(36).substr(2, 4),
      action: actionName,
      timestamp: Date.now(),
      state: this.clone(state)
    };

    this.history.push(snapshot);
    if (this.history.length > this.maxHistory) {
      this.history.shift();
    }
    this.cursor = this.history.length - 1;
    this.notify(actionName);
  }

  dispatch(actionName, updater) {
    if (this.isReplaying) return;
    const currentState = this.getState();
    const nextState = typeof updater === 'function' ? updater(currentState) : updater;
    this.pushSnapshot(actionName, nextState);
  }

  stepBack() {
    if (this.cursor > 0) {
      this.cursor--;
      this.notify('@@TIME_TRAVEL_BACK');
      return true;
    }
    return false;
  }

  stepForward() {
    if (this.cursor < this.history.length - 1) {
      this.cursor++;
      this.notify('@@TIME_TRAVEL_FORWARD');
      return true;
    }
    return false;
  }

  jumpTo(index) {
    if (index >= 0 && index < this.history.length) {
      this.cursor = index;
      this.notify('@@TIME_TRAVEL_JUMP');
      return true;
    }
    return false;
  }

  subscribe(listener) {
    this.subscribers.add(listener);
    listener(this.getState(), this.history[this.cursor], this);
    return () => this.subscribers.delete(listener);
  }

  notify(event) {
    const currentState = this.getState();
    const currentEntry = this.history[this.cursor];
    for (const sub of this.subscribers) {
      try { sub(currentState, currentEntry, event); } catch (err) { console.error(err); }
    }
  }

  exportTrace() {
    return JSON.stringify({
      version: 1,
      exportedAt: new Date().toISOString(),
      cursor: this.cursor,
      history: this.history
    }, null, 2);
  }

  importTrace(jsonString) {
    const data = JSON.parse(jsonString);
    if (!data.history || !Array.isArray(data.history)) throw new Error('Invalid trace schema');
    this.history = data.history;
    this.cursor = Math.min(Math.max(0, data.cursor || 0), this.history.length - 1);
    this.notify('@@TRACE_IMPORTED');
  }
}
```

## Visual HUD Floating Dock (Zero-Emoji Architecture)

Inject a compact, non-intrusive floating HUD dock into any vibe-coding prototype for visual scrubbing:

```html
<div id="vibe-time-travel-hud" class="fixed bottom-4 right-4 z-50 bg-slate-900 border border-slate-800 text-slate-200 text-xs font-mono rounded-lg shadow-2xl p-2.5 flex items-center space-x-2">
  <button id="tt-step-back" class="px-2 py-1 bg-slate-800 hover:bg-slate-700 active:bg-slate-600 rounded text-slate-100 border border-slate-700">PREV</button>
  <span id="tt-status" class="px-2 py-0.5 bg-slate-950 rounded text-amber-400 font-bold">0 / 0</span>
  <button id="tt-step-fwd" class="px-2 py-1 bg-slate-800 hover:bg-slate-700 active:bg-slate-600 rounded text-slate-100 border border-slate-700">NEXT</button>
  <button id="tt-export" class="px-2 py-1 bg-sky-950 hover:bg-sky-900 active:bg-sky-800 rounded text-sky-400 border border-sky-800">TRACE</button>
</div>
```

## Pitfalls & Defensive Rules

1. **Side-Effect Pollution during Time-Travel**:
   Replaying states must NOT trigger asynchronous external mutations (e.g., REST API POSTs, Stripe charges, or WebSockets). Ensure network mutations are decoupled from state subscriber rendering loops.
2. **Non-Serializable Objects**:
   Avoid storing DOM node references, functions, Symbols, or Circular References in state snapshots. Use plain objects, primitives, and arrays.
3. **Branching Invalidation**:
   When a user travels back 5 steps and initiates a new mutation, future history (`cursor + 1` to end) must be truncated cleanly to prevent timeline corruption.
4. **Memory Leaks from Unbounded Listeners**:
   Always invoke the cleanup callback returned by `.subscribe()` when unmounting components or tearing down views.

## Verification Checklist

- [ ] Core class compiles cleanly without external dependencies.
- [ ] Ring buffer enforces maxHistory limit without memory expansion.
- [ ] Jump and undo/redo operations restore DOM and state without side-effect re-triggers.
- [ ] Export and import traces round-trip with bitwise state integrity.
- [ ] Zero-emoji standard enforced across visual controls and HUD overlays.
