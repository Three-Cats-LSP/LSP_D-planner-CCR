/**
 * LSP D-PLANNER — Settings Integration Test Suite
 * Verifies that all dropdown settings (GF, Water, WV, Rounding)
 * are correctly applied to deco schedule calculations.
 */
'use strict';

const { lspDeco } = require('./lsp_engine');
const apex        = require('/home/claude/apexdeco_engine.js');

let pass = 0, fail = 0;
const log = [];

function check(label, condition, detail = '') {
  if (condition) { pass++; log.push(`  ✅ ${label}`); }
  else           { fail++; log.push(`  ❌ ${label}${detail ? ' — ' + detail : ''}`); }
}
function fmtS(stops) {
  return stops.map(s => `${s.depth}m:${Math.floor(s.dur)}:${String(Math.round(s.dur%1*60)).padStart(2,'0')}`).join(' ');
}

// ── TEST 1: ALL GF PRESETS PRODUCE VALID PLANS ───────────────────────
console.log('\n══ TEST 1: All GF presets produce valid plans ════════════════');
{
  const presets = [[20,85],[30,70],[30,85],[40,80],[45,85],[45,95],[50,75]];
  for (const [lo,hi] of presets) {
    const r = lspDeco({depth:40, bt:25, gfLow:lo, gfHigh:hi});
    check(`GF ${lo}/${hi} — valid plan, RT>0`, !r.error && r.rt > 0 && r.stops.length > 0, r.error);
  }
  // GF Low controls first stop depth — lower GF Low = deeper first stop
  const lo20 = lspDeco({depth:40, bt:25, gfLow:20, gfHigh:85});
  const lo50 = lspDeco({depth:40, bt:25, gfLow:50, gfHigh:75});
  check('GF Low 20 gives deeper first stop than GF Low 50',
    lo20.stops[0]?.depth >= lo50.stops[0]?.depth,
    `GF20/85 first=${lo20.stops[0]?.depth}m vs GF50/75 first=${lo50.stops[0]?.depth}m`);
  // GF High controls surface clearance — lower GF High = more deco at last stop
  const hi70 = lspDeco({depth:40, bt:25, gfLow:30, gfHigh:70});
  const hi95 = lspDeco({depth:40, bt:25, gfLow:30, gfHigh:95});
  check('GF High 70 gives more deco than GF High 95 (same GF Low)',
    hi70.decoTime >= hi95.decoTime,
    `GF30/70 deco=${hi70.decoTime} vs GF30/95 deco=${hi95.decoTime}`);
  // GF 30/70 is strictly more conservative than 40/80 (both lower)
  const gf3070 = lspDeco({depth:40, bt:25, gfLow:30, gfHigh:70});
  const gf4080 = lspDeco({depth:40, bt:25, gfLow:40, gfHigh:80});
  check('GF 30/70 more deco than 40/80 (both dimensions more conservative)',
    gf3070.decoTime >= gf4080.decoTime,
    `30/70 deco=${gf3070.decoTime} vs 40/80 deco=${gf4080.decoTime}`);
}

// ── TEST 2: CUSTOM GF ────────────────────────────────────────────────
console.log('\n══ TEST 2: Custom GF values ══════════════════════════════════');
{
  const custom = lspDeco({depth:40, bt:25, gfLow:35, gfHigh:75});
  const pre3070 = lspDeco({depth:40, bt:25, gfLow:30, gfHigh:70});
  const pre4080 = lspDeco({depth:40, bt:25, gfLow:40, gfHigh:80});
  check('Custom 35/75 valid plan', !custom.error && custom.rt > 0);
  check('Custom 35/75 RT between 30/70 and 40/80',
    custom.rt >= pre4080.rt && custom.rt <= pre3070.rt,
    `custom=${custom.rt}, 40/80=${pre4080.rt}, 30/70=${pre3070.rt}`);
  // Custom GF propagates to mGF correctly
  check('Custom 35/75 first stop depth between 30/70 and 40/80',
    custom.stops[0]?.depth <= pre3070.stops[0]?.depth + 3 &&
    custom.stops[0]?.depth >= pre4080.stops[0]?.depth - 3,
    `custom=${custom.stops[0]?.depth}m, 30/70=${pre3070.stops[0]?.depth}m, 40/80=${pre4080.stops[0]?.depth}m`);
  // Edge cases
  const extreme = lspDeco({depth:40, bt:25, gfLow:100, gfHigh:100});
  check('GF 100/100 produces a plan (no deco or minimal)', !extreme.error);
  const tight = lspDeco({depth:40, bt:25, gfLow:5, gfHigh:5});
  check('GF 5/5 produces a plan (very conservative)', !tight.error && tight.rt > 0);
}

