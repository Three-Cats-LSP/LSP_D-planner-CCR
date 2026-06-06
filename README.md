# LSP D-Planner

**Version 2.5 Beta 1**

A technical dive decompression planner for mixed-gas deco diving.

## Supported Algorithms

- Bühlmann ZH-L16C + Gradient Factors (GF)
- VPM-B (Varying Permeability Model)
- VPM-B + GFS

## Live App

https://three-cats-lsp.github.io/LSP_D-planner/

## Files

| File | Purpose |
|------|---------|
| `index.html` | Main self-contained web app (no build needed) |
| `vpmb.py` | VPM-B Python reference engine |
| `VpmbEngine.java` | VPM-B Java engine |
| `VpmbGfsEngine.java` | VPM-B GFS Java engine |

## Deployment

This is a static single-file app. GitHub Pages serves it directly from `index.html` on the `main` branch.

## Disclaimer

Planning Aid Only. Not a substitute for training, certification, or a dive computer. Use at your own risk.
