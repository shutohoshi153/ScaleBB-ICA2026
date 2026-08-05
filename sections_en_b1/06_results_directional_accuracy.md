# §6 Results II — The Directional Accuracy Finding

In this chapter we measure a second evaluation axis — directional accuracy DA (equations 3.11–3.12). The original validation plan (§4) did not measure it. We state the conclusion first. At $y_c = 2014$, the cutoff where the point forecast MAPE fell behind most (§5), the direction agreement rate for the six main diseases (all causes, cerebrovascular disease, heart disease, diabetes, cancer, kidney failure) reaches 77.7–95.0%. The model that lost every point forecast comparison captured the sign of the trend — improvement or worsening — almost correctly. This gap is the central finding of this paper. All numbers below match the regenerated results of the reproduction package `reproduction/backtest/output/directional/` (sex = total).

---

## 6.1 Directional accuracy at $y_c = 2014$ — 77.7–95.0% for the six main diseases

We show the directional accuracy by disease for $y_c = 2014$ (forecasting the 10 years 2015–2024). This is the cutoff where the MAPE gap was largest. DA is evaluated only on cells where an actual change occurred (equation 3.12). Therefore we also report the number of valid cells $n$ (§4.3).

Table 6.1: Directional accuracy of Scale BB-D by disease at $y_c = 2014$ (sex = total)

| Disease | $n$ (valid cells) | DA [%] |
|---|---:|---:|
| `total` | 140 | 95.00 |
| `cerebrovascular` | 134 | 91.04 |
| `heart_disease` | 137 | 90.51 |
| `diabetes` | 123 | 80.49 |
| `cancer` | 138 | 79.71 |
| `kidney` | 112 | 77.68 |
| `liver` | 118 | 27.97 |
| `hypertensive` | 110 | 23.64 |

When we place these results next to §5.1, the size of the gap stands out. For example, `cerebrovascular` had a MAPE of 47.14%. That was the third worst of the 8 diseases in point forecasts. Yet its direction agreement rate reaches 91.04%. `total` misses the level by 26% on average over the 10-year window. Still, it gets the direction of change right in 133 of 140 valid cells. In other words, the error of Scale BB-D is not an error of "wrong direction". It is an error of "going too far in the right direction" (over-extrapolating improvement). This is consistent with the dominance of negative bias observed in §5.1.

In contrast, two diseases miss the direction itself: `liver` (27.97%) and `hypertensive` (23.64%). Their mortality rates turned upward from the mid-2010s. However, the default setting ($L = +1\%$, continued improvement) kept producing projections in the improving direction. We treat this in detail in §6.5.

## 6.2 Across the 3 cutoffs — does the model capture direction regardless of the training period?

Table 6.2 and Figure 6.1 show the Scale BB-D directional accuracy when we vary the training cutoff in three ways.

Table 6.2: Directional accuracy [%] of Scale BB-D by disease and training cutoff (sex = total)

| Disease | $y_c{=}2014$ | $y_c{=}2021$ | $y_c{=}2022$ |
|---|---:|---:|---:|
| `total` | 95.00 | 42.86 | 60.71 |
| `cerebrovascular` | 91.04 | 69.23 | 51.85 |
| `heart_disease` | 90.51 | 50.00 | 52.00 |
| `diabetes` | 80.49 | 30.30 | 85.71 |
| `cancer` | 79.71 | 65.00 | 70.37 |
| `kidney` | 77.68 | 54.55 | 71.43 |
| `liver` | 27.97 | 45.95 | 52.00 |
| `hypertensive` | 23.64 | 68.97 | 85.00 |

![](figures/fig_6_1_scalebb_directional_per_cutoff.png)

