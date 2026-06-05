# LSP D-PLANNER Changelog

## v2.0 Beta 1 — 2026-06-05

### New Features
- **VPM-B** (Varying Permeability Model) — fully implemented, verified 9/9 vs MultiDeco C+2
- **VPM-B/GFS** — VPM-B with Gradient Factor surface stop
- **Real PDF export** via jsPDF with Noto Sans Unicode font (replaces `window.print()`)
  - Deco PDF: stat grid, gas tags, alerts, deco table, CNS highlighting, gas consumption, dive graph + stop legend, GF curve + legend, tissue saturation bars, compartment detail
  - Emergency PDF: same complete set including GF curve, tissue saturation, compartment detail
- **Unified colour system**:
  - RoyalBlue `#4169E1` — deco gas elements (cards, pills, banners, switch borders)
  - Nitrox sticker standard `#FFD700`/`#007A33` — gas switch rows
  - Red `#cc0000` — all danger/warning banners unified
- **Warning modal** — I UNDERSTAND only (Close button removed for safety)
- **CNS alert** correctly isolated to emergency card (not main deco plan)
- **Deco table** `vertical-align:middle` on all rows

### Fixes
- O2 switch at correct 6m depth (was 3m)
- VPM CNS calculation corrected (removed spurious ×100)
- Emergency plan CNS banner appears only under emergency table
- PDF gas switch row equal top/bottom border weight
- PDF graph legends match web view numbered stop tables

### Audit
- 182 checks passing (up from 142 in v1.3)

---

## v1.3 — Previous Release
- Bühlmann ZHL-16C+GF fully verified
- Last Bühlmann-only release
