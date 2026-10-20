# Do Innovate UK grants change how firms grow? — study protocol (v1.0, FINAL, 12 Oct 2026)

Status: **final (v1.0), fixed before any funded-vs-comparison outcome was computed.** Its SHA-256 fingerprint and UTC
time are in `data/study/PROTOCOL-LOCK.json`, written before the analysis script first ran; the analysis refuses to run if
this file no longer matches that fingerprint. Every later change is logged in §8 with its reason and marked as made after
results were seen. Designed to the HM Treasury Magenta Book (2026).

## 1. Questions
1. **Primary (two, set by what the record allows):**
   a. **Net assets** for every cohort (filed by 97–100% of firms in every year 2013–2025);
   b. **Average employees** for cohorts whose two pre-grant years fall in accounting periods from 2016 onwards
      (small companies were not required to disclose employees before 2016; first awards from 2019/20).
2. Do they end up financially stronger (net assets, total assets less current liabilities, cash)?
3. Are they more likely to still be trading five years on (survival)?
4. Do effects differ by firm size, grant size, programme type (e.g. collaborative R&D, feasibility, Smart), sector, region
   and year? The 2020 cohort (2,172 first-time recipients, about double a normal year, largely Covid-era emergency innovation
   funding) is reported separately as well as pooled.
5. Where turnover is filed (mostly larger firms): does it rise faster?

## 2. Theory of change (summary)
Grant money (input) → R&D project delivered with partners (activities) → new products, processes, skills, partnerships
(outputs) → more staff, investment and capability (outcomes) → firm growth, resilience and wider productivity (impacts).
External factors: the economic cycle, Covid-19 support schemes (2020–22), sector shocks, other public funding.
What can go wrong in the chain: substitution (the firm would have done the R&D anyway), selection (stronger firms apply and
win), time lags beyond the observation window.

## 3. Data
- **Treatment:** UKRI "Innovate UK funded projects, 2016/17 to present" (published Sept 2026). 48,121 participant rows;
  39,175 carry a valid company registration number (CRN); 15,782 distinct companies. Fields: award offered, project dates,
  product type, sector, region, enterprise size, withdrawn flag, project status.
- **Outcomes:** Companies House bulk accounts (inline XBRL), monthly archives 2014–2026, read by company number.
  Every figure is kept with its source filing (archive month, file name), stored gzipped as the receipt.
- **Which filing a figure comes from:** a year's value is taken from the company's own accounts made up to that year;
  the prior-year comparative in the next filing is used only when the own-year filing is missing. Data checks found the two
  agree for 92% (net assets) and 94% (employees) of firm-years seen both ways; the rest are restatements or tagging faults.
  Where a firm filed more than one set for the same year, the latest-filed is used.
- **Coverage rule:** the bulk data holds accounts filed electronically (inline XBRL); paper/PDF filings are not in it.
  The same rule applies to funded and comparison firms alike.
- **Comparison pool:** companies that **filed accounts in the years before each grant cohort**, taken from the archive
  indexes themselves (so firms that later closed are included), that never appear in either grant file (2004 onwards).
  Sector (SIC) and incorporation date from the live register for firms still on it, and from the Companies House API for
  firms that have since closed. The live register alone is never used to draw controls: it lists only survivors and would
  flatter the comparison group (survivor bias).
- **Known gaps, stated up front:** small and micro companies file abridged accounts that usually omit turnover
  (in a test month, 5% of grant-firm filings carried turnover, 86% employees, 75% net assets); firms with no CRN
  (19% of rows: universities, public bodies, sole traders, some overseas) are out of scope; dissolved companies stop
  filing, so survival is read from filing status and Companies House records, not assumed.

## 4. Design
- **Unit:** company, business recipients only (enterprise size micro/small/medium/large/SME; public sector bodies, academic,
  research and technology organisations, Catapults and charities are excluded even where they hold a company number).
- **Treated:** first project start from April 2016, never funded in the 2004–2016 file, award offered > £0, not withdrawn. **Treatment year t0:** start year of the firm's first Innovate UK project in the file.
  Firms whose first award predates 2016/17 (found in the 2004–2016 file) are excluded from the treated group and the pool.
