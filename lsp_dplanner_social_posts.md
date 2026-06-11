# LSP D-Planner — Social Media Posts

---

## v2.9.0 Post

**Title:**
LSP D-Planner v2.9.0 — PDF exports, copy preview modal, slate rework, Math Verification Suite

**Body:**

LSP D-Planner v2.9.0 is out. Free, open source, runs in any browser and as an Android APK — offline, no account, no ads.

This release is focused on export quality and verification.

---

**PDF exports — completely reworked**

Both the Dive Plan PDF and Emergency Plan PDF now have a section picker dialog before export — choose which sections to include.

Dive Plan PDF sections: Gas Consumption · Dive Profile · Deco Slate · GF Curve · Tissue Saturation

Emergency Plan PDF sections: Emergency Gas Consumption · Ascent Schedule · Dive Profile · GF Curve · Tissue Saturation · Emergency Slate

Both PDFs now use a single Unicode font (DejaVu Sans) throughout — proper rendering of ✓ ✗ ⚠ ↑ ↓ and all Unicode symbols. Same header/footer layout, same section title style, same font sizes. Only the theme color differs (blue for dive plan, red for emergency). The ⚠ warning icon in the emergency PDF header is now the real Unicode character, not `[!]`.

---

**Copy preview modal**

The copy button now opens a preview modal showing the full formatted plan text before copying — same style as the Slate modal. Both Deco Plan and Emergency Plan use this. No more silent clipboard writes.

---

**Export footer rework — all formats**

Copy footer (two lines now):
```
Run Time:66'00" Deco:27'24"
CNS:36.2% OTU:73 PrT:21.7
```

Slate footer (two lines):
```
TRT: 66'00" | DECO: 27'24"
CNS: 36.2% OTU: 73 PrT: 21.7
```

TRT = Total Run Time (renamed from TBT to avoid confusion with BT = Bottom Time). Full MM'SS" format. Both deco and emergency slates use the same footer format.

All exports (copy, slate, TXT) now include:
- `DECO PLAN` / `EMERGENCY PLAN` title on the first line
- Date/time stamp `YYYY/DD/MM HH:MM` on the second line
- Divider line after the stamp

`LSP D-PLANNER` prefix removed from slate headers — just `DECO SLATE` / `EMERGENCY SLATE`.

---

**UI**

- Collapsible result cards (Gas Consumption, Contingency Plans, Dive Graph, Tissue Saturation, GF Curve) — caret on the right side of each card header
- Card order: Dive Profile → Gas Consumption → Contingency Plans → Dive Graph → Tissue Saturation → GF Curve
- Tissue Saturation in PDF now matches the web view format (per-compartment bars)
- All 9 deco table columns exported to PDF: Phase / Depth / Stop / Run / Mix / EAD / END / PPO2 / CNS%

---

**Math Verification Suite — new**

`tests-verify.html` — standalone verification page, runs against the live engine in an iframe.

Sections A–H:
- A: Pinned regression VPM-B (LSP v2.9.0 outputs must not change between versions)
- B: Pinned regression Bühlmann ZHL-16C+GF
- C: Baker Python cross-check — stop depths and RT within 30% of Baker VPM-B reference
- D: Cross-model ordering (Maiken invariants) — monotonicity across depth, BT, conservatism, gas mix
- E: ZHL-16C coefficient verification — all 16 compartments vs canonical Bühlmann 2003 values
- F: Physics constants — BAR_PER_METRE, WATER_VAPOR, ppO₂, MOD, EAD, END
- G: Determinism and edge cases — same profile = same result, NDL, extreme depth, 1 min BT, 180 min BT
- H: MultiDeco / V-Planner compatibility — VPM-B/GFS ordering, GF Hi monotone, pinned tables, water vapor

