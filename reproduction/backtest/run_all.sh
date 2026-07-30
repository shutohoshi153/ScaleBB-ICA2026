#!/usr/bin/env bash
# =============================================================================
# Paper_ICA2026 §3 再現ドライバ (ワンショット)
#
# §3 で記述した検証パイプラインを、生の人口動態統計 5-15 表から全成果物まで
# 一括再生成する。出力はすべて ./output/ 配下に生成される。
#
# 使い方:
#     bash run_all.sh                 # 既定 Python (python3) を使用
#     PY=/path/to/venv/bin/python bash run_all.sh   # 明示指定
#
# 依存: pandas / numpy / scipy / matplotlib (リポジトリ .venv に同梱済み)
# =============================================================================
set -euo pipefail

# スクリプト自身のディレクトリで実行 (import _paths を解決するため)
cd "$(dirname "$0")"

# Python 実行体: 環境変数 PY 優先 → リポジトリ .venv → python3
# (backtest/ は ICA/Paper_ICA2026/reproduction/backtest/ にあり、.venv はリポジトリルート)
if [[ -n "${PY:-}" ]]; then
    :
elif [[ -x "../../../../.venv/bin/python" ]]; then
    PY="../../../../.venv/bin/python"
else
    PY="python3"
fi
echo "[run_all] using Python: $($PY --version 2>&1)  ($PY)"

echo ""
echo "=== [1/5] パネル構築 (5-15 表 → data/disease_panel_mortality.csv) ==="
$PY build_panel.py

echo ""
echo "=== [2/5] ScaleBB fit/project + ベースライン (3 cutoff) ==="
# --- cutoff = 2014 (10年先予測 → output/) ---
$PY run_backtest.py --train-cutoff 2014 --validation-end 2024
$PY run_baselines.py --train-cutoff 2014 --validation-end 2024 --trend-window 15
# --- cutoff = 2021 (3年先予測 → output/cutoff_2021/) ---
$PY run_backtest.py --train-cutoff 2021 --validation-end 2024 --output-subdir cutoff_2021
$PY run_baselines.py --train-cutoff 2021 --validation-end 2024 --output-subdir cutoff_2021 --trend-window 15
# --- cutoff = 2022 (2年先予測 → output/cutoff_2022/) ---
$PY run_backtest.py --train-cutoff 2022 --validation-end 2024 --output-subdir cutoff_2022
$PY run_baselines.py --train-cutoff 2022 --validation-end 2024 --output-subdir cutoff_2022 --trend-window 15

echo ""
echo "=== [3/5] cutoff 横断比較 (→ output/cutoff_comparison/) ==="
$PY compare_cutoffs.py

echo ""
echo "=== [4/6] 方向性的中率 §3.4 (→ output/directional/) ==="
$PY compute_directional_accuracy.py

echo ""
echo "=== [5/6] キャリブレーション回復図 §6.5 (→ output/directional/ + 図 6.3) ==="
$PY make_calibration_recovery_figure.py

echo ""
echo "=== [6/6] 論文掲載図の生成・収集 (→ ../../sections/figures/) ==="
$PY make_paper_figures.py

echo ""
echo "[run_all] 完了。成果物は ./output/ (論文掲載図は ../../sections/figures/) を参照。"
