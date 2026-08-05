**日本語** | [English](FMS_BoosterRunCases_Tier1_20260805.en.md)

# FMS Booster 実行ケース定義書 — Tier 1(ケースA/B/C)

**作成日:** 2026-08-05
**目的:** 論文 §8 の BEL 感応度デモ(簡易 Python 版)を、保険会社での導入実績を持つ実務プロジェクションモデル FMS Booster 上で再実行し、
(A) BASE シナリオの PV レベル突合(V1b)、(B) 6 シナリオ × 8 MP の感応度一表の再現、(C) 実行負荷の実測(論文 §9.2 論拠 4)を一体で実施する。
**関連文書:** `BEL_Demo_WorkInstruction_FMS_20260710.md`(原作業指示書)、`bel_demo_effort_log.md`(計測記録)、`../scripts/bel_demo/README.md`(簡易 Python 版)、`../../../ValidationTools/BoosterFMS/CLAUDE.md`(ガバナンス)
**論文上の位置づけ:** §10.4 第一項(実務プロジェクションモデル上での再実行と率・現価レベルの突合、実行負荷の実測)および §9.2 論拠 4(計算負荷の実測値)を閉じる。§8 の「簡易プロジェクションモデルによるデモ」という記述を最終版で格上げする根拠となる。

---

## 1. 方式の決定 — データ注入方式(FMS コード改修 0 行)

原作業指示書 §5 は 4 モジュール改修(シナリオループ追加・`TBL_CLAIM_SCN` 参照切替)を想定していたが、`Base_Model_v251208/` の実装を精読した結果、**コード改修なし**で全ケースを実行できる「データ注入方式」を採用する。

**根拠(モジュール精読で確定した実装事実):**

1. `IXP_Prot/B04_Set_Bnft_Info.txt:207` — `Qxt(srno, t) = RiskRate(srno).val(gender, MP.AGE + t - 1)`。率は**到達年齢軸のみ**で読まれ、投影年と到達年齢が同期して歩む。したがって世代対角線 `m(x0+dur, 2026+dur)` を加入年齢コホート別に `TBL_RSKRT`(`RSK_RT0..RSK_RT120`)へ事前焼込みすれば、暦年次元は不要。
2. `IXP_Prot/A01_Main.txt:43` — IXP にはシナリオループがない(`scn_loop = 1` 固定。経済シナリオ軸は割引率専用)。シナリオ軸は **PROD_CD(商品コード=セル)に折り込む**方が、ループ追加改修より侵襲が小さい。
3. 改修 0 行は、論文 §7 の主張「シナリオ間の差分は仮定差のみに帰着する」の**最強形の実装**である(計算コアどころか全モジュールがシナリオ間で同一)。
4. 導入負担(§9.2)の実測値としても「FMS 改修 0 モジュール・0 行」はそのまま論拠になる。

**ガバナンス:** 実行は `ValidationTools/BoosterFMS/Scenario_Model_BELDemo/`(2026-08-05 作成、原本と byte 同一のコピー)上で行う。`Base_Model_v251208/` は無改変厳守。今後もし改修が必要になれば `Scenario_Model_BELDemo/` のみ、`' [BELDEMO]` マーカー付きで行う。

### 1.1 意味論マッピング(簡易 Python 版 ↔ FMS 実装)

