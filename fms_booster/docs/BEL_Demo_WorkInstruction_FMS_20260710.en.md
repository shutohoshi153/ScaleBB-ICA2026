[日本語](BEL_Demo_WorkInstruction_FMS_20260710.md) | **English**

# Work Instruction: BEL Sensitivity Demo (Paper §8) — FMS Booster Execution Version

*English translation of [BEL_Demo_WorkInstruction_FMS_20260710.md](BEL_Demo_WorkInstruction_FMS_20260710.md) (as of 2026-08-05). If the versions disagree, the Japanese version is authoritative. Parts of this instruction (§5, §7) have been refined and superseded by [FMS_BoosterRunCases_Tier1_20260805.en.md](FMS_BoosterRunCases_Tier1_20260805.en.md).*

**Created:** 2026-07-10
**Purpose:** For §8 "Financial Impact Demonstration" of the ICA paper, demonstrate ScaleBB's scenario-generation capability (L ±50bp, etc.) on the production projection model (FMS Booster), and produce a single table and a figure of BEL (present value of benefits) sensitivity by model point.
**Related documents:** `Paper_Outline_20260710.md` (paper outline), `../../BackTest_2015_2024/docs/report.md` §9 (theoretical basis for scenario generation)
**Prerequisites already confirmed:**
- Permission obtained from the vendor (FMS Booster) for use in paper validation
- Agreed policy: keep `Base_Model_v251208/` unmodified and edit a copy

---

## 0. Governance (do this first)

- [ ] Copy `ValidationTools/BoosterFMS/Base_Model_v251208/` to `ValidationTools/BoosterFMS/Scenario_Model_BELDemo/`. **Do not touch the original in any way**
- [ ] Update `ValidationTools/BoosterFMS/CLAUDE.md`:
  - Revise the "Read-only reference" statement to: "`Base_Model_v251208/` is reference-only (unmodified). `Scenario_Model_BELDemo/` is a modified copy for the BEL sensitivity demo and may be edited"
  - Add a note that vendor permission for use in paper validation has been obtained
- [ ] Make all modifications only under `Scenario_Model_BELDemo/`, and keep the state such that differences from the original can be tracked with `diff`

---

## 1. Overall Architecture (3-layer pipeline)

```
[Python layer (1)] ScaleBB core (reusing the existing fit)
             → generate projected rate surfaces for 5 scenarios × 3 diseases
             → expand cohort diagonals (x0+t, 2026+t) into duration-specific rates
             → load scenario rate tables into DB_ASSUMP
      ↓
[FMS layer]  Scenario_Model_BELDemo reads TBL_CLAIM_SCN per scenario,
             computes PVs → outputs with SCN_CD attached
      ↓
[Python layer (2)] aggregate FMS output → the table (CSV) + bar chart (PNG) for paper §8
```

**Design principles:**
1. The cohort-diagonal transformation (calendar year × attained age → duration-specific rates) is **precomputed on the Python side**. Rates are passed to FMS as conventional-format "duration-specific claim rates", minimizing FMS modifications
2. The FMS calculation core (`C01`–`C04`) is **left unmodified**. This backs up, in its FMS implementation, the paper §7 claim that "differences between scenarios reduce solely to differences in assumptions"
3. All assumptions other than claim rates (lapse, expense, commission) are common to all scenarios and are not changed

---

## 2. Scenario Definitions (5 scenarios)

| SCN_CD | Scenario name | long_term_rate (L) | Additional rate operation | Role in the paper |
|---|---|---|---|---|
| `BASE` | Base | 0.010 (1.0%) | None | Current default |
| `UP50` | Trend Up | 0.015 (1.5%) | None | IFRS 17 sensitivity +50bp |
| `DN50` | Trend Down | 0.005 (0.5%) | None | IFRS 17 sensitivity −50bp |
| `ICS_T` | ICS Trend shock | 0.000 (0.0%) | None | ICS zero-improvement stress |
| `ICS_C` | ICS Trend+Level | 0.000 (0.0%) | Multiply rates uniformly ×1.125 | ICS combined stress |

