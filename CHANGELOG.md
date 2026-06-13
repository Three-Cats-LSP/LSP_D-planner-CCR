# Changelog

All notable changes to LSP D-Planner are documented here.

---

## v2.10.0 — 2026-06-13  ★ Milestone

### Added
- **@capacitor/status-bar plugin** — native Android status bar control; transparent/edge-to-edge layout with `WindowCompat.setDecorFitsSystemWindows`
- **Status bar icon color sync** — dark icons in light theme, white icons in dark theme; theme preference written to `document.cookie` on every toggle and startup so native Java reads the correct value on cold launch via `CookieManager`
- **Collapsible ENV settings group** — environment settings (altitude, water type, acclimatization) collapse/expand; state persisted in `localStorage`
- **Collapsible Advanced Settings group** — advanced algorithm settings collapse/expand; state persisted in `localStorage`
- **Dive profile presets** — quick-select common dive profiles (depth + bottom time combinations); applied to both Rec and Tec modes
- **Advanced config presets** — quick-select common algorithm/GF configurations; one-tap apply
- **Water type tooltip** — inline `?` explanation of density values and effect on deco obligation per water type
- **Per-algorithm tooltips** — inline `?` on algorithm selector explains ZHL-16C+GF, VPM-B, and VPM-B/GFS; includes conservatism note
- **Planning Aid Only banner** — prominent banner displayed when a non-default conservatism or GF is in use

### Changed
- **`APP_VERSION`** — bumped to `2.10.0`; `build.gradle` `versionCode` updated to `21000`
- **`windowLightStatusBar`** — set to `true` in `styles.xml` (dark icons as safe XML default); Java flips to white icons at startup if dark theme cookie is present
- **`windowTranslucentStatus`** — removed from `styles.xml`; edge-to-edge now handled exclusively by `WindowCompat.setDecorFitsSystemWindows(false)` in `MainActivity`
- **CI workflow** — added `git reset --hard HEAD` before `git pull --rebase` to clear unstaged `cap sync` changes that were causing the APK commit step to fail

### Fixed
- **Status bar bg color** — `#f0f4ff` → `#ffffff` in `StatusBar.setBackgroundColor` for light theme (was creamy off-white)
- **`.algo-label` in light theme** — `#00d9ff` (invisible cyan on white) → `#0055aa` (dark blue, matches `--padi-accent` token)
- **`onResume` access modifier** — changed from `protected` to `public` to correctly override `BridgeActivity.onResume()`; was causing compile error
- **Removed broken `applyStatusBarStyle()`** — was reading `diveTheme` from `CapacitorStorage` SharedPreferences which is never populated by `localStorage.setItem()`; JS `loadThemePreference()` now owns all status bar styling

---

## v2.9.1 — 2026-06-12

