'use strict';
// UIUX-070: Nested scroll containers, container resize & focus continuity.
// Uses real keyboard navigation + application-driven promise settlement.
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const {execFileSync, spawnSync} = require('node:child_process');
const http = require('node:http');
const path = require('node:path');
const fs = require('node:fs');

const {measure} = require('./test_focus_reflow_chromium.cjs');
const fixture = JSON.parse(execFileSync('python3', ['-B', path.join(__dirname, 'native_clipboard_fixture.py')], {encoding: 'utf8'}));
const output = path.join(__dirname, '../references/uiux-070-browser.json');

const evidence = {
  target: 'UIUX-070',
  records: [],
  negativeControls: {},
  errors: [],
  pass: false,
  limitations: [
    'Explicit computed-font scaling, not native browser zoom or OS DPI scaling',
    'Known foreground opaque rectangles and sampled hit-testing, not arbitrary CSS paint proof',
    'Rounded outline AABB is conservative; no pixel-area or screen-reader speech claim',
    'Controlled clipboard promises; native Tab/Enter; no OS clipboard daemon claim',
    'Clipboard button, bar, nested wrappers, and document overflow audited; not all possible UI surfaces'
  ]
};

async function awaitAnim(page) {
  await page.evaluate(async () => {
    await new Promise(requestAnimationFrame);
    const b = document.querySelector('.dag-breadcrumb-copy-btn');
    if (b && typeof b.getAnimations === 'function') {
      await Promise.all(b.getAnimations().map(a => a.finished));
    }
  });
}

async function prepareNested(page, origin, meta) {
  await page.goto(origin);
  await page.bringToFront();

  await page.evaluate(({scale}) => {
    // Snapshot font baseline before mutation
    window.fontBaseline = [document.body, ...document.querySelectorAll('main, main *')]
      .filter(el => el instanceof HTMLElement).map(el => [el, parseFloat(getComputedStyle(el).fontSize)]);
    for (const [el, size] of window.fontBaseline) el.style.fontSize = (size * scale) + 'px';

    const realSetTimeout = window.setTimeout.bind(window);
    window.setTimeout = (callback, ms, ...args) => ms === 1500 ? 777777 : realSetTimeout(callback, ms, ...args);
    window.writeCalls = 0;
    window.trustedClicks = 0;

    // Wrap existing section with outer scroll container (no gratuitous production change)
    const s = document.querySelector('section[aria-label="Navigasi riwayat"]');
    const outerWrap = document.createElement('div');
    outerWrap.id = 'dag-scroll-outer';
    outerWrap.style.cssText = 'overflow: auto; max-height: 450px; width: 100%; border-radius: 0px; box-sizing: border-box;';
    s.parentNode.insertBefore(outerWrap, s);
    outerWrap.appendChild(s);

    // Wrap breadcrumbs bar with inner horizontal scroll container
    const bc = document.getElementById('dag-breadcrumbs');
    const innerWrap = document.createElement('div');
    innerWrap.id = 'dag-scroll-inner';
    innerWrap.style.cssText = 'overflow-x: auto; overflow-y: hidden; max-width: 100%; border-radius: 0px; box-sizing: border-box;';
    bc.parentNode.insertBefore(innerWrap, bc);
    innerWrap.appendChild(bc);
    bc.style.minWidth = '1000px';
    bc.style.paddingRight = '120px';
    bc.style.flexWrap = 'nowrap';
    bc.style.borderRadius = '0px';

    const b = document.querySelector('.dag-breadcrumb-copy-btn');
    window.initialCopyButton = b;
    b.addEventListener('click', e => { if (e.isTrusted) window.trustedClicks++; });
    Object.defineProperty(navigator, 'clipboard', {configurable: true, value: {
      writeText: () => {
        window.writeCalls++;
        return new Promise((resolve, reject) => { window.settleCopy = {resolve, reject}; });
      }
    }});
  }, meta);

  await page.locator('#outside').focus();
  let tabs = 0;
  while (tabs < 30 && !await page.evaluate(() => document.activeElement.matches('.dag-breadcrumb-copy-btn'))) {
    await page.keyboard.press('Tab');
    tabs++;
  }
  assert.ok(tabs > 0 && tabs < 30, 'native Tab must reach copy button');
  await awaitAnim(page);
  return {...meta, tabCount: tabs};
}

async function extractPhase(page, phaseName, measurement, extra = {}) {
  const domInfo = await page.evaluate(() => {
    const b = document.querySelector('.dag-breadcrumb-copy-btn');
    const outer = document.getElementById('dag-scroll-outer');
    const inner = document.getElementById('dag-scroll-inner');
    return {
      sameNode: b === window.initialCopyButton,
      isConnected: Boolean(b && b.isConnected),
      activeElementMatchesBtn: Boolean(document.activeElement && document.activeElement.matches('.dag-breadcrumb-copy-btn')),
      trustedClicks: window.trustedClicks || 0,
      writeCalls: window.writeCalls || 0,
      outerScrollTop: outer ? outer.scrollTop : 0,
      innerScrollLeft: inner ? inner.scrollLeft : 0,
      containerWidth: outer ? outer.clientWidth : 0,
      windowWidth: window.innerWidth,
      windowHeight: window.innerHeight
    };
  });
  return {
    phase: phaseName,
    ...domInfo,
    ...extra,
    measurement
  };
}

