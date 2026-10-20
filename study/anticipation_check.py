"""EXPLORATORY (added 12 Oct 2026, after results; not in the locked plan): is the pre-grant run-up firms hiring in hope of a
grant they'd applied for? The placebo moves the grant date two years earlier, so its year 0 is the real t-2 and its year 1
the real t-1, both measured from the real t-3. Hiring after applying should sit in the last year before the grant (t-1); a
gap already open at t-2 would need applications made more than a year before the project began. Same designs and matching
as the primary analysis (run_analysis.run with shift=2). Writes data/study/RESULTS-anticipation.md.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_analysis as R  # noqa: E402
from analysis_data import ROOT, load_firms, load_panel  # noqa: E402

DESIGNS = {"employees": False, "net_assets": True}   # as primary: plain matched / established firms, trend-adjusted


def main():
    lock = R.check_lock()
    firms = load_firms()
    L = ["# Innovate UK study — when the pre-grant gap opened (EXPLORATORY, INTERNAL until published)", "",
         f"Protocol v{lock['version']} (locked {lock['locked_utc']}). Added 12 Oct 2026 after results were seen, to test one "
         "objection: that the run-up before the grant is firms hiring in hope of a grant they had applied for. Placebo as in "
         "RESULTS-robustness (grant date moved two years earlier); its year 0 is the real t−2 and its year 1 the real t−1, both "
         "measured from the real t−3.", "",
         "| Measure (design) | funded matched | gap at real t−2 | 95% interval | gap at real t−1 | 95% interval | share of the t−1 gap already open at t−2 |",
         "|---|---|---|---|---|---|---|"]
    for name, trend in DESIGNS.items():
        panel = load_panel(name)
        r = R.run(name, firms, panel, trend, shift=2)
        a0, a1 = r["levels_winsorised"][0], r["levels_winsorised"][1]
        share = a0["att"] / a1["att"] if a1["att"] else float("nan")
        L.append(f"| {name.replace('_', ' ')} ({'established, trend-adjusted' if trend else 'plain matched'}) | "
                 f"{r['funded_matched']:,} | {R.fmt(a0['att'], name, 'l')} | {R.fmt(a0['lo'], name, 'l')} to {R.fmt(a0['hi'], name, 'l')} | "
                 f"{R.fmt(a1['att'], name, 'l')} | {R.fmt(a1['lo'], name, 'l')} to {R.fmt(a1['hi'], name, 'l')} | {100 * share:.0f}% |")
        print(L[-1], flush=True)
        del panel
    L += ["", "Read: hiring after applying would put most of the gap in the last year (t−1). A large share already open at t−2 "
          "points to the firms' own momentum, unless applications commonly came more than a year before the project start, which "
          "the public file cannot show (no application dates; Recommendation 3).", ""]
    (ROOT / "RESULTS-anticipation.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
