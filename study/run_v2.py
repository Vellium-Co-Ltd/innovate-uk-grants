"""PROTOCOL.md v2.0 analyses beyond v1.0 (each marked [after results] in the plan). Same lock check as run_analysis.

  §5.7  survival first (funded vs matched, open at t+3 / t+5) + two bounds on every growth headline
        (closed firms at zero from their closure year; trimming bounds that drop the excess survivors)
  §5.6  anticipation variant (base year t-3, two years of run-up allowed)
  §5.8  dose-response by award tercile and by award per pre-grant employee
  §5.9  Smart grants public-data replication (first grant in a Smart competition, cohorts 2019-2024)
  §5.11 minimum detectable effect (2.8 x bootstrap SE) + E-value for every headline
  §5.2  young firms (growth from first filing, matched on incorporation year, first-filing year, sector, region, size)
  §7    value for money ranges

Writes data/study/RESULTS-v2.md and results-v2.json.   .venv/bin/python study/run_v2.py
"""
import collections
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import estimate as E  # noqa: E402
import run_analysis as R  # noqa: E402
from analysis_data import ROOT, load_firms, load_panel  # noqa: E402

DESIGN = {"net_assets": True, "employees": False}       # the v1.0 primaries: B for net assets, A for employees
LAST_FULL_YEAR = 2025                                    # closures and accounts complete to here (data to Sep 2026)
REPS = 500


# ---------- closure dating (PROTOCOL §4) ----------
def closure_years(firms, panels):
    last = collections.defaultdict(int)
    for P in panels:
        for (c, y) in P:
            last[c] = max(last[c], y)
    out = {}
    for c, f in firms.items():
        if f["ceased_year"]:
            out[c] = f["ceased_year"]
        elif f["closed"]:
            out[c] = (last[c] + 1) if last[c] else None
    return out


def zero_after_closure(closed):
    def hook(Y, crns, years):
        Z = Y.copy()
        for i, c in enumerate(crns):
            cy = closed.get(c)
            if cy:
                for j, y in enumerate(years):
                    if y >= cy and np.isnan(Z[i, j]):
                        Z[i, j] = 0.0
        return Z
    return hook


# ---------- helpers ----------
def mde(lo, hi):
    return 2.8 * (hi - lo) / 3.92


def e_value(att, lo, hi, sd):
    """VanderWeele–Ding approximation for a difference in means: RR ~ exp(0.91 d), d = effect / SD of the outcome."""
    def ev(x):
        rr = np.exp(0.91 * abs(x) / sd)
        return float(rr + np.sqrt(rr * (rr - 1)))
    near = 0.0 if lo <= 0 <= hi else (lo if att > 0 else hi)
    return ev(att), (1.0 if near == 0.0 else ev(near))


def boot_mean(d, reps=REPS, seed=1):
    d = d[np.isfinite(d)]
    if len(d) < 2:
        return (np.nan, np.nan)
    rng = np.random.default_rng(seed)
    draws = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(reps)]
    return float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def survival(I, closed, ks=(3, 5), from_open_at_t0=True):
    """Share open at t+k, funded minus matched. from_open_at_t0 (PROTOCOL v2.1): only firms still open at the end of the grant
    year count, on both sides — a funded firm must exist to receive its grant, a control need not (immortal-time bias)."""
    g, crns, M = I["g"], I["crns"], I["matches"]
    out = {}
    for k in ks:
        diffs, tr, co = [], [], []
        for t, cs in M.items():
            if g[t] + k > LAST_FULL_YEAR:
                continue
            def open_(i, yr):
                cy = closed.get(crns[i])
                return 0.0 if (cy and cy <= yr) else 1.0
            if from_open_at_t0:
                cs = [c for c in cs if open_(c, g[t])]
                if not cs or not open_(t, g[t]):
                    continue
            ot, oc = open_(t, g[t] + k), np.mean([open_(c, g[t] + k) for c in cs])
            diffs.append(ot - oc); tr.append(ot); co.append(oc)
        d = np.array(diffs)
        lo, hi = boot_mean(d)
        out[k] = dict(effect_pp=100 * d.mean() if len(d) else np.nan, lo=100 * lo, hi=100 * hi, n=len(d),
                      funded_open=100 * np.mean(tr) if tr else np.nan, matched_open=100 * np.mean(co) if co else np.nan)
    return out