| 簡易 Python 版の前提 | FMS 上の実装 | 実現手段 |
|---|---|---|
| シナリオ 6 本(率のみ相違) | PROD_CD = `BD_{SCN}_{AGE}` の 24 商品 | データのみ |
| 世代対角線率 m(x0+dur, 2026+dur) | 到達年齢軸 `TBL_RSKRT` へコホート別焼込み | `build_fms_input_tables.py` |
| 三大疾病一時金 100 万円(初回罹患時) | 給付 3 本(BNFT_CRIT_CD='S'、BNFT_RT=1.0)× JOIN_AMT=100 万 | TBL_BNFT / TBL_MP |
| 解約 3%/年 = 無価値脱退(解約返戻金なし) | **解約テーブル 0 + Lives(脱退)率へ 3% 合算** | TBL_LAPSE=0、`R_*_LIV` に合算 |
| 死亡脱退 = 全死因率(BASE 固定) | 同上(Lives 率 = 3 疾病 + 全死因 + 3%) | `R_*_LIV` |
| 給付のみ(保険料・事業費なし) | PREM=0、事業費・手数料テーブル 0、予定事業費なし | TBL_MP / TBL_ACQ 等 |
| 発行 2026 年・発行時点 BEL | Val_YM='202512'、CTR_DT='202601' → elapsed_time=0 | TBL_MP / GParam |
| ESR 無リスク金利カーブ(年次スポット) | 月次フォワード(ln 線形補間から導出)を TBL_DC_RT へ | `build_fms_input_tables.py` |
| BEL = 給付現価 | S03 `Net_CF`(= PV_Outgo_M。収入・その他支出は全て 0) | 突合スクリプト |

**解約の扱いの補足:** IXP の解約返戻金は純保険料式責任準備金から計算され(`C01`/`C02`)、データ設定だけではゼロ化できない。解約率を Lives(脱退)率へ合算し解約テーブルを 0 とすることで、`C03` の解約経路(`No_Pol.surr`)が消えて解約返戻金の支払いが発生せず、簡易 Python 版の「解約 = 無価値脱退」と同じ意味論になる。年次では両者の残存率は厳密に一致する(結合年次率 q_sum の月次幾何変換は年境界で (1−q_sum) に戻るため)。なお、この設計により `GParam.Lapse_Sens` による解約感応度(Tier 3 ケース F)はこの入力セットでは使えない(その際は TBL_LAPSE 側へ移す)。

---

## 2. 受入基準(V1b の精緻化)

原作業指示書 §7 の V1b「FMS と簡易 Python 版の PV が全 8 MP で ±1%」は、両者の**支払タイミング規約差**により、そのままでは達成不可能であることが事前定量化で判明した(下記)。V1b の本旨(検証対象は FMS ではなく本デモで新規に作る配管部分)に沿い、次の 3 段に精緻化する。

**事前定量化(2026-08-05、`verify_v1b_fms_pv.py` 事前モード):** 簡易 Python 版は「年次・年始払い・期始割引」、FMS は「月次・月央払い・年内エクスポージャ逓減」。FMS 規約を鏡写しにした独立ミラー計算によるギャップは全 48 セルで **−5.1%〜−3.7%**(高齢加入・高率シナリオほど大きい)。一方 BASE 比感応度 ΔBEL% への影響は**最大 0.35pp**(ICS_C の若年 MP。レベル倍率 1.125 を年次で掛けてから月次変換する順序に起因)で、合計 BEL の感応度はミラーでも UP50 −6.5 / DN50 +7.1 / ICS_T +14.9 / ICS_C +27.5 / ESR_M +17.9% と論文値(−6.6 / +7.2 / +15.0 / +27.7 / +18.0%)に 0.2pp 以内で一致する。