Common parameters (fixed across all scenarios): `convergence_year=2035`, `lam_row=40, lam_col=40, diff_order=2`, `age_taper_start=90, age_taper_end=120` (per KDB `config.yaml > scalebb_presets > defaults`). Since the Phase 1 fit does not depend on L, **run the fit only once and re-run only Phase 2 (project) per scenario**.

## 3. Model Point Definitions (8 points)

| MP_ID | Issue age x0 | Sex | Issue year | Coverage |
|---|---|---|---|---|
| MP01–MP04 | 30 / 40 / 50 / 60 | Male | 2026 | Three major diseases lump-sum benefit JPY 1,000,000 (on first occurrence), maturing at age 90 |
| MP05–MP08 | 30 / 40 / 50 / 60 | Female | 2026 | Same as above |

**Other assumptions:** lapse rate fixed at 2% per year (common to all scenarios), discount rate flat 1.5% (common to all scenarios), mortality decrements use the all-cause projected rates (fixed at the BASE L, common to all scenarios — so that the sensitivity reduces solely to disease incidence rates). The benefit-triggering diseases are cancer (cancer), heart disease (heart_broad), and cerebrovascular disease (cerebrovascular), mapped in `BNFT_Q` as one benefit item per disease.

**Note (consistent with paper §3 and §10):** the rates are mortality proxies (derived from Vital Statistics 5-15), not direct estimates of incidence rates. The purpose of the demo is to show "direction and order of magnitude".

---

## 4. Python Layer (1) — Scenario Rate Generation and DB Load

### 4.1 Script: scenario rate generation

**File name:** `ScaleBB/Research/scripts/bel_demo/build_scenario_claim_rates.py`

```python
# [Purpose] Reuse ScaleBB's existing fit, swapping only long_term_rate, to
#         generate projected rates for 5 scenarios × 3 diseases (+ all-cause),
#         and expand each model point's cohort diagonal into duration-specific rates
#
# [Inputs]
#   - ScaleBB/BackTest_2015_2024/data/disease_panel_mortality.csv (rate panel)
#   - fit_scale_bb / project_scale_bb / ScaleBBConfig from the KDB vendored core
#
# [Processing]
#   1. For each target disease (cancer, heart_broad, cerebrovascular) × sex (male, female),
#      run fit_scale_bb once (full period 1950-2024, last_observed_year=2024)
#   2. For each L in the scenario table (§2), re-run project_scale_bb and
#      generate the rate surface m(x, t) up to horizon_year=2086 (issue 2026 + 60-year term)
#   3. For ICS_C, multiply the ICS_T rates uniformly by 1.125
#   4. For each model point (x0 ∈ {30,40,50,60}), read out the cohort diagonal:
#        rate[dur] = m(x0 + dur, 2026 + dur)   dur = 0 .. (90 - x0 - 1)
#   5. Convert per-100k → rates (decimals) and shape into TBL_CLAIM_SCN-compatible records
#
# [Outputs]
#   - data/processed/bel_demo/scn_claim_rates.csv
#     Columns: SCN_CD, BNFT_Q, GNDR_CD, ISSUE_AGE, DUR, ASSM_RT
#   - data/processed/bel_demo/scn_mortality_rates.csv (all-cause, fixed at BASE; same format)
#   - For cross-checking: data/processed/bel_demo/rate_surface_{disease}_{sex}_{scn}.csv
```

**Acceptance criteria:**
- [ ] `BASE` rates are order-of-magnitude consistent with the existing `predicted_rate_apc/` and back-test artifacts (spot-check at least 3 points)
- [ ] No missing combinations across all (SCN, BNFT_Q, GNDR, ISSUE_AGE, DUR); rates lie within (0, 1)
- [ ] Machine-check that scenarios with larger L have lower future rates (accelerated improvement)

### 4.2 Script: DB load

**File name:** `ScaleBB/Research/scripts/bel_demo/load_scenario_to_db.py`

