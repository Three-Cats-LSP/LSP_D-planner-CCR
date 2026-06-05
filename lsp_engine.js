/**
 * LSP D-PLANNER — Headless Deco Engine for Node.js
 * Extracted verbatim from index.html for automated regression testing.
 *
 * Usage:
 *   const { lspDeco } = require('./lsp_engine');
 *   const r = lspDeco({ depth:40, bt:25, gfLow:40, gfHigh:80 });
 *   // r: { rt, decoTime, stops:[{depth,dur,gas}], steps:[...] }
 */
'use strict';

// ── Minimal stubs ─────────────────────────────────────────────────────
const _DOM = {};
global.window   = { _lastPlan: null };
global.document = {
  getElementById:   id  => _DOM[id] || null,
  querySelectorAll: ()  => [],
  querySelector:    ()  => null,
  body: { classList: { contains:()=>false, add:()=>{}, remove:()=>{} } },
};
global.localStorage = { getItem:()=>null, setItem:()=>{}, removeItem:()=>{} };

// Non-calc stubs
function calcCNS(){}
function drawDecoProfile(){}
function drawGFCurve(){}
function attachGFCurveInteraction(){}
function attachDiveProfileInteraction(){}
function buildContingencyButtons(){}
function mToFt(m){ return Math.round(m*3.28084); }
function toMMSS(t){ const tt=Math.round(t*60); return `${Math.floor(tt/60)}'${String(tt%60).padStart(2,'0')}"`; }
function calcEND(d,fN2){ return Math.round(((1.013+d/10.078)*fN2/0.79-1.013)*10.078); }
function fmtEAD(){ return '-'; }
// Gas fraction constants (normally defined after ZHL16C in index.html)
const FN2_AIR   = 0.79;
const FN2_EAN32 = 0.68;
const FN2_EAN36 = 0.64;
let mGF = { low:30, high:70 };
global.mGF = mGF;
let units = 'metric';
global.units = units;
// State vars declared in index.html outside the extracted section
let lastTissues = null;
let algo = 'padi';

// ── ENGINE (verbatim from index.html) ─────────────────────────────────────────────────────────
const ZHL16C = [
  [4.0,   1.2599, 0.5050],[8.0,   1.0000, 0.6514],[12.5,  0.8618, 0.7222],
  [18.5,  0.7562, 0.7825],[27.0,  0.6200, 0.8126],[38.3,  0.5043, 0.8434],
  [54.3,  0.4410, 0.8693],[77.0,  0.4000, 0.8910],[109.0, 0.3750, 0.9092],
  [146.0, 0.3500, 0.9222],[187.0, 0.3295, 0.9319],[239.0, 0.3065, 0.9403],
  [305.0, 0.2835, 0.9477],[390.0, 0.2610, 0.9544],[498.0, 0.2480, 0.9602],
  [635.0, 0.2327, 0.9653],
];

// Rec RDP data
const PADI_DEPTHS_M  = [10,12,15,18,21,24,27,30,33,36,40];
const PADI_DEPTHS_FT = [35,40,50,60,70,80,90,100,110,120,130];
const PADI_NDL_M  = [310,230,100,60,35,25,20,15,13,10,8];
const PADI_NDL_FT = [310,230,100,60,35,25,20,15,13,10,8];
const PADI_GROUPS = ['A','B','C','D','E','F','G','H','I','J','K'];

// PADI Nitrox NDL tables (IANTD/PADI Enriched Air Diver standard tables)
// EAN32 (32% O2) — indexed to match PADI_DEPTHS_M
const NITROX_NDL_EAN32 = [310,230,145,75,55,30,25,20,16,13,9];
// EAN36 (36% O2) — indexed to match PADI_DEPTHS_M
const NITROX_NDL_EAN36 = [310,230,170,100,60,40,30,25,20,15,10];
// MOD for nitrox mixes at ppO2 1.4 bar (recreational limit)
// MOD (m) = (1.4 / fO2 - 1) * 10  for salt water
function nitroxMOD(fO2, ppO2limit) {
  return Math.floor(((ppO2limit / fO2) - 1) * 10);
}
function getNitroxNDL(depthM, mix) {
  // Return the correct PADI NDL for a given mix at a given depth
  // Finds closest depth in table (same logic as padiNDL)
  const depths = PADI_DEPTHS_M;
  let closest = 0, minDiff = Infinity;
  depths.forEach((d,i) => { const diff = Math.abs(d-depthM); if(diff<minDiff){minDiff=diff;closest=i;} });
  if (mix === 'ean32') return NITROX_NDL_EAN32[closest];
  if (mix === 'ean36') return NITROX_NDL_EAN36[closest];
  if (mix === 'custom') {
    // Interpolate between air, EAN32, EAN36 using Bühlmann for custom mixes in rec mode
    const fN2 = getN2Frac(mix);
    return buhNDL(depthM, fN2, 50, 100); // conservative GF for rec nitrox
  }
  return PADI_NDL_M[closest]; // air fallback
}

let _contingencyRunning = false; // flag to suppress contingency side effects
let contGasLose = 'none'; // contingency: 'none' | '1' | '2' | 'both'
let contExtraBT = 0;      // contingency extra BT: 0 | 3 | 5 | 10

const SURFACE_P = 1.013;
let WATER_VAPOR = 0.0627; // alveolar water vapor pressure (bar) — updated by waterVapor setting

// Water density pressure factors (bar per metre)
const WATER_DENSITY = {
  fresh:    0.09681,  // 1000 kg/m³ × 9.80665 / 100000 — fresh water
  en13319:  0.09964,  // 1020 kg/m³ — EN13319 standard (most dive computers)
  salt:     0.10020,  // 1027 kg/m³ — standard salt water (1/10.078 ≈ 0.09923 → ApexDeco uses 10.078m/bar)
};
let BAR_PER_METRE = 1/10.078; // ApexDeco salt water default (1027 kg/m³)

// ── Narcosis settings ──
let narcoticN2 = true;   // N₂ always narcotic by default
let narcoticO2 = true;   // O₂ narcotic by default (NOAA/IANTD standard)

function setNarcosis(gas, isNarc) {
  if (gas === 'n2') {
    narcoticN2 = isNarc;
    const sel = document.getElementById('n2NarcSel');
    if (sel) sel.value = isNarc ? 'yes' : 'no';
  } else {
    narcoticO2 = isNarc;
    const sel = document.getElementById('o2NarcSel');
    if (sel) sel.value = isNarc ? 'yes' : 'no';
  }
}

/**
 * Equivalent Narcotic Depth (END)
 * END = ((ppNarcotic / ppNarcotic_air_at_surface) - 1) / BAR_PER_METRE  ... simplified:
 * Standard formula: END = (pNarc / pNarc_air_surface) * 10 - 10  (in metres)
 * pNarc = total narcotic partial pressure at depth
 * pNarc_air_surface = narcotic pp of air at surface (reference)
 *
 * fNarcN2: N₂ fraction in gas (0–1), used if narcoticN2
 * fNarcO2: O₂ fraction in gas (0–1), used if narcoticO2
 * depthM : actual depth
 * returns END in metres (0 if no narcotic component)
 */
function calcEND(depthM, fN2) {
  const fO2 = 1 - fN2;
  const pAmb = SURFACE_P + depthM * BAR_PER_METRE;

  // Narcotic partial pressures at depth
  const pNarcN2 = narcoticN2 ? pAmb * fN2 : 0;
  const pNarcO2 = narcoticO2 ? pAmb * fO2 : 0;
  const pNarc   = pNarcN2 + pNarcO2;

  // Reference: narcotic pp of air at surface
  const fN2air = FN2_AIR;
  const fO2air = 1 - FN2_AIR;
  const pNarcAirSurface = (narcoticN2 ? SURFACE_P * fN2air : 0) +
                           (narcoticO2 ? SURFACE_P * fO2air : 0);

  if (pNarcAirSurface <= 0) return 0; // no narcotic component at all

  // END = depth at which air would produce same narcotic pp
  // pNarcAirSurface + END * BAR_PER_METRE * (fN2air*(narcoticN2?1:0) + fO2air*(narcoticO2?1:0)) = pNarc
  const narcoticFracAir = (narcoticN2 ? fN2air : 0) + (narcoticO2 ? fO2air : 0);
  const end = narcoticFracAir > 0
    ? (pNarc / narcoticFracAir - SURFACE_P) / BAR_PER_METRE
    : 0;
  return Math.max(0, end);
}

function setWaterDensity(type) {
  BAR_PER_METRE = WATER_DENSITY[type] || WATER_DENSITY.salt;
  const sel = document.getElementById('waterDensitySelect');
  if (sel) sel.value = type;
  localStorage.setItem('waterDensity', type);
}
function updateWaterVapor() {
  const val = parseFloat(document.getElementById('waterVapor')?.value) || 0.0627;
  WATER_VAPOR = val;
}

function initTissues() {
  const pN2 = (SURFACE_P - WATER_VAPOR) * 0.7902;  // alveolar N2 at surface
  return ZHL16C.map(() => pN2);
}

function toggleCustomO2() {
  const isCustom = document.getElementById('gasMix').value === 'custom';
  document.getElementById('customO2Field').style.display = isCustom ? 'block' : 'none';
}

function getN2Frac(mix) {
  if (mix === 'ean32') return FN2_EAN32;
  if (mix === 'ean36') return FN2_EAN36;
  if (mix === 'custom') {
    const o2pct = parseFloat(document.getElementById('customO2')?.value) || 21;
    return (100 - Math.min(40, Math.max(21, o2pct))) / 100;
  }
  return FN2_AIR;
}

function depthBar(m)   { return SURFACE_P + m * BAR_PER_METRE; }
function schreiner(p0, pGas, ht, t) { return pGas + (p0-pGas) * Math.exp(-Math.LN2/ht*t); }

/**
 * Schreiner equation for linearly changing ambient pressure (ascent/descent).
 * pAmb changes at rate R (bar/min) from p0Amb over time t.
 * R = rateM * BAR_PER_METRE for descent (+ve), negative for ascent.
 */
function schreinerLinear(p0, fN2, ht, t, p0Amb, R) {
  const k   = Math.LN2 / ht;
  const piN2 = (p0Amb - WATER_VAPOR) * fN2;  // inspired pN2 minus water vapor
  const rN2  = R * fN2;                         // rate of change of inspired pN2
  return piN2 + rN2 * (t - 1/k) - (piN2 - p0 - rN2/k) * Math.exp(-k * t);
}

/**
 * Saturate tissues during a linear pressure change (descent or ascent).
 * fromDepth → toDepth over time t minutes, breathing fN2.
 */
function saturateLinear(tissues, fromDepth, toDepth, t, fN2) {
  if (t <= 0) return tissues;
  const p0Amb = depthBar(fromDepth);
  const pEndAmb = depthBar(toDepth);
  const R = (pEndAmb - p0Amb) / t;  // bar/min (+ve descent, -ve ascent)
  return tissues.map((p0, i) => schreinerLinear(p0, fN2, ZHL16C[i][0], t, p0Amb, R));
}

