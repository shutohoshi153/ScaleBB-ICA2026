#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V1b — FMS Booster 出力 PV との突合(2 段構え)+ FMS 月次規約ミラー計算。

【受入基準(実行ケース定義書 §6。作業指示書 §7 V1b を規約差の実測を踏まえ精緻化)】
    V1b-①(パイプライン検証・主基準): FMS 出力 Net_CF vs 本スクリプトの月次ミラー
        独立実装が全 8 MP × 6 シナリオで ±1% 以内(期待値は ≲0.1%)。
        検証対象は配管(テーブル焼込み・単位換算・月次換算・割引フォワード投入)。
    V1b-②(規約差の定量化・報告値): FMS 出力 vs 論文 §8 の年次 BEL
        (bel_by_mp_scenario.csv)の乖離を報告する。事前推定(ミラー計算)
        −5.1〜−3.7% は支払タイミング規約差(年次・年始払い vs 月次・月央払い+
        年内エクスポージャ逓減)によるもので、合否基準ではなく測定結果として
        記録する(論文 §8/§10 の「簡易モデルの限界の定量化」に転用)。
    V1b-③(感応度整合): ΔBEL%(BASE 比)が FMS と論文年次版で全セル ±0.5pp 以内。
        規約差は BASE 比でほぼ相殺される(事前推定の系統成分は最大 0.35pp、
        ICS_C の若年 MP。レベル倍率 1.125 を年次で掛けてから月次変換する順序に
        起因)ため、論文の中心的主張(トレンドショックの年齢勾配)の頑健性を
        直接確認する。

【FMS ミラーの再現規約(IXP_Prot C03/C04 に一致、解約率 0・保険料 0・事業費 0)】
    - 年次率(生成済み TBL_RSKRT の到達年齢セル)→ 月次 q_m = 1-(1-q_yr)^(1/12)
    - 月初エクスポージャ b、脱退 b·q_liv_m(解約 0 のため 0.5 クロス項は消える)、
      給付件数 b·q_dis_m、給付額 JOIN_AMT × BNFT_RT
    - 現価は後退再帰: v = (1+DC_RT(m))^(-1/12)、期中 CF は v^(1/2)
    - 入力はすべて fms_input/ の SQLite から読む(FMS が読むものをそのまま検証)

【使い方】
    事前モード(FMS 実行前): python3 verify_v1b_fms_pv.py
        → fms_expected_pv.csv(ミラー PV・年次 BEL・予測ギャップ)を生成
    突合モード(FMS 実行後): python3 verify_v1b_fms_pv.py --fms-csv <S03 出力 CSV>
        → verify_v1b_fms_pv.csv(V1b-①②③ の判定付き突合表)を生成
        S03 出力(*_PV_ByPol.csv)は CTR_POLNO 列('MP01_BASE' 形式)で対応付ける。
        複数 Run に分かれる場合は CSV を連結して渡すか、--fms-csv を複数回指定する。
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# パス定義のみ作業リポジトリ版(ScaleBB/Research/scripts/bel_demo/)から
# fms_booster/ パッケージ配置に変更。ロジックは同一。
PKG_ROOT = Path(__file__).resolve().parents[1]
FMS_DIR = PKG_ROOT / "fms_input"
REF_DIR = PKG_ROOT / "reference_output"   # bel_by_mp_scenario.csv(論文 §8 年次 BEL)
OUT_DIR = PKG_ROOT / "output"             # 突合結果の出力先(git 追跡外)

