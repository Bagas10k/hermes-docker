---
name: android-apk-packaging
description: Use when building or signing Android APKs via CLI tools.
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [android, apk, aapt2, d8, apksigner, build-tools, offline-first, mobile]
---

# Android CLI APK Packaging (Headless Toolchain)

Build, package, align, and sign small standalone Android APKs directly via Android SDK build-tools (`aapt2`, `javac`, `d8`, `zipalign`, `apksigner`) when the existing project supports a direct CLI build. Keep packaging evidence separate from UI, storage, security, and physical-device verification.

## When to Use

- Building lightweight standalone Android apps (Webview shells, offline POS, micro utilities) on headless servers or low-memory VPS environments.
- Packaging local offline web apps into installable `.apk` binaries where a small toolchain is appropriate; measure actual build memory/time rather than promising fixed limits.
- Signing and aligning pre-built or custom APKs with release keystores.
- Setting up automated headless build scripts where installing full Gradle/Android Studio is prohibited or unnecessary.

Don't use for:
- Large multi-module native Android projects with hundreds of external Jetpack/Gradle dependencies requiring complex Maven resolution.

## Prerequisites

- OpenJDK 11 or 17 (`javac`, `keytool`).
- Android SDK Build-Tools (version 30.0.0+): `aapt2`, `d8`, `zipalign`, `apksigner`.
- Target platform jar: `$ANDROID_HOME/platforms/android-<API>/android.jar`.

## Ordered release workflow and evidence gates

1. Inspect the existing build script, manifest, WebView entry URL, native bridge, bundled assets, and storage keys before choosing a toolchain. Prefer a working repository build over replacing it with the generic recipe. Preserve the package ID, release signing identity, storage origin, and key/schema contracts during UI-only work; changing them can prevent an in-place update or make existing records inaccessible.
2. Lock the approved visual direction and test scope. Complete one real browser slice with neutral synthetic records before packaging; browser startup or `about:blank` does not test the app. Apply `ui-ux-execution-standard` for UI refinement and screenshots of the actual catalogue/cart and open payment state.
3. Distinguish intended release metadata from completed artifacts. For a release, advance the existing `versionCode`, set the intended `versionName`, and build a distinct versioned APK; a tracker entry alone changes neither the manifest nor the published binary. Never replace a keystore to work around a signing problem.
4. Build with the existing script or the pipeline below, verify the resulting package/signature, and record its hash. A small APK can be a local-assets shell using the installed Android System WebView; size and signing success do not establish completeness, security, compatibility, or battery performance.
5. Exercise the native boundaries separately: permission denial/grant, Bluetooth connect/print with a physical printer, native share, and any file export. A desktop browser pass proves web behavior only; mark unavailable device/hardware gates NOT RUN instead of inferring success from Java source.
6. Publish only the verified artifact, then fetch the exact public APK without authentication and compare its bytes/hash to the local build. Report source changes, browser results, package/signature, public delivery, and device tests separately. Until publication and read-back pass, describe the existing download as the old release.

### Storage and privacy claims

- Inspect actual manifest backup/network settings and native/WebView behavior before describing privacy or offline operation. Local storage and local assets alone do not prove zero network access, encryption, or immunity to data loss; never promise “100% safe.”
- Inventory products, transactions, settings, and schema before claiming a backup. A transaction CSV is a report, not a full restorable backup. Prove an export/import round trip in isolated storage before claiming recovery; `allowBackup` is a configuration flag, not evidence that restore worked.
- Treat JavaScript `Blob`/object-URL/`<a download>` handlers and success toasts as intent, not Android file-delivery evidence. Inspect the native handoff and test that an exported file actually exists and opens outside the WebView; a `DownloadListener` search alone cannot establish support for every download scheme.
- For the bounded device/storage/export test recipe, see [WebView verification](references/webview-verification.md).

## The 6-Step Headless Build Pipeline

1. **Compile & Link Resources (`aapt2`)**:
   Compile XML resources and produce the base APK with `R.java`:
   ```bash
   aapt2 compile --dir res/ -o build/compiled_res.zip
   aapt2 link -I $ANDROID_HOME/platforms/android-33/android.jar \
     --manifest AndroidManifest.xml \
     --java src/ \
     -o build/base.apk \
     build/compiled_res.zip
   ```

2. **Compile Java Source (`javac`)**:
   Compile application sources including the generated `R.java`:
   ```bash
   javac -cp $ANDROID_HOME/platforms/android-33/android.jar \
     -source 1.8 -target 1.8 \
     -d build/classes/ \
     src/com/example/app/*.java
   ```