| # | 基準 | 内容 | 合否 |
|---|---|---|---|
| **V1b-①** | パイプライン検証(主基準) | FMS 出力 `Net_CF` vs 月次ミラー独立実装(`verify_v1b_fms_pv.py`)が**全 8 MP × 6 シナリオで ±1% 以内**(期待値 ≲0.1%。ミラーは FMS が読む SQLite をそのまま読んで C03/C04 規約を再現している) | 合否基準 |
| **V1b-②** | 規約差の実測(= 提案時のケース D) | FMS 出力 vs 論文 §8 の年次 BEL の乖離を全セルで記録。事前推定 −5.1〜−3.7% と整合すること(±0.5pp)を確認し、乖離の内訳(支払タイミング・年内エクスポージャ逓減)とともに `bel_demo_reconciliation.md` に記録。論文 §8.4/§10.4 で「簡易モデルの規約差の実測値」として引用可能 | 報告値 |
| **V1b-③** | 感応度整合(ケース B の合否) | ΔBEL%(BASE 比)が FMS と論文年次版で**全セル ±0.5pp 以内**。論文の中心的主張(トレンドショックの年齢勾配 30 歳 +31〜32% / 60 歳 +10〜11%、レベルショックの年齢一律性)が FMS 上で保たれることの直接確認 | 合否基準 |
| **S-inv** | 不変量チェック | S02 全行で `Surr_Val = 0`・`Prem_Inc = 0`・`Commission = Exp_Acq = Exp_Mnt = 0`、S03 全行で `PV_Income_* = 0` かつ `Net_CF = PV_Outgo_M` | 合否基準 |
| **C-1** | 実行負荷の実測 | §5 の計測項目を `bel_demo_effort_log.md` の記入欄に記録(作業と同時進行) | 記録 |

---

## 3. 実行ケース一覧

**共通の必須要件 — セル実行順:** IXP は `PV` 配列(`C04`)を MP 間で初期化しない。長い保険期間の MP の後に短い MP を計算すると、現価後退再帰の初項が前 MP の残存値を読む(`PV.outgo_m(prj_m+1)` の stale read)。**セルは保険期間の昇順(加入年齢 60 → 50 → 40 → 30)で並べること。** この順序なら未初期化領域は常に 0 で汚染しない。

| RUN | ケース | Cell_List(この順で) | MP 数 | 目的・合否 |
|---|---|---|---|---|
| **RUN-00** | 疎通 | `BD_BASE_60`(Test_Opt='Y' で 1 MP に限定) | 1 | 正常終了・S02 が 360 行・S-inv 成立・`Net_CF` がミラー値 MP04_BASE ≈ 95,550 円の ±1% |
| **RUN-A1** | ケース A(V1b) | `BD_BASE_60, BD_BASE_50, BD_BASE_40, BD_BASE_30` | 8 | V1b-①(BASE 8 MP)+ V1b-② + S-inv。1 シナリオ実行時間の計測(C-1) |
| **RUN-B1** | ケース B | `BD_UP50_60, BD_UP50_50, BD_UP50_40, BD_UP50_30` | 8 | UP50。以降 RUN-B2〜B5 も同形 |
| **RUN-B2** | ケース B | DN50 同順 | 8 | |
| **RUN-B3** | ケース B | ICS_T 同順 | 8 | |
| **RUN-B4** | ケース B | ICS_C 同順 | 8 | |
| **RUN-B5** | ケース B | ESR_M 同順 | 8 | RUN-A1〜B5 完了後に V1b-③ を判定 |
| **RUN-C1** | ケース C(任意) | 全 24 セルを「`*_60` 6 本 → `*_50` 6 本 → `*_40` 6 本 → `*_30` 6 本」の順で 1 Run | 48 | 一括実行時間の計測。結果は RUN-A1〜B5 と一致すること(回帰確認) |

- 6 シナリオ合計時間 = RUN-A1〜B5 の合計(per-scenario の内訳が §9.2 の記述に使える)。RUN-C1 は「1 Run に統合した場合」の参考値。
- マルチコア(`SParam.TotNo_Core` > 1)は使用可(コアごとに同一セル順が保たれるため実行順要件は破れない)が、**計測はまず 1 コアで**取り、コア数を記録欄に明記する。

---

## 4. モデル設定と入力データ

### 4.1 入力 DB(生成済み・検証済み)

生成: `ScaleBB/Research/scripts/bel_demo/build_fms_input_tables.py`
出力: `ScaleBB/Research/data/processed/bel_demo/fms_input/`(CSV ミラー付き)
検証: `verify_fms_input_tables.py` — **2026-08-05 合格(突合 23,314 件・不一致 0)**。率は検算用サーフェスからの独立再導出と 1e-12 で一致、割引フォワードの年次累積はカーブの割引係数と 1e-10 で一致。

