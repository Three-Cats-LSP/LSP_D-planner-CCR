#!/usr/bin/env python3
"""
LSP D-PLANNER audit script
Run before every release: python3 audit.py
All checks must pass before packaging.
"""
import re, os, sys

html = open('index.html').read()
checks = []
failures = []

def check(name, result, detail=''):
    checks.append((name, result, detail))

# ── JS SYNTAX ──────────────────────────────────────────────────────────
scripts = re.findall(r'<script(?:\s[^>]*)?>(.+?)</script>', html, re.DOTALL)
open('/tmp/_audit_extracted.js', 'w').write('\n'.join(scripts))
js_ok = os.system('node --check /tmp/_audit_extracted.js 2>/dev/null') == 0
check('JS syntax clean', js_ok)

# ── STRUCTURE ──────────────────────────────────────────────────────────
check('DOCTYPE present', '<!DOCTYPE html>' in html)
check('Deco tab default active', 'tab-btn buh-only active' in html and 'id="tab-deco"' in html)
check('Deco panel active by default', '<div class="panel active" id="deco">' in html)
check('Planner panel NOT active by default', '<div class="panel active" id="planner">' not in html)

# ── TAB SWITCHING ──────────────────────────────────────────────────────
check('switchTab uses .panel .active classes', '.panel' in html and '.active' in html)

# ── EXPORT FUNCTIONS DEFINED ───────────────────────────────────────────
check('exportPDF defined', 'function exportPDF()' in html)
check('exportContingencyPDF defined', 'function exportContingencyPDF()' in html)
check('exportTXT defined', 'function exportTXT(' in html)
check('buildExportText defined', 'function buildExportText(' in html)
check('buildMessengerText defined', 'function buildMessengerText(' in html)

# ── TXT EXPORT: ASCII CLEANLINESS ─────────────────────────────────────
bex = html[html.find('function buildExportText'):html.find('\nfunction buildMessengerText')]
mes = html[html.find('function buildMessengerText'):html.find('\nfunction exportTXT')]

bad_out = [line.strip()[:80] for line in (bex+mes).split('\n')
           if ('lines.push' in line or 'result.push' in line)
           and not line.strip().startswith('//')
           and not re.search(r'/\[.*\]/[gi]', line)
           and any(ord(c)>127 for c in line)]
check('No non-ASCII in TXT output lines', len(bad_out)==0,
      '\n'.join(bad_out[:3]) if bad_out else '')

check('ppO2 not ppO₂ in calcContingency msg',
      'ppO₂' not in html[html.find('function calcContingency()'):html.find('function calcContingency()')+3000])
check('Note field uses clean(c.msg)', 'clean(c.msg)' in html)
check('No GSw in phaseLabel', "'GSw'" not in html)

# ── TXT EXPORT: COLUMN FORMAT ──────────────────────────────────────────
# Header must be exactly 49 chars
header_line = "Phase Depth  Stop   Run   Mix   EAD    PPO2  CNS%"
check(f'TXT header is {len(header_line)} chars', f"'{header_line}'" in html,
      f'Expected: {header_line!r}')

# Separator must match header length (49)
check('TXT separator is 49 dashes', "'-'.repeat(49)" in html or 'repeat(49)' in html)

# run column: short run times right-justified (padStart(5) for <=4 char values)
check('Run col: short times right-justified (padStart(5))', 'padStart(5)' in bex)
check('Stop col: short times right-justified (padStart(5))', 'stpVal.padStart(5)' in bex)
check('Depth col: single-digit depths right-justified (padStart(3))', 'depRaw.padStart(3)' in bex)
check('PPO2 col: right-justified (padStart(4))', "(c[6] || '').padStart(4)" in bex)
check('CNS% col: right-justified (padStart(4/5))', 'cnsRaw.padStart(4)' in bex and 'cnsRaw.padStart(5)' in bex)

# EAD column: right-aligned ('-' gets padStart(2), values get padStart(3))
check('EAD col: dash right-aligned (padStart(2))', "padStart(2)" in bex)
check('EAD col: values right-aligned (padStart(3))', "padStart(3)" in bex)

# run padEnd(6) not padEnd(7)
check('Run col: padEnd(6) not padEnd(7)',
      'padEnd(7)' not in bex[bex.find('const run'):bex.find('const run')+60])

