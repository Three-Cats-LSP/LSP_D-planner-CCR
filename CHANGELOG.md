# Changelog

## [5.8.5] - 2026-05-30

### Added
- SAC rate / gas consumption — bottom + deco SAC, per-gas litres, cylinder runtime
- EAD per stop — in deco table, TXT and PDF exports
- Tissue saturation bar graph — 16 compartments under deco plan
- Cylinder setup inline with each gas card (size + bar/psi)
- Emergency Gas Consumption card (separate from main plan)
- Automated audit pipeline — 28 checks before every package

### Fixed
- Imperial units: comprehensive fix across all UI, exports, graphs, PDFs
- Export ASCII: zero non-ASCII in all TXT/copy exports (—, ·, •, ⚠ all replaced)
- PDF: EAD column added, colspan corrected, filenames consistent
- Graph: dive profile X-axis was cut short (lastT included totals row)
- REF section: depth limits and NDL dropdown now update with units
- Bühlmann mode: no stale planner result flash on algo switch
- Mobile: two-row result headers, icon-only export buttons

---

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
