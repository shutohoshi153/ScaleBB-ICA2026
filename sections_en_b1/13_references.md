# References

<!-- 引用検証の完了記録（2026-08-05）
     README「未対応」1 の原典確認を実施し、*[TO BE VERIFIED]* マーカーをすべて解消した。
     対応内容:
       - Alai et al. (2015) / Arnold & Sherris (2013): 書誌・主張内容とも確認済、マーカー除去のみ。
       - Bergeron-Boucher et al. (2017) → Kjærgaard et al. (2019) に差し替え（§2.2 本文も修正）。
       - AAA: 年金債務測定の文脈であることを §1.1 本文と本エントリの両方に明記。
       - CMI: 最新版 CMI_2025 / Working Paper 211（2026 年 3 月公表）で確定。
       - イールドカーブ作成ツール: 正式名称・URL・版を確定。openpyxl で実ファイルを検査し、
         基準日が「2026年3月末」であること、観測年限が 1–10/15/20/30 年の 13 点で
         あることを確認済み（§8.1 の記述と一致）。ツールは基準日ごとに差し替えられるが
         掲載ページの URL は共通のため、「2026年 3 月 23 日公表」という説明だけを取り下げた。
       - Vital Statistics / e-Stat: 利用規約 URL を明記（商用利用可・出典表示必須）。
         アクセス日は 2026 年 3 月で確定（著者確認済・記載済）。
       - GBD: 特定ラウンドに依存しない論旨のため、IHME プロジェクトへの一般参照に変更。
       - OECD (2023): 書誌自体は実在確認済みだが、§1.1 が帰属させていた具体的主張を
         原典で特定できなかったため、§1.1 を帰属なしの一般論に書き直し、本エントリを削除した。
         将来 PDF 本文で該当箇所（章・節）を特定できれば、帰属付きで復活させる価値がある:
         OECD (2023), Mortality and the Provision of Retirement Income, OECD Publishing, Paris,
         DOI 10.1787/a10a6c09-en. -->

Alai, D. H., Arnold, S., and Sherris, M. (2015). Modelling cause-of-death mortality and the impact of cause-elimination. *Annals of Actuarial Science*, 9(1), 167–186. DOI 10.1017/S174849951400027X.

American Academy of Actuaries, Pension Committee (2023). *Selecting and Documenting Mortality Assumptions for Measuring Pension Obligations*. Practice note, revised January 2023. Cited in §1.1; note that this practice note addresses the measurement of pension obligations, not third-sector insurance.

Arnold, S., and Sherris, M. (2013). Forecasting mortality trends allowing for cause-of-death mortality dependence. *North American Actuarial Journal*, 17(4), 273–282.

Cairns, A. J. G., Blake, D., and Dowd, K. (2006). A two-factor model for stochastic mortality with parameter uncertainty: Theory and calibration. *Journal of Risk and Insurance*, 73(4), 687–718.

Clayton, D., and Schifflers, E. (1987). Models for temporal variation in cancer rates. I: Age–period and age–cohort models; II: Age–period–cohort models. *Statistics in Medicine*, 6(4), 449–467 and 469–481.

Continuous Mortality Investigation (2026). *CMI Mortality Projections Model: CMI_2025*. CMI Working Paper 211, Institute and Faculty of Actuaries, March 2026. Calibrated to England and Wales population mortality data to 31 December 2025.

Currie, I. D., Durban, M., and Eilers, P. H. C. (2004). Smoothing and forecasting mortality rates. *Statistical Modelling*, 4(4), 279–298.

European Parliament and Council (2009). Directive 2009/138/EC on the taking-up and pursuit of the business of Insurance and Reinsurance (Solvency II).

Financial Services Agency of Japan (2025). 保険業法施行規則第八十六条及び第八十七条等の規定に基づき保険金等の支払能力に相当する額及び通常の予測を超える危険に相当する額の計算方法等を定める件 [Notice prescribing the methods of calculating the amount corresponding to the capacity to pay insurance claims and the amount corresponding to risks exceeding normal predictions, pursuant to Articles 86 and 87 of the Ordinance for Enforcement of the Insurance Business Act]. FSA Notice No. 74 of 2025 (Reiwa 7), promulgated 23 July 2025. In Japanese; the English title is an unofficial translation. https://www.fsa.go.jp/news/r7/hoken/20250723/20250723.html