# Contingency TXT has its own shortMix
cont_body = bex[bex.find("} else if (mode === 'contingency')"):]
check('Contingency TXT has shortMix', 'const shortMix' in cont_body)
check('Contingency TXT mix col uses shortMix()', 'shortMix(c2[4]' in cont_body)
check('Contingency TXT run: short times right-justified', 'padStart(5)' in cont_body)
check('Contingency TXT stop: short times right-justified', 'stpVal.padStart(5)' in cont_body)
check('Contingency TXT depth: single-digit right-justified', 'depRaw.padStart(3)' in cont_body)
check('Contingency TXT PPO2: right-justified', "(c2[6]||'').padStart(4)" in cont_body)
check('Contingency TXT CNS%: right-justified', 'cnsRaw.padStart(4)' in cont_body and 'cnsRaw.padStart(5)' in cont_body)
check('Contingency TXT EAD right-aligned', 'padStart(2)' in cont_body)

# Deco TXT: ascent arrowMatch handles > (from clean())
check('Deco TXT arrowMatch handles > after clean()', '[→>]' in bex)
check('Contingency TXT arrowMatch handles >', '[→>]' in cont_body)

# Header spacing (2 spaces between fields, not 4)
check('Descent header uses 2-space separators',
      '${du}/min  Ascent:' in html or "/min  Ascent:" in html)
check('Deco Gas switch: single space before (', "g.gas} (switch @" in html or
      "g.gas} (switch" in html)
check('Deco Time header uses 2-space separator', '"  Run Time: ' in html or
      '  Run Time:' in html)

# ── MESSENGER FORMAT ───────────────────────────────────────────────────
check('EAN no space in messenger shortMix', "'EAN ' +" not in mes)
check('Contingency messenger: lastRunFmt used', 'c.lastRunFmt' in html)
check('Contingency messenger: CNS line', 'cnsLine' in html)
check('Contingency messenger: digit-unit collapse', r'(\d)\s+(m|ft)' in mes[:2000])

# ── GRAPH ──────────────────────────────────────────────────────────────
profile_fn = html[html.find('function _drawDiveProfileCore'):html.find('\nfunction drawPlannerProfile')]
gf_fn      = html[html.find('function drawGFCurve()'):html.find('\nfunction ', html.find('function drawGFCurve()') + 100)]
deco_prof  = html[html.find('function drawDecoProfile()'):html.find('\nfunction ', html.find('function drawDecoProfile()') + 100)]

check('Graph: wps sorted by t after gasswitch injection', 'wps.sort((a, b) => a.t - b.t)' in html)
check('Graph: profile line excludes gasswitch waypoints', "wp.type !== 'gasswitch'" in profile_fn)
check('Graph: tooltip uses pathWps (no gasswitch)', 'pathWps = waypoints.filter' in html[html.find('function attachDiveProfileInteraction'):])
check('Graph: single merged deco zone (not per-stop fills)', 'decoStops[0]' in profile_fn)
check('Graph: unit-aware depth axis (_du)', 'const _du' in profile_fn)
check('Graph: unit-aware GF curve axis (_gfDu)', 'const _gfDu' in html)
check('Graph: gas switch vertical markers drawn', "'gasswitch'" in html)
check('decoProfileCanvas exists', 'id="decoProfileCanvas"' in html)
check('plannerProfileCanvas exists', 'id="plannerProfileCanvas"' in html)
check('drawDecoProfile defined', 'function drawDecoProfile()' in html)
check('drawPlannerProfile defined', 'function drawPlannerProfile()' in html)
check('Graph lastT excludes totals row', "phase !== 'totals'" in html)

# ── GRAPH: PAD / layout ─────────────────────────────────────────────────
check('Graph: isMobile detected before PW/PH (not after)', \
      profile_fn.index('const isMobile') < profile_fn.index('const PW'))
check('Graph: mobile PAD.top <= 10', 'PAD.top    = 6' in profile_fn or 'PAD.top = 6' in profile_fn)
check('Graph: mobile PAD.right <= 4', 'PAD.right  = 2' in profile_fn or 'PAD.right = 2' in profile_fn)
check('Graph: mobile PAD.bottom <= 18', 'PAD.bottom = 14' in profile_fn or 'PAD.bottom = 14' in profile_fn)
check('Graph: mobile PAD.left <= 26', 'PAD.left   = 22' in profile_fn or 'PAD.left = 22' in profile_fn)
check('Graph: GF curve isMobile before PW/PH', \
      gf_fn.index('const isMobile') < gf_fn.index('const PW'))
