# WebView application verification boundaries

Use when a packaged local web app persists operational records, exports files, or calls native hardware. This recipe defines evidence to collect; it does not claim that a native export or restore implementation already exists.

## 1. Establish the persistence contract before mutations

1. Read the WebView entry URL, DOM-storage settings, origin, storage keys, and complete record schemas. Inspect manifest backup/network settings rather than assuming them from an offline-first brief.
2. Keep tests isolated from the user's records. Preserve package ID, signing identity, origin, and storage contracts for an update; never test uninstall/clear-storage against the only copy of real records.
3. Create neutral synthetic product, transaction, and settings records. Reload the same origin and verify exact record retention. Browser reload establishes browser persistence only; separately exercise activity restart and an in-place APK update on an isolated Android installation when those claims are in scope.

Do not equate absence of an operational backend with absence of network activity. Do not equate `allowBackup=true` with a tested restore, or `allowBackup=false` with encrypted local records.

## 2. Complete the web slice before the native gates

1. Open the actual application route, assert an app-specific element, and use its intended mobile viewport.
2. For a cashier, search/filter, add an item, change quantity, open payment, reject insufficient cash without creating a transaction, accept sufficient cash with correct change, and inspect history after reload. Use the smallest relevant CRUD check when product editing is in scope.
3. Capture the populated workbench and open checkout after transitions settle. Verify the last action is reachable above fixed navigation. Inspect the actual saved images; a CSS write or blank browser tab is not visual evidence.
4. Stop after the essential pass and report specific failures/untested boundaries; do not spend the delivery budget repeatedly auditing unchanged surfaces.

## 3. Prove native file delivery rather than a click handler

1. Trace the export path from JS through any native bridge, download callback, or document/save intent. Identify the URL scheme (`blob:`, `data:`, local file, or HTTPS); one download mechanism's presence does not prove that it handles every scheme.
2. Trigger export on Android. Complete or cancel the native save/share flow and verify the reported outcome matches it.
3. Open the saved file outside the WebView and inspect filename, encoding, headers, and synthetic records. For CSV, check the currency/date fields and non-ASCII text used by the app.
4. If no physical or emulator export test was run, report “JavaScript export handler present; Android file delivery NOT RUN.” A toast, anchor click, or desktop download is insufficient.

## 4. Distinguish reports from recoverable backups

1. Enumerate required recovery content: products, transactions and line items, settings, stable identifiers, and schema version. An export containing only transaction rows remains a report.
2. If restore exists, export a synthetic fixture, restore into separate empty storage, and compare all required records and values. Do not delete source records to demonstrate recovery.
3. Exercise malformed/unsupported input without writes. Existing-data restore requires an explicit merge/replace and conflict policy; do not infer one during UI work.
4. Claim backup/recovery only for the exact round trip exercised. Otherwise state the unsupported or untested scope plainly.

## 5. Separate package, public delivery, and device evidence

Run the existing build, then use the final artifact paths in these checks:

```bash
apksigner verify --verbose dist/App-v1.0.0.apk
sha256sum dist/App-v1.0.0.apk
curl --fail --silent --show-error --location \
  --output "$FETCHED_APK" "$PUBLIC_APK_URL"
sha256sum "$FETCHED_APK"
cmp dist/App-v1.0.0.apk "$FETCHED_APK"
```

Set `FETCHED_APK` to a fresh scratch-workspace file and `PUBLIC_APK_URL` to the exact unauthenticated release URL. Record final URL/status and APK content type as well: an HTML login page can return HTTP 200. Matching bytes establish delivery of the built artifact, not Android install/update success.

Report independently: web smoke results, screenshots, build exit/signature, local/public hash match, Android install/update, native share/export, and physical printer test. Leave unexercised gates NOT RUN; never turn a small package or signed artifact into an absolute security/readiness claim.