/**
 * Z-factor (compressibility) for N₂ at diving pressures.
 * Uses a simplified virial equation fitted to NIST data for N₂ (0–20 bar, 20–37°C).
 * Z ≈ 1 + B(T)·P  where B ≈ −4.0e-3 bar⁻¹ at ~25°C for N₂.
 * Effective pN2_real = pN2_ideal / Z(pAmb)
 * This correction is small (<2% at 6 bar) but included for completeness.
 */
function zFactorN2(pBar) {
  // Second virial coefficient B for N₂ at ~25°C ≈ -4.0e-3 L/mol, converted to bar⁻¹ ≈ +0.00166
  // Net effect: at high pressure N₂ is slightly less soluble than ideal
  const B = 0.00166; // bar⁻¹  (positive = slightly supra-ideal at dive pressures)
  return 1 + B * pBar;
}

function saturate(tissues, depthM, t, fN2) {
  const pN2 = (depthBar(depthM) - WATER_VAPOR) * fN2;
  return tissues.map((p0,i) => schreiner(p0, pN2, ZHL16C[i][0], t));
}

function ceiling(tissues, gfHigh) {
  // Baker GF formula: stop required if pN2 > pAmb + GF*(M_value - pAmb)
  // Equivalent ceiling: pAmb = (pN2 - GF*a) / (1 - GF + GF/b)
  let maxC = 0;
  tissues.forEach((pN2, i) => {
    const [,a,b] = ZHL16C[i];
    const pAmbMin = (pN2 - gfHigh * a) / (1 - gfHigh + gfHigh / b);
    const cM = Math.max(0, (pAmbMin - SURFACE_P) / BAR_PER_METRE);
    if (cM > maxC) maxC = cM;
  });
  return maxC;
}

function buhNDL(depthM, fN2, gfLow, gfHigh) {
  let tissues = initTissues();
  for (let t=0; t<=500; t++) {
    const next = saturate(tissues, depthM, 1, fN2);
    if (ceiling(next, gfHigh/100) > 0) return t;
    tissues = next;
  }
  return 500;
}

function maxSatPct(tissues, gfHigh) {
  let max = 0;
  tissues.forEach((pN2, i) => {
    const [,a,b] = ZHL16C[i];
    const mv = a*(gfHigh/100) + SURFACE_P/b;
    const pct = Math.round((pN2/mv)*100);
    if (pct > max) max = pct;
  });
  return max;
}

// ═══════════════════════════════════════════════
// PADI LOOKUP
// ═══════════════════════════════════════════════
function padiNDL(depthM, mix) {
  return getNitroxNDL(depthM, mix || 'air');
}
function padiGroup(depthM, time, mix) {
  const ndl = getNitroxNDL(depthM, mix || 'air');
  const pct = time/ndl;
  const gi  = Math.min(PADI_GROUPS.length-1, Math.floor(pct * PADI_GROUPS.length * 0.7));
  return PADI_GROUPS[gi];
}

// ═══════════════════════════════════════════════
// PLANNER
// ═══════════════════════════════════════════════
function runPlanner() {
  const isMetric = units === 'metric';
  const rawD = parseFloat(document.getElementById('depth').value)||30;
  const depthM = isMetric ? rawD : rawD/3.28084;
  const bt  = parseInt(document.getElementById('bt').value)||25;
  const gfL = mGF.low;
  const gfH = mGF.high;
  const mix = document.getElementById('gasMix').value;
  const fN2 = getN2Frac(mix);
  const dDisp = isMetric ? rawD+' m' : rawD+' ft';
  const stopFt = stopDepthM === 3 ? 10 : 20;

  let html = '';

  if (algo === 'padi') {
    const fO2 = 1 - fN2;
    const isNitrox = mix !== 'air';
    const gasLabel = mix === 'ean32' ? 'EAN 32' : mix === 'ean36' ? 'EAN 36' : mix === 'custom' ? `EAN ${Math.round(fO2*100)}` : 'Air';
    const ndl = padiNDL(depthM, mix);
    const rem = Math.max(0, ndl-bt);
    const group = padiGroup(depthM, bt, mix);
    const pct = Math.min(100, Math.round((bt/ndl)*100));
    const bc  = pct>=100?'var(--red)':pct>=80?'var(--orange)':pct>=65?'var(--yellow)':'var(--green)';
    const btOk = bt <= ndl;
    const pO2  = parseFloat((depthBar(depthM) * fO2).toFixed(2));
    const ppO2Ok = pO2 <= 1.4;
    const modM = isNitrox ? nitroxMOD(fO2, 1.4) : null;
    const modFt = modM !== null ? Math.floor(modM * 3.28084) : null;
    const beyondMOD = isNitrox && depthM > modM;

    const gasStatHtml = isNitrox
      ? `<div class="stat"><div class="stat-val ${ppO2Ok?'g':'r'}">${pO2.toFixed(2)}</div><div class="stat-lbl">ppO₂ (bar)</div></div>`
      : '';
    const modInfoHtml = isNitrox
      ? `<div class="alert info" style="margin-top:12px;"><span>💡</span><div>MOD for ${gasLabel} @ 1.4 bar ppO₂: <strong>${isMetric ? modM+' m' : modFt+' ft'}</strong></div></div>`
      : '';
    const tableRef = isNitrox ? `PADI Nitrox ${gasLabel}` : 'PADI Air';

    html = `<div class="card">
      <div style="margin-bottom:12px;">
        <div style="margin-bottom:6px;">
          <div class="card-title" style="margin:0 0 8px 0;">Rec Results · ${dDisp} / ${bt} min · ${gasLabel}</div>
          <div class="export-row">
            <button class="btn-export" onclick="copyDiveProfile('planner')" title="Copy to clipboard"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg></button>
          <button class="btn-export" onclick="exportTXT('planner')" title="Download .txt"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg></button>
        </div>
      </div>
      <div class="stats" style="grid-template-columns:repeat(${isNitrox?4:3},1fr);margin-top:4px;margin-bottom:4px;">
        <div class="stat"><div class="stat-val ${btOk&&!beyondMOD?'g':'r'}">${bt}</div><div class="stat-lbl">Your BT</div></div>
        <div class="stat"><div class="stat-val ${rem===0?'r':rem<10?'o':'g'}">${rem}</div><div class="stat-lbl">Remaining</div></div>
        <div class="stat"><div class="stat-val" style="font-size:22px;"><span class="group-badge">${group}</span></div><div class="stat-lbl">Press. Group</div></div>
        ${gasStatHtml}
      </div>
      <div style="margin-top:14px;">
        <div style="display:flex;justify-content:space-between;font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--muted);margin-bottom:5px;letter-spacing:1px;"><span>NDL USAGE · ${tableRef}</span><span>${pct}%</span></div>
        <div class="bar-wrap"><div class="bar-fill" style="width:${pct}%;background:${bc};"></div></div>
      </div>
      ${beyondMOD ? `<div class="alert dang" style="margin-top:12px;"><span>⚠</span><div><strong>BEYOND MOD.</strong> ${dDisp} exceeds ${gasLabel} MOD of ${isMetric ? modM+' m' : modFt+' ft'} at 1.4 bar ppO₂. CNS oxygen toxicity risk — use a lower O₂ mix or reduce depth.</div></div>` : ''}
      ${!beyondMOD && !btOk ? '<div class="alert dang" style="margin-top:12px;"><span>⚠</span><div><strong>NDL EXCEEDED.</strong> Not permitted for recreational diving. Reduce bottom time.</div></div>' : ''}
      ${!beyondMOD && btOk && pct>=80 ? '<div class="alert warn" style="margin-top:12px;"><span>⚡</span><div><strong>APPROACHING LIMIT.</strong> 80%+ NDL used. Monitor closely and ascend conservatively.</div></div>' : ''}
      ${!beyondMOD && btOk && pct<80 ? '<div class="alert ok" style="margin-top:12px;"><span>✓</span><div><strong>WITHIN LIMITS.</strong> '+rem+' minutes remaining. Good safety margin.</div></div>' : ''}
      ${modInfoHtml}
      ${safetyStopHTML(stopDepthM, stopFt, stopDurMin)}
    </div>`;

  } else {
    // Bühlmann
    let tissues = initTissues();
    tissues = saturate(tissues, depthM, bt, fN2);
    lastTissues = tissues;
    const gfHF = gfH/100;
    const ndl = buhNDL(depthM, fN2, gfL, gfH);
    const ceil = ceiling(tissues, gfHF);
    const sat  = maxSatPct(tissues, gfH);
    const rem  = Math.max(0, ndl-bt);
    const pct  = Math.min(100, Math.round((bt/ndl)*100));
    const bc   = pct>=100?'var(--red)':pct>=85?'var(--orange)':pct>=70?'var(--yellow)':'var(--green)';
    const btOk = bt <= ndl && ceil <= 0;
    const pO2  = parseFloat((depthBar(depthM)*(1-fN2)).toFixed(2));

    updateTissueViz(tissues, gfH);

    html = `<div class="card">
      <div style="margin-bottom:12px;">
        <div style="margin-bottom:6px;">
          <div class="card-title" style="margin:0 0 8px 0;">Bühlmann · ${dDisp} / ${bt} min · GF ${gfL}/${gfH}</div>
          <div class="export-row">
            <button class="btn-export" onclick="copyDiveProfile('planner')" title="Copy to clipboard"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg></button>
          <button class="btn-export" onclick="exportTXT('planner')" title="Download .txt"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg></button>
        </div>
      </div>
      <div class="stats" style="grid-template-columns:repeat(5,1fr);margin-top:4px;margin-bottom:4px;">
        <div class="stat"><div class="stat-val ${btOk?'g':'r'}">${bt}</div><div class="stat-lbl">Your BT</div></div>
        <div class="stat"><div class="stat-val ${rem===0?'r':rem<10?'o':'g'}">${rem}</div><div class="stat-lbl">Remaining</div></div>
        <div class="stat"><div class="stat-val ${ceil>0?'r':'g'}">${ceil>0?Math.ceil(ceil)+' m':'0 m'}</div><div class="stat-lbl">Deco Ceil</div></div>
        <div class="stat"><div class="stat-val ${sat>=100?'r':sat>=85?'o':sat>=70?'y':'g'}">${sat}%</div><div class="stat-lbl">Max Sat</div></div>
        <div class="stat"><div class="stat-val ${pO2>1.4?'r':'g'}">${pO2.toFixed(1)}</div><div class="stat-lbl">ppO₂</div></div>
      </div>
      <div style="margin-top:14px;">
        <div style="display:flex;justify-content:space-between;font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--muted);margin-bottom:5px;letter-spacing:1px;"><span>NDL USAGE</span><span>${pct}%</span></div>
        <div class="bar-wrap"><div class="bar-fill" style="width:${pct}%;background:${bc};"></div></div>
      </div>
      ${ceil>0 ? '<div class="alert deco" style="margin-top:12px;"><span>🟣</span><div><strong>DECOMPRESSION REQUIRED.</strong> Deco ceiling at '+Math.ceil(ceil)+' m. See Deco Schedule tab for full profile.</div></div>' : ''}
      ${!btOk && ceil<=0 ? '<div class="alert dang" style="margin-top:12px;"><span>⚠</span><div><strong>NDL EXCEEDED.</strong> Reduce bottom time by '+(bt-ndl)+' min.</div></div>' : ''}
      ${btOk ? '<div class="alert ok" style="margin-top:12px;"><span>✓</span><div><strong>WITHIN NDL.</strong> GF '+gfL+'/'+gfH+'. '+rem+' minutes remaining.</div></div>' : ''}
      ${pO2>1.4 ? '<div class="alert dang"><span>⚠</span><div><strong>ppO₂ EXCEEDS 1.4 bar.</strong> CNS oxygen toxicity risk. Use lower O₂ mix or reduce depth.</div></div>' : ''}
      <div style="margin-top:8px;"><div class="alert info" style="margin-bottom:0;"><span>💡</span><div>Tissue saturation chart updated — see <strong>Tissue Sat.</strong> tab.</div></div></div>
      ${safetyStopHTML(stopDepthM, stopFt, stopDurMin)}
    </div>`;
  }

  document.getElementById('plannerResult').innerHTML = html;
  document.getElementById('plannerResult').style.display = 'block';
  setTimeout(drawPlannerProfile, 30);
}