check('Graph: GF curve mobile PAD overrides present', 'PAD.bottom = 20' in gf_fn)
check('Graph: canvas aspect ratio 700/420', 'aspect-ratio:700/420' in html)
check('Graph: hint div outside canvas (HTML not canvas draw)', 'decoProfileCanvas-hint' in html)
check('Graph: hint not drawn on canvas (no ctx.fillText hint)', \
      'scroll·zoom' not in profile_fn)

# ── GRAPH: gas segments ─────────────────────────────────────────────────
check('Graph: gas segments stored on window', 'window._decoGasSegments' in html)
check('Graph: gas color map stored on window', 'window._decoGasColorMap' in html)
check('Graph: bottom gas segment prepended (unshift)', 'gasSegs.unshift' in html)
check('Graph: gas segment fromT starts at bt (run time)', 'let gsT = bt' in html)
check('Graph: fill uses rgba() not hex alpha', 'rgba(${r2}' in html)
check('Graph: fill clipped to x-column per segment', 'clipX1' in profile_fn and 'clipX2' in profile_fn)
check('Graph: fill gradient anchored to segTopY', 'segTopY' in profile_fn)
check('Graph: isBottomSeg fill distinction', 'isBottomSeg' in profile_fn)

# ── GRAPH: ceiling line ─────────────────────────────────────────────────
check('Graph: ceiling waypoints stored on window', 'window._decoCeilingWps' in html)
check('Graph: ceiling walk starts at bt', 'let walkT = bt' in html)
check('Graph: ceiling samples during descent phase', 'descent' in html[html.find('window._decoCeilingWps') - 500:html.find('window._decoCeilingWps')])
check('Graph: ceiling filter threshold 0.5m', 'ceil > 0.5' in profile_fn)
check('Graph: ceiling uses clipToPlot', 'clipToPlot' in profile_fn)
check('Graph: ceiling line dashed', 'setLineDash' in profile_fn)

# ── GRAPH: labels ───────────────────────────────────────────────────────
check('Graph: mobile labels suppressed (dots only)', 'if (isMobile) return' in profile_fn)
check('Graph: label collision uses usedY map', 'usedY' in profile_fn)
check('Graph: label collision bucket by labelW', 'labelW' in profile_fn and 'lKey' in profile_fn)
check('Graph: ppO2 label side-switching', 'ppAlign' in profile_fn)
check('Graph: ppO2 clamped to canvas edge', 'rightEdge' in profile_fn)
check('Graph: bottom dot label below dot', "wp.type === 'bottom'" in profile_fn)

# ── GRAPH: GF curve ─────────────────────────────────────────────────────
check('Graph: GF curve canvas exists', 'id="gfCurveCanvas"' in html)
check('Graph: drawGFCurve defined', 'function drawGFCurve()' in html)
check('Graph: GF 100% label right-aligned', "gf === 1.0 ? 'right' : 'center'" in html)
check('Graph: GF axis titles removed', 'Gradient Factor %' not in gf_fn)
check('Graph: GF depth buffer <= 1.05 on mobile', '1.01' in gf_fn or '1.02' in gf_fn or '1.03' in gf_fn)
check('Graph: GF curve tooltip defined', 'GF CURVE' in html)

# ── GRAPH: zoom/pan ─────────────────────────────────────────────────────
check('Graph: zoom state _graphZoom', '_graphZoom' in html)
check('Graph: scroll zoom handler', 'wheel' in html)
check('Graph: drag pan handler', 'mousemove' in html or 'pointermove' in html)
check('Graph: pinch zoom handler', 'pinch' in html or 'touch' in html)
check('Graph: dbl-click reset', 'dblclick' in html or 'dbl' in html)
check('Graph: zoom apply function', 'function _graphZoomApply' in html)
check('Graph: zoom reset function', '_graphZoomReset' in html)