// ── TEST 3: WATER DENSITY ────────────────────────────────────────────
console.log('\n══ TEST 3: Water density affects N₂ loading ══════════════════');
{
  const salt  = lspDeco({depth:40, bt:30, gfLow:40, gfHigh:80, waterDensity:'salt'});
  const fresh = lspDeco({depth:40, bt:30, gfLow:40, gfHigh:80, waterDensity:'fresh'});
  const en    = lspDeco({depth:40, bt:30, gfLow:40, gfHigh:80, waterDensity:'en13319'});
  check('Salt water plan valid',    !salt.error  && salt.rt  > 0);
  check('Fresh water plan valid',   !fresh.error && fresh.rt > 0);
  check('EN13319 water plan valid', !en.error    && en.rt    > 0);
  // Salt > EN13319 > Fresh in terms of pressure per metre → more loading
  check('Salt deco >= fresh deco (higher density = more N₂)',
    salt.decoTime >= fresh.decoTime,
    `salt=${salt.decoTime} fresh=${fresh.decoTime}`);
  check('EN13319 deco >= fresh deco',
    en.decoTime >= fresh.decoTime,
    `en=${en.decoTime} fresh=${fresh.decoTime}`);
  check('Salt RT >= fresh RT',
    salt.rt >= fresh.rt,
    `salt=${salt.rt} fresh=${fresh.rt}`);
  console.log(`  decoTime: salt=${salt.decoTime} en13319=${en.decoTime} fresh=${fresh.decoTime}`);
}

// ── TEST 4: WATER VAPOR CONSTANT ─────────────────────────────────────
console.log('\n══ TEST 4: Water vapor constant ══════════════════════════════');
{
  const wv0627 = lspDeco({depth:60, bt:30, gfLow:40, gfHigh:80, waterVapor:0.0627});
  const wv0577 = lspDeco({depth:60, bt:30, gfLow:40, gfHigh:80, waterVapor:0.0577});
  check('WV=0.0627 valid plan', !wv0627.error && wv0627.rt > 0);
  check('WV=0.0577 valid plan', !wv0577.error && wv0577.rt > 0);
  // Lower WV = higher inspired pN2 = more tissue loading = same or more deco
  check('WV=0.0577 deco >= WV=0.0627',
    wv0577.decoTime >= wv0627.decoTime,
    `0.0577=${wv0577.decoTime} 0.0627=${wv0627.decoTime}`);
  // Plans should differ (different tissue states)
  const differ = wv0577.rt !== wv0627.rt ||
    wv0577.stops.some((s,i) => {
      const other = wv0627.stops[i];
      return other && Math.abs(s.dur - other.dur) > 0.01;
    });
  check('WV=0.0577 and 0.0627 produce different results for same dive',
    differ || wv0577.decoTime !== wv0627.decoTime,
    'Plans identical on this profile — try deeper dive');
  console.log(`  decoTime: WV0.0627=${wv0627.decoTime} WV0.0577=${wv0577.decoTime}`);
}