- **Matching (v0.1 intent — superseded by 'as built' below and §4a; kept for the record):** for each treated firm, comparison firms with: the same 2-digit SIC; incorporation within ±3 years;
  the same size band and similar pre-period levels and trends (employees, net assets) in t−2 and t−1; filing in the
  same calendar year. Primary: nearest-neighbour propensity score matching (up to 5 controls, caliper 0.2 SD of the logit),
  exact on SIC-2 and t0 year. Balance reported for every matching variable (standardised differences < 0.1 target).
- **Matching (as built):** separately for each grant cohort, on that cohort's own three pre-grant years of the outcome (levels
  and slope) plus firm age, within exact sector strata; up to 5 never-funded firms within 0.2 SD of the propensity logit.
  If any matching variable's standardised difference exceeds 0.1, the caliper is tightened to 0.1 and both are reported.
- **Primary estimator — chosen on simulated data only, before any real outcome was seen (`data/study/SIM-CHECK.md`):**
  cohort-by-cohort difference-in-differences against the matched firms, after removing each firm's own growth trend
  estimated from the three years **before** the matching window (so the trend never reuses the matched years). In 40
  simulated runs per scenario with selection on unobserved growth: no-effect bias ≈ +0.1, true-effect estimates within
  0.1 of the truth, 95% intervals covering the truth 85–98% of the time. The plain matched comparison was biased
  (+0.5 to +0.7) and covered the truth only 2–30% of the time; the naive comparison overstated by ≈0.65.
  It needs six pre-grant years: available for net assets for cohorts from 2019; for employees (disclosed from 2016) the
  plain matched comparison is reported with its bias measured from the placebo years shown alongside.
- **Uncertainty:** firm-level bootstrap (500 draws), funded firms resampled with their matched controls.
- **Survival:** share still active at t+3 and t+5, treated vs matched, with the same design.

## 4a. Analysis rules fixed at v1.0 (from the pool counts in `data/study/POOL-CHECKS.md` — counts only)
- **Strata:** grant cohort × 2-digit SIC. Where a cohort's 2-digit sector holds fewer than 25 eligible never-funded firms,
  that sector is matched within its SIC 2007 section (letter) instead; the count of firms matched this way is reported, and
  a robustness run drops them.
- **Eligibility, primary (established firms):** the base year t−1 is present, at least 2 of the 3 matching years (t−3…t−1)
  and at least 2 of the 3 trend years (t−6…t−4). The same rule applies to the funded firm and every possible control.
  Plain matched analysis: base year present and at least 2 of the 3 matching years.
