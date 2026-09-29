# Motion UI Morphing & Live Web Showcase Recipe

Use this reference when building a live web microinteraction demo inspired by a short motion reel or UI reference. The target output is a working public artifact, not just a description.

## Procedure

1. **Extract the reference mechanics before coding.** If the user gives an Instagram/Reel URL, use `yt-dlp --dump-json` to capture title/description and, when allowed, download a local MP4 for frame sampling. Read the caption because creators often encode the motion spec there (`one shape`, `states`, `BPM`, `zero cuts`, `pure springs`). Sample frames with `ffmpeg -vf fps=1` or `fps=2` and OCR corner labels if the reel enumerates states.

2. **Distill the reel into a deterministic state machine.** Define an ordered `STATES` array with `id`, `step`, `name`, target width/height/radius, background, foreground, glow, and one-sentence purpose. Build one continuous parent surface whose geometry changes across states; keep content layers inside it and cross-fade/scale them. Do not render separate unrelated cards for each state, because that breaks the visual promise of a single morphing surface.

3. **Implement controls that prove the motion is real.** Add autoplay at the stated BPM, previous/next controls, a timeline to jump to any state, keyboard shortcuts, and at least a few interactive inner states such as scrubber, volume slider, toggle, tabs, or search input. For tests, support a deterministic query parameter such as `?autoplay=0` so Playwright can assert state transitions without racing the BPM timer.

4. **Use the user’s visual doctrine.** Prefer Warm Paper `#EFECE6`, Carbon Obsidian `#111318`, soft periwinkle/violet glow, Outfit + JetBrains Mono + Playfair Display, viewfinder/HUD details, full SVG/Lucide iconography, and zero emoji. Keep touch controls large enough for mobile thumb use.

5. **Gate accessibility while preserving the look.** Run Playwright plus Axe across 390, 768, and 1440px. Common fixes: add a valid role when using `aria-label` on a non-interactive div (for example `role="status"` on a loader), darken small accent text on Warm Paper (`#FF5C00` can fail; use a darker orange such as `#9A3412` for small labels), and darken tiny timestamp text on white cards.

6. **Publish through the existing Express static route and privacy boundary.** Build with Vite, serve the `dist` directory from `penelitian-pola-pikir-ai/server.js`, and add matching public regexes in `src/privacy-boundary.js`; otherwise the route can return 401 even when Express has a static handler. Restart `pm2` and verify both local and public headers with `curl -I`.

7. **Capture evidence before reporting done.** Verify `npm run build`, `npm test`, public `HTTP/2 200`, mobile no-overflow, and a screenshot/visual review. Then commit the standalone project locally and book the result into Obsidian if it is part of Bagas’s public catalog.

## Pitfalls

- Add a public regex in the privacy boundary whenever adding a new public static route, because the boundary runs before route handlers and will fail closed with auth errors.
- Disable autoplay in tests with a query flag, because a BPM timer can move the state before assertions and create nondeterministic failures.
- Do not treat downloaded reference media as source assets for the shipped demo; use it only to analyze timing and structure, then recreate the UI with original vectors and code.
