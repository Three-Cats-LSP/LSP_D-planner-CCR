# LSP D-Planner

**Version 2.8.4**

A technical dive decompression planner for mixed-gas deco diving. Runs entirely in the browser — no install, no build step, no server.

🌐 **Live App**: https://three-cats-lsp.github.io/LSP_D-planner/

📱 **Android APK**: [`Android Apk/LSP_D-planner.apk`](https://github.com/Three-Cats-LSP/LSP_D-planner/raw/main/Android%20Apk/LSP_D-planner.apk)

---

## Features

### Decompression Algorithms
- **Bühlmann ZH-L16C + Gradient Factors (GF)** — industry-standard tissue model with configurable Low/High GF presets or custom entry
- **VPM-B** — Varying Permeability Model bubble decompression with configurable conservatism margin
- **VPM-B/GF hybrid (VPM-B/GFS)** — VPM-B bubble mechanics set deep stop depth; GF High applied at shallow/surface stops only. GF High configurable via presets or custom.

### Dive Planning
- Multi-dive support with surface interval tissue loading
- Configurable descent / ascent / deco ascent / surface ascent rates
- Stop rounding (whole minute or 30-second)
- Water vapour correction (Bühlmann standard 0.0577 bar)
- Transit Mode (MultiDeco compatible) for deco algorithm switching
- **Named dive profile presets** — save and recall full dive setups, opened from the **★ PRESETS** button in the Decompression Schedule card header (see Tools & Productivity)

### Gas Management
- **Bottom gas** — primary mix including full trimix (O₂/He/N₂) with gas consumption tracking
- **Travel gas** — dedicated descent/ascent transit gas card (orange `🟠`)
  - Auto switch depth (based on MOD) or manual diver-set depth
  - Descent table split into travel-gas and bottom-gas rows
  - Ascent transit above bottom MOD handled automatically
- **Deco gases** — up to multiple deco mixes (nitrox or trimix), each with MOD display and cylinder tracking
- All gas cards show real-time MOD (maximum operating depth)
- SAC-based gas consumption in litres or cubic feet — converted correctly on unit switch

### Gas Labels
| Mix | Label |
|-----|-------|
| 21% O₂ / 0% He | `Air` |
| EAN32 | `32/00` |
| EAN50 | `50/00` |
| Trimix 21/35 | `21/35` |
| 100% O₂ | `100%` |

### Helium / Trimix Support
- Bottom gas: full trimix entry (O₂ %, He %)
- Deco gases: trimix deco gas entry for each gas card
- He half-time selector: Bühlmann 2003 (1.51 min) or Baker (1.88 min)
- Equivalent Narcotic Depth (END) display throughout the dive profile
- ppO₂ checks and MOD calculations fully He-aware
- All trimix fractions wired through VPM-B and Bühlmann engines

### Altitude Diving
- Altitude presets: sea level, 500 m, 1000 m, 1500 m, 2000 m, 2500 m, 3000 m, custom
- Acclimatization toggle (adjusts effective surface pressure)
- All engine calculations use altitude-corrected surface pressure
- **VPM-B: altitude-adjusted critical radii** — at altitude, lower crush pressure enlarges initial bubble nuclei: `r_alt = r₀ × (P_SL / P_alt)^(1/3)`; produces correctly reduced deco obligation at altitude
- Custom altitude input in both Tec and Rec modes; settings persisted across sessions

### VPM-B Repetitive Dives
- After any VPM-B calculation, a **Repetitive VPM Dive** panel appears
- Carries both **tissue gas pressures** (N₂/He off-gassing, Haldane) and **bubble state** (adjusted critical radii) from the previous dive into the next
- Bubble radii regenerate during surface interval: `r(t) = r_init + (r_end − r_init) × exp(−t / REGEN_TIME)` (REGEN_TIME = 14 days)
- Surface interval input (minutes) with persistent state
- Result summary shows altitude radii factor badge and repetitive dive badge

### Surface Interval Calculator
- **In-results panels** *(new in 2.8.1)* — a collapsible **Surface Interval** panel is available directly in both **Rec** and **Tec** results, below the dive output. It pre-fills Dive 1 depth and bottom time from the dive you just calculated.
- Also available as a standalone **Surf Int** sub-tab in the Tools tab.
- Simulates Dive 1 forward on the same Bühlmann ZH-L16C tissue model used by the planner, off-gasses all 16 compartments at the surface, and finds the minimum surface interval before a planned second dive.
- Shows minimum SI, recommended SI (min × 1.5), the controlling compartment, a reverse-profile warning, and a per-compartment tissue-loading bar chart.

### Units
- **Metric** (metres, bar, litres) and **Imperial** (feet, psi, cu ft) — switchable globally
- All inputs, labels, MOD displays, rate selectors, gas cards, and SAC values update on unit change
- Gas consumption volumes and SAC footer units correctly reflect current unit mode in both Bühlmann and VPM-B paths

### CNS & OTU Tracking
- Full CNS O₂ and OTU calculation throughout the dive profile
- Displayed per segment and as totals

### Tools Tab
The Tools tab bundles quick planning calculators and reference material:
- **MOD** — O₂% + ppO₂ slider → Maximum Operating Depth in m/ft
- **Best Mix** — depth + ppO₂ → best O₂%, ppO₂, and gas name
- **Max Depth** — O₂% → max depth at 1.4 and 1.6 bar (m + ft)
- **Avg Depth** — max + average depth → planning depth, ratio, profile class
- **Gas Table** — MOD and MND reference table for common mixes (Air, EAN32/36/40/50, 100% O₂, trimix 21/35, 18/45, 15/55). Live ppO₂ selector recalculates the MOD column; MND computed at END = 3.5 bar (N₂+O₂ narcotic, He non-narcotic). Respects metric/imperial units.
- **Surf Int** — Surface Interval calculator (also embedded in Rec and Tec results, see above). Simulates Dive 1 forward on the Bühlmann ZH-L16C tissue model, off-gasses all 16 compartments at the surface, and finds the minimum surface interval before a planned second dive. Shows minimum SI, recommended SI (min × 1.5), the controlling compartment, a reverse-profile warning, and a per-compartment tissue-loading bar chart.
- **Unit Converter** — bidirectional pressure / volume / depth / temperature / weight conversion
- **Knowledge** — static reference, algorithm notes, and links to the Knowledge Base PDFs

### Output & Export
- Colour-coded dive table (descent, bottom, deco stops)
- **END column toggle** — show/hide an Equivalent Narcotic Depth column directly in the deco table (button in the Dive Profile header). State persists across sessions and applies on every recalculation and on page load.
- **Deco Slate export** — compact, monospaced waterproof-slate format showing deco stops only (depth, cumulative run time, gas, ppO₂) with a header (date, algorithm, bottom + switch gases) and footer (total bottom time, total deco time). Opens in a copyable modal via the **SLATE** button (now with a slate/tablet icon). The same slate is also appended to **PDF** and **TXT** exports. Respects metric/imperial units.
- Export buttons ordered **Copy → SLATE → TXT → PDF**.
- Summary stats bar: max depth, bottom time, TTS, CNS, OTU, altitude chip, travel gas chip
- Gas tags strip: colour-coded pills per gas (surface → MOD ranges)
- Profile export / print view; TXT, COPY, and PDF exports include altitude and acclimatization state

### UI
- Unified `?` tooltip icon system across all settings — consistent colour, size, and style
- Algorithm, conservatism, GF, and altitude all have inline tooltip explanations
- Dark / light theme toggle

---

## Repository Structure

| Path | Purpose |
|------|---------|
| `index.html` | Self-contained web app — the entire planner in one file |
| `audit.py` | Static analysis script — 147 checks across 20+ groups. Run before every commit. |
| `vpmb.py` | VPM-B Python reference engine |
| `VpmbEngine.java` | VPM-B Java engine |
| `VpmbGfsEngine.java` | VPM-B/GF hybrid Java engine |
| [`tests.html`](https://three-cats-lsp.github.io/LSP_D-planner/tests.html) | Core regression suite — engine presence, NDL, deco, VPM-B, CNS/OTU, edge cases |
| [`tests-extended.html`](https://three-cats-lsp.github.io/LSP_D-planner/tests-extended.html) | Extended algorithm suite — GF, trimix, conservatism ordering, first stop depths |
| [`tests-massive.html`](https://three-cats-lsp.github.io/LSP_D-planner/tests-massive.html) | 294-check regression suite — engines, UI/DOM, travel gas, altitude, trimix, VPM, GF UI |
| `Knowledge Base/` | Reference PDFs and study materials (see below) |

### Knowledge Base

All reference documents used in developing and validating the planner are in `Knowledge Base/`:

| File | Description |
|------|-------------|
| `00_README_start_here.pdf` | Orientation guide for the KB |
| `Baker_1998_Understanding_M-Values_GradientFactors.pdf` | Baker — M-values and gradient factors explained |
| `VPM_Decompression_Reinders.pdf` | Reinders — VPM decompression theory |
| `VPM_Explanation_Corado.pdf` | Corado — VPM practical explanation |
| `VPM_for_Dummies_Andy_Davis.pdf` | Andy Davis — accessible VPM introduction |
| `VPM_FORTRAN_Source_Baker_VPMDECO.txt` | Baker's original VPMDECO FORTRAN source |
| `VPM_Knowledge_Base_LSP.pdf` | LSP internal VPM knowledge base |
| `EUBS_2009_Decompression_Conference.pdf` | EUBS 2009 decompression research proceedings |
| `Reverse_Dive_Profiles_Workshop_RDPW.pdf` | Reverse dive profiles workshop |
| `Dive_Computer_Manual_TDC-3.pdf` | TDC-3 dive computer manual |
| `Comparison_VPMBv32_vs_RGBM_GF_100ft_Air.pdf` | VPM-B vs RGBM/GF — 100 ft air |
| `Comparison_VPMBv32_vs_RGBM_GF_100ft_Nitrox32.pdf` | VPM-B vs RGBM/GF — 100 ft nitrox |
| `Comparison_VPMBv32_vs_RGBM_GF_100ft_Trimix3030.pdf` | VPM-B vs RGBM/GF — 100 ft trimix 30/30 |
| `Comparison_VPMBv32_vs_RGBM_GF_200ft_Trimix1845.pdf` | VPM-B vs RGBM/GF — 200 ft trimix 18/45 |
| `Comparison_VPMBv32_vs_RGBM_GF_300ft_Trimix1070.pdf` | VPM-B vs RGBM/GF — 300 ft trimix 10/70 |
| `Comparison_VPMB_vs_RGBM_GF_200ft_Trimix1845_TandG.pdf` | VPM-B vs RGBM/GF — T&G comparison 200 ft |
| `Comparison_HSE_vs_GAP_RGBM_200ft_Trimix1845.pdf` | HSE vs GAP RGBM — 200 ft trimix |
| `Materials and links.txt` | Additional study links and references |

---

## Running the Audit

```bash
python3 audit.py index.html
```

Exit 0 = all 147 checks pass. Run before every commit to main.

---

## Branches

| Branch | Purpose |
|--------|---------|
| `main` | Stable releases — what GitHub Pages serves |
| `dev` | Active development and new features |

---

## Deployment

Static single-file app. GitHub Pages serves `index.html` directly from the `main` branch. No build tools, no dependencies, no network calls at runtime.

To deploy a new version: replace `index.html` on `main`.

---

## Changelog

### 2.8.4 (current)

UX fixes over 2.8.3. Additive only — no engine changes; all 147 `audit.py` checks pass.

**Decompression table**
- **PRESETS button restyled** — the Decompression Schedule header PRESETS control now uses the `btn-export` style with a save (floppy-disk) icon, matching the Copy/SLATE/TXT/PDF export buttons.
- **END column always on** — the Equivalent Narcotic Depth column is now permanently visible in the deco table; the show/hide toggle was removed.

**Surface Interval**
- **Dedicated sub-tab** — Surface Interval is now a proper **Surf Int** sub-tab in the main tab bar, available at any time in both **Rec** and **Tec** modes (no calculation required first).

### 2.8.3

UX polish over 2.8.1. Additive only — no engine changes; all 147 `audit.py` checks pass.

**Decompression table**
- **Gas switch row border** — removed the bottom border and extra padding on the gas-switch row; only the thin top green border remains, so the row height matches every other row.
- **END column toggle fix** — the END column now reliably shows/hides on mobile too. A mobile-layout flex rule was overriding the column's hidden state; the toggle now wins in both desktop and mobile views.

**Surface Interval**
- **Always visible** — the embedded Rec/Tec Surface Interval panel containers now default to visible, so the collapsible panel header is shown after every dive calculation.

**Navigation & controls**
- **Reference button moved to top nav** — the `[?]` Reference & Info button moved to the header mode-switcher row, right after **🔧 Tools**, and was removed from the sub-tab and Tools tab bars.
- **PRESETS button restyled** — the Decompression Schedule header PRESETS control is now a compact `★` icon button matching the Rec/Tec/Tools style, instead of a large accent-colored button.

### 2.8.1

Bug fixes and UX improvements over 2.8.0. Additive only — no engine changes; all 147 `audit.py` checks pass.

**Decompression table**
- **Gas switch row border** — replaced the heavy inset box-shadow borders on the gas-switch row with standard thin 1px green borders, matching every other row; kept the yellow highlight. The row's colspan now spans all columns (including the optional END column), so no unfilled trailing cell remains.
- **END column toggle fix** — the END column now actually shows/hides when toggled. `applyEndColumn()` runs after every deco-table render (Bühlmann and VPM-B) and on page load when the toggle is already enabled from a previous session.

**Surface Interval**
- **Embedded in Rec and Tec results** — the Surface Interval calculator is now available as a collapsible panel directly within both Rec and Tec results, not just in the Tools tab. It pre-fills Dive 1 depth and bottom time from the dive just calculated. Collapsed by default.

**Output & export**
- **SLATE button icon** — the SLATE export button now shows a slate/tablet icon, matching the size and style of the other export buttons.
- **Export button order** — buttons reordered to **Copy → SLATE → TXT → PDF**.
- **Slate in PDF and TXT** — the deco slate is now appended as a section to both the PDF and TXT exports (reusing the same slate generator as the SLATE modal), not just the copyable modal.

**Productivity**
- **PRESETS button relocated** — the **★ PRESETS** button moved from the bottom of the gas settings to the Decompression Schedule card header, styled as a prominent accent button alongside the card title and help icon.

### 2.8.0

**New planning tools**
- **Gas Table** — new Tools sub-tab: MOD and MND quick-reference table for common nitrox and trimix mixes (Air, EAN32/36/40/50, 100% O₂, 21/35, 18/45, 15/55). Live ppO₂ selector recalculates the MOD column; MND computed at END = 3.5 bar (N₂+O₂ narcotic, He non-narcotic). Respects metric/imperial units.
- **Surface Interval calculator** — new Tools sub-tab: simulates Dive 1 on the existing Bühlmann ZH-L16C tissue model, off-gasses all 16 compartments at the surface, and finds the minimum surface interval for a planned second dive. Reports minimum SI, recommended SI (× 1.5), controlling compartment, a reverse-profile warning, and a tissue-loading bar chart.

**Output & export**
- **Deco Slate export** — new **SLATE** button: compact monospaced waterproof-slate output (deco stops only, cumulative run time, gas, ppO₂) with date/algorithm/gas header and TBT/deco-time footer, in a copyable modal. Respects units.
- **END column toggle** — show/hide an Equivalent Narcotic Depth column in the deco table from the Dive Profile header; trimix-aware (He non-narcotic); state persisted in `localStorage`.

**Productivity**
- **Named dive profile presets** — save the full dive setup (algorithm, GF/conservatism, all gas mixes and cylinders, depth, bottom time, altitude, water type, SAC, min-deco settings, rounding) as a named preset and recall it later. Stored in `localStorage` (up to 20 presets); each preset shows a one-line summary.

**Quality**
- All 147 `audit.py` checks pass; changes are additive over 2.7.8 with no engine changes.

### 2.7.8

**Algorithms**
- **getPPO2Limit trimix fix** — function previously used `1-fN2` as fO2, which is wrong for trimix (e.g. 21/35 trimix gave fO2=0.56 instead of 0.21, selecting the wrong ppO2 band and placing the switch depth ~9m too shallow). Fixed in 4 places: function signature now takes fO2 directly; all call sites compute `Math.max(0, 1-fN2-fHe)` before calling

**Quality**
- **audit.py** — expanded to 147 checks; Group 23 added covering `getPPO2Limit` trimix correctness

### 2.7.7

**Decompression**
- **Min Deco Profile UI** — Off/On toggle and 9m/6m inputs now flow as standard-sized grid cells alongside other settings (no overflow, correct on mobile and desktop)
- **Reset to Defaults** — fixed 6 fields that were not being reset: `minDecoProfileEnable`, `minDeco9m`, `minDeco6m`, `cylTravelGas_size`, `cylTravelGas_pres`, `heHalfTimeMode`

**Quality**
- **audit.py** — expanded to 143 checks; new Groups 21 (Min Deco Profile) and 22 (Reset to Defaults completeness)
- Tooltip title renamed to **Minimum Decompression Profile**

### 2.7.6

**Decompression**
- **Min Deco Profile** — settings toggle with configurable 9m and 6m minimum stop durations; injected stops always show the correct actively-breathed gas (not bottom gas); stop table order correct with ascent rows split around injected stops; ppO₂ computed for injected stops

**Android**
- APK version number now propagates from `APP_VERSION` in `index.html` at build time
- External links open in system browser
- APK download icon visible in web view only (hidden inside app)

**UI**
- Browser window title renamed to **Rec & Tec**
- Min Deco Profile settings and values included in TXT, copy, and PDF exports

### 2.7.3

**Android**
- **APK download icon** — third footer icon (alongside Instagram and GitHub) links directly to `Android Apk/LSP_D-planner.apk` for one-tap device download

**UI**
- **Custom reset confirm dialog** — replaced native `confirm()` with an in-app modal; removes the "The page at file:// says:" prefix shown by Android WebView

### 2.7 (milestone)

**Algorithms**
- **Helium / Trimix** — full O₂/He/N₂ entry for bottom gas and all deco gases; He half-time selector (Bühlmann 2003 1.51 min / Baker 1.88 min); END display throughout profile
- **VPM-B altitude-adjusted critical radii** — bubble nuclei radii scaled by `(P_SL / P_alt)^(1/3)` at altitude; sea-level dives unchanged
- **VPM-B repetitive dive bubble state carry** — carries tissue loading and per-compartment bubble radii between dives; surface-interval regeneration model
- **VPM-B/GFS GF UI** — GF High-only mode when VPMB_GFS selected (VPM-B bubble mechanics replace GF Low); preset dropdown rebuilt with Hi-only values; restores full Low+High UI on switch back to Bühlmann

**Gas & Units**
- **Travel gas** — dedicated card, descent table split, ascent transit above bottom MOD
- **Gas label format** — standardised to O₂/He fraction notation (`32/00`, `21/35`, `100%`, `Air`)
- **Imperial gas consumption** — SAC values convert correctly on unit switch (L/min ↔ cu ft/min); gas card volumes show `cu ft` in imperial mode; SAC footer label switches in both Bühlmann and VPM paths

**UI**
- **Unified `?` tooltip system** — consistent icon colour, size, and style across all tooltip instances; GF and altitude tooltips added
- **Footer icons** — Instagram and GitHub icons same size (36px), vertically centered

**Quality**
- **`audit.py`** — 111 static checks across 20+ groups
- **`tests-massive.html`** — 294-check regression suite including algorithm switching, VPM-B/GFS GF UI, SAC unit conversion, gas volume display
- **Knowledge Base** — 18 reference PDFs organised in `Knowledge Base/` directory
- **Dead code removed** — `zFactorN2` (non-standard, incompatible with ZHL-16C ideal-gas model)

### 2.5
- Altitude + Acclimatize in exports
- GF custom dropdowns
- Tap/click tooltip popups with SVG `?` icon
- Travel gas — full implementation
- Altitude diving — altitude-corrected surface pressure for all engine calculations
- Metric/Imperial unit switching across all inputs and displays
- GF fixes — default GF corrected to 20/85
- Bühlmann ZH-L16C + GF engine
- VPM-B / VPM-B/GF algorithms
- Multi-dive support
- Transit Mode (MultiDeco)
- CNS / OTU tracking

---

## Disclaimer

**Planning Aid Only.** This tool is not a substitute for formal dive training, certification, or a calibrated dive computer. Decompression models are theoretical and carry inherent uncertainty. Always dive within your training and experience level. Use at your own risk.

---

*Developed by Three Cats LSP · [@threecats_lsp](https://www.instagram.com/threecats_lsp)*


