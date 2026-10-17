# Mounted Subpaths and Sandboxed Embeds

Two bug classes that pass every unit test and still break on the deployed URL:
serving an app under a path prefix, and embedding AI-generated HTML in an iframe.
Both are only caught by measuring the live page.

---

## 1. App mounted under `/appname` behind a shared router

A path mount is not a redirect. The reverse proxy strips the prefix, so the app
believes it lives at `/` while the browser believes it lives at `/appname/`.
Every absolute URL the app emits escapes the mount.

### Router side (the proxy that strips the prefix)

```js
const proxy = createProxyMiddleware({
  target: 'http://127.0.0.1:3100',
  changeOrigin: true,
  pathRewrite: { '^/appname': '' },
  on: { proxyReq: (r, req) => {
    r.setHeader('X-Forwarded-Prefix', '/appname');
    r.setHeader('X-Forwarded-Host', req.headers.host || 'example.com');
    r.setHeader('X-Forwarded-Proto', 'https');
  }}
});
app.use('/appname', proxy);
```

Add the mount to the portal's allowlist/boundary module too, or the request is
rejected before it ever reaches the proxy.

**`secure: false` does nothing on http-proxy-middleware v4+.** v4 proxies through
undici, which ignores the legacy option and rejects a self-signed backend cert —
symptom is an instant `504` (milliseconds, not a timeout). Pass an agent:

```js
const agent = new (require('https').Agent)({ rejectUnauthorized: false });
// ... agent, target: 'https://127.0.0.1:3100'
```

A backend that is not listening produces the same instant 504. Check
`ss -ltn | grep <port>` before debugging the proxy.

### Client side (every URL stays inside the mount)

- One helper everywhere:
  `const BASE = location.pathname.startsWith('/appname') ? '/appname' : '';`
  then `const U = p => BASE + p;`
- `fetch(U('/api/state'))`, never `fetch('/api/state')`.
- Asset refs relative: `href="./manifest.webmanifest"`, `src="./icon.svg"`.
- Manifest `"start_url": "./"`, `"scope": "./"`. Absolute `/` breaks install on
  the mounted path.
- Service worker: register `U('/sw.js')` and derive cached URLs from
  `self.registration.scope`, not `/`.
- Assert statically: regex the bundle for `fetch("/api` → must be zero hits.

### Backend side (do not trust loopback Host behind a proxy)

A path proxy connects **from 127.0.0.1**, so a naive "loopback peer = trusted"
rule hands unauthenticated access to the whole datastore through the public
domain. Exploitable, not theoretical.

- Local only if peer is loopback **and** effective host is a loopback name.
  Effective host = `X-Forwarded-Host` when present, else `Host`.
- Believe `CF-Connecting-IP` / `X-Real-IP` / `X-Forwarded-For` **only when the
  peer is the local proxy**; otherwise a LAN client spoofs IPs to dodge rate
  limits or lock others out.
- Same-origin checks must compare against the forwarded host, or every POST
  through the mount returns 403.

### Measure the mount, in this order

```bash
curl -s -o /dev/null -w '%{http_code}\n' https://example.com/appname/           # 200
curl -s -o /dev/null -w '%{http_code}\n' https://example.com/appname/api/state  # 401
# prove the bypass is closed: simulate the proxy, no token -> must be 401
curl -sk -H 'Host: 127.0.0.1:3100' -H 'X-Forwarded-Host: example.com' \
     https://127.0.0.1:3100/api/state -o /dev/null -w '%{http_code}\n'
```

Cloudflare answers bare scripted clients (`python-urllib`) with `error code: 1010`
on a public hostname. Use `curl` for domain checks; keep scripted HTTP clients
pointed at `127.0.0.1`.

---

## 2. Sandboxed iframe embedding AI-generated HTML

### The parent cannot measure the frame

`sandbox="allow-scripts ..."` without `allow-same-origin` gives the frame an
**opaque origin**. `iframe.contentDocument` is null / throws, so "read the height
and size the frame" code silently never works. Inject a reporter instead:

```js
const report = `<script>(function(){
  function r(){
    var b=document.body, d=document.documentElement;
    var h=Math.max(b?b.getBoundingClientRect().height:0, b?b.scrollHeight:0, b?b.offsetHeight:0);
    if (h < 60) h = d.scrollHeight;
    parent.postMessage({__h:Math.round(h)},'*');
  }
  addEventListener('load',r); addEventListener('resize',r);
  addEventListener('message',function(e){if(e.data&&e.data.__askHeight)r()});
  setTimeout(r,80); setTimeout(r,300); setTimeout(r,900);
  try{new ResizeObserver(r).observe(document.documentElement)}catch(e){}
  try{new MutationObserver(r).observe(document.documentElement,{childList:true,subtree:true,attributes:true})}catch(e){}
})();<\/script>`;
```

Parent: listen on `message` and match `iframe.contentWindow === e.source` so a
multi-artifact page resizes the right frame.

### Neutralise viewport units inside the frame

`100vh` / `min-height:100vh` inside an embedded document resolves to the **frame**
height, not the screen. The layout stretches, content pins to the bottom, and the
remainder is a dead band of the document's own background — reads as "preview is
broken / black". Inject before the content:

```html
<style>html,body{min-height:0!important;height:auto!important}body{overflow-x:hidden}</style>
```

### Size generously, never pin a fixed height

- Start at a neutral ~320px; set the measured height inline afterwards.
- Reset to neutral **before** assigning `srcdoc`, or the new document measures
  itself against the previous document's inflated height.
- Cap high (a few thousand px) and let the page scroll. A tight ceiling silently
  clips the document behind a scrollbar nobody notices, and everything below the
  fold looks missing.
- A media-query `height: … !important` overrides your inline measurement. Give the
  expanded variant `!important`, leave the default un-`!important`ed.
- Hide the raw source block that produced the artifact (usually still in the
  rendered markdown) or the same document renders twice.

### Keep the sandbox tight

`sandbox="allow-scripts allow-forms allow-modals allow-popups"` plus
`referrerpolicy="no-referrer"`. Never add `allow-same-origin` beside
`allow-scripts` — that lets the embedded document reach the host's storage and DOM.

### Verify by measuring, not by looking

```js
const rep = await new Promise(res => {
  const on = e => { if (e.data && e.data.__h) { removeEventListener('message', on); res(e.data.__h); } };
  addEventListener('message', on);
  frame.contentWindow.postMessage({__askHeight: 1}, '*');
  setTimeout(() => res(null), 2000);
});
// pass when rep !== null && parseInt(frame.style.height) >= rep - 2
```

Frames created before the reporter existed never resize — reload before concluding
the reporter is broken.

---

## 3. Reading the screenshot correctly

A screenshot is one viewport. A correctly sized 700px element on an 844px phone
*looks* clipped when it is merely scrolled, and a tall frame showing its own dark
background *looks* like a render failure. Before calling either a bug, compare
measured numbers: reported document height vs applied frame height, and
`scrollWidth` vs `clientWidth`. Fix the number, not the impression.
