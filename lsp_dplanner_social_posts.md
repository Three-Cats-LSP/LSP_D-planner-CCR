# LSP D-Planner + CCR — Social Media Posts

Posts for v2.30.30 (Safety Sign-Off release). Adapt tone and length to platform.

---

## Post A — Full Feature Overview (Reddit r/technicaldiving, r/rebreathers, forums, GitHub)

**Title:**
LSP D-Planner + CCR v2.30.30 — free open-source rebreather deco planner (CCR · pSCR · bailout · Bühlmann ZHL-16C + VPM-B) with Android app

**Body:**

LSP D-Planner + CCR is a free browser-based decompression planner for rebreather divers — CCR, passive SCR, and bailout. Native Android app. Completely offline, no account, no subscription.

🌐 **Web app:** https://threecats-lsp.com/d-planner-ccr/
📲 **Android APK:** https://threecats-lsp.com/d-planner-ccr/download.html
💻 **GitHub:** https://github.com/Three-Cats-LSP/LSP_D-planner-CCR

---

**Three breathing circuit modes:**

**CCR (closed-circuit rebreather)**
- Phase-aware setpoints: descent SP / bottom SP / deco SP — each configurable
- Setpoint crossing on ascent/descent calculated correctly
- Diluent-aware tissue loading — loop vs OC for every segment
- On-loop gas consumption via metabolic injection rate (not OC SAC)

**pSCR (passive SCR)**
- GUE-style loop O₂ depletion model: loop volume + metabolic O₂ rate + cumulative runtime
- 0.16 bar ppO₂ floor — physiologically realistic
- Loop gas consumption: `metabolic rate × bypass ratio` (default 10×) — corrected formula
- OTU/CNS: full plan-walk with per-segment runtime, accurate on long dives

**Bailout (CCR → OC emergency)**
- Configurable bailout GF (default 50/85, independent of dive GF)
- Deepest-capable bailout gas auto-selected at each deco stop
- Stress/problem-solve reserve distributed across bottom + all deco depths

---

**Two deco engines, both with full rebreather paths:**

- **Bühlmann ZHL-16C + GF** — GF presets (GUE, MultiDeco, Abysner, Subsurface, DiveKit) or custom. Shallow gradient toggle.
- **VPM-B / VPM-B/GFS** — conservatism +0 to +5, altitude-adjusted radii, CCR/pSCR setpoint through entire bubble model.

Both engines use the same OTU/CNS plan-walk engine (`computePlanExposureTotals`) — descent → bottom → deco — with segment-accurate pSCR runtime. Cross-validated against each other.

---

**Gas Management:**
- Diluent card (cylinder size, pressure, reserve) — consumption via correct metabolic model
- Up to 2 bailout/deco gas cards with MOD validation per ppO₂ limit
- Stress + problem-solve reserve allocated to the right gas at each depth
- Rule of thirds or half tank; metric or imperial (SAC in L/min or cu ft/min)

