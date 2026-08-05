# §3 Data and Methodology

This chapter describes our framework, which extends Scale BB from all-cause mortality to cause-specific (disease-specific) mortality. We present the data used for the validation (§3.1), the mathematics of the extended algorithm (§3.2), the APC extension that separates cohort effects (§3.3), and the baseline methods and evaluation metrics used for comparison (§3.4). The goal of this chapter is to make the later chapters reproducible: the validation of point forecast accuracy (§5) and the findings on directional accuracy (§6). We define all notation here.

About notation: the math symbols follow the earlier study, the SOA (2012) *Mortality Improvement Scale BB Report*. Age is $x$, calendar year is $y$, the long-term improvement rate is $L$, the end (convergence) year of the blend is $P$, and the slope of the log-linear regression is $s$. We use the continuous piecewise-linear blend function $h(y)$ from §7.4 of the original report.

---

## 3.1 Data and Target Diseases

### 3.1.1 Input data

The input for the validation is the cause-specific crude mortality rate $m(x, y)$ per 100,000 total population. We took it from Table 5-15 of the Vital Statistics of Japan (MHLW), which gives annual trends by cause of death (cause of death × sex × 5-year age group × year). Here $x$ is the age group and $y$ is the calendar year.

Table 3.1: Specification of the input panel

| Item | Content |
|---|---|
| Source | Vital Statistics Table 5-15 (annual-trend cause-of-death classification × sex × 5-year age group × year) |
| Period | 1950–2024 (5-year steps for 1950–2010, yearly for 2013–2024) |
| Unit | Crude mortality rate per 100,000 population |
| Target diseases | 8 diseases (table below) |
| Sex | 3 groups: total / male / female |
| Age | 21 groups from 0–4 to 100+ (the validation uses the 14 groups for ages 20–89) |

Table 5-15 is a cause-of-death time series in which 5-year age groups × year are available over a long period. The observation years are not evenly spaced (5-year steps in the first half, yearly in the second half). The annualization logic in §3.2 handles this point (equation (3.3)). Under its terms of use, the Vital Statistics data can be used for commercial purposes, provided the source is stated; where the content is edited or processed, that fact and the party responsible must also be stated.[^estat]

[^estat]: e-Stat terms of use: https://www.e-stat.go.jp/terms-of-use (English: https://www.e-stat.go.jp/en/terms-of-use). The rates used in this paper are processed by the authors from the published tables.

![](figures/fig_3_1_input_panel_overview.png)

Figure 3.1: Overview of the input panel — the cause-specific mortality rates $m(x,y)$ from 1950 to 2024 (sex = total; left: ages 40–44; right: ages 75–79; log scale). The markers are observation points. They show the uneven spacing: 5-year steps in the first half (1950–2010) and yearly points in the second half (2013–2024). The diseases differ greatly in level (a gap of more than 100 times) and in the shape of the long-term trend. For example, `cerebrovascular` falls steadily, while `cancer` rises and then turns down. (Generation script: `reproduction/backtest/make_paper_figures.py`)

### 3.1.2 Target disease mapping

From the definitions of insured diseases (`disease_estat_mapping.csv`), we built a panel of the 8 diseases for which Table 5-15 provides age-specific time series.

Table 3.2: Mapping of the 8 target diseases to the cause-of-death codes of Vital Statistics Table 5-15

| disease_id | 5-15 cause code | Label | Remarks |
|---|---|---|---|
| `cancer` | Hi022017 | Cancer (malignant neoplasms) | Mortality proxy for the disease incidence rate |
| `diabetes` | Hi03 | Diabetes | Same as above |
| `hypertensive` | Hi042017 | Hypertensive diseases | Same as above |
| `heart_disease` | Hi05 | Heart disease (excluding hypertensive) | Same as above |
| `cerebrovascular` | Hi06 | Cerebrovascular disease | Same as above |
| `liver` | Hi11 | Liver disease | Same as above |
| `kidney` | Hi12 | Kidney failure | Table 5-15 has no glomerular diseases etc., so kidney failure only |
| `total` | Hi00 | Total | Sum of all causes |

Ischemic heart disease (`heart_ischemic`) does not exist in the annual-trend cause-of-death classification of Table 5-15, so we excluded it. The panel shape is 8 diseases × 3 sexes × 25 years × 21 age groups = 12,600 rows.

