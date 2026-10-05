const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert');

const htmlPath = path.join(__dirname, 'history_browser.js');
const jsCode = fs.readFileSync(htmlPath, 'utf8');

function createFakeDOM(initialData, svgContent = '', initialStorage = new Map()) {
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
      get className() {
        return Array.from(classSet).join(' ');
      },
      set className(val) {
        classSet.clear();
        if (typeof val === 'string') {
          val.trim().split(/\s+/).filter(Boolean).forEach(c => classSet.add(c));
        }
      },
      classList: {
        classes: classSet,
        add(c) { classSet.add(c); },
        remove(c) { classSet.delete(c); },
        contains(c) { return classSet.has(c); }
      },
      listeners: {},
      setAttribute(k, v) { this.attributes[k] = String(v); this[k] = String(v); },
      getAttribute(k) { return this.attributes[k] !== undefined ? this.attributes[k] : (this[k] !== undefined ? String(this[k]) : null); },
      addEventListener(type, fn) {
        if (!this.listeners[type]) this.listeners[type] = [];
        this.listeners[type].push(fn);
      },
      dispatchEvent(type, eventObj = {}) {
        const ev = { preventDefault: () => {}, ...eventObj };
        (this.listeners[type] || []).forEach(fn => fn(ev));
      },
      click() {
        if (this.disabled) return;
        this.dispatchEvent('click');
      },
      focus(opts) {
        doc.activeElement = this;
        this.dispatchEvent('focus');
      },
      blur() {
        this.dispatchEvent('blur');
      },
      mouseenter() {
        this.dispatchEvent('mouseenter');
      },
      mouseleave() {
        this.dispatchEvent('mouseleave');
      },
      keydown(key) {
        this.dispatchEvent('keydown', { key });
      },
      replaceChildren(...nodes) {
        this.children = nodes;
        this.textContent = nodes.map(n => n.textContent || '').join(' ');
      },
      appendChild(node) {
        this.children.push(node);
        this.textContent = (this.textContent ? this.textContent + ' ' : '') + (node.textContent || '');
      },
      contains(node) {
        return this.children.includes(node) || this === node;
      },
      querySelectorAll(selector) {
        const matches = [];
        function walk(node) {
          if (!node || !node.children) return;
          node.children.forEach(c => {
            if (selector === '.node-item' && c.classList && c.classList.contains('node-item')) matches.push(c);
            else if (selector === '.minimap-node' && c.classList && c.classList.contains('minimap-node')) matches.push(c);
            else if (selector === '.dag-breadcrumb-item' && c.classList && c.classList.contains('dag-breadcrumb-item')) matches.push(c);
            else if (selector === '.dag-breadcrumb-badge' && c.classList && c.classList.contains('dag-breadcrumb-badge')) matches.push(c);
            else if (selector === '.dag-minimap-scale-btn' && c.classList && c.classList.contains('dag-minimap-scale-btn')) matches.push(c);
            walk(c);
          });
        }
        walk(this);
        return matches;
      },
      querySelector(selector) {
        let found = null;
        function walk(node) {
          if (found || !node || !node.children) return;
          for (const c of node.children) {
            if (selector === '.node-circle' && c.classList && c.classList.contains('node-circle')) { found = c; return; }
            if (selector === '.node-label' && c.classList && c.classList.contains('node-label')) { found = c; return; }
            if (selector === '.dag-breadcrumb-badge' && c.classList && c.classList.contains('dag-breadcrumb-badge')) { found = c; return; }
            if (selector === '.dag-breadcrumb-label' && c.classList && c.classList.contains('dag-breadcrumb-label')) { found = c; return; }
            if (selector === '.dag-breadcrumb-copy-btn' && c.classList && c.classList.contains('dag-breadcrumb-copy-btn')) { found = c; return; }
            if (selector === '.dag-minimap-scale-btn' && c.classList && c.classList.contains('dag-minimap-scale-btn')) { found = c; return; }
            walk(c);
            if (found) return;
          }
        }
        walk(this);
        return found;
      }
    };
    return el;
  }

  const doc = {
    activeElement: null,
    getElementById(id) {
      if (!elements[id]) elements[id] = makeElement(id);
      return elements[id];
    },
    createElement(tag) {
      return makeElement(null, tag);
    }
  };

  elements['history-data'] = {
    textContent: JSON.stringify(initialData)
  };
  elements['branches'] = makeElement('branches');
  elements['undo'] = makeElement('undo', 'button');
  elements['status'] = makeElement('status', 'p');
  elements['preview'] = makeElement('preview', 'pre');
  elements['dag-diff-popover'] = makeElement('dag-diff-popover');
  elements['dag-breadcrumbs'] = makeElement('dag-breadcrumbs', 'nav');
  elements['dag-minimap-wrap'] = makeElement('dag-minimap-wrap');
  elements['dag-minimap-status'] = makeElement('dag-minimap-status', 'span');
  elements['dag-minimap-toggle'] = makeElement('dag-minimap-toggle', 'button');
  elements['dag-search-bar'] = makeElement('dag-search-bar');
  elements['dag-search-input'] = makeElement('dag-search-input', 'input');
  elements['dag-search-count'] = makeElement('dag-search-count', 'span');
  elements['dag-search-clear'] = makeElement('dag-search-clear', 'button');
  
  const scaleControls = makeElement('dag-minimap-scale-controls', 'div');
  [1, 1.5, 2].forEach(scaleVal => {
    const sBtn = makeElement(null, 'button');
    sBtn.classList.add('dag-minimap-scale-btn');
    if (scaleVal === 1) sBtn.classList.add('active');
    sBtn.dataset.scale = String(scaleVal);
    sBtn.attributes['data-scale'] = String(scaleVal);
    scaleControls.children.push(sBtn);
  });
  elements['dag-minimap-scale-controls'] = scaleControls;
  
  const minimapFrame = makeElement('minimap-viewport-frame', 'rect');
  minimapFrame.attributes['x'] = '0';
  minimapFrame.attributes['width'] = '180';
  elements['minimap-viewport-frame'] = minimapFrame;

  const dagView = makeElement('dag-view');
  dagView.clientWidth = 400; // Mock container width for auto-centering calculation
  dagView.scrollLeft = 0;
  dagView.scrollTo = function(opts) {
    if (opts && typeof opts.left === 'number') {
      this.scrollLeft = opts.left;
      this.dispatchEvent('scroll');
    }
  };

  const minimapSvg = makeElement('dag-minimap-svg', 'svg');
  minimapSvg.attributes['width'] = '180';
  minimapSvg.attributes['height'] = '90';
  minimapSvg.attributes['data-world-width'] = '800';
  minimapSvg.attributes['data-world-height'] = '200';
  minimapSvg.dataset.worldWidth = '800';
  minimapSvg.dataset.worldHeight = '200';
  minimapSvg.children.push(minimapFrame);
  minimapFrame.parentElement = minimapSvg;

  // Populate fake minimap node items matching initialData
  if (initialData && initialData.nodes) {
    const clusterMap = {
      root: '#94A3B8',
      alpha: '#10B981',
      beta: '#8B5CF6',
      alpha_child: '#10B981'
    };
    Object.keys(initialData.nodes).forEach(nodeId => {
      const mmNode = makeElement(null, 'circle');
      mmNode.classList.add('minimap-node');
      if (nodeId === initialData.cursor) mmNode.classList.add('active');
      mmNode.dataset.node = nodeId;
      const cColor = clusterMap[nodeId] || '#94A3B8';
      mmNode.dataset.clusterColor = cColor;
      mmNode.attributes['data-node'] = nodeId;
      mmNode.attributes['data-cluster-color'] = cColor;
      mmNode.style.fill = (nodeId === initialData.cursor) ? '#38BDF8' : cColor;
      minimapSvg.children.push(mmNode);
    });
  }

  minimapSvg.closest = function(selector) {
    if (selector === 'svg') return minimapSvg;
    return null;
  };
  minimapFrame.closest = function(selector) {
    if (selector === 'svg') return minimapSvg;
    return null;
  };
  elements['dag-minimap-svg'] = minimapSvg;
  dagView.children.push(minimapSvg);
  // Populate fake SVG node items if initialData has nodes
  if (initialData && initialData.nodes) {
    const coordsMap = {
      root: { cx: '58.0', cy: '83.0' },
      alpha: { cx: '178.0', cy: '58.0' },
      beta: { cx: '178.0', cy: '108.0' },
      alpha_child: { cx: '298.0', cy: '58.0' }
    };

    Object.keys(initialData.nodes).forEach(nodeId => {
      const nodeItem = makeElement(null, 'g');
      nodeItem.classList.add('node-item');
      nodeItem.dataset.node = nodeId;
      const coords = coordsMap[nodeId] || { cx: '100.0', cy: '100.0' };
      nodeItem.dataset.cx = coords.cx;
      nodeItem.dataset.cy = coords.cy;
      
      const diffInfo = {
        summary: nodeId === 'root' ? '0' : '+1',
        total_mutations: nodeId === 'root' ? 0 : 1,
        added: nodeId === 'root' ? {} : { A1: 'value_' + nodeId },
        modified: {},
        deleted: {}
      };
      nodeItem.dataset.diffJson = JSON.stringify(diffInfo);
      nodeItem.dataset.summary = diffInfo.summary;
      nodeItem.dataset.mutations = String(diffInfo.total_mutations);

      const circle = makeElement(null, 'circle');
      circle.classList.add('node-circle');
      if (nodeId === initialData.cursor) circle.classList.add('active');
      const label = makeElement(null, 'text');
      label.classList.add('node-label');
      nodeItem.children.push(circle, label);
      dagView.children.push(nodeItem);
    });
  }
  elements['dag-view'] = dagView;

  const winListeners = {};
  const mockStorage = initialStorage;
  const mockLocalStorage = {
    getItem: (key) => mockStorage.has(key) ? mockStorage.get(key) : null,
    setItem: (key, val) => mockStorage.set(key, String(val)),
    removeItem: (key) => mockStorage.delete(key),
    clear: () => mockStorage.clear()
  };

  const mockWindow = {
    addEventListener: (type, cb) => {
      if (!winListeners[type]) winListeners[type] = [];
      winListeners[type].push(cb);
    },
    removeEventListener: (type, cb) => {
      if (winListeners[type]) {
        winListeners[type] = winListeners[type].filter(fn => fn !== cb);
      }
    },
    dispatchEvent: (type, ev = {}) => {
      if (winListeners[type]) {
        winListeners[type].forEach(fn => fn(ev));
      }
    },
    localStorage: mockLocalStorage
  };

  const sandbox = {
    document: doc,
    window: mockWindow,
    Object: Object,
    JSON: JSON,
    Array: Array,
    Math: Math,
    parseFloat: parseFloat,
    setTimeout: (cb, ms) => { if (typeof cb === 'function') cb(); },
    console: console
  };

  vm.createContext(sandbox);
  vm.runInContext(jsCode, sandbox);
  return { sandbox, elements, doc, window: mockWindow };
}

