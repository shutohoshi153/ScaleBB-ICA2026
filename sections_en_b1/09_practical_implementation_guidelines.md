# §9 Practical Implementation Guidelines

In §7 we repositioned this framework as a scenario generator. In §8 we quantified its sensitivity. This chapter gives guidance for bringing the framework into the assumption workflow of practical work. §9.1 gives guidance for disease-specific calibration based on the backtest results (§5–§6), and for tuning the hyperparameters (§3.2.3). §9.2 gives a systematic answer to an expected objection: "Building a new generator may be a heavy burden to introduce." It also shows a step-by-step introduction path. §9.3 reports a real case of integration into an existing system.

---

## 9.1 Guidance for Calibration and Tuning

Premise: two channels share the work. As we separated in §6.5, disease-specific calibration (resetting $L$ and $P$) controls the long-term direction after the convergence year. The short-term direction near the end of the observed data is handled by regular refitting with the latest data (the data channel). Therefore, this section gives guidance on two things together: "disease-specific settings of $L$ and $P$" and "the operation of regular refitting". The first alone cannot fix short-term direction errors (the experiment in §6.5). The second alone does not secure consistency after the convergence year — the period that dominates the projection horizon of insurance liabilities.

Disease-specific long-term rate $L$. Table 9.1 shows guidance by disease group, derived from the backtest results (the default is $L = 1\%$ for all diseases, §3.2.3).

Table 9.1: Calibration guidance for the long-term rate $L$ by disease group

| Disease group | Target diseases | Guidance for $L$ | Supporting validation results |
|---|---|---|---|
| Clear improvement trend | `cancer` / `heart_disease` / `cerebrovascular` / `total` | Keep the default 1%, or consider raising it to 2% | DA 79.7–95.0% ($y_c{=}2014$, §6.1). `cancer` shows under-extrapolation of improvement (positive bias, §5.1), so there is room to raise $L$ |
| Watch for a turn to worsening | `diabetes` / `kidney` | Set a modest value of 0.5 to 1% | DA is high (77.7–80.5% at $y_c{=}2014$), but the direction is unstable when the observed data ends around the COVID period (§6.2) |
| Direction reversal | `liver` / `hypertensive` | 0 or below (0 to -1%) | With the default settings, the model misses the direction itself (DA 23.6–28.0%, §6.5). Resetting to $L \le 0$ is a necessary condition for long-term scenario consistency |

When applying Table 9.1, one must note the period in which the effect of resetting $L$ appears. Setting $L \le 0$ for reversal diseases changes the direction agreement rate very little within the backtest validation period (10 years) (§6.5, Table 6.1). This is not a flaw in the guidance. It happens because the validation period lies inside the blending interval, where the anchor at the end of the observed data dominates. It reflects the division of work: the refitting described below handles the short-term direction within the validation period, and $L$ handles the long-term direction after the convergence year.

Convergence year $P$. The default is 2035. In some situations, the improvement rate at the end of the observed data differs greatly from the long-term assumption — right after a structural break, or for direction-reversal diseases. In those cases, consider moving $P$ earlier, to 2025–2030. This releases the dominance of the end-of-data anchor sooner and speeds up the return to the long-term assumption. (In §6.5, DA within the validation period recovered partly only when $L = 0\%$ was combined with an earlier $P$.) In contrast, when the continuation of the recent trend matters most, the default can stay as it is.

Smoothing strength $\lambda_{\text{year}}$ (`lam_col`). The default is 40 (§3.2.3). Use different values for different purposes. For monitoring and analysis, where you want the model to follow structural change, lower it to 10–20 so that it respects the local trend at the end of the observed data. For uses where year-to-year stability of the rates matters, such as generating forward-looking assumed rate tables, raise it to 60 (the age20 preset in the note of §3.2.3). The age-direction $\lambda_{\text{age}}$ and the difference order $d$ were robust at their defaults (40 and 2) within the scope of this validation.

Regular refitting. As a basic rule, refit once a year, in line with the annual release of the Vital Statistics of Japan (MHLW). As the data channel in §6.5 shows, short-term self-correction for direction reversals and structural breaks works through refitting, not through calibration operations. (This was demonstrated by the reflection of COVID-19; §5.3 and §6.2.) The computing load of refitting is small (§9.2, argument 4), so it is not an obstacle to annual operation.

A pattern for model validation. When you extend the model to new diseases, new granularity, or new products, we recommend measuring DA before applying it. Use the 3-cutoff backtest of this paper (§4) and the directional accuracy (equation 3.12) as the template. The validation procedures of §5–§6 can be reused directly as a model-validation template at each company.

