#!/usr/bin/env node
/**
 * Render an HTML motion piece to a PNG sequence, resumable.
 *
 *   node render-frames.cjs <file.html> <outDir> [fps=30] [dur=34.4] [w=720] [h=1280]
 *
 * Then:
 *   ffmpeg -framerate <fps> -i <outDir>/frame_%05d.png -i vo_sync.mp3 \
 *     -c:v libx264 -pix_fmt yuv420p -preset fast -crf 20 -c:a aac -b:a 192k \
 *     -shortest out.mp4
 *
 * Two rules that make or break the export:
 *   1. Seek with suppressEvents = false. tl.pause(t) defaults to
 *      suppressEvents = true, which skips every tl.call()/side effect — the
 *      exported video then differs from live playback (labels never swap).
 *   2. Resume. A 1000+ frame render outlives most command timeouts; re-running
 *      must continue from the first missing frame instead of starting over.
 *
 * The page must expose window.tl (a paused GSAP timeline).
 */
const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

const [, , html, outDir, fpsArg, durArg, wArg, hArg] = process.argv;
if (!html || !outDir) {
  console.error('usage: node render-frames.cjs <file.html> <outDir> [fps] [dur] [w] [h]');
  process.exit(1);
}
const FPS = Number(fpsArg || 30);
const DUR = Number(durArg || 34.4);
const W = Number(wArg || 720);
const H = Number(hArg || 1280);
const TOTAL = Math.ceil(FPS * DUR);
const frameFile = i => path.join(outDir, `frame_${String(i).padStart(5, '0')}.png`);

const CHROME = process.env.CHROME_PATH || [
  '/usr/local/bin/chromium', '/usr/bin/chromium', '/usr/bin/chromium-browser',
  '/usr/bin/google-chrome', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
].find(p => fs.existsSync(p));

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  let start = 0;
  while (fs.existsSync(frameFile(start))) start++;
  if (start >= TOTAL) { console.log(`all ${TOTAL} frames already rendered`); return; }
  console.log(`rendering frames ${start}..${TOTAL - 1} @ ${FPS}fps (${W}x${H})`);

  const browser = await puppeteer.launch({
    headless: 'new',
    ...(CHROME ? { executablePath: CHROME } : {}),
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu',
           '--font-render-hinting=none'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: W, height: H, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('PAGE ERROR:', e.message));
  await page.goto('file://' + path.resolve(html), { waitUntil: 'networkidle0' });

  // hide review-only chrome (?debug panel etc.) so it never enters the video
  await page.evaluate(() => {
    ['#dbg', '#debug'].forEach(id => { const el = document.querySelector(id); if (el) el.style.display = 'none'; });
  });

  for (let f = start; f < TOTAL; f++) {
    await page.evaluate((t) => {
      if (!window.tl) throw new Error('window.tl missing');
      window.tl.pause(t, false);            // <-- false = do NOT suppress callbacks
      if (window.gsap && window.gsap.ticker) window.gsap.ticker.tick();
    }, f / FPS);
    await page.screenshot({ path: frameFile(f) });
    if (f % 120 === 0) console.log(`  frame ${f}/${TOTAL} (${(f / FPS).toFixed(1)}s)`);
  }

  await browser.close();
  console.log(`done: ${TOTAL} frames in ${outDir}`);
  console.log(`mux: ffmpeg -framerate ${FPS} -i ${outDir}/frame_%05d.png -i vo_sync.mp3 ` +
              `-c:v libx264 -pix_fmt yuv420p -preset fast -crf 20 -c:a aac -b:a 192k -shortest out.mp4`);
})();