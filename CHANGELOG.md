# Changelog

## [5.8.0] - 2026-05-30

### Added
- Average Depth Converter tool (Tools tab) — converts log-book avg depth to planning depth, classifies profile type, explains when avg depth is/isn't safe for repetitive planning
- Dive Solver (Multi Dive → Solver tab) — interactive sliders showing max bottom time and minimum surface interval for 2–4 dive days, driven by real Bühlmann tissue simulation
- Custom O₂% option in Multi Dive gas selector for each dive

### Fixed
- Units toggle moved to global header — single control affects all tabs (Planner, Bühlmann, NDL, Multi Dive)
- Safety stop depth buttons now update to ft when imperial selected (was showing "3 m / 6 m" regardless)
- Dive Solver now responds to dive count selection (2/3/4)

---

## [5.7.0] - 2026-05-30

### Algorithm fixes (critical)

**Baker GF formula** — ceiling was calculated using `(pN2 − a·gf)·b` (incorrect). Correct formula per Baker 1998: `(pN2 − gf·a) / (1 − gf + gf/b)`. This is the most significant fix: moves 12m stop times from 1:00 to ~3:20 (target: 4:00).

**ZHL-16C constants** — updated to canonical values matching ApexDeco and DiveProMe source:
- Compartment 1: ht=4.0 min (was 5.0), a=1.2599, b=0.5050
- Compartments 5–15: corrected a-values

**Water vapour** — alveolar water vapour (0.0627 bar at 37°C) now subtracted from inspired gas in all tissue loading functions.

### Other changes
- Three ascent rates: to first stop / between stops / last stop to surface
- GF presets updated to 30/70 / 40/80 / 70/85
- Stop times display as fractional minutes (no rounding)
- ASCII-safe export dividers (= and − not box-drawing characters)

---

## [5.6.3] - 2026-05-28

Initial public release. PADI RDP recreational planning, Bühlmann ZH-L16C deco schedule, multi-dive planning, CNS/OTU tracking, export to text/PDF/clipboard.
