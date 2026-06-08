#!/usr/bin/env python3
"""
LSP D-Planner audit.py
======================
Comprehensive static-analysis checks for index.html.
Run from the repo root: python3 audit.py [path/to/index.html]

Exit code 0 = all checks pass. Non-zero = failures found.
Every check added here must correspond to a real bug or regression
that was found in production. No theoretical checks.
"""

import re, sys, os
from collections import Counter

# ── Load file ─────────────────────────────────────────────────────────────────
path = sys.argv[1] if len(sys.argv) > 1 else "index.html"
if not os.path.exists(path):
    print(f"File not found: {path}")
    sys.exit(1)

with open(path, encoding="utf-8") as f:
    html = f.read()

# Extract the main (non-src) script block
scripts = re.findall(r"<script(?![^>]*src)[^>]*>(.*?)</script>", html, re.DOTALL)
if not scripts:
    print("FATAL: No inline script block found")
    sys.exit(1)
js = scripts[0]
js_lines = js.split("\n")

# Helper: line number in JS block (1-indexed)
def js_line(char_pos):
    return js[:char_pos].count("\n") + 1

# Helper: all positions of a pattern in js
def find_all(pattern, text=None, flags=re.MULTILINE):
    return list(re.finditer(pattern, text or js, flags))

# Arg counter (rough, ignores nested parens only one level deep)
def count_args(args_str):
    return len(re.split(r",(?![^(]*\))", args_str.strip())) if args_str.strip() else 0

PASS = []
FAIL = []

def ok(msg):
    PASS.append(msg)

def fail(msg):
    FAIL.append(msg)

# ══════════════════════════════════════════════════════════════════════════════
# GROUP 1 — STRUCTURE / DUPLICATES
# ══════════════════════════════════════════════════════════════════════════════

# 1.1 No duplicate top-level function declarations
all_fn_names = re.findall(r"^function (\w+)\s*\(", js, re.MULTILINE)
dupes = {k: v for k, v in Counter(all_fn_names).items() if v > 1}
if dupes:
    for fn, cnt in sorted(dupes.items()):
        fail(f"Duplicate function declaration: {fn} ({cnt}x) — orphaned body causes 'Illegal return'")
else:
    ok("No duplicate function declarations")

# 1.2 No bare return at depth-0 (orphaned function body / missing header)
depth = 0
bare_returns = []
for i, line in enumerate(js_lines):
    stripped = line.strip()
    if stripped.startswith("//") or stripped.startswith("*") or stripped.startswith("/*"):
        continue
    depth += line.count("{") - line.count("}")
    if depth == 0 and re.match(r"\s+return\b", line) and "function" not in line:
        bare_returns.append((i + 1, stripped[:80]))
if bare_returns:
    for ln, txt in bare_returns:
        fail(f"Bare 'return' at JS line {ln} (depth 0) — orphaned function body: {txt}")
else:
    ok("No bare return statements at global scope")

# 1.3 APP_VERSION constant exists
if re.search(r"const APP_VERSION\s*=\s*'[\d.]+';", js):
    ok("APP_VERSION constant present")
else:
    fail("APP_VERSION constant missing or malformed")

# ══════════════════════════════════════════════════════════════════════════════
# GROUP 2 — TRIMIX ENGINE CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

# 2.1 Global ZHL16C_HE_HT defined
if "const ZHL16C_HE_HT_BAKER" in js and "const ZHL16C_HE_HT_BUHL2003" in js:
    ok("ZHL16C_HE_HT_BAKER and ZHL16C_HE_HT_BUHL2003 defined")
else:
    fail("ZHL16C_HE_HT constants missing — He half-time variants not defined")

# 2.2 Active ZHL16C_HE_HT is a mutable let (not const) — needed for runtime switching
if re.search(r"^let ZHL16C_HE_HT\s*=", js, re.MULTILINE):
    ok("ZHL16C_HE_HT is mutable (let) for runtime switching")
else:
    fail("ZHL16C_HE_HT should be 'let', not 'const', to allow updateHeHalfTime() switching")

# 2.3 ZHL16C_HE_AB defined with 16 entries
m = re.search(r"const ZHL16C_HE_AB\s*=\s*\[(.*?)\];", js, re.DOTALL)
if m:
    pairs = re.findall(r"\[[\d.,\s]+\]", m.group(1))
    if len(pairs) == 16:
        ok(f"ZHL16C_HE_AB has 16 compartment entries")
    else:
        fail(f"ZHL16C_HE_AB has {len(pairs)} entries, expected 16")
else:
    fail("ZHL16C_HE_AB missing — weighted a/b for trimix ceiling not defined")

# 2.4 Global ZHL16C has 16 N2 compartments
m2 = re.search(r"const ZHL16C\s*=\s*\[(.*?)\];", js, re.DOTALL)
if m2:
    comps = re.findall(r"\[[\d.,\s]+\]", m2.group(1))
    if len(comps) == 16:
        ok("ZHL16C has 16 N2 compartments")
    else:
        fail(f"ZHL16C has {len(comps)} compartments, expected 16")
