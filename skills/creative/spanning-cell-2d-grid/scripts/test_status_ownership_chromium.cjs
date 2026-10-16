'use strict';
// UIUX-074: Dynamic status ownership during pending clipboard checkout and stale reset.
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const {execFileSync, spawnSync} = require('node:child_process');
const http = require('node:http');
const path = require('node:path');
const fs = require('node:fs');

const fixture = JSON.parse(execFileSync('python3', ['-B', path.join(__dirname, 'dynamic_status_fixture.py')], {encoding: 'utf8'}));
const output = path.join(__dirname, '../references/uiux-074-browser.json');
const evidence = {
  target: 'UIUX-074',
  browser: null,
  records: [],
  negativeControls: {},
  errors: [],
  pass: false
};

const INITIAL_ID = 'feat/virtualized-2d-grid-with-asymmetric-spans-and-history-c98f820b784913c98b671a5392812d4a7536901234567890abcdef';
const TARGET_ID = 'cabang-rekonsiliasi-jejak-audit-terdistribusi-skala-2026';

async function frames(page, count = 3) {
  await page.evaluate(async (n) => {
    for (let i = 0; i < n; i++) await new Promise(requestAnimationFrame);
  }, count);
}

async function setupPage(page, origin, meta, fault) {
  await page.goto(origin);
  await page.bringToFront();
  await page.evaluate(({scale, initialId, fault}) => {
    window.INITIAL_ID = initialId; window.fault = fault; window.scale = scale;
    window.phase = 'setup';
    window.mutationTrace = [];
    window.mutationSeq = 0;
    window.eventTrace = [];
    window.eventSeq = 0;
    window.timerEvidence = [];
    window.pendingCopyList = [];
    window.writeCalls = 0;

    // Font scaling
    window.fontBaseline = [document.body, ...document.querySelectorAll('main, main *')]
      .filter(e => e instanceof HTMLElement).map(e => [e, parseFloat(getComputedStyle(e).fontSize)]);
    for (const [el, size] of window.fontBaseline) el.style.fontSize = size * scale + 'px';

    // Preserve CSS-font magnification on nodes created by checkout, not just initial nodes.
    window.fontExpectations = {};
    const fontStyle = document.createElement('style');
    for (const selector of ['.dag-breadcrumb-copy-btn','.dag-breadcrumb-item','.dag-breadcrumb-label','.dag-breadcrumb-badge','#status']) {
      const size = parseFloat(getComputedStyle(document.querySelector(selector)).fontSize);
      window.fontExpectations[selector] = size;
      fontStyle.textContent += `${selector}{font-size:${size}px !important}`;
    }
    document.head.append(fontStyle);
    window.buttonTrace = [];
    const buttonObserver = new MutationObserver(rows => {
      for(let i=0;i<rows.length;i++) {
        const m=rows[i], el=m.target;
        if(!el.classList?.contains('dag-breadcrumb-copy-btn')) continue;
        let field='text', value;
        if(m.type==='attributes') {
          field=m.attributeName;
          const next=rows.slice(i+1).find(n=>n.target===el && n.type==='attributes' && n.attributeName===field);
          value=next ? next.oldValue : el.getAttribute(field);
        } else value=[...m.addedNodes].map(n=>n.textContent).join('');
        window.buttonTrace.push({seq:window.buttonTrace.length+1,phase:window.phase,
          observedTime:performance.now(),field,value});
      }
    });
    buttonObserver.observe(document.getElementById('dag-breadcrumbs'), {subtree:true, childList:true,
      attributes:true, attributeOldValue:true, attributeFilter:['class','aria-label','disabled']});

    // Observe focus events
    const desc = el => el ? {
      tag: el.tagName?.toLowerCase() || null,
      id: el.id || null,
      dataBreadcrumbNode: el.getAttribute?.('data-breadcrumb-node') || null,
      isInitialCopyBtn: el === window.initialCopyButton,
      isCopyBtn: el.classList?.contains?.('dag-breadcrumb-copy-btn') || false
    } : null;

    for (const type of ['focusin', 'focusout']) {
      document.addEventListener(type, e => {
        window.eventTrace.push({
          seq: ++window.eventSeq,
          phase: window.phase,
          type,
          target: desc(e.target),
          relatedTarget: desc(e.relatedTarget),
          timeStamp: e.timeStamp,
          observedTime: performance.now()
        });
      }, true);
    }

    // Observe continuous text mutations on status and shadow reserve
    const statusEl = document.getElementById('status');
    const reserveEl = document.getElementById('dag-status-reserve-idle');
    const obs = new MutationObserver(mutations => {
      for (let i=0; i<mutations.length; i++) {
        const m=mutations[i];
        const next=mutations.slice(i+1).find(n=>n.type==='characterData' && n.target===m.target);
        let newText = m.type === 'characterData' ? (next ? next.oldValue : m.target.textContent) : Array.from(m.addedNodes).map(n => n.textContent).join('');
        if (!newText && m.target.textContent) newText = m.target.textContent;
        window.mutationTrace.push({
          seq: ++window.mutationSeq,
          phase: window.phase,
          targetId: m.target.id || (m.target.parentElement ? m.target.parentElement.id : null),
          oldText: m.oldValue,
          newText: newText,
          observedTime: performance.now()
        });
      }
    });
    if (statusEl) obs.observe(statusEl, {childList: true, characterData: true, subtree: true, characterDataOldValue: true});
    if (reserveEl) obs.observe(reserveEl, {childList: true, characterData: true, subtree: true, characterDataOldValue: true});

    // Native timer tracking
    const realSetTimeout = window.setTimeout.bind(window);
    const realClearTimeout = window.clearTimeout.bind(window);
    let timerSeq = 0;
    window.setTimeout = (cb, ms, ...args) => {
      const tid = ++timerSeq;
      const tRec = {
        id: tid,
        delay: ms,
        registeredAt: performance.now(),
        clearedAt: null,
        firedAt: null,
        calls: 0,
        cancelled: false
      };
      window.timerEvidence.push(tRec);
      const h = realSetTimeout(() => {
        tRec.firedAt = performance.now();
        tRec.calls++;
        cb(...args);
      }, fault === 'timerEarlyFire' && ms === 1500 ? 300 : ms);
      tRec.handle = h;
      return h;
    };
    window.clearTimeout = (h) => {
      for (const t of window.timerEvidence) {
        if (t.handle === h && !t.clearedAt) {
          t.clearedAt = performance.now();
          t.cancelled = true;
        }
      }
      if(fault !== 'staleTimerExecution') return realClearTimeout(h);
    };

    // Save initial button reference for tracking disowned nodes
    window.initialCopyButton = document.querySelector('.dag-breadcrumb-copy-btn');

    // Clipboard mock with deferred promise handles
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: {
        writeText: (text) => {
          window.writeCalls++;
          return new Promise((resolve, reject) => {
            window.pendingCopyList.push({resolve, reject, text, settled: false});
          });
        }
      }
    });
  }, {...meta, initialId: INITIAL_ID, fault});

  // Focus the initial copy button
  await page.locator('.dag-breadcrumb-copy-btn').focus();
  await frames(page);
}

