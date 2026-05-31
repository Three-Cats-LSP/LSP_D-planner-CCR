# Building Android APK for LSP D-PLANNER

## Overview

LSP D-PLANNER can be packaged as an Android APK for installation on Android devices.

## Quick Build (GitHub Actions)

GitHub Actions automatically builds an APK wrapper when you push a tag.

```bash
git tag v5.6.3-beta
git push origin v5.6.3-beta
```

APK will be available in the automated release.

## Manual Build (Local)

### Prerequisites

- Android Studio
- Android SDK 21+
- Gradle 7.0+
- Java 11+

### Option 1: Using Apache Cordova (Recommended)

```bash
# Install Cordova
npm install -g cordova

# Create Cordova project
cordova create lsp-d-planner-app com.example.lspdplanner LSPDPlanner
cd lsp-d-planner-app

# Add Android platform
cordova platform add android

# Copy app files
cp ../index.html www/

# Build APK
cordova build android

# APK location: platforms/android/app/build/outputs/apk/debug/app-debug.apk
```

### Option 2: Using Android Studio

1. **Create New Project**
   - File → New → New Project
   - Select "Empty Activity"
   - Name: LSP D-PLANNER
   - Package: com.example.lspdplanner

2. **Add Web Assets**
   - Copy `index.html` to `app/src/main/assets/`

3. **Create WebView Activity**
   ```java
   import android.webkit.WebView;
   
   public class MainActivity extends AppCompatActivity {
       @Override
       protected void onCreate(Bundle savedInstanceState) {
           super.onCreate(savedInstanceState);
           setContentView(R.layout.activity_main);
           
           WebView webView = findViewById(R.id.webview);
           webView.loadUrl("file:///android_asset/index.html");
       }
   }
   ```

4. **Build APK**
   - Build → Build Bundle(s) / APK(s) → Build APK(s)
   - Locate: `app/build/outputs/apk/debug/app-debug.apk`

### Option 3: Using Gradle (Command Line)

```bash
# Create minimal Android project structure
mkdir -p lsp-d-planner-android/app/src/main/assets
cp index.html lsp-d-planner-android/app/src/main/assets/

# Build with Gradle
cd lsp-d-planner-android
gradle build

# APK: app/build/outputs/apk/debug/app-debug.apk
```

## GitHub Actions APK Build

The `.github/workflows/build.yml` workflow automatically builds:

1. **On every push to main**: Artifact created
2. **On tag push**: Release with APK attached

### Triggering APK Build

```bash
# Create a release version
git tag v5.6.3-beta
git push origin v5.6.3-beta

# GitHub Actions will:
# 1. Validate HTML
# 2. Build APK
# 3. Create Release
# 4. Attach APK to Release
```

## Signing APK (Release)

For Google Play Store, you need to sign the APK:

```bash
# Generate keystore (one time)
keytool -genkey -v -keystore lsp-d-planner.keystore \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias lsp-d-planner

# Sign APK
jarsigner -verbose -sigalg SHA1withRSA \
  -digestalg SHA1 \
  -keystore lsp-d-planner.keystore \
  app-release-unsigned.apk lsp-d-planner

# Align APK
zipalign -v 4 app-release-unsigned.apk lsp-d-planner-release.apk
```

## Publishing to Google Play

1. **Create Google Play Developer Account** ($25)
2. **Create Application**
3. **Upload Signed APK**
   - Sign APK as shown above
   - Upload to Play Store Console
4. **Fill in Store Listing**
   - Screenshots
   - Description
   - Category
5. **Set Release Notes**
6. **Submit for Review**

## Testing APK

```bash
# Install on connected device/emulator
adb install app-debug.apk

# Run app
adb shell am start -n com.example.lspdplanner/.MainActivity

# Check logs
adb logcat | grep LSPDPlanner

# Uninstall
adb uninstall com.example.lspdplanner
```

## APK Features

The Android APK includes:

✅ Full LSP D-PLANNER application
✅ PADI REC calculations
✅ Bühlmann ZH-L16C algorithm
✅ Emergency planning
✅ Export to Text/PDF
✅ Copy to clipboard
✅ Offline capability
✅ Touch-optimized interface
✅ Material Design
✅ Android 5.0+ support

## Troubleshooting

### Build Fails with Java Error
- Update Java to version 11+
- Check JAVA_HOME is set correctly

### APK Won't Install
- Check Android version (minimum API 21)
- Use `adb install -r` to replace existing
- Clear app data: `adb shell pm clear com.example.lspdplanner`

### App Crashes on Load
- Check WebView is enabled
- Verify `index.html` copied to assets
- Check console logs with `adb logcat`

### Large File Size
- Use ProGuard/R8 minification
- Compress assets
- Remove unnecessary resources

## Resources

- [Android Studio Guide](https://developer.android.com/studio)
- [Cordova Documentation](https://cordova.apache.org/)
- [Android WebView Guide](https://developer.android.com/guide/webapps/webview)
- [Google Play Publishing](https://developer.android.com/studio/publish)

## CI/CD Integration

GitHub Actions automatically builds APK on tag creation:

```yaml
# Triggered by:
git tag v5.6.3-beta
git push origin v5.6.3-beta

# Builds:
1. Validates HTML
2. Creates APK
3. Creates Release
4. Attaches APK
```

No local build needed for most users!