**Export:**
- PDF, TXT, deco slate, messenger copy — all labelled DECO PLAN (CCR) or (OC)
- PDF filenames include circuit tag: `LSP_CCR_2026-06-21_Deco_40m_...`
- Share to T-Viewer (https://threecats-lsp.com/t-viewer/) for buddy/surface review

---

**v2.30.30 — Safety Sign-Off:**

This release closes 85 independently verified audit findings (BUG-01 through BUG-85) across 28 audit passes. 383/383 static checks passing. Includes a 36-test pSCR OTU/CNS validation suite covering 20/40/60 m × EAN32/EAN36 × Bühlmann + VPM.

Full certification: https://github.com/Three-Cats-LSP/LSP_D-planner-CCR/blob/main/SAFETY_CERTIFICATION_v2.30.30.md

This is planning software for trained rebreather and mixed-gas divers — verify all plans against your dive computer and training standards.

Free and open source (MIT).

---

## Post B — Short (Instagram / X / Mastodon)

LSP D-Planner + CCR v2.30.30 — free open-source rebreather deco planner.

CCR · pSCR · Bailout
Bühlmann ZHL-16C + GF · VPM-B · VPM-B/GFS
Phase-aware setpoints · loop gas model · bailout GF
Full gas plan · stress reserve · PDF & TXT export
Android app · full offline · no account

Safety Sign-Off: 85 audit findings closed · 383/383 checks passing

🌐 https://threecats-lsp.com/d-planner-ccr/
📲 APK: https://threecats-lsp.com/d-planner-ccr/download.html
💻 https://github.com/Three-Cats-LSP/LSP_D-planner-CCR

#scubadiving #technicaldiving #rebreather #CCR #pSCR #decompression #diveplanning #opensource #android #trimix

---

## Post C — Algorithm/Physics Focus (Reddit r/technicaldiving / r/rebreathers / ScubaBoard)

**Title:**
Open-source pSCR/CCR deco planner — phase-aware setpoints, loop depletion model, dual-engine OTU/CNS parity, 36-test validation suite

**Body:**

LSP D-Planner + CCR is a client-side rebreather deco planner — single HTML file, no server, runs fully offline in browser or as Android app (Capacitor).

**pSCR loop physics:**

The pSCR module (`computePSCRFractions`) models O₂ depletion as:
- O₂ consumed = metabolic rate × cumulative runtime (L at ambient pressure)
- Loop O₂ fraction = max(`PSCR_MIN_PPO2`, fresh_fO₂ − consumed / (loop_vol × pAmb))
- Diluent gas consumption = metabolic_rate × bypass_ratio (default 10×) — NOT a function of depleted fO₂
- Per-segment runtime-tracking so long stops and ascents compute the correct depleted ppO₂

**CCR setpoints:**

Three independent setpoints: descent (default 0.7 bar), bottom, deco. `getEffectiveSetpointAtDepth(depth, cfg, surfP, phase)` selects the correct SP based on phase and depth crossover. Applied in Bühlmann tissue loading, VPM bubble model, ppO₂ display, OTU/CNS accumulation, calcCNS tab, and all export paths.

**Dual-engine OTU/CNS parity:**

Both engines use `computePlanExposureTotals(plan, settings, ...)` — a plan-walk function that:
- Uses baked `pO₂` from each step when available (computed by `_ccrPpo2Opts`)
- Sub-steps through pSCR ascent segments at midpoint runtime for depth interpolation
- Phase-aware: descent/bottom/deco mapped to correct SP tier
- Prior-dive O₂ carry handled once, no double-counting

Validated in `tests-pscr-otu-cns.html` (36 tests: 20/40/60 m × EAN32/EAN36 × Bühlmann + VPM, OTU/CNS cross-check within 2%).

**References cross-checked against:** ApexDeco, DivePro, MultiDeco, Subsurface, Baker FORTRAN, VPMb.py.

🌐 https://threecats-lsp.com/d-planner-ccr/
🔬 Tests: https://threecats-lsp.com/d-planner-ccr/tests-pscr-otu-cns.html
💻 https://github.com/Three-Cats-LSP/LSP_D-planner-CCR

Free and open source (MIT).

---

## Post D — Android / APK Focus

**LSP D-Planner + CCR — Android rebreather deco planner**

Native Android app for CCR and pSCR dive planning. Direct APK download — no Play Store.

**What it does:**
- Full deco planning: Bühlmann ZHL-16C + GF, VPM-B, VPM-B/GFS
- CCR mode: phase-aware setpoints, diluent-aware tissue loading, loop gas plan
- pSCR mode: GUE-style loop depletion, bypass ratio gas consumption
- Bailout planning with configurable GF
- Trimix, travel gas, altitude, repetitive dives
- Gas plan with stress/problem-solve reserve per deco stop
- Export TXT and PDF to Downloads; share to buddy

**Android features:**
- Edge-to-edge, transparent status bar
- Light/dark theme (system or manual)
- Full offline after install
- No account, no ads, no tracking

📲 **Download:** https://threecats-lsp.com/d-planner-ccr/download.html

Requires Android 5.1+ (API 22). Free, open source (MIT).