### 3.1.3 The dual role of the data — proxy and direct target

The cause-specific mortality rates used in this study play two different roles, depending on the target product. This distinction is a core assumption. It defines the practical scope of the framework (§7 and §8) and its limits (§10).

1. For the disease incidence rates of medical insurance, the data are a "proxy" for validating the methodology. Medical insurance that pays benefits when a disease occurs really needs disease incidence rates as its assumption. However, as noted above, Japan's public statistics have no long-term incidence panel by disease × age × year. So we use cause-specific mortality, which we expect to share the same age and cohort structure as incidence, as a proxy. In this way we validate the methodology of the Scale BB extension itself. Because it is a proxy, this validation cannot separate level differences that come from changes over time in the case fatality rate (mortality after diagnosis). We state this reservation clearly in §10.

2. For death benefits contingent on specific diseases, the data are the "direct assumption" itself. Some products pay death benefits based on the cause of death: death coverage for the three major diseases, cancer death insurance, and cause-specific disease-death riders. For these products, cause-specific mortality is not a proxy. It is the assumption itself for computing the present value of benefits. We apply the framework directly to these products.

> Note: The data in this study are cause-specific mortality rates per total Japanese population. They are not mortality after diagnosis (case fatality rate = deaths by cause ÷ number of diagnosed cases). Case fatality rates need observed incidence rates in the denominator, so they are outside the scope of this study. We do not try to "predict the prognosis after diagnosis" (see §10).

---

## 3.2 The Scale BB Extension Algorithm

Scale BB here extends SOA (2012) *Mortality Improvement Scale BB* to disease-specific mortality. It has two phases: Phase 1 (smoothing of observations and extraction of improvement rates) and Phase 2 (blending with the long-term rate and future projection). The implementation is based on the pure functions in `_scalebb_core/model.py` (`fit_scale_bb` / `project_scale_bb`).

### 3.2.1 Phase 1 — Two-dimensional smoothing and improvement-rate extraction

We take the log of the observed crude rate $m(x, y)$ and set $z(x, y) = \log m(x, y)$. Cells that are $0$ or below, or missing, receive weight $0$.

We apply two-dimensional Whittaker-Henderson penalized smoothing to the log-rate matrix $Z = (z_{x,y})$. This is equivalent to the P-spline smoothing of the original SOA report (tensor-product B-spline + difference penalty). We find the smoothed matrix $\hat{Z}$ that minimizes the following objective function.

$$
J(\hat{Z}) \;=\; \sum_{x,y} w_{x,y}\,\bigl(z_{x,y} - \hat{z}_{x,y}\bigr)^2
\;+\; \lambda_{\text{age}}\,\bigl\lVert D^{(d)}_{\text{age}}\,\hat{Z} \bigr\rVert_F^2
\;+\; \lambda_{\text{year}}\,\bigl\lVert \hat{Z}\,\bigl(D^{(d)}_{\text{year}}\bigr)^{\!\top} \bigr\rVert_F^2
\tag{3.1}
$$

Here,

- $w_{x,y}$ are the observation weights (missing and non-positive cells get $0$),
- $D^{(d)}_{\bullet}$ is the difference matrix of order $d$ (default $d = 2$),
- $\lambda_{\text{age}}, \lambda_{\text{year}}$ are the smoothing strengths in the age direction and the calendar-year direction,
- $\lVert \cdot \rVert_F$ is the Frobenius norm.

If we arrange $\mathrm{vec}(\hat{Z})$ in column-major (Fortran) order, the stationary condition of equation (3.1) becomes a sparse linear system. Set $P_{\text{age}} = I_{n_{\text{year}}} \otimes \bigl(D^{(d)\top}_{\text{age}} D^{(d)}_{\text{age}}\bigr)$, $P_{\text{year}} = \bigl(D^{(d)\top}_{\text{year}} D^{(d)}_{\text{year}}\bigr) \otimes I_{n_{\text{age}}}$, and $W = \mathrm{diag}\bigl(\mathrm{vec}(w)\bigr)$. Then we solve

$$
\bigl(W + \lambda_{\text{age}} P_{\text{age}} + \lambda_{\text{year}} P_{\text{year}}\bigr)\,\mathrm{vec}(\hat{Z})
\;=\; W\,\mathrm{vec}(Z)
\tag{3.2}
$$

