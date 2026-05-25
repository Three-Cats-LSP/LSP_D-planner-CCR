# 🎨 LSP D-PLANNER — BETA 3.5 MILESTONE

**Version:** Beta 3.5  
**Release Date:** May 25, 2026  
**Focus:** Mobile Design Polish  
**Status:** ✅ COMPLETE & PRODUCTION READY  
**Lines of Code:** 4,012  

---

## 🎯 BETA 3.5 SUMMARY

Beta 3.5 focuses on mobile usability — the biggest improvement being a dual-view Dive Profile table with a toggle button letting users switch between a compact standard table and the card layout. Plus a series of small but impactful polish fixes across the app.

---

## ✨ WHAT'S NEW

### 1. Dual-View Dive Profile Table (Mobile) ⭐

On screens < 600px a toggle button appears in the Dive Profile header:

**Table view (default on mobile):**
- Compact horizontally-scrollable standard table
- 10px font — fits all 7 columns on screen
- Same layout as desktop, just smaller
- Great for quick at-a-glance reference

**Card view:**
- Full label-on-left, value-on-right layout
- Each row is a card with phase header bar
- Easy to read one stop at a time

**Toggle button:**
- `⊟ Table` (active, cyan) ↔ `⊞ Cards`
- Sits next to TXT and PDF buttons
- Preference saved to localStorage
- Only visible on mobile — desktop unchanged

### 2. Phase Column — Symbols Only

Removed all text labels from the Phase column:
- Before: `🔴 DECO` / `🔵 BOTTOM` / `↓ DESCENT`
- After: `🔴` / `🔵` / `↓`

Cleaner, more compact, works better on narrow screens.

### 3. Gas Switch Row — Icon Added

Gas switch row now has a proper `⇄` icon in the Phase column — consistent with all other rows. Previously the icon was embedded in the text cell.

### 4. PDF — Phase Column Centered

Phase column icons now properly centered in the PDF export with fixed 32px width.

---

## 📝 CHANGELOG

### Added ✨
- `toggleTableView()` — switch between table/card view
- `loadTableViewPreference()` — restore saved view on load
- `⊟ Table` / `⊞ Cards` toggle button (mobile only)
- `.table-view` CSS class with full `!important` overrides
- `.table-scroll-wrap` horizontal scroll container
- `data-phase="switch"` on gas switch rows
- localStorage key: `decoTableView`

### Changed 🔄
- Table view is default on mobile (was cards)
- Phase column: symbols only, no text labels
- Gas switch: separate icon cell + info cell
- Gas switch: `colspan="6"` not `colspan="7"` (icon has own cell)
- PDF: `th:first-child, td:first-child` centered, 32px width

### Fixed 🐛
- Gas switch row had no icon in Phase column
- PDF Phase column icons not centered
- Mobile card view couldn't switch back to table
- `display:table` immediately overridden by `display:block`

---

## 📊 STATISTICS

| Metric | Beta 3.0 | Beta 3.5 | Change |
|--------|----------|----------|--------|
| Lines of code | 3,924 | 4,012 | +88 |
| File size | 167 KB | 170 KB | +3 KB |
| Mobile views | 1 | 2 | +1 |
| Breaking changes | 0 | 0 | — |

---

## 🔄 BACKWARDS COMPATIBLE

- ✅ All Beta 3.0 features preserved
- ✅ Desktop unchanged
- ✅ Dark/Light theme unchanged
- ✅ PDF export unchanged (except icon centering)
- ✅ Zero breaking changes

---

**Contact:** @threecats_lsp  
**License:** MIT  
🤿 *Better on every screen!*
