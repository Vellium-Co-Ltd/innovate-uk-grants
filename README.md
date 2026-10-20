# Innovate UK grants and the firms that win them — code and results

Vellium & Co Ltd (company 17045518). The study compares firms that received Innovate UK grants with matched firms that
did not, using accounts filed at Companies House. The report sets out the method, results and limits in full.

## What is here
- `study/` — the analysis: matching, estimation, every check and exploratory analysis, and the estimator's simulation test.
- `data/study/*.gz` — the prepared company-level data every result is computed from: funded firms and the comparison
  sample (`firms`, `treated`, `pool`), one panel per outcome (company number, year, value, the accounts tag and filing it
  came from), UKRI's funded-projects file, and the Companies House register rows for these firms. No personal data.
- `study/PROTOCOL.md` — the analysis plan; `study/protocol_versions/` every locked version; `data/study/PROTOCOL-LOCK.json`
  the fingerprints and the change log. The plan was made public with the study, after results were seen; the change log
  says when each change was made and whether results had been seen.
- `data/study/RESULTS-*.md`, `results-*.json` — every results file the report cites.

## Running it
`gunzip -k data/study/*.gz`, then run any analysis script from the repository root, for example
`python3 study/run_analysis.py`; each writes the results file named in the plan's index (§12), which you can compare with the
one published here. Every random draw uses a fixed seed.

## What isn't here
The data preparation (downloading the Companies House accounts archive and reading every filing into the panels) is done
by Vellium's own software and isn't published. Every value in the panels names the filing it was read from, so any figure
can be checked against Companies House by hand. Three results files come from that preparation stage and can't be re-run
from this repository: DATA-CHECKS.md (the filing reader's checks), PANEL-STRUCTURE.md and RESULTS-profit.md (the
retained-earnings split, built from the filings); its coverage check (RESULTS-profit-coverage.md) and young-firm split
(RESULTS-profit-young.md) can be. The sources are public, under the Open Government Licence v3.0: UKRI's funded-projects
file and Companies House.

Requires Python 3.12 and the packages in `requirements.txt`.

## Notes like "L48"
Comments and the plan's change log refer to entries in Vellium's lessons register, such as "L48". Each entry records a fault
found during the work, its cause and the check added so it can't recur. L48, for example, is the filing reader dropping
retained earnings; the reader was fixed for every filing and a test now refuses a reader that drops them again.

## Licence
Code: all rights reserved; view, run and quote only to check the published results (see LICENSE). Results files: Open Government Licence v3.0 terms apply to the underlying data.
