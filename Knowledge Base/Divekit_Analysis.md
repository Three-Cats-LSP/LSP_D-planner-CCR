# Dive Kit App — Deco Engine Analysis
**App:** `app.skuba.diving` (Dive Kit)  
**Developer:** Ronny Majani / Lazuli Global  
**Play Store:** https://play.google.com/store/apps/details?id=app.skuba.diving  
**Documentation:** https://divekit.app/docs/  
**Analysis date:** June 2026

---

## Versions Analysed

| Version | Source | Build date | Notes |
|---|---|---|---|
| **1.1.8** | APKCombo (December 2025) | Dec 2025 | No `libDecoEngine.so` — C++ engine absent |
| **2.8.5** | User device APK (Dropbox) | **2026-06-11 23:43 UTC** | C++ engine present; `libDecoEngine.so` in split APK |

The v2.8.5 base APK was analysed directly. The architecture-specific split APK (`config.arm64_v8a.apk`) containing `libDecoEngine.so` was not included in the provided zip — it is downloaded separately by the Play Store at install time. The JS bundle (Hermes v98, 25 MB) and DEX files in the base APK were fully analysed.

---

## Key Finding: C++ Native Engine Confirmed via DEX Analysis

The `classes5.dex` in v2.8.5 contains the loader class `com.margelo.nitro.divekit.deco.DecoEngineOnLoad` with the literal call:

```java
System.loadLibrary("DecoEngine");
// → loads libDecoEngine.so from split APK at runtime
```

Log strings recovered from DEX:
- `"Loading DecoEngine C++ library..."`
- `"Successfully loaded DecoEngine C++ library!"`
- `"Failed to load DecoEngine C++ library! Is it properly installed and linked? Is the name correct? (see CMakeLists.txt, at add_library(...))"`

The React Native package class is `com.divekit.deco.DecoEnginePackage` (in `classes3.dex`).

---

## Architecture (v2.8.5)

| Component | Technology |
|---|---|
| UI framework | React Native 19.2.3 + Expo SDK 56.0.0 |
| JS runtime | Hermes **v98** bytecode (25 MB bundle, up from 13 MB in v1.1.8) |
| Native bridge | Nitro Modules (margelo/nitro) — JSI bridge |
| **Deco engine** | **`libDecoEngine.so`** — C++ native, Nitro HybridObject |
| Storage | MMKV via `libNitroMmkv.so` |
| Crash tracking | Sentry (`de.sentry.io`, project `divekit-app`, org `lazuli-global`) |
| React compiler | Experimental React Compiler enabled (`reactCompiler: true`) |

### Class Hierarchy

```
com.divekit.deco.DecoEnginePackage        (React Native package registration)
  └─ com.margelo.nitro.divekit.deco.DecoEngineOnLoad  (SO loader)
       └─ System.loadLibrary("DecoEngine")             (→ libDecoEngine.so)
```

The DecoEngine is a **Nitro HybridObject** — a C++ class registered via
`HybridObjectRegistry` and exposed to JavaScript via the Nitro JSI bridge.
JS calls it through `NitroModules` global proxy.

---

## JS Bundle Analysis (v2.8.5)

The Hermes v98 bundle contains the complete planner UI and settings schemas.
Key structures recovered from the disassembled bytecode:

### Default Settings Object (confirmed from bytecode literal)

