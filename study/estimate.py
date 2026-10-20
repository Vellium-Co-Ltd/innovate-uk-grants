"""The study's estimator: propensity-score matching within exact strata, then staggered difference-in-differences
(Callaway–Sant'Anna style group-time effects against matched never-funded firms), with a firm-level bootstrap.

Pure numpy, so it runs on a small machine. Proven on simulated data with a
known answer before it ever touches real outcomes (test_estimator.py → data/study/SIM-CHECK.md).

Data shape (all numpy arrays, one row per firm):
  firm ids, cohort g (first grant year; 0 = never funded), stratum (e.g. sector x cohort), covariates X (pre-period),
  outcome panel Y[firm, year_index] with NaN where not filed.
"""
import numpy as np


def logit_fit(X, d, iters=50):
    """Logistic regression by IRLS (with a tiny ridge for stability). Returns coefficients incl. intercept."""
    Xc = np.column_stack([np.ones(len(X)), X])
    b = np.zeros(Xc.shape[1])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-np.clip(Xc @ b, -30, 30)))
        W = p * (1 - p)
        H = Xc.T @ (Xc * W[:, None]) + 1e-6 * np.eye(Xc.shape[1])
        step = np.linalg.solve(H, Xc.T @ (d - p))
        b += step
        if np.abs(step).max() < 1e-8:
            break
    return b


def match(g, stratum, X, k=5, caliper_sd=0.2):
    """For each funded firm, up to k never-funded firms in the same stratum with the nearest propensity logit within
    caliper_sd standard deviations. Returns {treated_index: [control_indices]} (with replacement)."""
    treated = np.where(g > 0)[0]
    out = {}
    for s in np.unique(stratum[treated]):
        t_idx = treated[stratum[treated] == s]
        c_idx = np.where((g == 0) & (stratum == s))[0]
        if len(c_idx) == 0:
            continue
        idx = np.concatenate([t_idx, c_idx])
        d = np.r_[np.ones(len(t_idx)), np.zeros(len(c_idx))]
        b = logit_fit(X[idx], d)
        lp = np.column_stack([np.ones(len(idx)), X[idx]]) @ b
        cal = caliper_sd * lp.std() if lp.std() > 0 else np.inf
        lt, lc = lp[:len(t_idx)], lp[len(t_idx):]
        for i, ti in enumerate(t_idx):
            dist = np.abs(lc - lt[i])
            order = np.argsort(dist)[:k]
            keep = order[dist[order] <= cal]
            if len(keep):
                out[int(ti)] = c_idx[keep].tolist()
    return out


def cohort_covariates(Y, years, gg, extra=None, pre=3):
    """Covariates for matching cohort gg: each firm's outcome in the `pre` calendar years before gg (levels) and its
    pre-period slope, plus any extra columns. Missing values filled with the firm's own pre-period mean, then the column mean."""
    cols = [years.index(y) for y in range(gg - pre, gg) if y in years]
    P = Y[:, cols]
    with np.errstate(all="ignore"):
        rowmean = np.nanmean(P, axis=1, keepdims=True) if P.size else P
    P = np.where(np.isnan(P), rowmean, P)
    P = np.where(np.isnan(P), np.nanmean(P, axis=0), P)
    t = np.arange(P.shape[1]) - (P.shape[1] - 1) / 2
    slope = (P * t).sum(1) / (t ** 2).sum() if P.shape[1] > 1 else np.zeros(len(P))
    X = np.column_stack([P, slope] + ([extra] if extra is not None else []))
    return X


def match_by_cohort(Y, years, g, stratum, extra=None, k=5, caliper_sd=0.2, pre=3):
    """Match each cohort separately on its own pre-grant years; controls are never-funded firms only."""
    out = {}
    for gg in np.unique(g[g > 0]):
        X = cohort_covariates(Y, years, int(gg), extra, pre)
        sub_g = np.where(g == gg, gg, np.where(g == 0, 0, -1))
        keep = sub_g >= 0
        idx = np.where(keep)[0]
        m = match(sub_g[keep], stratum[keep], X[keep], k, caliper_sd)
        out.update({int(idx[t]): idx[c].tolist() for t, c in m.items()})
    return out