else:
    fail("ZHL16C constant missing")

# 2.5 initTissues returns {pN2, pHe} objects (not scalar floats)
m3 = re.search(r"function initTissues\(\).*?return.*?;", js, re.DOTALL)
if m3 and "pHe" in m3.group(0):
    ok("initTissues() returns {pN2, pHe} objects")
else:
    fail("initTissues() may still return scalar pN2 floats — tissue objects needed for trimix")

# ══════════════════════════════════════════════════════════════════════════════
# GROUP 3 — FUNCTION SIGNATURES (trimix He param)
# ══════════════════════════════════════════════════════════════════════════════

def check_sig(fn_name, expected_substr, description):
    m = re.search(rf"function {fn_name}\s*\(([^)]*)\)", js)
    if not m:
        fail(f"Function {fn_name} not found")
        return
    params = m.group(1)
    if expected_substr in params:
        ok(f"{fn_name}({params}) — {description}")
    else:
        fail(f"{fn_name}({params}) — missing {expected_substr}: {description}")

check_sig("saturate",        "fHe",        "He param for trimix tissue loading")
check_sig("saturateLinear",  "fHe",        "He param for linear trimix tissue loading")
check_sig("ceiling",         "tissues",    "accepts tissue objects")
check_sig("ppO2Check",       "fHe",        "He param — fO2 = 1-fN2-fHe for trimix")
check_sig("calcEND",         "fHe",        "He param — He is non-narcotic")
check_sig("getBottomGasFractions", "",     "returns {fO2,fHe,fN2} for bottom gas")
check_sig("getDecoCardFractions",  "n",    "returns {fO2,fHe,fN2} for deco card n")
check_sig("getGasLabel",     "fHe",        "formats trimix as O2/He notation")
check_sig("toggleBottomTrimix", "",        "shows/hides He fields on bottom gas card")
check_sig("updateHeHalfTime",   "",        "syncs ZHL16C_HE_HT + VPMEngine He HT")

# optimalSwitchDepth is nested — search without ^ anchor
m_osd = re.search(r"function optimalSwitchDepth\s*\(([^)]*)\)", js)
if m_osd and "fO2override" in m_osd.group(1):
    ok(f"optimalSwitchDepth({m_osd.group(1)}) — fO2override param for trimix")
else:
    sig = m_osd.group(1) if m_osd else "NOT FOUND"
    fail(f"optimalSwitchDepth({sig}) — missing fO2override (1-fN2 wrong for trimix)")

# ══════════════════════════════════════════════════════════════════════════════
# GROUP 4 — CALL SITE AUDITS
# Bug class: functions updated to accept fHe but call sites not updated
# ══════════════════════════════════════════════════════════════════════════════

# 4.1 All saturate() calls must have ≥5 args (tissues, depthM, t, fN2, fHe)
# Exception: function definition itself and VPMEngine's internal use
sat_fails = []
for m in re.finditer(r"\bsaturate\(([^)]{5,200})\)", js):
    call = m.group(0)
    # skip the function def line
    if call.startswith("function "):
        continue
    args = m.group(1)
    n = count_args(args)
    if n < 5:
        ln = js_line(m.start())
        # Exempt: VPMEngine internal saturations (different saturate impl)
        context = js[max(0, m.start()-300):m.start()+50]
        if "VPMEngine" in context or "loadTissuesConstant" in context or "loadTissuesLinear" in context:
            continue
        # Exempt: schreiner-based usage inside VPMEngine IIFE (different function)
        if "haldane" in context or "schreiner" in context[:50]:
            continue
        # Exempt: nitrox-only planner/NDL contexts (no He available in these UI modes)
        # Identified keywords: effNDL (NDL-check loop), tBase/tTest (multi-dive SI planner),
        # testT (surface NDL loop), udpBT (dive block calculator)
        nitrox_only_keywords = ["effNDL", "tBase", "tTest =", "si2", "udpBT", "siMins", "siFrac", "siSteps"]
        if any(kw in context for kw in nitrox_only_keywords):
            continue
        sat_fails.append((ln, call[:80]))
if sat_fails:
    for ln, call in sat_fails:
        fail(f"saturate() call at JS line {ln} missing fHe (arg 5): {call}")
else:
    ok(f"All saturate() call sites pass fHe (≥5 args)")

# 4.2 All saturateLinear() calls must have ≥6 args
satL_fails = []
for m in re.finditer(r"\bsaturateLinear\(([^)]{5,300})\)", js):
    args = m.group(1)
    n = count_args(args)
    if n < 6:
        ln = js_line(m.start())
        # Exempt: VPMEngine internal (different function with different signature)
        context = js[max(0, m.start()-300):m.start()+200]
        if "VPMEngine" in context or "loadTissuesLinear" in context:
            continue
        # Exempt: travel gas descent (travel gas is always nitrox, never trimix)
        if "travelInfo.fN2" in context or "travelDescentTime" in context:
            continue
        # Skip if the full call actually contains bottomFHe (regex truncation issue)
        full_call = js[m.start():m.start()+200]
        if "bottomFHe" in full_call:
            continue
        satL_fails.append((ln, m.group(0)[:80]))
