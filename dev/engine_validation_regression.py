#!/usr/bin/env python3
"""Engine validation regression for CCR planner — gas fractions, deco gases, profiles."""
from __future__ import annotations

import sys
import threading
import http.server
import socketserver
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
PASS: list[str] = []
FAIL: list[str] = []


def ok(msg: str) -> None:
    PASS.append(msg)
    print(f"  ✓ {msg}")


def fail(msg: str) -> None:
    FAIL.append(msg)
    print(f"  ✗ {msg}")


def start_server():
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(ROOT), **kwargs)

        def log_message(self, fmt, *args):
            pass

    httpd = socketserver.TCPServer(("127.0.0.1", 0), Handler)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, port


def run_checks(page, port: int) -> None:
    page.goto(f"http://127.0.0.1:{port}/index.html?massiveSuite=1", wait_until="domcontentloaded")
    page.wait_for_function(
        "() => window.ZHLEngine && window.VPMEngine && window.validateCcrCalculationInputs",
        timeout=60000,
    )
    page.wait_for_timeout(3000)

    settings = {
        "metric": True,
        "gfLo": 30,
        "gfHi": 85,
        "stepSize": 3,
        "lastStop": 3,
        "minStopTime": 1,
    }
    ccr = {
        **settings,
        "circuit": "CCR",
        "setpoint": 1.3,
        "descentSetpoint": 0.7,
        "bottomSetpoint": 1.2,
        "decoSetpoint": 1.3,
    }
    pscr = {
        **settings,
        "circuit": "pSCR",
        "setpoint": 0,
        "descentSetpoint": 0,
        "bottomSetpoint": 0,
        "decoSetpoint": 0,
        "scrLoopVolume": 7,
        "scrMetabolicO2": 0.85,
    }

    results = page.evaluate(
        """(payload) => {
      const { settings, ccr, pscr } = payload;
      const lv = (d, t, o2, he) => [{ depth: d, time: t, o2, he }];
      const zhl = (levels, gases, s) => window.ZHLEngine.calculate(levels, gases || [], s);
      const vpm = (levels, gases, s) => window.VPMEngine.calculate(levels, gases || [], s, 'VPMB');
      const out = {};

      out.ccrValid = zhl(lv(40, 25, 21, 0), [], ccr);
      out.ccrNoDescentSp = zhl(lv(40, 25, 21, 0), [], { ...ccr, descentSetpoint: undefined });
      out.pscrValid = zhl(lv(40, 20, 21, 0), [], pscr);
      out.ccrNanHe = zhl(lv(40, 25, 21, NaN), [], ccr);
      out.ccrBadDeco = zhl(lv(40, 25, 21, 0), [{ o2: 150, he: 0 }], ccr);
      out.ccrBadDecoMix = zhl(lv(40, 25, 21, 0), [{ o2: 50, he: 60 }], ccr);
      out.ccrNegDecoO2 = zhl(lv(40, 25, 21, 0), [{ o2: -10, he: 0 }], ccr);
      out.vpmNanHe = vpm(lv(40, 25, 21, NaN), [], ccr);
      out.vpmEmpty = vpm([], [], ccr);
      out.zhlEmpty = zhl([], [], ccr);
      out.o2OnePct = zhl(lv(40, 25, 1, 0), [], ccr);

      const dom = document.getElementById('decoGas');
      const prevMix = dom ? dom.value : null;
      const prevO2 = document.getElementById('botTrimixO2')?.value;
      const prevHe = document.getElementById('botTrimixHe')?.value;
      if (dom) dom.value = 'trimix';
      const o2El = document.getElementById('botTrimixO2');
      const heEl = document.getElementById('botTrimixHe');
      if (o2El) o2El.value = '50';
      if (heEl) heEl.value = '60';
      out.domInvalidBottom = window.validateDomDecoGases();
      if (dom && prevMix != null) dom.value = prevMix;
      if (o2El && prevO2 != null) o2El.value = prevO2;
      if (heEl && prevHe != null) heEl.value = prevHe;

      const dgMix = document.getElementById('dg1Mix');
      const prevDgMix = dgMix ? dgMix.value : null;
      const prevDgO2 = document.getElementById('dg1TrimixO2')?.value;
      const prevDgHe = document.getElementById('dg1TrimixHe')?.value;
      if (dgMix) dgMix.value = 'trimix';
      const dgO2 = document.getElementById('dg1TrimixO2');
      const dgHe = document.getElementById('dg1TrimixHe');
      if (dgO2) dgO2.value = '-10';
      if (dgHe) dgHe.value = '35';
      out.domInvalidDeco = window.validateDomDecoGases();
      if (dgMix && prevDgMix != null) dgMix.value = prevDgMix;
      if (dgO2 && prevDgO2 != null) dgO2.value = prevDgO2;
      if (dgHe && prevDgHe != null) dgHe.value = prevDgHe;

      return out;
    }""",
        {"settings": settings, "ccr": ccr, "pscr": pscr},
    )

    if results["ccrValid"].get("totalRuntime", 0) > 0 and not results["ccrValid"].get("code"):
        ok("CCR 40m/25min air produces schedule")
    else:
        fail(f"valid CCR dive failed: {results['ccrValid']}")

    if results["ccrNoDescentSp"].get("totalRuntime", 0) > 0 and not results["ccrNoDescentSp"].get("code"):
        ok("CCR without explicit descentSetpoint uses defaults")
    else:
        fail(f"CCR default setpoint dive failed: {results['ccrNoDescentSp']}")

    if results["pscrValid"].get("totalRuntime", 0) > 0 and not results["pscrValid"].get("code"):
        ok("pSCR with zero setpoints produces schedule")
    else:
        fail(f"pSCR dive failed: {results['pscrValid']}")

    for label, key, code in [
        ("CCR NaN He", "ccrNanHe", "INVALID_GAS_FRACTIONS"),
        ("CCR deco O2>100%", "ccrBadDeco", "INVALID_GAS_FRACTIONS"),
        ("CCR deco O2+He>100%", "ccrBadDecoMix", "INVALID_GAS_FRACTIONS"),
        ("CCR deco negative O2", "ccrNegDecoO2", "INVALID_GAS_FRACTIONS"),
        ("VPM CCR NaN He", "vpmNanHe", "INVALID_GAS_FRACTIONS"),
        ("VPM empty levels", "vpmEmpty", "INVALID_PROFILE"),
        ("ZHL empty levels", "zhlEmpty", "INVALID_PROFILE"),
    ]:
        got = results[key].get("code")
        if got == code:
            ok(f"{label} → {code}")
        else:
            fail(f"{label}: expected {code}, got {got!r} ({results[key]})")

    for label, key in [
        ("VPM empty levels totalRuntime", "vpmEmpty"),
        ("ZHL empty levels totalRuntime", "zhlEmpty"),
    ]:
        r = results[key]
        if r.get("totalRuntime") == 0 and r.get("error"):
            ok(f"{label} is 0")
        else:
            fail(f"{label}: expected totalRuntime 0, got {r!r}")

    o2one = results["o2OnePct"]
    if not o2one.get("code") and o2one.get("totalRuntime", 0) > 0:
        ok("O2=1 treated as 1% (matches calculation path)")
    else:
        fail(f"O2=1 percent convention failed: {o2one}")

    dom_bottom = results["domInvalidBottom"]
    if dom_bottom.get("ok") is False and any(
        e.get("code") == "INVALID_GAS_FRACTIONS" for e in dom_bottom.get("errors", [])
    ):
        ok("validateDomDecoGases rejects invalid bottom trimix in DOM")
    else:
        fail(f"DOM bottom gas validation failed: {dom_bottom}")

    dom_deco = results["domInvalidDeco"]
    if dom_deco.get("ok") is False and any(
        e.get("code") == "INVALID_GAS_FRACTIONS" for e in dom_deco.get("errors", [])
    ):
        ok("validateDomDecoGases rejects negative deco O2 in DOM")
    else:
        fail(f"DOM deco gas validation failed: {dom_deco}")


def main() -> int:
    from playwright.sync_api import sync_playwright

    print("CCR engine validation regression")
    print("=" * 50)
    httpd, port = start_server()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            run_checks(page, port)
            browser.close()
    finally:
        httpd.shutdown()

    print(f"\n{'─' * 50}")
    print(f"  Results: {len(PASS)} passed, {len(FAIL)} failed")
    print(f"{'─' * 50}\n")
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
