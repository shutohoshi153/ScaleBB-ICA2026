[日本語](README.md) | **English**

# backtest — §3 Backtest Reproduction Package

*English translation of [README.md](README.md) (as of 2026-08-05). If the versions disagree, the Japanese version is authoritative.*

This directory is a self-contained package for **standalone reproduction and verification** of the **backtest** (point-forecast accuracy and directional accuracy) in paper §3 "Data and Methods". It regenerates everything in one shot, from the raw Vital Statistics table 5-15 through all artifacts for point-forecast accuracy (§5) and directional accuracy (§6).

It has no dependency on any other directory in the repository (input data and the algorithm core are all bundled).

For a detailed explanation of what each script does (inputs, processing, outputs), see [SCRIPTS.en.md](SCRIPTS.en.md).

> One of the two packages under `Paper_ICA2026/reproduction/`. It shares the algorithm core and input mortality data
> with its sister package `../generational/` (APC generational assumed-rate generation, §3.3; details in `../generational/README.md`).
> For the overall division of roles and consistency, see `../README.md`.

---

## Quick Start

```bash
# Use the repository .venv (recommended; pandas/numpy/scipy/matplotlib included)
bash run_all.sh

# Specify a Python interpreter explicitly
PY=/path/to/python bash run_all.sh
```

It completes in a few minutes, and all artifacts are generated under `./output/`.

**Dependencies:** Python 3.10+ and `pandas` / `numpy` / `scipy` / `matplotlib` only.

---

## Package Layout

```
backtest/
├── run_all.sh                       One-shot reproduction driver (full §3 pipeline)
├── _paths.py                        Self-contained path layer (see "Modifications from the Original Scripts" below)
├── build_panel.py                   [1] Table 5-15 → disease panel (§3.1)
├── run_backtest.py                  [2] ScaleBB fit/project + validation (§3.2)
├── run_baselines.py                 [3] naive/mean_3pts/loglin baselines (§3.4.1)
├── compute_directional_accuracy.py  [4] Directional accuracy DA (§3.4.2, Eqs. 3.11–3.12)
├── compare_cutoffs.py               [5] Cross-comparison over 3 cutoffs (§4)
├── make_calibration_recovery_figure.py  [6] Recalibration experiment for direction-reversal diseases (§6.5, Fig. 6.3)
├── make_paper_figures.py            [7] Generation and collection of paper figures (→ ../../sections/figures/)
├── vendor/
│   └── experience_rate/_scalebb_core/
│       ├── model.py                 Scale BB core (§3.2, Eqs. 3.1–3.6). Bundled unmodified from KDB
│       └── apc_model.py             APC extension (§3.3, Eqs. 3.7–3.8). Bundled for reference
├── data/
│   ├── raw/5-15_…_0003411659.csv    Input: Vital Statistics table 5-15 (1950–2024)
│   ├── disease_estat_mapping.csv    Disease → cause-of-death code mapping (§3.1.2)
│   └── prebuilt_disease_panel_mortality.csv   Expected output of build_panel (for cross-checking)
└── output/                          [Generated] Rebuilt by run_all.sh (not under git)
```

## Execution Order and Correspondence to §3

`run_all.sh` follows the reproduction procedure in the report and runs the following in order.

| Step | Script | Artifacts | Correspondence to §3 |
|---|---|---|---|
| 1 | `build_panel.py` | `data/disease_panel_mortality.csv` (8 diseases × 3 sexes × 25 years × 21 ages = 12,600 rows) | §3.1 data and disease mapping |
| 2 | `run_backtest.py` (cutoffs 2014/2021/2022) | `output[/cutoff_*]/tables/validation_summary.csv` etc. | §3.2 ScaleBB fit/project, Eqs. (3.1)–(3.6) |
| 3 | `run_baselines.py` (same 3 cutoffs) | `output[/cutoff_*]/tables/validation_summary_baseline.csv` etc. | §3.4.1 baselines, §3.4.2 MAPE/bias (Eqs. 3.9–3.10) |
| 4 | `compare_cutoffs.py` | `output/cutoff_comparison/` | §4 validation design (across the 3 cutoffs) |
| 5 | `compute_directional_accuracy.py` | `output/directional/` | §3.4.2 directional accuracy DA (Eqs. 3.11–3.12) → §6 |
| 6 | `make_calibration_recovery_figure.py` | `output/directional/tables/calibration_recovery.csv`, Fig. 6.3 (committed) | §6.5 recalibration experiment for direction-reversal diseases (liver / hypertensive; re-setting L and P × cutoff) |
| 7 | `make_paper_figures.py` | `../../sections/figures/` (committed) | Generation of the explanatory figures for §3 and §4 of the main text, and collection of the result figures referenced by §5 and §6 |

## Expected Key Figures (Ground Truth for Cross-Checking)

Whether the reproduction ran correctly can be checked against the following representative values (`sex=total`, cutoff=2014). All of them match the tables in paper §5 and §6.

**ScaleBB MAPE [%]** (`output/cutoff_comparison/tables/scalebb_cutoff_comparison.csv`)

| disease | 2014 | 2021 | 2022 |
|---|---:|---:|---:|
| cancer | 22.41 | 9.20 | 8.87 |
| total | 26.01 | 9.33 | 7.33 |
| hypertensive | 73.83 | 24.13 | 20.53 |

**Directional accuracy DA [%]** (`output/directional/tables/directional_summary.csv`, cutoff=2014)

| disease | scalebb | naive_last | loglin_trend |
|---|---:|---:|---:|
| total | 95.00 | 0.00 | 94.29 |
| cerebrovascular | 91.04 | 0.00 | 91.04 |
| cancer | 79.71 | 0.00 | 93.48 |

The DA of `naive_last` is 0.00 in every cell because, by construction, $\Delta_{\text{pred}} \equiv 0$ (Eq. 3.11) and it carries no directional information — exactly the behavior described in §3.4.2.

## Modifications from the Original Scripts (Stated for Transparency)

The 5 bundled scripts make **no change whatsoever to the algorithm, aggregation, or plotting logic** of the research-side `ScaleBB/BackTest_2015_2024/scripts/`. The only modifications are the **few path-anchor lines at the top of each file**:

- Originally, `ROOT = Path(__file__).resolve().parents[2]` walked up to the repository root and referenced `KDB/src`, `ScaleBB_Research/data/raw`, and `MedicalInsuranceProduct/`. These were invalidated by the 2026-07 repository reorganization.
- In this package, the input data and algorithm core are bundled, and paths are resolved in a single place, `_paths.py`. Each modified location in the scripts is marked with a `# [REPRO]` marker.

`vendor/experience_rate/_scalebb_core/` is an **unmodified copy** from KDB (`ValidationTools/KDB/src/experience_rate/_scalebb_core/`), and is the very implementation corresponding to the equations in §3.2/§3.3.

## Data Sources and License

- **Vital Statistics table 5-15** (statistics table ID 0003411659): source **Ministry of Health, Labour and Welfare, "Vital Statistics" (人口動態調査) (portal site of official statistics of Japan, e-Stat)**. Commercial use is permitted with attribution under the Government of Japan Standard Terms of Use (Version 2.0).
- For the list of sources and terms of use of the bundled third-party data, see `../../DATA_SOURCES.md`.
- This package is an academic validation based on public data and does not guarantee the profitability or capital requirements of any specific product (see paper §10).