def balance(X, matches):
    """Standardised mean differences of covariates, funded vs matched (control weights 1/k_i)."""
    t = np.array(list(matches))
    w_c = np.concatenate([np.full(len(c), 1 / len(c)) for c in matches.values()])
    c = np.concatenate(list(matches.values()))
    mt, mc = X[t].mean(0), (X[c] * w_c[:, None]).sum(0) / w_c.sum()
    sd = np.sqrt((X[t].var(0) + X[c].var(0)) / 2)
    return (mt - mc) / np.where(sd > 0, sd, 1)


def firm_diffs(Y, years, g, matches, events=range(-3, 6), detrend_pre=0, trend_gap=0):
    """Matrix D[funded firm, event]: the firm's change in Y from its base year (g-1) to g+e, minus the same change averaged
    over its matched controls. NaN where either side lacks data. e = -1 is the base year itself (always 0, omitted)."""
    yi = {y: j for j, y in enumerate(years)}
    events = list(events)
    keys = list(matches)
    D = np.full((len(keys), len(events)), np.nan)
    for r, i in enumerate(keys):
        base = g[i] - 1
        if base not in yi:
            continue
        cs = np.array(matches[i])
        for c, e in enumerate(events):
            tgt = g[i] + e
            if e == -1 or tgt not in yi:
                continue
            dt_ = Y[i, yi[tgt]] - Y[i, yi[base]]
            dc = Y[cs, yi[tgt]] - Y[cs, yi[base]]
            if detrend_pre:  # subtract each firm's own pre-grant slope, taken from years BEFORE the matching window
                tb = base - trend_gap  # trend_gap = matching window length, so the trend never reuses matched years
                dt_ -= _slope(Y[i], yi, tb, detrend_pre) * (tgt - base)
                dc = dc - np.array([_slope(Y[cc], yi, tb, detrend_pre) for cc in cs]) * (tgt - base)
            if not np.isnan(dt_) and not np.all(np.isnan(dc)):
                D[r, c] = dt_ - np.nanmean(dc)
    return keys, events, D


def _slope(row, yi, base, n):
    """OLS slope of a firm's outcome over the n years ending at base (needs at least 2 points)."""
    ys = [y for y in range(base - n + 1, base + 1) if y in yi and not np.isnan(row[yi[y]])]
    if len(ys) < 2:
        return np.nan
    t = np.array(ys, float); v = np.array([row[yi[y]] for y in ys])
    t -= t.mean()
    return float((t * (v - v.mean())).sum() / (t ** 2).sum())


def att_by_event(Y, years, g, matches, events=range(-3, 6), detrend_pre=0, trend_gap=0):
    """{event: (ATT, number of funded firms contributing)}."""
    _, events, D = firm_diffs(Y, years, g, matches, events, detrend_pre, trend_gap)
    return {e: (float(np.nanmean(D[:, c])) if np.isfinite(D[:, c]).any() else np.nan, int(np.isfinite(D[:, c]).sum()))
            for c, e in enumerate(events)}


def bootstrap(Y, years, g, matches, events=range(-3, 6), reps=500, seed=1, detrend_pre=0, trend_gap=0):
    """Firm-level bootstrap over funded firms (each carries its matched controls): 95% percentile intervals."""
    rng = np.random.default_rng(seed)
    _, events, D = firm_diffs(Y, years, g, matches, events, detrend_pre, trend_gap)
    n = D.shape[0]
    draws = np.array([np.nanmean(D[rng.integers(0, n, n)], axis=0) for _ in range(reps)])
    return {e: (float(np.nanpercentile(draws[:, c], 2.5)), float(np.nanpercentile(draws[:, c], 97.5)))
            for c, e in enumerate(events)}
