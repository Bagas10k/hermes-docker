'use strict';
// UIUX-072: Full default scroll anchoring matrix, virtual timer reset continuity, and neighbor geometry audit.
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const {execFileSync, spawnSync} = require('node:child_process');
const http = require('node:http');
const path = require('node:path');
const fs = require('node:fs');
const {measure} = require('./test_focus_reflow_chromium.cjs');
const fixture = JSON.parse(execFileSync('python3', ['-B', path.join(__dirname, 'native_clipboard_fixture.py')], {encoding:'utf8'}));
const output = path.join(__dirname, '../references/uiux-072-browser.json');
const evidence = {target:'UIUX-072', records:[], negativeControls:{}, comparisons:{}, errors:[], pass:false};

async function frames(page) {
  await page.evaluate(async () => { for(let i=0; i<3; i++) await new Promise(requestAnimationFrame); });
}

async function setup(page, origin, meta, anchor='auto') {
  await page.goto(origin);
  await page.bringToFront();
  await page.evaluate(({scale, anchor}) => {
    window.trace = []; window.seq = 0; window.phase = 'setup';
    window.desc = el => el ? {
      tag: el.tagName?.toLowerCase() || null, id: el.id || null,
      role: el.getAttribute?.('role') || null, dataNode: el.getAttribute?.('data-node') || null,
      dataBreadcrumbNode: el.getAttribute?.('data-breadcrumb-node') || null,
      isCopyBtn: el === window.initialCopyButton,
    } : null;
    for(const type of ['focusin','focusout','keydown','scroll']) document.addEventListener(type, e => {
      if(type === 'keydown' && !['Tab','Enter'].includes(e.key)) return;
      window.trace.push({
        seq: ++window.seq, phase: window.phase, type,
        target: window.desc(e.target), relatedTarget: window.desc(e.relatedTarget),
        timeStamp: e.timeStamp, observedTime: performance.now(), trusted: e.isTrusted,
        key: e.key || null, shiftKey: !!e.shiftKey
      });
    }, true);
    window.fontBaseline = [document.body, ...document.querySelectorAll('main, main *')]
      .filter(e => e instanceof HTMLElement).map(e => [e, parseFloat(getComputedStyle(e).fontSize)]);
    for(const [el, size] of window.fontBaseline) el.style.fontSize = size * scale + 'px';

    // Observe the native app timer; do not freeze, accelerate or manually invoke it.
    window.timerEvidence = [];
    const realTimer = window.setTimeout.bind(window);
    window.setTimeout = (cb, ms, ...args) => {
      if(ms !== 1500) return realTimer(cb, ms, ...args);
      const timer = {delay: ms, registeredAt: performance.now(), firedAt: null, calls: 0};
      window.timerEvidence.push(timer);
      return realTimer(() => {
        timer.firedAt = performance.now(); timer.calls++;
        cb(...args);
      }, ms);
    };

    const section = document.querySelector('section[aria-label="Navigasi riwayat"]');
    const outer = document.createElement('div'); outer.id = 'dag-scroll-outer';
    outer.style.cssText = `overflow:auto;max-height:450px;width:100%;border-radius:0;box-sizing:border-box;overflow-anchor:${anchor}`;
    section.before(outer); outer.append(section);
    const bar = document.getElementById('dag-breadcrumbs');
    const inner = document.createElement('div'); inner.id = 'dag-scroll-inner';
    inner.style.cssText = `overflow-x:auto;overflow-y:hidden;max-width:100%;border-radius:0;box-sizing:border-box;overflow-anchor:${anchor}`;
    bar.before(inner); inner.append(bar);
    Object.assign(bar.style, {minWidth: '1000px', paddingRight: '120px', flexWrap: 'nowrap', borderRadius: '0px'});
    window.initialCopyButton = document.querySelector('.dag-breadcrumb-copy-btn');
    window.writeCalls = 0; window.trustedClicks = 0;
    window.initialCopyButton.addEventListener('click', e => { if(e.isTrusted) window.trustedClicks++; });
    Object.defineProperty(navigator, 'clipboard', {configurable: true, value: {writeText: () => {
      window.writeCalls++; return new Promise((resolve, reject) => { window.settleCopy = {resolve, reject}; });
    }}});
    window.scrollState = () => Object.fromEntries([
      ['windowX', window.scrollX], ['windowY', window.scrollY],
      ...['dag-scroll-outer', 'dag-scroll-inner', 'dag-view'].flatMap(id => {
        const e = document.getElementById(id); return [[id + 'X', e.scrollLeft], [id + 'Y', e.scrollTop]];
      })
    ]);
  }, {...meta, anchor});

  await page.locator('#outside').focus();
  let tabs = 0;
  while(tabs < 30 && !await page.evaluate(() => document.activeElement === window.initialCopyButton)) {
    await page.keyboard.press('Tab'); tabs++;
  }
  assert.ok(tabs > 0 && tabs < 30);
  await frames(page);
  return tabs;
}

