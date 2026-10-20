"""PROTOCOL.md §5 robustness for the two primary designs (net assets: established firms, trend-adjusted; employees: plain
matched), all reported whichever way they point. Same lock check as run_analysis. Writes data/study/RESULTS-robustness.md.

Not yet here (stated in the report): coarsened exact matching, Rosenbaum bounds / E-values.
"""
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_analysis as R  # noqa: E402
from analysis_data import ROOT, load_firms, load_panel  # noqa: E402

PRIMARY = {"net_assets": True, "employees": False}   # trend-adjusted or plain


def award_counts():
    n = collections.Counter()
    for line in open(ROOT / "grants.jsonl"):
        r = json.loads(line)
        if float(r.get("Award Offered (£)") or 0) > 0 and not (r.get("Participant Withdrawn From Project") or "").lower().startswith("withdrawn"):
            n[r["CRN"]] += 1
    return n


def main():
    lock = R.check_lock()
    firms = load_firms()
    treated = {c: f for c, f in firms.items() if f["g"] > 0}
    cut = sorted(f["award"] for f in treated.values())[int(0.99 * len(treated))]
    counts = award_counts()
    variants = [
        ("Main design (as reported)", {}),
        ("Placebo: grant date moved 2 years earlier", {"shift": 2}),
        ("1:1 matching (one control each)", {"k": 1}),
        ("Covid-era cohorts (2020, 2021) left out", {"keep": {c for c, f in treated.items() if f["g"] not in (2020, 2021)}}),
        (f"Largest 1% of awards left out (> £{cut:,.0f})", {"keep": {c for c, f in treated.items() if f["award"] <= cut}}),
        ("Single-award firms only", {"keep": {c for c in treated if counts[c] == 1}}),
        ("Firms matched at sector-section level left out", {"drop_fallback": True}),
    ]
    L = ["# Innovate UK study — robustness (INTERNAL until published)", "",
         f"Protocol v{lock['version']} (locked {lock['locked_utc']}). Headline year t+{R.HEADLINE}; the placebo row's effect "
         "should be near zero because the 'grant' it tests had not yet happened.", ""]
    for name, trend in PRIMARY.items():
        panel = load_panel(name)
        design = "established firms, trend-adjusted" if trend else "plain matched"
        L += [f"## {name.replace('_', ' ')} — {design}", "",
              "| Variant | funded matched | t+3 effect (levels) | 95% interval | t+3 effect (" +
              ("asinh" if name == "net_assets" else "log 1+x") + ") | 95% interval | median firm-level t+3 (levels) | "
              "share of funded firms above their controls |", "|---|---|---|---|---|---|---|---|"]
        for label, opt in variants:
            r = R.run(name, firms, panel, trend, diag=True, **opt)
            a, b, s = r["levels_winsorised"][R.HEADLINE], r["transformed"][R.HEADLINE], r["levels_winsorised_t3_spread"]
            if opt.get("shift"):  # shifted t+1 = real t-1, the last year before the real grant
                a, b, s = r["levels_winsorised"][1], r["transformed"][1], {"median": None, "share_above_zero": None}
                label += " — effect at real t−1"
            L.append(f"| {label} | {r['funded_matched']:,} | {R.fmt(a['att'], name, 'l')} | {R.fmt(a['lo'], name, 'l')} to "
                     f"{R.fmt(a['hi'], name, 'l')} | {R.fmt(b['att'], name, 'transformed')} | {R.fmt(b['lo'], name, 'transformed')} "
                     f"to {R.fmt(b['hi'], name, 'transformed')} | {R.fmt(s['median'], name, 'l')} | "
                     f"{'' if s['share_above_zero'] is None else f'{100 * s['share_above_zero']:.0f}%'} |")
            print(L[-1], flush=True)
        L.append("")
        del panel
    L += ["Still to run: coarsened exact matching; sensitivity to unobserved confounding (Rosenbaum bounds / E-values).", ""]
    (ROOT / "RESULTS-robustness.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
