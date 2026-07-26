# Paper_ICA2026 — 公開用論文マニュスクリプト

International Congress of Actuaries (ICA) 提出論文の**公開用ドラフト置き場**。

**題目:** *Extending Scale BB from All-Cause to Cause-Specific Mortality: A Scenario Generator for Disease-Contingent Insurance under Economic-Value-Based Valuation (ICS/IFRS 17)*

## このディレクトリの位置づけ

- 本ディレクトリは、**共著者・査読者と継続的に共有していく公開用の正本**。清書済みの本文と、その再現検証環境を集約する。研究側の素材・分析コード・作業メモは `ScaleBB/Research/`, `ScaleBB/BackTest_2015_2024/` 等に散在するが、公開・共有の対象は本ディレクトリに一本化する。
- 再現環境は、旧 `CoAuthor_Share_20260711/05_reproduction/`（世代別予定率生成）を 2026-07-22 に本ディレクトリへ移行し、バックテストと合わせて `reproduction/` 配下に統合済み。
- 章立ては `ScaleBB/Research/docs/Paper_Outline_20260710.md`（2026-07-15 共著者合意版）に準拠。
- 数式は LaTeX 記法（`$...$` / `$$...$$`）で記述する。
- 執筆言語は日本語ドラフト（最終稿は英訳予定。アウトライン参照）。

## 構成

| パス | 内容 | 状態 |
|---|---|---|
| `sections/03_data_and_methodology.md` | §3 データと手法（本文） | ドラフト初稿（2026-07-21） |
| `sections/04_backtest_design.md` | §4 検証設計（本文） | ドラフト初稿（2026-07-22） |
| `sections/05_results_point_forecast.md` | §5 点予測精度の結果（本文） | ドラフト初稿（2026-07-22） |
| `reproduction/` | §3–§5 の**再現パッケージ群**（分担説明は `reproduction/README.md`） | — |
| `reproduction/backtest/` | 点予測精度 + 方向性的中率（§3.1/3.2/3.4・§5・§6）。自己完結・単体実行可 | 動作確認済み（2026-07-22） |
| `reproduction/generational/` | APC世代別 予定率テーブル生成（§3.3・§8A）。KDB CLI | 追跡検証済み（2026-07-15） |

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

本リポジトリは著者の作業リポジトリから一方向で同期される公開ミラーのため、
`main` への直接コミットは次回同期で巻き戻される。変更は Issue または
`main` 以外のブランチからの Pull Request でお願いしたい。詳細は
[`CONTRIBUTING.md`](CONTRIBUTING.md) を参照。

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
