"""Prove the estimator on simulated firms where the true grant effect is known (writes data/study/SIM-CHECK.md).

The simulation copies the real problem: bigger, faster-growing firms are more likely to win grants (selection on
observables), grants arrive in staggered cohorts, firms have their own levels and trends, and some years are missing.
Scenario A plants a known effect that builds over time; scenario B plants none. Repeated runs check that 95% intervals
cover the truth about 95% of the time, and that a naive funded-vs-unfunded comparison is wrong.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import estimate as E  # noqa: E402

YEARS = list(range(2010, 2026))
EVENTS = list(range(-6, 6))
TRUE = {e: (0.0 if e < 0 else 0.6 * (e + 1)) for e in EVENTS}   # employees gained by year e after the grant


def simulate(rng, n=20000, effect=True):
    size0 = rng.lognormal(1.5, 0.9, n)                      # baseline employees
    growth = rng.normal(0.25, 0.4, n)                       # firm's own trend (employees per year)
    sector = rng.integers(0, 8, n)
    age = rng.integers(1, 30, n)
    score = -5.2 + 0.45 * np.log(size0) + 1.1 * growth + 0.02 * (sector == 3) - 0.01 * age
    funded = rng.random(n) < 1 / (1 + np.exp(-score))       # selection: bigger, faster growers win more often
    g = np.where(funded, rng.choice(np.arange(2017, 2023), n), 0)
    Y = np.empty((n, len(YEARS)))
    for j, y in enumerate(YEARS):
        Y[:, j] = size0 + growth * (y - 2013) + rng.normal(0, 0.8, n)
        if effect:
            e = y - g
            Y[:, j] += np.where((g > 0) & (e >= 0), 0.6 * (np.clip(e, 0, 5) + 1), 0)
    Y[rng.random(Y.shape) < 0.12] = np.nan                  # missing filings
    pre = np.column_stack([Y[:, YEARS.index(2014)], Y[:, YEARS.index(2015)], age])  # last column = age (used as extra)  # pre-period covariates (before any grant)
    pre = np.where(np.isnan(pre), np.nanmean(pre, 0), pre)
    stratum = sector
    return g, stratum, pre, Y


def naive(Y, g, e=3):
    """What a careless study reports: funded firms' growth after the grant vs all unfunded firms' growth, same years."""
    out = []
    for gg in np.unique(g[g > 0]):
        b, t = YEARS.index(gg - 1), YEARS.index(gg + e) if gg + e in YEARS else None
        if t is None:
            continue
        out.append(np.nanmean(Y[g == gg, t] - Y[g == gg, b]) - np.nanmean(Y[g == 0, t] - Y[g == 0, b]))
    return float(np.mean(out))


def main(reps=40):
    rng = np.random.default_rng(20261011)
    lines = ["# Estimator check on simulated firms (known answer)", "",
             "Selection on size and growth, staggered cohorts 2017–2022, firm-specific trends, 12% missing filings, "
             f"20,000 firms per run, {reps} runs per scenario. Matching: 5 nearest within sector, caliper 0.2 SD; "
             "matched within each grant cohort on its own three pre-grant years (levels and slope) plus firm age.", ""]
    for name, eff in (("A: true effect builds to +3.6 employees by year 5", True), ("B: no effect at all", False)):
        cover = {e: {} for e in EVENTS if e != -1}
        ests = {e: {} for e in EVENTS if e != -1}
        naive_e3, smd_max = [], []
        for _ in range(reps):
            g, st, X, Y = simulate(rng, effect=eff)
            age = X[:, -1]
            m = E.match_by_cohort(Y, YEARS, g, st, extra=age)
            smd_max.append(float(np.abs(E.balance(E.cohort_covariates(Y, YEARS, 2019, age), {t: c for t, c in m.items() if g[t] == 2019})).max()))
            seed = int(rng.integers(1e9))
            for tag, dtp in (("matched DiD", 0), ("trend-adjusted", 3)):
                att = E.att_by_event(Y, YEARS, g, m, EVENTS, detrend_pre=dtp, trend_gap=3 if dtp else 0)
                ci = E.bootstrap(Y, YEARS, g, m, EVENTS, reps=200, seed=seed, detrend_pre=dtp, trend_gap=3 if dtp else 0)
                for e in cover:
                    truth = TRUE[e] if eff else 0.0
                    ests[e].setdefault(tag, []).append(att[e][0])
                    cover[e].setdefault(tag, 0)
                    cover[e][tag] += ci[e][0] <= truth <= ci[e][1]
            naive_e3.append(naive(Y, g))
        lines += [f"## Scenario {name}", "", "Years −6 to −4 are before the matching window (placebo: should be ~0); −3 to −2 are matched on.", "",
                  "| Years after grant | True effect | Matched DiD estimate | covers truth | Trend-adjusted (trend from years before matching) | covers truth |",
                  "|---|---|---|---|---|---|"]
        for e in cover:
            truth = TRUE[e] if eff else 0.0
            a, b = "matched DiD", "trend-adjusted"
            lines.append(f"| {e} | {truth:+.2f} | {np.nanmean(ests[e][a]):+.2f} | {100 * cover[e][a] / reps:.0f}% | "
                         f"{np.nanmean(ests[e][b]):+.2f} | {100 * cover[e][b] / reps:.0f}% |")
        t3 = TRUE[3] if eff else 0.0
        lines += ["", f"- Naive funded-vs-unfunded comparison at year 3: {np.mean(naive_e3):+.2f} (truth {t3:+.2f}) — "
                  f"{'overstates' if np.mean(naive_e3) > t3 else 'understates'} by {abs(np.mean(naive_e3) - t3):.2f}.",
                  f"- Largest covariate imbalance after matching (standardised difference): mean {np.mean(smd_max):.3f} "
                  "(target < 0.1).", ""]
    out = Path(__file__).resolve().parent.parent / "data" / "study" / "SIM-CHECK.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 40)
