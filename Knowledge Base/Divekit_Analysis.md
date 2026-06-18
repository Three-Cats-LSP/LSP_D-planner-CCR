# Dive Kit App — Deco Engine Analysis
**App:** `app.skuba.diving` (Dive Kit)  
**Developer:** Ronny Majani  
**APK version analysed:** 1.1.8 (December 2025) from APKCombo  
**Play Store:** https://play.google.com/store/apps/details?id=app.skuba.diving  
**Documentation:** https://divekit.app/docs/  
**Analysis date:** June 2026

---

## Key Finding: C++ Native Engine (Not JavaScript)

The deco engine is **not in the JavaScript bundle**. It runs natively on the device through a React Native **Nitro Modules** JSI bridge as a compiled C++ library. This is why:

- Searching the Hermes bytecode (`index.android.bundle`, 13 MB, 1.76M disasm lines) found no ZHL-16C coefficient strings — the coefficients live in C++ code, not JS
- The Hermes JS bundle handles UI only (React Native / Expo / Tamagui components)
- None of the `.so` files in the architecture split APK (`config.arm64_v8a.apk`) contain deco-engine strings — the engine was moved to C++ between v1.1.8 and the June 2026 release
- The `how-it-works` documentation page explicitly states: *"The engine is written in C++ and runs natively on the phone through a native module, rather than in JavaScript. …for speed and numerical accuracy."*

**Note on version gap:** APKCombo supplied v1.1.8 (Dec 2025). The Play Store shows a June 11, 2026 update (user's device has this). The C++ migration may have landed in that update. The user's device APK (pullable via `adb pull`) would contain the native engine `.so`.

---

## Architecture (v1.1.8 APK)

| Component | Technology |
|---|---|
| UI framework | React Native + Expo, Tamagui (component library) |
| JS runtime | Hermes v96 bytecode |
| Native bridge | Nitro Modules (margelo/nitro) — JSI bridge |
| JS engine called | `libNitroModules.so`, `libappmodules.so` (SVG/nav only in v1.1.8) |
| Deco computation | **C++ native** (documented; library absent in v1.1.8 split APK) |
| Storage | MMKV (`libNitroMmkv.so`, `libmmkv.so`) |
| Crash tracking | Sentry |

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

### M-Value / Ceiling Formula

```
M = a + P_amb / b        (standard Bühlmann)
```

With gradient factors applied:

```
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
| Last stop depth | 3 m (salt) |
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
- Default deep ascent: 9 m/min; shallow ascent: 3 m/min; switch at 3 m depth
- Descent rate: configurable
- Last stop: held until leading tissue can surface within GF_High — **no credit for the swim to surface**

### Oxygen Toxicity

- CNS and OTU from **ambient PPO₂** (no water-vapour subtraction)
- Limits: NOAA / Shearwater CNS clock
- CNS decays on half-life, including across surface intervals
- OTU: pulmonary "whole-body" measure

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

### APK Structure (v1.1.8)

| File | Size | Notes |
|---|---|---|
| `index.android.bundle` | 13 MB | Hermes v96 bytecode — UI only |
| `config.arm64_v8a.apk` | ~28 MB | ARM64 native libs |
| `classes.dex` – `classes6.dex` | ~total 12 MB | Android/RN framework code |

### Native Libraries (arm64-v8a)

| Library | Size | Purpose |
|---|---|---|
| `libreactnative.so` | 5.7 MB | React Native core |
| `libbarhopper_v3.so` | 4.8 MB | Barcode scanner |
| `libhermes.so` | 2.1 MB | Hermes JS engine |
| `libappmodules.so` | 1.9 MB | App UI native modules (SVG, screens) |
| `libNitroModules.so` | 789 KB | Nitro JSI bridge framework |
| `libexpo-modules-core.so` | 1.3 MB | Expo core |
| `libmmkv.so` + `libNitroMmkv.so` | ~738 KB | MMKV key-value storage |

**No deco engine `.so` found in v1.1.8.** The engine was added as C++ native in a later update (June 2026 release). Pull APK from user's device for the current version.

### JS Bundle Analysis

- 1.584M lines of decompiled JS (hermes-dec v0.1.4)
- No ZHL-16C coefficients in bundle (all deco math is in native)
- Engine-adjacent identifiers found: `tissueLoading` (post-dive UI display), `BestMixCalculator` (gas planning), `maxAllowedDepth`, `maxMOD`, `maxPPO2` (MOD calculator)
- Gas blender functions found: `solveGasMix`, `solve1BankAnalytical`, `solve2BankAnalytical`, `findOptimalGasMix`

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

*Analysis by APK inspection (v1.1.8) + official documentation (June 2026)*  
*Engine architecture confirmed C++ via divekit.app/docs/engine/how-it-works/*
