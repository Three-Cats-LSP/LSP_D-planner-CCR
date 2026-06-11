# LSP D-Planner — Social Media Posts

Posts are written as evergreen app descriptions — no version numbers, no "what's new" framing.
Use these as a base and adapt tone/length to the platform.

---

## Post A — Full Feature Overview

**Title:**
LSP D-Planner — free open-source decompression planner (Bühlmann ZHL-16C + VPM-B + VPM-B/GFS)

**Body:**

LSP D-Planner is a free dive planning app by Three Cats LSP. Runs in any browser and as a native Android APK — completely offline, no account, no ads, no subscription.

---

**Two modes: Rec and Tec**

Recreational:
- NDL tables with pressure group tracking (PADI RDP-based)
- Multi-dive day planning with residual nitrogen tracking
- Surface Interval calculator — tissue loading per compartment, controlling compartment, reverse-profile warning
- Average Depth converter
- CNS O₂ tracker
- MOD calculator for nitrox

Technical:
- Bühlmann ZHL-16C + Gradient Factors — configurable GF Low/High (presets or custom), 16 tissue compartments, water vapour correction
- VPM-B — Varying Permeability Model, conservatism margin +0 to +5
- VPM-B/GFS hybrid — VPM-B bubble mechanics for deep stops, GF High applied at shallow and surface stops

---

**Gas management**

- Full trimix entry (O₂ / He / N₂) for bottom gas and all deco gases
- Travel gas card — dedicated descent/ascent transit gas, auto-switch depth by MOD or manual
- Gas Consumption card — GAS · TOTAL VOL · THIRDS · TURN PRESS · RESERVE · SUFFICIENT
- Rule of Thirds / Half Tank toggle — live update, no recalculation needed
- Travel gas pools with bottom gas automatically when same mix
- SAC-based consumption in litres or cubic feet

---

**Trimix and helium**

- He half-time: Bühlmann 2003 (1.51 min) or Baker (1.88 min)
- END column in deco schedule — He-aware (non-narcotic)
- He-aware ppO₂ checks and MOD calculations throughout both engines
- N₂ / O₂ narcotic toggle — configure whether O₂ counts toward END

---

**Altitude diving**

- Presets: sea level to 3000 m + custom; acclimatization toggle
- VPM-B altitude-adjusted critical radii: r_alt = r₀ × (P_SL / P_alt)^(1/3)

---

**Repetitive diving**

- Multi-dive with surface interval tissue loading (N₂/He off-gassing across all 16 compartments)
- VPM-B bubble state carry between dives — 14-day regeneration constant

---

**Export**

- Copy — preview modal before clipboard write; two-line footer (Run/Deco + CNS/OTU/PrT)
- Deco Slate — compact monospaced waterproof format; header, stops-only table, TRT/DECO footer
- TXT export — full plan with settings, deco table, gas consumption
- PDF (Dive Plan) — section picker dialog; Gas Consumption, Dive Profile, Deco Slate, GF Curve, Tissue Saturation; 9-column deco table; Unicode font
- PDF (Emergency Plan) — same section picker; Emergency Gas Consumption, Ascent Schedule, Dive Profile, GF Curve, Tissue Saturation, Emergency Slate; red theme

---

**Presets**

Save and recall up to 20 full dive setups (algorithm, GF, all gases, cylinders, depth, BT, altitude, SAC, min-deco settings) via localStorage.

---

**Quality**

- Static audit script — structural checks across 20+ code groups; run before every commit
- Regression test suites — 446-test suite covering engines, UI/DOM, travel gas, altitude, trimix, VPM-B/GFS, presets, gas plan, slate
- Math Verification Suite — ZHL-16C + VPM-B cross-check against Baker/FORTRAN reference; sections covering pinned regression, Baker Python cross-check, Maiken invariants, coefficient verification, physics constants, determinism, MultiDeco/V-Planner compatibility

---

**Links:**
- Web: https://three-cats-lsp.github.io/LSP_D-planner/
- Android APK: https://github.com/Three-Cats-LSP/LSP_D-planner/raw/main/Android%20Apk/LSP_D-planner.apk
- GitHub: https://github.com/Three-Cats-LSP/LSP_D-planner

Free, open source, runs entirely offline.

---

## Post B — Short (Instagram / X)

**Body:**

LSP D-Planner — free, open-source deco planner for recreational and technical divers.

Bühlmann ZHL-16C + GF · VPM-B · VPM-B/GFS hybrid
Trimix · travel gas · altitude · repetitive dives
Gas consumption with rule of thirds · deco slate · PDF export
Runs offline in any browser or as an Android APK — no account, no ads.

Web: https://three-cats-lsp.github.io/LSP_D-planner/
GitHub: https://github.com/Three-Cats-LSP/LSP_D-planner

---

## Post C — Algorithm-Focused (Reddit / dive forums)

**Title:**
Open-source deco planner — Bühlmann ZHL-16C, VPM-B, and VPM-B/GFS hybrid, with a Math Verification Suite

**Body:**

LSP D-Planner is a client-side decompression planning app — single HTML file, no dependencies, runs offline in any browser or as an Android APK.

**Three algorithms, switchable at any time:**

- **Bühlmann ZHL-16C + GF** — 16 tissue compartments, dissolved gas model. GF Low controls first-stop depth; GF High controls surface ceiling. Configurable via presets or manual entry. Default 55/80.
- **VPM-B** — Varying Permeability Model. Tracks bubble nuclei rather than tissue tension. Conservatism margin +0 to +5.
- **VPM-B/GFS** — Hybrid: VPM-B sets deep stop depth, GF High applied at shallow stops and the surface. Useful for divers who want bubble-model deep stops with GF-controlled shallow stops.

**Trimix support** — full O₂/He/N₂ entry, He half-time selector (Bühlmann 2003 or Baker), END column (narcotic gas toggle), He-aware ppO₂ and MOD checks throughout both engines.

**Altitude** — surface pressure presets up to 3000 m, acclimatization toggle. VPM-B applies altitude-adjusted critical radii: r_alt = r₀ × (P_SL / P_alt)^(1/3).

**Math Verification Suite** (`tests-verify.html`) — standalone page that runs the live engine in an iframe and cross-checks outputs against Baker/FORTRAN reference values. Covers pinned regression (ZHL and VPM-B), Baker Python cross-check, Maiken ordering invariants, coefficient verification (all 16 compartments vs canonical Bühlmann 2003), physics constants, determinism, and MultiDeco/V-Planner compatibility.

**Links:**
- Web: https://three-cats-lsp.github.io/LSP_D-planner/
- Math Verification Suite: https://three-cats-lsp.github.io/LSP_D-planner/tests-verify.html
- GitHub: https://github.com/Three-Cats-LSP/LSP_D-planner

Free and open source. Happy to go deep on algorithm implementation, the VPM-B/GFS hybrid, or the verification methodology.
