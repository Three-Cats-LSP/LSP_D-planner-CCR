# Changelog

All notable changes to LSP D-Planner are documented here.

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
- **Math Verification Suite** (`tests-verify.html`) — ZHL-16C Bühlmann + VPM-B cross-check against Baker/FORTRAN reference; 68 tests across sections A–H (pinned regression, Baker Python cross-check, Maiken invariants, coefficient verification, physics constants, determinism, MultiDeco/V-Planner compatibility)
- **Tissue saturation chart** — per-compartment saturation bars in a dedicated collapsible card
- **Contingency shortcut buttons** — quick links to contingency scenarios from the results area

### Changed
- **Collapsible result cards** — Gas Consumption, Contingency Plans, Dive Graph, Tissue Saturation, GF Curve all collapsible; caret on the right side of each card header
- **Card order** — result cards reordered: Dive Profile → Gas Consumption → Contingency Plans → Dive Graph → Tissue Saturation → GF Curve
- **Slate footer** — renamed TBT → TRT (Total Run Time); footer now shows `TRT: MM'SS" | DECO: MM'SS"` with full seconds format
- **Copy footer** — split into two lines: `Run Time:MM'SS" Deco:MM'SS"` / `CNS:x% OTU:x PrT:x`
- **Export headers** — `DECO PLAN` / `EMERGENCY PLAN` title lines added; `LSP D-PLANNER` prefix removed from slate headers
- **Consistent PDF rendering** — both PDFs use identical helper structure (fonts, layout, header/footer format, section title style); theme colors differ (blue vs red)
- **END column in PDF deco table** — all 9 columns exported (Phase / Depth / Stop / Run / Mix / EAD / END / PPO2 / CNS%)
- **⚠ icon in Emergency PDF** — `[!]` replaced with Unicode warning triangle `⚠` in emergency PDF header and scenario box

### Fixed
- ZHL CNS renderer: `bottomFO2` used instead of `(1-bottomFN2)` for trimix ppO2 on descent/bottom rows
- Custom bottom gas cap raised from 40% to 100%; `max` attribute and JS clamp updated; MOD display now updates live on input
- `segCNSfrac` and `rowCNS`: ppO2 > 1.6 now clamps to the 45-min NOAA limit instead of returning 100% per segment
- Test harness: `gfs:hi` double-division fix, `WATER_VAPOR` NaN-safe re-sync, ZHL16C fallback path, dead `stops()` code removed

---

## v2.8.9 — 2026-06-09

### Added
- **Gas Consumption card** — replaces separate Gas Plan tab; rule-of-thirds table integrated directly into the deco schedule results (columns: GAS / TOTAL VOL / THIRDS / TURN PRESS / RESERVE / SUFFICIENT)
- **Gas Rule toggle** — Rule of Thirds / Half Tank switch on the gas consumption card; updates live without recalculating
- **Travel gas pooling** — when travel gas matches bottom gas, volumes are pooled and labelled (e.g. `Air (+Travel)`)
- **Warning row colours** — SHORT / TIGHT rows highlighted in red/yellow directly in the gas table
- **Best Mix tab (Tec)** — trimix optimizer; reads depth/gas from the current dive plan, calculates He% for target END and optimal O2%
- **END Calculator** — new Tools tab: depth + O2/He% → Equivalent Narcotic Depth and narcotic partial pressure
- **EAD Table** — MOD and MND reference for common mixes; ppO2 selector recalculates MOD column live
- **Gas Table** — MOD @ 1.4 / MOD @ 1.6 / MND columns for common mixes; respects metric/imperial
- **Avg Depth sub-tab** — moved from Tools to Rec submenu
- **PayPal donate button** — added to footer and Ref modal

### Changed
- **Tec mode default** — app now opens in Tec mode by default
- **Main tab order** — Deco > Gas Plan > Surf Int > Dive Planner > Multi Dive > CNS > NDL
- **Gas consumption table** — uses deco-table style matching Gas Plan layout with proper column alignment

### Fixed
- `calcSurfInt` tolTension now uses surface pAmb (not Dive 2 depth)
- Preset button placement in form grid
- Gas Plan cross-checks bottom gas vs deco plan consumption, shows max BT suggestion when short
- Tools panel unit consistency; END/MOD altitude correctness

---

## v2.8.7 — 2026-06-09

- Emergency plan button order fix
- Slate export added to Emergency Plan PDF

---

## v2.8.6 — 2026-06-09

- SLATE button added to Emergency Plan

---

## v2.8.5 — 2026-06-09

- Surf Int removed from Tools tab nav (now in main tabs nav)

---

## v2.8.4 — 2026-06-09

- Presets icon added to header
- END column always visible (removed toggle)
- Surf Int promoted to dedicated sub-tab in main nav

---

## v2.8.3 — 2026-06-09

- Border fix, presets icon correction, END fix, Surf Int visibility fix, ref modal nav fix

---

## v2.8.2 — 2026-06-09

- Travel Gas documentation merged into deco `[?]` tooltip; removed from Ref modal

---

## v2.8.1 — 2026-06-09

- Border fix, presets header fix, slate icon fix, END fix, Surf Int panel fix

---

## v2.8.0 — 2026-06-09

### Added
- **Gas Table** — MOD reference table for common mixes in Tools tab
- **Surface Interval Calculator** — full tissue-model SI calculation; available as Surf Int sub-tab and embedded panel in Rec/Tec results
- **Deco Slate** — compact waterproof-slate format export; monospaced, stops-only, header + footer
- **Named Presets** — save and recall up to 20 full dive setups (algorithm, GF, all gases, cylinders, depth, BT, altitude, SAC, min-deco settings) via localStorage
- **END column toggle** — Equivalent Narcotic Depth column in deco table, He-aware; configurable narcotic gas toggle (O2 counts or excluded)

---

## v2.7.8 — 2026-06-09

- `getPPO2Limit` trimix fix
- Audit script expanded to 147 checks

---

## v2.7.7 — 2026-06-09

- Min Deco Profile UI fix
- Reset defaults fix
- Audit script expanded to 143 checks

---

## v2.7.6 — 2026-06-09

### Added
- **Min Deco Profile** — enforce minimum stop times at 9 m and 6 m; configurable per dive; applied to both Bühlmann and VPM-B output

---

## v2.7.5 — 2026-06-09

- Browser tab title renamed from "Rec & Bühlmann" to "Rec & Tec"

---

## v2.7.4 — 2026-06-09

- Android APK: external links open in system browser
- APK footer icon replaced with Magnific gradient PNG; hidden inside WebView
- `APP_VERSION` propagated to Android `versionName`/`versionCode` at build time
- Custom Android UA string: `LSPDPlanner/Android`

---

## v2.7.3 — 2026-06-09

- Custom reset confirm modal (removes Android WebView `file://` prefix artefact)
- APK download icon added to footer (direct link)

---

## v2.7.2 — 2026-06-08

### Added (PDF export)
- Trimix bottom gas in PDF header
- Imperial SAC unit support in PDF gas consumption
- Trimix END in PDF deco table
- Altitude-adjusted VPM-B critical radii in PDF
- VPM-B repetitive dive state carry in PDF
- He half-time selector reflected in PDF
- Travel gas rows in PDF deco table

---

## v2.7.1 — 2026-06-08

- Gas consumption section added to TXT export (volumes, available, SAC footer)

---

## v2.7 — 2026-06-08

Milestone release. See earlier development history in git log.

---
