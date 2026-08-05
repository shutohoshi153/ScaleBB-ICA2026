[日本語](FMS_BoosterRunCases_Tier1_20260805.md) | **English**

# FMS Booster Run Case Definitions — Tier 1 (Cases A/B/C)

*English translation of [FMS_BoosterRunCases_Tier1_20260805.md](FMS_BoosterRunCases_Tier1_20260805.md) (as of 2026-08-05). If the versions disagree, the Japanese version is authoritative.*

**Date created:** 2026-08-05
**Purpose:** Re-execute the BEL sensitivity demo of paper §8 (simplified Python version) on FMS Booster, a production projection model with a deployment track record at an insurance company, and carry out as a single exercise:
(A) PV-level reconciliation of the BASE scenario (V1b), (B) reproduction of the 6-scenario × 8-MP sensitivity table, and (C) measurement of execution load (paper §9.2, rationale 4).
**Related documents:** `BEL_Demo_WorkInstruction_FMS_20260710.md` (original work instruction), `bel_demo_effort_log.md` (measurement log), `../scripts/bel_demo/README.md` (simplified Python version), `../../../ValidationTools/BoosterFMS/CLAUDE.md` (governance)
**Position within the paper:** Closes §10.4 item 1 (re-execution on a production projection model with reconciliation at the rate and present-value levels, plus measured execution load) and §9.2 rationale 4 (measured computational load). Provides the basis for upgrading the §8 phrase "demo on a simplified projection model" in the final version.

---

## 1. Approach decision — data-injection approach (0 lines of FMS code modification)

The original work instruction §5 envisaged modifying 4 modules (adding a scenario loop, switching the reference to `TBL_CLAIM_SCN`), but after a close reading of the implementation in `Base_Model_v251208/`, we adopt a "data-injection approach" that executes all cases with **no code modification**.

**Rationale (implementation facts established by close reading of the modules):**

1. `IXP_Prot/B04_Set_Bnft_Info.txt:207` — `Qxt(srno, t) = RiskRate(srno).val(gender, MP.AGE + t - 1)`. Rates are read on the **attained-age axis only**, and the projection year and attained age advance in lockstep. Therefore, if the generational diagonal `m(x0+dur, 2026+dur)` is pre-baked into `TBL_RSKRT` (`RSK_RT0..RSK_RT120`) per entry-age cohort, no calendar-year dimension is needed.
2. `IXP_Prot/A01_Main.txt:43` — IXP has no scenario loop (`scn_loop = 1` fixed; the economic-scenario axis is dedicated to discount rates). Folding the scenario axis into **PROD_CD (product code = cell)** is less invasive than a loop-adding modification.
3. Zero lines of modification is the **strongest-form implementation** of the paper's §7 claim that "differences between scenarios reduce solely to assumption differences" (not just the calculation core but every module is identical across scenarios).
4. As a measured value of adoption burden (§9.2), "0 FMS modules modified, 0 lines" serves directly as evidence.

**Governance:** Execution takes place on `ValidationTools/BoosterFMS/Scenario_Model_BELDemo/` (created 2026-08-05; a byte-identical copy of the original). `Base_Model_v251208/` must remain strictly unmodified. If a modification ever becomes necessary, it will be made only in `Scenario_Model_BELDemo/`, tagged with the `' [BELDEMO]` marker.

### 1.1 Semantic mapping (simplified Python version ↔ FMS implementation)

| Assumption in the simplified Python version | Implementation on FMS | Means of realization |
|---|---|---|
| 6 scenarios (differ only in rates) | 24 products with PROD_CD = `BD_{SCN}_{AGE}` | Data only |
| Generational diagonal rates m(x0+dur, 2026+dur) | Pre-baked per cohort into attained-age-axis `TBL_RSKRT` | `build_fms_input_tables.py` |
| Critical-illness lump-sum benefit (three major diseases) of 1,000,000 yen (on first diagnosis) | 3 benefits (BNFT_CRIT_CD='S', BNFT_RT=1.0) × JOIN_AMT = 1,000,000 yen | TBL_BNFT / TBL_MP |
| Lapse 3%/year = lapse without value (no surrender value) | **Lapse table 0 + 3% added into the Lives (decrement) rates** | TBL_LAPSE=0, added into `R_*_LIV` |
| Death decrement = all-cause rate (BASE, fixed) | Same as above (Lives rate = 3 diseases + all-cause + 3%) | `R_*_LIV` |
| Benefits only (no premiums or expenses) | PREM=0, expense/commission tables 0, no assumed expenses | TBL_MP / TBL_ACQ etc. |
| Issue in 2026; BEL at issue | Val_YM='202512', CTR_DT='202601' → elapsed_time=0 | TBL_MP / GParam |
| ESR risk-free interest rate curve (annual spot) | Monthly forwards (derived from ln-linear interpolation) into TBL_DC_RT | `build_fms_input_tables.py` |
| BEL = present value of benefits | S03 `Net_CF` (= PV_Outgo_M; income and other outgo are all 0) | Reconciliation script |

