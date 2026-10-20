# Do Innovate UK grants change how firms grow? — study plan (v2.0, 12 Oct 2026)

Vellium & Co. An independent study using public data; not commissioned by, or endorsed by, UKRI or Innovate UK.
Designed to the HM Treasury Magenta Book (2026) and graded on the Maryland Scientific Methods Scale (What Works Growth).

**How this plan was fixed, said plainly.** v1.0 was fixed and fingerprinted before any funded-versus-comparison outcome was
computed (12 Oct 2026, 11:52 UTC), but it was not made public first. Its first results and a failed placebo test were then
seen, and the plan was reviewed against the reporting standard and the buyer's own evidence. Everything added after that
point is marked **[after results]** below and in §11. Every version's exact text and fingerprint is published with the study
(`protocol_versions/`, `PROTOCOL-LOCK.json`). Nothing in v1.0 has been removed without a line in §11 saying so.

## 1. Questions
1. **Growth (primary).** Did funded firms' **net assets** and **employees** change more than those of comparable firms
   that were not funded, over the five years after the grant?
2. **Financial resilience.** Did funded firms end up more or less resilient: **survival** to t+3 and t+5, **cash**, and the
   share slipping into **negative net assets** (liabilities above assets)? Survival is answered first, because it changes how
   question 1 must be read (§5.7).
