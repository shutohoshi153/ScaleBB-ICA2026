[日本語](bel_demo_effort_log.md) | **English**

# BEL Demo — Measured Adoption-Burden Log (evidence for paper §9.2)

*English translation of [bel_demo_effort_log.md](bel_demo_effort_log.md) (as of 2026-08-05). If the versions disagree, the Japanese version is authoritative.*

Effort log kept pursuant to §5.5 of the work instruction `BEL_Demo_WorkInstruction_FMS_20260710.md`.
**Because the fallback decision point of 2026-07-24 had passed, FMS integration was not carried out and the simplified Python version
(`scripts/bel_demo/`) was used as the primary calculation.** This log therefore contains
"measured values of the simplified Python version", not "measured values of FMS integration". The paper's §9.2 cannot cite measured FMS-integration values
(§9.2 consists solely of the 5 rationales plus the phased adoption path).

**Policy change of 2026-07-29 (final):** Because the processing times of the simplified Python version lack
production-grade persuasiveness, the draft version (7/31) makes no mention of processing time whatsoever (references to figures and
measurements have been removed from §7.2, §8.2, §8.4, and §9.2 rationale 4; rationale 4 is qualitative only).
For the final version, Run times will be measured on FMS Booster, which has a production deployment track record, and recorded under §9.2 rationale 4.
See "Measurement of FMS Booster run times" below. FMS integration effort (lines modified, person-days) was
not carried out and thus remains uncited.

## Measured values (2026-07-28, using Claude Code)

| Item | Measured |
|---|---|
| Number of FMS modules modified / lines modified | 0 / 0 (not carried out; `Base_Model_v251208/` was consulted read-only) |
| Python implementation | 5 new scripts (ESR discount-curve reproduction, rate generation, V1a verification, BEL main calculation, aggregation & plotting) + README |
| Work effort | 2 Claude Code sessions (initial version approx. 0.5 person-hours + ESR implementation-spec conformance approx. 0.5 person-hours) |
| Computation time for rate generation | 0.2 s (6 scenarios × 3 diseases × 2 sexes + all-cause; 8 fits + 26 projections) |
| ESR discount-curve reproduction | under 1 s (Smith-Wilson fitting + α search) |
| Computation time for BEL calculation | 0.03 s (8 MPs × 6 scenarios) |
| V1a full reconciliation | 0.5 s (6,840 records) |

Breakdown of the ESR implementation-spec conformance work (second session): obtaining and reading FSA published materials (the yield-curve
tool xlsx; identifying the coefficients from the 167-page Pillar 1 notice), implementing the Smith-Wilson extrapolation,
adding the ESR_M scenario, and writing paper §8.

Additional research and implementation (continuation of the same session): after surveying domestic explanatory sources (FSA deliberation status / provisional decisions /
remaining issues & Q&A; Nomura Institute of Capital Markets Research 2022; Seimei Hoken Ronshu [life insurance journal], Ueno 2023; the web journal Kyosai to Hoken,
Morimoto 2025), identified from the notice the life-insurance sub-risk aggregation (Article 81, correlation matrix), lapse
(Articles 61–63), longevity (Article 57), and MOCE (Articles 29–30, cost-of-capital rate 3%), and implemented them as
`calc_esr_life_risk.py` (computation time under 1 s). Paper §8.5 appended.

## Measurement of FMS Booster run times (for final-version §9.2 rationale 4; to be done before the final version)

**Preparation complete (2026-08-05):** Run cases, input tables, and reconciliation scripts are in place.
Following the run case definition document `FMS_BoosterRunCases_Tier1_20260805.md`, execute and measure
RUN-00 (smoke test) → RUN-A1 (BASE, 8 MPs) → RUN-B1 through B5 (remaining 5 scenarios) using
`Scenario_Model_BELDemo/` (created; byte-identical to the original) + the 4 SQLite files in `fms_input/`.
The approach is the data-injection approach (**0 FMS modules modified, 0 lines** — the scenario axis is folded into PROD_CD and
the generational diagonal rates are pre-baked into TBL_RSKRT). This 0/0 itself becomes the measured adoption-burden value for §9.2.

| Measurement item | Measured (fill in) |
|---|---|
| FMS 1-scenario run time (8 MPs, RUN-A1) | (not yet measured) |
| FMS 6-scenario total (RUN-A1 through B5; reference: RUN-C1 batched) | (not yet measured) |
| Execution environment (machine spec, FMS version, core count) | (not yet filled in) |
| Measurement date | (not yet filled in) |
| Number of FMS modules modified / lines modified | 0 / 0 (data-injection approach; confirmed via `diff -rq`) |
| FMS input-table generation + independent verification (Python side) | generation 0.5 s; V1a-F verification 23,314 records passed (2026-08-05) |

After measurement, record the measured FMS values under §9.2 rationale 4 in the final version (the draft version contains no processing-time
statements and no placeholders). Since present values are obtained from the same Runs, the V1b reconciliation
(all 8 MPs within ±1%, work instruction §7) can be performed at the same time (the future verification of paper §10.4).

## Implications usable in the paper

- Scenario generation (Phase 2 re-projection) requires only swapping L, at under a second per scenario.
  Usable as support for "the computational load is light" (§9.2 rationale 4)
- The fact that the sensitivity table was obtained from the existing rate panel and the algorithmic core alone, without FMS integration,
  is corroborating evidence for "upstream placement, same-format output" (§9.2 rationale 1)
- The re-execution on FMS (V1b) is recorded in §10 as future verification