```python
# [Purpose] Load the scenario rates into the FMS assumption DB (DB_ASSUMP)
#
# [Approach] Leave the existing TBL_CLAIM unchanged. Create a new table TBL_CLAIM_SCN (Approach A)
#
# [Proposed table schema] TBL_CLAIM_SCN
#   SCN_CD   TEXT    -- scenario code (BASE/UP50/DN50/ICS_T/ICS_C)
#   PROD_GRP TEXT    -- product group (fixed to 'BELDEMO' for the demo)
#   BNFT_Q   INTEGER -- benefit item (1=cancer, 2=heart_broad, 3=cerebrovascular)
#   GNDR_CD  TEXT    -- sex code (match the coding scheme of the existing TBL_CLAIM)
#   CHN_CD   TEXT    -- channel (fixed to any one existing value)
#   BAS_YM   TEXT    -- base year-month (match the existing coding scheme, e.g. '202601')
#   ISSUE_AGE INTEGER-- issue age (30/40/50/60)
#   DUR      INTEGER -- duration (elapsed years or elapsed months; match the granularity of the existing TBL_CLAIM)
#   ASSM_RT  REAL    -- assumed rate
#   PRIMARY KEY (SCN_CD, PROD_GRP, BNFT_Q, GNDR_CD, CHN_CD, BAS_YM, ISSUE_AGE, DUR)
#
# [Cautions]
#   - Be sure to verify the actual schema of the existing TBL_CLAIM (column names, key granularity,
#     monthly/annual) against the real thing, and adjust the proposal above to the actual schema
#   - Back up the existing DB before making changes. Restrict DROP/DELETE to the new table only
#   - If model point definitions are needed (registering the BELDEMO product group in TBL_PROD_MAP etc.),
#     load them at the same time
```

**Acceptance criteria:**
- [ ] A pre-change DB backup exists
- [ ] Loaded record count = 5 scenarios × 3 benefits × 2 sexes × 4 issue ages × number of durations
- [ ] Record counts and checksums of existing tables are unchanged before and after

---

## 5. FMS Layer — Modifications (4 modules, minimally invasive)

Scope: only under `ValidationTools/BoosterFMS/Scenario_Model_BELDemo/` (the copy).

### 5.1 `General_Modules/__import_GParams.txt` / `A04_Set_Param.txt`

- [ ] Add the following global parameters:
  - `GParam.SCN_CD` (the scenario code currently being executed)
  - `GParam.SCN_List` (array of scenarios to run: BASE, UP50, DN50, ICS_T, ICS_C)
  - `GParam.TBL_CLAIM_SCN` (scenario rate table name)
- Add Japanese comment headings such as "BELデモ用シナリオパラメータ" (scenario parameters for the BEL demo) so the modified locations are searchable (recommended marker: `' [BELDEMO]`)

### 5.2 `IXP_Prot/A01_Main.txt`

- [ ] Add a scenario loop **outside** the Cell loop (pseudocode):

```vb
' [BELDEMO] Scenario loop: compute all Cells for each scenario in SCN_List
For scn_i = 1 To UBound(GParam.SCN_List)
    GParam.SCN_CD = GParam.SCN_List(scn_i)
    ' --- Below, run the existing Cell loop (Import_Cell_Data → calculation → Output) as-is ---
Next scn_i
```

- If the existing `Map_Scn_Idx` mechanism is used for economic scenarios such as interest rates, do **not** reuse it; add an independent loop instead (to avoid conflating roles). Decide after reading the implementation of `Map_Scn_Idx`, and record the rationale in the commit message

### 5.3 `IXP_Prot/B05_Import_Assumption.txt`

- [ ] Switch the reference table of `Import_claim_Ratio` from `TBL_CLAIM` to `GParam.TBL_CLAIM_SCN`
- [ ] Add `SCN_CD = GParam.SCN_CD` and `ISSUE_AGE = MP.issue age` (the corresponding field of the existing MP) to the WHERE clause
- [ ] Leave `Import_Lapse_Ratio` / `Import_Expense_Ratio` / `Import_commission` **unchanged**
- [ ] Known concern: the analysis notes flag what appears to be a missing `Next t` at the end of the code. Check the actual file; if it causes real harm, fix it (and if fixed, record it as a difference from the original); if not, leave a note "checked; no actual harm"

### 5.4 `IXP_Prot/O01_Set_Output.txt`

- [ ] Add an `SCN_CD` column to the output records so that PVs are identifiable per scenario × Cell × MP
- [ ] Point the output destination (table/file) paths under `output/bel_demo/` (do not contaminate existing output)

### 5.5 Overall acceptance criteria for the FMS modifications

