'use strict';
// UIUX-068: Real Chromium clipboard feedback contrast repair and state matrix runner.
// Tests rendered idle/pending/success/failure crossed with hover off/on at 390/768/1280
// across normal light, forced-colors light, and forced-colors dark (72 records total).
// Reuses Playwright from NODE_PATH=/home/ubuntu/website-security-auditor/node_modules.

const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const {execFileSync} = require('node:child_process');
const http = require('node:http');
const path = require('node:path');
const fs = require('node:fs');

const fixturePy = path.join(__dirname, 'native_clipboard_fixture.py');
const fixture = JSON.parse(execFileSync('python3', ['-B', fixturePy], {encoding: 'utf8'}));

// Exact W3C WCAG 2.1 relative luminance and contrast ratio calculations
function srgbToLinear(c) {
  const v = c / 255.0;
  return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
}

function parseRgb(str) {
  const m = str.match(/rgba?\(\s*([\d\.]+)\s*,\s*([\d\.]+)\s*,\s*([\d\.]+)/);
  if (!m) throw new Error('Cannot parse color: ' + str);
  return [parseFloat(m[1]), parseFloat(m[2]), parseFloat(m[3])];
}

function relativeLuminance(rgbStr) {
  const [r, g, b] = parseRgb(rgbStr);
  return 0.2126 * srgbToLinear(r) + 0.7152 * srgbToLinear(g) + 0.0722 * srgbToLinear(b);
}

function contrastRatio(color1, color2) {
  const l1 = relativeLuminance(color1);
  const l2 = relativeLuminance(color2);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

const evidence = {
  browser: null,
  records: [],
  errors: [],
  pass: false,
  limitations: [
    'Not an official WCAG certification or compliance endorsement',
    'No screen reader speech or synthetic audio announcement claim',
    'No physical high-contrast OS or operating system setting synchronization',
    'Text/backgrounds opaque; translucent system outline composited over recorded opaque adjacent bar by Python gate',
    'Controlled clipboard promises and feedback reset timer; not native clipboard timing or OS clipboard verification',
  ],
};

(async () => {
  const server = http.createServer((req, res) => {
    res.writeHead(200, {
      'Content-Type': 'text/html; charset=utf-8',
      'Cache-Control': 'no-store',
    });
    res.end(fixture.html);
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));

  let browser;
  try {
    const origin = `http://127.0.0.1:${server.address().port}`;
    browser = await chromium.launch({headless: true});
    evidence.browser = browser.version();

    for (const viewport of [390, 768, 1280]) {
      for (const [mode, mediaOpts] of [
        ['normal', {colorScheme: 'light'}],
        ['forced-light', {forcedColors: 'active', colorScheme: 'light'}],
        ['forced-dark', {forcedColors: 'active', colorScheme: 'dark'}],
      ]) {
        const context = await browser.newContext({
          viewport: {width: viewport, height: 1000},
        });
        const page = await context.newPage();
        page.setDefaultTimeout(10000);
        page.on('pageerror', e => evidence.errors.push(String(e)));

        await page.emulateMedia(mediaOpts);
        await page.goto(origin);
        await page.bringToFront();

        // Controlled promise setup and frozen app feedback reset timer
        await page.evaluate(() => {
          const origSetTimeout = window.setTimeout;
          window._feedbackTimers = [];
          // Freeze ONLY app feedback reset timer (1500ms) to avoid expired states
          window.setTimeout = (cb, ms) => {
            if (ms === 1500) {
              window._feedbackTimers.push(cb);
              return 77700 + window._feedbackTimers.length;
            }
            return origSetTimeout(cb, ms);
          };

          window._deferred = null;
          window._copyPromise = null;

          window.setControlledState = async (state) => {
            if (state === 'idle') {
              window.historyPreview.refresh();
            } else if (state === 'pending') {
              window.historyPreview.refresh();
              let resolve, reject;
              const promise = new Promise((res, rej) => { resolve = res; reject = rej; });
              window._deferred = { resolve, reject };
              Object.defineProperty(navigator, 'clipboard', {
                configurable: true,
                value: { writeText: () => promise },
              });
              window._copyPromise = window.historyPreview.copyLineage();
            } else if (state === 'success') {
              if (window._deferred) {
                window._deferred.resolve();
                await window._copyPromise;
                window._deferred = null;
                window._copyPromise = null;
              } else {
                Object.defineProperty(navigator, 'clipboard', {
                  configurable: true,
                  value: { writeText: () => Promise.resolve() },
                });
                await window.historyPreview.copyLineage();
              }
            } else if (state === 'failure') {
              window.historyPreview.refresh();
              Object.defineProperty(navigator, 'clipboard', {
                configurable: true,
                value: { writeText: () => Promise.reject(new Error('clipboard-denied')) },
              });
              await window.historyPreview.copyLineage();
            }
          };
        });

        // Activate native Tab focus onto the breadcrumb copy button
        await page.locator('#outside').focus();
        for (let i = 0; i < 15; i++) {
          const isCopy = await page.evaluate(() =>
            document.activeElement && document.activeElement.classList.contains('dag-breadcrumb-copy-btn')
          );
          if (isCopy) break;
          await page.keyboard.press('Tab');
        }

        // Settle focus transition
        await page.evaluate(async () => { await new Promise(requestAnimationFrame); await Promise.all(document.querySelector('.dag-breadcrumb-copy-btn').getAnimations().map(a => a.finished)); });

        // State loop: idle, pending, success, failure
        for (const state of ['idle', 'pending', 'success', 'failure']) {
          await page.evaluate(s => window.setControlledState(s), state);
          await page.evaluate(async () => { await new Promise(requestAnimationFrame); await Promise.all(document.querySelector('.dag-breadcrumb-copy-btn').getAnimations().map(a => a.finished)); });

          // Hover loop: false, true
          for (const hovered of [false, true]) {
            const btn = page.locator('.dag-breadcrumb-copy-btn');
            if (hovered) {
              await btn.hover();
            } else {
              await page.mouse.move(0, 0);
            }
            // Wait for transition/animation to end
            await page.evaluate(async () => { await new Promise(requestAnimationFrame); await Promise.all(document.querySelector('.dag-breadcrumb-copy-btn').getAnimations().map(a => a.finished)); });

            const metrics = await page.evaluate(() => {
              const b = document.querySelector('.dag-breadcrumb-copy-btn');
              const bar = document.querySelector('.dag-breadcrumbs-bar');
              const statusEl = document.getElementById('status');
              const csBtn = window.getComputedStyle(b);
              const csBar = window.getComputedStyle(bar);
              return {
                focused: document.activeElement === b,
                focusVisible: b.matches(':focus-visible'),
                hoveredMatch: b.matches(':hover'),
                buttonColor: csBtn.color,
                buttonBg: csBtn.backgroundColor,
                adjacentBg: csBar.backgroundColor,
                outlineColor: csBtn.outlineColor,
                outlineWidth: csBtn.outlineWidth,
                outlineOffset: csBtn.outlineOffset,
                outlineStyle: csBtn.outlineStyle,
                opacity: csBtn.opacity,
                forcedColorAdjust: csBtn.forcedColorAdjust,
                transitionProperty: csBtn.transitionProperty,
                animationsRunning: b.getAnimations().filter(a => a.playState === 'running').length,
                buttonBackgroundImage: csBtn.backgroundImage,
                adjacentBackgroundImage: csBar.backgroundImage,
                ancestorOpaque: (() => { for (let p = b.parentElement; p; p = p.parentElement) if (getComputedStyle(p).opacity !== '1') return false; return true; })(),
                borderColor: csBtn.borderColor,
                borderWidth: csBtn.borderWidth,
                borderStyle: csBtn.borderStyle,
                label: b.textContent,
                statusText: statusEl ? statusEl.textContent : '',
                ariaBusy: b.getAttribute('aria-busy') === 'true',
                forcedColorsQuery: window.matchMedia('(forced-colors: active)').matches,
                colorSchemeQuery: window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light',
              };
            });

            assert.equal(metrics.hoveredMatch, hovered);
            assert.equal(metrics.forcedColorsQuery, mode !== 'normal');
            assert.equal(metrics.colorSchemeQuery, mode === 'forced-dark' ? 'dark' : 'light');
            assert.equal(metrics.forcedColorAdjust, 'auto');
            assert.equal(metrics.transitionProperty, 'outline-offset', 'Do not animate opposite-polarity text/background colors');
            assert.equal(typeof metrics.ariaBusy, 'boolean'); // informational; app uses live status, not aria-busy
            // Focus and outline invariants
            assert.equal(metrics.focused, true, `Button must remain focused in ${state}`);
            assert.equal(metrics.focusVisible, true, `Button must match :focus-visible in ${state}`);
            assert.equal(metrics.outlineWidth, '2px', `Outline width must be 2px in ${state}`);
            assert.equal(metrics.outlineOffset, '2px', `Outline offset must be 2px in ${state}`);
            assert.equal(metrics.outlineStyle, 'solid', `Outline style must be solid in ${state}`);
            assert.equal(metrics.opacity, '1', `Button opacity must be 1 in ${state}`);

            // Textual status distinctions
            if (state === 'idle') {
              assert.equal(metrics.label, 'Salin Rute');
            } else if (state === 'pending') {
              assert.equal(metrics.label, 'Menyalin…');
              assert.equal(metrics.statusText, 'Menyalin silsilah rute ke clipboard…');
            } else if (state === 'success') {
              assert.equal(metrics.label, 'Tersalin!');
              assert.equal(metrics.statusText, 'Silsilah rute berhasil disalin ke clipboard');
            } else if (state === 'failure') {
              assert.equal(metrics.label, 'Gagal menyalin');
              assert.equal(metrics.statusText, 'Gagal menyalin silsilah rute ke clipboard');
            }

            const record = {
              viewport,
              mode,
              state,
              hovered,
              hoveredMatch: metrics.hoveredMatch,
              forcedColorAdjust: metrics.forcedColorAdjust,
              transitionProperty: metrics.transitionProperty,
              animationsRunning: metrics.animationsRunning,
              buttonBackgroundImage: metrics.buttonBackgroundImage,
              adjacentBackgroundImage: metrics.adjacentBackgroundImage,
              ancestorOpaque: metrics.ancestorOpaque,
              forcedColors: metrics.forcedColorsQuery,
              colorScheme: metrics.colorSchemeQuery,
              buttonColor: metrics.buttonColor,
              buttonBg: metrics.buttonBg,
              adjacentBg: metrics.adjacentBg,
              outlineColor: metrics.outlineColor,
              outlineWidth: metrics.outlineWidth,
              outlineOffset: metrics.outlineOffset,
              outlineStyle: metrics.outlineStyle,
              focused: metrics.focused,
              focusVisible: metrics.focusVisible,
              opacity: metrics.opacity,
              borderColor: metrics.borderColor,
              borderWidth: metrics.borderWidth,
              borderStyle: metrics.borderStyle,
              label: metrics.label,
              statusText: metrics.statusText,
              ariaBusy: metrics.ariaBusy,
            };

            // Non-forced colors: strict WCAG 2.1 contrast evaluation
            if (mode === 'normal') {
              const textRatio = contrastRatio(record.buttonColor, record.buttonBg);
              const outlineRatio = contrastRatio(record.outlineColor, record.adjacentBg);
              record.textContrastRatio = Math.round(textRatio * 10000) / 10000;
              record.outlineAdjacentContrastRatio = Math.round(outlineRatio * 10000) / 10000;

              assert.ok(
                textRatio >= 4.5,
                `State ${state} hovered=${hovered} text contrast ratio ${textRatio} < 4.5 (${record.buttonColor} on ${record.buttonBg})`
              );
              assert.ok(
                outlineRatio >= 3.0,
                `State ${state} hovered=${hovered} outline contrast ratio ${outlineRatio} < 3.0 against adjacent bar (${record.outlineColor} on ${record.adjacentBg})`
              );
            }

            evidence.records.push(record);
          }
        }

        await context.close();
      }
    }

    // Matrix checks
    assert.equal(evidence.records.length, 72, `Expected exactly 72 records, got ${evidence.records.length}`);
    const keySet = new Set(evidence.records.map(r => `${r.viewport}:${r.mode}:${r.state}:${r.hovered}`));
    assert.equal(keySet.size, 72, 'All 72 matrix combinations must be unique');
    assert.deepEqual(evidence.errors, [], 'No page errors allowed during matrix execution');

    const audit = JSON.parse(execFileSync('python3', ['-B', '-c',
      'import json,sys; from feedback_contrast import audit_matrix; a=audit_matrix(json.load(sys.stdin)); assert a["passed"]; print(json.dumps({k:v for k,v in a.items() if k != "audits"}))'],
      {cwd: __dirname, input: JSON.stringify(evidence.records), encoding: 'utf8'}));
    evidence.audit = audit;
    evidence.pass = true;

    // Save evidence JSON file
    const refDir = path.join(__dirname, '..', 'references');
    if (!fs.existsSync(refDir)) {
      fs.mkdirSync(refDir, {recursive: true});
    }
    const outputPath = path.join(refDir, 'uiux-068-browser.json');
    fs.writeFileSync(outputPath, JSON.stringify(evidence, null, 2), 'utf8');

    console.log(JSON.stringify({
      pass: true,
      records: evidence.records.length,
      browser: evidence.browser,
      evidenceFile: outputPath,
      errors: evidence.errors,
    }));
  } catch (err) {
    console.error('Test runner failed:', err);
    process.exitCode = 1;
  } finally {
    if (browser) await browser.close();
    server.close();
  }
})();
