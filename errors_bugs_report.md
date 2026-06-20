# LSP D-Planner + CCR — Errors & Bugs Report

**Repo:** `Three-Cats-LSP/LSP_D-planner-CCR`  
**Version analysed:** v2.30.0 (commit `d8ddf2e`)  
**Date:** 2026-06-20  
**Audit result:** 271 checks, 0 failures (audit.py passes — these are logic/consistency bugs not covered by audit)

---

## CRITICAL

### BUG-01 — Android `versionCode`/`versionName` not updated for v2.30.0

**File:** `android/app/build.gradle` lines 10–11  
**Finding:**
```
versionCode 21012
versionName "2.10.12"
```
**Expected:** `versionCode 23000`, `versionName "2.30.0"` (matching `APP_VERSION = '2.30.0'` and `package.json "version": "2.30.0"`).  
**Impact:** APK built from this repo will self-identify as v2.10.12. Android Play Store / sideload version tracking is broken. The shipped APK file is named `LSP_D-planner-CCR.apk` v2.30.0 but the manifest inside the APK says v2.10.12.

**Versions across files:**

| File | Value |
|---|---|
| `index.html` `APP_VERSION` | `2.30.0` ✓ |
| `package.json` `version` | `2.30.0` ✓ |
| `android/app/build.gradle` `versionName` | `2.10.12` ✗ |
| `android/app/build.gradle` `versionCode` | `21012` ✗ |
| `index.html` `<p id="appVersionLabel">` (static HTML, line 3301) | `Version 2.10.12` ✗ (stale hardcoded fallback — overwritten at runtime by JS on line 17422, but visible in raw HTML) |

---

### BUG-02 — Android `compileSdkVersion`/`targetSdkVersion`/`minSdkVersion` regressed vs main LSP D-Planner

**File:** `android/variables.gradle`  
**Finding:**
```
minSdkVersion = 22
compileSdkVersion = 34
targetSdkVersion = 34
```
**Main LSP D-Planner (v2.10.0+):** `minSdk 21`, `compileSdk 35`, `targetSdk 35`.  
**Impact:** CCR variant targets API 34, main variant targets API 35 — inconsistency between sibling products. Android 15 (API 35) edge-to-edge behaviour and `WindowCompat` flags that the main repo depends on may not be applied correctly. Also `minSdkVersion=22` is more restrictive than necessary (main uses 21).

---

## HIGH

### BUG-03 — CCR ppO₂ column in Bühlmann deco table shows diluent ppO₂, not setpoint

**File:** `index.html`  
**Location:** `ppO2Check()` (line 6647) called at lines 9528, 9568, 9602 for CCR on-loop stop rows.  
**Finding:** `ppO2Check(depthM, fN2, fHe)` always computes `fO2 × P_amb` using the diluent gas fractions. When a deco stop is on-loop (`onLoop=true`), `stopFN2=bottomFN2`, `stopFHe=bottomFHe`, so the ppO₂ column displays the diluent's partial pressure rather than the maintained setpoint.  
**Example:** 40 m stop on CCR with SP 1.3 and air diluent → `ppO2Check` returns `≈ 1.07 bar` (air ppO₂ at 40 m) instead of `1.3 bar` (setpoint).  
**Impact:** Misleading ppO₂ display — user sees lower-than-actual O₂ exposure. The same `pO2` value propagates to text export, PDF, and gas switch decision logging.

---

### BUG-04 — `_scrRuntimeMin` never assigned in VPM engine path → pSCR O₂ consumption always 0

