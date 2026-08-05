[日本語](README.md) | **English**

# Paper_ICA2026 — Public Paper Manuscript

*English translation of [README.md](README.md) (as of 2026-08-05). If the versions disagree, the Japanese version is authoritative.*

**Public draft repository** for a paper to be submitted to the International Congress of Actuaries (ICA).

**Title:** *Extending Scale BB from All-Cause to Cause-Specific Mortality: A Scenario Generator for Disease-Contingent Insurance under Economic-Value-Based Valuation (ICS/IFRS 17)*

## Role of this directory

- This directory is the **public master copy shared on an ongoing basis with co-authors and reviewers**. It consolidates the clean manuscript text and the environment for verifying its reproduction. Research-side materials, analysis code, and working notes are scattered across `ScaleBB/Research/`, `ScaleBB/BackTest_2015_2024/`, etc., but everything published and shared is unified in this directory.
- The reproduction environment was migrated to this directory on 2026-07-22 from the former `CoAuthor_Share_20260711/05_reproduction/` (generational assumed-rate generation), and has been consolidated under `reproduction/` together with the backtest.
- The chapter structure follows `ScaleBB/Research/docs/Paper_Outline_20260710.md` (the version agreed with co-authors on 2026-07-15).
- Mathematical expressions are written in LaTeX notation (`$...$` / `$$...$$`).
- The working language is a Japanese draft (the final manuscript will be translated into English; see the outline).

## Languages

This repository is maintained bilingually in Japanese and English.

- **Documentation**: each Japanese original `<name>.md` has an English translation `<name>.en.md` next to it (e.g. `README.md` ⇔ `README.en.md`); the language links at the top of each file switch between them. Where the two versions disagree, the **Japanese version is authoritative**. Documents with Japanese filenames use English filenames for their translations (`Scale_BB機能.md` ⇔ `Scale_BB_features.en.md`, `設計書.md` ⇔ `design_document.en.md`).
- **Manuscript**: the Japanese draft lives in `sections/`, the English draft in `sections_en_b1/` (matching filenames).
- **Data and code**: Japanese strings that function as data values (e-Stat category names, column names, etc.) are kept untranslated everywhere; the English documentation adds glosses in parentheses instead.

## Structure

| Path | Contents | Status |
|---|---|---|
| `sections/01_introduction.md` | §1 Introduction (main text). Two shifts (structural change in disease rates; the regulatory environment) → the gap along the disease-risk axis → novelties A/B → the three-stage structure of findings | First draft (2026-07-28) |
| `sections/02_related_work_and_regulatory_requirements.md` | §2 Related work and regulatory requirements (main text) | First draft (2026-07-28) |
| `sections/03_data_and_methodology.md` | §3 Data and methodology (main text) | First draft (2026-07-21) |
| `sections/04_backtest_design.md` | §4 Backtest design (main text) | First draft (2026-07-22) |
| `sections/05_results_point_forecast.md` | §5 Results on point-forecast accuracy (main text) | First draft (2026-07-22) |
| `sections/06_results_directional_accuracy.md` | §6 Findings on directional accuracy (main text). Includes the recalibration experiment for direction-reversing diseases (`reproduction/backtest/make_calibration_recovery_figure.py`) | First draft (2026-07-28) |
| `sections/07_repositioning_scenario_generator.md` | §7 Repositioning as a scenario generator (main text). Implementation correspondence table, comparison with ESGs, and the two-layer application (novelty B) | First draft (2026-07-28) |
| `sections/08_financial_impact_demo.md` | §8 Financial impact demonstration (main text). Reflects the results of the BEL sensitivity demo (simplified Python version, conforming to the ESR implementation specification, `ScaleBB/Research/scripts/bel_demo/`) | First draft (2026-07-28) |
| `sections/09_practical_implementation_guidelines.md` | §9 Practical implementation guidelines (main text). Disease-specific calibration guidance (Table 9.1, consistent with the two-path division of §6.5), five arguments on adoption burden plus a phased adoption path (assuming no observed FMS values), and adoption track record | First draft (2026-07-28) |
| `sections/10_limitations_and_future_work.md` | §10 Limitations and future work (main text). Proxy validity, long-term verifiability (a framework that does not wait for data accumulation), systematization of calibration, re-running production models, and stochastic extensions | First draft (2026-07-28) |
| `sections/11_conclusion.md` | §11 Conclusion (main text). Restates the three-stage structure of results and the two-layer contribution (novelties A/B) | First draft (2026-07-28) |
| `sections/figures/` | Figures included in the main text (§3–§6 generated and collected by `reproduction/backtest/make_paper_figures.py` and others; Figure 8.1 by `ScaleBB/Research/scripts/bel_demo/aggregate_bel_results.py`) | Figures 3.1–3.3, 4.1, 5.1–5.5, 6.1–6.3, 8.1 (2026-07-28) |
| `reproduction/` | **Reproduction packages** for §3–§5 (division of roles explained in `reproduction/README.md`) | — |
| `reproduction/backtest/` | Point-forecast accuracy + directional accuracy (§3.1/3.2/3.4, §5, §6). Self-contained; runnable standalone | Verified working (2026-07-22) |
| `reproduction/generational/` | Generation of APC generational assumed-rate tables (the forward-running pipeline for the APC extension of §3.3; details in `reproduction/generational/README.md`). KDB CLI | Trace-verified (2026-07-15) |

