'use strict';
const { chromium } = require('playwright');

async function testScenario(page, { name, cursorText, cssRules, useShadowReserve = false, scale = 2 }) {
  const html = `
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* { box-sizing: border-box; }
body { margin: 0; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 14px; }
.dag-scroll-outer { overflow: auto; max-height: 450px; width: 100%; overflow-anchor: auto; border: 1px solid #ccc; }
.container { width: 390px; padding: 10px; }
/* Applied CSS */
${cssRules}
</style>
</head>
<body>
<div class="container">
  <div class="dag-scroll-outer" id="outer">
    <div style="height: 50px; background: #eee;">Header (Top of Scroll Port)</div>
    <div class="dag-status-region" aria-hidden="false">
      <span class="dag-status-reserve" aria-hidden="true">Silsilah rute berhasil disalin ke clipboard</span>
      <span class="dag-status-reserve" aria-hidden="true">Gagal menyalin silsilah rute ke clipboard</span>
      <span class="dag-status-reserve" aria-hidden="true">Menyalin silsilah rute ke clipboard…</span>
      ${useShadowReserve ? `<span class="dag-status-reserve" id="status-reserve-idle" aria-hidden="true">${cursorText}</span>` : ''}
      <p id="status" role="status" aria-live="polite" aria-atomic="true">${cursorText}</p>
    </div>
    <div id="target" tabindex="0" style="height: 60px; background: #cbd5e1; margin-top: 10px; border: 2px solid #2563eb;">Simpul Terfokus (Anchor Node)</div>
    <div style="height: 800px; background: #fafafa;">Konten Tambahan Scroll</div>
  </div>
</div>
</body>
</html>
  `;

  await page.setContent(html);
  await page.setViewportSize({ width: 390, height: 900 });

  // Snapshot computed font sizes first, then scale
  await page.evaluate((scaleFactor) => {
    const elements = [document.body, ...document.querySelectorAll('body *')].filter(e => e instanceof HTMLElement);
    const baseline = elements.map(e => [e, parseFloat(getComputedStyle(e).fontSize)]);
    for (const [el, size] of baseline) {
      el.style.fontSize = (size * scaleFactor) + 'px';
    }
  }, scale);

  async function sample() {
    return await page.evaluate(() => {
      const region = document.querySelector('.dag-status-region');
      const rRect = region.getBoundingClientRect();
      const statusEl = document.getElementById('status');
      const target = document.getElementById('target');
      const tRect = target.getBoundingClientRect();
      const outer = document.getElementById('outer');
      return {
        regionHeight: rRect.height,
        regionWidth: rRect.width,
        statusScrollWidth: statusEl.scrollWidth,
        statusClientWidth: statusEl.clientWidth,
        targetTop: tRect.top,
        outerScrollTop: outer.scrollTop,
        overflowX: statusEl.scrollWidth > statusEl.clientWidth
      };
    });
  }

  // 1. Initial phase
  const initial = await sample();

  // Scroll target into view like in forward Tab
  await page.evaluate(() => {
    document.getElementById('target').focus();
    document.getElementById('outer').scrollTop = 120;
  });
  const scrolled = await sample();

  // 2. Pending phase
  await page.evaluate(() => {
    document.getElementById('status').textContent = 'Menyalin silsilah rute ke clipboard…';
  });
  const pending = await sample();

  // 3. Settled phase
  await page.evaluate(() => {
    document.getElementById('status').textContent = 'Silsilah rute berhasil disalin ke clipboard';
  });
  const settled = await sample();

  // 4. Reset phase
  await page.evaluate((text) => {
    document.getElementById('status').textContent = text;
  });
  const reset = await sample();

  const heights = [initial.regionHeight, pending.regionHeight, settled.regionHeight, reset.regionHeight];
  const deltaH = Math.max(...heights) - Math.min(...heights);
  const targetShift = Math.abs(settled.targetTop - scrolled.targetTop);
  const scrollShift = Math.abs(settled.outerScrollTop - scrolled.outerScrollTop);

  return {
    scenario: name,
    scale,
    initialHeight: initial.regionHeight,
    pendingHeight: pending.regionHeight,
    settledHeight: settled.regionHeight,
    resetHeight: reset.regionHeight,
    deltaH,
    targetShift,
    scrollShift,
    statusScrollWidth: initial.statusScrollWidth,
    statusClientWidth: initial.statusClientWidth,
    overflowX: initial.overflowX
  };
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  const baselineCSS = `
.dag-status-region{display:grid;grid-template-areas:"status";margin:1em 0}
.dag-status-reserve{grid-area:status;visibility:hidden;pointer-events:none;line-height:1.35;margin:0}
#status{grid-area:status;margin:0;line-height:1.35}
  `;

  const hardenedCSS = `
.dag-status-region{display:grid;grid-template-areas:"status";margin:1em 0;min-width:0;overflow-wrap:anywhere}
.dag-status-reserve{grid-area:status;visibility:hidden;pointer-events:none;line-height:1.35;margin:0;min-width:0;overflow-wrap:anywhere}
#status{grid-area:status;margin:0;line-height:1.35;min-width:0;overflow-wrap:anywhere}
  `;

  const tests = [
    {
      name: 'Baseline 1: Short ID ("anak-雪")',
      cursorText: 'Versi anak-雪. 0 cabang lanjutan.',
      cssRules: baselineCSS,
      useShadowReserve: false,
      scale: 2
    },
    {
      name: 'Baseline 2: Long Branch ID (with hyphens/slashes)',
      cursorText: 'Versi feat/virtualized-2d-grid-with-asymmetric-spans-and-history-undo-redo. 2 cabang lanjutan.',
      cssRules: baselineCSS,
      useShadowReserve: false,
      scale: 2
    },
    {
      name: 'Baseline 3: Unbroken Commit Hash (SHA-256 token)',
      cursorText: 'Versi c98f820b784913c98b671a5392812d4a7536901234567890abcdef1234567890. 0 cabang lanjutan.',
      cssRules: baselineCSS,
      useShadowReserve: false,
      scale: 2
    },
    {
      name: 'Proposed 1: Short ID + Shadow + Hardened CSS',
      cursorText: 'Versi anak-雪. 0 cabang lanjutan.',
      cssRules: hardenedCSS,
      useShadowReserve: true,
      scale: 2
    },
    {
      name: 'Proposed 2: Long Branch ID + Shadow + Hardened CSS',
      cursorText: 'Versi feat/virtualized-2d-grid-with-asymmetric-spans-and-history-undo-redo. 2 cabang lanjutan.',
      cssRules: hardenedCSS,
      useShadowReserve: true,
      scale: 2
    },
    {
      name: 'Proposed 3: Unbroken Commit Hash + Shadow + Hardened CSS',
      cursorText: 'Versi c98f820b784913c98b671a5392812d4a7536901234567890abcdef1234567890. 0 cabang lanjutan.',
      cssRules: hardenedCSS,
      useShadowReserve: true,
      scale: 2
    }
  ];

  const results = [];
  for (const t of tests) {
    results.push(await testScenario(page, t));
  }

  console.log(JSON.stringify(results, null, 2));

  await browser.close();
})();
