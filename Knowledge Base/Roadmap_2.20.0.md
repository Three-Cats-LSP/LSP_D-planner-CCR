# LSP D-Planner — Roadmap to v2.20.0

**Baseline:** `v2.10.44-milestone` tag (192/192 audit checks passing)
**Status:** Planning — scoped after deep-dive verification against current `index.html`, not assumptions from prior session summaries.

---

## Important correction before this roadmap was written

Two items originally proposed for 2.20.0 turned out to already be implemented after checking the actual code (not just the comparison docs, which were stale/wrong on these two points). Recording this so we don't re-litigate it later.

### ❌ NOT a gap: Schreiner vs Haldane
LSP already uses the **true Schreiner equation** for changing-depth segments:
- `schreinerLinear()` (line ~4808, ZHL engine) — exact textbook form: `P(t) = P_i + R(t - 1/k) - (P_i - P_0 - R/k)e^{-kt}`
- `schreiner()` (line ~6608, VPM engine) — same equation, used inside `makeScheduleContext`
- Plain `saturate()` (closed-form Haldane) is correctly reserved for constant-depth segments (bottom time, stop holds) — this is the same `stagnate()`/`descend()` split AquaBSD's libbuhlmann uses, which the comparison doc called "the most clearly structured" reference implementation.

**No work item needed.** The earlier framing ("LSP uses Haldane for everything") was incorrect — likely a stale claim carried over from an old session summary that was never re-verified against the live file. There's nothing to add here, and no per-algorithm-tab "Schreiner vs Haldane" choice is needed since both are already used where each is mathematically correct.

### ❌ NOT a gap: Altitude pre-saturation toggle
Already implemented, and arguably more rigorous than MultiDeco's version:
- "Acclimatized: Yes/No" select, in the main ENV row (`acclimatizedRow`, next to Altitude), with a full tooltip explaining the Cross-correction and VPM bubble-radius scaling.
- `initTissues()` (line ~4776): Acclimatized → tissues initialize at altitude surface pressure (lower N2 load). Not acclimatized → tissues initialize at sea-level pressure (conservative, models "just arrived, still carrying sea-level N2").

**Only open question:** should this toggle move from the main ENV row into the Advanced Settings panel for consistency? This is a UI placement decision, not a feature gap — see Item 4 below for a recommendation.

---

## Item 1 — Surface GF display

**Status:** Scoped, ready to implement.

**What it is:** A read-only diagnostic metric showing how close the diver's leading tissue compartment is to the raw (GF-unmodified) M-value at surface pressure, expressed as a percentage. **It is not an algorithm input** — confirmed in `OpenSource_Deco_Libraries.md`, tl5915's `DecoResult.surfGF` is populated after the schedule is computed, purely for display.

**Formula (tl5915, confirmed correct):**
```
denom = a + (P_surface / b) - P_surface
surfGF = (tissue_load - P_surface) / denom * 100
```
Computed per-compartment at end-of-dive tissue state; report `max()` over all 16 compartments (the controlling/leading compartment), same convention as the existing Compartment Detail table's "Sat %" column (line ~2230) — in fact this is closely related to that existing column. Surface GF is essentially "Sat % of the single worst compartment, using GF=100% (no conservatism) as the reference" rather than the GF-adjusted M-value already shown there.

**Where it goes:** The results footer (`decoTotals`, line ~2148), alongside the existing TTS / CNS / OTU / PrT / Decozone / First-deco fields (see `buildExportText`-style summary at line ~4452). Also include in TXT/PDF export per the existing **export consistency rule** — any new summary field must appear in all export modes/formats, not just the live DOM.

**Acceptance:**
- New `surfaceGF` field on the result object from both ZHL and VPM engines.
- Shown in the on-screen summary footer.
- Included in TXT export, PDF export (deco mode), and Messenger-text export.
- Audit check: confirm `surfaceGF` is present and a number 0–~150% on a representative dive.

---

## Item 2 — CNS/OTU dual-method audit

**Status:** Needs verification, not "implementation" — the two existing methods may already agree, this is about confirming it and documenting which is authoritative.

**What was found:** Two independent CNS computation paths exist:
1. **VPM engine scope** (line ~7085): `CNS_RATE_ANDROID`, a 131-point Android-dive-computer-style instantaneous rate table, accumulated via `calculateCNS(ppO2, time)`.
2. **ZHL/display scope** (line ~8848): `rowCNS()` / `segCNSfrac()`, an 11-point NOAA single-dive CNS-limit table, used for the deco table's per-row CNS% column.

These are two legitimate, different CNS methodologies (rate-accumulation vs limit-interpolation) and they're scoped to different algorithm tabs (VPM vs ZHL), so this is not necessarily a bug — but nobody has verified they produce consistent CNS% for the same ppO2/duration input, and a diver switching between the ZHL and VPM tabs on the same profile shouldn't see materially different CNS%.