Financial Services Agency of Japan (2026). 前掲告示の一部を改正する件 [Notice amending the above]. FSA Notice No. 6 of 2026 (Reiwa 8), promulgated 23 March 2026, applicable from 31 March 2026. In Japanese. https://www.fsa.go.jp/news/r7/hoken/20260323/20260323.html — the amendment consists of typographical and formatting corrections only and does not affect the provisions cited in §7–§8 of this paper.

Financial Services Agency of Japan (2026). 経済価値ベースのソルベンシー規制に関する Q&A [Q&A on the economic value-based solvency regulation], March 2026 edition (first published 23 July 2025; revised 23 March 2026). In Japanese; the English title is an unofficial translation. https://www.fsa.go.jp/policy/economic_value-based_solvency/11.pdf — cited in §2.3 (Art. 12 Q7, Q8, Q6(6): reflection of forward-looking trends in the current estimate and the objectivity and sensitivity-analysis requirements attaching to it), §3.3 (Art. 12 Q4 and Art. 72 Q3: exclusion of data arising from temporary factors, with COVID-19 named as an example), §7.2 and §8.1 (Art. 56 Q1 and Art. 60 Q1: how the prescribed life insurance stresses are applied; Art. 59 Q1: product classification for morbidity and disability risk; Art. 105 Q1: yen UFR of 3.8% and the 2.0% expected inflation embedded in it), and §9 (Art. 12 Q6 and Q11, and the interim-reporting Q&A: documentation of expert judgment, comparison of the current estimate with experience, and the data cut-off allowance).

Financial Services Agency of Japan (2026). 経済価値ベースのソルベンシー規制におけるイールド・カーブ作成ツール [Yield curve creation tool for the economic value-based solvency regulation], version for the 31 March 2026 valuation date (the workbook records its valuation date as 「2026年3月末」). In Japanese; the English title is an unofficial translation. The tool is distributed from a standing page linked from the FSA's economic value-based solvency portal and is reissued for each valuation date: https://www.fsa.go.jp/policy/economic_value-based_solvency/20260323/20260323.html — the source of the discount-curve parameters used in §8.1.

Holford, T. R. (1983). The estimation of age, period and cohort effects for vital rates. *Biometrics*, 39(2), 311–324.

Hoshi, S. (2026). *Scale BB-D — supplementary material and reproduction package*. GitHub repository. https://github.com/shutohoshi153/scale-bb-d — the reproduction package cited throughout this paper (§4.5). Source code under the MIT License; figures under CC BY 4.0.

Institute for Health Metrics and Evaluation (IHME). *Global Burden of Disease (GBD) Study*. University of Washington. https://www.healthdata.org/research-analysis/gbd — cited in §2.2 as a general reference to the GBD programme; the argument there does not depend on any particular GBD round.

International Accounting Standards Board (2017). *IFRS 17 Insurance Contracts*. IASB, effective 2023.

International Association of Insurance Supervisors (2024). *Insurance Capital Standard (ICS)*. IAIS, adopted December 2024.

Kjærgaard, S., Ergemen, Y. E., Kallestrup-Lamb, M., Oeppen, J., and Lindahl-Jacobsen, R. (2019). Forecasting causes of death by using compositional data analysis: The case of cancer deaths. *Journal of the Royal Statistical Society Series C: Applied Statistics*, 68(5), 1351–1370. DOI 10.1111/rssc.12357.

Lee, R. D., and Carter, L. R. (1992). Modeling and forecasting U.S. mortality. *Journal of the American Statistical Association*, 87(419), 659–671.

Ministry of Health, Labour and Welfare (Japan). *Vital Statistics of Japan*, Table 5-15: Trends in deaths and death rates (per 100,000 population) by cause of death, sex, and age group. Retrieved through the e-Stat portal (https://www.e-stat.go.jp/), accessed March 2026. Terms of use: https://www.e-stat.go.jp/terms-of-use (content may be freely used, reproduced and adapted, including for commercial purposes, provided the source is stated; where the content is edited or processed, that fact and the party responsible must also be stated).

Renshaw, A. E., and Haberman, S. (2006). A cohort-based extension to the Lee–Carter model for mortality reduction factors. *Insurance: Mathematics and Economics*, 38(3), 556–570.

Society of Actuaries (2012). *Mortality Improvement Scale BB Report*. SOA.

Society of Actuaries (2014). *Mortality Improvement Scale MP-2014 Report*. SOA.

Wilmoth, J. R. (1995). Are mortality projections always more pessimistic when disaggregated by cause of death? *Mathematical Population Studies*, 5(4), 293–319.