// Test 1: Navigation and status updates
const data1 = {
  cursor: 'root',
  nodes: {
    root: { parent: null, children: ['alpha', 'beta'], cells: { A1: 'base' } },
    alpha: { parent: 'root', children: ['alpha_child'], cells: { A1: 'alpha' } },
    beta: { parent: 'root', children: [], cells: { A1: 'beta' } },
    alpha_child: { parent: 'alpha', children: [], cells: { A1: 'child' } }
  }
};

const dom1 = createFakeDOM(data1);
assert.strictEqual(dom1.elements['undo'].disabled, true);
assert.strictEqual(dom1.elements['branches'].children.length, 2);
assert.ok(dom1.elements['status'].textContent.includes('Versi root'));

// Click branch beta
dom1.elements['branches'].children[1].click();
assert.strictEqual(dom1.sandbox.window.historyPreview.state().cursor, 'beta');
assert.strictEqual(dom1.elements['undo'].disabled, false);
assert.strictEqual(dom1.elements['branches'].children.length, 0);
assert.ok(dom1.elements['status'].textContent.includes('Versi beta'));

// Click undo
dom1.elements['undo'].click();
assert.strictEqual(dom1.sandbox.window.historyPreview.state().cursor, 'root');
assert.strictEqual(dom1.elements['undo'].disabled, true);
// Focus should land back on branch button beta
assert.strictEqual(dom1.doc.activeElement.dataset.branch, 'beta');

