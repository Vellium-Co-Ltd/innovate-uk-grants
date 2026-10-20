"""What the matched comparison is made of (lesson L13): latest accounts category on the live Companies House register for funded
firms and their matched controls, in the two main designs. Firms no longer on the register (closed) are counted as such.
Writes data/study/RESULTS-dormant.md.   .venv/bin/python study/dormant_check.py"""
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_analysis as R  # noqa: E402
from analysis_data import ROOT, load_firms, load_panel  # noqa: E402


def main():
    R.check_lock()
    firms = load_firms()
    L = ["# Innovate UK study — what the matched groups are made of (INTERNAL until published)", "",
         "Latest accounts category on the live Companies House register (register.tsv). Closed firms are no longer on it.", ""]
    for name, trend, label in (("net_assets", True, "net assets, design B"), ("employees", False, "employees, design A")):
        I = R.run(name, firms, load_panel(name), trend, internals=True, reps=2)["_internals"]
        crns, M = I["crns"], I["matches"]
        funded = [crns[t] for t in M]
        controls = [crns[c] for cs in M.values() for c in cs]
        want, cat = set(funded) | set(controls), {}
        with open(ROOT / "register.tsv") as fh:
            ix = fh.readline().rstrip("\n").split("\t").index("Accounts.AccountCategory")
            for line in fh:
                p = line.rstrip("\n").split("\t")
                if p[0] in want:
                    cat[p[0]] = p[ix] or "not stated"
        L += [f"## {label}", "", "| Latest accounts category | funded firms | matched controls (each match counted) |", "|---|---|---|"]
        nf = collections.Counter(cat.get(c, "not on register (closed)") for c in funded)
        nc = collections.Counter(cat.get(c, "not on register (closed)") for c in controls)
        for k in sorted(set(nf) | set(nc), key=lambda k: -nc[k]):
            L.append(f"| {k} | {100 * nf[k] / len(funded):.1f}% | {100 * nc[k] / len(controls):.1f}% |")
        L += ["", f"Funded firms {len(funded):,}; control matches {len(controls):,}.", ""]
        print("\n".join(L[-4 - len(set(nf) | set(nc)):]), flush=True)
    (ROOT / "RESULTS-dormant.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
