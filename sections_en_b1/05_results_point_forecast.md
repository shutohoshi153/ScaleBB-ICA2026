# §5 Results I — Point-Forecast Accuracy

This chapter reports the point forecast accuracy results based on the 3-cutoff design of §4. We state the conclusion first. Scale BB-D performs worse than the best baseline in MAPE (Equation 3.9) at every cutoff and in every cell. Within the original goal (testing the usefulness of Scale BB-D for point forecasts), this result leads to a negative conclusion: "Scale BB-D is not suitable for short-term point forecasts." This chapter reports this result openly and directly. It also quantifies how accuracy changes when COVID-19 is included in the training data or not. This is a by-product with independent value. All numbers below match the regenerated results in the reproduction package `reproduction/backtest/output/` (sex = total).

---

## 5.1 Point forecast accuracy of Scale BB-D alone ($y_c = 2014$)

We cut off the observations at 2014 and forecast the 10 years from 2015 to 2024. Table 5.1 shows the accuracy of Scale BB-D alone.

Table 5.1: Point forecast accuracy of Scale BB-D at $y_c = 2014$ (sex = total)

| Disease | MAPE [%] | bias [per $10^5$] | MAPE 2015 (1 year ahead) | MAPE 2024 (10 years ahead) |
|---|---:|---:|---:|---:|
| `cancer` | 22.41 | +42.6 | 11.96 | 30.95 |
| `total` | 26.01 | −496.2 | 10.99 | 41.54 |
| `heart_disease` | 31.27 | −85.3 | 11.12 | 48.52 |
| `diabetes` | 35.59 | −3.9 | 10.48 | 55.75 |
| `kidney` | 40.87 | −5.1 | 13.46 | 59.39 |
| `cerebrovascular` | 47.14 | −59.1 | 22.77 | 64.03 |
| `liver` | 49.49 | −7.8 | 20.53 | 67.50 |
| `hypertensive` | 73.83 | −7.1 | 37.02 | 88.33 |

There are three main observations.

1. The error grows as the forecast horizon gets longer. One year ahead (2015), the MAPE is 10.5–37.0%. This is an acceptable level for short-term forecasts in practice. But 10 years ahead (2024), it grows to 31.0–88.3%. Scale BB-D is a structural model. It respects the long-term trend, not the local level near the end of the observations. So when the horizon gets longer, the error from trend extrapolation builds up.

2. All diseases except `cancer` show a negative bias (the forecast is too low). A negative bias means forecast < actual. In other words, Scale BB-D extrapolated the continued improvement too far. It could not capture the excess mortality caused by COVID-19 in 2020–2022. This shows exactly the design hypothesis of §4.2: trend-extrapolation models are weak against structural breaks.

3. Only `cancer` shows a positive bias (the forecast is too high). The reason is that real progress in treatment was faster than the slow past decline. So the improvement in Scale BB-D was too small compared with the actual results.

These three points match Table 5.1 and Figures 5.1–5.3.

![](figures/fig_5_1_overall_mape_bias_by_year.png)

Figure 5.1: Yearly MAPE (left) and mean relative bias (right) by disease ($y_c = 2014$, sex = total, ages 20–89). For all diseases, MAPE grows steadily as the forecast horizon gets longer (Observation 1). The relative bias moves deeper into negative values for all diseases except `cancer` (Observation 2). (Reproduction: `reproduction/backtest/output/figures/overall_mape_bias_by_year.png`)

![](figures/fig_5_2_heart_disease_total_trajectory.png)

Figure 5.2: Heart disease (sex = total, three example ages): observed rates, Phase 1 smoothed rates, the Scale BB-D projection ($y_c = 2014$), and the actual rates 2015–2024. Scale BB-D (green dashed line) extrapolates the improvement trend of the training period as it is. So it stays systematically below the actual rates (red ×), which include the excess mortality of the COVID-19 period — a typical example of the negative bias in Observation 2. (Reproduction: `reproduction/backtest/output/figures/heart_disease_total_trajectory.png`)

![](figures/fig_5_3_cancer_total_trajectory.png)

