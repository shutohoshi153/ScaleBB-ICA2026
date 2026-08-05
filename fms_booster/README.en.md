[日本語](README.md) | **English**

# fms_booster — FMS Booster run package (re-running the §8 BEL sensitivity demo on a production model)

*English translation of [README.md](README.md) (as of 2026-08-05). If the versions disagree, the Japanese version is authoritative.*

Everything needed to re-run the paper's §8 BEL sensitivity demo (simplified Python version) on the production projection model **FMS Booster**. The run cases are Tier 1 (cases A/B/C) = (A) PV-level reconciliation of BASE (V1b), (B) reproduction of the 6-scenario × 8-MP sensitivity table, and (C) measurement of the execution load (§9.2 argument 4; first item of §10.4).

For details, see **[`docs/FMS_BoosterRunCases_Tier1_20260805.md`](docs/FMS_BoosterRunCases_Tier1_20260805.md)** (the run-case definition document).

## Contents

| Path | Contents | Status |
|---|---|---|
| `docs/FMS_BoosterRunCases_Tier1_20260805.md` | Run-case definition document (approach decision, acceptance criteria V1b-①②③, RUN list, GParam/SParam settings, diagnostic procedure) | Finalized (2026-08-05) |
| `docs/BEL_Demo_WorkInstruction_FMS_20260710.md` | Original work instruction (starting point of the Tier definitions; partially refined and superseded by §1–§2 of the definition document) | Reference |
| `docs/bel_demo_effort_log.md` | Case C measurement log (with fill-in fields; **record while running FMS, not afterwards**) | Awaiting entries |
| `fms_input/BELDemo_{Input,Assump,Scn,MP}.db` | The 4 SQLite files FMS connects to (definition document §4.1; verification passed: 23,314 comparisons, 0 mismatches) | Generated and verified |
| `fms_input/tbl_*.csv` | CSV mirrors of the tables above (for visual inspection) | Same |
| `fms_input/fms_run_case_map.csv` | Mapping table MP×SCN ↔ PROD_CD / rate codes | Generated |
| `fms_input/fms_expected_pv.csv` | Mirror PV, annual BEL, and predicted gap (pre-mode output) | Generated |
| `scripts/verify_v1b_fms_pv.py` | Pre-mode (generates the expected-value table) + reconciliation mode (V1b-①②③ verdicts). **Only the path definitions differ from the working-repository version; the logic is identical** | Verified working |
| `reference_output/bel_by_mp_scenario.csv` | The paper's §8 annual BEL (the comparison target for V1b-②③) | Bundled |
| `reference_output/verify_fms_input_tables.csv` | Pass record of the independent input-table verification (V1a-F) | Bundled |
| `output/` | Output directory for reconciliation mode (not tracked by git) | — |

## What is NOT bundled

- **The FMS Booster model source (`Scenario_Model_BELDemo/`, an unmodified copy of `Base_Model_v251208/`)** — vendor-supplied, so it is not bundled in this (public) repository. Run against the model in the internal B-FMS environment (working repository `ValidationTools/BoosterFMS/Scenario_Model_BELDemo/`). Thanks to the data-injection approach, **zero lines of model code are modified** (definition document §1).
- The vendor's coding-guide PDF — likewise.
- The input-table generation and independent-verification scripts (`build_fms_input_tables.py` / `verify_fms_input_tables.py`) — they depend on data from the upstream simplified-Python pipeline (`ScaleBB/Research/scripts/bel_demo/`), so they are not bundled. The generated DBs have already passed verification; the pass record is bundled as `reference_output/verify_fms_input_tables.csv`.

## Run procedure (summary; details in §3–§7 of the definition document)

```bash
# ① Optional pre-check: confirm the expected-value table reproduces
cd fms_booster && python3 scripts/verify_v1b_fms_pv.py
#    → fms_expected_pv.csv (48 cells). OK if the convention gap −5.07% to −3.65% is printed

# ② FMS side (Windows / B-FMS execution environment)
#    - Load Scenario_Model_BELDemo/ (internal environment) as the model
#    - Connect the 4 DBs in fms_input/ per §4.2 of the definition document; set GParam/SParam per §4.2–4.3
#    - Execute RUN-00 → RUN-A1 → RUN-B1..B5 (→ optionally RUN-C1) in order, per §3
#      ★ Cells MUST run in ascending policy-term order (issue age 60 → 50 → 40 → 30; see the §3 preamble)
#    - Record run times in docs/bel_demo_effort_log.md
# ③ Reconciliation (bring the FMS S03 output CSVs back to this environment)
python3 scripts/verify_v1b_fms_pv.py \
  --fms-csv <RUN_A1's *_PV_ByPol.csv> --fms-csv <RUN_B1's …> … (all 6 runs)
#    → output/verify_v1b_fms_pv.csv, the reconciliation table with V1b-①②③ verdicts
```

## Path mapping to the working repository

Paths inside the definition document and the work instruction are written relative to the working repository. They map to this package as follows.

| Reference in the documents (working repository) | This package |
|---|---|
| `ScaleBB/Research/docs/FMS_BoosterRunCases_Tier1_20260805.md` and other docs | `docs/` |
| `ScaleBB/Research/data/processed/bel_demo/fms_input/` | `fms_input/` |
| `ScaleBB/Research/scripts/bel_demo/verify_v1b_fms_pv.py` | `scripts/verify_v1b_fms_pv.py` (path definitions only changed) |
| `ScaleBB/Research/output/bel_demo/bel_by_mp_scenario.csv` | `reference_output/bel_by_mp_scenario.csv` |
| `ScaleBB/Research/output/bel_demo/verify_v1b_fms_pv.csv` (reconciliation result) | `output/verify_v1b_fms_pv.csv` |
| `ValidationTools/BoosterFMS/{Base_Model_v251208,Scenario_Model_BELDemo}/` | **Not bundled** (use the internal B-FMS environment) |
