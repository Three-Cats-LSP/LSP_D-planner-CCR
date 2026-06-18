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

## Update — MultiDeco binary fully obtained and independently re-verified

Roman provided the actual `MultiDeco_226.apk` and both `libmultideco.so` builds (arm64-v8a, armeabi-v7a), now in `MultiDeco Binary/` in this repo, along with two analysis docs (`MultiDeco_Engine_Full_Analysis.md`, `MultiDeco_ShallowGradient_Analysis.md`). Claude independently re-disassembled and byte-verified the contested claims directly against the binary (not by re-reading the docs) — see `MultiDeco_Verified_Findings_2_Claude.md` for full method and evidence. Two things this changes for the roadmap:

1. **Item 4 (Shallow Gradient) is now unblocked** — formula confirmed instruction-for-instruction against the real binary. See the rewritten Item 4 below.
2. **The a5=0.6491 theory for the RT/TTS gap is retired.** Both of MultiDeco's stored N2 a-tables were found and verified (`0x15d00` = "A/B" variant a5=0.6667, `0x15d80` = "C" variant a5=0.6200) — neither uses 0.6491, and the "C"/GF mode table matches LSP's existing 0.6200 exactly. This is good news (one less unexplained discrepancy) but means the `OpenSource_Deco_Libraries_2.md` batch-2 doc's categorization of MultiDeco under the "canonical Bühlmann a5=0.6491" column was incorrect and should be disregarded.
3. **New finding, not on the original roadmap:** MultiDeco's N2 and He tissue compartments use each other's half-time constants — confirmed via direct pointer-tracing through `GAS_LOADINGS_CONST_DEPTH`'s disassembly, not inference. N2 tissue loading uses canonical *He* half-times (faster), He tissue loading uses canonical *N2* half-times (slower). This looks like a genuine bug in MultiDeco, not a design choice, and would explain RT/TTS gaps specifically on trimix dives (consistent with `Subsurface_Engine_Analysis.md` already flagging He-bearing scenarios as having the largest deltas) while leaving air/nitrox-only gaps unexplained by this mechanism. **Recommendation: do not replicate this in LSP.** No action item needed beyond noting it as a resolved piece of the historical gap investigation — this doesn't require any LSP code change, since LSP already has correct N2/He half-time assignment.

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

**Status:** Unblocked. Formula confirmed via direct ARM64 disassembly of the real binary, independently re-verified instruction-for-instruction by Claude (not just transcribed from the original analysis doc). Ready to scope an implementation.

**What it actually is (confirmed, not symbol-name guesswork):** Shallow Gradient is **not** an additional conservatism layer on the ceiling itself — the GF-derived ceiling is unchanged. It's a stop-scheduling smoothness adjustment with two independent triggers, both of which set a single `Apply_Shallow_Grad` flag:

**Trigger 1 — tissue-loading ratio** (`ShallowGradDepthTest`, confirmed at binary address `0x3251c`):
```
ratio = mean(N2_Press[i] - He_Press[i], i=0..15) / 32.0 / first_stop_depth_bar
Apply_Shallow_Grad = (ratio > 0.40)
if Apply_Shallow_Grad:
    Shallow_Grad_Max_ATA_Factor = min((ratio - 0.40) * 10.0, 1.0)   // 0→1 as ratio goes 0.40→0.50
```
Also applies a Boyle's Law compensation call (`BOYLES_LAW_COMPENSATION(depth/3, depth/3)`) as a side effect before computing the ratio — this dependency is itself a separate, already-disassembled function (`0x342ac`) if exact parity is wanted, though it's plausible the Boyle's-law call matters more for the VPM-B path than the ratio computation itself; needs a decision on whether to port it or treat the ratio check as Bühlmann/GF-only.

**Trigger 2 — stop-time-based** (`ShallowGradTimeTest`, confirmed at `0x35710`):
```
Apply_Shallow_Grad |= (current_stop_time_min > 60.0)
if overtime:
    Shallow_Grad_Time_Factor = min((current_stop_time_min - 60.0) * 0.05, 1.0)  // 0→1 as time goes 60→80 min
```

**Effect when active** (in `DECOMPRESS_STOP`): bypasses a fractional ceiling-to-stop-depth snap-extension check — when the computed ceiling falls awkwardly between two standard stop depths, the algorithm normally adds an extra rounding cycle; Shallow Gradient skips that check. **Net effect is usually a slightly shorter or smoother shallow-stop schedule, not a longer one** — this corrects an earlier assumption (carried in `MultiDeco_ShallowGradient_Analysis.md`'s own framing and in this roadmap's first draft) that the feature adds conservatism. It does the opposite in the common case.

