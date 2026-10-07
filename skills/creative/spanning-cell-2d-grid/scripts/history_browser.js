'use strict';
(() => {
  // Trusted Python export only; never hydrate arbitrary remote JSON here.
  const history = JSON.parse(document.getElementById('history-data').textContent);
  const branches = document.getElementById('branches');
  const undo = document.getElementById('undo');
  const status = document.getElementById('status');
  const preview = document.getElementById('preview');
  const dagView = document.getElementById('dag-view');
  const popover = document.getElementById('dag-diff-popover');
  const breadcrumbsBar = document.getElementById('dag-breadcrumbs');
  const minimapWrap = document.getElementById('dag-minimap-wrap');
  const minimapFrame = document.getElementById('minimap-viewport-frame');
  const minimapStatus = document.getElementById('dag-minimap-status');
  const minimapToggle = document.getElementById('dag-minimap-toggle');
  const minimapScaleControls = document.getElementById('dag-minimap-scale-controls');
  const searchInput = document.getElementById('dag-search-input');
  const searchCount = document.getElementById('dag-search-count');
  const searchClear = document.getElementById('dag-search-clear');
  let cursor = history.cursor;
  let activeSearchQuery = '';
  let isDraggingMinimap = false;
  let minimapDisposed = false;
  let minimapObserver = null;
  const minimapListeners = [];

  function listenMinimap(target, type, callback) {
    const guarded = (event) => { if (!minimapDisposed) callback(event); };
    target.addEventListener(type, guarded);
    minimapListeners.push([target, type, guarded]);
  }

  // Minimap only: history/search/shortcuts/popover remain live. No remount.
  function disposeMinimap() {
    if (minimapDisposed) return false;
    minimapDisposed = true;
    isDraggingMinimap = false;
    if (minimapObserver) minimapObserver.disconnect();
    minimapObserver = null;
    for (const [target, type, callback] of minimapListeners) {
      target.removeEventListener(type, callback);
    }
    minimapListeners.length = 0;
    return true;
  }
  const MINIMAP_STORAGE_KEY = 'dag_minimap_collapsed';
  const MINIMAP_SCALE_STORAGE_KEY = 'dag_minimap_scale';
  let minimapScale = (() => {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        const val = parseFloat(window.localStorage.getItem(MINIMAP_SCALE_STORAGE_KEY));
        if (val === 1 || val === 1.5 || val === 2) return val;
      }
    } catch (_) {}
    return 1;
  })();
  let isMinimapCollapsed = (() => {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        return window.localStorage.getItem(MINIMAP_STORAGE_KEY) === 'true';
      }
    } catch (_) {}
    return false;
  })();

  function setMinimapScale(multiplier) {
    if (minimapDisposed) return minimapScale;
    const val = parseFloat(multiplier);
    if (val !== 1 && val !== 1.5 && val !== 2) return minimapScale;
    minimapScale = val;
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        window.localStorage.setItem(MINIMAP_SCALE_STORAGE_KEY, String(minimapScale));
      }
    } catch (_) {}
    
    // Update active class on scale buttons
    if (minimapScaleControls) {
      const btns = minimapScaleControls.querySelectorAll('.dag-minimap-scale-btn');
      btns.forEach(btn => {
        const btnScale = parseFloat(btn.dataset.scale);
        const isActive = (btnScale === minimapScale);
        if (isActive) {
          btn.classList.add('active');
          btn.setAttribute('aria-pressed', 'true');
        } else {
          btn.classList.remove('active');
          btn.setAttribute('aria-pressed', 'false');
        }
      });
    }

    // Apply scale to radar container and SVG
    const baseW = 180;
    const baseH = 90;
    const scaledW = Math.round(baseW * minimapScale);
    const scaledH = Math.round(baseH * minimapScale);
    
    const mmFrame = document.getElementById('minimap-viewport-frame') || minimapFrame;
    const minimapSvg = mmFrame ? (typeof mmFrame.closest === 'function' ? mmFrame.closest('svg') : (mmFrame.parentElement || (dagView && dagView.querySelector ? dagView.querySelector('svg.dag-minimap-svg') : null))) : null;
    if (minimapSvg) {
      minimapSvg.setAttribute('width', String(scaledW));
      minimapSvg.setAttribute('height', String(scaledH));
      minimapSvg.style.width = `${scaledW}px`;
      minimapSvg.style.height = 'auto';
    }
    syncMinimapViewport();
    return minimapScale;
  }

  function setupMinimapScaleControls() {
    if (!minimapScaleControls) return;
    const btns = minimapScaleControls.querySelectorAll('.dag-minimap-scale-btn');
    btns.forEach(btn => {
      listenMinimap(btn, 'click', (e) => {
        if (e && typeof e.stopPropagation === 'function') e.stopPropagation();
        const targetScale = parseFloat(btn.dataset.scale);
        if (!isNaN(targetScale)) {
          setMinimapScale(targetScale);
        }
      });
    });
    // Apply loaded scale preset
    setMinimapScale(minimapScale);
  }

  let clipboardDisposed = false;
  let clipboardRequest = null;
  let clipboardTimer = null;
  let clipboardButton = null;
  let clipboardClick = null;

  function invalidateClipboard() {
    clipboardRequest = null;
    if (clipboardTimer !== null) clearTimeout(clipboardTimer);
    clipboardTimer = null;
  }

  // Clipboard-only ownership; pending OS writes cannot be cancelled.
  function disposeClipboard() {
    if (clipboardDisposed) return false;
    clipboardDisposed = true;
    invalidateClipboard();
    if (clipboardButton) {
      clipboardButton.removeEventListener('click', clipboardClick);
      clipboardButton.disabled = true;
      clipboardButton.textContent = 'Salin Rute';
      clipboardButton.classList.remove('copied');
    }
    return true;
  }

  async function copyLineageToClipboard() {
    const formatted = computeLineagePath(cursor).join(' > ');
    if (clipboardDisposed) return {text: formatted, success: false};
    invalidateClipboard();
    const request = clipboardRequest = {};
    const button = clipboardButton;
    const owns = () => !clipboardDisposed && clipboardRequest === request &&
      clipboardButton === button && button && breadcrumbsBar.contains(button);
    if (owns()) {
      button.textContent = 'Menyalin…';
      button.classList.remove('copied');
    }
    let success = false;
    try {
      if (typeof navigator !== 'undefined' && navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
        await navigator.clipboard.writeText(formatted);
        success = true;
      } else if (typeof document.execCommand === 'function') {
        const active = document.activeElement;
        const ta = document.createElement('textarea');
        try {
          ta.value = formatted;
          ta.style.position = 'fixed';
          ta.style.opacity = '0';
          document.body.appendChild(ta);
          ta.select();
          success = document.execCommand('copy') === true;
        } finally {
          ta.remove();
          if (active && active.isConnected) active.focus({preventScroll: true});
        }
      }
    } catch (_) { success = false; }
    if (owns()) {
      button.textContent = success ? 'Tersalin!' : 'Gagal menyalin';
      if (success) button.classList.add('copied');
      clipboardTimer = setTimeout(() => {
        if (!owns()) return;
        clipboardTimer = null;
        clipboardRequest = null;
        button.textContent = 'Salin Rute';
        button.classList.remove('copied');
      }, 1500);
    }
    return {text: formatted, success};
  }

  function toggleMinimap(forceCollapse = null) {
    if (minimapDisposed || !minimapWrap) return isMinimapCollapsed;
    isMinimapCollapsed = (forceCollapse !== null) ? Boolean(forceCollapse) : !isMinimapCollapsed;
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        window.localStorage.setItem(MINIMAP_STORAGE_KEY, isMinimapCollapsed ? 'true' : 'false');
      }
    } catch (_) {}
    if (isMinimapCollapsed) {
      minimapWrap.classList.add('collapsed');
      if (minimapToggle) {
        minimapToggle.textContent = 'Buka';
        minimapToggle.setAttribute('aria-expanded', 'false');
      }
    } else {
      minimapWrap.classList.remove('collapsed');
      if (minimapToggle) {
        minimapToggle.textContent = 'Tutup';
        minimapToggle.setAttribute('aria-expanded', 'true');
      }
      syncMinimapViewport();
    }
    return isMinimapCollapsed;
  }

  function setupMinimapToggle() {
    if (!minimapToggle) return;
    // Apply initial persisted collapsed state to DOM if loaded from localStorage
    if (isMinimapCollapsed) {
      if (minimapWrap) minimapWrap.classList.add('collapsed');
      minimapToggle.textContent = 'Buka';
      minimapToggle.setAttribute('aria-expanded', 'false');
    }
    listenMinimap(minimapToggle, 'click', (e) => {
      if (e && typeof e.stopPropagation === 'function') {
        e.stopPropagation();
      }
      toggleMinimap();
    });
  }

  function setupBreadcrumbShortcuts() {
    if (typeof window.addEventListener !== 'function') return;
    window.addEventListener('keydown', (e) => {
      // Alt + Digit1..Digit9: Jump to N-th breadcrumb ancestor (1-indexed)
      if (e && e.altKey && !e.ctrlKey && !e.metaKey && e.code && e.code.startsWith('Digit')) {
        const digit = parseInt(e.code.replace('Digit', ''), 10);
        if (!isNaN(digit) && digit >= 1) {
          const lineage = computeLineagePath(cursor);
          const targetIndex = digit - 1;
          if (targetIndex < lineage.length) {
            if (typeof e.preventDefault === 'function') {
              e.preventDefault();
            }
            const targetId = lineage[targetIndex];
            if (targetId && cursor !== targetId) {
              cursor = targetId;
              draw(true);
            }
          }
        }
      }
    });
  }

  function syncMinimapViewport() {
    if (minimapDisposed) return;
    const mmFrame = document.getElementById('minimap-viewport-frame') || minimapFrame;
    if (!dagView || !mmFrame) return;
    const minimapSvg = (typeof mmFrame.closest === 'function' ? mmFrame.closest('svg') : null) || mmFrame.parentElement || (dagView.querySelector ? dagView.querySelector('svg.dag-minimap-svg') : null);
    if (!minimapSvg) return;
    const worldWidth = parseFloat(minimapSvg.dataset ? minimapSvg.dataset.worldWidth : minimapSvg.getAttribute('data-world-width')) || 300;
    // Frame attributes are viewBox units, never scaled CSS pixels.
    const mapWidth = parseFloat((minimapSvg.getAttribute('viewBox') || '0 0 180 90').split(/\s+/)[2]);
    const scaleX = mapWidth / worldWidth;

    const containerWidth = dagView.clientWidth || 400;
    const scrollLeft = dagView.scrollLeft || 0;

    const frameWidth = Math.min(mapWidth, containerWidth * scaleX);
    const maxFrameX = Math.max(0, mapWidth - frameWidth);
    const frameX = maxFrameX > 0 ? Math.max(0, Math.min(maxFrameX, scrollLeft * scaleX)) : 0;

    mmFrame.setAttribute('x', frameX.toFixed(1));
    mmFrame.setAttribute('width', frameWidth.toFixed(1));
    // SVGAnimatedLength properties are read-only; attributes are authoritative.

    if (minimapStatus) {
      const pct = worldWidth > 0 ? Math.min(100, Math.round((containerWidth / worldWidth) * 100)) : 100;
      minimapStatus.textContent = `${pct}%`;
    }
  }

  function setupMinimapDragPan() {
    if (!minimapFrame || !dagView) return;
    const minimapSvg = minimapFrame.closest ? minimapFrame.closest('svg') : (minimapFrame.parentElement || null);
    if (!minimapSvg) return;

    function handlePan(clientX) {
      if (minimapDisposed) return;
      const rect = (typeof minimapSvg.getBoundingClientRect === 'function') 
        ? minimapSvg.getBoundingClientRect() 
        : { left: 0, width: parseFloat(minimapSvg.getAttribute('width')) || 180 };
      const mapWidth = rect.width || 180;
      const worldWidth = parseFloat(minimapSvg.dataset.worldWidth) || 300;
      const containerWidth = dagView.clientWidth || 400;
      const scaleX = mapWidth / worldWidth;

      const clickX = Math.max(0, Math.min(mapWidth, clientX - rect.left));
      const frameWidth = Math.min(mapWidth, containerWidth * scaleX);
      // Center frame at clickX
      const targetFrameX = Math.max(0, Math.min(mapWidth - frameWidth, clickX - frameWidth / 2));
      const targetScrollLeft = targetFrameX / scaleX;

      if (typeof dagView.scrollTo === 'function') {
        dagView.scrollTo({ left: targetScrollLeft, behavior: 'auto' });
      } else {
        dagView.scrollLeft = targetScrollLeft;
      }
      syncMinimapViewport();
    }

    listenMinimap(minimapSvg, 'mousedown', (e) => {
      if (e.button !== 0) return;
      e.preventDefault();
      isDraggingMinimap = true;
      handlePan(e.clientX || 0);
    });

    if (typeof window.addEventListener === 'function') {
      listenMinimap(window, 'mousemove', (e) => {
        if (isDraggingMinimap) {
          handlePan(e.clientX || 0);
        }
      });

      listenMinimap(window, 'blur', () => { isDraggingMinimap = false; });
      listenMinimap(window, 'resize', syncMinimapViewport);
      listenMinimap(window, 'mouseup', () => {
        isDraggingMinimap = false;
      });
    }

    listenMinimap(dagView, 'scroll', () => {
      if (!isDraggingMinimap) {
        syncMinimapViewport();
      }
    });
    if (typeof ResizeObserver === 'function') {
      minimapObserver = new ResizeObserver(syncMinimapViewport);
      minimapObserver.observe(dagView);
    }
  }

  function computeLineagePath(targetId) {
    if (!targetId || !history.nodes[targetId]) return [];
    const path = [];
    let curr = targetId;
    while (curr && history.nodes[curr]) {
      path.push(curr);
      curr = history.nodes[curr].parent;
    }
    path.reverse();
    return path;
  }

  function renderBreadcrumbs(activeId) {
    invalidateClipboard();
    if (clipboardButton) clipboardButton.removeEventListener('click', clipboardClick);
    clipboardButton = null;
    if (!breadcrumbsBar) return;
    const lineage = computeLineagePath(activeId);
    if (!lineage.length) {
      breadcrumbsBar.replaceChildren();
      return;
    }

    const items = [];
    lineage.forEach((nodeId, idx) => {
      if (idx > 0) {
        const sep = document.createElement('span');
        sep.className = 'dag-breadcrumb-sep';
        sep.textContent = '>';
        items.push(sep);
      }
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'dag-breadcrumb-item' + (nodeId === activeId ? ' active' : '');
      btn.dataset.breadcrumbNode = nodeId;
      btn.dataset.breadcrumbIndex = idx;

      // Add numeric shortcut badge [N] for first 9 ancestors (Alt+1..Alt+9)
      if (idx < 9) {
        const badge = document.createElement('span');
        badge.className = 'dag-breadcrumb-badge';
        badge.textContent = `[${idx + 1}]`;
        badge.title = `Pintasan keyboard: Alt+${idx + 1}`;
        btn.appendChild(badge);
      }

      const label = document.createElement('span');
      label.className = 'dag-breadcrumb-label';
      label.textContent = nodeId;
      btn.appendChild(label);

      btn.setAttribute('aria-label', `Pindah ke simpul silsilah ${nodeId} (Alt+${idx + 1})` + (nodeId === activeId ? ' (aktif)' : ''));
      btn.addEventListener('click', () => {
        if (cursor !== nodeId) {
          cursor = nodeId;
          draw(true);
        }
      });
      items.push(btn);
    });

    // Add Copy Lineage button at the end of breadcrumbs bar
    const copyBtn = document.createElement('button');
    copyBtn.type = 'button';
    copyBtn.className = 'dag-breadcrumb-copy-btn';
    copyBtn.textContent = 'Salin Rute';
    copyBtn.title = 'Salin jejak silsilah rute ke clipboard';
    copyBtn.setAttribute('aria-label', 'Salin seluruh jejak silsilah rute ke clipboard');
    copyBtn.disabled = clipboardDisposed;
    clipboardButton = copyBtn;
    clipboardClick = (e) => {
      if (e && typeof e.stopPropagation === 'function') e.stopPropagation();
      copyLineageToClipboard();
    };
    if (!clipboardDisposed) copyBtn.addEventListener('click', clipboardClick);
    items.push(copyBtn);

    breadcrumbsBar.replaceChildren(...items);
  }

  function autoCenterViewport(activeId) {
    if (!dagView || !activeId) return;
    const nodeItems = dagView.querySelectorAll('.node-item');
    const targetItem = Array.from(nodeItems).find(it => it.dataset.node === activeId);
    if (!targetItem) return;

    const cx = parseFloat(targetItem.dataset.cx) || 0;
    const containerWidth = dagView.clientWidth || 600;
    const targetScrollLeft = Math.max(0, cx - containerWidth / 2);

    if (typeof dagView.scrollTo === 'function') {
      dagView.scrollTo({ left: targetScrollLeft, behavior: 'smooth' });
    } else {
      dagView.scrollLeft = targetScrollLeft;
    }
  }

  function updateDagSelection(activeId) {
    if (!dagView) return;
    const nodeItems = dagView.querySelectorAll('.node-item');
    nodeItems.forEach(item => {
      const id = item.dataset.node;
      const isCur = (id === activeId);
      const circle = item.querySelector('.node-circle');
      const text = item.querySelector('.node-label');
      if (circle) {
        if (isCur) {
          circle.classList.add('active');
          circle.classList.remove('path');
        } else {
          circle.classList.remove('active');
        }
      }
      if (text) {
        if (isCur) text.classList.add('active');
        else text.classList.remove('active');
      }
    });

    if (minimapDisposed) return;
    // Synchronize minimap active cursor dot & cluster color
    const mmFrame = document.getElementById('minimap-viewport-frame') || minimapFrame;
    const minimapSvg = mmFrame ? (typeof mmFrame.closest === 'function' ? mmFrame.closest('svg') : (mmFrame.parentElement || (dagView && dagView.querySelector ? dagView.querySelector('svg.dag-minimap-svg') : null))) : null;
    if (minimapSvg && minimapSvg.querySelectorAll) {
      const mmNodes = minimapSvg.querySelectorAll('.minimap-node');
      mmNodes.forEach(mmNode => {
        const nid = mmNode.dataset ? mmNode.dataset.node : mmNode.getAttribute('data-node');
        const isCur = (nid === activeId);
        if (isCur) {
          mmNode.classList.add('active');
          mmNode.style.fill = '#38BDF8';
        } else {
          mmNode.classList.remove('active');
          const clusterColor = (mmNode.dataset && mmNode.dataset.clusterColor) || mmNode.getAttribute('data-cluster-color') || '#94A3B8';
          mmNode.style.fill = clusterColor;
        }
      });
    }
  }

  function showDiffPopover(item) {
    if (!popover || !item) return;
    const rawDiff = item.dataset.diffJson;
    const nodeId = item.dataset.node;
    if (!rawDiff) return;

    let diff;
    try {
      diff = JSON.parse(rawDiff);
    } catch (_) {
      return;
    }

    const titleDiv = document.createElement('div');
    titleDiv.className = 'diff-popover-title';
    titleDiv.textContent = `Node: ${nodeId} (${diff.summary || '0'})`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'diff-popover-content';

    let hasItems = false;
    const maxEntries = 6;
    let count = 0;

    if (diff.added) {
      for (const [k, v] of Object.entries(diff.added)) {
        if (count >= maxEntries) break;
        const line = document.createElement('div');
        line.className = 'diff-item-added';
        line.textContent = `+ ${k}: ${v}`;
        contentDiv.appendChild(line);
        count++;
        hasItems = true;
      }
    }
    if (diff.modified) {
      for (const [k, info] of Object.entries(diff.modified)) {
        if (count >= maxEntries) break;
        const line = document.createElement('div');
        line.className = 'diff-item-modified';
        line.textContent = `~ ${k}: ${info.old} -> ${info.new}`;
        contentDiv.appendChild(line);
        count++;
        hasItems = true;
      }
    }
    if (diff.deleted) {
      for (const [k, v] of Object.entries(diff.deleted)) {
        if (count >= maxEntries) break;
        const line = document.createElement('div');
        line.className = 'diff-item-deleted';
        line.textContent = `- ${k} (was ${v})`;
        contentDiv.appendChild(line);
        count++;
        hasItems = true;
      }
    }

    const total = diff.total_mutations || 0;
    if (total > count) {
      const more = document.createElement('div');
      more.className = 'diff-item-empty';
      more.textContent = `... and ${total - count} more mutations`;
      contentDiv.appendChild(more);
    } else if (!hasItems) {
      const empty = document.createElement('div');
      empty.className = 'diff-item-empty';
      empty.textContent = 'Root revision (no parent mutations)';
      contentDiv.appendChild(empty);
    }

    popover.replaceChildren(titleDiv, contentDiv);
    popover.classList.add('visible');
    popover.setAttribute('aria-hidden', 'false');

    // Position popover relative to dagView container
    const cx = parseFloat(item.dataset.cx) || 0;
    const cy = parseFloat(item.dataset.cy) || 0;
    popover.style.left = `${cx + 25}px`;
    popover.style.top = `${Math.max(10, cy - 25)}px`;
  }

  function hideDiffPopover() {
    if (!popover) return;
    popover.classList.remove('visible');
    popover.setAttribute('aria-hidden', 'true');
    popover.replaceChildren();
  }

  function findSpatialNeighbor(currentId, direction) {
    if (!dagView || !currentId) return null;
    const nodeItems = Array.from(dagView.querySelectorAll('.node-item'));
    const currentItem = nodeItems.find(it => it.dataset.node === currentId);
    if (!currentItem) return null;

    const cx = parseFloat(currentItem.dataset.cx) || 0;
    const cy = parseFloat(currentItem.dataset.cy) || 0;

    const candidates = [];
    nodeItems.forEach(item => {
      const nid = item.dataset.node;
      if (nid === currentId) return;
      const x = parseFloat(item.dataset.cx) || 0;
      const y = parseFloat(item.dataset.cy) || 0;
      const dx = x - cx;
      const dy = y - cy;

      if (direction === 'ArrowRight') {
        if (dx > 5) {
          candidates.push({ dist: dx + 1.5 * Math.abs(dy), node: item });
        }
      } else if (direction === 'ArrowLeft') {
        if (dx < -5) {
          candidates.push({ dist: Math.abs(dx) + 1.5 * Math.abs(dy), node: item });
        }
      } else if (direction === 'ArrowDown') {
        if (dy > 5) {
          candidates.push({ dist: dy + 1.5 * Math.abs(dx), node: item });
        }
      } else if (direction === 'ArrowUp') {
        if (dy < -5) {
          candidates.push({ dist: Math.abs(dy) + 1.5 * Math.abs(dx), node: item });
        }
      }
    });

    if (!candidates.length) return null;
    candidates.sort((a, b) => a.dist - b.dist);
    return candidates[0].node;
  }

  function setupDagInteractiveHandlers() {
    if (!dagView) return;
    const nodeItems = dagView.querySelectorAll('.node-item');
    nodeItems.forEach(item => {
      const id = item.dataset.node;
      if (!id || !history.nodes[id]) return;

      // Click to checkout
      item.addEventListener('click', (e) => {
        e.preventDefault();
        if (cursor !== id) {
          cursor = id;
          draw(true);
        }
      });

      // Hover diff popover
      item.addEventListener('mouseenter', () => {
        showDiffPopover(item);
      });
      item.addEventListener('mouseleave', () => {
        hideDiffPopover();
      });

      // Focus / blur diff popover for keyboard accessibility
      item.addEventListener('focus', () => {
        showDiffPopover(item);
      });
      item.addEventListener('blur', () => {
        hideDiffPopover();
      });

      // Keyboard handling: Enter/Space to checkout, Arrow keys for spatial navigation
      item.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          if (cursor !== id) {
            cursor = id;
            draw(true);
          }
        } else if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
          e.preventDefault();
          const targetItem = findSpatialNeighbor(id, e.key);
          if (targetItem) {
            targetItem.focus({ preventScroll: true });
          }
        }
      });
    });
  }

  function draw(focus = false, preferred = null) {
    const node = history.nodes[cursor];
    undo.disabled = node.parent === null;
    status.textContent = `Versi ${cursor}. ${node.children.length} cabang lanjutan.`;
    preview.textContent = JSON.stringify(node.cells, null, 2);
    updateDagSelection(cursor);
    renderBreadcrumbs(cursor);
    autoCenterViewport(cursor);
    syncMinimapViewport();
    const buttons = node.children.map(id => {
      const button = document.createElement('button');
      button.type = 'button';
      button.dataset.branch = id;
      button.textContent = `Buka cabang ${id}`;
      button.addEventListener('click', () => { cursor = id; draw(true); });
      return button;
    });
    branches.replaceChildren(...buttons);
    if (!buttons.length) branches.textContent = 'Tidak ada cabang lanjutan.';
    if (focus) {
      const target = buttons.find(b => b.dataset.branch === preferred) || buttons[0] || undo;
      if (!target.disabled) target.focus({preventScroll: true});
    }
  }

  undo.addEventListener('click', () => {
    const previous = cursor;
    const parent = history.nodes[cursor].parent;
    if (parent !== null) { cursor = parent; draw(true, previous); }
  });

  function searchNodes(query) {
    activeSearchQuery = (typeof query === 'string') ? query.trim() : '';
    if (!dagView) return [];
    const nodeItems = dagView.querySelectorAll('.node-item');
    const mmFrame = document.getElementById('minimap-viewport-frame') || minimapFrame;
    const minimapSvg = mmFrame ? (typeof mmFrame.closest === 'function' ? mmFrame.closest('svg') : (mmFrame.parentElement || (dagView && dagView.querySelector ? dagView.querySelector('svg.dag-minimap-svg') : null))) : null;
    const minimapNodes = !minimapDisposed && minimapSvg && minimapSvg.querySelectorAll ? minimapSvg.querySelectorAll('.minimap-node') : [];

    if (!activeSearchQuery) {
      // Clear search highlights and dimming
      nodeItems.forEach(item => {
        item.classList.remove('search-match');
        item.classList.remove('search-dim');
      });
      if (minimapNodes && minimapNodes.length) {
        minimapNodes.forEach(mmNode => {
          mmNode.classList.remove('search-match');
          mmNode.classList.remove('search-dim');
        });
      }
      if (searchCount) searchCount.textContent = '';
      if (searchInput && searchInput.value !== '') searchInput.value = '';
      return [];
    }

    const q = activeSearchQuery.toLowerCase();
    const matchedNodes = [];

    nodeItems.forEach(item => {
      const id = item.dataset.node || '';
      const rawDiff = item.dataset.diffJson || '';
      let isMatch = id.toLowerCase().includes(q);

      if (!isMatch && rawDiff) {
        try {
          const diff = JSON.parse(rawDiff);
          if (diff.summary && diff.summary.toLowerCase().includes(q)) isMatch = true;
          if (!isMatch && diff.added) {
            for (const [k, v] of Object.entries(diff.added)) {
              if (k.toLowerCase().includes(q) || String(v).toLowerCase().includes(q)) { isMatch = true; break; }
            }
          }
          if (!isMatch && diff.modified) {
            for (const [k, info] of Object.entries(diff.modified)) {
              if (k.toLowerCase().includes(q) || String(info.old).toLowerCase().includes(q) || String(info.new).toLowerCase().includes(q)) { isMatch = true; break; }
            }
          }
          if (!isMatch && diff.deleted) {
            for (const [k, v] of Object.entries(diff.deleted)) {
              if (k.toLowerCase().includes(q) || String(v).toLowerCase().includes(q)) { isMatch = true; break; }
            }
          }
        } catch (_) {}
      }

      if (isMatch) {
        item.classList.add('search-match');
        item.classList.remove('search-dim');
        matchedNodes.push(id);
      } else {
        item.classList.remove('search-match');
        item.classList.add('search-dim');
      }
    });

    // Synchronize minimap radar node indicators
    if (minimapNodes && minimapNodes.length) {
      const matchSet = new Set(matchedNodes);
      minimapNodes.forEach(mmNode => {
        const nid = mmNode.dataset ? mmNode.dataset.node : mmNode.getAttribute('data-node');
        if (nid && matchSet.has(nid)) {
          mmNode.classList.add('search-match');
          mmNode.classList.remove('search-dim');
        } else {
          mmNode.classList.remove('search-match');
          mmNode.classList.add('search-dim');
        }
      });
    }

    if (searchCount) {
      searchCount.textContent = `${matchedNodes.length} simpul`;
    }
    if (searchInput && searchInput.value !== activeSearchQuery) {
      searchInput.value = activeSearchQuery;
    }

    // Auto-focus and center camera to the first matched node
    if (matchedNodes.length > 0) {
      autoCenterViewport(matchedNodes[0]);
    }

    return matchedNodes;
  }

  function setupDagSearchControls() {
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        searchNodes(e && e.target ? e.target.value : searchInput.value);
      });
      searchInput.addEventListener('keydown', (e) => {
        if (e && e.key === 'Escape') {
          searchNodes('');
          if (typeof searchInput.blur === 'function') searchInput.blur();
        }
      });
    }
    if (searchClear) {
      searchClear.addEventListener('click', () => {
        searchNodes('');
      });
    }
  }

  // Wire SVG interactive handlers on initial load
  setupDagInteractiveHandlers();
  setupMinimapDragPan();
  setupMinimapToggle();
  setupMinimapScaleControls();
  setupBreadcrumbShortcuts();
  setupDagSearchControls();

  // Native buttons provide Tab, Shift+Tab, Enter and Space; no tree role.
  window.historyPreview = Object.freeze({
    refresh: () => {
      const active = document.activeElement;
      const owned = branches.contains(active);
      draw(owned, owned ? active.dataset.branch : null);
    },
    checkout: (id) => {
      if (history.nodes[id]) {
        cursor = id;
        draw(true);
      }
    },
    navigate: (direction) => {
      const targetItem = findSpatialNeighbor(cursor, direction);
      if (targetItem) {
        const id = targetItem.dataset.node;
        if (id && history.nodes[id]) {
          cursor = id;
          draw(true);
          targetItem.focus({ preventScroll: true });
          return id;
        }
      }
      return null;
    },
    popoverFor: (id) => {
      const item = dagView ? Array.from(dagView.querySelectorAll('.node-item')).find(it => it.dataset.node === id) : null;
      if (item) {
        showDiffPopover(item);
        return popover ? popover.textContent : null;
      }
      return null;
    },
    lineage: (id) => computeLineagePath(id || cursor),
    breadcrumbs: () => breadcrumbsBar ? Array.from(breadcrumbsBar.querySelectorAll('.dag-breadcrumb-item')).map(b => {
      const lbl = b.querySelector('.dag-breadcrumb-label');
      return lbl ? lbl.textContent : b.textContent;
    }) : [],
    breadcrumbBadges: () => breadcrumbsBar ? Array.from(breadcrumbsBar.querySelectorAll('.dag-breadcrumb-badge')).map(b => b.textContent) : [],
    breadcrumbJump: (indexOrDigit) => {
      const lineage = computeLineagePath(cursor);
      // If 1-indexed digit passed
      const idx = (typeof indexOrDigit === 'number' && indexOrDigit >= 1) ? indexOrDigit - 1 : indexOrDigit;
      if (idx >= 0 && idx < lineage.length) {
        const targetId = lineage[idx];
        if (targetId && cursor !== targetId) {
          cursor = targetId;
          draw(true);
          return targetId;
        }
      }
      return null;
    },
    viewportScrollLeft: () => dagView ? dagView.scrollLeft : 0,
    minimapFrameBounds: () => {
      const mmFrame = document.getElementById('minimap-viewport-frame') || minimapFrame;
      if (!mmFrame) return null;
      const xVal = mmFrame.getAttribute('x') !== null ? mmFrame.getAttribute('x') : mmFrame.x;
      const wVal = mmFrame.getAttribute('width') !== null ? mmFrame.getAttribute('width') : mmFrame.width;
      return {
        x: parseFloat(xVal) || 0,
        width: parseFloat(wVal) || 0
      };
    },
    // Disposed minimap APIs are inert; read APIs retain the last values.
    disposeMinimap,
    minimapPan: (scrollLeft) => {
      if (!minimapDisposed && dagView) {
        if (typeof dagView.scrollTo === 'function') {
          dagView.scrollTo({ left: scrollLeft, behavior: 'auto' });
        } else {
          dagView.scrollLeft = scrollLeft;
        }
        dagView.scrollLeft = scrollLeft;
        syncMinimapViewport();
      }
    },
    toggleMinimap: (force) => toggleMinimap(force),
    isMinimapCollapsed: () => isMinimapCollapsed,
    minimapScale: () => minimapScale,
    setMinimapScale: (multiplier) => setMinimapScale(multiplier),
    disposeClipboard,
    copyLineage: () => copyLineageToClipboard(),
    search: (query) => searchNodes(query),
    searchQuery: () => activeSearchQuery,
    state: () => ({cursor, cells: {...history.nodes[cursor].cells}})
  });
  draw();
})();
