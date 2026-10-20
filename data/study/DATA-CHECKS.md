# Study data checks

Quality and coverage only. No funded-vs-comparison outcomes have been computed (that waits for the final, dated protocol).

## Grants file (UKRI, 2016/17 onwards, participants with a company number)

- Participant rows: **39,175**; companies: **15,782**; companies with more than one award: **5,701** (36%) — first award defines t0.
- Award offered: median £76,215; total £13.23bn; rows with zero or no award: 4,186 (excluded from 'treated').
- Award above the project's total costs: 1 rows (checked by hand before use).
- Withdrawn participants: 88 (treated as not treated; sensitivity check both ways).
- Enterprise size: Micro/Small: 19,411, Large: 5,195, Academic: 4,707, Medium: 2,627, Micro: 2,182, Small: 1,725, RTO: 989, Catapult: 890, PSO: 628, : 328, PSRE: 147, Unknown: 135, Industrial: SME: 107, Micro or small: 45, Charity: 29, Micro/ Small: 16, Industrial: Large: 6, Non UK: 4, SME: 2, v: 1, Business: 1

## Filed accounts fetched so far (Companies House bulk iXBRL)

- Months fetched: **153** (2014-01 to 2026-09); filings: **85,521**; unreadable: 88 (0.10%).
- Grant firms with at least one filing so far: **12,888 of 15,782** (82%; rises as months complete).
- Firm-years with more than one filing (amended or restated accounts): 853 — rule: keep the latest-filed.
- Share of filings carrying each figure: employees: 76%; NetAssetsLiabilities: 73%; TotalAssetsLessCurrentLiabilities: 88%; CashBankOnHand: 57%; TurnoverRevenue: 4%; ProfitLoss: 8%; Equity: 77%
- Employees: 65,772 values; outside 0–200,000: 206; fractional (0–1, i.e. part-time director only): 1,797.
- Net assets: 62,869 values; negative (liabilities exceed assets): 15,296 (24%); above £50bn in absolute value (scale error suspects): 0.
- Net assets ≠ equity on the same date (should match on a balance sheet): 1,299 facts — checked by hand; the larger of the two tags is not picked silently.

## Outcome coverage by year of accounts (share of filings; old and new tag names mapped)

| Year | Filings | Unread/empty | employees | net assets | total assets less current liabilities | cash | current assets | fixed assets | creditors within one year | turnover | profit after tax |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2013 | 1,324 | 0.0% | 0% | 100% | 87% | 93% | 88% | 79% | 89% | 2% | 2% |
| 2014 | 2,624 | 0.0% | 0% | 100% | 86% | 89% | 88% | 81% | 89% | 1% | 2% |
| 2015 | 3,225 | 1.7% | 0% | 97% | 84% | 86% | 87% | 79% | 89% | 2% | 2% |
| 2016 | 3,933 | 0.1% | 10% | 98% | 85% | 81% | 88% | 79% | 72% | 2% | 4% |
| 2017 | 4,804 | 0.1% | 42% | 98% | 85% | 66% | 89% | 80% | 13% | 3% | 8% |
| 2018 | 5,799 | 0.1% | 46% | 99% | 87% | 66% | 91% | 81% | 5% | 4% | 8% |
| 2019 | 6,967 | 0.0% | 64% | 99% | 87% | 66% | 92% | 81% | 5% | 5% | 9% |
| 2020 | 8,053 | 0.0% | 95% | 99% | 89% | 67% | 93% | 82% | 6% | 5% | 10% |
| 2021 | 8,936 | 0.0% | 97% | 99% | 89% | 66% | 93% | 82% | 6% | 5% | 10% |
| 2022 | 9,268 | 0.0% | 98% | 99% | 88% | 66% | 93% | 82% | 7% | 5% | 10% |
| 2023 | 9,954 | 0.0% | 98% | 99% | 88% | 66% | 94% | 83% | 8% | 4% | 11% |
| 2024 | 10,089 | 0.1% | 99% | 99% | 88% | 65% | 94% | 84% | 9% | 5% | 11% |
| 2025 | 9,458 | 0.3% | 99% | 99% | 89% | 63% | 94% | 84% | 10% | 5% | 11% |
| 2026 | 1,082 | 0.4% | 99% | 99% | 88% | 61% | 95% | 81% | 15% | 3% | 7% |

Employees are largely missing before 2016 because small companies were not required to disclose them for earlier accounting periods. This is a feature of the record, not a reading fault.

## Cross-filing consistency (own-year figure vs the next filing's comparative)

- net assets: 68,939 firm-years seen both ways; agree 92.1%; 5,465 disagree (restatements or tagging faults; own-year figure used). Comparative-only years used to fill gaps: 9,274.
- employees: 48,651 firm-years seen both ways; agree 93.9%; 2,962 disagree (restatements or tagging faults; own-year figure used). Comparative-only years used to fill gaps: 8,454.

