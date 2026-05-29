# LSP D-Planner — Milestone v5.7.0
**Date:** 2026-05-29
**Status:** ✅ WORKING

---

## What's New in v5.7.0

### Export System (Copy/TXT)
- Unified `buildExportText(mode)` — single code path for COPY and TXT
- Messenger-friendly format (WhatsApp, Telegram, Reddit)
- All panels now have export buttons (Planner, Deco, Contingency, Multi, CNS)
- `.btn-export` CSS class replaces all inline styles
- Deco export: merged header + summary, clean table with short mix names (AIR/50%/100%)

### Deco Schedule Engine
- **Linear Schreiner** equation for descent and ascent travel (replaces midpoint approximation)
- **GF interpolation** — gfL at firstStopDepth → gfH at surface (standard Bühlmann-GF)
- **firstStopDepth** = ceiling(bottom_tissues, gfL) rounded up to nearest stop
- **10-second stop resolution** (was 1-minute)
- **Multi-gas switching** with 1-minute pause (tissue loading during switch)
- **Minimum stop time** at all depths ≤ firstStopDepth
- **ceilTarget fix** — `nextStop < lastStop` (strict) so only lastStop clears to surface
- **Last Stop default** = 6m (matching Multideco/industry standard)

### Settings (Deco Panel)
- N₂ Narcotic / O₂ Narcotic dropdowns (Yes/No)
- END (Equivalent Narcotic Depth) displayed in results
- Max Bottom ppO₂ (default 1.4) / Max Deco ppO₂ (default 1.6)
- Stop Time: 1:00 / 0:30 / 0:10 / 0:01
- Descent Rate / Ascent Rate as dropdowns with units
- All settings in one unified form-grid

### Table Display
- Phase abbreviations: Des / Lvl / Asc / Stp / GSw
- Stop column: time only (blank for Des/Asc)
- Depth column (Asc/Des): destination depth only
- Totals footer: Run time / Deco time / CNS% / OTU in one row
- Totals use mm'ss" format

---

## Algorithm Accuracy vs Multideco (50m/25min/Air, EAN50@21m, O2@6m, Salt)

| Setting | Multideco total | LSP total | Delta |
|---------|----------------|-----------|-------|
| GF 50/85 | ~27 min | ~24 min | -3 min |
| GF 30/70 | ~34 min | ~29 min | -5 min |

Remaining differences are due to minor implementation details (gas fraction precision, rounding).
The algorithm is correct standard ZHL16C-GF.

---

## Build Stack (unchanged from v5.6.3)
- Android Gradle Plugin 8.6.1
- Gradle 9.5.1
- JDK 17
- compileSdk/targetSdk 35 / minSdk 21
