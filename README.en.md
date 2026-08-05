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
| `sections_en_b1/00_front_matter.md` | Title, authors, Abstract, Keywords | **New (2026-08-05). Author name and affiliation finalized; the Abstract is a draft** |
| `sections_en_b1/12_acknowledgment.md` | Acknowledgment (disclosure of generative-AI use, data acknowledgments, disclaimer; no peer-review acknowledgment since no peer review is planned) | **New (2026-08-05). Template — needs rewriting** |
| `sections_en_b1/13_references.md` | References | **New (2026-08-05). Source verification complete** |
| `sections/figures/` | Figures included in the main text (§3–§6 generated and collected by `reproduction/backtest/make_paper_figures.py` and others; Figure 8.1 by `ScaleBB/Research/scripts/bel_demo/aggregate_bel_results.py`) | Figures 3.1–3.3, 4.1, 5.1–5.5, 6.1–6.3, 8.1 (2026-07-28) |
| `reproduction/` | **Reproduction packages** for §3–§5 (division of roles explained in `reproduction/README.md`) | — |
| `reproduction/backtest/` | Point-forecast accuracy + directional accuracy (§3.1/3.2/3.4, §5, §6). Self-contained; runnable standalone | Verified working (2026-07-22) |
| `reproduction/generational/` | Generation of APC generational assumed-rate tables (the forward-running pipeline for the APC extension of §3.3; details in `reproduction/generational/README.md`). KDB CLI | Trace-verified (2026-07-15) |

## Compliance with the official ICA 2026 guidance (as of 2026-08-05)

The English manuscript (`sections_en_b1/`) was checked against the *Guidance for Preparing a Paper* / *Guidelines for Peer Review*, with the following addressed.

**Addressed**

- Added a References section (an explicit requirement of the guidance)
- Added an Acknowledgment section with a disclosure slot for generative-AI use (an explicit requirement of the guidance)
- Added front matter with the Abstract, author information, and Keywords
- Resolved the internal contradiction caused by conflated definitions of "cell" in §5 (the validation cells of §3.4.2/§4.3 and the disease×sex cells of §5/§6 are now defined separately)
- Fixed the horizon/cutoff conflation in §5.4
- Added a paragraph on prior work in cause-specific mortality forecasting to §2.2 and narrowed the claim of novelty A to "first within the family of improvement-rate scales" (§1.2 and §11 aligned accordingly)
- Unified the inconsistent notation of the ESR effective date (§1.1 / §2.3 / §8.1)
- Fixed the broken cross-reference in §4.5 ("see §3") and added an Availability statement
- Removed duplicated figure captions (alt text emptied; hand-written captions are now the single source)
- Numbered all tables sequentially (Table 2.1 / 3.1–3.6 / 4.1–4.2 / 5.1–5.3 / 6.1–6.4; former Table 6.1 renamed to 6.4, with the reference in §9.1 corrected)
- Added a hyperparameter table for the §3.3 APC extension, stated explicitly that it is out of validation scope (Scope note), and added a note to the same effect in §7.2

### Additional items addressed in the second check on 2026-08-05

- Revised the citation of the FSA Pillar 1 Notice to include the promulgation date (2025-07-23) and the **partial amendment of 23 March 2026 (effective 2026-03-31)** (§7.2, §8.1, References)
- Specified the version of the yield curve creation tool and added a References entry (on 2026-08-05 the actual file was inspected with openpyxl to pin down the valuation date and observed maturities; an entry was also added to `DATA_SOURCES.md`)
- Corrected "10-year-ahead level" in §6.1 to mean the 10-year aggregate (the same kind of horizon conflation as in §5.4)
- Aligned the cell notation in §11 with the definition in §5.2
- Condensed §10.2 (removed the near-verbatim repetition of the end of §6.5)
- Corrected the GBD entry in References to point to §2.2 instead of §10
- Detected the rounding inconsistency in §8.5 (a 1-yen discrepancy in the total); verified against the computation output the same day and confirmed it is an artifact of rounding. A note was added right after the table (no value changes needed)

**Outstanding (requires action by the author)**

Grep for the `<!-- TODO(著者確認) -->` (author-check TODO) comments in each file and clear them. Main items:

