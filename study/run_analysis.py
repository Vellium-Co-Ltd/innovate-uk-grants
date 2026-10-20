"""The Innovate UK study's outcome analysis, exactly as PROTOCOL.md v1.0 §4–4b fixes it. Refuses to run if PROTOCOL.md no
longer matches the fingerprint in data/study/PROTOCOL-LOCK.json.

Per outcome (net assets, employees) and per population (established = trend-adjusted primary; plain matched), for each grant
cohort: eligible funded and never-funded firms → strata (cohort x SIC-2, thin sectors to their SIC section) → nearest-neighbour
propensity matching on the cohort's own pre-years (asinh / log scale) + firm age → balance check (caliper 0.2, tightened to
0.1 where any |SMD| > 0.1) → difference-in-differences on winsorised levels (primary) and the transformed scale (secondary),
firm-level bootstrap. Writes data/study/RESULTS-primary.md + results-primary.json.

    .venv/bin/python study/run_analysis.py
"""
import collections
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import estimate as E  # noqa: E402
from analysis_data import ROOT, load_firms, load_panel  # noqa: E402

HERE = Path(__file__).resolve().parent
YEARS = list(range(2008, 2027))
EVENTS = list(range(-6, 6))
HEADLINE = 3
MIN_POOL = 25
SECTION = [(3, "A"), (9, "B"), (33, "C"), (35, "D"), (39, "E"), (43, "F"), (47, "G"), (53, "H"), (56, "I"), (63, "J"),
           (66, "K"), (68, "L"), (75, "M"), (82, "N"), (84, "O"), (85, "P"), (88, "Q"), (93, "R"), (96, "S"), (98, "T"),
           (99, "U")]
SCALE = {"net_assets": np.arcsinh, "employees": np.log1p, "cash": np.arcsinh, "negative_net_assets": lambda y: y,
         "retained_earnings": np.arcsinh, "capital_in": np.arcsinh,
         "total_assets_less_current_liabilities": np.arcsinh, "fixed_assets": np.arcsinh, "turnover": np.arcsinh}
# Every outcome's scale lives here, nowhere else (L82: a check refuses a script that sets its own)
SIGNED = {"net_assets", "retained_earnings", "capital_in", "total_assets_less_current_liabilities"}   # outcomes that can be negative: never clipped at zero


def review_gaps():
    """Floor items and lessons (study/guards.py) with no verdict in the plan review."""
    import guards
    return guards.review_missing(HERE / "PROTOCOL-REVIEW.md")


def check_lock():
    """This study's plan lock, through the shared check every study uses (study/guards.py)."""
    import guards
    return guards.check_study_lock(HERE, ROOT)


def section(sic2):
    n = int(sic2)
    return next(s for top, s in SECTION if n <= top)


def winsorise(Y):
    W = Y.copy()
    for j in range(Y.shape[1]):
        col = Y[:, j]
        if np.isfinite(col).sum() > 100:
            lo, hi = np.nanpercentile(col, [1, 99])
            W[:, j] = np.clip(col, lo, hi)
    return W


def eligible(Y, yi, gg, trend):
    """Base year t-1 present; >= 2 of t-3..t-1; if trend, >= 2 of t-6..t-4 as well."""
    def n_have(ys):
        cols = [yi[y] for y in ys if y in yi]
        return np.isfinite(Y[:, cols]).sum(1) if cols else np.zeros(len(Y), int)
    ok = np.isfinite(Y[:, yi[gg - 1]]) & (n_have(range(gg - 3, gg)) >= 2)
    if trend:
        ok &= n_have(range(gg - 6, gg - 3)) >= 2
    return ok