function safetyStopHTML(depthM, depthFt, dur) {
  const desc = depthM === 3
    ? '3 m standard safety stop. Ascend at max 9 m/min (30 ft/min) and hold for ' + dur + ' min.'
    : depthM === 6
      ? '6 m deep stop: recommended for dives below 30 m. Follow with a standard 3 m stop before surfacing.'
      : '5 m safety stop. Ascend at max 9 m/min (30 ft/min) and hold for ' + dur + ' min.';
  return `<div style="background:rgba(38,208,124,0.06);border:1px solid rgba(38,208,124,0.2);border-radius:10px;padding:14px;margin-top:14px;">
    <div style="font-family:'Bebas Neue',sans-serif;font-size:13px;letter-spacing:3px;color:var(--green);margin-bottom:10px;">SAFETY STOP</div>
    <div class="stats" style="margin-top:0;">
      <div class="stat" style="padding:10px;"><div class="stat-val g" style="font-size:22px;">${depthM} m</div><div class="stat-lbl">Depth (${depthFt} ft)</div></div>
      <div class="stat" style="padding:10px;"><div class="stat-val g" style="font-size:22px;">${dur}</div><div class="stat-lbl">Duration (min)</div></div>
      <div class="stat" style="padding:10px;"><div class="stat-val g" style="font-size:22px;">9 m/min</div><div class="stat-lbl">Max ascent</div></div>
    </div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--muted);margin-top:10px;line-height:1.5;">${desc}</div>
  </div>`;
}

// ═══════════════════════════════════════════════
// NDL TABLE
// ═══════════════════════════════════════════════
function renderNDLTable() {
  const isM  = ndlUnits === 'metric';
  const ranges = { shallow:[0,1], moderate:[2,3], deeper:[4,6], deep:[7,10] };
  const sel = document.getElementById('ndlRange').value;
  const [from, to] = ranges[sel];
  const depths = isM ? PADI_DEPTHS_M.slice(from, to+1) : PADI_DEPTHS_FT.slice(from, to+1);
  const ndls   = PADI_NDL_M.slice(from, to+1);
  const isBuh  = algo === 'buh';
  const tbody  = document.getElementById('ndlBody');
  tbody.innerHTML = '';

  depths.forEach((d, i) => {
    const depthM = isM ? d : d/3.28084;
    let ndl = ndls[i];
    let buhNDLVal = '';
    if (isBuh) {
      const fN2 = FN2_AIR;
      buhNDLVal = buhNDL(depthM, fN2, mGF.low, mGF.high);
    }
    const dUnit = isM ? ' m' : ' ft';
    const isDeep = depthM > 30;
    const isCaution = depthM > 21 && depthM <= 30;
    let rowClass = isDeep ? 'danger-row' : isCaution ? 'warn-row' : '';
    let ndlClass = isDeep ? 'td-r' : isCaution ? 'td-o' : 'td-g';
    const groupIdx = Math.min(PADI_GROUPS.length-1, Math.floor(i * PADI_GROUPS.length / depths.length));
    const group = PADI_GROUPS[groupIdx];

    // MOD checks for nitrox at 1.4 bar ppO2
    const mod32 = nitroxMOD(0.32, 1.4); // ~33.75m → 33m
    const mod36 = nitroxMOD(0.36, 1.4); // ~28.9m → 28m
    const beyondMOD32 = depthM > mod32;
    const beyondMOD36 = depthM > mod36;

    // EAN32 NDL cell
    const idx2 = PADI_DEPTHS_M.indexOf(PADI_DEPTHS_M.reduce((a,v)=>Math.abs(v-depthM)<Math.abs(a-depthM)?v:a));
    const ndl32 = beyondMOD32 ? `<span style="color:var(--red);font-weight:700;" title="Beyond MOD (${isM?mod32+' m':Math.floor(mod32*3.28084)+' ft'})">—</span>` : `<span style="color:#26d07c;">${NITROX_NDL_EAN32[idx2]} min</span>`;
    const ndl36 = beyondMOD36 ? `<span style="color:var(--red);font-weight:700;" title="Beyond MOD (${isM?mod36+' m':Math.floor(mod36*3.28084)+' ft'})">—</span>` : `<span style="color:#00d9ff;">${NITROX_NDL_EAN36[idx2]} min</span>`;

    const ndlDisplay = isBuh
      ? `${buhNDLVal>=500?'500+':buhNDLVal} min <span style="color:var(--muted);font-size:10px;">(Air: ${ndl}) GF ${mGF.low}/${mGF.high}</span>`
      : `${ndl} min`;

    tbody.innerHTML += `<tr class="${rowClass}">
      <td><strong>${d}${dUnit}</strong></td>
      <td class="${ndlClass}">${ndlDisplay}</td>
      <td>${isBuh ? '—' : ndl32}</td>
      <td>${isBuh ? '—' : ndl36}</td>
      <td>${isBuh ? '—' : `<span class="group-badge">${group}</span>`}</td>
      <td style="color:var(--muted);">60+ min recommended</td>
    </tr>`;
  });
}

// ═══════════════════════════════════════════════
// TISSUE VIZ (Bühlmann)
// ═══════════════════════════════════════════════
function updateTissueViz(tissues, gfH) {
  const gfF   = gfH / 100;
  const grid  = document.getElementById('tissueGrid');
  const tbody = document.getElementById('tissueTableBody');
  if (!grid) return;
  grid.innerHTML = '';
  if (tbody) tbody.innerHTML = '';

  tissues.forEach((pN2, i) => {
    const [ht, a, b] = ZHL16C[i];
    const mv  = a * gfF + SURFACE_P / b;
    const pct = Math.min(100, Math.round((pN2 / mv) * 100));
    const col = pct >= 100 ? 'var(--red)' : pct >= 85 ? 'var(--orange)' : pct >= 70 ? 'var(--yellow)' : 'var(--green)';
    const tc  = pct >= 100 ? '#ff7080' : pct >= 85 ? '#ff9a40' : pct >= 70 ? '#ffe060' : '#70f0aa';
    const status = pct >= 100 ? '!! LIMIT' : pct >= 85 ? '! HIGH' : pct >= 70 ? '~ MED' : 'OK';

    // Horizontal bar row
    const row = document.createElement('div');
    row.style.cssText = 'display:flex;align-items:center;gap:8px;margin-bottom:5px;';
    row.innerHTML = `
      <span style="font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--muted);min-width:24px;text-align:right;">${i+1}</span>
      <div style="flex:1;background:var(--bg-alt);border-radius:3px;height:12px;overflow:hidden;">
        <div style="width:${pct}%;height:100%;background:${col};border-radius:3px;transition:width 0.3s;"></div>
      </div>
      <span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:${col};min-width:36px;text-align:right;">${pct}%</span>`;
    grid.appendChild(row);

    if (tbody) tbody.innerHTML += `<tr>
      <td>${i+1}</td><td>${ht}</td>
      <td>${pN2.toFixed(3)}</td><td>${mv.toFixed(3)}</td>
      <td style="color:${tc}">${pct}%</td><td>${status}</td>
    </tr>`;
  });
  const ttc = document.getElementById('tissueTableCard');
  if (ttc) ttc.style.display = 'block';
}

// ═══════════════════════════════════════════════
// DECO SCHEDULE
// ═══════════════════════════════════════════════
function toggleDecoCustomO2(selectId, fieldId) {
  const isCustom = document.getElementById(selectId).value === 'custom';
  document.getElementById(fieldId).style.display = isCustom ? 'block' : 'none';
}

function getDecoGasFrac(selectId, customId) {
  const mix = document.getElementById(selectId)?.value;
  if (!mix || mix === 'none') return null;
  if (mix === 'ean50')  return 0.50;  // fN2 = 50%
  if (mix === 'ean80')  return 0.20;  // fN2 = 20%
  if (mix === 'o2')     return 0.00;  // pure O2, fN2 = 0
  if (mix === 'custom') {
    const o2pct = parseFloat(document.getElementById(customId)?.value) || 50;
    return (100 - Math.min(100, Math.max(21, o2pct))) / 100;
  }
  return null;
}

function getDecoGasLabel(selectId, customId) {
  const mix = document.getElementById(selectId)?.value;
  if (!mix || mix === 'none') return null;
  if (mix === 'ean50')  return 'EAN 50';
  if (mix === 'ean80')  return 'EAN 80';
  if (mix === 'o2')     return '100% O₂';
  if (mix === 'custom') return `EAN ${document.getElementById(customId)?.value || 50}`;
  return null;
}

