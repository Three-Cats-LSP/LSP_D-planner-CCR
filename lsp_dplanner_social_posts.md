# LSP D-Planner — Social Media Posts (v2.8.9)

---

## Reddit — r/scuba

**Title:**
I built a free dive planner that works offline — no subscriptions, no account, real deco planning (Bühlmann + VPM-B) + a full Tools section for gas and narcosis calculations

**Body:**

Hey r/scuba — sharing something we've been building for a while. Just pushed a big update and wanted to get it in front of more divers.

**LSP D-Planner** is a free dive planning app made by [Three Cats LSP](https://github.com/Three-Cats-LSP/LSP_D-planner). It runs as a native Android APK and also works in any browser — completely offline, no account required, no subscription, no ads.

**What it does:**

- Recreational NDL tables and full decompression planning with **Bühlmann ZHL-16C + Gradient Factors** (configurable GF Low/High)
- **VPM-B** and **VPM-B/GFS** (hybrid) algorithm support
- Full metric/imperial switching, altitude diving support

**Planning tabs (Rec mode):**
- Dive Planner, Surface Interval calculator, Average Depth converter, Multi-Dive planner, CNS O₂ tracker, NDL Tables

**Planning tabs (Tec mode):**
- Deco Schedule with END column, Best Mix optimizer (Nitrox/Trimix toggle), Surf Int, Dive Planner, Multi Dive, CNS O₂, NDL Tables

**Gas management (integrated into Deco Schedule):**
- Gas Consumption card shows: GAS · TOTAL VOL · THIRDS · TURN PRESSURE · RESERVE · SUFFICIENT · MARGIN
- Rule of Thirds or Half Tank toggle — live update
- Travel gas auto-pools with bottom gas if same mix
- Color-coded sufficiency: green = OK, red = SHORT

**Tools section:**
- Best Mix calculator with nitrox reference table (depths 10–40 m at your ppO₂ limit)
- MOD calculator with full reference table (Air + EAN22–40 at 1.4 and 1.6 bar)
- END Calculator — narcotic depth, ppN₂/ppO₂/ppHe, risk level, narcosis toggle
- EAD Table — Equivalent Air Depth for EAN22–40 across 12–38 m
- Gas Table — MOD + MND for all common mixes at a glance
- Unit Converter (pressure, volume, depth, temp, weight)
- Average Depth planning converter
- Knowledge Base — 18 reference PDFs

**Export:**
- Deco Slate — compact waterproof slate format
- Copy / TXT / PDF — full deco schedule + gas consumption table

It's not trying to replace your dive computer — there's a clear disclaimer about that. But as a pre-dive planning tool it's genuinely capable.

**Try it in your browser:** https://three-cats-lsp.github.io/LSP_D-planner/
**Android APK:** https://raw.githubusercontent.com/Three-Cats-LSP/LSP_D-planner/main/Android%20Apk/LSP_D-planner.apk
**Source code:** https://github.com/Three-Cats-LSP/LSP_D-planner

Open source and completely free. Happy to answer questions about how any of it works.

---

## Reddit — r/diving

**Title:**
Free dive planner for Android and browser — offline, no sign-up, deco + NDL + gas planning + narcosis tools

**Body:**

Hey everyone — sharing something we've been heads-down on for a while.

**LSP D-Planner** is a free Android app (also a browser-based web app) for dive planning. No account, no subscription, works completely offline once installed.

**Recreational divers:**
- No-decompression limit (NDL) tables
- Dive Planner with CNS O₂ tracking
- Multi-dive day planning — residual nitrogen tracked across dives and surface intervals
- Surface Interval calculator — see your tissue loading in real time
- Average Depth converter — enter your log-book average depth, get a recommended planning depth (avg + 75% × (max − avg) formula explained with tooltip)
- MOD calculator for nitrox with full reference table

**Decompression divers:**
- Bühlmann ZHL-16C with configurable Gradient Factors
- VPM-B and VPM-B/GFS hybrid
- Full trimix support (O₂/He/N₂)
- Best Mix optimizer — Nitrox and Trimix modes, calculates optimal O₂% (and He% for target END)
- Gas Consumption card — turn pressure (Rule of Thirds or Half Tank), total volume, sufficiency check, MARGIN, all in the Deco Schedule
- END and EAD calculators with narcosis toggle

**Tools:**
- Best Mix, MOD, END Calc, EAD Table, Gas Table, Unit Converter, Avg Depth, Knowledge Base

**Export:**
- Deco Slate (waterproof slate format), Copy, TXT, PDF — gas consumption included in all formats

The web version runs in any browser so you can try it now without installing anything:
👉 https://three-cats-lsp.github.io/LSP_D-planner/

Android APK: https://raw.githubusercontent.com/Three-Cats-LSP/LSP_D-planner/main/Android%20Apk/LSP_D-planner.apk

Open source: https://github.com/Three-Cats-LSP/LSP_D-planner

Built because we wanted a proper planning tool we actually trusted. Would love feedback from anyone who tries it.

---

## Reddit — r/techscuba

**Title:**
LSP D-Planner v2.8.9 — free open-source deco planner, Bühlmann ZHL-16C + VPM-B + full trimix, integrated gas management, END/EAD/MOD tools, 147-check audit suite

**Body:**

Sharing a project we're genuinely proud of: **LSP D-Planner**, a free open-source technical dive planner — native Android APK and browser-based web app.

**Algorithms:**

- **Bühlmann ZHL-16C + Gradient Factors** — configurable GF Low/High (presets or custom), standard 0.0577 bar water vapour correction
- **VPM-B** — full Varying Permeability Model with configurable conservatism margin
- **VPM-B/GFS hybrid** — VPM-B bubble mechanics for deep stops; GF High applied at shallow/surface stops

**Trimix / helium:**

- Full O₂/He/N₂ entry for bottom gas and all deco gases
- Helium half-time selector: **Bühlmann 2003 (1.51 min)** or **Baker (1.88 min)**
- END column always visible throughout the deco schedule
- He-aware ppO₂ checks and MOD calculations in both Bühlmann and VPM-B engines

**Best Mix optimizer (Tec mode tab):**

- Nitrox mode — calculates best O₂% for target ppO₂ at planned depth, live nitrox reference table (depths 10–42 m)
- Trimix mode — adds He% slider for target END; shows O₂%, He%, N₂%, END, MOD @ 1.4/1.6 bar, ppO₂
- Reads current dive plan depth and gas automatically; narcotic depth warning banner with tooltip explanation

**Narcosis tools:**

- **END Calculator** — depth + O₂% + He% sliders → END, risk level, ppN₂/ppO₂/ppHe, MOD @ 1.4/1.6, alert banners; narcosis toggle (N₂ only vs N₂+O₂)
- **EAD Table** — Equivalent Air Depth for EAN22–40 across 12–38 m, live-computed
- Narcotic depth warning banners throughout (VPM-B, Bühlmann, Best Mix) — all wired to tooltip explaining why 30 m is the conventional narcosis limit

**Gas management:**

- Gas Consumption card integrated into Deco Schedule — GAS · TOTAL VOL · THIRDS · TURN PRESS · RESERVE · SUFFICIENT · MARGIN
- Rule of Thirds and Half Tank toggle — live update
- Travel gas pools with bottom gas automatically if same mix; label shows `Air (+Travel)` to confirm
- Warning rows: red `#FF4433` banner for BT limit and tight margin gas; green = OK, red = SHORT
- MARGIN column — `+/−X L` in green/red matching text export
- Info `?` button on card title with full explanation of both rules

**MOD reference:**

- MOD tab: full Air + EAN22–40 reference table at 1.4 and 1.6 bar ppO₂, with row highlight for current O₂%; tooltip with formula, examples, safety context
- Gas Table: MOD + MND (narcotic depth) for all common mixes, ppO₂ limit slider adjusts MOD column live

**Repetitive diving:**

- Multi-dive with surface interval tissue loading (Haldane N₂/He off-gassing)
- Surface Interval calculator — tissue saturation state across any interval
- VPM-B bubble state carry: `r(t) = r_init + (r_end − r_init) × exp(−t / REGEN_TIME)`, 14-day regeneration constant

**Altitude:**

- Presets sea level to 3000 m + custom input; acclimatization toggle
- VPM-B altitude-adjusted critical radii: `r_alt = r₀ × (P_SL / P_alt)^(1/3)`

**Export:**

- Copy / TXT / PDF — full deco schedule + gas consumption table with correct pooled totals and MARGIN
- Deco Slate — compact waterproof slate format
- PDF gas table: 7-column jsPDF table with color-coded rows, dark header, matching on-screen style

**Quality assurance:**

- 147-check static audit (`audit.py`) across 20+ code groups
- HTML regression test suite (`tests-massive.html`) — algorithm switching, VPM-B/GFS GF UI, SAC unit conversion, gas volume, Gas Table formulas, Slate output, Preset persistence, END column correctness
- Knowledge Base of 18 reference PDFs (Baker FORTRAN source, EUBS proceedings, published Bühlmann/VPM comparisons)

**Links:**

- Web version (no install): https://three-cats-lsp.github.io/LSP_D-planner/
- Android APK: https://raw.githubusercontent.com/Three-Cats-LSP/LSP_D-planner/main/Android%20Apk/LSP_D-planner.apk
- GitHub: https://github.com/Three-Cats-LSP/LSP_D-planner

Free, open source, runs entirely offline. Happy to go deep on algorithm implementation or methodology.

---

## Instagram Caption

A proper dive planner. No subscriptions. No account. Just your dive. 🌊

LSP D-Planner v2.8.9 — free Android app and web app for real dive planning, built by @threecats_lsp for divers who care about their deco.

─────────────────────

🧮 ALGORITHMS
Bühlmann ZHL-16C + Gradient Factors
VPM-B and VPM-B/GFS hybrid
Full trimix support (O₂/He/N₂)

⛽ GAS MANAGEMENT
Gas Consumption card — right in the Deco Schedule
Rule of Thirds / Half Tank toggle — live update
Turn pressure · total volume · reserve · margin
Travel gas auto-pools with bottom gas if same mix
Color-coded: green = OK · red = SHORT

🔬 NARCOSIS & GAS TOOLS
Best Mix calculator — Nitrox and Trimix modes
MOD reference table — Air + EAN22–40 at 1.4 and 1.6 bar
END Calculator — narcotic depth, risk level, narcosis toggle
EAD Table — Equivalent Air Depth for all nitrox mixes
Narcotic depth warnings with explanation tooltips

📊 PLANNING TABS
Rec: Dive Planner · Surf Int · Avg Depth · Multi Dive · CNS O₂ · NDL Tables
Tec: Deco Schedule · Best Mix · Surf Int · Multi Dive · CNS O₂ · NDL Tables

📋 EXPORT
Deco Slate — compact waterproof slate format
Copy / TXT / PDF — full schedule + gas table
PDF gas consumption: 7-column table, color-coded

⭐ PRESETS
Save up to 20 named dive configs
Reload with one tap — stored locally, works offline

📱 THE APP
Native Android APK — works completely offline
No account · no subscription · always free
Open source on GitHub

─────────────────────

Try it in your browser right now 👇
🔗 three-cats-lsp.github.io/LSP_D-planner

Android APK on GitHub (link in bio)

Built by divers, for divers. 🤿

─────────────────────

#scuba #diveplanning #technicaldiving #decompression #trimix #deco #scubadiving #techscuba #diver #nitrox #openwater #diverlife #decoplanning #buehlmann #vpmb #narcosis #gasmixture #divecomputer #endcalculator #nitroxplanning

---

## Facebook Post

We just pushed a major update to LSP D-Planner v2.8.9 — a free dive planning app for Android and browser, and we wanted to share what's changed.

It started as a tool we built for ourselves because we wanted something we actually trusted for planning deco dives. This update brings a fully overhauled Tools section alongside the gas management improvements from earlier in the cycle.

**What's new in v2.8.9:**

**Gas Consumption (Deco Schedule)**
The gas table now lives directly in the Deco Schedule — GAS · TOTAL VOLUME · THIRDS · TURN PRESSURE · RESERVE · SUFFICIENT · MARGIN. Rule of Thirds and Half Tank toggle with live update. Travel gas auto-pools with bottom gas if same mix. MARGIN column shows `+/−X L` in green/red. Color-coded sufficiency throughout.

**Best Mix — Nitrox and Trimix modes**
The Best Mix tab in Tec mode now has a Nitrox/Trimix toggle. Nitrox mode calculates optimal O₂% and shows a live depth reference table (10–42 m). Trimix mode adds He% for a target END and shows full gas breakdown. Reads depth and gas directly from your current dive plan.

**Narcosis tools (Tools section)**
→ **END Calculator** — depth + O₂% + He% → narcotic depth, risk level, ppN₂/ppO₂/ppHe, MOD at 1.4 and 1.6 bar. Narcosis toggle (N₂ only vs N₂+O₂)
→ **EAD Table** — Equivalent Air Depth for EAN22–40 across 12–38 m, live-computed
→ **MOD reference table** — Air + EAN22–40 at both 1.4 and 1.6 bar, row highlight for your current O₂%
→ Narcotic depth warning banners across all relevant tabs, all wired to a tooltip explaining the 30 m convention

**Rec mode navigation**
New sub-menu: Dive Planner · Surf Int · Avg Depth · Multi Dive · CNS O₂ · NDL Tables. Average Depth moved from Tools into Rec — it's a planning tool for rec divers and belongs here.

**PDF export**
Gas consumption renders as a proper 7-column table in the PDF — dark header, color-coded rows, MARGIN column — matching the on-screen view exactly.

Everything else is unchanged: Bühlmann ZHL-16C with GF, VPM-B, VPM-B/GFS hybrid, altitude diving, Named Presets, Deco Slate export.

Try it in your browser: https://three-cats-lsp.github.io/LSP_D-planner/
Download the Android APK: https://raw.githubusercontent.com/Three-Cats-LSP/LSP_D-planner/main/Android%20Apk/LSP_D-planner.apk
Source code: https://github.com/Three-Cats-LSP/LSP_D-planner

Free, open source, offline. Always will be.

— Three Cats LSP (@threecats_lsp)
