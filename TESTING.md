# Algorithm Testing

## Reference profile

All algorithm changes are validated against this profile:

**Inputs:** 50m / 25 min BT / Air bottom gas / EAN50 switch @ 21m / O2 switch @ 6m / Salt water / Last stop 6m / Step 3m

### GF 30/70 — expected output

| Depth | Multideco 4.19 | DiveProMe | ApexDeco | LSP target |
|-------|---------------|-----------|----------|------------|
| 24m   | 1:07          | —         | 0:09     | ~1:10      |
| 12m   | 4:00          | 4:00      | 3:40     | 3:10–3:30  |
| 9m    | 5:00          | 5:00      | 4:40     | 4:20–4:40  |
| 6m    | 16:00         | 16:00     | 16:00    | 16:00–18:00|

### GF 50/85 — expected output

| Depth | Multideco | DiveProMe | LSP target |
|-------|-----------|-----------|------------|
| 9m    | 4:00      | 5:00      | 3:40–4:10  |
| 6m    | 14:00     | 14:00     | 14:00–15:30|

## Notes on inter-planner variance

The reference apps do not agree with each other. Multideco and ApexDeco differ by up to 60 seconds per stop. DiveProMe uses a different GF anchor formula (anchors at bottom depth rather than first stop depth). These differences are inherent to the algorithm, not bugs.

LSP uses Baker's GF formula, ZHL-16C canonical constants, and anchors GF at the first ceiling-forced stop depth.

## Regression test procedure

1. Open LSP, switch to Bühlmann mode, go to Deco Schedule tab
2. Set: Depth=50m, BT=25min, Air, EAN50+O2 deco gases, Salt, GF 30/70
3. Compare output to table above
4. Repeat for GF 50/85