def lee_bounds(I, e=R.HEADLINE):
    """Trimming bounds at t+e on the plain change from t-1 (Lee 2009, matched sets pooled, controls weighted 1/k)."""
    g, M, Z = I["g"], I["matches"], I["Yw"]
    yi = {y: j for j, y in enumerate(R.YEARS)}
    dt_, obs_t, dc, wc, obs_c = [], [], [], [], []
    for t, cs in M.items():
        tgt, base = g[t] + e, g[t] - 1
        if tgt > LAST_FULL_YEAR or tgt not in yi:
            continue
        v = Z[t, yi[tgt]] - Z[t, yi[base]]
        obs_t.append(np.isfinite(v))
        if np.isfinite(v):
            dt_.append(v)
        for c in cs:
            u = Z[c, yi[tgt]] - Z[c, yi[base]]
            obs_c.append((np.isfinite(u), 1 / len(cs)))
            if np.isfinite(u):
                dc.append(u); wc.append(1 / len(cs))
    p_t = np.mean(obs_t) if obs_t else np.nan
    p_c = sum(w for o, w in obs_c if o) / sum(w for _, w in obs_c) if obs_c else np.nan
    dt_, dc, wc = np.array(dt_), np.array(dc), np.array(wc)
    mc = (dc * wc).sum() / wc.sum()
    mt = dt_.mean()
    if p_t >= p_c:   # funded firms are seen more often (they survive more): trim the funded side
        q = (p_t - p_c) / p_t
        s = np.sort(dt_); n = int(round(q * len(s)))
        lo, hi = s[:len(s) - n].mean() - mc, s[n:].mean() - mc
    else:            # trim the control side (weighted)
        q = (p_c - p_t) / p_c
        o = np.argsort(dc); cw = np.cumsum(wc[o]) / wc.sum()
        keep_low, keep_high = o[cw <= 1 - q], o[cw > q]
        lo = mt - (dc[keep_high] * wc[keep_high]).sum() / wc[keep_high].sum()
        hi = mt - (dc[keep_low] * wc[keep_low]).sum() / wc[keep_low].sum()
    return dict(seen_funded=100 * p_t, seen_matched=100 * p_c, trimmed_share=100 * q, lower=float(lo), upper=float(hi))


def sub_effect(I, keep_t, e=R.HEADLINE):
    sub = {t: c for t, c in I["matches"].items() if t in keep_t}
    if not sub:
        return dict(att=np.nan, lo=np.nan, hi=np.nan, n=0)
    a = E.att_by_event(I["Yw"], R.YEARS, I["g"], sub, [e], **I["kw"])[e]
    ci = E.bootstrap(I["Yw"], R.YEARS, I["g"], sub, [e], reps=REPS, seed=1, **I["kw"])[e]
    return dict(att=a[0], n=a[1], lo=ci[0], hi=ci[1])


def terciles(values):
    v = np.array(values, float)
    q1, q2 = np.nanpercentile(v, [100 / 3, 200 / 3])
    return q1, q2


# ---------- Smart ----------
def excel_year(v):
    try:
        return (dt.date(1899, 12, 30) + dt.timedelta(days=int(float(v)))).year, int(float(v))
    except (TypeError, ValueError):
        return None, None


def first_project_is_smart():
    first = {}
    for line in open(ROOT / "grants.jsonl"):
        r = json.loads(line)
        if float(r.get("Award Offered (£)") or 0) <= 0 or (r.get("Participant Withdrawn From Project") or "").lower().startswith("withdrawn"):
            continue
        y, d = excel_year(r.get("Project Start Date"))
        if d is None:
            continue
        smart = "smart" in (r.get("Competition Title") or "").lower()
        if r["CRN"] not in first or d < first[r["CRN"]][0]:
            first[r["CRN"]] = (d, smart)
    return {c for c, (_, s) in first.items() if s}


