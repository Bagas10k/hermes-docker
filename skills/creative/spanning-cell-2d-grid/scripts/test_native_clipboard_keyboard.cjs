'use strict';
// UIUX-066: Native clipboard keyboard activation (Enter/Space) and focus continuity
// Under granted -> denied -> recovered write permissions across viewports 390, 768, 1280.
// NODE_PATH=<installed Playwright node_modules> node scripts/test_native_clipboard_keyboard.cjs
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const {execFileSync} = require('node:child_process');
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');

const fixture = JSON.parse(execFileSync('python3', ['-B', path.join(__dirname, 'native_clipboard_fixture.py')], {encoding: 'utf8'}));

const evidence = {
  kind: 'native headless Chromium clipboard keyboard activation; loopback secure context; CDP permission intervention',
  limitations: [
    'Not physical system clipboard or cross-application paste integration',
    'No native OS permission prompt UI, other browser engine, or screen-reader speech output claim',
    'CDP AX tree verification represents computed accessibility nodes, not end-user screen-reader audio experience',
  ],
  records: [],
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
      const context = await browser.newContext({viewport: {width, height: 1100}});
      const page = await context.newPage();
      page.setDefaultTimeout(10000);
      page.on('pageerror', e => evidence.errors.push(String(e)));

      await page.goto(origin);
      await page.bringToFront();

      const cdp = await context.newCDPSession(page);
      const {browserContextId} = (await cdp.send('Target.getTargetInfo')).targetInfo;

      const permission = async write => {
        for (const [name, setting] of [['clipboard-read', 'granted'], ['clipboard-write', write]]) {
          await cdp.send('Browser.setPermission', {permission: {name}, setting, origin, browserContextId});
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
      // Observe native activation; do not stub clipboard, timers or click().
      const activate = async (key, label) => {
        await button.evaluate(b => {
          const o = window.copyObservation = {button:b, clicks:[]};
          o.observe = e => o.clicks.push({
            trusted:e.isTrusted, detail:e.detail, pending:b.textContent,
            status:document.getElementById('status').textContent,
            focused:document.activeElement===b
          });
          b.addEventListener('click', o.observe);
        });
        await page.keyboard.press(key);
        await page.waitForFunction(expected =>
          window.copyObservation.clicks.length === 1 &&
          window.copyObservation.button.textContent === expected, label);
        const observation = await page.evaluate(() => {
          const o=window.copyObservation;
          o.button.removeEventListener('click', o.observe);
          return {clicks:o.clicks, same:document.querySelector('.dag-breadcrumb-copy-btn')===o.button,
            focused:document.activeElement===o.button, connected:o.button.isConnected};
        });
        assert.deepEqual(observation, {clicks:[{trusted:true,detail:0,pending:'Menyalin…',
          status:'Menyalin silsilah rute ke clipboard…',focused:true}],same:true,focused:true,connected:true});
        return observation;
      };

      const uiState = () => button.evaluate(b => ({
        text: b.textContent,
        ariaLabel: b.getAttribute('aria-label'),
        copied: b.classList.contains('copied'),
        focused: document.activeElement === b,
        connected: b.isConnected,
      }));

      const axStatus = async () => {
        const ax = await cdp.send('Accessibility.getFullAXTree');
        const sNode = ax.nodes.find(n => n.role?.value === 'status');
        const sTextNode = sNode ? ax.nodes.find(n => (sNode.childIds || []).includes(n.nodeId)) : null;
        const bNode = ax.nodes.find(n => n.role?.value === 'button' && (
          n.name?.value?.includes('disalin') ||
          n.name?.value?.includes('menyalin') ||
          n.name?.value === 'Salin seluruh jejak silsilah rute ke clipboard'
        ));
        return {
          statusRole: sNode?.role?.value || null,
          statusText: sTextNode?.name?.value || sNode?.name?.value || null,
          buttonName: bNode?.name?.value || null,
        };
      };

      // Native boundary verification
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

      // --- 1. Granted: Enter activates copy, retains focus on same connected button
      let states = await permission('granted');
      const seedEnter = `UIUX-066 seed enter ${width}`;
      await page.evaluate(s => navigator.clipboard.writeText(s), seedEnter);
      assert.equal(await read(), seedEnter);

      await button.focus();
      let ui = await uiState();
      assert.equal(ui.focused, true, 'button must accept initial focus');

      await activate('Enter', 'Tersalin!');
      ui = await uiState();
      let text = await read();
      const domStatusEnter = await page.evaluate(() => document.getElementById('status').textContent);
      const axEnter = await axStatus();

      assert.equal(text, fixture.initial.text, 'Enter must copy exact route text');
      assert.equal(ui.focused, true, 'Enter must preserve focus on the same button');
      assert.equal(ui.connected, true, 'Button must remain connected in DOM');
      assert.equal(ui.copied, true, 'Button must have copied class on success');
      assert.equal(domStatusEnter, 'Silsilah rute berhasil disalin ke clipboard');
      assert.equal(axEnter.statusText, 'Silsilah rute berhasil disalin ke clipboard');
      assert.equal(axEnter.buttonName, 'Silsilah rute berhasil disalin ke clipboard');

      evidence.records.push({
        width,
        nativeActivationChecked: true, pendingFocusChecked: true, sameButtonChecked: true,
        case: 'enter-granted-exact-route',
        key: 'Enter',
        states,
        native,
        ui,
        text,
        domStatus: domStatusEnter,
        ax: axEnter,
        pass: true,
      });

      // --- 2. Sensible Tab & Shift+Tab navigation continuation
      await button.focus();
      assert.equal((await uiState()).focused, true);

      // Shift+Tab should move to the preceding active breadcrumb item
      await page.keyboard.press('Shift+Tab');
      const prevElement = await page.evaluate(() => ({
        tag: document.activeElement.tagName.toLowerCase(),
        node: document.activeElement.getAttribute('data-breadcrumb-node'),
        isActive: document.activeElement.classList.contains('active'),
      }));
      assert.equal(prevElement.tag, 'button');
      assert.equal(prevElement.node, fixture.initial.id);
      assert.equal(prevElement.isActive, true);

      // Tab moves back to copy button
      await page.keyboard.press('Tab');
      assert.equal((await uiState()).focused, true, 'Tab must return focus to copy button');

      // Tab moves forward to next interactive element in document
      await page.keyboard.press('Tab');
      const nextElement = await page.evaluate(() => ({
        tag: document.activeElement.tagName.toLowerCase(),
        className: document.activeElement.className?.baseVal || document.activeElement.className || '',
      }));
      assert.ok(nextElement.className.includes('node-item') || nextElement.className.includes('dag-minimap'));

      // Shift+Tab returns cleanly to copy button
      await page.keyboard.press('Shift+Tab');
      assert.equal((await uiState()).focused, true, 'Shift+Tab must return focus to copy button from next item');

      evidence.records.push({
        width,
        case: 'keyboard-tab-shift-tab-continuation',
        prevElement,
        nextElement,
        focusPreserved: true,
        pass: true,
      });

      // --- 3. Granted: Space activates copy, no page scroll, retains focus
      const seedSpace = `UIUX-066 seed space ${width}`;
      await page.evaluate(s => navigator.clipboard.writeText(s), seedSpace);
      assert.equal(await read(), seedSpace);

      const scrollBefore = await page.evaluate(() => window.scrollY);
      await button.focus();
      await activate('Space', 'Tersalin!');
      const scrollAfter = await page.evaluate(() => window.scrollY);

      ui = await uiState();
      text = await read();
      const domStatusSpace = await page.evaluate(() => document.getElementById('status').textContent);
      const axSpace = await axStatus();

      assert.equal(text, fixture.initial.text, 'Space must copy exact route text');
      assert.equal(scrollAfter, scrollBefore, 'Space must not scroll page');
      assert.equal(ui.focused, true, 'Space must preserve focus on the same button');
      assert.equal(ui.connected, true);
      assert.equal(domStatusSpace, 'Silsilah rute berhasil disalin ke clipboard');
      assert.equal(axSpace.statusText, 'Silsilah rute berhasil disalin ke clipboard');

      evidence.records.push({
        width,
        case: 'space-granted-no-scroll',
        key: 'Space',
        scrollBefore,
        scrollAfter,
        ui,
        text,
        domStatus: domStatusSpace,
        ax: axSpace,
        pass: true,
      });

      // --- 4. Denied: Enter reports failure, retains prior clipboard, retains focus
      await page.evaluate(() => historyPreview.refresh());
      assert.equal((await uiState()).focused, true, 'refresh restores focus to replacement copy control');
      // Explicit checkout deliberately moves focus into branch navigation.
      await page.evaluate(id => historyPreview.checkout(id), fixture.recovery.id);
      states = await permission('denied');

      const rejection = await page.evaluate(async () => {
        try {
          await navigator.clipboard.writeText('denied write test');
          return null;
        } catch (e) {
          return {name: e.name, message: e.message};
        }
      });
      assert.equal(rejection?.name, 'NotAllowedError');

      await button.focus();
      await activate('Enter', 'Gagal menyalin');

      ui = await uiState();
      text = await read();
      const domStatusDeniedEnter = await page.evaluate(() => document.getElementById('status').textContent);
      const axDeniedEnter = await axStatus();

      assert.equal(text, fixture.initial.text, 'Denied write must preserve prior clipboard content');
      assert.equal(ui.focused, true, 'Focus must survive denied write');
      assert.equal(ui.connected, true);
      assert.equal(ui.copied, false, 'Button must not have copied class on denial');
      assert.equal(domStatusDeniedEnter, 'Gagal menyalin silsilah rute ke clipboard');
      assert.equal(axDeniedEnter.statusText, 'Gagal menyalin silsilah rute ke clipboard');
      assert.equal(axDeniedEnter.buttonName, 'Gagal menyalin silsilah rute ke clipboard');

      evidence.records.push({
        width,
        case: 'enter-denied-retains-clipboard',
        key: 'Enter',
        states,
        rejection,
        ui,
        text,
        domStatus: domStatusDeniedEnter,
        ax: axDeniedEnter,
        pass: true,
      });

      // --- 5. Denied: Space reports failure, retains prior clipboard, retains focus
      await button.focus();
      await activate('Space', 'Gagal menyalin');

      ui = await uiState();
      text = await read();
      const domStatusDeniedSpace = await page.evaluate(() => document.getElementById('status').textContent);
      const axDeniedSpace = await axStatus();

      assert.equal(text, fixture.initial.text, 'Space denied write must preserve prior clipboard content');
      assert.equal(ui.focused, true, 'Focus must survive Space denied write');
      assert.equal(ui.connected, true);
      assert.equal(domStatusDeniedSpace, 'Gagal menyalin silsilah rute ke clipboard');
      assert.equal(axDeniedSpace.statusText, 'Gagal menyalin silsilah rute ke clipboard');

      evidence.records.push({
        width,
        case: 'space-denied-retains-clipboard',
        key: 'Space',
        states,
        ui,
        text,
        domStatus: domStatusDeniedSpace,
        ax: axDeniedSpace,
        pass: true,
      });

      // --- 6. Recovered: Enter copies new route after permission restored
      states = await permission('granted');

      await button.focus();
      await activate('Enter', 'Tersalin!');

      ui = await uiState();
      text = await read();
      const domStatusRecoveredEnter = await page.evaluate(() => document.getElementById('status').textContent);
      const axRecoveredEnter = await axStatus();

      assert.equal(text, fixture.recovery.text, 'Recovered Enter must copy new active route');
      assert.equal(ui.focused, true, 'Focus must remain on copy button after recovery');
      assert.equal(ui.connected, true);
      assert.equal(ui.copied, true);
      assert.equal(domStatusRecoveredEnter, 'Silsilah rute berhasil disalin ke clipboard');
      assert.equal(axRecoveredEnter.statusText, 'Silsilah rute berhasil disalin ke clipboard');
      assert.equal(axRecoveredEnter.buttonName, 'Silsilah rute berhasil disalin ke clipboard');

      evidence.records.push({
        width,
        case: 'enter-permission-recovery-new-route',
        key: 'Enter',
        states,
        ui,
        text,
        domStatus: domStatusRecoveredEnter,
        ax: axRecoveredEnter,
        pass: true,
      });

      // --- 7. Recovered: Space copies new route with distinct seed
      const seedSpaceRecovery = `UIUX-066 recovery space seed ${width}`;
      await page.evaluate(s => navigator.clipboard.writeText(s), seedSpaceRecovery);
      assert.equal(await read(), seedSpaceRecovery);

      await button.focus();
      await activate('Space', 'Tersalin!');

      ui = await uiState();
      text = await read();
      const domStatusRecoveredSpace = await page.evaluate(() => document.getElementById('status').textContent);
      const axRecoveredSpace = await axStatus();

      assert.equal(text, fixture.recovery.text, 'Recovered Space must copy new active route');
      assert.equal(ui.focused, true);
      assert.equal(ui.connected, true);
      assert.equal(domStatusRecoveredSpace, 'Silsilah rute berhasil disalin ke clipboard');
      assert.equal(axRecoveredSpace.statusText, 'Silsilah rute berhasil disalin ke clipboard');

      evidence.records.push({
        width,
        case: 'space-permission-recovery-new-route',
        key: 'Space',
        states,
        ui,
        text,
        domStatus: domStatusRecoveredSpace,
        ax: axRecoveredSpace,
        pass: true,
      });

      // The real feedback timer must not move focus or leave a stale AX name.
      await page.waitForFunction(() => document.querySelector('.dag-breadcrumb-copy-btn').textContent === 'Salin Rute');
      assert.equal((await uiState()).focused, true);
      assert.equal((await uiState()).ariaLabel, 'Salin seluruh jejak silsilah rute ke clipboard');
      assert.equal(await page.evaluate(() => document.getElementById('status').textContent),
        `Versi ${fixture.recovery.id}. 0 cabang lanjutan.`);
      evidence.records.push({width,case:'native-feedback-reset-focus',pass:true});
      await context.close();
    }

    assert.equal(evidence.records.length, 24, '8 cases across 3 viewports = 24 records');
    assert.deepEqual(evidence.errors, []);
    evidence.pass = true;
  } catch (e) {
    evidence.pass = false;
    evidence.failure = String(e);
    throw e;
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
    fs.writeFileSync(path.join(__dirname, '../references/uiux-066-browser.json'), JSON.stringify(evidence, null, 2) + '\n');
  }
  console.log(JSON.stringify({pass: evidence.pass, records: evidence.records.length, browser: evidence.browser}));
})().catch(e => {
  console.error(e);
  process.exitCode = 1;
});
