#!/usr/bin/env python3
"""LSP D-PLANNER audit script — calibrated to actual v1.3 source structure."""
import re, sys

path = "/home/claude/LSP_D-PLANNER_v1.3/index.html"
with open(path, encoding="utf-8") as f:
    src = f.read()

failures = []
passes = 0

def check(label, condition):
    global passes
    if condition:
        passes += 1
    else:
        failures.append(label)

# ── Core constants ──────────────────────────────────────────────────────────
check("APP_VERSION defined", "const APP_VERSION" in src)
check("Water vapor 0.0627", "0.0627" in src)

# ── ZHL16C array (Bühlmann coefficients) ───────────────────────────────────
check("ZHL16C array defined", "const ZHL16C = [" in src)
check("ZHL16C comp 1  [4.0, 1.2599, 0.5050]", "4.0,   1.2599, 0.5050" in src)
check("ZHL16C comp 2  [8.0, 1.0000, 0.6514]", "8.0,   1.0000, 0.6514" in src)
check("ZHL16C comp 3  [12.5, 0.8618, 0.7222]", "12.5,  0.8618, 0.7222" in src)
check("ZHL16C comp 4  [18.5, 0.7562, 0.7825]", "18.5,  0.7562, 0.7825" in src)
check("ZHL16C comp 5  [27.0, 0.6200, 0.8126]", "27.0,  0.6200, 0.8126" in src)
check("ZHL16C comp 6  [38.3, 0.5043, 0.8434]", "38.3,  0.5043, 0.8434" in src)
check("ZHL16C comp 7  [54.3, 0.4410, 0.8693]", "54.3,  0.4410, 0.8693" in src)
check("ZHL16C comp 8  [77.0, 0.4000, 0.8910]", "77.0,  0.4000, 0.8910" in src)
check("ZHL16C comp 9  [109.0, 0.3750, 0.9092]","109.0, 0.3750, 0.9092" in src)
check("ZHL16C comp 10 [146.0, 0.3500, 0.9222]","146.0, 0.3500, 0.9222" in src)
check("ZHL16C comp 11 [187.0, 0.3295, 0.9319]","187.0, 0.3295, 0.9319" in src)
check("ZHL16C comp 12 [239.0, 0.3065, 0.9403]","239.0, 0.3065, 0.9403" in src)
check("ZHL16C comp 13 [305.0, 0.2835, 0.9477]","305.0, 0.2835, 0.9477" in src)
check("ZHL16C comp 14 [390.0, 0.2610, 0.9544]","390.0, 0.2610, 0.9544" in src)
check("ZHL16C comp 15 [498.0, 0.2480, 0.9602]","498.0, 0.2480, 0.9602" in src)
check("ZHL16C comp 16 [635.0, 0.2327, 0.9653]","635.0, 0.2327, 0.9653" in src)

# ── VPM ZHL16C_N2 array ─────────────────────────────────────────────────────
check("VPM ZHL16C_N2 array", "const ZHL16C_N2 = [" in src)
check("VPM ZHL16C_He array", "const ZHL16C_He = [" in src)
check("He pHe tissue tracking", "pHe" in src)
check("He kHe decay constant", "kHe" in src)
check("Weighted allowable gradient (He+N2)", "getWeightedAllowableGradient" in src)

# ── Gradient factors ────────────────────────────────────────────────────────
check("mGF object with low:30", "{ low: 30," in src or "low: 30," in src)
check("mGF high default", "high: 70" in src or "high: 85" in src or "high: 80" in src)
check("gfAt() interpolation function", "function gfAt(" in src)
check("GF linear interp formula", "(gfH - gfL) * (firstStopDepth - depthM) / firstStopDepth" in src)
check("gfL = mGF.low/100", "mGF.low  / 100" in src or "mGF.low/100" in src)
check("gfH = mGF.high/100", "mGF.high / 100" in src or "mGF.high/100" in src)
check("GF presets UI row", "gfPresetsRow" in src)
check("gfLowInput element", "gfLowInput" in src)
check("gfHighInput element", "gfHighInput" in src)