# ── PDF ────────────────────────────────────────────────────────────────
epdf_start = html.find('function exportPDF()')
epdf_end   = html.find('\nfunction ', epdf_start + 100)
epdf = html[epdf_start : epdf_end if epdf_end != -1 else len(html)]
cont_pdf = html[html.find('function exportContingencyPDF()'):html.find('\nfunction calcCNS')]
check('PDF: du defined in exportPDF', "units === 'imperial' ? 'ft' : 'm'" in epdf)
check('PDF: lastStopDisp defined', 'lastStopDisp' in epdf)
check('PDF: stepDisp defined', 'stepDisp' in epdf)
check('PDF: switch row colspan 7', 'colspan="7"' in html)
check('PDF: totals row colspan 8', 'colspan="8"' in html)
check('PDF: EAD c[5] in rows', 'c[5]' in html)
check('PDF: PPO2 c[6] in rows', 'c[6]' in html)
check('PDF: CNS c[7] in rows', 'c[7]' in html)
check('PDF: page-title font 10px', 'font-size: 10px' in epdf)
check('PDF: tissue bars use viewBox 400', 'viewBox="0 0 400 10"' in html)
check('PDF: body padding-bottom for footer clearance', 'padding-bottom: 60px' in epdf or 'padding-bottom:60px' in epdf)
check('Contingency PDF: captures profile graph', 'contProfileImgSrc' in cont_pdf)
check('Contingency PDF: saves/restores tbody', 'savedBody' in cont_pdf)
check('Contingency PDF: cDu defined', 'cDu' in cont_pdf)

# ── PDF: gas consumption header ─────────────────────────────────────────
build_fn = html[html.find('function buildPdfGasCards'):html.find('\nfunction ', html.find('function buildPdfGasCards') + 100)]
check('PDF: buildPdfGasCards uses page-title class (not inline style)',
      'class="page-title"' in build_fn or "class='page-title'" in build_fn)
check('PDF: gas consumption title has color override', 'color:${tc}' in build_fn)
check('PDF: deco PDF gas cards get page-break before',
      'page-break"></div><div class="page-spacer"></div>${buildPdfGasCards(document.getElementById(\'gasConsumptionSummary\')' in html or
      'page-break\"></div><div class=\"page-spacer\"></div>${buildPdfGasCards(document.getElementById(\'gasConsumptionSummary\')' in html)
check('PDF: emergency PDF gas cards get page-break before (standalone)',
      'page-break"></div><div class="page-spacer"></div>${buildPdfGasCards(document.getElementById(\'emergencyGasConsumption\')' in html or
      'page-break\"></div><div class=\"page-spacer\"></div>${buildPdfGasCards(document.getElementById(\'emergencyGasConsumption\')' in html)
check('PDF: emergency standalone has .page-break CSS class', \
      '.page-break { page-break-before:always' in cont_pdf or \
      '.page-break { page-break-before: always' in cont_pdf)
check('PDF: emergency standalone has .page-spacer CSS class',
      '.page-spacer { height:38px' in cont_pdf or '.page-spacer { height: 38px' in cont_pdf)
check('PDF: deco page-title has page-break-after:avoid',
      'page-break-after: avoid' in epdf or 'page-break-after:avoid' in epdf)
check('PDF: emergency page-title has page-break-after:avoid',
      'page-break-after:avoid' in cont_pdf)


# ── COLOURS ────────────────────────────────────────────────────────────
check('Light theme yellow: Amber #FFBF00', '--yellow: #FFBF00' in html)
check('Light theme green: Emerald #50C878', '--green:  #50C878' in html)
check('Dark theme yellow: #ffb703', '--yellow: #ffb703' in html)
check('Dark theme green: #26d07c', '--green:  #26d07c' in html)

# ── EXPORT BUTTONS ─────────────────────────────────────────────────────
# PDF button: text-only SVG, same 16x16 size as copy/TXT, viewBox scaled for readability
pdf_btn_svg = '<svg width="16" height="16" viewBox="0 0 18 14"'

# The document-page SVG path is correct on TXT buttons; verify PDF buttons don't use it
pdf_btn_deco = html[html.find("onclick=\"exportPDF()\""):html.find("onclick=\"exportPDF()\"")+200]
pdf_btn_cont = html[html.find("onclick=\"exportContingencyPDF()\""):html.find("onclick=\"exportContingencyPDF()\"")+200]
check('PDF button: no document page SVG (page removed)',
      'M14 2H6a2 2 0 0 0-2 2v16' not in pdf_btn_deco and
      'M14 2H6a2 2 0 0 0-2 2v16' not in pdf_btn_cont)