```js
{
  gfLow: 50,
  gfHigh: 80,
  ascentRateDeep: 9,          // m/min
  ascentRateShallow: 3,       // m/min
  ascentRateChangeDepth: 6,   // m — switch depth between the two rates
  descentRate: 20,            // m/min
  lastStopDepth: 6,           // m (shown in settings schema; 3 m documented as minimum stop)
  decoStepSize: 3,            // m stop grid
  stopTimePrecision: 'roundMinutes',
  maxPO2Lean: 1.4,
  maxPO2Mid: 1.5,
  maxPO2Rich: 1.6,
  waterType: 'salt',
  workingRmv: 20,             // L/min
  decoRmv: 15,                // L/min
  ccrMetabolicO2Rate: 0.85,   // L/min
  gasSwitchTime: 0,           // min
  switchGasAtMod: true,
  treatO2AsNarcotic: false,
  stayOnLoop: true,
  airBreaksEnabled: false,
  airBreakPO2Threshold: 1.4,
  airBreakInterval: 20,       // min
  airBreakDuration: 5,        // min
  airBreaksOnCCR: false,
  includeTravelInLevelTime: false,
  maxENDWarning: 30,          // m
  gasDensityWarning: 5.2,     // g/L
  gasDensityCritical: 6.2,    // g/L
  cnsWarningThreshold: 80,    // %
  otuWarningThreshold: 300,   // OTU
  minPO2Warning: 0.18,        // bar
  ccrDefaults: null
}
```

### Plan Input Schema (confirmed from bytecode array literal)

All 31 fields that constitute a dive plan input to the engine:

```
mode, levels, gfLow, gfHigh, cylinders, ascentRateDeep, ascentRateShallow,
ascentRateChangeDepth, descentRate, lastStopDepth, decoStepSize,
stopTimePrecision, gasSwitchTime, switchGasAtMod, maxPO2Lean, maxPO2Mid,
maxPO2Rich, altitude, waterType, surfaceInterval, workingRmv, decoRmv,
treatO2AsNarcotic, airBreaksEnabled, airBreaksOnCCR, airBreakPO2Threshold,
airBreakInterval, airBreakDuration, includeTravelInLevelTime, maxENDWarning,
minPPO2, otuWarningThreshold, switchGasAtMod, treatO2AsNarcotic,
waterType, workingRmv, ccrMetabolicO2Rate, maxPO2Lean, maxPO2Mid, maxPO2Rich,
stopTimePrecision
```

### Tissue State Validation (from error string in string pool)

```
"Invalid tissue state from native engine: expected 16 compartments, got N2=..."
```

Confirms the C++ engine returns a tissue state object with **16 N₂ compartment values + 16 He compartment values** to JavaScript (for repetitive dive chaining and UI display).

### Other Engine-Related Strings in Bundle

- `"Native DecoEngine module not available. This requires a native build (not Expo Go)."` — fallback error if `.so` not loaded
- `"/(tabs)/manage/settings/deco-planner.ts"` — settings screen source path
- GF auto-raise: `"GF high raised to {{usedGfHigh}}"` — engine can automatically raise GF High when configured GF cannot produce a valid plan
- `"Your configured GF {{gfLow}}/{{requestedGfHigh}} cannot produce a valid plan. This export uses the closest GF that can: {{gfLow}}/{{usedGfHigh}}"` — export behaviour when GF is auto-raised

---

## Algorithm: Bühlmann ZH-L16C + Gradient Factors

### Model Identity