// ── TEST 5: STOP ROUNDING ─────────────────────────────────────────────
console.log('\n══ TEST 5: Stop rounding modes ═══════════════════════════════');
{
  const frac  = lspDeco({depth:40, bt:25, gfLow:40, gfHigh:80, wholeMin:false});
  const whole = lspDeco({depth:40, bt:25, gfLow:40, gfHigh:80, wholeMin:true});
  check('Fractional mode valid', !frac.error  && frac.rt  > 0);
  check('Whole-min mode valid',  !whole.error && whole.rt > 0);
  check('Whole-min: all ceiling-hold stops are whole minutes',
    whole.stops.filter(s => s.dur >= 1).every(s => Math.round(s.dur % 1 * 60) === 0),
    `non-whole: ${whole.stops.filter(s=>s.dur>=1&&Math.round(s.dur%1*60)!==0).map(s=>s.depth+'m:'+s.dur.toFixed(3)).join(' ')}`);
  check('Fractional: has at least one sub-minute or fractional stop',
    frac.stops.some(s => s.dur < 1 || Math.round(s.dur % 1 * 60) !== 0));
  check('Both modes: same number of stops',
    frac.stops.length === whole.stops.length,
    `frac=${frac.stops.length} whole=${whole.stops.length}`);
  check('Both modes: same stop depths',
    frac.stops.every((s,i) => whole.stops[i] && s.depth === whole.stops[i].depth));
  console.log(`  Frac:  ${fmtS(frac.stops)}`);
  console.log(`  Whole: ${fmtS(whole.stops)}`);
}

// ── TEST 6: GF PRESETS vs ApexDeco ───────────────────────────────────
console.log('\n══ TEST 6: All GF presets vs ApexDeco reference ══════════════');
{
  const base = {metric:true,waterType:0,decoModel:'ZHLC_GF',descentRate:22,ascentRate:9,
    decoAscentRate:9,surfaceAscentRate:9,stepSize:3,lastStop:6,minStopTime:1,
    ppO2Low:1.4,ppO2Mid:1.5,ppO2High:1.6,ppO2Bottom:1.4,ppO2Deco:1.6,
    o2MaxDepth:6,firstStop30sec:false,extendedStops:false};
  const dg = [{o2:50,he:0},{o2:100,he:0}];
  for (const [lo,hi] of [[20,85],[30,70],[30,85],[40,80],[45,85],[45,95],[50,75]]) {
    const s = {...apex.createDefaultSettings(),...base,gfLo:lo,gfHi:hi};
    const ar = apex.calculate([{depth:40,time:25,o2:21,he:0}],dg,s);
    const lr = lspDeco({depth:40,bt:25,gfLow:lo,gfHigh:hi,waterVapor:0.0627});
    const rtOk = Math.abs(lr.rt - ar.totalRuntime) <= 2;
    check(`GF ${lo}/${hi}: RT within ±2 of ApexDeco`,rtOk,
      `LSP=${lr.rt} Apex=${ar.totalRuntime}`);
  }
}

// ── TEST 7: COMBINED SETTINGS ─────────────────────────────────────────
console.log('\n══ TEST 7: Combined settings interaction ═════════════════════');
{
  // All settings combined — should produce consistent valid plan
  const combined = lspDeco({
    depth:50, bt:30, gfLow:30, gfHigh:70,
    waterDensity:'salt', waterVapor:0.0577, wholeMin:true
  });
  check('Combined salt+WV0577+wholeMin+GF30/70 valid', !combined.error && combined.rt > 0);
  check('Combined plan has stops', combined.stops.length > 0);
  check('Combined whole-min stops are whole minutes',
    combined.stops.filter(s=>s.dur>=1).every(s=>Math.round(s.dur%1*60)===0));

  // Water density change should shift RT for same GF
  const r1 = lspDeco({depth:50,bt:30,gfLow:30,gfHigh:70,waterDensity:'salt'});
  const r2 = lspDeco({depth:50,bt:30,gfLow:30,gfHigh:70,waterDensity:'fresh'});
  check('Salt RT >= fresh RT for 50m/30min GF30/70',
    r1.rt >= r2.rt, `salt=${r1.rt} fresh=${r2.rt}`);
}

// ── PRINT RESULTS ────────────────────────────────────────────────────
console.log('\n' + log.join('\n'));
const total = pass + fail;
console.log('\n' + '═'.repeat(60));
console.log(`  Settings Integration: ${pass}/${total} passed  ${fail===0?'🎉 ALL PASS':'⚠ '+fail+' FAIL'}`);
console.log('═'.repeat(60) + '\n');