// Test 2: SVG Click-to-Checkout interaction
const svgNodeAlpha = dom1.elements['dag-view'].children.find(c => c.dataset.node === 'alpha');
assert.ok(svgNodeAlpha, 'SVG node for alpha must exist in dag-view');
svgNodeAlpha.click();
assert.strictEqual(dom1.sandbox.window.historyPreview.state().cursor, 'alpha');
assert.strictEqual(dom1.elements['undo'].disabled, false);
assert.ok(dom1.elements['status'].textContent.includes('Versi alpha'));

// Test 3: Programmatic window.historyPreview.checkout()
dom1.sandbox.window.historyPreview.checkout('beta');
assert.strictEqual(dom1.sandbox.window.historyPreview.state().cursor, 'beta');
assert.strictEqual(dom1.elements['undo'].disabled, false);

// Test 4: Hover Diff Inspector Popover (UIUX-054)
const popover = dom1.elements['dag-diff-popover'];
assert.strictEqual(popover.classList.contains('visible'), false);

// Mouseenter on alpha node
svgNodeAlpha.mouseenter();
assert.strictEqual(popover.classList.contains('visible'), true);
assert.strictEqual(popover.getAttribute('aria-hidden'), 'false');
assert.ok(popover.textContent.includes('Node: alpha'));
assert.ok(popover.textContent.includes('+ A1: value_alpha'));