**File:** `index.html`  
**Location:** VPM engine internal functions (lines 7545, 7574, 7701, 7748, 8177): `scrRuntimeMin: settings._scrRuntimeMin || 0`  
**Finding:** `settings._scrRuntimeMin` is never set anywhere in the codebase. `getCCRSettingsFromDOM()` does not return `_scrRuntimeMin`. Searching the entire file confirms no assignment.  
**Impact:** In VPM-B/VPM-B+GFS mode, `computePSCRFractions()` always receives `runtimeMin = 0`, meaning zero O₂ is consumed from the loop regardless of dive duration. The pSCR inspired gas fractions are identical to fresh-gas fractions for the entire dive — pSCR mode is effectively broken in the VPM path.  
**Note:** Bühlmann path correctly passes `rt` (running time in minutes) at lines 9175 and 9181, so this bug is VPM-only.

---

### BUG-05 — `sw.js` still references `/LSP_D-planner/` paths, not `/LSP_D-planner-CCR/`

**File:** `sw.js` lines 28, 81, 94  
**Finding:**
```js
'/LSP_D-planner/index.html'          // line 28 — install cache
'/LSP_D-planner/index.html'          // line 81 — fallback fetch
url.pathname.startsWith('/LSP_D-planner/')  // line 94 — cache update guard
```
The `CACHE_VERSION` on line 5 is correctly `lsp-dplanner-ccr-v2.30.0`, but the path constants still point to the original OC planner's GitHub Pages path.  
**Impact:** PWA offline caching will fail. On first install the service worker caches the wrong URL, and the cache-update guard on line 94 will never fire for any request under `/LSP_D-planner-CCR/`. The app will not work offline.

---

## MEDIUM

### BUG-06 — `getEffectiveSetpointAtDepth()` called without `surfP` in several Bühlmann-path locations → altitude dives use wrong setpoint crossover depth

**File:** `index.html`  
**Locations:**
- Line 5671 (inside `getEffectivePpo2`): `getEffectiveSetpointAtDepth(..., cfg)` — no `surfP`  
- Line 5713 (inside `saturateCCR`): `getEffectiveSetpointAtDepth(depthM, cfg)` — no `surfP`  
- Line 9169 (Bühlmann main path): `getEffectiveSetpointAtDepth(depthM, _ccrSettings)` — no `surfP`  

**Finding:** The function signature is `getEffectiveSetpointAtDepth(depthM, ccr, surfP)`. When `surfP` is omitted it falls back to `altSurfaceP` — which is only correct if the global has already been set. In headless/test contexts (`document` absent) `altSurfaceP` may be the sea-level default regardless of the dive's altitude parameter.  
**Impact:** At altitude, setpoint crossover depth is calculated against sea-level surface pressure, making the descent-SP window slightly wrong. Not catastrophic but produces incorrect tissue loading during the descent phase on altitude dives.

---

### BUG-07 — pSCR loop initialisation uses `fHe` from outer scope incorrectly inside `getEffectivePpo2`

**File:** `index.html` line 5668  
**Finding:**
```js
const fr = computePSCRFractions(pAmb, fO2, 1 - fO2 - (ccr.fHe || 0), cfg.scrRuntimeMin, cfg);
```
`fHe` is derived as `1 - fO2 - (ccr.fHe || 0)` — this treats `ccr.fHe` as the He fraction. But `ccr` here is the settings/config object, not a gas object; `ccr.fHe` is not a defined field anywhere in `getCCRSettingsFromDOM()` or `mergeCCRSettings()`. It will always resolve to `0`.  
**Impact:** For Trimix diluent pSCR dives, He content is ignored in `getEffectivePpo2`, so the diluent fO₂ computed for loop O₂ bookkeeping is incorrect (N₂ absorbs the He fraction). Tissue loading via `getInspiredInertPressures` uses the correct He fractions because it receives explicit `fHe` parameters — but the ppO₂ display and loop-state calculations via `getEffectivePpo2` will be wrong.

---

### BUG-08 — CNS calculator tab does not account for CCR setpoint — computes OC ppO₂