- [ ] No differences in `C01`–`C04` (calculation core) and `C09_Initialize` (machine-verified with `diff`)
- [ ] Every modified line carries the `' [BELDEMO]` marker, so all modified locations can be enumerated with `grep`
- [ ] A smoke run with the single BASE scenario and the single model point MP01 completes normally
- [ ] **Measured record of the adoption burden (for paper §9.2 — mandatory):** record the following in `docs/bel_demo_effort_log.md`
  - Number of modified modules and their names (expected: 4)
  - Number of modified lines (machine-count added/changed lines from `diff`; reconcile against the count of `' [BELDEMO]` marker lines)
  - Work effort (person-days per step: ① governance, ② rate generation, ③ FMS modification, ④ pipeline verification, ⑤ aggregation; note when Claude Code was used)
  - Computation time (time to generate rates for 1 scenario; time for FMS to run 1 scenario)
  - This record is the evidence that backs the paper's claim that "adoption is easy" with measured values, so record it as the work proceeds (retrospective estimation is not acceptable)

---

## 6. Python Layer (2) — Aggregation and Figure/Table Generation

**File name:** `ScaleBB/Research/scripts/bel_demo/aggregate_fms_results.py`

```python
# [Purpose] Aggregate the per-scenario FMS output and generate the table and figure for paper §8
#
# [Input] FMS output (PVs per SCN_CD × Cell × MP)
#
# [Output 1] output/bel_demo/bel_sensitivity_table.csv
#   Rows: MP01–MP08 + total (9 rows)
#   Columns: BASE_PV, UP50_PV, UP50_pct, DN50_PV, DN50_pct,
#       ICS_T_PV, ICS_T_pct, ICS_C_PV, ICS_C_pct
#   (pct columns are the % change relative to BASE)
#
# [Output 2] output/bel_demo/bel_sensitivity_bar.png
#   x-axis: model point; y-axis: % change vs BASE; bar chart colored by scenario
#   Order by issue age so that structural observations for the caption can be read off,
#   e.g. "the younger the issue age, the larger the impact of the Trend shock"
```

---

## 7. Verification (summary of acceptance criteria)

| # | Verification item | Criterion | Action on failure |
|---|---|---|---|
| V1a | **Pipeline verification, rate level (strict)** | An independent script re-derives the cohort diagonals from the rate surfaces (`rate_surface_*.csv`) and independently applies the unit conversion (per 100k → decimals); the result **matches exactly** (tolerance 1e-12) every record of `TBL_CLAIM_SCN` in the DB | Identify and fix off-by-one errors in the cohort diagonal, unit conversion, or key mix-ups. Since FMS is not involved, the cause must be on the plumbing side |
| V1b | **Pipeline verification, PV level** | For the BASE scenario, the independently implemented simplified Python calculation (see V1 supplement below) and the FMS output PVs agree **within ±1% for all 8 MPs** | Identify the cause of the difference (rounding, monthly/annual conversion, order of decrement deductions, beginning/end-of-period treatment) and record it in `docs/bel_demo_reconciliation.md` (internal QA document; not cited in the paper) |
| V2 | Directionality | Monotonicity — higher L → lower incidence rates → lower benefit PV — holds for all MPs | Suspect the sign of the rate tables or the diagonal read-out |
| V3 | Composition consistency | Deviation from ICS_C ≒ ICS_T × 1.125 is explainable (attributable only to the lapse interaction) | Decompose the deviation factors and annotate |
| V4 | Reproducibility | One-shot reproduction from a clean state using the command sequence in the `README` | Fix the pipeline |

**V1 supplement — positioning of the verification, and scripts**

V1 is **not a validation of FMS Booster itself** (FMS is a validated tool with an adoption track record at insurance companies; its validity is taken as given). The scope of verification is limited to the pipeline parts newly built for this demo — ① unit conversion (per 100k → decimals), ② duration expansion of the cohort diagonals, ③ monthly/annual granularity conversion, ④ the TBL_CLAIM_SCN load and the WHERE-clause modification. The division of labor: V1a verifies ① and ② strictly, and V1b verifies the integrated path including ③ and ④. This verification is in-process quality assurance and is **not mentioned in the body of the paper** (the paper only keeps the framing "a demo on a production-validated model").