// Mouseleave hides popover
svgNodeAlpha.mouseleave();
assert.strictEqual(popover.classList.contains('visible'), false);
assert.strictEqual(popover.getAttribute('aria-hidden'), 'true');

// Focus triggers popover for keyboard accessibility
svgNodeAlpha.focus();
assert.strictEqual(popover.classList.contains('visible'), true);
svgNodeAlpha.blur();
assert.strictEqual(popover.classList.contains('visible'), false);

// Test 5: Arrow Key Spatial Navigation (UIUX-054)
// Starting at alpha (178, 58), ArrowDown should navigate to beta (178, 108)
svgNodeAlpha.focus();
svgNodeAlpha.keydown('ArrowDown');
assert.strictEqual(dom1.doc.activeElement.dataset.node, 'beta');

// From beta (178, 108), ArrowUp should navigate to alpha (178, 58)
const svgNodeBeta = dom1.elements['dag-view'].children.find(c => c.dataset.node === 'beta');
svgNodeBeta.keydown('ArrowUp');
assert.strictEqual(dom1.doc.activeElement.dataset.node, 'alpha');

// From alpha (178, 58), ArrowRight should navigate to alpha_child (298, 58)
svgNodeAlpha.keydown('ArrowRight');
assert.strictEqual(dom1.doc.activeElement.dataset.node, 'alpha_child');

// From alpha_child (298, 58), ArrowLeft should navigate back to alpha (178, 58)
const svgNodeChild = dom1.elements['dag-view'].children.find(c => c.dataset.node === 'alpha_child');
svgNodeChild.keydown('ArrowLeft');
assert.strictEqual(dom1.doc.activeElement.dataset.node, 'alpha');

// Test 6: API window.historyPreview.navigate & popoverFor
dom1.sandbox.window.historyPreview.checkout('root');
const nextNav = dom1.sandbox.window.historyPreview.navigate('ArrowRight');
assert.strictEqual(nextNav, 'alpha'); // root -> alpha on ArrowRight
const popoverText = dom1.sandbox.window.historyPreview.popoverFor('alpha');
assert.ok(popoverText.includes('Node: alpha'));

// Test 7: Breadcrumb Lineage Trail & Viewport Auto-Centering (UIUX-055)
// Check root breadcrumbs
dom1.sandbox.window.historyPreview.checkout('root');
assert.deepEqual(Array.from(dom1.sandbox.window.historyPreview.breadcrumbs()), ['root']);
assert.deepEqual(Array.from(dom1.sandbox.window.historyPreview.lineage('root')), ['root']);
assert.strictEqual(dom1.sandbox.window.historyPreview.viewportScrollLeft(), 0);

// Navigate to deep branch alpha_child
dom1.sandbox.window.historyPreview.checkout('alpha_child');
assert.deepEqual(Array.from(dom1.sandbox.window.historyPreview.breadcrumbs()), ['root', 'alpha', 'alpha_child']);
assert.deepEqual(Array.from(dom1.sandbox.window.historyPreview.lineage('alpha_child')), ['root', 'alpha', 'alpha_child']);

// Check auto-centering scrollLeft: cx=298, clientWidth=400 -> scrollLeft = max(0, 298 - 200) = 98
assert.strictEqual(dom1.sandbox.window.historyPreview.viewportScrollLeft(), 98);

// Click breadcrumb item 'alpha' to jump back
const breadcrumbItems = dom1.elements['dag-breadcrumbs'].children.filter(c => c.classList && c.classList.contains('dag-breadcrumb-item'));
assert.strictEqual(breadcrumbItems.length, 3);
const alphaBreadcrumb = breadcrumbItems.find(b => b.dataset.breadcrumbNode === 'alpha');
assert.ok(alphaBreadcrumb, 'Breadcrumb for alpha must exist');
alphaBreadcrumb.click();

assert.strictEqual(dom1.sandbox.window.historyPreview.state().cursor, 'alpha');
assert.deepEqual(Array.from(dom1.sandbox.window.historyPreview.breadcrumbs()), ['root', 'alpha']);
// cx=178, clientWidth=400 -> scrollLeft = max(0, 178 - 200) = 0
assert.strictEqual(dom1.sandbox.window.historyPreview.viewportScrollLeft(), 0);

