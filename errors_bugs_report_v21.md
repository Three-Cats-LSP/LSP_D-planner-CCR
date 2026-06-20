# LSP D-Planner+CCR — Errors & Bugs Report v21

**App version audited:** v2.30.26  
**Audit date:** 2026-06-21  
**Previous report:** errors_bugs_report_v20.md (v2.30.26 — BUG-75 fixed, 0 open bugs)  
**Audit tool:** audit.py — 353 checks, 0 failures  
**Commits audited:** `bbc92a4` (v19 baseline) → `35e0059` (v2.30.26)

---

## Summary

v2.30.25 refactored ZHLEngine headless OTU/CNS into a shared
`computePlanExposureTotals()` helper, replacing the inline `headlessPpo2`
block. v2.30.26 fixed BUG-75 (`ccrDiluentSurfaceLpm` pSCR formula) and
added CCR cross-validation tests.

**All changes verified correct. 0 new bugs found.**

---

## BUG-75 Fix Verification (v2.30.26, commit `fa2659a`)

**Status:** ✅ Fixed and verified

```js
// Before (wrong):
const fr = computePSCRFractions(pSurf, bot.fO2, bot.fHe, runtimeMin, ccr);
const fO2Loop = Math.max(0.01, fr.fO2);
return (metRate / fO2Loop) * PSCR_DEFAULT_BYPASS_RATIO;

// After (correct):
if (ccr.circuit === 'pSCR' && !ccr.bailout) {
  return metRate * PSCR_DEFAULT_BYPASS_RATIO;
}
```

`computePSCRFractions` and `fO2Loop` removed entirely from the pSCR branch.
Result: `1.5 × 10 = 15 L/min` at default settings (was ~93 L/min for EAN32 at 40 m).

**Regression coverage added:**
- `tests-verify.html` section I — pSCR surface LPM ≈ 15 (not 93)
- `tests-massive.html` — CCR/pSCR DOM cross-validation
- `audit.py` GROUP 58 — static guard against `metRate / fO2Loop` pattern

---

## v2.30.25 Refactor Verification (`ecb3a49`)

### `computePlanExposureTotals()` — new shared OTU/CNS integration helper

Replaces the inline `headlessPpo2`/`hCNSfrac`/`hOTU` block in `ZHLEngine.calculate()`.

**Correctness verified:**

- `mergeCCRSettings(settings)` used for config — all CCR fields with DOM fallbacks ✅
- pSCR path: `getEffectivePpo2(pAmb, 0, fo2, { ...cfg, scrRuntimeMin: run, bailout: false }, depth, fh)` — `run` is cumulative runtime per segment, correctly propagates depletion ✅
- CCR path: `getEffectiveSetpointAtDepth(depth, cfg, surfP, phase)` → `getEffectivePpo2(pAmb, sp, ...)` — phase derived from `seg.type` ('descent'/'bottom'/'deco'/'stop'/'ascent') ✅
- OC/bailout: `fo2 * pAmb` fallback ✅
- `segFrac(val, fallback)`: integer percentage (e.g. `o2: 32` → `0.32`) and fractional (`o2: 0.32` → `0.32`) both handled correctly ✅
- `run` field injected into every ZHLEngine plan segment (cumulative, monotone) before `computePlanExposureTotals` is called ✅
- VPMEngine unaffected — continues to use `vpmAccumPpo2` internally; exposes `normPlan` with `run: seg.run ?? seg.runtime` to test harnesses ✅

**No duplication between VPM and ZHL paths** — `computePlanExposureTotals` used only by ZHLEngine headless; VPM has its own integrated accumulation. ✅

---

## Full Audit — All Areas Clean

### CCR engine logic
- `mergeCCRSettings`: clean centralised config merge, used by all CCR helpers ✅
- `computePSCRFractions` / `getEffectivePpo2` / `getEffectiveSetpointAtDepth`: unchanged, correct ✅
- `vpmAccumPpo2` (9 call sites) / `ctxUseOCForPpo2(settings)`: unchanged, correct ✅
- `addBailoutStressReserve`: correct depth distribution ✅

### Gas plan / gas consumption
- `ccrDiluentSurfaceLpm` pSCR: `metRate × PSCR_DEFAULT_BYPASS_RATIO = 15 L/min` ✅
- `ccrDiluentSurfaceLpm` OC/CCR: `metRate / fO2Dil` (unchanged, correct) ✅
- `sacDomToLpm` imperial conversion intact ✅
- `gpVolDisp` imperial display intact ✅

### Exports
- All export OTU/CNS paths unchanged; source from engine `totalCNS/totalOTU` ✅
- ZHLEngine `totalOTU`/`totalCNS` now from `computePlanExposureTotals` — correct for CCR/pSCR/OC ✅

### UI / settings / persistence
- `appSettings.clear()` — all keys cleared ✅
- Version sync: all four files at `2.30.26` ✅

### VPM vs Bühlmann parity
- Both engines route CCR/pSCR OTU/CNS through `getEffectivePpo2` ✅
- Both use cumulative runtime for pSCR depletion (`scrRuntimeMin`) ✅
- OTU / CNS formulae consistent ✅

### Regression suite
- `audit.py` 353 checks, 0 failures ✅
- `tests-pscr-otu-cns.html` gas reference helpers updated for corrected BUG-75 formula ✅
- `tests-massive.html` CCR cross-val recalibrated to DiveKit-aligned first-stop + RT (stop distribution effect on helium dives documented) ✅
- BUG-75 regression (pSCR surface LPM value) now covered ✅

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
| v1–v13 | – v2.30.15 | BUG-01–68 | ✅ All fixed |
| v14 | v2.30.15 | BUG-69–70 | ✅ Fixed |
| v15 | v2.30.16 | BUG-71 | ✅ Fixed |
| v16 | v2.30.17 | BUG-72 | ✅ Fixed |
| v17 | v2.30.23 | BUG-73–74 | ✅ Fixed |
| v18–v19 | v2.30.24 | BUG-75 | ✅ Fixed (v2.30.26) |
| v20 | v2.30.26 | 0 bugs | ✅ Clean |
| **v21** | **v2.30.26** | **0 new bugs** | **✅ Clean** |