Figure 6.1: Scale BB-D directional accuracy by training cutoff (sex = total). The dashed line is the chance level (a coin flip, 50%). At $y_c = 2014$ (red), the six diseases with continued improvement are far above the chance level, while `liver` / `hypertensive` are far below it. At $y_c = 2021/2022$ (orange, green) the pattern reverses, and `liver` / `hypertensive` recover (§6.5). (Reproduction: `reproduction/backtest/output/directional/figures/scalebb_directional_per_cutoff.png`)

Two points need care when reading Figure 6.1. First, $y_c = 2014$ is statistically the most stable. The number of valid cells is 110–140 at $y_c = 2014$. It is only 29–42 at $y_c = 2021$ and 20–28 at $y_c = 2022$ (§4.3). For cutoffs with a short validation period, the DA can move in steps of 10pp depending on the outcome of a few cells. Second, the lower values for short validation periods reflect the year-to-year swings just after COVID-19. For example, `total` at $y_c = 2021$ (42.86%) uses the excess mortality level of 2021 as the last observation. It then asks about the direction of the rebound in 2022–2024. This setting differs in nature from $y_c = 2014$, which asks about the sign of a trend over decades. The swing of `diabetes` from 30.30% ($y_c{=}2021$) to 85.71% ($y_c{=}2022$) shows the same short-term noise. The topic of this chapter is the direction of long-term trends. For that topic, the $y_c = 2014$ result — 77.7–95.0% for the diseases with continued improvement, with a 10-year validation period and 140 cells — is the most reliable estimate.

## 6.3 Baseline comparison — few methods carry direction information

We compare the DA of the four methods under the same definition. Over 24 comparisons (8 diseases × 3 cutoffs, sex = total), the win-loss record of Scale BB-D is as follows.

Table 6.3: Directional accuracy — win / tie / loss record of Scale BB-D against each baseline (24 comparisons, sex = total)

| Compared against | Scale BB-D wins | Ties | Losses |
|---|---:|---:|---:|
| vs `naive_last` | 24 | 0 | 0 |
| vs `mean_3pts` | 15 | 0 | 9 |
| vs `loglin_trend` | 12 | 5 | 7 |

`naive_last` has $\Delta_{\text{pred}} \equiv 0$ by construction (equation 3.11). It carries no direction information at all (DA = 0%). In §5 this method was among the strongest on MAPE. On the direction axis, it cannot even enter the contest. This is the clearest sign of the gap between MAPE and DA. The direction information of `mean_3pts` is accidental. It predicts a "change" equal to the gap between the mean of the last 3 points and the observed value in the cutoff year. So it scores high when the cutoff-year value happened to dip: 76.36% for `hypertensive` and 61.02% for `liver`, both in a rising phase. But it misses almost systematically for diseases with clear improvement (4.29% for `total`). This is not direction information based on trend structure.

The only meaningful rival is `loglin_trend`. It holds explicit direction information through its OLS slope. Scale BB-D wins on net, with 12 wins, 5 ties, and 7 losses. But the details have structure. At $y_c = 2014$, the two methods are exactly equal for `cerebrovascular` (91.04%) and `heart_disease` (90.51%). For `total` they are nearly equal: 95.00% vs 94.29%. For diseases with a clear improvement trend, the long-term structural model and log-linear extrapolation reach the same sign. The losses of Scale BB-D concentrate mainly in `cancer` (it falls behind at all 3 cutoffs; 79.71% vs 93.48% at $y_c{=}2014$) and in $y_c = 2022$, where the validation period is only 2 years. In contrast, at $y_c = 2021$ Scale BB-D is far ahead for `heart_disease` (50.00% vs 26.19%) and `total` (42.86% vs 16.67%). The 15-year OLS includes the COVID period, so the level shift pulls it off course and it misses the direction. Even in that phase, Scale BB-D sets the direction from decades of structure, and it degrades more gently (Figure 6.2).

![](figures/fig_6_2_scalebb_vs_loglin_directional.png)

