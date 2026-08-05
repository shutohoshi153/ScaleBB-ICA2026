# §8 Financial Impact Demonstration

In this chapter, we show the practical meaning of the "repositioning as a scenario generator" from §7. We show it in numbers, as the sensitivity of the BEL (present value of benefits) in a simple projection model. The goal is not a precise valuation of liabilities. Instead, we show the direction and the size of the effect that changes in the long-term improvement rate $L$ have on the present value of benefits. We present this in a form that can be applied directly in an economic-value-based evaluation framework. Japan's economic-value-based solvency regulation (ESR) applies from fiscal year 2025, so its first valuation date is 31 March 2026, which is also the valuation date of this demonstration (§1.1, §2.3). Within the limits of a simple model, we made the calculation follow the ESR implementation rules as closely as possible (§8.1).

---

## 8.1 Design of the Demonstration — A Simple Model Aligned with the ESR Implementation Rules

The calculation engine is a simple projection model. It is deterministic and works in annual steps. For a model point issued in 2026 with entry age $x_0$, we value the present value of benefits as

$$
\mathrm{BEL}(x_0) \;=\; \sum_{t=0}^{T-1} P(t)\, S(t)\,
q_{\text{dis}}(x_0 + t,\; 2026 + t)\, \mathrm{SA}
\tag{8.1}
$$

$$
S(0) = 1, \qquad
S(t+1) \;=\; S(t)\,\bigl(1 - q_{\text{dis}} - q_{\text{death}} - q_{\text{lapse}}\bigr)
\tag{8.2}
$$

Here $q_{\text{dis}}$ is the sum of the scenario-specific claim rates for the 3 diseases (cancer, heart disease, and cerebrovascular disease). $q_{\text{death}}$ is the projected all-cause mortality rate. It is fixed at the base scenario and shared by all scenarios, so that the sensitivity comes only from changes in the disease rates. $q_{\text{lapse}}$ is the lapse rate. $P(t)$ is the discount factor for term $t$, and $\mathrm{SA}$ is the sum assured. We take the rate for each age and each year from the cohort diagonal $m(x_0 + t,\, 2026 + t)$ of the rate surface $m(x, y)$ that the framework in §3 outputs.

The calculation follows the ESR implementation rules on the next 4 points.

1. Position of the BEL. Equation (8.1) corresponds to the "current estimate" part of insurance liabilities in the ESR. The current estimate is the present value of future cash flows, with the assumptions re-evaluated at the valuation date. In §8.5 we make a simple calculation of the aggregation of sub-risks within life insurance risk and of the MOCE (uncertainty margin, Margin Over Current Estimate). Aggregation across risk categories (with market, credit, operational risk, and so on), eligible capital, and the ESR ratio itself are outside the scope of this demonstration, because it has no asset side.
2. Discount rate. For the discount factor $P(t)$, we use a risk-free interest rate curve rebuilt by Smith-Wilson extrapolation. We use the parameters of the "yield curve creation tool" published by the FSA, as of the end of March 2026 (the 31 March 2026 version). These are: the last observed maturity for yen interest rates, 30 years; the ultimate forward rate (UFR: Ultimate Forward Rate), 3.8%; the convergence maturity, 60 years; and the zero-coupon risk-free rates by maturity (13 observed maturities). The UFR of 3.8% for the yen, and the expected inflation rate of 2.0% embedded in it, are the values stated in the notice's Q&A. The curve matches the observed maturities exactly. The instantaneous forward rate at the convergence maturity is within ±1bp of the UFR. We do not apply spread adjustments such as the general bucket.
3. How we measure the sensitivity. In the ESR, life insurance risk is calculated by a "stress method". This method measures the change in net assets when set stresses are applied to economic-value-based assets and liabilities. The sensitivity $\Delta \mathrm{BEL}$ in this demonstration has the same form. If the asset side does not change, it corresponds directly to the fall in net assets under the stress method.
4. Use of the regulatory stress factors. For some scenarios (ESR_M and the level part of ICS_C in §8.2), we use the exact stress factors set by the Pillar 1 regulatory notice (defined in §7.2; the March 2026 amendment leaves the provisions cited here unchanged). These are: incidence rate +20% for morbidity and disability risk (Articles 59 and 60: product class that pays a lump sum when a health event occurs, Japan), and mortality rate +12.5% for mortality risk (Article 56: Japan). We apply them in the manner the notice's Q&A prescribes — a uniform multiplication of the rate assumption at every age over the whole projection period, in the risk groups where the increase reduces net assets (§7.2). The model point of this demonstration pays a lump sum on first diagnosis of one of the three major diseases, which the Q&A places in the lump-sum-on-a-health-event class alongside cancer diagnosis benefits.