Also fixed 4 bugs in the test harness discovered during the audit:
- `gfs` parameter double-division bug (passed `hi/100` when engine already divides by 100)
- `WATER_VAPOR` re-sync used `||` fallback which misfires on value `0`
- `ZHL16C` fallback chain pointed at the test page's local const, not the engine window
- `stops()` helper had dead `s.time` fallback (engine only uses `s.dur`)

---

**Links:**
- Web: https://three-cats-lsp.github.io/LSP_D-planner/
- Math Verification Suite: https://three-cats-lsp.github.io/LSP_D-planner/tests-verify.html
- Android APK: https://github.com/Three-Cats-LSP/LSP_D-planner/raw/main/Android%20Apk/LSP_D-planner.apk
- GitHub: https://github.com/Three-Cats-LSP/LSP_D-planner

Free and open source. Happy to go deep on algorithm implementation, the VPM-B/GFS hybrid, or the verification methodology.

---

## v2.8.x Archive Post (previous milestone)

**Title:**
LSP D-Planner — free open-source deco planner (Bühlmann ZHL-16C + VPM-B + VPM-B/GFS), 446-test regression suite

**Body:**

LSP D-Planner is a free dive planning app by [Three Cats LSP](https://www.instagram.com/threecats_lsp). It runs in any browser and as a native Android APK — completely offline, no account, no ads, no subscription.

**Two modes:**

**Recreational divers:**
- NDL tables with pressure group tracking (PADI RDP-based)
- Multi-dive day planning with residual nitrogen tracking across dives and surface intervals
- Surface Interval calculator — shows tissue loading per compartment in real time
- Average Depth converter — enter your logbook average depth, get a recommended planning depth
- CNS O₂ tracker
- MOD calculator for nitrox

**Decompression divers:**

Algorithms:
- Bühlmann ZHL-16C + Gradient Factors — configurable GF Low/High (presets or custom), water vapour correction, 16 tissue compartments
- VPM-B — Varying Permeability Model with configurable conservatism margin (+0 to +5)
- VPM-B/GFS hybrid — VPM-B bubble mechanics set deep stop depth; GF High applied at shallow and surface stops

Gas management:
- Gas Consumption card — GAS · TOTAL VOL · THIRDS · TURN PRESS · RESERVE · SUFFICIENT
- Rule of Thirds and Half Tank toggle — live update, no recalculation needed
- Travel gas pools with bottom gas automatically if same mix; label shows Air (+Travel) to confirm
- SAC-based consumption in litres or cubic feet with correct unit conversion

Trimix / helium:
- Full O₂/He/N₂ entry for bottom gas and all deco gases
- He half-time selector: Bühlmann 2003 (1.51 min) or Baker (1.88 min)
- END column in the deco schedule; trimix-aware (He non-narcotic)
- He-aware ppO₂ checks and MOD calculations throughout both engines

Repetitive diving:
- Multi-dive with surface interval tissue loading (Haldane N₂/He off-gassing)
- Surface Interval calculator — all 16 compartments, controlling compartment, reverse-profile warning, tissue bar chart
- VPM-B bubble state carry between dives: r(t) = r_init + (r_end − r_init) × exp(−t / REGEN_TIME), 14-day regeneration constant

Altitude:
- Presets sea level to 3000 m + custom; acclimatization toggle
- VPM-B altitude-adjusted critical radii: r_alt = r₀ × (P_SL / P_alt)^(1/3)

Quality:
- Static audit (audit.py) — structural checks across 20+ code groups
- 446-test regression suite (tests-massive.html) — engines, UI/DOM, Tier 1–3 scenarios, travel gas, altitude, trimix, VPM-B/GFS, GF UI, gas plan, slate, presets, preset persistence

**Links:**
- Web: https://three-cats-lsp.github.io/LSP_D-planner/
- Android APK: https://github.com/Three-Cats-LSP/LSP_D-planner/raw/main/Android%20Apk/LSP_D-planner.apk
- GitHub: https://github.com/Three-Cats-LSP/LSP_D-planner

Free, open source, runs entirely offline.