- **Scales:** matching covariates (pre-years and slope) are read on the asinh scale (net assets) or log(1+x) (employees), so
  a few very large firms cannot steer the propensity model; firm age is added in years.
  Outcomes: **net assets in £**, each calendar year winsorised at its 1st and 99th percentiles across all analysed firms
  (primary, because it can be set against the grant's own size); asinh(net assets) as secondary. **Employees as a headcount**,
  winsorised the same way (primary); log(1+employees) secondary.
- **Headline:** the effect at **t+3** for each population and each primary outcome, with its 95% interval; the whole event
  path (t−6…t+5) is always shown beside it. t+3 is the latest year reached by cohorts up to 2022 in accounts filed by
  Sept 2026. Cohorts with no year after the grant yet (2025, 2026) are matched and shown, but add nothing after t0.
- **The grant's own money:** grant income passes into retained earnings, so part of any net-assets effect is the award itself.
  Every net-assets effect is shown next to the median award of the firms it rests on; an effect no larger than the award is
  reported as such, never as growth.
- **Survival:** a funded firm and its matched controls are followed from t0; closed = dissolved, in liquidation or
  administration, or a cessation date on the record. Share still open at t+3 and t+5, funded minus matched, same bootstrap.
- **Inference:** 500 firm-level bootstrap draws (seed 1), 95% percentile intervals. With two primary outcomes, both are
  always reported; none is chosen after the fact.
- **The 2020 cohort** is reported on its own and within the pooled result; so is every other cohort.

## 4b. Who each analysis covers (counted before any outcome was looked at — `data/study/PANEL-STRUCTURE.md`)
Of 11,150 funded businesses, the primary trend-adjusted analysis (net assets; base year present, at least two of the three
matching years and two of the three earlier trend years) covers **2,457 established firms (median age at grant 10 years)**.
The plain matched analysis covers 5,110 firms for net assets and 3,988 for employees. Firms left out are young: median age
3 at grant, 62% under four. Results are therefore reported **by population**, never pooled into one headline:
1. **Established firms** — primary design above (strongest evidence).
2. **Young firms (under four at grant, or too few pre-years)** — matched on incorporation year, 2-digit sector, region
   and size in their first filed accounts; outcomes = growth from first filing and survival to t+3 / t+5; plain
   difference-in-differences. Reported as **weaker evidence**: there is no pre-grant trend to test, so selection on
   unobserved ambition may remain.
The summary states plainly which population each finding describes and how many funded firms it rests on.

## 5. Robustness (all reported, whichever way they point)
Placebo treatment dates (t0 − 2); alternative matching (coarsened exact matching; 1:1 without replacement);
dropping Covid years; excluding very large awards (top 1%); restricting to single-award firms; outcomes in logs and levels;
pre-trend tests; sensitivity to unobserved confounding (Rosenbaum bounds / E-values).

## 6. What this study cannot tell us (said where it bites)
Unobserved differences (ambition, management quality) may remain after matching. Abridged accounts limit turnover and profit
analysis to larger firms. It measures firm-level outcomes, not spillovers to other firms or the economy. It is an
independent study using public data; it is not commissioned by, or endorsed by, UKRI or Innovate UK.

## 7. Outputs
Two-page summary first; findings by question with key-findings boxes; full method and balance tables in appendices;
analysis code and derived (non-personal) data released; every figure traceable to its filing.

## 8. Change log
- v0.1 (11 Oct 2026): first draft, before any outcome analysis.
- v0.2 (11 Oct 2026): data checks only (no outcomes compared): employees are structurally absent from small-company
  accounts before 2016 periods, so the primary outcome is split — net assets for all cohorts, employees for cohorts with
  pre-grant years from 2016. Tag names mapped across the old UK GAAP and FRS 102 taxonomies (`concepts.py`); reader fixed
  for 2008-format inline XBRL and plain XBRL after the checks showed early years reading empty (`DATA-CHECKS.md`).
- v0.3 (11 Oct 2026): comparison pool drawn from pre-grant filers in the archive indexes (includes later-closed firms),
  never from the live register alone, to avoid survivor bias. No outcomes compared.
- v0.4 (11 Oct 2026): estimator fixed from simulation evidence only (no real outcomes seen): per-cohort matching on the
  cohort's own pre-years, primary = trend-adjusted DiD with trend from the years before matching; balance rule; electronic
  filings coverage rule stated.
- v0.4 addendum (11 Oct 2026): own-year filing rule (comparatives only fill gaps); reader fixed for software that labels
  every total "original" (Oct 2023 – Feb 2024 filings had read as empty). No outcomes compared.
- v0.5 (11 Oct 2026): populations fixed from panel structure counts only (no outcomes): established firms (primary) and
  young firms (separate, weaker design); results never pooled into one headline.
- v1.0 (12 Oct 2026): FINAL, before any funded-vs-comparison outcome was computed. Pool coverage counted (counts only,
  `POOL-CHECKS.md`); analysis rules fixed (§4a): strata with thin-sector fallback, eligibility, scales, t+3 headline,
  grant-money caveat, survival definition, inference. Fingerprint in `data/study/PROTOCOL-LOCK.json`.
- **v1.1 (12 Oct 2026) — ADDED AFTER RESULTS WERE SEEN.** The §5 placebo (grant date moved two years earlier) failed for
  both primary designs: funded firms were already pulling ahead in the two years before the real grant (employees +1.6,
  net assets +£57k, both intervals clear of zero). The v1.0 headlines are kept unchanged and reported with that failure.
  Added, as a secondary analysis labelled post hoc: the same designs with **later winners as controls** — firms whose
  first grant came six or more years after the cohort (so their own two pre-grant years fall after the t+3 headline year),
  matched by the same rules. They share the trait of applying and winning, which never-funded firms lack. Nothing in v1.0
  is changed or removed.
