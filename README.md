# LSP D-Planner

**Version 2.5**

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
- **Bottom gas** — primary mix with full cylinder gas consumption tracking
- **Travel gas** — dedicated descent and ascent transit gas card (orange `🟠`)
  - Auto switch depth (based on MOD) or manual diver-set depth
  - Descent table split into travel-gas and bottom-gas rows
  - Ascent transit above bottom MOD handled automatically
- **Deco gases** — up to multiple deco mixes, each with MOD display and cylinder tracking
- All gas cards show real-time MOD (maximum operating depth)
- SAC-based gas consumption in litres or cubic feet

### Altitude Diving
- Altitude presets: sea level, 500 m, 1000 m, 1500 m, 2000 m, 2500 m, 3000 m, custom
- Acclimatization toggle (adjusts effective surface pressure)
- All engine calculations use altitude-corrected surface pressure
- Custom altitude input available in both Tec and Rec modes
- Settings persisted across sessions

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
- **Export includes Altitude and Acclimatization** — text export, copy, and TXT filename all reflect current altitude and acclimatization state

---

## Repository Files

| File | Purpose |
|------|---------| 
| `index.html` | Main self-contained web app — the entire planner in one file |
| `vpmb.py` | VPM-B Python reference engine |
| `VpmbEngine.java` | VPM-B Java engine |
| `VpmbGfsEngine.java` | VPM-B/GF hybrid Java engine |
| [`tests.html`](https://three-cats-lsp.github.io/LSP_D-planner/tests.html) | Core regression test suite |
| [`tests-extended.html`](https://three-cats-lsp.github.io/LSP_D-planner/tests-extended.html) | Extended algorithm regression suite |
| [`tests-massive.html`](https://three-cats-lsp.github.io/LSP_D-planner/tests-massive.html) | Massive test suite — 300+ engine plans, UI/DOM integration, travel gas, altitude, imperial, stress tests |

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

### 2.5
- **Altitude + Acclimatize in exports** — altitude label and acclimatization state now appear in text export, copy output, and TXT filename suffix (`_AltNNNmAccl` / `_AltNNNmNoAccl`); no suffix added at sea level
- **"Alt:" label** — toolbar label shortened from "Altitude:" to "Alt:" in both Tec and Rec modes for a cleaner interface
- **Rec mode custom altitude input** — Custom altitude option in Rec toolbar now shows an input field (mirrors Tec side behaviour); `applyCustomAltitudeRec()` syncs value back to engine
- **GF custom dropdowns** — GF Low and High custom inputs replaced with dropdowns (Low: 10–100 step 5, default 40; High: 50–100 step 5, default 80) for easier entry on touchscreens and desktop
- **Tap/click tooltip popups** — all 11 settings info icons replaced with tap/click `?` SVG buttons that open a centred popup modal (`#tipModal`); hover-only tooltips removed for full mobile compatibility
- **SVG `?` icon** — pixel-perfect pure-path SVG icon used for all tooltip buttons and the Decompression Schedule header `?` button, ensuring consistent design across all controls
- **tipModal display fix** — removed duplicate `display:none` in inline style that prevented the popup from opening

### 2.5 Beta 2
- **Travel gas** — full implementation: dedicated card below bottom gas, descent table split into travel + bottom rows, ascent transit above bottom MOD, orange UI accent throughout
- **Altitude diving** — altitude-corrected surface pressure for all engine calculations (ceiling, depth bar, tissue init), dropdown presets with acclimatization toggle, localStorage persistence
- **Metric/Imperial fix** — complete: all gas card inputs, cylinder fields, MOD displays, travel gas switch depth, and dynamic deco gas cards all respond to global unit setting
- **GF fixes** — default GF corrected to 20/85; `setCustomGF` no longer clamps mid-type; `appSettings` correctly tracks both GF fields
- **Altitude globals** — `altSurfaceP`, `altitudeM`, `altAcclimatized` exposed on `window` for test suite access
- **Help system** — `?` modal and `📖` Reference updated with Travel Gas and Altitude sections; field-level tooltips on all new controls

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
