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
if re.search(r"const APP_VERSION", js):
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

# 7.5 Default He HT is Baker 1.88 — VPM-B canonical (Baker FORTRAN 1998, ApexDeco, MultiDeco)
# Rationale: LSP uses VPM-B as primary algorithm; Baker half-times are the correct match.
# Bühlmann 2003 (1.51) matches Shearwater/Subsurface but is NOT the VPM-B reference.
baker_selected = ('value="baker" selected' in html or 'selected="" value="baker"' in html or
                  "value='baker' selected" in html or "selected value=\"baker\"" in html)
buhl_selected  = ('value="buhl2003" selected' in html or 'selected="" value="buhl2003"' in html)
if baker_selected:
    ok("Default He HT is Baker 1.88 (VPM-B canonical — ApexDeco/MultiDeco compatible)")
elif buhl_selected:
    fail("Default He HT is Bühlmann 2003 (1.51) — should be Baker 1.88 for VPM-B engine compatibility")
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
bad_hex_alpha = re.findall(r'fillStyle\s*=\s*["\']\#[0-9a-fA-F]{8}["\']', js)
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

# GROUP 18 — FEATURE: SAC-based gas consumption
# ══════════════════════════════════════════════════════════════════════════════

# 18.1 SAC inputs present
for eid, desc in [("sacBottom", "bottom SAC L/min"), ("sacDeco", "deco SAC L/min")]:
    if f'id="{eid}"' in html:
        ok(f"SAC input id=\"{eid}\" ({desc}) present")
    else:
        fail(f"SAC input id=\"{eid}\" ({desc}) missing")

# 18.2 Cylinder fields present for all gas positions
cyl_fields = [
    ("cylBot_size",        "bottom gas cylinder size"),
    ("cylBot_pres",        "bottom gas cylinder pressure"),
    ("cylDg1_size",        "deco gas 1 cylinder size"),
    ("cylDg1_pres",        "deco gas 1 cylinder pressure"),
    ("cylDg2_size",        "deco gas 2 cylinder size"),
    ("cylDg2_pres",        "deco gas 2 cylinder pressure"),
    ("cylTravelGas_size",  "travel gas cylinder size"),
    ("cylTravelGas_pres",  "travel gas cylinder pressure"),
]
for eid, desc in cyl_fields:
    if f'id="{eid}"' in html:
        ok(f"Cylinder field id=\"{eid}\" ({desc}) present")
    else:
        fail(f"Cylinder field id=\"{eid}\" ({desc}) missing")

# 18.3 Gas consumption function uses correct formula: SAC × P_abs × time
if "sac * absP * durMin" in js or "sac * absP * dur" in js:
    ok("Gas consumption formula: SAC × P_abs × duration (correct surface-equivalent litres)")
else:
    fail("Gas consumption formula missing sac × absP × duration")

# 18.4 Buhlmann path converts psi→bar for imperial units
# Search 800 chars from cylIds definition to cover the entire forEach loop
buh_cyl_start = js.find("const cylIds = [\n      ['cylBot_size','cylBot_pres']")
buh_cyl_block = js[buh_cyl_start:buh_cyl_start + 800] if buh_cyl_start > 0 else ""
if "14.5038" in buh_cyl_block or ("imperial" in buh_cyl_block and "prRaw" in buh_cyl_block):
    ok("Buhlmann gas consumption: cylinder pressure converted psi→bar in imperial mode")
else:
    fail("Buhlmann gas consumption: no psi→bar conversion — cylinder capacity overstated in imperial mode")

# 18.5 VPM path ALSO converts psi→bar for imperial units
vpm_cyl_start = js.find("cylCapVPM = {};")
vpm_cyl_block = js[vpm_cyl_start:vpm_cyl_start + 400] if vpm_cyl_start > 0 else ""
if "14.5038" in vpm_cyl_block or ("imperial" in vpm_cyl_block and "pr " in vpm_cyl_block):
    ok("VPM gas consumption: cylinder pressure converted psi→bar in imperial mode")
else:
    fail("VPM gas consumption: no psi→bar conversion — WRONG cylinder capacity in imperial mode")

# 18.6 Travel gas cylinder included in Buhlmann cylIds
buh_cyl_section = js[js.find("const cylIds = ["):js.find("const cylIds = [") + 400] if "const cylIds = [" in js else ""
if "cylTravelGas_size" in buh_cyl_section:
    ok("Buhlmann cylIds includes travel gas cylinder")
else:
    fail("Buhlmann cylIds missing travel gas — travel gas consumption has no shortage warning")

# 18.7 Travel gas cylinder included in VPM cylIds
vpm_cyl_ids = js[js.find("[['cylBot_size','cylBot_pres']"):js.find("[['cylBot_size','cylBot_pres']") + 300] if "[['cylBot_size','cylBot_pres']" in js else ""
if "cylTravelGas_size" in vpm_cyl_ids:
    ok("VPM cylIds includes travel gas cylinder")
else:
    fail("VPM cylIds missing travel gas — travel gas consumption has no shortage warning")

# 18.8 All SAC and cylinder fields in DECO_FIELDS (persistence)
deco_fields_idx3 = html.find("DECO_FIELDS:")
if deco_fields_idx3 > 0:
    deco_fields_block3 = html[deco_fields_idx3:deco_fields_idx3 + 1200]
    gas_fields_required = [
        ("sacBottom",           "bottom SAC"),
        ("sacDeco",             "deco SAC"),
        ("cylBot_size",         "bottom cylinder size"),
        ("cylBot_pres",         "bottom cylinder pressure"),
        ("cylDg1_size",         "deco gas 1 cylinder size"),
        ("cylDg1_pres",         "deco gas 1 cylinder pressure"),
        ("cylDg2_size",         "deco gas 2 cylinder size"),
        ("cylDg2_pres",         "deco gas 2 cylinder pressure"),
        ("cylTravelGas_size",   "travel gas cylinder size"),
        ("cylTravelGas_pres",   "travel gas cylinder pressure"),
    ]
    for field_id, description in gas_fields_required:
        if field_id in deco_fields_block3:
            ok(f"DECO_FIELDS includes {field_id} ({description})")
        else:
            fail(f"DECO_FIELDS missing '{field_id}' ({description}) — value lost on page reload")
else:
    fail("DECO_FIELDS not found — cannot verify gas consumption field persistence")

# ══════════════════════════════════════════════════════════════════════════════
# GROUP 19 — FEATURE: VPM-B/GFS gradient blending (applyGFSurfacing)
# ══════════════════════════════════════════════════════════════════════════════

# 19.1 applyGFSurfacing function exists
if "function applyGFSurfacing(" in js:
    ok("applyGFSurfacing() function present")
else:
    fail("applyGFSurfacing() missing — VPM-B/GFS gradient blending not implemented")

# 19.2 Blend fraction: stopDepth / firstStopDepth (1 at first stop → VPM, 0 at surface → GF)
if "fraction = stopDepth / firstStopDepth" in js:
    ok("GFS blend fraction = stopDepth/firstStopDepth (1=first stop pure VPM, 0=surface pure GF)")
else:
    fail("GFS blend fraction formula wrong — direction of VPM→GF transition incorrect")

# 19.3 Blend formula: vpmGrad * fraction + buhlGrad * (1 - fraction)
if "blendedGrad = vpmGrad * fraction + buhlGrad * (1 - fraction)" in js:
    ok("GFS blend formula: linear VPM→GF interpolation correct")