**Note on the treatment of lapses:** In IXP, the surrender value is computed from the net-premium policy reserve (`C01`/`C02`) and cannot be zeroed out by data settings alone. By adding the lapse rate into the Lives (decrement) rates and setting the lapse table to 0, the surrender path in `C03` (`No_Pol.surr`) disappears and no surrender-value payments arise, yielding the same semantics as the simplified Python version's "lapse = lapse without value". On an annual basis the survival rates of the two agree exactly (the monthly geometric transform of the combined annual rate q_sum returns to (1−q_sum) at year boundaries). Note that, as a consequence of this design, the lapse sensitivity via `GParam.Lapse_Sens` (Tier 3 case F) cannot be used with this input set (in that case, move the lapses back to the TBL_LAPSE side).

---

## 2. Acceptance criteria (refinement of V1b)

The original work instruction §7's V1b ("FMS vs simplified Python version PV within ±1% for all 8 MPs") turned out, through prior quantification, to be unattainable as stated because of the **payment-timing convention difference** between the two (see below). In keeping with the original intent of V1b (the object of verification is not FMS itself but the plumbing newly built for this demo), it is refined into the following 3 tiers.

**Prior quantification (2026-08-05, `verify_v1b_fms_pv.py` pre-run mode):** The simplified Python version uses "annual, beginning-of-year payment, beginning-of-period discounting"; FMS uses "monthly, mid-month payment, within-year exposure decay". The gap from an independent mirror calculation that replicates the FMS conventions is **−5.1% to −3.7% across all 48 cells** (larger for older entry ages and higher-rate scenarios). Meanwhile, the impact on the BASE-relative sensitivity ΔBEL% is **at most 0.35pp** (young-age MPs of ICS_C; caused by the order of applying the level multiplier 1.125 annually before the monthly conversion), and the total-BEL sensitivities under the mirror are UP50 −6.5 / DN50 +7.1 / ICS_T +14.9 / ICS_C +27.5 / ESR_M +17.9%, matching the paper values (−6.6 / +7.2 / +15.0 / +27.7 / +18.0%) within 0.2pp.

| # | Criterion | Content | Pass/report |
|---|---|---|---|
| **V1b-①** | Pipeline verification (primary criterion) | FMS output `Net_CF` vs the monthly-mirror independent implementation (`verify_v1b_fms_pv.py`) within **±1% for all 8 MPs × 6 scenarios** (expected ≲0.1%. The mirror reads the very SQLite files that FMS reads and reproduces the C03/C04 conventions) | Pass/fail criterion |
| **V1b-②** | Measurement of the convention difference (= Case D at proposal time) | Record the deviation of FMS output vs the paper §8 annual BEL for every cell. Confirm consistency with the prior estimate of −5.1 to −3.7% (±0.5pp), and record it, together with the decomposition of the deviation (payment timing, within-year exposure decay), in `bel_demo_reconciliation.md`. Citable in paper §8.4/§10.4 as "the measured convention difference of the simplified model" | Reported value |
| **V1b-③** | Sensitivity consistency (pass/fail for Case B) | ΔBEL% (relative to BASE) between FMS and the paper's annual version within **±0.5pp for all cells**. Direct confirmation that the paper's central claims (age gradient of the trend shock: age 30 +31–32% / age 60 +10–11%; age-uniformity of the level shock) hold on FMS | Pass/fail criterion |
| **S-inv** | Invariant checks | For all S02 rows: `Surr_Val = 0`, `Prem_Inc = 0`, `Commission = Exp_Acq = Exp_Mnt = 0`; for all S03 rows: `PV_Income_* = 0` and `Net_CF = PV_Outgo_M` | Pass/fail criterion |
| **C-1** | Measured execution load | Record the measurement items of §5 in the fill-in fields of `bel_demo_effort_log.md` (concurrently with the work) | Record |

---

## 3. Run case list

**Common mandatory requirement — cell execution order:** IXP does not reinitialize the `PV` array (`C04`) between MPs. If a short-term MP is computed after an MP with a long policy term, the initial term of the backward present-value recursion reads a leftover value from the previous MP (a stale read of `PV.outgo_m(prj_m+1)`). **Cells must be ordered by ascending policy term (entry age 60 → 50 → 40 → 30).** With this order, the uninitialized region is always 0 and causes no contamination.