| DB ファイル | FMS 接続先 | テーブル(行数) |
|---|---|---|
| `BELDemo_Input.db` | DB_INPUT | TBL_BNFT (192)、TBL_RSKRT (192)、TBL_PROD_INRT (24)、TBL_EXPCT_EXPENSE (0) |
| `BELDemo_Assump.db` | DB_ASSUMP | TBL_PROD_MAP (24)、TBL_CLAIM (4)、TBL_LAPSE (2)、TBL_SKEW (1)、TBL_ACQ (1)、TBL_MNT (1)、TBL_COMM (1) |
| `BELDemo_Scn.db` | DB_SCN | TBL_DC_RT (840: PRD 1..840、SCN_NO='1') |
| `BELDemo_MP.db` | DB_MP | TBL_MP (48) |

**キー体系:** PROD_CD = `BD_{SCN}_{AGE}`(例 `BD_ICS_T_30`)、率コード = `R_{SCN}_{AGE}_{Q1|Q2|Q3|LIV}`(Q1=がん, Q2=心, Q3=脳血管, LIV=脱退)、CTR_POLNO = `{MP_ID}_{SCN}`(例 `MP01_BASE`)。対応表は `fms_input/fms_run_case_map.csv`。

### 4.2 GParam(グローバルパラメータ。B-FMS マスターシートで設定)

| 項目 | 設定値 | 備考 |
|---|---|---|
| Val_YM | `202512` | CTR_DT='202601' と合わせ elapsed_time=0(発行時評価) |
| Proj_Obj | `PV` | Calc_PV を有効化 |
| Scn_Range | `1` | 経済シナリオは 1 本(割引率は全シナリオ共通) |
| TBL_BNFT / TBL_RSKRT / TBL_PROD_INRT / TBL_EXPCT_EXPENSE | 同名 | DB_INPUT |
| TBL_PROD_MAP / TBL_CLAIM / TBL_LAPSE / TBL_SKEW / TBL_ACQ / TBL_MNT / TBL_COMM | 同名 | DB_ASSUMP |
| TBL_DC_RT | 同名 | DB_SCN |
| TBL_MP | 同名 | DB_MP |
| Mort_Sens / Dis_Sens / Lapse_Sens / Acq_Sens / Mnt_Sens | `1.0` | 感応度スカラーは全て中立 |
| DiscR_Sens | `0.0` | 割引率スプレッドなし |
| Output_No | S02・S03 を有効化 | S01 は IXP に無関係 |
| DB ファイル名(Input / Assump_Actu / Assump_Econ / MP) | `BELDemo_*.db` のパス | `A04_Connect_DB.txt` の GParam 名は実機マスターシートで確認(§7) |

### 4.3 SParam(Run パラメータ)

| 項目 | 設定値 |
|---|---|
| Master_Name | `BELDEMO` |
| Run_Name | `RUN_00` / `RUN_A1` / `RUN_B1`〜`RUN_B5` / `RUN_C1` |
| Cell_List / TotNo_Cell | §3 の順序どおり |
| Test_Opt | RUN-00 のみ `Y`(1 MP 限定)、他は `N` |
| TotNo_Core | 計測 Run は `1`(参考として多コア再実行可) |

---

## 5. ケース C — 計測項目(`bel_demo_effort_log.md` の記入欄と対応)

作業と同時進行で記録する(後からの推定は不可。原作業指示書 §5.5)。

