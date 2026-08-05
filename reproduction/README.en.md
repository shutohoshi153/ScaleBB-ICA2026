[日本語](README.md) | **English**

# reproduction — §3 Reproduction Packages (for Reviewers and Co-authors)

*English translation of [README.md](README.md) (as of 2026-08-05). If the versions disagree, the Japanese version is authoritative.*

This directory packages the validation pipeline of paper §3 "Data and Methods" in a form that can be reproduced and verified standalone.
It consists of **two complementary packages**, which together cover all of §3.

```
reproduction/
├── README.md        ← This file (division of roles and consistency)
├── backtest/        Point-forecast accuracy + directional accuracy validation   (§3.1 / §3.2 / §3.4 / §5 / §6)
└── generational/    APC generational assumed-rate table generation             (§3.3; details in generational/README.md)
```

## Division of Roles Between the Two Packages

| Package | What it reproduces | Runtime | Input | Main outputs |
|---|---|---|---|---|
| **`backtest/`** | Backtest: point-forecast MAPE (Eqs. 3.9–3.10) and directional accuracy DA (Eqs. 3.11–3.12) for 3 cutoffs × ScaleBB × 3 baselines | Standalone scripts (`run_all.sh`) | Vital Statistics table 5-15 (bundled) | Validation tables and figures under `output/` |
| **`generational/`** | APC fit/project → per-issue-year 1D assumed-rate tables (generational projection) | KDB CLI (`experience_rate`) | `mortality_apc_panel` (bundled) | Assumed-rate tables to be checked against `reference_output/` |

`backtest/` tests "whether Scale BB is suited to point forecasting" (conclusion: it loses on MAPE but gets the direction right),
while `generational/` covers the stage of "running the improvement-rate framework forward to produce rate tables in a practice-ready distribution format."
Their scopes do not overlap.

## Consistency Between the Two Packages (Verified, 2026-07-22)

The following checks confirm that the shared directory is free of contradictions.

1. **Identical algorithm core**: `backtest/vendor/experience_rate/_scalebb_core/` and
   `generational/KDB/src/experience_rate/_scalebb_core/` are **bit-identical** (and also match the current KDB).
   Both packages use the same Scale BB / APC implementation (§3.2 Eqs. 3.1–3.6, §3.3 Eqs. 3.7–3.8).
2. **Identical input mortality data**: both start from cause-of-death mortality rates from the e-Stat Vital Statistics (人口動態統計).
   For the shared cells (cancer / cerebrovascular / heart / hypertensive / total), an **exact match** (difference 0) was confirmed.
3. **Common two-layer framing of the data**: cause-of-death mortality rates are used as (i) a proxy for medical-insurance
   incidence rates and (ii) the direct target of critical-illness death benefits (§3.1.3 and generational README §1).
4. **Common core hyperparameters**: `long_term_rate=0.01`, `convergence_year=2035`,
   `lam_row=40`, `diff_order=2`.

### Differences in Settings and Notation (Use-Case Differences, Not Contradictions)

| Item | `backtest/` | `generational/` | Notes |
|---|---|---|---|
| `lam_col` (calendar-year smoothing) | 40 | 60 | backtest uses the KDB default (consistent with the BackTest report). generational uses 60 to suppress young-age noise after the age20 migration. Each is justified for its own use case (see the footnote in §3.2.3) |
| Age range | 20–89 | 20–85 (age20 preset) | Minor setting-dependent difference |

> The disease slug is unified as `heart_disease` (Hi05, heart diseases excluding hypertensive) in both packages.

## Usage

```bash
# Backtest (regenerates all artifacts in a few minutes)
cd backtest && bash run_all.sh

# Generational assumed-rate tables (KDB CLI; details in generational/README.md §3–4)
cd generational/KDB && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && export PYTHONPATH=src
python -m experience_rate scalebb-apc-fit --source mortality --sex male \
  --disease cancer heart_disease cerebrovascular --use-preset --run-id male_repro
```

For each package's details, expected key figures, and modifications, see the respective `backtest/README.md` /
`generational/README.md`.

## Data Sources

Attribution and terms of use for the third-party data bundled with both packages (Vital Statistics and Patient Survey / e-Stat,
National Cancer Registry / National Cancer Center, Standard Life Tables / The Institute of Actuaries of Japan) are
consolidated in `../DATA_SOURCES.md`.
