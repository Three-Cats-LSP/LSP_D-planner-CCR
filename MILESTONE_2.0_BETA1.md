# LSP D-PLANNER — v2.0 Beta 1 Milestone

## Release Date
2026-06-05

## Summary
First Beta release of v2.0. Full VPM-B + VPM-B/GFS implementation alongside
Bühlmann ZHL-16C+GF. Real PDF generation (no browser print). Complete UI
colour system refresh with technical diving sticker conventions.

## New Features

### Algorithms
- VPM-B (Varying Permeability Model) fully implemented and verified 9/9 vs MultiDeco C+2
- VPM-B/GFS (VPM-B with Gradient Factor surface stop) implemented
- All three algorithms: Bühlmann ZHL-16C+GF, VPM-B, VPM-B/GFS

### PDF Export — Complete Rewrite
- **Real PDF file download** via jsPDF (replaced browser print/window.print)
- Unicode font embedding (Noto Sans v42, fetched async, cached)
- Deco PDF: stat grid, gas tags, alerts, deco table, gas consumption, dive graph + legend, GF curve + legend, tissue saturation bars, compartment detail
- Emergency PDF: scenario info, emergency schedule, CNS highlighting, dive graph + legend, GF curve + legend, tissue saturation, compartment detail
- CNS yellow row highlighting in both PDFs
- HIGH CNS% banner after table in both PDFs
- Nitrox-standard yellow/green gas switch rows

### UI Colour System
- **RoyalBlue #4169E1** — all deco gas elements (Gas 1/2 cards, deco gas pills, Bottom gas tag, DECOMPRESSION DIVE banner, gas switch row borders)
- **Nitrox sticker standard** — gas switch rows: yellow #FFD700 bg, dark green #007A33 text
- **Red #cc0000** — all danger/warning banners (gas shortage, emergency scenario, DECOMPRESSION DIVE border)
- Warning modal: red border, I UNDERSTAND button only (Close removed)
- Planning Aid header: red border

### Other Fixes
- CNS alert correctly placed under emergency plan only (not main plan)
- Deco table: vertical-align middle on all rows
- Gas switch row: equal top/bottom borders in PDF

## Audit
182 checks passing (up from 142 in v1.3)
