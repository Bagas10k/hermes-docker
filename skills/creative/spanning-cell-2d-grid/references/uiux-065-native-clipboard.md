# UIUX-065: native headless clipboard permission/readback

Run from `/home/ubuntu` with existing dependencies:

```sh
export NODE_PATH=/home/ubuntu/website-security-auditor/node_modules
export PYTHONDONTWRITEBYTECODE=1
python3 -B -m unittest discover -s /home/ubuntu/.hermes/skills/creative/spanning-cell-2d-grid/scripts -q
node /home/ubuntu/.hermes/skills/creative/spanning-cell-2d-grid/scripts/test_browser_clock.cjs
node /home/ubuntu/.hermes/skills/creative/spanning-cell-2d-grid/scripts/test_history_browser.cjs
node /home/ubuntu/.hermes/skills/creative/spanning-cell-2d-grid/scripts/test_native_clipboard_chromium.cjs
```

Use the existing renderer unchanged through `native_clipboard_fixture.py`; serve its HTML over an ephemeral HTTP loopback listener, not `setContent` on about:blank. Assert `isSecureContext`, focus and native clipboard methods before testing. The browser's HTTP loopback trust exemption supplies a secure context; this is not TLS testing.

Use `Browser.setPermission` with PermissionDescriptor names `clipboard-read` and `clipboard-write`, scoped to origin and browserContextId. Do not use `clipboardReadWrite` / `clipboardSanitizedWrite` here: those are grantPermissions enum names and setPermission rejects them. Query permission state after each intervention. Leave read granted while denying write so retained content can be inspected without another permission transition.

Click the real Copy button in all three cases. Seed distinct native content first; compare readText against independent literal routes (including Unicode and HTML punctuation), not solely against the adapter's own lineage calculation. Denial must produce native NotAllowedError, failure label without copied class, false API result, and unchanged clipboard. Regrant write on the same page/button and copy the new branch. Do not replace clipboard APIs, execCommand, timers or application handlers.

Verified: Chromium 153.0.8010.12, 9 scenarios (3 cases at 390/768/1280), 336 Python methods (3 new fixture tests), 39 Node fake-clock cases, existing history suite and 11 controlled clipboard scenarios. Commands/output are in uiux-065-tests.json; actual native readback/UI/permissions are in uiux-065-browser.json. Running the existing history suite also regenerates uiux-064-node.json.

Scope: browser-managed native headless clipboard only. No physical system clipboard, desktop application paste, native permission prompt, other browser, screen-reader or performance guarantee. Next gap: headed desktop cross-application paste/readback with explicit permission prompts and system clipboard isolation. No application adapter, SKILL.md, production service, vault or runtime configuration change was needed.