// Test 8: Interactive SVG Mini-Map Radar & Drag Viewport Pan (UIUX-056)
// Verify minimap frame bounds and viewport sync at scrollLeft = 0
// mapWidth=180, containerWidth=400, worldWidth=800 -> scaleX = 180 / 800 = 0.225
// frameWidth = 400 * 0.225 = 90.0, frameX = 0
const initialFrame = dom1.sandbox.window.historyPreview.minimapFrameBounds();
assert.ok(initialFrame, 'Minimap frame bounds must be exposed');
assert.strictEqual(initialFrame.x, 0);
assert.strictEqual(initialFrame.width, 90.0);

// Programmatic / drag pan to scrollLeft = 200 -> frameX = 200 * 0.225 = 45.0
dom1.sandbox.window.historyPreview.minimapPan(200);
assert.strictEqual(dom1.sandbox.window.historyPreview.viewportScrollLeft(), 200);
const pannedFrame = dom1.sandbox.window.historyPreview.minimapFrameBounds();
assert.strictEqual(pannedFrame.x, 45.0);

// Test minimap status label updates: containerWidth (400) / worldWidth (800) = 50%
assert.strictEqual(dom1.elements['dag-minimap-status'].textContent, '50%');

// Test 9: Minimap Collapsible Toggle & Keyboard Quick-Jump Navigation (UIUX-057)
// Test Minimap Toggle Collapse/Expand
assert.strictEqual(dom1.sandbox.window.historyPreview.isMinimapCollapsed(), false);
assert.strictEqual(dom1.elements['dag-minimap-wrap'].classList.contains('collapsed'), false);

// Click toggle button to collapse minimap
dom1.elements['dag-minimap-toggle'].click();
assert.strictEqual(dom1.sandbox.window.historyPreview.isMinimapCollapsed(), true);
assert.strictEqual(dom1.elements['dag-minimap-wrap'].classList.contains('collapsed'), true);
assert.strictEqual(dom1.elements['dag-minimap-toggle'].textContent, 'Buka');
assert.strictEqual(dom1.elements['dag-minimap-toggle'].getAttribute('aria-expanded'), 'false');
// Verify localStorage persistence was saved
assert.strictEqual(dom1.sandbox.window.localStorage.getItem('dag_minimap_collapsed'), 'true');

// Toggle again to re-expand
dom1.elements['dag-minimap-toggle'].click();
assert.strictEqual(dom1.sandbox.window.historyPreview.isMinimapCollapsed(), false);
assert.strictEqual(dom1.elements['dag-minimap-wrap'].classList.contains('collapsed'), false);
assert.strictEqual(dom1.elements['dag-minimap-toggle'].textContent, 'Tutup');
assert.strictEqual(dom1.elements['dag-minimap-toggle'].getAttribute('aria-expanded'), 'true');
assert.strictEqual(dom1.sandbox.window.localStorage.getItem('dag_minimap_collapsed'), 'false');

// Programmatic toggleMinimap(force)
dom1.sandbox.window.historyPreview.toggleMinimap(true);
assert.strictEqual(dom1.sandbox.window.historyPreview.isMinimapCollapsed(), true);
assert.strictEqual(dom1.sandbox.window.localStorage.getItem('dag_minimap_collapsed'), 'true');
dom1.sandbox.window.historyPreview.toggleMinimap(false);
assert.strictEqual(dom1.sandbox.window.historyPreview.isMinimapCollapsed(), false);
assert.strictEqual(dom1.sandbox.window.localStorage.getItem('dag_minimap_collapsed'), 'false');

// Test Breadcrumb Jump: Checkout deep node 'alpha_child' (lineage: ['root', 'alpha', 'alpha_child'])
dom1.sandbox.window.historyPreview.checkout('alpha_child');
assert.strictEqual(dom1.sandbox.window.historyPreview.state().cursor, 'alpha_child');

// Jump to 1st ancestor ('root') via breadcrumbJump(1)
const jumped1 = dom1.sandbox.window.historyPreview.breadcrumbJump(1);
assert.strictEqual(jumped1, 'root');
assert.strictEqual(dom1.sandbox.window.historyPreview.state().cursor, 'root');

// Navigate back to alpha_child
dom1.sandbox.window.historyPreview.checkout('alpha_child');
// Jump to 2nd ancestor ('alpha') via breadcrumbJump(2)
const jumped2 = dom1.sandbox.window.historyPreview.breadcrumbJump(2);
assert.strictEqual(jumped2, 'alpha');
assert.strictEqual(dom1.sandbox.window.historyPreview.state().cursor, 'alpha');

