# Estimator check on simulated firms (known answer)

Selection on size and growth, staggered cohorts 2017–2022, firm-specific trends, 12% missing filings, 20,000 firms per run, 40 runs per scenario. Matching: 5 nearest within sector, caliper 0.2 SD; matched within each grant cohort on its own three pre-grant years (levels and slope) plus firm age.

## Scenario A: true effect builds to +3.6 employees by year 5

Years −6 to −4 are before the matching window (placebo: should be ~0); −3 to −2 are matched on.

| Years after grant | True effect | Matched DiD estimate | covers truth | Trend-adjusted (trend from years before matching) | covers truth |
|---|---|---|---|---|---|
| -6 | +0.00 | -0.42 | 18% | +0.13 | 92% |
| -5 | +0.00 | -0.32 | 22% | +0.14 | 85% |
| -4 | +0.00 | -0.20 | 58% | +0.17 | 90% |
| -3 | +0.00 | +0.02 | 100% | +0.25 | 52% |
| -2 | +0.00 | +0.01 | 100% | +0.12 | 78% |
| 0 | +0.60 | +0.83 | 30% | +0.70 | 88% |
| 1 | +1.20 | +1.52 | 12% | +1.29 | 92% |
| 2 | +1.80 | +2.21 | 8% | +1.87 | 90% |
| 3 | +2.40 | +2.95 | 2% | +2.47 | 98% |
| 4 | +3.00 | +3.64 | 5% | +3.08 | 98% |
| 5 | +3.60 | +4.32 | 10% | +3.66 | 92% |

- Naive funded-vs-unfunded comparison at year 3: +3.08 (truth +2.40) — overstates by 0.68.
- Largest covariate imbalance after matching (standardised difference): mean 0.144 (target < 0.1).

## Scenario B: no effect at all

Years −6 to −4 are before the matching window (placebo: should be ~0); −3 to −2 are matched on.

| Years after grant | True effect | Matched DiD estimate | covers truth | Trend-adjusted (trend from years before matching) | covers truth |
|---|---|---|---|---|---|
| -6 | +0.00 | -0.40 | 25% | +0.11 | 90% |
| -5 | +0.00 | -0.30 | 28% | +0.09 | 90% |
| -4 | +0.00 | -0.19 | 48% | +0.11 | 82% |
| -3 | +0.00 | +0.02 | 100% | +0.21 | 70% |
| -2 | +0.00 | +0.01 | 100% | +0.11 | 75% |
| 0 | +0.00 | +0.20 | 30% | +0.10 | 78% |
| 1 | +0.00 | +0.30 | 12% | +0.11 | 88% |
| 2 | +0.00 | +0.38 | 10% | +0.08 | 95% |
| 3 | +0.00 | +0.48 | 5% | +0.08 | 85% |
| 4 | +0.00 | +0.60 | 8% | +0.12 | 95% |
| 5 | +0.00 | +0.69 | 10% | +0.07 | 95% |

- Naive funded-vs-unfunded comparison at year 3: +0.64 (truth +0.00) — overstates by 0.64.
- Largest covariate imbalance after matching (standardised difference): mean 0.150 (target < 0.1).

