'use strict';
// UIUX-067: Node VM fake DOM unit tests for pending clipboard focus continuity,
// repeated DOM status updates, stale completion rejection, and absent matchMedia fallback.
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert');

const jsCode = fs.readFileSync(path.join(__dirname, 'history_browser.js'), 'utf8');

function createFakeDOM(initialData) {
  const elements = {};
  function makeElement(id, tagName = 'div') {
    const classSet = new Set();
    const el = {
      id,
      tagName,
      textContent: '',
      disabled: false,
      dataset: {},
      children: [],
      style: {},
      attributes: {},
      get className() { return Array.from(classSet).join(' '); },
      set className(val) {
        classSet.clear();
        if (typeof val === 'string') val.trim().split(/\s+/).filter(Boolean).forEach(c => classSet.add(c));
      },
      classList: {
        add(c) { classSet.add(c); },
        remove(c) { classSet.delete(c); },
        contains(c) { return classSet.has(c); }
      },
      listeners: {},
      setAttribute(k, v) { this.attributes[k] = String(v); this[k] = String(v); },
      getAttribute(k) { return this.attributes[k] !== undefined ? this.attributes[k] : (this[k] !== undefined ? String(this[k]) : null); },
      removeAttribute(k) { delete this.attributes[k]; delete this[k]; },
      addEventListener(type, fn) {
        if (!this.listeners[type]) this.listeners[type] = [];
        this.listeners[type].push(fn);
      },
      removeEventListener(type, fn) {
        this.listeners[type] = (this.listeners[type] || []).filter(cb => cb !== fn);
      },
      isConnected: true,
      parentElement: null,
      focus() { doc.activeElement = this; this.dispatchEvent('focus'); },
      blur() { if (doc.activeElement === this) doc.activeElement = null; this.dispatchEvent('blur'); },
      dispatchEvent(type, eventObj = {}) {
        const ev = { preventDefault: () => {}, stopPropagation: () => {}, ...eventObj };
        (this.listeners[type] || []).forEach(fn => fn(ev));
      },
      click() { if (this.disabled) return; this.dispatchEvent('click'); },
      replaceChildren(...nodes) {
        this.children = nodes;
        nodes.forEach(n => { n.parentElement = this; });
        this.textContent = nodes.map(n => n.textContent || '').join(' ');
      },
      appendChild(node) {
        node.parentElement = this;
        this.children.push(node);
      },
      contains(node) {
        let cur = node;
        while (cur) {
          if (cur === this) return true;
          cur = cur.parentElement;
        }
        return false;
      },
      querySelectorAll(selector) {
        const matches = [];
        function walk(n) {
          if (!n || !n.children) return;
          for (const c of n.children) {
            if (selector === '.dag-breadcrumb-item' && c.classList.contains('dag-breadcrumb-item')) matches.push(c);
            if (selector === '.dag-breadcrumb-copy-btn' && c.classList.contains('dag-breadcrumb-copy-btn')) matches.push(c);
            if (selector === '.node-item' && c.classList.contains('node-item')) matches.push(c);
            walk(c);
          }
        }
        walk(this);
        return matches;
      },
      querySelector(selector) {
        let found = null;
        function walk(n) {
          if (found || !n || !n.children) return;
          for (const c of n.children) {
            if (selector === '.dag-breadcrumb-copy-btn' && c.classList.contains('dag-breadcrumb-copy-btn')) { found = c; return; }
            if (selector === '.dag-breadcrumb-item' && c.classList.contains('dag-breadcrumb-item')) { found = c; return; }
            walk(c);
            if (found) return;
          }
        }
        walk(this);
        return found;
      }
    };
    elements[id] = el;
    return el;
  }

  const doc = {
    activeElement: null,
    getElementById(id) { return elements[id] || makeElement(id); },
    createElement(tag) { return makeElement('anon-' + Math.random(), tag); },
    body: makeElement('body', 'body')
  };

  // Pre-create required elements
  makeElement('history-data', 'script');
  elements['history-data'].textContent = JSON.stringify(initialData);
  makeElement('dag-view', 'div');
  elements['dag-view'].scrollTo = () => {};
  elements['dag-view'].scrollLeft = 0;
  elements['dag-view'].clientWidth = 600;
  makeElement('dag-breadcrumbs', 'nav');
  makeElement('dag-search-bar', 'div');
  makeElement('dag-search-input', 'input');
  makeElement('dag-search-count', 'span');
  makeElement('dag-search-clear', 'button');
  makeElement('undo', 'button');
  makeElement('preview', 'pre');
  makeElement('status', 'p');
  makeElement('branches', 'div');

  let timerId = 0;
  const timers = new Map();
  const sandbox = {
    document: doc,
    window: { localStorage: null },
    navigator: {
      clipboard: {
        writeText: () => Promise.resolve()
      }
    },
    setTimeout: (cb) => { const id = ++timerId; timers.set(id, cb); return id; },
    clearTimeout: (id) => { timers.delete(id); },
    console
  };
  sandbox.window.document = doc;
  vm.createContext(sandbox);
  vm.runInContext(jsCode, sandbox);
  return { sandbox, doc, elements };
}