with a sparse matrix solver. On a coarse age × year grid (at most about 80 × 80), it converges instantly. We recover the smoothed rates as $\tilde{m}(x, y) = \exp\bigl(\hat{z}(x, y)\bigr)$. Figure 3.2 compares the rates before and after smoothing on real data (heart disease, sex = total).

![Before and after smoothing — observed rates and two-dimensional Whittaker-Henderson smoothed rates for heart disease, total (left: cross-sections along calendar year, right: cross-sections along age)](figures/fig_3_2_smoothing_before_after.png)

Figure 3.2: Comparison before and after two-dimensional Whittaker-Henderson smoothing (equations 3.1–3.2, $\lambda_{\text{age}} = \lambda_{\text{year}} = 40$) (heart disease, sex = total, observations $\leq$ 2022, log scale). The markers show the observed crude rates $m(x, y)$; the solid lines show the smoothed rates $\tilde{m}(x, y)$. The left panel shows cross-sections along calendar year (3 representative ages). The short-term noise typical of yearly data is smoothed out, while the long-term trend is kept. The right panel shows cross-sections along age (3 representative calendar years). The age slope, which is almost linear on the log scale, is recovered smoothly. The smoothing works in the age and calendar-year directions at the same time. So it has a consistency that one-dimensional smoothing of each cross-section cannot give. (Generation script: `reproduction/backtest/make_paper_figures.py`)

Note that in the left panel, for ages 75–79, the smoothed rate stays a little below the peak of the observations around 1960–1990. The reason is that the default smoothing strength ($\lambda = 40$) prefers extracting the long-term trend over following the local level. This behavior is intended (the settings are the same for all diseases, §3.2.3).

Next, we extract the annual observed improvement rate $i(x, y)$ from the smoothed rates. The BFLL (best-fit log-linear) method in §3.1 of the original report gets the annual improvement $1 - e^{s}$ from the slope $s$. We follow the same idea. Even when the observation years are unevenly spaced, we convert to the geometric mean improvement rate between two neighboring time points. Using the year gap $\Delta y_k = y_k - y_{k-1}$, we define

$$
i(x, y_k) \;=\; 1 - \left(\frac{\tilde{m}(x, y_k)}{\tilde{m}(x, y_{k-1})}\right)^{1/\Delta y_k}
\tag{3.3}
$$

Here $i > 0$ means the rate falls (improvement), and $i < 0$ means the rate rises (worsening). The stability of the sign of this improvement rate is what the directional accuracy in §6 measures, and it leads to the scenario generation in §7.

### 3.2.2 Phase 2 — Long-term rate blending and future projection

In Phase 2, we blend the smoothed improvement rate at the last observed year, $i(x, y_{\text{obs}})$, linearly toward the long-term assumed improvement rate $L$ (default 1%) up to the convergence year $P$ (default 2035). At high ages, improvement slows down and disappears in reality. To reflect this, we introduce an age-specific taper factor $\tau(x)$ and set the age-specific long-term rate to $L_{\text{age}}(x) = L \cdot \tau(x)$. With a taper start age $a_0$ (default 90) and a taper end age $a_1$ (default 120), we define

$$
\tau(x) =
\begin{cases}
1 & x \le a_0 \\[2pt]
1 - \dfrac{x - a_0}{a_1 - a_0} & a_0 < x < a_1 \\[6pt]
0 & x \ge a_1
\end{cases}
\tag{3.4}
$$

(This matches §5.2 of the original report: the long-term rate applies up to age 90 and falls linearly to 0% at age 120.)

The weight for the linear transition from the last observation to the long-term rate follows the continuous piecewise-linear blend function $h(y)$ in §7.4 of the original report. The original report defines $h(y)$ as a multiplicative factor that moves linearly from $1$ to $L$ between a fixed start year (2005) and $P$. We change this in two ways: (i) we generalize the start year to the last observed year $y_{\text{obs}}$ (to allow a variable cutoff and the extension to causes of death); (ii) we use $h(y)$ not as a multiplicative rescaling of the rates, but as the weight of a linear interpolation between the observed improvement rate and the long-term rate. That is, we set

