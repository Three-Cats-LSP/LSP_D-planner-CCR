# LSP D-Planner + CCR

**Rebreather edition** of [LSP D-Planner](https://github.com/Three-Cats-LSP/LSP_D-planner) — full closed-circuit (CCR), passive SCR (pSCR), bailout, and descent setpoint planning on top of the v2.20.x open-circuit foundation.

This is a **separate product and repository**. The main [LSP D-Planner](https://github.com/Three-Cats-LSP/LSP_D-planner) stays on the stable open-circuit release line (v2.20.x) without rebreather code.

Part of the [Three Cats LSP](https://threecats-lsp.com) **Diver's Toolkit**.

🌐 **Live App (GitHub Pages)**: https://threecats-lsp.github.io/LSP_D-planner-CCR/

**Current version: 2.30.0**

---

## Diver's Toolkit

| App | Purpose |
|-----|---------|
| **[LSP D-Planner](https://github.com/Three-Cats-LSP/LSP_D-planner)** | Open-circuit decompression planning |
| **LSP D-Planner + CCR** | Rebreather planning (this app) |
| **[T-Viewer](https://threecats-lsp.com/t-viewer/)** | Open and share exported dive plan TXT/PDF files |
| **[Get In Water](https://threecats-lsp.com/get-in-water/)** | Trip packing checklists |

---

## What's different from LSP D-Planner?

Built from LSP D-Planner **v2.20.21** with rebreather-specific additions only in this repo:

- **CCR (closed circuit)** — diluent-aware tissue loading, setpoint crossing, loop vs OC deco gas logic
- **pSCR (passive SCR)** — GUE-style O₂ drop model
- **Bailout mode** — OC ascent with GF 90/90 (Bühlmann)
- **Descent setpoint** — default 0.7 bar until high setpoint depth
- Both **Bühlmann ZH-L16C + GF** and **VPM-B / VPM-B/GFS** engines

All other features (Surf GF, prior-dive O₂ carry, shallow gradient, export/banner, presets, etc.) match the v2.20.x base.

---

## Web App

Open https://threecats-lsp.github.io/LSP_D-planner-CCR/ in any modern browser — no install required.

**Installation:** Add to home screen from your browser (Safari → Share → Add to Home Screen; Chrome → Install app).

---

## Android APK

Separate Android package (`com.threecats.lsp.dplannerccr`) so it can be installed **alongside** the standard LSP D-Planner APK.

Build: `npm run cap:sync` then open the `android/` project in Android Studio.

---

## Development

Same single-file architecture as LSP D-Planner — primary code in `index.html`.

```bash
python audit.py index.html    # 271 checks (includes GROUP 41 CCR)
```

Test suites: `tests-verify.html` (Section I · CCR), `tests-massive.html` (T3-CCR MultiDeco cross-val).

---

## License & disclaimer

Same terms as [LSP D-Planner](https://github.com/Three-Cats-LSP/LSP_D-planner). For **trained mixed-gas and rebreather divers only**. Not a substitute for proper certification, equipment checks, or dive planning discipline.