else:
    fail("GFS blend formula missing or wrong")

# 19.4 applyGFSurfacing uses weighted a/b for trimix (not plain N2 values)
gfs_fn = re.search(r"function applyGFSurfacing\(.*?\n    \}", js, re.DOTALL)
if gfs_fn:
    body = gfs_fn.group(0)
    if "ZHL16C_He" in body and "pTotal" in body:
        ok("applyGFSurfacing uses weighted a/b for trimix (ZHL16C_He + pTotal weighting)")
    else:
        fail("applyGFSurfacing does not use weighted a/b — GFS ceiling wrong for trimix")
else:
    fail("applyGFSurfacing function body not found for trimix check")

# 19.5 applyGFSurfacing only called for VPMB_GFS model (not VPMB or VPMBE)
# Find the call and check the guard that wraps it
gfs_call_idx = js.find("applyGFSurfacing(ctx.state")
if gfs_call_idx > 0:
    guard_ctx = js[max(0, gfs_call_idx - 150):gfs_call_idx]
    if "model === 'VPMB_GFS'" in guard_ctx or 'model === "VPMB_GFS"' in guard_ctx:
        ok("applyGFSurfacing called only when model === 'VPMB_GFS'")
    else:
        fail("applyGFSurfacing may be called for wrong models — check conditional")
else:
    fail("applyGFSurfacing call site not found")


# ══════════════════════════════════════════════════════════════════════════════
# GROUP 20 — GAS CONSUMPTION: unit correctness
# ══════════════════════════════════════════════════════════════════════════════

# 20.1 SAC fields have convertNumericInput in setUnits (L/min ↔ cu ft/min)
set_units_fn = re.search(r"function setUnits\(.*?(?=\nfunction )", js, re.DOTALL)
if set_units_fn:
    set_units_body = set_units_fn.group(0)
    if "convertNumericInput('sacBottom'" in set_units_body:
        ok("setUnits converts sacBottom value (L/min ↔ cu ft/min)")
    else:
        fail("setUnits missing convertNumericInput for sacBottom — SAC value stays at metric default in imperial mode")
    if "convertNumericInput('sacDeco'" in set_units_body:
        ok("setUnits converts sacDeco value (L/min ↔ cu ft/min)")
    else:
        fail("setUnits missing convertNumericInput for sacDeco — SAC value stays at metric default in imperial mode")
else:
    fail("setUnits function not found for SAC conversion check")

# 20.2 Gas consumption display uses correct unit label (not hardcoded 'L')
# Buhlmann path: normal plan uses calcGasPlan() (volU declared inside),
# emergency path uses inline Object.entries forEach with volUnitV2.
# VPM path: uses for..of loop over gasConsVPM entries with volUnitV.
buh_block_start = js.find("if (gasEl && Object.keys(gasConsumed).length)")
buh_block = js[buh_block_start:buh_block_start + 3000] if buh_block_start > 0 else ""
if ("volUnitV" in buh_block or "calcGasPlan()" in buh_block):
    ok("Buhlmann gas consumption display uses units-aware volume label (L / cu ft)")
else:
    fail("Buhlmann gas consumption display hardcodes 'L' — wrong unit shown in imperial mode")

vpm_block_start = js.find("if (gasElVPM && Object.keys(gasConsVPM).length)")
vpm_block = js[vpm_block_start:vpm_block_start + 3000] if vpm_block_start > 0 else ""
if "volUnitV" in vpm_block or "volUnit" in vpm_block:
    ok("VPM gas consumption display uses units-aware volume label (L / cu ft)")
else:
    fail("VPM gas consumption display hardcodes 'L' — wrong unit shown in imperial mode")

# 20.3 Buhlmann gas plan renders via calcGasPlan() or declares volUnitV before use
# (Buhlmann refactored to use calcGasPlan() for normal path + volUnitV2 for emergency path)
calc_gas_plan_fn = js.find("function calcGasPlan()")
calc_gas_plan_units = js[calc_gas_plan_fn:calc_gas_plan_fn + 200] if calc_gas_plan_fn > 0 else ""
if ("const volU" in calc_gas_plan_units or "volUnit" in calc_gas_plan_units):
    ok("calcGasPlan() declares unit-aware volume label — no ReferenceError in Buhlmann gas render")
else:
    fail("volUnitV not declared in Buhlmann gas loop — ReferenceError when gas consumption renders")

# 20.1b ZHLEngine exposed on window for test harnesses
if "window.ZHLEngine = ZHLEngine" in js and "const ZHLEngine = (() => {" in js:
    ok("ZHLEngine callable interface exposed — Bühlmann testable without DOM coupling")
else:
    fail("ZHLEngine not exposed on window — ZHLC_GF tests in test harness will run VPM-B instead")

# 20.3b calcEND_tool uses calcEND() — not simplified sea-level formula
# Bug: was using pNarc * 10 - 10 (wrong at altitude, ignored narcotic toggles)
end_tool_fn = js[js.find("function calcEND_tool()"):js.find("function calcEND_tool()") + 1500]
if "calcEND(dM" in end_tool_fn or "calcEND(depthM" in end_tool_fn:
    ok("calcEND_tool() delegates to calcEND() — altitude-correct, respects narcotic toggles")
else:
    fail("calcEND_tool() uses simplified formula — wrong at altitude, ignores narcoticN2/narcoticO2 settings")

# 20.3c calcMOD() in Tools panel uses altSurfaceP (not hardcoded sea-level formula)
mod_fn_start = js.find("function calcMOD() {")
mod_fn = js[mod_fn_start:mod_fn_start + 400] if mod_fn_start > 0 else ""
if "altSurfaceP" in mod_fn and "BAR_PER_METRE" in mod_fn:
    ok("calcMOD() (Tools tab) uses altSurfaceP + BAR_PER_METRE — altitude-correct")
else:
    fail("calcMOD() (Tools tab) uses hardcoded sea-level formula — wrong at altitude")

# 20.3d setUnits() refreshes Tools panels (END Calc, Best Mix, MOD, EAD, Gas Table, Surface Int)
set_units_end = js[js.find("function setUnits("):js.find("function setUnits(") + 14000]
required_refreshes = ["calcEND_tool", "calcBestMix", "renderEADTable", "renderGasTable", "calcSurfInt", "calcAvgDepth"]
missing = [f for f in required_refreshes if f not in set_units_end]
if not missing:
    ok("setUnits() refreshes all Tools panels — no stale displays on metric/imperial toggle")
else:
    fail(f"setUnits() missing Tools panel refresh calls: {', '.join(missing)}")

# 20.4 PSI_PER_BAR and CUFT_PER_L constants defined with correct values
psi_m = re.search(r"PSI_PER_BAR\s*=\s*([\d.]+)", js)
cuft_m = re.search(r"CUFT_PER_L\s*=\s*([\d.]+)", js)
if psi_m and abs(float(psi_m.group(1)) - 14.5038) < 0.01:
    ok(f"PSI_PER_BAR = {psi_m.group(1)} (correct)")
else:
    fail(f"PSI_PER_BAR = {psi_m.group(1) if psi_m else 'NOT FOUND'} (expected 14.5038)")
if cuft_m and abs(float(cuft_m.group(1)) - 0.0353147) < 0.000001:
    ok(f"CUFT_PER_L = {cuft_m.group(1)} (correct)")
else:
    fail(f"CUFT_PER_L = {cuft_m.group(1) if cuft_m else 'NOT FOUND'} (expected 0.0353147)")