| RUN | Case | Cell_List (in this order) | # MPs | Purpose / pass criteria |
|---|---|---|---|---|
| **RUN-00** | Smoke test | `BD_BASE_60` (limited to 1 MP with Test_Opt='Y') | 1 | Normal completion; S02 has 360 rows; S-inv holds; `Net_CF` within ±1% of the mirror value MP04_BASE ≈ 95,550 yen |
| **RUN-A1** | Case A (V1b) | `BD_BASE_60, BD_BASE_50, BD_BASE_40, BD_BASE_30` | 8 | V1b-① (BASE 8 MPs) + V1b-② + S-inv. Measure the 1-scenario run time (C-1) |
| **RUN-B1** | Case B | `BD_UP50_60, BD_UP50_50, BD_UP50_40, BD_UP50_30` | 8 | UP50. RUN-B2 to B5 below follow the same pattern |
| **RUN-B2** | Case B | DN50, same order | 8 | |
| **RUN-B3** | Case B | ICS_T, same order | 8 | |
| **RUN-B4** | Case B | ICS_C, same order | 8 | |
| **RUN-B5** | Case B | ESR_M, same order | 8 | Judge V1b-③ after RUN-A1 through B5 are complete |
| **RUN-C1** | Case C (optional) | All 24 cells in one Run, ordered "`*_60` × 6 → `*_50` × 6 → `*_40` × 6 → `*_30` × 6" | 48 | Measure the batched run time. Results must match RUN-A1 through B5 (regression check) |

- 6-scenario total time = sum of RUN-A1 through B5 (the per-scenario breakdown can be used in the §9.2 text). RUN-C1 is a reference value for "if consolidated into 1 Run".
- Multi-core (`SParam.TotNo_Core` > 1) is permitted (the same cell order is preserved per core, so the execution-order requirement is not violated), but **take the measurement on 1 core first**, and record the core count explicitly in the log field.

---

## 4. Model settings and input data

### 4.1 Input DBs (generated and verified)

Generation: `ScaleBB/Research/scripts/bel_demo/build_fms_input_tables.py`
Output: `ScaleBB/Research/data/processed/bel_demo/fms_input/` (with CSV mirrors)
Verification: `verify_fms_input_tables.py` — **passed 2026-08-05 (23,314 reconciliation records, 0 mismatches)**. Rates match an independent re-derivation from the checking surface to 1e-12, and the annual accumulation of the discount forwards matches the curve's discount factors to 1e-10.

| DB file | FMS connection | Tables (row counts) |
|---|---|---|
| `BELDemo_Input.db` | DB_INPUT | TBL_BNFT (192), TBL_RSKRT (192), TBL_PROD_INRT (24), TBL_EXPCT_EXPENSE (0) |
| `BELDemo_Assump.db` | DB_ASSUMP | TBL_PROD_MAP (24), TBL_CLAIM (4), TBL_LAPSE (2), TBL_SKEW (1), TBL_ACQ (1), TBL_MNT (1), TBL_COMM (1) |
| `BELDemo_Scn.db` | DB_SCN | TBL_DC_RT (840: PRD 1..840, SCN_NO='1') |
| `BELDemo_MP.db` | DB_MP | TBL_MP (48) |

**Key scheme:** PROD_CD = `BD_{SCN}_{AGE}` (e.g. `BD_ICS_T_30`), rate code = `R_{SCN}_{AGE}_{Q1|Q2|Q3|LIV}` (Q1=cancer, Q2=heart, Q3=cerebrovascular, LIV=decrement), CTR_POLNO = `{MP_ID}_{SCN}` (e.g. `MP01_BASE`). The mapping table is `fms_input/fms_run_case_map.csv`.

### 4.2 GParam (global parameters; set on the B-FMS master sheet)

| Item | Setting | Notes |
|---|---|---|
| Val_YM | `202512` | Combined with CTR_DT='202601' gives elapsed_time=0 (valuation at issue) |
| Proj_Obj | `PV` | Enables Calc_PV |
| Scn_Range | `1` | Single economic scenario (discount rates common to all scenarios) |
| TBL_BNFT / TBL_RSKRT / TBL_PROD_INRT / TBL_EXPCT_EXPENSE | Same names | DB_INPUT |
| TBL_PROD_MAP / TBL_CLAIM / TBL_LAPSE / TBL_SKEW / TBL_ACQ / TBL_MNT / TBL_COMM | Same names | DB_ASSUMP |
| TBL_DC_RT | Same name | DB_SCN |
| TBL_MP | Same name | DB_MP |
| Mort_Sens / Dis_Sens / Lapse_Sens / Acq_Sens / Mnt_Sens | `1.0` | All sensitivity scalars neutral |
| DiscR_Sens | `0.0` | No discount-rate spread |
| Output_No | Enable S02 and S03 | S01 is irrelevant to IXP |
| DB file names (Input / Assump_Actu / Assump_Econ / MP) | Paths to `BELDemo_*.db` | Confirm the GParam names of `A04_Connect_DB.txt` on the live master sheet (§7) |