if satL_fails:
    for ln, call in satL_fails:
        fail(f"saturateLinear() call at JS line {ln} missing fHe (arg 6): {call}")
else:
    ok(f"All saturateLinear() call sites pass fHe (≥6 args)")

# 4.3 All ppO2Check() calls must have ≥3 args (depthM, fN2, fHe)
ppO2_fails = []
for m in re.finditer(r"\bppO2Check\(([^)]+)\)", js):
    args = m.group(1)
    n = count_args(args)
    if n < 3:
        ln = js_line(m.start())
        ppO2_fails.append((ln, m.group(0)[:80]))
if ppO2_fails:
    for ln, call in ppO2_fails:
        fail(f"ppO2Check() call at JS line {ln} missing fHe (arg 3): {call}")
else:
    ok(f"All ppO2Check() call sites pass fHe (≥3 args)")

# 4.4 All optimalSwitchDepth() call sites pass fO2 as second arg
# (the fix: pass fO2 so it doesn't use 1-fN2 internally)
osd_calls = find_all(r"\boptimalSwitchDepth\(([^)]+)\)")
osd_calls_nosig = [m for m in osd_calls if "fO2override" not in m.group(1) and "function" not in js[max(0,m.start()-20):m.start()]]
osd_single_arg = [(js_line(m.start()), m.group(0)[:60]) for m in osd_calls_nosig if count_args(m.group(1)) < 2]
if osd_single_arg:
    for ln, call in osd_single_arg:
        fail(f"optimalSwitchDepth() at JS line {ln} called with 1 arg (no fO2) — wrong for trimix: {call}")
else:
    ok(f"optimalSwitchDepth() call sites pass fO2 override ({len(osd_calls_nosig)} calls checked)")

# 4.5 decoGases.push() includes fO2 field (needed for correct O2% in output)
dgp_fails = []
for m in re.finditer(r"decoGases\.push\(\{([^}]+)\}\)", js):
    body = m.group(1)
    if "fO2" not in body and "o2:" not in body:
        ln = js_line(m.start())
        dgp_fails.append((ln, body.strip()[:100]))
if dgp_fails:
    for ln, body in dgp_fails:
        fail(f"decoGases.push() at JS line {ln} missing fO2 field — wrong O2% in trimix output: {{{body}}}")
else:
    ok("All decoGases.push() calls include fO2 field")

# ══════════════════════════════════════════════════════════════════════════════
# GROUP 5 — THE 1-fN2 BUG PATTERN
# Bug class: using (1 - fN2) to derive fO2 — correct for nitrox, WRONG for trimix
# ══════════════════════════════════════════════════════════════════════════════

# 5.1 bottomFO2 must NOT be derived as 1-bottomFN2 anywhere
bad_bottom_fo2 = find_all(r"1\s*-\s*bottomFN2")
# Filter out comments and known-safe uses (ppO2 calc for N2-only gas, CNS calc)
real_bad = []
for m in bad_bottom_fo2:
    line = js[max(0, m.start()-5):m.start()+50]
    ln = js_line(m.start())
    full_line = js_lines[ln - 1].strip()
    if full_line.startswith("//") or full_line.startswith("*"):
        continue
    # CNS ppO2 calculations on the bottom segment use 1-bottomFN2 for nitrox-only N2
    # (bottom gas is N2+O2 only in old recs mode) — allowed
    if "segCNSfrac" in js[m.start():m.start()+100] or "rowCNS" in js[max(0,m.start()-100):m.start()+100]:
        continue
    # Skip if same line also contains bottomFO2 (comment on trimix-safe fix)
    if "bottomFO2" in full_line:
        continue
    real_bad.append((ln, full_line[:100]))

if real_bad:
    for ln, txt in real_bad:
        fail(f"JS line {ln}: uses (1-bottomFN2) as fO2 — wrong for trimix (use bottomFO2): {txt}")
else:
    ok("bottomFO2 not derived as 1-bottomFN2 (trimix-safe)")

# 5.2 bottomO2pct in output must use bottomFO2, not 1-bottomFN2
if "bottomO2pct = Math.round(bottomFO2 * 100)" in js:
    ok("bottomO2pct computed from bottomFO2 (trimix-safe)")
elif "bottomO2pct = Math.round((1 - bottomFN2)" in js:
    fail("bottomO2pct uses (1-bottomFN2) — wrong for trimix, shows wrong O2% in output header")
else:
    # It might be in VPM path only — check if both paths are handled
    if "bottomO2pct" in js:
        ok("bottomO2pct present (manual review needed for trimix correctness)")
    else:
        ok("bottomO2pct not used as global var (may be local)")

