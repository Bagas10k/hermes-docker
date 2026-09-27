import { chromium } from 'playwright';
import { createServer } from 'vite';
import assert from 'node:assert/strict';

async function runBrowserTests() {
  console.log('Starting isolated Vite dev server...');
  const server = await createServer({
    root: new URL('..', import.meta.url).pathname,
    server: { port: 5199, host: '127.0.0.1' },
    logLevel: 'error'
  });
  await server.listen();
  const baseUrl = 'http://127.0.0.1:5199';

  console.log('Launching Playwright Chromium...');
  const browser = await chromium.launch({
    headless: true,
    executablePath: '/home/ubuntu/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome'
  });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // 1. Guard check: without ?mock=1, mocking must be disabled
    await page.goto(`${baseUrl}/`);
    const statusNoMock = await page.textContent('#msw-status');
    assert.match(statusNoMock, /Mocks disabled/);
    console.log('✔ Verified opt-in guard: disabled without flag');

    // 2. Opt-in flow
    await page.goto(`${baseUrl}/?mock=1`);
    await page.waitForFunction(() => document.getElementById('msw-status').textContent.includes('Active (MSW 2.x'));
    const statusWithMock = await page.textContent('#msw-status');
    assert.match(statusWithMock, /synthetic=true/);
    console.log('✔ Verified MSW 2.x worker registration and health intercept');

    // 3. Fetch synthetic seed
    await page.click('#btn-fetch-seed');
    await page.waitForFunction(() => document.getElementById('seed').value === '7');
    console.log('✔ Verified MSW synthetic REST interception (/api/seed)');

    // 4. Deterministic streaming test
    await page.click('#btn-start');
    await page.waitForFunction(() => document.getElementById('status').textContent === 'done');
    const firstRunRows = await page.$$eval('.row', els => els.map(e => e.textContent.trim()));
    assert.equal(firstRunRows.length, 6);
    assert.ok(firstRunRows.every(r => r.includes('[SYNTHETIC]')));
    console.log(`✔ Verified streaming completion with 6 labelled records`);

    // 5. Deterministic replay test
    await page.click('#btn-reset');
    await page.waitForFunction(() => document.getElementById('status').textContent === 'done');
    const secondRunRows = await page.$$eval('.row', els => els.map(e => e.textContent.trim()));
    assert.deepEqual(firstRunRows, secondRunRows);
    console.log('✔ Verified deterministic sequence equality across reset');

    // 6. Rapid restart / fencing test
    await page.fill('#count', '25');
    await page.click('#btn-start');
    // Immediately restart with count=4
    await page.fill('#count', '4');
    await page.click('#btn-start');
    await page.waitForFunction(() => document.getElementById('status').textContent === 'done');
    const fencedRows = await page.$$eval('.row', els => els.map(e => e.textContent.trim()));
    assert.equal(fencedRows.length, 4, 'Superseded run must not leak rows into active view');
    console.log('✔ Verified run fencing: superseded run cancelled and prevented stale updates');

    // 7. Error scenario test
    await page.selectOption('#scenario', 'error');
    await page.click('#btn-start');
    await page.waitForFunction(() => document.getElementById('status').textContent === 'error');
    const errText = await page.textContent('#error-box');
    assert.match(errText, /Synthetic failure/);
    console.log('✔ Verified error state simulation and recovery signal');

    // 8. Empty scenario test
    await page.selectOption('#scenario', 'empty');
    await page.click('#btn-start');
    await page.waitForFunction(() => document.getElementById('status').textContent === 'empty');
    const recordEmptyText = await page.textContent('#records');
    assert.match(recordEmptyText, /No records loaded/);
    console.log('✔ Verified empty state simulation');

    // 9. Abort test
    await page.selectOption('#scenario', 'success');
    await page.fill('#count', '50');
    await page.click('#btn-start');
    await page.waitForFunction(() => document.getElementById('status').textContent === 'streaming');
    await page.click('#btn-abort');
    await page.waitForFunction(() => document.getElementById('status').textContent === 'aborted');
    console.log('✔ Verified abort controller termination');

    console.log('\nAll 9 browser verification tests passed successfully!');
  } finally {
    await browser.close();
    await server.close();
  }
}

runBrowserTests().catch(err => {
  console.error('Test run failed:', err);
  process.exit(1);
});
