# CCR Engine Differential Report

**Generated:** 2026-06-22 12:15 UTC  
**LSP version:** 2.30.31  
**Scenarios:** 21  
**Failures:** 0  
**Inconclusive:** 72  

---

## CCR-C1 — Air diluent baseline

- **LSP:** RT 47 min · first stop 12 m · TTS 18.8
- **MultiDeco:** `PASS` 
- **DiveKit:** `PASS` 
- **Abysner:** `PASS` 
- **Subsurface:** `PASS` 
- **Metamorphic:** depth↑ → RT not shorter ✓, GF high↓ → RT not shorter ✓, deterministic repeat ✓

## CCR-C2 — Tx18/45 trimix

- **LSP:** RT 62 min · first stop 24 m · TTS 40.3
- **MultiDeco:** `EXPECTED_DIFFERENCE` runtimeMin Δ7; ttsMin Δ3.700000000000003
- **DiveKit:** `EXPECTED_DIFFERENCE` runtimeMin Δ6; ttsMin Δ3.1000000000000014; otu Δ5.5
- **Abysner:** `EXPECTED_DIFFERENCE` runtimeMin Δ9.5; ttsMin Δ6.5; cnsPercent Δ3.1000000000000014; otu Δ8
- **Subsurface:** `EXPECTED_DIFFERENCE` runtimeMin Δ9.700000000000003; ttsMin Δ6.700000000000003; cnsPercent Δ3.1999999999999957; otu Δ8.299999999999997

## CCR-C3 — Tx12/60 deep trimix

- **LSP:** RT 81 min · first stop 36 m · TTS 65.4
- **MultiDeco:** `EXPECTED_DIFFERENCE` firstStopDepthM Δ9; runtimeMin Δ17; ttsMin Δ12.599999999999994; cnsPercent Δ6.399999999999999; otu Δ16
- **DiveKit:** `EXPECTED_DIFFERENCE` runtimeMin Δ16; ttsMin Δ11.799999999999997; cnsPercent Δ7.299999999999997; otu Δ19.400000000000006
- **Abysner:** `EXPECTED_DIFFERENCE` runtimeMin Δ27.599999999999994; ttsMin Δ23.19999999999999; cnsPercent Δ12.199999999999996; otu Δ32.5
- **Subsurface:** `EXPECTED_DIFFERENCE` runtimeMin Δ27.599999999999994; ttsMin Δ23.19999999999999; cnsPercent Δ12.199999999999996; otu Δ32.5

## CCR-NDL — Shallow no-decompression CCR

- **LSP:** RT 26 min · first stop 0 m · TTS 5.7
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **abysner:** `INCONCLUSIVE` no golden capture
- **subsurface:** `INCONCLUSIVE` no golden capture

## CCR-SP — Distinct descent/bottom/deco setpoints

- **LSP:** RT 50 min · first stop 12 m · TTS 21.6
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **abysner:** `INCONCLUSIVE` no golden capture
- **subsurface:** `INCONCLUSIVE` no golden capture

## CCR-ML — Tx18/45 multilevel

- **LSP:** RT 64 min · first stop 27 m · TTS 44.3
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **abysner:** `INCONCLUSIVE` no golden capture
- **subsurface:** `INCONCLUSIVE` no golden capture

## CCR-GF-A — GF 50/80 sensitivity (C1 profile)

- **LSP:** RT 47 min · first stop 12 m · TTS 18.8
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **abysner:** `INCONCLUSIVE` no golden capture
- **subsurface:** `INCONCLUSIVE` no golden capture

## CCR-GF-B — GF 50/50 sensitivity (C1 profile)

- **LSP:** RT 56 min · first stop 12 m · TTS 27.8
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **abysner:** `INCONCLUSIVE` no golden capture
- **subsurface:** `INCONCLUSIVE` no golden capture

## CCR-LAST-A — Last stop 3 m (C1 profile)

- **LSP:** RT 47 min · first stop 12 m · TTS 18.8
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **abysner:** `INCONCLUSIVE` no golden capture
- **subsurface:** `INCONCLUSIVE` no golden capture

## CCR-LAST-B — Last stop 6 m (C1 profile)

- **LSP:** RT 49 min · first stop 12 m · TTS 20.8
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **abysner:** `INCONCLUSIVE` no golden capture
- **subsurface:** `INCONCLUSIVE` no golden capture

## CCR-BO — Planned bailout to OC

- **LSP:** RT 55 min · first stop 18 m · TTS 27
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **abysner:** `INCONCLUSIVE` no golden capture
- **subsurface:** `INCONCLUSIVE` no golden capture

## CCR-LOST-GAS — Bailout with EAN50 unavailable

- **LSP:** RT 65 min · first stop 18 m · TTS 37
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **abysner:** `INCONCLUSIVE` no golden capture
- **subsurface:** `INCONCLUSIVE` no golden capture

## CCR-REP — Repetitive dive — 60 min surface interval

- **LSP:** RT 53 min · first stop 12 m · TTS 24.8
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **abysner:** `INCONCLUSIVE` no golden capture
- **subsurface:** `INCONCLUSIVE` no golden capture

## CCR-ALT — Acclimatized dive at 1500 m

- **LSP:** RT 49 min · first stop 12 m · TTS 21.1
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **abysner:** `INCONCLUSIVE` no golden capture
- **subsurface:** `INCONCLUSIVE` no golden capture

## CCR-PRECISE-A — One-second minimum stops

- **LSP:** RT 47 min · first stop 12 m · TTS 18.8
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **abysner:** `INCONCLUSIVE` no golden capture
- **subsurface:** `INCONCLUSIVE` no golden capture

## CCR-PRECISE-B — Whole-minute stop rounding

- **LSP:** RT 47 min · first stop 12 m · TTS 18.8
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **abysner:** `INCONCLUSIVE` no golden capture
- **subsurface:** `INCONCLUSIVE` no golden capture

## CCR-SP-CROSSING — Valid deco setpoint crossing near surface

- **LSP:** RT 47 min · first stop 12 m · TTS 18.8
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **abysner:** `INCONCLUSIVE` no golden capture
- **subsurface:** `INCONCLUSIVE` no golden capture

## CCR-INVALID-SP — Bottom setpoint above configured maximum

- **LSP:** RT None min · first stop None m · TTS None
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **abysner:** `INCONCLUSIVE` no golden capture
- **subsurface:** `INCONCLUSIVE` no golden capture

## CCR-INVALID-GAS-SUM — Diluent fractions sum above 100%

- **LSP:** RT None min · first stop None m · TTS None
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **abysner:** `INCONCLUSIVE` no golden capture
- **subsurface:** `INCONCLUSIVE` no golden capture

## CCR-INVALID-GAS-NEGATIVE — Negative helium fraction

- **LSP:** RT None min · first stop None m · TTS None
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **abysner:** `INCONCLUSIVE` no golden capture
- **subsurface:** `INCONCLUSIVE` no golden capture

## CCR-INVALID-PROFILE — Non-positive bottom time

- **LSP:** RT None min · first stop None m · TTS None
- **multideco:** `INCONCLUSIVE` no golden capture
- **divekit:** `INCONCLUSIVE` no golden capture
- **abysner:** `INCONCLUSIVE` no golden capture
- **subsurface:** `INCONCLUSIVE` no golden capture

---

See [CCR_ENGINE_DIFFERENTIAL_TEST_PLAN.md](CCR_ENGINE_DIFFERENTIAL_TEST_PLAN.md) for methodology.