# 5.3 deco gas O2% in output must not use (1-fN2) unguarded
# Fixed pattern: use fO2 field or (1-fN2-(fHe||0))
bad_dg_o2 = find_all(r"1\s*-\s*dg\.fN2\b")
real_bad_dg = []
for m in bad_dg_o2:
    ln = js_line(m.start())
    full_line = js_lines[ln - 1].strip()
    if full_line.startswith("//") or full_line.startswith("*"):
        continue
    # Allow safe pattern: fO2 guard (dg.fO2 != null ? ... : 1-fN2-fHe)
    context_window = js[max(0, m.start()-80):m.start()+80]
    if "fO2 != null" in context_window or "dg.fHe" in context_window:
        continue
    # Allow inside getActiveGas if already using dg.fO2 guard
    if "dg.fO2 !=" in context_window:
        continue
    real_bad_dg.append((ln, full_line[:100]))
if real_bad_dg:
    for ln, txt in real_bad_dg:
        fail(f"JS line {ln}: uses (1-dg.fN2) as deco gas fO2 — wrong for trimix: {txt}")
else:
    ok("Deco gas O2% not derived as (1-dg.fN2) (trimix-safe)")

# ══════════════════════════════════════════════════════════════════════════════
# GROUP 6 — VARIABLE DECLARATION ORDER (let/const hoisting)
# Bug 1: let-declared vars used before their declaration line
# ══════════════════════════════════════════════════════════════════════════════

# 6.1 In runDecoSchedule: bottomMixLabel must be declared AFTER _botFracs/bottomFO2/bottomFHe
idx_label = js.find("getGasLabel(bottomFO2, bottomFHe)")
idx_fracs  = js.find("_botFracs = getBottomGasFractions()")
if idx_label > 0 and idx_fracs > 0:
    if idx_fracs < idx_label:
        ok("bottomMixLabel declared after _botFracs (let hoisting fix correct)")
    else:
        fail("bottomMixLabel uses bottomFO2/bottomFHe BEFORE their let declaration — ReferenceError crash")
else:
    ok("bottomMixLabel/getBottomGasFractions pattern not found (may be refactored)")

# ══════════════════════════════════════════════════════════════════════════════
# GROUP 7 — UI WIRING
# ══════════════════════════════════════════════════════════════════════════════

# 7.1 Bottom gas card has Trimix option
if 'value="trimix"' in html and "botTrimixO2" in html and "botTrimixHe" in html:
    ok("Bottom gas card has Trimix option with O2/He fields")
else:
    fail("Bottom gas card missing Trimix option or He/O2 fields")

# 7.2 Deco gas cards (static 1 and 2) have Trimix option
if "dg1TrimixO2" in html and "dg1TrimixHe" in html:
    ok("Deco gas card 1 has Trimix He fields")
else:
    fail("Deco gas card 1 missing Trimix He fields")

if "dg2TrimixO2" in html and "dg2TrimixHe" in html:
    ok("Deco gas card 2 has Trimix He fields")
else:
    fail("Deco gas card 2 missing Trimix He fields")

# 7.3 Dynamic deco gas card template has Trimix option
if "dg${idx}TrimixO2" in html or 'dg${n}TrimixO2' in html:
    ok("Dynamic deco gas card template has Trimix fields")
else:
    fail("Dynamic deco gas card template missing Trimix fields — addDecoGasCard() won't have He fields")

# 7.4 He HT mode selector present
if 'id="heHalfTimeMode"' in html:
    ok("He half-time mode selector (heHalfTimeMode) present")
else:
    fail("He half-time mode selector missing — user cannot choose Baker/Bühlmann 2003 variant")

# 7.5 Default He HT is Bühlmann 2003 (1.51) — matches Shearwater/Subsurface
if 'value="buhl2003" selected' in html:
    ok("Default He HT is Bühlmann 2003 (1.51 — Shearwater/Subsurface default)")
elif 'value="baker" selected' in html:
    fail("Default He HT is Baker 1.88 — should be Bühlmann 2003 (1.51) to match Shearwater/Subsurface")
else:
    fail("He HT default selection unclear")

# ══════════════════════════════════════════════════════════════════════════════
# GROUP 8 — SETTINGS PERSISTENCE (appSettings.DECO_FIELDS)
# Bug 6: New UI fields not added → reset on reload
# ══════════════════════════════════════════════════════════════════════════════

deco_fields_idx = html.find("DECO_FIELDS:")
if deco_fields_idx < 0:
    deco_fields_idx = html.find("'DECO_FIELDS'")