async function sample(page, name, meta, tabs) {
  const state = name === 'initial' || name === 'reset' ? 'idle' : name === 'settled' ? meta.outcome : 'pending';
  const measurement = await page.evaluate(measure, {...meta, state, container: 'normal', tabCount: tabs});
  const snap = await page.evaluate(() => {
    const b = window.initialCopyButton, outer = document.getElementById('dag-scroll-outer');
    const active = document.activeElement;
    const box = el => {const r=el.getBoundingClientRect();return {left:r.left,top:r.top,right:r.right,bottom:r.bottom};};
    const clips = [];
    for(let el=active?.parentElement; el; el=el.parentElement) {
      const cs=getComputedStyle(el), paint=/(paint|strict|content)/.test(cs.contain);
      const x=paint||/^(auto|scroll|hidden|clip)$/.test(cs.overflowX);
      const y=paint||/^(auto|scroll|hidden|clip)$/.test(cs.overflowY);
      if(x||y) {const r=box(el);clips.push({left:r.left+el.clientLeft,top:r.top+el.clientTop,
        right:r.left+el.clientLeft+el.clientWidth,bottom:r.top+el.clientTop+el.clientHeight,x,y});}
    }
    const overlays=[];
    // Bounded known opaque foregrounds, including pointer-events:none.
    for(const el of document.querySelectorAll('#dag-diff-popover, #dag-minimap-wrap, [data-focus-audit-overlay]')) {
      const s=getComputedStyle(el), r=el.getBoundingClientRect();
      if(s.display==='none'||s.visibility==='hidden'||!r.width||!r.height) continue;
      const o=box(el);
      for(let p=el.parentElement;p;p=p.parentElement) {
        const cs=getComputedStyle(p), pr=box(p);
        if(/^(auto|scroll|hidden|clip)$/.test(cs.overflowX)) {o.left=Math.max(o.left,pr.left+p.clientLeft);o.right=Math.min(o.right,pr.left+p.clientLeft+p.clientWidth);}
        if(/^(auto|scroll|hidden|clip)$/.test(cs.overflowY)) {o.top=Math.max(o.top,pr.top+p.clientTop);o.bottom=Math.min(o.bottom,pr.top+p.clientTop+p.clientHeight);}
      }
      if(o.right>o.left&&o.bottom>o.top) overlays.push(o);
    }
    // SVG groups contain unpainted areas: probe their actual circle, not empty AABB corners.
    const paint=active?.querySelector('.node-circle')||active, pr=paint.getBoundingClientRect();
    const hit=document.elementFromPoint(pr.left+pr.width/2,pr.top+pr.height/2);
    const activeTarget = active ? {
      tag: active.tagName?.toLowerCase() || null,
      id: active.id || null,
      role: active.getAttribute?.('role') || null,
      dataNode: active.getAttribute?.('data-node') || null,
      dataBreadcrumbNode: active.getAttribute?.('data-breadcrumb-node') || null,
      isCopyBtn: active === b,
      focused: true, connected: active.isConnected,
      viewport: {left:0,top:0,right:innerWidth,bottom:innerHeight}, clips, overlays,
      hit: hit === active || active.contains(hit),
      focusVisible: active.matches(':focus-visible'),
      outlineStyle: getComputedStyle(active).outlineStyle,
      outlineWidth: parseFloat(getComputedStyle(active).outlineWidth) || 0,
      outlineOffset: parseFloat(getComputedStyle(active).outlineOffset) || 0,
      rect: (() => {
        const r = active.getBoundingClientRect();
        return {left: r.left, top: r.top, right: r.right, bottom: r.bottom, width: r.width, height: r.height};
      })(),
    } : null;

    return {
      sameNode: b === document.querySelector('.dag-breadcrumb-copy-btn'),
      isConnected: b.isConnected,
      activeElementMatchesBtn: document.activeElement === b,
      activeElement: window.desc(document.activeElement),
      activeTarget,
      statusHeight: document.querySelector('.dag-status-region').getBoundingClientRect().height,
      statusText: document.getElementById('status').textContent,
      buttonText: b.textContent,
      copied: b.classList.contains('copied'),
      trustedClicks: window.trustedClicks,
      writeCalls: window.writeCalls,
      outerScrollTop: outer.scrollTop,
      innerScrollLeft: document.getElementById('dag-scroll-inner').scrollLeft,
      containerWidth: outer.clientWidth,
      windowWidth: innerWidth,
      windowHeight: innerHeight,
      eventSeq: window.seq,
      scrollEventCount: window.trace.filter(e => e.type === 'scroll').length,
      scroll: window.scrollState(),
      checkpointTime: performance.now(),
      anchorPolicy: getComputedStyle(outer).overflowAnchor
    };
  });
  return {phase: name, ...snap, measurement};
}

