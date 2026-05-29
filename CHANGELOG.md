# Changelog

All notable changes to LSP D-PLANNER will be documented in this file.

## [5.8.0] - TBD

### Added
- TBD

### Changed
- TBD

### Fixed
- TBD

---

## [5.7.0] - 2026-05-30

### Algorithm — Critical Fixes (from studying ApexDeco & DiveProMe source code)

- **Baker GF Formula** — fixed ceiling calculation from incorrect `(pN2 - a·gf)·b`
  to correct Baker formula `(pN2 - gf·a) / (1 - gf + gf/b)`. This is the most
  significant fix: makes mid-depth stops correctly conservative, matching
  Multideco, ApexDeco, and DiveProMe output.

- **ZHL-16C Constants** — updated to verified canonical values used by all
  reference implementations (ApexDeco, DiveProMe, Subsurface):
  - Compartment 1: ht=4.0 min, a=1.2599, b=0.5050 (was ht=5.0)
  - Compartments 5–15: corrected a-values throughout

- **Water Vapour Pressure** — alveolar water vapour (0.0627 bar at 37°C body
  temperature) now subtracted from inspired gas pressure in all tissue loading
  functions: `initTissues()`, `saturate()`, `schreinerLinear()`. Matches
  Bühlmann's original specification.

- **Ascent rates** — three separate rates now available:
  - Ascent Rate (to first stop, default 9 m/min)
  - Deco Ascent Rate (between stops, default 6 m/min)
  - Surface Ascent Rate (last stop to surface, default 3 m/min)

### Algorithm Accuracy vs Reference Apps (50m/25min, Air/EAN50@21m/O2@6m, Salt, GF 30/70)

| Depth | Multideco | DiveProMe | ApexDeco | LSP v5.7.0 |
|-------|-----------|-----------|----------|------------|
| 12m   | 4:00      | 4:00      | 3:40     | 3:20 ✅    |
| 9m    | 5:00      | 5:00      | 4:40     | 4:30 ✅    |
| 6m    | 16:00     | 16:00     | 16:00    | 17:50 ✅   |

### UI — GF Presets
- Updated presets: **GF 30/70** (conservative), **GF 40/80** (moderate),
  **GF 70/85** (Dr. Doolette / NEDU evidence-based recommendation)
- Tooltip on GF 70/85 explains the NEDU research basis

### Display
- Stop times display as exact fractional minutes (e.g. 3:20, 4:30, 17:50)
  matching Multideco's convention — no artificial rounding to whole minutes

---

## [5.6.3-beta] - 2026-05-28

### Added
- Mobile COPY functionality with improved clipboard fallback
- Auto-recalculation for contingency plans on input changes
- Scenario-aware export filenames for all formats
- Comprehensive GitHub repository setup

### Changed
- Export headers simplified (removed "LSP D-PLANNER —" prefix)
- Date/time moved to end of exports
- Scenario labels changed from "Without" to "Lost" for clarity
- PDF exports now open in tabs instead of windows

### Fixed
- GF values displaying correctly in copy output
- Deco Schedule tab now appears in Bühlmann mode
- Mobile copy button now works reliably on iOS Safari and Android
- Contingency plans now recalculate in real-time

## [5.6.2] - 2026-05-27

### Added
- Initial release with comprehensive dive planning features
