# generational — 予定発生率表 生成スクリプトと追跡検証環境

> 本パッケージは `Paper_ICA2026/reproduction/` の一部です（旧 `CoAuthor_Share_20260711/05_reproduction/`
> から 2026-07-22 に移行）。論文 **§3.3（APC拡張）** の再現と、その前向き実行系である世代投影
> （発行年別 予定率テーブル生成。本文の章としては扱わず、本 README で説明）に対応します。
> 姉妹パッケージ `../backtest/`（点予測精度・方向性的中率、§3.4/§5/§6）とアルゴリズムコアを共有し、
> 両者を合わせて §3 全体を再現します。分担の全体像は `../README.md` を参照。

ScaleBB (APC拡張) による**予定疾病発生率テーブル**の生成パイプライン一式を、
共同執筆者の手元で再実行・追跡検証できる形で同梱したものです。
2026-07-15 に本ディレクトリのコピー上で一連の再現実行を行い、
基準出力と一致することを確認済みです（§5 参照）。

## 1. データ出所に関する重要な注記（誤解防止）

- **予定発生率表の入力データは e-Stat 人口動態統計の疾病別死亡率**
  （`KDB/data/processed/mortality_apc_panel.parquet`、死亡率を発生率のプロキシとして使用）です。
- **がん研究センター（国立がん研究センター）由来のデータ = 全国がん登録（NCR）罹患率**
  （`KDB/data/RowData/cancer_incidenceNCR(2016-2023).xls`、出典: 国立がん研究センター
  がん情報サービス「がん統計」（全国がん登録））は、
  予定率表の入力では**なく**、真の罹患率としての **最高品質（A-tier）ベンチマーク** に使われます
  （`KDB/scripts/build_cancer_registry_panel.py` が発生率パネル化 → `population_incidence` に
  `rate_type='registry'` として格納）。同梱している `.xls` は提供元からダウンロードした原本
  そのままであり、パネル化後の数値は本研究による加工物です（提供元は加工結果に責任を負いません）。
- 死亡率ベース予定率とがん登録罹患率ベースの乖離定量化は、仕様書
  `docs/apc_predicted_rate_tables_by_sex_20260423.md` §B.9 に**今後の課題**として記載されています。
- **用語について（2026-07-15 改題に伴う補足）:** 本パイプラインが生成する「予定発生率テーブル」は、
  実体としては**死因別死亡率**（人口10万対）から計算した率テーブルです。論文の枠組み（改題後）では、
  この死因別死亡率を **(i) 医療保険の疾病発生率に対する代理**、**(ii) 特定疾病死亡保障に対する
  対象そのもの（直接のアサンプション）** という二層で用います。ファイル名・旧ラベルの「発生率
  （incidence）」表記は製品面の呼称であり、入力・計算は一貫して死因別死亡率である点にご留意ください
  （アルゴリズムは入力の意味に非依存のため、再現結果・数値は不変）。

## 2. 構成

| パス | 内容 |
| --- | --- |
| `KDB/` | 実行環境（自己完結の SQLite + Python アプリのコピー）。スクリプト・アルゴリズムコア・設定・入力データを含む |
| `KDB/scripts/build_cancer_registry_panel.py` | **がん登録（NCR）→ 発生率パネル** 変換スクリプト |
| `KDB/data/lifetable/seimeihyo960718.xlsx` | 標準生命表（出典: 公益社団法人日本アクチュアリー会「標準生命表1996 / 2007 / 2018」の 7 系統を単一ブックに束ねたもの）。入力データの妥当性検証用（§4.3） |
| `KDB/src/experience_rate/_scalebb_core/` | ScaleBB / APC アルゴリズムコア（2D Whittaker-Henderson、コホート罰則、世代投影） |
| `KDB/config.yaml` | パラメータプリセット（現在は **20歳始（age20）版** の設定状態） |
| `docs/apc_predicted_rate_tables_by_sex_20260423.md` | **仕様・工程書**: 目的、入力、パイプライン全体図、全再現コマンド、結果サマリ |
| `docs/age20_pipeline_migration_20260423.md` | 20歳始拡張の経緯と設定変更 |
| `reference_output/` | **追跡検証用の基準出力**（研究側で生成済みの現行成果物のスナップショット） |
| `reference_output/predicted_rate_apc/` | APC版 予定率表（issue_age=40、発行年2024–2028） |
| `reference_output/predicted_rate_apc_age20/` | APC版 予定率表（issue_age=20） |
| `reference_output/predicted_rate_tables/` | 従来AP版（比較用） |
| `reference_output/scalebb_apc_*.parquet ほか` | fit / projection の中間成果物 |