async function samplePhase(page, phaseName) {
  return await page.evaluate((phase) => {
    const curBtn = document.querySelector('.dag-breadcrumb-copy-btn');
    const statusEl = document.getElementById('status');
    const reserveEl = document.getElementById('dag-status-reserve-idle');
    const region = document.querySelector('.dag-status-region');
    const active = document.activeElement;

    const textFit = el => {
      if (!el) return false;
      const s = getComputedStyle(el), r = el.getBoundingClientRect();
      const range = document.createRange(); range.selectNodeContents(el);
      return !['hidden', 'clip'].includes(s.overflowX) && !['hidden', 'clip'].includes(s.overflowY)
        && s.visibility === 'visible' && s.textOverflow !== 'ellipsis'
        && [...range.getClientRects()].every(t => t.left >= r.left - 1 && t.right <= r.right + 1 && t.top >= r.top - 1 && t.bottom <= r.bottom + 1);
    };

    const breadcrumb = document.querySelector('.dag-breadcrumb-item.active');

    return {
      phase,
      cursor: window.historyPreview ? window.historyPreview.state().cursor : null,
      statusText: statusEl ? statusEl.textContent : '',
      reservationText: reserveEl ? reserveEl.textContent : '',
      buttonText: curBtn ? curBtn.textContent : '',
      buttonDisabled: curBtn ? curBtn.disabled : true,
      copied: curBtn ? curBtn.classList.contains('copied') : false,
      activeElementMatchesCurrentButton: active === curBtn,
      activeElement: active ? {
        tag: active.tagName?.toLowerCase() || null,
        id: active.id || null,
        dataBreadcrumbNode: active.getAttribute?.('data-breadcrumb-node') || null,
        isInitialCopyBtn: active === window.initialCopyButton,
        isCopyBtn: active.classList?.contains?.('dag-breadcrumb-copy-btn') || false
      } : null,
      statusHeight: region ? region.getBoundingClientRect().height : 0,
      statusClientWidth: statusEl ? statusEl.clientWidth : 0,
      statusScrollWidth: statusEl ? statusEl.scrollWidth : 0,
      containerWidth: region ? region.clientWidth : 0,
      statusTextFits: textFit(statusEl),
      breadcrumbTextFits: textFit(breadcrumb),
      activeRect: (()=>{const r=active.getBoundingClientRect();return {left:r.left,top:r.top,right:r.right,bottom:r.bottom};})(),
      scroll: {x:scrollX,y:scrollY},
      eventSeq: window.eventSeq, mutationSeq: window.mutationSeq, buttonSeq: window.buttonTrace.length,
      sameInitialButton: curBtn === window.initialCopyButton,
      initialButtonConnected: window.initialCopyButton.isConnected,
      currentButtonConnected: curBtn?.isConnected === true,
      fontScaleVerified: Object.entries(window.fontExpectations).every(([s,size]) =>
        [...document.querySelectorAll(s)].every(el=>Math.abs(parseFloat(getComputedStyle(el).fontSize)-size)<.1)),
      checkpointTime: performance.now()
    };
  }, phaseName);
}