check('Copy button: 16x16 SVG', 'onclick="copyDiveProfile' in html and 'width="16" height="16"' in html)
check('TXT button: 16x16 SVG', 'onclick="exportTXT' in html and 'width="16" height="16"' in html)

# ── UI / LAYOUT ───────────────────────────────────────────────────────
check('Settings left-aligned on mobile (flex-start)',
      'justify-content: flex-start !important' in html)
check('Settings NOT center-aligned on mobile',
      'justify-content: center !important' not in html)
check('Settings groups NOT full-width on mobile',
      'width: 100% !important' not in html)

# REF button in main tabs-nav
check('REF button in main tabs-nav',
      'toggleReference()' in html[html.find('<div class="tabs-nav">'):html.find('<!-- ══ TABS ══', html.find('<div class="tabs-nav">') + 10)])

# REF button in Tools sub-nav
tools_subnav_start = html.find('id="toolsSubNav"')
tools_subnav_end   = html.find('</div>', tools_subnav_start)
check('REF button in Tools sub-nav',
      'toggleReference()' in html[tools_subnav_start:tools_subnav_end])

# REF button has margin-left:auto to stay right-aligned
check('REF button uses margin-left:auto',
      html.count("margin-left:auto") >= 2 or html.count("margin-left: auto") >= 2 or
      (html.count("margin-left:auto") + html.count("margin-left: auto")) >= 2)

# Gas switch rows left-aligned in web table
check('Gas switch row td forced left-align in web table',
      'tr[data-phase="switch"] td' in html and 'text-align:left' in html[html.find('tr[data-phase="switch"] td'):html.find('tr[data-phase="switch"] td')+60])

# Numeric columns right-aligned in deco table
check('Deco table numeric cols right-aligned (nth-child)',
      'nth-child(2)' in html and 'nth-child(7)' in html and 'nth-child(8)' in html and 'text-align:right' in html)

# ── PDF TABLE ALIGNMENT ────────────────────────────────────────────────
# Deco PDF rows: numeric columns right-aligned
check('Deco PDF table: numeric cols right-aligned',
      'text-align:right;">${c[1]' in html and 'text-align:right;">${c[6]' in html and 'text-align:right;">${c[7]' in html)
# Contingency PDF CSS: nth-child right-align
eg_pdf_start = html.find('function exportContingencyPDF()')
eg_pdf_end2  = html.find('\nfunction calcCNS', eg_pdf_start + 100)
eg_pdf_end   = eg_pdf_end2 if eg_pdf_end2 != -1 else len(html)
eg_pdf_body  = html[eg_pdf_start:eg_pdf_end]
check('Emergency PDF CSS: numeric cols right-aligned (nth-child)',
      'th:nth-child(2)' in eg_pdf_body)
# Gas switch left-align override in emergency PDF CSS
check('Emergency PDF CSS: switch rows left-aligned',
      'tr[data-phase="switch"] td' in eg_pdf_body)

# ── EMERGENCY PDF GAS BARS ──────────────────────────────────────────────
# Emergency PDF has color bars (same structure as deco PDF)
check('Emergency PDF: gas uses buildPdfGasCards', 'buildPdfGasCards' in eg_pdf_body)
check('Emergency PDF: uses buildPdfGasCards', 'buildPdfGasCards' in eg_pdf_body)
gas_fn_start2 = html.find('function buildPdfGasCards(')
gas_fn_end2   = html.find('\nfunction ', gas_fn_start2 + 100)
gas_fn_body2  = html[gas_fn_start2:gas_fn_end2]
check('Emergency PDF: SAC line in gas builder', 'sacLine' in gas_fn_body2)

# Deco PDF gas warning card
# buildPdfGasCards helper — single definition, called in all 3 places
check('PDF: buildPdfGasCards helper defined once',
      html.count('function buildPdfGasCards(') == 1)
check('PDF: deco gas uses buildPdfGasCards blue',
      "buildPdfGasCards(document.getElementById('gasConsumptionSummary'), '#0055aa')" in html)
