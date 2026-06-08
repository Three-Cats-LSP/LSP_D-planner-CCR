# LSP D-Planner

**Version 2.6**

A technical dive decompression planner for mixed-gas deco diving. Runs entirely in the browser — no install, no build step, no server.

🌐 **Live App**: https://three-cats-lsp.github.io/LSP_D-planner/

---

## Features

### Decompression Algorithms
- **Bühlmann ZH-L16C + Gradient Factors (GF)** — industry-standard tissue model with configurable Low/High GF
- **VPM-B** — Varying Permeability Model bubble decompression
- **VPM-B/GF hybrid** — VPM-B conservatism with GF ceilings

### Dive Planning
- Multi-dive support with surface interval tissue loading
- Configurable descent / ascent / deco ascent / surface ascent rates
- Stop rounding (whole minute or 30-second)
- Water vapour correction (Buhl standard 0.0577 bar)
- Transit Mode (MultiDeco compatible) for deco algorithm switching

### Gas Management
- **Bottom gas** — primary mix including full trimix (O₂/He/N₂) with gas consumption tracking
- **Travel gas** — dedicated descent and ascent transit gas card (orange `🟠`)
  - Auto switch depth (based on MOD) or manual diver-set depth
  - Descent table split into travel-gas and bottom-gas rows
  - Ascent transit above bottom MOD handled automatically
- **Deco gases** — up to multiple deco mixes (nitrox or trimix), each with MOD display and cylinder tracking
- All gas cards show real-time MOD (maximum operating depth)
- SAC-based gas consumption in litres or cubic feet

### Helium / Trimix Support (v2.6)
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
- Custom altitude input available in both Tec and Rec modes
- Settings persisted across sessions

### VPM-B Repetitive Dives (v2.6)
- After any VPM-B calculation, a **Repetitive VPM Dive** panel appears
- Carries both **tissue gas pressures** (N₂/He off-gassing, Haldane) and **bubble state** (adjusted critical radii) from the previous dive into the next
- Bubble radii regenerate during surface interval: `r(t) = r_init + (r_end − r_init) × exp(−t / REGEN_TIME)` (REGEN_TIME = 14 days)
- Surface interval input (minutes) with persistent state
- Result summary shows altitude radii factor badge and repetitive dive badge

### Units
- **Metric** (metres, bar, litres) and **Imperial** (feet, psi, cu ft) — switchable globally
- All inputs, labels, MOD displays, rate selectors, and gas cards update on unit change

### CNS & OTU Tracking
- Full CNS O₂ and OTU calculation throughout the dive profile
- Displayed per segment and as totals

### Output
- Colour-coded dive table (descent, bottom, deco stops)
- Summary stats bar: max depth, bottom time, TTS, CNS, OTU, altitude chip, travel gas chip
- Gas tags strip: colour-coded pills per gas (surface → MOD ranges)
- Profile export / print view
- Export includes Altitude and Acclimatization state

---

## Repository Files

| File | Purpose |
|------|---------|
| `index.html` | Main self-contained web app — the entire planner in one file |
| `audit.py` | Static analysis script — 17 groups, 81 checks. Run before every commit. |
| `vpmb.py` | VPM-B Python reference engine |
| `VpmbEngine.java` | VPM-B Java engine |
| `VpmbGfsEngine.java` | VPM-B/GF hybrid Java engine |
| [`tests.html`](https://three-cats-lsp.github.io/LSP_D-planner/tests.html) | Core regression test suite |
| [`tests-extended.html`](https://three-cats-lsp.github.io/LSP_D-planner/tests-extended.html) | Extended algorithm regression suite |
| [`tests-massive.html`](https://three-cats-lsp.github.io/LSP_D-planner/tests-massive.html) | Massive test suite — 288 checks, engine plans, UI/DOM integration, travel gas, altitude, trimix, VPM |

---

## Running the Audit

```bash
python3 audit.py index.html
```

Exit 0 = all 81 checks pass. Run before every commit to main.

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

### 2.6
- **Helium / Trimix support** — full O₂/He/N₂ entry for bottom gas and all deco gases; He half-time selector (Bühlmann 2003 1.51 min / Baker 1.88 min); END display throughout profile
- **VPM-B altitude-adjusted critical radii** — initial bubble nuclei radii scaled by `(P_SL / P_alt)^(1/3)` at altitude; sea-level dives unchanged
- **VPM-B repetitive dive bubble state carry** — carries both tissue loading and per-compartment bubble radii between dives with surface-interval regeneration; UI panel with surface interval input and persistent checkbox state
- **Bug fixes (8 + 1 bonus):**
  - `bottomMixLabel` declared before `bottomFO2`/`bottomFHe` — crash fixed
  - `bottomO2pct` used `1 - fN2` — wrong for trimix; fixed to `fO2`
  - Deco gas O₂% tags used `1 - fN2` — wrong for trimix; fixed
  - `optimalSwitchDepth()` used `1 - fN2` — wrong for trimix; `fO2override` param added
  - `ppO2Check()` ignored He — `fHe` param added, all 5 call sites updated
  - `updateHeHalfTime()` never called on init — VPM-B always used Baker 1.88; fixed
  - 7 trimix fields missing from `DECO_FIELDS` — all added for persistence
  - Ceiling descent waypoints missing `bottomFHe` in `saturateLinear` — fixed
  - **Bonus:** `getActiveGas()` used `1 - dg.fN2` for ppO₂ check — trimix deco gases rejected; fixed
- **`audit.py`** — static analysis script (17 groups, 81 checks) added to repo

### 2.5
- **Altitude + Acclimatize in exports** — altitude label and acclimatization state now appear in text export, copy output, and TXT filename suffix
- **"Alt:" label** — toolbar label shortened for cleaner interface
- **Rec mode custom altitude input** — Custom altitude option in Rec toolbar now shows an input field
- **GF custom dropdowns** — GF Low and High replaced with dropdowns for easier entry
- **Tap/click tooltip popups** — all settings info icons replaced with tap/click `?` SVG buttons
- **SVG `?` icon** — pixel-perfect pure-path SVG icon for all tooltip buttons

### 2.5 Beta 2
- **Travel gas** — full implementation with dedicated card, descent table split, ascent transit
- **Altitude diving** — altitude-corrected surface pressure for all engine calculations
- **Metric/Imperial fix** — complete unit switching across all inputs and displays
- **GF fixes** — default GF corrected to 20/85

### 2.5 Beta 1
- Bühlmann ZH-L16C + GF engine
- VPM-B / VPM-B/GF algorithms
- Multi-dive support
- Transit Mode (MultiDeco)
- CNS / OTU tracking
- Metric / Imperial unit switching

---

## Disclaimer

**Planning Aid Only.** This tool is not a substitute for formal dive training, certification, or a calibrated dive computer. Decompression models are theoretical and carry inherent uncertainty. Always dive within your training and experience level. Use at your own risk.

---

*Developed by Three Cats LSP · [@threecats_lsp](https://www.instagram.com/threecats_lsp)*