# ---------- young firms (PROTOCOL §5.2 population 3) ----------
def region_map():
    """Postcode area -> region, by majority in the grants file (which carries both); used for every firm alike."""
    votes = collections.defaultdict(collections.Counter)
    for line in open(ROOT / "grants.jsonl"):
        r = json.loads(line)
        pc, reg = (r.get("Postcode") or "").strip(), (r.get("Address Region") or "").strip()
        area = "".join(ch for ch in pc.split(" ")[0] if ch.isalpha())[:2]
        if area and reg:
            votes[area][reg] += 1
    return {a: v.most_common(1)[0][0] for a, v in votes.items()}


def young_firms(name, firms, panel, closed, established, regions):
    yrs = R.YEARS; yi = {y: j for j, y in enumerate(yrs)}
    first = {}
    for (c, y) in panel:
        first[c] = min(first.get(c, 9999), y)
    rows = []
    for c, f in firms.items():
        if not f["sic2"].isdigit() or not f["inc_year"] or c not in first:
            continue
        if f["g"] > 0 and (c in established or first[c] > f["g"] + 1 or f["g"] + R.HEADLINE > LAST_FULL_YEAR):
            continue   # established firms are in the main designs; first filing must come by t0+1; t+3 must be observable
        rows.append(c)
    region_of = lambda c: regions.get(firms[c]["postcode_area"], "")
    reg_list = sorted({region_of(c) for c in rows} - {""})
    strat = np.array([f"{first[c]}|{firms[c]['inc_year']}|{R.section(firms[c]['sic2'])}" for c in rows])
    g = np.array([firms[c]["g"] for c in rows])
    yb = np.array([panel[(c, first[c])][0] for c in rows])
    scale = R.SCALE[name]                 # the shared rule; a name switch here sent signed outcomes to log1p (L82)
    X = np.column_stack([scale(yb if name in R.SIGNED else np.clip(yb, 0, None))] +
                        [np.array([region_of(c) == r for c in rows], float) for r in reg_list[:-1]])
    m = E.match(np.where(g > 0, 1, 0), strat, X, k=5, caliper_sd=0.2)
    smd = float(np.nanmax(np.abs(E.balance(X, m)))) if m else np.nan
    hook = zero_after_closure(closed)
    out = {"funded_young_eligible": int((g > 0).sum()), "matched": len(m), "max_smd": smd}
    for label, zero in (("as filed", False), ("closed firms at zero", True)):
        diffs, surv = [], {3: [], 5: []}
        for t, cs in m.items():
            ct = rows[t]; tgt = firms[ct]["g"] + R.HEADLINE
            def val(i, y):
                v = panel.get((rows[i], y))
                if v is not None:
                    return v[0]
                cy = closed.get(rows[i])
                return 0.0 if (zero and cy and y >= cy) else np.nan
            d_t = val(t, tgt) - yb[t]
            d_c = np.array([val(c, tgt) - yb[c] for c in cs])
            if np.isfinite(d_t) and np.isfinite(d_c).any():
                diffs.append(d_t - np.nanmean(d_c))
            if not zero:
                for k in (3, 5):
                    if firms[ct]["g"] + k <= LAST_FULL_YEAR:
                        op = lambda i, yr: 0.0 if (closed.get(rows[i]) and closed[rows[i]] <= yr) else 1.0
                        cs0 = [c for c in cs if op(c, firms[ct]["g"])]   # open at end of t0, both sides (v2.1)
                        if cs0 and op(t, firms[ct]["g"]):
                            surv[k].append(op(t, firms[ct]["g"] + k) - np.mean([op(c, firms[ct]["g"] + k) for c in cs0]))
        d = np.array(diffs)
        lo, hi = boot_mean(d)
        out[label] = dict(att=float(np.mean(d)) if len(d) else np.nan, lo=lo, hi=hi, n=len(d))
        if not zero:
            for k in (3, 5):
                s = np.array(surv[k]); a, b = boot_mean(s)
                out[f"survival_t{k}"] = dict(effect_pp=100 * s.mean() if len(s) else np.nan, lo=100 * a, hi=100 * b, n=len(s))
    return out