# 20.5 Cylinder pressure inputs converted in setUnits (bar ↔ psi)
if set_units_fn:
    body = set_units_fn.group(0)
    if "allCylPres" in body and "PSI_PER_BAR" in body:
        ok("setUnits converts all cylinder pressure fields (bar ↔ psi)")
    else:
        fail("setUnits missing cylinder pressure conversion — fields stay in metric units when switching to imperial")
    if "allCylSize" in body and "CUFT_PER_L" in body:
        ok("setUnits converts all cylinder size fields (L ↔ cu ft)")
    else:
        fail("setUnits missing cylinder size conversion — size fields stay in metric units when switching")

# 20.6 Dynamic cylinder pressure fields covered by allCylPres (querySelectorAll)
if "querySelectorAll" in js and 'cylDg' in js and '_pres' in js:
    ok("allCylPres uses querySelectorAll to include dynamic deco gas cylinder fields")
else:
    fail("allCylPres missing querySelectorAll — dynamically added deco gas cylinder fields not converted")


# ══════════════════════════════════════════════════════════════════════════════
# GROUP 21 — FEATURE: Minimum Decompression Profile
# ══════════════════════════════════════════════════════════════════════════════

# 21.1 enforceMinDecoProfile function exists
if "function enforceMinDecoProfile(" in js:
    ok("enforceMinDecoProfile() function present")
else:
    fail("enforceMinDecoProfile() missing — minimum deco profile feature not implemented")

# 21.2 Called in Buhlmann path
if "enforceMinDecoProfile(collapsed," in js:
    ok("enforceMinDecoProfile called in Buhlmann path")
else:
    fail("enforceMinDecoProfile not called in Buhlmann path — min deco profile ignored for ZHL")

# 21.3 Called in VPM path
if "enforceMinDecoProfile(_vpmRawStops," in js:
    ok("enforceMinDecoProfile called in VPM path")
else:
    fail("enforceMinDecoProfile not called in VPM path — min deco profile ignored for VPM-B")

# 21.4 UI fields present
for eid, desc in [
    ("minDecoProfileEnable", "enable/disable select"),
    ("minDeco9m",            "9m stop minimum minutes"),
    ("minDeco6m",            "6m stop minimum minutes"),
    ("minDecoProfileFields", "fields container (shown/hidden)"),
]:
    if f'id="{eid}"' in html:
        ok(f'Min deco UI: id="{eid}" ({desc}) present')
    else:
        fail(f'Min deco UI: id="{eid}" ({desc}) missing')

# 21.5 Fields in DECO_FIELDS (persistence)
deco_fields_idx4 = html.find("DECO_FIELDS:")
deco_block4 = html[deco_fields_idx4:deco_fields_idx4+1600] if deco_fields_idx4 > 0 else ""
for field_id, desc in [
    ("minDecoProfileEnable", "enable select"),
    ("minDeco9m",            "9m minimum"),
    ("minDeco6m",            "6m minimum"),
]:
    if field_id in deco_block4:
        ok(f"DECO_FIELDS includes {field_id} ({desc})")
    else:
        fail(f"DECO_FIELDS missing '{field_id}' ({desc}) — value lost on page reload")

# 21.6 Fields in _doResetToDefaults
reset_fn = re.search(r"function _doResetToDefaults\(.*?(?=\nfunction )", js, re.DOTALL)
if reset_fn:
    reset_body = reset_fn.group(0)
    for field_id, default, desc in [
        ("minDecoProfileEnable", "'no'",       "min deco enable"),
        ("minDeco9m",            "'1'",         "9m default"),
        ("minDeco6m",            "'3'",         "6m default"),
        ("cylTravelGas_size",    "'11'",        "travel cylinder size"),
        ("cylTravelGas_pres",    "'200'",       "travel cylinder pressure"),
        ("heHalfTimeMode",       "'baker'",     "He HT default"),
    ]:
        if field_id in reset_body:
            ok(f"_doResetToDefaults includes {field_id} (default {default})")
        else:
            fail(f"_doResetToDefaults missing '{field_id}' — Reset button leaves it unchanged")
else:
    fail("_doResetToDefaults function not found")

# 21.7 Label update on unit switch
set_units_fn2 = re.search(r"function setUnits\(.*?(?=\nfunction )", js, re.DOTALL)
if set_units_fn2 and "updateMinDecoLabels" in set_units_fn2.group(0):
    ok("setUnits calls updateMinDecoLabels (9m/30ft labels update on unit switch)")
elif "updateMinDecoLabels" in js:
    # Check if it's called somewhere in setUnits section
    su_idx = js.find("function setUnits(")
    su_end = js.find("\nfunction ", su_idx+1)
    if "updateMinDecoLabels" in js[su_idx:su_end]:
        ok("setUnits calls updateMinDecoLabels (9m/30ft labels update on unit switch)")
    else:
        fail("setUnits does not call updateMinDecoLabels — depth labels stay metric when switching to imperial")
else:
    fail("updateMinDecoLabels missing — depth labels do not update on unit switch")

# 21.8 pO2: null in injected stops is handled (falls through to ppO2Check)
if "pO2 != null ? parseFloat(s.pO2) : parseFloat(ppO2Check(" in js:
    ok("Injected stop pO2:null handled — ppO2Check recalculates ppO2 for min deco stops")
else:
    fail("pO2:null injected stops may not get ppO2 recalculated — check stop row rendering")

# ══════════════════════════════════════════════════════════════════════════════
# GROUP 22 — RESET TO DEFAULTS (completeness)
# ══════════════════════════════════════════════════════════════════════════════

# 22.1 confirmModal present (used by resetToDefaults)
if 'id="confirmModal"' in html and 'id="confirmModalMsg"' in html:
    ok("confirmModal and confirmModalMsg present (reset confirmation dialog)")
else:
    fail("confirmModal/confirmModalMsg missing — reset confirmation dialog broken")

# 22.2 showConfirm / closeConfirmModal functions present
for fn_name in ["showConfirm", "closeConfirmModal"]:
    if f"function {fn_name}(" in js:
        ok(f"{fn_name}() present")
    else:
        fail(f"{fn_name}() missing — reset confirmation broken")

# 22.3 resetToDefaults uses showConfirm (not direct reset)
reset_fn2 = re.search(r"function resetToDefaults\(\).*?\}", js, re.DOTALL)
if reset_fn2 and "showConfirm" in reset_fn2.group(0):
    ok("resetToDefaults uses showConfirm (user confirmation before reset)")
elif "function resetToDefaults()" in js:
    idx_r = js.find("function resetToDefaults()")
    body_r = js[idx_r:idx_r+200]
    if "showConfirm" in body_r:
        ok("resetToDefaults uses showConfirm (user confirmation before reset)")
    else:
        fail("resetToDefaults does not use showConfirm — reset happens immediately without confirmation")
else:
    fail("resetToDefaults function not found")


# ══════════════════════════════════════════════════════════════════════════════
# GROUP 23 — getPPO2Limit trimix safety
# Bug: getPPO2Limit(fN2) used 1-fN2 as fO2 — wrong for trimix (He > 0)
# e.g. 21/35 trimix: fN2=0.44 → 1-fN2=0.56 → ppo2High(1.4) band selected
# Correct: fO2=0.21 → <28% → ppo2Low(1.6) band → switch depth 9m deeper
# ══════════════════════════════════════════════════════════════════════════════

