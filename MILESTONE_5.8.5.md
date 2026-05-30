# LSP D-PLANNER — Milestone v5.8.5
**Date:** 2026-05-30
**Status:** ✅ RELEASE — GitHub Rollout
**SHA256:** (see SHA256.txt)

---

## Summary

v5.8.5 is the feature-complete release of the v5.8 series. Builds on v5.8.0
(Unified Day Dive Plan, mobile UX) with four new deco features, comprehensive
imperial/metric fixes, export system hardening, and a fully automated audit
pipeline that runs 28 checks before every package.

---

## New Features (v5.8.x series)

### SAC Rate / Gas Consumption
- Bottom SAC (L/min) and Deco SAC (L/min) inputs in Deco Settings
- Gas consumed tracked per phase at correct ambient pressure
- Gas Consumption card shown below deco table: litres per gas
- Cylinder setup inline with each gas card (Size L + bar/psi pressure)
- Runtime warning if cylinder runs out before surfacing
- Emergency plan shows separate Emergency Gas Consumption card
- Imperial: cylinder pressure shows psi, converts correctly in calculation

### EAD Per Stop
- New EAD column in deco table between Mix and PPO2
- Formula: EAD = (fN2 × (depth+10) / 0.79) − 10
- Shows `-` for air stops, unit-aware (m/ft)
- Included in TXT export (both deco and emergency)
- Included in PDF export (colspan and row indices updated)

### Tissue Saturation Bar Graph
- 16 horizontal bars shown below deco table after calculation
- Colour: green <70% · yellow 70–85% · orange 85–100% · red ≥100%
- Separate from existing Tissue Sat. tab (which remains)

### Unified Day Dive Plan
- Replaced separate Day Plan + Solver tabs with one unified slider view
- Depth (5–45m) and BT (5–90min) sliders for every dive (1–4)
- Live colour feedback based on residual nitrogen after previous dives
- Surface interval sliders between dives (10–240 min)

---

## Fixes

### Imperial / Metric Consistency (comprehensive)
- Stats bar: Depth, Last Stop, Step Size, END all unit-aware
- Dive graph and GF curve Y-axis: ft ticks when imperial
- Rate, Step, Last Stop dropdowns: ft/ft/min when imperial
- Cylinder pressure: bar/psi toggle with conversion
- REF modal Key Depth Limits: updates with units
- NDL range dropdown: labels switch between m and ft ranges
- TXT exports: all headers unit-aware (was reading stale localStorage)
- PDF exports: stats bar, header, title, contingency header all unit-aware
- Changing units auto-recalculates all active plans

### Export System (all modes: deco, emergency, planner, multi, cns)
- **Zero non-ASCII** in any TXT or copy export: — → - · → - • → - ⚠ → !!
- GSw → >> in all modes
- EAD column added to TXT export (deco + emergency), width 49 chars
- PDF: EAD column c[5], PPO2 c[6], CNS c[7] — colspan corrected
- PDF filenames: LSP_date_type_depth_bt_GF.pdf (both deco + contingency)
- Emergency scenario label uses "and" not "·": "Lost EAN 50 and +3 min BT"
- Emergency gas consumption separate from main plan gas consumption
- Rates line reformatted: "Rates : Descent: 18 m/min  Ascent: ..."

### Mobile UX
- Result headers: two-row layout (title row 1, buttons + stat cards row 2)
- Export buttons: icon-only SVG (copy/txt/pdf), same stroke style
- btn-export active flash: cyan fill on press, returns to dark on release
- Deco Schedule is default tab on load
- Bühlmann mode no longer flashes stale planner result on switch

### Graph
- Dive profile graph X-axis was cut short — lastT was reading totals row
  (single colspan td). Fixed to exclude data-phase="totals" rows.

---

## Audit Pipeline (audit.py — 28 checks)
Runs automatically before every package. Zero failures required to ship.

| # | Check |
|---|---|
| 1 | JS syntax (node --check) |
| 2-4 | Tab system: Deco Schedule default, planner not active, deco panel active |
| 5-7 | Export filenames: TXT LSP_ format, both PDF titles |
| 8 | Zero non-ASCII in all lines.push / result.push |
| 9 | No hardcoded m units in TXT exports |
| 10 | No stale localStorage units reads |
| 11 | No GSw in exports |
| 12 | No btn-export primary class |
| 13 | No nested version folders |
| 14-17 | PDF: cDu, du, lastStopDisp, stepDisp all defined |
| 18 | PDF: no hardcoded m in HTML strings |
| 19-20 | PDF: colspan 7 (switch) and 8 (totals) |
| 21 | PDF: EAD c[5], PPO2 c[6], CNS c[7] in row builder |
| 22 | PDF: no problematic non-ASCII in template strings |
| 23 | Graph: lastT excludes totals row |
| 24-25 | Canvas elements exist for both profile graphs |
| 26-28 | Draw functions defined (decoProfile, plannerProfile, diveProfile) |

---

## Build
- Single-file PWA: `index.html` (~6,740 lines)
- Package: 100K, 31 files
- Audit: 28/28 passed
- Branched from v5.8.0 → v5.8.5
