## [6.0.2] - 2026-05-31

### Fixed
- Emergency PDF: gas consumption now shows color progress bars and avail status (matching deco PDF and web view)
- Emergency PDF: gas shortage warning card now included when gas is insufficient
- PDF table: Depth, Stop, Run, EAD, PPO2 columns now right-aligned in both deco and emergency PDF exports
- Emergency PDF standalone (exportContingencyPDF): added nth-child right-align CSS + gas switch rows forced left

### Changed
- Export filename: 'Contingency' renamed to 'Emergency' in both TXT and PDF filenames for clarity
  (e.g. LSP_..._Emergency_50m_25min_Lost_EAN_50.txt)

---

# Changelog

## [6.0.1] - 2026-05-31

### Fixed (Critical)
- Dive profile graph: gas switch waypoints injected out-of-order caused diagonal "fan" lines — fixed by sorting wps by time; gasswitch type excluded from profile line/fill/tooltip interpolation
- TXT export: `ppO₂` (subscript Unicode) in Note field — fixed at source in calcContingency msg + clean(c.msg) safety net
- TXT export: all three clean() helpers now fully ASCII-safe (→, —, ≈, ≥, Bühlmann, expanded emoji strip)
- Contingency TXT: mix column was outputting raw DOM text (AIR (21%)) — added shortMix() to contingency branch

### Fixed (TXT Column Alignment)
- Depth, Stop, Run, EAD, PPO2 columns: numeric values right-justified (padStart) for clean column alignment
- Header 49 chars, separator 49 dashes — matched exactly
- Header field separators: 2-space (was 4-space); gas switch single space before parenthesis

### Fixed (Messenger)
- Contingency messenger: run/deco totals now mm'ss" format with CNS% (was plain integer minutes, missing CNS)
- Contingency clean(): digit-unit collapse added (50 m → 50m)
- EAN shortMix: no space (EAN50 not EAN 50) consistent across all paths

### Added
- Interactive dive profile graph: hover/touch tooltip with depth, time, gas, ppO2, CNS%
- Gas switch vertical markers on profile graph (dashed cyan lines)
- Single merged deco zone background (replaces per-stop overlapping fills)
- Unit-aware depth axis labels in profile graph and GF curve
- Contingency PDF: dive profile graph page
- audit.py: 87 automated pre-release checks

### Changed (PDF)
- Section headers: 13px → 10px, tighter padding
- Tissue saturation bars: full-width SVG viewBox
- Footer: padding-bottom 40px prevents overlap

### Changed (UI/Theme)
- Light theme yellow: #FAFA33 → #FFBF00 (Amber)
- Light theme green: #7CFC00 → #50C878 (Emerald)
- Web deco table: Depth/Stop/Run/EAD/PPO2 right-aligned; gas switch rows left-aligned
- Settings row mobile: left-aligned (was centered)
- REF button: moved to tabs-nav and Tools sub-nav right side
- PDF export button: plain 16×16px text span (was small-text document SVG)


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