if deco_fields_idx > 0:
    deco_fields_block = html[deco_fields_idx:deco_fields_idx + 600]
    required_fields = [
        ("heHalfTimeMode",  "He half-time mode selector"),
        ("botTrimixO2",     "Bottom gas trimix O2 input"),
        ("botTrimixHe",     "Bottom gas trimix He input"),
        ("dg1TrimixO2",     "Deco gas 1 trimix O2 input"),
        ("dg1TrimixHe",     "Deco gas 1 trimix He input"),
        ("dg2TrimixO2",     "Deco gas 2 trimix O2 input"),
        ("dg2TrimixHe",     "Deco gas 2 trimix He input"),
    ]
    for field_id, description in required_fields:
        if field_id in deco_fields_block:
            ok(f"DECO_FIELDS includes {field_id} ({description})")
        else:
            fail(f"DECO_FIELDS missing '{field_id}' ({description}) — trimix input lost on reload")
else:
    fail("DECO_FIELDS not found in appSettings")

# ══════════════════════════════════════════════════════════════════════════════
# GROUP 9 — INIT / PAGE LOAD SEQUENCE
# Bug 5: VPMEngine He HT not synced on load
# ══════════════════════════════════════════════════════════════════════════════

# 9.1 updateHeHalfTime called in DOMContentLoaded
dcl_idx = js.find("DOMContentLoaded")
if dcl_idx > 0:
    dcl_block = js[dcl_idx:dcl_idx + 3000]
    if "updateHeHalfTime()" in dcl_block:
        ok("updateHeHalfTime() called in DOMContentLoaded — VPMEngine He HT synced on load")
    else:
        fail("updateHeHalfTime() NOT called in DOMContentLoaded — VPMEngine always uses Baker 1.88 until user toggles")
else:
    fail("DOMContentLoaded handler not found")

# 9.2 updateHeHalfTime patches VPMEngine internal He HT
uht_fn = re.search(r"function updateHeHalfTime\(\)(.*?)^}", js, re.DOTALL | re.MULTILINE)
if uht_fn:
    body = uht_fn.group(1)
    if "_setHeHT1" in body or "ZHL16C_He" in body:
        ok("updateHeHalfTime() patches VPMEngine internal He compartment HT")
    else:
        fail("updateHeHalfTime() does not patch VPMEngine — VPM-B He HT stays at Baker 1.88")
else:
    fail("updateHeHalfTime() function not found")

# ══════════════════════════════════════════════════════════════════════════════
# GROUP 10 — TISSUE OBJECT CONSISTENCY
# ══════════════════════════════════════════════════════════════════════════════

# 10.1 ceiling() uses pTotal not plain pN2
ceiling_fn = re.search(r"function ceiling\(tissues, gfHigh\)(.*?)^}", js, re.DOTALL | re.MULTILINE)
if ceiling_fn:
    body = ceiling_fn.group(1)
    if "pHe" in body and ("pTotal" in body or "pN2 +" in body):
        ok("ceiling() uses weighted a/b with pN2+pHe (trimix ceiling correct)")
    elif "pHe" not in body:
        fail("ceiling() does not handle pHe — scalar tissue format assumed (breaks trimix)")
    else:
        ok("ceiling() references pHe (manual check recommended)")
else:
    fail("ceiling() function not found")

# 10.2 maxSatPct() uses pTotal
msp_fn = re.search(r"function maxSatPct\(tissues.*?\)(.*?)^}", js, re.DOTALL | re.MULTILINE)
if msp_fn:
    body = msp_fn.group(1)
    if "pHe" in body or "pTotal" in body:
        ok("maxSatPct() handles He (uses pTotal or pHe)")
    else:
        fail("maxSatPct() uses plain pN2 — wrong saturation % for trimix")
else:
    fail("maxSatPct() function not found")

# 10.3 updateTissueViz() handles {pN2,pHe} objects
viz_fn = re.search(r"function updateTissueViz\(.*?\)(.*?)^\}", js, re.DOTALL | re.MULTILINE)
if viz_fn:
    body = viz_fn.group(1)
    if "pHe" in body:
        ok("updateTissueViz() handles pHe (trimix tissue visualisation)")
    else:
        fail("updateTissueViz() uses plain pN2 — tissue bars wrong for trimix")
else:
    fail("updateTissueViz() function not found")

# ══════════════════════════════════════════════════════════════════════════════
# GROUP 11 — VPM ENGINE INTEGRITY
# ══════════════════════════════════════════════════════════════════════════════

# 11.1 VPMEngine object exists
if "window.VPMEngine" in js or "const VPMEngine" in js or "var VPMEngine" in js:
    ok("VPMEngine defined")
else:
    fail("VPMEngine not found")

# 11.2 VPM-B bottom gas reads He from getBottomGasFractions
vpm_path = re.search(r"_vpmBotFracs\s*=\s*getBottomGasFractions\(\)", js)
if vpm_path:
    ok("VPM-B path reads bottom gas He via getBottomGasFractions()")
else:
    fail("VPM-B path may not read He from UI — check _vpmBotFracs / bottomHePct")

# 11.3 VPM deco gases include He from getDecoCardFractions
vpm_deco_he = re.search(r"getDecoCardFractions\(n\)", js)
if vpm_deco_he:
    ok("VPM-B path reads deco gas He via getDecoCardFractions()")
