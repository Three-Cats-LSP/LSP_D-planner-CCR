# Pro Dive Planner — Web + Android APK

Professional dive planner with Rec NDL tables and Bühlmann ZH-L16C algorithm. Deploy to Netlify (web) and build APK for Android in one project!

## Features

✅ **Rec Mode** — PADI RDP no-decompression tables
✅ **Bühlmann Mode** — ZH-L16C algorithm with 16 tissue compartments
✅ **Multi-dive Planning** — Nitrogen tracking and surface intervals
✅ **Offline Support** — Works completely offline
✅ **Web + Mobile** — Both Netlify web app and native Android APK

---

## Two Ways to Use

### 🌐 Option 1: Deploy Web App (Netlify)

**Instant deployment, no code needed:**

1. Go to **https://app.netlify.com/drop**
2. Drag and drop the `www/index.html` file
3. Get a live URL instantly
4. Share with anyone!

**Or via Git:**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR-USERNAME/dive-planner.git
git push -u origin main
```

Then connect to Netlify via GitHub → auto-deploys on every push!

### 📱 Option 2: Build Android APK (GitHub Actions)

**Get a native app for Android phones:**

1. Upload this repo to GitHub
2. Enable GitHub Actions
3. Push to GitHub
4. GitHub automatically builds APK (~20 min)
5. Download from Actions artifacts

---

## Quick Start

### Deploy Web App (5 minutes)

```bash
# Fastest way:
# Go to https://app.netlify.com/drop
# Drag www/index.html here
# Done! You have a live URL
```

### Build Android APK (25 minutes)

```bash
# On your computer:
git init
git add .
git commit -m "Initial: Dive Planner"
git remote add origin https://github.com/YOUR-USERNAME/dive-planner.git
git push -u origin main

# Then on GitHub:
# 1. Go to Actions tab
# 2. Click Build APK
# 3. Click Run workflow
# 4. Wait 20 minutes
# 5. Download APK
```

---

## Project Structure

```
dive-planner-complete/
├── www/
│   └── index.html                 ← The app (both web & APK)
├── android/                        ← Native Android project
│   ├── app/build.gradle
│   ├── build.gradle
│   ├── gradlew
│   ├── settings.gradle
│   └── gradle/
├── .github/workflows/
│   └── build-apk.yml              ← GitHub Actions APK build
├── netlify.toml                    ← Netlify web deployment
├── capacitor.config.json           ← Android settings
├── package.json                    ← Dependencies
├── README.md                       ← This file
└── LICENSE
```

---

## Installing APK on Android Phone

1. **Download APK** from GitHub Actions artifacts
2. **Transfer to phone** (email, USB, cloud, etc.)
3. **On phone**: Settings → Apps & notifications → Advanced → Install unknown apps → [File Manager] → Allow
4. **Open file manager** → find APK → tap → Install
5. **Done!** App is on your home screen

---

## Customizing

### Change App Name
Edit `capacitor.config.json`:
```json
{
  "appName": "My Custom App",
  "appId": "com.mycompany.customapp"
}
```

### Update Web App
Replace `www/index.html` with newer version:
```bash
# Update file, then:
git add www/index.html
git commit -m "Update app"
git push

# Web auto-deploys on Netlify
# APK auto-builds on GitHub Actions
```

---

## What's Pre-Generated

✅ `android/` folder — complete native Android project
✅ `www/index.html` — pre-built web app
✅ `netlify.toml` — web deployment config
✅ `.github/workflows/build-apk.yml` — APK build automation
✅ All Gradle files ready to build

**No setup needed — just push to GitHub!**

---

## Support

- **Netlify Docs**: https://docs.netlify.com
- **GitHub Actions**: https://docs.github.com/en/actions
- **Capacitor**: https://capacitorjs.com/docs/android
- **Android Gradle**: https://developer.android.com/studio/build

---

## License

MIT License — See LICENSE file

---

## Disclaimer

⚠️ For educational and planning purposes only. Diving is dangerous. Do not use as your primary dive computer. Always follow your training and obey your dive computer. Decompression diving requires professional training.

---

🤿 **Happy Diving!**

Deploy to Netlify, build APK on GitHub, share both!