### 4.3 SParam (Run parameters)

| Item | Setting |
|---|---|
| Master_Name | `BELDEMO` |
| Run_Name | `RUN_00` / `RUN_A1` / `RUN_B1`–`RUN_B5` / `RUN_C1` |
| Cell_List / TotNo_Cell | In the order specified in §3 |
| Test_Opt | `Y` for RUN-00 only (limit to 1 MP), `N` otherwise |
| TotNo_Core | `1` for measured Runs (multi-core re-runs allowed for reference) |

---

## 5. Case C — measurement items (corresponding to the fill-in fields of `bel_demo_effort_log.md`)

Record concurrently with the work (after-the-fact estimation is not allowed; original work instruction §5.5).

1. FMS 1-scenario run time (8 MPs): measured value of RUN-A1 (and individually for RUN-B1 through B5 if possible)
2. FMS 6-scenario total: sum of RUN-A1 through B5 (reference: batched time of RUN-C1)
3. Execution environment: machine spec (CPU/memory), FMS Booster version, core count
4. Measurement date
5. **Number of FMS modules modified / lines modified: 0 / 0 (data-injection approach)** — record the result of `diff -rq Base_Model_v251208 Scenario_Model_BELDemo` (no differences) as evidence
6. Python-side time for input-table generation and verification (build 0.5 s, verify a few seconds; already measured)

---

## 6. Execution procedure (overall)

```bash
# ⓪ Prerequisite: the simplified-Python-version pipeline is up to date (steps ①–③ can be skipped if already run)
cd ICA/ScaleBB/Research/scripts/bel_demo
python3 build_esr_discount_curve.py
python3 build_scenario_claim_rates.py
python3 calc_bel_standalone.py

# ① Generate the FMS input tables + independent verification (V1a-F) + expected-value table
python3 build_fms_input_tables.py
python3 verify_fms_input_tables.py          # Confirm it passes (0 mismatches)
python3 verify_v1b_fms_pv.py                # Pre-run mode: generates fms_expected_pv.csv

# ② FMS side (Windows / B-FMS execution environment)
#   - Load Scenario_Model_BELDemo/ into B-FMS as the model
#   - Connect the 4 DBs in fms_input/ as per §4.2, and set GParam/SParam as per §4.2–4.3
#   - Execute RUN-00 → RUN-A1 → RUN-B1..B5 of §3 in order (→ optionally RUN-C1),
#     recording the elapsed time of each Run

# ③ Reconciliation (bring the FMS S03 output CSVs back to this environment)
python3 verify_v1b_fms_pv.py \
  --fms-csv <RUN_A1's *_PV_ByPol.csv> --fms-csv <RUN_B1's …> … (for all 6 Runs)
#   → verify_v1b_fms_pv.csv: reconciliation table with V1b-①②③ verdicts
```

---

## 7. Items to confirm on the live system (resolve at first setup)

Items that cannot be settled from the model source (.txt) alone and require confirmation in the B-FMS execution environment / master sheet. Detected via the RUN-00 smoke test.

1. **Actual GParam names:** The DB-file-name parameters referenced by `A04_Connect_DB.txt` (Input_DB_Name etc.), and the exact key names of the table-name GParams and `Output_No`, are defined on the master sheet (Excel) side. Confirm they can be set as mapped in §4.2.
2. **Output format and paths:** The output file-name pattern for S02/S03 (assumed `{Run}_{Master}_PV_ByPol.csv`) and the output destination (`SParam.OutputPath`), plus the split suffix under multi-core. The reconciliation script depends only on the CTR_POLNO column, so it is robust to format differences.
3. **The `Next t` notation in `B05_Import_Assumption.txt`** (lines 124–126 and 130–132; a `For th` loop closed with `Next t`): a concern already flagged in the original work instruction §5.3. With this input set the lapse rate is 0, so skew does not affect the calculation, but confirm in RUN-00 **whether the interpreter raises an error**. Only if it errors, fix it to `Next th` on the `Scenario_Model_BELDemo/` side, leaving the `' [BELDEMO]` marker and a diff record (the sole permitted modification candidate).
4. **The ROWID assumption of TBL_MP:** `B03` looks up MPs with `WHERE ROWID = MP_Idx` inside DB_CACHE. Confirm that `FMS.SQLite.Attach` guarantees insertion-order ROWIDs (1..N) (if as expected, MPs come in male→female order within each product, MP01 onward).
5. **Numeric precision:** Check whether the digit count (rounding) of the FMS-side CSV output affects the apparent deviation in V1b-① (if Net_CF is emitted with fewer than 7 significant digits, use the values from the SQLite output DB instead).