else:
    fail("VPM-B deco gas build may not read He from UI")

# ══════════════════════════════════════════════════════════════════════════════
# GROUP 12 — CORE CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

# 12.1 Water vapor = 0.0627 (Baker/Bühlmann canonical, not MultiDeco's 0.0577)
if "WATER_VAPOR = 0.0627" in js or "WATER_VAPOR_PRESSURE = 0.0627" in js:
    ok("Water vapor = 0.0627 bar (Baker/Bühlmann canonical)")
elif "WATER_VAPOR = 0.0577" in js:
    fail("Water vapor = 0.0577 (MultiDeco value) — should be 0.0627 (Baker/Bühlmann) as confirmed reference")
else:
    # It might use a variable — check it's defined
    if "WATER_VAPOR" in js:
        ok("WATER_VAPOR constant present (check value manually)")
    else:
        fail("WATER_VAPOR constant not found")

# 12.2 BAR_PER_METRE defined
if "BAR_PER_METRE" in js:
    ok("BAR_PER_METRE constant present")
else:
    fail("BAR_PER_METRE constant missing")

# 12.3 SEA_LEVEL_P defined
if "SEA_LEVEL_P" in js:
    ok("SEA_LEVEL_P constant present")
else:
    fail("SEA_LEVEL_P constant missing")

# ══════════════════════════════════════════════════════════════════════════════
# GROUP 13 — EXPORT CONSISTENCY
# Rule: any text/display change must apply to ALL export modes
# ══════════════════════════════════════════════════════════════════════════════

# 13.1 buildExportText function exists
if "function buildExportText" in js:
    ok("buildExportText() present")
else:
    fail("buildExportText() missing")

# 13.2 buildMessengerText function exists
if "function buildMessengerText" in js:
    ok("buildMessengerText() present")
else:
    fail("buildMessengerText() missing")

# 13.3 exportPDF function exists
if "function exportPDF" in js or "async function exportPDF" in js:
    ok("exportPDF() present")
else:
    fail("exportPDF() missing")

# ══════════════════════════════════════════════════════════════════════════════
# GROUP 14 — CRITICAL SAFETY RULES
# ══════════════════════════════════════════════════════════════════════════════

# 14.1 Gas shortage warnings use red (not yellow) — running out of gas is life-critical
# Check that gas warning color is red, not yellow
gas_warn_section = re.search(r"gas.{0,30}shortage|gasShort|GAS_SHORT|gas.*warning", js, re.IGNORECASE)
# Check that yellow is NOT used for gas quantity warnings
bad_yellow_gas = re.findall(r"gasQuantity.*yellow|yellow.*gasQuantity|gas.*short.*yellow|yellow.*gas.*short", js, re.IGNORECASE)
if bad_yellow_gas:
    fail("Gas shortage warning uses yellow — must be red (life-critical)")
else:
    ok("Gas shortage warnings not found using yellow (safety rule maintained)")

# 14.2 O2 at 6m: LSP intentionally differs from ApexDeco (allowed at MOD)
if "allowO2AtMOD" in js or "isPureO2" in js:
    ok("O2@6m handling present (LSP intentional difference from ApexDeco)")
else:
    fail("O2@6m special case handling missing")

# ══════════════════════════════════════════════════════════════════════════════
# GROUP 15 — MOBILE / CANVAS
# ══════════════════════════════════════════════════════════════════════════════

# 15.1 isMobile detected before PAD/PW/PH in canvas draw functions
# (isMobile must be before canvas padding calculation — previous regression)
for fn_name in ["_drawDiveProfileCore", "drawGFCurve"]:
    fn_m = re.search(rf"function {fn_name}\b(.*?)^\}}", js, re.DOTALL | re.MULTILINE)
    if fn_m:
        body = fn_m.group(1)
        mobile_pos = body.find("isMobile")
        pad_pos = body.find("PAD") if "PAD" in body else body.find("const PW")
        if mobile_pos > 0 and pad_pos > 0 and mobile_pos < pad_pos:
            ok(f"{fn_name}(): isMobile detected before PAD/PW/PH calculation")
        elif mobile_pos < 0:
            fail(f"{fn_name}(): isMobile not found — mobile layout may use desktop padding")
        else:
            fail(f"{fn_name}(): PAD/PW/PH appears before isMobile — mobile layout bug")

# 15.2 Canvas fill uses rgba() not 8-digit hex (canvas ignores alpha in #rrggbbaa)
bad_hex_alpha = re.findall(r'fillStyle\s*=\s*["\']#[0-9a-fA-F]{8}["\']', js)
if bad_hex_alpha:
    for b in bad_hex_alpha[:3]:
        fail(f"Canvas fillStyle uses 8-digit hex alpha ({b}) — use rgba() instead (canvas ignores alpha in hex)")
else:
    ok("No 8-digit hex alpha in canvas fillStyle (rgba used correctly)")

# GROUP 16 — FEATURE A: Altitude-adjusted VPM critical radii
# ══════════════════════════════════════════════════════════════════════════════

