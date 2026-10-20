"""Why do funded firms survive more? EXPLORATORY: not in PROTOCOL v2.2; added 12 Oct 2026 after all results were seen, to test
why funded firms survive more, the first question a reader would ask. Reported as exploratory, never as a plan result.

The best-identified studies of R&D grants (Howell 2017, AER; Santoleri et al. 2024, REStat; Bronzini & Iachini 2014, AEJ:EP)
find the money works by easing financing constraints, most for constrained firms, and Santoleri et al. find lower failure.
If our survival gap is the grant money keeping firms going, three things should hold; if it is selection of firms that were
going to survive anyway, none need to:
  1. dose: the gap rises with the first year's grant (survival had no placebo; a dose pattern is the next best check)
  2. constraint: the gap is larger where the funded firm was short of money a year before the grant
     (negative net assets at t-1; cash at t-1 in the lowest third)
  3. timing: the gap opens while grant money is flowing (t+1, t+2) rather than only later.
Same matched sets, same survival rule as run_v2.survival (firms open at the end of the grant year, both sides).

Writes data/study/RESULTS-mechanism.md.     .venv/bin/python study/survival_mechanism.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_analysis as R  # noqa: E402
import run_appendix as A  # noqa: E402
import run_v2 as V  # noqa: E402
from analysis_data import ROOT, load_firms, load_panel  # noqa: E402

REPS = 500


def diffs(I, closed, keep, k):
    """Per matched set: funded open at g+k minus mean of its matches open at g+k (both open at end of grant year)."""
    g, crns, M = I["g"], I["crns"], I["matches"]
    out, tr, co = [], [], []
    for t, cs in M.items():
        if t not in keep or g[t] + k > V.LAST_FULL_YEAR:
            continue
        open_ = lambda i, yr: 0.0 if (closed.get(crns[i]) and closed[crns[i]] <= yr) else 1.0
        cs = [c for c in cs if open_(c, g[t])]
        if not cs or not open_(t, g[t]):
            continue
        a, b = open_(t, g[t] + k), float(np.mean([open_(c, g[t] + k) for c in cs]))
        out.append(a - b); tr.append(a); co.append(b)
    return np.array(out), tr, co


def boot_gap(d1, d2, seed=1):
    """95% interval for mean(d1) - mean(d2), resampling matched sets within each group."""
    rng = np.random.default_rng(seed)
    if len(d1) < 2 or len(d2) < 2:
        return np.nan, np.nan
    s = [d1[rng.integers(0, len(d1), len(d1))].mean() - d2[rng.integers(0, len(d2), len(d2))].mean() for _ in range(REPS)]
    return float(np.percentile(s, 2.5)), float(np.percentile(s, 97.5))


def row(label, I, closed, keep, k):
    d, tr, co = diffs(I, closed, keep, k)
    lo, hi = V.boot_mean(d)
    return d, (f"| {label} | {100 * np.mean(tr):.1f}% | {100 * np.mean(co):.1f}% | {100 * d.mean():+.1f} pts "
               f"({100 * lo:+.1f} to {100 * hi:+.1f}) | {len(d):,} |" if len(d) else f"| {label} | – | – | – | 0 |")


def project_ends(firms):
    """Share of funded firms whose first-year projects had all ended by grant year + k (UKRI file, project end dates)."""
    import json
    ends = {}
    for line in open(ROOT / "grants.jsonl"):
        r = json.loads(line)
        c = r["CRN"]
        if c not in firms or firms[c]["g"] == 0:
            continue
        s_, _ = V.excel_year(r.get("Project Start Date"))
        e_, _ = V.excel_year(r.get("Project End Date"))
        if s_ == firms[c]["g"] and e_:
            ends[c] = max(ends.get(c, 0), e_ - s_)
    lag = np.array(list(ends.values()))
    return len(lag), {k: 100 * float(np.mean(lag <= k)) for k in (0, 1, 2, 3)}


def main():
    lock = R.check_lock()
    firms = load_firms()
    na, emp, cash = load_panel("net_assets"), load_panel("employees"), load_panel("cash")
    closed = V.closure_years(firms, [na, emp])
    gy = A.grant_years(firms)
    L = ["# Innovate UK study: why funded firms survive more (EXPLORATORY)", "",
         f"Not in the plan (v{lock['version']}); added after all results were seen. Survival as in RESULTS-v2 (open at the end of the "
         "grant year, both sides), on the same matched sets. Intervals: 500 bootstrap draws of matched sets.", ""]
    n_, ended = project_ends(firms)
    L += ["## When first projects end", "", f"Of {n_:,} funded firms, the share whose first-year projects had all ended by: "
          + "; ".join(f"t+{k} {v:.0f}%" for k, v in ended.items()) + ".", ""]
    for name, trend, P in (("net_assets", True, na), ("employees", False, emp)):
        I = R.run(name, firms, P, trend, internals=True)["_internals"]
        crn = lambda t: I["crns"][t]
        g = lambda t: int(I["g"][t])
        allm = set(I["matches"])
        head = "| Group | funded open | matched open | gap (95%) | matched sets |"
        L += [f"## Sample: {'established firms, design B (net assets)' if trend else 'employee sample, design A'}", ""]
        # 3. timing
        L += ["### Timing: the gap year by year", "", head, "|---|---|---|---|---|"]
        for k in (1, 2, 3, 4, 5):
            L.append(row(f"t+{k}", I, closed, allm, k)[1])
        # 1. dose
        d0 = {t: gy[crn(t)].get(g(t), 0.0) for t in allm}
        q1, q2 = V.terciles(list(d0.values()))
        L += ["", f"### Dose: by first-year grant (cuts £{q1:,.0f} and £{q2:,.0f}), survival at t+3", "", head, "|---|---|---|---|---|"]
        parts = {}
        for lab, lo_, hi_ in (("smallest third", -1, q1), ("middle third", q1, q2), ("largest third", q2, 1e18)):
            parts[lab], line = row(lab, I, closed, {t for t, v in d0.items() if lo_ < v <= hi_}, 3)
            L.append(line)
        lo, hi = boot_gap(parts["largest third"], parts["smallest third"])
        L.append(f"\nLargest minus smallest third: {100 * (parts['largest third'].mean() - parts['smallest third'].mean()):+.1f} pts "
                 f"({100 * lo:+.1f} to {100 * hi:+.1f}).")
        # 2. constraint
        neg = {t for t in allm if (crn(t), g(t) - 1) in na and na[(crn(t), g(t) - 1)][0] < 0}
        pos = {t for t in allm if (crn(t), g(t) - 1) in na and na[(crn(t), g(t) - 1)][0] >= 0}
        cv = {t: cash[(crn(t), g(t) - 1)][0] for t in allm if (crn(t), g(t) - 1) in cash}
        c1, c2 = V.terciles(list(cv.values()))
        L += ["", "### Financial position a year before the grant (t−1), survival at t+3", "", head, "|---|---|---|---|---|"]
        dn, ln = row("negative net assets at t−1", I, closed, neg, 3)
        dp, lp = row("positive net assets at t−1", I, closed, pos, 3)
        L += [ln, lp]
        lo, hi = boot_gap(dn, dp)
        L.append(f"| negative minus positive | | | {100 * (dn.mean() - dp.mean()):+.1f} pts ({100 * lo:+.1f} to {100 * hi:+.1f}) | |")
        dl, ll = row(f"cash at t−1 in the lowest third (≤ £{c1:,.0f})", I, closed, {t for t, v in cv.items() if v <= c1}, 3)
        dh, lh = row(f"cash at t−1 in the highest third (> £{c2:,.0f})", I, closed, {t for t, v in cv.items() if v > c2}, 3)
        L += [ll, lh]
        lo, hi = boot_gap(dl, dh)
        L += [f"| lowest minus highest cash third | | | {100 * (dl.mean() - dh.mean()):+.1f} pts ({100 * lo:+.1f} to {100 * hi:+.1f}) | |", ""]
        print("\n".join(L[-30:]), flush=True)
    (ROOT / "RESULTS-mechanism.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