const mockHistory = {
  cursor: 'alpha_child',
  lineage: ['root', 'alpha', 'alpha_child'],
  branch_clusters: { root: '#94A3B8', alpha: '#10B981', alpha_child: '#10B981' },
  branch_roots: { root: 'root', alpha: 'alpha', alpha_child: 'alpha' },
  nodes: {
    root: { parent: null, children: ['alpha'], cells: { A1: 'init' } },
    alpha: { parent: 'root', children: ['alpha_child'], cells: { A1: 'mod' } },
    alpha_child: { parent: 'alpha', children: [], cells: { A1: 'child' } }
  }
};

(() => {
  const { sandbox, doc, elements } = createFakeDOM(mockHistory);
  const api = sandbox.window.historyPreview;
  const statusEl = elements['status'];
  const breadcrumbs = elements['dag-breadcrumbs'];
  const searchInput = elements['dag-search-input'];

  // Test 1: absent matchMedia does not throw and defaults to smooth
  assert.strictEqual(typeof sandbox.window.matchMedia, 'undefined');
  assert.strictEqual(api.prefersReducedMotion(), false);
  api.checkout('alpha');
  assert.strictEqual(api.state().cursor, 'alpha');

  // Test 2: Repeated status updates in DOM
  const copyBtn = breadcrumbs.querySelector('.dag-breadcrumb-copy-btn');
  assert.ok(copyBtn);
  copyBtn.focus();
  assert.strictEqual(doc.activeElement, copyBtn);

  // Controlled writeText
  let deferred = null;
  sandbox.navigator.clipboard.writeText = () => new Promise((resolve, reject) => {
    deferred = { resolve, reject };
  });

  // First copy: pending status
  const p1 = api.copyLineage();
  assert.strictEqual(copyBtn.textContent, 'Menyalin…');
  assert.strictEqual(statusEl.textContent, 'Menyalin silsilah rute ke clipboard…');
  deferred.resolve();

  // Microtask flush
  return p1.then(res1 => {
    assert.strictEqual(res1.success, true);
    assert.strictEqual(copyBtn.textContent, 'Tersalin!');
    assert.strictEqual(statusEl.textContent, 'Silsilah rute berhasil disalin ke clipboard');

    // Repeated copy on same route: pending status then success status again
    const p2 = api.copyLineage();
    assert.strictEqual(copyBtn.textContent, 'Menyalin…');
    assert.strictEqual(statusEl.textContent, 'Menyalin silsilah rute ke clipboard…');
    deferred.resolve();

    return p2.then(res2 => {
      assert.strictEqual(res2.success, true);
      assert.strictEqual(statusEl.textContent, 'Silsilah rute berhasil disalin ke clipboard');

      // Test 3: Tab/search focus while pending -> settlement does not steal focus
      const p3 = api.copyLineage();
      assert.strictEqual(copyBtn.textContent, 'Menyalin…');
      // User moves focus to search input while pending
      searchInput.focus();
      assert.strictEqual(doc.activeElement, searchInput);

      deferred.resolve();
      return p3.then(() => {
        // Settlement occurred, focus must NOT be stolen back to copyBtn!
        assert.strictEqual(doc.activeElement, searchInput);

        // Test 4: Search focus while pending -> refresh does not steal focus & stale completion inert
        const p4 = api.copyLineage();
        searchInput.focus();
        assert.strictEqual(doc.activeElement, searchInput);

        // Refresh called while write pending
        api.refresh();
        const newCopyBtn = breadcrumbs.querySelector('.dag-breadcrumb-copy-btn');
        assert.notStrictEqual(newCopyBtn, copyBtn);
        assert.strictEqual(doc.activeElement, searchInput, 'refresh did not steal focus');

        // Stale promise resolves
        deferred.resolve();
        return p4.then(() => {
          assert.strictEqual(newCopyBtn.textContent, 'Salin Rute', 'stale completion did not mutate button');
          assert.strictEqual(doc.activeElement, searchInput, 'stale completion did not steal focus');

          // Test 5: Refresh focus restoration differential
          // Case 5A: newCopyBtn has focus -> refresh restores focus to replacement
          newCopyBtn.focus();
          assert.strictEqual(doc.activeElement, newCopyBtn);
          api.refresh();
          const repl1 = breadcrumbs.querySelector('.dag-breadcrumb-copy-btn');
          assert.strictEqual(doc.activeElement, repl1, 'focus restored to copy button because old copy button had focus');

          // Case 5B: searchInput has focus -> refresh does NOT restore focus to copy button
          searchInput.focus();
          assert.strictEqual(doc.activeElement, searchInput);
          api.refresh();
          const repl2 = breadcrumbs.querySelector('.dag-breadcrumb-copy-btn');
          assert.strictEqual(doc.activeElement, searchInput, 'focus remained on searchInput');
          assert.notStrictEqual(doc.activeElement, repl2);

          // Test 6: Disposal resets neutral status and stays inert on stale completion
          const p6 = api.copyLineage();
          searchInput.focus();
          api.disposeClipboard();
          assert.strictEqual(repl2.disabled, true);
          assert.ok(statusEl.textContent.startsWith('Versi '));
          assert.strictEqual(doc.activeElement, searchInput);

          deferred.resolve();
          return p6.then(() => {
            assert.strictEqual(repl2.disabled, true);
            assert.ok(statusEl.textContent.startsWith('Versi '));
            assert.strictEqual(doc.activeElement, searchInput);
            console.log('OK: all Node VM clipboard focus and status tests passed');
          });
        });
      });
    });
  });
})().catch(err => {
  console.error(err);
  process.exit(1);
});
