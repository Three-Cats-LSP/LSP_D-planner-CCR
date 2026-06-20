# LSP D-Planner + CCR — Errors & Bugs Report v6

**Repo:** `Three-Cats-LSP/LSP_D-planner-CCR`  
**Version analysed:** v2.30.0 post-fix-5 (commit `491d83a`)  
**Date:** 2026-06-20  
**Audit result:** 271 checks, 0 failures  
**Scope:** Sixth verification pass. All 6 v5 bugs confirmed fixed. New findings below.

---

## HIGH

### BUG-33 — VPM cylinder label lookup uses wrong DOM IDs (`decoGas1Mix`/`decoGas2Mix`) — deco gas cylinders never matched in VPM gas plan

**File:** `index.html`  
**Location:** VPM gas consumption block, lines ~7423–7424

```js
{ ids: ['cylDg1_size','cylDg1_pres','cylDg1_reserve'],
  label: (getDecoGasLabel('decoGas1Mix', 'decoGas1Custom') || null) },
{ ids: ['cylDg2_size','cylDg2_pres','cylDg2_reserve'],
  label: (getDecoGasLabel('decoGas2Mix', 'decoGas2Custom') || null) },
```

The actual deco gas card select IDs are `dg1Mix` / `dg2Mix` (and custom O₂ fields `dg1CustomO2` / `dg2CustomO2`). The IDs `decoGas1Mix` and `decoGas2Mix` do not exist in the DOM — `getElementById()` returns `null` → `getDecoGasLabel()` returns `null` → both cylinder defs always get `label: null` → they are never matched to any consumed gas.

**Impact:** In VPM mode, deco gas cylinder 1 and cylinder 2 always show no data in the gas plan — available volume, turn pressure, and sufficiency status are blank regardless of what the user enters. Only the bottom gas (cylinder 0) is correctly mapped. This affects every CCR and OC dive planned with VPM-B or VPM-B+GFS.

**Fix:** Change `'decoGas1Mix'` → `'dg1Mix'`, `'decoGas1Custom'` → `'dg1CustomO2'`, `'decoGas2Mix'` → `'dg2Mix'`, `'decoGas2Custom'` → `'dg2CustomO2'`.

---

### BUG-34 — Stress/problem-solve reserve gas uses `mixes[0]` without checking if it covers dive depth

**File:** `index.html`  
**Location:** Gas consumption block, lines ~10392–10401

```js
const mixes = getConfiguredBailoutMixes();  // unsorted, unfiltered by depth
const reserveLabel = mixes.length ? mixes[0].label : ...;
if (reserveLabel) {
  addGas(reserveLabel, rawD, reserveMin, _ccrSettings.sacStress || sacBottom);
}
```

`getConfiguredBailoutMixes()` returns all configured bailout mixes in DOM order, with no filtering by dive depth. `mixes[0]` is the first gas card's mix regardless of its MOD.

**Example:** Gas card 1 = EAN50 (MOD 18 m), gas card 2 = EAN32 (MOD 30 m), dive depth = 40 m. `mixes[0]` = EAN50. The reserve is added as EAN50 at 40 m — a gas that cannot be breathed at that depth. The diver should be carrying the deepest-capable bailout mix (EAN32) as the reserve, not EAN50.

**Note:** `validateCcrGasConfiguration()` correctly filters by depth (checking `bailoutAtDepth.length === 0`) but the reserve selection does not apply this filter.

**Impact:** Gas plan shows reserve volume attributed to the wrong (shallowest MOD) bailout gas. For dives deeper than mixes[0].modM this produces a misleading reserve figure.

---

## MEDIUM

### BUG-35 — VPM gas consumption does not apply `sacDecoCcr` for OC bailout deco gases (inconsistent with Bühlmann path)

**File:** `index.html`  
**Location:** VPM gas consumption block, line ~7393

```js
const sac = (ph === 'bottom') ? sacBotVPM : sacDecoVPM;   // always UI sacDeco, no CCR override
gasConsVPM[gasKey] = (gasConsVPM[gasKey] || 0) + ccrGasLitres(gasKey, depthM2, durMin, sac);
```

The Bühlmann path uses `resolveSacForGas()` which substitutes `_ccrSettings.sacDecoCcr` for OC deco gases on a CCR dive. The VPM path uses `sacDecoVPM` (the main SAC deco field) unconditionally — `sacDecoCcr` is ignored.

**Impact:** On a CCR dive with VPM-B, deco gas consumption is estimated using the general deco SAC instead of the CCR-specific deco SAC. If a user sets a different `ccrSacDeco`, the VPM gas plan will not reflect it.

---

### BUG-36 — VPM gas plan has no stress/problem-solve bailout reserve (Bühlmann path has it, VPM does not)

**File:** `index.html`  
**Location:** VPM gas consumption block (~lines 7378–7395)

The Bühlmann path (lines ~10392–10401) adds a gas reserve for `stressTimeMin + problemSolveMin` at `sacStress` to the first (deepest-capable) bailout mix. This reserve does not exist in the VPM gas consumption block at all.

**Impact:** On a CCR dive with VPM-B, the gas plan never includes the stress/problem-solve bailout reserve regardless of the configured values. The Bühlmann and VPM gas plans produce different total gas requirements for the same dive and settings, with VPM always underestimating the required bailout volume.

---

## Summary Table

| # | Severity | Area | Description |
|---|---|---|---|
| BUG-33 | HIGH | VPM/Gas plan | VPM deco gas cylinder lookup uses wrong DOM IDs — cyl 1 & 2 always blank in gas plan |
| BUG-34 | HIGH | Gas plan | Stress/reserve gas picks `mixes[0]` without depth check — may assign reserve to a gas not breathable at dive depth |
| BUG-35 | MEDIUM | VPM/Gas plan | VPM gas consumption ignores `sacDecoCcr` for bailout deco gases — inconsistent with Bühlmann path |
| BUG-36 | MEDIUM | VPM/Gas plan | VPM gas plan has no stress/problem-solve bailout reserve — Bühlmann and VPM gas plans diverge |