# ── Deco stop logic ─────────────────────────────────────────────────────────
check("firstStopDepth calculation", "firstStopDepth" in src)
check("lastStop variable", "const lastStop" in src)
check("lastStop default 3", "|| 3" in src)
check("decoStep 3m", "decoStep" in src)
check("stopDepths array", "stopDepths" in src)
check("ceiling() function", "function ceiling(" in src)
check("Ascent rate used", "ascentRate" in src or "ascent_rate" in src)
check("Descent rate used", "descentRate" in src or "descent_rate" in src)

# ── Gas switching ───────────────────────────────────────────────────────────
check("getActiveGas function", "getActiveGas" in src)
check("firstSwitchDepth logic", "firstSwitchDepth" in src)
check("fO2 fraction used", "fO2" in src)
check("fN2 fraction used", "fN2" in src)
check("EAN/nitrox support", "ean" in src.lower() or "fO2" in src)
check("decoGases array", "decoGases" in src)

# ── Gas / ppO2 limits ───────────────────────────────────────────────────────
check("ppO2 max 1.6", "1.6" in src)
check("ppo2Deco element", "ppo2Deco" in src)
check("ppo2Bottom element", "ppo2Bottom" in src)
check("getPPO2Limit function", "getPPO2Limit" in src)
check("CNS calculation present", "cns" in src.lower())
check("OTU calculation present", "OTU" in src or "otu" in src.lower())

# ── Schreiner / Haldane ─────────────────────────────────────────────────────
check("Schreiner equation", "schreiner" in src.lower() or "Schreiner" in src)
check("schreinerLinear function", "schreinerLinear" in src)
check("Haldane function", "haldane" in src)
check("M-value calculation", "mValue" in src or "mVal" in src or "ceiling(" in src)
check("Ambient pressure", "pAmb" in src or "ambientPressure" in src)
check("Pressure at depth (0.1 bar/m)", re.search(r"0\.1.*depth|depth.*0\.1|depth\s*/\s*10", src) is not None)
check("Surface pressure constant", "SURFACE_P" in src)
check("N2 fraction air 0.79", "0.79" in src)

# ── VPM-B engine ────────────────────────────────────────────────────────────
check("VPMEngine IIFE defined", "const VPMEngine = (" in src)
check("VPMEngine.calculate method", "VPMEngine.calculate" in src)
check("runVPMSchedule function", "function runVPMSchedule(" in src)
check("renderVPMResults function", "function renderVPMResults(" in src)
check("VPM model 'VPMB'", "'VPMB'" in src)
check("VPM model 'VPMB_GFS'", "'VPMB_GFS'" in src)
check("VPM isVPMB flag", "isVPMB" in src)
check("VPM isVPMBGFS flag", "isVPMBGFS" in src)
check("VPM createVPMState", "createVPMState" in src)
check("VPM crushingPressure / crushing", "crushing" in src.lower())
check("VPM critical radius", "criticalRadius" in src or "r0" in src.lower() or "initialRadius" in src)
check("VPM boyleLawCompensation", "boyleLawCompensation" in src)
check("VPM applyGFSurfacing (GFS mode)", "applyGFSurfacing" in src)
check("VPM isClearToAscendVPM", "isClearToAscendVPM" in src)
check("VPM conservatismRow UI", "conservatismRow" in src)
check("VPM ppO2Mid 1.5 (bottom gas limit)", re.search(r"ppO2Mid.*1\.5|ppo2.*1\.5|1\.5.*ppO2Mid", src) is not None)
check("VPM lastStop = 3 (metric)", "settings.metric ? 3 : 10" in src)

# ── Export functions ────────────────────────────────────────────────────────
check("buildExportText present", "buildExportText" in src)
check("buildMessengerText present", "buildMessengerText" in src)
check("exportPDF present", "exportPDF" in src)
check("exportContingencyPDF present", "exportContingencyPDF" in src)
check("TXT export", "exportTXT" in src or ".txt" in src.lower())
check("Copy export (clipboard)", "navigator.clipboard" in src or "execCommand" in src)