async function runScenario(page, origin, meta, fault = null) {
  const {scenario} = meta;
  await setupPage(page, origin, meta, fault);

  const phases = {};

  // Phase 1: initial
  await page.evaluate(() => window.phase = 'initial');
  phases.initial = await samplePhase(page, 'initial');

  // Phase 2: pending (initiate copy on initial cursor)
  await page.evaluate(() => window.phase = 'pending');
  await page.evaluate(() => { window.historyPreview.copyLineage(); });
  await frames(page);
  phases.pending = await samplePhase(page, 'pending');

  // Scenario branching for checkout/dispose & settlement
  if (scenario === 'pendingCheckoutSuccess' || scenario === 'pendingCheckoutFailure') {
    // Phase 3: checkout to TARGET_ID while copy is pending
    await page.evaluate((tId) => {
      window.phase = 'checkout';
      window.historyPreview.checkout(window.fault === 'wrongCursorOwnership' ? 'root' : tId);
    }, TARGET_ID);
    await frames(page);
    phases.checkout = await samplePhase(page, 'checkout');

    // Phase 4: settled (settle old pending promise)
    await page.evaluate(() => window.phase = 'settled');
    await page.evaluate((outcome) => {
      const p = window.pendingCopyList[0];
      if (p) {
        p.settled = true;
        if (outcome === 'success') p.resolve();
        else p.reject(new Error('controlled denial'));
      }
    }, scenario === 'pendingCheckoutSuccess' ? 'success' : 'failure');

    // Negative fault injections
    if (fault === 'staleStatusWrite') {
      await page.evaluate(() => {
        document.getElementById('status').textContent = 'Silsilah rute berhasil disalin ke clipboard';
      });
    }
    if (fault === 'staleShadowWrite') {
      await page.evaluate((id) => {
        document.getElementById('dag-status-reserve-idle').textContent = `Versi ${id}. 0 cabang lanjutan.`;
      }, INITIAL_ID);
    }
    if (fault === 'transientStaleWrite') {
      await page.evaluate(() => {
        const s = document.getElementById('status');
        const orig = s.textContent;
        s.textContent = 'Silsilah rute berhasil disalin ke clipboard';
        s.textContent = orig;
      });
    }
    if (fault === 'staleFocusTheft') {
      await page.evaluate(() => {
        if (window.initialCopyButton) {
          document.body.appendChild(window.initialCopyButton);
          window.initialCopyButton.focus({preventScroll: true});
        }
      });
    }
    if (fault === 'transientFocusStealReturn') {
      await page.evaluate(() => {
        const cur = document.activeElement;
        if (window.initialCopyButton) {
          document.body.appendChild(window.initialCopyButton);
          window.initialCopyButton.focus({preventScroll: true});
          if (cur) cur.focus({preventScroll: true});
          window.initialCopyButton.remove();
        }
      });
    }
    if (fault === 'disownedButtonActive') {
      await page.evaluate(() => {
        const curBtn = document.querySelector('.dag-breadcrumb-copy-btn');
        if (curBtn) curBtn.classList.add('copied');
      });
    }

    await frames(page);
    phases.settled = await samplePhase(page, 'settled');

    // Phase 5: completed (observe that status remains stable)
    await page.evaluate(() => window.phase = 'completed');
    await page.waitForTimeout(100);
    await frames(page);
    phases.completed = await samplePhase(page, 'completed');

  } else if (scenario === 'settledCheckoutReset') {
    // Settle copy on initial revision first
    await page.evaluate(() => {
      const p = window.pendingCopyList[0];
      if (p) { p.settled = true; p.resolve(); }
    });
    // Wait for button to say 'Tersalin!'
    await page.waitForFunction(() => document.querySelector('.dag-breadcrumb-copy-btn')?.textContent === 'Tersalin!');

    // Phase 3: checkout before 1500ms reset deadline
    await page.evaluate((tId) => {
      window.phase = 'checkout';
      window.historyPreview.checkout(window.fault === 'wrongCursorOwnership' ? 'root' : tId);
    }, TARGET_ID);
    await frames(page);
    phases.checkout = await samplePhase(page, 'checkout');

    // Phase 4: settled snapshot
    await page.evaluate(() => window.phase = 'settled');
    phases.settled = await samplePhase(page, 'settled');


    // Phase 5: completed — wait out full 1600ms native deadline
    await page.evaluate(() => window.phase = 'completed');
    await page.waitForTimeout(1600);
    await frames(page);
    phases.completed = await samplePhase(page, 'completed');

  } else if (scenario === 'settledDisposeReset') {
    // Settle copy on initial revision first
    await page.evaluate(() => {
      const p = window.pendingCopyList[0];
      if (p) { p.settled = true; p.resolve(); }
    });
    await page.waitForFunction(() => document.querySelector('.dag-breadcrumb-copy-btn')?.textContent === 'Tersalin!');

    // Phase 3: dispose clipboard before 1500ms reset deadline
    await page.evaluate(() => {
      window.phase = 'checkout';
      window.historyPreview.disposeClipboard();
    });
    await frames(page);
    phases.checkout = await samplePhase(page, 'checkout');

    // Phase 4: settled snapshot
    await page.evaluate(() => window.phase = 'settled');
    phases.settled = await samplePhase(page, 'settled');

    // Phase 5: completed — wait out full 1600ms native deadline
    await page.evaluate(() => window.phase = 'completed');
    await page.waitForTimeout(1600);
    await frames(page);
    phases.completed = await samplePhase(page, 'completed');

  } else if (scenario === 'pipelinedRequest') {
    // Checkout to TARGET_ID while req1 is pending
    await page.evaluate((tId) => {
      window.phase = 'checkout';
      window.historyPreview.checkout(window.fault === 'wrongCursorOwnership' ? 'root' : tId);
    }, TARGET_ID);
    await frames(page);
    phases.checkout = await samplePhase(page, 'checkout');

    // Trigger req2 on the new revision
    await page.evaluate(() => {
      window.historyPreview.copyLineage();
    });
    await frames(page);

    // Phase 4: settle old req1 while req2 is still pending
    await page.evaluate(() => window.phase = 'settled');
    await page.evaluate(() => {
      const req1 = window.pendingCopyList[0];
      if (req1) { req1.settled = true; req1.resolve(); }
    });

    if (fault === 'pipelinedContamination') {
      await page.evaluate(() => {
        const btn = document.querySelector('.dag-breadcrumb-copy-btn');
        if (btn) btn.textContent = 'Salin Rute';
      });
    }

    await frames(page);
    phases.settled = await samplePhase(page, 'settled');

    // Phase 5: settle req2 and observe its 1500ms timer
    await page.evaluate(() => window.phase = 'completed');
    await page.evaluate(() => {
      const req2 = window.pendingCopyList[1];
      if (req2) { req2.settled = true; req2.resolve(); }
    });
    await page.waitForFunction(() => document.querySelector('.dag-breadcrumb-copy-btn')?.textContent === 'Tersalin!');

    // Native timer is unmodified except the explicit early-fire negative control.
    await page.waitForFunction(() => document.querySelector('.dag-breadcrumb-copy-btn')?.textContent === 'Salin Rute', null, {timeout: 3000});

    await frames(page);
    phases.completed = await samplePhase(page, 'completed');

  } else if (scenario === 'pendingDispose') {
    // Dispose while req1 is pending
    await page.evaluate(() => {
      window.phase = 'checkout';
      window.historyPreview.disposeClipboard();
    });
    await frames(page);
    phases.checkout = await samplePhase(page, 'checkout');

    // Settle old req1
    await page.evaluate(() => window.phase = 'settled');
    await page.evaluate(() => {
      const req1 = window.pendingCopyList[0];
      if (req1) { req1.settled = true; req1.resolve(); }
    });
    await frames(page);
    phases.settled = await samplePhase(page, 'settled');

    await page.evaluate(() => window.phase = 'completed');
    await page.waitForTimeout(100);
    await frames(page);
    phases.completed = await samplePhase(page, 'completed');
  }

  const mutationTrace = await page.evaluate(() => window.mutationTrace);
  const eventTrace = await page.evaluate(() => window.eventTrace);
  const timers = await page.evaluate(() => window.timerEvidence);

  return {
    scenario,
    viewport: meta.viewport,
    scale: meta.scale,
    initialCursor: INITIAL_ID,
    targetCursor: TARGET_ID,
    phases,
    mutationTrace,
    eventTrace,
    timers,
    buttonTrace: await page.evaluate(() => window.buttonTrace),
    passed: true
  };
}