3. **For whom.** Do effects grow with **grant size** (relative to the firm's size), and differ by **programme type**? For
   **Smart grants**, does public data reproduce UKRI's own estimate (§5.9)? **[after results]**
4. **Turnover** is filed by about 5% of these firms (abridged small-company accounts omit it), mostly large ones: one
   paragraph says what the public record can and cannot show; no estimate is built on it.
Sector, region and cohort results are shown as appendix tables (descriptive, not tested one by one).

## 2. What is already known **[after results]**
- **Frontier Economics for BEIS and Innovate UK (2017):** Innovate UK support 2008–2012, matched to the ONS Business Structure
  Database (BSD), propensity matching + difference-in-differences: survival +11 percentage points at t+3 and +16 at t+5;
  employment gains, with the warning that the survival effect biases employment results of unknown direction.
- **Vanino, Becker and Roper (ERC Research Paper 61, 2018):** Research Council and Innovate UK projects 2004–2016, c.10,000
  firms, BSD, PSM + DiD: turnover and employment 5.8–6.0% faster growth over three years, 22.5–28% over six.
- **Ipsos UK, Technopolis and George Barrett for Innovate UK (Smart Grants final impact evaluation, May 2026):** Smart
  2019/20–2024/25 (£531m, 1,688 projects); comparison with high-scoring declined applicants, early-vs-late winners and staggered
  DiD (Callaway–Sant'Anna) on ONS Secure Research Service data: employment +4.3%, turnover +6.0%, GVA +4.0%, R&D spend
  +5.4–7.8%; £1.27 of productivity gains per £1 of social cost by 2024/25.
- **ICURe (Ipsos MORI, 2020)** studies academic teams, not firms: out of this study's population; noted for method only.
- **[v2.3, after results] The strongest designs abroad**, read in their own texts, as the yardstick: regression discontinuity at
  a funding line or size threshold (Howell 2017; Santoleri et al. 2020/2024; Bronzini and Iachini 2014; Dechezleprêtre et al.
  2023), each with its sample size. They set the two tests run in v2.3's exploratory analyses (dose; firms short of finance).
What this study adds: every Innovate UK product, not one; public data and published code that anyone can re-run (the ONS
secure-lab studies cannot be re-run outside it); the full balance sheet and survival from filed accounts; formal placebo
tests of the pre-grant trend, reported whichever way they point.

## 3. Theory of change, and which link each analysis tests
| Link | What would show it | Tested here by |
|---|---|---|
| Grant → project delivered | project status, spend | UKRI file (status, withdrawn flag) — descriptive |
| Project → new capacity (staff, assets) | employees, fixed assets rise | Q1 employees; appendix fixed assets |
| Capacity → stronger firm | net assets, cash, fewer firms in negative net assets | Q1 net assets; Q2 |
| Stronger firm → survives and grows | survival, longer-run employees | Q2 survival; Q1 at t+4, t+5 |
| Stated aims → outcomes | firms whose projects said they would hire / launch fare differently | §5.10 project-description test |
| Wider economy (spillovers, products, skills) | — | not testable from firm accounts; said in §8 |
What can break the chain: substitution (the firm would have done it anyway), selection (stronger, faster-growing firms apply
and win — the placebo test measures this directly), time lags beyond the window, Covid-era shocks (2020–22).

## 4. Data
- **Treatment:** UKRI "Innovate UK funded projects, 2016/17 to present" (Sept 2026): 39,175 participant rows with a company
  number, 15,782 companies. Award offered, project dates, product type, competition, sector, region, size, withdrawn flag,
  public project description (96% of rows).
- **Outcomes:** Companies House bulk accounts (inline XBRL), monthly archives 2014–2026, read by company number; every value
  kept with its source filing (receipt). Own-year filing first; the next filing's comparative fills a gap only (the two agree
  for 92% of net-assets and 94% of employee firm-years seen both ways); latest-filed wins for amended accounts. Tag names mapped
  across UK GAAP and FRS 102 taxonomies.
- **Comparison pool:** a 1-in-100 hash sample of every company that filed accounts 2013–2026 (71,515 firms, 45% since closed),
  never in either grant file (2004 onwards). Sector and incorporation from the live register, or from Companies House for closed
  firms — never the live register alone (it lists only survivors).
- **Survival:** closure year = the cessation date on the record; a dissolved or insolvent firm with no date is dated to the year
  after its last accounts period. **[after results]**
- **Known gaps:** electronic filings only (paper/PDF accounts absent, same rule for both groups); firms without a company number
  (19% of rows: universities, public bodies, sole traders) out of scope; small companies did not disclose employees before 2016
  periods; "average employees" in small-company accounts includes directors. **[after results — last item]**
- **Data protection:** company-level figures only; directors' and people's personal details are not used.

## 5. Design
**5.1 Unit and treated.** Companies, business recipients only (micro/small/medium/large/SME); academic, research and public
bodies, Catapults and charities excluded. Treated: first Innovate UK project starting April 2016 or later, never in the 2004–2016
file, award > £0, not withdrawn. Treatment year t0 = start year of the first project.

**5.2 Populations (never pooled into one headline).** (1) Established firms with the pre-grant record the trend-adjusted design
needs (2,457 of 11,150 funded firms; median age 10); (2) the plain matched population (5,110 for net assets, 3,988 employees);
(3) young firms (under four at grant, or too few pre-years: median age 3) — matched on incorporation year, sector, region and
size in their first filed accounts; growth from first filing and survival; weaker evidence, said so.

**5.3 Comparisons.** Each result is shown for every comparison that can be built, with its Maryland level:
| | Comparison group | Built from | Maryland level |
|---|---|---|---|
| A | never-funded firms, matched (v1.0 primary) | 1-in-100 pool | 3 |
| B | never-funded, matched, net of each firm's own earlier trend (v1.0 primary for net assets) | pool | 3 |
| C | later winners: first grant 6+ years after the cohort **[after results]** | grants file | 3 |
| D | declined applicants, by score band if released **[after results]** | FOI request to UKRI | 3 (4 would need exact scores) |

**5.4 Matching.** For each cohort separately: strata = cohort × 2-digit SIC (a sector with fewer than 25 eligible comparison
firms is matched within its SIC section; count reported). Propensity on the cohort's own three pre-grant years (levels + slope,
on the asinh scale for net assets and log(1+x) for employees) plus firm age; up to 5 nearest within 0.2 SD of the logit; if any
|standardised difference| > 0.1, caliper 0.1, both reported. Eligibility: base year t−1 present and ≥2 of t−3…t−1; design B also
≥2 of t−6…t−4 (the trend comes from years before the matching window, so it never reuses matched years). The estimator was chosen
on simulated firms with a known answer before any real outcome was seen (`SIM-CHECK.md`).