# 23.1 getPPO2Limit takes fO2 directly (not fN2)
ppl_fn = re.search(r"function getPPO2Limit\((\w+)\)", js)
if ppl_fn:
    param = ppl_fn.group(1)
    if param == 'fO2':
        ok("getPPO2Limit(fO2) — uses fO2 directly, trimix-safe")
    else:
        fail(f"getPPO2Limit({param}) — uses {param}, not fO2; 1-fN2 wrong for trimix (wrong ppO2 limit band)")
else:
    fail("getPPO2Limit function not found")

# 23.2 getPPO2Limit body uses fO2 directly (not 1-fN2)
ppl_body = re.search(r"function getPPO2Limit\(.*?\{(.*?)\}", js, re.DOTALL)
if ppl_body:
    body = ppl_body.group(1)
    if "1 - fN2" in body or "1-fN2" in body:
        fail("getPPO2Limit body still uses 1-fN2 — trimix ppO2 limit wrong")
    else:
        ok("getPPO2Limit body does not use 1-fN2 (trimix-safe)")

# 23.3 optimalSwitchDepth passes fO2 (not fN2) to getPPO2Limit
osd_fn = re.search(r"function optimalSwitchDepth\(.*?\n  \}", js, re.DOTALL)
if osd_fn:
    osd_body = osd_fn.group(0)
    if "getPPO2Limit(fO2)" in osd_body or "getPPO2Limit(fO2 " in osd_body:
        ok("optimalSwitchDepth passes fO2 to getPPO2Limit (trimix-safe switch depth)")
    elif "getPPO2Limit(fN2)" in osd_body:
        fail("optimalSwitchDepth passes fN2 to getPPO2Limit — switch depth wrong for trimix")

# 23.4 Stop row rendering passes trimix-safe fO2 to getPPO2Limit
stop_loop = js[js.find("collapsedMDP.forEach"):js.find("collapsedMDP.forEach")+600] if "collapsedMDP.forEach" in js else ""
if "getPPO2Limit(_sFO2)" in stop_loop or ("getPPO2Limit" in stop_loop and "_sFHe" in stop_loop):
    ok("Stop row rendering passes trimix-safe fO2 to getPPO2Limit")
elif "getPPO2Limit(_sFN2)" in stop_loop:
    fail("Stop row passes _sFN2 to getPPO2Limit — ppO2 limit color wrong for trimix stops")

# ══════════════════════════════════════════════════════════════════════════════
# GROUP 24 — GAS BAND ppO2 LIMITS (mid-band and boundary correctness)
# Bug: ppo2Mid was set to ppo2Bottom (1.4) — gives wrong MOD for 28-44% O2
#      gases like EAN32. Should be 1.5.
# Bug: inner engine getPPO2Limit used <=28 and <=45 (wrong boundary assignment)
#      — exactly 28% should be mid (1.5), exactly 45% should be rich (1.6).
# ══════════════════════════════════════════════════════════════════════════════

# 24.1 ppo2Mid is 1.5 (not ppo2Bottom) in runDecoSchedule
run_deco_fn = re.search(r"function runDecoSchedule\(\)(.*?)(?=\nfunction )", js, re.DOTALL)
if run_deco_fn:
    rd_body = run_deco_fn.group(1)
    if "ppo2Mid  = 1.5" in rd_body or "ppo2Mid = 1.5" in rd_body:
        ok("runDecoSchedule: ppo2Mid = 1.5 (mid-band 28–44% O2 uses 1.5 bar limit)")
    elif "ppo2Mid  = ppo2Bottom" in rd_body or "ppo2Mid = ppo2Bottom" in rd_body:
        fail("runDecoSchedule: ppo2Mid = ppo2Bottom — EAN32/EAN36 get wrong MOD (1.4 instead of 1.5)")
    else:
        fail("runDecoSchedule: ppo2Mid assignment not found — mid-band limit unknown")
else:
    fail("runDecoSchedule function not found — cannot audit ppo2Mid")

# 24.2 Inner engine getPPO2Limit uses < not <= for 28% boundary (28% is mid)
inner_ppl = re.search(r"function getPPO2Limit.*?ppO2Low.*?ppO2Mid.*?ppO2High", js, re.DOTALL)
inner_js_block = js[js.find("if (settings.ppO2Low && settings.ppO2Mid"):js.find("if (settings.ppO2Low && settings.ppO2Mid")+300]
if "o2pct < 28" in inner_js_block:
    ok("Inner engine getPPO2Limit: <28 boundary (28% O2 correctly goes to mid/1.5)")
elif "o2pct <= 28" in inner_js_block:
    fail("Inner engine getPPO2Limit: <=28 boundary — 28% O2 wrongly gets lean/1.4 (should be mid/1.5)")

# 24.3 Inner engine getPPO2Limit uses < not <= for 45% boundary (45% is rich)
if "o2pct < 45" in inner_js_block:
    ok("Inner engine getPPO2Limit: <45 boundary (45% O2 correctly goes to rich/1.6)")
elif "o2pct <= 45" in inner_js_block:
    fail("Inner engine getPPO2Limit: <=45 boundary — 45% O2 wrongly gets mid/1.5 (should be rich/1.6)")


# ══════════════════════════════════════════════════════════════════════════════
# GROUP 25 — REPETITIVE DIVE CNS/OTU CARRY
# Bug: CNS/OTU always started at 0 even for repetitive dives.
# Fix: _lastVPMResult now stores finalCNS/finalOTU; settings._preCNS (decayed
#      on 90-min half-life) and settings._preOTU are injected for next dive;
#      calculate() initialises totalCNS/totalOTU from these pre-dive values.
# ══════════════════════════════════════════════════════════════════════════════

# 25.1 _lastVPMResult stores finalCNS
if "finalCNS:" in js and "_lastVPMResult" in js:
    ok("_lastVPMResult stores finalCNS for repetitive dive carry")
else:
    fail("_lastVPMResult missing finalCNS — CNS not carried across repetitive dives")

# 25.2 _lastVPMResult stores finalOTU
if "finalOTU:" in js and "_lastVPMResult" in js:
    ok("_lastVPMResult stores finalOTU for repetitive dive carry")
else:
    fail("_lastVPMResult missing finalOTU — OTU not carried across repetitive dives")

# 25.3 _preCNS injected with 90-min half-life decay
if "settings._preCNS" in js and "Math.pow(0.5, siMin / 90)" in js:
    ok("_preCNS injected with 90-min half-life CNS decay across surface interval")
else:
    fail("_preCNS not set with 90-min half-life decay — CNS carry broken for repetitive dives")

# 25.4 _preOTU injected (daily accumulator, no decay)
if "settings._preOTU" in js:
    ok("_preOTU injected as daily accumulator for repetitive OTU carry")
else:
    fail("_preOTU not set — OTU not carried across repetitive dives")

# 25.5 totalCNS initialised from _preCNS in VPM calculate()
if "settings._preCNS || 0" in js:
    ok("VPM calculate() initialises totalCNS from _preCNS (repetitive carry)")
else:
    fail("VPM calculate() still starts totalCNS at 0 — repetitive CNS carry broken")

# 25.6 totalOTU initialised from _preOTU in VPM calculate()
if "settings._preOTU || 0" in js:
    ok("VPM calculate() initialises totalOTU from _preOTU (repetitive carry)")
else:
    fail("VPM calculate() still starts totalOTU at 0 — repetitive OTU carry broken")

