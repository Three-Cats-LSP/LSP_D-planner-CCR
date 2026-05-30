# LSP D-PLANNER — Milestone v5.8.0
**Date:** 2026-05-30
**Status:** ✅ LOCAL MILESTONE — Not yet on GitHub

---

## Summary

v5.8.0 delivers the interactive planning milestone and mobile UX polish.
The Multi Dive tab is completely redesigned as a unified Day Dive Plan with
live bidirectional sliders. New tools added. Full imperial unit consistency
across all UI, exports, and graphs. Mobile layout cleaned up.

---

## New Features

### Unified Day Dive Plan (Multi Dive tab)
- Depth + BT sliders for every dive (1–4), live colour feedback
- Residual nitrogen tracked across all dives and surface intervals
- 🟢 >10 min to NDL · 🟡 6–10 min · 🔴 ≤5 min or exceeded
- Light theme vivid colours: Grass Green #7CFC00 / Lemon Yellow #FAFA33 / Neon Red #FF3131
- Surface interval sliders between dives (10–240 min)

### Average Depth Converter (Tools tab)
- Planning depth formula: avg + 75% × (max − avg)
- Profile classification: Square / Multi-level / Deep Excursion / Spike
- Explains when avg depth is/isn't safe for repetitive dive planning

### Mobile UX
- Result headers split into two rows: title on row 1, buttons + stat cards on row 2
- Export buttons icon-only SVG (Copy / TXT / PDF) — same stroke style
- Deco Schedule is now the default tab on load
- Button active/pressed flash on tap

---

## Bug Fixes

### Imperial Unit Consistency (comprehensive)
- Stats bar: Depth, Last Stop, Step Size, END all unit-aware
- Dive graph and GF curve Y-axis show ft ticks when imperial
- Rate dropdowns: ft/min when imperial
- Deco Step / Last Deco Stop dropdowns: ft when imperial
- TXT exports: all headers unit-aware (was reading stale localStorage)
- PDF exports: stats bar, header, titles all unit-aware
- Changing units auto-recalculates plan and rebuilds all views

### Export System
- All filenames: `LSP_date_type_depth_bt_GF.txt/.pdf`
- GSw → >> in all TXT and copy exports
- CNS tracker depth was hardcoded m
- PDF totals row spacing fixed
- Emergency plan renamed from Contingency throughout

### Day Dive Solver
- buhNDL was called with fractions — NDL always returned 0, fixed
- Colour scheme: var(--accent) → var(--green) for safe state

---

## Audit Results (pre-milestone)
- ✅ JS syntax clean (node --check)
- ✅ Zero hardcoded m units in exports
- ✅ Zero stale localStorage unit reads
- ✅ Zero GSw in exports
- ✅ Zero btn-export primary (removed)
- ✅ No nested version folders
- ✅ Default tab: Deco Schedule

---

## Build
- Single-file PWA: `index.html` (6,610 lines)
- Package: 96K, 31 files
- Branched from v5.7.1

## Next: Beta 6.0 (remaining v5.8 features)
1. SAC rate / gas consumption — bottom + deco SAC, per-gas volume and bar
2. Tissue saturation bar graph — 16 compartments, in UI + TXT + PDF exports
3. EAD per stop — in deco table, per stop row
4. SAC-based runtime — cylinder setup, gas duration, warn if runs out