## 9.2 Analysis of the Introduction Burden — Five Arguments and a Step-by-Step Path

The proposal to "build a new scenario generator for the disease-risk axis" (§7.4) may bring to mind a large system investment and operational change, as the introduction of an Economic Scenario Generator (ESG) once did. However, the introduction burden of this framework is low, for the following five reasons.

1. Upstream position, same output format. The generator sits upstream of the projection engine. Its output is a format that existing valuation practice already consumes: rate tables by age x calendar year (or age x policy duration). Downstream steps — the valuation model, the closing process, and reports — need no change. In fact, the demonstration in §8 reached a sensitivity table using only the existing rate panel and the algorithm core. The only thing it asked from the valuation side was to read scenario-specific rate tables.

2. Replacement, not addition. Current practice already has a step that builds rate tables for stress (static table x uniform factor). This framework replaces that step. It does not increase the number of scenario runs. A level shock that the uniform-factor method could express can still be expressed as a uniform multiplication in this framework (Table 7.1). The output of the current method can be reproduced as a special case of this framework.

3. No new data preparation is needed. The inputs are public statistics (the Vital Statistics of Japan) and the company's own experience data, which each company already collects for experience-rate analysis. There is no need to buy new external data or to build a new data-collection system.

4. The computing load is light. The framework is deterministic, so it does not need the infrastructure for computing and storing thousands of paths, as an ESG does. On the generator side (creating rate tables), the Phase 1 fit is shared across all scenarios. The marginal cost of adding a scenario is only one Phase 2 re-projection (§7.2). On the valuation side (computing the present value of benefits), the only requirement is reading scenario-specific rate tables (argument 1). Since these tables have the same format as the existing ones (arguments 1 and 2), the extra load on the existing valuation batch stays linear in the number of runs. Measuring the actual run load and the integration effort on a practical projection model is left to future validation (§10.4).

5. The governance burden is low. The judgment parameters are essentially only $L$ and $P$. Both are quantities that can be explained to management and validation teams: "how much improvement do we assume will continue in the long term?" and "when do we converge to the long-term assumption?". The computation is deterministic and reproducible. For model validation, the backtest of this paper (§4–§6) serves directly as the template (§9.1). This differs in kind from black-box machine-learning models, where explainability itself becomes the issue for validation and explanation.

A step-by-step introduction path. Introduction does not require a full switch at once. A design is possible that promotes the framework step by step, starting from low-risk uses.

- Stage 1 — Trial use in internal sensitivity analysis and ORSA (Own Risk and Solvency Assessment): Outside regulatory calculations, run the framework in parallel with the current uniform-factor method. Bring the extra information from trend scenarios (the age gradient in §8.4) into internal management and risk understanding. This can start without changing current practice at all.
- Stage 2 — IFRS 17 sensitivity disclosure: Use grid runs such as $L \pm 50$bp (Table 7.1) for the calculation of disclosed sensitivities.
- Stage 3 — Regulatory calculations under the Insurance Capital Standard (ICS) and economic-value-based solvency regulation (ESR): Extend the scope to required-capital calculations under the stress method (§8.5).

Whether to promote the framework at each stage can be judged on evidence, by passing the backtest validation of §9.1 (measuring DA on the target of application). A transition that starts with parallel operation and comparison with the current method acts as a buffer. It does not demand a "jump away from uniform factors".

## 9.3 A Real Case of Integration into an Existing System

The algorithm core of this framework is a small implementation. It consists of pure smoothing and projection functions (`fit_scale_bb` / `project_scale_bb`) and a configuration object (`ScaleBBConfig`) (§3.2). This core has already been integrated into the authors' experience-rate aggregation process system. Within one workflow, it can run from the aggregation of the company's own experience data to the generation of projected rate tables using disease-specific presets. The integration required only copying the core and adding configuration presets. No changes to the existing aggregation and output steps were needed. In this form, a projection function is added downstream of the existing experience-rate analysis steps. This case supports, at the implementation level, argument 1 of §9.2 (upstream position, same output format) and argument 3 (existing data is enough).

---

*In this chapter, Scale BB-D as a scenario generator became concrete, down to "how to configure it and how to introduce it". The next chapter, §10, faces the limitations of this study — the proxy nature of the data, the limits of long-term verifiability, and the simplicity of the financial demonstration — and shows a path toward future work.*