$$
h(y) =
\begin{cases}
0 & y \le y_{\text{obs}} \\[2pt]
\alpha_y \;=\; \dfrac{y - y_{\text{obs}}}{P - y_{\text{obs}}} & y_{\text{obs}} < y < P \\[6pt]
1 & y \ge P
\end{cases}
$$

Then the final improvement rate $i^*(x, y)$ is given by

$$
i^*(x, y) \;=\; \bigl(1 - h(y)\bigr)\, i(x, y_{\text{obs}}) \;+\; h(y)\, L_{\text{age}}(x)
\tag{3.5}
$$

In other words, in the observed period ($y \le y_{\text{obs}}$) the rate keeps the value at the last observed year, $i(x, y_{\text{obs}})$. It then moves linearly toward the long-term rate $L_{\text{age}}(x)$ up to the convergence year $P$. From $P$ on ($y \ge P$), it stays flat at $L_{\text{age}}(x)$. Figure 3.3 shows a real example of $i^*(x, y)$ on real data (heart disease, sex = total, $y_{\text{obs}} = 2022$).

![Example of the improvement-rate blend — annual improvement rate i*(x,y) for heart disease, total, cutoff 2022](figures/fig_3_3_blend_schematic.png)

Figure 3.3: A real example of the blend in equation (3.5) (heart disease, sex = total, $y_{\text{obs}} = 2022$, 3 representative ages). In the observed period, the lines show the observed improvement rates smoothed in Phase 1 (including the drop in improvement during the COVID-19 period). From the value $i(x, y_{\text{obs}})$ at the last observed year $y_{\text{obs}} = 2022$, the rate moves linearly to the long-term rate $L = 1\%$ up to the convergence year $P = 2035$ (shaded band), and stays flat after that. (Generation script: `reproduction/backtest/make_paper_figures.py`)

We add three comments on Figure 3.3. First, the sharp peak in 2014–2015 (5.6 to 7.0% per year) shows the smoothed curve capturing the fast fall of heart disease mortality in the mid-2010s. However, it is also affected by the annualization (equation 3.3) of the 2010→2013 gap, where the observation grid switches from 5-year steps to yearly data. So we do not read it as the true level of a single year. Second, the improvement rate at the last observed year 2022 is a little under 0.2% for ages 60–64 / 75–79. This reflects the stalled improvement in the COVID-19 period, and it is far below the historical level (1 to 2%). The blend starts from this reduced value. It does not assume that the recent anomaly lasts forever, and it does not assume an immediate return to normal. Instead, it moves back to the long-term rate over the years up to the convergence year. Third, for ages 40–44, $i(x, 2022) \approx 1.0\%$ happens to be almost equal to $L$, so the blend section is almost flat. This shows that the blend really works only when the improvement rate at the last observation differs from the long-term rate.

We generate the future rates forward from the rate $m(x, y_0)$ of the base year $y_0$, by accumulating the improvement rates.

$$
m(x, y) \;=\; m(x, y_0)\,\prod_{u = y_0 + 1}^{y}\bigl(1 - i^*(x, u)\bigr)
\tag{3.6}
$$

The structural key point of the framework is this: the future rates are fully rebuilt as "base-year rate × cumulative $(1 - i^*)$". If we replace $i^*(x, y)$, we get new future rates at once. So we can generate several scenarios with different long-term rates $L$ or convergence years $P$ in an internally consistent way, while keeping the same age-curve shape and the same base-year rates (§7).

### 3.2.3 Hyperparameters

The output of Scale BB depends on quantities estimated from the data, such as the smoothed matrix $\hat{Z}$ and the improvement rates $i(x, y)$. It also depends on settings that the analyst gives from outside, before the estimation. In this paper we call the latter hyperparameters. They are: $\lambda_{\text{age}}, \lambda_{\text{year}}, d$, which set the strength and smoothness of the smoothing (equation 3.1); $L, P$, which set the long-term improvement assumption (equation 3.5); and $a_0, a_1$, which set the fade-out of improvement at high ages (equation 3.4). Table 3.3 lists them with their default values.

In this validation we did no disease-specific tuning. We applied the default preset of the experience-rate aggregation process (`config.yaml > scalebb_presets > defaults`) to all diseases. We discuss guidance for disease-specific calibration separately in §9.