// Out of bounds jump returns null and preserves cursor
const invalidJump = dom1.sandbox.window.historyPreview.breadcrumbJump(99);
assert.strictEqual(invalidJump, null);
assert.strictEqual(dom1.sandbox.window.historyPreview.state().cursor, 'alpha');

// Test Alt+Digit keyboard event dispatched on window
dom1.sandbox.window.historyPreview.checkout('alpha_child');
dom1.window.dispatchEvent('keydown', {
  altKey: true,
  ctrlKey: false,
  metaKey: false,
  code: 'Digit1'
});
assert.strictEqual(dom1.sandbox.window.historyPreview.state().cursor, 'root');

// Test 10: Breadcrumb Visual Shortcut Badges & Minimap LocalStorage Persistence (UIUX-058)
// Verify breadcrumbs badges rendered on alpha_child lineage: ['root', 'alpha', 'alpha_child']
dom1.sandbox.window.historyPreview.checkout('alpha_child');
const badges = dom1.sandbox.window.historyPreview.breadcrumbBadges();
assert.deepEqual(badges, ['[1]', '[2]', '[3]']);

// Check DOM breadcrumb items structure
const bcItems = dom1.elements['dag-breadcrumbs'].children.filter(c => c.classList && c.classList.contains('dag-breadcrumb-item'));
assert.strictEqual(bcItems.length, 3);
assert.strictEqual(bcItems[0].dataset.breadcrumbIndex, 0);
assert.strictEqual(bcItems[0].querySelector('.dag-breadcrumb-badge').textContent, '[1]');
assert.strictEqual(bcItems[0].querySelector('.dag-breadcrumb-label').textContent, 'root');
assert.strictEqual(bcItems[1].dataset.breadcrumbIndex, 1);
assert.strictEqual(bcItems[1].querySelector('.dag-breadcrumb-badge').textContent, '[2]');
assert.strictEqual(bcItems[1].querySelector('.dag-breadcrumb-label').textContent, 'alpha');
assert.strictEqual(bcItems[2].dataset.breadcrumbIndex, 2);
assert.strictEqual(bcItems[2].querySelector('.dag-breadcrumb-badge').textContent, '[3]');
assert.strictEqual(bcItems[2].querySelector('.dag-breadcrumb-label').textContent, 'alpha_child');

// Test LocalStorage pre-populated simulation (re-executing with pre-existing collapsed state)
const sharedStorage = new Map();
sharedStorage.set('dag_minimap_collapsed', 'true');
const domPreload = createFakeDOM(data1, '', sharedStorage);
assert.strictEqual(domPreload.sandbox.window.historyPreview.isMinimapCollapsed(), true);
assert.strictEqual(domPreload.elements['dag-minimap-wrap'].classList.contains('collapsed'), true);
assert.strictEqual(domPreload.elements['dag-minimap-toggle'].textContent, 'Buka');
assert.strictEqual(domPreload.elements['dag-minimap-toggle'].getAttribute('aria-expanded'), 'false');

// Test 11: Minimap Scale Preset Multipliers & Breadcrumb Lineage Clipboard Export (UIUX-059)
// 1. Breadcrumb Lineage Clipboard Export
dom1.sandbox.window.historyPreview.checkout('alpha_child');
const copyBtn = dom1.elements['dag-breadcrumbs'].querySelector('.dag-breadcrumb-copy-btn');
assert.ok(copyBtn, 'Copy route button must be present in breadcrumbs bar');
assert.strictEqual(copyBtn.textContent, 'Salin Rute');

const exportedLineage = dom1.sandbox.window.historyPreview.copyLineage();
assert.strictEqual(exportedLineage, 'root > alpha > alpha_child');
assert.ok(copyBtn.textContent === 'Tersalin!' || copyBtn.textContent === 'Salin Rute');

// 2. Minimap Scale Presets (1x, 1.5x, 2x)
assert.strictEqual(dom1.sandbox.window.historyPreview.minimapScale(), 1);
const scaleBtns = dom1.elements['dag-minimap-scale-controls'].querySelectorAll('.dag-minimap-scale-btn');
assert.strictEqual(scaleBtns.length, 3);
assert.strictEqual(scaleBtns[0].classList.contains('active'), true);