**5.5 Outcomes and scales.** Net assets in £ and employees as a headcount, each calendar year winsorised at the 1st/99th
percentiles (primary: they can be set against the grant's own size); asinh(net assets) and log(1+employees) secondary. Where
the two scales disagree in sign, both are reported with the spread of firm-level results (median, share above controls).

**5.6 Headline and timing.** The effect at **t+3**, with its 95% interval, for each population, comparison and outcome; the
full path t−6…t+5 alongside. Anticipation variant **[after results]**: base year moved to t−3 (matching on t−5…t−3), allowing two
years of run-up before the grant; reported as "including any pre-grant run-up".

**5.7 Survival first, and its effect on the growth results [after results].** Survival effects are estimated before growth
(funded vs matched, open at t+3 and t+5). Because the growth comparison can only see firms still filing, two bounds are shown
beside every growth headline: (i) closed firms counted from their closure year at zero employees / zero net assets; (ii)
trimming bounds (Lee) that drop the excess survivors from the group that survives more.

**5.8 Grant size [after results].** Dose-response: effects by tercile of the award, and by tercile of the award per pre-grant
employee (firms with employees at t−1), terciles fixed within the matched sample; a rising pattern across terciles is evidence
against pure selection, a flat one is not.

**5.9 Smart grants: public-data replication [after results].** Treated = firms whose first grant is in a Smart competition,
cohorts 2019–2024 (Ipsos' window). The same designs on employees (log scale, to compare with Ipsos' +4.3% employment) and
net assets; set beside Ipsos' estimates with the differences in data and design named.

**5.10 Project descriptions [after results].** Software sorts each public project description by stated aim (hire staff;
launch a product or service; research or feasibility only); a person checks a random 200. Q1 effects by aim test the theory
of change's "stated aims → outcomes" link. No profiles or case studies beyond this.

**5.11 Inference and power.** 500 firm-level bootstrap draws (seed 1), funded firms resampled with their controls; 95%
percentile intervals. The minimum detectable effect is reported for every headline (2.8 × the bootstrap standard error: 80%
power at 5%), so a null reads "no effect larger than X". **[after results]** Both primary outcomes are always reported.

**5.12 How the comparisons are combined [after results].** No comparison is picked after the fact. Each headline is shown for
A–D with its Maryland level and its own placebo (the effect at the real t−1 when the grant date is moved two years earlier).
The conclusion weighs them: the more an effect is matched by a pre-grant gap of the same size, the less it is credited to the
grant; where the comparisons disagree, the disagreement is reported and the claim narrowed to what they share. Wording follows
the evidence: "shown", "suggested", or "not established".

## 6. Robustness (all reported, whichever way they point)
Placebo grant date (t0 − 2); 1:1 matching; Covid-era cohorts (2020, 2021) left out; largest 1% of awards left out; single-award
firms only; firms matched at SIC-section level left out; sensitivity to an unmeasured difference (E-value for each headline).
Dropped from v1.0's list (§11): coarsened exact matching (1:1 matching already serves as the alternative) and Rosenbaum bounds
(the E-value covers the same question more readably).

## 7. Value for money [after results]
As ranges from the intervals, never single points: £ change in net assets per £1 of grant at t+3 (the grant's own money passes
into retained earnings, so a ratio near or below £1 is not growth); cost per additional employee-year where the employee effect is
established, otherwise "not estimable from these data". Left out and said so: R&D, new products, skills, spillovers to other firms,
benefits to customers. Not comparable with Ipsos' £1.27 benefit-cost ratio (productivity measure, Smart only), and said so.

## 8. What this study cannot tell us (said where it bites)
Unobserved differences (ambition, management) may remain after matching — the placebo measures how much. Abridged accounts rule
out turnover and profit for most firms. Firm-level only: no spillovers or economy-wide effects. Without declined applicants
(unless released), the comparison is weaker than the one UKRI's own Smart evaluation could use.

## 9. Software, independence and review [after results]
Which steps software did (reading filings, matching, estimation, drafting) and which a person checked are listed in an appendix,
per the Magenta Book 2026 guidance on AI use in evaluation. An external evaluator with no stake reads the method and the draft
before publication; their comments and our replies are published. Founder declarations of interest are on the first page.

## 10. Outputs
A two-page standalone summary first (what was evaluated → method with counts → findings → recommendations); findings by question,
each with a key-findings box and Maryland level; recommendations to named bodies (UKRI / Innovate UK, DSIT) with the trade-off;
a forward section (monitoring data, access to declined applicants, linking to ONS data); appendices: question-to-method matrix,
balance tables, every figure traced to its filing; analysis code and derived non-personal data released. Length: summary 2 pages,
main report ~10–12k words, then appendices. [v2.3, after results] Every number in the report names its
source (results line, reference, calculation or definition); the theory of change drawn as a figure; each recommendation names
its first step and the objection it answers, and one tests a change to how the programme runs; a field-by-field data note for
UKRI. The main text came to ~13.3k words, above the ~10–12k set here, for the exploratory tests and the evidence abroad.

## 11. Change log
- v0.1–v0.5 (11 Oct 2026), before any outcome analysis: first draft; data checks split the employee outcome (disclosed from 2016);
  tag mapping; comparison pool from pre-grant filers (survivor bias); estimator fixed on simulation; own-year filing rule;
  populations fixed from panel counts. (Original matching intent — same size band, incorporation ±3 years — superseded by §5.4.)
- v1.0 (12 Oct 11:52 UTC), before any funded-vs-comparison outcome: analysis rules fixed (strata, eligibility, scales, t+3
  headline, grant-money caveat, inference). Not made public first.
- After v1.0's results: the placebo failed for both primary designs (funded firms already pulling ahead before the grant:
  employees +1.6, net assets +£57k, intervals clear of zero).