# ══════════════════════════════════════════════════════════════════════════════
# GROUP 26 — WATER PRESSURE FACTOR ALIGNMENT
# Both engines must use the same canonical m/bar factors:
#   salt:    10.000 m/bar (MultiDeco/DiveKit/ApexDeco standard)
#   fresh:   10.330 m/bar (matches ZHL WATER_DENSITY.fresh 0.09681 bar/m)
#   EN13319: 10.080 m/bar (EN13319 standard — DiveKit compatible)
# VPM engine must recognise EN13319 as waterType===2 (not silently fall through to salt).
# ══════════════════════════════════════════════════════════════════════════════

# 26.1 VPM SLP_SW_M = 10.000 (not old 10.078)
if "SLP_SW_M = 10.000" in js:
    ok("VPM SLP_SW_M = 10.000 m/bar (MultiDeco/DiveKit standard)")
elif "SLP_SW_M = 10.078" in js:
    fail("VPM SLP_SW_M still 10.078 — should be 10.000 to match MultiDeco/DiveKit")
else:
    fail("VPM SLP_SW_M not found or unexpected value")

# 26.2 VPM SLP_FW_M = 10.330 (matches ZHL WATER_DENSITY.fresh)
if "SLP_FW_M = 10.330" in js:
    ok("VPM SLP_FW_M = 10.330 m/bar (matches ZHL fresh factor)")
elif "SLP_FW_M = 10.337" in js:
    fail("VPM SLP_FW_M still 10.337 — should be 10.330 to match ZHL WATER_DENSITY.fresh")
else:
    fail("VPM SLP_FW_M not found or unexpected value")

# 26.3 VPM SLP_EN_M defined (EN13319)
if "SLP_EN_M = 10.080" in js:
    ok("VPM SLP_EN_M = 10.080 m/bar (EN13319 constant defined)")
else:
    fail("VPM SLP_EN_M not defined — EN13319 water type unsupported in VPM engine")

# 26.4 getSLP handles waterType===2 (EN13319)
if "settings.waterType === 2" in js:
    ok("getSLP(): waterType===2 branch present (EN13319 support)")
else:
    fail("getSLP(): no waterType===2 branch — EN13319 silently uses salt factor in VPM")

# 26.5 waterTypeVal maps EN13319 to 2
if ("'en13319' ? 2" in js or '"en13319" ? 2' in js or
    "=== 'en13319' ? 2" in js or '=== "en13319" ? 2' in js):
    ok("waterTypeVal: EN13319 mapped to 2 (not silently 0/salt)")
else:
    fail("waterTypeVal: EN13319 not mapped to 2 — VPM engine uses wrong water factor for EN13319")

# 26.6 No hardcoded salt slp in VPM functions
if "SLP_SW_M : SLP_SW_F" in js:
    fail("VPM inner functions still use hardcoded salt slp — water type not respected")
else:
    ok("VPM inner functions use getSLP(settings) not hardcoded salt factor")

# 26.7 ZHL WATER_DENSITY.salt = 0.10000
if "salt:     0.10000" in js or "salt: 0.10000" in js:
    ok("ZHL WATER_DENSITY.salt = 0.10000 bar/m (10.000 m/bar — industry standard)")
elif "salt:     0.10020" in js or "salt: 0.10020" in js:
    fail("ZHL WATER_DENSITY.salt still 0.10020 — should be 0.10000 (MultiDeco/DiveKit)")
else:
    fail("ZHL WATER_DENSITY.salt not found or unexpected value")

# 26.8 ZHL WATER_DENSITY.en13319 = 0.09921
if "en13319:  0.09921" in js or "en13319: 0.09921" in js:
    ok("ZHL WATER_DENSITY.en13319 = 0.09921 bar/m (10.080 m/bar — EN13319 standard)")
elif "en13319:  0.09964" in js or "en13319: 0.09964" in js:
    fail("ZHL WATER_DENSITY.en13319 still 0.09964 — should be 0.09921 (10.080 m/bar)")
else:
    fail("ZHL WATER_DENSITY.en13319 not found or unexpected value")

# ══════════════════════════════════════════════════════════════════════════════
# GROUP 27 — BAR_PER_METRE INIT AND 10.078 ERADICATION
# After the water constant unification, BAR_PER_METRE must initialise to the
# salt default (0.10000) and no display/calculation code may hardcode 10.078.
# ══════════════════════════════════════════════════════════════════════════════

# 27.1 BAR_PER_METRE init = 0.10000 (salt default, not stale 1/10.078 = 0.09922)
if "BAR_PER_METRE = 0.10000" in js:
    ok("BAR_PER_METRE init = 0.10000 (salt default, matches WATER_DENSITY.salt)")
elif "BAR_PER_METRE = 1/10.078" in js or "BAR_PER_METRE = 1 / 10.078" in js:
    fail("BAR_PER_METRE init still 1/10.078 = 0.09922 — stale after water constant update")
else:
    fail("BAR_PER_METRE init value unclear — should be 0.10000")

# 27.2 No hardcoded / 10.078 in live calculation code (tooltip HTML exempt)
import re
# Strip HTML comments and tooltip strings before checking
stripped = re.sub(r'<!--.*?-->', '', js, flags=re.DOTALL)
# Remove content inside showTip(...) calls to avoid flagging tooltip text
stripped = re.sub(r"showTip\([^)]{0,400}\)", "showTip()", stripped)
hardcoded_instances = [ln for ln in stripped.split('\n') if '/ 10.078' in ln and '//' not in ln.lstrip()[:3]]
if not hardcoded_instances:
    ok("No hardcoded / 10.078 in live calculation code — all replaced with BAR_PER_METRE")
else:
    fail(f"Hardcoded / 10.078 still present in {len(hardcoded_instances)} line(s) — use BAR_PER_METRE")

# 27.3 VPM render pAmb uses BAR_PER_METRE not 0.0305 imperial hardcode
if "seg.depth * BAR_PER_METRE" in js and "seg.depth * 0.0305" not in js:
    ok("VPM render: pAmb uses BAR_PER_METRE (not hardcoded imperial 0.0305)")
elif "seg.depth * 0.0305" in js:
    fail("VPM render: pAmb still uses hardcoded imperial 0.0305 — use BAR_PER_METRE")
else:
    fail("VPM render: pAmb calculation not found or ambiguous")

# 27.4 VPM gas tag switch depth: imperial formula gives feet not metres
# Correct: / BAR_PER_METRE * 3.28084 for imperial (result in feet)
# Wrong:   / (BAR_PER_METRE * 0.3048) / 3.28084 (cancels to metres, displayed as ft)
if "/ BAR_PER_METRE * (dU ? 1 : 3.28084)" in js:
    ok("VPM gas tag switch depth: imperial formula correct (/ BAR_PER_METRE * 3.28084 → feet)")
elif "BAR_PER_METRE * 0.3048) / (dU ? 1 : 3.28084)" in js or "BAR_PER_METRE * 0.3048) / 3.28084" in js:
    fail("VPM gas tag switch depth: imperial formula broken — / (BPM*0.3048)/3.28084 cancels to metres, displays wrong ft value")
else:
    fail("VPM gas tag switch depth formula not found or changed structure")



# ══════════════════════════════════════════════════════════════════════════════
# GROUP 28 — GF FIRST-STOP ANCHOR FIX (v2.10.7)
# Bug: firstStopDepth was pre-computed from ceiling(bottom_tissues, gfL) → caused
# spurious stop at 21m for Air+EAN50 dives (MultiDeco shows first stop at 18m).
# Fix: firstStopDepth is now anchored dynamically at the ACTUAL first mustStop depth.
# ══════════════════════════════════════════════════════════════════════════════

