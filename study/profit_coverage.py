"""Does uneven coverage drive the profit split? EXPLORATORY, Appendix N, after RESULTS-profit.md was seen (13 Oct 2026).

Retained earnings sit on 64% of funded filings but 42% of comparison filings (RESULTS-profit.md), and profit_split.py drops a
firm-year with no retained-earnings line. If the firms whose filings leave the line out differ in profit (micro-entity and
filleted accounts show only the reserves total), the comparison is skewed. Test, with no cut-off of our choosing: keep only
firms whose filings carry retained earnings in EVERY year they file net assets (both groups), and rerun the same designs on
retained earnings, capital put in and net assets. Same result → coverage is not driving it; a different one → it is.

Writes data/study/RESULTS-profit-coverage.md.    .venv/bin/python study/profit_coverage.py
"""
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_analysis as R  # noqa: E402
from analysis_data import ROOT, load_firms, load_panel  # noqa: E402
from analysis_data import gbp  # noqa: E402


def main():
    lock = R.check_lock()
    firms = load_firms()
    na, re_ = load_panel("net_assets"), load_panel("retained_earnings")
    na_years, re_years = collections.defaultdict(set), collections.defaultdict(set)
    for c, y in na:
        na_years[c].add(y)
    for c, y in re_:
        re_years[c].add(y)
    complete = {c for c, ys in na_years.items() if ys and ys <= re_years.get(c, set())}
    L = ["# Innovate UK study: does uneven coverage drive the profit split? (EXPLORATORY)", "",
         f"Not in the plan (v{lock['version']}); run after RESULTS-profit.md was seen. Kept: firms whose filings carry retained "
         "earnings in every year they file net assets, funded and comparison alike.", "",
         "| Group | firms with net assets | of which complete | share |", "|---|---|---|---|"]
    for label, g in (("funded firms", True), ("comparison firms", False)):
        have = [c for c in na_years if c in firms and bool(firms[c]["g"]) == g]
        k = sum(1 for c in have if c in complete)
        L.append(f"| {label} | {len(have):,} | {k:,} | {100 * k / len(have):.1f}% |")
    L.append("")
    print("\n".join(L), flush=True)
    sub = {c: f for c, f in firms.items() if c in complete}
    cap = {k: (na[k][0] - v[0],) for k, v in re_.items() if k in na}
    for name, what, P in (("retained_earnings", "Retained earnings (profit kept in the firm)", re_),
                          ("capital_in", "Capital put in (net assets less retained earnings)", cap),
                          ("net_assets", "Net assets, same firms", na)):
        L += [f"## {what}", "", "| Design | t+3 effect (95%; firms at t+3) | placebo at real t−1 (95%) | funded firms matched |",
              "|---|---|---|---|"]
        for trend, dname in ((True, "B trend-adjusted"), (False, "A plain matched")):
            r = R.run(name, sub, P, trend)
            e = r["levels_winsorised"][R.HEADLINE]
            p = R.run(name, sub, P, trend, shift=2)["levels_winsorised"][1]
            L.append(f"| {dname} | {gbp(e['att'])} ({gbp(e['lo'])} to {gbp(e['hi'])}; {e['n']:,}) | "
                     f"{gbp(p['att'])} ({gbp(p['lo'])} to {gbp(p['hi'])}) | {r['funded_matched']:,} |")
            print(L[-1], flush=True)
        L.append("")
    (ROOT / "RESULTS-profit-coverage.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
