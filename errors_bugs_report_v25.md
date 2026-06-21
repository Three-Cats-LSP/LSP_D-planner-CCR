# LSP D-Planner+CCR — Errors & Bugs Report v25

**App version audited:** v2.30.30  
**Audit date:** 2026-06-21  
**Previous reports:** v21b–v24 (committed during this session — BUG-76–84)  
**Audit tool:** audit.py — 381 checks, 0 failures  
**Commits audited:** `62e0ccc` (v21 baseline) → `99a411f` (v2.30.30)

---

## Summary

v2.30.27–30 fixed BUG-76 (partial), BUG-77–84 across five rapid patch cycles.  
Final commit `13a35c9` fixed BUG-77 (`dg1Mix`/`dg2Mix` persistence), BUG-83
(audit.py stale version pin) and BUG-84 (version sync).

**1 bug remains open: BUG-76 (`VPMEngine._setHeHT1` never defined).**  
**0 new bugs found.**

---

## BUG-77–84 Fix Verification

| Bug | Fix commit | Status |
|-----|-----------|--------|
| BUG-77 — `dg1Mix`/`dg2Mix` not in `DECO_FIELDS` | `13a35c9` (v2.30.30) | ✅ Fixed |
| BUG-78 — Massive suite 51× iframe ZHLEngine errors | `4fdbcc6` (v2.30.29) | ✅ Fixed |
| BUG-79 — CCR C3 RT cross-val pin stale | `4fdbcc6` (v2.30.29) | ✅ Fixed |
| BUG-80 — ZHL headless OTU/CNS plan-walk baked pO2 | `4fdbcc6` (v2.30.29) | ✅ Fixed |
| BUG-81 — Massive main VPM `calculate is not a function` | `d610f1d` (v2.30.30) | ✅ Fixed |
| BUG-82 — ZHL pSCR OTU single-sample vs plan walk | `86e5135` (v2.30.30) | ✅ Fixed |
| BUG-83 — `audit.py` version pin stale | `13a35c9` (v2.30.30) | ✅ Fixed |
| BUG-84 — Version mismatch across all files | `13a35c9` (v2.30.30) | ✅ Fixed |

### BUG-77 detail

`DECO_FIELDS` (line 17519) now includes:
`'dg1Mix'`, `'dg1CustomO2'`, `'dg2Mix'`, `'dg2CustomO2'`,
`'dg1TrimixO2'`, `'dg1TrimixHe'`, `'dg2TrimixO2'`, `'dg2TrimixHe'`.

`settingsFingerprint` array (line 17763–17764) also updated — fingerprint
will change when gas mixes change, triggering correct plan invalidation.

`restoreSettings` calls `toggleDecoCustomO2` for both `dg1Mix`/`dg1CustomField`
and `dg2Mix`/`dg2CustomField` (line 17825–17827) — custom O₂ input visibility
correctly restored with the saved mix mode. ✅

### BUG-82 detail

`accumulateHeadlessPlanExposure()` builds a proper plan array (descent +
bottom + all collapsed deco steps) and delegates entirely to
`computePlanExposureTotals()`. Ascent segments propagate `from`/`to` so
the pSCR sub-step depth interpolation (`seg.from + (seg.to-seg.from)×frac`)
fires correctly. Carries `_priorDiveCarry` OTU/CNS once, after the plan walk.

`ZHLEngine.calculate()` returns `totalOTU`/`totalCNS` from
`accumulateHeadlessPlanExposure` (via `_headlessExposure`) — same plan-walk
path as VPM. Both engines now fully consistent. ✅

---

## Open Bug

### BUG-76 — VPMEngine `_setHeHT1` never defined (LOW) — still open

**Location:** `updateHeHalfTime()` line 3959; VPMEngine `return { calculate, … }` line 9412