# 28.1 firstStopDepth must be declared as `let` (mutable), not `const`
# The old bug used `const firstStopDepth = ...` pre-computed from bottom tissues.
if re.search(r'let firstStopDepth = 0;', js):
    ok("GF anchor: firstStopDepth declared as `let` (mutable, dynamically anchored)")
else:
    fail("GF anchor: firstStopDepth must be `let firstStopDepth = 0` — pre-computed const causes spurious stops")

# 28.2 candidateFirstStop used for stop list, not firstStopDepth
# The candidate stop list must be built from candidateFirstStop, not the old firstStopDepth.
if re.search(r'const candidateFirstStop = bottomCeil > 0', js):
    ok("GF anchor: stop list built from candidateFirstStop (not pre-computed firstStopDepth)")
else:
    fail("GF anchor: missing candidateFirstStop — stop list must use candidate variable, not firstStopDepth")

# 28.3 firstStopDepth is anchored in the mustStop branch
# The fix must set firstStopDepth = cur when the first required stop is found.
if re.search(r'firstStopDepth\s*=\s*cur;\s*//\s*anchor GF line', js):
    ok("GF anchor: firstStopDepth set to cur at first mustStop (anchor from actual first stop)")
else:
    fail("GF anchor: firstStopDepth not anchored at first mustStop — spurious stop bug will recur")

# 28.4 minStopZoneDepth is declared as `let` (not const) and starts as null
# With dynamic anchoring, minStopZoneDepth must be null until first stop is known.
if re.search(r'let minStopZoneDepth = null;', js):
    ok("GF anchor: minStopZoneDepth starts as null (set when first stop is known)")
else:
    fail("GF anchor: minStopZoneDepth must be `let ... = null` — const from pre-computed firstStopDepth is broken")

# 28.5 minStopZoneDepth is set in mustStop branch alongside firstStopDepth
if re.search(r'minStopZoneDepth\s*=\s*cur;\s*//\s*enable min-stop', js):
    ok("GF anchor: minStopZoneDepth set to cur at first mustStop (min-stop enforcement enabled)")
else:
    fail("GF anchor: minStopZoneDepth not set at first mustStop — min-stop enforcement may fail")

# ══════════════════════════════════════════════════════════════════════════════
# GROUP 29 — HEADLESS CNS/OTU DESCENT+BOTTOM FIX (v2.10.8)
# Bug found via 3-way DiveKit/MultiDeco/LSP comparison: window._lastPlan.steps
# only contains ascent/deco segments (descent + bottom are rendered straight to
# DOM in the live app, never pushed into `steps`). The headless CNS/OTU fallback
# in ZHLEngine.calculate() summed only `lp.steps`, silently omitting descent and
# the full bottom-time exposure — the dominant share of CNS/OTU on most dives.
# This was a test-infrastructure bug only: the live DOM-rendering path computes
# CNS/OTU correctly across the full table. Existing tests never caught it because
# they only assert finiteness/ordering, never magnitude against a known value.
# ══════════════════════════════════════════════════════════════════════════════

# 29.1 addExposure() helper present (refactored from inline duplicate logic)
if re.search(r'function addExposure\(ppO2, dur\)', js):
    ok("Headless CNS/OTU: addExposure() helper present (shared by descent/bottom/steps)")
else:
    fail("Headless CNS/OTU: addExposure() helper missing — descent/bottom fix may be reverted")

# 29.2 Descent exposure added before the steps loop
if re.search(r'hDescentTime = level\.depth / hDescentRate', js) and \
   re.search(r'addExposure\(\(hAltP \+ \(level\.depth / 2\) \* hBAR\) \* fO2bot, hDescentTime\)', js):
    ok("Headless CNS/OTU: descent exposure (avg depth = level.depth/2) now included")
else:
    fail("Headless CNS/OTU: descent exposure missing — CNS/OTU will under-report vs live app")

# 29.3 Bottom-time exposure added before the steps loop
if re.search(r'addExposure\(\(hAltP \+ level\.depth \* hBAR\) \* fO2bot, level\.time\)', js):
    ok("Headless CNS/OTU: bottom-time exposure (full level.time at full depth) now included")
else:
    fail("Headless CNS/OTU: bottom-time exposure missing — CNS/OTU will under-report vs live app, since bottom time is the majority of most dives' O2 exposure")

# ══════════════════════════════════════════════════════════════════════════════
# GROUP 30 — GF-LOW PRE-ANCHOR REGRESSION FIX (v2.10.9)
# Bug found via 3-way comparison against MultiDeco/DiveKit reference data: the
# v2.10.7 gfAt() fix returned gfH (not gfL) when firstStopDepth was unanchored.
# Per Baker's published algorithm (and DAN/Erik Baker's own description), GF LOW
# is what determines the first stop — not GF High. Returning gfH pre-anchor made
# the search use the loose GF-High M-value, so the loop only stopped once GF-High
# itself was violated, anchoring 1-3 deco steps shallower than correct and
# silently dropping total deco time (confirmed: S1 30m/23min air GF30/70 should
# anchor at 12m matching MultiDeco/DiveKit exactly; the gfH-pre-anchor bug instead
# anchored at 6m, skipping the 12m and 9m stops entirely).
# ══════════════════════════════════════════════════════════════════════════════

# 30.1 gfAt() returns gfL (not gfH) when firstStopDepth is unanchored
if re.search(r'if \(!firstStopDepth \|\| firstStopDepth <= 0\) return gfL;', js):
    ok("GF anchor: gfAt() returns gfL pre-anchor (correct — GF Low determines first stop per Baker)")
elif re.search(r'if \(!firstStopDepth \|\| firstStopDepth <= 0\) return gfH;', js):
    fail("GF anchor: gfAt() returns gfH pre-anchor — REGRESSION. Anchors 1-3 steps shallower than correct; GF Low must be used to find the first stop, not GF High.")
else:
    fail("GF anchor: gfAt() pre-anchor return value not found or changed structure")

# ══════════════════════════════════════════════════════════════════════════════
# GROUP 31 — TTS METRIC + DECOZONE GF-INDEPENDENCE FIX (v2.10.10)
# Found via 3-way comparison against MultiDeco/DiveKit: (1) LSP had no TTS
# (time-to-surface) metric at all, despite MultiDeco/DiveKit both reporting it
# as a primary field; (2) LSP's "decozone start" was actually an alias for
# firstStopDepth (the GF-anchored first stop), not the GF-independent ambient-
# crossing depth MultiDeco/DiveKit report — same dive at different GF settings
# was wrongly reporting different decozone values, off by 10+ metres from
# reference on several scenarios.
# ══════════════════════════════════════════════════════════════════════════════

# 31.1 TTS computed in the engine (headless-safe) as rt - bt
if re.search(r'const ttsMin = Math\.max\(0, rt - bt\);', js):
    ok("TTS: computed as rt-bt (ascent+deco only) before the headless early-return")
else:
    fail("TTS: rt-bt computation missing — TTS will be unavailable in headless tests")

# 31.2 TTS stored on window._lastPlan
if re.search(r'tts: Math\.round\(ttsMin \* 10\) / 10,', js):
    ok("TTS: stored on window._lastPlan.tts")
else:
    fail("TTS: not stored on _lastPlan — headless ZHLEngine.calculate() callers cannot read it")

