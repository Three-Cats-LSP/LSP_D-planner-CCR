## LSP D-Planner + CCR v2.30.31

**Issue #1 Deep Audit Fix** — closes all production defects and CI gaps from the post–v2.30.30 external audit · **405/405 checks passing**

🌐 **Live app:** https://threecats-lsp.com/d-planner-ccr/  
📲 **Android APK:** https://threecats-lsp.com/d-planner-ccr/download.html

---

### Milestone

This release completes **[Issue #1](https://github.com/Three-Cats-LSP/LSP_D-planner-CCR/issues/1)** — a deep audit of v2.30.30 that found nine production bugs and five test/CI gaps. All items were fixed, independently verified, and signed off in the final review comment on the issue.

Builds on the [v2.30.30 Safety Sign-Off](https://github.com/Three-Cats-LSP/LSP_D-planner-CCR/releases/tag/v2.30.30) (84 CCR audit findings, BUG-01–BUG-85).

---

### Critical fixes

| Area | Fix |
|------|-----|
| **pSCR trimix** | Fraction normalization — 18/45 diluent sums to 1.0; inspired inert pressures correct |
| **pSCR O₂ floor** | True **0.16 bar** minimum (not a 16% fraction scaling with depth) |
| **Imperial units** | Save/reload preserves unit system and **all UI labels** (ft, psi, cu ft/min) |
| **Input validation** | Invalid depth/BT blocked on technical deco **and** recreational planner; 300 min BT cap |
| **EAN80** | ZHL and VPM recognize 80% deco gas |
| **Tissue chart** | Uses live GF High and algorithm controls |
| **Export / PWA** | Recreational gas line in text export; relative manifest paths; SW offline fallback |

Also includes the Android launch crash fix (MainActivity package + site APK sync) and launcher label **LSP CCR**.

---

### Release gates (CI)

Every push to `main` now runs:

| Gate | Result |
|------|--------|
| `audit.py` static analysis | **405 passed** |
| `tests-verify.html` | **68 pass** (8 RT-drift warnings, 0 fail) |
| `tests-pscr-otu-cns.html` | **39 pass** |
| `dev/validate_pscr_e2e.py` | **PASS** (5 pSCR profiles + suite) |

---

### Upgrade notes

- **Web / PWA:** hard refresh or clear site data once to pick up the new service worker cache (`v2.30.31`).
- **Android:** uninstall any pre-fix APK if you had launch crashes, then install fresh from the download page.

---

### Part of the Diver's Toolkit

| App | Link |
|-----|------|
| LSP D-Planner (OC) | https://threecats-lsp.com/d-planner/ |
| LSP D-Planner + CCR | https://threecats-lsp.com/d-planner-ccr/ |
| T-Viewer | https://threecats-lsp.com/t-viewer/ |
| Get In Water | https://threecats-lsp.com/get-in-water/ |

---

*Planning software for trained rebreather and mixed-gas divers. Verify all plans against your dive computer and training standards.*
