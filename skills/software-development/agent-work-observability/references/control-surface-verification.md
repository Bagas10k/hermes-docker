# Verify authenticated agent-control dashboards

Use this recipe for a browser control surface with authentication, streaming updates and real process actions. Keep the documented action scope fixed; a fixture proves the shipped adapter, not control over an unrelated live gateway.

## 1. Freeze sources and action ownership

1. Enumerate the UI assets, runtime adapter, authentication module and process registry under test. Hash them before and after the run.
2. Inject a private temporary state directory, fixture token, fixture database/vault and command executor into the real router. Do not duplicate handler logic in the harness or add production branches keyed to test names.
3. For process controls, spawn an actual harmless child through the adapter. Bind control to the child object/process group held by that adapter, never a client-supplied or stale persisted PID. Assert `stopping` immediately after a stop request and a terminal state only after observed exit.
4. Test external executors through injected fixtures; do not restart live daemons or publish real content merely to obtain green tests. Keep a separate explicitly authorized nonmutating real-model smoke test when model integration needs evidence.

## 2. Preserve real HTTPS and SSE semantics

1. Generate a short-lived self-signed certificate in the temporary directory with `openssl req -x509 -newkey rsa:2048 -nodes -keyout <key.pem> -out <cert.pem> -days 1 -subj /CN=localhost`.
2. Start the actual Express router through `https.createServer(...)` on `127.0.0.1` port `0`. Add that exact generated origin to the injected test auth options; do not broaden production origins.
3. Launch an installed Chromium binary through the existing browser driver and allow the fixture certificate only in this test context. Use the actual browser URL, not a rewritten production hostname whose stream is buffered by interception.
4. For a Telegram Mini App fixture, intercept only the SDK resource to provide a fake-token-signed `initData` shim. Exercise the real HMAC exchange, session and CSRF middleware. Never fabricate a production login or call the fixture an authenticated physical-Telegram test.
5. Let the browser consume the real SSE response. Do not accumulate response chunks until `end` before forwarding them: an SSE connection stays open, so that forwarding strategy prevents all events from reaching the browser. Assert initial heartbeat, a genuine update, and closure after logout/expiry.
6. On teardown, await adapter cleanup, stop only owned children, close browser and server connections, and remove private fixture state. Record the exact owned handles before cleanup so a failure cannot become a broad process kill.

## 3. Test the mobile usage scene, not just the first viewport

1. Run desktop and narrow-mobile checks together. Navigate all screens after their asynchronous content has loaded and collect page errors.
2. Scroll to the task form, submit, then click the next tab using a real browser click. Verify the active screen changed. A wrapping header can cover a sticky tab whose offset assumes desktop height; repair actual stacking/positioning instead of bypassing the failed click with `element.click()` in page JavaScript.
3. Verify fork/join layout with a fixture containing two parallel tool calls: sibling nodes must occupy the same rank and distinct horizontal positions, with matching call-result edges. Require unknown state for unresolved work rather than a completed placeholder.
4. Separate document overflow from intentional canvas/table overflow. Assert the page fits the viewport, then scroll the inner container to its far edge and confirm the hidden branch/action becomes reachable. Provide a short gesture hint where the scrollbar is not obvious on touch devices.
5. Take screenshots after state assertions. Label synthetic metrics and records as fixtures. Do not report human comprehension, latency thresholds or complete device compatibility from screenshot counts alone.

## 4. Publish and distinguish evidence boundaries

1. For a static refinement, test a separate candidate asset directory through the unchanged real router before touching the live directory. Retain the incumbent palette, function and route unless a redesign was requested.
2. Publish the coherent reviewed asset set only after the integration gate passes. Restart a service only when its serving mechanism requires it; direct disk-served static assets need served-byte verification, not an unrelated gateway restart.
3. Fetch the exact public HTML, CSS and JS with an explicit client profile. Compare hashes to the tested files. If the edge injects a known analytics script, record the raw HTML difference and verify that removing only that exact known injection restores equality; do not normalize arbitrary differences away.
4. Build negative access expectations from the actual existing policy. A login redirect ending at a public login page is not disclosure, and an already-public sibling reader is not a private endpoint newly exposed by the change. Record original status, redirect target and request headers rather than weakening a failing check blindly.
5. If installing a Telegram menu, verify bot identity first, save the previous owner-specific menu, call `setChatMenuButton` with the explicit owner chat and URL, then require `getChatMenuButton` to match. Do not consume updates or change webhooks for this operation.
6. Report four independent states: fixture workflow tests, exact public route, menu configuration, and genuine Telegram-client acceptance. A successful menu readback does not prove that the owner has opened or authenticated in the Mini App.