**File:** `index.html` `calcCNS()` function (line 15289)  
**Finding:** The standalone CNS tab always computes `ppo2 = P_amb × fO₂`. There is no CCR setpoint integration. On a CCR dive the actual ppO₂ exposure is the setpoint (e.g. 1.3 bar), but if the user enters the diluent O₂% (e.g. 21% air) the tab shows `~1.07 bar` at 40 m instead of 1.3 bar.  
**Impact:** User gets a false-low CNS/OTU estimate from the CNS tab when on CCR. There is no documentation warning on the tab that it is OC-only. The main deco schedule output does correctly track CCR CNS (via `calculateCNS(ppO2Stop, stopTime)` in the engine), but the standalone CNS tab is disconnected from CCR logic.

---

### BUG-09 — `tests-massive-main.html` contains zero CCR tests; `tests-extended.html` contains zero CCR tests

**File:** `tests-massive-main.html`, `tests-extended.html`  
**Finding:**  
- `tests-massive-main.html` (372 tests): 0 CCR/pSCR references  
- `tests-extended.html` (1082 lines): 0 CCR/pSCR references  
- `tests-verify.html`: 6 CCR tests (Section I) — only covers ZHL path + one VPM smoke test  
- `tests-massive.html`: 8 CCR cross-val tests (Section T3-CCR) against MultiDeco references  

**Impact:** Core new functionality (pSCR, bailout, descent setpoint, VPM CCR, altitude CCR, trimix CCR) has very thin test coverage. Regressions in CCR tissue-loading logic will not be caught by the existing suites.

---

## LOW / COSMETIC

### BUG-10 — `manifest.json` missing 512×512 icon

**File:** `manifest.json`  
**Finding:** Only one icon entry (`icon-192.png` at 192×192, declared twice with `purpose: "any"` and `purpose: "maskable"`). No 512×512 icon.  
**Impact:** Chrome/Android PWA install banner will show a warning; Google Play Store requires a 512×512 icon for proper listing.

---

### BUG-11 — `download.html` logo `alt` text still reads "LSP D-Planner" not "LSP D-Planner + CCR"

**File:** `download.html` line 50  
**Finding:** `<img alt="LSP D-Planner" ...>` — missing `+ CCR` suffix.  
**Impact:** Minor accessibility/branding inconsistency.

---

### BUG-12 — `tests-extended.html` and `tests.html` page titles not updated for CCR variant

**File:** `tests-extended.html` line 4, `tests.html`  
**Finding:** `<title>LSP D-Planner — Extended Algorithm Test Suite</title>` — no CCR branding.  
**Impact:** Cosmetic only.

---

## Summary Table

| # | Severity | Area | Description |
|---|---|---|---|
| BUG-01 | CRITICAL | Android | `versionCode`/`versionName` still `2.10.12` in build.gradle |
| BUG-02 | CRITICAL | Android | SDK versions regressed vs main (API 34 vs 35, minSdk 22 vs 21) |
| BUG-03 | HIGH | CCR/Display | Deco table ppO₂ column shows diluent ppO₂ not setpoint on CCR stops |
| BUG-04 | HIGH | pSCR/VPM | `_scrRuntimeMin` never assigned → pSCR O₂ consumption = 0 in VPM path |
| BUG-05 | HIGH | PWA | `sw.js` caches `/LSP_D-planner/` paths → offline mode broken |
| BUG-06 | MEDIUM | CCR/Altitude | `getEffectiveSetpointAtDepth` called without `surfP` in 3 locations |
| BUG-07 | MEDIUM | pSCR/Trimix | `ccr.fHe` not a valid field → Trimix diluent He ignored in pSCR ppO₂ |
| BUG-08 | MEDIUM | CCR/CNS | CNS tab computes OC ppO₂ only — no CCR setpoint integration |
| BUG-09 | MEDIUM | Testing | Near-zero CCR test coverage in main test suites |
| BUG-10 | LOW | PWA | No 512×512 icon in manifest |
| BUG-11 | LOW | Branding | `download.html` alt text still "LSP D-Planner" not "+ CCR" |
| BUG-12 | LOW | Branding | Test page titles not updated for CCR variant |

