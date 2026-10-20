"""Second set of buyer-read checks (12 Oct 2026).

  3. Like for like: the placebo can only be built for firms with the longer pre-grant history. The main t+3 effect re-estimated
     on exactly the funded firms that the placebo matched, so effect and pre-grant gap describe the same firms.
  4. Negative net assets with closed firms counted, only among firms open at the end of the grant year (both sides), so a
     closure before the grant cannot count against the comparison alone (the immortal-time rule, lesson L07).

Appends to data/study/RESULTS-review.md.   .venv/bin/python study/review_checks2.py"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_analysis as R  # noqa: E402
import run_v2 as V  # noqa: E402
from analysis_data import ROOT, load_firms, load_panel  # noqa: E402


def neg_from_closure_open_at_t0(closed, firms, as_negative):
    """Closed firms count as negative (or not) from closure; firms closed before or in their (or their match's) grant year
    are blanked from the grant year on, so they never enter t+3 for either side."""
    def hook(Y, crns, years):
        Z = Y.copy()
        for i, c in enumerate(crns):
            cy = closed.get(c)
            if cy:
                for j, y in enumerate(years):
                    if y >= cy and np.isnan(Z[i, j]):
                        Z[i, j] = -1.0 if as_negative else 1.0
        return np.where(np.isfinite(Z), (Z < 0).astype(float), np.nan)
    return hook


def att_open_at_t0(I, closed, e=R.HEADLINE, reps=500, seed=1):
    """Mean over funded firms open at end of t0 of (funded change − mean change of its controls open at end of t0)."""
    g, M, Z, crns = I["g"], I["matches"], I["Yw"], I["crns"]
    yi = {y: j for j, y in enumerate(R.YEARS)}
    op = lambda i, yr: not (closed.get(crns[i]) and closed[crns[i]] <= yr)
    d = []
    for t, cs in M.items():
        t0 = int(g[t]); tgt, base = t0 + e, t0 - 1
        if tgt > V.LAST_FULL_YEAR or tgt not in yi or not op(t, t0):
            continue
        dt = Z[t, yi[tgt]] - Z[t, yi[base]]
        dc = [Z[c, yi[tgt]] - Z[c, yi[base]] for c in cs if op(c, t0)]
        dc = [x for x in dc if np.isfinite(x)]
        if np.isfinite(dt) and dc:
            d.append(dt - np.mean(dc))
    d = np.array(d); lo, hi = V.boot_mean(d)
    return dict(att=float(d.mean()), lo=lo, hi=hi, n=len(d))


def main():
    R.check_lock()
    firms = load_firms()
    na, emp = load_panel("net_assets"), load_panel("employees")
    closed = V.closure_years(firms, [na, emp])
    L = ["", "## 3. Like for like: main effect on the firms the placebo could match", "",
         "| Design | placebo-matched funded firms | t+3 effect on those firms (95%; firms at t+3) | their pre-grant gap (placebo) | t+3 effect, all firms |",
         "|---|---|---|---|---|"]
    for name, trend, P in (("net_assets", True, na), ("employees", False, emp)):
        f = (lambda v: f"£{v:+,.0f}") if name == "net_assets" else (lambda v: f"{v:+.2f}")
        pl = R.run(name, firms, P, trend, shift=2, internals=True)
        keep = {pl["_internals"]["crns"][t] for t in pl["_internals"]["matches"]}
        sub = R.run(name, firms, P, trend, keep=keep)["levels_winsorised"][R.HEADLINE]
        allf = R.run(name, firms, P, trend)["levels_winsorised"][R.HEADLINE]
        p1 = pl["levels_winsorised"][1]
        L.append(f"| {name.replace('_', ' ')} {'B' if trend else 'A'} | {len(keep):,} | {f(sub['att'])} ({f(sub['lo'])} to {f(sub['hi'])}; {sub['n']:,}) | "
                 f"{f(p1['att'])} ({f(p1['lo'])} to {f(p1['hi'])}) | {f(allf['att'])} |")
        print(L[-1], flush=True)
    L += ["", "## 4. Negative net assets with closed firms counted, firms open at the end of the grant year only", "",
          "| Design | closed firms treated as | t+3 effect (95%; firms) | placebo at real t−1 |", "|---|---|---|---|"]
    pts = lambda e: f"{100 * e['att']:+.1f} pts ({100 * e['lo']:+.1f} to {100 * e['hi']:+.1f}; {e['n']:,})"
    for trend, d in ((False, "A plain"), (True, "B matched sample, plain change")):
        for neg, lab in ((True, "negative net assets from closure"), (False, "not negative from closure")):
            hook = neg_from_closure_open_at_t0(closed, firms, neg)
            I = R.run("net_assets", firms, na, trend, outcome_hook=hook, internals=True)["_internals"]
            Ip = R.run("net_assets", firms, na, trend, outcome_hook=hook, shift=2, internals=True)["_internals"]
            r = att_open_at_t0(I, closed)
            p = att_open_at_t0(Ip, closed, e=1)   # placebo: open at the end of the shifted grant year, gap at real t−1
            L.append(f"| {d} | {lab} | {pts(r)} | {pts(p)} |"); print(L[-1], flush=True)
    with open(ROOT / "RESULTS-review.md", "a") as fh:
        fh.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