3. **Convert Bytecode to DEX (`d8`)**:
   Convert class files into Android Dalvik executable bytecode:
   ```bash
   d8 --min-api 21 \
     --lib $ANDROID_HOME/platforms/android-33/android.jar \
     --output build/dex/ \
     build/classes/com/example/app/*.class
   ```

4. **Package DEX and Assets into APK**:
   Inject `classes.dex` and any bundled assets (offline web app, HTML/CSS/JS) into the base archive:
   ```bash
   cd build/dex && zip -u ../base.apk classes.dex && cd ../..
   if [ -d "assets" ]; then
     zip -ur build/base.apk assets/
   fi
   ```

5. **4-Byte Alignment (`zipalign`)**:
   Align uncompressed data on 4-byte boundaries (mandatory for Android runtimes):
   ```bash
   zipalign -p -f -v 4 build/base.apk build/aligned.apk
   ```

6. **V2/V3 Digital Signature (`apksigner`)**:
   Sign the aligned APK using a release keystore:
   ```bash
   apksigner sign --ks release.keystore \
     --ks-pass env:KEYSTORE_PASS \
     --ks-key-alias "$KEY_ALIAS" \
     --out dist/App-v1.0.0.apk \
     build/aligned.apk
   ```

## Native Hardware & POS Integrations

For offline web-to-hardware bridges (e.g. thermal Bluetooth printers, receipt printers):
- **SPP Bluetooth Protocol**: Use standard Serial Port Profile UUID `00001101-0000-1000-8000-00805F9B34FB` via `BluetoothAdapter` and `BluetoothSocket`.
- **Bluetooth runtime permissions**: Determine which adapter operations the app actually uses and request their applicable permissions. A permission request is asynchronous: guard each protected native entry point on confirmed permission and handle denial; requesting in `onCreate()` alone does not make later bridge calls safe. Exercise both denied and granted paths on the target Android device.
- **ESC/POS Command Set**: Send raw byte streams (`0x1B 0x40` init, `0x1B 0x61` align, `0x1D 0x56` cut) directly to the socket output stream.
- **JavaScriptInterface**: Expose methods annotated with `@JavascriptInterface` to communicate between WebView and native hardware.
- Inspectable starter code and build recipe: see `references/cli-toolchain-recipe.md`. Treat snippets as examples, not evidence of physical-device verification.

## Public Distribution via Existing Reverse Proxies

When serving APK downloads through an authenticated host or multi-service VPS (e.g. Express dashboard + Next.js portal behind Cloudflare Tunnel):
- Place download assets in directories whitelisted by public bypass middlewares (e.g., `/public/v/<app>/` or `/public/uploads/`).
- Verify via direct unauthenticated curl against the actual public domain: `curl -s -I https://domain/v/<app>/app.apk` must return `HTTP/2 200` with `content-type: application/vnd.android.package-archive`, not a `302/307 Redirect` to `/login` or `404 Not Found` from a mismatched ingress frontend.
- Check Cloudflare Tunnel ingress routing (`cloudflared` config or process ports) to confirm which local service (e.g. :3000 vs :3050) actually owns the public domain path.

## Pitfalls

- **Resilient Receipt Sharing (Anti-Crash)**: Avoid hardcoding `intent.setPackage("com.whatsapp")` without a fallback chooser. Many merchants use WhatsApp Business (`com.whatsapp.w4b`) or other chat apps; wrap share triggers in `Intent.createChooser` to prevent `ActivityNotFoundException`.
- **Edge Ingress vs Local Port Mismatch**: Never accept a local `http://127.0.0.1:<port>` 200 OK as verification of public delivery. In multi-service environments behind Cloudflare Tunnel or reverse proxies, public domains frequently route to an edge portal process (e.g. Next.js on port 3050) while background services run on separate ports (e.g. Express on port 3000). Always test the live HTTPS domain directly.
- **Sign Before Align Breaks Signatures**: Always run `zipalign` *before* `apksigner`. Running `zipalign` on an already signed APK invalidates the v2/v3 cryptographic signatures.
- **Bound build resources**: Check host headroom and project requirements before starting concurrent builds or Gradle workers on a shared server. Use the existing supported build with bounded concurrency; do not assume direct CLI tools always fit a fixed memory budget.
- **WebView File Access Security**: Enable `setAllowFileAccess(true)` and `setDomStorageEnabled(true)` for offline `file:///android_asset/` SPAs, but keep `setAllowUniversalAccessFromFileURLs(false)` unless local cross-origin loading is strictly necessary.
- **Signature verification is a separate gate**: Run `apksigner verify --verbose dist/App-v1.0.0.apk` on the final unmodified artifact and report the schemes actually verified. Do not infer installability on every supported Android version, hardware support, or an audit of the application from a valid signature.
