/**
 * TimeTravelDebugger - Zero-dependency, bounded state time-travel engine.
 * Author: Bagas Cihuy & Hermes Agent
 */

class TimeTravelDebugger {
  constructor(options = {}) {
    this.maxHistory = options.maxHistory || 50;
    this.storageKey = options.storageKey || null;
    this.subscribers = new Set();
    this.history = [];
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
    listener(this.getState(), this.history[this.cursor], '@@SUBSCRIBE');
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

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { TimeTravelDebugger };
}
