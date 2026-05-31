# LSP D-PLANNER — Beta 6.0.2 Milestone

**Release date:** 01 Jun 2026
**Version:** 6.0.2
**Branch:** Beta 6

---

## Summary

Beta 6.0.2 is a PDF quality, safety, and polish release. No algorithmic changes.

---

## What's New

### 🚨 Gas Warning — Red (Life-Critical)

Gas shortage warnings are now **red** across all surfaces, not yellow. Running out of gas underwater is a life-critical emergency, not a caution.

- **Web/mobile dark theme**: already used `.alert.dang` (red) — correct
- **Web/mobile light theme**: added explicit `body.light-theme .dang` override with solid `#cc0000` — was near-invisible pale pink on white background
- **PDF**: changed from yellow (`#fff3cd`) to solid red (`#fff0f0` / `#cc0000` / `font-weight:700` / `🚨` icon)
- Audit checks: yellow banned from gas warnings, solid red enforced

### 📊 PDF — Card-Style Gas Consumption

All three PDF export locations (deco PDF, emergency standalone PDF, main PDF page 4) now render gas consumption as card-style layout matching the web view:
- Large bold volume number (red if short)
- Gas label in small caps
- Colored progress bar (red/green)
- Availability line (`⚠ SHORT` / `✓ avail`)
- Red danger card when gas is insufficient
- SAC line in section header (not footer — prevents page footer overlap)
- `print-color-adjust: exact` throughout — backgrounds print correctly
- Single `buildPdfGasCards()` helper used in all three locations

### 📐 PDF Table Alignment

Depth, Stop, Run, EAD, PPO2, CNS% columns right-aligned in all PDF exports (deco and emergency).

### 📁 Export Filename

`Contingency` → `Emergency` in both TXT and PDF filenames.

### 🐛 Bug Fixes

- **PDF crash**: `ReferenceError: title is not defined` in `buildPdfGasCards` — `title` variable was lost when duplicate function was removed. Fixed with fallback derivation from `.card-title` element.
- **Emergency PDF**: missing null check on `window.open()` — silent crash when popups blocked. Added guard + `alert()` fallback matching main PDF.
- **Emergency TXT header**: Run Time / Deco Time now show `mm'ss"` format (was plain integer minutes).
- **Double `⚠ ⚠`**: warning text already contained `⚠` before our prefix was added. Now strips leading symbols before prepending `🚨`.
- **Emergency PDF Run/Deco Time**: header and main deco PDF page 4 emergency section now use `lastRunFmt`/`decoTimeFmt`.

---

## Audit

130 automated checks. Run: `python3 audit.py`

---

*LSP D-PLANNER is a planning aid only. Not a substitute for training, certification, or a dive computer.*