<!-- TODO(著者確認): 上記の商品区分について。Q&A 第59条―Q1 は第2号を「事故・災害、重症疾患、
     永久身体障害に係る給付であり、請求時に一時金で支払われるもの。例えば災害死亡給付金、
     がん診断給付金、後遺障害保険金」としており、本稿のモデルポイント（三大疾病診断一時金）
     はこれに該当すると考えられる。
     なお旧稿にあった「保険期間5年超」という修飾は削除した。Q&A によれば5年の境界は
     第3号（短期的定期給付）と第4号（長期的定期給付）の区別に係るものであり、
     一時金区分（第2号）の要件ではない可能性が高い。告示第60条のストレス係数表で
     保険期間による区分があるかを一次資料で確認し、+20% の適用根拠を確定させること。 -->

At the same time, we state the limits of the simple model clearly. The cash flows include benefits only. Premiums and expenses are not included (the valuation is a present value of benefits). We treat decrements with an independence approximation. The all-cause mortality rate includes deaths caused by the 3 diseases. This effect on the sensitivity is second-order, because the rate is shared by all scenarios. Also, as stated in §3.1.3, the rates are cause-specific mortality rates. They are a proxy for the incidence rates of medical insurance. Re-running the demonstration on a practical projection model that insurance companies already use is a task for future validation (§10).

## 8.2 Scenarios and Model Points

There are 6 scenarios, listed below. All of them share the same fit (Phase 1) from §3.2. UP50/DN50/ICS_T only replace the setting $L$ and re-run the Phase 2 projection. ICS_C and ESR_M are generated only by a uniform multiplication of the rates.

| SCN_CD | Content | How it is generated | Regulatory meaning |
|---|---|---|---|
| BASE | Base ($L = 1.0\%$) | Default settings | Base scenario for the current estimate |
| UP50 | Faster improvement ($L = 1.5\%$) | Replace $L$ | IFRS 17 sensitivity disclosure +50bp |
| DN50 | Slower improvement ($L = 0.5\%$) | Replace $L$ | IFRS 17 sensitivity disclosure −50bp |
| ICS_T | Improvement stops ($L = 0\%$) | Replace $L$ | Trend shock (zero improvement rate) |
| ICS_C | Improvement stops + level | ICS_T × 1.125 | Combination of trend and mortality level shocks (+12.5% is the same level as the mortality risk factor in Article 56 of the notice) |
| ESR_M | Morbidity stress | BASE × 1.20 | Articles 59 and 60 of the notice, morbidity and disability risk (lump-sum class, long term, Japan: incidence rate +20%) |

The model points cover a product that pays a lump sum of 1 million yen for the three major diseases (at first diagnosis), with coverage to age 90. We place it at 8 points: entry ages 30/40/50/60 × male and female (MP01–MP04 male, MP05–MP08 female). The lapse rate is fixed at 3% per year. Death exits follow the projected all-cause rate. Both are shared by all scenarios.

The scenario table matches the two layers of applicability in §3.1.3 in the following way. The same rate table can be read in two ways. (i) If we read it as a proxy for the disease incidence rates of medical insurance, it falls under morbidity and disability risk (ESR_M). (ii) If we read it as an assumption for death benefits contingent on specific diseases, it falls under mortality risk (+12.5%, the same level as the level part of ICS_C). In other words, the single table of this demonstration maps to a regulatory stress under either of the two readings.

## 8.3 Results — One Table of BEL Sensitivities

Table 8.1 shows, for each model point, the BASE-scenario BEL (in yen, per 1 million yen of sum assured) and the change rate of each scenario compared with BASE.

Table 8.1: BEL sensitivity by model point (change rate vs BASE, %)

