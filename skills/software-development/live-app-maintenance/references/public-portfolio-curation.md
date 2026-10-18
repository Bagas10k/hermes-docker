# Public portfolio curation and JajanDigital homepage

## Privacy and truthful selection
- Treat reachable HTTP 200 as availability only, never as consent to public showcase. Inspect actual interactive drawers/modals and outgoing links before admitting a project.
- Exclude client accounting/ERP, financial ops, agent control, private notes/vaults, telemetry, credentials, and ambiguous internal tools. Do not promote a catalog that links onward to excluded systems.
- Veto fake transactions: a demo that alerts an order succeeded without persistence is not a working store. Omit it rather than expanding a homepage-only task into a backend rebuild.
- Remove private project objects and detail copy from served frontend data, not only visible cards. Avoid unsupported 'production', posting-volume, or offline claims.
- Keep a small verified selection instead of padding the grid. For one accepted work, center a full-width featured card with a real screenshot and its original aspect ratio.

## Source and deployment mapping
- Discover the serving source empirically. At JajanDigital, PM2 `jajandigital` on 3000 is not the public portfolio homepage; the public edge is served by `penelitian-ai` on 3050.
- Homepage source: `/home/ubuntu/bobong/{app.js,style.css,index.html}`. Root entry is a separate file `/home/ubuntu/penelitian-pola-pikir-ai/public/index.html`, not a symlink. Its assets use `/p/bobong/`; the standalone bobong entry uses relative assets.
- Compare local response bytes with candidate source files before changing them. Public edge HTML may contain Cloudflare-injected markup; do not save that response as source.
- Add content-hash asset query strings to both index entries because edge/browser JS/CSS caching can retain removed project content.
- Back up exact targets, record SHA256, reject intervening source changes, deploy assets before HTML, and read back public HTML plus exact hashed JS/CSS/image targets. Static files do not require restarting an unrelated service.

## Browser gates
- Exercise category filters, positive/negative search, clear/reset, grid/list, detail dialogs, keyboard Enter/Escape and focus restoration, loaded thumbnails, and no runtime errors at 390/768/1440px.
- Compare document scrollWidth with clientWidth. Decorative transformed SVG or hero artwork can enlarge the page outside the project section and break mobile coordinate-based clicks. Isolate the actual overflowing decorative container instead of hiding all page overflow blindly.
- Use fresh isolated browser contexts for localStorage utilities. Test add, complete, reload persistence, delete, and cleanup without touching existing user storage.
- Inspect full source screenshots before diagnosing crop problems. Cropping a 1920px-wide screenshot at x=1440 can cut a valid panel; that is not a layout defect.
- Own preview servers in the parent session. A worker-owned background preview can disappear when the ephemeral worker exits; explicitly verify readiness before QA.

## Bounded orchestration
- Give curators an explicit candidate list and require an artifact before broadening discovery. If a worker times out, preserve partial assets, restart only the unfinished scope, and do not repeat source discovery already empirically established by the parent.
- Pass source mappings, installed Puppeteer path, executable Chromium, exact target files, privacy vetoes, and acceptance tests in worker context. Never embed JavaScript template literals in shell-quoted Python commands: use write_file/patch to prevent shell backtick and ${...} expansion.