Figure 5.3: The same trajectory for cancer (malignant neoplasms) (sex = total, three example ages). For `cancer`, the actual rates fall faster than the Scale BB-D projection, so the projection is above the actual rates (the positive bias in Observation 3). (Reproduction: `reproduction/backtest/output/figures/cancer_total_trajectory.png`)

## 5.2 Baseline comparison ($y_c = 2014$) — worse in all 24 cells

We compare Scale BB-D with the 3 baselines (§3.4.1) under the same settings.

Table 5.2: Scale BB-D versus the 3 baselines, MAPE [%] at $y_c = 2014$ (sex = total)

| Disease | scalebb | naive_last | mean_3pts | loglin_trend | Best baseline | Gap to best [pp] |
|---|---:|---:|---:|---:|---|---:|
| `cancer` | 22.41 | 12.78 | 14.92 | 5.86 | loglin_trend | +16.55 |
| `total` | 26.01 | 8.73 | 12.79 | 5.74 | loglin_trend | +20.27 |
| `heart_disease` | 31.27 | 14.91 | 18.29 | 8.28 | loglin_trend | +22.99 |
| `diabetes` | 35.59 | 21.36 | 20.50 | 19.23 | loglin_trend | +16.36 |
| `kidney` | 40.87 | 14.52 | 13.10 | 14.63 | mean_3pts | +27.77 |
| `cerebrovascular` | 47.14 | 18.52 | 26.81 | 12.27 | loglin_trend | +34.87 |
| `liver` | 49.49 | 10.44 | 10.17 | 17.51 | mean_3pts | +39.32 |
| `hypertensive` | 73.83 | 39.29 | 30.33 | 35.88 | mean_3pts | +43.50 |

A note on granularity before we read the table. Two different units appear in this paper and they must not be confused. A **validation cell** (§3.4.2, §4.3) is one age group × one validation year within a disease × sex; this is the unit on which MAPE and DA are computed. A **disease × sex cell** is the aggregate of all validation cells belonging to one disease and one sex, over the whole validation window — at $y_c = 2014$, the 10-year aggregate MAPE of 2015–2024. There are 24 of the latter (8 diseases × 3 sexes), and it is these 24 that the phrase "all 24 cells" refers to here and in §6. On this definition, Scale BB-D performs worse than all 3 baselines in all 24 disease × sex cells. Look at the gap to the best baseline. For diseases with a clear improvement trend (`cancer` / `total` / `heart_disease`), the gap to loglin_trend is +16 to +23pp. For diseases with an unclear trend (`liver` / `hypertensive`), the gap to mean_3pts is +39 to +44pp. Figure 5.4 shows the size of this gap. At the finer granularity of a single validation year, there is one exception for sex = total: in 2015 alone, `diabetes` beats all 3 baselines. This does not change the result at the disease × sex level, because the 10-year aggregate for `diabetes` remains +16.36pp behind the best baseline.

![](figures/fig_5_4_scalebb_gap_vs_best_baseline.png)

Figure 5.4: Gap of Scale BB-D MAPE − best baseline MAPE [pp] (positive = Scale BB-D performs worse, sex = total). At $y_c = 2014$ (red), Scale BB-D is worse by +16 to +44pp for all diseases. At $y_c = 2021/2022$ (orange / green), the gap shrinks, but the sign stays positive (§5.3). (Reproduction: `reproduction/backtest/output/cutoff_comparison/figures/scalebb_gap_vs_best_baseline.png`)

## 5.3 When the COVID-19 period is included in training ($y_c = 2021 / 2022$)

When we move the training cutoff to 2021 / 2022 and include the pandemic period in training, the MAPE of Scale BB-D shrinks dramatically.

Table 5.3: Scale BB-D MAPE [%] by training cutoff (sex = total)

| Disease | $y_c{=}2014$ | $y_c{=}2021$ | $y_c{=}2022$ |
|---|---:|---:|---:|
| `cancer` | 22.41 | 9.20 | 8.87 |
| `cerebrovascular` | 47.14 | 15.07 | 15.52 |
| `diabetes` | 35.59 | 16.02 | 13.29 |
| `heart_disease` | 31.27 | 10.27 | 8.37 |
| `hypertensive` | 73.83 | 24.13 | 20.53 |
| `kidney` | 40.87 | 16.69 | 15.59 |
| `liver` | 49.49 | 29.17 | 29.52 |
| `total` | 26.01 | 9.33 | 7.33 |

