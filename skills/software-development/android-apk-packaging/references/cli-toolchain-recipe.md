# Android Headless Toolchain & Hardware Recipe

This reference provides illustrative starter code for Android micro-shells with Bluetooth ESC/POS printing and native share capabilities. Adapt it to the existing application's contracts and verify it on the target device; source snippets are not proof of production readiness, printer compatibility, successful backup, or native export.

## 1. Minimal AndroidManifest.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.kasirkilat.app"
    android:versionCode="1"
    android:versionName="1.0.0">

    <uses-sdk android:minSdkVersion="24" android:targetSdkVersion="34" />

    <!-- Bluetooth for Thermal Receipt Printing -->
    <uses-permission android:name="android.permission.BLUETOOTH" android:maxSdkVersion="30" />
    <uses-permission android:name="android.permission.BLUETOOTH_ADMIN" android:maxSdkVersion="30" />
    <uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />
    <uses-permission android:name="android.permission.BLUETOOTH_SCAN" />
    <!-- Fine location for Bluetooth LE/Classic discovery on Android <= 11 -->
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" android:maxSdkVersion="30" />

    <application
        android:label="KasirKilat"
        android:allowBackup="false"
        android:supportsRtl="true">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|screenSize|keyboardHidden"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

## 2. Hardware Bridge (`MainActivity.java`)

```java
package com.kasirkilat.app;

import android.Manifest;
import android.app.Activity;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.webkit.JavascriptInterface;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.widget.Toast;

import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.Set;
import java.util.UUID;

public class MainActivity extends Activity {
    private static final UUID SPP_UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB");
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        webView = new WebView(this);
        setContentView(webView);

        // Runtime permissions check for Android 12+ (API 31+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            if (checkSelfPermission(Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED ||
                checkSelfPermission(Manifest.permission.BLUETOOTH_SCAN) != PackageManager.PERMISSION_GRANTED) {
                requestPermissions(new String[]{
                    Manifest.permission.BLUETOOTH_CONNECT,
                    Manifest.permission.BLUETOOTH_SCAN
                }, 101);
            }
        }

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);

        webView.addJavascriptInterface(new WebAppInterface(), "AndroidBridge");
        webView.loadUrl("file:///android_asset/index.html");
    }

    public class WebAppInterface {
        @JavascriptInterface
        public String getPairedPrinters() {
            BluetoothAdapter adapter = BluetoothAdapter.getDefaultAdapter();
            if (adapter == null || !adapter.isEnabled()) return "[]";
            
            // Safety guard for Android 12+
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S &&
                checkSelfPermission(Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                return "[]";
            }

            Set<BluetoothDevice> devices = adapter.getBondedDevices();
            StringBuilder sb = new StringBuilder("[");
            boolean first = true;
            for (BluetoothDevice d : devices) {
                if (!first) sb.append(",");
                sb.append("{\"name\":\"").append(d.getName()).append("\",\"address\":\"").append(d.getAddress()).append("\"}");
                first = false;
            }
            sb.append("]");
            return sb.toString();
        }

        @JavascriptInterface
        public boolean printReceipt(String macAddress, String text) {
            BluetoothAdapter adapter = BluetoothAdapter.getDefaultAdapter();
            if (adapter == null) return false;
            try {
                BluetoothDevice device = adapter.getRemoteDevice(macAddress);
                BluetoothSocket socket = device.createRfcommSocketToServiceRecord(SPP_UUID);
                socket.connect();
                OutputStream out = socket.getOutputStream();

                // ESC/POS Init: ESC @
                out.write(new byte[]{0x1B, 0x40});
                // Send payload
                out.write(text.getBytes(StandardCharsets.UTF_8));
                // Feed 3 lines & Paper Cut (GS V 66 0)
                out.write(new byte[]{0x0A, 0x0A, 0x0A, 0x1D, 0x56, 0x42, 0x00});
                out.flush();

                socket.close();
                return true;
            } catch (Exception e) {
                return false;
            }
        }

        @JavascriptInterface
        public void shareToWhatsApp(String text) {
            Intent intent = new Intent(Intent.ACTION_SEND);
            intent.setType("text/plain");
            intent.putExtra(Intent.EXTRA_TEXT, text);
            // Universal chooser supports WhatsApp, WhatsApp Business, Telegram, etc.
            Intent chooser = Intent.createChooser(intent, "Bagikan Struk Transaksi");
            try {
                startActivity(chooser);
            } catch (Exception e) {
                Toast.makeText(MainActivity.this, "Gagal membagikan struk", Toast.LENGTH_SHORT).show();
            }
        }
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
```

## 3. Automated Headless Build Script (`build.sh`)

```bash
#!/usr/bin/env bash
set -euo pipefail

ANDROID_JAR="$ANDROID_HOME/platforms/android-34/android.jar"
BUILD_TOOLS="$ANDROID_HOME/build-tools/34.0.0"

rm -rf build dist && mkdir -p build/{classes,dex} dist

# 1. Compile resources
$BUILD_TOOLS/aapt2 compile --dir res/ -o build/compiled_res.zip
$BUILD_TOOLS/aapt2 link -I "$ANDROID_JAR" \
  --manifest AndroidManifest.xml \
  --java src/ \
  -o build/base.apk \
  build/compiled_res.zip

# 2. Compile Java
javac -cp "$ANDROID_JAR" -source 1.8 -target 1.8 -d build/classes/ src/com/kasirkilat/app/*.java

# 3. DEX conversion
$BUILD_TOOLS/d8 --min-api 24 --lib "$ANDROID_JAR" --output build/dex/ build/classes/com/kasirkilat/app/*.class

# 4. Assemble package
(cd build/dex && zip -u ../base.apk classes.dex)
if [ -d "assets" ]; then
  zip -ur build/base.apk assets/
fi

# 5. 4-Byte alignment
$BUILD_TOOLS/zipalign -p -f -v 4 build/base.apk build/aligned.apk

# 6. Cryptographic sign (v2+v3)
$BUILD_TOOLS/apksigner sign \
  --ks keystore/release.keystore \
  --ks-pass env:KEYSTORE_PASS \
  --ks-key-alias "$KEY_ALIAS" \
  --out dist/App-v1.0.0.apk \
  build/aligned.apk

# 7. Verification check
$BUILD_TOOLS/apksigner verify --verbose dist/App-v1.0.0.apk
```