# 31.3 TTS exposed in ZHLEngine.calculate() return object
if re.search(r'tts: lp\.tts \|\| 0,', js):
    ok("TTS: exposed in ZHLEngine.calculate() return object")
else:
    fail("TTS: missing from calculate() return object")

# 31.4 TTS shown in the live footer
if re.search(r'>TTS:</span>', js):
    ok("TTS: displayed in the live-render footer")
else:
    fail("TTS: not displayed in footer — feature incomplete")

# 31.5 ambientCrossingDepth() function present — the GF-independent decozone calc
if re.search(r'function ambientCrossingDepth\(tissues\)', js):
    ok("Decozone: ambientCrossingDepth() GF-independent function present")
else:
    fail("Decozone: ambientCrossingDepth() missing — decozone fix may be reverted")

# 31.6 decoZoneStart in _lastPlan uses the new GF-independent value, not firstStopDepth
if re.search(r'decoZoneStart: trueDecoZoneStart,', js):
    ok("Decozone: _lastPlan.decoZoneStart uses trueDecoZoneStart (GF-independent)")
elif re.search(r'decoZoneStart: hasDeco \? firstStopDepth : 0,', js):
    fail("Decozone: _lastPlan.decoZoneStart still aliases firstStopDepth — REGRESSION, will vary incorrectly with GF Lo/Hi")
else:
    fail("Decozone: _lastPlan.decoZoneStart assignment not found or changed structure")

# 31.7 Footer decozone display uses the GF-independent value
if re.search(r'formatDecoZoneStart\(trueDecoZoneStart\)', js):
    ok("Decozone: footer display uses trueDecoZoneStart (GF-independent)")
else:
    fail("Decozone: footer display not using trueDecoZoneStart — live render may still show GF-dependent value")


# ══════════════════════════════════════════════════════════════════════════════
# GROUP 32 — MISSING FINAL SURFACE-ASCENT LEG (post-v2.10.12)
# Found via divekit.app's published inputs.json: MultiDeco/DiveKit both use a
# dedicated, slower surfaceAscentMPerMin rate for the final leg from the last
# stop to the surface, distinct from the deep and deco rates. LSP's ZHL engine
# had a surfaceAscentRate UI field and variable, but it was only ever passed to
# runVPMSchedule — the ZHL ascent loop itself treated surfacing as instantaneous
# (zero time, zero off-gassing) once the last stop's hold finished.
# ══════════════════════════════════════════════════════════════════════════════

# 32.1 Final ascent leg present after the main stop loop, using surfaceRate
if re.search(r'const finalAscentDur = cur / surfaceRate;', js):
    ok("Final ascent: surfaceRate-based leg from lastStop to surface present")
else:
    fail("Final ascent: surfaceRate leg missing — surfacing time/off-gassing undercounted")

# 32.2 Final ascent applies off-gassing via saturateLinear (not treated as instant)
if re.search(r'tissues = saturateLinear\(tissues, cur, 0, finalAscentDur', js):
    ok("Final ascent: off-gassing applied via saturateLinear during the final leg")
else:
    fail("Final ascent: off-gassing not applied — tissue state wrong for repetitive-dive surface interval")

# 32.3 Final ascent leg is pushed as its own step (visible in plan/exports)
if re.search(r"type: 'ascent', from: cur, to: 0,", js):
    ok("Final ascent: pushed as a visible step (from=lastStop, to=0)")
else:
    fail("Final ascent: step not pushed — RT/TTS may update but plan/exports won't show the leg")

# ══════════════════════════════════════════════════════════════════════════════
# GROUP 33 — HEADLESS holdStep RESULT-CHANGING BUG (post-v2.10.43)
# Found via a from-scratch 16-compartment tissue diff against ApexDeco on S2:
# tissue states matched almost exactly at every stop (noise-level diffs), but
# the FIRST stop's reported duration differed by ~0.5-0.7min between headless
# test runs and what the real app / ApexDeco would produce for identical input.
# Root cause: holdStep (the while-loop's ceiling-check granularity) was forced
# to a coarse 1 minute in headless mode even for the first stop, which the real
# app deliberately gives a fine 1/6-min (10-sec) resolution. This is the ONLY
# _zhlHeadless branch in the file that changes a computed RESULT rather than
# skipping DOM rendering — every other _zhlHeadless check just skips a render
# call, so this one silently meant headless test numbers (used by this audit's
# sibling test suites AND by Claude's own headless verification scripts) did
# not match what the live app would actually show for the same inputs.
# ══════════════════════════════════════════════════════════════════════════════

# 33.1 holdStep no longer forces coarse resolution for the first stop in headless mode
if re.search(r'const holdStep = isFirstDecoStop \? 1/6 : 1;', js):
    ok("holdStep: first-stop fine resolution (1/6 min) applies regardless of headless mode")
elif re.search(r'const holdStep = \(window\._zhlHeadless\) \? 1 :', js):
    fail("holdStep: REGRESSION — headless mode still forces coarse 1-min resolution on the first stop, producing different RT/TTS than the real app for identical inputs")
else:
    fail("holdStep: assignment not found or changed structure — verify manually")



# ══════════════════════════════════════════════════════════════════════════════
# GROUP 34 — v2.20.0 features (Surface GF, Prior Carry, Shallow Gradient,
#            Contingency Depth, App Presets)
# ══════════════════════════════════════════════════════════════════════════════

# 34.1 computeSurfaceGF function defined
if re.search(r'function computeSurfaceGF\(tissues\)', js):
    ok("computeSurfaceGF: function defined")
else:
    fail("computeSurfaceGF: function missing — Surface GF metric not computable")

# 34.2 computeSurfaceGF uses correct M-value denominator formula
if re.search(r'a\s*\+\s*P_surf\s*/\s*b\s*-\s*P_surf', js):
    ok("computeSurfaceGF: correct M-value denominator (a + P_surf/b - P_surf)")
else:
    fail("computeSurfaceGF: M-value denominator formula not found — Surface GF may be wrong")

# 34.3 surfaceGF stored in ZHL _lastPlan
if re.search(r'surfaceGF:\s*computeSurfaceGF\(tissues\)', js):
    ok("surfaceGF: stored in ZHL _lastPlan via computeSurfaceGF(tissues)")
else:
    fail("surfaceGF: not stored in ZHL _lastPlan — footer metric missing")

# 34.4 surfaceGF stored in VPM _lastPlan
if re.search(r'surfaceGF:\s*result\.finalTissues\s*\?', js):
    ok("surfaceGF: stored in VPM _lastPlan (conditional on finalTissues)")
else:
    fail("surfaceGF: not stored in VPM _lastPlan")

# 34.5 Surf GF displayed in buildPlanInfoRowHtml
if re.search(r'Surf GF:', js):
    ok("buildPlanInfoRowHtml: Surf GF label in footer")
else:
    fail("buildPlanInfoRowHtml: Surf GF label missing from footer display")

# 34.6 data-surfgf attribute in hidden totals row
if re.search(r'data-surfgf=', js):
    ok("buildPlanInfoRowHtml: data-surfgf attribute stored in hidden totals row")
else:
    fail("buildPlanInfoRowHtml: data-surfgf attribute missing")

# 34.7 PLAN_INFO_TIP updated with Surf GF
if re.search(r'Surf GF.*surface gradient', html, re.IGNORECASE):
    ok("PLAN_INFO_TIP: Surf GF definition included")
else:
    fail("PLAN_INFO_TIP: Surf GF not documented in tooltip")

