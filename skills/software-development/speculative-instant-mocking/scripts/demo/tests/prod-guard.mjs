import { preview } from 'vite';
import { chromium } from 'playwright';
import assert from 'node:assert/strict';

async function testProductionBuild() {
  const root = new URL('..', import.meta.url).pathname;
  const previewServer = await preview({
    root,
    preview: { port: 5198, host: '127.0.0.1' },
    logLevel: 'error'
  });
  const baseUrl = 'http://127.0.0.1:5198';
  const browser = await chromium.launch({
    headless: true,
    executablePath: '/home/ubuntu/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome'
  });
  const page = await browser.newPage();

  try {
    // Even if ?mock=1 is passed, production build must keep mocks disabled
    await page.goto(`${baseUrl}/?mock=1`);
    const status = await page.textContent('#msw-status');
    assert.match(status, /Mocks disabled/, 'Production build must fail-closed and block mocking');
    console.log('✔ Verified production build fail-closed guard (mocks disabled despite ?mock=1)');
  } finally {
    await browser.close();
    await previewServer.close();
  }
}

testProductionBuild().catch(err => {
  console.error('Production preview test failed:', err);
  process.exit(1);
});
