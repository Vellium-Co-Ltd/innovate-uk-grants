# Innovate UK study — appendix analyses (v2.2; INTERNAL until published)

Plan v2.5 (locked 2026-10-13T18:35:55Z). Produced by `study/run_appendix.py`.

## The funded population (counts and money only)

- Funded business recipients (first project from April 2016, never funded 2004–16): **11,150**.
- Awards offered to them on projects starting April 2016 onwards: **£4.14bn** (median per firm £92,284; mean £371,034; largest £39.2m).
- Awards on projects starting in each firm's first grant year: median £65,744, mean £178,685.
- Firms with more than one grant year: 3,217 (29%).

| First project's product type | funded firms |
|---|---|
| Collaborative R&D | 6,153 |
| Feasibility Studies | 1,766 |
| Grant for R&D | 1,056 |
| Study | 417 |
| EU-Funded | 294 |
| BEIS-Funded Programmes | 269 |
| Small Business Research Initiative | 252 |
| Investment Accelerator | 221 |
| Fast Start Response | 190 |
| Responsive Strategy and Planning | 180 |
| CR&D Bilateral | 97 |
| Launchpad | 64 |
| Innovation Loans | 36 |
| Demonstrator | 35 |
| Legacy Department of Trade & Industry | 34 |
| SME Support | 28 |
| Knowledge Transfer Network | 17 |
| Business Connect | 17 |
| Department for Science, Innovation & Technology | 6 |
| Missions | 5 |
| Centres | 5 |
| Unknown | 5 |
| Procurement | 3 |

| Enterprise size (UKRI file) | funded firms |
|---|---|
| Micro/Small | 8,648 |
| Micro | 761 |
| Large | 683 |
| Medium | 648 |
| Small | 294 |
| Industrial: SME | 88 |
| Micro or small | 12 |
| Micro/ Small | 11 |
| Industrial: Large | 3 |
| SME | 2 |

| Region (UKRI file) | funded firms |
|---|---|
| London | 2,815 |
| South East | 1,621 |
| South West | 1,101 |
| East of England | 1,053 |
| North West | 852 |
| Scotland | 712 |
| West Midlands | 705 |
| Yorkshire and The Humber | 604 |
| East Midlands | 570 |
| Wales | 421 |
| North East | 382 |
| Northern Ireland | 297 |
| Outside UK | 15 |
| #N/A | 1 |
| Channel Islands | 1 |

| First grant year (t0) | funded firms |
|---|---|
| 2016 | 96 |
| 2017 | 770 |
| 2018 | 702 |
| 2019 | 734 |
| 2020 | 2,120 |
| 2021 | 933 |
| 2022 | 1,621 |
| 2023 | 1,808 |
| 2024 | 1,419 |
| 2025 | 692 |
| 2026 | 255 |

| Sector (SIC section) | funded firms |
|---|---|
| Information and communication | 3,115 |
| Professional, scientific and technical | 3,063 |
| Manufacturing | 2,093 |
| Wholesale and retail | 459 |
| Administrative services | 442 |
| Agriculture, forestry, fishing | 382 |
| Health and social work | 241 |
| Other services | 197 |
| Construction | 188 |
| Education | 158 |
| Transport | 150 |
| Arts and recreation | 133 |
| sector not recorded | 105 |
| Finance and insurance | 104 |
| Energy supply | 89 |
| Water and waste | 87 |
| Hospitality | 36 |
| Real estate | 32 |
| Mining | 31 |
| Extraterritorial organisations | 30 |
| Public administration | 14 |
| Households as employers | 1 |

## Q4 Turnover in the public record (coverage only)

- Funded firms filing turnover in any year t−1…t+3: **708 of 11,150 (6.3%)**; among firms UKRI records as large: 8% (686 firms); all other sizes 6.3%.
- Comparison pool firms that ever filed turnover: 5.3% of 71,515.
- Small companies may file abridged accounts without a profit and loss account, so most funded firms never put turnover on the public record. No turnover estimate is built (plan §1 Q4).

## Capacity measures — design B (trend-adjusted), with placebo

| Outcome | funded matched | t+3 effect (95%; firms) | placebo at real t−1 | minimum detectable effect |
|---|---|---|---|---|
| Fixed assets | 1,789 | £+88,220 (£+38,051 to £+137,500; 775) | £+48,876 (£+18,517 to £+77,052) | £71,035 |
| Total assets less current liabilities | 1,957 | £+125,379 (£+42,980 to £+205,687; 857) | £+69,070 (£+29,661 to £+110,886) | £116,219 |