**Task:**
1. Write a test harness that feeds identical ppO2/duration pairs through `calculateCNS()`/`getCNSRate()` and `rowCNS()`/`segCNSfrac()` across the full ppO2 range (0.5–1.8 bar) and diffs the output.
2. If they diverge meaningfully, decide on one authoritative table (the 131-point table is more granular and matches what most real dive computers ship — likely the better candidate) and use it in both places.
3. Confirm OTU is consistent too — both `calculateOTU()` (VPM scope) and `segOTU()` (ZHL scope) use the same NOAA formula (`time * ((ppO2-0.5)/0.5)^0.833` vs `^0.8333` — note the exponent differs in the 4th decimal between the two copies in the file, worth normalizing to one constant).
4. Add audit checks (new GROUP) once the authoritative method is confirmed/fixed, to catch future drift between the two CNS/OTU copies.

**Acceptance:** Single source of truth for CNS rate table and OTU exponent constant, referenced from both engine scopes, with a regression test proving ZHL-tab and VPM-tab CNS% match for identical ppO2/duration inputs.

---

## Item 3 — Multi-day residual loading ("Last Dive" / surface interval in dd/hh:mm)

**Status:** Real, scoped gap. New item added per Roman's request.

**What exists today:**
- VPM engine has a single repetitive-dive carry mechanism (`vpmRepMode` checkbox + `vpmSurfaceInterval` numeric minutes input, max 10080 = 7 days expressed awkwardly as raw minutes). Carries: N2/He tissue state, VPM bubble state (critical radii), CNS (90-min half-life decay — correct), OTU (carried with **no decay or day-boundary reset** — this is the actual bug-shaped gap).
- ZHL engine has **no repetitive-dive carry at all** — its "Surface Interval" feature (line ~2785) is a one-way calculator ("how long until I *can* dive again"), not a state-carry mechanism like VPM's.
- Everything is keyed to a single prior dive. There's no concept of a multi-day dive trip history (e.g. "day 4 of a liveaboard, last dive ended 14h22m ago").