**File name:** `ScaleBB/Research/scripts/bel_demo/verify_pipeline_rates.py` (for V1a)

```python
# [Purpose] Independently re-derive the cohort diagonals and unit conversion from the rate surfaces,
#         and reconcile against every record of TBL_CLAIM_SCN in the DB (pipeline verification, rate level)
# [Verification formula] expected = rate_surface[x0 + dur, 2026 + dur] / 100_000
#           For all (SCN, BNFT_Q, GNDR, ISSUE_AGE, DUR), the difference from the DB value is within 1e-12
# [Output] output/bel_demo/verify_pipeline_rates.csv (list of mismatched records; pass if 0 records)
# [Caution] Do not import functions from build_scenario_claim_rates.py; implement the diagonal
#         extraction and unit conversion independently within this script (so they do not share the same bug)
```

**File name:** `ScaleBB/Research/scripts/bel_demo/verify_bel_standalone.py` (for V1b)

```python
# [Purpose] Independently of FMS, compute BEL in a simplified way from the same assumptions and cross-check
#         (pipeline verification, PV level)
# [Formulas]
#   BEL(x0) = Σ_t  v^t · S(t) · q_dis(x0+t, 2026+t) · SA
#   S(t)    = Π_{s<t} (1 − q_dis − q_death − q_lapse)   * independent approximation; to be checked against FMS's decrement order
# [Output] output/bel_demo/verify_standalone_vs_fms.csv (per MP: FMS PV, independent PV, deviation %)
# [Secondary role] If the 7/24 fallback is triggered, this script is promoted to the main calculation
```

---

## 8. Work Order and Fallback Decision Point

| Order | Work | Target completion |
|---|---|---|
| ① | Governance (§0): model copy, CLAUDE.md update | 7/16 |
| ② | `build_scenario_claim_rates.py` (BASE only, ahead of the rest) + verify the actual schema of the existing TBL_CLAIM | 7/18 |
| ③ | The 4 FMS modifications + smoke run with 1 BASE scenario, 1 point MP01 | 7/22 |
| ④ | Pipeline verification V1a (rate level, full reconciliation) + V1b (PV level, BASE, all 8 MPs) | **7/24 ★ decision point** |
| ⑤ | Load, run, and aggregate the remaining 4 scenarios; generate the table/figure | 7/28 |
| ⑥ | Verifications V2–V4, prepare the README, draft 1–2 paragraphs of the paper §8 body | 7/31 |

**★ Fallback decision (7/24):** if at step ④ V1b does not converge, or FMS debugging is judged to be squeezing the remaining effort, defer the FMS version to "future validation" and write §8 with the **simplified Python version**, promoting `verify_bel_standalone.py` to the main calculation (contingent on V1a passing; if the rate level is verified, the reliability of the simplified version is also assured). Decision criterion: V1b not achieved as of 7/24 AND the cause is not expected to be resolved within 2 business days.

---

## 9. Deliverables (upon completion)

```
ScaleBB/Research/scripts/bel_demo/
├── build_scenario_claim_rates.py   — scenario rate generation
├── load_scenario_to_db.py          — DB_ASSUMP load
├── verify_pipeline_rates.py        — pipeline verification, rate level (V1a)
├── verify_bel_standalone.py        — pipeline verification, PV level (V1b; main calculation under fallback)
├── aggregate_fms_results.py        — aggregation and figure/table generation
└── README.md                       — reproduction steps (command sequence)

ScaleBB/Research/data/processed/bel_demo/
├── scn_claim_rates.csv / scn_mortality_rates.csv
└── rate_surface_*.csv (for cross-checking)

ScaleBB/Research/output/bel_demo/
├── bel_sensitivity_table.csv       — the table for paper §8
├── bel_sensitivity_bar.png         — the figure for paper §8
├── verify_pipeline_rates.csv       — V1a verification result (list of mismatched records; pass if 0 records)
└── verify_standalone_vs_fms.csv    — V1b verification result

ValidationTools/BoosterFMS/
├── Base_Model_v251208/             — original (unmodified)
├── Scenario_Model_BELDemo/         — modified copy (with ' [BELDEMO] markers)
└── CLAUDE.md                       — policy updated
```
