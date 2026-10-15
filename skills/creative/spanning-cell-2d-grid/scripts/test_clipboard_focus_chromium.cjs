'use strict';
// UIUX-067: Real Chromium clipboard focus continuity, repeated status DOM/AX,
// and deterministic pending promise control across viewports 390, 768, 1280.
// NODE_PATH=/home/ubuntu/website-security-auditor/node_modules node scripts/test_clipboard_focus_chromium.cjs
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const {execFileSync} = require('node:child_process');
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');

const fixture = JSON.parse(
  execFileSync('python3', ['-B', path.join(__dirname, 'native_clipboard_fixture.py')], {
    cwd: __dirname,
    encoding: 'utf8',
  })
);

const evidence = {
  kind: 'Chromium clipboard focus continuity, repeated same-route status DOM/AX, and deterministic pending promise control',
  target: 'UIUX-067',
  limitations: [
    'Not physical system clipboard or cross-application OS paste integration',
    'No native OS permission prompt UI, Firefox/WebKit engines, or audio screen-reader speech output claims',
    'Repeated live-region DOM/AX updates verify DOM textContent and computed accessibility tree nodes, not AT audio speech synthesis or announcement coalescing',
    'Controlled promise tests use deterministic interception on navigator.clipboard.writeText, explicitly distinguished from the native OS clipboard API',
    'Native writeText remains non-cancellable without an AbortSignal; no Escape handler is implemented for clipboard',
  ],
  categories: {
    native_api: 'Real navigator.clipboard.writeText / readText with CDP permissions; no stubs',
    controlled_promise: 'Deterministic promise holding to test user focus shifts while pending, settlement, refresh, and dispose',
    lifecycle_focus: 'Differential focus restoration on refresh (only restored if old copy button held focus)',
    motion: 'Verification of matchMedia prefers-reduced-motion in autoCenterViewport and search camera scrolling',
  },
  records: [],
  errors: [],
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
    evidence.origin = origin;
    browser = await chromium.launch({headless: true});
    evidence.browser = browser.version();

    for (const width of [390, 768, 1280]) {
      const context = await browser.newContext({viewport: {width, height: 1100}});
      const page = await context.newPage();
      page.setDefaultTimeout(10000);
      page.on('pageerror', e => evidence.errors.push(String(e)));

      await page.goto(origin);
      await page.bringToFront();

      const cdp = await context.newCDPSession(page);
      const {browserContextId} = (await cdp.send('Target.getTargetInfo')).targetInfo;

      const permission = async write => {
        for (const [name, setting] of [
          ['clipboard-read', 'granted'],
          ['clipboard-write', write],
        ]) {
          await cdp.send('Browser.setPermission', {
            permission: {name},
            setting,
            origin,
            browserContextId,
          });
        }
        const state = await page.evaluate(async () => ({
          read: (await navigator.permissions.query({name: 'clipboard-read'})).state,
          write: (await navigator.permissions.query({name: 'clipboard-write'})).state,
        }));
        assert.deepEqual(state, {read: 'granted', write});
        return state;
      };

      const button = page.locator('.dag-breadcrumb-copy-btn');
      const read = () => page.evaluate(() => navigator.clipboard.readText());

      const uiState = () =>
        button.evaluate(b => ({
          text: b.textContent,
          ariaLabel: b.getAttribute('aria-label'),
          copied: b.classList.contains('copied'),
          focused: document.activeElement === b,
          connected: b.isConnected,
          disabled: b.disabled,
        }));

      const axStatus = async () => {
        const ax = await cdp.send('Accessibility.getFullAXTree');
        const sNode = ax.nodes.find(n => n.role?.value === 'status');
        const sTextNode = sNode ? ax.nodes.find(n => (sNode.childIds || []).includes(n.nodeId)) : null;
        const bNode = ax.nodes.find(
          n =>
            n.role?.value === 'button' &&
            (n.name?.value?.includes('disalin') ||
              n.name?.value?.includes('menyalin') ||
              n.name?.value === 'Salin seluruh jejak silsilah rute ke clipboard')
        );
        return {
          statusRole: sNode?.role?.value || null,
          statusText: sTextNode?.name?.value || sNode?.name?.value || null,
          buttonName: bNode?.name?.value || null,
        };
      };

      // Native boundary check
      const native = await page.evaluate(() => ({
        secure: isSecureContext,
        focused: document.hasFocus(),
        write: Function.prototype.toString.call(navigator.clipboard.writeText),
        read: Function.prototype.toString.call(navigator.clipboard.readText),
        own: Object.hasOwn(navigator, 'clipboard'),
      }));
      assert.equal(native.secure, true);
      assert.equal(native.focused, true);
      assert.equal(native.own, false);
      assert.match(native.write, /\[native code\]/);
      assert.match(native.read, /\[native code\]/);

      // --- SCENARIO 1: Native repeated same-route success status updates (DOM + AX)
      await permission('granted');
      const seed1 = `UIUX-067 seed 1 ${width}`;
      await page.evaluate(s => navigator.clipboard.writeText(s), seed1);
      assert.equal(await read(), seed1);

      await button.focus();
      assert.equal((await uiState()).focused, true);

      // Activation 1 (Enter)
      await button.evaluate(b => {
        window.__copyObs = {clicks: []};
        b.addEventListener('click', e => {
          window.__copyObs.clicks.push({
            trusted: e.isTrusted,
            pendingText: b.textContent,
            pendingStatus: document.getElementById('status').textContent,
            focused: document.activeElement === b,
          });
        }, {once: true});
      });
      await page.keyboard.press('Enter');
      await page.waitForFunction(() => document.querySelector('.dag-breadcrumb-copy-btn').textContent === 'Tersalin!');

      const obs1 = await page.evaluate(() => window.__copyObs.clicks[0]);
      assert.equal(obs1.trusted, true);
      assert.equal(obs1.pendingText, 'Menyalin…');
      assert.equal(obs1.pendingStatus, 'Menyalin silsilah rute ke clipboard…');
      assert.equal(obs1.focused, true);

      let text1 = await read();
      assert.equal(text1, fixture.initial.text);
      let ui1 = await uiState();
      assert.equal(ui1.focused, true, 'focus retained after activation 1');
      assert.equal(ui1.copied, true);
      let domStatus1 = await page.evaluate(() => document.getElementById('status').textContent);
      let ax1 = await axStatus();
      assert.equal(domStatus1, 'Silsilah rute berhasil disalin ke clipboard');
      assert.equal(ax1.statusText, 'Silsilah rute berhasil disalin ke clipboard');

      // Activation 2: REPEATED activation on the EXACT SAME ROUTE (Space)
      await button.evaluate(b => {
        window.__copyObs = {clicks: []};
        b.addEventListener('click', e => {
          window.__copyObs.clicks.push({
            trusted: e.isTrusted,
            pendingText: b.textContent,
            pendingStatus: document.getElementById('status').textContent,
            focused: document.activeElement === b,
          });
        }, {once: true});
      });
      await page.keyboard.press('Space');
      await page.waitForFunction(() => document.querySelector('.dag-breadcrumb-copy-btn').textContent === 'Tersalin!');

      const obs2 = await page.evaluate(() => window.__copyObs.clicks[0]);
      assert.equal(obs2.trusted, true);
      assert.equal(obs2.pendingText, 'Menyalin…');
      assert.equal(obs2.pendingStatus, 'Menyalin silsilah rute ke clipboard…');
      assert.equal(obs2.focused, true);

      let text2 = await read();
      assert.equal(text2, fixture.initial.text);
      let ui2 = await uiState();
      assert.equal(ui2.focused, true, 'focus retained after repeated same-route activation 2');
      assert.equal(ui2.copied, true);
      let domStatus2 = await page.evaluate(() => document.getElementById('status').textContent);
      let ax2 = await axStatus();
      assert.equal(domStatus2, 'Silsilah rute berhasil disalin ke clipboard');
      assert.equal(ax2.statusText, 'Silsilah rute berhasil disalin ke clipboard');

      evidence.records.push({
        width,
        case: 'repeated-same-route-success-dom-ax',
        category: 'native_api',
        controlledPromise: false,
        activations: 2,
        route: fixture.initial.text,
        domStatus: domStatus2,
        ax: ax2,
        ui: ui2,
        focusPreserved: ui1.focused && ui2.focused,
        atSpeechClaim: false,
        note: 'Repeated same-route DOM and AX status updates verified; not screen-reader speech output',
        pass: true,
      });

      // --- SCENARIO 2: Native repeated same-route denial status updates (DOM + AX)
      await permission('denied');
      const seedDenial = `UIUX-067 denial seed ${width}`;
      // Direct set via permission granted first, then deny
      await permission('granted');
      await page.evaluate(s => navigator.clipboard.writeText(s), seedDenial);
      assert.equal(await read(), seedDenial);
      await permission('denied');

      await button.focus();
      assert.equal((await uiState()).focused, true);

      // Denial Activation 1 (Enter)
      await button.evaluate(b => {
        window.__copyObs = {clicks: []};
        b.addEventListener('click', e => {
          window.__copyObs.clicks.push({
            trusted: e.isTrusted,
            pendingText: b.textContent,
            pendingStatus: document.getElementById('status').textContent,
            focused: document.activeElement === b,
          });
        }, {once: true});
      });
      await page.keyboard.press('Enter');
      await page.waitForFunction(() => document.querySelector('.dag-breadcrumb-copy-btn').textContent === 'Gagal menyalin');

      const obsDenial1 = await page.evaluate(() => window.__copyObs.clicks[0]);
      assert.equal(obsDenial1.pendingText, 'Menyalin…');
      assert.equal(obsDenial1.pendingStatus, 'Menyalin silsilah rute ke clipboard…');
      assert.equal(obsDenial1.focused, true);

      let textDenial1 = await read();
      assert.equal(textDenial1, seedDenial, 'denied write retains prior seed');
      let uiDenial1 = await uiState();
      assert.equal(uiDenial1.focused, true);
      assert.equal(uiDenial1.copied, false);
      let domStatusDenial1 = await page.evaluate(() => document.getElementById('status').textContent);
      let axDenial1 = await axStatus();
      assert.equal(domStatusDenial1, 'Gagal menyalin silsilah rute ke clipboard');
      assert.equal(axDenial1.statusText, 'Gagal menyalin silsilah rute ke clipboard');

      // Denial Activation 2: REPEATED denial on the EXACT SAME ROUTE (Space)
      await button.evaluate(b => {
        window.__copyObs = {clicks: []};
        b.addEventListener('click', e => {
          window.__copyObs.clicks.push({
            trusted: e.isTrusted,
            pendingText: b.textContent,
            pendingStatus: document.getElementById('status').textContent,
            focused: document.activeElement === b,
          });
        }, {once: true});
      });
      await page.keyboard.press('Space');
      await page.waitForFunction(() => document.querySelector('.dag-breadcrumb-copy-btn').textContent === 'Gagal menyalin');

      const obsDenial2 = await page.evaluate(() => window.__copyObs.clicks[0]);
      assert.equal(obsDenial2.pendingText, 'Menyalin…');
      assert.equal(obsDenial2.pendingStatus, 'Menyalin silsilah rute ke clipboard…');
      assert.equal(obsDenial2.focused, true);

      let textDenial2 = await read();
      assert.equal(textDenial2, seedDenial, 'repeated denial retains prior seed');
      let uiDenial2 = await uiState();
      assert.equal(uiDenial2.focused, true);
      assert.equal(uiDenial2.copied, false);
      let domStatusDenial2 = await page.evaluate(() => document.getElementById('status').textContent);
      let axDenial2 = await axStatus();
      assert.equal(domStatusDenial2, 'Gagal menyalin silsilah rute ke clipboard');
      assert.equal(axDenial2.statusText, 'Gagal menyalin silsilah rute ke clipboard');

      evidence.records.push({
        width,
        case: 'repeated-same-route-denial-dom-ax',
        category: 'native_api',
        controlledPromise: false,
        activations: 2,
        domStatus: domStatusDenial2,
        ax: axDenial2,
        ui: uiDenial2,
        clipboardRetained: true,
        focusPreserved: uiDenial1.focused && uiDenial2.focused,
        pass: true,
      });

      // --- SCENARIO 3: Native permission recovery after repeated denial
      await permission('granted');
      await button.focus();
      // Recovery proves a new successful native write; do not infer cancellation timing.
      await page.keyboard.press('Enter');
      await page.waitForFunction(() => document.querySelector('.dag-breadcrumb-copy-btn').textContent === 'Tersalin!');
      const recoveryText = await read();
      assert.equal(recoveryText, fixture.initial.text, 'native write succeeds after permission recovery');

      // Verify search input Escape behavior is preserved (clears search query and blurs)
      const searchInput = page.locator('#dag-search-input');
      await searchInput.focus();
      await page.keyboard.type('alpha');
      assert.equal(await page.evaluate(() => historyPreview.searchQuery()), 'alpha');
      await page.keyboard.press('Escape');
      assert.equal(await page.evaluate(() => historyPreview.searchQuery()), '');
      assert.notEqual(await page.evaluate(() => document.activeElement?.id), 'dag-search-input');

      evidence.records.push({
        width,
        case: 'native-permission-recovery-search-regression',
        category: 'native_api',
        controlledPromise: false,
        completed: true,
        searchEscapePreserved: true,
        pass: true,
      });

      // =========================================================================
      // CONTROLLED PROMISE HARNESS INSTALLATION
      // Explicitly distinguished from the native API tested above.
      // =========================================================================
      await page.evaluate(() => {
        window.__ctrl = {
          pending: null,
          install() {
            this.orig = navigator.clipboard.writeText.bind(navigator.clipboard);
            navigator.clipboard.writeText = (txt) =>
              new Promise((resolve, reject) => {
                window.__ctrl.pending = {resolve, reject, txt};
              });
          },
          resolve() {
            if (this.pending) {
              const p = this.pending;
              this.pending = null;
              p.resolve();
            }
          },
          reject(err) {
            if (this.pending) {
              const p = this.pending;
              this.pending = null;
              p.reject(err || new Error('controlled rejection'));
            }
          },
          restore() {
            if (this.orig) {
              navigator.clipboard.writeText = this.orig;
            }
            this.pending = null;
          },
        };
        window.__ctrl.install();
      });

      // --- SCENARIO 4: Controlled pending promise -> user Tab focus -> settlement without theft
      await button.focus();
      assert.equal((await uiState()).focused, true);

      // Trigger copy: Enter initiates pending promise
      await page.keyboard.press('Enter');
      await page.waitForFunction(() => document.querySelector('.dag-breadcrumb-copy-btn').textContent === 'Menyalin…');
      assert.equal(await page.evaluate(() => Boolean(window.__ctrl.pending)), true, 'writeText must be pending');

      // User presses Tab to move focus away while write is pending
      await page.keyboard.press('Tab');
      const activeWhilePending = await page.evaluate(() => ({
        tag: document.activeElement.tagName.toLowerCase(),
        id: document.activeElement.id || null,
        className: document.activeElement.className?.baseVal || document.activeElement.className || '',
        isCopyBtn: document.activeElement.classList.contains('dag-breadcrumb-copy-btn'),
      }));
      assert.equal(activeWhilePending.isCopyBtn, false, 'focus must have moved away from copy button via Tab');

      await page.evaluate(() => { window.__pendingFocusOwner = document.activeElement; });
      // Now resolve the controlled pending promise
      await page.evaluate(() => window.__ctrl.resolve());
      await page.waitForFunction(() => document.querySelector('.dag-breadcrumb-copy-btn').textContent === 'Tersalin!');

      // THEFT CHECK: focus must NOT be stolen back to the copy button!
      const activeAfterSettlement = await page.evaluate(() => ({
        tag: document.activeElement.tagName.toLowerCase(),
        id: document.activeElement.id || null,
        className: document.activeElement.className?.baseVal || document.activeElement.className || '',
        isCopyBtn: document.activeElement.classList.contains('dag-breadcrumb-copy-btn'),
      }));
      assert.equal(activeAfterSettlement.isCopyBtn, false, 'settlement must not steal focus back to copy button');
      assert.deepEqual(activeAfterSettlement, activeWhilePending, 'focus must stay on the tabbed element');
      assert.equal(await page.evaluate(() => document.activeElement === window.__pendingFocusOwner), true);

      evidence.records.push({
        width,
        case: 'controlled-pending-tab-focus-settlement-no-theft',
        category: 'controlled_promise',
        controlledPromise: true,
        activeWhilePending,
        activeAfterSettlement,
        theftDetected: false,
        pass: true,
      });

      // --- SCENARIO 5: Controlled pending promise -> user focuses search -> settlement without theft
      // Reset button to clean state
      await page.evaluate(() => historyPreview.refresh());
      await button.focus();
      assert.equal((await uiState()).focused, true);

      // Trigger copy
      await page.keyboard.press('Enter');
      await page.waitForFunction(() => document.querySelector('.dag-breadcrumb-copy-btn').textContent === 'Menyalin…');
      assert.equal(await page.evaluate(() => Boolean(window.__ctrl.pending)), true);

      // User moves focus to #dag-search-input while write is pending
      await page.focus('#dag-search-input');
      assert.equal(await page.evaluate(() => document.activeElement?.id), 'dag-search-input');

      // Now reject the controlled pending promise (e.g. denied write)
      await page.evaluate(() => window.__ctrl.reject());
      await page.waitForFunction(() => document.querySelector('.dag-breadcrumb-copy-btn').textContent === 'Gagal menyalin');

      // THEFT CHECK: focus must remain on search input
      assert.equal(
        await page.evaluate(() => document.activeElement?.id),
        'dag-search-input',
        'settlement rejection must not steal focus from search input'
      );

      evidence.records.push({
        width,
        case: 'controlled-pending-search-focus-settlement-no-theft',
        category: 'controlled_promise',
        controlledPromise: true,
        activeElement: 'dag-search-input',
        theftDetected: false,
        pass: true,
      });

      // --- SCENARIO 6: Controlled pending promise -> search focus -> refresh -> stale completion
      await button.focus();
      await page.keyboard.press('Enter');
      await page.waitForFunction(() => document.querySelector('.dag-breadcrumb-copy-btn').textContent === 'Menyalin…');
      assert.equal(await page.evaluate(() => Boolean(window.__ctrl.pending)), true);

      // Focus search input
      await page.focus('#dag-search-input');
      assert.equal(await page.evaluate(() => document.activeElement?.id), 'dag-search-input');

      // Call refresh while write is still pending
      await page.evaluate(() => historyPreview.refresh());

      // REFRESH CHECK: replacement copy button must NOT steal focus
      assert.equal(
        await page.evaluate(() => document.activeElement?.id),
        'dag-search-input',
        'refresh must not steal focus when old copy button did not hold focus'
      );
      assert.equal(await page.evaluate(() => document.querySelector('.dag-breadcrumb-copy-btn').textContent), 'Salin Rute');

      const neutralRefreshStatus = await page.locator('#status').textContent();
      assert.match(neutralRefreshStatus, /^Versi /);
      // Now resolve the stale pending promise
      await page.evaluate(() => window.__ctrl.resolve());
      await page.evaluate(() => new Promise(r => setTimeout(r, 50)));

      assert.equal(await page.locator('#status').textContent(), neutralRefreshStatus);
      // STALE CHECK: replacement button and status must not be mutated, focus intact
      assert.equal(
        await page.evaluate(() => document.querySelector('.dag-breadcrumb-copy-btn').textContent),
        'Salin Rute',
        'stale completion must not mutate replacement button'
      );
      assert.equal(
        await page.evaluate(() => document.activeElement?.id),
        'dag-search-input',
        'stale completion must not steal focus'
      );

      evidence.records.push({
        width,
        case: 'controlled-pending-search-focus-refresh-stale-completion',
        category: 'controlled_promise',
        controlledPromise: true,
        refreshTheftDetected: false,
        staleMutationDetected: false,
        activeElement: 'dag-search-input',
        pass: true,
      });

      // --- SCENARIO 7: Controlled pending promise -> search focus -> dispose -> stale completion
      await page.evaluate(() => historyPreview.refresh());
      await button.focus();
      await page.keyboard.press('Enter');
      await page.waitForFunction(() => document.querySelector('.dag-breadcrumb-copy-btn').textContent === 'Menyalin…');
      assert.equal(await page.evaluate(() => Boolean(window.__ctrl.pending)), true);

      // Focus search input
      await page.focus('#dag-search-input');
      assert.equal(await page.evaluate(() => document.activeElement?.id), 'dag-search-input');

      // Call disposeClipboard while write is still pending
      const disposed = await page.evaluate(() => historyPreview.disposeClipboard());
      assert.equal(disposed, true);

      // DISPOSE CHECK: button disabled, status neutral, focus unchanged
      const uiDisposed = await uiState();
      assert.equal(uiDisposed.disabled, true);
      const statusDisposed = await page.evaluate(() => document.getElementById('status').textContent);
      assert.match(statusDisposed, /^Versi /);
      assert.equal(
        await page.evaluate(() => document.activeElement?.id),
        'dag-search-input',
        'disposal must not steal focus'
      );

      // Now resolve the stale pending promise after disposal
      await page.evaluate(() => window.__ctrl.resolve());
      await page.evaluate(() => new Promise(r => setTimeout(r, 50)));

      // STALE DISPOSE CHECK: button remains disabled, status remains neutral, focus intact
      assert.equal((await uiState()).disabled, true);
      assert.equal((await uiState()).text, 'Salin Rute');
      assert.equal(await page.evaluate(() => document.getElementById('status').textContent), statusDisposed);
      assert.equal(await page.evaluate(() => document.activeElement?.id), 'dag-search-input');

      evidence.records.push({
        width,
        case: 'controlled-pending-search-focus-dispose-stale-completion',
        category: 'controlled_promise',
        controlledPromise: true,
        disposedButtonDisabled: true,
        disposedStatusNeutral: true,
        staleMutationDetected: false,
        activeElement: 'dag-search-input',
        pass: true,
      });

      // Restore native clipboard
      await page.evaluate(() => window.__ctrl.restore());

      // --- SCENARIO 8: Refresh focus restoration differential (only when old copy button owned focus)
      // Reload page to reset disposed state cleanly
      await page.goto(origin);
      await page.bringToFront();

      // Case 8A: Copy button HAS focus before refresh -> replacement receives focus
      await button.focus();
      assert.equal((await uiState()).focused, true);
      await page.evaluate(() => historyPreview.refresh());
      assert.equal((await uiState()).focused, true, 'refresh restores focus when old copy button had focus');

      // Case 8B: #undo button HAS focus before refresh -> replacement does NOT receive focus
      await page.focus('#undo');
      assert.equal(await page.evaluate(() => document.activeElement?.id), 'undo');
      await page.evaluate(() => historyPreview.refresh());
      assert.equal(await page.evaluate(() => document.activeElement?.id), 'undo', 'focus remains on #undo after refresh');
      assert.equal((await uiState()).focused, false, 'copy button must NOT receive focus when #undo had focus');

      evidence.records.push({
        width,
        case: 'refresh-focus-restoration-differential',
        category: 'lifecycle_focus',
        controlledPromise: false,
        focusedWhenOwned: true,
        unfocusedWhenNotOwned: true,
        pass: true,
      });

      // --- SCENARIO 9: Reduced motion decision in autoCenterViewport & search
      // Spy on dagView.scrollTo
      await page.evaluate(() => {
        window.__scrollToCalls = [];
        const view = document.getElementById('dag-view');
        const orig = view.scrollTo.bind(view);
        view.scrollTo = function(opt) {
          window.__scrollToCalls.push(opt);
          return orig(opt);
        };
      });

      // Step 9A: Emulate prefers-reduced-motion: reduce
      await page.emulateMedia({reducedMotion: 'reduce'});
      assert.equal(await page.evaluate(() => historyPreview.prefersReducedMotion()), true);
      await page.evaluate(() => historyPreview.checkout('root'));
      const callReduce = await page.evaluate(() => window.__scrollToCalls.pop());
      assert.equal(callReduce.behavior, 'auto', 'autoCenterViewport must use behavior: auto under reduced motion');

      // Step 9B: Emulate prefers-reduced-motion: no-preference
      await page.emulateMedia({reducedMotion: 'no-preference'});
      assert.equal(await page.evaluate(() => historyPreview.prefersReducedMotion()), false);
      await page.evaluate(() => historyPreview.checkout('alpha'));
      const callNoPref = await page.evaluate(() => window.__scrollToCalls.pop());
      assert.equal(callNoPref.behavior, 'smooth', 'autoCenterViewport must use behavior: smooth under no-preference');

      // Step 9C: Search camera auto-centering under reduced motion
      await page.emulateMedia({reducedMotion: 'reduce'});
      await page.evaluate(() => historyPreview.search('root'));
      const callSearchReduce = await page.evaluate(() => window.__scrollToCalls.pop());
      assert.equal(callSearchReduce.behavior, 'auto', 'search autoCenterViewport must use behavior: auto under reduced motion');

      evidence.records.push({
        width,
        case: 'reduced-motion-autocenter-decision',
        category: 'motion',
        controlledPromise: false,
        reduceBehavior: callReduce.behavior,
        noPreferenceBehavior: callNoPref.behavior,
        searchReduceBehavior: callSearchReduce.behavior,
        pass: true,
      });

      await context.close();
    }

    assert.equal(evidence.records.length, 27, '9 scenarios across 3 viewports = 27 records');
    assert.deepEqual(evidence.errors, []);
    evidence.pass = true;
  } catch (e) {
    evidence.pass = false;
    evidence.failure = String(e);
    throw e;
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
    const outPath = path.join(__dirname, '../references/uiux-067-focus-browser.json');
    fs.writeFileSync(outPath, JSON.stringify(evidence, null, 2) + '\n');
  }
  console.log(
    JSON.stringify({
      pass: evidence.pass,
      records: evidence.records.length,
      browser: evidence.browser,
      origin: evidence.origin,
    })
  );
})().catch(e => {
  console.error(e);
  process.exit(1);
});