Table 3.3: Hyperparameters of the Scale BB extension and their default values

| Symbol | Parameter | Default |
|---|---|---|
| $L$ | Long-term improvement rate (`long_term_rate`) | 0.01 (1%) |
| $P$ | Convergence year (`convergence_year`) | 2035 |
| $\lambda_{\text{age}}$ | Smoothing in the age direction (`lam_row`) | 40 |
| $\lambda_{\text{year}}$ | Smoothing in the calendar-year direction (`lam_col`) | 40 |
| $d$ | Difference order (`diff_order`) | 2 |
| $a_0, a_1$ | Age taper start and end | 90, 120 |
| $y_{\text{obs}}$ | Last observed year (`last_observed_year`) | cutoff (§4) |

> Note on the range of settings: The table above shows the settings used for the backtest in this chapter (validation of point forecasts and direction). It corresponds to the reproduction package `reproduction/backtest/`. The forward-looking pipeline that generates generational assumed rate tables (`reproduction/generational/`, details in `reproduction/generational/README.md`) uses the age20 preset with `lam_col=60` (stronger smoothing in the calendar-year direction) and the age range `age_min=20`. This reduces year-to-year swings in the rates for young ages (starting at age 20). The core parameters other than $\lambda_{\text{year}}$ ($L=0.01$, $P=2035$, $\lambda_{\text{age}}=40$, $d=2$) are the same in both.

---

## 3.3 The APC Cohort-Penalty Extension

The Age-Period (AP) model above absorbs the cohort effect $\gamma(c)$ (where $c = y - x$ is the birth cohort) into the period effect $\beta(y)$. So it cannot mathematically identify "long-term health effects specific to a cohort that experienced a pandemic at a certain age". To separate this, we extend to an Age-Period-Cohort (APC) model with an additive decomposition (`scale_bb_apc_model.py`).

The observation model is

$$
\log m(x, y) \;=\; \alpha(x) + \beta(y) + \gamma(c) + \varepsilon(x, y), \qquad c = y - x
\tag{3.7}
$$

Here $\alpha(x)$ is the age effect. $\beta(y)$ is the period effect (health-system reforms, epidemics, the COVID-19 shock). $\gamma(c)$ is the cohort effect (lifestyle, access to medical technology, disease exposure in youth). The smoothing objective adds a diagonal (cohort) difference penalty to equation (3.1):

$$
J(\hat{Z}) \;=\; \sum_{x,y} w_{x,y}\bigl(z_{x,y} - \hat{z}_{x,y}\bigr)^2
+ \lambda_{\text{age}}\bigl\lVert D^{(d)}_{\text{age}}\hat{Z}\bigr\rVert_F^2
+ \lambda_{\text{year}}\bigl\lVert \hat{Z}\,(D^{(d)}_{\text{year}})^{\!\top}\bigr\rVert_F^2
+ \lambda_{\text{cohort}}\bigl\lVert D^{(d)}_{\text{cohort}}\,\mathrm{vec}(\hat{Z})\bigr\rVert^2
\tag{3.8}
$$

We build the diagonal difference matrix $D^{(d)}_{\text{cohort}}$ as a second-order difference along the same cohort. On $\mathrm{vec}(\hat Z)$ (column-major), it takes the form $\hat{z}_{i+2,\,j+2} - 2\hat{z}_{i+1,\,j+1} + \hat{z}_{i,\,j}$ (here $i, j$ are the matrix indexes for age and calendar year). After smoothing, we extract $\alpha, \beta, \gamma$ with an iterative weighted least-squares method (`decompose_apc_additive`).

Identifiability. Because of the linear dependence $\text{age} + \text{cohort} = \text{period}$, an APC model cannot identify the absolute levels and the linear trend parts of the three effects. Our implementation handles this with two tools used together.

- Second-order difference penalty ($d = 2$): the constant and linear parts are not penalized. Under the penalty, only the nonlinear parts of order 2 and higher are identified uniquely. Our research interest is the nonlinear deviation of cohorts that were at a certain age during the pandemic. This nonlinear part is identifiable, so it matches the research hypothesis.
- Reference cell constraints: we impose $\alpha(x_{\min}) = \beta(y_{\min}) = 0$ to remove the indeterminacy of the constant level (Holford 1983).