## Grant money counted in the outcome's own window (definition corrected)

v2.0 used every award a firm was offered in the whole file, including projects that started after t+3. A firm that grows wins more and larger grants later, so that measure partly follows the outcome. Below: the dose is the first grant year's awards; value for money divides by awards on projects started t0…t+3, for the firms seen at t+3. v2.0 figures beside.

### net assets — B trend-adjusted: dose by first-year award (cuts £45,926 and £88,679)

| Third | t+3 effect (95%; firms) | placebo at real t−1 |
|---|---|---|
| lowest third | £+83,630 (£-28,647 to £+194,354; 248) | £+78,995 (£+22,472 to £+132,286; 483) |
| middle third | £+90,013 (£+1,636 to £+193,560; 370) | £+41,891 (£-1,424 to £+81,997; 469) |
| highest third | £-40,716 (£-153,934 to £+75,933; 420) | £+48,556 (£-35,859 to £+135,723; 380) |

**Value for money, net assets at t+3 per £1 of grant:**

| Grant counted | mean per firm | per £1 (95%) |
|---|---|---|
| v2.0: every award in the file, all matched firms | £196,427 | £0.18 (£-0.15 to £0.51) |
| every award in the file, firms seen at t+3 | £235,613 | £0.15 (£-0.13 to £0.43) |
| **projects started t0…t+3, firms seen at t+3** | £205,261 | **£0.17 (£-0.15 to £0.49)** |
(1,032 firms seen at t+3.)

### employees — A plain: dose by first-year award (cuts £48,477 and £99,410)

| Third | t+3 effect (95%; firms) | placebo at real t−1 |
|---|---|---|
| lowest third | +0.11 (-0.85 to +1.06; 389) | +1.26 (+0.61 to +1.94; 669) |
| middle third | +1.93 (+1.11 to +2.81; 504) | +1.01 (+0.37 to +1.64; 533) |
| highest third | +3.39 (+2.33 to +4.46; 529) | +2.64 (+1.87 to +3.48; 489) |

## By sector and region (descriptive; not tested one by one)

### Sector — net assets, B trend-adjusted

| Group | funded firms | matched | t+3 effect (95%; firms at t+3) | placebo at real t−1 |
|---|---|---|---|---|
| Information and communication | 3,115 | 610 | £-27,321 (£-126,071 to £+58,985; 271) | £+30,107 (£-31,007 to £+87,080) |
| Professional, scientific and technical | 3,063 | 613 | £+88,963 (£+28,770 to £+153,491; 299) | £+49,741 (£-1,182 to £+98,756) |
| Manufacturing | 2,093 | 406 | £+48,210 (£-120,832 to £+211,890; 213) | £+50,517 (£-23,632 to £+137,088) |
| Wholesale and retail | 459 | 111 | £-87,731 (£-366,467 to £+219,436; 45) | £+58,769 (£-23,615 to £+161,603) |
| Administrative services | 442 | 108 | £+22,898 (£-157,892 to £+204,056; 43) | £+161,069 (£+63,878 to £+271,254) |
| Agriculture, forestry, fishing | 382 | 163 | £+73,535 (£-190,743 to £+357,917; 28) | £+129,307 (£+30,773 to £+234,603) |
| Health and social work | 241 | 40 | £-7,296 (£-187,171 to £+184,084; 21) | £-74,395 (£-335,306 to £+113,927) |
| all other sectors | 1,355 | 216 | £+72,752 (£-99,363 to £+237,547; 88) | £+23,837 (£-59,217 to £+93,200) |

### Region — net assets, B trend-adjusted