// Set scale to 1.5x via API
const newScale15 = dom1.sandbox.window.historyPreview.setMinimapScale(1.5);
assert.strictEqual(newScale15, 1.5);
assert.strictEqual(dom1.sandbox.window.historyPreview.minimapScale(), 1.5);
assert.strictEqual(dom1.sandbox.window.localStorage.getItem('dag_minimap_scale'), '1.5');
assert.strictEqual(scaleBtns[0].classList.contains('active'), false);
assert.strictEqual(scaleBtns[1].classList.contains('active'), true);
assert.strictEqual(scaleBtns[1].getAttribute('aria-pressed'), 'true');

// Check SVG dimensions updated to 180 * 1.5 = 270, 90 * 1.5 = 135
const mmSvg = dom1.elements['dag-minimap-svg'];
assert.strictEqual(mmSvg.getAttribute('width'), '270');
assert.strictEqual(mmSvg.getAttribute('height'), '135');

// Click 2x scale button
scaleBtns[2].click();
assert.strictEqual(dom1.sandbox.window.historyPreview.minimapScale(), 2);
assert.strictEqual(dom1.sandbox.window.localStorage.getItem('dag_minimap_scale'), '2');
assert.strictEqual(scaleBtns[2].classList.contains('active'), true);
assert.strictEqual(mmSvg.getAttribute('width'), '360');
assert.strictEqual(mmSvg.getAttribute('height'), '180');

// Invalid multiplier ignored
const invalidScale = dom1.sandbox.window.historyPreview.setMinimapScale(3.5);
assert.strictEqual(invalidScale, 2);

// Test persistence across reloads: preloading storage with scale 2
const storageScale = new Map();
storageScale.set('dag_minimap_scale', '2');
const domPreloadScale = createFakeDOM(data1, '', storageScale);
assert.strictEqual(domPreloadScale.sandbox.window.historyPreview.minimapScale(), 2);
assert.strictEqual(domPreloadScale.elements['dag-minimap-svg'].getAttribute('width'), '360');
assert.strictEqual(domPreloadScale.elements['dag-minimap-svg'].getAttribute('height'), '180');

// Test 12: Interactive Node Search & Filter Omnibar on Visual DAG Viewer (UIUX-060)
// 1. Initial empty search state
assert.strictEqual(dom1.sandbox.window.historyPreview.searchQuery(), '');
assert.strictEqual(dom1.elements['dag-search-count'].textContent, '');

// 2. Search by exact node ID 'alpha' -> matches 'alpha' and 'alpha_child'
const matchesAlpha = dom1.sandbox.window.historyPreview.search('alpha');
assert.deepEqual(matchesAlpha, ['alpha', 'alpha_child']);
assert.strictEqual(dom1.sandbox.window.historyPreview.searchQuery(), 'alpha');
assert.strictEqual(dom1.elements['dag-search-count'].textContent, '2 simpul');
assert.strictEqual(dom1.elements['dag-search-input'].value, 'alpha');

// Check classList of matched and dimmed node elements in DOM
const allNodeEls = dom1.elements['dag-view'].children.filter(c => c.classList && c.classList.contains('node-item'));
const alphaEl = allNodeEls.find(el => el.dataset.node === 'alpha');
const betaEl = allNodeEls.find(el => el.dataset.node === 'beta');
const childEl = allNodeEls.find(el => el.dataset.node === 'alpha_child');
const rootEl = allNodeEls.find(el => el.dataset.node === 'root');

assert.strictEqual(alphaEl.classList.contains('search-match'), true);
assert.strictEqual(alphaEl.classList.contains('search-dim'), false);
assert.strictEqual(childEl.classList.contains('search-match'), true);
assert.strictEqual(childEl.classList.contains('search-dim'), false);
assert.strictEqual(betaEl.classList.contains('search-match'), false);
assert.strictEqual(betaEl.classList.contains('search-dim'), true);
assert.strictEqual(rootEl.classList.contains('search-match'), false);
assert.strictEqual(rootEl.classList.contains('search-dim'), true);

// 3. Search by mutation value in diffJson ('value_beta') -> matches 'beta'
const matchesBetaVal = dom1.sandbox.window.historyPreview.search('value_beta');
assert.deepEqual(matchesBetaVal, ['beta']);
assert.strictEqual(dom1.elements['dag-search-count'].textContent, '1 simpul');
assert.strictEqual(betaEl.classList.contains('search-match'), true);
assert.strictEqual(betaEl.classList.contains('search-dim'), false);
assert.strictEqual(alphaEl.classList.contains('search-dim'), true);

