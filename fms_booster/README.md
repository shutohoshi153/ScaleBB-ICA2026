**日本語** | [English](README.en.md)

# fms_booster — FMS Booster 実行パッケージ(§8 BEL 感応度デモの実務モデル再実行)

論文 §8 の BEL 感応度デモ(簡易 Python 版)を、実務プロジェクションモデル **FMS Booster** 上で再実行するための一式。実行ケースは Tier 1(ケース A/B/C)= (A) BASE の PV レベル突合(V1b)、(B) 6 シナリオ × 8 MP の感応度再現、(C) 実行負荷の実測(§9.2 論拠 4・§10.4 第一項)。

詳細は **[`docs/FMS_BoosterRunCases_Tier1_20260805.md`](docs/FMS_BoosterRunCases_Tier1_20260805.md)**(実行ケース定義書)を参照。

## 構成

| パス | 内容 | 状態 |
|---|---|---|
| `docs/FMS_BoosterRunCases_Tier1_20260805.md` | 実行ケース定義書(方式決定・受入基準 V1b-①②③・RUN 一覧・GParam/SParam 設定・診断手順) | 確定(2026-08-05) |
| `docs/BEL_Demo_WorkInstruction_FMS_20260710.md` | 原作業指示書(Tier 定義の出発点。定義書 §1–§2 で一部を精緻化・上書き) | 参照用 |
| `docs/bel_demo_effort_log.md` | ケース C の計測記録(記入欄あり。**FMS 実行と同時進行で記入**) | 記入待ち |
| `fms_input/BELDemo_{Input,Assump,Scn,MP}.db` | FMS 接続用 SQLite 4 ファイル(定義書 §4.1。検証合格済み: 突合 23,314 件・不一致 0) | 生成・検証済み |
| `fms_input/tbl_*.csv` | 上記テーブルの CSV ミラー(目視確認用) | 同上 |
| `fms_input/fms_run_case_map.csv` | MP×SCN ↔ PROD_CD / 率コード対応表 | 生成済み |
| `fms_input/fms_expected_pv.csv` | ミラー PV・年次 BEL・予測ギャップ(事前モード出力) | 生成済み |
| `scripts/verify_v1b_fms_pv.py` | 事前モード(期待値表生成)+ 突合モード(V1b-①②③ 判定)。**パス定義のみ本パッケージ配置に変更、ロジックは作業リポジトリ版と同一** | 動作確認済み |
| `reference_output/bel_by_mp_scenario.csv` | 論文 §8 の年次 BEL(V1b-②③ の比較対象) | 同梱 |
| `reference_output/verify_fms_input_tables.csv` | 入力テーブル独立検証(V1a-F)の合格記録 | 同梱 |
| `output/` | 突合モードの出力先(git 追跡外) | — |

## 同梱していないもの

- **FMS Booster モデルソース(`Scenario_Model_BELDemo/` = `Base_Model_v251208/` の無改変コピー)** — ベンダー提供物のため本リポジトリ(public)には同梱しない。実行は社内の B-FMS 環境にあるモデル(作業リポジトリ `ValidationTools/BoosterFMS/Scenario_Model_BELDemo/`)を使用すること。データ注入方式のため**モデル改修は 0 行**(定義書 §1)。
- ベンダーのコーディングガイド PDF — 同上。
- 入力テーブルの生成・独立検証スクリプト(`build_fms_input_tables.py` / `verify_fms_input_tables.py`)— 上流の簡易 Python 版パイプライン(`ScaleBB/Research/scripts/bel_demo/`)のデータに依存するため未同梱。生成済み DB は検証合格済みで、合格記録は `reference_output/verify_fms_input_tables.csv` に同梱。

## 実行手順(要約。詳細は定義書 §3–§7)

```bash
# ① 事前確認(任意): 期待値表が再現されること
cd fms_booster && python3 scripts/verify_v1b_fms_pv.py
#    → fms_expected_pv.csv(48 セル)。規約差ギャップ −5.07〜−3.65% が表示されれば OK

# ② FMS 側(Windows / B-FMS 実行環境)
#    - Scenario_Model_BELDemo/(社内環境)をモデルとして読込み
#    - fms_input/ の 4 DB を定義書 §4.2 のとおり接続、GParam/SParam を §4.2〜4.3 のとおり設定
#    - 定義書 §3 の RUN-00 → RUN-A1 → RUN-B1..B5(→ 任意で RUN-C1)を順に実行
#      ★ セルは保険期間の昇順(加入年齢 60 → 50 → 40 → 30)厳守(§3 冒頭)
#    - 所要時間を docs/bel_demo_effort_log.md に記入

# ③ 突合(FMS の S03 出力 CSV をこの環境へ持ち帰る)
python3 scripts/verify_v1b_fms_pv.py \
  --fms-csv <RUN_A1 の *_PV_ByPol.csv> --fms-csv <RUN_B1 の…> …(6 Run 分)
#    → output/verify_v1b_fms_pv.csv に V1b-①②③ の判定付き突合表
```

## 作業リポジトリとのパス対応

定義書・作業指示書の中のパスは作業リポジトリ基準で書かれている。本パッケージとの対応は以下のとおり。

| 文書中の参照(作業リポジトリ) | 本パッケージ |
|---|---|
| `ScaleBB/Research/docs/FMS_BoosterRunCases_Tier1_20260805.md` ほか docs | `docs/` |
| `ScaleBB/Research/data/processed/bel_demo/fms_input/` | `fms_input/` |
| `ScaleBB/Research/scripts/bel_demo/verify_v1b_fms_pv.py` | `scripts/verify_v1b_fms_pv.py`(パス定義のみ変更) |
| `ScaleBB/Research/output/bel_demo/bel_by_mp_scenario.csv` | `reference_output/bel_by_mp_scenario.csv` |
| `ScaleBB/Research/output/bel_demo/verify_v1b_fms_pv.csv`(突合結果) | `output/verify_v1b_fms_pv.csv` |
| `ValidationTools/BoosterFMS/{Base_Model_v251208,Scenario_Model_BELDemo}/` | **同梱せず**(社内 B-FMS 環境を使用) |