### Fixed
- ZHL CNS renderer: `bottomFO2` used instead of `(1-bottomFN2)` for trimix ppO₂ on descent/bottom rows
- Custom bottom gas cap raised 40% → 100%; MOD display now updates live on O₂% input
- `segCNSfrac`, `rowCNS`, ZHLEngine headless `hCNSfrac`: ppO₂ > 1.6 now clamps to 45-min NOAA limit instead of returning 100% per segment
- Gas switch flags on dive graph: colour changed to yellow/green (#FFD700 / #007A33) to match deco table switch row style; same fix applied to PDF deco table (3 locations)
- Dive graph card tooltip added — explains all visual elements (profile line, Bühlmann ceiling, gas switch flags, stop dots, ppO₂ halos, interaction)
- Multi TXT export (`mode=multi`) rewired from orphaned `#multiCards`/`#multiWarnings` to live `#unifiedDivePlan` renderer
- Static inline-SVG favicon replaces dynamically injected one (was broken after `initPWA` removal)

### Changed
- Dead code cleanup: 14 unused functions removed (`ftToM`, `setNDLUnits`, `setMultiUnits`, `updateGF`, `floorPPO2`, `depthFromPressure`, `getEl`, `switchMultiMode`, `runMulti`, `buildBuhRef`, `initPWA`, `calcMaxDepth`, `exportContingencyTXT`, `buildPdfGasCards`); archived to `dev/legacy.js`
- 12 dead CSS classes and 22 utility CSS rules removed
- Whitespace and separator comment cleanup (-5.7 KB)

### Added
- Proper PWA: `manifest.json` + `sw.js` (cache-first, offline-capable); Android Chrome install banner; iOS Safari Add-to-Home-Screen instructions
- `CHANGELOG.md` — full version history from v2.7
- `dev/legacy.js` — archive of removed functions for reference

---

## v2.9.0 — 2026-06-09

### Added
- **PDF Export section picker** — dialog before export lets you choose which sections to include (Dive Plan PDF and Emergency Plan PDF)
- **Emergency Plan PDF** — full PDF export for contingency plans: emergency gas consumption, ascent schedule, dive profile, GF curve, tissue saturation, emergency slate
- **DejaVu Sans Unicode font** — all PDFs now use a single DejaVu Sans (regular + bold) font; correct rendering of ✓ ✗ ⚠ ↑ ↓ and all Unicode symbols
- **Copy preview modal** — copy button opens a preview modal showing the full formatted plan text before copying to clipboard (Deco Plan and Emergency Plan)
- **Timestamps on all exports** — `YYYY/DD/MM HH:MM` date/time stamp added to all copy, slate, and TXT exports
- **CNS/OTU/PrT footer line** — second footer line added to all deco and emergency slates and copy exports
- **Math Verification Suite** (`tests-verify.html`) — ZHL-16C Bühlmann + VPM-B cross-check against Baker/FORTRAN reference; 68 tests across sections A–H
- **Tissue saturation chart** — per-compartment saturation bars in a dedicated collapsible card
- **Contingency shortcut buttons** — quick links to contingency scenarios from the results area

### Changed
- Collapsible result cards — Gas Consumption, Contingency Plans, Dive Graph, Tissue Saturation, GF Curve
- Card order reordered: Dive Profile → Gas Consumption → Contingency Plans → Dive Graph → Tissue Saturation → GF Curve
- Slate footer: TBT → TRT (Total Run Time); `TRT: MM'SS" | DECO: MM'SS"`
- Copy footer split into two lines
- Export headers: `DECO PLAN` / `EMERGENCY PLAN` title lines added
- END column in PDF deco table — all 9 columns exported

### Fixed
- ZHL CNS renderer trimix ppO₂ fix
- Custom bottom gas cap raised 40% → 100%
- Test harness: `gfs:hi` double-division fix, `WATER_VAPOR` NaN-safe re-sync

---

## v2.8.9 — 2026-06-09

### Added
- **Gas Consumption card** — rule-of-thirds table integrated into deco schedule results
- **Gas Rule toggle** — Rule of Thirds / Half Tank; updates live
- **Travel gas pooling** — pools with bottom gas when same mix
- **Warning row colours** — SHORT / TIGHT rows highlighted
- **Best Mix tab (Tec)** — trimix optimizer
- **END Calculator** — Tools tab: depth + O₂/He% → END and narcotic ppO₂
- **EAD Table** — MOD and MND reference for common mixes
- **Gas Table** — MOD @ 1.4 / MOD @ 1.6 / MND columns
- **PayPal donate button** — footer and Ref modal

### Changed
- Tec mode default on startup
- Main tab order: Deco > Gas Plan > Surf Int > Dive Planner > Multi Dive > CNS > NDL

### Fixed
- `calcSurfInt` tolTension: uses surface pAmb (not Dive 2 depth)
- Preset button placement
- Gas Plan cross-checks and max BT suggestion

---

## v2.8.0 — 2026-06-09

### Added
- **Gas Table** — MOD reference table for common mixes in Tools tab
- **Surface Interval Calculator** — full tissue-model SI calculation
- **Deco Slate** — compact waterproof-slate format export
- **Named Presets** — save and recall up to 20 full dive setups
- **END column toggle** — Equivalent Narcotic Depth in deco table

---

## v2.7.6 — 2026-06-09

### Added
- **Min Deco Profile** — enforce minimum stop times at 9 m and 6 m

---

## v2.7.4 — 2026-06-09

- Android APK: external links open in system browser
- `APP_VERSION` propagated to Android `versionName`/`versionCode` at build time
- Custom Android UA string: `LSPDPlanner/Android`

---

## v2.7 — 2026-06-08

Milestone release. See git log for earlier history.

---