// Returns the best available gas at a given depth.
// "Best" = lowest fN2 (highest O₂) whose floored ppO₂ at curDepthM is within
// that gas's own ppO2 limit (determined by O2 fraction band via getPPO2Limit).
// Switch depths are exact meters so gas switches happen precisely at the right ppO₂.
function resetToDefaults() {
  if (!confirm('Reset all settings to defaults?')) return;

  // ApexDeco-matched defaults
  const defaults = {
    // Rates
    descentRate:      '22',
    ascentRate:       '9',
    decoAscentRate:   '9',
    surfaceAscentRate:'9',
    // Stop settings
    decoStep:         '3',
    lastDecoStop:     '6',
    minStopTime:      '1',
    stopRounding:     'fractional',
    waterVapor:       '0.0627',
    // ppO2 limits
    ppo2Bottom:       '1.4',
    ppo2Deco:         '1.6',
    // SAC rates
    sacBottom:        '22',
    sacDeco:          '20',
    // Narcosis
    n2NarcSel:        'yes',
    o2NarcSel:        'yes',
    // Deco plan inputs
    decoDepth:        '40',
    decoBT:           '25',
    decoGas:          'air',
    // Deco gases
    dg1Mix:           'ean50',
    dg2Mix:           'o2',
    // Cylinder defaults
    cylBot_size:      '12',
    cylBot_pres:      '200',
    cylDg1_size:      '11',
    cylDg1_pres:      '200',
    cylDg2_size:      '11',
    cylDg2_pres:      '200',
  };

  // Apply to all DOM fields
  Object.entries(defaults).forEach(([id, val]) => {
    const el = document.getElementById(id);
    if (el) el.value = val;
  });

  // Reset GF to default preset 40/80
  setGF(20, 85);

  // Reset water density to salt default
  setWaterDensity('salt');

  // Apply water vapor constant
  updateWaterVapor();

  // Clear custom O2 fields visibility
  toggleDecoCustomO2?.('dg1Mix', 'dg1CustomField');
  toggleDecoCustomO2?.('dg2Mix', 'dg2CustomField');

  // Clear localStorage v4
  try { localStorage.removeItem('lspDiveSettings_v5'); } catch(e) {}

  // Save fresh defaults
  if (typeof appSettings !== 'undefined' && appSettings.save) {
    appSettings.save(false);
  }

  // Clear any existing results
  const dr = document.getElementById('decoResult');
  if (dr) dr.style.display = 'none';

  // Update switch depth displays without running full schedule
  if (typeof runDecoSchedule === 'function') {
    // Only update the switch depth display fields, not generate a full plan
    const el1 = document.getElementById('dg1SwitchDepthDisplay');
    const el2 = document.getElementById('dg2SwitchDepthDisplay');
    if (el1) el1.value = 'Calculate to see';
    if (el2) el2.value = 'Calculate to see';
  }

  console.log('[LSP] ↺ Settings reset to defaults (ApexDeco-matched)');
}


function getActiveGas(curDepthM, bottomFN2, decoGases, getPPO2LimitFn, bottomLabel) {
  let best = null;
  for (const dg of decoGases) {
    if (curDepthM > dg.depth) continue;
    const fO2 = 1 - dg.fN2;
    // Pure O2 (≥99.5%): allowed at its switch depth regardless of ppO2
    // ApexDeco uses o2MaxDepth special-case — we mirror that here
    const isPureO2 = fO2 >= 0.995;
    if (!isPureO2) {
      const limit = getPPO2LimitFn ? getPPO2LimitFn(dg.fN2) : 1.6;
      const ppO2AtCur = (SURFACE_P + curDepthM * BAR_PER_METRE) * fO2;
      if (ppO2AtCur > limit + 0.001) continue;
    }
    if (best === null || dg.fN2 < best.fN2) {
      best = dg;
    }
  }
  return best || { fN2: bottomFN2, label: bottomLabel || 'Bottom' };
}

// Truncate ppO2 to 1 decimal place (floor, not round) — 1.67 → 1.6
function floorPPO2(val) {
  return Math.floor(val * 10) / 10;
}


function ppO2Check(depthM, fN2) {
  const o2frac = 1 - fN2;
  return ((SURFACE_P + depthM * BAR_PER_METRE) * o2frac).toFixed(2);
}