**Confirmed constants (independently re-verified against raw binary bytes by Claude, not just transcribed):**
- Ratio threshold: `0.40` (rodata, confirmed)
- Ratio-to-factor scale: `×10`, capped at `1.0`
- Time threshold: `60.0` minutes (confirmed)
- Time-to-factor scale: `×0.05`, capped at `1.0` (reaches cap at 80 min)

**Proposed scope for 2.20.0:**
1. Implement the ratio-trigger and time-trigger as a single `shouldApplyShallowGrad(tissues, firstStopDepthBar, currentStopTimeMin)` helper in LSP's ZHL engine, following the LSP convention of pure functions operating on the existing `tissues` array shape (no need for the `Apply_Shallow_Grad` global flag pattern — keep it functional).
2. Implement the bypass effect: in LSP's own stop-time loop, identify the equivalent fractional-rounding logic (if LSP has one — needs a code-read first, since LSP's stop loop architecture differs from MultiDeco's; this may be a no-op if LSP doesn't have an equivalent snap-extension check to begin with, in which case the toggle would have no effect and that should be stated plainly in the tooltip rather than silently doing nothing).
3. Advanced Settings toggle, **off by default**, named clearly as MultiDeco-compatible behavior (not a Bühlmann/VPM-B standard feature), consistent with the existing "MultiDeco compatible" labeling pattern already used for Transit Mode / Stop Rounding.
4. Decide on the Boyle's Law compensation dependency (open question above) before finalizing — may be VPM-B-only in practice, which would simplify the Bühlmann/GF-mode implementation to just the ratio/time triggers with no Boyle's-law side effect.

**Acceptance:**
- New toggle in Advanced Settings, off by default, with tooltip stating plainly what it does (smooths/shortens shallow stops under high tissue loading or long stop times) and that it's MultiDeco-specific behavior, not a standard algorithm feature.
- Audit check confirming the toggle defaults to off and that enabling it only affects shallow-stop rounding, not the underlying ceiling.
- Regression test on at least one scenario from the existing cross-reference suite where the ratio trigger is expected to activate (a long/deep dive with high tissue loading relative to first-stop depth — S6 or A2 from the existing 21-scenario suite are good candidates given their already-large MultiDeco deltas) to confirm the toggle moves LSP's output in the expected direction (shorter/smoother, not longer).

---

## Item 5 — Multi-level dive profile support

**Status:** Real, large item. Previously deferred ("too large for current session scope") — now being added to 2.20.0 proper per Roman's request, but should be treated as the biggest single item in this release and may justify its own sub-milestone/branch rather than landing in one pass.

**What exists today:** LSP's entire planning pipeline is single-level. The whole UI and both engines are built around one `decoDepth` input and one bottom-time value — confirmed by reading the live code, not assumed: `decoDepth` (a single numeric field, e.g. line ~14388) drives `bottomDepth`, which flows into a single descent→bottom→ascent schedule. There is no concept of "descend to 40m for 10 min, then move to 25m for 20 min, then ascend" as a single planned dive — multi-level dives today have to be approximated by running LSP multiple times and manually combining results, which doesn't correctly track tissue loading across the transition.

