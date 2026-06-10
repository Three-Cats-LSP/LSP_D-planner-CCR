# LSP D-Planner — Social Media Posts (v2.8.9)

---

## Reddit — r/scuba

**Title:**
I built a free Android dive planner that works offline — no subscriptions, no account, just real deco planning (Bühlmann + VPM-B)

**Body:**

Hey r/scuba — sharing something we've been building for a while, just pushed a big update and wanted to get it in front of more divers.

**LSP D-Planner** is a free dive planning app made by [Three Cats LSP](https://github.com/Three-Cats-LSP/LSP_D-planner). It runs as a native Android APK and also works in any browser — completely offline, no account required, no subscription, no ads.

**What it does:**

- Recreational NDL tables and full decompression planning with **Bühlmann ZHL-16C + Gradient Factors** (configurable GF Low/High)
- **VPM-B** and **VPM-B/GFS** (hybrid) algorithm support
- Multi-dive day planning — surface interval off-gassing is tracked and available NDL updates for each subsequent dive
- **Surface Interval calculator** — shows tissue saturation state after any surface interval, directly in the planner
- CNS O₂ and OTU tracking throughout the profile
- **Gas Consumption card** — now integrated directly in the Deco Schedule. Shows Rule of Thirds or Half Tank turn pressure, total volume, reserve, and whether you have enough gas for your planned dive. Travel gas is automatically pooled with bottom gas when they share the same mix.
- Travel gas support (automatic MOD-based switch depths)
- **Gas Table** — MOD and MND (narcotic depth) for all configured mixes at a glance
- **Deco Slate export** — compact waterproof dive slate format, exportable alongside PDF and TXT
- **Named Presets** — save and reload your dive configurations (up to 20 presets, stored locally)
- Full metric/imperial switching
- Altitude diving support

It's not trying to replace your dive computer — there's a clear disclaimer about that. But as a pre-dive planning tool it's genuinely capable.

**Try it in your browser:** https://three-cats-lsp.github.io/LSP_D-planner/
**Android APK (direct download):** https://raw.githubusercontent.com/Three-Cats-LSP/LSP_D-planner/main/Android%20Apk/LSP_D-planner.apk
**Source code:** https://github.com/Three-Cats-LSP/LSP_D-planner

It's open source and completely free. Happy to answer questions about how any of it works.

---

## Reddit — r/diving

**Title:**
Made a free dive planner app for Android — offline, no sign-up, does deco and NDLs. Here's what's in it.

**Body:**

Hey everyone — sharing something we've been heads-down on for a while.

**LSP D-Planner** is a free Android app (also a browser-based web app) for dive planning. No account, no subscription, works completely offline once installed.

Here's the honest summary of what it covers:

**Recreational divers:**
- No-decompression limit (NDL) tables
- Multi-dive day planning with residual nitrogen tracked across dives and surface intervals
- **Surface Interval calculator** — see your tissue loading drop in real time across any interval
- CNS oxygen toxicity tracker
- MOD calculator for nitrox

**Decompression divers:**
- Bühlmann ZHL-16C with configurable Gradient Factors
- VPM-B and VPM-B/GFS hybrid
- Full trimix support (O₂/He/N₂)
- Travel gas, deco gas, **Gas Consumption card** — turn pressure (Rule of Thirds or Half Tank), total volume, sufficiency check, all in the Deco Schedule. Travel gas pools with bottom gas automatically if the mix is the same.
- **Gas Table** — instant MOD and narcotic depth (MND) for all configured mixes
- **Deco Slate** — export your plan as a compact waterproof slate (Copy / SLATE / TXT / PDF)
- **Named Presets** — save your favorite dive configs with a name, reload them instantly
- END (Equivalent Narcotic Depth) column always visible in the deco schedule
- Altitude diving with corrected surface pressure

The web version runs in any browser so you can try it right now without installing anything:
👉 https://three-cats-lsp.github.io/LSP_D-planner/

Android APK download: https://raw.githubusercontent.com/Three-Cats-LSP/LSP_D-planner/main/Android%20Apk/LSP_D-planner.apk

It's open source: https://github.com/Three-Cats-LSP/LSP_D-planner

We built this because we wanted a proper planning tool we actually trusted. Would love feedback from anyone who tries it.

---

## Reddit — r/techscuba

**Title:**
LSP D-Planner v2.8.9 — free open-source Android deco planner, Bühlmann ZHL-16C + VPM-B + full trimix, integrated Gas Consumption card with Rule of Thirds / Half Tank, 147-check audit suite

**Body:**

Sharing a project we're genuinely proud of: **LSP D-Planner**, a free open-source technical dive planner — native Android APK and browser-based web app.

**Algorithms implemented:**

- **Bühlmann ZHL-16C + Gradient Factors** — industry-standard tissue model with configurable GF Low/High (presets or custom entry), standard 0.0577 bar water vapour correction
- **VPM-B** — full Varying Permeability Model with configurable conservatism margin
- **VPM-B/GFS hybrid** — VPM-B bubble mechanics determine deep stop depth; GF High applies at shallow/surface stops (configurable via presets or custom entry)

**Trimix / helium support:**

- Full O₂/He/N₂ entry for bottom gas and all deco gases
- Helium half-time selector: **Bühlmann 2003 (1.51 min)** or **Baker (1.88 min)**
- **END (Equivalent Narcotic Depth)** column always visible throughout the profile
- He-aware ppO₂ checks and MOD calculations wired through both Bühlmann and VPM-B engines

**Repetitive diving:**

- Multi-dive with surface interval tissue loading (Haldane N₂/He off-gassing)
- **Surface Interval calculator** — dedicated sub-tab showing tissue saturation state after any given interval
- VPM-B bubble state carry across dives — critical radii regenerate during surface interval using `r(t) = r_init + (r_end − r_init) × exp(−t / REGEN_TIME)` with a 14-day regeneration constant

**Altitude diving:**

- Altitude presets from sea level to 3000 m + custom input
- Acclimatization toggle for effective surface pressure correction
- VPM-B altitude-adjusted critical radii: `r_alt = r₀ × (P_SL / P_alt)^(1/3)`

**Gas management (new in v2.8.9):**

- **Gas Consumption card merged into Deco Schedule** — no separate Gas Plan tab. The card sits directly below the deco table and shows: GAS | TOTAL VOL | THIRDS | TURN PRESS | RESERVE | SUFFICIENT
- **Rule of Thirds and Half Tank** — toggle between rules live; turn pressure and sufficiency update instantly
- **Travel gas pooling** — if travel gas shares the same mix as bottom gas, its usable litres are added to the bottom total automatically. Label shows `Air (+Travel)` to confirm. No double-counting.
- **Warning rows** — gas short: red ✗ with volume deficit. BT suggestion (max bottom time for current cylinder): solid red `#FF4433` banner with white/black text depending on theme. Tight (<10% margin): same red banner treatment.
- **Info button** — `?` next to card title opens a popup explaining both rules, one-way deco gas logic, and the Short/Tight/OK status definitions
- SAC-based gas consumption in litres or cu ft, converting correctly on unit switch

**Export (all three updated in v2.8.9):**

- Copy / TXT / PDF all reflect the pooled travel gas label and correct totals
- PDF now correctly shows SHORT status on the bottom gas row when insufficient (was showing TURN)
- PDF renders the BT suggestion as a red banner row matching the on-screen style
- Text export uses `BOTTOM GAS: Air + Travel cyl` format when pooled

**Quality assurance:**

- **147-check static audit** (`audit.py`) across 20+ code groups — run before every commit
- HTML regression test suite (`tests-massive.html`) covering algorithm switching, VPM-B/GFS GF UI, SAC unit conversion, gas volume display, Gas Table formulas, Slate output, Preset persistence, END column correctness, and more
- Knowledge Base of 18 reference PDFs including Baker's original VPM FORTRAN source, EUBS proceedings, and published Bühlmann/VPM comparisons

**Links:**

- Web version (try now, no install): https://three-cats-lsp.github.io/LSP_D-planner/
- Android APK: https://raw.githubusercontent.com/Three-Cats-LSP/LSP_D-planner/main/Android%20Apk/LSP_D-planner.apk
- GitHub (open source): https://github.com/Three-Cats-LSP/LSP_D-planner

It's free, open source, and runs entirely offline once installed. Happy to go deep on the algorithm implementation or answer any questions about the methodology.

---

## Instagram Caption

A proper deco planner. No subscriptions. No account. Just your dive. 🌊

LSP D-Planner v2.8.9 is out — a free Android app (and web app) for real dive planning, built by @threecats_lsp for divers who actually care about their deco.

─────────────────────

🧮 ALGORITHMS
Bühlmann ZHL-16C + Gradient Factors
VPM-B and VPM-B/GFS hybrid
Full trimix support (O₂/He/N₂)

⛽ GAS MANAGEMENT (new in 2.8.9)
Gas Consumption card — right in the Deco Schedule
Rule of Thirds / Half Tank toggle — live updates
Turn pressure, total volume, reserve, sufficiency check
Travel gas auto-pools with bottom gas if same mix
BT suggestion shown as red banner when cylinder is too small

📊 PLANNING TOOLS
Multi-dive day planner — residual N₂ tracked
Surface Interval calculator — tissue off-gassing in real time
CNS + OTU oxygen toxicity tracking
Gas Table — MOD + narcotic depth for all mixes
Altitude diving support

📋 EXPORT
Deco Slate — compact waterproof slate format
Copy / TXT / PDF — full deco schedule export
Gas consumption in all exports — pooled travel gas included

⭐ PRESETS
Save up to 20 named dive configs
Reload with one tap — stored locally, works offline

📱 THE APP
Native Android APK — works completely offline
No account, no subscription, always free
Open source on GitHub

─────────────────────

Try it in your browser right now 👇
🔗 three-cats-lsp.github.io/LSP_D-planner

Download the Android APK from our GitHub (link in bio)

Built by divers, for divers. 🤿

─────────────────────

#scuba #diveplanning #technicaldiving #decompression #trimix #deco #scubadiving #techscuba #underwaterworld #diver #nitrox #openwater #diverlife #scubagear #decoplanning #buehlmann #vpmb #gasmixture #divecomputer #freediving

---

## Facebook Post

We just released LSP D-Planner v2.8.9 — a free dive planning app for Android, and we wanted to share what's new.

It started as a tool we built for ourselves because we wanted something we actually trusted for planning deco dives. v2.8.9 brings a major overhaul to gas management planning.

**What's new in v2.8.9 — Gas Consumption card:**

The standalone Gas Plan tab is gone. Instead, the full gas consumption table now lives directly in the Deco Schedule, right below your deco table where it belongs. It shows every gas you're planning to breathe — GAS, TOTAL VOLUME, THIRDS (turn pressure), RESERVE, and whether you have enough.

A few details worth highlighting:

→ **Rule of Thirds / Half Tank toggle** — switch between rules and watch the turn pressure and sufficiency update instantly, no recalculation needed
→ **Travel gas pooling** — if your travel gas is the same mix as your bottom gas (e.g. both Air), the volumes are pooled automatically. The card shows `Air (+Travel)` so you can see both cylinders were counted
→ **Warning rows** — if your cylinder is too small for the planned dive, a red banner tells you the maximum bottom time and turn pressure for your current cylinder. Same red treatment for one-way gases that are tight on margin
→ **Info button** — `?` next to the card title explains both gas rules, how one-way deco gas planning works, and what Short / Tight / OK mean
→ **Exports updated** — Copy, TXT, and PDF all reflect the pooled totals and correct labels. The PDF now correctly shows SHORT on the bottom gas row when gas is insufficient, and renders the BT suggestion as a red banner

The rest of the planner is unchanged: Bühlmann ZHL-16C with GF, VPM-B, VPM-B/GFS hybrid, full trimix, altitude diving, multi-dive planning, Surface Interval calculator, Deco Slate export, Named Presets.

Try it in your browser: https://three-cats-lsp.github.io/LSP_D-planner/
Download the Android APK: https://raw.githubusercontent.com/Three-Cats-LSP/LSP_D-planner/main/Android%20Apk/LSP_D-planner.apk
Source code and full changelog: https://github.com/Three-Cats-LSP/LSP_D-planner

Free, open source, offline. Always will be.

— Three Cats LSP (@threecats_lsp)
