# LSP D-Planner

A technical dive decompression planner for recreational and mixed-gas technical diving. Runs entirely in the browser — no install, no build step, no server required.

Part of the [Three Cats LSP](https://threecats-lsp.com) **Diver's Toolkit**.

🌐 **Live App**: https://threecats-lsp.com/d-planner/

**Current version: 2.20.21**

---

## Diver's Toolkit

| App | Purpose |
|-----|---------|
| **LSP D-Planner** | Decompression planning (this app) |
| **[T-Viewer](https://threecats-lsp.com/t-viewer/)** | Open and share exported dive plan TXT/PDF files |
| **[Get In Water](https://threecats-lsp.com/get-in-water/)** | Trip packing checklists |

All apps live on the [Diver's Toolkit hub](https://threecats-lsp.com).

---

## Web App

Open https://threecats-lsp.com/d-planner/ in any modern browser — no install required. Add it to your home screen for quick access like a native app.

**Installation:**
1. Open https://threecats-lsp.com/d-planner/ on your phone, tablet, or computer
2. **Safari (iPhone / iPad):** Tap **Share** (square with arrow) → **Add to Home Screen** → **Add**
3. **Chrome (Android):** Tap **⋮** menu → **Install app** or **Add to Home screen** → confirm
4. **Chrome (desktop):** Click the install icon in the address bar, or **⋮** → **Install LSP D-Planner**

---

## Android App

LSP D-Planner is available as a native Android app built with Capacitor by Ionic.

📲 **[Download APK](https://threecats-lsp.com/d-planner/download.html)**

> Direct download page: https://threecats-lsp.com/d-planner/download.html

**APK installation:**
1. Open the download page on your Android device
2. Tap **Download APK**
3. Open the downloaded file from your Downloads folder
4. If prompted, allow *Install from unknown sources* in Settings
5. Install and launch LSP D-Planner

**What the app includes:**
- Full offline operation — no internet required after install
- Edge-to-edge transparent status bar — app content fills the full screen
- Status bar icon color synced to light/dark theme (dark icons in light mode, white in dark mode)
- Export dive plans as TXT and PDF directly to your Downloads folder
- Dark/light theme with collapsible ENV and Advanced Settings panels
- All algorithms (Bühlmann ZHL-16C + GF, VPM-B, VPM-B/GFS), all tools

---

## T-Viewer

[T-Viewer](https://github.com/Three-Cats-LSP/T-Viewer) is a companion app for reading dive plan **TXT** and **PDF** files exported by LSP D-Planner — syntax highlighting, edit mode, pinch-to-zoom, and share on Android or in the browser.

📲 **[Download T-Viewer APK](https://threecats-lsp.com/t-viewer/download.html)**

🌐 **Web app**: https://threecats-lsp.com/t-viewer/

---

## Get In Water

[Get In Water](https://github.com/Three-Cats-LSP/Get-In-Water) is a companion app for **dive trip packing** — master gear list, starter templates (Rec, Photo, Tech), per-trip checklists with quantities, notes, critical items, packing phases, tags, unpack mode, buddy copy, JSON backup, Android widget, and TXT/PDF export.

📲 **[Download Get In Water APK](https://threecats-lsp.com/get-in-water/download.html)**

🌐 **Web app**: https://threecats-lsp.com/get-in-water/

**Current version: 1.3.0**

---

## Overview

LSP D-Planner supports two modes: **Rec** for recreational divers using PADI-based NDL tables, and **Tec** for technical divers requiring full decompression planning with trimix, multiple deco gases, and advanced algorithms. Everything runs client-side in a single `index.html` file with no external dependencies.

---

## Decompression Algorithms

Three algorithms are available, switchable at any time:

- **Bühlmann ZH-L16C + Gradient Factors (ZHLC_GF)** — dissolved gas tissue model with 16 parallel compartments. GF Low and GF High are fully configurable via presets or custom entry. GF Low controls first-stop depth; GF High controls the surface ceiling. Default 55/80.
- **VPM-B** — Varying Permeability Model bubble mechanics. Tracks bubble nuclei in tissues rather than tissue tension. Produces more and shallower deep stops compared to Bühlmann. Conservatism margin configurable from +0 to +5.
- **VPM-B/GFS** — Hybrid mode: VPM-B bubble mechanics set the deep stop depth, GF High applied at shallow and surface stops. GF High configurable via presets or custom entry.

---

## Rec Mode

Recreational dive planning using the PADI Recreational Dive Planner (RDP) lookup table:

- NDL time lookup for any depth and gas mix (air or nitrox)
- Pressure group tracking (A–Z) for repetitive dives
- Recommended surface interval calculation between dives
- Nitrox MOD and best mix calculator

**Rec sub-tabs:** Deco Schedule / Dive Planner / Surf Int / Avg Depth / Multi Dive / CNS O₂ / NDL Tables

---

## Tec Mode — Decompression Planning

Full decompression schedule calculation for multi-gas technical dives:

- Configurable descent rate, ascent rate, deco ascent rate, and surface ascent rate
- Stop rounding: whole minute or 30-second intervals
- Water vapour correction (default **0.0577 bar** — MultiDeco; Bühlmann **0.0627 bar** also available)
- **Transit Mode** — Schreiner (accurate) or MultiDeco-compatible ascent tissue loading
- **EAD / END columns** — Equivalent Air Depth and Equivalent Narcotic Depth in the deco table; trimix-aware
- Colour-coded deco table: descent, bottom, first deco stop, gas switch rows

### Deco Table Column Order

| # | Column | Description |
|---|--------|-------------|
| 0 | Phase | Row type (Desc / Bott / Deco / Switch) |
| 1 | Depth | Stop depth in m or ft |
| 2 | Stop | Stop duration in minutes |
| 3 | Mix | Gas mix label (e.g. `21/35`, `50/00`) |
| 4 | Run | Cumulative run time MM:SS |
| 5 | TTS | Time To Surface from this stop |
| 6 | PPO2 | Partial pressure of O₂ at stop depth |
| 7 | END | Equivalent Narcotic Depth |
| 8 | EAD | Equivalent Air Depth |
| 9 | CNS% | CNS oxygen toxicity contribution |

Columns auto-size to their content (`width:min-content`) — no fixed widths, no empty space. The table wrapper enables horizontal scroll on small screens.

### Warning Banners

Both warning banners use the same unified red style (`#FF4433` background, white bold text):

- **NARCOTIC DEPTH WARNING** — shown when END exceeds the narcotic depth threshold
- **DECOMPRESSION DIVE** — shown when the dive requires decompression stops

---

## Gas Management

### Bottom Gas
Full trimix entry (O₂ %, He %). Auto-labelled by composition:

| Mix | Label |
|-----|-------|
| 21% O₂ / 0% He | `Air` |
| EAN32 | `32/00` |
| EAN50 | `50/00` |
| Trimix 21/35 | `21/35` |
| 100% O₂ | `100%` |

### Travel Gas
Dedicated descent/ascent transit gas card. Auto-switch depth based on MOD or manually set. Descent table shows travel-gas and bottom-gas rows separately. Ascent transit above bottom gas MOD handled automatically.

### Deco Gases
Multiple deco gas cards (nitrox or trimix), each with MOD display and cylinder tracking. ppO₂ checks and MOD calculations are fully He-aware across all gas cards.

### Gas Consumption
A **Gas Consumption** card displays below the deco table after each calculation:
- Columns: GAS | TOTAL VOL | THIRDS | TURN PRESS | RESERVE | SUFFICIENT
- Rule of Thirds / Half Tank toggle — updates live without recalculating
- Travel gas pooling: if travel gas matches bottom gas, volumes are pooled and labelled (e.g. `Air (+Travel)`)
- SAC-based consumption in litres or cubic feet, with correct unit conversion
- Status per gas: SHORT / TIGHT / OK

---

## Helium and Trimix

- He % entry on bottom gas and all deco gas cards
- **He half-time selector**: Bühlmann 2003 (1.51 min) or Baker (1.88 min)
- **N₂ / O₂ narcotic toggle**: configures whether O₂ counts toward END (NOAA/IANTD count both; some agencies exclude O₂)
- END displayed throughout the dive profile and in the END Calc tool
- All trimix fractions wired through both Bühlmann and VPM-B engines

---

## Altitude Diving

- Altitude presets: sea level, 500 m, 1000 m, 1500 m, 2000 m, 2500 m, 3000 m, and custom
- Acclimatization toggle (adjusts effective surface pressure)
- All engine calculations use altitude-corrected surface pressure
- **VPM-B altitude-adjusted critical radii**: at altitude, lower crush pressure enlarges initial bubble nuclei — `r_alt = r₀ × (P_SL / P_alt)^(1/3)` — producing correctly reduced deco obligation at altitude

---

## Repetitive and Multi-Dive Planning

### Multi-Dive (Tec)
- Multiple dives with surface interval tissue loading carried between them
- **VPM-B repetitive dive state**: carries tissue gas pressures (N₂/He off-gassing) and bubble state (adjusted critical radii) from the previous dive
- Bubble radii regeneration model: `r(t) = r_init + (r_end − r_init) × exp(−t / REGEN_TIME)` with REGEN_TIME = 14 days
- Surface interval input in minutes; state persisted across sessions

### Surface Interval Calculator
- Simulates Dive 1 forward on the Bühlmann ZH-L16C tissue model, off-gasses all 16 compartments at the surface, and finds the minimum surface interval before a planned second dive
- Reports: minimum SI, recommended SI (min × 1.5), controlling compartment, reverse-profile warning
- Per-compartment tissue-loading bar chart
- Available as a standalone **Surf Int** sub-tab in both Rec and Tec, and as an embedded panel in Rec and Tec results (pre-fills depth and bottom time from the current dive)

---

## Units

Metric (metres, bar, litres) and Imperial (feet, psi, cu ft) — switchable globally. All inputs, labels, MOD displays, rate selectors, gas cards, and SAC values update on unit change. Gas consumption volumes and SAC footer units reflect the current mode across all calculation paths.

---

## Output and Export

### Copy
Opens a **preview modal** (same style as the Slate modal) showing the full formatted plan text before copying. Both Deco Plan and Emergency Plan share this modal. Footer format:

```
Run Time:66'00" Deco:27'24"
CNS:36.2% OTU:73 PrT:21.7
```

### Deco Slate
Compact monospaced waterproof-slate format (deco stops only). Header: date/time, algorithm, bottom gas and switch gases. Table columns: depth, run time, gas, ppO₂. Footer:

```
TRT: 66'00" | DECO: 27'24"
CNS: 36.2% OTU: 73 PrT: 21.7
```

TRT = Total Run Time (reads from totals row, full MM'SS" format). Same footer format in both deco and emergency slates.

### TXT Export
Full plan text including settings, deco table, and gas consumption. Header: `DECO PLAN` / `EMERGENCY PLAN` with date/time stamp and divider. Saved to device Downloads folder on Android. Open exported TXT or PDF files with [T-Viewer](https://github.com/Three-Cats-LSP/T-Viewer).

### PDF Export (Dive Plan)
Section picker dialog before export. Available sections:
- Gas Consumption
- Dive Profile
- Deco Slate
- GF Curve
- Tissue Saturation

All sections use DejaVu Sans Unicode font. 10-column deco table (Phase / Depth / Stop / Mix / Run / TTS / PPO2 / END / EAD / CNS%). Proper ✓ ✗ ⚠ rendering. Saved to device Downloads folder on Android.

### PDF Export (Emergency Plan)
Section picker dialog before export. Available sections:
- Emergency Gas Consumption
- Ascent Schedule
- Dive Profile
- GF Curve
- Tissue Saturation
- Emergency Slate

Red theme (vs blue for dive plan). Same font, layout, header/footer structure as the dive plan PDF.

### Named Presets
Save and recall full dive setups (algorithm, GF/conservatism, all gas mixes, cylinders, depth, bottom time, altitude, SAC, min-deco settings). Up to 20 presets stored in `localStorage`. Accessed via the **★ PRESETS** button in the Deco Schedule card header.

---

## Emergency / Contingency Plans

The **Contingency Plans** card shows auto-generated emergency ascent schedules based on the current dive profile. Each scenario shows: ascent schedule, gas required vs available, run time, deco time, CNS, OTU, PrT, and a severity indicator.

Export options per scenario: Copy (preview modal) / Slate / TXT / PDF.

---

## Tools Tab

Quick planning calculators and reference material:

| Tool | Description |
|------|-------------|
| **Best Mix** | Depth + ppO₂ → recommended O₂%, resulting ppO₂, and gas name |
| **MOD** | O₂% + ppO₂ slider → Maximum Operating Depth in m/ft |
| **END Calc** | Depth + O₂/He % → Equivalent Narcotic Depth and narcotic partial pressure |
| **EAD Table** | MOD and MND reference for common mixes (Air, EAN32/36/40/50, 100% O₂, trimix 21/35, 18/45, 15/55). Live ppO₂ selector recalculates MOD column; MND at END = 3.5 bar |
| **Gas Table** | Same mixes as EAD Table — MOD @ 1.4 / MOD @ 1.6 / MND columns; respects metric/imperial |
| **Unit Converter** | Bidirectional conversion: pressure, volume, depth, temperature, weight |
| **Knowledge** | Reference links and Knowledge Base PDFs |

---

## Rec Sub-tabs

| Sub-tab | Description |
|---------|-------------|
| **Deco Schedule** | Main NDL/deco output for the current dive |
| **Dive Planner** | PADI RDP-style dive planner with pressure group tracking |
| **Surf Int** | Surface interval calculator |
| **Avg Depth** | Planning depth calculator: max + average depth → profile class and planning depth ratio |
| **Multi Dive** | Multi-dive planner with surface interval between dives |
| **CNS O₂** | CNS oxygen exposure tracker |
| **NDL Tables** | NDL reference tables for air and common nitrox mixes |

---

## UI

- Dark / light theme toggle
- Unified `?` tooltip icon system across all settings — inline explanations for every algorithm, GF, conservatism, altitude, and gas setting
- **`?` reference panel — Links:** Diver's Toolkit hub, LSP D-Planner GitHub, APK download, Thingiverse, Instagram, PayPal
- Collapsible result cards (Gas Consumption, Contingency Plans, Dive Graph, Tissue Saturation, GF Curve) with right-side caret
- All settings cards use a consistent grid layout; mobile-responsive
- Gas switch rows highlighted in amber (`#FFBF00`) in light mode, full-width border on all 10 columns

---

## Quality & Testing

| Suite | Description |
|-------|-------------|
| [`tests.html`](https://threecats-lsp.com/d-planner/tests.html) | Core regression — engine presence, NDL, deco, VPM-B, CNS/OTU, edge cases |
| [`tests-extended.html`](https://threecats-lsp.com/d-planner/tests-extended.html) | Extended algorithm suite — GF, trimix, conservatism ordering, first stop depths |
| [`tests-massive.html`](https://threecats-lsp.com/d-planner/tests-massive.html) | 446-test regression suite — engines, UI/DOM, Tier 1–3 scenarios, travel gas, altitude, trimix, VPM-B/GFS, GF UI, gas plan, slate, presets |
| [`tests-massive-main.html`](https://threecats-lsp.com/d-planner/tests-massive-main.html) | Mobile-optimised — same scope as tests-massive, minus heaviest Tier 3 groups |
| [`tests-verify.html`](https://threecats-lsp.com/d-planner/tests-verify.html) | **Math Verification Suite** — ZHL-16C + VPM-B cross-check vs Baker/FORTRAN reference; sections A–H (pinned regression, Baker cross-check, Maiken invariants, coefficient verification, physics constants, determinism, MultiDeco/V-Planner compatibility) |
| `audit.py` | Static analysis — **191** structural checks across 31 code groups. Run before every commit. |

```bash
python3 audit.py index.html
```

---

## Repository Structure

| Path | Purpose |
|------|---------| 
| `index.html` | Self-contained web app — the entire planner in one file |
| `capacitor-bridge.js` | Android native file export bridge (Capacitor) |
| `sw.js` | Service worker — offline caching, network-first for HTML |
| `download.html` | Android APK download page |
| `audit.py` | Static analysis script |
| `vpmb.py` | VPM-B Python reference engine |
| `VpmbEngine.java` | VPM-B Java engine |
| `VpmbGfsEngine.java` | VPM-B/GF hybrid Java engine |
| `VpmbGfsPlanner.java` | VPM-B/GF planner Java |
| `android/` | Capacitor Android project |
| `Android Apk/` | Latest built APK (auto-updated by CI) |
| `Knowledge Base/` | Reference PDFs, DiveKit/MultiDeco cross-reference data, Baker FORTRAN source, study links |

### Knowledge Base

| File | Description |
|------|-------------|
| `00_README_start_here.pdf` | Orientation guide |
| `Baker_1998_Understanding_M-Values_GradientFactors.pdf` | M-values and gradient factors |
| `VPM_Decompression_Reinders.pdf` | VPM decompression theory |
| `VPM_Explanation_Corado.pdf` | VPM practical explanation |
| `VPM_for_Dummies_Andy_Davis.pdf` | Accessible VPM introduction |
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
| `DiveKit_Engine_Knowledge_Base.md` | DiveKit engine docs + MultiDeco comparison synthesis for LSP |
| `divekit-cross-reference/` | Published 26-scenario inputs + MultiDeco/DiveKit results JSON |

---

## Branches

| Branch | Purpose |
|--------|---------|
| `main` | Stable releases — what GitHub Pages serves |
| `dev` | Active development and new features |

---

## Deployment

Static single-file app. GitHub Pages serves `index.html` directly from `main`. No build tools, no dependencies, no network calls at runtime.

Android APK is built automatically by GitHub Actions on every push to `main` and committed back to `Android Apk/LSP_D-planner.apk`.

---

## Disclaimer

**Planning Aid Only.** This tool is not a substitute for formal dive training, certification, or a calibrated dive computer. Decompression models are theoretical and carry inherent uncertainty. Always dive within your training and experience level. Use at your own risk.

---

*Developed by Three Cats LSP · [@threecats_lsp](https://www.instagram.com/threecats_lsp)*

See [CHANGELOG.md](CHANGELOG.md) for version history. Current release: **v2.20.21**.
