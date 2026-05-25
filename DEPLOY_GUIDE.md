# Complete Deployment Guide — Web + APK

Everything you need to deploy to Netlify AND build an Android APK.

---

## 🌐 OPTION A: Deploy to Netlify (Web App) — 5 Minutes

### Method 1: Instant Drag & Drop (Easiest!)

1. Go to **https://app.netlify.com/drop**
2. Drag `www/index.html` into the drop zone
3. Wait 10 seconds
4. You get a live URL!
5. Share the URL with anyone

**No code, no login needed!**

### Method 2: GitHub Auto-Deploy (Recommended)

1. Push this repo to GitHub
2. Go to **netlify.com** → Sign up (free)
3. Click **New site from Git**
4. Connect GitHub → select your repo
5. Build settings:
   - **Base directory**: (leave empty)
   - **Publish directory**: `www`
   - **Build command**: (leave empty)
6. Click **Deploy**
7. Every push to GitHub auto-deploys!

---

## 📱 OPTION B: Build Android APK — 25 Minutes

### Step 1: Upload to GitHub

```bash
# On your computer
git init
git add .
git commit -m "Initial commit: Dive Planner Web + APK"
git remote add origin https://github.com/YOUR-USERNAME/dive-planner.git
git branch -M main
git push -u origin main
```

### Step 2: Enable GitHub Actions

1. Go to your GitHub repo
2. Click **Settings** → **Actions** → **General**
3. Select **"Allow all actions and reusable workflows"**
4. Click **Save**

### Step 3: Trigger APK Build

1. Go to **Actions** tab
2. Click **Build APK** workflow
3. Click **Run workflow** button
4. Watch the build (takes ~20 minutes)

### Step 4: Download APK

1. Once build is complete, scroll to **Artifacts**
2. Download **dive-planner-apk**
3. Extract the APK file

---

## 📥 Installing APK on Android Phone

1. Connect phone to computer via USB (or use cloud storage)
2. Transfer APK file to phone
3. On phone:
   - **Settings** → **Apps & notifications** → **Advanced**
   - **Install unknown apps** → Select **File Manager**
   - Toggle **Allow** ON
4. Open **File Manager**
5. Navigate to **Downloads**
6. Tap the APK file
7. Click **Install**
8. Wait for installation
9. **Done!** App is on your home screen

---

## 🚀 Do BOTH — Web + APK!

You can do both at the same time:

```
Step 1: Drag www/index.html to Netlify Drop → Web live in 10 sec
Step 2: Push to GitHub → APK builds in 20 min → App on Android phone
Step 3: Share Netlify link + tell friends to sideload APK
```

**Result: Web version + native Android app, all from one codebase!**

---

## Updating Your App

To update either version:

1. Edit `www/index.html` (or replace it)
2. Run:
   ```bash
   git add www/index.html
   git commit -m "Update dive planner app"
   git push origin main
   ```
3. **Netlify** auto-deploys web version (5 min)
4. **GitHub Actions** auto-builds new APK (20 min)
5. Both versions updated!

---

## Sharing Your App

### Web Version
- Share Netlify URL in email, Discord, Twitter, etc.
- Anyone can use instantly (no install needed)
- Works on phone, tablet, desktop

### Android APK
- Share APK file via email, Drive, etc.
- Friends tap to install (enable unknown sources first)
- Native app on Android

### Both!
- "Use web version here: [URL]"
- "Or download Android app: [APK file]"

---

## Troubleshooting

### Netlify Issues

**"Can't drag and drop"**
→ Make sure you're at https://app.netlify.com/drop (not /drop/)

**"Live site won't load"**
→ Check that `www/index.html` exists and is valid HTML

**"Can't connect GitHub"**
→ Make sure repo is public and you're signed into Netlify

### GitHub Actions Issues

**"Build fails with gradle error"**
→ Check that `android/` folder exists (it should be in zip)
→ See Actions logs for details

**"No artifacts to download"**
→ Build not complete yet, wait 20 minutes
→ Check Actions tab for build status

**"APK won't install on phone"**
→ Enable "Unknown sources" in Settings
→ Make sure phone has Android 8.0+
→ Try downloading APK again

---

## File Reference

| File | Purpose |
|------|---------|
| `www/index.html` | Your app (used by both web & APK) |
| `android/` | Native Android project for APK build |
| `netlify.toml` | Web deployment config |
| `.github/workflows/build-apk.yml` | Automates APK build on GitHub |
| `capacitor.config.json` | Android app settings |
| `package.json` | Dependencies |

---

## Commands Cheat Sheet

```bash
# Deploy web app
# Option 1: Netlify Drop
# Go to https://app.netlify.com/drop
# Drag www/index.html

# Option 2: GitHub → Netlify
git push origin main
# Netlify auto-deploys

# Build APK
git push origin main
# GitHub Actions auto-builds (20 min)

# Create release (auto-attaches APK)
git tag v1.0.0
git push origin v1.0.0
```

---

## Next Steps

1. ✅ Extract zip
2. ✅ Deploy to Netlify (5 min)
3. ✅ Push to GitHub (2 min)
4. ✅ Wait for APK build (20 min)
5. ✅ Download APK
6. ✅ Install on Android phone
7. ✅ Share both versions with friends!

---

🤿 **Happy Diving!**

You now have both a web app and native Android app!
