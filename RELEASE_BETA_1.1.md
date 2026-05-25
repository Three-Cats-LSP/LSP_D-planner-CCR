# LSP D-PLANNER - Release Beta 1.1

**Release Date:** May 19, 2026  
**Status:** PRODUCTION READY ✅

---

## 🎉 MILESTONE: Beta 1.1 Release

This is the official baseline for **LSP D-Planner Beta 1.1**. Use this as the foundation for all future versions and updates.

---

## ✅ Features Included

### Core Dive Planning
- ✅ **Rec (Recreational Dive Planner)** - Conservative lookup table approach
- ✅ **Bühlmann ZH-L16C** - Full tissue compartment model with 16 compartments
- ✅ **Gradient Factors** - Baker's gradient factors for safety
- ✅ **Multi-Dive Planning** - Plan up to 4 consecutive dives with surface intervals
- ✅ **NDL Tables** - Complete No-Decompression Limit lookup tables
- ✅ **Deco Calculations** - Decompression stop recommendations

### User Interface
- ✅ **LSP D-PLANNER Branding** - Professional app name and styling
- ✅ **Responsive Design** - Works on all screen sizes
- ✅ **Dark/Light Theme Support** - Adapts to device settings
- ✅ **Tab Navigation** - Dive Planner, Multi-Dive, Reference tabs
- ✅ **Algorithm Switcher** - Easy toggle between Rec and Bühlmann

### Instagram Integration
- ✅ **Square Gradient Icon** - Bottom center of main screen
- ✅ **Working QR Code** - Scannable QR in Reference section
- ✅ **Direct Instagram Link** - @threecats_lsp profile
- ✅ **Professional Styling** - Instagram gradient colors (Yellow→Purple→Blue)

### Data & Settings
- ✅ **Settings Persistence** - Saves user preferences (v3 storage)
- ✅ **Empty Defaults** - Clean input fields for all modes
- ✅ **Surface Interval Defaults** - 60 minutes for multi-dive planning
- ✅ **Algorithm Memory** - Remembers selected algorithm between sessions

### Deployment
- ✅ **Web Version** - HTML5, PWA compatible
- ✅ **Android APK** - Full native app support
- ✅ **GitHub Actions** - Automated APK building
- ✅ **Netlify Ready** - Web deployment configured

---

## 📁 Project Structure

```
dive-planner-complete/
├── index.html                    ← Main source (web)
├── www/index.html                ← Web version
├── android/
│   ├── app/src/main/assets/app.html
│   ├── app/src/main/res/         ← Icons, strings
│   └── build.gradle              ← Android config
├── .github/workflows/build-apk.yml ← GitHub Actions
├── capacitor.config.json         ← PWA config
├── netlify.toml                  ← Web deployment
├── RELEASE_BETA_1.1.md           ← This file
├── QUICK_START.md                ← Setup guide
└── README.md                     ← Project overview
```

---

## 🔧 Technical Stack

- **Frontend:** Vanilla JavaScript, HTML5, CSS3
- **Algorithms:** 
  - Bühlmann ZH-L16C with 16 tissue compartments
  - Schreiner equation for saturation calculation
  - Gradient factors for safety
- **Storage:** LocalStorage (browser), encrypted key format
- **Build:** Gradle (Android), Capacitor (hybrid)
- **CI/CD:** GitHub Actions

---

## 📊 App Features Summary

| Feature | Status |
|---------|--------|
| Rec Dive Planning | ✅ Complete |
| Bühlmann Modeling | ✅ Complete |
| Multi-Dive Support | ✅ Complete |
| Instagram Integration | ✅ Complete |
| QR Code Scanner | ✅ Working |
| Settings Persistence | ✅ Complete |
| Responsive Design | ✅ Complete |
| Dark Mode | ✅ Complete |
| PWA Support | ✅ Complete |
| Android APK | ✅ Ready |
| Web Deployment | ✅ Ready |

---

## 🚀 How to Use This Baseline

### For Future Development:
1. **Clone from this baseline** - Use this release as your starting point
2. **Update version** in:
   - `capacitor.config.json` (versionName)
   - `.github/workflows/build-apk.yml` (tag version)
   - Create new `RELEASE_[VERSION].md`
3. **Make changes** to all three files:
   - `index.html` (main source)
   - `www/index.html` (web copy)
   - `android/app/src/main/assets/app.html` (APK copy)
4. **Keep them in sync** - All three must match exactly
5. **Test thoroughly** - Run in browser, PWA, and APK before release

### Branch Strategy:
- `main` - Always production-ready (current: Beta 1.1)
- `develop` - Active development
- `feature/*` - Individual feature branches
- `release/*` - Release candidates

---

## 🎯 Known Limitations (Beta)

- ⚠️ Training use only - Not for live diving
- ⚠️ No real-time dive computer sync
- ⚠️ No cloud backup (local storage only)
- ⚠️ Offline-only (QR code requires internet)

---

## 🔐 Important Notes

### File Sync Rule:
**ALL THREE FILES MUST BE IDENTICAL:**
```bash
index.html
www/index.html
android/app/src/main/assets/app.html
```

Verify with:
```bash
diff index.html www/index.html
diff index.html android/app/src/main/assets/app.html
```

### Storage Key:
- Current: `lspDiveSettings_v3`
- Old keys cleaned up: `lspDiveSettings`, `lspDiveSettings_v2`, `lspDiveDefaults_v2`

### GitHub Actions:
- Requires workflow permissions enabled
- Set to: "Read and write permissions"
- APK folder created in main branch automatically

---

## 📝 Changelog - Beta 1.1

**Latest Updates:**
- ✅ Added working QR code to Reference section
- ✅ Added Instagram square gradient icon to footer
- ✅ Converted round icon to square with rounded corners
- ✅ Fixed storage persistence (v3 keys)
- ✅ Removed old storage keys automatically
- ✅ Professional branding throughout
- ✅ Both web and APK fully functional

---

## 🤿 Credits

**LSP Diving Team**  
Instagram: @threecats_lsp  
Algorithms: PADI RDP + Bühlmann ZH-L16C

---

## 📦 File Size

- `dive-planner-complete-web-apk.zip` - 114 KB
- Main HTML file - ~100 KB
- Android APK - ~15-20 MB (built separately)

---

## 🚀 Next Steps for Future Versions

- [ ] Add custom profile settings
- [ ] Implement dive history log
- [ ] Add weather integration
- [ ] Real-time dive computer sync
- [ ] Cloud backup support
- [ ] Offline QR code generation
- [ ] Multi-language support
- [ ] Advanced statistics
- [ ] Buddy system integration

---

## ✅ QUALITY CHECKLIST

- ✅ Code is clean and documented
- ✅ All features tested and working
- ✅ Instagram integration complete
- ✅ Both web and APK versions ready
- ✅ Settings persist correctly
- ✅ No console errors
- ✅ Responsive on all devices
- ✅ Professional design
- ✅ Production deployment ready

---

**THIS IS RELEASE BETA 1.1 - STABLE BASELINE FOR FUTURE DEVELOPMENT** 🎉

---

*Timestamp: May 19, 2026 - 06:52 UTC*