We merge the linear part into the period effect, following the Holford convention, and report results as relative improvement rates and residuals.

Treatment of the COVID-19 period. The pandemic period (2020–2022) is a structural break outside the normal trend. Simple smoothing would distort the estimate of the long-term improvement rate. Our implementation offers 3 modes.

This is not only a modelling convenience. Japan's ESR contemplates the same problem explicitly. The Q&A accompanying the Pillar 1 notice allows actual data arising from a temporary factor to be excluded from the data used for future cash flows where the pattern is judged not to continue, and it names the COVID-19 pandemic as an example — both the increase in claim payments and the effect on hospitalisation and other medical activity. The conditions it attaches are that the temporary nature be reasonably justified, that the effect be quantified, and that the treatment be applied consistently across assumptions. Our `weight_down` mode is a softer form of the same operation, and the quantification in §5.3 — how far the validation error moves according to whether the pandemic is inside the training window — is the kind of evidence those conditions call for.

Table 3.4: Treatment modes for the COVID-19 period in the APC extension

| Mode | Treatment | Recommended use |
|---|---|---|
| `weight_down` | Reduce the observation weights of the COVID years: $w \mapsto c_w \cdot w$ ($c_w \in [0,1]$, default 0.3) | Diseases whose long-term improvement continues smoothly (cancer) |
| `dummy` | Replace $\beta(y)$ in the COVID years with $\beta_{\text{corr}}(y)$, the linear interpolation from non-COVID years, and rebuild the rates with $\beta_{\text{corr}}$. Keep the shock part $\beta(y) - \beta_{\text{corr}}(y)$ separately | Diseases with clear irregular movements in the COVID period (heart disease, cerebrovascular disease) |
| `none` | COVID years also keep weight 1.0 (reference for comparison) | Baseline |

For the projection, we must extrapolate $\gamma(c)$ for new, unobserved cohorts that appear during the projection period. The default is `last_drift`, which extends the last first-order difference (consistent with the Scale BB philosophy). A conservative option is `flat`, which holds the last value fixed.

Hyperparameters of the APC extension. The settings specific to this extension are listed below. They are additional to the Scale BB hyperparameters of §3.2.3, which the APC extension inherits unchanged.

Table 3.5: Hyperparameters specific to the APC cohort-penalty extension

| Symbol / setting | Parameter | Default |
|---|---|---|
| $\lambda_{\text{cohort}}$ | Smoothing in the cohort (diagonal) direction (equation 3.8) | *[TO BE COMPLETED — fill in the default value from the implementation]* |
| — | COVID-19 treatment mode | `weight_down` |
| $c_w$ | Weight multiplier for COVID years under `weight_down` | 0.3 |
| — | Cohort extrapolation for unobserved cohorts | `last_drift` |
| $d$ | Difference order of the cohort penalty | 2 |

<!-- TODO(著者確認): 上表の $\lambda_{cohort}$ 既定値を `_scalebb_core/apc_model.py` から確認して埋めること。他の値も実装と照合すること。 -->

> **Scope note.** The APC extension defined in this section is *not* used in the backtest of §5–§6 or in the financial demonstration of §8. Those results are all produced by the Age-Period framework of §3.2. We present the APC extension here because §7.2 refers to cohort shocks as an implementable scenario type on this framework, and because §10.3 identifies the backtest validation of APC projections as future work. Readers who are only following the validated results may skip to §3.4.

<!-- TODO(著者判断): 査読者は「検証されていない手法がなぜ方法論の章にあるのか」を必ず問う。
     対応は二択。
       (a) §3.3 全体を付録に移し、本文には §7.2 のコホートショック実装可能性への言及のみ残す
           （分量削減にもなるため、Final Paper 締切までの残り期間を考えるとこちらが現実的）
       (b) APC を含む DA を最低限 1 表だけ §6 に追加する
     上記の Scope note は、どちらを選ぶにせよ暗黙の前提を明示化するための暫定措置。 -->

---

## 3.4 Baseline Methods and Evaluation Metrics

### 3.4.1 Three baseline methods

To evaluate the usefulness of Scale BB in relative terms, we compare it with three non-Scale-BB baselines. They either have no explicit concept of an improvement rate, or hold it in a different way. All of them are built for each age $x$ separately. Let $y_c$ be the cutoff year (the end of the training period).