def run(name, firms, panel, trend, k=5, shift=0, keep=None, drop_fallback=False, reps=500, diag=False, later_winners=None,
        outcome_hook=None, internals=False):
    """Robustness options (PROTOCOL §5): k controls; shift = placebo grant date moved `shift` years earlier;
    keep = the funded firms allowed in; drop_fallback = leave out firms matched at SIC-section level;
    later_winners = L: controls are firms whose FIRST grant came L or more years after the cohort (they also applied and
    won), instead of never-funded firms — added after results were seen (PROTOCOL §8 v1.1);
    outcome_hook(Y, crns, years) -> Y used for OUTCOMES only (matching keeps the filed values), e.g. closed firms at zero
    (PROTOCOL v2.0 §5.7); internals = return the matched sets and arrays for the v2.0 analyses."""
    crns = [c for c, f in firms.items() if f["sic2"].isdigit() and f["inc_year"] > 0
            and (f["g"] == 0 or keep is None or c in keep)]
    yi = {y: j for j, y in enumerate(YEARS)}
    Y = np.full((len(crns), len(YEARS)), np.nan)
    for i, c in enumerate(crns):
        for y in YEARS:
            v = panel.get((c, y))
            if v is not None:
                Y[i, yi[y]] = v[0]
    g = np.array([firms[c]["g"] - shift if firms[c]["g"] else 0 for c in crns])
    sic2 = np.array([firms[c]["sic2"] for c in crns])
    inc = np.array([firms[c]["inc_year"] for c in crns])
    award = np.array([firms[c]["award"] for c in crns])
    Ym = SCALE[name](Y if name in SIGNED else np.clip(Y, 0, None))
    Yw = winsorise(Y)
    matches, per_cohort = {}, {}
    for gg in sorted(set(g[g > 0].tolist())):
        if gg - 1 not in yi:
            continue
        ok = eligible(Y, yi, gg, trend)
        ctrl = (g == 0) if later_winners is None else (g >= gg + later_winners)
        sub = np.where(ok & ((g == gg) | ctrl))[0]
        if not ctrl[sub].any():
            continue
        if not (g[sub] == gg).any():
            continue
        n_pool = collections.Counter(sic2[sub][g[sub] != gg].tolist())
        strat = np.array([s if n_pool[s] >= MIN_POOL else section(s) for s in sic2[sub]])
        X = E.cohort_covariates(Ym[sub], YEARS, gg, extra=(gg - inc[sub]).astype(float), pre=3)
        sub_g = np.where(g[sub] == gg, gg, 0)
        used_cal, m = 0.2, E.match(sub_g, strat, X, k=k, caliper_sd=0.2)
        smd = E.balance(X, m) if m else np.array([np.nan])
        smd02 = float(np.nanmax(np.abs(smd)))
        smd01 = None
        if smd02 > 0.1:
            m01 = E.match(sub_g, strat, X, k=k, caliper_sd=0.1)
            if m01:
                smd01 = float(np.nanmax(np.abs(E.balance(X, m01))))
                used_cal, m = 0.1, m01
        gm = {int(sub[t]): sub[c].tolist() for t, c in m.items() if not (drop_fallback and strat[t] != sic2[sub][t])}
        matches.update(gm)
        t_all = int((g[sub] == gg).sum())
        per_cohort[gg] = dict(eligible_funded=t_all, matched=len(gm), pool_eligible=int((g[sub] != gg).sum()),
                              section_fallback=int(sum(1 for t in m if strat[t] != sic2[sub][t])),
                              max_smd_cal02=smd02, max_smd_cal01=smd01, caliper_used=used_cal,
                              median_award=float(np.median(award[list(gm)])) if gm else None)
    if outcome_hook is not None:
        Yo = outcome_hook(Y, crns, YEARS)
        Ym = SCALE[name](Yo if name in SIGNED else np.clip(Yo, 0, None))
        Yw = winsorise(Yo)
    kw = dict(detrend_pre=3, trend_gap=3) if trend else {}
    out = {"per_cohort": per_cohort, "funded_matched": len(matches),
           "median_award": float(np.median(award[list(matches)])) if matches else None}
    for label, Z in (("levels_winsorised", Yw), ("transformed", Ym)):
        att = E.att_by_event(Z, YEARS, g, matches, EVENTS, **kw)
        ci = E.bootstrap(Z, YEARS, g, matches, EVENTS, reps=reps, seed=1, **kw)
        out[label] = {e: dict(att=att[e][0], n=att[e][1], lo=ci[e][0], hi=ci[e][1]) for e in EVENTS}
        by_c = {}
        for gg in per_cohort:
            sub_m = {t: c for t, c in matches.items() if g[t] == gg}
            if sub_m:
                a = E.att_by_event(Z, YEARS, g, sub_m, [HEADLINE], **kw)[HEADLINE]
                by_c[gg] = dict(att=a[0], n=a[1])
        out[label + "_t3_by_cohort"] = by_c
        if diag:  # spread of the firm-level differences at the headline year (median, share above zero)
            _, ev, D = E.firm_diffs(Z, YEARS, g, matches, [HEADLINE], **kw)
            d = D[:, 0][np.isfinite(D[:, 0])]
            out[label + "_t3_spread"] = dict(median=float(np.median(d)) if len(d) else None,
                                               share_above_zero=float((d > 0).mean()) if len(d) else None, n=int(len(d)))
    if internals:
        out["_internals"] = dict(crns=crns, g=g, matches=matches, Yw=Yw, Ym=Ym, kw=kw, award=award)
    return out