async function run(page, origin, meta, fault = null) {
  const anchor = fault === 'optOut' ? 'none' : 'auto';
  const tabs = await setup(page, origin, meta, anchor);

  if(['oldUnstableAuto', 'optOut'].includes(fault)) {
    await page.evaluate(() => {
      const reg = document.querySelector('.dag-status-region');
      if (reg) reg.style.display = 'block';
      for (const e of document.querySelectorAll('.dag-status-reserve')) e.style.display = 'none';
    });
  }

  const phases = {};
  for(const name of ['initial','pending','scrolled','shrunk','regrown','departed','settled','reset']) {
    await page.evaluate(p => window.phase = p, name);
    if(name === 'pending') await page.keyboard.press('Enter');
    if(name === 'scrolled') await page.evaluate(() => {
      document.getElementById('dag-scroll-outer').scrollTop += 30;
      const i = document.getElementById('dag-scroll-inner');
      i.scrollLeft += i.scrollLeft >= 30 ? -25 : 25;
    });
    if(name === 'shrunk') await page.evaluate(v => {
      document.getElementById('dag-scroll-outer').style.maxWidth = ({320: 250, 390: 310, 768: 660}[v]) + 'px';
    }, meta.viewport);
    if(name === 'regrown') await page.evaluate(() => document.getElementById('dag-scroll-outer').style.maxWidth = '');
    if(name === 'shrunk' && fault === 'transientBlurRefocus') await page.evaluate(() => {
      window.initialCopyButton.blur();
      window.initialCopyButton.focus({preventScroll: true});
    });
    if(name === 'departed') {
      if(meta.departure !== 'stay') await page.keyboard.press(meta.departure === 'forward' ? 'Tab' : 'Shift+Tab');
      if(fault === 'wrongDepartureIdentity') await page.evaluate(() => document.getElementById('outside').focus({preventScroll: true}));
    }
    if(name === 'settled') {
      await page.evaluate(out => out === 'success' ? window.settleCopy.resolve() : window.settleCopy.reject(new Error('controlled denial')), meta.outcome);
      await page.waitForFunction(out => window.initialCopyButton.textContent === (out === 'success' ? 'Tersalin!' : 'Gagal menyalin'), meta.outcome);
      if(['completionFocusTheft','completionStealReturn'].includes(fault)) await page.evaluate(restore => {
        const before = document.activeElement;
        window.initialCopyButton.focus({preventScroll: true});
        if(restore && before) before.focus({preventScroll: true});
      }, fault === 'completionStealReturn');
    }
    if(name === 'reset') {
      await page.waitForFunction(() => window.initialCopyButton.textContent === 'Salin Rute');
      await page.evaluate(fault => {
        if(fault === 'resetFocusTheft') {
          const before = document.activeElement;
          window.initialCopyButton.focus({preventScroll: true});
          if(before) before.focus({preventScroll: true});
        }
      }, fault);
      await page.waitForFunction(() => window.initialCopyButton.textContent === 'Salin Rute');
      if(fault === 'transientResetScroll') await page.evaluate(async () => {
        const e = document.getElementById('dag-scroll-outer'), y = e.scrollTop;
        e.scrollTop = y + 35;
        await new Promise(requestAnimationFrame);
        await new Promise(requestAnimationFrame);
        e.scrollTop = y;
      });
    }
    if(name === 'reset' && ['targetClipped','targetCovered'].includes(fault)) await page.evaluate(fault => {
      const a=document.activeElement, r=a.getBoundingClientRect();
      if(fault==='targetClipped') {a.style.transform='translateX(-1000px)';}
      else {const o=document.createElement('div');o.dataset.focusAuditOverlay='';
        Object.assign(o.style,{position:'fixed',left:r.left+'px',top:r.top+'px',width:r.width+'px',height:r.height+'px',background:'rgb(0,0,0)',zIndex:'2147483647',pointerEvents:'none'});document.body.append(o);}
    },fault);
    await frames(page);
    phases[name] = await sample(page, name, meta, tabs);
  }
  const eventTrace = await page.evaluate(() => window.trace);
  const timers = await page.evaluate(() => window.timerEvidence);
  return {...meta, anchorPolicy: anchor, layout: ['oldUnstableAuto', 'optOut'].includes(fault) ? 'unreserved' : 'reserved',
    resetTimerExecuted: timers.length === 1 && timers[0].calls === 1, timers, phases, eventTrace};
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

    // Full 36-sequence matrix under default scroll anchoring (overflow-anchor: auto)
    for(const viewport of [320, 390, 768]) {
      const ctx = await browser.newContext({viewport: {width: viewport, height: 900}, reducedMotion: 'reduce'});
      const page = await ctx.newPage();
      page.on('pageerror', e => evidence.errors.push(String(e)));
      for(const scale of [1, 2]) {
        for(const outcome of ['success', 'failure']) {
          for(const departure of ['stay', 'forward', 'backward']) {
            evidence.records.push(await run(page, origin, {viewport, scale, outcome, departure}));
          }
        }
      }
      await ctx.close();
    }

    // Explicit negative controls
    for(const fault of ['oldUnstableAuto', 'transientBlurRefocus', 'completionFocusTheft', 'completionStealReturn', 'resetFocusTheft', 'transientResetScroll', 'wrongDepartureIdentity', 'targetClipped', 'targetCovered']) {
      const meta = fault === 'oldUnstableAuto' ? {viewport: 390, scale: 2, outcome: 'failure', departure: 'forward'} :
        {viewport: 320, scale: 1, outcome: 'success', departure: ['completionFocusTheft', 'completionStealReturn', 'resetFocusTheft', 'wrongDepartureIdentity', 'targetClipped', 'targetCovered'].includes(fault) ? 'forward' : 'stay'};
      const ctx = await browser.newContext({viewport: {width: meta.viewport, height: 900}, reducedMotion: 'reduce'});
      const page = await ctx.newPage();
      page.on('pageerror', e => evidence.errors.push(String(e)));
      evidence.negativeControls[fault] = {record: await run(page, origin, meta, fault)};
      await ctx.close();
    }

    // Honest comparison with anchor opt-out (overflow-anchor: none)
    {
      const meta = {viewport: 390, scale: 2, outcome: 'failure', departure: 'forward'};
      const ctx = await browser.newContext({viewport: {width: meta.viewport, height: 900}, reducedMotion: 'reduce'});
      const page = await ctx.newPage();
      page.on('pageerror', e => evidence.errors.push(String(e)));
      evidence.comparisons.optOut = {record: await run(page, origin, meta, 'optOut')};
      await ctx.close();
    }

    assert.equal(evidence.records.length, 36);
    assert.deepEqual(evidence.errors, []);
    evidence.pass = true;
  } catch(e) {
    evidence.errors.push(String(e));
  } finally {
    if(browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }

  fs.writeFileSync(output, JSON.stringify(evidence, null, 2));
  const gate = spawnSync('python3', ['-B', path.join(__dirname, 'clipboard_scroll_anchor.py'), output], {encoding: 'utf8'});
  console.log(JSON.stringify({
    browser: evidence.browser,
    records: evidence.records.length,
    controls: Object.keys(evidence.negativeControls).length,
    comparisons: Object.keys(evidence.comparisons).length,
    gateExit: gate.status,
    gate: gate.stdout,
    stderr: gate.stderr,
    errors: evidence.errors
  }));
  process.exit(gate.status === 0 ? 0 : 1);
})();