- v1.1 (11:59 UTC): later-winners comparison (C) added.
- v1.2 (12:17 UTC): review against the reporting standard: theory-of-change map, dose-response, anticipation, minimum detectable effect,
  value for money, project-description test, software disclosure, external review, FOI request.
- v1.3 (12:29 UTC): second review (complete but lean): existing evidence, Maryland grading, one combining rule, resilience question;
  turnover, total assets less current liabilities, the employees trend-adjusted design and sector/region cuts to appendices;
  coarsened exact matching and Rosenbaum bounds dropped (E-value kept).
- v2.0 (time in the lock file): the buyer's own evidence read in full (Ipsos Smart 2026, Frontier 2017, ERC 2018, ICURe): Smart public-data replication
  (§5.9); survival estimated first with bounds on the growth results (§5.7); survival dating rule; FOI asks for score bands;
  the whole plan rewritten as one document, every post-results item marked.
- v2.1 (time in the lock file) — AFTER v2.0 RESULTS, a definition corrected: survival counts only firms still open at the end
  of the grant year, funded and matched alike (a funded firm must exist to receive its grant; a control need not — immortal-time
  bias). The v2.0 figure is shown beside it. Added: the placebo test within each award third (§5.8), because a rising
  dose-response only argues against selection if the pre-grant gap does not rise with it.
- v2.2 (time in the lock file) — AFTER v2.1 RESULTS: §5.10 (project descriptions by stated aim) dropped under the lean rule:
  only 3% of funded firms' descriptions mention hiring, 11% launching, 14% feasibility; most state no sortable aim, and product
  type already records the project's stage (Q3). Floor item 11 (mixed methods) is therefore not met by this desk study and is
  said so in §8; interviews would come only through an associate. Q2 and Q3 run on the same designs as Q1: cash and the share of
  firms with negative net assets (designs A and B, each with its placebo); effects by the first project's product type (with placebo).
- v2.3 (time in the lock file) — AFTER v2.2 RESULTS. Nothing planned before was changed or dropped; everything below is new,
  added after results were seen, and is EXPLORATORY: it is reported in its own appendix (N), never as a plan result, and it
  shapes the reading of the plan's results only where the report says so.
  (a) Survival mechanism (Q2): the survival gap by first-year grant third, by negative net assets and by cash third a year before
      the grant, and year by year to t+5 (study/survival_mechanism.py, RESULTS-mechanism).
  (b) When the pre-grant gap opened (Q1): the placebo split into t−2 and t−1, to test whether the run-up is hiring in hope of a
      grant (study/anticipation_check.py, RESULTS-anticipation).
  (c) Who is funded, and where the first-year money goes (descriptive): funded firms against the 1-in-100 sample in the same
      calendar years, both groups filing for t−1; first-year money by the employee dose table's award thirds
      (study/who_and_money.py, RESULTS-profile). It prices Recommendation 6; it estimates no new effect.
  (d) Profit and capital (Q4): the accounts reader had dropped dimensional facts, retained earnings among them (lesson L48).
      Every funded filing was reread (identical apart from retained earnings, so no locked result moved); the comparison
      firms are being refetched, and the retained-earnings / capital-in split (study/profit_split.py) runs on the same
      designs A and B with placebos, reported with its coverage.
  (e) Reporting: the strongest designs abroad added to §2; every number sourced; Recommendation 6 and Appendix O (§10).

