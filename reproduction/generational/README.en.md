[日本語](README.md) | **English**

# generational — Expected Incidence Rate Table Generation Scripts and Traceable Verification Environment

*English translation of [README.md](README.md) (as of 2026-08-05). If the versions disagree, the Japanese version is authoritative.*

> This package is part of `Paper_ICA2026/reproduction/` (migrated on 2026-07-22 from the former
> `CoAuthor_Share_20260711/05_reproduction/`). It corresponds to the reproduction of paper **§3.3 (APC extension)**
> and to its forward-looking runtime, the generational projection (generation of per-issue-year assumed-rate tables;
> not treated as a chapter of the main text and explained in this README instead).
> It shares the algorithm core with its sister package `../backtest/` (point-forecast accuracy and directional accuracy, §3.4/§5/§6),
> and together the two reproduce all of §3. For the overall division of roles, see `../README.md`.

This is the full pipeline for generating **expected disease incidence rate tables** with ScaleBB (APC extension),
bundled so that co-authors can re-run and trace-verify it on their own machines.
On 2026-07-15, a full reproduction run was performed on a copy of this directory,
and the outputs were confirmed to match the reference outputs (see §5).

## 1. Important Note on Data Provenance (to Prevent Misunderstanding)

- **The input data for the assumed incidence rate tables is disease-specific mortality from the e-Stat Vital Statistics (人口動態統計)**
  (`KDB/data/processed/mortality_apc_panel.parquet`; mortality rates are used as a proxy for incidence rates).
- **The data originating from the National Cancer Center = National Cancer Registry (NCR) incidence rates**
  (`KDB/data/RowData/cancer_incidenceNCR(2016-2023).xls`; source: National Cancer Center
  Cancer Information Service, "Cancer Statistics" (National Cancer Registry)) are
  **not** an input to the assumed-rate tables; they are used as the **highest-quality (A-tier) benchmark** of true incidence
  (`KDB/scripts/build_cancer_registry_panel.py` converts them into an incidence panel → stored in `population_incidence`
  with `rate_type='registry'`). The bundled `.xls` is the original file downloaded from the provider, unmodified;
  the post-panelization figures are derived products of this research (the provider bears no responsibility for the processed results).
- Quantification of the divergence between the mortality-based assumed rates and the cancer-registry incidence rates is
  recorded as **future work** in specification `docs/apc_predicted_rate_tables_by_sex_20260423.md` §B.9.
- **On terminology (supplementary note accompanying the 2026-07-15 retitling):** the "assumed incidence rate tables" produced by
  this pipeline are, in substance, rate tables computed from **cause-of-death mortality rates** (per 100,000 population). In the
  paper's (post-retitling) framework, these cause-of-death mortality rates are used in two layers: **(i) as a proxy for medical-insurance
  disease incidence rates**, and **(ii) as the direct target itself (the direct assumption) for critical-illness death benefits**.
  The "incidence" wording in file names and legacy labels is product-side naming; please note that the inputs and computations
  are consistently cause-of-death mortality rates
  (since the algorithm is agnostic to the meaning of its input, the reproduction results and figures are unchanged).

## 2. Layout

| Path | Contents |
| --- | --- |
| `KDB/` | Runtime environment (a copy of the self-contained SQLite + Python application). Includes scripts, algorithm core, configuration, and input data |
| `KDB/scripts/build_cancer_registry_panel.py` | **Cancer registry (NCR) → incidence panel** conversion script |
| `KDB/data/lifetable/seimeihyo960718.xlsx` | Standard life tables (source: the 7 series of "Standard Life Tables 1996 / 2007 / 2018" published by The Institute of Actuaries of Japan (公益社団法人日本アクチュアリー会), bundled into a single workbook). Used for validity checks of the input data (§4.3) |
| `KDB/src/experience_rate/_scalebb_core/` | ScaleBB / APC algorithm core (2D Whittaker-Henderson, cohort penalty, generational projection) |
| `KDB/config.yaml` | Parameter presets (currently in the **age-20-start (age20)** configuration state) |
| `docs/apc_predicted_rate_tables_by_sex_20260423.md` | **Specification and process document**: purpose, inputs, full pipeline diagram, all reproduction commands, result summary |
| `docs/age20_pipeline_migration_20260423.md` | Background and configuration changes for the age-20-start extension |
| `reference_output/` | **Reference outputs for trace verification** (a snapshot of the current artifacts generated on the research side) |
| `reference_output/predicted_rate_apc/` | APC assumed-rate tables (issue_age=40, issue years 2024–2028) |
| `reference_output/predicted_rate_apc_age20/` | APC assumed-rate tables (issue_age=20) |
| `reference_output/predicted_rate_tables/` | Legacy AP version (for comparison) |
| `reference_output/scalebb_apc_*.parquet etc.` | Intermediate artifacts of fit / projection |