リポジトリ原本: `KDB` は `ICA/ValidationTools/KDB/`、仕様書は `ICA/ScaleBB/Research/docs/`。
容量削減のため e-Stat 生データ（`estat_api/`, `estat_processed/`, 約235MB）は同梱していません
（パネル類は構築済みのものを `KDB/data/processed/` に同梱）。

> **経験率（A/E）分析機能の除外について**
> 本研究では実績の保有（In-Force）・異動（Movement）・請求データを一切使用せず、
> 経験率（A/E）分析も利用しません。そのため `KDB` 原本が備える以下の機能は
> **本配布物から除外**しています。同梱しているのは人口統計（e-Stat / 全国がん登録）
> のみを入力とする経路です。
>
> - 個人医療保険インポータ（`ins_*` テーブル群、`import-validate` / `import-table` /
>   `import-all` / `import-history`、YAML マッピング定義）
> - 経験率・ベンチマーク分析（`analyze` / `analyze-benchmark`）
> - Web UI / REST API（`serve`、FastAPI 一式）
> - サンプル契約データ生成（`generate_medical_sample.py` / `generate_lapse_sample.py`）
>
> 原本の該当機能を参照したい場合は `ICA/ValidationTools/KDB/` を参照してください。

## 3. セットアップ

Python 3.11+ を想定。すべて `KDB/` ディレクトリ直下で実行します。

```bash
cd Paper_ICA2026/reproduction/generational/KDB
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=src

python -m experience_rate init --drop   # SQLite スキーマ初期化
```

> 仕様書内のコマンド例は PowerShell 表記（`` ` `` 改行、`$env:PYTHONPATH`）かつ
> 旧ディレクトリ構成（`../data/processed/...`）です。本環境では bash +
> KDB 内相対パス（`data/processed/...`）に読み替えてください（下記が読み替え済み手順）。

## 4. 再現手順

### 4.1 予定発生率表（APC版、男女 × 3疾病）

```bash
# ① APC fit（2D WH平滑化 + コホート罰則 + COVIDダミー）
python -m experience_rate scalebb-apc-fit --source mortality --sex male \
  --disease cancer heart_disease cerebrovascular --use-preset --run-id male_repro

# ② projection（改善率 × 長期率Lブレンド、〜2100年）
python -m experience_rate scalebb-apc-project \
  --fit data/processed/scalebb_apc_fit_male.parquet --use-preset --run-id male_repro_proj

# ③ 世代投影テーブル（発行年別 1D [age]、log-linear 単年齢補間）
python -m experience_rate scalebb-gen-table --run-id male_repro_proj --use-preset \
  --output-dir data/processed/predicted_rate_repro

# female も --sex female / fit ファイル名 female で同様に実行
```

**注意**: 同梱の `config.yaml` は **age20 プリセット**（`age_min=20, issue_age=20, lam_col=60`）の
状態です。この設定での出力は `reference_output/predicted_rate_apc_age20/` に対応します。
issue_age=40 版（`reference_output/predicted_rate_apc/`）を再現する場合は、仕様書 §4.1 の
40歳始パラメータ（`age_min=40, lam_col=40, issue_age=40`）に `config.yaml` を戻すか、
CLI 引数で明示指定してください。

### 4.2 がん登録（がん研究センター NCR）パネルの構築

```bash
python scripts/build_cancer_registry_panel.py                    # 単体実行（行数・内訳を表示）
python scripts/build_cancer_registry_panel.py --output data/processed/registry_panel.csv
python -m experience_rate load-incidence                          # 同梱の incidence_panel を DB へロード
python -m experience_rate export-incidence --rate-type registry \
  --output output/registry_rates.csv                             # 罹患率を条件付きで CSV 出力