| Group | funded firms | matched | t+3 effect (95%; firms at t+3) | placebo at real t−1 |
|---|---|---|---|---|
| London | 2,815 | 388 | £-53,674 (£-198,316 to £+82,764; 180) | £+69,435 (£-18,709 to £+163,785) |
| South East | 1,621 | 330 | £-4,479 (£-183,729 to £+169,659; 156) | £+14,124 (£-54,940 to £+79,583) |
| South West | 1,101 | 262 | £+227,683 (£+55,056 to £+399,909; 101) | £+72,065 (£+18,163 to £+136,702) |
| East of England | 1,053 | 199 | £+52,564 (£-98,556 to £+215,341; 90) | £+52,121 (£-11,843 to £+106,677) |
| North West | 852 | 176 | £+118,577 (£-72,126 to £+299,027; 78) | £+55,066 (£-29,983 to £+139,432) |
| Scotland | 712 | 139 | £-640 (£-105,998 to £+111,832; 84) | £+110,721 (£+12,599 to £+221,164) |
| West Midlands | 705 | 169 | £+23,100 (£-100,395 to £+143,617; 81) | £+40,476 (£-31,033 to £+116,437) |
| Yorkshire and The Humber | 604 | 145 | £-48,752 (£-189,855 to £+85,976; 57) | £+70,704 (£-29,873 to £+170,124) |
| East Midlands | 570 | 129 | £+186,691 (£-38,221 to £+422,397; 52) | £+129,183 (£+7,568 to £+285,934) |
| Wales | 421 | 87 | £-86,588 (£-389,601 to £+225,329; 27) | £+246,920 (£+58,907 to £+445,960) |
| North East | 382 | 86 | £+88,757 (£-227,196 to £+409,311; 25) | £+63,601 (£-56,366 to £+204,824) |
| Northern Ireland | 297 | 51 | £+39,541 (£-61,325 to £+168,527; 23) | £+85,360 (£-54,844 to £+262,668) |
| all other / not stated | 17 | 3 | £+0 (£+0 to £+0; 1) | £+5,702 (£+5,702 to £+5,702) |

### Sector — employees, A plain

| Group | funded firms | matched | t+3 effect (95%; firms at t+3) | placebo at real t−1 |
|---|---|---|---|---|
| Information and communication | 3,115 | 1,121 | +1.78 (+0.86 to +2.79; 451) | +1.59 (+1.05 to +2.07) |
| Professional, scientific and technical | 3,063 | 886 | +2.42 (+1.53 to +3.39; 349) | +1.23 (+0.58 to +1.84) |
| Manufacturing | 2,093 | 609 | +2.15 (+0.75 to +3.47; 288) | +1.81 (+1.12 to +2.58) |
| Wholesale and retail | 459 | 165 | +0.57 (-1.33 to +2.21; 63) | +1.34 (-0.12 to +2.74) |
| Administrative services | 442 | 156 | +2.42 (+0.33 to +4.74; 52) | +2.24 (+0.83 to +3.53) |
| Agriculture, forestry, fishing | 382 | 199 | +2.37 (-1.63 to +6.39; 42) | +0.55 (-0.91 to +2.06) |
| Health and social work | 241 | 71 | +0.64 (-3.13 to +3.84; 32) | +4.31 (-0.12 to +9.36) |
| all other sectors | 1,355 | 347 | +1.51 (-0.32 to +3.29; 120) | +1.45 (+0.42 to +2.50) |

### Region — employees, A plain

| Group | funded firms | matched | t+3 effect (95%; firms at t+3) | placebo at real t−1 |
|---|---|---|---|---|
| London | 2,815 | 778 | +2.00 (+0.86 to +3.14; 309) | +1.79 (+0.99 to +2.69) |
| South East | 1,621 | 485 | +2.92 (+1.68 to +4.24; 198) | +1.61 (+0.97 to +2.39) |
| South West | 1,101 | 378 | +1.93 (+0.68 to +3.29; 139) | +0.67 (+0.04 to +1.32) |
| East of England | 1,053 | 279 | +2.55 (+1.23 to +4.00; 109) | +1.02 (-0.03 to +1.95) |
| North West | 852 | 267 | +0.06 (-2.28 to +2.74; 103) | +1.12 (+0.30 to +1.90) |
| Scotland | 712 | 202 | +1.45 (+0.14 to +2.97; 102) | +1.37 (+0.21 to +2.76) |
| West Midlands | 705 | 216 | +1.95 (+0.65 to +3.76; 78) | +1.60 (+0.49 to +2.91) |
| Yorkshire and The Humber | 604 | 199 | +0.95 (-0.95 to +2.78; 67) | +1.56 (+0.07 to +3.00) |
| East Midlands | 570 | 180 | +2.25 (+0.01 to +4.67; 65) | +0.81 (-0.77 to +2.19) |
| Wales | 421 | 136 | +2.79 (+0.57 to +4.74; 45) | +1.12 (+0.43 to +1.96) |
| North East | 382 | 115 | +3.41 (+1.30 to +5.90; 32) | +0.29 (-1.21 to +1.94) |
| Northern Ireland | 297 | 79 | +0.83 (-2.76 to +3.88; 38) | +1.65 (-0.03 to +3.71) |
| all other / not stated | 17 | 5 | – (– to –; 0) | -0.25 (-0.50 to +0.00) |