TOL_V1B1 = 0.01      # V1b-①: FMS vs ミラー ±1%
TOL_V1B3 = 0.5       # V1b-③: 感応度 ΔBEL%(BASE 比)の乖離 ±0.5pp


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, np.ndarray]:
    with sqlite3.connect(FMS_DIR / "BELDemo_Input.db") as con:
        rskrt = pd.read_sql("SELECT * FROM TBL_RSKRT", con).set_index(
            ["RSK_RT_CD", "GNDR_CD"])
        bnft = pd.read_sql("SELECT * FROM TBL_BNFT", con)
    with sqlite3.connect(FMS_DIR / "BELDemo_MP.db") as con:
        mp = pd.read_sql("SELECT * FROM TBL_MP", con)
    with sqlite3.connect(FMS_DIR / "BELDemo_Scn.db") as con:
        dc = pd.read_sql("SELECT PRD, DC_RT FROM TBL_DC_RT WHERE SCN_NO='1' "
                         "ORDER BY PRD", con)
    v_mon = (1.0 + dc["DC_RT"].to_numpy()) ** (-1.0 / 12.0)   # v_mon[m-1] = PRD m
    return rskrt, bnft, mp, v_mon


def mirror_pv(mp_row: pd.Series, bnft: pd.DataFrame, rskrt: pd.DataFrame,
              v_mon: np.ndarray) -> float:
    """FMS IXP_Prot の月次 CF・現価再帰を 1 MP について鏡写しに再計算する。"""
    prod = bnft[bnft["PROD_CD"] == mp_row["PROD_CD"]]
    g = int(mp_row["GNDR_CD"])
    x0, term_y = int(mp_row["AGE"]), int(mp_row["INSTRM_YYCNT"])
    n_mon = term_y * 12
    sa = float(mp_row["JOIN_AMT"])

    def annual_rates(rsk_rt_cd: str) -> np.ndarray:
        row = rskrt.loc[(rsk_rt_cd, g)]
        return np.array([row[f"RSK_RT{x0 + t}"] for t in range(term_y)])

    liv_cd = prod.loc[prod["CRIT_INFO_NO"] == 11, "Q_LX_CALC_CD"].iloc[0]
    q_liv = annual_rates(liv_cd)
    q_liv_m = 1.0 - (1.0 - q_liv) ** (1.0 / 12.0)

    # 給付(CRIT_INFO_NO=21)ごとに CX_CALC_MTD='q#' → CRIT_INFO_NO=1 の率コード
    q1 = prod[prod["CRIT_INFO_NO"] == 1].set_index("SRNO")["Q_LX_CALC_CD"]
    bens = []
    for _, ben in prod[prod["CRIT_INFO_NO"] == 21].iterrows():
        q_idx = int(ben["CX_CALC_MTD"][1:])
        q_yr = annual_rates(q1.loc[q_idx])
        bens.append((1.0 - (1.0 - q_yr) ** (1.0 / 12.0), float(ben["BNFT_RT"])))

    # 月次 CF(C03: b(th)=e(th-1)、脱退 b·q_liv_m、給付 b·q_dis_m·SA·BNFT_RT)
    outgo_m = np.zeros(n_mon + 1)   # outgo_m[th]、th=1..n_mon
    b = 1.0
    for th in range(1, n_mon + 1):
        t = (th - 1) // 12
        outgo_m[th] = sum(b * q_m[t] * sa * rt for q_m, rt in bens)
        b *= 1.0 - q_liv_m[t]

    # 現価の後退再帰(C04: v=(1+DC_RT(prj_m+1))^(-1/12)、期中 v^(1/2))
    pv = 0.0
    for prj_m in range(n_mon - 1, -1, -1):
        v = v_mon[prj_m]            # PRD = prj_m + 1
        pv = pv * v + outgo_m[prj_m + 1] * np.sqrt(v)
    return pv


def build_expected() -> pd.DataFrame:
    rskrt, bnft, mp, v_mon = load_inputs()
    case_map = pd.read_csv(FMS_DIR / "fms_run_case_map.csv")
    annual = pd.read_csv(REF_DIR / "bel_by_mp_scenario.csv")

    rows = []
    for _, m in mp.iterrows():
        pv = mirror_pv(m, bnft, rskrt, v_mon)
        rows.append({"CTR_POLNO": m["CTR_POLNO"], "PV_MIRROR": pv})
    df = pd.merge(case_map, pd.DataFrame(rows), on="CTR_POLNO")
    df = pd.merge(df, annual.rename(columns={"BEL": "BEL_ANNUAL"})[
        ["MP_ID", "SCN_CD", "BEL_ANNUAL"]], on=["MP_ID", "SCN_CD"])
    df["GAP_MIRROR_VS_ANNUAL_PCT"] = 100 * (df["PV_MIRROR"] / df["BEL_ANNUAL"] - 1)
    return df


