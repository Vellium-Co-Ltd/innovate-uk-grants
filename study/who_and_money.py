"""EXPLORATORY (added 12 Oct 2026, after results; not in the locked plan). Two things the winning evaluations show and ours lacked
(data/teardown/fullread/SYNTHESIS.md; floor items 1 and 8):

  A. Who is funded: funded firms against the 1-in-100 sample of all filing companies, on age, sector, nation, size and the
     two years before. Each funded firm is described in the year before its grant (t−1); each sample firm in a year drawn,
     by a fixed hash of its company number, from the funded firms' grant-year mix, among years it filed accounts — so
     both groups are seen in the same calendar years. Descriptive only.
  B. Where the first-year money goes: the share of first-year grant money in each third of first-year awards (the cuts of
     the employee dose table in RESULTS-appendix), beside that table's effect and pre-grant gap per third, and the money a
     year in the top third. It prices one change to the programme itself; it estimates no new effect.

Writes data/study/RESULTS-profile.md.   .venv/bin/python study/who_and_money.py
"""
import collections
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_analysis as R  # noqa: E402
import run_appendix as A  # noqa: E402
from analysis_data import ROOT, load_firms, load_panel  # noqa: E402

CUTS = (48_477, 99_410)                       # employee dose-table cuts (RESULTS-appendix, design A)
SCOT = set("AB DD DG EH FK G HS IV KA KW KY ML PA PH ZE".split())
WALES = set("CF LL NP SA LD".split())
LONDON = set("E EC N NW SE SW W WC".split())


def nation(pc):
    return ("Northern Ireland" if pc == "BT" else "Scotland" if pc in SCOT else "Wales" if pc in WALES
            else "London" if pc in LONDON else "England outside London" if pc else "not recorded")


def age_band(a):
    return "under 3" if a < 3 else "3 to 5" if a < 6 else "6 to 10" if a < 11 else "11 to 20" if a < 21 else "over 20"


def emp_band(e):
    return "not filed" if e is None else "0 to 1" if e < 2 else "2 to 9" if e < 10 else "10 to 49" if e < 50 else "50 or more"


def main():
    lock = R.check_lock()
    firms = load_firms()
    emp = load_panel("employees")
    funded = {c: f for c, f in firms.items() if f["g"] > 0}
    years = sorted(f["g"] for f in funded.values())
    have = collections.defaultdict(set)              # years a firm filed any accounts (net assets are on almost every filing)
    with open(ROOT / "panel_net_assets.tsv") as fh:
        next(fh)
        for line in fh:
            c, y = line.split("\t", 2)[:2]
            have[c].add(int(y))

    def ref_year(c, f):
        if f["g"]:
            return f["g"]
        h = int(hashlib.sha1(c.encode()).hexdigest()[:8], 16)
        for k in range(12):                                           # first draw the firm was alive and filing in
            y = years[(h + k * 7919) % len(years)]
            if f["inc_year"] and f["inc_year"] < y and (not f["ceased_year"] or f["ceased_year"] >= y) and (y - 1) in have[c]:
                return y
        return None

    rows = {"funded": collections.defaultdict(collections.Counter), "sample": collections.defaultdict(collections.Counter)}
    n = collections.Counter()
    for c, f in firms.items():
        grp = "funded" if f["g"] else "sample"
        y = ref_year(c, f)
        if y is None or not f["inc_year"] or (y - 1) not in have[c]:      # same rule both sides: accounts filed for t−1
            continue
        n[grp] += 1
        e1 = emp.get((c, y - 1)); e3 = emp.get((c, y - 3))
        rows[grp]["Age at the grant year (sample: reference year)"][age_band(y - f["inc_year"])] += 1
        rows[grp]["Sector"][A.SECTION_NAME.get(R.section(f["sic2"]) if f["sic2"].isdigit() else "?", "sector not recorded")] += 1
        rows[grp]["Nation (registered address)"][nation(f["postcode_area"])] += 1
        rows[grp]["Employees in the year before"][emp_band(e1[0] if e1 else None)] += 1
        if e1 and e3:
            rows[grp]["Employees over the two years before (firms filing both years)"][
                "grew" if e1[0] > e3[0] else "fell" if e1[0] < e3[0] else "no change"] += 1
    L = ["# Innovate UK study — who is funded, and where the first-year money goes (EXPLORATORY, INTERNAL until published)", "",
         f"Protocol v{lock['version']} (locked {lock['locked_utc']}). Added 12 Oct 2026 after results were seen. Descriptive: no "
         "effect is estimated here.", "",
         f"## A. Who is funded: {n['funded']:,} funded firms against {n['sample']:,} firms from the 1-in-100 sample", "",
         "Funded firms are described at their grant year; each sample firm at a year drawn from the funded firms' grant-year mix "
         "among years it was alive. Both groups: only firms that filed accounts for the year before (t−1).", ""]
    for measure in rows["funded"]:
        tf, ts = sum(rows["funded"][measure].values()), sum(rows["sample"][measure].values())
        L += [f"### {measure}", "", f"| | funded ({tf:,}) | sample ({ts:,}) |", "|---|---|---|"]
        keys = sorted(set(rows["funded"][measure]) | set(rows["sample"][measure]), key=lambda k: -rows["funded"][measure][k])
        for k in keys:
            L.append(f"| {k} | {100 * rows['funded'][measure][k] / tf:.1f}% | {100 * rows['sample'][measure][k] / ts:.1f}% |")
        L.append("")
    gy = A.grant_years(firms)
    first = {c: gy[c].get(f["g"], 0.0) for c, f in funded.items()}
    total = sum(first.values())
    span = max(years) - min(years) + 1
    L += ["## B. Where the first-year money goes", "",
          f"First-year awards (projects starting in each firm's grant year), all {len(first):,} funded firms, {min(years)}–{max(years)}: "
          f"£{total / 1e9:.2f}bn. Thirds use the cuts of the employee dose table (£{CUTS[0]:,} and £{CUTS[1]:,}).", "",
          "| First-year award | funded firms | share of firms | first-year money | share of money | money a year |", "|---|---|---|---|---|---|"]
    for lab, lo, hi in (("up to £48,477", -1, CUTS[0]), ("£48,478 to £99,410", CUTS[0], CUTS[1]), ("over £99,410", CUTS[1], 1e18)):
        sel = [v for v in first.values() if lo < v <= hi]
        L.append(f"| {lab} | {len(sel):,} | {100 * len(sel) / len(first):.0f}% | £{sum(sel) / 1e6:,.0f}m | "
                 f"{100 * sum(sel) / total:.0f}% | £{sum(sel) / span / 1e6:,.0f}m |")
    L += ["", f"Money a year divides by the {span} grant years in the file ({min(years)}–{max(years)}); the last years are part-years.",
          "Effects by the same thirds are in RESULTS-appendix (employee dose table): the top third's employee gap at t+3 is "
          "close to the gap it already had before the grant.", ""]
    (ROOT / "RESULTS-profile.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