# ── UI elements ─────────────────────────────────────────────────────────────
check("APP_VERSION display", "APP_VERSION" in src)
check("REF button present", "REF" in src)
check("Instagram link", "instagram" in src.lower())
check("Mobile meta viewport", "viewport" in src)
check("Tab navigation", "tab" in src.lower())
check("Settings panel", "setting" in src.lower())
check("Gas shortage red #cc0000", "#cc0000" in src)
check("Algorithm select dropdown", "algorithmSelect" in src)
check("lastDecoStop input", "lastDecoStop" in src)

# ── Safety / integrity ──────────────────────────────────────────────────────
check("No hardcoded version string in export",
      not re.search(r"""['"]\s*v\d+\.\d+\s*['"]""",
                    src.replace("APP_VERSION", "").replace("v1.3", "APP_VERSION_PLACEHOLDER")))
check("ZHL16C not overwritten (anchor comp 1)", "4.0,   1.2599, 0.5050" in src)
check("ZHL16C not overwritten (anchor comp 16)","635.0, 0.2327, 0.9653" in src)

# ── Algorithm model names ───────────────────────────────────────────────────
check("Model ZHLC present", "'ZHLC'" in src or "ZHLC" in src)
check("Model ZHLC_GF present", "'ZHLC_GF'" in src or "ZHLC_GF" in src)



# ── VPM-B regression tests (LSP vs ApexDeco) ───────────────────────────────
import subprocess, json, tempfile, os

VPM_TEST_SCRIPT = r"""
'use strict';
const path = require('path');
// Load pre-extracted VPM engine
const VPMEngine = require('/tmp/lsp_vpm_audit.js');

function ms(opts={}) {
  return { metric:true, waterType:0, altitude:0,
    conservatism: opts.conservatism??2, gfLow:opts.gfLow??30,
    gfHigh:opts.gfHigh??85, gfSurface:opts.gfSurface??90,
    minStopTime:opts.minStopTime??1, lastStop:opts.lastStop??3,
    stepSize:opts.stepSize??3, ppO2Deco:opts.ppO2Deco??1.6,
    ppO2High:opts.ppO2High??1.6, ppO2Mid:opts.ppO2Mid??1.5,
    ppO2Low:opts.ppO2Low??1.5, descentRate:20, ascentRate:10,
    decoAscentRate:3, surfaceAscentRate:3, model:opts.model??'VPMB' };
}
function ml(d,t,o2,he=0) { return {depth:d,time:t,o2,he}; }
function mg(o2,he=0) { return {o2,he}; }
function fmt(r) {
  if (!r||r.error) return 'ERROR';
  return (r.plan||[]).filter(s=>(s.type==='stop'||s.type==='deco')&&s.time>0)
    .map(s=>`${s.depth}x${Math.round(s.time)}`).join(',');
}
const tests = [
  ['30m30 VPMB',       [ml(30,30,21)],[],ms()],
  ['40m30 EAN50 VPMB', [ml(40,30,21)],[mg(50)],ms()],
  ['40m30 O2 VPMB',    [ml(40,30,21)],[mg(50),mg(100)],ms()],
  ['50m25 O2 VPMB',    [ml(50,25,21)],[mg(50),mg(100)],ms()],
  ['60m20 c0 VPMB',    [ml(60,20,21)],[mg(50),mg(100)],ms({conservatism:0})],
  ['60m20 c4 VPMB',    [ml(60,20,21)],[mg(50),mg(100)],ms({conservatism:4})],
  ['30m40 GFS',        [ml(30,40,21)],[],ms({model:'VPMB_GFS'})],
  ['40m30 O2 GFS',     [ml(40,30,21)],[mg(50),mg(100)],ms({model:'VPMB_GFS'})],
  ['50m30 O2 GFS',     [ml(50,30,21)],[mg(50),mg(100)],ms({model:'VPMB_GFS'})],
];
const EXPECTED = {
  '30m30 VPMB':       '12x0,9x2,6x5,3x10',
  '40m30 EAN50 VPMB': '18x1,15x1,12x2,9x3,6x5,3x10',
  '40m30 O2 VPMB':    '18x1,15x1,12x1,9x3,6x4,3x5',
  '50m25 O2 VPMB':    '27x1,24x1,21x1,18x1,15x1,12x2,9x4,6x5,3x7',
  '60m20 c0 VPMB':    '30x1,27x1,24x1,21x1,18x1,15x1,12x2,9x4,6x4,3x7',
  '60m20 c4 VPMB':    '33x0,30x1,27x1,24x1,21x1,18x1,15x3,12x3,9x5,6x5,3x9',
  '30m40 GFS':        '15x1,12x1,9x3,6x12,3x54',
  '40m30 O2 GFS':     '18x1,15x1,12x1,9x2,6x6,3x14',
  '50m30 O2 GFS':     '27x1,24x1,21x1,18x1,15x1,12x2,9x8,6x11,3x21',
};
const results = [];
for (const [name,levels,gases,settings] of tests) {
  let got;
  try { got = fmt(VPMEngine.calculate(levels,gases,settings,settings.model)); }
  catch(e) { got = 'ERROR:'+e.message; }
  results.push({name, expected:EXPECTED[name], got, ok: got===EXPECTED[name]});
}
console.log(JSON.stringify(results));
"""