| MP | Entry age and sex | BASE BEL (yen) | UP50 | DN50 | ICS_T | ICS_C | ESR_M |
|---|---|---:|---:|---:|---:|---:|---:|
| MP01 | 30 M | 14,420 | −12.6 | +14.5 | +31.0 | +45.3 | +18.3 |
| MP02 | 40 M | 29,094 | −9.5 | +10.5 | +22.2 | +35.5 | +18.1 |
| MP03 | 50 M | 56,215 | −6.7 | +7.3 | +15.1 | +27.5 | +17.7 |
| MP04 | 60 M | 100,454 | −4.4 | +4.6 | +9.5 | +21.1 | +17.2 |
| MP05 | 30 F | 9,681 | −12.5 | +14.7 | +31.8 | +47.1 | +19.1 |
| MP06 | 40 F | 19,221 | −9.7 | +10.9 | +23.3 | +37.6 | +18.9 |
| MP07 | 50 F | 36,139 | −7.2 | +7.9 | +16.5 | +29.9 | +18.7 |
| MP08 | 60 F | 62,764 | −5.0 | +5.3 | +11.0 | +23.7 | +18.4 |
| Total | — | 327,988 | −6.6 | +7.2 | +15.0 | +27.7 | +18.0 |

![](figures/fig_8_1_bel_sensitivity_bar.png)

Figure 8.1: BEL sensitivity by model point and scenario (change rate vs BASE, %). The horizontal axis shows the model points (entry age and sex, ordered by entry age). The series are the 5 scenarios UP50 / DN50 / ICS_T / ICS_C / ESR_M. (Generation script: `ScaleBB/Research/scripts/bel_demo/aggregate_bel_results.py`)

We can summarize the results in 3 points. First, the order UP50 < BASE < DN50 < ICS_T < ICS_C holds at every model point. The results are monotonic in $L$, so changes in $L$ translate into the present value of benefits in a consistent way. Second, the sensitivity has a clear age gradient. It is larger when the entry age is younger (under ICS_T, +31 to +32% at age 30 against +10 to +11% at age 60). A change in the improvement trend builds up like compound interest over the remaining term. So longer contracts feel a larger effect, which matches intuition. Third, for women the BASE level of the present value of benefits is lower than for men. However, their sensitivity in change-rate terms is slightly higher than men's in all scenarios.

## 8.4 Discussion — Trend Shock versus Level Shock

The most telling point in Table 8.1 is the contrast between ESR_M and ICS_T. The effect of morbidity and disability risk under the stress method of the notice (ESR_M: a uniform level shock of +20% on incidence rates) is almost constant across entry ages (+17.2 to +19.1%). This is a natural result of the structure of current practice (§2.3), which multiplies a static rate table by a uniform factor. In contrast, the effect of the trend shock (ICS_T: zero improvement rate) has an age gradient from +9.5% to +31.8%. In total, it is close to the regulatory level shock (+15.0% versus +18.0%). But at age 30 it is about 1.7 times the regulatory level shock, and at age 60 it is a little under 60% of it.

This contrast has 2 practical implications. First, the uncertainty of the improvement trend concentrates in young, long-term contracts. If we capture risk only with a uniform level factor, we may systematically under-estimate (or over-estimate) trend risk, depending on the age mix of the portfolio. Second, a shock with this time structure can only be generated by a framework that outputs the improvement rate $i^*(x, y)$ explicitly (the limit of the baseline methods in §7.3). In our framework, we can generate it just by replacing $L$. Moreover, as §6 showed, the backtest has validated its direction in advance. The standard method in Pillar 1 of the regulation is based on level shocks. Our framework can therefore be applied as it is, with no extra changes, to run trend scenarios as a complement in ORSA, sensitivity disclosure, and internal management (Pillar 2).

Also, the level part of ICS_C (×1.125) is the same level as the mortality risk factor in Article 56 of the notice (Japan +12.5%). So for death benefits contingent on specific diseases (Novelty B, the layer of direct application), ICS_C keeps a direct regulatory reading as "a combination of a trend shock and the regulatory mortality stress". For medical insurance (the layer of proxy application to incidence rates), ESR_M is the matching scenario. Under either of the two readings, the sensitivities of this demonstration can be interpreted in the vocabulary of regulatory stresses.

We discuss the adoption burden in §9.2.

## 8.5 Extension — Simple Calculation of Life Insurance Risk Capital and Insurance Liabilities