check('PDF: emergency standalone uses buildPdfGasCards red',
      "buildPdfGasCards(document.getElementById('emergencyGasConsumption'), '#bb2233')" in html and
      html.count("buildPdfGasCards(document.getElementById('emergencyGasConsumption'), '#bb2233')") == 2)
gas_fn_start = html.find('function buildPdfGasCards(')
gas_fn_end   = html.find('\nfunction ', gas_fn_start + 100)
gas_fn_body  = html[gas_fn_start:gas_fn_end]
check('PDF: gas cards use flex layout (card style)', 'display:flex' in gas_fn_body)
check('PDF: gas cards show warning alerts', 'alertDivs' in gas_fn_body or 'alert' in gas_fn_body.lower())
check('PDF: gas warning is solid red', '#fff0f0' in gas_fn_body and '#cc0000' in gas_fn_body)
check('PDF: gas warning not yellow/pink', '#fff3cd' not in gas_fn_body and '#ff4757' not in gas_fn_body)
# Web: gas warning uses .dang class (red) - already correct
check('Web: gas warning uses .dang class (red)', 'alert dang' in html[html.find('runs out')-120:html.find('runs out')])
check('Light theme .dang is solid red', 'body.light-theme .dang' in html and '#cc0000' in html[html.find('body.light-theme .dang'):html.find('body.light-theme .dang')+80])
check('PDF: SAC line in gas header (not footer)', 'sacLine' in gas_fn_body and 'margin-left:10px' in gas_fn_body)

# ── FILENAMES ────────────────────────────────────────────────────────────
check('TXT filename uses Emergency not Contingency',
      'tag = `Emergency_' in html and 'tag = `Contingency_' not in html)
check('PDF title uses Emergency not Contingency',
      'LSP_${isoDate}_Emergency_' in html and 'LSP_${isoDate}_Contingency_' not in html)


# ── GOLDEN TXT FORMAT ───────────────────────────────────────────────────
# Locked from approved output files (31 May 2026).
# DO NOT CHANGE these checks without an explicit user instruction to update
# the TXT export format.
#
# Column layout (0-indexed positions):
#   lbl[0:5]+sp  dep[6:12]  stp[12:19]  run[19:25]+sp  mix[26:31]+sp
#   ead[32:38]+sp  ppo2[39:44]  cns[44:]
#
# Key rules locked:
#   - Header: 'Phase Depth  Stop   Run   Mix   EAD    PPO2  CNS%' (49 chars)
#   - Separator: 49 dashes
#   - Depth: single-digit right-justified (' 6m', ' 9m')
#   - Stop:  short times right-justified (' 1:00', ' 3:10')
#   - Run:   short times right-justified (' 2:48')
#   - EAD:   dash right-aligned (' -'), values right-aligned (' 8m','10m')
#   - PPO2:  padStart(4) → ' 0.7', '1.26', padEnd(5) → ' 0.7 ','1.26 '
#   - CNS%:  % values rjust(5) → ' 0.5%','39.6%'; dash rjust(4) → '   -'
#   - Emergency header: Run Time / Deco Time use mm'ss" format
#   - Deco header:      Deco Time / Run Time use mm'ss" format

bex = html[html.find('function buildExportText'):html.find('\nfunction buildMessengerText')]

# Header and separator exact strings
check('GOLDEN: TXT header exact string',
      "'Phase Depth  Stop   Run   Mix   EAD    PPO2  CNS%'" in bex)
check('GOLDEN: TXT separator 49 dashes',
      "'-'.repeat(49)" in bex or "repeat(49)" in bex)

# Column padding rules
check('GOLDEN: dep padEnd(6)', 'depRaw.padEnd(6)' in bex or '.padEnd(6)' in bex)
check('GOLDEN: stp padStart(5) for short times', 'stpVal.padStart(5)' in bex)
check('GOLDEN: run padStart(5) for short times', 'runRaw.padStart(5)' in bex or 'padStart(5)' in bex)
check('GOLDEN: run padEnd(6)', 'padEnd(6)' in bex)
check('GOLDEN: ead dash padStart(2)', "padStart(2)" in bex)
check('GOLDEN: ead values padStart(3)', "padStart(3)" in bex)
check('GOLDEN: ppo2 padStart(4) padEnd(5)', "padStart(4).padEnd(5)" in bex or ("padStart(4)" in bex and "padEnd(5)" in bex))
check('GOLDEN: cns % rjust(5) padStart(5)', "padStart(5)" in bex)
check('GOLDEN: cns dash rjust(4) padStart(4)', "padStart(4)" in bex)

