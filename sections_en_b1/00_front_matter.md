<!-- 前付け（著者・Abstract・Keywords）。表題ページ自体は pandoc の -M title / -M date が生成するため、本ファイルでは表題を繰り返さない。 -->

# Authors

Shuto Hoshi, Milliman

<!-- 著者名・所属は確定済（2026-08-05）。現時点で単著。
     共著者を加える場合は、ここへの並記・責任著者の明示・本文の単数形表記（the author）の
     見直し・公開リポジトリの CITATION.cff の更新をまとめて行うこと。
     なお提出テンプレートが連絡先（メールアドレス等）を求める場合は追記すること。 -->

# Abstract

This paper extends Scale BB, the mortality improvement scale published by the Society of Actuaries in 2012, from all-cause mortality to cause-specific (disease-specific) mortality. We call the extended framework Scale BB-D. We test it with a 3-cutoff backtest on a panel built from Table 5-15 of the Vital Statistics of Japan (1950–2024), covering 8 disease groups. The results form three steps. First, the original goal fails: as a point forecast, Scale BB-D is worse in MAPE than the best of three simple baselines in all 24 disease × sex cells at every cutoff. Second, when we measure the same output by the direction of change, the picture reverses: the directional accuracy for the six main diseases reaches 77.7–95.0%, a clear gap over the baselines, which hold direction information only by chance or not at all. Third, this validated direction is exactly the property that economic-value-based valuation (ICS, IFRS 17, and ESR in Japan) requires: an explicit improvement-rate output whose direction has been validated can generate level, trend, and catastrophe shocks, sensitivity disclosure, and ORSA stress with internal consistency. A BEL sensitivity demonstration that follows the ESR implementation details shows the practical stake: the trend shock has a clear age gradient (+31 to 32% at entry age 30 against +10 to 11% at entry age 60), a structure that the current practice of static tables with uniform factors cannot express in principle. We conclude that the value of Scale BB-D is not point forecasting. It is a scenario generator for insurance contingent on specific diseases.

<!-- TODO(著者確認): Abstract は §1・§11 から起こしたドラフト。ICA2026 ガイダンスの語数制限・体裁要件を確認のうえ、著者が内容を確定させること。 -->

Keywords: mortality improvement scale; Scale BB; cause-specific mortality; Age-Period-Cohort model; backtest; directional accuracy; scenario generation; economic-value-based valuation; ICS; IFRS 17; ESR

---