Repository originals: `KDB` is from `ICA/ValidationTools/KDB/`, and the specification documents are from `ICA/ScaleBB/Research/docs/`.
To reduce size, the raw e-Stat data (`estat_api/`, `estat_processed/`, ~235MB) is not bundled
(the pre-built panels are bundled in `KDB/data/processed/`).

> **On the exclusion of the experience-rate (A/E) analysis features**
> This research uses no actual in-force, movement, or claims data whatsoever,
> and does not use experience-rate (A/E) analysis. Therefore the following features of the
> original `KDB` are **excluded from this distribution**. What is bundled is only the path
> that takes population statistics (e-Stat / National Cancer Registry) as input.
>
> - Individual medical insurance importers (the `ins_*` tables, `import-validate` / `import-table` /
>   `import-all` / `import-history`, YAML mapping definitions)
> - Experience-rate and benchmark analysis (`analyze` / `analyze-benchmark`)
> - Web UI / REST API (`serve`, the FastAPI stack)
> - Sample policy data generation (`generate_medical_sample.py` / `generate_lapse_sample.py`)
>
> To consult these features in the original, see `ICA/ValidationTools/KDB/`.

## 3. Setup

Python 3.11+ is assumed. Everything is run directly under the `KDB/` directory.

```bash
cd Paper_ICA2026/reproduction/generational/KDB
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=src

python -m experience_rate init --drop   # Initialize the SQLite schema
```