1. FMS 1 シナリオ実行所要時間(8 MP): RUN-A1 の実測(可能なら RUN-B1〜B5 も個別に)
2. FMS 6 シナリオ合計: RUN-A1〜B5 の合計(参考: RUN-C1 の一括時間)
3. 実行環境: マシンスペック(CPU/メモリ)、FMS Booster バージョン、コア数
4. 計測日
5. **FMS 改修モジュール数 / 改修行数: 0 / 0(データ注入方式)** — `diff -rq Base_Model_v251208 Scenario_Model_BELDemo` の結果(差分なし)を証跡として記録
6. 入力テーブル生成・検証のPython 側所要時間(build 0.5 秒・verify 数秒、実測済み)

---

## 6. 実行手順(全体)

```bash
# ⓪ 前提: 簡易 Python 版パイプラインが最新(①〜③は既実行済みなら省略可)
cd ICA/ScaleBB/Research/scripts/bel_demo
python3 build_esr_discount_curve.py
python3 build_scenario_claim_rates.py
python3 calc_bel_standalone.py

# ① FMS 入力テーブル生成 + 独立検証(V1a-F)+ 期待値表
python3 build_fms_input_tables.py
python3 verify_fms_input_tables.py          # 合格(不一致 0)を確認
python3 verify_v1b_fms_pv.py                # 事前モード: fms_expected_pv.csv 生成

# ② FMS 側(Windows / B-FMS 実行環境)
#   - Scenario_Model_BELDemo/ をモデルとして B-FMS に読込み
#   - fms_input/ の 4 DB を §4.2 のとおり接続、GParam/SParam を §4.2〜4.3 のとおり設定
#   - §3 の RUN-00 → RUN-A1 → RUN-B1..B5(→ 任意で RUN-C1)を順に実行し、
#     各 Run の所要時間を記録

# ③ 突合(FMS の S03 出力 CSV をこの環境へ持ち帰る)
python3 verify_v1b_fms_pv.py \
  --fms-csv <RUN_A1 の *_PV_ByPol.csv> --fms-csv <RUN_B1 の…> …(6 Run 分)
#   → verify_v1b_fms_pv.csv に V1b-①②③ の判定付き突合表
```

---

## 7. 実機確認事項(初回セットアップ時に潰す)

モデルソース(.txt)からは確定できず、B-FMS 実行環境・マスターシートでの確認が必要な事項。RUN-00 疎通で検出する。

1. **GParam の実名:** `A04_Connect_DB.txt` が参照する DB ファイル名パラメータ(Input_DB_Name 等)と、テーブル名 GParam・`Output_No` の正確なキー名はマスターシート(Excel)側の定義。§4.2 の対応で設定できるか確認。
2. **出力の形式とパス:** S02/S03 の出力ファイル名パターン(`{Run}_{Master}_PV_ByPol.csv` 想定)と出力先(`SParam.OutputPath`)、マルチコア時の分割サフィックス。突合スクリプトは CTR_POLNO 列だけに依存するため形式差異には頑健。
3. **`B05_Import_Assumption.txt` の `Next t` 記法**(124–126 行・130–132 行、`For th` ループを `Next t` で閉じている): 原作業指示書 §5.3 で指摘済みの懸念。本入力セットでは解約率 0 のため skew は計算に影響しないが、**インタプリタがエラーにしないか**を RUN-00 で確認。エラーになる場合のみ `Scenario_Model_BELDemo/` 側で `Next th` に修正し、`' [BELDEMO]` マーカーと差分記録を残す(唯一の許容改修候補)。
4. **TBL_MP の ROWID 前提:** `B03` は DB_CACHE 内 `WHERE ROWID = MP_Idx` で MP を引く。`FMS.SQLite.Attach` が挿入順 ROWID(1..N)を保証するか確認(想定どおりなら商品内 男→女 の順で MP01〜)。
5. **数値精度:** FMS 側 CSV 出力の桁数(丸め)が V1b-① の見かけ乖離に効かないか(Net_CF が有効 7 桁未満で出る場合は SQLite 出力 DB 側の値を使う)。

---

## 8. 乖離時の診断手順(V1b-① 不合格セルが出た場合)