function runDecoSchedule() {
  try {
  const rawD   = parseFloat(document.getElementById('decoDepth').value) || 40;
  const depthM = units === 'metric' ? rawD : rawD / 3.28084;
  const bt     = parseInt(document.getElementById('decoBT').value) || 30;
  const rate            = Math.max(1, parseInt(document.getElementById('ascentRate').value)        || 9);  // to first stop
  const decoRate        = Math.max(1, parseInt(document.getElementById('decoAscentRate').value)    || 9);  // between deco stops
  const surfaceRate     = Math.max(1, parseInt(document.getElementById('surfaceAscentRate').value) || 9);  // last stop to surface
  const descentRate = Math.max(1, parseInt(document.getElementById('descentRate').value) || 22);
  const gfL    = mGF.low  / 100;
  const gfH    = mGF.high / 100;
  const ppo2Bottom = parseFloat(document.getElementById('ppo2Bottom').value) || 1.4; // bottom / lean gas
  const ppo2Deco   = parseFloat(document.getElementById('ppo2Deco').value)   || 1.6; // rich deco gas (≥45% O2)
  const minStopT   = parseFloat(document.getElementById('minStopTime').value) || 1;   // minimum stop duration (minutes)
  const switchPauseT = 0; // Gas switch is instantaneous — ApexDeco behaviour
  const wholeMinStops = (document.getElementById('stopRounding')?.value || 'fractional') === 'wholeminute';
  // Apply water vapor setting before any tissue calculations
  updateWaterVapor();
  // Keep backward-compat aliases so getPPO2Limit bands still work
  const ppo2High = ppo2Deco;    // ≥45% O2 — deco gas
  const ppo2Mid  = ppo2Bottom;  // 28–44% O2 — nitrox bottom
  const ppo2Low  = ppo2Bottom;  // ≤28%  O2 — air / lean
  const lastStop    = parseInt(document.getElementById('lastDecoStop').value) || 6;
  const decoStep    = parseInt(document.getElementById('decoStep').value)     || 3;

  // Returns the ppO2 limit for a given fN2 based on O2 fraction bands
  function getPPO2Limit(fN2) {
    const fO2pct = (1 - fN2) * 100;
    if (fO2pct >= 45) return ppo2High;
    if (fO2pct >= 28) return ppo2Mid;
    return ppo2Low;
  }

  // Convenience: most permissive limit for colour coding thresholds in table
  const maxPPO2 = Math.max(ppo2High, ppo2Mid, ppo2Low);

  // Bottom gas
  const bottomMix = document.getElementById('decoGas').value;
  const bottomMixEl = document.getElementById('decoGas');
  const bottomMixLabel = (bottomMixEl?.options[bottomMixEl?.selectedIndex]?.text || bottomMix).toUpperCase();
  let bottomFN2;
  if (bottomMix === 'custom') {
    const o2 = parseFloat(document.getElementById('decoCustomO2')?.value) || 21;
    bottomFN2 = (100 - Math.min(40, Math.max(21, o2))) / 100;
  } else {
    bottomFN2 = getN2Frac(bottomMix);
  }

  // ── Calculate optimal switch depth from ppO2 limit ──
  // ppO2 = (SURFACE_P + depth * 0.1) * fO2  ≤  maxPPO2
  // depth = (maxPPO2 / fO2 - SURFACE_P) / 0.1
  function optimalSwitchDepth(fN2) {
    const fO2 = 1 - fN2;
    if (fO2 <= 0) return 0;
    // Pure O2 (≥99.5%): switch at lastStop (ApexDeco o2MaxDepth logic)
    if (fO2 >= 0.995) return lastStop;
    const limit = getPPO2Limit(fN2);
    // Exact MOD: deepest depth where raw ppO2 strictly <= limit (no floor truncation)
    const exactMOD = (limit / fO2 - SURFACE_P) / BAR_PER_METRE;
    // Snap DOWN to nearest deco stop (multiple of decoStep) that is <= exactMOD
    const snapped = Math.floor(exactMOD / decoStep) * decoStep;
    // Never go shallower than lastStop
    return Math.max(lastStop, Math.max(0, snapped));
  }

  // Deco gas 1
  const dg1FN2   = getDecoGasFrac('dg1Mix', 'dg1CustomO2');
  const dg1Label = getDecoGasLabel('dg1Mix', 'dg1CustomO2');
  const dg1Depth = dg1FN2 !== null ? optimalSwitchDepth(dg1FN2) : null;

  // Deco gas 2
  const dg2FN2   = getDecoGasFrac('dg2Mix', 'dg2CustomO2');
  const dg2Label = getDecoGasLabel('dg2Mix', 'dg2CustomO2');
  const dg2Depth = dg2FN2 !== null ? optimalSwitchDepth(dg2FN2) : null;

  // Update switch depth display fields
  const dU = units === 'metric';
  document.getElementById('dg1SwitchDepthDisplay').value =
    dg1Depth !== null
      ? (dU ? dg1Depth + ' m' : mToFt(dg1Depth) + ' ft') +
        '  (ppO₂ ' + ((SURFACE_P + dg1Depth * BAR_PER_METRE) * (1 - dg1FN2)).toFixed(2) + ')'
      : '—';
  document.getElementById('dg2SwitchDepthDisplay').value =
    dg2Depth !== null
      ? (dU ? dg2Depth + ' m' : mToFt(dg2Depth) + ' ft') +
        '  (ppO₂ ' + ((SURFACE_P + dg2Depth * BAR_PER_METRE) * (1 - dg2FN2)).toFixed(2) + ')'
      : '—';

  // Build sorted deco gases array (deepest first — getActiveGas takes last match = shallowest applicable)
  const decoGases = [
    dg1FN2 !== null ? { depth: dg1Depth, fN2: dg1FN2, label: dg1Label } : null,
    dg2FN2 !== null ? { depth: dg2Depth, fN2: dg2FN2, label: dg2Label } : null,
  ].filter(Boolean).sort((a, b) => b.depth - a.depth);

  // Saturate tissues at depth for bottom time
  let tissues = initTissues();

  // Descent phase — proper linear Schreiner equation (pressure increases linearly)
  const descentTime = depthM / descentRate;
  tissues = saturateLinear(tissues, 0, depthM, descentTime, bottomFN2);

  // Bottom time input = total time from leaving surface (industry standard).
  // Subtract descent time to get actual time spent at depth.
  const btAtDepth = Math.max(0, bt - descentTime);
  tissues = saturate(tissues, depthM, btAtDepth, bottomFN2);
  const tissuesAtBottom = [...tissues]; // snapshot for ceiling graph overlay

  const steps = [];
  let cur = depthM;
  let rt  = bt; // run time = full BT input (descent already counted in BT)


  // ── GF anchor = ceiling(bottom_tissues, gfL) rounded up to nearest stop depth ──
  const bottomCeil = ceiling(tissues, gfL);
  const firstStopDepth = bottomCeil > 0
    ? Math.max(lastStop, Math.ceil(bottomCeil / decoStep) * decoStep)
    : 0;

  // ── Stop-based ascent engine ──
  // Start stop iteration from firstStopDepth — ascent from bottom to first stop
  // is a single linear segment. Gas switch happens at the first stop where it's available.
  // This matches ApexDeco: ascend to first stop, then iterate stops down to lastStop.
  const startStop = firstStopDepth > 0 ? firstStopDepth : lastStop;
  const stopDepths = [];
  for (let d = startStop; d >= lastStop; d -= decoStep) {
    stopDepths.push(d);
  }
  if (stopDepths.length === 0 || stopDepths[stopDepths.length - 1] !== lastStop) stopDepths.push(lastStop);

  let prevEngineGas = bottomMixLabel; // track gas for switch pause
  let decoZoneEntered = false; // true once first ceiling-forced stop fires

  // firstSwitchDepth — find first deco gas switch depth
  let firstDecoDepth   = null;
  let firstSwitchDepth = null;
  {
    let simCur = cur;
    let simPrevGas = bottomMixLabel;
    for (const sd of stopDepths) {
      if (simCur > sd) simCur = sd;
      const gas2 = getActiveGas(simCur, bottomFN2, decoGases, getPPO2Limit, bottomMixLabel);
      if (gas2.label !== simPrevGas) { firstSwitchDepth = simCur; break; }
      simPrevGas = gas2.label;
    }
  }

  // minStop zone: only enforce minimum stops within the GF-anchored deco zone
  // Do NOT force a pre-switch stop above the gas switch depth — ApexDeco switches
  // gas at the first stop where ppO2 is within limits, no forced stop above.
  const minStopZoneDepth = firstStopDepth || null;

  // ── GF interpolation: gfL at firstStopDepth → gfH at surface ──
  function gfAt(depthM) {
    if (!firstStopDepth || firstStopDepth <= 0) return gfH;
    if (depthM >= firstStopDepth) return gfL;
    const gf = gfL + (gfH - gfL) * (firstStopDepth - depthM) / firstStopDepth;
    return Math.min(gfH, Math.max(gfL, gf));
  }

  for (let si = 0; si < stopDepths.length; si++) {
    const stopDepth = stopDepths[si];
    const nextStop  = si + 1 < stopDepths.length ? stopDepths[si + 1] : 0;

    // Travel from cur to stopDepth — use appropriate ascent rate:
    // - Before first deco stop: use main ascent rate
    // - Between deco stops: use decoRate
    if (cur > stopDepth) {
      const travelGas = getActiveGas(cur, bottomFN2, decoGases, getPPO2Limit, bottomMixLabel);
      const travelRate = decoZoneEntered ? decoRate : rate;
      const travelDur = (cur - stopDepth) / travelRate;
      tissues = saturateLinear(tissues, cur, stopDepth, travelDur, travelGas.fN2);
      steps.push({
        type: 'ascent', from: cur, to: stopDepth,
        dur: travelDur, gas: travelGas.label,
        pO2: ppO2Check(cur, travelGas.fN2), fN2: travelGas.fN2
      });
      rt  += travelDur;
      cur  = stopDepth;
    }

    // Transit time for minimum stop rounding (ApexDeco style):
    // si=0: arrived via fast ascent (rate m/min), transitDur=0 for min-stop purposes
    // si>0: travelled at decoRate between stops
    const transitDur = (si === 0) ? 0 : (stopDepths[si - 1] - stopDepth) / decoRate;

    // Select best gas available at this stop depth
    const stopGas  = getActiveGas(cur, bottomFN2, decoGases, getPPO2Limit, bottomMixLabel);
    const stopFN2  = stopGas.fN2;
    const gasLabel = stopGas.label;

    // Gas switch pause — saturate tissues at this depth during the switch
    if (gasLabel !== prevEngineGas && switchPauseT > 0) {
      tissues = saturate(tissues, cur, switchPauseT, stopFN2);
      rt += switchPauseT;
    }
    prevEngineGas = gasLabel;

    // Ceiling clearance: evaluate GF at the TARGET (next stop or surface),
    // not the current stop. Baker/ApexDeco: "can I ascend TO the next stop?"
    // At last stop: target=0 → uses gfH (surface GF). This is correct.
    // Use nextStop exactly — ceiling must be strictly below the next stop.
    const ceilTarget = (nextStop < lastStop) ? 0 : nextStop;
    const gfForClear = gfAt(nextStop < lastStop ? 0 : nextStop);

    const isFirstDecoStop = (firstDecoDepth === null);
    // Step resolution: first deco stop uses fine (10-sec) resolution like ApexDeco.
    // Subsequent stops use minStopT increments — ApexDeco line 658: increment = isFirstStop ? 1/60 : minStopTime
    const holdStep = isFirstDecoStop ? 1/6 : minStopT;

    const ceil     = ceiling(tissues, gfForClear);
    const mustStop = ceil > ceilTarget;

    if (mustStop) {
      // Record the first depth where ceiling forces a stop
      if (firstDecoDepth === null) firstDecoDepth = cur;
      decoZoneEntered = true;
      // Capture RT before ceiling loop — ApexDeco snaps the arrival RT to next minute
      const rtOnArrival = rt;
      let stopT = 0;
      while (ceiling(tissues, gfForClear) > ceilTarget && stopT < 360) {
        tissues = saturate(tissues, cur, holdStep, stopFN2);
        stopT += holdStep; rt += holdStep;
      }
      if (isFirstDecoStop) {
        // First stop: always use RT-snap (fractional) — both ApexDeco and MultiDeco
        // keep the exact first-stop time (e.g. 0:33, 0:27) regardless of rounding mode.
        const rawRounded = Math.round(stopT * 60) / 60;
        const minFirstStop = Math.round((Math.ceil(rtOnArrival / minStopT) * minStopT - rtOnArrival) * 60) / 60;
        const actualStop = Math.max(rawRounded, minFirstStop);
        if (actualStop > stopT) {
          const extra = actualStop - stopT;
          tissues = saturate(tissues, cur, extra, stopFN2);
          rt += extra; stopT = actualStop;
        }
        if (stopT < 1/60) { tissues = saturate(tissues, cur, 1/60 - stopT, stopFN2); rt += 1/60 - stopT; stopT = 1/60; }
      } else {
        // Non-first stops rounding
        let roundedStop;
        if (wholeMinStops) {
          // Whole-minute: round raw hold up to nearest whole minute (transit loaded separately)
          roundedStop = Math.max(minStopT, Math.ceil(stopT / minStopT) * minStopT);
        } else {
          // Fractional: round (transit + raw) up, subtract transit
          const totalAtLevel = Math.max(minStopT, Math.ceil((transitDur + stopT) / minStopT) * minStopT);
          roundedStop = totalAtLevel - transitDur;
        }
        if (roundedStop > stopT) {
          const extra = roundedStop - stopT;
          tissues = saturate(tissues, cur, extra, stopFN2);
          rt += extra; stopT = roundedStop;
        }
      }
      steps.push({ type: 'deco', depth: cur, dur: stopT, gas: gasLabel, pO2: ppO2Check(cur, stopFN2), fN2: stopFN2 });
    } else if (minStopT > 0 && minStopZoneDepth !== null && cur <= minStopZoneDepth && cur !== lastStop) {
      decoZoneEntered = true;
      let stopT = 0;
      if (isFirstDecoStop) {
        if (firstDecoDepth === null) firstDecoDepth = cur;
        const minFirstStop = Math.ceil(rt / minStopT) * minStopT - rt;
        const snapped = Math.max(0, Math.round(minFirstStop * 60) / 60);
        // Whole-min mode: enforce minStopT only when snapped is truly near-zero (<2 sec).
        // Meaningful fractional first stops (e.g. 0:07, 0:33, 0:40) are kept — MultiDeco behaviour.
        const minVal = (wholeMinStops && snapped < 1/30) ? minStopT : 1/60;
        stopT = Math.max(snapped, minVal);
      } else {
        const needed = wholeMinStops
          ? Math.max(0, minStopT)
          : Math.max(0, minStopT - transitDur);
        stopT = needed;
      }
      if (stopT > 0) {
        tissues = saturate(tissues, cur, stopT, stopFN2);
        rt += stopT;
      }
      while (ceiling(tissues, gfForClear) > ceilTarget && stopT < 360) {
        tissues = saturate(tissues, cur, minStopT, stopFN2);
        stopT += minStopT; rt += minStopT;
      }
      if (stopT > 0) {
        steps.push({ type: 'deco', depth: cur, dur: stopT, gas: gasLabel, pO2: ppO2Check(cur, stopFN2), fN2: stopFN2 });
      }
    } else if (cur === lastStop) {
      const isDecoNeeded = steps.some(s => s.type === 'deco');
      const stopType = isDecoNeeded ? 'deco' : 'safety';
      let stopT = 0;
      if (isDecoNeeded) {
        const transitToLastStop = (stopDepths.length > 1) ? (stopDepths[stopDepths.length - 2] - lastStop) / decoRate : 0;
        while (ceiling(tissues, gfAt(0)) > 0.01 && stopT < 180) {
          tissues = saturate(tissues, cur, minStopT, stopFN2);
          stopT += minStopT; rt += minStopT;
        }
        let roundedLastStop;
        if (wholeMinStops) {
          roundedLastStop = Math.max(minStopT, Math.ceil(stopT / minStopT) * minStopT);
        } else {
          const totalAtLevel = Math.max(minStopT, Math.ceil((transitToLastStop + stopT) / minStopT) * minStopT);
          roundedLastStop = totalAtLevel - transitToLastStop;
        }
        if (roundedLastStop > stopT) {
          const extra = roundedLastStop - stopT;
          tissues = saturate(tissues, cur, extra, stopFN2);
          stopT += extra; rt += extra;
        }
        if (stopT < minStopT) {
          const extra = minStopT - stopT;
          tissues = saturate(tissues, cur, extra, stopFN2);
          stopT += extra; rt += extra;
        }
      } else {
        stopT = Math.max(3, minStopT);
        tissues = saturate(tissues, cur, stopT, stopFN2);
        rt += stopT;
      }
      steps.push({ type: stopType, depth: cur, dur: stopT, gas: gasLabel, pO2: ppO2Check(cur, stopFN2), fN2: stopFN2 });
    }
    // No stop needed and not lastStop — continue ascending
  }

  // Collapse consecutive ascent steps with the same gas into single rows
  const collapsed = [];
  for (const s of steps) {
    const prev = collapsed[collapsed.length - 1];
    if (s.type === 'ascent' && prev && prev.type === 'ascent' && prev.gas === s.gas) {
      prev.to   = s.to;
      prev.dur += s.dur;
      prev.pO2  = s.pO2; // keep last ppO2
    } else {
      collapsed.push({ ...s });
    }
  }

  const decoStops = collapsed.filter(s => s.type === 'deco');
  const decoTime  = Math.round(decoStops.reduce((a, s) => a + s.dur, 0) * 60) / 60;
  const hasDeco   = decoStops.length > 0;
  const gasUsed   = [...new Set(collapsed.map(s => s.gas))];

  // ── Headless hook: store plan for Node testing ──
  const runTimeMin = Math.round(rt);
  window._lastPlan = {
    rt: runTimeMin,
    decoTime: Math.round(decoTime),
    stops: decoStops.map(s => ({ depth: s.depth, dur: s.dur, gas: s.gas })),
    steps: collapsed,
  };

  // ── Store ceiling waypoints for graph overlay ──
  // Sample ceiling at finer resolution for smooth overlay line
  // Track ceiling from dive start (descent + bottom + deco ascent)
  {
    let ceilWps = [];

    // ── Phase 1: descent (0 → depthM over descentTime) ──
    {
      const descSteps = 8;
      let dTissues = initTissues();
      for (let di = 0; di <= descSteps; di++) {
        const frac = di / descSteps;
        const partDur = descentTime * frac;
        const partDepth = depthM * frac;
        const tis = di === 0 ? dTissues : saturateLinear([...initTissues()], 0, partDepth, partDur, bottomFN2);
        const gf = gfAt ? gfAt(partDepth) : gfH;
        const ceilM = Math.max(0, ceiling(tis, gf));
        ceilWps.push({ t: partDur, ceil: ceilM });
      }
    }

    // ── Phase 2: bottom time (at depthM, descentTime → bt) ──
    {
      const btDuration = Math.max(0, bt - descentTime);
      const btSteps = Math.min(8, Math.max(2, Math.floor(btDuration)));
      let bTissues = [...tissuesAtBottom]; // end of bottom
      // Reconstruct intermediate bottom states (simplified: just record ceiling at start and end)
      const gfBottom = gfAt ? gfAt(depthM) : gfH;
      ceilWps.push({ t: descentTime, ceil: Math.max(0, ceiling(saturateLinear([...initTissues()], 0, depthM, descentTime, bottomFN2), gfBottom)) });
      ceilWps.push({ t: bt, ceil: Math.max(0, ceiling(bTissues, gfBottom)) });
    }

    // ── Phase 3: deco ascent (from bt onward through collapsed steps) ──
    let cTissues2 = tissuesAtBottom ? [...tissuesAtBottom] : null;
    if (cTissues2) {
      let walkT = bt;
      for (const s of collapsed) {
        const gf = gfAt ? gfAt(s.type === 'ascent' ? s.to : (s.depth || 0)) : gfH;
        const ceilM = Math.max(0, ceiling(cTissues2, gf));
        ceilWps.push({ t: walkT, ceil: ceilM });
        // Intermediate samples for smoother line
        if (s.dur > 1.5) {
          const nSteps = Math.min(Math.floor(s.dur), 8);
          for (let si = 1; si < nSteps; si++) {
            const frac = si / nSteps;
            const partDur = s.dur * frac;
            const midTis = s.type === 'ascent'
              ? saturateLinear([...cTissues2], s.from, s.to, partDur, s.fN2 || bottomFN2)
              : saturate([...cTissues2], s.depth || 0, partDur, s.fN2 || bottomFN2);
            const gfMid = gfAt ? gfAt(s.type === 'ascent' ? (s.from + (s.to - s.from) * frac) : (s.depth || 0)) : gfH;
            ceilWps.push({ t: walkT + partDur, ceil: Math.max(0, ceiling(midTis, gfMid)) });
          }
        }
        if (s.type === 'ascent') {
          cTissues2 = saturateLinear(cTissues2, s.from, s.to, s.dur, s.fN2 || bottomFN2);
        } else {
          cTissues2 = saturate(cTissues2, s.depth || 0, s.dur, s.fN2 || bottomFN2);
        }
        walkT += s.dur;
      }
      ceilWps.push({ t: walkT, ceil: 0 }); // surface
    }

    // Sort by time (phases may have out-of-order due to descent reconstruction)
    ceilWps.sort((a, b) => a.t - b.t);
    window._decoCeilingWps = ceilWps;

    // Gas color segments: [{fromT, toT, gas, color}]
    // bt is run time including descent — deco phase starts at bt
    const gasColors = ['#00d9ff','#26d07c','#ffb703','#ff8c00','#a78bfa','#f472b6'];
    const gasColorMap = {};
    let gcIdx = 0;
    let gsT = bt;   // deco phase starts at bt (run time)
    const gasSegs = [];
    for (const s of collapsed) {
      if (!gasColorMap[s.gas]) { gasColorMap[s.gas] = gasColors[gcIdx++ % gasColors.length]; }
      gasSegs.push({ fromT: gsT, toT: gsT + s.dur, gas: s.gas, color: gasColorMap[s.gas] });
      gsT += s.dur;
    }
    // Prepend descent + bottom segment using bottom gas (covers 0 → bt)
    if (!gasColorMap[bottomMixLabel]) { gasColorMap[bottomMixLabel] = gasColors[gcIdx++ % gasColors.length]; }
    gasSegs.unshift({ fromT: 0, toT: bt, gas: bottomMixLabel, color: gasColorMap[bottomMixLabel] });
    window._decoGasSegments = gasSegs;
    window._decoGasColorMap = gasColorMap;
  }

  // Build gas info row with real values: label @ switch depth — O₂%
  const bottomO2pct  = Math.round((1 - bottomFN2) * 100);
  const bottomGasTag = `<span style="background:rgba(0,200,255,0.1);border:1px solid var(--accent);border-radius:4px;padding:2px 8px;font-size:10px;color:var(--accent);">Bottom: ${bottomMixLabel} — ${bottomO2pct}% O₂ @ surface→${dU ? rawD+'m' : mToFt(rawD)+'ft'}</span>`;
  const decoGasTags  = decoGases.map(dg => {
    const o2pct = Math.round((1 - dg.fN2) * 100);
    const depthDisp = dU ? dg.depth + ' m' : mToFt(dg.depth) + ' ft';
    return `<span style="background:rgba(38,208,124,0.1);border:1px solid var(--green);border-radius:4px;padding:2px 8px;font-size:10px;color:var(--green);">Deco: ${dg.label.toUpperCase()} — ${o2pct}% O₂ @ ${depthDisp}</span>`;
  }).join(' ');

  // ── END (Equivalent Narcotic Depth) at bottom depth ──
  const endM     = calcEND(depthM, bottomFN2);
  const endDisp  = Math.round(endM);
  const endColor = endM > 40 ? 'var(--red)' : endM > 30 ? 'var(--orange)' : endM > 20 ? 'var(--yellow)' : 'var(--green)';
  const narcoStr = `N₂:${narcoticN2?'✓':'✗'} O₂:${narcoticO2?'✓':'✗'}`;

  // Update live END display in the settings card
  const endLive = document.getElementById('endDisplayLive');
  if (endLive) {
    endLive.textContent = `${endDisp} m  (${narcoStr})`;
    endLive.style.color = endColor;
  }

  document.getElementById('decoSummary').innerHTML = `
    <div class="stats" style="margin-top:0;">
      <div class="stat"><div class="stat-val">${rawD} m</div><div class="stat-lbl">Depth</div></div>
      <div class="stat"><div class="stat-val">${bt} min</div><div class="stat-lbl">BT Time</div></div>
      <div class="stat"><div class="stat-val" style="font-size:13px;">${bottomMixLabel}</div><div class="stat-lbl">Bottom Gas</div></div>
      <div class="stat"><div class="stat-val ${hasDeco?'o':'g'}">${Math.round(decoTime)} min</div><div class="stat-lbl">Deco Time</div></div>
      <div class="stat"><div class="stat-val">${Math.round(rt)} min</div><div class="stat-lbl">Total Run Time</div></div>
      <div class="stat"><div class="stat-val">${mGF.low}/${mGF.high}</div><div class="stat-lbl">GF Low/High</div></div>
      <div class="stat"><div class="stat-val">${lastStop} m</div><div class="stat-lbl">Last Stop</div></div>
      <div class="stat"><div class="stat-val">${decoStep} m</div><div class="stat-lbl">Step Size</div></div>
      <div class="stat"><div class="stat-val" style="color:${endColor};font-size:15px;">${endDisp} m</div><div class="stat-lbl">END <span style="font-size:9px;color:var(--muted);">${narcoStr}</span></div></div>
    </div>
    ${decoGases.length > 0 || true ? `<div style="margin-top:10px;font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--muted);display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
      ${bottomGasTag} ${decoGasTags}
    </div>` : ''}
    ${hasDeco
      ? '<div class="alert deco" style="margin-top:10px;"><span>🟣</span><div><strong>DECOMPRESSION DIVE.</strong> Do not skip mandatory stops. Switch gas at optimal depth shown above. Verify ppO₂ before each switch.</div></div>'
      : '<div class="alert ok" style="margin-top:10px;"><span>✓</span><div><strong>NO-DECO DIVE.</strong> 3 min safety stop at 3 m included.</div></div>'}
    ${endM > 40 ? '<div class="alert dang" style="margin-top:8px;"><span>⚠</span><div><strong>HIGH NARCOTIC DEPTH.</strong> END exceeds 40 m equivalent. Consider a less narcotic gas mix.</div></div>' : endM > 30 ? '<div class="alert warn" style="margin-top:8px;"><span>⚡</span><div><strong>NARCOTIC DEPTH WARNING.</strong> END exceeds 30 m equivalent.</div></div>' : ''}`;

  const tbody = document.getElementById('decoTableBody');
  const descentTimeMin = Math.round((depthM / descentRate) * 10) / 10;

  tbody.innerHTML = '';
  let prevGas = bottomMixLabel;
  let rowRT = 0;
  // ── EAD (Equivalent Air Depth) ──
  // EAD = (fN2 × (depth + 10) / 0.79) − 10  [metres]
  function calcEAD(depthM, fN2) {
    if (fN2 >= 0.79) return null; // air — no EAD benefit
    const ead = (fN2 * (depthM + 10) / 0.79) - 10;
    return Math.max(0, Math.round(ead));
  }
  function fmtEAD(depthM, fN2) {
    const ead = calcEAD(depthM, fN2);
    if (ead === null) return '-';
    const dispEAD = dU ? ead + ' m' : Math.round(ead * 3.28084) + ' ft';
    return dispEAD;
  }

  // ── SAC gas consumption ──
  const sacBottom = parseFloat(document.getElementById('sacBottom')?.value) || 20;
  const sacDeco   = parseFloat(document.getElementById('sacDeco')?.value)   || 15;
  const BAR_PER_M = BAR_PER_METRE;
  // gasConsumed[gasLabel] = litres
  const gasConsumed = {};
  function addGas(label, depthM, dur, sac) {
    const absP = SURFACE_P + depthM * BAR_PER_M;
    const litres = sac * absP * dur;
    gasConsumed[label] = (gasConsumed[label] || 0) + litres;
  }



  // CNS% helper for a given ppO2 and duration
  function rowCNS(ppo2, dur) {
    const key = Math.round(ppo2 * 10);
    if (key < 6 || ppo2 <= 0.5) return '-';
    const limits = {6:720,7:570,8:450,9:360,10:300,11:240,12:210,13:180,14:150,15:120,16:45};
    const lo = Math.floor(ppo2*10), hi = lo+1;
    const vLo = limits[lo]||0, vHi = limits[hi]||0;
    const lim = vLo + (vHi-vLo)*(ppo2*10-lo);
    if (lim <= 0) return '>100%';
    const pct = (dur/lim)*100;
    return pct.toFixed(1)+'%';
  }

  // ── OTU per segment (NOAA formula) ──
  function segOTU(ppo2, dur) {
    if (ppo2 <= 0.5) return 0;
    return dur * Math.pow((ppo2 - 0.5) / 0.5, 0.833);
  }
  // ── CNS raw fraction per segment ──
  function segCNSfrac(ppo2, dur) {
    if (ppo2 <= 0.5) return 0;
    const limits = {6:720,7:570,8:450,9:360,10:300,11:240,12:210,13:180,14:150,15:120,16:45};
    const lo = Math.floor(ppo2*10), hi = lo+1;
    const vLo = limits[lo]||0, vHi = limits[hi]||0;
    const lim = vLo + (vHi-vLo)*(ppo2*10-lo);
    return lim > 0 ? dur / lim : 1;
  }
  // ── mm'ss" formatter ──
  function toMMSS(minutes) {
    const totalSec = Math.round(minutes * 60);
    const m = Math.floor(totalSec / 60);
    const s = totalSec % 60;
    return `${m}'${String(s).padStart(2,'0')}"`;
  }

  // Accumulators for footer
  let totalCNSfrac = 0;
  let totalOTU     = 0;

  // ── mm:ss formatter for table cells ──
  function fmtMM(minutes) {
    const totalSec = Math.round(minutes * 60);
    const m = Math.floor(totalSec / 60);
    const s = totalSec % 60;
    return `${m}:${String(s).padStart(2,'0')}`;
  }

  // ── DESCENT ROW ──
  rowRT += descentTimeMin;
  const descentPPO2 = ((rawD/2 * BAR_PER_METRE + SURFACE_P) * (1 - bottomFN2)).toFixed(2);
  totalCNSfrac += segCNSfrac(parseFloat(descentPPO2), descentTimeMin);
  totalOTU     += segOTU(parseFloat(descentPPO2), descentTimeMin);
  addGas(bottomMixLabel, rawD / 2, descentTimeMin, sacBottom);
  tbody.innerHTML += `<tr class="asc-row" data-phase="descent">
    <td><span style="font-size:18px;color:#ff8080;">↓</span></td>
    <td data-label="Depth" style="color:#ff8080;">0 → ${dU?rawD+' m':mToFt(rawD)+' ft'}</td>
    <td data-label="Stop" style="color:#ff8080;"></td>
    <td data-label="Run" style="color:#ff8080;">${fmtMM(rowRT)}</td>
    <td data-label="Mix"><span style="color:var(--accent);">${bottomMixLabel}</span></td>
    <td data-label="EAD" style="color:var(--muted);"></td>
    <td data-label="PPO2" style="color:var(--muted);">${descentPPO2}</td>
    <td data-label="CNS%" style="color:var(--muted);">${rowCNS(parseFloat(descentPPO2), descentTimeMin)}</td>
  </tr>`;

  // ── BOTTOM ROW ──
  const btAtDepthMin = Math.max(0, bt - descentTimeMin);
  rowRT += btAtDepthMin;
  const btPPO2 = ((rawD * BAR_PER_METRE + SURFACE_P) * (1 - bottomFN2)).toFixed(2);
  const btCNS  = rowCNS(parseFloat(btPPO2), btAtDepthMin);
  totalCNSfrac += segCNSfrac(parseFloat(btPPO2), btAtDepthMin);
  totalOTU     += segOTU(parseFloat(btPPO2), btAtDepthMin);
  addGas(bottomMixLabel, rawD, btAtDepthMin, sacBottom);
  tbody.innerHTML += `<tr class="asc-row" data-phase="bottom">
    <td>🔵</td>
    <td data-label="Depth" style="color:var(--accent);">${dU?rawD+' m':mToFt(rawD)+' ft'}</td>
    <td data-label="Stop" style="color:var(--accent);">${fmtMM(btAtDepthMin)}</td>
    <td data-label="Run" style="color:var(--accent);">${fmtMM(rowRT)}</td>
    <td data-label="Mix"><span style="color:var(--accent);">${bottomMixLabel}</span></td>
    <td data-label="EAD" style="color:var(--muted);"></td>
    <td data-label="PPO2" style="color:var(--muted);">${btPPO2}</td>
    <td data-label="CNS%" style="color:var(--muted);">${btCNS}</td>
  </tr>`;

  collapsed.forEach(s => {
    const pO2Val   = parseFloat(s.pO2);
    const gasLimit = getPPO2Limit(s.fN2 ?? bottomFN2);
    const pO2Color = pO2Val > gasLimit ? 'color:var(--red);font-weight:700;' : pO2Val > gasLimit * 0.97 ? 'color:var(--orange);' : 'color:var(--muted);';
    const stepDur  = typeof s.dur === 'number' ? s.dur : parseFloat(s.dur) || 0;
    rowRT += stepDur;
    const rtDisp = fmtMM(rowRT);

    // ── GAS SWITCH ROW ──
    if (s.gas !== prevGas && s.gas !== bottomMixLabel) {
      const isO2        = s.fN2 === 0;
      const switchDepth = s.type === 'deco' ? s.depth : s.from;
      const switchDepthDisp = dU ? switchDepth + ' m' : mToFt(switchDepth) + ' ft';
      const switchPpO2  = ppO2Check(switchDepth, s.fN2);
      const sppVal      = parseFloat(switchPpO2);
      const switchLimit = getPPO2Limit(s.fN2 ?? bottomFN2);
      const sppColor    = sppVal > switchLimit ? 'color:var(--red);font-weight:700;' : sppVal > switchLimit * 0.97 ? 'color:var(--orange);font-weight:700;' : '';
      tbody.innerHTML += `<tr data-phase="switch">
        <td style="font-size:16px;text-align:center;padding:10px 6px;">⇄</td>
        <td colspan="7" style="font-weight:700;font-family:'JetBrains Mono',monospace;font-size:12px;letter-spacing:1px;padding:10px 10px;">
          <strong>${s.gas.toUpperCase()}</strong> @ ${switchDepthDisp}  -  <span style="${sppColor}">ppO₂ ${switchPpO2}</span>
        </td>
      </tr>`;
    }
    prevGas = s.gas;

    const gasColor = s.type === 'deco'
      ? 'var(--red)'
      : s.fN2 === 0 ? 'var(--accent)' : 'var(--green)';

    // ── DECO STOP ROW ──
    if (s.type === 'deco') {
      const cnsPct = rowCNS(pO2Val, stepDur);
      totalCNSfrac += segCNSfrac(pO2Val, stepDur);
      totalOTU     += segOTU(pO2Val, stepDur);
      addGas(s.gas, s.depth, stepDur, sacDeco);
      const cnsColor = parseFloat(cnsPct) > 80 ? 'color:var(--red);font-weight:700;' : parseFloat(cnsPct) > 40 ? 'color:var(--yellow);' : 'color:var(--muted);';
      const eadDisp = fmtEAD(s.depth, s.fN2);
      tbody.innerHTML += `<tr class="deco-row" data-phase="deco">
        <td>🔴</td>
        <td data-label="Depth">${dU ? s.depth+' m' : mToFt(s.depth)+' ft'}</td>
        <td data-label="Stop" style="color:var(--red);">${fmtMM(stepDur)}</td>
        <td data-label="Run">${rtDisp}</td>
        <td data-label="Mix" style="color:var(--red);">${s.gas.toUpperCase()}</td>
        <td data-label="EAD" style="color:var(--muted);font-size:11px;">${eadDisp}</td>
        <td data-label="PPO2" style="${pO2Color}">${s.pO2}</td>
        <td data-label="CNS%" style="${cnsColor}">${cnsPct}</td>
      </tr>`;
    // ── SAFETY STOP ROW ──
    } else if (s.type === 'safety') {
      const cnsPct = rowCNS(pO2Val, stepDur);
      totalCNSfrac += segCNSfrac(pO2Val, stepDur);
      totalOTU     += segOTU(pO2Val, stepDur);
      addGas(s.gas, s.depth, stepDur, sacDeco);
      tbody.innerHTML += `<tr class="safe-row" data-phase="safety">
        <td style="font-size:16px;">🟢</td>
        <td data-label="Depth">${dU ? s.depth+' m' : mToFt(s.depth)+' ft'}</td>
        <td data-label="Stop" style="color:var(--green);">${fmtMM(stepDur)}</td>
        <td data-label="Run">${rtDisp}</td>
        <td data-label="Mix" style="color:${gasColor};">${s.gas.toUpperCase()}</td>
        <td data-label="EAD" style="color:var(--muted);font-size:11px;">${fmtEAD(s.depth, s.fN2)}</td>
        <td data-label="PPO2" style="color:var(--muted);">${s.pO2||'—'}</td>
        <td data-label="CNS%" style="color:var(--muted);">${cnsPct}</td>
      </tr>`;
    // ── ASCENT ROW ──
    } else {
      const cnsPct = rowCNS(pO2Val, stepDur);
      totalCNSfrac += segCNSfrac(pO2Val, stepDur);
      totalOTU     += segOTU(pO2Val, stepDur);
      addGas(s.gas, (s.from + s.to) / 2, stepDur, sacDeco);
      tbody.innerHTML += `<tr class="asc-row" data-phase="ascent">
        <td><span style="font-size:18px;" class="asc-color">↑</span></td>
        <td data-label="Depth" class="asc-color">${dU ? s.from+' m' : mToFt(s.from)+' ft'} → ${dU ? s.to+' m' : mToFt(s.to)+' ft'}</td>
        <td data-label="Stop" class="asc-color"></td>
        <td data-label="Run" class="asc-color">${rtDisp}</td>
        <td data-label="Mix" style="color:${gasColor};">${s.gas.toUpperCase()}</td>
        <td data-label="EAD" style="color:var(--muted);"></td>
        <td data-label="PPO2" style="${pO2Color}">${s.pO2}</td>
        <td data-label="CNS%" style="color:var(--muted);">${cnsPct}</td>
      </tr>`;
    }
  });

  // ── Update Tissue Saturation tab with final deco tissues ──
  if (!_contingencyRunning) {
    lastTissues = tissues;
    updateTissueViz(tissues, mGF.high);
  }

  // ── TOTALS FOOTER ROW ──
  const totalCNSpct  = (totalCNSfrac * 100).toFixed(1);
  const totalOTUval  = Math.round(totalOTU);
  const totalRunMMSS = toMMSS(rowRT);
  const decoTimeMMSS = toMMSS(decoTime);
  const cnsFootColor = totalCNSfrac >= 1 ? 'var(--red)' : totalCNSfrac >= 0.8 ? 'var(--orange)' : totalCNSfrac >= 0.5 ? 'var(--yellow)' : 'var(--green)';
  const otuFootColor = totalOTUval >= 300 ? 'var(--red)' : totalOTUval >= 200 ? 'var(--orange)' : totalOTUval >= 100 ? 'var(--yellow)' : 'var(--green)';
  tbody.innerHTML += `<tr style="background:rgba(0,200,255,0.04);border-top:2px solid var(--border-hi);" data-phase="totals">
    <td colspan="8" style="padding:8px 10px;font-family:'JetBrains Mono',monospace;font-size:11px;white-space:nowrap;">
      <span style="color:var(--muted);">Run time:</span> <span style="color:var(--text);font-weight:700;margin-right:16px;">${totalRunMMSS}</span><span style="color:var(--muted);">Deco time:</span> <span style="color:${hasDeco ? 'var(--orange)' : 'var(--green)'};font-weight:700;margin-right:16px;">${decoTimeMMSS}</span><span style="color:var(--muted);">CNS:</span> <span style="color:${cnsFootColor};font-weight:700;margin-right:16px;">${totalCNSpct}%</span><span style="color:var(--muted);">OTU:</span> <span style="color:${otuFootColor};font-weight:700;">${totalOTUval}</span>
    </td>
  </tr>`;

  document.getElementById('decoResult').style.display = 'block';

  // ── GAS CONSUMPTION SUMMARY ──
  const gasEl = _contingencyRunning
    ? document.getElementById('emergencyGasConsumption')
    : document.getElementById('gasConsumptionSummary');
  if (!_contingencyRunning) {
    // Clear emergency gas section when running main plan
    const emEl = document.getElementById('emergencyGasConsumption');
    if (emEl) emEl.style.display = 'none';
  }
  if (gasEl && Object.keys(gasConsumed).length) {

    // Build cylinder capacity map: gas label → available litres
    // Match cylinders to gas labels by position (bottom, deco1, deco2)
    const gasLabels  = Object.keys(gasConsumed); // e.g. ['AIR','EAN 50','100% O2']
    const cylIds = [
      ['cylBot_size','cylBot_pres'],
      ['cylDg1_size','cylDg1_pres'],
      ['cylDg2_size','cylDg2_pres'],
    ];
    const cylCapacity = {}; // gas label → available litres
    gasLabels.forEach((label, idx) => {
      const [sId, pId] = cylIds[idx] || [];
      if (!sId) return;
      const sz  = parseFloat(document.getElementById(sId)?.value) || 0;
      const prRaw = parseFloat(document.getElementById(pId)?.value) || 0;
      // Pressure input is in bar (metric) or psi (imperial) — always calc in bar
      const pr = units === 'imperial' ? prRaw / 14.5038 : prRaw;
      if (sz > 0 && pr > 0) cylCapacity[label] = sz * pr;
    });

    const hasCylinders = Object.keys(cylCapacity).length > 0;
    let warnings = '';
    let html = `<div class="card" style="margin-top:8px;"><div class="card-title">${_contingencyRunning ? 'Emergency Gas Consumption' : 'Gas Consumption'}</div>`;
    html += '<div class="stats" style="grid-template-columns:repeat(auto-fit,minmax(140px,1fr));margin-top:0;">';

    for (const [gas, litres] of Object.entries(gasConsumed)) {
      const avail    = cylCapacity[gas];
      const hasInfo  = avail > 0;
      const barUsed  = hasInfo ? Math.round(litres / (cylCapacity[gas] / (parseFloat(document.getElementById(cylIds[Object.keys(gasConsumed).indexOf(gas)]?.[0])?.value) || 1))) : null;
      const pct      = hasInfo ? Math.min(100, Math.round((litres / avail) * 100)) : null;
      const over     = hasInfo && litres > avail;
      const col      = over ? 'var(--red)' : pct > 80 ? 'var(--yellow)' : 'var(--green)';

      html += `<div class="stat">
        <div class="stat-val" style="font-size:18px;color:${over?'var(--red)':'var(--text)'};">${Math.round(litres)} L</div>
        <div class="stat-lbl">${gas.toUpperCase()}</div>
        ${hasInfo ? `<div style="margin-top:4px;background:var(--bg-alt);border-radius:3px;height:6px;overflow:hidden;">
          <div style="width:${pct}%;height:100%;background:${col};border-radius:3px;"></div>
        </div>
        <div style="font-size:10px;color:${col};margin-top:2px;font-family:'JetBrains Mono',monospace;">${over?'⚠ SHORT':'✓'} ${Math.round(avail)} L avail</div>` : ''}
      </div>`;

      if (over) {
        const short = Math.round(litres - avail);
        warnings += `<div class="alert dang" style="margin-top:6px;"><span>⚠</span><div><strong>${gas.toUpperCase()} runs out</strong> — need ${Math.round(litres)} L, have ${Math.round(avail)} L. Short by <strong>${short} L</strong>. Reduce BT or add more gas.</div></div>`;
      }
    }

    html += `</div>`;
    if (warnings) html += warnings;
    html += `<div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--muted);margin-top:8px;letter-spacing:1px;">Bottom SAC: ${sacBottom} L/min · Deco SAC: ${sacDeco} L/min</div></div>`;
    gasEl.innerHTML = html;
    gasEl.style.display = 'block';
  }

  // Tissue handled by updateTissueViz via tissueInlineCard

  if (!_contingencyRunning) {
    document.getElementById('tissueInlineCard').style.display = 'block';
    document.getElementById('tissueTableCard').style.display = 'block';
    document.getElementById('gfCurveInlineCard').style.display = 'block';
    document.getElementById('contingencyCard').style.display = 'block';
    const _dgc = document.getElementById('diveGraphCard'); if (_dgc) _dgc.style.display = 'block';
    buildContingencyButtons();
    document.getElementById('contingencyResult').style.display = 'none';
    setTimeout(() => {
      const dgc = document.getElementById('diveGraphCard');
      if (dgc) dgc.style.display = 'block';
      setTimeout(drawDecoProfile, 50);
    }, 100);
    setTimeout(() => { drawGFCurve(); attachGFCurveInteraction(); }, 250);
  }
  } catch(err) {
    console.error('[Deco] Error:', err);
    document.getElementById('decoSummary').innerHTML = `<div class="alert dang"><span>⚠</span><div><strong>Error:</strong> ${err.message}</div></div>`;
    document.getElementById('decoResult').style.display = 'block';
  }
}
// ═══════════════════════════════════════════════
// MULTI DIVE
// ═══════════════════════════════════════════════
const DEFAULT_DEPTHS_M  = ['','','',''];
const DEFAULT_DEPTHS_FT = ['','','',''];