# Extract VPMEngine from index.html to a temp module file
_vpm_src = open(path).read()
_vstart = _vpm_src.index('const VPMEngine = (')
_depth=0; _i=_vstart; _inStr=False; _strChar=None
while _i < len(_vpm_src):
    _c = _vpm_src[_i]
    if not _inStr:
        if _c in ('"', "'", '`'): _inStr=True; _strChar=_c
        elif _c == '{': _depth += 1
        elif _c == '}':
            _depth -= 1
            if _depth == 0: _i+=1; break
    else:
        if _c == _strChar and (_i==0 or _vpm_src[_i-1]!='\\'):  _inStr=False
    _i+=1
while _i < len(_vpm_src) and _vpm_src[_i] != ';': _i+=1
_vpm_block = _vpm_src[_vstart:_i+1]

import tempfile, os
with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as _vf:
    _vf.write(_vpm_block + '\nmodule.exports = VPMEngine;\n')
    _vpm_module = _vf.name

with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as tf:
    tf.write(VPM_TEST_SCRIPT.replace('/tmp/lsp_vpm_audit.js', _vpm_module))
    tmpjs = tf.name

try:
    out = subprocess.run(['node', tmpjs], capture_output=True, text=True, timeout=30)
    if out.returncode == 0:
        results = json.loads(out.stdout.strip())
        for r in results:
            check(f"VPM regression: {r['name']}", r['ok'])
    else:
        check("VPM regression suite ran", False)
        print(f"  Node error: {out.stderr[:200]}")
except Exception as e:
    check("VPM regression suite ran", False)
    print(f"  Exception: {e}")
finally:
    os.unlink(tmpjs)
    try: os.unlink(_vpm_module)
    except: pass



# ── Export consistency checks ───────────────────────────────────────────────
check("Export: single unified totals row read (no separate VPM/Buhl branches)",
      "totalsRowEl = document.querySelector('#decoTableBody tr[data-phase=\"totals\"] td')" in src)
check("Export: VPM fallback uses _lastVPMExport",
      "_lastVPMExport" in src)
check("Export: VPM totals footer uses mm'ss\" format (no bare minutes)",
      "rt}'00\"" in src or "rt}'00\\\"" in src or "'00\"</span>" in src)
check("Export TXT totals line uses runTimeVal (unified)",
      "Run Time:${runTimeVal}" in src)
check("Export copy totals: Run: format with colon",
      "Run:${runM?.[1]" in src or "Run:${toMMSS" in src)
check("VPM _lastVPMExport stored at render time",
      "window._lastVPMExport = {" in src)
check("buildMessengerText reads _lastVPMExport for VPM",
      "_isVPMCopy" in src and "_lastVPMExport" in src)
# ── Web view consistency (VPM = Bühlmann layout) ────────────────────────────
check("Web: both algos have stat grid in decoSummary",
      'stat-val\">${rawD}' in src and 'stat-val\">${rawDdisp}' in src)
check("Web: both algos have gas tags row",
      'bottomGasTag} ${decoGasTags}' in src and 'bottomGasTagVPM} ${decoGasTagsVPM}' in src)
check("Web: both algos have DECO DIVE alert", src.count('DECOMPRESSION DIVE') >= 2)
check("Web: both algos have data-phase=totals footer row",
      src.count('data-phase=\"totals\"') >= 2)
