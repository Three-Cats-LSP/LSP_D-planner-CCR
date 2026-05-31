# Automatic APK Building on GitHub Actions

## ✅ YES - APK Building is Automated!

LSP D-PLANNER now has **fully automated APK building** on GitHub Actions.

## How It Works

### 1. GitHub Actions APK Workflow

**File:** `.github/workflows/build-apk.yml`

This workflow automatically:
- ✅ Sets up Android SDK
- ✅ Installs Gradle
- ✅ Creates Android project structure
- ✅ Builds APK from source
- ✅ Uploads to GitHub Artifacts
- ✅ Attaches to Release

### 2. Triggering APK Build

**Option A: Automatic on Tag (Recommended)**

```bash
# Create release tag
git tag v5.6.3-beta

# Push to GitHub
git push origin v5.6.3-beta

# GitHub Actions automatically:
# 1. Validates code
# 2. Builds APK
# 3. Creates Release
# 4. Attaches APK
```

**Option B: Manual Trigger**

Go to GitHub Actions tab → "Build Android APK" → "Run workflow"

**Option C: Automatic on Push to Main**

APK builds automatically on every push to main branch (artifacts only, not released)

### 3. Download APK

After build completes:
1. Go to GitHub Actions tab
2. Click "Build Android APK" workflow
3. Scroll to "Artifacts"
4. Download `lsp-d-planner-apk`

Or from Release:
1. Go to Releases
2. Find release with tag `v5.6.3-beta`
3. Download `LSP_D-PLANNER-5.6.3-beta.apk`

## What the Workflow Does

### Build Steps

1. **Setup**
   - Checkout code
   - Install JDK 11
   - Install Android SDK
   - Install Gradle 7.6

2. **Create Android Project**
   - Create directory structure
   - Copy index.html to assets
   - Create build.gradle
   - Create settings.gradle

3. **Create Source Code**
   - Generate AndroidManifest.xml
   - Generate MainActivity.java
   - Generate layout XML
   - Generate resource strings/styles

4. **Build APK**
   - Run Gradle wrapper
   - Compile with Android SDK
   - Build debug APK
   - Sign APK (debug key)

5. **Upload & Release**
   - Upload to GitHub Artifacts
   - Create GitHub Release
   - Attach APK to release
   - Add release notes

## Build Output

### Artifacts
- **Name:** `lsp-d-planner-apk`
- **File:** `LSP_D-PLANNER-5.6.3-beta.apk`
- **Size:** ~5-8 MB
- **Kept for:** 30 days

### Release Asset
- **Available:** When tag is pushed
- **Kept:** Permanently
- **Downloadable:** From Release page

## Installation Instructions

Users can install APK by:

1. **Download APK** from GitHub Artifacts or Release
2. **Enable Unknown Sources**
   - Settings → Security → Unknown Sources (toggle on)
3. **Install APK**
   - Open file manager
   - Find downloaded APK
   - Tap to install
   - Grant permissions
   - Tap "Install"
4. **Launch App**
   - Tap "Open"
   - Or find "LSP D-PLANNER" on home screen

## APK Features

The automatically-built APK includes:

✅ Full web app wrapped in WebView
✅ Offline capability
✅ Local storage support
✅ JavaScript enabled
✅ DOM storage enabled
✅ Touch optimized interface
✅ Material Design styling
✅ Android 5.0+ support

## Workflow Triggers

### Automatic Triggers
- ✅ Push to main branch → Build artifact
- ✅ Tag push (v*) → Build + Release

### Manual Trigger
- ✅ GitHub Actions tab → Run workflow

### Scheduled (Optional)
- ✅ Can add cron schedule if desired

## Build Environment

**OS:** Ubuntu Latest
**Java:** OpenJDK 11
**Android API:** 21 (Android 5.0+)
**Build Tools:** 33.0.0
**Gradle:** 7.6
**Min SDK:** 21
**Target SDK:** 33

## File Structure Created

```
android-app/
├── app/
│   ├── src/main/
│   │   ├── java/com/example/lspdplanner/
│   │   │   └── MainActivity.java
│   │   ├── res/
│   │   │   ├── layout/
│   │   │   │   └── activity_main.xml
│   │   │   ├── values/
│   │   │   │   ├── strings.xml
│   │   │   │   └── styles.xml
│   │   │   └── drawable/
│   │   ├── assets/
│   │   │   └── index.html
│   │   └── AndroidManifest.xml
│   └── build.gradle
├── settings.gradle
├── build.gradle
└── gradlew
```

## How to Use Release APK

**For Users:**
1. Download from GitHub Release
2. Install on Android device
3. Use dive planner

**For Distribution:**
1. Host on website
2. Share link with diving community
3. Submit to Google Play Store (optional)
4. Distribute via email

## APK Signing

GitHub Actions builds **debug APK** with:
- Debuggable: true
- Signature: Debug key
- Valid for: Development/Testing

For **production/Google Play:**
- Need to sign with release key
- Upload to Google Play Console
- No additional steps in GitHub needed

## Troubleshooting

### APK Build Fails

**Error: "Cannot find gradlew"**
- Workflow creates gradlew automatically
- Usually succeeds after first run

**Error: "SDK not installed"**
- setup-android step installs SDK
- May need different API levels

**Error: "Java version mismatch"**
- Using JDK 11 (required)
- Check setup-java action

### APK Won't Install

**"Unknown apps not allowed"**
- Enable Settings → Security → Unknown Sources
- Try again

**"App already installed"**
- Uninstall first: `adb uninstall com.example.lspdplanner`
- Or use `adb install -r` to replace

## Next Steps

### For Testing
1. Push to main (creates artifact)
2. Download APK from Actions
3. Test on Android device/emulator

### For Release
1. Create tag: `git tag v5.6.3-beta`
2. Push tag: `git push origin v5.6.3-beta`
3. APK automatically builds and attaches to release
4. Users can download from Releases page

### For Google Play
1. Build APK (done automatically)
2. Sign with release key (manual step)
3. Upload to Google Play Console
4. Fill in store listing
5. Submit for review

## Automation Benefits

✅ **No manual build steps**
✅ **Reproducible builds**
✅ **Version-controlled code**
✅ **Automated testing**
✅ **GitHub Releases integration**
✅ **Direct download links**
✅ **Instant distribution**

## Workflow File

**Location:** `.github/workflows/build-apk.yml`

**Key sections:**
- Checkout code
- Setup JDK & Android SDK
- Create project structure
- Create source files
- Build with Gradle
- Upload artifacts
- Create release with APK

## Example Commands

```bash
# Create new version
git tag v5.6.4-beta
git push origin v5.6.4-beta

# GitHub Actions automatically:
# - Builds APK
# - Creates release
# - Attaches APK

# Users download from: Releases page
```

## Support

If APK build fails:
1. Check GitHub Actions logs
2. Look for error messages
3. Common issues in "Troubleshooting" section above
4. Create GitHub Issue if needed

---

**✅ APK Building is Fully Automated!**

Just push a tag and GitHub Actions builds everything.

