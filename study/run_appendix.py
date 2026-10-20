"""Appendix analyses the plan (v2.2) lists but earlier runs did not produce, plus one definition corrected.

  §1   sector (SIC section) and region tables for the two primaries, each row with its placebo (descriptive, not tested one by one)
  §1 Q4 turnover: how many firms file it at all (coverage only, no estimate)
  §3   fixed assets (capacity link) and total assets less current liabilities (v1.3 appendix), design B with placebo
  §5.8 / §7 grant money counted in the outcome's own window: v2.0 summed every award a firm was ever offered in the file,
       including projects started after t+3 (and the larger awards growing firms win later). Here: the first year's awards (dose)
       and awards on projects started t0..t+3 for firms seen at t+3 (value for money). Both shown beside the v2.0 figures.
  descriptives: the funded population (counts and money only; no outcomes)

Writes data/study/RESULTS-appendix.md.   .venv/bin/python study/run_appendix.py
"""
import collections
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_analysis as R  # noqa: E402
import run_v2 as V  # noqa: E402
from analysis_data import ROOT, load_firms, load_panel  # noqa: E402

SECTION_NAME = {"A": "Agriculture, forestry, fishing", "B": "Mining", "C": "Manufacturing", "D": "Energy supply",
                "E": "Water and waste", "F": "Construction", "G": "Wholesale and retail", "H": "Transport", "I": "Hospitality",
                "J": "Information and communication", "K": "Finance and insurance", "L": "Real estate",
                "M": "Professional, scientific and technical", "N": "Administrative services", "O": "Public administration",
                "P": "Education", "Q": "Health and social work", "R": "Arts and recreation", "S": "Other services", "T": "Households as employers",
                "U": "Extraterritorial organisations", "?": "sector not recorded"}
MIN_GROUP = 200   # funded firms in a group before it gets its own row; the rest pooled as "all other"


def grant_years(firms):
    """crn -> {start year: award offered} for the funded firms (same row rules as pool.treated)."""
    by = collections.defaultdict(lambda: collections.defaultdict(float))
    for line in open(ROOT / "grants.jsonl"):
        r = json.loads(line)
        c = r["CRN"]
        if c not in firms or firms[c]["g"] == 0:
            continue
        if float(r.get("Award Offered (£)") or 0) <= 0 or (r.get("Participant Withdrawn From Project") or "").lower().startswith("withdrawn"):
            continue
        y, _ = V.excel_year(r.get("Project Start Date"))
        if y:
            by[c][y] += float(r["Award Offered (£)"])
    return by


def gbp(v):
    return "–" if not np.isfinite(v) else f"£{v:+,.0f}"


def num(v):
    return "–" if not np.isfinite(v) else f"{v:+.2f}"


def cell(e):
    return f"{e['fmt'](e['att'])} ({e['fmt'](e['lo'])} to {e['fmt'](e['hi'])}; {e['n']:,})"


def effect(name, firms, P, trend, keep=None, shift=0):
    r = R.run(name, firms, P, trend, keep=keep, shift=shift)
    e = r["levels_winsorised"][1 if shift else R.HEADLINE]
    return dict(e, matched=r["funded_matched"])


def split_table(L, title, name, trend, firms, P, groups):
    fmt = gbp if name != "employees" else num
    L += [f"### {title}", "", "| Group | funded firms | matched | t+3 effect (95%; firms at t+3) | placebo at real t−1 |", "|---|---|---|---|---|"]
    for label, keep in groups:
        a = effect(name, firms, P, trend, keep=keep); p = effect(name, firms, P, trend, keep=keep, shift=2)
        a["fmt"] = p["fmt"] = fmt
        L.append(f"| {label} | {len(keep):,} | {a['matched']:,} | {cell(a)} | {fmt(p['att'])} ({fmt(p['lo'])} to {fmt(p['hi'])}) |")
        print(L[-1], flush=True)
    L.append("")


