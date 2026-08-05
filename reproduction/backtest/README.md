**日本語** | [English](README.en.md)

# backtest — §3 バックテスト再現パッケージ

本ディレクトリは、論文 §3「データと手法」の**バックテスト**（点予測精度と方向性的中率）を、**単体で再現検証**できるようにした自己完結パッケージである。生の人口動態統計 5-15 表から、点予測精度（§5）・方向性的中率（§6）の全成果物までを一括再生成する。

リポジトリの他ディレクトリには一切依存しない（入力データ・アルゴリズムコアをすべて同梱）。

各スクリプトの処理内容（入力・処理・出力）の詳細な解説は [SCRIPTS.md](SCRIPTS.md) を参照。

> `Paper_ICA2026/reproduction/` の 2 パッケージの一方。姉妹パッケージ `../generational/`
> （APC世代別予定率生成、§3.3。詳細は `../generational/README.md`）とアルゴリズムコア・入力死亡率データを共有する。
> 分担と整合性の全体像は `../README.md` を参照。

---

## クイックスタート

```bash
# リポジトリ .venv を使う場合 (推奨。pandas/numpy/scipy/matplotlib 同梱)
bash run_all.sh

# Python を明示指定する場合
PY=/path/to/python bash run_all.sh
```

数分で完了し、全成果物が `./output/` 配下に生成される。

**依存:** Python 3.10+、`pandas` / `numpy` / `scipy` / `matplotlib` のみ。

---

## パッケージ構成

```
backtest/
├── run_all.sh                       ワンショット再現ドライバ (§3 全パイプライン)
├── _paths.py                        自己完結パス層 (下記「元スクリプトからの改変」参照)
├── build_panel.py                   [1] 5-15 表 → 疾病パネル (§3.1)
├── run_backtest.py                  [2] ScaleBB fit/project + 検証 (§3.2)
├── run_baselines.py                 [3] naive/mean_3pts/loglin ベースライン (§3.4.1)
├── compute_directional_accuracy.py  [4] 方向性的中率 DA (§3.4.2, 式 3.11–3.12)
├── compare_cutoffs.py               [5] 3 cutoff 横断比較 (§4)
├── make_calibration_recovery_figure.py  [6] 方向反転疾病の再キャリブレーション実験 (§6.5, 図 6.3)
├── make_paper_figures.py            [7] 論文掲載図の生成・収集 (→ ../../sections/figures/)
├── vendor/
│   └── experience_rate/_scalebb_core/
│       ├── model.py                 Scale BB コア (§3.2, 式 3.1–3.6)。KDB から無改変で同梱
│       └── apc_model.py             APC 拡張 (§3.3, 式 3.7–3.8)。参照用に同梱
├── data/
│   ├── raw/5-15_…_0003411659.csv    入力: 人口動態統計 5-15 表 (1950–2024)
│   ├── disease_estat_mapping.csv    疾病 → 死因コード対応 (§3.1.2)
│   └── prebuilt_disease_panel_mortality.csv   build_panel の期待出力 (照合用)
└── output/                          [生成物] run_all.sh で再構築 (git 管理外)
```

## 実行順序と §3 との対応

`run_all.sh` は報告書の再現手順に従い、以下を順に実行する。

| 順 | スクリプト | 生成物 | §3 の対応 |
|---|---|---|---|
| 1 | `build_panel.py` | `data/disease_panel_mortality.csv`（8疾病×3性別×25年×21年齢＝12,600行） | §3.1 データ・疾病マッピング |
| 2 | `run_backtest.py`（cutoff 2014/2021/2022） | `output[/cutoff_*]/tables/validation_summary.csv` ほか | §3.2 ScaleBB fit/project、式 (3.1)–(3.6) |
| 3 | `run_baselines.py`（同 3 cutoff） | `output[/cutoff_*]/tables/validation_summary_baseline.csv` ほか | §3.4.1 ベースライン、§3.4.2 MAPE/bias（式 3.9–3.10） |
| 4 | `compare_cutoffs.py` | `output/cutoff_comparison/` | §4 検証設計（3 cutoff 横断） |
| 5 | `compute_directional_accuracy.py` | `output/directional/` | §3.4.2 方向性的中率 DA（式 3.11–3.12）→ §6 |
| 6 | `make_calibration_recovery_figure.py` | `output/directional/tables/calibration_recovery.csv`、図 6.3（コミット対象） | §6.5 方向反転疾病の再キャリブレーション実験（liver / hypertensive、L・P 再設定 × cutoff） |
| 7 | `make_paper_figures.py` | `../../sections/figures/`（コミット対象） | 本文 §3・§4 の説明図の生成と、§5・§6 が参照する成果図の収集 |

## 期待される主要数値（照合用グラウンドトゥルース）

再現が正しく走ったかは、以下の代表値で確認できる（`sex=total`, cutoff=2014）。すべて論文 §5・§6 の表と一致する。

**ScaleBB MAPE [%]**（`output/cutoff_comparison/tables/scalebb_cutoff_comparison.csv`）

| disease | 2014 | 2021 | 2022 |
|---|---:|---:|---:|
| cancer | 22.41 | 9.20 | 8.87 |
| total | 26.01 | 9.33 | 7.33 |
| hypertensive | 73.83 | 24.13 | 20.53 |

**方向性的中率 DA [%]**（`output/directional/tables/directional_summary.csv`, cutoff=2014）

| disease | scalebb | naive_last | loglin_trend |
|---|---:|---:|---:|
| total | 95.00 | 0.00 | 94.29 |
| cerebrovascular | 91.04 | 0.00 | 91.04 |
| cancer | 79.71 | 0.00 | 93.48 |

`naive_last` の DA が全セルで 0.00 になるのは、構造上 $\Delta_{\text{pred}} \equiv 0$（式 3.11）となり方向情報を持たないためで、§3.4.2 の記述どおりの挙動である。

## 元スクリプトからの改変（透明性のための明記）

同梱スクリプト 5 本は、研究側 `ScaleBB/BackTest_2015_2024/scripts/` の**アルゴリズム・集計・作図ロジックを一切変更していない**。改変したのは各ファイル先頭の**パスアンカー数行のみ**である:

- 元は `ROOT = Path(__file__).resolve().parents[2]` でリポジトリルートを辿り、`KDB/src`・`ScaleBB_Research/data/raw`・`MedicalInsuranceProduct/` を参照していた。2026-07 のリポジトリ再編でこれらは無効化された。
- 本パッケージでは、入力データとアルゴリズムコアを同梱し、`_paths.py` 1 か所で解決する。各スクリプトの改変箇所には `# [REPRO]` マーカーを付した。

`vendor/experience_rate/_scalebb_core/` は KDB（`ValidationTools/KDB/src/experience_rate/_scalebb_core/`）からの**無改変コピー**であり、§3.2/§3.3 の数式に対応する実装そのものである。

## データ出典・ライセンス

- **人口動態統計 5-15 表**（統計表 ID 0003411659）: 出典 **厚生労働省「人口動態調査」（政府統計の総合窓口 e-Stat）**。政府標準利用規約（第2.0版）に基づき出典明示のうえ商用利用可。
- 同梱する第三者提供データの出典一覧・利用条件は `../../DATA_SOURCES.md` を参照。
- 本パッケージは公開データに基づく学術的検証であり、特定商品の収益性・資本要件を保証しない（論文 §10 参照）。