(async () => {
  const server = http.createServer((req, res) => {
    res.writeHead(200, {'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store'});
    res.end(fixture.html);
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));

  let browser;
  try {
    const origin = `http://127.0.0.1:${server.address().port}`;
    browser = await chromium.launch({headless: true});
    evidence.browser = browser.version();

    for (const viewport of [320, 390, 768]) {
      const context = await browser.newContext({
        viewport: {width: viewport, height: 900},
        reducedMotion: 'reduce'
      });
      const page = await context.newPage();
      page.setDefaultTimeout(10000);
      page.on('pageerror', e => evidence.errors.push(String(e)));

      for (const scale of [1, 2]) {
        for (const outcome of ['success', 'failure']) {
          const meta = await prepareNested(page, origin, {viewport, container: 'normal', scale, outcome});
          const tabs = meta.tabCount;

          // 1. Initial Phase: Focused via Tab
          const mInit = await page.evaluate(measure, {...meta, state: 'idle', tabCount: tabs});
          const pInit = await extractPhase(page, 'initial', mInit);

          // 2. Pending Phase: Enter pressed, promise pending via real app
          await page.keyboard.press('Enter');
          await page.waitForFunction(() => window.writeCalls === 1 && document.querySelector('.dag-breadcrumb-copy-btn').textContent === 'Menyalin…');
          await awaitAnim(page);
          const mPend = await page.evaluate(measure, {...meta, state: 'pending', tabCount: tabs});
          const pPend = await extractPhase(page, 'pending', mPend);

          // 3. Scrolled Phase: Both nested scroll offsets change while pending
          await page.evaluate(() => {
            const outer = document.getElementById('dag-scroll-outer');
            const inner = document.getElementById('dag-scroll-inner');
            outer.scrollTop += 30;
            if (inner.scrollLeft >= 30) {
              inner.scrollLeft -= 25;
            } else {
              inner.scrollLeft += 25;
            }
          });
          await awaitAnim(page);
          const mScrl = await page.evaluate(measure, {...meta, state: 'pending', tabCount: tabs});
          const pScrl = await extractPhase(page, 'scrolled', mScrl);

          // 4. Shrunk Phase: Container width shrinks, window unchanged, button remains focused
          await page.evaluate(vp => {
            const outer = document.getElementById('dag-scroll-outer');
            const shrinkW = vp === 320 ? 250 : (vp === 390 ? 310 : 660);
            outer.style.maxWidth = shrinkW + 'px';
            void outer.offsetWidth;
          }, viewport);
          await awaitAnim(page);
          const mShrn = await page.evaluate(measure, {...meta, state: 'pending', tabCount: tabs});
          const pShrn = await extractPhase(page, 'shrunk', mShrn);

          // 5. Regrown Phase: Container width regrows, window unchanged, button remains focused
          await page.evaluate(() => {
            const outer = document.getElementById('dag-scroll-outer');
            outer.style.maxWidth = '';
            void outer.offsetWidth;
          });
          await awaitAnim(page);
          const mRegr = await page.evaluate(measure, {...meta, state: 'pending', tabCount: tabs});
          const pRegr = await extractPhase(page, 'regrown', mRegr);

          // 6. Settled Phase: Resolve or reject via real app promise settlement
          if (outcome === 'success') {
            await page.evaluate(() => window.settleCopy.resolve());
          } else {
            await page.evaluate(() => window.settleCopy.reject(new Error('controlled denial')));
          }
          await page.waitForFunction(
            st => document.querySelector('.dag-breadcrumb-copy-btn').textContent === (st === 'success' ? 'Tersalin!' : 'Gagal menyalin'),
            outcome
          );
          await awaitAnim(page);
          const mSetl = await page.evaluate(measure, {...meta, state: outcome, tabCount: tabs});
          const pSetl = await extractPhase(page, 'settled', mSetl);

          // 7. Keyboard Roundtrip Phase: Tab to neighbor and Shift+Tab return
          await page.keyboard.press('Tab');
          const neighborMoved = await page.evaluate(() => !document.activeElement.matches('.dag-breadcrumb-copy-btn'));
          const neighbor = await page.evaluate(() => ({neighborTag:document.activeElement.tagName,
            neighborNode:document.activeElement.getAttribute('data-node'),neighborRole:document.activeElement.getAttribute('role')}));
          assert.deepEqual(neighbor,{neighborTag:'g',neighborNode:'alpha',neighborRole:'button'});
          await page.keyboard.down('Shift');
          await page.keyboard.press('Tab');
          await page.keyboard.up('Shift');
          const returnedToCopy = await page.evaluate(() => document.activeElement.matches('.dag-breadcrumb-copy-btn'));
          await awaitAnim(page);
          const mRt = await page.evaluate(measure, {...meta, state: outcome, tabCount: tabs});
          const pRt = await extractPhase(page, 'roundtrip', mRt, {...neighbor, neighborMoved, returnedToCopy});

          evidence.records.push({
            viewport,
            scale,
            outcome,
            phases: {
              initial: pInit,
              pending: pPend,
              scrolled: pScrl,
              shrunk: pShrn,
              regrown: pRegr,
              settled: pSetl,
              roundtrip: pRt
            }
          });
        }
      }
      await context.close();
    }

    // Negative controls in isolated context
    const ctx = await browser.newContext({viewport: {width: 320, height: 900}, reducedMotion: 'reduce'});
    const page = await ctx.newPage();
    page.on('pageerror', e => evidence.errors.push(String(e)));

    for (const name of ['stickyOcclusionAuto', 'stickyOcclusionPointerEventsNone', 'clipping', 'outlineOnly', 'unfocused', 'textOverflow']) {
      const meta = await prepareNested(page, origin, {viewport: 320, container: 'normal', scale: 1, outcome: 'success'});
      const tabs = meta.tabCount;

      const controlMeta = await page.evaluate(ctrlName => {
        const b = document.querySelector('.dag-breadcrumb-copy-btn');
        const r = b.getBoundingClientRect();
        let overlayPos = null;

        if (ctrlName.startsWith('stickyOcclusion')) {
          const o = document.createElement('div');
          o.dataset.focusAuditOverlay = '';
          const inner=document.getElementById('dag-scroll-inner');
          const clipLeft=inner.getBoundingClientRect().left+inner.clientLeft;
          const inset=r.left-clipLeft-15, width=r.width+20;
          Object.assign(o.style,{position:'sticky',left:inset+'px',width:width+'px',
            flex:'0 0 '+width+'px',marginRight:-(width+6)+'px',height:r.height+'px',
            backgroundColor:'rgb(0, 0, 0)',zIndex:'9999',
            pointerEvents:ctrlName==='stickyOcclusionAuto'?'auto':'none'});
          // Net zero flex footprint: the negative margin includes the existing gap.
          b.parentElement.insertBefore(o,b.parentElement.firstChild);
          const leftBefore=o.getBoundingClientRect().left, scrollBefore=inner.scrollLeft;
          inner.scrollLeft+=10;
          const leftAfter=o.getBoundingClientRect().left, scrollAfter=inner.scrollLeft;
          o.style.position='relative';o.style.left='0px';
          const normalLeft=o.getBoundingClientRect().left;
          o.style.position='sticky';o.style.left=inset+'px';
          return {overlayPosition:getComputedStyle(o).position,scrollBefore,scrollAfter,
            inset,clipLeft,leftBefore,leftAfter,normalLeft,pointerEvents:getComputedStyle(o).pointerEvents};
        } else if (ctrlName === 'clipping') {
          const wrap = document.getElementById('dag-scroll-outer');
          const wr = wrap.getBoundingClientRect();
          wrap.style.height = (r.bottom - wr.top - 2) + 'px';
          wrap.style.overflow = 'hidden';
        } else if (ctrlName === 'outlineOnly') {
          const o = document.createElement('div');
          o.dataset.focusAuditOverlay = '';
          Object.assign(o.style, {
            position: 'fixed',
            left: (r.left - 3.5) + 'px',
            top: (r.top + 5) + 'px',
            width: '1px',
            height: (r.height - 10) + 'px',
            backgroundColor: 'rgb(0, 0, 0)',
            zIndex: '2147483647',
            pointerEvents: 'none'
          });
          document.body.appendChild(o);
        } else if (ctrlName === 'unfocused') {
          document.getElementById('outside').focus();
        } else if (ctrlName === 'textOverflow') {
          b.style.whiteSpace = 'nowrap';
          b.style.maxWidth = '30px';
        }
        return {overlayPos};
      }, name);

      await awaitAnim(page);
      const m = await page.evaluate(measure, {...meta, state: 'idle', tabCount: tabs});
      const ctrlEntry = {record: m, ...controlMeta};
      if (controlMeta.overlayPos) {
        ctrlEntry.overlayPosition = controlMeta.overlayPos;
      }
      evidence.negativeControls[name] = ctrlEntry;
    }
    await ctx.close();

    assert.equal(evidence.records.length, 12, 'Expected 12 matrix records');
    assert.deepEqual(evidence.errors, [], 'Expected 0 errors');
    evidence.pass = true;
  } catch (err) {
    evidence.errors.push(String(err));
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }

  fs.writeFileSync(output, JSON.stringify(evidence, null, 2));
  const gate = spawnSync('python3', ['-B', path.join(__dirname, 'clipboard_nested_reflow.py'), output], {encoding: 'utf8'});
  console.log(JSON.stringify({
    browser: evidence.browser,
    records: evidence.records.length,
    negativeControls: Object.keys(evidence.negativeControls).length,
    gateExit: gate.status,
    gate: gate.stdout,
    errors: evidence.errors,
    stderr: gate.stderr
  }));
  process.exit(gate.status === 0 ? 0 : 1);
})();
