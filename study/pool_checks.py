"""Comparison-pool checks — COUNTS ONLY, no funded-vs-comparison outcome is computed here (PROTOCOL.md §3–4).

Answers, before the protocol is locked: does the 1-in-100 pool carry the outcomes in the same years as the funded firms,
and are there enough never-funded firms in every cohort x sector stratum to match on? Writes data/study/POOL-CHECKS.md.
"""
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_data import ROOT, load_firms, load_panel  # noqa: E402


def main():
    firms = load_firms()
    out = ["# Comparison pool checks (counts only — no outcomes compared)", ""]
    treated = {c: f for c, f in firms.items() if f["g"] > 0}
    pool = {c: f for c, f in firms.items() if f["g"] == 0}
    no_sic = sum(1 for f in pool.values() if not f["sic2"])
    no_inc = sum(1 for f in pool.values() if not f["inc_year"])
    out += [f"- Funded businesses (treated.tsv): **{len(treated):,}**; never-funded pool firms: **{len(pool):,}** "
            f"(1-in-100 hash sample of every filer 2013–2026, closed firms included).",
            f"- Pool firms with no sector code: {no_sic:,}; with no incorporation date: {no_inc:,} (both left out of matching).",
            f"- Pool firms that have since closed (dissolved / liquidation / not on the live register): "
            f"{sum(1 for f in pool.values() if f['closed']):,} ({100 * sum(1 for f in pool.values() if f['closed']) / len(pool):.0f}%).", ""]
    for name in ("net_assets", "employees"):
        P = load_panel(name)
        out += [f"## {name.replace('_', ' ')}", "",
                "| Cohort | funded with 3 pre-years | pool with the same 3 years | funded with 6 pre-years | pool with the same 6 | "
                "funded in a sector with < 25 pool firms (3-yr) |", "|---|---|---|---|---|---|"]
        for g in sorted({f["g"] for f in treated.values()}):
            def has(c, n):
                return all((c, y) in P for y in range(g - n, g))
            t3 = [c for c, f in treated.items() if f["g"] == g and has(c, 3)]
            p3 = [c for c in pool if has(c, 3)]
            t6 = sum(1 for c, f in treated.items() if f["g"] == g and has(c, 6))
            p6 = sum(1 for c in pool if has(c, 6))
            per_sic = collections.Counter(pool[c]["sic2"] for c in p3)
            thin = sum(1 for c in t3 if per_sic[treated[c]["sic2"]] < 25)
            out.append(f"| {g} | {len(t3):,} | {len(p3):,} | {t6:,} | {p6:,} | {thin:,} |")
        src = collections.Counter(v[3] for k, v in P.items() if k[0] in pool)
        out += ["", f"Pool values by source: own-year filing {src['own']:,}; comparative filling a gap {src['comparative']:,}.", ""]
    (ROOT / "POOL-CHECKS.md").write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
