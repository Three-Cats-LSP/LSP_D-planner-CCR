## [1.0] - 2026-06-02

### 🎉 First Public Release

LSP D-PLANNER exits beta and ships as Version 1.0. All core features
are complete, audited, and tested across desktop and mobile.

Full Bühlmann ZHL-16C decompression engine with GF Low/High, all 16
N₂ compartments verified against ApexDeco, DivePro, MultiDeco and
DiveKit reference implementations.

### What's in 1.0
- Decompression planner: depth/BT → full deco schedule with EAD, ppO₂, CNS%
- Multi-gas support: bottom gas + up to 2 deco gases, optimal switch depths
- Emergency plans: gas loss + extended BT scenarios with combined deco
- Interactive dive profile graph: per-gas color zones, deco ceiling overlay,
  scroll/pinch zoom, drag pan, hover tooltip, dbl-click reset
- GF Gradient Factor curve with interactive hover tooltip
- Tissue saturation bars (all 16 compartments) + compartment detail table
- Gas consumption calculator with cylinder volume warnings (solid red)
- PDF export: 4-page deco plan + 3-page emergency plan, print-safe layout
- TXT export: golden column-aligned format for all plan modes
- Messenger export: compact plaintext for WhatsApp/Telegram briefings
- Light and dark themes, mobile-first responsive layout
- Imperial/metric units toggle
- No-decompression limits table, multi-dive repetitive planning
- CNS% / OTU tracker, MOD calculator, best mix calculator
- REF panel: full algorithm reference, M-values, half-times

### Technical
- 181 automated audit checks enforced before every release
- Pure vanilla JS/HTML/CSS — no dependencies, no frameworks
- Single-file deployment, works offline
- Hosted: https://three-cats-lsp.github.io/LSP_D-planner/

## [7.0] - 2026-06-01

### Added (Beta 7 — Interactive Graph)
- Scroll/wheel zoom: zoom in centered on cursor, scroll to zoom out
- Drag-to-pan: click and drag left/right along time axis
- Pinch-to-zoom: two-finger pinch on mobile/touchscreen
- Double-click: instant zoom reset to full view
- Zoom hint always shown (20% opacity at rest, 50% when zoomed)
- Per-gas color zones on profile line (each gas a distinct color)
- Deco ceiling line overlay (dashed red) computed from tissue state
- Ceiling depth shown in hover tooltip when above current position
- Gas switch flags: top-pinned colored labels with dashed line to depth
  (staggered 2 rows, never overlap stop dots)
- Planner graph: gas segments + ceiling waypoints + full zoom/pan
- Canvas aspect ratio 700×420 — scales proportionally on all screen sizes
- Mobile PAD tightened (36px left vs 52px) — more plot area on small screens
- APP_VERSION constant — version shown on main screen and REF panel,
  both set from single source; audit enforces consistency with VERSION file

### Fixed (Mobile graph polish)
- Canvas PAD ultra-tight on mobile: top 8px, right 4px, bottom 18px, left 26px
- Depth buffer reduced to 2% on mobile (was 15%) — profile fills near 100% of vertical axis
- Canvas aspect ratio 700/320 — less dead air vertically
- Axis label offsets tightened (3px depth, 12px time)
- Time grid step 15min on mobile for 60min dives — fewer, more legible labels
- Stop text labels suppressed on mobile canvas — numbered dots only; legend table below has all info
- Zoom hint moved outside canvas to HTML div below the frame — canvas stays clean
- Hint prefixed with "Hint:" so users know it's a usage tip, not stray code
- Hint brightens from 55% → 85% opacity when zoom is active
- Card padding reduced to 10px/8px on mobile
- "Version" label changed to "Beta" throughout (REF panel + main page)


- Gas segment fills: fixed 8-digit hex alpha (#rrggbbaa) silently ignored by
  canvas — converted all fills to rgba() format
- Gas segment time alignment: gsT origin was descentTime+bt (wrong) → bt,
  aligning gas color zones with profile waypoints and ceiling line
- Bottom gas segment: descent+bottom phase now covered by prepended segment
  (was missing entirely — cyan fill showed nothing)
- drawDecoProfile: bottom waypoint placed at t=btVal (run time) not
  t=descentT+btVal — was causing 2.3min mismatch between waypoints and
  gas segment boundaries
- Fill bleed between gas zones: each segment now clipped to exact x-column
  (no ±1px overlap padding that caused colour bleed)
- Fill flooding (deep column): clip rect now vertically capped at
  segTopY + proportional fadeH (50% of depth span, 60–200px) — deep
  segments like cyan descent get 200px fade, shallow deco stops get 60px
- Gradient fill: switched from top-of-plot anchor to segment shallowest-
  point anchor, so gradient fades from the actual profile line, not the axis
- Deco zone background rect: removed full-height solid rectangle that was
  flooding the lower 60% of the graph in both themes
- Ceiling line: removed artificial lead-point that was causing a rogue
  vertical stroke at the gas switch position
- Ceiling line: now samples during descent and bottom phases too (8 points
  during descent, 2 at bottom) so ceiling tracks from dive start
- Ceiling waypoint resolution: long segments now sample up to 8 intermediate
  points for a smooth curve through the ascent
- Stop labels: collision-avoidance — labels stagger upward when at same
  x-bucket; bottom dots label below, deco dots label above
- ppO₂ labels: placed on opposite side from main label; clamped to canvas
  right edge using measured text width
- Profile line: drawn in a separate pass (no clip) so segment joins are
  seamless — no gap at gas switch points
- Canvas plot clip (clipToPlot helper): all graph drawing clipped to plot
  area; labels drawn outside clip so they can extend into padding margins

- PDF garbled page 2: body padding-bottom 60px + page-break-inside:avoid
  on gas section prevents footer overlap with warning card
- Gas switch flag position: flags now pinned to top of graph, not at depth
- Canvas height responsive via aspect-ratio CSS (was fixed 240px)

---

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