Figure 6.2: Direct comparison of the directional accuracy of Scale BB-D (green) and `loglin_trend` (red) (sex = total, 3 cutoffs side by side, dashed line at 50%). On the left ($y_c{=}2014$), Scale BB-D is equal or better except for `cancer`. In the middle ($y_c{=}2021$), Scale BB-D leads for `heart_disease` / `total` / `cerebrovascular`. On the right ($y_c{=}2022$), more cells favor `loglin_trend` amid the noise of the short validation period. (Reproduction: `reproduction/backtest/output/directional/figures/scalebb_vs_loglin_directional.png`)

## 6.4 What does the gap mean? — the essential difference between a structural model and a point predictor

The gap between MAPE (§5) and DA (this chapter) is not chance. It comes from model design. `naive_last` / `mean_3pts` are point predictors. They assume that the recent level continues. `loglin_trend` is a short-term extrapolator. It assumes that the log-linear slope of the last 15 years continues. Over short horizons (1–3 years), the level is almost fully set by the level at the end of observation and the recent trend. So these methods hold a structural advantage in point forecasts. Scale BB-D is designed differently. It respects the long-term trend extracted from more than 60 years of observations, and the convergence to the long-term rate $L$ (equation 3.5). It gives these more weight than the local level near the end of observation. It deliberately ignores noise and short-term shocks near the end of observation. This is the root cause of its weaker short-term MAPE (§5.4).

What it gains in exchange is stability of direction. The sign of the improvement rate comes from structure over a span of decades. So it does not swing much, whatever phase the end of observation falls in. The robustness across cutoffs seen in §6.2 shows this. In other words, Scale BB-D is not a tool for hitting next year's level with minimum error. It is a tool that extracts the direction and strength of the long-term trend explicitly, as an improvement rate $i^*(x, y)$ whose direction has been validated. As long as we ask about point forecasts of the level, the negative conclusion of §5 stands. But some uses ask about the sign of the improvement rate and the ability to control it — generating multiple scenarios. For those uses, this property becomes the requirement (§2.3, §7).

## 6.5 Handling direction-reversal diseases — the scope and limits of calibration

The direction misses of `liver` / `hypertensive` (DA 23.6–28.0%) are cases where the default setting of Scale BB-D, $L = +1\%$ (continued improvement), conflicted with the facts. These mortality rates turned upward from the mid-2010s. For practical use, the key question is whether this direction miss can be corrected. Here we separate and test two correction paths: (i) the calibration path — reset $L$ and $P$ per disease; (ii) the data path — include the recent post-reversal data in training. Table 6.4 and Figure 6.3 show the results.

Table 6.4: Recalibration experiment for direction-reversal diseases (sex = total, DA [%])

| Setting | Path | `liver` | `hypertensive` |
|---|---|---:|---:|
| $y_c{=}2014$, default ($L{=}{+}1\%$, $P{=}2035$) | — | 27.97 ($n{=}118$) | 23.64 ($n{=}110$) |
| $y_c{=}2014$, $L{=}0\%$ ($P$ unchanged) | Calibration | 27.97 | 23.64 |
| $y_c{=}2014$, $L{=}0\%$, $P{=}2020$ | Calibration | 33.05 | 30.91 |
| $y_c{=}2021$, default | Data | 45.95 ($n{=}37$) | 68.97 ($n{=}29$) |
| $y_c{=}2022$, default | Data | 52.00 ($n{=}25$) | 85.00 ($n{=}20$) |

![](figures/fig_6_3_calibration_recovery.png)

Figure 6.3: Recovery of the direction agreement rate for direction-reversal diseases — the calibration path (reds: keep $y_c = 2014$ and reset $L$ and $P$) and the data path (orange, green: include post-reversal data in training). The dashed line is 50%. (Generation script: `reproduction/backtest/make_calibration_recovery_figure.py`)

This experiment shows three facts.