def main():
    lock = R.check_lock()
    firms = load_firms()
    funded = {c: f for c, f in firms.items() if f["g"] > 0}
    treated = {p[0]: p for p in (l.rstrip("\n").split("\t") for l in list(open(ROOT / "treated.tsv"))[1:])}
    gy = grant_years(firms)
    L = ["# Innovate UK study — appendix analyses (v2.2; INTERNAL until published)", "",
         f"Plan v{lock['version']} (locked {lock['locked_utc']}). Produced by `study/run_appendix.py`.", ""]

    # ---- descriptives (no outcomes) ----
    money = [sum(gy[c].values()) for c in funded]
    first = [gy[c].get(f["g"], 0.0) for c, f in funded.items()]
    L += ["## The funded population (counts and money only)", "",
          f"- Funded business recipients (first project from April 2016, never funded 2004–16): **{len(funded):,}**.",
          f"- Awards offered to them on projects starting April 2016 onwards: **£{sum(money) / 1e9:,.2f}bn** "
          f"(median per firm £{np.median(money):,.0f}; mean £{np.mean(money):,.0f}; largest £{max(money) / 1e6:,.1f}m).",
          f"- Awards on projects starting in each firm's first grant year: median £{np.median(first):,.0f}, mean £{np.mean(first):,.0f}.",
          f"- Firms with more than one grant year: {sum(len(gy[c]) > 1 for c in funded):,} ({100 * np.mean([len(gy[c]) > 1 for c in funded]):.0f}%).", ""]
    for col, label in ((3, "First project's product type"), (4, "Enterprise size (UKRI file)"), (5, "Region (UKRI file)")):
        cnt = collections.Counter(treated[c][col] or "not stated" for c in funded if c in treated)
        L += [f"| {label} | funded firms |", "|---|---|"] + [f"| {k} | {v:,} |" for k, v in cnt.most_common()] + [""]
    cnt = collections.Counter(f["g"] for f in funded.values())
    L += ["| First grant year (t0) | funded firms |", "|---|---|"] + [f"| {k} | {v:,} |" for k, v in sorted(cnt.items())] + [""]
    cnt = collections.Counter(R.section(f["sic2"]) if f["sic2"].isdigit() else "?" for f in funded.values())
    L += ["| Sector (SIC section) | funded firms |", "|---|---|"] + \
         [f"| {SECTION_NAME.get(k, 'not known')} | {v:,} |" for k, v in cnt.most_common()] + [""]
    print("descriptives done", flush=True)

    # ---- turnover coverage (no estimate) ----
    tp = load_panel("turnover")
    with_t = {c for (c, y) in tp}
    win = lambda c: any((c, y) in tp for y in range(firms[c]["g"] - 1, firms[c]["g"] + 4))
    big = {c for c in funded if treated.get(c, [""] * 5)[4].lower() in ("large", "industrial: large")}
    pool = [c for c, f in firms.items() if f["g"] == 0]
    L += ["## Q4 Turnover in the public record (coverage only)", "",
          f"- Funded firms filing turnover in any year t−1…t+3: **{sum(win(c) for c in funded):,} of {len(funded):,} "
          f"({100 * np.mean([win(c) for c in funded]):.1f}%)**; among firms UKRI records as large: "
          f"{100 * np.mean([win(c) for c in big]):.0f}% ({len(big):,} firms); all other sizes "
          f"{100 * np.mean([win(c) for c in funded if c not in big]):.1f}%.",
          f"- Comparison pool firms that ever filed turnover: {100 * np.mean([c in with_t for c in pool]):.1f}% of {len(pool):,}.",
          "- Small companies may file abridged accounts without a profit and loss account, so most funded firms never put turnover "
          "on the public record. No turnover estimate is built (plan §1 Q4).", ""]
    del tp
    print("turnover done", flush=True)

    # ---- capacity measures (design B, as net assets) ----
    L += ["## Capacity measures — design B (trend-adjusted), with placebo", "",
          "| Outcome | funded matched | t+3 effect (95%; firms) | placebo at real t−1 | minimum detectable effect |", "|---|---|---|---|---|"]
    for name, label in (("fixed_assets", "Fixed assets"), ("total_assets_less_current_liabilities", "Total assets less current liabilities")):
        P = load_panel(name)
        a = effect(name, firms, P, True); p = effect(name, firms, P, True, shift=2)
        a["fmt"] = gbp
        L.append(f"| {label} | {a['matched']:,} | {cell(a)} | {gbp(p['att'])} ({gbp(p['lo'])} to {gbp(p['hi'])}) | "
                 f"£{V.mde(a['lo'], a['hi']):,.0f} |")
        print(L[-1], flush=True)
        del P
    L.append("")

    # ---- grant money in the outcome's own window ----
    na, emp = load_panel("net_assets"), load_panel("employees")
    L += ["## Grant money counted in the outcome's own window (definition corrected)", "",
          "v2.0 used every award a firm was offered in the whole file, including projects that started after t+3. A firm that grows "
          "wins more and larger grants later, so that measure partly follows the outcome. Below: the dose is the first grant year's "
          "awards; value for money divides by awards on projects started t0…t+3, for the firms seen at t+3. v2.0 figures beside.", ""]
    for name, trend, P in (("net_assets", True, na), ("employees", False, emp)):
        fmt = gbp if name == "net_assets" else num
        I = R.run(name, firms, P, trend, internals=True)["_internals"]
        antI = R.run(name, firms, P, trend, shift=2, internals=True)["_internals"]
        crn = lambda J, t: J["crns"][t]
        d0 = {t: gy[crn(I, t)].get(firms[crn(I, t)]["g"], 0.0) for t in I["matches"]}
        q1, q2 = V.terciles(list(d0.values()))
        d0p = {t: gy[crn(antI, t)].get(firms[crn(antI, t)]["g"], 0.0) for t in antI["matches"]}
        L += [f"### {name.replace('_', ' ')} — {'B trend-adjusted' if trend else 'A plain'}: dose by first-year award "
              f"(cuts £{q1:,.0f} and £{q2:,.0f})", "", "| Third | t+3 effect (95%; firms) | placebo at real t−1 |", "|---|---|---|"]
        for lab, lo_, hi_ in (("lowest", -1, q1), ("middle", q1, q2), ("highest", q2, 1e18)):
            a = V.sub_effect(I, {t for t, v in d0.items() if lo_ < v <= hi_})
            p = V.sub_effect(antI, {t for t, v in d0p.items() if lo_ < v <= hi_}, e=1)
            a["fmt"] = fmt
            L.append(f"| {lab} third | {cell(a)} | {fmt(p['att'])} ({fmt(p['lo'])} to {fmt(p['hi'])}; {p['n']:,}) |")
            print(L[-1], flush=True)
        L.append("")
        if name == "net_assets":
            seen = [t for t in I["matches"] if int(I["g"][t]) + R.HEADLINE <= V.LAST_FULL_YEAR
                    and np.isfinite(I["Yw"][t, R.YEARS.index(int(I["g"][t]) + R.HEADLINE)])]
            w3 = float(np.mean([sum(v for y, v in gy[crn(I, t)].items() if int(I["g"][t]) <= y <= int(I["g"][t]) + 3) for t in seen]))
            wall = float(np.mean([sum(gy[crn(I, t)].values()) for t in seen]))
            v20 = float(np.mean([I["award"][t] for t in I["matches"]]))
            h = R.run(name, firms, P, trend)["levels_winsorised"][R.HEADLINE]
            L += ["**Value for money, net assets at t+3 per £1 of grant:**", "",
                  "| Grant counted | mean per firm | per £1 (95%) |", "|---|---|---|",
                  f"| v2.0: every award in the file, all matched firms | £{v20:,.0f} | £{h['att'] / v20:.2f} (£{h['lo'] / v20:.2f} to £{h['hi'] / v20:.2f}) |",
                  f"| every award in the file, firms seen at t+3 | £{wall:,.0f} | £{h['att'] / wall:.2f} (£{h['lo'] / wall:.2f} to £{h['hi'] / wall:.2f}) |",
                  f"| **projects started t0…t+3, firms seen at t+3** | £{w3:,.0f} | **£{h['att'] / w3:.2f} (£{h['lo'] / w3:.2f} to £{h['hi'] / w3:.2f})** |",
                  f"({len(seen):,} firms seen at t+3.)", ""]
            print(L[-5:], flush=True)

    # ---- sector and region (descriptive appendix tables) ----
    L += ["## By sector and region (descriptive; not tested one by one)", ""]
    secs = collections.Counter(R.section(f["sic2"]) for f in funded.values() if f["sic2"].isdigit())
    big_s = [s for s, n in secs.most_common() if n >= MIN_GROUP]
    sec_groups = [(SECTION_NAME.get(s, s), {c for c, f in funded.items() if f["sic2"].isdigit() and R.section(f["sic2"]) == s}) for s in big_s]
    sec_groups.append(("all other sectors", {c for c, f in funded.items() if not (f["sic2"].isdigit() and R.section(f["sic2"]) in big_s)}))
    regs = collections.Counter(treated[c][5] for c in funded if c in treated)
    big_r = [r for r, n in regs.most_common() if n >= MIN_GROUP and r]
    reg_groups = [(r, {c for c in funded if c in treated and treated[c][5] == r}) for r in big_r]
    reg_groups.append(("all other / not stated", {c for c in funded if not (c in treated and treated[c][5] in big_r)}))
    for name, trend, P in (("net_assets", True, na), ("employees", False, emp)):
        d = f"{name.replace('_', ' ')}, {'B trend-adjusted' if trend else 'A plain'}"
        split_table(L, f"Sector — {d}", name, trend, firms, P, sec_groups)
        split_table(L, f"Region — {d}", name, trend, firms, P, reg_groups)
    (ROOT / "RESULTS-appendix.md").write_text("\n".join(L) + "\n")
    print("written", flush=True)


if __name__ == "__main__":
    main()
