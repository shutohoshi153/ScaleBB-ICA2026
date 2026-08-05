**日本語** | [English](README.en.md)

# Paper_ICA2026 — 公開用論文マニュスクリプト

International Congress of Actuaries (ICA) 提出論文の**公開用ドラフト置き場**。

**題目:** *Extending Scale BB from All-Cause to Cause-Specific Mortality: A Scenario Generator for Disease-Contingent Insurance under Economic-Value-Based Valuation (ICS/IFRS 17)*

## このディレクトリの位置づけ

- 本ディレクトリは、**共著者・査読者と継続的に共有していく公開用の正本**。清書済みの本文と、その再現検証環境を集約する。研究側の素材・分析コード・作業メモは `ScaleBB/Research/`, `ScaleBB/BackTest_2015_2024/` 等に散在するが、公開・共有の対象は本ディレクトリに一本化する。
- 再現環境は、旧 `CoAuthor_Share_20260711/05_reproduction/`（世代別予定率生成）を 2026-07-22 に本ディレクトリへ移行し、バックテストと合わせて `reproduction/` 配下に統合済み。
- 章立ては `ScaleBB/Research/docs/Paper_Outline_20260710.md`（2026-07-15 共著者合意版）に準拠。
- 数式は LaTeX 記法（`$...$` / `$$...$$`）で記述する。
- 執筆言語は日本語ドラフト（最終稿は英訳予定。アウトライン参照）。

## 言語 / Languages

本リポジトリは日英二言語で運用する。英語圏の共著者・査読者は各英語版を参照のこと。

- **ドキュメント**: 日本語原本 `<name>.md` の隣に英語版 `<name>.en.md` を置く（例: `README.md` ⇔ `README.en.md`）。各ファイル先頭の言語リンクで相互に行き来できる。両者に差異がある場合は**日本語版を正**とする。日本語ファイル名のドキュメントは英語版で英語ファイル名を用いる（`Scale_BB機能.md` ⇔ `Scale_BB_features.en.md`、`設計書.md` ⇔ `design_document.en.md`）。
- **本文（原稿）**: 日本語ドラフトは `sections/`、英語ドラフトは `sections_en_b1/`（同一ファイル名で対応）。
- **データ・コード**: e-Stat 由来のカテゴリ名・列名など、データ値として機能する日本語文字列は翻訳せずそのまま保持する（英語版ドキュメントでは括弧書きで英語の注釈を付す）。

## 構成