`updateHeHalfTime()` checks and calls `window.VPMEngine._setHeHT1(src[0])` but
`VPMEngine`'s exported API object does not include `_setHeHT1`. The `typeof …
=== 'function'` guard silently no-ops.

**Effect:** When user selects `heHalfTimeMode = 'buhl2003'`, VPMEngine He
compartment [0] retains Baker 1998 value (1.88 min) instead of Bühlmann 2003
(1.51 min). Bühlmann engine correctly updates. 20% half-time error on fastest
He compartment for trimix VPM dives with buhl2003 mode.

**Fix:**
```js
// In VPMEngine return object (line 9412):
_setHeHT1: function(htRow) {
  if (ZHL16C_He[0]) ZHL16C_He[0].ht = htRow.ht;
},
```

---

## Full Audit — All Areas Clean

### CCR engine logic
- `mergeCCRSettings`: centralised, correct ✅
- `computePlanExposureTotals` pSCR path: sub-step depth interpolation for ascent
  segments uses `seg.from + (seg.to - seg.from) × frac` — correct ✅
- `baked pO2` fast-path: deco steps with `s.pO2` set by `_ccrPpo2Opts` bypass
  `computePSCRFractions` (already correct at construction time) ✅
- `planSegDepthM` ascent midpoint `(from+to)/2` used only for CCR/OC single-sample
  path — pSCR uses sub-step interpolation ✅
- `vpmAccumPpo2` (9 call sites), `ctxUseOCForPpo2(settings)`: unchanged, correct ✅

### Gas plan / gas consumption
- `ccrDiluentSurfaceLpm` pSCR: `metRate × PSCR_DEFAULT_BYPASS_RATIO` (BUG-75 fix) ✅
- `sacDomToLpm` imperial conversion intact ✅
- `addBailoutStressReserve` depth distribution correct ✅

### Exports
- Bühlmann: `_lastPlan.totalCNS/totalOTU` from `_headlessExposure`
  (`accumulateHeadlessPlanExposure`) ✅
- VPM: `_lastVPMExport.cns/otu` from `result.totalCNS/totalOTU`
  (`computePlanExposureTotals` via `VPMEngine.calculate`) ✅
- PDF, text, messenger, slate all source from above paths ✅

### UI / settings / persistence
- `dg1Mix`, `dg1CustomO2`, `dg2Mix`, `dg2CustomO2` now persisted (BUG-77 fix) ✅
- `dg1TrimixO2`, `dg1TrimixHe`, `dg2TrimixO2`, `dg2TrimixHe` also persisted ✅
- `appSettings.clear()` — all keys cleared correctly ✅
- Version sync: `APP_VERSION`, `package.json`, `build.gradle`, `sw.js` all `2.30.30` ✅

### VPM vs Bühlmann parity
- Both engines use `computePlanExposureTotals` for final OTU/CNS walk ✅
- Both engines use `mergeCCRSettings` + per-segment runtime for pSCR depletion ✅
- He half-time parity: BUG-76 aside, all other compartments consistent ✅

### Regression suite
- `audit.py` 381 checks, 0 failures ✅
- `tests-pscr-otu-cns.html` updated to use live `altSurfaceP`/`BAR_PER_METRE` ✅
- `tests-massive.html` / `tests-massive-main.html` iframe stale-ref + run-id guards ✅
- `tests-verify.html` ±1–2 min RT WARN tolerance for stop-distribution drift ✅

---

## New Bugs Found

**None.**

---

## Carry-Over OC Main Bugs (out of scope for CCR repo)

| Bug | Description | Repo |
|-----|-------------|------|
| BUG-40 | Bühlmann emergency gas `sz` not converted cu ft→L (~line 9789) | LSP_D-planner |
| BUG-41 | `appSettings.clear()` only removes `lspDiveSettings_v3` (~line 16449) | LSP_D-planner |

---

## All CCR Repo Bugs — Cumulative Status

| Report | Version | Bugs | Status |
|--------|---------|------|--------|
| v1–v21 | – v2.30.26 | BUG-01–75 | ✅ All fixed |
| v21b | v2.30.26 | BUG-76, BUG-77 | BUG-76 ❌ open, BUG-77 ✅ fixed |
| v22 | v2.30.30 | BUG-78–82 | ✅ All fixed |
| v23 | v2.30.29 | BUG-77 (still open) | ✅ Fixed (v2.30.30) |
| v24 | v2.30.30 | BUG-83–84 | ✅ Fixed (v2.30.30) |
| **v25** | **v2.30.30** | **0 new bugs** | **BUG-76 still open** |
