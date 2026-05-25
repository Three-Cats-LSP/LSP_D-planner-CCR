# LSP D-PLANNER - Release Beta 2.0

**Release Date:** May 19, 2026  
**Status:** PRODUCTION READY ✅  
**Base Version:** Built from Beta 1.1

---

## 🎉 MILESTONE: Beta 2.0 Release

Major feature update with **Dynamic Gradient Factor (GF) Selection** and **GF-Responsive NDL Tables**.

---

## 🆕 NEW FEATURES IN BETA 2.0

### 1. **Dynamic GF Selector in Header**
When you select **Bühlmann**, the header expands to show:

```
REC | BÜHLMANN | GF 30/70 | GF 40/80 | GF 50/90 | Custom GF [__/__]
```

**Features:**
- ✅ Quick preset buttons (Conservative, Moderate, Liberal)
- ✅ Custom GF input fields
- ✅ Instant recalculation of all tables
- ✅ GF values displayed in results
- ✅ Settings persist across sessions

### 2. **GF-Responsive NDL Tables**
- ✅ NDL values now **dynamically calculate** based on selected GF
- ✅ Shows both Bühlmann and Rec NDL for comparison
- ✅ GF values displayed next to NDL in table
- ✅ Updates instantly when GF preset changes
- ✅ Works with custom GF values

### 3. **Unified GF Management**
- ✅ Removed redundant GF input fields from other tabs
- ✅ All GF control centralized in header
- ✅ Single source of truth for GF values
- ✅ Multi-dive and deco tabs use header GF settings

---

## ✅ FEATURES CARRIED FROM BETA 1.1

**Core Dive Planning:**
- ✅ Rec (Recreational Dive Planner)
- ✅ Bühlmann ZH-L16C (16 compartments)
- ✅ Multi-Dive Planning (4 dives)
- ✅ NDL Tables & Deco Calculations
- ✅ Gradient Factors (Baker safety model)

**User Interface:**
- ✅ Professional LSP D-PLANNER branding
- ✅ Responsive design (all screen sizes)
- ✅ Dark/Light theme support
- ✅ Tab navigation
- ✅ Algorithm switcher

**Instagram Integration:**
- ✅ Square gradient icon (bottom center)
- ✅ Scannable QR code in Reference
- ✅ Direct profile link (@threecats_lsp)

**Deployment:**
- ✅ Web version (HTML5, PWA)
- ✅ Android APK
- ✅ GitHub Actions CI/CD

---

## 📊 TECHNICAL CHANGES

### Updated Functions:
- `setAlgo()` - Now toggles GF selector visibility
- `setGF(low, high)` - New function for preset selection
- `setCustomGF()` - New function for custom GF input
- `renderNDLTable()` - Now uses global `mGF` object
- `runPlanner()` - Uses centralized GF values

### Global Variable:
```javascript
let mGF = { low: 30, high: 70 };
```

### CSS Updates:
```css
.gf-btn { ... }          /* GF button styling */
.gf-btn.active { ... }   /* Active GF button */
```

---

## 🎯 USER EXPERIENCE IMPROVEMENTS