S02(月次 CF)で原因を月単位に切り分ける。ミラー側の月次系列は `verify_v1b_fms_pv.py` の `mirror_pv()` をデバッグ出力に改造して得る。

1. **月 1 の Lives・Tot_Claim を突合** — 初月から異なれば率の読み違い(率コード ↔ PROD_CD 対応、GNDR_CD、A/E=1.0、Sens=1.0 のどれか)。`fms_run_case_map.csv` で対応を確認。
2. **月 13, 25, … 年境界で突合** — 年境界のみずれる場合は年次→月次変換(`1-(1-q)^(1/12)`)や t の切替(`Int((th-1)/12)+1`)の不一致。
3. **CF は一致するが PV が乖離** — 割引の問題。整数年時点の累積割引係数を突合(D1 検証は通過済みなので、FMS 側 DC_RT の読出し(BAS_YM/SCN_NO の WHERE)や `DiscR_Sens≠0` を疑う)。
4. **短期セルのみ乖離(30 年セルなど)** — §3 の実行順違反による PV stale read を疑う。Cell_List の順序を確認し、順序修正後に再実行。
5. **Surr_Val ≠ 0 の行がある** — TBL_LAPSE が 0 で読めていない(BAS_YM/PROD_GRP/CHN_CD/PAY_STATUS のキー不一致)。
6. **elapsed_time ≠ 0 の疑い**(S02 の th が 1 始まりでない)— Val_YM と CTR_DT の解釈を確認(`elapsed = 12*(ValYr−CtrYr)+ValMon−CtrMon+1`)。

原因と対処は `bel_demo_reconciliation.md`(社内 QA 文書、論文では引用しない)に記録する。

---

## 9. 成果物一覧

```
ScaleBB/Research/scripts/bel_demo/
├── build_fms_input_tables.py       — FMS 入力テーブル生成(§4.1)         [作成済み]
├── verify_fms_input_tables.py      — V1a-F 独立検証(合格済み)           [作成済み]
└── verify_v1b_fms_pv.py            — 事前モード + V1b-①②③ 突合         [作成済み]

ScaleBB/Research/data/processed/bel_demo/fms_input/
├── BELDemo_{Input,Assump,Scn,MP}.db — FMS 接続用 SQLite(4 ファイル)     [生成済み]
├── tbl_*.csv                        — テーブル CSV ミラー(目視確認用)    [生成済み]
├── fms_run_case_map.csv             — MP×SCN ↔ PROD_CD/率コード対応表    [生成済み]
└── fms_expected_pv.csv              — ミラー PV・年次 BEL・予測ギャップ   [生成済み]

ScaleBB/Research/output/bel_demo/
├── verify_fms_input_tables.csv      — V1a-F 突合結果(不一致 0)          [生成済み]
└── verify_v1b_fms_pv.csv            — V1b 突合表(判定付き)              [FMS 実行後]

ScaleBB/Research/docs/
├── FMS_BoosterRunCases_Tier1_20260805.md — 本書
├── bel_demo_effort_log.md           — C-1 計測記録(記入欄あり)          [FMS 実行時に記入]
└── bel_demo_reconciliation.md       — 乖離原因記録(必要時)              [FMS 実行後]

ValidationTools/BoosterFMS/
├── Base_Model_v251208/              — 原本(無改変、diff -rq で確認済み)
└── Scenario_Model_BELDemo/          — 実行用コピー(現時点で原本と同一)  [作成済み]
```

**FMS 実行後の論文反映(参考):** V1b 合格時は、§8.2 の「簡易プロジェクションモデル」記述に「実務導入実績のあるプロジェクションモデル(FMS Booster)上での再実行により、シナリオ間感応度が ±0.5pp 以内で再現されることを確認済み(月次・月央払い規約による水準差 −5〜−4% は分解済み)」の趣旨を追記、§9.2 論拠 4 に実測時間、§10.4 第一項を「実施済み」に書き換える。文面の作成は別作業とする。