def fmt(v, name, label):
    if v is None or not np.isfinite(v):
        return "–"
    if label == "transformed":
        return f"{v:+.3f}"
    return f"£{v:+,.0f}" if name == "net_assets" else f"{v:+.2f}"


def report(lock, results):
    L = ["# Innovate UK study — primary outcome results (INTERNAL until published)", "",
         f"Protocol v{lock['version']} locked {lock['locked_utc']} (SHA-256 {lock['sha256'][:16]}…). Every number below "
         "was produced by `study/run_analysis.py` after the lock. Nothing here is claimed in public until the write-up is published.", ""]
    for (name, pop), r in results.items():
        title = {"trend": "Established firms — trend-adjusted" + (" (primary design)" if name == "net_assets" else
                           " (few firms have six pre-years of employees; shown for completeness)"),
                 "plain": "Plain matched comparison" + (" (primary for employees; bias read from the placebo years)"
                                                        if name == "employees" else "")}[pop]
        L += [f"## {name.replace('_', ' ')} — {title}", "",
              f"Funded firms matched: **{r['funded_matched']:,}**; median award of those firms: "
              f"£{(r['median_award'] or 0):,.0f}.", ""]
        L += ["| Years from grant | effect (winsorised levels) | 95% interval | firms | effect (" +
              ("asinh" if name == "net_assets" else "log 1+x") + ") | 95% interval |", "|---|---|---|---|---|---|"]
        for e in EVENTS:
            a, b = r["levels_winsorised"][e], r["transformed"][e]
            if e == -1:
                L.append("| −1 (base) | 0 | – | – | 0 | – |")
                continue
            mark = " **(headline)**" if e == HEADLINE else (" (placebo, before matching)" if e <= -4 and pop == "trend" else "")
            L.append(f"| {e}{mark} | {fmt(a['att'], name, 'l')} | {fmt(a['lo'], name, 'l')} to {fmt(a['hi'], name, 'l')} | "
                     f"{a['n']:,} | {fmt(b['att'], name, 'transformed')} | {fmt(b['lo'], name, 'transformed')} to "
                     f"{fmt(b['hi'], name, 'transformed')} |")
        L += ["", "| Cohort | eligible funded | matched | pool eligible | sector-section fallback | max |SMD| cal 0.2 | "
              "cal 0.1 | caliper used | t+3 effect (levels) | firms at t+3 |", "|---|---|---|---|---|---|---|---|---|---|"]
        for gg, c in sorted(r["per_cohort"].items()):
            t3 = r["levels_winsorised_t3_by_cohort"].get(gg, {})
            L.append(f"| {gg} | {c['eligible_funded']:,} | {c['matched']:,} | {c['pool_eligible']:,} | {c['section_fallback']} | "
                     f"{c['max_smd_cal02']:.3f} | {'' if c['max_smd_cal01'] is None else f'{c['max_smd_cal01']:.3f}'} | "
                     f"{c['caliper_used']} | {fmt(t3.get('att'), name, 'l')} | {t3.get('n', 0):,} |")
        L.append("")
    (ROOT / "RESULTS-primary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


def main():
    lock = check_lock()
    firms = load_firms()
    results = {}
    for name in ("net_assets", "employees"):
        panel = load_panel(name)
        for pop, trend in (("trend", True), ("plain", False)):
            results[(name, pop)] = run(name, firms, panel, trend)
        del panel
    (ROOT / "results-primary.json").write_text(json.dumps({f"{k[0]}|{k[1]}": v for k, v in results.items()}, default=str, indent=1))
    report(lock, results)


if __name__ == "__main__":
    main()
