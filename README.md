# LSP D-Planner + CCR

**Rebreather edition** of [LSP D-Planner](https://github.com/Three-Cats-LSP/LSP_D-planner) — closed-circuit (CCR), passive SCR (pSCR), bailout, and descent-setpoint planning on top of the v2.20.x open-circuit foundation.

This is a **separate product and repository**. The main [LSP D-Planner](https://github.com/Three-Cats-LSP/LSP_D-planner) stays on the stable open-circuit release line (v2.20.x) without rebreather code.

Part of the [Three Cats LSP](https://threecats-lsp.com) **Diver's Toolkit**.

🌐 **Live App**: https://threecats-lsp.com/d-planner-ccr/

📦 **GitHub Pages mirror**: https://three-cats-lsp.github.io/LSP_D-planner-CCR/

**Current version: 2.30.9**

---

## Diver's Toolkit

| App | Purpose |
|-----|---------|
| **[LSP D-Planner](https://threecats-lsp.com/d-planner/)** | Open-circuit decompression planning |
| **LSP D-Planner + CCR** | Rebreather planning (this app) |
| **[T-Viewer](https://threecats-lsp.com/t-viewer/)** | Open and share exported dive plan TXT/PDF files |
| **[Get In Water](https://threecats-lsp.com/get-in-water/)** | Trip packing checklists |

All apps live on the [Diver's Toolkit hub](https://threecats-lsp.com).

---

## What's different from LSP D-Planner?

Built from LSP D-Planner **v2.20.21** with rebreather-specific additions only in this repo:

| Feature | Description |
|---------|-------------|
| **CCR (closed circuit)** | Diluent-aware tissue loading, setpoint crossing, loop vs OC deco gas logic |
| **pSCR (passive SCR)** | GUE-style O₂ drop model (loop volume + metabolic O₂, 0.16 bar floor) |
| **Bailout mode** | OC ascent with GF 90/90 (Bühlmann) for emergency planning |
| **Descent setpoint** | Default 0.7 bar until high setpoint depth |
| **Rebreather Adv. Settings** | SAC stress/deco CCR, stress time, problem-solve reserve wired into gas plan |
| **Dual engines** | Bühlmann ZH-L16C + GF **and** VPM-B / VPM-B/GFS — both with full CCR paths |

Everything else from the v2.20.x base is included: Surf GF, prior-dive O₂ carry, shallow gradient, export/banner, presets, contingency plans, imperial units, travel gas, altitude, and the full **Tools** mode (Best Mix, MOD, END, EAD/Gas tables, unit converter, knowledge base).

---

## App Modes

Three top-level modes (header switcher):

| Mode | Description |
|------|-------------|
| **Rec** | PADI RDP recreational planner — NDL tables, pressure groups, nitrox |
| **Tec** | Full technical decompression planning — trimix, multi-gas, Bühlmann + VPM |
| **Tools** | Standalone calculators and reference tables (no dive schedule) |

**Tec sub-tabs:** Deco Schedule · Dive Planner · Surf Int · Avg Depth · Multi Dive · CNS O₂ · NDL Tables

**Tools sub-tabs:** Best Mix · MOD · END Calc · EAD Table · Gas Table · Unit Converter · Knowledge

---

## Rebreather Planning (Tec)

Configure under **Circuit** on the Deco Schedule card:

- **OC** — standard open-circuit (same as main LSP D-Planner)
- **CCR** — on-loop setpoints (descent / bottom / deco), diluent-as-bailout option, loop gas in profile and export
- **pSCR** — passive SCR with loop volume and metabolic O₂; setpoint fields hidden (not applicable)
- **Bailout** — OC breathing from bailout gas with GF 90/90

Shared CCR physics used by both Bühlmann and VPM engines: `getInspiredInertPressures()`, `splitSegmentAtSetpoint()`, `getEffectivePpo2()`, `loadTissuesWithCCR()`.

Gas validation checks MOD at the correct ppO₂ limit (on-loop setpoint vs OC bailout limit). Stress/problem-solve reserve gas is included in the gas plan when configured.

---

## Web App

Open https://threecats-lsp.com/d-planner-ccr/ in any modern browser — no install required.

**Installation (PWA):**
1. Open the live URL on your phone, tablet, or computer
2. **Safari (iPhone / iPad):** Share → **Add to Home Screen**
3. **Chrome (Android):** Menu → **Install app** / **Add to Home screen**
4. **Chrome (desktop):** Install icon in the address bar

Service worker caches static assets; HTML is always fetched fresh. Hard-refresh after deploy if you see an old version.

---

## Android APK

Separate Android package (`com.threecats.lsp.dplannerccr`) — can be installed **alongside** the standard LSP D-Planner APK.

📲 **[Download APK](https://threecats-lsp.com/d-planner-ccr/download.html)**

**Build locally:**
```bash
npm install
npm run cap:sync
npm run cap:open    # opens Android Studio
```

APK builds are also published under `Android Apk/` by CI on release.

---

## Decompression Algorithms

- **Bühlmann ZH-L16C + Gradient Factors** — 16-compartment dissolved-gas model; GF presets (20/85 default) or custom; CCR-aware tissue loading and bailout GF 90/90
- **VPM-B** — bubble-mechanics model; conservatism +0 to +5; CCR setpoint phases wired for bottom and deco
- **VPM-B/GFS** — VPM deep stops + GF High at shallow/surface stops

---

## Output and Export

Same export stack as LSP D-Planner v2.20.x: Copy preview modal, Deco Slate, TXT, PDF (section picker), named presets (20 max), contingency/emergency plans with gas sufficiency checks.

CCR plans label loop gas, setpoints, and bailout switches in the deco table, profile graph, banner, and text export.

---

## Development

Single-file architecture — primary code in `index.html` (~18k lines). Capacitor bridge in `capacitor-bridge.js`, offline caching in `sw.js`.

**Before every commit:**
```bash
python audit.py index.html
```

Static analysis: **323 checks** across 50 code groups (includes GROUP 50 v2.30.16 BUG-69–70 fixes).

Pushes to `main` that touch app files trigger **Notify Site on Push** → auto-sync to [threecats-lsp.com/d-planner-ccr/](https://threecats-lsp.com/d-planner-ccr/) via the `threecats-lsp.com` repo.

---

## Quality & Testing

Open any suite in a browser (loads `index.html` in a hidden iframe and runs against the live engine).

| Suite | Repo | Live |
|-------|------|------|
| [`tests.html`](tests.html) | Core regression — engine presence, NDL, deco, VPM-B, CNS/OTU, edge cases | [Live](https://threecats-lsp.com/d-planner-ccr/tests.html) |
| [`tests-verify.html`](tests-verify.html) | **Math Verification** — ZHL-16C + VPM-B vs Baker/FORTRAN reference; sections A–H **+ Section I · CCR / Rebreather** | [Live](https://threecats-lsp.com/d-planner-ccr/tests-verify.html) |
| [`tests-pscr-otu-cns.html`](tests-pscr-otu-cns.html) | **pSCR OTU/CNS & gas validation** — 36 safety-critical tests (20/40/60 m × EAN32/EAN36); guards `getEffectivePpo2` regression | [Live](https://threecats-lsp.com/d-planner-ccr/tests-pscr-otu-cns.html) |
| [`tests-extended.html`](tests-extended.html) | Extended algorithm suite — GF, trimix, conservatism ordering, first-stop depths | [Live](https://threecats-lsp.com/d-planner-ccr/tests-extended.html) |
| [`tests-massive.html`](tests-massive.html) | Full regression — 300+ engine plans, UI/DOM, Tier 1–3, travel gas, altitude, gas plan, slate, presets, **T3-CCR MultiDeco cross-val** | [Live](https://threecats-lsp.com/d-planner-ccr/tests-massive.html) |
| [`tests-massive-main.html`](tests-massive-main.html) | Mobile-optimised massive suite — same scope minus heaviest Tier 3 groups; includes **T3-CCR** | [Live](https://threecats-lsp.com/d-planner-ccr/tests-massive-main.html) |
| `audit.py` | Static structural analysis — **323 checks**. Run: `python audit.py index.html` | — |
| `pSCR_gas_consumption_validation_v2.30.15.md` | pSCR gas draw vs metabolic O₂ / OTU-CNS end-to-end validation report (v2.30.15 sign-off) | — |
| `pSCR_OTU_CNS_consistency_audit.md` | OTU/CNS code-path audit + test plan (companion to suite above) | — |

Bug reports: `errors_bugs_report.md` through `errors_bugs_report_v8.md` in repo root.

---

## Repository Structure

| Path | Purpose |
|------|---------|
| `index.html` | Self-contained web app |
| `sw.js` | Service worker — offline cache, network-first HTML |
| `capacitor-bridge.js` | Android native file export bridge |
| `download.html` | Android APK download page |
| `manifest.json` | PWA manifest |
| `audit.py` | Static analysis (323 checks) |
| `vpmb.py` | VPM-B Python reference engine |
| `VpmbEngine.java` | VPM-B Java reference |
| `android/` | Capacitor Android project |
| `Android Apk/` | Latest built APK (CI) |
| `Knowledge Base/` | Reference PDFs, MultiDeco cross-reference data, Baker FORTRAN source |
| `tests*.html` | Browser test suites (see above) |
| `errors_bugs_report_v*.md` | Verification pass bug reports |

---

## Recent releases (v2.30.x)

| Version | Highlights |
|---------|------------|
| **2.30.16** | Surface GF uses `altSurfaceP` at altitude (BUG-69); stress reserve split across deco stop depths (BUG-70) |
| **2.30.15** | pSCR OTU/CNS parity complete (BUG-64–68); dedicated `tests-pscr-otu-cns.html` + gas/toxicity validation report |
| **2.30.9** | Imperial Bühlmann emergency gas capacity fix; `appSettings.clear()` key fix; faster settings restore (no double `change` burst) |
| **2.30.8** | Tools panel HTML fix (panels no longer nested inside `#deco`); emoji brand icons restored |
| **2.30.0** | ★ Milestone — CCR repo split; full rebreather planning shipped |

Full history: [`CHANGELOG.md`](CHANGELOG.md)

---

## License & disclaimer

Same terms as [LSP D-Planner](https://github.com/Three-Cats-LSP/LSP_D-planner).

For **trained mixed-gas and rebreather divers only**. Not a substitute for proper certification, equipment checks, or dive planning discipline. Verify all plans against your dive computer and training agency standards.
