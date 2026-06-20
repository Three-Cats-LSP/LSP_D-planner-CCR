# LSP D-Planner + CCR — Errors & Bugs Report v9

**Repo:** `Three-Cats-LSP/LSP_D-planner-CCR`  
**Version analysed:** v2.30.9 (commit `a96e77b`)  
**Date:** 2026-06-21  
**Scope:** Ninth verification pass. Covers the full CCR/pSCR/bailout engine introduced in v2.30.0 and all fixes through v2.30.9. Also cross-checks `LSP_D-planner` (main) at v2.20.21 for regressions.  
**Status of v8 bugs:** BUG-40, BUG-41, BUG-42 all confirmed fixed in LSP_D-planner-CCR v2.30.9 (not yet fixed in LSP_D-planner v2.20.21 — see section D).

---

## A — HIGH

### BUG-43 — `ccrDiluentSurfaceLpm()` uses wrong fallback for metabolic O₂ rate (0.85 vs DOM default 1.5)

**File:** `index.html`  
**Location:** `ccrDiluentSurfaceLpm()` line ~5939; `computePSCRFractions()` line ~5754

```js
// ccrDiluentSurfaceLpm():
const metRate = ccr.scrMetabolicO2 || 0.85;   // ← fallback 0.85 L/min

// computePSCRFractions():
const metO2 = ccr.scrMetabolicO2 || 0.85;     // ← same fallback 0.85 L/min

// getCCRSettingsFromDOM():
const metO2 = parseFloat(document.getElementById('ccrMetabolicO2')?.value)
           || parseFloat(document.getElementById('scrMetabolicO2')?.value) || 1.5;
// ↑ DOM default is 1.5 L/min, hidden legacy field default is also 1.5
```

The DOM input `ccrMetabolicO2` defaults to `1.5` L/min, and `appSettings.DECO_FIELDS` saves it as `'1.5'`. But both `ccrDiluentSurfaceLpm()` and `computePSCRFractions()` fall back to `0.85` L/min when `ccr.scrMetabolicO2` is falsy. If the settings object is constructed via `mergeCCRSettings()` with no DOM access (e.g. headless tests or a preset load path where `scrMetabolicO2` is `0`/`null`/`undefined`), diluent consumption and pSCR O₂ drop are both calculated at `0.85` instead of `1.5` — a 43% underestimate of O₂ consumption. The fallback should be `1.5` to match the DOM default and the settings save default.

**Impact:** Diluent gas consumption underestimated by ~43% in edge cases; pSCR loop O₂ fraction miscalculated, producing shallower "safe" tissue loading than the actual breathed gas would give.

---

### BUG-44 — `validateCcrGasConfiguration()` uses `ccrBottomSetpoint` as the ppO₂ limit for pSCR diluent MOD check — wrong for pSCR

**File:** `index.html`  
**Location:** `validateCcrGasConfiguration()` lines ~6082–6085

```js
const activePpo2 = parseFloat(document.getElementById('ccrBottomSetpoint')?.value)
  || parseFloat(document.getElementById('ppo2Bottom')?.value) || 1.4;
const diluentMod = calcGasMODm(bot.fO2, activePpo2);
```

`ccrBottomSetpoint` is hidden (CSS `display:none`) when circuit is `pSCR` — the SP rows are only shown for `isCCR`. In pSCR mode the field retains its default value of `1.2 bar`. So the diluent MOD check runs against `ppO₂ = 1.2 bar` in pSCR mode, not the diver's actual open-circuit `ppo2Bottom` limit (default 1.4 bar, user-configurable). This produces a more conservative MOD warning than intended: e.g. for Air diluent the check yields MOD = 50 m (at 1.2 bar) instead of the correct 56 m (at 1.4 bar), potentially showing a spurious error or warning when the diver's actual ppO₂ limit is higher.

For pSCR, the correct limit to use is `ppo2Bottom` (the OC ppO₂ limit), since pSCR has no active electronic setpoint.