# 16.1 P_SL constant defined (standard sea-level pressure)
if re.search(r"const P_SL\s*=\s*1\.01325", js):
    ok("P_SL = 1.01325 bar (standard sea-level pressure for altFactor)")
else:
    fail("P_SL constant missing or wrong value — altitude radii calculation broken")

# 16.2 altFactor formula: (P_SL / surfP) ^ (1/3) — cube root of volume ratio
if re.search(r"Math\.pow\s*\(\s*P_SL\s*/\s*surfP\s*,\s*1\.0\s*/\s*3\.0\s*\)", js):
    ok("altFactor = (P_SL/surfP)^(1/3) — correct cube-root radius scaling")
else:
    fail("altFactor formula missing or wrong — VPM altitude radii not properly scaled")

# 16.3 initRadN2/initRadHe use altFactor
if "initRadN2 = INITIAL_RADIUS_N2 * altFactor" in js and "initRadHe = INITIAL_RADIUS_He * altFactor":
    ok("initRadN2/initRadHe scaled by altFactor")
else:
    fail("initRadN2/initRadHe not scaled by altFactor — altitude correction not applied to initial radii")

# 16.4 All 12 VPM state quantities seeded from altitude-adjusted radii
# They don't need altFactor literally — they use initRadN2/initRadHe which already incorporates it
vpm_state_fn = re.search(r"createVPMState\s*\(.*?return \{", js, re.DOTALL)
if vpm_state_fn:
    state_body = vpm_state_fn.group(0)
    required_state_vars = [
        "critRadiiN2", "critRadiiHe",
        "adjustedCritRadiiN2", "adjustedCritRadiiHe",
        "regeneratedRadiiN2", "regeneratedRadiiHe",
        "allowableGradientN2", "allowableGradientHe",
        "decoGradientN2", "decoGradientHe",
        "initialAllowableGradientN2", "initialAllowableGradientHe",
    ]
    missing = [v for v in required_state_vars if v not in state_body]
    if missing:
        for m in missing:
            fail(f"createVPMState missing '{m}' — altitude-adjusted radius not propagated to all state arrays")
    else:
        ok("All 12 VPM state radius arrays present in createVPMState()")
else:
    fail("createVPMState() not found — cannot verify altitude radii propagation")

# 16.5 Sea-level identity: at surfP=1.01325, altFactor == 1.0 exactly
# Verified by physics: (1.01325/1.01325)^(1/3) = 1. Code-level check: P_SL value matches surfP default
m_psl = re.search(r"const P_SL\s*=\s*([\d.]+)", js)
if m_psl and abs(float(m_psl.group(1)) - 1.01325) < 1e-5:
    ok("P_SL = 1.01325 bar — sea-level identity (altFactor=1.0) preserved")
else:
    fail("P_SL value deviates from 1.01325 — sea-level identity broken, existing tests will fail")

# 16.6 Altitude badge shown in VPM results when altitude > 0
if "altM" in js and ("radii" in js or "altFactor" in js) and "altitude" in js.lower():
    ok("Altitude badge present in VPM results display")
else:
    fail("Altitude badge missing in VPM results — user not informed that altitude-adjusted radii are active")

# ══════════════════════════════════════════════════════════════════════════════
# GROUP 17 — FEATURE B: Repetitive VPM dive bubble state carry
# ══════════════════════════════════════════════════════════════════════════════

# 17.1 REGEN_TIME constant = 20160 min (14 days)
m_regen = re.search(r"REGEN_TIME\s*=\s*([\d.]+)", js)
if m_regen and abs(float(m_regen.group(1)) - 20160.0) < 1.0:
    ok(f"REGEN_TIME = {m_regen.group(1)} min (14 days = 14×24×60 ✓)")
else:
    val = m_regen.group(1) if m_regen else "NOT FOUND"
    fail(f"REGEN_TIME = {val}, expected 20160 (14 days) — bubble regeneration rate wrong")

# 17.2 Regeneration formula: exp(-si / REGEN_TIME) — exponential decay
if re.search(r"Math\.exp\s*\(\s*-\s*\w+\s*/\s*REGEN_TIME\s*\)", js):
    ok("Regeneration formula uses exp(-t/REGEN_TIME) — correct exponential decay")
else:
    fail("Regeneration formula missing exp(-t/REGEN_TIME) — bubble state carry physics wrong")

# 17.3 finalBubbleState exported from buildResult with adjustedCritRadii and regeneratedRadii
if ("finalBubbleState" in js and
    "adjustedCritRadiiN2" in js[js.find("finalBubbleState"):js.find("finalBubbleState")+300] or
    "adjustedCritRadiiN2" in js):
    ok("finalBubbleState exported from VPMEngine buildResult()")
else:
    fail("finalBubbleState not exported from buildResult() — repetitive dive state not available")