// ── NODE API ──────────────────────────────────────────────────────────
/**
 * @param {object} opts - see file header
 * @returns {{ rt, decoTime, stops:[{depth,dur,gas}], steps }} or { error }
 */
function lspDeco(opts = {}) {
  const {
    depth, bt,
    bottomFN2    = 0.79,
    gfLow        = 30,   gfHigh       = 70,
    decoGases    = [{fN2:0.50,label:'EAN50'},{fN2:0.00,label:'100% O2'}],
    waterVapor   = 0.0627,
    wholeMin     = false,
    descentRate  = 22,   ascentRate   = 9,
    decoRate     = 9,    surfRate     = 9,
    lastStop     = 6,    decoStep     = 3,   minStopT = 1,
    ppo2Bottom   = 1.4,  ppo2Deco     = 1.6,
    waterDensity = 'salt',
  } = opts;

  // Set engine globals
  WATER_VAPOR   = waterVapor;
  BAR_PER_METRE = WATER_DENSITY[waterDensity] || WATER_DENSITY.salt;
  mGF.low = gfLow;  mGF.high = gfHigh;
  global.mGF   = mGF;
  global.units = 'metric';
  window._lastPlan = null;

  // DOM helper
  const set = (id, val) => { _DOM[id] = { value:String(val), options:[{text:String(val)}], selectedIndex:0 }; };

  set('decoDepth',         depth);
  set('decoBT',            bt);
  set('descentRate',       descentRate);
  set('ascentRate',        ascentRate);
  set('decoAscentRate',    decoRate);
  set('surfaceAscentRate', surfRate);
  set('decoStep',          decoStep);
  set('lastDecoStop',      lastStop);
  set('minStopTime',       minStopT);
  set('ppo2Bottom',        ppo2Bottom);
  set('ppo2Deco',          ppo2Deco);
  set('stopRounding',      wholeMin ? 'wholeminute' : 'fractional');
  set('waterVapor',        waterVapor);
  set('n2NarcSel',         'yes');
  set('o2NarcSel',         'yes');
  set('sacBottom',         22);
  set('sacDeco',           20);
  set('customO2',          Math.round((1-bottomFN2)*100));

  // Bottom gas
  const o2bot = Math.round((1-bottomFN2)*100);
  _DOM['decoGas'] = { value: o2bot===21?'air':'custom', options:[{text:o2bot===21?'Air (21%)':'Custom'}], selectedIndex:0 };

  // Deco gases — engine reads dg1Mix/dg1CustomO2, dg2Mix/dg2CustomO2
  decoGases.forEach((g, i) => {
    const n   = i + 1;
    const o2  = g.fN2 === 0.0 ? 100 : Math.round((1-g.fN2)*100);
    // Map fN2 to select value
    let val;
    if      (g.fN2 === 0.0)  val = 'o2';
    else if (g.fN2 === 0.50) val = 'ean50';
    else if (g.fN2 === 0.20) val = 'ean80';
    else                     val = 'custom';
    _DOM[`dg${n}Mix`]      = { value: val, options:[{text:g.label||''}], selectedIndex:0 };
    set(`dg${n}CustomO2`,    o2);
    set(`dg${n}CylSize`,     g.cylSize  || 11);
    set(`dg${n}CylBar`,      g.cylBar   || 200);
  });
  for (let i = decoGases.length + 1; i <= 3; i++) {
    _DOM[`dg${i}Mix`] = { value:'none', options:[{text:'None'}], selectedIndex:0 };
  }

  // Sink DOM write targets
  const _uiSinks = [
    'decoTableBody','decoSummary','endDisplayLive','gasConsumptionSummary',
    'decoGasConsumption','emergencyGasConsumption','decoResult',
    'tissueInlineCard','tissueTableCard','gfCurveInlineCard',
    'contingencyCard','diveGraphCard','contingencyResult',
    'gasLossButtons','decoError','cnsDisplay','otuDisplay',
  ];
  _uiSinks.forEach(id => {
    _DOM[id] = { get innerHTML(){ return ''; }, set innerHTML(v){}, textContent:'', style:{display:''} };
  });
  // Switch depth display fields
  ['dg1SwitchDepthDisplay','dg2SwitchDepthDisplay','dg3SwitchDepthDisplay'].forEach(id => {
    _DOM[id] = { value:'' };
  });
  // buildContingencyButtons stub
  if (typeof buildContingencyButtons === 'undefined') {
    global.buildContingencyButtons = () => {};
  }

  try {
    runDecoSchedule();
  } catch(e) {
    return { error: e.message, stack: e.stack };
  }

  const plan = window._lastPlan;
  if (!plan) return { error: 'Engine did not store _lastPlan' };
  return plan;
}

module.exports = { lspDeco };
