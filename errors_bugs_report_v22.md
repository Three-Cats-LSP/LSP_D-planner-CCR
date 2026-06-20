# LSP D-Planner + CCR — Errors & Bugs Report v22

**Repo:** `Three-Cats-LSP/LSP_D-planner-CCR`  
**Version analysed:** v2.30.28 (commit `a945d5f`)  
**Date:** 2026-06-21  
**Audit result:** 363 checks, 0 failures  
**Scope:** Verification of BUG-76/77 fixes. One finding remains partially open; no new critical bugs.

---

## Verification

### BUG-76 — Massive test suite hang / VPMEngine He HT CNS impact
**Status:** ✅ Substantially fixed

Two separate issues were addressed under this label:

1. **Test suite hang** (their interpretation): `index.html` now sets `_zhlHeadless=true` immediately at parse time when loaded with `?massiveSuite=1` query param. `renderNDLTable()` is guarded by `!window._zhlHeadless` in all 3 call sites. This prevents DOM recalc storms during test execution. ✓

2. **VPM CNS/OTU accuracy** (our concern): VPMEngine now uses `computePlanExposureTotals(normPlan, settings, ...)` instead of inline `vpmAccumPpo2` accumulators. For pSCR dives, `scrRuntimeMin` is correctly computed as `runEnd - dur` (segment-start runtime), improving OTU/CNS accuracy. ✓

**Remaining:** VPMEngine internal `ZHL16C_He` tissue loading still uses Baker ht[0]=1.88 regardless of `heHalfTimeMode`. `_setHeHT1` is still defined nowhere in VPMEngine. However, since CNS/OTU now flows through `computePlanExposureTotals` (which uses the global `ZHL16C_HE_HT` array), this only affects VPM tissue loading itself — a design-appropriate choice since VPM-B canonical uses Baker 1.88.

### BUG-77 — Deco gas mixes not persisted in `DECO_FIELDS`
**Status:** ⚠️ Partially fixed

- `'decoGas'` (bottom gas selector) and `'decoCustomO2'` were added to `DECO_FIELDS`. ✓  
- `'dg1Mix'`, `'dg2Mix'`, `'dg1CustomO2'`, `'dg2CustomO2'` are **still absent** from `DECO_FIELDS`. ✗

Deco gas 1 and gas 2 mix selectors still revert to 'none' on every page reload. The bottom gas (`decoGas`) is now saved. Trimix O₂/He inputs (`dg1TrimixO2`, `dg1TrimixHe`, etc.) are saved but without the mode selector (`dg1Mix`) they have no effect after reload.

---

## Improvements Verified

| Change | Status |
|---|---|
| `computePlanExposureTotals` exposed on `window` for test access | ✓ |
| `planSegDepthM` uses midpoint for ascent segments (was: shallow end) | ✓ Improves CNS accuracy on ascent |
| `planSegRunEndMin` uses `run ?? runtime` — handles both VPM and ZHL segments | ✓ |
| pSCR `scrRuntimeMin = runEnd - dur` — correct segment-start runtime | ✓ |
| CCR phase detection in `computePlanExposureTotals` correct ('descent'/'bottom'/'deco') | ✓ |
| VPM `buildResult` now uses `computePlanExposureTotals` consistently | ✓ |

---

## Open Bug

### BUG-77 (partial) — `dg1Mix` and `dg2Mix` still not in `DECO_FIELDS`

**File:** `index.html`  
**Location:** `appSettings.DECO_FIELDS` line ~17430  
**Severity:** LOW

`'dg1Mix'`, `'dg2Mix'`, `'dg1CustomO2'`, `'dg2CustomO2'` remain absent. Users must re-select deco gas 1 and gas 2 mixes after every page reload.

**Fix:** Add to `DECO_FIELDS`:
```js
'dg1Mix', 'dg1CustomO2', 'dg2Mix', 'dg2CustomO2',
```

---

## Summary

| # | Severity | Status | Description |
|---|---|---|---|
| BUG-76 | LOW | ✅ Fixed (CNS path) / Acceptable (VPM tissue HT) | He HT CNS/OTU now via computePlanExposureTotals |
| BUG-77 | LOW | ⚠️ Partial | decoGas saved; dg1Mix/dg2Mix still not persisted |