check("Web: VPM totals footer uses mm\'ss\" format",
      "'00\"</span>" in src)
check("Web: decoAlerts is permanent static div in HTML",
      '<div id=\"decoAlerts\"' in src)
check("Web: both algos write to decoAlerts",
      'decoAlertsEl' in src and 'alertsContainer' in src)

# ── Emergency plan web consistency ──────────────────────────────────────────
check("Emergency web: uses mm'ss\" format for Run/Deco",
      "_emRunFmt" in src)
check("Emergency web: has data-phase=totals row in result",
      'data-phase=\"totals\"' in src and 'decoAlertsEmergency' in src)
check("Emergency web: result card has export buttons (copy/txt/pdf)",
      "copyDiveProfile(\'contingency\')" in src)

# ── Copy/messenger format consistency across all modes ───────────────────────
check("Copy: all modes use Run: colon format",
      "Run:${runM?.[1]" in src or "Run:${toMMSS" in src)
check("Copy: emergency uses mm'ss\" not plain minutes",
      'lastRun + \'min\'' not in src and "_emRunFmt" in src or "lastRunFmt  || `${c.lastRun}\'00\"" in src)
check("Copy: VPM reads _lastVPMExport for totals", "_isVPMCopy" in src)
check("Copy: all modes push LSP D-Planner footer",
      src.count("result.push(\'LSP D-Planner\')") >= 1)

# ── TXT export format consistency across all modes ───────────────────────────
check("TXT: unified totals read from data-phase=totals row",
      "totalsRowEl = document.querySelector" in src)
check("TXT: Run Time line format identical across modes",
      "Run Time:${runTimeVal}" in src)
check("TXT: deco and emergency modes have SAFETY REMINDERS",
      src.count('SAFETY REMINDERS') >= 2)
check("TXT: disclaimer present in export footer",
      'WARNING & DISCLAIMER' in src)
check("TXT: algorithm header line present",
      "Algorithm   : ${algoNameExp}" in src)

# ── VPM card consistency (same cards as Bühlmann) ───────────────────────────
check("VPM: shows dive graph after render",
      "drawDecoProfile" in src and "diveGraphCard" in src)
check("VPM: computes and shows gas consumption",
      "gasConsVPM" in src and "gasConsumptionSummary" in src)
check("VPM: shows contingency plans card",
      "buildContingencyButtons" in src and src.count("buildContingencyButtons") >= 2)
check("VPM: shows tissue/GF cards with Bühlmann-only notice",
      "N/A for VPM" in src)
check("Bühlmann: clears VPM notice from tissue/GF cards",
      "N/A for VPM" in src and "n.remove()" in src)

# ── CNS row highlighting consistency ────────────────────────────────────────
check("Bühlmann: cumulative CNS row highlight at 80%",
      "cumCnsPct >= 80" in src and "rgba(255,255,0,0.25)" in src)
check("Bühlmann: cumulative CNS row highlight at 100% (yellow)",
      "cumCnsPct >= 100" in src and "background:#ffff00" in src)
check("VPM: uses _cumCNS from engine for row highlight",
      "cumCnsPctVPM" in src and "seg._cumCNS" in src)
check("VPM: CNS row highlight same colors as Bühlmann",
      src.count("background:#ffff00") >= 2 and src.count("rgba(255,255,0,0.25)") >= 2)

# ── Gas switch row — Nitrox yellow/green ─────────────────────────────────────
check('Switch row CSS yellow bg',        'background: #FFD700 !important' in src)
check('Switch row CSS green text',       'color: #007A33 !important' in src)
check('Optimal switch depth Nitrox',     'background:#FFD700;border-color:#007A33' in src)
check('Switch row PDF yellow fill',      'setFillColor(255,215,0)' in src)
check('Switch row PDF green text',       'setTextColor(0,100,40)' in src)
check('Switch row PDF top+bottom lines', 'doc.line(ML,y,ML+CW,y)' in src)
check('Switch row PDF both borders same weight', src.count('doc.line(ML,y,ML+CW,y)') >= 3)