Table 3.6: The three baseline methods

| Method | Forecast rule | Intuition |
|---|---|---|
| `naive_last` | $\hat{m}(x, y) = m(x, y_c)$ | "The latest value continues." By construction, $\hat{m}$ does not depend on $y$ |
| `mean_3pts` | $\hat{m}(x, y) = \frac{1}{3}\sum_{k=0}^{2} m(x, y_c^{(k)})$ (mean of the last 3 observation points) | Noise removal, level averaging |
| `loglin_trend` | Fit $\log m(x, y) = a_x + s_x\, y$ by OLS (ordinary least squares) for each age over the last 15 years, and extrapolate with $\hat{m}(x, y) = \exp(a_x + s_x\, y)$ | A classical actuarial method. It has the same form as the BFLL in §3.1 of the original report, and it implies an annual improvement of $1 - e^{s_x}$ |

`naive_last` carries the cutoff-year value forward. So its predicted change, defined below, is always $0$ (it has no direction information). `loglin_trend` is the only baseline with explicit direction information, through the age-specific slope $s_x$. So it is the most meaningful rival of Scale BB (§6).

### 3.4.2 Evaluation metrics

For each validation cell (age $x$ × validation year $y$ × disease × sex), we compare the actual value $m_{\text{act}}(x, y)$ with the forecast $\hat{m}(x, y)$ and compute the metrics below. Cells with an actual value of $0$ are excluded from MAPE.

Point forecast accuracy metrics. For the set of validation cells $\mathcal{C}$ (with $N = |\mathcal{C}|$ elements),

$$
\text{MAPE} \;=\; \frac{100}{N} \sum_{(x,y) \in \mathcal{C}} \frac{\bigl|\hat{m}(x, y) - m_{\text{act}}(x, y)\bigr|}{m_{\text{act}}(x, y)} \quad [\%]
\tag{3.9}
$$

$$
\text{bias} \;=\; \frac{1}{N} \sum_{(x,y) \in \mathcal{C}} \bigl(\hat{m}(x, y) - m_{\text{act}}(x, y)\bigr) \quad [\text{per } 10^5]
\tag{3.10}
$$

A positive bias means the forecast is too high; a negative bias means it is too low. As support, we also use RMSE (Root Mean Square Error) and the mean relative bias ($\frac{100}{N}\sum (\hat{m} - m_{\text{act}})/m_{\text{act}}$).

Directional accuracy (DA below). This metric supports the central finding of this study (§6). It measures how well the forecast predicts whether the rate moves up or down, compared with the last training year $y_c$. For each cell, we define the actual change and the predicted change as

$$
\Delta_{\text{act}}(x, y) = m_{\text{act}}(x, y) - m(x, y_c), \qquad
\Delta_{\text{pred}}(x, y) = \hat{m}(x, y) - m(x, y_c)
\tag{3.11}
$$

We restrict to the set of cells where the actual value changed, $\mathcal{D} = \{(x, y) : \Delta_{\text{act}}(x, y) \neq 0\}$, and compute the sign agreement rate

$$
\text{DA} \;=\; \frac{1}{|\mathcal{D}|} \sum_{(x,y) \in \mathcal{D}} \mathbf{1}\!\left[\, \operatorname{sign}\Delta_{\text{pred}}(x, y) = \operatorname{sign}\Delta_{\text{act}}(x, y) \,\right] \quad [\%]
\tag{3.12}
$$

Here $\mathbf{1}[\cdot]$ is the indicator function.

Under this definition, `naive_last` has $\Delta_{\text{pred}} \equiv 0$ by construction and carries no direction information (its DA is in effect $0$). This is an intended axis of evaluation: DA asks whether the model tried to call the direction. Point forecast accuracy (MAPE) measures "getting the level right". Directional accuracy (DA) measures "getting the sign of the trend right". The gap between the two is the starting point of the argument for repositioning Scale BB as a scenario generator, not a point forecaster (§7).

---

*The notation of this chapter is used throughout §4 and later. §4 gives the details of the validation design (3 cutoffs). §5 gives the point forecast accuracy results. §6 gives the directional accuracy results. §10 discusses head-on the limits that come from the proxy nature of the data.*