**Impact:** False validation errors/warnings in pSCR mode when planned depth is between the 1.2 bar and 1.4 bar MOD of the diluent. No safety risk (conservative direction), but incorrectly blocks valid pSCR dive plans.

---

## B — MEDIUM

### BUG-45 — Gas Plan tab `gpBot` row is always labelled "Bottom Gas" even in CCR mode — no dedicated diluent cylinder row

**File:** `index.html`  
**Location:** Gas Plan tab inputs (`gpBot_size`, `gpBot_fill`, `gpBot_reserve`) and `calcGasPlan()` lines ~13620–13630; `updateCcrGasCardLabels()` lines ~5996–6030

In OC mode `gpBot` is the bottom gas cylinder. In CCR/pSCR mode the Gas Plan tab correctly relabels the gas card title to "DILUENT" (`diluentCardTitle`), but the `gpBot` cylinder row in the Gas Plan tab retains static labels ("Size (L)", "Fill bar", "Reserve bar") and is still treated as a rule-of-thirds/half-tank gas. 

For CCR/pSCR diluent consumption, `ccrGasLitres()` returns `ccrDiluentSurfaceLpm() * durMin` — a flat surface-equivalent rate independent of cylinder pressure. However, `calcGasPlan()` checks the diluent cylinder against `_lastGasConsumed` keyed by gas label (e.g. `"AIR"`). In CCR on-loop mode, the gas consumed is stored under the `loopMixLabelFor()` key (e.g. `"CCR Air"`), not the raw `"AIR"` label — so `gpRequiredFor(botLabel)` returns `null` for the diluent, the sufficiency check always shows "run plan", and the Gas Plan tab never cross-checks the diluent cylinder against actual plan consumption in CCR mode.

**Impact:** Gas Plan tab cannot validate diluent cylinder sufficiency in CCR/pSCR mode — the most safety-critical gas planning check for rebreather diving is silently skipped.

---

### BUG-46 — `ccrDiluentSurfaceLpm()` ignores depth — diluent consumption modelled at surface-equivalent rate only

**File:** `index.html`  
**Location:** `ccrGasLitres()` line ~5963; `ccrDiluentSurfaceLpm()` line ~5937

```js
function ccrGasLitres(label, depthM, durMin, sac) {
  if (isCcrDiluentGasLabel(label)) return ccrDiluentSurfaceLpm() * durMin;  // depth ignored
  ...
}
function ccrDiluentSurfaceLpm() {
  const metRate = ccr.scrMetabolicO2 || 0.85;
  return metRate / Math.max(0.01, bot.fO2 || 0.21);   // surface L/min of diluent
}
```

CCR diluent consumption is the gas used to maintain loop volume (buoyancy changes, O₂ injector flush, loop losses). The dominant component is gas-density-compensated O₂ addition: at depth the diluent cylinder delivers gas at ambient pressure, so actual diluent consumption (in litres of free gas at surface equivalent) scales with ambient pressure. Using a flat `surface_L/min × duration` underestimates diluent use at depth. For a 40 m dive the factor is ≈5 bar, so the estimate is ~5× too low vs the actual cylinder draw.

This is a modelling limitation carried forward from the initial implementation. It means the Gas Plan tab (once BUG-45 is fixed) will still show underestimated diluent requirements for deep dives.

**Note:** This is a known simplification that other planners also use as a first approximation. Flagged here for awareness; the correct model would be `metRate / fO2 × (pAmb / p_surface)` integrated over the dive profile.

**Impact:** Diluent gas requirement displayed in Gas Plan will be substantially underestimated for dives deeper than ~20 m.

---

## C — LOW

### BUG-47 — `<meta name="description">` still references the OC app description

**File:** `index.html`  
**Location:** line 17

```html
<meta content="Professional dive planner with Rec NDL tables and Bühlmann ZH-L16C decompression algorithm." name="description"/>
```

This is the OC LSP D-Planner description, copied unchanged from the source repo. It does not mention CCR, pSCR, or rebreather planning. This affects PWA install metadata, Google search snippets, and link previews.

