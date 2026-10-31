# Scroll-Linked & Cursor-Proximity Motion

## When to Use

Load this when a component animates in response to **scroll position**, **pointer proximity**,
or **per-character text**, rather than a discrete open/close or enter/loop/exit lifecycle.
Covers: sticky stacking decks, magnetic hover docks, kinetic split type, and how to register
a new card in a component-bank gallery page.

Recipes for the three motion classes that are NOT enter/loop/exit lifecycle work:
sticky scroll stacks, pointer-proximity (magnetic) docks, and per-glyph kinetic type.
All three stay compositor-friendly (transform/scale/brightness only, zero layout writes).

---

## 1. Sticky Scroll Stack (`SCROLL_STACKED_REVEAL`)

Cards share one scroll container, each `position: sticky`, each with its own `top`
offset so headers stay readable as they pile up.

```html
<div id="stackScroll" class="h-[300px] overflow-y-auto p-3 space-y-3">
  <article class="stack-card sticky" style="top:0px"  data-i="0">…</article>
  <article class="stack-card sticky" style="top:22px" data-i="1">…</article>
  <article class="stack-card sticky" style="top:44px" data-i="2">…</article>
  <article class="stack-card sticky" style="top:66px" data-i="3">…</article>
</div>
```

```js
function paint() {
  queued = false;
  const top = scroller.getBoundingClientRect().top;
  let covered = 0;
  cards.forEach((card, i) => {
    const next = cards[i + 1];
    const h = card.offsetHeight || 1;
    // Depth = how far the NEXT card has climbed toward the sticky top.
    const p = next ? Math.min(1, Math.max(0, 1 - (next.getBoundingClientRect().top - top) / h)) : 0;
    if (p > 0.5) covered++;
    card.style.transform = `scale(${1 - p * 0.035}) translateY(${p * -4}px)`;
    card.style.filter = p > 0.02 ? `brightness(${1 - p * 0.28})` : 'none';
    card.style.zIndex = String(100 - i);
  });
  status.innerText = `DECK: ${covered}/${cards.length - 1} TERTUMPUK`;
}

scroller.addEventListener('scroll', () => {
  if (queued) return;
  queued = true;
  requestAnimationFrame(paint);   // one write pass per frame
}, { passive: true });
paint();
```

### Pitfalls (each one cost a rebuild cycle)

- **Never measure depth from the scroller's own top.** `scrollerTop - card.top` is ~0 for
every card once pinned, so `p` stays 0 and the stack looks dead. Measure against the
**next** card: `1 - (next.top - scrollerTop) / cardHeight`.
- **Never fade stacked cards with `opacity`.** Semi-transparent cards overlap and the
covered card's text bleeds through the card on top of it — unreadable mush. Keep cards
fully opaque and dim with `filter: brightness(1 - p*0.28)`; only scale + a 4px lift
suggests depth.
- **Give each card a distinct `top`, not `top:0` for all.** Identical offsets stack them
pixel-perfect and the titles disappear; 22px per layer keeps every header sliver legible.
- **Guarantee scroll travel.** If `scrollHeight - clientHeight` is smaller than one card
height, the effect barely moves. Add content (progress rows, metadata) until each card
contributes roughly its own height of travel.
- `filter` on the card creates a stacking context — always set an explicit `zIndex`
per layer instead of relying on DOM order.

---

## 2. Magnetic Cursor Dock (`MAGNETIC_CURSOR_DOCK`)

Linear proximity falloff, written through `gsap.quickTo` setters (no per-move tween allocation).

```js
const items = [...dock.querySelectorAll('.mag-item')];
const RADIUS = 120;
const setters = items.map(el => ({
  x: gsap.quickTo(el, 'x', { duration: 0.45, ease: 'power3.out' }),
  y: gsap.quickTo(el, 'y', { duration: 0.45, ease: 'power3.out' }),
  s: gsap.quickTo(el, 'scale', { duration: 0.45, ease: 'power3.out' })
}));

dock.addEventListener('pointermove', e => {
  items.forEach((el, i) => {
    const r = el.getBoundingClientRect();
    const dx = e.clientX - (r.left + r.width / 2);
    const dy = e.clientY - (r.top + r.height / 2);
    const pull = Math.max(0, 1 - Math.hypot(dx, dy) / RADIUS);
    setters[i].x(dx * 0.28 * pull);
    setters[i].y(dy * 0.28 * pull);
    setters[i].s(1 + 0.22 * pull);
  });
});

dock.addEventListener('pointerleave', () => setters.forEach(s => { s.x(0); s.y(0); s.s(1); }));
```

- Reset on `pointerleave` is mandatory; without it icons stay displaced after the cursor exits.
- Expose the field state in a status line (`FIELD: ENGAGED · PULL 0.87`) — it doubles as the
runtime proof that the handler ran.
- Touch devices fire no hover: the dock must still be usable with plain taps (buttons, not divs).

---

## 3. Kinetic Split Text (`KINETIC_SPLIT_TEXT`)

```js
const text = line.dataset.text || '';
line.setAttribute('aria-label', text);           // screen readers read the whole phrase
line.innerHTML = text.split('').map(ch =>
  ch === ' '
    ? '<span class="inline-block w-[0.28em]"></span>'
    : `<span aria-hidden="true" class="k-glyph inline-block will-change-transform">${ch}</span>`
).join('');

gsap.timeline()
  .fromTo('.k-glyph', { yPercent: 110, opacity: 0, rotate: 4 },
    { yPercent: 0, opacity: 1, rotate: 0, duration: 0.6, ease: 'power3.out', stagger: 0.035 })
  .fromTo(sub, { yPercent: 120, opacity: 0 },
    { yPercent: 0, opacity: 1, duration: 0.5, ease: 'power2.out' }, '-=0.35');
```

- Wrap the line in `overflow: hidden` (and `line-height: 1.05`) so glyphs rise out of a mask
instead of appearing from empty space; add `transform-origin: 50% 100%` for the magnet.
- Build once, guard with `line.dataset.built = '1'` — re-splitting on every replay duplicates glyphs.
- Play once via `IntersectionObserver` (`threshold: 0.4`) and `io.disconnect()`; offer an explicit
`PUTAR ULANG` button for repeat viewing. Never run an idle loop.
- `innerHTML` here is safe only because the string is author-controlled `data-text`; state that in a
comment so a reviewer does not have to re-derive it. Never interpolate user or DB content this way.

---

## 4. Registering a New Component in a Bank / Gallery Page

Adding a card is four edits, not one — miss any and the page lies about itself:

1. The card markup, with `data-cat="<category>"` matching an existing or new filter.
2. A filter tab button for a new category (`filterCategory('<category>')`).
3. The inventory counter in the header (`TOTAL: N PRESET`).
4. A code drawer (`id="code-<slug>"` + `toggleCodeView` + `copySnippet`) showing the real snippet.

Number new entries as `max(existing) + 1`. Legacy galleries often contain duplicate numbers
(`01/`, `02/`, `03/` appearing twice); do not "fix" them, but never reuse a number either.

Also add the component to the page's `prefers-reduced-motion` block so the gallery stays
accessible.
