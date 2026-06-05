# MILESTONE v1.2 — Algorithm Settings & Export Consistency
**Date:** 2026-06-03  
**Audit:** 223/223 checks passed ✅

---

## What shipped

### Stop Rounding setting
New **No / Yes** dropdown replacing Fractional/Whole min.

- **No** — transit time absorbed into stop, precise values like 0:33 or 1:40. Matches ApexDeco exactly.
- **Yes** — every ceiling-hold stop rounded up to nearest whole minute. First stops always remain fractional (RT-snap). Closer to MultiDeco output.

### Water Vapor setting
New **0.0627 bar (B) / 0.0577 bar (M)** dropdown.

- **B (Bühlmann)** — original ZH-L16 standard at 37°C. Default.
- **M (MultiDeco)** — value used by MultiDeco. Pair with Yes rounding for closest MultiDeco match.
- `WATER_VAPOR` is now a runtime `let` — `updateWaterVapor()` called inside `runDecoSchedule()` and after every `appSettings.load()`. Bug fixed: previously always used 0.0627 even when 0.0577 was saved (load order bug).

### Settings `?` help modal
Full plain-language guide for every setting, accessible from the Decompression Schedule card header. Stop Rounding and Water Vapor explain the Yes/No and B/M labels with pairing guidance.

### Export consistency
Stop Rounding and WV now appear in all export formats:
- **Copy:** `Stp Rounding: Yes  WV: 0.0577(M)` (deco + emergency)
- **TXT:** `Stop Rounding: Yes  WV: 0.0577(M)` (deco + emergency)
- **PDF:** Dive Profile header + Emergency page 4 info block + Emergency standalone alert

### UI improvements
- Reset button: `btn-export` class, red colour, SVG icon only — matches Copy/TXT/PDF buttons
- Salt water is now the default density
- BT SAC label consistent everywhere
- Ascent row ppO₂ shows peak ppO₂ at starting depth (not destination)

---

## Algorithm verification summary
14 profiles tested (7×GF40/80, 7×GF30/70) in both modes:

**Fractional + WV=0.0627:** Exact match with ApexDeco on 11/14 profiles. Remaining 3 differ by ≤2 seconds — inherent WV=0.0627 vs ApexDeco's 0.0577 boundary effect.

**Whole min + WV=0.0577:** Matches MultiDeco stop structure (fractional first stops, whole-minute ceiling-hold stops). Per-stop differences ±1 min from residual WV boundary effect. Total RT within 1-2 min on all profiles.

---

## Storage key
Bumped to **v5** — clears stale settings on first load after update.