**Impact:** Cosmetic/SEO only. No functional effect.

---

### BUG-48 — `apple-mobile-web-app-title` is still `"D-Planner"` (not `"D-Planner+CCR"`)

**File:** `index.html`  
**Location:** line 14

```html
<meta content="D-Planner" name="apple-mobile-web-app-title"/>
```

The `manifest.json` correctly sets `"short_name": "D-Planner+CCR"` and the window `<title>` is `LSP D-Planner + CCR`. Only the iOS home screen title (Apple-specific meta tag) still reads `"D-Planner"`, matching the parent OC app.

**Impact:** On iOS, when the PWA is added to the home screen the icon label reads "D-Planner" instead of "D-Planner+CCR", making it indistinguishable from the OC version.

---

## D — LSP_D-planner (main, v2.20.21) — Carry-over bugs NOT yet back-ported

The following bugs were fixed in **CCR** (v2.30.9) but are **still present** in the main OC repo at v2.20.21.

| Bug | Status in CCR | Status in main OC |
|-----|--------------|-------------------|
| BUG-40 — Bühlmann emergency gas `sz` not converted from cu ft | ✅ Fixed (v2.30.9, line 10700) | ❌ Still present (line 9789 — `sz` = raw cu ft, not converted) |
| BUG-41 — `appSettings.clear()` removes wrong key (`v3` only) | ✅ Fixed (v2.30.9, removes v6+v3+v2+v1) | ❌ Still present (only removes `lspDiveSettings_v3`) |
| BUG-42 — `_restoreFields()` calls `checkAndRestore` twice per field | ⚠️ Still present in CCR too (line ~17456 `setTimeout(checkAndRestore, 100)`) | ❌ Still present (same pattern, line ~16442) |

**BUG-42 clarification:** Looking at the CCR code again, the double-restore pattern (`checkAndRestore()` immediate + `setTimeout(checkAndRestore, 100)`) is present in **both** repos at v2.30.9 and v2.20.21. It was reported fixed in v8 but the deferred second call is still there in both codebases.

---

## Summary Table

| # | Severity | Repo | Area | Description |
|---|----------|------|------|-------------|
| BUG-43 | HIGH | CCR | pSCR/CCR gas | `ccrDiluentSurfaceLpm()` and `computePSCRFractions()` fall back to 0.85 L/min metabolic O₂, DOM defaults 1.5 — 43% underestimate |
| BUG-44 | HIGH | CCR | pSCR validation | `validateCcrGasConfiguration()` uses `ccrBottomSetpoint` (hidden, stuck at 1.2) as ppO₂ limit in pSCR mode; should use `ppo2Bottom` |
| BUG-45 | MEDIUM | CCR | Gas Plan | Diluent cylinder in Gas Plan never cross-checked vs plan consumption in CCR/pSCR mode — `gpRequiredFor()` gets `null` due to label mismatch (`AIR` vs `CCR Air`) |
| BUG-46 | MEDIUM | CCR | Gas Plan | Diluent consumption modelled at surface-equivalent rate only — ignores depth scaling, underestimates by ~5× at 40 m |
| BUG-47 | LOW | CCR | Metadata | `<meta name="description">` still has OC description text — no mention of CCR/pSCR |
| BUG-48 | LOW | CCR | iOS PWA | `apple-mobile-web-app-title` is `"D-Planner"` not `"D-Planner+CCR"` |
| BUG-40 | HIGH | OC main | Gas plan/Imperial | Bühlmann emergency gas `sz` not converted cu ft → L (fixed in CCR, not back-ported to main) |
| BUG-41 | MEDIUM | OC main | Settings | `appSettings.clear()` removes only `v3` key — settings persist (fixed in CCR, not back-ported) |
| BUG-42 | LOW | Both | Settings/Perf | `_restoreFields()` fires `checkAndRestore` twice per field (immediate + 100ms setTimeout) — ~120 `change` events on every load |
