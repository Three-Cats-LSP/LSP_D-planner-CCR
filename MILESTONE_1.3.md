# MILESTONE v1.3 — Settings Dropdowns, Visual Polish & Test Infrastructure
**Date:** 2026-06-03
**Audit:** 236/236 checks passed ✅
**Tests:** 42/42 settings integration ✅ | 14-profile regression ✅

---

## What shipped

### Compact settings header
Three button groups replaced with dropdowns — significantly more compact on mobile:
- **Water:** Salt (default) / EN13319 / Fresh
- **Units:** m (metric) / ft (imperial)
- **GF:** 20/85 · 30/70 · 30/85 · 40/80 · 45/85 · 45/95 · 50/75 · Custom…
  - Custom shows inline inputs, remembers last values via localStorage
  - GF hidden in Rec mode (irrelevant for recreational planning)
  - Default: **20/85**

### Gas switch row redesign
Full action-required visual treatment in both themes:
- Dark: amber-yellow tinted card with border + box-shadow frame
- Light: bright yellow card with amber border
- Both PDF exports match

### Table readability
- Ascent depth/run/arrow: proper green (was pale hardcoded `#80e0a0`)
- Light theme green: `#1a9e55` (was washed-out `#50C878`)

### Headless test infrastructure
- `lsp_engine.js` — engine extracted from index.html, runs in Node.js
- `test_regression.js` — 14 profiles vs ApexDeco and MultiDeco
- `test_settings.js` — 42 settings integration checks

---

## Algorithm verification
21 profiles across GF 20/85 + 30/70 + 40/80 vs MultiDeco:
- **Zero structural errors** — correct stop sequence, gas switches, depths
- **All deltas ±1 min maximum** — confirmed WV=0.0627 boundary effect
- Algorithm is correct and unchanged from v1.2