**What MultiDeco/dive computers do that LSP doesn't:** track elapsed real time since the last dive in a human dd/hh:mm format, and use that to determine:
- Residual N2/He loading (already physically correct in LSP's math — the gap is purely the *input format and multi-day framing*, not the underlying Haldane offgassing math, which already handles arbitrarily long surface intervals correctly via `Math.exp(-k * si)`)
- Whether CNS has fully decayed (at 90-min half-life, ~9 hours ≈ 6 half-lives ≈ <2% residual — effectively zero for any interval beyond ~12h, so this is mostly about *not having to know that*, the UI should just handle it)
- Whether OTU should reset (daily-dose model — should reset at a real calendar-day boundary, not carry indefinitely as it does today)

**Proposed scope for 2.20.0:**
1. Replace the single `vpmSurfaceInterval` minutes-only input with a `dd/hh:mm` formatted "Last Dive" input (e.g. `02/14:30` = 2 days, 14 hours, 30 minutes since last dive surfaced). Parse to total minutes internally — the existing tissue-offgassing math (`Math.exp(-kN2 * settings._surfaceInterval)`) needs no change, since it already correctly handles arbitrarily large `si` values; this is purely an input-format and OTU-reset fix.
2. Fix OTU carry: if elapsed time crosses a real day boundary (>24h, or per a configurable "OTU day" convention — confirm whether NOAA defines this as calendar day or rolling 24h window before implementing), reset `_preOTU` to 0 instead of carrying forward unconditionally.
3. At 5+ days (or some explicit threshold — confirm a sensible value, e.g. when N2 in the slowest compartment (635 min half-time) has decayed to <1% above baseline, which is ~10 half-lives ≈ 4.4 days), treat the diver as "fully clean" — this may already fall out naturally from the existing exponential decay math once arbitrary multi-day `si` values can actually be entered; verify rather than special-case it.
4. Decide whether to extend this same carry mechanism to the **ZHL engine** (currently VPM-only) — recommend yes, for parity between the two algorithm tabs, since residual N2 loading is policy-relevant regardless of which model the diver is planning with.
5. Update the repetitive-dive badge/tooltip (line ~6321) to show the parsed dd/hh:mm rather than just raw minutes.

**Acceptance:**
- `dd/hh:mm` input parses correctly (including edge cases: `00/00:30`, `05/00:00`, single-digit days).
- OTU resets correctly across a day boundary; does not reset spuriously within a day.
- ZHL engine gains the same repetitive carry VPM already has, or an explicit documented decision for why not.
- Existing VPM repetitive dive tests (tissue/bubble carry) still pass unchanged — this is additive, not a rewrite of the carry math itself.

---

## Item 4 — Shallow Gradient (MultiDeco proprietary feature)

**Status:** Research spike required before any implementation can be scoped. Do not attempt to implement from current information — there is no formula yet, only symbol names.

**What we actually have:** From `APK_Reverse_Engineering.md`, a list of *symbol names* pulled from MultiDeco's stripped native binary's symbol table:
```
Shallow_Grad_Depth_Factor
Shallow_Grad_Time_Factor
Shallow_Grad_Max_ATA_Factor
ShallowGradDepthTest()
Apply_Shallow_Grad
```
No disassembled function bodies, no formula, no coefficients were extracted — the original analysis (credited to "Three-Cats-LSP / Perplexity Computer" in the doc header) only went as far as the symbol table. **I have not personally inspected the MultiDeco binary** — no `.so` file or disassembly exists anywhere in this sandbox; only the markdown summary and a results JSON were available this session.

**To make progress, one of the following is needed:**
1. **Roman uploads the actual MultiDeco APK** (available from APKPure/AppBrain/Aptoide — `com.hhssoftware.multideco`, ~4.2 MB, latest v2.26) so the native `libmultideco.so` (both `arm64-v8a` and `armeabi-v7a` variants exist) can be disassembled directly — `strings`, `nm -D`, and a `struct`-based float64/float32 scanner against the `.text`/`.rodata` sections, the same method already used successfully to pull the confirmed ZHL-16C b-coefficient table out of this binary previously. This is the highest-confidence path to an actual formula.
2. **Alternatively**, if the MultiDeco UI itself exposes a "Shallow Gradient" toggle with a help/tooltip description (most likely under its Advanced or Bailout settings, based on the `bailConserveGFHi`-adjacent symbol naming), screenshots or a written description of what the feature claims to do in plain English would let us design an equivalent from first principles rather than reverse-engineer the exact internal formula.
3. **Lowest-confidence fallback:** infer a reasonable behavior from the symbol names alone (`Depth_Factor` × `Time_Factor`, capped by `Max_ATA_Factor`, gated by a `DepthTest()`) and implement a documented **approximation**, clearly labeled as such in the UI tooltip and CHANGELOG, not a faithful port. Only pursue this if (1) and (2) are unavailable, since shipping a guessed safety-relevant deco algorithm change under a name that implies parity with a specific competitor's feature is misleading to users.

**Recommendation:** Pause this item until Roman can upload the APK (path 1). It's a half-day task once we have the binary, given the existing tooling and successful precedent on the same binary. Don't burn tokens guessing at safety-relevant math from five symbol names.

**If/when implemented:** Advanced Settings toggle, off by default, with a tooltip that's explicit about it being MultiDeco-compatible shallow-stop acceleration (or whatever it's confirmed to do), not a Bühlmann/VPM-B standard feature — same spirit as the existing "MultiDeco compatible" labeling already used elsewhere in Advanced Settings (e.g. Transit Mode, Stop Rounding per `DiveKit_Engine_Knowledge_Base.md`).

---

## Deferred — CCR/SCR support

Explicitly deferred to a future version (2.30+ or later) per Roman's instruction — not worth the token/time cost in 2.20.0. For when it is picked up, the formula is already verified and ready from `OpenSource_Deco_Libraries.md` (tl5915):
```
pN2_alv = P_amb - ppO2_setpoint - WATER_VAPOR   (CCR mode)
```
and MultiDeco's full CCR/SCR/bailout symbol set is documented in `APK_Reverse_Engineering.md` for reference (`CALC_O2_LOADINGS_CLOSED`, `SCRO2Drop`, `ppO2Above/Below/Deep/ReallyDeep/Swaps`, etc.) if/when this is picked back up.

---

## Suggested implementation order for 2.20.0

1. **Item 1 (Surface GF)** — smallest, self-contained, no architectural decisions pending.
2. **Item 2 (CNS/OTU audit)** — should happen before Item 3, since Item 3's OTU-reset fix depends on knowing which OTU formula is authoritative.
3. **Item 3 (Last Dive dd/hh:mm + OTU day-boundary fix)** — the most user-facing win Roman specifically asked for.
4. **Item 4 (Shallow Gradient)** — blocked on Roman uploading the MultiDeco APK; can run in parallel with 1–3 if the upload happens early, otherwise slips to 2.20.x or later.

Each item gets its own audit GROUP and CHANGELOG entry per existing project convention. Run the full `tests-massive.html` / `tests-massive-main.html` / `tests-verify.html` suite after each item, not just `audit.py`, since these touch live calculation paths (Items 2 and 3 especially).