# ---------- report ----------
def f(v, name, pct=False):
    if v is None or not np.isfinite(v):
        return "–"
    if pct:
        return f"{v:+.1f} pts"
    return f"£{v:+,.0f}" if name == "net_assets" else f"{v:+.2f}"


def main():
    lock = R.check_lock()
    firms = load_firms()
    panels = {n: load_panel(n) for n in ("net_assets", "employees")}
    closed = closure_years(firms, panels.values())
    smart = first_project_is_smart()
    regions = region_map()
    res = {}
    L = ["# Innovate UK study — v2.0 analyses (INTERNAL until published)", "",
         f"Plan v{lock['version']} (locked {lock['locked_utc']}). Each section is marked [after results] in the plan. Headline t+{R.HEADLINE}; "
         f"closures and outcomes counted to {LAST_FULL_YEAR}.", ""]
    for name, trend in DESIGN.items():
        P = panels[name]
        design = "trend-adjusted (B)" if trend else "plain matched (A)"
        main_ = R.run(name, firms, P, trend, internals=True, reps=REPS)
        I = main_["_internals"]
        established = {I["crns"][t] for t in I["matches"]}
        h = main_["levels_winsorised"][R.HEADLINE]
        vals = []   # SD of the outcome at each funded firm's own t+3, funded and matched alike
        for t, cs in I["matches"].items():
            y = int(I["g"][t]) + R.HEADLINE
            if y in R.YEARS:
                j = R.YEARS.index(y)
                vals += [I["Yw"][t, j]] + [I["Yw"][c, j] for c in cs]
        sd = float(np.nanstd(np.array(vals)))
        ev = e_value(h["att"], h["lo"], h["hi"], sd)
        r = {"headline": h, "mde": mde(h["lo"], h["hi"]), "e_value": ev, "sd_outcome": sd}
        r["survival"] = survival(I, closed)
        r["survival_unconditional"] = survival(I, closed, from_open_at_t0=False)
        r["lee"] = lee_bounds(I)
        zero = R.run(name, firms, P, trend, outcome_hook=zero_after_closure(closed), reps=REPS)
        r["zero_after_closure"] = zero["levels_winsorised"][R.HEADLINE]
        ant = R.run(name, firms, P, trend, shift=2, reps=REPS)
        r["anticipation"] = ant["levels_winsorised"][R.HEADLINE + 2]
        r["anticipation_placebo_t_minus1"] = ant["levels_winsorised"][1]
        # dose-response
        awards = {t: I["award"][t] for t in I["matches"]}
        q1, q2 = terciles(list(awards.values()))
        r["dose_award"] = {lab: sub_effect(I, {t for t, a in awards.items() if lo_ < a <= hi_})
                           for lab, lo_, hi_ in (("lowest third", -1, q1), ("middle third", q1, q2), ("highest third", q2, 1e18))}
        r["dose_award_cuts"] = (q1, q2)
        antI = R.run(name, firms, P, trend, shift=2, reps=REPS, internals=True)["_internals"]
        aw2 = {t: antI["award"][t] for t in antI["matches"]}
        r["dose_award_placebo"] = {lab: sub_effect(antI, {t for t, a in aw2.items() if lo_ < a <= hi_}, e=1)
                                   for lab, lo_, hi_ in (("lowest third", -1, q1), ("middle third", q1, q2), ("highest third", q2, 1e18))}
        emp = panels["employees"]
        per = {}
        for t in I["matches"]:
            v = emp.get((I["crns"][t], int(I["g"][t]) - 1))
            if v is not None and v[0] >= 1:
                per[t] = I["award"][t] / v[0]
        if len(per) > 30:
            p1, p2 = terciles(list(per.values()))
            r["dose_per_employee"] = {lab: sub_effect(I, {t for t, a in per.items() if lo_ < a <= hi_})
                                      for lab, lo_, hi_ in (("lowest third", -1, p1), ("middle third", p1, p2), ("highest third", p2, 1e18))}
            r["dose_per_employee_cuts"] = (p1, p2)
        # Smart replication
        keep = {c for c in smart if 2019 <= firms.get(c, {}).get("g", 0) <= 2024}
        sm = R.run(name, firms, P, trend, keep=keep, reps=REPS)
        sm_pl = R.run(name, firms, P, trend, keep=keep, shift=2, reps=REPS)
        r["smart"] = dict(matched=sm["funded_matched"], levels={e: sm["levels_winsorised"][e] for e in range(0, 4)},
                          transformed={e: sm["transformed"][e] for e in range(0, 4)},
                          placebo_t_minus1=sm_pl["levels_winsorised"][1], placebo_t_minus1_transformed=sm_pl["transformed"][1])
        # young firms
        r["young"] = young_firms(name, firms, P, closed, established, regions)
        # value for money (net assets only, PROTOCOL §7)
        if name == "net_assets":
            mean_award = float(np.mean([I["award"][t] for t in I["matches"]]))
            r["vfm"] = dict(mean_award=mean_award, per_pound=h["att"] / mean_award, lo=h["lo"] / mean_award, hi=h["hi"] / mean_award)
        res[name] = r
        print(name, "done", flush=True)
        # ----- write section -----
        L += [f"## {name.replace('_', ' ')} — {design}", "",
              f"**Headline t+3:** {f(h['att'], name)} (95% {f(h['lo'], name)} to {f(h['hi'], name)}; {h['n']:,} firms). "
              f"Minimum detectable effect {f(r['mde'], name)[1:] if name != 'net_assets' else '£' + format(r['mde'], ',.0f')}. "
              f"E-value {ev[0]:.2f} (interval limit {ev[1]:.2f}).", "",
              "**Survival (§5.7)** — share still open, funded minus matched:", "",
              "| | effect | 95% interval | funded open | matched open | firms |", "|---|---|---|---|---|---|"]
        for k, s in r["survival"].items():
            L.append(f"| t+{k} | {f(s['effect_pp'], name, True)} | {f(s['lo'], name, True)} to {f(s['hi'], name, True)} | "
                     f"{s['funded_open']:.1f}% | {s['matched_open']:.1f}% | {s['n']:,} |")
        L.append("")
        for k, s in r["survival_unconditional"].items():
            L.append(f"Without the open-at-t0 condition (v2.0 definition, biased toward funded firms): t+{k} {f(s['effect_pp'], name, True)}.")
        lb, z = r["lee"], r["zero_after_closure"]
        L += ["", f"**Bounds on the headline (§5.7):** closed firms at zero from closure: {f(z['att'], name)} "
                  f"({f(z['lo'], name)} to {f(z['hi'], name)}; {z['n']:,} firms). Trimming bounds (plain change from t−1; "
                  f"seen at t+3: funded {lb['seen_funded']:.1f}%, matched {lb['seen_matched']:.1f}%, trimmed {lb['trimmed_share']:.1f}%): "
                  f"{f(lb['lower'], name)} to {f(lb['upper'], name)}.", "",
              f"**Anticipation (§5.6, base t−3):** {f(r['anticipation']['att'], name)} ({f(r['anticipation']['lo'], name)} to "
              f"{f(r['anticipation']['hi'], name)}) — includes any pre-grant run-up, which was itself "
              f"{f(r['anticipation_placebo_t_minus1']['att'], name)} by t−1.", "",
              "**Grant size (§5.8)** — t+3 effect by tercile:", "", "| | by award | by award per pre-grant employee |", "|---|---|---|"]
        for lab in ("lowest third", "middle third", "highest third"):
            a = r["dose_award"][lab]; b = r.get("dose_per_employee", {}).get(lab, {})
            L.append(f"| {lab} | {f(a['att'], name)} ({f(a['lo'], name)} to {f(a['hi'], name)}; {a['n']}) | "
                     + (f"{f(b['att'], name)} ({f(b['lo'], name)} to {f(b['hi'], name)}; {b['n']})" if b else "–") + " |")
        c1, c2 = r["dose_award_cuts"]
        L += ["", "Placebo by award third (grant date −2, effect at real t−1; the same cuts): " + "; ".join(
            f"{lab} {f(v['att'], name)} ({f(v['lo'], name)} to {f(v['hi'], name)}; {v['n']})" for lab, v in r["dose_award_placebo"].items()) + "."]
        L += ["", f"Award cuts: £{c1:,.0f} and £{c2:,.0f}." +
              (f" Per-employee cuts: £{r['dose_per_employee_cuts'][0]:,.0f} and £{r['dose_per_employee_cuts'][1]:,.0f}." if "dose_per_employee_cuts" in r else ""), ""]
        sm_ = r["smart"]
        L += [f"**Smart replication (§5.9)** — {sm_['matched']:,} Smart firms matched (first grant in a Smart competition, cohorts 2019–2024):", "",
              "| years from grant | effect (levels) | 95% | firms | effect (" + ("asinh" if name == "net_assets" else "log 1+x") + ") | 95% |",
              "|---|---|---|---|---|---|"]
        for e in range(0, 4):
            a, b = sm_["levels"][e], sm_["transformed"][e]
            L.append(f"| {e} | {f(a['att'], name)} | {f(a['lo'], name)} to {f(a['hi'], name)} | {a['n']:,} | {b['att']:+.3f} | {b['lo']:+.3f} to {b['hi']:+.3f} |")
        p, pt = sm_["placebo_t_minus1"], sm_["placebo_t_minus1_transformed"]
        L += ["", f"Smart placebo (grant date −2, effect at real t−1): {f(p['att'], name)} ({f(p['lo'], name)} to {f(p['hi'], name)}); "
                  f"transformed {pt['att']:+.3f} ({pt['lo']:+.3f} to {pt['hi']:+.3f}).", ""]
        y = r["young"]
        L += [f"**Young firms (§5.2, weaker design)** — {y['matched']:,} of {y['funded_young_eligible']:,} matched (max |SMD| {y['max_smd']:.2f}); "
              f"change from first filing to t+3: as filed {f(y['as filed']['att'], name)} ({f(y['as filed']['lo'], name)} to {f(y['as filed']['hi'], name)}; "
              f"{y['as filed']['n']:,}); closed firms at zero {f(y['closed firms at zero']['att'], name)} "
              f"({f(y['closed firms at zero']['lo'], name)} to {f(y['closed firms at zero']['hi'], name)}). Survival t+3 "
              f"{f(y['survival_t3']['effect_pp'], name, True)} ({f(y['survival_t3']['lo'], name, True)} to {f(y['survival_t3']['hi'], name, True)}; "
              f"{y['survival_t3']['n']:,}); t+5 {f(y['survival_t5']['effect_pp'], name, True)} ({f(y['survival_t5']['lo'], name, True)} to "
              f"{f(y['survival_t5']['hi'], name, True)}; {y['survival_t5']['n']:,}).", ""]
        if "vfm" in r:
            v = r["vfm"]
            L += [f"**Value for money (§7):** net assets change per £1 of grant at t+3: £{v['per_pound']:.2f} (£{v['lo']:.2f} to £{v['hi']:.2f}); "
                  f"mean award £{v['mean_award']:,.0f}. The grant's own money passes into retained earnings, so a ratio near or below £1 is not growth.", ""]
        del main_, zero, ant, sm, sm_pl
    (ROOT / "results-v2.json").write_text(json.dumps(res, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o), indent=1))
    (ROOT / "RESULTS-v2.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
