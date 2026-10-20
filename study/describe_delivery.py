"""Theory of change, first link (grant -> project delivered): the UKRI file's own status and spend for the funded firms'
participant rows (descriptive; no outcomes). Writes data/study/RESULTS-delivery.md.   .venv/bin/python study/describe_delivery.py"""
import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "data" / "study"


def main():
    funded = {l.split("\t")[0] for l in list(open(ROOT / "treated.tsv"))[1:]}
    status, rows, withdrawn, offered, spent = collections.Counter(), 0, 0, 0.0, 0.0
    closed_offered = closed_spent = 0.0
    for line in open(ROOT / "grants.jsonl"):
        r = json.loads(line)
        if r["CRN"] not in funded or float(r.get("Award Offered (£)") or 0) <= 0:
            continue
        if (r.get("Participant Withdrawn From Project") or "").lower().startswith("withdrawn"):
            withdrawn += 1
            continue
        rows += 1
        status[r.get("Project Status") or "not stated"] += 1
        a, s = float(r["Award Offered (£)"]), float(r.get("Actual Spend to Date (£)") or 0)
        offered += a; spent += s
        if r.get("Project Status") == "Closed":
            closed_offered += a; closed_spent += s
    L = ["# Innovate UK study — project delivery in the UKRI file (descriptive; INTERNAL until published)", "",
         f"- Participant rows of the {len(funded):,} funded firms (award > £0, participant not withdrawn): **{rows:,}**; "
         f"participant-withdrawn rows left out: {withdrawn:,}.",
         f"- Award offered on those rows: **£{offered / 1e9:.2f}bn**; actual spend to date: **£{spent / 1e9:.2f}bn** "
         f"({100 * spent / offered:.0f}% of the offer).",
         f"- Closed projects only: spend {100 * closed_spent / closed_offered:.0f}% of the award offered "
         f"(£{closed_spent / 1e9:.2f}bn of £{closed_offered / 1e9:.2f}bn).", "",
         "| Project status (UKRI file) | participant rows |", "|---|---|"] + [f"| {k} | {v:,} |" for k, v in status.most_common()]
    (ROOT / "RESULTS-delivery.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
