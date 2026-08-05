**日本語** | [English](README.en.md)

# reproduction — §3 再現パッケージ群（査読者・共著者向け）

論文 §3「データと手法」の検証パイプラインを、単体で再現検証できる形にまとめたディレクトリ。
**2 つの相補的なパッケージ**からなり、両者を合わせて §3 全体をカバーする。

```
reproduction/
├── README.md        ← 本ファイル（分担と整合性の説明）
├── backtest/        点予測精度 + 方向性的中率の検証   （§3.1 / §3.2 / §3.4 / §5 / §6）
└── generational/    APC世代別 予定率テーブル生成       （§3.3。詳細は generational/README.md）
```

## 2 パッケージの分担

| パッケージ | 再現対象 | 実行系 | 入力 | 主な出力 |
|---|---|---|---|---|
| **`backtest/`** | バックテスト：3 cutoff × ScaleBB × 3 ベースラインの点予測 MAPE（式 3.9–3.10）と方向性的中率 DA（式 3.11–3.12） | 単体スクリプト（`run_all.sh`） | 人口動態統計 5-15 表（同梱） | `output/` 配下の検証テーブル・図 |
| **`generational/`** | APC fit/project → 発行年別 1D 予定率テーブル（世代投影） | KDB CLI（`experience_rate`） | `mortality_apc_panel`（同梱） | `reference_output/` と突合する予定率表 |

`backtest/` は「Scale BB が点予測に向くか」を検証し（結論：MAPE では劣後だが方向は当てる）、
`generational/` は「その改善率フレームワークを前向きに回して実務配布形式の率テーブルを作る」段を担う。
スコープは重複しない。

## 両パッケージの整合性（検証済み・2026-07-22）

共有ディレクトリとして矛盾がないことを以下で確認済み。

1. **アルゴリズムコアが同一**：`backtest/vendor/experience_rate/_scalebb_core/` と
   `generational/KDB/src/experience_rate/_scalebb_core/` は**ビット一致**（現行 KDB とも一致）。
   両パッケージは同一の Scale BB / APC 実装（§3.2 式 3.1–3.6、§3.3 式 3.7–3.8）を使う。
2. **入力死亡率データが同一**：両者とも e-Stat 人口動態統計の死因別死亡率が起点。
   共有セル（cancer / cerebrovascular / heart / hypertensive / total）で**完全一致**（差 0）を確認。
3. **データの二層フレーミングが共通**：死因別死亡率を (i) 医療保険発生率の代理／
   (ii) 特定疾病死亡保障の対象そのもの、として用いる（§3.1.3・generational README §1）。
4. **中核ハイパーパラメータが共通**：`long_term_rate=0.01`、`convergence_year=2035`、
   `lam_row=40`、`diff_order=2`。

### 設定・表記の差（矛盾ではなく用途差）

| 項目 | `backtest/` | `generational/` | 備考 |
|---|---|---|---|
| `lam_col`（暦年方向平滑化） | 40 | 60 | backtest は KDB 既定（BackTest 報告準拠）。generational は age20 移行で若年ノイズ抑制のため 60。各々の用途で正当（§3.2.3 脚注参照） |
| 年齢範囲 | 20–89 | 20–85（age20 プリセット） | 設定依存の軽微差 |

> 疾病スラグは両パッケージとも `heart_disease`（Hi05・心疾患・高血圧性除く）で統一済み。

## 使い方

```bash
# バックテスト（数分で全成果物を再生成）
cd backtest && bash run_all.sh

# 世代別予定率テーブル（KDB CLI。詳細は generational/README.md §3–4）
cd generational/KDB && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && export PYTHONPATH=src
python -m experience_rate scalebb-apc-fit --source mortality --sex male \
  --disease cancer heart_disease cerebrovascular --use-preset --run-id male_repro
```

各パッケージの詳細・期待される主要数値・改変点は、それぞれの `backtest/README.md` /
`generational/README.md` を参照。

## データ出典

両パッケージが同梱する第三者提供データ（人口動態調査・患者調査 / e-Stat、全国がん登録 /
国立がん研究センター、標準生命表 / 日本アクチュアリー会）の出典表記と利用条件は
`../DATA_SOURCES.md` に集約する。
