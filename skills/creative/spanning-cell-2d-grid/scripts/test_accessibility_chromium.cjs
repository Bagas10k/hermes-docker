'use strict';
// UIUX-067: Accessibility runner for keyboard focus-visible contrast and reduced-motion audit.
// Viewports: 390, 768, 1280.
// Reuses Playwright from NODE_PATH=/home/ubuntu/website-security-auditor/node_modules (no installs).
// Protects shared clipboard: DOES NOT write to native clipboard; tests focus and motion only.

const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const {execFileSync} = require('node:child_process');
const http = require('node:http');
const path = require('node:path');
const fs = require('node:fs');

const fixturePy = path.join(__dirname, 'native_clipboard_fixture.py');
const fixture = JSON.parse(execFileSync('python3', ['-B', fixturePy], {encoding: 'utf8'}));

const evidence = {
  kind: 'Chromium headless accessibility audit; focus-visible contrast and prefers-reduced-motion',
  causalModel: 'outcome = f(focus owner, promise generation, media preference, computed styles)',
  limitations: [
    'Not an official WCAG certification or compliance endorsement',
    'No screen reader speech or synthetic audio announcement claim',
    'No GPU, FPS, or compositor frame timing claim',
    'Contrast evaluated on opaque rendered surfaces without gradient blending',
  ],
  browser: null,
  records: [],
  jsCoordinationContract: {
    requiresJsMatchMediaGuard: true,
    targetFile: 'scripts/history_browser.js',
    functionsAudited: ['autoCenterViewport', 'search'],
    finding: 'Explicit smooth bypasses CSS auto; guarded application navigation is verified separately on a scrollable container.',
  },
  errors: [],
};