# Emergency header uses mm\'ss" format
cont_body = bex[bex.find("} else if (mode === 'contingency')"):]
check("GOLDEN: emergency header Run Time uses mm ss format",
      'lastRunFmt' in cont_body or "lastRunFmt" in html[html.find('function buildExportText'):html.find('\nfunction buildMessengerText')+1000])
check("GOLDEN: emergency header Deco Time uses mm ss format",
      'decoTimeFmt' in cont_body or "decoTimeFmt" in html[html.find('function buildExportText'):html.find('\nfunction buildMessengerText')+1000])

# Deco header uses mm\'ss" format (from totals row)
check("GOLDEN: deco header Run Time from totals row (mm ss format)",
      'data-phase="totals"' in bex and 'runTimeVal' in bex)

# Mix column: AIR not AIR (21%), EAN50 not EAN 50
check("GOLDEN: mix col AIR not AIR(21%)", "return 'AIR'" in bex)
check("GOLDEN: mix col EAN50 no space", "'EAN' + ean[1]" in bex or "'EAN' +" in bex)

# Contingency branch identical column rules
cont_body2 = bex[bex.find("} else if (mode === 'contingency')"):]
check('GOLDEN: contingency dep right-justified', 'depRaw.padStart(3)' in cont_body2)
check('GOLDEN: contingency stp right-justified', 'stpVal.padStart(5)' in cont_body2)
check('GOLDEN: contingency run right-justified', 'padStart(5)' in cont_body2)
check('GOLDEN: contingency ppo2 padStart(4).padEnd(5)', 'padStart(4).padEnd(5)' in cont_body2)
check('GOLDEN: contingency cns padStart(4/5)', 'padStart(4)' in cont_body2 and 'padStart(5)' in cont_body2)
check('GOLDEN: contingency ead padStart(2/3)', 'padStart(2)' in cont_body2 and 'padStart(3)' in cont_body2)

# ── END GOLDEN TXT FORMAT ───────────────────────────────────────────────
# ── VERSION ────────────────────────────────────────────────────────────
version = open('VERSION').read().strip()
check(f'VERSION file present ({version})', bool(version))
check('CHANGELOG has current version entry', f'[{version}]' in open('CHANGELOG.md').read())

# ── NO REGRESSIONS ─────────────────────────────────────────────────────
check('No btn-export primary class', 'class="btn-export primary"' not in html)
check('No nested version folders', not any(
    os.path.isdir(d) for d in ['LSP_D-PLANNER_v5.8.5', 'LSP_D-PLANNER_v6.0.0', 'LSP_D-PLANNER_v6.0.1', 'LSP_D-PLANNER_v6.0.2', 'LSP_D-PLANNER_v7.0']))
import pathlib
dir_name = pathlib.Path(os.getcwd()).name
check('Directory name matches VERSION (LSP_D-PLANNER_vX.Y.Z)', dir_name == f'LSP_D-PLANNER_v{version}')
check('No stale localStorage units reads', "localStorage.getItem('units')" not in html)
check('No invisible chars in template strings',
      not any(any(ord(c) in range(0x200B,0x200F) for c in s)
              for s in re.findall(r'`[^`]{0,500}`', html)))

# ── RESULTS ────────────────────────────────────────────────────────────
passed = sum(1 for _,r,_ in checks if r)
total  = len(checks)
width  = 54

print(f"\n{'='*width}")
print(f"  LSP D-PLANNER AUDIT  —  v{version}")
print(f"{'='*width}")
for name, result, detail in checks:
    print(f"  {'✅' if result else '❌'}  {name}")
    if not result and detail:
        for line in detail.split('\n')[:2]:
            print(f"      ↳ {line}")
print(f"{'='*width}")
if passed == total:
    print(f"  ✅  ALL {total} CHECKS PASSED — ready to ship")
else:
    print(f"  ❌  {total-passed}/{total} FAILED — do not ship")
    failures = [name for name,r,_ in checks if not r]
    for f in failures:
        print(f"      • {f}")
print(f"{'='*width}\n")

sys.exit(0 if passed == total else 1)
