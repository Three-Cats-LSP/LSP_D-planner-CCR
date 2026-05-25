# 🚀 LSP D-PLANNER — BETA 3.0 MILESTONE

**Version:** Beta 3.0  
**Release Date:** May 25, 2026  
**Focus:** Advanced Features + Professional PDF Export  
**Status:** ✅ COMPLETE & PRODUCTION READY  
**Lines of Code:** 3,924  

---

## 🎯 BETA 3.0 SUMMARY

Beta 3.0 is the biggest feature release yet — adding three major new features (CNS O₂ Tracking, GF Curve Visualizer, Professional PDF Export), a completely redesigned Dive Profile table, real-time dive profile graphs in both Rec and Bühlmann modes, and a fully featured multi-page PDF export with header/footer on every page.

---

## ✨ NEW FEATURES

### 1. CNS O₂ Toxicity Tracker — New Tab
Full Central Nervous System oxygen toxicity calculator:
- Real-time ppO₂ calculation from depth, O₂%, bottom time
- Single dive CNS% with animated progress bar (green→yellow→red)
- Daily total CNS% across multiple dives
- OTU (pulmonary toxicity) tracking
- NOAA exposure limits reference table
- Clear status warnings at 50%, 80%, 100% thresholds
- Works in both Rec and Bühlmann modes

### 2. GF Curve Visualizer — New Bühlmann Tab
Professional gradient factor curve on canvas:
- GF envelope line (dashed cyan): vertical at GF Low → diagonal to GF High
- Actual dive profile line (green) with waypoints
- 🔴 Red dots at mandatory deco stops with depth/time labels
- 🟢 Green dot at safety stop
- 🔵 Blue dot at bottom depth
- Depth axis (left) + GF% axis (bottom) with grid
- Auto-updates when switching to tab
- Works in both light and dark theme
- Placeholder message when no deco plan run

### 3. Professional PDF Export — Multi-Page
Full professional PDF with header/footer on every page:

**Page 1:** Dive Plan Summary + Dive Profile Table
- 8 stat cells (Depth, BT, Gas, Deco Time, Total RT, GF, Last Stop, Step)
- Gas info row with colour-coded tags
- Full dive profile table (Phase/Depth/Stop/Run/Mix/PPO2/CNS%)
- Icon legend

**Page 2:** Dive Profile Graph
- Full-width canvas snapshot
- Depth/time axes with grid

**Page 3:** Tissue Saturation
- All 16 Bühlmann compartments
- Colour-coded saturation %

**Page 4:** Gradient Factor Curve
- GF envelope + profile canvas snapshot

**Every Page:**
- Blue header: 🤿 LSP D-PLANNER · depth · BT · gas · GF · algo · date
- Footer: ⚠️ Training Use Only · @threecats_lsp · date
- 10mm top/bottom margins

---

## 🔄 DIVE PROFILE TABLE — COMPLETE REDESIGN

### New Columns: PHASE | Depth | Stop | Run | Mix | PPO2 | CNS%
- **Removed:** Duration, Type columns
- **Added:** Stop (time at depth), PPO2 (per row), CNS% (per row, colour-coded)
- **Renamed:** Run Time→Run, Gas→Mix

### New Rows:
- ✅ **Descent row** added at top (light red ↓)
- ✅ **Bottom row** (blue dot 🔵)
- ✅ Icons only in Phase column (centered)
- ✅ Mobile card layout on screens < 600px

### Icons:
- `↓` light red — Descent
- 🔵 — Bottom
- `↑` light green — Ascent
- 🔴 — Mandatory Deco Stop
- 🟢 — Safety Stop
- `⇄` — Gas Switch

### Gas Column (Mix):
- Shows real gas name (AIR, EAN 32, 100% O₂) — never "Bottom"
- Uppercase throughout
- Colour-coded by type

### Gas Info Row:
- `[Bottom: AIR — 21% O₂ @ surface→60m]` `[Deco: EAN 50 — 50% O₂ @ 22m]`
- Uppercase gas names
- Switch depth shown

---

## 📊 DIVE PROFILE GRAPH

Added to both Dive Planner and Deco Schedule tabs:
- Blue profile line with gradient fill underneath
- Red shading at deco stops
- Green shading at safety stop
- Dashed horizontal lines at stop depths
- Colour-coded dots (🔵 bottom, 🔴 deco, 🟢 safety)
- PPO₂ halo on dots (orange ≥1.4, red ≥1.6)
- Time axis (bottom) + depth axis (left)
- Redraws on theme toggle
- Included in PDF export as canvas snapshot

---

## 🔧 OTHER IMPROVEMENTS

### Tissue Saturation
- Now updates from Deco Schedule (not just Dive Planner)
- Final tissue loading after full deco profile