The sensitivities up to the previous section were $\Delta \mathrm{BEL}$ for individual stresses. In this section, we go one step further into the standard method of the Pillar 1 notice. We calculate the 5 sub-risks of life insurance risk for this portfolio, using the stress factors of the notice (all with the geographic class Japan). We then continue to correlation aggregation (Article 81) and the MOCE (Article 29), and show the results.

Table 8.2: Simple calculation of life insurance risk capital and insurance liabilities (total of the 8 model points, yen)

| Item | Amount (yen) | Applied provision of the notice |
|---|---:|---|
| Sub-risk: mortality | 0 | Article 56 (mortality rate +12.5%. In this product, death works as an exit, so it does not reduce net assets, and the amount is 0) |
| Sub-risk: longevity | 11,698 | Article 57 (mortality rate −20% → more survivors, so the present value of benefits rises) |
| Sub-risk: morbidity and disability | 58,917 | Articles 59 and 60 (incidence rate +20%. By definition this equals the ΔBEL of ESR_M in Table 8.1) |
| Sub-risk: lapse | 50,096 | Articles 61 to 63 (the larger of a level-and-trend shock of ±25% and a mass lapse of 30%. For this product, the lapse-decrease side binds) |
| Sub-risk: expense | 0 | Article 64 (this demonstration has no expense cash flows) |
| Life insurance risk (after correlation aggregation) | 80,067 | Correlation matrix of Article 81 (diversification effect of −34% against the simple sum of 120,711) |
| Current estimate (total BASE BEL) | 327,988 | Equation (8.1) |
| MOCE | 32,286 | Articles 29 and 30 (cost-of-capital rate 3%, approximation of the run-off pattern of the estimated required capital. 9.8% of the current estimate) |
| Insurance liabilities (current estimate + MOCE) | 360,273 | — |

*Note: all amounts are rounded to the nearest yen, and each row is rounded independently from the underlying calculation. The insurance liability is therefore ¥1 less than the sum of the two rounded components shown above (the unrounded figures are 327,987.72 + 32,285.59 = 360,273.31). The diversification effect is likewise rounded: 80,066.70 against a simple sum of 120,711.07 is −33.7%.*

This calculation has 3 implications. First, the largest component of life insurance risk for this product (morbidity benefits) is morbidity and disability risk. Its amount comes directly from the ESR_M scenario in Table 8.1. In other words, the rate-table output of our framework can be applied in the same form, not only to sensitivity analysis but also to the stress-method calculation of required capital. Second, mortality risk is 0 because, in this product, death works on the exit side (it reduces benefits). If we read the same rate table as death benefits contingent on specific diseases (Novelty B), the mortality stress of +12.5% applies directly to the claim rates (the level part of ICS_C). This contrast shows clearly the regulatory difference between the two layers of application. Third, the standard method of the regulation, on the required-capital side, consists only of static level stresses. The uncertainty of the improvement trend (the risk with an age gradient, shown in §8.4) does not appear as a prescribed stress in Pillar 1. But it would be wrong to conclude that the trend axis is a Pillar 2 and Pillar 3 matter only. As §2.3 sets out, the notice's Q&A contemplates the reflection of a forward-looking trend inside the current estimate itself, and requires the objectivity of that reflection to be secured against public data — and it asks that the effect of the principal assumptions on the current estimate be understood through sensitivity analysis. So the framework has two homes in the regulation, not one. On the current-estimate side of Pillar 1, it supplies a trend whose direction has been validated against the public statistics the Q&A points to. On the shock side, it supplies trend scenarios as a complement in ORSA and internal management (Pillar 2) and in sensitivity disclosure (Pillar 3). §9 discusses the implementation of both.

Note that the calculation in this section is an illustration. It applies the standard method to a simple portfolio with a single product and benefit cash flows only. It does not include the setting of homogeneous risk groups, expense and premium cash flows, or aggregation across risk categories, which a real required-capital calculation needs.

---

*The demonstration in this chapter showed one thing. The explicit output of improvement rates, whose direction was validated in advance (§6–§7), translates into concrete sensitivity numbers on the implementation rules of the first year of ESR application. In the next chapter, §9, we discuss the calibration guidance and the adoption burden for introducing this into practice.*
