# LSP D-Planner + CCR

**Rebreather decompression planner** — CCR, pSCR, bailout and open-circuit planning on Bühlmann ZHL-16C + GF and VPM-B / VPM-B/GFS.

Part of the [Three Cats LSP](https://threecats-lsp.com) **Diver's Toolkit**. A separate product from [LSP D-Planner](https://github.com/Three-Cats-LSP/LSP_D-planner) (open-circuit line, v2.20.x), maintained in its own repository to keep the OC release clean.

🌐 **Live app:** https://threecats-lsp.com/d-planner-ccr/  
📦 **GitHub Pages mirror:** https://three-cats-lsp.github.io/LSP_D-planner-CCR/  
📲 **Android APK:** https://threecats-lsp.com/d-planner-ccr/download.html  

**Current version: 2.30.30** — Safety Sign-Off release. 85 audit findings (BUG-01–85) closed across 28 independent verification passes. 383/383 `audit.py` checks passing. See [SAFETY_CERTIFICATION_v2.30.30.md](SAFETY_CERTIFICATION_v2.30.30.md).

---

## Diver's Toolkit

| App | Description | Link |
|-----|-------------|------|
| **[LSP D-Planner](https://threecats-lsp.com/d-planner/)** | Open-circuit decompression planning — Bühlmann, VPM-B, Rec/Tec | [Repo](https://github.com/Three-Cats-LSP/LSP_D-planner) |
| **LSP D-Planner + CCR** ← *this app* | Rebreather planning — CCR, pSCR, bailout | [Repo](https://github.com/Three-Cats-LSP/LSP_D-planner-CCR) |
| **[T-Viewer](https://threecats-lsp.com/t-viewer/)** | Open and share exported dive plan TXT/PDF files | — |
| **[Get In Water](https://threecats-lsp.com/get-in-water/)** | Dive trip packing checklists | [Repo](https://github.com/Three-Cats-LSP/Get-In-Water) |

All apps at the [Diver's Toolkit hub](https://threecats-lsp.com).

---

## What CCR adds over LSP D-Planner

| Feature | Description |
|---------|-------------|
| **CCR (closed circuit)** | Phase-aware setpoints (descent / bottom / deco), diluent-aware tissue loading, setpoint crossing |
| **pSCR (passive SCR)** | GUE-style loop O₂ depletion model — loop volume, metabolic O₂, 0.16 bar floor, runtime-tracked |
| **Bailout** | OC emergency ascent with configurable bailout GF (default 50/85) |
| **Rebreather Adv. Settings** | Stress SAC, deco CCR SAC, stress time, problem-solve reserve — all wired into gas plan |
| **Diluent & bailout gas UI** | Separate diluent and bailout gas cards with MOD validation |
| **Dual-engine CCR/pSCR** | Bühlmann and VPM both compute OTU/CNS via shared plan-walk engine, segment-accurate |
| **Circuit-aware exports** | Plans labelled DECO PLAN (OC) vs DECO PLAN (CCR); filenames include circuit tag |

Everything from LSP D-Planner OC is also here: GF presets, trimix, travel gas, altitude, repetitive dives, gas consumption, emergency contingency, PDF/TXT/slate export, Android app.

---

## Algorithms

| Algorithm | Notes |
|-----------|-------|
| **Bühlmann ZHL-16C + GF** | 16 compartments. GF Low/High via presets or custom (20/85, 30/85, 50/85, GUE, custom). Shallow gradient toggle. |
| **VPM-B** | Varying Permeability Model. Conservatism +0 to +5. Altitude-adjusted critical radii. |
| **VPM-B/GFS** | VPM-B deep stops + GF High at shallow stops. |

All algorithms support CCR, pSCR, bailout, trimix, altitude, and repetitive dives.

---

## Web App

Open https://threecats-lsp.com/d-planner-ccr/ in any modern browser — no install required. Add to your home screen for native-app feel.

**Install as PWA:**
1. **Safari (iPhone/iPad):** Share → Add to Home Screen → Add
2. **Chrome (Android):** ⋮ → Install app / Add to Home Screen → confirm
3. **Chrome (desktop):** Click install icon in address bar, or ⋮ → Install

---

## Android App

Built with [Capacitor](https://capacitorjs.com). Direct APK — no Play Store needed.

**Requirements:** Android 5.1+ (API 22)

**Install:**
1. Download APK from https://threecats-lsp.com/d-planner-ccr/download.html
2. Allow "Install from unknown sources" in your Android settings
3. Open the downloaded APK and install

**Build stack:** AGP 8.6.1 · Gradle 9.5.1 · JDK 17 · compileSdk/targetSdk 35 · minSdk 22 · Capacitor 6

---

## Gas Planning

- **Diluent cylinder** — size, pressure, reserve; consumption via metabolic bypass rate (pSCR) or diluent injection rate (CCR)
- **Bailout gases** — up to 4 deco gas cards; deepest-capable gas selected automatically for each stop in the stress reserve
- **Stress/problem-solve reserve** — configurable minutes, distributed across bottom depth + every deco stop using the appropriate gas at each depth
- **Gas rule** — rule of thirds or half tank; imperial or metric
- **SAC rates** — bottom, deco, CCR deco (separate), stress — all saved per settings profile

---

## Export

| Format | Contents |
|--------|----------|
| **Copy** | Plain text preview → clipboard |
| **Deco Slate** | Compact monospaced format for writing on a slate |
| **TXT** | Full plan to Downloads (Android) or browser download |
| **PDF — Dive Plan** | Section picker: Gas Consumption, Dive Profile, Deco Slate, GF Curve, Tissue Saturation |
| **PDF — Emergency Plan** | Emergency Gas, Ascent Schedule, Dive Profile, GF Curve, Tissue Saturation, Emergency Slate |

All exports include circuit tag (OC/CCR/pSCR) and algorithm label.

---

## Decompression Algorithms — Presets

| Preset | GF Lo | GF Hi | Transit | Rounding | Water Vapor |
|--------|-------|-------|---------|----------|-------------|
| GUE DecPlanner | 20 | 85 | MultiDeco | Whole min | 0.0577 |
| MultiDeco | 30 | 85 | MultiDeco | Whole min | 0.0577 |
| Abysner | 30 | 85 | Schreiner | Fractional | 0.0627 |
| Subsurface | 35 | 75 | Schreiner | Whole min | 0.0627 |
| DiveKit | 45 | 85 | MultiDeco | Whole min | 0.0577 |

---

## Tools (in-app)

- **MOD Calculator** — ppO₂ limits, altitude-aware
- **Best Mix** — optimal O₂% for target depth and ppO₂
- **END Calculator** — narcotic equivalent depth, N₂ or N₂+O₂ model
- **EAD Table** — 22–40% O₂ at 12–38 m
- **Gas Table** — fO₂, fN₂, ppO₂, EAD, MOD for common mixes
- **Unit Converter** — depth, pressure, volume, SAC rate
- **Knowledge** — algorithm background, pSCR physiology, altitude correction, GF guidance

---

## Test Suites

| Suite | Tests | Scope |
|-------|-------|-------|
| [`tests-pscr-otu-cns.html`](https://threecats-lsp.com/d-planner-ccr/tests-pscr-otu-cns.html) | 36 | pSCR OTU/CNS & gas draw — Sections A–F |
| [`tests-verify.html`](https://threecats-lsp.com/d-planner-ccr/tests-verify.html) | 68 | Baker/FORTRAN cross-val, Section I CCR/Rebreather |
| [`tests-massive.html`](https://threecats-lsp.com/d-planner-ccr/tests-massive.html) | 376+ | Full engine plans, gas plan, T3-CCR MultiDeco RT |
| [`tests-massive-main.html`](https://threecats-lsp.com/d-planner-ccr/tests-massive-main.html) | 376+ | Mobile-optimised |
| [`tests-extended.html`](https://threecats-lsp.com/d-planner-ccr/tests-extended.html) | — | GF, trimix, conservatism ordering |
| [`tests.html`](https://threecats-lsp.com/d-planner-ccr/tests.html) | — | Core engine, NDL, VPM-B, CNS/OTU |
| `audit.py` | **383** | Static analysis — 383/383 passing |

---

## Safety & Verification

- **28 independent audit passes** (v2.30.0 → v2.30.30)
- **85 verified findings closed** (BUG-01 through BUG-85)
- **Full audit trail:** `errors_bugs_report_v1.md` through `errors_bugs_report_v28.md`
- **[Safety certification memo](SAFETY_CERTIFICATION_v2.30.30.md)** — approved for production, 2026-06-21

This app is planning software for **trained rebreather and mixed-gas divers**. It is not a substitute for diver training, pre-dive equipment checks, or a calibrated dive computer.

---

## License

MIT — free to use, modify, and distribute. No account, no ads, no subscription.

---

*Three Cats LSP · [threecats-lsp.com](https://threecats-lsp.com)*