```

がん登録（NCR）由来の罹患率は `population_incidence` に `rate_type='registry'`,
`quality_flag='A'` として格納されます（§1 のとおり予定率表の入力ではなく、
真の罹患率としての最高品質ベンチマーク）。本再現環境には契約データがないため、
経験率との A/E 対比は行いません（§2 の注記を参照）。

> **パネル再構築スクリプトについての注意**: `scripts/build_incidence_panel.py` /
> `build_los_panel.py` / `build_discharge_panel.py` / `build_initial_visit_panel.py` は
> e-Stat 生データ（`data/RowData/estat_processed/`、§2 のとおり容量削減のため**未同梱**）を入力とします。
> 未同梱のまま実行すると該当サブビルダが 0 行を返すため、同梱済みパネルを縮退版で
> 上書きしないよう、`build_incidence_panel.py` と `build_los_panel.py` は書き込みを中止します
> （意図的に上書きする場合のみ `--force`）。同梱パネルはそのまま使えるので、
> 通常の再現手順でこれらを再実行する必要はありません。

### 4.3 標準生命表との整合性検証（入力データの妥当性チェック）

```bash
python scripts/analyze_standard_life_table.py
```

公益社団法人日本アクチュアリー会公表の標準生命表（`data/lifetable/seimeihyo960718.xlsx`、
生保標準生命表 1996 / 2007 / 2018 および第三分野標準生命表 2007 / 2018 の 7 系統。
加工前の原データは同会公表の「標準生命表1996」「標準生命表2007」「標準生命表2018」）と、
本パイプラインの入力である e-Stat 人口動態の死因別死亡率（`population_incidence`,
`rate_type='mortality'`）を突合し、`ratio = population_rate / standard_rate` を算出します。
死亡保険用は安全割増により `ratio < 1`、年金開始後用は `ratio > 1` となることが
保険数理上の期待で、`[5] 妥当性チェック` に期待符号との一致が `[OK]` で表示されます
（第三分野は罹患率概念のため `[REF]` = 参考値）。

**予定発生率表の生成経路とは独立**した入力データの妥当性検証であり、
本スクリプトを実行しなくても §4.1 の再現結果は変わりません。
出力は `output/standard_vs_population_{band10,detail}.csv`、
`standard_vs_population_judgement.csv`、`standard_life_table_tidy.csv`、
`disease_breakdown_std2018_male_40_59.csv` に保存されます。
なお `population_incidence` を参照するため、先に §4.2 の `load-incidence` を実行してください。

## 5. 追跡検証の方法（実施済み）

再現出力を `reference_output/` と突き合わせます。

```bash
diff data/processed/predicted_rate_repro/predicted_rate_cancer_male_issue2026_ia20.csv \
     ../reference_output/predicted_rate_apc_age20/predicted_rate_cancer_male_issue2026_ia20.csv
```

**2026-07-15 実施の検証結果**: 本コピー環境で `init → scalebb-apc-fit（cancer, male）→
scalebb-apc-project → scalebb-gen-table` を実行し、`predicted_rate_cancer_male_issue2026_ia20.csv`
を基準出力と比較。**全46行が有効数字15桁レベルで一致**（相対差 ~1e-15、浮動小数点演算順序に
起因する最終桁のみの差）を確認しました。この検証実行の生成物
（`KDB/experience_rate.db`、`KDB/data/processed/scalebb_apc_fit_male.*` /
`scalebb_apc_projection_male.*`、`KDB/data/processed/predicted_rate_verify/`）は
そのまま残置しています。ゼロから再実行する場合は `init --drop` で DB を作り直してください。

そのほかの検証手段:

- `python -m experience_rate scalebb-runs --last 10` — 実行履歴とパラメータ（config_json）の監査
- fit / projection の中間値は `reference_output/scalebb_apc_*.parquet` と比較可能
- DB スキーマ・格納件数の期待値は仕様書 §6.1 / §B.4 に記載

## 6. スクリプトの仕様・目的の参照先

| 知りたいこと | 参照先 |
| --- | --- |
| パイプラインの目的・入力・全体図・パラメータ・結果 | `docs/apc_predicted_rate_tables_by_sex_20260423.md` |
| 20歳始拡張の動機と設定差分 | `docs/age20_pipeline_migration_20260423.md` |
| 数理的定式化（APC・識別性） | `../../../ScaleBB/Research/docs/methodology_apc_extension_20260422.md`（論文 §3.3 に対応） |
| CLI 全般・DB スキーマ | `KDB/README.md`、`KDB/docs/Scale_BB機能.md` |
| NCR パネル化の入出力仕様 | `KDB/scripts/build_cancer_registry_panel.py` 冒頭 docstring |