---

## 8. Diagnostic procedure on deviation (if a V1b-① failing cell appears)

Isolate the cause month by month using S02 (monthly CF). Obtain the mirror-side monthly series by adapting `mirror_pv()` in `verify_v1b_fms_pv.py` for debug output.

1. **Reconcile Lives and Tot_Claim for month 1** — if they differ from the first month, a rate was read incorrectly (one of: rate code ↔ PROD_CD mapping, GNDR_CD, A/E=1.0, Sens=1.0). Check the mapping in `fms_run_case_map.csv`.
2. **Reconcile at months 13, 25, … (year boundaries)** — if the deviation appears only at year boundaries, suspect a mismatch in the annual→monthly conversion (`1-(1-q)^(1/12)`) or in the switching of t (`Int((th-1)/12)+1`).
3. **CF matches but PV deviates** — a discounting problem. Reconcile the cumulative discount factors at integer years (the D1 verification has already passed, so suspect the FMS-side read of DC_RT (the WHERE on BAS_YM/SCN_NO) or `DiscR_Sens≠0`).
4. **Only short-term cells deviate (e.g. the 30-year cells)** — suspect a PV stale read from violating the execution order of §3. Check the Cell_List order and re-run after fixing the order.
5. **Rows with Surr_Val ≠ 0 exist** — TBL_LAPSE is not being read as 0 (key mismatch on BAS_YM/PROD_GRP/CHN_CD/PAY_STATUS).
6. **Suspected elapsed_time ≠ 0** (th in S02 does not start at 1) — check the interpretation of Val_YM and CTR_DT (`elapsed = 12*(ValYr−CtrYr)+ValMon−CtrMon+1`).

Record causes and remedies in `bel_demo_reconciliation.md` (an internal QA document, not cited in the paper).

---

## 9. Deliverables

```
ScaleBB/Research/scripts/bel_demo/
├── build_fms_input_tables.py       — generates the FMS input tables (§4.1)     [created]
├── verify_fms_input_tables.py      — V1a-F independent verification (passed)   [created]
└── verify_v1b_fms_pv.py            — pre-run mode + V1b-①②③ reconciliation    [created]

ScaleBB/Research/data/processed/bel_demo/fms_input/
├── BELDemo_{Input,Assump,Scn,MP}.db — SQLite files for FMS connection (4 files) [generated]
├── tbl_*.csv                        — CSV mirrors of the tables (for visual check) [generated]
├── fms_run_case_map.csv             — MP×SCN ↔ PROD_CD/rate-code mapping table [generated]
└── fms_expected_pv.csv              — mirror PV, annual BEL, predicted gap      [generated]

ScaleBB/Research/output/bel_demo/
├── verify_fms_input_tables.csv      — V1a-F reconciliation results (0 mismatches) [generated]
└── verify_v1b_fms_pv.csv            — V1b reconciliation table (with verdicts)  [after FMS run]

ScaleBB/Research/docs/
├── FMS_BoosterRunCases_Tier1_20260805.md — this document
├── bel_demo_effort_log.md           — C-1 measurement log (with fill-in fields) [fill in during FMS run]
└── bel_demo_reconciliation.md       — record of deviation causes (if needed)    [after FMS run]

ValidationTools/BoosterFMS/
├── Base_Model_v251208/              — original (unmodified; confirmed via diff -rq)
└── Scenario_Model_BELDemo/          — execution copy (currently identical to the original) [created]
```

**Reflecting the results in the paper after the FMS run (for reference):** If V1b passes, append to the §8.2 "simplified projection model" description language to the effect of "confirmed by re-execution on a projection model with a production deployment track record (FMS Booster) that inter-scenario sensitivities are reproduced within ±0.5pp (the level difference of −5 to −4% from the monthly, mid-month payment convention has been decomposed)", add the measured times to §9.2 rationale 4, and rewrite §10.4 item 1 to "completed". Drafting the actual text is a separate task.