## Reproduction verification (for reviewers and co-authors)

`reproduction/` consists of two complementary packages that reproduce §3. Both share the algorithm core (`_scalebb_core`) and the input mortality data, and their consistency has been verified (see "Consistency between the two packages" in `reproduction/README.md`).

```bash
# Backtest (generates all outputs in output/ within a few minutes)
cd reproduction/backtest && bash run_all.sh

# Generational assumed-rate tables (KDB CLI; details in reproduction/generational/README.md)
cd reproduction/generational/KDB && python -m experience_rate scalebb-apc-fit --use-preset ...
```

For details of each package, the expected key figures, and the modifications from the original scripts, see each README.

## For co-authors and reviewers

Co-authors may commit and push directly to `main` (run `git pull` before pushing).
The author reviews the content when incorporating it into the working repository.
For consultations on direction, or comments where a concrete fix has not yet crystallized, please open an Issue.
See [`CONTRIBUTING.en.md`](CONTRIBUTING.en.md) for details.

## Data sources

The sources and terms of use of the bundled third-party data are consolidated in **[`DATA_SOURCES.en.md`](DATA_SOURCES.en.md)**. The main sources are as follows.

- Vital Statistics (人口動態調査), Ministry of Health, Labour and Welfare, via e-Stat (政府統計の総合窓口) — the primary input of this study (cause-specific mortality rates)
- Patient Survey (患者調査), Ministry of Health, Labour and Welfare, via e-Stat (政府統計の総合窓口) — reference series based on consultation rates and average length of stay
- Cancer Statistics (がん統計), Cancer Information Service, National Cancer Center Japan (National Cancer Registry, 全国がん登録) — incidence-rate benchmark
- The Institute of Actuaries of Japan (公益社団法人日本アクチュアリー会), Standard Life Tables 1996 / 2007 / 2018 — validation of the input data

The repository license does not extend to the third-party data above. See `DATA_SOURCES.en.md` for details and the English citation text.

## Sources of material

Each subsection of §3 is based on the following (source documents for the clean copy):

- Data and panel specification: `ScaleBB/BackTest_2015_2024/docs/report.md` §2
- ScaleBB algorithm: `ValidationTools/KDB/src/experience_rate/_scalebb_core/model.py`, `report.md` §3
- APC extension: `ScaleBB/Research/docs/methodology_apc_extension_20260422.md`
- Baselines and evaluation metrics: `report.md` §3.3–3.4, §8.1