// 4. Clear search via API
const clearedMatches = dom1.sandbox.window.historyPreview.search('');
assert.deepEqual(clearedMatches, []);
assert.strictEqual(dom1.sandbox.window.historyPreview.searchQuery(), '');
assert.strictEqual(dom1.elements['dag-search-count'].textContent, '');
assert.strictEqual(alphaEl.classList.contains('search-match'), false);
assert.strictEqual(alphaEl.classList.contains('search-dim'), false);
assert.strictEqual(betaEl.classList.contains('search-match'), false);
assert.strictEqual(betaEl.classList.contains('search-dim'), false);

// 5. Test Clear button click
dom1.sandbox.window.historyPreview.search('root');
assert.strictEqual(dom1.sandbox.window.historyPreview.searchQuery(), 'root');
dom1.elements['dag-search-clear'].click();
assert.strictEqual(dom1.sandbox.window.historyPreview.searchQuery(), '');
assert.strictEqual(dom1.elements['dag-search-count'].textContent, '');

// 6. Test Escape key on search input
dom1.sandbox.window.historyPreview.search('alpha');
assert.strictEqual(dom1.sandbox.window.historyPreview.searchQuery(), 'alpha');
dom1.elements['dag-search-input'].dispatchEvent('keydown', { key: 'Escape' });
assert.strictEqual(dom1.sandbox.window.historyPreview.searchQuery(), '');

// Test 13: Search Match Indicators & Color-Coded Branch Clustering on Minimap Radar (UIUX-061)
// 1. Color-coded branch clusters and styles
const mmNodes = dom1.elements['dag-minimap-svg'].querySelectorAll('.minimap-node');
assert.strictEqual(mmNodes.length, 4);

const mmRoot = mmNodes.find(n => n.dataset.node === 'root');
const mmAlpha = mmNodes.find(n => n.dataset.node === 'alpha');
const mmBeta = mmNodes.find(n => n.dataset.node === 'beta');
const mmChild = mmNodes.find(n => n.dataset.node === 'alpha_child');

assert.strictEqual(mmRoot.dataset.clusterColor, '#94A3B8');
assert.strictEqual(mmAlpha.dataset.clusterColor, '#10B981');
assert.strictEqual(mmBeta.dataset.clusterColor, '#8B5CF6');
assert.strictEqual(mmChild.dataset.clusterColor, '#10B981');

// Isolate this scenario from the preceding navigation scenarios.
dom1.sandbox.window.historyPreview.checkout('root');
// When cursor is at root, mmRoot is active with #38BDF8
assert.strictEqual(mmRoot.classList.contains('active'), true);
assert.strictEqual(mmRoot.style.fill, '#38BDF8');
assert.strictEqual(mmAlpha.classList.contains('active'), false);
assert.strictEqual(mmAlpha.style.fill, '#10B981');

// Checkout to beta: active cursor moves to mmBeta
dom1.sandbox.window.historyPreview.checkout('beta');
assert.strictEqual(mmBeta.classList.contains('active'), true);
assert.strictEqual(mmBeta.style.fill, '#38BDF8');
assert.strictEqual(mmRoot.classList.contains('active'), false);
assert.strictEqual(mmRoot.style.fill, '#94A3B8');

// 2. Search match indicators on minimap radar
// Search for 'alpha' -> matches alpha and alpha_child
dom1.sandbox.window.historyPreview.search('alpha');
assert.strictEqual(mmAlpha.classList.contains('search-match'), true);
assert.strictEqual(mmAlpha.classList.contains('search-dim'), false);
assert.strictEqual(mmChild.classList.contains('search-match'), true);
assert.strictEqual(mmChild.classList.contains('search-dim'), false);
assert.strictEqual(mmBeta.classList.contains('search-match'), false);
assert.strictEqual(mmBeta.classList.contains('search-dim'), true);
assert.strictEqual(mmRoot.classList.contains('search-match'), false);
assert.strictEqual(mmRoot.classList.contains('search-dim'), true);

// Clear search -> removes search-match and search-dim from minimap nodes
dom1.sandbox.window.historyPreview.search('');
assert.strictEqual(mmAlpha.classList.contains('search-match'), false);
assert.strictEqual(mmAlpha.classList.contains('search-dim'), false);
assert.strictEqual(mmBeta.classList.contains('search-match'), false);
assert.strictEqual(mmBeta.classList.contains('search-dim'), false);

console.log('OK: all Node DOM browser history unit checks passed (including hover diff inspector, spatial arrow navigation, breadcrumbs, auto-centering, minimap radar, collapsible quick-jump navigation, visual shortcut badges, localStorage persistence, scale presets, clipboard export, search omnibar & minimap search/clustering indicators)');