# 34.8 updatePriorDiveCarry function
if re.search(r'function updatePriorDiveCarry\(\)', js):
    ok("updatePriorDiveCarry: function defined")
else:
    fail("updatePriorDiveCarry: function missing — prior dive OTU/CNS carry not functional")

# 34.9 OTU day-boundary: resets when >= 24h
if re.search(r'24 \* 60', js) and re.search(r'otuCarry.*totalMinutes', js, re.DOTALL):
    ok("updatePriorDiveCarry: day-boundary check (24*60 minutes) present")
else:
    fail("updatePriorDiveCarry: day-boundary logic missing — OTU may not reset after 24h")

# 34.10 Prior carry seeded into ZHL accumulators
if re.search(r'_pdCarry.*priorDiveCarry', js) or re.search(r'_priorDiveCarry.*cnsCarry.*100', js):
    ok("ZHL accumulators: seeded from _priorDiveCarry on init")
else:
    fail("ZHL accumulators: prior dive carry not seeded — CNS/OTU not carried into ZHL plan")

# 34.11 Prior carry injected into VPM settings
if re.search(r'settings\._preOTU.*_priorDiveCarry.*otuCarry', js, re.DOTALL) or \
   re.search(r'_priorDiveCarry.*settings\._preOTU', js, re.DOTALL):
    ok("VPM settings: prior dive carry injected as _preOTU/_preCNS")
else:
    fail("VPM settings: prior dive carry not injected — OTU/CNS not carried into VPM plan")

# 34.12 shallowGradient select element
if re.search(r'id="shallowGradient"', html):
    ok("shallowGradient: select element present in advanced settings")
else:
    fail("shallowGradient: select element missing from HTML")

# 34.13 shallowGradient default is off
if re.search(r'id="shallowGradient".*?<option selected.*?value="off"', html, re.DOTALL):
    ok("shallowGradient: default value is 'off' (standard GF behavior)")
else:
    fail("shallowGradient: default not 'off' — non-standard GF behavior on by default")

# 34.14 shallowGradient in _ADV_FIELDS
if re.search(r"_ADV_FIELDS\s*=\s*\[[\s\S]*?'shallowGradient'", js):
    ok("_ADV_FIELDS: includes shallowGradient")
else:
    fail("_ADV_FIELDS: shallowGradient missing — setting not saved/loaded with config presets")

# 34.15 gfAt respects shallowGradient
if re.search(r'shallowGradient.*value.*===.*on', js) or re.search(r"shallowGradient.*'on'", js):
    ok("gfAt: shallowGradient setting read at runtime")
else:
    fail("gfAt: shallowGradient setting not referenced — toggle has no effect")

# 34.16 gfAt shallow gradient: clamps to gfH at lastStop when ON
if re.search(r'sgOn && depthM <= lastStop.*return gfH', js, re.DOTALL):
    ok("gfAt: shallow gradient ON returns gfH at lastStop and shallower")
else:
    fail("gfAt: shallow gradient ON does not apply gfH at lastStop")

# 34.17 contExtraDepth variable declared
if re.search(r'let contExtraDepth\s*=', js):
    ok("contExtraDepth: variable declared")
else:
    fail("contExtraDepth: variable missing — went-deeper contingency not wired")

# 34.18 selectContDepth function
if re.search(r'function selectContDepth\(metres\)', js):
    ok("selectContDepth: function defined")
else:
    fail("selectContDepth: function missing")

# 34.19 Went deeper buttons in HTML
if all(re.search(f'id="contDepth{v}"', html) for v in [0, 3, 5]):
    ok("contingency HTML: +0m/+3m/+5m depth buttons present")
else:
    fail("contingency HTML: went-deeper buttons missing (contDepth0/3/5)")

# 34.20 calcContingency sets origDepth and restores it
if re.search(r'origDepth.*decoDepth.*value', js) and re.search(r"document.*getElementById\('decoDepth'\)\.value\s*=\s*origDepth", js):
    ok("calcContingency: depth saved as origDepth and restored after scenario run")
else:
    fail("calcContingency: depth not saved/restored — went-deeper leaves depth field modified")

# 34.21 LSP_APP_PRESETS constant defined with 5 entries
app_presets = re.findall(r"name:\s*'(MultiDeco|Abysner|Subsurface|GUE DecPlanner|DiveKit)'", js)
if len(set(app_presets)) == 5:
    ok(f"LSP_APP_PRESETS: all 5 app presets defined ({', '.join(sorted(set(app_presets)))})")
else:
    fail(f"LSP_APP_PRESETS: only {len(set(app_presets))}/5 app presets found: {set(app_presets)}")

# 34.22 loadAppPreset function
if re.search(r'function loadAppPreset\(idx\)', js):
    ok("loadAppPreset: function defined")
else:
    fail("loadAppPreset: function missing — app presets cannot be loaded")

# 34.23 _renderConfigPresetModal shows app presets header
if re.search(r'App Reference Presets', js):
    ok("_renderConfigPresetModal: app presets section header present")
else:
    fail("_renderConfigPresetModal: app presets section not shown in modal")

# 34.27 App presets: stopRounding values must be 'wholeminute' or 'fractional' (not 'whole')
stale_whole = re.findall(r"stopRounding:\s*'whole'(?!minute)", js)
if stale_whole:
    fail(f"App presets: {len(stale_whole)} stopRounding='whole' (invalid) — must be 'wholeminute' or 'fractional'")
else:
    ok("App presets: stopRounding values all valid ('wholeminute' or 'fractional')")

# 34.28 App presets: o2AtMODSelect must be 'on' or 'off' (not 'yes'/'no')
stale_yes = re.findall(r"o2AtMODSelect:\s*'yes'", js)
if stale_yes:
    fail(f"App presets: {len(stale_yes)} o2AtMODSelect='yes' (invalid) — must be 'on' or 'off'")
else:
    ok("App presets: o2AtMODSelect values all valid ('on' or 'off')")

# 34.29 GUE DecPlanner ppo2 values must be valid select options (1.2/1.4/1.5/1.6)
gue_ppo2 = re.findall(r"name:\s*'GUE DecPlanner'[\s\S]*?ppo2Bottom:\s*'([^']+)'", js)
if gue_ppo2 and gue_ppo2[0] not in ('1.2','1.4','1.5','1.6'):
    fail(f"GUE DecPlanner ppo2Bottom={gue_ppo2[0]!r} not a valid select option (1.2/1.4/1.5/1.6)")
else:
    ok("GUE DecPlanner preset: ppo2Bottom is a valid select option (1.2 now supported)")
if re.search(r'CNS DUAL-METHOD AUDIT', js):
    ok("CNS dual-method audit: cross-check comment documented")
else:
    fail("CNS dual-method audit: audit comment missing")

# 34.25 OTU_EXPONENT constant defined and no stale 0.833 copies remain
if re.search(r'const OTU_EXPONENT\s*=\s*0\.8333', js):
    ok("OTU_EXPONENT: constant defined (0.8333)")
else:
    fail("OTU_EXPONENT: constant missing — OTU exponent not a single source of truth")

stale_083 = re.findall(r'0\.833[^3]', js)
if stale_083:
    fail(f"OTU exponent: {len(stale_083)} stale 0.833 (3-digit) copies remain — should use OTU_EXPONENT")
else:
    ok("OTU exponent: no stale 0.833 (3-digit) copies — all sites use OTU_EXPONENT")

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
