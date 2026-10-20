"""PROTOCOL §8 v1.1 (post hoc): the two primary designs with later winners as controls — firms whose first grant came 6+
years after the cohort — plus the same placebo. Writes data/study/RESULTS-later-winners.md."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_analysis as R  # noqa: E402
from analysis_data import ROOT, load_firms, load_panel  # noqa: E402
from robustness import PRIMARY  # noqa: E402

LATER = 6


def main():
    lock = R.check_lock()
    firms = load_firms()
    L = ["# Innovate UK study — later winners as controls (POST HOC, v1.1; INTERNAL until published)", "",
         f"Protocol v{lock['version']} (locked {lock['locked_utc']}). Controls = firms whose first grant came {LATER}+ years "
         "after the funded firm's, matched by the same rules. Only cohorts up to 2020 have such controls in the file.", ""]
    for name, trend in PRIMARY.items():
        panel = load_panel(name)
        for label, opt in (("Never-funded controls (v1.0 design, same cohorts)", {"keep": {c for c, f in firms.items() if 0 < f["g"] <= 2026 - LATER}}),
                           ("Later winners as controls", {"later_winners": LATER}),
                           ("Later winners — placebo, grant moved 2 years earlier", {"later_winners": LATER, "shift": 2})):
            r = R.run(name, firms, panel, trend, diag=True, **opt)
            if "keep" in opt:   # keep also removes later winners from the pool; never-funded only, cohorts <= 2020
                r["per_cohort"] = {k: v for k, v in r["per_cohort"].items() if k <= 2026 - LATER}
            L += [f"## {name.replace('_', ' ')} ({'trend-adjusted' if trend else 'plain matched'}) — {label}", "",
                  f"Funded firms matched: {r['funded_matched']:,}.", "",
                  "| Years from grant | effect (levels) | 95% interval | firms | effect (transformed) | 95% interval |",
                  "|---|---|---|---|---|---|"]
            for e in R.EVENTS:
                if e == -1:
                    continue
                a, b = r["levels_winsorised"][e], r["transformed"][e]
                L.append(f"| {e} | {R.fmt(a['att'], name, 'l')} | {R.fmt(a['lo'], name, 'l')} to {R.fmt(a['hi'], name, 'l')} | "
                         f"{a['n']:,} | {R.fmt(b['att'], name, 'transformed')} | {R.fmt(b['lo'], name, 'transformed')} to "
                         f"{R.fmt(b['hi'], name, 'transformed')} |")
            L += ["", "Cohorts: " + "; ".join(f"{g}: {c['matched']} matched of {c['eligible_funded']} (controls eligible "
                                              f"{c['pool_eligible']}, max |SMD| {c['max_smd_cal02']:.2f})"
                                              for g, c in sorted(r["per_cohort"].items())), ""]
            print(f"{name} {label}: t+3 {r['levels_winsorised'][3]}", flush=True)
        del panel
    (ROOT / "RESULTS-later-winners.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
