# CCR Engine Differential Report

**Generated:** 2026-06-22 07:24 UTC  
**LSP version:** 2.30.31  
**Scenarios:** 17  
**Failures:** 0  
**Inconclusive:** 45  

---

## CCR-C1 — Air diluent baseline

- **LSP:** RT 47 min · first stop 12 m · TTS 18.8
- **MultiDeco:** `PASS` 
- **DiveKit:** `PASS` 
- **DiveProMe:** `INCONCLUSIVE` pinned commit 87741d22 — vendor adapter not vendored in CI; DiveKit captures used as open-source reference
- **Metamorphic:** depth↑ → RT not shorter ✓, GF high↓ → RT not shorter ✓, deterministic repeat ✓

## CCR-C2 — Tx18/45 trimix

- **LSP:** RT 62 min · first stop 24 m · TTS 40.3
- **MultiDeco:** `EXPECTED_DIFFERENCE` runtimeMin Δ7; ttsMin Δ3.700000000000003
- **DiveKit:** `EXPECTED_DIFFERENCE` ttsMin Δ3.1000000000000014
- **DiveProMe:** `INCONCLUSIVE` pinned commit 87741d22 — vendor adapter not vendored in CI; DiveKit captures used as open-source reference

## CCR-C3 — Tx12/60 deep trimix

- **LSP:** RT 81 min · first stop 36 m · TTS 65.4
- **MultiDeco:** `EXPECTED_DIFFERENCE` firstStopDepthM Δ9; runtimeMin Δ17; ttsMin Δ12.599999999999994
- **DiveKit:** `EXPECTED_DIFFERENCE` runtimeMin Δ16; ttsMin Δ11.799999999999997
- **DiveProMe:** `INCONCLUSIVE` pinned commit 87741d22 — vendor adapter not vendored in CI; DiveKit captures used as open-source reference

## CCR-NDL — Shallow no-decompression CCR

- **LSP:** RT 26 min · first stop 0 m · TTS 5.7
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **DiveProMe:** `INCONCLUSIVE` pinned commit 87741d22 — vendor adapter not vendored in CI; DiveKit captures used as open-source reference

## CCR-SP — Distinct descent/bottom/deco setpoints

- **LSP:** RT 50 min · first stop 12 m · TTS 21.6
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **DiveProMe:** `INCONCLUSIVE` pinned commit 87741d22 — vendor adapter not vendored in CI; DiveKit captures used as open-source reference

## CCR-ML — Tx18/45 multilevel

- **LSP:** RT 64 min · first stop 27 m · TTS 44.3
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **DiveProMe:** `INCONCLUSIVE` pinned commit 87741d22 — vendor adapter not vendored in CI; DiveKit captures used as open-source reference

## CCR-GF-A — GF 50/80 sensitivity (C1 profile)

- **LSP:** RT 47 min · first stop 12 m · TTS 18.8
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **DiveProMe:** `INCONCLUSIVE` pinned commit 87741d22 — vendor adapter not vendored in CI; DiveKit captures used as open-source reference

## CCR-GF-B — GF 50/50 sensitivity (C1 profile)

- **LSP:** RT 56 min · first stop 12 m · TTS 27.8
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **DiveProMe:** `INCONCLUSIVE` pinned commit 87741d22 — vendor adapter not vendored in CI; DiveKit captures used as open-source reference

## CCR-LAST-A — Last stop 3 m (C1 profile)

- **LSP:** RT 47 min · first stop 12 m · TTS 18.8
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **DiveProMe:** `INCONCLUSIVE` pinned commit 87741d22 — vendor adapter not vendored in CI; DiveKit captures used as open-source reference

## CCR-LAST-B — Last stop 6 m (C1 profile)

- **LSP:** RT 49 min · first stop 12 m · TTS 20.8
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **DiveProMe:** `INCONCLUSIVE` pinned commit 87741d22 — vendor adapter not vendored in CI; DiveKit captures used as open-source reference

## CCR-BO — Planned bailout to OC

- **LSP:** RT 55 min · first stop 18 m · TTS 27
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **DiveProMe:** `INCONCLUSIVE` pinned commit 87741d22 — vendor adapter not vendored in CI; DiveKit captures used as open-source reference

## CCR-LOST-GAS — Bailout with EAN50 unavailable

- **LSP:** RT 65 min · first stop 18 m · TTS 37
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **DiveProMe:** `INCONCLUSIVE` pinned commit 87741d22 — vendor adapter not vendored in CI; DiveKit captures used as open-source reference

## CCR-REP — Repetitive dive — 60 min surface interval

- **LSP:** RT 47 min · first stop 12 m · TTS 18.8
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **DiveProMe:** `INCONCLUSIVE` pinned commit 87741d22 — vendor adapter not vendored in CI; DiveKit captures used as open-source reference

## CCR-ALT — Acclimatized dive at 1500 m

- **LSP:** RT 47 min · first stop 12 m · TTS 18.8
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **DiveProMe:** `INCONCLUSIVE` pinned commit 87741d22 — vendor adapter not vendored in CI; DiveKit captures used as open-source reference

## CCR-PRECISE-A — One-second minimum stops

- **LSP:** RT 47 min · first stop 12 m · TTS 18.8
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **DiveProMe:** `INCONCLUSIVE` pinned commit 87741d22 — vendor adapter not vendored in CI; DiveKit captures used as open-source reference

## CCR-PRECISE-B — Whole-minute stop rounding

- **LSP:** RT 47 min · first stop 12 m · TTS 18.8
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **DiveProMe:** `INCONCLUSIVE` pinned commit 87741d22 — vendor adapter not vendored in CI; DiveKit captures used as open-source reference

## CCR-INVALID — Invalid setpoint and diluent fractions

- **LSP:** RT 36 min · first stop 3 m · TTS 7.9
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **DiveProMe:** `INCONCLUSIVE` pinned commit 87741d22 — vendor adapter not vendored in CI; DiveKit captures used as open-source reference

---

See [CCR_ENGINE_DIFFERENTIAL_TEST_PLAN.md](CCR_ENGINE_DIFFERENTIAL_TEST_PLAN.md) for methodology.

## Documented LSP defects (tracked, not CI-blocking)

- **CCR-DEFECT-INVALID-SETPOINT** (CCR-INVALID): Engine accepts impossible 2.5 bar setpoint and still produces a decompression schedule