1. Replacing the long-term rate alone does not change the direction within the validation period. Lowering $L$ from $+1\%$ to $0\%$ leaves the DA unchanged (the result is the same even down to $-1\%$). The reason lies in the structure of equation (3.5). The whole validation interval 2015–2024 sits inside the blend interval $y_{\text{obs}} < y < P$ (§4.1). There, the improvement rate is a linear interpolation between the end-of-observation improvement rate $i(x, y_c)$ and $L$. Years closer to the end of observation put more weight on the $i(x, y_c)$ side. At $y_c = 2014$, $i(x, y_c)$ is positive, because it reflects the continued improvement of the training period. In addition, the end of observation falls on the boundary where the observation grid switches from 5-year steps to annual steps. So the smoothed value comes out larger than the real trend (the same boundary effect we noted in Figure 3.3). This anchor dominates the short-term projection direction, and $L$ contributes almost nothing.

2. Moving the convergence year forward as well brings partial recovery, but it stays limited. We set $L = 0\%$ and also move $P$ forward from 2035 to 2020. Then the dominance of the end-of-observation anchor ends earlier, and the DA improves to 33.05% / 30.91%. But it still stays below the chance level. Most of the validation period is still projected with the positive, pre-reversal improvement rate.

3. Real recovery happens through the data path. At $y_c = 2021/2022$, the training data include the post-reversal observations. With the default calibration left fully unchanged, `liver` recovers to 45.95 / 52.00% and `hypertensive` to 68.97 / 85.00%. The reason is that the sign of the observed improvement rate $i(x, y)$ extracted in Phase 1 is itself corrected by the data. Once the recent trend enters the training data, Scale BB-D corrects the direction structurally.

The practical implication of this separation is as follows. Disease-specific calibration of $L$ and $P$ controls the long-term direction after the convergence year. Its effect cannot be observed within a 10-year validation period. But over the projection horizon of insurance liability valuation (decades), that part becomes dominant. So resetting $L \le 0$ for reversal diseases is a necessary condition for consistent long-term scenarios (see §9.1 for disease-specific calibration guidance). In contrast, the short-term direction near the end of observation is handled not by calibration but by regular refitting with the latest data. In other words, disease-specific long-term rate settings and regular refitting are not substitutes; they share the work. We add one more point. This correctability itself is a property unique to structural models. `naive_last` has no direction information to correct. Flipping the sign of the slope by hand in `loglin_trend` amounts to abandoning the premise of the estimation. Because the model holds the improvement rate and its long-term assumption as explicit parameters, we can identify a direction error, correct it, and validate it again.

Finally, we make clear what the limit of this verifiability means. The long-term effect of $L$ itself cannot be verified directly until actual data after the convergence year accumulate (with the default setting, this needs actuals from 2035 onward). However, this is not a weakness specific to this framework. It is a general property of long-term improvement assumptions. Moreover, while we wait for actuals, the next structural break — a new epidemic or a shift in medical technology — can arrive. So the policy of "wait until enough data accumulate and then complete the validation" can never close in principle. The design of this framework goes the other way. The part that can be validated even with limited data — the direction of the improvement rate — becomes the foundation, fixed by the validation up to this chapter. The long-term assumptions that validation cannot reach are not embedded as implicit premises. Instead, we state them as a small number of interpretable parameters ($L$, $P$) and turn them into objects to vary as scenarios (§7). Future structural breaks can also be handled. After the fact, regular refitting corrects the direction automatically (as the data path in this section demonstrated with COVID-19). Before the fact, we can quantify them as stress scenarios, such as $L \le 0$ or catastrophe shocks. We do not try to hit long-term uncertainty with a point forecast. We handle the uncertainty explicitly, on top of a validated direction. This stance fits economic-value-based valuation (§2.3), which requires consistency across scenarios rather than a single point forecast.

---

*§7 turns this property — an explicit improvement rate $i^*(x, y)$ whose direction has been validated — into the scenario structure that economic-value-based valuation requires (§2.3).*
