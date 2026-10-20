"""Young firms: is their net-assets gain profit kept or capital put in? EXPLORATORY, Appendix N, after RESULTS-profit.md was
seen (13 Oct 2026). Chapter 7's young-firm net-assets gain (growth from first filing, PROTOCOL §5.2) is the largest in the
study, and the report says it may be shares sold to investors rather than profit. profit_split.py covered the established-firm
designs only; this runs the same young-firm design (run_v2.young_firms, unchanged) on retained earnings and capital put in.
Funded firms already in the net-assets design B stay out, as in Chapter 7. As filed only: a closed firm's reserves aren't zero.

Writes data/study/RESULTS-profit-young.md.    .venv/bin/python study/profit_young.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_analysis as R  # noqa: E402
import run_v2 as V  # noqa: E402
from analysis_data import ROOT, load_firms, load_panel  # noqa: E402
from analysis_data import gbp  # noqa: E402


def main():
    lock = R.check_lock()
    firms = load_firms()
    na, emp = load_panel("net_assets"), load_panel("employees")
    closed = V.closure_years(firms, (na, emp))
    regions = V.region_map()
    I = R.run("net_assets", firms, na, V.DESIGN["net_assets"], internals=True, reps=V.REPS)["_internals"]
    established = {I["crns"][t] for t in I["matches"]}
    re_ = load_panel("retained_earnings")
    cap = {k: (na[k][0] - v[0],) for k, v in re_.items() if k in na}
    L = ["# Innovate UK study: young firms, profit kept or capital put in (EXPLORATORY)", "",
         f"Not in the plan (v{lock['version']}); run after RESULTS-profit.md was seen. Design: Chapter 7's young firms (PROTOCOL §5.2), "
         "change from first filing to t+3, as filed.", "",
         "| Outcome | change from first filing to t+3 (95%; firms) | funded young firms matched of eligible |", "|---|---|---|"]
    for name, label, P in (("retained_earnings", "Retained earnings (profit kept)", re_),
                           ("capital_in", "Capital put in (net assets less retained earnings)", cap),
                           ("net_assets", "Net assets, firms with retained earnings at first filing", {k: na[k] for k in re_ if k in na})):
        y = V.young_firms(name, firms, P, closed, established, regions)
        e = y["as filed"]
        L.append(f"| {label} | {gbp(e['att'])} ({gbp(e['lo'])} to {gbp(e['hi'])}; {e['n']:,}) | {y['matched']:,} of {y['funded_young_eligible']:,} |")
        print(L[-1], flush=True)
    (ROOT / "RESULTS-profit-young.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