### Before Beta 2.0:
- GF settings scattered across multiple tabs
- NDL table was hardcoded (didn't change with GF)
- Users couldn't quickly compare different GF settings

### After Beta 2.0:
- GF control in one place (header)
- NDL table recalculates instantly
- Easy GF preset switching
- Custom GF for advanced users
- Clear visual feedback on active GF preset

---

## 🔄 GF PRESET EXPLANATIONS

| Preset | GF | Profile | Use Case |
|--------|-----|---------|----------|
| **30/70** | Conservative | Maximum safety, longer deco | Beginners, multiple dives, heavy workload |
| **40/80** | Moderate | Balanced risk/no-deco | Standard recreational diving |
| **50/90** | Liberal | Shorter deco, tighter margins | Advanced divers, single dives |
| **Custom** | User defined | Fine-tuned control | Technical diving, research |

---

## 🧪 TESTING CHECKLIST FOR BETA 2.0

- ✅ GF selector appears when switching to Bühlmann
- ✅ GF selector hides when switching back to Rec
- ✅ Preset buttons (30/70, 40/80, 50/90) work
- ✅ Custom GF inputs accept valid values
- ✅ Custom GF validation (5-100 range)
- ✅ NDL table updates with GF change
- ✅ NDL shows correct values for each GF
- ✅ Dive planner shows selected GF in results
- ✅ Multi-dive uses header GF settings
- ✅ Deco schedule uses header GF settings
- ✅ Tissue saturation uses header GF
- ✅ Settings persist on page reload
- ✅ Works on mobile and desktop
- ✅ Works in web and APK versions

---

## 📁 FILES MODIFIED IN BETA 2.0

```
index.html (Main source - 2650+ lines)
├── Header section (lines 631-657)
│   └── New GF selector HTML
├── CSS section (lines 195-230)
│   └── New .gf-btn styles
├── JavaScript (lines 1112-1190)
│   ├── Updated setAlgo()
│   ├── New setGF()
│   ├── New setCustomGF()
│   ├── Updated renderNDLTable()
│   └── Updated runPlanner()
```

Copied to:
- `www/index.html`
- `android/app/src/main/assets/app.html`

---

## 🚀 DEPLOYMENT NOTES

1. **All three files must be in perfect sync:**
   ```bash
   diff index.html www/index.html
   diff index.html android/app/src/main/assets/app.html
   ```

2. **Storage key remains:** `lspDiveSettings_v3`

3. **New GF settings included in save:**
   - `mGF.low` and `mGF.high` are part of app state
   - Persist automatically via appSettings

4. **GitHub Actions:** No changes needed, uses existing workflow

---

## 📝 CHANGELOG - Beta 2.0

**New Features:**
- ✅ Dynamic GF selector in header (shows when Bühlmann selected)
- ✅ Quick GF presets (30/70, 40/80, 50/90)
- ✅ Custom GF input fields
- ✅ GF-responsive NDL table calculations
- ✅ Unified GF management system

**Improvements:**
- ✅ Cleaner UI (removed scattered GF controls)
- ✅ Faster GF switching
- ✅ Better visual feedback
- ✅ More intuitive workflow

**Bug Fixes:**
- ✅ NDL table now respects GF values
- ✅ Multi-dive uses correct GF settings
- ✅ Deco calculations match selected GF

---

## 🎓 ALGORITHM DETAILS

### Bühlmann NDL Calculation with Dynamic GF:
```
1. Initialize 16 tissue compartments
2. Saturate tissues for entered depth & time
3. Calculate ceiling using:
   M-value_adjusted = GF_high × (original_M - a) + a
4. Iterate time until ceiling > 0
5. Return NDL in minutes
```

### GF Impact on Results:
- **Lower GF (Conservative):** More deco time, shorter NDL
- **Higher GF (Liberal):** Less deco time, longer NDL
- **Current setting:** Displayed in header and results

---

## ⚠️ KNOWN LIMITATIONS

- ⚠️ Training use only - Not for live diving
- ⚠️ QR code requires internet connection
- ⚠️ No cloud backup (local storage only)
- ⚠️ No real-time dive computer sync

---

## 🔮 FUTURE ENHANCEMENTS (Beta 3.0+)

- [ ] GF profile curves visualization
- [ ] CNS oxygen toxicity calculation
- [ ] DCIEM tables integration
- [ ] Dive log history
- [ ] Weather integration
- [ ] Multi-gas support
- [ ] Offline QR code generation
- [ ] Export to PDF

---

## 🤿 CREDITS

**LSP Diving Team**  
Instagram: @threecats_lsp  
Algorithms: PADI RDP + Bühlmann ZH-L16C  
Development: May 2026

---

## ✅ QUALITY ASSURANCE

- ✅ All GF calculations verified
- ✅ NDL tables match reference implementations
- ✅ No console errors
- ✅ Responsive on all devices
- ✅ Settings persist correctly
- ✅ Both web and APK fully functional
- ✅ Production deployment ready

---

**THIS IS RELEASE BETA 2.0 - DYNAMIC GF SELECTION IMPLEMENTED** 🎉

---

*Timestamp: May 19, 2026*
