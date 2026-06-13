# LSP D-Planner — Social Media Posts

Posts are written as evergreen app descriptions. Adapt tone/length to the platform.

---

## Post A — Full Feature Overview (Reddit / forums / GitHub)

**Title:**
LSP D-Planner v2.10.0 — free open-source deco planner (Bühlmann ZHL-16C + VPM-B + VPM-B/GFS) with native Android app

**Body:**

LSP D-Planner is a free dive planning app by Three Cats LSP. Runs in any browser and as a native Android app — completely offline, no account, no ads, no subscription.

📱 **Android APK:** https://three-cats-lsp.github.io/LSP_D-planner/download.html
🌐 **Web app:** https://three-cats-lsp.github.io/LSP_D-planner/
💻 **GitHub:** https://github.com/Three-Cats-LSP/LSP_D-planner

---

**Two modes: Rec and Tec**

Recreational:
- NDL tables with pressure group tracking (PADI RDP-based)
- Multi-dive day planning with residual nitrogen tracking
- Surface Interval calculator — tissue loading per compartment, controlling compartment, reverse-profile warning
- Average Depth converter, CNS O₂ tracker, MOD calculator

Technical:
- Bühlmann ZHL-16C + Gradient Factors — configurable GF Low/High (presets or custom), 16 tissue compartments
- VPM-B — Varying Permeability Model, conservatism margin +0 to +5
- VPM-B/GFS hybrid — VPM-B deep stops, GF High applied at shallow stops

---

**Gas management**
- Full trimix entry (O₂ / He / N₂) for bottom gas and all deco gases
- Travel gas card — auto-switch depth by MOD or manual
- Gas Consumption card — GAS · TOTAL VOL · THIRDS · TURN PRESS · RESERVE · SUFFICIENT
- Rule of Thirds / Half Tank toggle — live update
- SAC-based consumption in litres or cubic feet

---

**Export**
- Copy — preview modal before clipboard write
- Deco Slate — compact monospaced waterproof format
- TXT export — full plan, saved to Downloads on Android
- PDF (Dive Plan) — section picker; Gas Consumption, Dive Profile, Deco Slate, GF Curve, Tissue Saturation
- PDF (Emergency Plan) — section picker; Emergency Gas, Ascent Schedule, Dive Profile, GF Curve, Tissue Saturation, Emergency Slate

---

**v2.10.0 — what's new**
- Native Android status bar: transparent, edge-to-edge, icons sync with light/dark theme
- Collapsible ENV and Advanced Settings groups — cleaner UI on small screens
- Dive profile presets and advanced config presets — one-tap common setups
- Water type tooltip and per-algorithm tooltips
- Planning Aid Only banner

---

## Post B — Short (Instagram / X)

LSP D-Planner v2.10.0 — free open-source deco planner for rec and tec divers.

Bühlmann ZHL-16C + GF · VPM-B · VPM-B/GFS
Trimix · travel gas · altitude · repetitive dives
Gas consumption · deco slate · PDF & TXT export
Native Android app — edge-to-edge UI, light/dark theme, full offline

No account. No ads. No subscription.

🌐 https://three-cats-lsp.github.io/LSP_D-planner/
📱 APK: https://three-cats-lsp.github.io/LSP_D-planner/download.html
💻 https://github.com/Three-Cats-LSP/LSP_D-planner

#scubadiving #technicaldiving #decompression #diveplanning #opensource #android

---

## Post C — Algorithm-Focused (Reddit r/scubadiving / r/technicaldiving / forums)

**Title:**
Open-source deco planner — Bühlmann ZHL-16C, VPM-B, VPM-B/GFS hybrid, native Android app, Math Verification Suite

**Body:**

LSP D-Planner is a client-side decompression planning app — single HTML file, no dependencies, runs offline in any browser or as a native Android app (Capacitor).

**Three algorithms, switchable at any time:**
- **Bühlmann ZHL-16C + GF** — 16 tissue compartments, dissolved gas model. GF Low/High configurable via presets or manual. Default 55/80.
- **VPM-B** — Varying Permeability Model. Tracks bubble nuclei. Conservatism margin +0 to +5.
- **VPM-B/GFS** — Hybrid: VPM-B sets deep stop depth, GF High applied at shallow and surface stops.

**Trimix** — full O₂/He/N₂ entry, He half-time selector (Bühlmann 2003 or Baker), END column, He-aware ppO₂ and MOD checks through both engines.

**Altitude** — surface pressure presets to 3000 m, acclimatization toggle. VPM-B altitude-adjusted critical radii: `r_alt = r₀ × (P_SL / P_alt)^(1/3)`.

**Math Verification Suite** (`tests-verify.html`) — cross-checks live engine output against Baker/FORTRAN reference values. Covers: pinned regression (ZHL and VPM-B), Baker Python cross-check, Maiken ordering invariants, coefficient verification (all 16 compartments vs canonical Bühlmann 2003), physics constants, determinism, MultiDeco/V-Planner compatibility.

**v2.10.0** adds native Android status bar integration — transparent, edge-to-edge, icon color synced to light/dark theme via `@capacitor/status-bar`.

🌐 https://three-cats-lsp.github.io/LSP_D-planner/
📱 https://three-cats-lsp.github.io/LSP_D-planner/download.html
🔬 https://three-cats-lsp.github.io/LSP_D-planner/tests-verify.html
💻 https://github.com/Three-Cats-LSP/LSP_D-planner

Free and open source.

---

## Post D — Android App Focus (Play Store alternative / APKPure / XDA)

LSP D-Planner is a native Android dive planning app built with Capacitor — no Play Store, direct APK download.

**What it does:**
- Full decompression planning: Bühlmann ZHL-16C + GF, VPM-B, VPM-B/GFS
- Recreational NDL tables with pressure group tracking
- Trimix, travel gas, altitude, multi-dive, repetitive diving
- Gas consumption with rule of thirds / half tank
- Export TXT and PDF direct to your Downloads folder
- Full offline — no internet needed after install

**v2.10.0 Android improvements:**
- Edge-to-edge transparent status bar
- Status bar icon color follows your light/dark theme setting
- Collapsible settings panels for better mobile UX

📲 **Download:** https://three-cats-lsp.github.io/LSP_D-planner/download.html

Free, open source, no account required.