def sensitivity(df: pd.DataFrame, col: str) -> pd.DataFrame:
    wide = df.pivot_table(index="MP_ID", columns="SCN_CD", values=col)
    return 100 * (wide.div(wide["BASE"], axis=0) - 1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fms-csv", action="append", default=[],
                    help="FMS S03 出力(*_PV_ByPol.csv)。複数指定可")
    ap.add_argument("--pv-col", default="Net_CF",
                    help="FMS 出力の PV 列名(既定 Net_CF)")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = build_expected()

    if not args.fms_csv:
        # --- 事前モード: 期待値表の生成のみ --------------------------------
        df.to_csv(FMS_DIR / "fms_expected_pv.csv", index=False)
        g = df["GAP_MIRROR_VS_ANNUAL_PCT"]
        print(f"事前モード: fms_expected_pv.csv を生成({len(df)} セル)")
        print(f"  ミラー vs 論文年次 BEL のギャップ(規約差): "
              f"{g.min():.2f}% 〜 {g.max():.2f}%")
        s_m = sensitivity(df, "PV_MIRROR")
        s_a = sensitivity(df, "BEL_ANNUAL")
        d = (s_m - s_a).abs().max().max()
        print(f"  感応度 ΔBEL%(BASE 比)の規約差影響: 最大 {d:.3f}pp")
        return 0

    # --- 突合モード --------------------------------------------------------
    fms = pd.concat([pd.read_csv(p) for p in args.fms_csv], ignore_index=True)
    fms = fms.rename(columns={args.pv_col: "PV_FMS"})[["CTR_POLNO", "PV_FMS"]]
    if fms["CTR_POLNO"].duplicated().any():
        print("警告: FMS 出力に CTR_POLNO 重複あり(マルチコア分割出力の重複連結?)")
    df = pd.merge(df, fms, on="CTR_POLNO", how="left")
    missing = df["PV_FMS"].isna()
    df["V1B1_DIFF_PCT"] = 100 * (df["PV_FMS"] / df["PV_MIRROR"] - 1)
    df["V1B2_DIFF_PCT"] = 100 * (df["PV_FMS"] / df["BEL_ANNUAL"] - 1)
    df["V1B1_PASS"] = df["V1B1_DIFF_PCT"].abs() <= 100 * TOL_V1B1

    s_f = sensitivity(df.dropna(subset=["PV_FMS"]), "PV_FMS")
    s_a = sensitivity(df, "BEL_ANNUAL")
    sens_diff = (s_f - s_a).abs()

    df.to_csv(OUT_DIR / "verify_v1b_fms_pv.csv", index=False)

    n = (~missing).sum()
    base_ok = df[(df["SCN_CD"] == "BASE") & df["V1B1_PASS"]].shape[0]
    print(f"突合モード: FMS 出力 {n}/{len(df)} セル(欠落 {missing.sum()})")
    print(f"V1b-① FMS vs ミラー: 最大乖離 {df['V1B1_DIFF_PCT'].abs().max():.4f}% "
          f"(基準 ±{100 * TOL_V1B1:.0f}%)、BASE 8MP 合格 {base_ok}/8")
    print(f"V1b-② FMS vs 論文年次 BEL(規約差の実測): "
          f"{df['V1B2_DIFF_PCT'].min():.2f}% 〜 {df['V1B2_DIFF_PCT'].max():.2f}%")
    if not s_f.empty:
        print(f"V1b-③ 感応度乖離: 最大 {sens_diff.max().max():.3f}pp "
              f"(基準 ±{TOL_V1B3}pp)")
    ok = (not missing.any()) and df["V1B1_PASS"].all() \
        and sens_diff.max().max() <= TOL_V1B3
    print("総合判定:", "合格" if ok else "不合格(verify_v1b_fms_pv.csv 参照)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
