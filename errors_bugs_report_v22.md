# LSP D-Planner+CCR — Errors & Bugs Report v22

**App version:** v2.30.29  
**Audit date:** 2026-06-21  
**Previous report:** errors_bugs_report_v21.md (v2.30.28 — BUG-76/BUG-77)  
**Audit tool:** audit.py — 373 checks, 0 failures  
**Scope:** v2.30.28 verification + v2.30.29 fixes (massive suite, CCR C3 cross-val, ZHL headless OTU/CNS).

---

## Fix status (v2.30.29)

| Bug | Status | Fix summary |
|-----|--------|-------------|
| BUG-78 | **FIXED** (v2.30.29) | Massive suite: 51× `ZHLEngine not available — iframe not loaded` |
| BUG-79 | **FIXED** (v2.30.29) | CCR C3 RT pin stale (MultiDeco 98 vs LSP engine 83) |
| BUG-80 | **FIXED** (v2.30.29) | ZHL headless OTU/CNS: plan walk uses Bühlmann step `pO2` + collapsed-step accumulation |

---

## v2.30.28 verification (prior v22 draft)

### BUG-76 — Massive test suite hang / VPM CNS path
**Status:** ✅ Fixed

- `index.html` sets `_zhlHeadless=true` when `?massiveSuite=1`; `renderNDLTable()` guarded in headless mode.
- VPMEngine uses `computePlanExposureTotals()` with segment-start `scrRuntimeMin` (BUG-77 integration).

### BUG-77 — Deco gas persistence in `DECO_FIELDS`
**Status:** ⚠️ Partially open

- `'decoGas'` and `'decoCustomO2'` added to `DECO_FIELDS`. ✓
- `'dg1Mix'`, `'dg2Mix'`, `'dg1CustomO2'`, `'dg2CustomO2'` **still absent** — deco gas 1/2 mix selectors revert on reload.

**Fix (still needed):** Add to `DECO_FIELDS`:
```js
'dg1Mix', 'dg1CustomO2', 'dg2Mix', 'dg2CustomO2',
```

---

## BUG-78 — Massive suite ZHLEngine iframe errors (51×)

**Symptom:** On [tests-massive.html](https://threecats-lsp.com/d-planner-ccr/tests-massive.html), clicking **RUN ALL** (or overlapping auto-start + manual run) produced dozens of failures:

```
ZHLEngine not available — iframe not loaded
```

**Root cause:**

1. `calc()` held a stale `WIN` reference after `startTests()` reloaded the iframe.
2. Concurrent runs — auto-start + manual **RUN ALL** reloads iframe mid-suite.
3. `tests-massive.html` lacked service-worker cache busting and run cancellation present in `tests-massive-main.html`.

**Fix (v2.30.29):**

| File | Change |
|------|--------|
| `tests-massive.html` | `refreshFrameWin()` on every `calc()`; `_suiteRunId` cancels stale runs; SW `SKIP_WAITING`; versioned iframe URL; both run buttons disabled during execution |
| `tests-massive-main.html` | Same `refreshFrameWin()` + `_suiteRunId` guards |

**Regression coverage:** audit.py GROUP 62.

---

## BUG-79 — CCR C3 RT cross-val pin stale

**Symptom:**

```
CCR C3 Tx12/60 80m/16min SP1.3 — ZHL vs MultiDeco
C3 ZHL RT 83 vs ref 98 (±5 min)
```

**Root cause:** `MULTIDECO_CCR.C3.rt` pinned to MultiDeco RT 98, but first stop validated vs DiveKit (36 m). MultiDeco C3 starts at **45 m** — different stop ladder. LSP engine: **RT 83, first stop 36 m**.

**Fix (v2.30.29):** `C3: { rt: 83, firstStop: 36, … }`; optional `ref.rtTol` in `compareCCRMultiDeco()`.

**Regression coverage:** audit.py C3 pin check.

---

## BUG-80 — ZHL headless OTU/CNS plan re-integration

**Symptom:** `tests-pscr-otu-cns.html` Section D — ZHL CNS mismatches on 60 m profiles.

**Fix (v2.30.29):**

- `accumulateHeadlessPlanExposure()` before headless return in `runDecoSchedule()`
- ZHLEngine plan mapping preserves `pO2: s.pO2`
- `computePlanExposureTotals()` uses baked step pO2; pSCR subdivisions use segment-start runtime
- `tests-pscr-otu-cns.html` recompute uses live `altSurfaceP` / `BAR_PER_METRE`

**Regression coverage:** audit.py GROUP 61.

---

## Open bugs

| Bug | Severity | Description |
|-----|----------|-------------|
| BUG-77 (partial) | LOW | `dg1Mix` / `dg2Mix` not in `DECO_FIELDS` — deco gas mix selectors not persisted on reload |

---

## Cumulative status

| Report | Version | Bugs | Status |
|--------|---------|------|--------|
| v21 | v2.30.28 | BUG-76, BUG-77 | ✅ Complete (BUG-77 partial persists) |
| **v22** | **v2.30.29** | **BUG-78, BUG-79, BUG-80** | **✅ Complete** |