MAPE shrinks for all 8 diseases, in some cases by a factor of 6 to 8 (for example: `hypertensive` 73.83 → 24.13, `total` 26.01 → 9.33). At the same time, the absolute value of the bias also shrinks for all diseases. For `liver` at $y_c{=}2021$ (−7.8 → +0.1 per $10^5$) and for `hypertensive` at $y_c{=}2022$ (−7.1 → +0.4), the sign turns from negative to positive. This shows the quantitative value of putting a structural break into the training data. As a measurement of the effect of COVID-19 on cause-specific mortality, it has meaning that is independent of the weak point forecasts (Figure 5.5).

![](figures/fig_5_5_scalebb_cutoff_comparison.png)

Figure 5.5: Scale BB-D MAPE by training cutoff (sex = total). When the pandemic period is included in training — $y_c = 2021$ (orange) and $y_c = 2022$ (green) — MAPE shrinks strongly for all diseases compared with $y_c = 2014$ (red). Note, however, that the forecast horizon also becomes shorter at the same time (10 years vs 2–3 years) (§4.2). (Reproduction: `reproduction/backtest/output/cutoff_comparison/figures/scalebb_cutoff_comparison.png`)

However, a smaller MAPE does not mean "catching up with the baselines." The gap to the best baseline (Figure 5.4) shrinks from +16 to +44pp at $y_c{=}2014$ to +1 to +24pp at $y_c{=}2021/2022$. But for sex = total, Scale BB-D is still worse than the best baseline at every cutoff and for every disease. Count the cells where Scale BB-D beats "at least one baseline": only 0 / 10 / 7 of the 24 cells at each cutoff. (It beats all baselines in only 2 cells each at $y_c{=}2021/2022$.) With more training data, Scale BB-D reaches a level where it can compete with either naive_last or loglin_trend. For example, `kidney` at $y_c{=}2021$ beats naive_last (19.85) and mean_3pts (17.36), but it misses the best method, loglin_trend (15.69), by +1.00pp. It does not reach the best method.

## 5.4 Summary — a negative conclusion and the turn to the next chapter

The validation results on point forecast accuracy are clear.

- Short horizon ($y_c = 2021 / 2022$; 2–3 years ahead, with the pandemic period in training): the aggregate MAPE of Scale BB-D is 7–30%. This is an acceptable level in practice, but it is still worse than the baselines.
- Long horizon ($y_c = 2014$; 10 years ahead, with the pandemic unknown to the model): the 10-year aggregate MAPE is 22–74%. Within that window the error grows from 10.5–37.0% one year ahead (2015) to 31.0–88.3% ten years ahead (2024), and the gap to the baselines is at its largest.
- At every cutoff, Scale BB-D fails to reach the best baseline in MAPE in all 24 disease × sex cells. At $y_c = 2021 / 2022$ it does overtake at least one baseline in 10 / 7 of the 24 (all three baselines in 2 of them each), but never the best one (§5.3).

If the original goal was "point forecast accuracy," the conclusion of this chapter is a negative one: "Scale BB-D is not suitable for short-term point forecasts. naive_last, which carries the latest level forward, and the log-linear extrapolation loglin_trend are more accurate." This result also fits the original design idea of Scale BB-D. It is a model that extracts long-term improvement trends over several decades. It is not a tool for hitting next year's level with the smallest error.

But if we judge Scale BB-D on the single axis of point forecast accuracy, we may miss the essential output of this structural model — the improvement rates $i^*(x, y)$ with a guaranteed direction. In the next chapter, §6, we measure the directional accuracy DA (Equation 3.12), which the original goal did not measure. There the picture changes completely. The negative conclusion of this chapter turns from a "failure" into a "restatement of the question."

---

*§6 measures the same model output on a second axis: the direction of change.*