| パス | 内容 | 状態 |
|---|---|---|
| `sections/01_introduction.md` | §1 序論（本文）。二つの転換（疾病率の構造変化・規制環境）→ 疾病リスク軸の空白 → 新規性 A/B → 三段の発見構造 | ドラフト初稿（2026-07-28） |
| `sections/02_related_work_and_regulatory_requirements.md` | §2 先行研究と規制要件（本文） | ドラフト初稿（2026-07-28） |
| `sections/03_data_and_methodology.md` | §3 データと手法（本文） | ドラフト初稿（2026-07-21） |
| `sections/04_backtest_design.md` | §4 検証設計（本文） | ドラフト初稿（2026-07-22） |
| `sections/05_results_point_forecast.md` | §5 点予測精度の結果（本文） | ドラフト初稿（2026-07-22） |
| `sections/06_results_directional_accuracy.md` | §6 方向性的中率の発見（本文）。方向反転疾病の再キャリブレーション実験（`reproduction/backtest/make_calibration_recovery_figure.py`）を含む | ドラフト初稿（2026-07-28） |
| `sections/07_repositioning_scenario_generator.md` | §7 シナリオ生成器への再定位（本文）。実装対応表・ESG 対比・二層適用（新規性 B） | ドラフト初稿（2026-07-28） |
| `sections/08_financial_impact_demo.md` | §8 財務インパクトのデモ（本文）。BEL 感応度デモ（簡易 Python 版・ESR 実装仕様準拠、`ScaleBB/Research/scripts/bel_demo/`）の結果を反映 | ドラフト初稿（2026-07-28） |
| `sections/09_practical_implementation_guidelines.md` | §9 実務ガイドライン（本文）。疾病別キャリブレーション指針（表 9.1、§6.5 の二経路分担と整合）・導入負担 5 論拠＋段階的導入パス（FMS 実測値なし前提）・組み込み実績 | ドラフト初稿（2026-07-28） |
| `sections/10_limitations_and_future_work.md` | §10 限界と今後の課題（本文）。代理性・長期検証可能性（蓄積待ちにしない枠組み）・キャリブレーション体系化・実務モデル再実行・確率論的拡張 | ドラフト初稿（2026-07-28） |
| `sections/11_conclusion.md` | §11 結論（本文）。三段の結果構造・二層の貢献（新規性 A/B）の再掲 | ドラフト初稿（2026-07-28） |
| `sections/figures/` | 本文掲載図（§3–§6 は `reproduction/backtest/make_paper_figures.py` ほか、図 8.1 は `ScaleBB/Research/scripts/bel_demo/aggregate_bel_results.py` で生成・収集） | 図 3.1–3.3, 4.1, 5.1–5.5, 6.1–6.3, 8.1（2026-07-28） |
| `reproduction/` | §3–§5 の**再現パッケージ群**（分担説明は `reproduction/README.md`） | — |
| `reproduction/backtest/` | 点予測精度 + 方向性的中率（§3.1/3.2/3.4・§5・§6）。自己完結・単体実行可 | 動作確認済み（2026-07-22） |
| `reproduction/generational/` | APC世代別 予定率テーブル生成（§3.3 の APC 拡張の前向き実行系。詳細は `reproduction/generational/README.md`）。KDB CLI | 追跡検証済み（2026-07-15） |

## 再現検証（査読者・共著者向け）

`reproduction/` は §3 を再現する 2 つの相補パッケージからなる。両者はアルゴリズムコア（`_scalebb_core`）と入力死亡率データを共有し、整合性は検証済み（`reproduction/README.md`「両パッケージの整合性」参照）。

```bash
# バックテスト（数分で output/ に全成果物を生成）
cd reproduction/backtest && bash run_all.sh

# 世代別予定率テーブル（KDB CLI。詳細は reproduction/generational/README.md）
cd reproduction/generational/KDB && python -m experience_rate scalebb-apc-fit --use-preset ...
```

各パッケージの詳細・期待される主要数値・元スクリプトからの改変点は各 README を参照。

## 共著者・査読者の方へ

共著者は `main` へ直接コミット・push して構わない（push 前に `git pull` すること）。
内容は著者が作業リポジトリへ取り込む際に確認する。
方針の相談や修正案が固まっていない指摘は Issue でお願いしたい。
詳細は [`CONTRIBUTING.md`](CONTRIBUTING.md) を参照。

## データ出典

同梱する第三者提供データの出典・利用条件は **[`DATA_SOURCES.md`](DATA_SOURCES.md)** に集約する。主な出典は以下のとおり。

- 厚生労働省「人口動態調査」（政府統計の総合窓口 e-Stat） — 本研究の主入力（死因別死亡率）
- 厚生労働省「患者調査」（政府統計の総合窓口 e-Stat） — 受療率・平均在院日数に基づく参照系列
- 国立がん研究センターがん情報サービス「がん統計」（全国がん登録） — 罹患率ベンチマーク
- 公益社団法人日本アクチュアリー会「標準生命表1996 / 2007 / 2018」 — 入力データの妥当性検証

リポジトリのライセンスは上記第三者データには及ばない。詳細と英文出典表記は `DATA_SOURCES.md` を参照。

## 出典・素材の対応

§3 の各節は以下を典拠とする（清書元）:

- データ・パネル仕様: `ScaleBB/BackTest_2015_2024/docs/report.md` §2
- ScaleBB アルゴリズム: `ValidationTools/KDB/src/experience_rate/_scalebb_core/model.py`、`report.md` §3
- APC 拡張: `ScaleBB/Research/docs/methodology_apc_extension_20260422.md`
- ベースライン・評価指標: `report.md` §3.3–3.4・§8.1