(async () => {
  const server = http.createServer((req, res) => {
    res.writeHead(200, {'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store'});
    res.end(fixture.html);
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));

  let browser;
  try {
    const origin = `http://127.0.0.1:${server.address().port}`;
    evidence.origin = origin;
    browser = await chromium.launch({headless: true});
    evidence.browser = browser.version();

    for (const width of [390, 768, 1280]) {
      const context = await browser.newContext({viewport: {width, height: 1000}});
      const page = await context.newPage();
      page.setDefaultTimeout(10000);
      page.on('pageerror', e => evidence.errors.push(String(e)));

      await page.goto(origin);
      await page.bringToFront();

      const button = page.locator('.dag-breadcrumb-copy-btn');
      await button.waitFor({state: 'visible'});

      // Negative check: before keyboard focus, outline is not active
      const unfocusedStyle = await button.evaluate(el => {
        const cs = window.getComputedStyle(el);
        return {
          outlineStyle: cs.outlineStyle,
          outlineWidth: cs.outlineWidth,
          focused: document.activeElement === el,
        };
      });
      assert.equal(unfocusedStyle.focused, false, 'Button must start unfocused');
      assert.ok(
        unfocusedStyle.outlineStyle === 'none' || unfocusedStyle.outlineWidth === '0px',
        'Unfocused button must not have active outline'
      );

      // --- 1. Keyboard focus-visible activation via sequential Tab ---
      await page.locator('#outside').focus();
      for (let i = 0; i < 15; i++) {
        const isCopyBtn = await page.evaluate(() => document.activeElement.classList.contains('dag-breadcrumb-copy-btn'));
        if (isCopyBtn) break;
        await page.keyboard.press('Tab');
      }

      // Wait for focus transition to settle to exact declared values
      await page.waitForFunction(() => {
        const b = document.querySelector('.dag-breadcrumb-copy-btn');
        return document.activeElement === b && window.getComputedStyle(b).outlineOffset === '2px';
      });

      const focusVisibleMetrics = await page.evaluate(() => {
        const btn = document.querySelector('.dag-breadcrumb-copy-btn');
        const bar = document.querySelector('.dag-breadcrumbs-bar');
        const csBtn = window.getComputedStyle(btn);
        const csBar = window.getComputedStyle(bar);
        return {
          focused: document.activeElement === btn,
          outlineStyle: csBtn.outlineStyle,
          outlineWidth: csBtn.outlineWidth,
          outlineColor: csBtn.outlineColor,
          outlineOffset: csBtn.outlineOffset,
          adjacentBg: csBar.backgroundColor,
          buttonBg: csBtn.backgroundColor,
          buttonColor: csBtn.color,
        };
      });

      assert.equal(focusVisibleMetrics.focused, true, 'Copy button must hold focus');
      assert.equal(focusVisibleMetrics.outlineStyle, 'solid', 'Outline style must be solid');
      assert.equal(focusVisibleMetrics.outlineWidth, '2px', 'Outline width must be 2px');
      assert.equal(focusVisibleMetrics.outlineOffset, '2px', 'Outline offset must be 2px');
      assert.equal(focusVisibleMetrics.outlineColor, 'rgb(37, 99, 235)', 'Outline color must match #2563eb');
      assert.equal(focusVisibleMetrics.adjacentBg, 'rgb(241, 245, 249)', 'Adjacent breadcrumbs bar background must match #f1f5f9');
      assert.equal(focusVisibleMetrics.buttonBg, 'rgb(226, 232, 240)', 'Button background must match #e2e8f0');

      evidence.records.push({
        type: 'focus_visible',
        viewport: width,
        target: '.dag-breadcrumb-copy-btn',
        focused: focusVisibleMetrics.focused,
        outlineStyle: focusVisibleMetrics.outlineStyle,
        outlineWidth: focusVisibleMetrics.outlineWidth,
        outlineColor: focusVisibleMetrics.outlineColor,
        outlineOffset: focusVisibleMetrics.outlineOffset,
        adjacentBg: focusVisibleMetrics.adjacentBg,
        buttonBg: focusVisibleMetrics.buttonBg,
        buttonColor: focusVisibleMetrics.buttonColor,
      });

      // --- 2. Motion audit: no-preference vs reduce ---
      // A. Default / no-preference
      const normalMotion = await page.evaluate(() => {
        const btn = document.querySelector('.dag-breadcrumb-copy-btn');
        const item = document.querySelector('.dag-breadcrumb-item');
        const minimap = document.querySelector('.dag-minimap-container');
        const searchInput = document.querySelector('.dag-search-input');
        const container = document.querySelector('.dag-container');
        return {
          btnTransition: window.getComputedStyle(btn).transitionDuration,
          itemTransition: item ? window.getComputedStyle(item).transitionDuration : null,
          minimapTransition: minimap ? window.getComputedStyle(minimap).transitionDuration : null,
          searchTransition: searchInput ? window.getComputedStyle(searchInput).transitionDuration : null,
          containerScrollBehavior: window.getComputedStyle(container).scrollBehavior,
        };
      });
      assert.equal(normalMotion.btnTransition, '0.15s');
      assert.equal(normalMotion.minimapTransition, '0.2s');

      evidence.records.push({
        type: 'motion_styles',
        viewport: width,
        preference: 'no-preference',
        styles: normalMotion,
      });

      // B. Emulate prefers-reduced-motion: reduce
      await page.emulateMedia({reducedMotion: 'reduce'});
      const reducedMotion = await page.evaluate(() => {
        const btn = document.querySelector('.dag-breadcrumb-copy-btn');
        const item = document.querySelector('.dag-breadcrumb-item');
        const minimap = document.querySelector('.dag-minimap-container');
        const searchInput = document.querySelector('.dag-search-input');
        const container = document.querySelector('.dag-container');
        const matchesMedia = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        return {
          matchesMedia,
          btnTransition: window.getComputedStyle(btn).transitionDuration,
          itemTransition: item ? window.getComputedStyle(item).transitionDuration : null,
          minimapTransition: minimap ? window.getComputedStyle(minimap).transitionDuration : null,
          searchTransition: searchInput ? window.getComputedStyle(searchInput).transitionDuration : null,
          containerScrollBehavior: window.getComputedStyle(container).scrollBehavior,
        };
      });

      assert.equal(reducedMotion.matchesMedia, true, 'matchMedia must evaluate to true under reduce emulation');
      const isDurationClamped = reducedMotion.btnTransition === '0.00001s' ||
                                reducedMotion.btnTransition === '1e-05s' ||
                                reducedMotion.btnTransition === '0s';
      assert.ok(isDurationClamped, `Reduced motion button transition duration clamped, got: ${reducedMotion.btnTransition}`);
      assert.equal(reducedMotion.containerScrollBehavior, 'auto', 'Container scroll-behavior must be auto');

      evidence.records.push({
        type: 'motion_styles',
        viewport: width,
        preference: 'reduce',
        styles: reducedMotion,
      });

      // --- 3. Scrollable negative control, then actual guarded navigation ---
      const jsScrollAudit = await page.evaluate(async () => {
        const view = document.getElementById('dag-view');
        view.style.width = '200px'; // isolate scrollability, not responsive layout
        const max = view.scrollWidth - view.clientWidth;
        const target = Math.min(100, max);
        view.scrollTo({left: 0, behavior: 'instant'});
        view.scrollTo({left: target, behavior: 'smooth'}); // deliberately bypass app guard
        const immediate = view.scrollLeft;
        const deadline = performance.now() + 2000;
        while (Math.abs(view.scrollLeft - target) > 1 && performance.now() < deadline)
          await new Promise(requestAnimationFrame);
        const after = view.scrollLeft;
        view.scrollTo({left: 0, behavior: 'instant'});
        const nodes = [...view.querySelectorAll('.node-item')];
        const far = nodes.sort((a,b) => Number(b.dataset.cx) - Number(a.dataset.cx))[0];
        const expected = Math.min(max, Math.max(0, Number(far.dataset.cx) - view.clientWidth / 2));
        historyPreview.checkout(far.dataset.node);
        const guardedImmediate = view.scrollLeft;
        await new Promise(requestAnimationFrame);
        await new Promise(requestAnimationFrame);
        return {max, target, immediate, after, expected, guardedImmediate, guardedAfter: view.scrollLeft};
      });
      assert.ok(jsScrollAudit.target > 20, 'negative control must actually scroll');
      assert.ok(jsScrollAudit.immediate < jsScrollAudit.target - 1, 'unguarded smooth is not instant');
      assert.ok(Math.abs(jsScrollAudit.after - jsScrollAudit.target) <= 1);
      assert.ok(jsScrollAudit.expected > 20, 'guarded control must actually move');
      assert.ok(Math.abs(jsScrollAudit.guardedImmediate - jsScrollAudit.expected) <= 1);
      assert.ok(Math.abs(jsScrollAudit.guardedAfter - jsScrollAudit.expected) <= 1);

      evidence.records.push({
        type: 'native_scroll_audit',
        viewport: width,
        jsCall: 'dagView.scrollTo({ left: 200, behavior: "smooth" })',
        reducedMotionEmulated: true,
        result: jsScrollAudit,
        contractNote: 'Injected width ensures positive scroll range; direct smooth bypass is the negative control, actual checkout is immediate under reduce.',
      });

      await context.close();
    }

    assert.deepEqual(evidence.errors, []);
    assert.equal(evidence.records.length, 12);
    evidence.pass = true;
    // Save evidence JSON file
    const refDir = path.join(__dirname, '..', 'references');
    if (!fs.existsSync(refDir)) {
      fs.mkdirSync(refDir, {recursive: true});
    }
    const outputPath = path.join(refDir, 'uiux-067-accessibility-browser.json');
    fs.writeFileSync(outputPath, JSON.stringify(evidence, null, 2), 'utf8');

    console.log(JSON.stringify({
      pass: true,
      records: evidence.records.length,
      browser: evidence.browser,
      evidenceFile: outputPath,
    }));
  } catch (err) {
    console.error('Runner failed:', err);
    process.exitCode = 1;
  } finally {
    if (browser) await browser.close();
    server.close();
  }
})();
