# 🚀 LSP D-PLANNER — BETA 4.0 MILESTONE

**Version:** Beta 4.0  
**Release Date:** May 26, 2026  
**Focus:** Tools Mode + Contingency Planning  
**Status:** ✅ COMPLETE & PRODUCTION READY  
**Lines of Code:** 4,849  
**File Size:** 214 KB  

---

## 🎯 BETA 4.0 SUMMARY

Beta 4.0 is the biggest feature release since Beta 3.0. It introduces a dedicated **Tools mode** with a full suite of dive planning calculators, **Contingency Plans** for the Deco Schedule, a complete **Unit Converter**, and a major header/navigation redesign that moves Reference info into a clean overlay modal.

---

## ✨ NEW FEATURES

### 1. 🔧 Tools Mode — Dedicated Mode Button

A new **Tools** button sits next to Rec | Bühlmann in the header. Switching to Tools:
- Hides the tab navigation entirely
- Shows a focused tools panel
- Updates header to `🔧 LSP D-PLANNER · TOOLS`

Tools has its own sub-nav with 4 calculators:

---

### 2. MOD Calculator — Maximum Operating Depth

Interactive dual-slider interface:
- **O₂ % slider** — 1–100%, tick marks at 1% · 21% · 32% · 50% · 80% · 100%
- **ppO₂ limit slider** — 1.0–2.0 bar in 0.1 steps
- Live result: MOD in metres + feet, colour-coded (red <20m, yellow <30m, cyan safe)
- Values update in real-time as you drag

---

### 3. Best Mix Calculator

Find the optimal O₂ % for any depth:
- **Depth slider** — 1–100m
- **ppO₂ limit slider** — 1.0–2.0 bar
- Live result: Best O₂ %, actual ppO₂ at depth, gas name (AIR / EAN 32 / EAN 50 / O₂)

---

### 4. Max Depth Calculator

Find safe depth limits for any gas:
- **O₂ % slider** — 1–100%
- Live result: Max depth at both 1.4 bar (working) AND 1.6 bar (deco) in metres + feet

---

### 5. Unit Converter — 5 Categories

Sub-tabs within Unit Converter:

| Tab | Conversion | Features |
|-----|-----------|---------|
| **Pressure** | Bar ⇄ PSI ⇄ MPa | Bidirectional · 200 bar tank reference |
| **Volume** | Litres ⇄ ft³ | Bidirectional · AL80 reference |
| **Depth** | m ⇄ ft | Slider + inputs · 1–100m |
| **Temp** | °C ⇄ °F | Slider + inputs · -10°C to 40°C |
| **Weight** | kg ⇄ lbs | Slider + inputs · dive weight references |

All input fields are **bidirectional** — type in either side, other updates instantly. Depth, Temperature and Weight also have drag sliders.

---

### 6. ⚠️ Contingency Plans (Deco Schedule)

Appears automatically after calculating a deco plan:

**🚨 Gas Loss Scenario**
- One button per configured deco gas (e.g. "Lose EAN 50")
- Instantly calculates and shows new run time + deco time without that gas
- Restores original plan after showing result

**⏱️ Extended Bottom Time**
- `+3 min` and `+5 min` buttons
- Shows new total run time + deco obligation
- Restores original plan after showing result

---

### 7. 📖 Reference Modal Overlay

Reference content (Algorithm Comparison, Key Depth Limits, Follow Three Cats LSP Diving Team) moved from the tab bar into a **modal overlay**:
- `📖 REF` button sits next to `⚠ Training Use Only` in header
- Available in ALL modes (Rec, Bühlmann, Tools) at all times
- Dark overlay background, scrollable content
- `✕ Close` button dismisses
- Reference tab removed from tab navigation

---

## 🎨 UX CHANGES

- **Theme toggle** moved to brand area (left side, next to logo)
- **Reference tab** removed from tab bar → modal overlay instead
- **Algorithm Comparison** removed from all tabs — only in Reference modal
- **Key Depth Limits** removed from all tabs — only in Reference modal
- **Instagram QR** renamed: "Follow Three Cats LSP Diving Team"

---

## 📝 CHANGELOG

### Added ✨
- Tools mode button in header
- `switchTool()` function for tools sub-nav
- `switchConverter()` function for converter sub-nav
- `initTools()`, `initConverter()` initializers
- `toggleReference()` modal function
- `calcMOD()`, `calcBestMix()`, `calcMaxDepth()` calculators
- `convertPressure()`, `convertVolume()`, `convertDepth()`, `convertTemp()`, `convertWeight()`
- `convertDepthSlider()`, `convertTempSlider()`, `convertWeightSlider()`
- `updateSliderFill()` CSS variable fill helper
- `buildContingencyButtons()` — builds gas loss buttons from deco plan
- `calcGasLoss()` — recalculates deco without a gas
- `calcContingencyTime()` — recalculates with +3/+5 min bottom time
- `.lsp-slider` CSS — custom range input with animated thumb
- `.slider-ticks` / `.slider-ticks-abs` — evenly/absolutely positioned ticks
- `.conv-row`, `.conv-field`, `.conv-arrow`, `.conv-ref` CSS
- `contingencyCard` div in Deco Schedule
- `referenceModal` overlay div
- `📖 REF` button in header

### Changed 🔄
- Theme toggle moved from right-side header → next to brand logo
- Reference tab → modal overlay accessible from all modes
- "Follow LSP Diving Team" → "Follow Three Cats LSP Diving Team"
- `setAlgo()` handles Tools mode, hides/shows tabs nav
- Contingency card shown/hidden with deco results

### Removed ❌
- Reference tab from tab navigation
- Algorithm Comparison / Key Depth Limits / Instagram from tab content

### Fixed 🐛
- `tab-reference` stale reference in setAlgo removed
- Duplicate pdfLegend template literal breaking JS (from Beta 3.6)

---

## 📊 STATISTICS

| Metric | Beta 3.6 | Beta 4.0 | Change |
|--------|----------|----------|--------|
| Lines of code | 4,171 | 4,849 | +678 |
| File size | 178 KB | 214 KB | +36 KB |
| Tools | 0 | 4 | +4 |
| Converters | 0 | 5 | +5 |
| Mode buttons | 2 | 3 | +1 |
| Breaking changes | 0 | 0 | — |

---

## 🔄 BACKWARDS COMPATIBLE

- ✅ All Beta 3.6 features preserved
- ✅ PADI RDP + Bühlmann ZH-L16C unchanged
- ✅ PDF export unchanged
- ✅ Mobile layout unchanged
- ✅ Zero breaking changes

---

**Contact:** @threecats_lsp  
**License:** MIT  
🤿 *Tools. Calculations. Everything a diver needs!*
