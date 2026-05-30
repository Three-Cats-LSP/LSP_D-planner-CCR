# LSP D-PLANNER — Milestone v5.8.0
**Date:** 2026-05-30
**Status:** ✅ RELEASE

---

## Summary

v5.8.0 is the interactive planning milestone. The Multi Dive tab is completely
redesigned as a unified Day Dive Plan with live bidirectional sliders for every
dive. New tools: Average Depth Converter, Dive Solver. Full imperial unit support
across all UI elements, exports, and graphs.

---

## New Features

### Unified Day Dive Plan (Multi Dive tab)
- Every dive (1–4) has a **Depth slider** (5–45m) and **Bottom Time slider** (5–90min)
- **Live colour feedback** on both sliders and progress bar:
  - 🟢 Green — >10 min remaining before NDL
  - 🟡 Yellow — 6–10 min remaining
  - 🔴 Red — ≤5 min or exceeded
- **Residual nitrogen tracked** — each dive's NDL accounts for tissue loading
  from all previous dives and surface intervals
- **Surface interval sliders** between dives (10–240 min)
- Replaces the separate Day Plan + Solver tabs with one unified view

### Average Depth Converter (Tools tab)
- Converts log-book average depth to recommended planning depth
- Formula: `avg + 75% × (max − avg)`
- Profile classification: Square, Multi-level, Deep Excursion, Spike Dive
- Explains when average depth is/isn't safe for repetitive dive planning

---

## Fixes

### Imperial Unit Consistency
- Stats bar (Depth, Last Stop, Step Size, END) now show ft
- Descent row shows `0 → 164ft` not `0 → 538ft` (was double-converting)
- Dive graph and GF curve Y-axis show ft ticks
- Rate dropdowns show ft/min when imperial
- Deco Step and Last Deco Stop dropdowns show ft
- TXT/PDF exports fully unit-aware (was reading stale localStorage)
- PDF stats bar, header, and title all unit-aware
- Changing units auto-recalculates deco plan and rebuilds multi dive

### Solver Bugs Fixed
- `buhNDL` was called with fractions instead of integers — NDL always returned 0
- Dive 1 sliders now show correct colour feedback
- All display spans start with `color:var(--text)` — no cyan flash on load
- `setTimeout(runSolver, 0)` ensures DOM is ready before first colour pass

### Colours
- Light theme traffic-light colours now vivid and visible:
  - Green: `#7CFC00` (Grass Green)
  - Yellow: `#FAFA33` (Lemon Yellow)
  - Red: `#FF3131` (Neon Red)
- Dark theme unchanged (already vivid)

### Copy / Export
- CNS tracker depth was hardcoded `m` — fixed
- `du` variable in `buildExportText` used live `units` global (not stale localStorage)
- All TXT and PDF exports fully unit-consistent

### PDF
- Totals row spacing: `Run time: 61'13"  Deco time: 30'20"  CNS: 58.3%  OTU: 85`
- Filenames match TXT convention: `LSP_date_Deco_depth_bt_GF.pdf`

### Rates TXT Export
- Reformatted: `Rates : Descent: 18 m/min  Ascent: 9 m/min  Deco: 6 m/min  Surface: 3 m/min`

---

## Build
- Single-file PWA: `index.html` (6,583 lines)
- JS syntax: clean (node --check verified)
- Branched from v5.7.1 (unit fix milestone)
