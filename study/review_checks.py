"""Checks a government analyst would ask for, run after the draft was read as the buyer (12 Oct 2026):

  1. Negative net assets vs survival: funded firms survive more, so their survivors may include weaker firms whose matched
     counterparts closed and left the sample. Bounds: every closed firm counted, from its closure year, as having negative net
     assets (failure = insolvent) and as not having them; each with the same placebo.
  2. Control reuse: matching is with replacement, and the bootstrap resamples funded firms only; how often is a control reused?
     And the headline intervals again with a bootstrap that resamples controls as well (each control's draws shared).

Writes data/study/RESULTS-review.md.   .venv/bin/python study/review_checks.py"""
import collections
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import estimate as E  # noqa: E402
import run_analysis as R  # noqa: E402
import run_v2 as V  # noqa: E402
from analysis_data import ROOT, load_firms, load_panel  # noqa: E402


def neg_after_closure(closed, as_negative):
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


def pts(e):
    return f"{100 * e['att']:+.1f} pts ({100 * e['lo']:+.1f} to {100 * e['hi']:+.1f}; {e['n']:,})"


def two_level_boot(I, reps=500, seed=1):
    """Resample funded firms, and independently reweight every control by a Poisson(1) draw shared wherever it is reused."""
    rng = np.random.default_rng(seed)
    g, M, Z = I["g"], I["matches"], I["Yw"]
    yi = {y: j for j, y in enumerate(R.YEARS)}
    rows = []
    for t, cs in M.items():
        tgt, base = int(g[t]) + R.HEADLINE, int(g[t]) - 1
        if tgt not in yi:
            continue
        kw = I["kw"]; n_pre, gap = kw.get("detrend_pre", 0), kw.get("trend_gap", 0)
        adj = lambda i: (E._slope(Z[i], yi, base - gap, n_pre) * (tgt - base)) if n_pre else 0.0   # same trend rule as estimate.firm_diffs
        dc = [(c, Z[c, yi[tgt]] - Z[c, yi[base]] - adj(c)) for c in cs]
        dc = [(c, d) for c, d in dc if np.isfinite(d)]
        dt = Z[t, yi[tgt]] - Z[t, yi[base]] - adj(t)
        if dc and np.isfinite(dt):
            rows.append((dt, dc))
    ctrl = sorted({c for _, dc in rows for c, _ in dc}); ci = {c: i for i, c in enumerate(ctrl)}
    est = []
    for _ in range(reps):
        w = rng.poisson(1.0, len(ctrl)).astype(float)
        pick = rng.integers(0, len(rows), len(rows))
        vals = []
        for k in pick:
            dt, dc = rows[k]
            ww = np.array([w[ci[c]] for c, _ in dc]); dd = np.array([d for _, d in dc])
            if ww.sum() > 0:
                vals.append(dt - (ww * dd).sum() / ww.sum())
        est.append(np.mean(vals))
    point = float(np.mean([dt - np.mean([d for _, d in dc]) for dt, dc in rows]))
    return float(np.percentile(est, 2.5)), float(np.percentile(est, 97.5)), len(rows), point


def main():
    R.check_lock()
    firms = load_firms()
    na, emp = load_panel("net_assets"), load_panel("employees")
    closed = V.closure_years(firms, [na, emp])
    L = ["# Innovate UK study — checks from the buyer's read of the draft (INTERNAL until published)", "",
         "## 1. Negative net assets, with closed firms counted", "",
         "| Design | closed firms treated as | t+3 effect (95%; firms) | placebo at real t−1 |", "|---|---|---|---|"]
    for trend, d in ((False, "A plain"), (True, "B trend-adjusted")):
        for neg, lab in ((True, "negative net assets from closure"), (False, "not negative from closure")):
            r = R.run("net_assets", firms, na, trend, outcome_hook=neg_after_closure(closed, neg))["levels_winsorised"][R.HEADLINE]
            p = R.run("net_assets", firms, na, trend, outcome_hook=neg_after_closure(closed, neg), shift=2)["levels_winsorised"][1]
            L.append(f"| {d} | {lab} | {pts(r)} | {pts(p)} |"); print(L[-1], flush=True)
    L += ["", "## 2. Control reuse and intervals that allow for it", "",
          "| Design | funded matched | control matches | distinct controls | matches whose control is used more than once | most uses of one control | "
          "headline (95%, funded firms resampled) | 95% with controls also resampled |", "|---|---|---|---|---|---|---|---|"]
    for name, trend, P in (("net_assets", True, na), ("employees", False, emp)):
        res = R.run(name, firms, P, trend, internals=True)
        I, h = res["_internals"], res["levels_winsorised"][R.HEADLINE]
        uses = collections.Counter(c for cs in I["matches"].values() for c in cs)
        n_m = sum(uses.values()); multi = sum(v for v in uses.values() if v > 1)
        lo, hi, n, point = two_level_boot(I)
        assert abs(point - h["att"]) <= 1e-6 * max(1, abs(h["att"])), f"reuse bootstrap centred on {point}, headline {h['att']}"
        f = (lambda v: f"£{v:+,.0f}") if name == "net_assets" else (lambda v: f"{v:+.2f}")
        L.append(f"| {name.replace('_', ' ')} {'B' if trend else 'A'} | {len(I['matches']):,} | {n_m:,} | {len(uses):,} | "
                 f"{100 * multi / n_m:.0f}% | {max(uses.values())} | {f(h['att'])} ({f(h['lo'])} to {f(h['hi'])}) | {f(lo)} to {f(hi)} ({n:,} firms) |")
        print(L[-1], flush=True)
    (ROOT / "RESULTS-review.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