**What's needed:**
1. **Input model change:** replace (or augment) the single depth/time pair with an ordered list of segments, each with its own depth, time, and optionally gas (a multi-level dive may also be a multi-gas dive, though gas switching during bottom segments is a related-but-separable concern — confirm whether to scope both together or gate gas-per-segment behind the existing gas-switch UI). UI needs an "Add Level" affordance, similar in spirit to the existing deco-gas add/remove list, ordered top-to-bottom by time (segment 1 happens first).
2. **Engine change:** both `loadTissuesConstant`-style segment processing and the Schreiner descent/ascent-between-segments math already exist and are correct (per the "Schreiner vs Haldane" correction above) — the work is in the *driving loop*, not the underlying physics. Each level transition is just another Schreiner-driven depth change followed by a Haldane-driven constant-depth hold; the existing per-segment functions should compose directly. The real engineering risk is in how `runDecoSchedule()` (line ~8152) currently assumes a single bottom phase — needs a careful read of that function's control flow before estimating effort further.
3. **TTS worst-point consideration (flagged separately in `Abysner_GUE_Crosscheck_Addendum.md`):** Abysner computes Time-To-Surface at every segment boundary, not just end-of-final-segment, specifically because a shallower-but-longer trailing segment can accumulate more deco obligation than the deep portion. LSP's reserve-gas/TTS logic should adopt this same per-boundary-max approach once multi-level segments exist — doing this from the start avoids a silent under-report of reserve gas on profiles where the worst point isn't the last segment.
4. **Result display:** the existing single-bottom-segment result table/export structure (deco table rows, TXT/PDF export, profile graph) needs to show multiple bottom/transition rows distinctly — check whether the existing row-type system (`'bottom'`, `'descent'`, etc., seen at line ~7684) already has the vocabulary for this or needs new row types for "transit between levels" vs "initial descent."
5. **Validation:** decide how strictly to validate segment ordering/depths (e.g. can a later segment be deeper than an earlier one — yes, that's a legitimate multi-level profile and just means the controlling ceiling tracks the max depth reached, not monotonically decreasing depths) and what happens to existing single-level saved dives/presets when this ships (should default to "1 segment" and behave identically to today for anyone not using the new feature).

**Recommended approach:** before writing any code, read `runDecoSchedule()` end-to-end and produce a short written breakdown of exactly which parts assume single-level vs which are already segment-agnostic. This item is large enough that estimating it accurately requires that read first — don't scope further from this roadmap doc alone.

**Acceptance:**
- User can add 2+ depth/time segments to a single dive plan and get one combined schedule with correctly continuous tissue loading across all segments (verify against a hand-computed or cross-app reference profile, not just "it runs without erroring").
- TTS/reserve-gas calculation checks every segment boundary, not just the last one.
- Existing single-segment dives (the overwhelming majority of current users) see zero behavior change — this is additive.
- All three test suites (`tests-massive.html`, `tests-massive-main.html`, `tests-verify.html`) still pass, plus new multi-level-specific test cases added to at least one of them.
- Export formats (TXT/PDF/Messenger) correctly show the multi-level structure, per the existing export consistency rule.

---

## Item 6 — Advanced Settings profiles: save/load, plus pre-built app-default presets

**Status:** Scoped, ready to implement. Builds directly on an existing mechanism rather than introducing new architecture.

**What exists today:** `appSettings` (line ~15717) already has exactly the right shape for this — `DECO_FIELDS` is a maintained list of every relevant setting's element ID, and `save()`/`load()` already serialize all of them to/from a single `localStorage` slot (`lspDiveSettings_v6`) as one JSON blob. This is a single implicit "current settings" slot, not a named multi-profile system — that's the actual gap.

**What's being added:**
1. **Named user profiles:** instead of one implicit slot, support N named profiles (e.g. "My Cave Setup", "Conservative Travel"), each storing the same field set `DECO_FIELDS` already tracks. Store as `lspDiveProfiles_v1: { profileName: { ...fields }, ... }` alongside (not replacing) the existing auto-save slot, which continues to behave as "last used settings" exactly as today. Add Save/Load/Delete/Rename UI in the Advanced Settings panel — a profile selector dropdown plus "Save as new profile" / "Save changes to current profile" / "Load" / "Delete" actions.
2. **Pre-built app-default presets:** a fixed, non-editable set of "load these values" buttons, one per reference app already studied, populating the *same* `DECO_FIELDS` that user profiles use — selecting one just pre-fills the form, exactly like loading a user profile, and the diver can then tweak and optionally save their own variant from there. Confirmed default values to seed each preset (already documented in the knowledge base, not invented for this item):

| Setting | LSP (current default) | MultiDeco | Abysner | GUE DecPlanner |
|---|---|---|---|---|
| GF Low | 40 (confirmed: `gfLowInput` selected option) | 30 | 60 | 20 (OC) |
| GF High | 80 (confirmed: `gfHighInput` selected option) | 85 | 70 | 85 (OC) |
| Descent rate | 20 m/min | ~18 m/min (60 ft/min) | 20 m/min | 20 m/min |
| Ascent rate | 10 m/min | ~5 m/min (15 ft/min) | 5 m/min | 9 m/min |
| Deco step size | 3 m | (smallest index, ~1m / 3.3ft) | 3 m | 3 m |
| Last deco stop | 3 m | ~3 m (10 ft) | 3 m | 3 m |
| Max ppO2 (bottom) | 1.4 bar (confirmed: `ppo2Bottom` selected option) | n/a (deco-only table documented) | 1.4 bar | 1.2 bar |
| Max ppO2 (deco) | 1.6 bar (confirmed: `ppo2Deco` selected option) | 1.6 ata | 1.6 bar | 1.2 bar (deco) / 1.5 bar (Max O2) |

   **This table still needs one more verification pass before implementation** — some values above were converted from imperial source units (MultiDeco's settings are stored as imperial-default indices per `MultiDeco_GUI_Planner_Analysis.md` §8) and rounded for display; exact metric conversions should be recomputed precisely. LSP's own current defaults (descent/ascent/step/last-stop/ppO2) are now confirmed directly from the live `<select>` markup; GF Low/High were also just confirmed (40/80) and should replace any stale "Lo=30/Hi=85" reference elsewhere in this knowledge base that was actually describing MultiDeco's defaults, not LSP's — worth a search-and-check across other docs for this mix-up before this item ships. An "ApexDeco" preset was also requested but has no dedicated analysis doc yet in this knowledge base — needs a short research pass (the existing `refs/` engine source files may be enough) before that specific preset can be seeded; don't block the other three presets on it.

3. **Known constraint to design around:** several of these settings are `<select>` dropdowns with a *fixed* list of options (e.g. `ascentRate` only offers 3/6/9/10/12/15/18 m/min), not free-text numeric inputs. A reference app's exact default may not exist as an option (e.g. MultiDeco's ~4.6 m/min ascent rate has no matching `<option>` in LSP's current dropdown). Decide per-field whether to (a) snap to the nearest existing option, (b) add the missing option to the dropdown itself if it's a value worth offering generally, or (c) convert affected fields to free-text numeric inputs. Recommend (b) where the missing value is a reasonable thing to offer regardless of presets, (a) otherwise — and document whichever choice is made per field, since "preset says one thing, loaded value is slightly different" needs a clear UI explanation (e.g. a small note "(rounded to nearest available value)") rather than silently snapping.
4. **Tooltip/labeling:** each preset button should be labeled by app name and have a tooltip noting it's an approximation of that app's *defaults*, not a guarantee of identical computed results (the underlying algorithm differences documented elsewhere in this knowledge base, e.g. MultiDeco's N2/He half-time swap, mean two apps with "the same settings" can still produce different schedules) — avoid implying these presets make LSP compute identically to the named competitor.

**Where it goes:** New subsection within the existing Advanced Settings panel (`advancedSettingsBody`, line ~1757) — a "Settings Profiles" group, likely near the top of the panel given it can replace everything below it.

**Acceptance:**
- User can save current Advanced Settings as a named profile, reload it later, and delete/rename it.
- At least 3 app-default presets (MultiDeco, Abysner, GUE DecPlanner) load correctly with verified-accurate values; ApexDeco preset added once its defaults are researched, or explicitly deferred with a note if not feasible in this pass.
- Loading any preset does not silently fail on fields where the target value isn't an available dropdown option — it either snaps with a visible note, or the dropdown gains the option.
- Existing single-slot auto-save/auto-load behavior (today's `appSettings.save()`/`.load()`) is unchanged for anyone not using the new named-profile UI — this is additive.
- Audit check confirming the new `lspDiveProfiles_v1` storage key round-trips correctly (save → reload page → load → values match).

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
4. **Item 6 (Settings profiles)** — straightforward extension of an existing mechanism (`appSettings`), no dependency on anything else in this list, good candidate to interleave with 1–3 if it speeds up parallel progress.
5. **Item 4 (Shallow Gradient)** — unblocked (formula confirmed against the real binary). Needs one design decision before starting (the Boyle's Law compensation dependency, see Item 4 above) plus a code-read of LSP's existing stop-time loop to find the equivalent fractional-rounding check the bypass applies to.
6. **Item 5 (Multi-level profiles)** — by far the largest item; do this last, after the smaller items are shipped and the team has fresh familiarity with `runDecoSchedule()` from working through Items 1–4. Strongly recommend a dedicated read-through of `runDecoSchedule()`'s current control flow as its own first step, written up before estimating further, rather than scoping the implementation purely from this roadmap doc. Consider shipping as its own minor version (e.g. 2.20.0 ships Items 1–4 and 6; multi-level lands in 2.21.0) if it threatens to hold up everything else — flag this trade-off with Roman once Items 1–4 and 6 are further along and there's a clearer sense of remaining time/complexity budget.

Each item gets its own audit GROUP and CHANGELOG entry per existing project convention. Run the full `tests-massive.html` / `tests-massive-main.html` / `tests-verify.html` suite after each item, not just `audit.py`, since these touch live calculation paths (Items 2, 3, 4, and 5 especially).