### Deco Schedule — Dive Profile Stats
- New labels: Depth, Bottom Time, Bottom Gas, Deco Time, Total Run Time, GF Low/High, Last Stop, Step Size
- Bottom Gas shown in UPPERCASE with display name
- Gas info row with switch depths and O₂%
- Removed: Deco Stops count, ppO₂ Limits, Descent time

### GF Curve — Fixed
- Now reads correct column (Depth is cells[1] not cells[0])
- Uses `data-phase` attribute for reliable row detection
- Shows placeholder when no deco plan run

---

## 📝 CHANGELOG

### Added ✨
- CNS O₂ Toxicity tab (full NOAA calculator)
- GF Curve Visualizer tab (Bühlmann only)
- PDF Export button in Deco Schedule
- Dive Profile Graph canvas (Dive Planner + Deco Schedule)
- `drawDiveProfile()` shared canvas function
- `drawPlannerProfile()` for Rec mode
- `drawDecoProfile()` for Bühlmann mode
- `rowCNS()` per-row CNS calculation
- Descent row in Dive Profile table
- Stop column in Dive Profile table
- PPO2 column in Dive Profile table
- CNS% column in Dive Profile table
- Mobile card layout for Dive Profile table
- Multi-page PDF with header/footer every page
- `data-phase` attribute on all table rows
- `bottomMixLabel` uppercase gas display
- Tissue saturation update from Deco Schedule

### Changed 🔄
- Dive Profile columns: Phase/Depth/Stop/Run/Mix/PPO2/CNS%
- Phase column icons only (centered, no text)
- Gas column shows real gas name (not "Bottom")
- Gas info row: uppercase, with Deco: prefix
- Dive Profile stats: 8 new labels
- PDF: 4 pages with bold titles and running header/footer
- PDF: Table on page 1, graph page 2, tissues page 3, GF page 4
- All icons use emoji (🔴🟢🔵⇄) for PDF compatibility

### Fixed 🐛
- GF Curve reading wrong column (was cells[0], now cells[1])
- Tissue saturation not updating from Deco Schedule
- PDF icons not showing (was HTML spans, now emoji)
- Gas name showing "Bottom" instead of real gas
- Ascent/descent arrows black in light theme
- PDF page titles hidden under fixed header
- Duplicate IIFE causing all buttons to break (Beta 3 launch fix)

---

## 📦 PACKAGE CONTENTS

```
LSP_D-PLANNER_BETA_3.0_GITHUB_RELEASE.zip
│
├── MILESTONE_BETA_3.0.md           ← This file
├── BETA_3.0_RELEASE_NOTES.md       ← User-facing notes  
├── RELEASE_PACKAGE_MANIFEST.md     ← Package guide
└── dive-planner-complete-web-apk.zip
    ├── index.html (3,924 lines · 167 KB)
    ├── www/index.html
    ├── android/ (full build)
    ├── .github/workflows/build-apk.yml
    └── docs & config
```

---

## 🚀 HOW TO USE NEW FEATURES

### CNS O₂ Tab
1. Switch to Bühlmann or Rec algorithm
2. Click **CNS O₂** tab
3. Enter depth, bottom time, O₂%, number of dives
4. See real-time CNS% bars and OTU values

### GF Curve Tab
1. Switch to **Bühlmann ZH-L16C**
2. Run a deco plan in Deco Schedule
3. Click **GF Curve** tab
4. See the gradient factor envelope and dive profile

### PDF Export
1. Switch to **Bühlmann ZH-L16C**
2. Run a deco plan in Deco Schedule
3. Click **⬇ PDF** button (next to 📥 TXT)
4. Print dialog opens — save as PDF
5. 4 pages with all dive data

---

## 📊 STATISTICS

| Metric | Beta 2.1 | Beta 3.0 | Change |
|--------|----------|----------|--------|
| Lines of code | 2,837 | 3,924 | +1,087 |
| File size | 117 KB | 167 KB | +50 KB |
| Tabs | 7 | 9 | +2 |
| JS Functions | ~47 | ~65 | +18 |
| PDF Pages | 0 | 4 | +4 |
| Table Columns | 6 | 7 | +1 |
| Breaking Changes | 0 | 0 | — |

---

## 🔄 BACKWARDS COMPATIBILITY

- ✅ All Beta 2.1 features preserved
- ✅ Light/Dark theme unchanged
- ✅ GF Selector unchanged
- ✅ All algorithms unchanged
- ✅ Settings persistence unchanged
- ✅ Zero breaking changes
- ✅ Default remains dark theme

---

## 🔮 ROADMAP

**Beta 3.1 (Possible):**
- [ ] Dive log history
- [ ] Auto OS theme detection
- [ ] Weather integration

**Beta 4.0 (Planned):**
- [ ] Multi-gas support
- [ ] DCIEM tables
- [ ] Buddy system

---

**Contact:** @threecats_lsp (Instagram)  
**License:** MIT  
🤿 *The most complete free dive planner!*

