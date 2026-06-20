# LSP D-Planner + CCR — Errors & Bugs Report v4

**Repo:** `Three-Cats-LSP/LSP_D-planner-CCR`  
**Version analysed:** v2.30.0 post-fix-3 (commit `395cecb`)  
**Date:** 2026-06-20  
**Audit result:** 271 checks, 0 failures  
**Scope:** Fourth verification pass. All 4 bugs from report v3 confirmed fixed. New findings below.

---

## HIGH

### BUG-23 — Dive graph ceiling overlay uses OC tissue loading for CCR dives (descent phase always wrong; deco phase wrong for intermediate samples)

**File:** `index.html`  
**Location:** Ceiling waypoints block, lines ~9763, ~9799–9806 (Phase 1 descent and Phase 3 deco intermediate samples)

**Phase 1 — descent** (line ~9763):
```js
const tis = saturateLinear([...initTissues()], 0, partDepth, partDur, bottomFN2, bottomFHe);
```
Uses OC `saturateLinear()` — ignores CCR setpoint. For a CCR dive the diver is on-loop during descent; inert loading is driven by `pAmb − setpoint − WV`, which is significantly lower than OC. The graph shows a higher/earlier ceiling during descent than is physically correct.

**Phase 3 — deco intermediate samples** (lines ~9799, 9801, 9803, 9805):
```js
saturateLinear([...cTissues2], s.from, s.to, partDur, s.fN2 || bottomFN2, ...)
saturate([...cTissues2], s.depth || 0, partDur, s.fN2 || bottomFN2, ...)
```
Again OC loading for intra-stop samples. Starting tissue state (`cTissues2`) is correctly carried from the CCR deco schedule, but each intermediate step loads OC gas — diverging progressively through the deco.

**Impact:** The ceiling curve on the dive graph is inaccurate for CCR dives. The discrepancy between the displayed ceiling and the actual deco stops (which are correctly computed) is visible to the user and could cause confusion or loss of trust.

**Note:** `tissuesAtBottom` (Phase 2 boundary, line ~9775) IS computed with CCR loading (`zhlLoadConst` with `_zhlOnLoop=true`), so the graph is correct at that snapshot point only.

---

## MEDIUM

### BUG-24 — Multi Dive Day Plan tab uses OC air tissue loading — misleading for CCR divers

**File:** `index.html`  
**Location:** `runUnifiedPlan()` lines ~10833–10857  
```js
const fN2 = FN2_AIR;
// ...
testT = saturate(testT, dM, 1, fN2);  // always OC air
tissues = saturate(tissues, dM, bt, fN2);  // always OC air
```
The multi-dive NDL planner hardcodes `FN2_AIR` and uses OC `saturate()` regardless of the selected circuit. For a CCR diver the actual inert gas loading (and therefore NDL) is completely different from air OC, yet the tab will show air-OC NDL values.  
**No disclaimer** on the tab states it is OC-only.  
**Impact:** CCR diver uses the multi-dive planner and sees NDL/margin estimates that do not reflect their actual on-loop tissue loading. Could lead to inadequate surface intervals or overconfident repeat dives.

---

### BUG-25 — pSCR circuit shows CCR setpoint and descent setpoint UI fields that are unused for pSCR

**File:** `index.html`  
**Location:** `toggleCircuitFields()` line ~5766  
```js
['ccrSetpointRow', 'ccrDescentSetpointRow', 'ccrBailoutRow'].forEach(id => {
  el.style.display = isRB ? '' : 'none';  // isRB = any rebreather incl. pSCR
});
```
When circuit is `pSCR`, both `ccrSetpointRow` (high setpoint) and `ccrDescentSetpointRow` (descent setpoint) are shown. These fields feed `getEffectiveSetpointAtDepth()`, which returns `0` for pSCR (`if (ccr.circuit === 'pSCR') return 0`). The visible setpoint inputs have no effect on the pSCR calculation.  
**Impact:** UI confusion — user adjusting the setpoint on pSCR mode believes it affects the plan, but it has no effect. No tooltip or label explains this.

---

### BUG-26 — Multi Dive export text says `LSP D-PLANNER - MULTI DIVE DAY PLAN` — missing `+ CCR`

**File:** `index.html` line ~13863  
```js
lines.push('LSP D-PLANNER - MULTI DIVE DAY PLAN');
```
**Impact:** Minor branding inconsistency in the multi-dive text export. Consistent with the pattern of missed `+ CCR` suffixes fixed in prior reports.

---

## Summary Table

| # | Severity | Area | Description |
|---|---|---|---|
| BUG-23 | HIGH | CCR/Graph | Dive graph ceiling overlay uses OC tissue loading — wrong for CCR descent and deco intermediate samples |
| BUG-24 | MEDIUM | CCR/Multi-dive | Multi Dive tab uses hardcoded OC air loading — NDL values meaningless for CCR divers, no disclaimer |
| BUG-25 | MEDIUM | pSCR/UX | pSCR circuit shows setpoint UI fields that have zero effect on pSCR calculation |
| BUG-26 | LOW | Branding | Multi Dive export header missing `+ CCR` |

