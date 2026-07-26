"""Scale BB 拡張アルゴリズムのコアライブラリ.

SOA (2012) の *Mortality Improvement Scale BB* 思想を疾病発生率に応用する際の
数理コアを切り出したモジュール。UI/CLI/DB ロード層から独立した純粋関数群として
実装し、以下の再利用先から直接呼び出される::

    scripts/scale_bb_disease.py             ... 研究用 CLI (fit + project)
    scripts/visualize_scale_bb_heatmaps.py  ... 研究用 可視化 CLI
    KDB/src/experience_rate/scalebb.py      ... KDB 側ラッパ (DB ロード含む)

原論文 Section 5.2 Phase 1 のアウトラインに準拠する::

    1. 実績率 m(x, t) を 2 次元平滑化（SOA は P-spline、本実装は等価な
       Whittaker-Henderson 差分罰則スムーザ）して改善率 i(x, t) を抽出
    2. 長期想定改善率 L と収束年 P を指定し、観測終端→P 年までの線形収束で
       2 次元改善率配列 i*(x, t) を合成
    3. 基準年 t0 からの累積で将来率 m(x, t) を投影
       m(x, t) = m(x, t0) * prod_{s=t0+1}^{t} (1 - i*(x, s))

観測年が不等間隔（例: 1950/1955/.../2005/2010/2013-2024）でも正しく
**年率ベース** の改善率に換算するため、`years` 配列は明示的に受け取って
ギャップを反映する。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

import numpy as np
from scipy.sparse import csr_matrix, diags, eye, kron
from scipy.sparse.linalg import spsolve


# ---------------------------------------------------------------------------
# 1. 2D Whittaker-Henderson smoother (P-spline 等価)
# ---------------------------------------------------------------------------
def _difference_matrix(n: int, d: int) -> csr_matrix:
    """``d`` 階差分行列 ``D`` (shape = (n-d, n)) を疎行列で構築."""
    if d < 1 or d >= n:
        raise ValueError(f"invalid diff order d={d} for n={n}")
    m = np.eye(n)
    for _ in range(d):
        m = np.diff(m, axis=0)
    return csr_matrix(m)


def whittaker_henderson_2d(
    y: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    lam_row: float = 10.0,
    lam_col: float = 10.0,
    diff_order: int = 2,
) -> np.ndarray:
    """2 次元 Whittaker-Henderson スムーザ。

    目的関数::

        min_Z  sum_{i,j} w_{ij} (y_{ij} - z_{ij})^2
               + lam_row * ||D_d Z||_F^2
               + lam_col * ||Z D_d^T||_F^2

    ここで ``D_d`` は ``diff_order`` 階差分行列。SOA Scale BB の P-spline 平滑化
    （tensor-product B-spline + 差分罰則）とほぼ等価で、実装が単純かつ
    年齢・暦年の粗いグリッド（最大でも 80 × 80 程度）でも瞬時に収束する。

    Args:
        y: shape (n_row, n_col) の観測値行列。NaN は ``weight=0`` 扱いで補間。
        weight: 同 shape の重み行列。NaN 要素は自動的に 0 にクリップ。
        lam_row: 行方向（年齢）の平滑化パラメータ (正の実数)
        lam_col: 列方向（暦年）の平滑化パラメータ (正の実数)
        diff_order: 差分罰則の階数 (通常 2)

    Returns:
        shape (n_row, n_col) の平滑化後行列。
    """
    y = np.asarray(y, dtype=float)
    if y.ndim != 2:
        raise ValueError("y must be 2-D")
    n_row, n_col = y.shape

    if weight is None:
        weight = np.ones_like(y)
    weight = np.asarray(weight, dtype=float).copy()

    # NaN セルは重み 0 で平滑化対象から除外し、穴埋めは罰則項任せ
    nan_mask = ~np.isfinite(y)
    y = np.where(nan_mask, 0.0, y)
    weight[nan_mask] = 0.0
    weight = np.where(np.isfinite(weight) & (weight >= 0), weight, 0.0)

    # vec(Z) は Fortran (column-major) で整列 → vec(Z)[i + n_row*j] = Z[i, j]
    w_vec = weight.flatten(order="F")
    y_vec = y.flatten(order="F")

    d_row = _difference_matrix(n_row, diff_order)
    d_col = _difference_matrix(n_col, diff_order)
    p_row = kron(eye(n_col, format="csr"), (d_row.T @ d_row), format="csr")
    p_col = kron((d_col.T @ d_col), eye(n_row, format="csr"), format="csr")

    w_diag = diags(w_vec, 0, format="csr")
    a = (w_diag + lam_row * p_row + lam_col * p_col).tocsc()
    b = w_vec * y_vec
    z_vec = spsolve(a, b)
    return z_vec.reshape((n_row, n_col), order="F")


# ---------------------------------------------------------------------------
# 2. Observed improvement rates (annualized for irregular year grids)
# ---------------------------------------------------------------------------
def compute_annual_improvement(
    rates: np.ndarray,
    years: np.ndarray,
) -> np.ndarray:
    """年率ベースの観測改善率行列を算出。

    年系列が不等間隔 (例: 1950, 1955, ..., 2013, 2014) でも、隣接 2 点間の
    幾何平均改善率に換算する::

        i_annual(x, t_k) = 1 - ( rate(x, t_k) / rate(x, t_{k-1}) )^{1 / (t_k - t_{k-1})}

    Args:
        rates: shape (n_age, n_year) の正値率行列 (NaN/負値可, 無効要素は NaN)
        years: 昇順の年配列 shape (n_year,)

    Returns:
        shape (n_age, n_year) の改善率行列。最初の年列は NaN。
    """
    rates = np.asarray(rates, dtype=float)
    years = np.asarray(years, dtype=float)
    if rates.shape[1] != years.size:
        raise ValueError("years length mismatch with rates columns")
    out = np.full_like(rates, np.nan)
    safe = np.where((rates > 0) & np.isfinite(rates), rates, np.nan)
    year_gaps = np.diff(years)
    if np.any(year_gaps <= 0):
        raise ValueError("years must be strictly increasing")
    ratio = safe[:, 1:] / safe[:, :-1]
    ratio = np.where(ratio > 0, ratio, np.nan)
    annual = 1.0 - ratio ** (1.0 / year_gaps)
    out[:, 1:] = annual
    return out


# ---------------------------------------------------------------------------
# 3. Scale BB core: blend observed improvements with long-term rate
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ScaleBBConfig:
    """Scale BB 拡張モデルの設定.

    `long_term_rate` (L) は原論文通常 1% (= 0.01)。`convergence_year` (P) は
    実績観測終端から先の年次で、`last_observed_year < convergence_year`。
    `cohort_convergence_years` は P と last_observed_year の差分として
    自動算出される。年齢別の長期率テーパ (age_taper_start / age_taper_end)
    を指定すると、指定範囲で L → 0 へ線形低減。
    """

    long_term_rate: float = 0.01
    convergence_year: int = 2035
    last_observed_year: int | None = None
    lam_row: float = 40.0
    lam_col: float = 40.0
    diff_order: int = 2
    age_taper_start: int | None = 90
    age_taper_end: int | None = 120
    horizon_year: int | None = None

    def taper_factor(self, age: int | float) -> float:
        """年齢別の長期率 テーパ係数 (1.0 → 0.0)."""
        if self.age_taper_start is None or self.age_taper_end is None:
            return 1.0
        if age <= self.age_taper_start:
            return 1.0
        if age >= self.age_taper_end:
            return 0.0
        span = max(self.age_taper_end - self.age_taper_start, 1)
        return max(0.0, 1.0 - (age - self.age_taper_start) / span)


def build_blended_improvements(
    smoothed_improvement: np.ndarray,
    years: np.ndarray,
    ages: np.ndarray,
    config: ScaleBBConfig,
) -> tuple[np.ndarray, np.ndarray]:
    """観測平滑化改善率と長期率 L を段階ブレンドした最終改善率を生成。

    原論文 Section 7.4 のブレンド関数 ``h(y)`` をそのまま採用::

        h(y) = 1.0                                 for y <= last_obs
        h(y) = linear( 1.0 → L_age/L ) in [last_obs+1, P-1]
        h(y) = L_age / L                           for y >= P

    投影期間は `last_observed_year+1` から `horizon_year` まで (デフォルトは
    `convergence_year + 15`)。実績期間では平滑化値をそのまま使う。

    Args:
        smoothed_improvement: shape (n_age, n_year) の平滑化済み改善率。
        years: 観測年配列 shape (n_year,)
        ages: 年齢配列 shape (n_age,)
        config: ScaleBBConfig

    Returns:
        (final_improvement, projection_years)  
        final_improvement: shape (n_age, n_project_year) で実績区間も含めた
            全期間改善率。
        projection_years: shape (n_project_year,) で投影対象年（実績 + 将来）。
    """
    ages_arr = np.asarray(ages, dtype=float)
    years_arr = np.asarray(years, dtype=int)
    last_obs = (
        int(config.last_observed_year)
        if config.last_observed_year is not None
        else int(years_arr.max())
    )
    horizon = (
        int(config.horizon_year)
        if config.horizon_year is not None
        else int(config.convergence_year + 15)
    )
    if horizon <= last_obs:
        horizon = last_obs + 1

    full_years = np.arange(int(years_arr.min()), horizon + 1)
    n_age = len(ages_arr)
    out = np.full((n_age, full_years.size), np.nan)

    # 実績区間: 観測年のみ既知。中間年は左隣の観測値で前進充填する (step-forward)
    year_index = {int(y): i for i, y in enumerate(years_arr)}
    last_obs_idx_in_smoothed = year_index[last_obs]
    for j, y in enumerate(full_years):
        y_int = int(y)
        if y_int <= last_obs:
            k = max(i for i in year_index.values() if years_arr[i] <= y_int)
            out[:, j] = smoothed_improvement[:, k]
        else:
            break

    # 観測終端の値 (改善率ベース) を blending の出発点に
    i_last = smoothed_improvement[:, last_obs_idx_in_smoothed]
    l_target = np.array(
        [config.long_term_rate * config.taper_factor(a) for a in ages_arr]
    )

    # 投影期間: linear blend in year domain (論文 Section 7.4 h(y))
    conv_year = int(config.convergence_year)
    for j, y in enumerate(full_years):
        y_int = int(y)
        if y_int <= last_obs:
            continue
        if y_int >= conv_year:
            out[:, j] = l_target
        else:
            denom = max(conv_year - last_obs, 1)
            t = (y_int - last_obs) / denom
            out[:, j] = (1.0 - t) * i_last + t * l_target

    return out, full_years


def project_rates(
    base_rates: np.ndarray,
    improvements: np.ndarray,
    base_year: int,
    years: np.ndarray,
) -> np.ndarray:
    """基準年率 × 改善率で将来率を累積生成。

    Args:
        base_rates: shape (n_age,) の基準年 (``base_year``) の率
        improvements: shape (n_age, n_year) の改善率行列
            列 ``k`` は ``years[k]`` の改善率 i(x, t_k)
        base_year: 基準年（``years[k]==base_year`` で ``m(x, base_year)=base_rates``）
        years: shape (n_year,) の年配列

    Returns:
        shape (n_age, n_year) の投影率行列。
    """
    base_rates = np.asarray(base_rates, dtype=float)
    years = np.asarray(years, dtype=int)
    if base_year not in years:
        raise ValueError(f"base_year {base_year} not in years")
    base_idx = int(np.where(years == base_year)[0][0])

    n_age, n_year = improvements.shape
    out = np.full((n_age, n_year), np.nan)
    out[:, base_idx] = base_rates

    # 前向き累積
    for k in range(base_idx + 1, n_year):
        prev = out[:, k - 1]
        imp = improvements[:, k]
        out[:, k] = prev * (1.0 - imp)
    # 後向き累積
    for k in range(base_idx - 1, -1, -1):
        nxt = out[:, k + 1]
        imp_next = improvements[:, k + 1]
        with np.errstate(divide="ignore", invalid="ignore"):
            out[:, k] = nxt / np.where(
                np.isfinite(1.0 - imp_next) & (1.0 - imp_next != 0),
                (1.0 - imp_next),
                np.nan,
            )
    return out


# ---------------------------------------------------------------------------
# 4. Convenience API: one-shot fit / project
# ---------------------------------------------------------------------------
@dataclass
class ScaleBBFitResult:
    """``fit_scale_bb`` の結果格納用データクラス."""

    ages: np.ndarray
    years: np.ndarray
    rate_observed: np.ndarray  # shape (n_age, n_year) observed rates
    rate_smoothed: np.ndarray  # shape (n_age, n_year) smoothed on log-scale
    improvement_observed: np.ndarray  # annualized observed improvement
    improvement_smoothed: np.ndarray  # smoothed improvement (Phase 1)
    config: ScaleBBConfig = field(default_factory=ScaleBBConfig)

    # 投影段で埋める
    projection_years: np.ndarray | None = None
    improvement_final: np.ndarray | None = None
    rate_projected: np.ndarray | None = None


def fit_scale_bb(
    rate_matrix: np.ndarray,
    ages: Iterable[int | float],
    years: Iterable[int],
    *,
    config: ScaleBBConfig | None = None,
) -> ScaleBBFitResult:
    """観測率行列 (age × year) に対し Scale BB Phase 1 平滑化を実行。

    率は log スケールで平滑化する（正値性を維持し、年齢・期間効果を乗法的に
    扱うため）。0 以下の値は NaN として扱う。

    Args:
        rate_matrix: shape (n_age, n_year) の率 (人口10万対でも無次元でも可)
        ages: 年齢配列
        years: 年配列 (昇順, 不等間隔可)
        config: ScaleBBConfig (None の場合はデフォルト)

    Returns:
        ScaleBBFitResult
    """
    cfg = config or ScaleBBConfig()
    ages_arr = np.asarray(list(ages), dtype=float)
    years_arr = np.asarray(list(years), dtype=int)
    rates = np.asarray(rate_matrix, dtype=float)

    if rates.shape != (ages_arr.size, years_arr.size):
        raise ValueError(
            f"rate_matrix shape {rates.shape} does not match "
            f"({ages_arr.size}, {years_arr.size})"
        )
    if np.any(np.diff(years_arr) <= 0):
        raise ValueError("years must be strictly increasing")

    # log 変換 (0/負は NaN 化して重み 0 扱いにする)
    with np.errstate(divide="ignore", invalid="ignore"):
        log_r = np.where(rates > 0, np.log(rates), np.nan)
    weight = np.where(np.isfinite(log_r), 1.0, 0.0)
    log_r_smoothed = whittaker_henderson_2d(
        log_r,
        weight=weight,
        lam_row=cfg.lam_row,
        lam_col=cfg.lam_col,
        diff_order=cfg.diff_order,
    )
    rate_smoothed = np.exp(log_r_smoothed)

    imp_obs = compute_annual_improvement(rates, years_arr)
    imp_smoothed = compute_annual_improvement(rate_smoothed, years_arr)

    return ScaleBBFitResult(
        ages=ages_arr,
        years=years_arr,
        rate_observed=rates,
        rate_smoothed=rate_smoothed,
        improvement_observed=imp_obs,
        improvement_smoothed=imp_smoothed,
        config=cfg,
    )


def project_scale_bb(
    fit: ScaleBBFitResult,
    *,
    base_year: int | None = None,
) -> ScaleBBFitResult:
    """Phase 2: 長期率ブレンド → 将来率投影。

    ``fit`` の ``projection_years`` / ``improvement_final`` / ``rate_projected``
    を埋めて返す（in-place）。

    Args:
        fit: ``fit_scale_bb`` の結果
        base_year: 投影起点となる基準年 (観測最終年がデフォルト)
    """
    cfg = fit.config
    last_obs = (
        int(cfg.last_observed_year)
        if cfg.last_observed_year is not None
        else int(fit.years.max())
    )
    cfg_effective = ScaleBBConfig(
        long_term_rate=cfg.long_term_rate,
        convergence_year=cfg.convergence_year,
        last_observed_year=last_obs,
        lam_row=cfg.lam_row,
        lam_col=cfg.lam_col,
        diff_order=cfg.diff_order,
        age_taper_start=cfg.age_taper_start,
        age_taper_end=cfg.age_taper_end,
        horizon_year=cfg.horizon_year,
    )
    improvement_final, projection_years = build_blended_improvements(
        fit.improvement_smoothed,
        years=fit.years,
        ages=fit.ages,
        config=cfg_effective,
    )

    base = base_year if base_year is not None else last_obs
    base_rates = fit.rate_smoothed[
        :, int(np.where(fit.years == base)[0][0])
    ].copy()
    rate_projected = project_rates(
        base_rates,
        improvements=improvement_final,
        base_year=base,
        years=projection_years,
    )

    fit.projection_years = projection_years
    fit.improvement_final = improvement_final
    fit.rate_projected = rate_projected
    return fit


__all__ = [
    "ScaleBBConfig",
    "ScaleBBFitResult",
    "whittaker_henderson_2d",
    "compute_annual_improvement",
    "build_blended_improvements",
    "project_rates",
    "fit_scale_bb",
    "project_scale_bb",
]