> The command examples in the specification document use PowerShell notation (`` ` `` line continuation, `$env:PYTHONPATH`)
> and the old directory layout (`../data/processed/...`). In this environment, read them as bash +
> KDB-relative paths (`data/processed/...`) — the steps below are already converted.

## 4. Reproduction Procedure

### 4.1 Expected Incidence Rate Tables (APC Version, Both Sexes × 3 Diseases)

```bash
# (1) APC fit (2D WH smoothing + cohort penalty + COVID dummies)
python -m experience_rate scalebb-apc-fit --source mortality --sex male \
  --disease cancer heart_disease cerebrovascular --use-preset --run-id male_repro

# (2) projection (improvement rate × long-term rate L blend, up to 2100)
python -m experience_rate scalebb-apc-project \
  --fit data/processed/scalebb_apc_fit_male.parquet --use-preset --run-id male_repro_proj

# (3) generational projection tables (per-issue-year 1D [age], log-linear single-age interpolation)
python -m experience_rate scalebb-gen-table --run-id male_repro_proj --use-preset \
  --output-dir data/processed/predicted_rate_repro

# For female, run the same with --sex female / the female fit file name
```

**Note**: the bundled `config.yaml` is in the **age20 preset** state (`age_min=20, issue_age=20, lam_col=60`).
Outputs under this configuration correspond to `reference_output/predicted_rate_apc_age20/`.
To reproduce the issue_age=40 version (`reference_output/predicted_rate_apc/`), either restore `config.yaml`
to the age-40-start parameters of specification §4.1 (`age_min=40, lam_col=40, issue_age=40`),
or specify them explicitly via CLI arguments.

### 4.2 Building the Cancer Registry (National Cancer Center NCR) Panel

```bash
python scripts/build_cancer_registry_panel.py                    # Standalone run (prints row counts and breakdown)
python scripts/build_cancer_registry_panel.py --output data/processed/registry_panel.csv
python -m experience_rate load-incidence                          # Load the bundled incidence_panel into the DB
python -m experience_rate export-incidence --rate-type registry \
  --output output/registry_rates.csv                             # Export incidence rates to CSV with filters
```

Incidence rates derived from the cancer registry (NCR) are stored in `population_incidence` with `rate_type='registry'`,
`quality_flag='A'` (as stated in §1, they are not an input to the assumed-rate tables but the highest-quality benchmark
of true incidence). Since this reproduction environment contains no policy data,
no A/E comparison against experience rates is performed (see the note in §2).

> **Note on the panel rebuild scripts**: `scripts/build_incidence_panel.py` /
> `build_los_panel.py` / `build_discharge_panel.py` / `build_initial_visit_panel.py` take as input the raw e-Stat data
> (`data/RowData/estat_processed/`, **not bundled** for size reasons as stated in §2).
> If run without it, the corresponding sub-builders return 0 rows, so to avoid overwriting the bundled panels
> with degenerate versions, `build_incidence_panel.py` and `build_los_panel.py` abort the write
> (use `--force` only if you intend to overwrite). The bundled panels can be used as-is,
> so the normal reproduction procedure does not require re-running these.

### 4.3 Consistency Check Against the Standard Life Tables (Validity Check of the Input Data)

```bash
python scripts/analyze_standard_life_table.py
```

This cross-checks the standard life tables published by The Institute of Actuaries of Japan
(`data/lifetable/seimeihyo960718.xlsx`; the 7 series of the Standard Life Tables for life insurance 1996 / 2007 / 2018
and the Standard Life Tables for the third sector 2007 / 2018; the unprocessed source data are the Institute's published
"Standard Life Table 1996", "Standard Life Table 2007", and "Standard Life Table 2018")
against the cause-of-death mortality rates from the e-Stat Vital Statistics that serve as this pipeline's input
(`population_incidence`, `rate_type='mortality'`), and computes `ratio = population_rate / standard_rate`.
The actuarial expectation is `ratio < 1` for the death-benefit tables (due to safety loading) and `ratio > 1`
for the post-commencement annuity tables; agreement with the expected sign is shown as `[OK]`
in `[5] 妥当性チェック` (validity check) (the third-sector tables are `[REF]` = reference values, being incidence-rate concepts).

This is a validity check of the input data that is **independent of the generation path of the assumed incidence rate tables**;
the reproduction results of §4.1 are unchanged whether or not this script is run.
Outputs are saved to `output/standard_vs_population_{band10,detail}.csv`,
`standard_vs_population_judgement.csv`, `standard_life_table_tidy.csv`, and
`disease_breakdown_std2018_male_40_59.csv`.
Note that because it references `population_incidence`, run `load-incidence` of §4.2 first.

## 5. Trace Verification Method (Already Performed)

Compare the reproduction outputs against `reference_output/`.

```bash
diff data/processed/predicted_rate_repro/predicted_rate_cancer_male_issue2026_ia20.csv \
     ../reference_output/predicted_rate_apc_age20/predicted_rate_cancer_male_issue2026_ia20.csv
```

**Verification result of 2026-07-15**: in this copied environment, `init → scalebb-apc-fit (cancer, male) →
scalebb-apc-project → scalebb-gen-table` was executed and `predicted_rate_cancer_male_issue2026_ia20.csv`
was compared against the reference output. **All 46 rows matched to about 15 significant digits**
(relative difference ~1e-15; differences only in the last digit, attributable to floating-point operation ordering).
The artifacts of this verification run
(`KDB/experience_rate.db`, `KDB/data/processed/scalebb_apc_fit_male.*` /
`scalebb_apc_projection_male.*`, `KDB/data/processed/predicted_rate_verify/`) have been
left in place as-is. To re-run from scratch, rebuild the DB with `init --drop`.

Other verification means:

- `python -m experience_rate scalebb-runs --last 10` — audit of the run history and parameters (config_json)
- Intermediate fit / projection values can be compared against `reference_output/scalebb_apc_*.parquet`
- Expected DB schema and record counts are given in specification §6.1 / §B.4

## 6. Where to Find the Scripts' Specifications and Purposes

| What you want to know | Where to look |
| --- | --- |
| Pipeline purpose, inputs, overall diagram, parameters, results | `docs/apc_predicted_rate_tables_by_sex_20260423.md` |
| Motivation and configuration diff of the age-20-start extension | `docs/age20_pipeline_migration_20260423.md` |
| Mathematical formulation (APC, identifiability) | `../../../ScaleBB/Research/docs/methodology_apc_extension_20260422.md` (corresponds to paper §3.3) |
| CLI in general, DB schema | `KDB/README.md`, `KDB/docs/Scale_BB機能.md` |
| I/O specification of the NCR panelization | Docstring at the top of `KDB/scripts/build_cancer_registry_panel.py` |