| Property | Value | Source |
|---|---|---|
| Model | Bühlmann ZH-L16C | [assumptions page](https://divekit.app/docs/engine/assumptions-and-limits/) |
| Variant | **C** (not A or B) | explicitly stated |
| Bubble model | None | stated explicitly |
| Deep-stop algorithm | None beyond GF Low implication | stated explicitly |
| Coefficient source | Bühlmann *Decompression: Decompression Sickness* | cited |
| GF method | Erik Baker's method, *"exactly as Baker's method specifies"* | [GF page](https://divekit.app/docs/engine/gradient-factors/) |

### Tissue Compartments

| Property | Value |
|---|---|
| Number of compartments | **16** |
| N₂ halftime range | ~4 min to **635 min** (fast → slow) |
| He halftime ratio | Roughly **2.65× faster** than N₂ (ratio of published ZHL-16C tables) |
| Gas tracking | N₂ and He tracked **separately** per compartment |
| Mixed gas | Continuously re-blended coefficients as mix changes |

*(Specific per-compartment halftimes and a/b coefficients are not published on the documentation site. They are ZH-L16C standard values identical to Subsurface, Abysner, and MultiDeco — see `Abysner_Analysis.md` for the full table.)*

### Integration

| Property | Value |
|---|---|
| Timestep | **1 second** |
| Equation | Haldane / Schreiner (standard dissolved-gas formula) |
| Scope | Every depth change, not only at fixed stops |

From JS bundle `formulaContent` string (Bühlmann help page):

```
P_tissue(t) = P₀ + (P_inspired - P₀) × (1 - e^(-k×t)) + (R × t - R/k) × (1 - e^(-k×t))

Where:
  P_tissue = tissue inert gas pressure after time t
  P₀       = initial tissue pressure
  P_inspired = inspired inert gas pressure
  k        = ln(2) / half-time (compartment constant)
  R        = rate of ambient pressure change
  t        = time
```

### M-Value / Ceiling Formula

```
M = a + P_amb / b        (standard Bühlmann)
```

With gradient factors applied (from bundle):

```
Ceiling = (P_tissue - M₀) / ΔM × 10     (shallowest depth where tissue ≤ M-value)

GF(depth) = GF_Low + (GF_High - GF_Low) × (depth_first_stop - depth) / depth_first_stop
ceiling_GF = a × GF + P_amb / b        (Baker-style scaled ceiling)
```

- GF interpolated **linearly with depth** from GF_Low at first stop to GF_High at surface
- "Gradient factors move the M-value ceiling, not the ambient line"
- Ceiling always **rounds up** (never shallower than true ceiling)

### Default Settings

| Setting | Default |
|---|---|
| GF Low | **50** |
| GF High | **80** |
| Stop grid | 3 m |
| Last stop depth | 6 m (in settings schema) / 3 m (documented minimum) |
| Stop time rounding | Whole minutes (default); precise MM'SS" opt-in |
| Minimum last stop | **1 minute** |
| Gas switch time | 0 minutes (default) |
| Water vapour | ~**0.0627 bar** (stated as "about 0.0627 bar") |
| Water vapour scope | Gas loading only — **never** the ceiling |
| Salt water | **10.000 m/bar** |
| Fresh water | 10.3 m/bar |
| EN13319 | 10.08 m/bar |
| Red Sea | 9.87 m/bar |
| Altitude | Configurable surface pressure |

### PPO₂ / Gas Switch Caps

| O₂% band | PPO₂ cap |
|---|---|
| Under 28% O₂ ("lean") | **1.4 bar** |
| 28% – under 45% O₂ ("mid") | **1.5 bar** |
| 45% and above O₂ ("rich") | **1.6 bar** |

Boundary: exactly 28% = mid; exactly 45% = rich. Gas-switch depth and hyperoxia warning both use the same band cap.

### Ascent Model

- **Two-rate model**: deep rate + shallow rate, switching at configurable depth
- Default deep ascent: **9 m/min**; shallow ascent: **3 m/min**; switch at **6 m** (from bytecode default object)
- Descent rate: **20 m/min** (default)
- Last stop: held until leading tissue can surface within GF_High — **no credit for the swim to surface**

### Oxygen Toxicity

- CNS and OTU from **ambient PPO₂** (no water-vapour subtraction)
- Limits: NOAA / Shearwater CNS clock
- CNS decays on half-life, including across surface intervals
- OTU: pulmonary "whole-body" measure
- CNS warning threshold: **80%** (default)
- OTU warning threshold: **300** (default)

### Air Breaks (CCR / Rich-O₂ Deco)

New in post-v1.1.8 releases (confirmed from settings schema):

| Setting | Default |
|---|---|
| Air breaks enabled | **false** |
| Air break PPO₂ threshold | 1.4 bar |
| Air break interval | 20 min |
| Air break duration | 5 min |
| Air breaks on CCR | false |

### CCR Support

| Feature | Detail |
|---|---|
| Setpoints | **3** (descent, bottom, deco) |
| Deco setpoint | Optional depth-keyed deco setpoint + diluent schedule |
| Setpoint cap | Capped at achievable ambient PPO₂ |
| Diluent slots | Up to 5 (Shearwater-style) |
| Bailout planning | From worst realistic failure point |

### Repetitive Dives

Tissue tension, CNS, and OTU carried across surface interval. Oxygen break re-loads fast tissues and that loading carries through the rest of the plan.

---

## Comparison vs MultiDeco (Published Cross-Reference)

DiveKit publishes a 26-scenario JSON dataset comparing its output to MultiDeco. Key documented divergences:

| Topic | Detail |
|---|---|
| Gas switch depths | EAN50 @ 21 m, O₂ @ 6 m — match exactly |
| Decozone start | Within ~one 3 m step on 25/26 scenarios |
| CNS/OTU and TTS | Within a few percent / few minutes on air/nitrox |
| Deep trimix first stop | May differ 1–4 steps — DiveKit documents continuous tissue recompute during ascent as He off-gasses faster than diver climbs |
| GF and decozone | Decozone is GF-independent (ambient crossing depth) — DiveKit and LSP v2.10.10+ agree on this |
| Integration timestep | DiveKit: 1 s; MultiDeco: coarser in places |
| Water vapour | DiveKit: 0.0627 bar; MultiDeco default: 0.0577 bar |

Cross-reference dataset files (local copies):

| File | Contents |
|---|---|
| `divekit-cross-reference/inputs.json` | 26 dive scenarios |
| `divekit-cross-reference/divekit-results.json` | DiveKit output per scenario |
| `divekit-cross-reference/multideco-results.json` | MultiDeco output per scenario |
| `divekit-cross-reference/notes.json` | Per-scenario commentary |

---

## APK Binary Analysis

### APK Structure

#### v1.1.8 (APKCombo, Dec 2025)

| File | Size | Notes |
|---|---|---|
| `index.android.bundle` | 13 MB | Hermes v96 bytecode — UI only |
| `config.arm64_v8a.apk` | ~28 MB | ARM64 native libs (no `libDecoEngine.so`) |
| `classes.dex` – `classes6.dex` | ~total 12 MB | Android/RN framework code |

#### v2.8.5 (User device, 2026-06-11)

| File | Size | Notes |
|---|---|---|
| `index.android.bundle` | **25 MB** | Hermes **v98** bytecode (was 13 MB in v1.1.8) |
| `classes.dex` – `classes7.dex` | 7 DEX files | One more DEX than v1.1.8; includes `DecoEngineOnLoad` and `DecoEnginePackage` classes |
| `config.arm64_v8a.apk` | not in zip | Contains `libDecoEngine.so` — distributed as separate split APK by Play Store |

### Native Libraries (v1.1.8, arm64-v8a — for reference)

| Library | Size | Purpose |
|---|---|---|
| `libreactnative.so` | 5.7 MB | React Native core |
| `libbarhopper_v3.so` | 4.8 MB | Barcode scanner |
| `libhermes.so` | 2.1 MB | Hermes JS engine |
| `libappmodules.so` | 1.9 MB | App UI native modules (SVG, screens) |
| `libNitroModules.so` | 789 KB | Nitro JSI bridge framework |
| `libexpo-modules-core.so` | 1.3 MB | Expo core |
| `libmmkv.so` + `libNitroMmkv.so` | ~738 KB | MMKV key-value storage |
| **`libDecoEngine.so`** | **absent** | **Added in post-v1.1.8 update** |

### v2.8.5 DEX: DecoEngine Loader (classes5.dex)

```java
// com.margelo.nitro.divekit.deco.DecoEngineOnLoad
public final void initializeNative() {
    if (DecoEngineOnLoad.didLoad) return;
    try {
        Log.i(TAG, "Loading DecoEngine C++ library...");
        System.loadLibrary("DecoEngine");  // ← libDecoEngine.so
        Log.i(TAG, "Successfully loaded DecoEngine C++ library!");
        DecoEngineOnLoad.didLoad = true;
    } catch (Error e) {
        Log.e(TAG, "Failed to load DecoEngine C++ library! ...", e);
        throw e;
    }
}
```

### JS Bundle Analysis (v2.8.5)

- Hermes v98 bytecode, 25 MB (hbc-disassembler used; full decompile not feasible — runs to 7+ GB)
- No ZHL-16C coefficients in bundle (all deco math is in C++ native)
- Default settings object embedded as bytecode literal (confirmed above)
- Tissue state validation: 16 N₂ + 16 He compartment values passed back to JS

---

## Comparison vs GUE DecPlanner

| Topic | GUE DecPlanner | Dive Kit |
|---|---|---|
| Architecture | Capacitor/Ionic web app, pure JS | React Native + C++ native module |
| Engine language | JavaScript (Decimal.js arbitrary precision) | C++ native (standard IEEE 754 double) |
| ZHL model | ZHL-16C | ZHL-16C |
| VPM-B | Yes (primary model) | No |
| Default GF | 20/85 (OC), 90/90 (bailout) | 50/80 |
| CCR | Yes | Yes |
| Air breaks | Yes | Yes (configurable) |
| Open source | Engine JS files extractable | Closed-source C++ |

---

## Comparison vs Abysner (Developer Fork)

Ronny Majani maintains `ronnymajani/Abysner` (a fork of `NeoTech-Software/Abysner`). Abysner is open-source Kotlin. Dive Kit is a separate, closed-source commercial app. They share algorithmic goals (ZHL-16C + GF) but Dive Kit's engine is independently written from the published Bühlmann papers and Baker equations — not ported from Abysner's Kotlin code.

---

## Notes for LSP D-Planner

1. **Water vapour (0.0627 bar):** DiveKit default. LSP defaults to 0.0577 (MultiDeco alignment). Make configurable.
2. **GF default 50/80:** DiveKit recreational default vs GUE's 20/85. LSP allows user to set.
3. **Decozone = GF-independent:** Both DiveKit and LSP v2.10.10+ agree — `ambientCrossingDepth(tissues)` not tied to `firstStopDepth`.
4. **1-second integration:** DiveKit and LSP both use 1 s. MultiDeco uses coarser steps → small RT/TTS differences expected.
5. **Cross-reference dataset:** Use `divekit-cross-reference/` for 3-way LSP vs MultiDeco vs DiveKit regression testing. Run after any ZHL+GF engine change.
6. **Coefficient table:** DiveKit uses standard ZH-L16C — same table as Abysner, Subsurface, MultiDeco, LSP. See `Abysner_Analysis.md` for verified a/b/halfTime tables.
7. **Air breaks:** DiveKit now supports configurable air breaks (disabled by default). Consider adding to LSP for completeness.
8. **Ascent rate change depth:** DiveKit default is **6 m** switch depth (confirmed from bytecode). LSP should verify this matches intended behaviour.
9. **GF auto-raise:** DiveKit silently raises GF High to the lowest value that produces a valid plan when the user's GF can't complete deco. LSP could add a similar guard/warning.

---

## References

- [Dive Kit documentation](https://divekit.app/docs/)
- [How the deco engine works](https://divekit.app/docs/engine/how-it-works/)
- [Gradient factors](https://divekit.app/docs/engine/gradient-factors/)
- [Design decisions](https://divekit.app/docs/engine/design-decisions/)
- [Assumptions and limits](https://divekit.app/docs/engine/assumptions-and-limits/)
- [Compared to MultiDeco](https://divekit.app/docs/engine/compared-to-multideco/)
- [Play Store listing](https://play.google.com/store/apps/details?id=app.skuba.diving)
- Cross-reference dataset: https://divekit.app/data/cross-reference/
- Erik Baker, "Understanding M-values" — GF method
- A. A. Bühlmann, *Decompression: Decompression Sickness* — ZH-L16C coefficients

---

*Analysis by APK inspection (v1.1.8 + v2.8.5) + official documentation (June 2026)*  
*Engine architecture confirmed via DEX class analysis (`libDecoEngine.so` via `System.loadLibrary`)*  
*v2.8.5 build date: 2026-06-11 23:43 UTC (commitTime: 1781221405060)*
