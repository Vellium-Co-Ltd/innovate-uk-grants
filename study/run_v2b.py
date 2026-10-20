"""PROTOCOL v2.2: Q2 financial resilience (cash; share with negative net assets) on designs A and B with their placebos, and
Q3 effects by the first project's product type (with placebo), for the two primaries. Writes data/study/RESULTS-v2b.md."""
import collections
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_analysis as R  # noqa: E402
import run_v2 as V  # noqa: E402
from analysis_data import ROOT, load_firms, load_panel  # noqa: E402


def negative(Y, crns, years):
    return np.where(np.isfinite(Y), (Y < 0).astype(float), np.nan)


def row(label, r, pl, fmt):
    a, p = r["levels_winsorised"][R.HEADLINE], pl["levels_winsorised"][1]
    return (f"| {label} | {r['funded_matched']:,} | {fmt(a['att'])} ({fmt(a['lo'])} to {fmt(a['hi'])}; {a['n']:,}) | "
            f"{fmt(p['att'])} ({fmt(p['lo'])} to {fmt(p['hi'])}) |")


def main():
    lock = R.check_lock()
    firms = load_firms()
    L = ["# Innovate UK study — resilience and programme type (v2.2; INTERNAL until published)", "",
         f"Plan v{lock['version']} (locked {lock['locked_utc']}). Each row: effect at t+3, and its placebo (grant date moved two "
         "years earlier, effect at the real t−1 — should be near zero).", "",
         "## Q2 Financial resilience", "", "| Measure, design | funded matched | t+3 effect | placebo at real t−1 |", "|---|---|---|---|"]
    na, cash = load_panel("net_assets"), load_panel("cash")
    gbp = lambda v: "–" if not np.isfinite(v) else f"£{v:+,.0f}"
    pts = lambda v: "–" if not np.isfinite(v) else f"{100 * v:+.1f} pts"
    for trend, d in ((False, "A plain"), (True, "B trend-adjusted")):
        r = R.run("cash", firms, cash, trend); pl = R.run("cash", firms, cash, trend, shift=2)
        L.append(row(f"Cash at bank, {d}", r, pl, gbp)); print(L[-1], flush=True)
        r = R.run("net_assets", firms, na, trend, outcome_hook=negative)
        pl = R.run("net_assets", firms, na, trend, outcome_hook=negative, shift=2)
        L.append(row(f"Share with negative net assets, {d}", r, pl, pts)); print(L[-1], flush=True)
    L += ["", "## Q3 By the first project's product type", ""]
    products = collections.Counter(f["product"] for f in firms.values() if f["g"] > 0)
    main_types = [p for p, n in products.most_common() if n >= 300]
    for name, trend in V.DESIGN.items():
        P = load_panel(name) if name != "net_assets" else na
        fmt = gbp if name == "net_assets" else (lambda v: "–" if not np.isfinite(v) else f"{v:+.2f}")
        L += [f"### {name.replace('_', ' ')} — {'B trend-adjusted' if trend else 'A plain'}", "",
              "| Product type | funded matched | t+3 effect | placebo at real t−1 |", "|---|---|---|---|"]
        for ptype in main_types + ["all other types"]:
            keep = {c for c, f in firms.items() if f["g"] > 0 and
                    (f["product"] == ptype if ptype != "all other types" else f["product"] not in main_types)}
            r = R.run(name, firms, P, trend, keep=keep); pl = R.run(name, firms, P, trend, keep=keep, shift=2)
            L.append(row(f"{ptype} ({products[ptype] if ptype in products else sum(n for p, n in products.items() if p not in main_types):,} funded)",
                         r, pl, fmt)); print(L[-1], flush=True)
        L.append("")
    (ROOT / "RESULTS-v2b.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