(async () => {
  const server = http.createServer((req, res) => {
    res.writeHead(200, {'Content-Type': 'text/html; charset=utf-8'});
    res.end(fixture.html);
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  let browser;
  try {
    browser = await chromium.launch({headless: true});
    evidence.browser = browser.version();
    const origin = `http://127.0.0.1:${server.address().port}`;

    const scenarios = [
      'pendingCheckoutSuccess',
      'pendingCheckoutFailure',
      'settledCheckoutReset',
      'settledDisposeReset',
      'pipelinedRequest',
      'pendingDispose'
    ];

    // Positive matrix: 6 scenarios x 3 viewports x 2 scales = 36 records
    for (const viewport of [320, 390, 768]) {
      const ctx = await browser.newContext({
        viewport: {width: viewport, height: 900},
        reducedMotion: 'reduce'
      });
      const page = await ctx.newPage();
      page.on('pageerror', e => evidence.errors.push(String(e)));

      for (const scale of [1, 2]) {
        for (const scenario of scenarios) {
          evidence.records.push(await runScenario(page, origin, {scenario, viewport, scale}));
        }
      }
      await ctx.close();
    }

    // Negative controls: 10 controls
    const negFaults = [
      'staleStatusWrite',
      'staleShadowWrite',
      'transientStaleWrite',
      'staleFocusTheft',
      'transientFocusStealReturn',
      'staleTimerExecution',
      'disownedButtonActive',
      'pipelinedContamination',
      'wrongCursorOwnership',
      'timerEarlyFire'
    ];

    for (const fault of negFaults) {
      const sc = (fault === 'staleTimerExecution') ? 'settledCheckoutReset' :
        (fault === 'pipelinedContamination' || fault === 'timerEarlyFire') ? 'pipelinedRequest' :
        'pendingCheckoutSuccess';
      const ctx = await browser.newContext({viewport: {width: 320, height: 900}, reducedMotion: 'reduce'});
      const page = await ctx.newPage();
      page.on('pageerror', e => evidence.errors.push(String(e)));
      evidence.negativeControls[fault] = {
        record: await runScenario(page, origin, {scenario: sc, viewport: 320, scale: 1}, fault)
      };
      await ctx.close();
    }

    assert.equal(evidence.records.length, 36);
    assert.deepEqual(evidence.errors, []);
    evidence.pass = true;
  } catch (e) {
    evidence.errors.push(String(e.stack || e));
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }

  fs.writeFileSync(output, JSON.stringify(evidence, null, 2));

  // Run the Python gate
  const gate = spawnSync('python3', ['-B', path.join(__dirname, 'clipboard_status_ownership.py'), output], {encoding: 'utf8'});
  console.log(JSON.stringify({
    browser: evidence.browser,
    records: evidence.records.length,
    controls: Object.keys(evidence.negativeControls).length,
    gateExit: gate.status,
    gate: gate.stdout ? JSON.parse(gate.stdout) : null,
    stderr: gate.stderr,
    errors: evidence.errors
  }, null, 2));

  process.exit(gate.status === 0 ? 0 : 1);
})();