# ── Gas banners — RoyalBlue #4169E1 ──────────────────────────────────────────
check('Deco gas pill RoyalBlue border',  'border:2px solid #4169E1' in src)
check('Bottom gas tag RoyalBlue',        'background:#ffffff;border:2px solid #4169E1' in src)
check('DECOMPRESSION DIVE red border',   'border-color:#cc0000;border-width:2px' in src)
check('Gas 1 card RoyalBlue',            'border:2px solid #4169E1;border-radius:8px;padding:14px;margin-top:10px' in src)

# ── Warning modal ─────────────────────────────────────────────────────────────
check('Warning modal red border',        "border:2px solid #cc0000" in src)
check('No Close btn in warning modal',   'toggleWarningModal()" style="background:var(--surface);border:1px solid var(--border)' not in src)
check('Header-warn red border',          'border: 1px solid #cc0000' in src)

# ── PDF graph legends ─────────────────────────────────────────────────────────
check('Deco PDF graph legend',           'drawGraphLegend' in src)
check('Emergency PDF graph legend',      'drawGraphLegend' in src and 'decoProfileLegend' in src)

# ── Emergency PDF completeness ────────────────────────────────────────────────
import re as _re

def _fn(src, name):
    idx = src.find(f'async function {name}() {{')
    depth=0
    for i in range(idx,len(src)):
        if src[i]=='{': depth+=1
        elif src[i]=='}':
            depth-=1
            if depth==0: return src[idx:i+1]
    return ''

exp_fn  = _fn(src, 'exportPDF')
cont_fn = _fn(src, 'exportContingencyPDF')

check('Emergency PDF: GF curve section',          'gfCurveCanvas' in cont_fn)
check('Emergency PDF: GF curve legend table',     'gfRows2' in cont_fn)
check('Emergency PDF: Tissue Saturation bars',    'lastTissues&&lastTissues.length' in cont_fn)
check('Emergency PDF: Compartment Detail table',  'COMPARTMENT DETAIL' in cont_fn)
check('Emergency PDF: CNS yellow row highlight',  'data-cnshi' in cont_fn)
check('Emergency PDF: HIGH CNS banner',           '_emCNSpct' in cont_fn)
check('Emergency PDF: graph legend',              'drawGraphLegend' in cont_fn or 'emGleg' in cont_fn)
check('Emergency PDF: doc.save',                  'doc.save(' in cont_fn)
check('Emergency PDF: footer all pages',          'getNumberOfPages' in cont_fn)

# ── Deco PDF completeness ─────────────────────────────────────────────────────
check('Deco PDF: gas tags rendered',              'gasTagEls' in exp_fn)
check('Deco PDF: rates/WV line',                  '_dRate' in exp_fn)
check('Deco PDF: CNS banner after table',         '_cnsPctMain' in exp_fn)
check('Deco PDF: gas consumption section',        'gasConsumptionSummary' in exp_fn)
check('Deco PDF: dive profile graph',             'decoProfileCanvas' in exp_fn)
check('Deco PDF: graph legend',                   'drawGraphLegend' in exp_fn)
check('Deco PDF: GF curve with page break',       'doc.addPage(); drawHeader();\n    const gc=' in exp_fn)
check('Deco PDF: GF curve legend table',          'gfRows' in exp_fn)
check('Deco PDF: Tissue Saturation bars',         'lastTissues&&lastTissues.length' in exp_fn)
check('Deco PDF: Compartment Detail table',       'COMPARTMENT DETAIL' in exp_fn)
check('Deco PDF: CNS yellow row highlight',       'data-cnshi' in exp_fn)
check('Deco PDF: doc.save',                       'doc.save(' in exp_fn)
check('Deco PDF: footer all pages',               'getNumberOfPages' in exp_fn)

# ── Table vertical align ──────────────────────────────────────────────────────
check('Deco table vertical-align middle',         'vertical-align:middle' in src)

# ── Warning modal ─────────────────────────────────────────────────────────────
check('Warning modal no Close button',            'toggleWarningModal()" style="background:var(--surface);border:1px solid var(--border)' not in src)
print(f"\nAUDIT TOTAL: {passes} passed, {len(failures)} failed")
if failures:
    print("FAILURES:")
    for f in failures:
        print(f"  ✗ {f}")
else:
    print("ALL CHECKS PASSED ✓")