0. ~~**Handling of the FSA Pillar 1 Notice amendment**~~ → **Resolved (2026-08-05).** The primary source (the old/new comparison table of FSA Public Notice No. 6 of 2026) was checked, establishing that **the amendment consists only of typographical, punctuation, and heading-level corrections**, and every provision cited in this paper is untouched. No changes to the §8 figures are needed. The citation wording has been fixed in §7.2, §8.1, and References (the evidence is recorded in the HTML comment in §7.2)
1. ~~**Source verification of the *[TO BE VERIFIED]* items in References**~~ → **Resolved (2026-08-05).** All 9 items were verified against their sources and the markers cleared. Six needed only bibliographic confirmation (Alai et al. 2015, Arnold & Sherris 2013, CMI_2025 / WP211, the yield curve creation tool, the e-Stat terms of use, GBD) and **3 had their citations corrected**: (a) the compositional-data-analysis citation was replaced from Bergeron-Boucher et al. (2017) with Kjærgaard et al. (2019) (the former is mainly about coherent multi-population forecasting and does not directly treat the cause-specific application), (b) §1.1 now notes that the AAA practice note is in the context of pension obligation measurement, (c) for OECD (2023) the specific claim could not be located in the source, so §1.1 was rewritten as a general statement without attribution and the entry removed (the bibliographic details are preserved in a comment at the top of `13_references.md` for potential reinstatement). **Nothing remains unverified.** The yield curve creation tool file was inspected with openpyxl, confirming the valuation date "end of March 2026" and the 13 observed maturities (1–10/15/20/30 years) match the description in §8.1. Since the hosting page shares a common URL across valuation dates, the References entry is dated by "valuation-date version" rather than publication date. The tool was also added as item 5 of `DATA_SOURCES.md`, where it had been missing
2. **Finalize the Abstract.** Authorship is now settled as a **single-author paper by Shuto Hoshi / Milliman** (2026-08-05). Accordingly, all plural references ("the authors") in the main text and the Acknowledgment have been unified to the singular (§1.2, §2.1, §9.3, §11, §12). What remains: the Abstract is still the draft derived from §1 and §11, and has not been checked against the guidance's word-count and formatting requirements. Note that changing the title, abstract, or presenter after registration requires notifying the secretariat (the guidance deadline was 7/31)

   **⚑ Fixes needed on the public repository side**: the citation examples in `CITATION.cff` and the README read "Hoshi, S. et al." — drop the `et al.`. Also, the README's citation example calls this congress the "32nd", but ICA 2026 Tokyo is correctly the "**33rd**" (per the header of the official guidance). If co-authors are added, handle everything together: adding them to the front matter, designating the corresponding author, revisiting the singular wording in the main text, and updating `CITATION.cff`
3. **Finalize the generative-AI disclosure statement to match actual usage** (tool names and scope)
4. ~~**Decision on whether to publish the reproduction package**~~ → **Resolved (2026-08-05).** The public repository https://github.com/shutohoshi153/scale-bb-d is ready (public; MIT, figures CC BY 4.0; `DATA_SOURCES.md` and `CITATION.cff` bundled). The Availability statement in §4.5 now gives the URL and license split, and a References entry was added. All `reproduction/...` and `_scalebb_core/...` references throughout the paper resolve against this repository
5. **Treatment of the §3.3 APC extension** (move it to an appendix, or add APC-inclusive DA results to §6)
6. ~~**The §8.5 rounding inconsistency**~~ → **Resolved (2026-08-05).** Checking the computation output (`ScaleBB/Research/output/bel_demo/esr_life_risk_summary.csv`) gave current estimate 327,987.72, MOCE 32,285.59, insurance liability 360,273.31 — **every value in the table was correctly rounded**. The apparent 1-yen difference arises because the first two both round upward, so the values were left unchanged and a note was added right after the table (stating the unrounded values). The same note records that the diversification effect −34% is a rounding of −33.7%
7. ~~**Remaining redundancy reduction**~~ → **Resolved (2026-08-05).** (a) §7.5 (the preview of adoption burden) overlapped with §9.2, so the whole subsection was deleted and its gist absorbed as two sentences at the end of §7.4; former §7.6 (two-layer application) was promoted to §7.5, and the roadmap at the top of §7 and the cross-reference in §10.1 were fixed. (b) Re-explanations of the narrative structure were consolidated into their proper homes: §1.3, §5.4, §6.4, and §11. The bridge passage at the end of §4 no longer pre-announces results and is down to one sentence; the bridges at the end of §5 and §6 each lost their overlap with the preceding subsection and are one sentence; the openings of §6 and §7 were compressed by removing repetition of the previous chapter's results (the italic end-of-chapter bridge format itself is retained)
8. **Internal clearance** (the in-house system adoption track record in §9.3; the ESR calculations in §8)

Note that the policy is not to conduct peer review (confirmed 2026-08-05). The Peer Review Authorisation Form therefore need not be submitted, but under the guidance's principle that "the responsibility for demonstrating the value of the paper rests with the author," the self-verification items 0, 1, and 6 above carry correspondingly more weight. As all three are resolved, the top priority before the Final deadline (9/30) has shifted to **item 8 (internal clearance)**. Since the public repository now exists, note that the scope of clearance also covers the code and data being published.

**Known file corruption → resolved (2026-08-05)**

The invalid UTF-8 byte sequences in `sections_en_b1/09_practical_implementation_guidelines.md` were removed by rewriting the whole file in clean UTF-8 (the comment block containing the corrupted duplicate paragraphs of the old version was also deleted wholesale, as instructed). All 14 files under `sections_en_b1/` were then inspected by full-file reads; no other mojibake was found. Note that partial reads via MCP (head/tail ranges) can split multibyte characters at chunk boundaries and display "��" — this is a display artifact, not corruption of the actual data. Before rebuilding the PDF, running a strict decode check on the WSL side (`bytes.decode('utf-8', errors='strict')`) once is recommended as a precaution.

**PDF build-side issue (the source is fine)**

In `Paper_ICA2026_draft_EN.pdf`, the §6.4 heading and opening sentence and the caption of Figure 6.2 were missing, although both exist in the Markdown source. This looks like a pagination accident during conversion — be sure to inspect visually after each rebuild.

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
