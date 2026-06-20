# LSP D-Planner + CCR — Errors & Bugs Report v7

**Repo:** `Three-Cats-LSP/LSP_D-planner-CCR`  
**Version analysed:** v2.30.1 (commit `51ae923`)  
**Date:** 2026-06-21  
**Audit result:** 271 checks, 0 failures  
**Scope:** Seventh verification pass. All 4 v6 bugs confirmed fixed. New findings below.

---

## MEDIUM

### BUG-37 — Emergency/contingency gas sufficiency wrong in imperial: cylinder size not converted cu ft → L

**File:** `index.html`  
**Location:** Emergency gas consumption block, lines ~10651–10656

```js
const sz  = parseFloat(document.getElementById(sId)?.value) || 0;  // cu ft in imperial, NOT converted
const prRaw = parseFloat(document.getElementById(pId)?.value) || 0;
const pr = units === 'imperial' ? prRaw / 14.5038 : prRaw;  // correctly converted to bar
if (sz > 0 && pr > 0) cylCapacity[label] = sz * pr;         // cu_ft × bar — WRONG
```

In imperial mode `sz` holds cu ft (value already converted from litres by `convertNumericInput`). It should be multiplied by `28.3168` to get litres before computing capacity. The main Gas Plan tab (`calcGasPlan()`) correctly uses `gpSizeL()` which divides the displayed cu ft by `GP_CUFT_PER_L`. The emergency/contingency path uses the raw input value with no such conversion.

**Impact:** In imperial mode, the emergency gas consumption table (shown when running the contingency/+3m/+5m scenario) calculates available gas as `cu_ft × bar` instead of `L × bar`. The required gas `reqL` is always in litres. This produces nonsensical sufficiency comparisons — typically showing dramatically undersized available gas, since e.g. 42 cu ft × 200 bar = 8400 vs the correct 1189 L × 200 bar = 237,831 L-bar available. Sufficiency column will almost always show "insufficient" for all gases in imperial.

---

### BUG-38 — `getBailoutReserveMixLabel()` uses `ccrBottomSetpoint` (1.2) for diluent-as-bailout MOD instead of OC ppO₂ limit (1.4)

**File:** `index.html`  
**Location:** `getBailoutReserveMixLabel()` lines ~6025–6030

```js
const activePpo2 = parseFloat(document.getElementById('ccrBottomSetpoint')?.value)
  || parseFloat(document.getElementById('ppo2Bottom')?.value) || 1.4;
if (calcGasMODm(fO2Bot, activePpo2) >= depthM - 0.01) {
  return getGasLabel(fO2Bot, fHeBot);  // diluent used as bailout reserve
}
```

When the diver bails out from CCR to OC, they breathe the diluent as an OC gas. The MOD check should use the OC ppO₂ limit (`getBailoutPpo2Limit()` → `ppo2Bottom` = 1.4 bar), not the on-loop bottom setpoint (1.2 bar).

**Example:** Air diluent (21% O₂): MOD at 1.2 = 47 m; MOD at 1.4 = 57 m. Both cover a 40 m dive so this is fine in that case. But for a richer diluent — e.g. 36% O₂: MOD at 1.2 = 23 m, MOD at 1.4 = 29 m — a 25 m dive with 36% diluent would be excluded as a reserve gas at 1.2 bar ppO₂ limit when it is actually breathable at 1.4. The stress/reserve calculation silently assigns `null` and no reserve gas is added.

**Note:** `validateCcrGasConfiguration()` has the same pattern at line ~6043 for the diluent MOD validation, but in that context the question is whether the diluent is safe on-loop at the bottom setpoint — which IS correct there. The reserve mix function is a different question (OC bailout MOD), hence the bug.

---

## LOW

### BUG-39 — Version mismatch: `APP_VERSION` / `sw.js` bumped to `2.30.1`, `package.json` and `android/app/build.gradle` still `2.30.0`

**Files:** `package.json` line 3, `android/app/build.gradle` lines 10–11

| File | Value |
|---|---|
| `index.html` `APP_VERSION` | `2.30.1` ✓ |
| `sw.js` `CACHE_VERSION` | `lsp-dplanner-ccr-v2.30.1` ✓ |
| `package.json` `version` | `2.30.0` ✗ |
| `android/app/build.gradle` `versionName` | `2.30.0` ✗ |
| `android/app/build.gradle` `versionCode` | `23000` ✗ |

**Impact:** APK built from this tag will report v2.30.0 while the web app reports v2.30.1. Repeat of BUG-01 pattern.

---

## Summary Table

| # | Severity | Area | Description |
|---|---|---|---|
| BUG-37 | MEDIUM | Gas plan/Imperial | Emergency gas plan: cylinder size not converted cu ft → L in imperial — sufficiency always wrong |
| BUG-38 | MEDIUM | CCR/Gas reserve | `getBailoutReserveMixLabel` uses on-loop SP (1.2) not OC ppO₂ limit (1.4) for diluent-as-bailout MOD |
| BUG-39 | LOW | Versioning | `package.json` and `build.gradle` still `2.30.0` after version bump to `2.30.1` |