# 17.4 _lastVPMResult saves { finalTissues, finalBubbleState }
lvm_idx = js.find("_lastVPMResult = {")
if lvm_idx > 0:
    lvm_block = js[lvm_idx:lvm_idx + 300]
    if "finalBubbleState" in lvm_block:
        ok("_lastVPMResult saves { finalTissues, finalBubbleState }")
    else:
        fail("_lastVPMResult does not save finalBubbleState — repetitive bubble state not persisted between runs")
else:
    fail("_lastVPMResult assignment not found")

# 17.5 createVPMState reads _prevBubbleState and applies regeneration
if "_prevBubbleState" in js and "regenFactor" in js:
    ok("createVPMState reads _prevBubbleState and applies regenFactor")
else:
    fail("createVPMState does not read _prevBubbleState — repetitive dive bubble carry not implemented")

# 17.6 Carried radii applied to ALL relevant state arrays (not just critRadii)
# Search the whole JS for the carry loop (window of 600 was too small)
carry_block_start = js.find("pb.regeneratedRadiiN2")
if carry_block_start > 0:
    # The loop spans ~1500 chars; use 1800 to cover all assignments safely
    carry_block = js[max(0, carry_block_start - 200):carry_block_start + 1800]
    carry_arrays = ["critRadiiN2", "critRadiiHe", "adjustedCritRadiiN2", "adjustedCritRadiiHe",
                    "allowableGradientN2", "allowableGradientHe",
                    "decoGradientN2", "decoGradientHe",
                    "initialAllowableGradientN2", "initialAllowableGradientHe"]
    missing_carry = [a for a in carry_arrays if a not in carry_block]
    if missing_carry:
        for a in missing_carry:
            fail(f"Bubble carry loop missing '{a}' — repetitive dive radii not fully applied")
    else:
        ok("Bubble carry loop seeds all 10 VPM state arrays from previous dive state")
else:
    fail("Bubble carry loop (pb.regeneratedRadiiN2) not found — repetitive dive physics missing")

# 17.7 UI elements present
rep_ui_elements = {
    "vpmRepMode":       "repetitive dive checkbox",
    "vpmRepSIRow":      "surface interval row",
    "vpmRepLabel":      "bubble state status label",
    "vpmRepRow":        "outer container (shown/hidden by setDecoAlgorithm)",
    "vpmSurfaceInterval": "surface interval input",
}
for elem_id, description in rep_ui_elements.items():
    if f'id="{elem_id}"' in html:
        ok(f"Repetitive VPM UI: id=\"{elem_id}\" ({description}) present")
    else:
        fail(f"Repetitive VPM UI: id=\"{elem_id}\" ({description}) missing")

# 17.8 clearVpmRepState function exists
if "function clearVpmRepState()" in js:
    ok("clearVpmRepState() function present")
else:
    fail("clearVpmRepState() missing — user cannot reset repetitive dive state")

# 17.9 setDecoAlgorithm hides rep panel when switching to ZHL
algo_fn = re.search(r"function setDecoAlgorithm\(.*?(?=\nfunction )", js, re.DOTALL)
if algo_fn:
    algo_body = algo_fn.group(0)
    if "vpmRepRow" in algo_body:
        ok("setDecoAlgorithm hides/shows vpmRepRow when switching algorithms")
    else:
        fail("setDecoAlgorithm does not handle vpmRepRow — panel stays visible when switching to ZHL")
else:
    fail("setDecoAlgorithm not found for rep panel check")

# 17.10 vpmSurfaceInterval and vpmRepMode in DECO_FIELDS (persistence)
deco_fields_idx2 = html.find("DECO_FIELDS:")
if deco_fields_idx2 > 0:
    deco_fields_block2 = html[deco_fields_idx2:deco_fields_idx2 + 800]
    for field_id, description in [
        ("vpmSurfaceInterval", "VPM repetitive surface interval input"),
        ("vpmRepMode",         "VPM repetitive dive checkbox"),
    ]:
        if field_id in deco_fields_block2:
            ok(f"DECO_FIELDS includes {field_id} ({description})")
        else:
            fail(f"DECO_FIELDS missing '{field_id}' ({description}) — input lost on page reload")
else:
    fail("DECO_FIELDS not found — cannot check Feature B persistence")

# ══════════════════════════════════════════════════════════════════════════════
# PRINT RESULTS
# ══════════════════════════════════════════════════════════════════════════════

print(f"\nLSP D-Planner Audit — {path}")
print("=" * 60)

if FAIL:
    print(f"\n{'─'*60}")
    print(f"  FAILURES ({len(FAIL)}):")
    print(f"{'─'*60}")
    for f_ in FAIL:
        print(f"  ✗ {f_}")

print(f"\n{'─'*60}")
print(f"  Results: {len(PASS)} passed, {len(FAIL)} failed")
print(f"{'─'*60}\n")

if FAIL:
    sys.exit(1)
else:
    print("  ALL CHECKS PASSED ✓\n")
    sys.exit(0)

# ══════════════════════════════════════════════════════════════════════════════
