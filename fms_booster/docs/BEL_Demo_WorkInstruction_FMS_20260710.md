**日本語** | [English](BEL_Demo_WorkInstruction_FMS_20260710.en.md)

# 作業指示書: BEL感応度デモ(論文§8) — FMS Booster実行版

**作成日:** 2026-07-10
**目的:** ICA論文§8「Financial Impact Demonstration」用に、ScaleBBのシナリオ生成能力(L±50bp等)を実務プロジェクションモデル(FMS Booster)上で実証し、モデルポイント別BEL(給付現価)感応度の一表と図を作成する。
**関連文書:** `Paper_Outline_20260710.md`(論文アウトライン)、`../../BackTest_2015_2024/docs/report.md` §9(シナリオ生成の理論的根拠)
**前提確認済み事項:**
- ベンダー(FMS Booster)から論文検証使用の許可取得済み
- `Base_Model_v251208/` は無改変で保持し、コピーを編集する方針で合意済み

---

## 0. ガバナンス(最初に実施)

- [ ] `ValidationTools/BoosterFMS/Base_Model_v251208/` を `ValidationTools/BoosterFMS/Scenario_Model_BELDemo/` へコピーする。**原本には一切手を入れない**
- [ ] `ValidationTools/BoosterFMS/CLAUDE.md` を更新する:
  - 「Read-only reference」の記述を「`Base_Model_v251208/` は参照専用(無改変)。`Scenario_Model_BELDemo/` はBEL感応度デモ用の改修コピーで編集可」に改める
  - 論文検証使用のベンダー許可取得済みである旨を追記
- [ ] 改修はすべて `Scenario_Model_BELDemo/` 配下で行い、原本との差分が `diff` で追跡できる状態を維持する

---

## 1. 全体アーキテクチャ(3層パイプライン)

```
[Python層①] ScaleBBコア(既存fit流用) 
             → 5シナリオ × 3疾病の投影率サーフェス生成
             → 世代対角線(x0+t, 2026+t)をデュレーション別率に展開
             → DB_ASSUMP へシナリオ率テーブルをロード
      ↓
[FMS層]      Scenario_Model_BELDemo がシナリオ別に TBL_CLAIM_SCN を読み分けて
             PV計算 → SCN_CD 付きで出力
      ↓
[Python層②] FMS出力を集計 → 論文§8の一表(CSV) + 棒グラフ(PNG)
```

**設計原則:**
1. 世代対角線の変換(暦年×到達年齢 → デュレーション別率)は **Python側で事前計算** する。FMS側には従来形式の「デュレーション別クレーム率」として渡し、FMS改修を最小化する
2. FMSの計算コア(`C01`〜`C04`)は **無改変** とする。「シナリオ間の差分は仮定差のみに帰着する」という論文§7の主張のFMS実装版の裏付けとするため
3. クレーム率以外の仮定(解約・事業費・報酬)は全シナリオ共通とし、変更しない

---

## 2. シナリオ定義(5本)

| SCN_CD | シナリオ名 | long_term_rate (L) | 率の追加操作 | 論文上の位置づけ |
|---|---|---|---|---|
| `BASE` | ベース | 0.010 (1.0%) | なし | 現行デフォルト |
| `UP50` | Trend Up | 0.015 (1.5%) | なし | IFRS17感応度 +50bp |
| `DN50` | Trend Down | 0.005 (0.5%) | なし | IFRS17感応度 −50bp |
| `ICS_T` | ICS Trend shock | 0.000 (0.0%) | なし | ICS改善率ゼロ・ストレス |
| `ICS_C` | ICS Trend+Level | 0.000 (0.0%) | 率を一律 ×1.125 | ICS合成ストレス |

共通パラメータ(全シナリオ固定): `convergence_year=2035`、`lam_row=40, lam_col=40, diff_order=2`、`age_taper_start=90, age_taper_end=120`(KDB `config.yaml > scalebb_presets > defaults` 準拠)。Phase 1 のfitはLに依存しないため、**fitは1回だけ実行し、Phase 2(project)のみシナリオ別に再実行**する。

## 3. モデルポイント定義(8点)

| MP_ID | 加入年齢 x0 | 性別 | 発行年 | 保障 |
|---|---|---|---|---|
| MP01–MP04 | 30 / 40 / 50 / 60 | 男 | 2026 | 三大疾病一時金 100万円(初回罹患時)、90歳満了 |
| MP05–MP08 | 30 / 40 / 50 / 60 | 女 | 2026 | 同上 |

**その他前提:** 解約率 年2%固定(全シナリオ共通)、割引率 フラット1.5%(全シナリオ共通)、死亡脱退は全死因投影率(BASEのLで固定、全シナリオ共通 — 感応度を疾病罹患率のみに帰着させるため)。給付発生の疾病はがん(cancer)・心疾患(heart_broad)・脳血管(cerebrovascular)の3つで、`BNFT_Q` に1疾病=1給付項目として対応付ける。

**注記(論文§3・§10と整合):** 率は死亡率プロキシ(人口動態統計5-15由来)であり、発生率の直接推定ではない。デモの目的は「方向と桁」の提示。

---

## 4. Python層① — シナリオ率生成・DBロード

### 4.1 スクリプト: シナリオ率生成

**ファイル名:** `ScaleBB/Research/scripts/bel_demo/build_scenario_claim_rates.py`

```python
# 【目的】ScaleBBの既存fitを流用し、long_term_rateのみ差し替えて
#         5シナリオ×3疾病(+全死因)の投影率を生成し、
#         モデルポイント別の世代対角線をデュレーション別率に展開する
#
# 【入力】
#   - ScaleBB/BackTest_2015_2024/data/disease_panel_mortality.csv(率パネル)
#   - KDBベンダリングコアのfit_scale_bb / project_scale_bb / ScaleBBConfig
#
# 【処理】
#   1. 対象疾病(cancer, heart_broad, cerebrovascular)×性別(male, female)ごとに
#      fit_scale_bb を1回実行(1950-2024全期間、last_observed_year=2024)
#   2. シナリオ表(§2)のLごとに project_scale_bb を再実行し、
#      horizon_year=2086(発行2026+満了60年)まで率サーフェス m(x, t) を生成
#   3. ICS_C は ICS_T の率を一律1.125倍する
#   4. モデルポイント(x0∈{30,40,50,60})ごとに世代対角線を読み出す:
#        rate[dur] = m(x0 + dur, 2026 + dur)   dur = 0 .. (90 - x0 - 1)
#   5. per-100k → 率(小数)へ換算し、TBL_CLAIM_SCN互換レコードに整形
#
# 【出力】
#   - data/processed/bel_demo/scn_claim_rates.csv
#     列: SCN_CD, BNFT_Q, GNDR_CD, ISSUE_AGE, DUR, ASSM_RT
#   - data/processed/bel_demo/scn_mortality_rates.csv(全死因・BASE固定、同形式)
#   - 検算用: data/processed/bel_demo/rate_surface_{disease}_{sex}_{scn}.csv
```

**受入基準:**
- [ ] `BASE` の率が既存 `predicted_rate_apc/`・バックテスト成果物とオーダー整合(スポットチェック3点以上)
- [ ] 全 (SCN, BNFT_Q, GNDR, ISSUE_AGE, DUR) の組に欠損なし、率は (0, 1) の範囲内
- [ ] L が大きいシナリオほど将来率が低い(改善加速)ことを機械チェック

### 4.2 スクリプト: DBロード

**ファイル名:** `ScaleBB/Research/scripts/bel_demo/load_scenario_to_db.py`

```python
# 【目的】シナリオ率をFMSの仮定DB(DB_ASSUMP)へロードする
#
# 【方式】既存TBL_CLAIMは無変更。新テーブル TBL_CLAIM_SCN を新設する(方式A)
#
# 【テーブルスキーマ案】TBL_CLAIM_SCN
#   SCN_CD   TEXT    -- シナリオコード(BASE/UP50/DN50/ICS_T/ICS_C)
#   PROD_GRP TEXT    -- 商品群(デモ用に 'BELDEMO' 固定)
#   BNFT_Q   INTEGER -- 給付項目(1=cancer, 2=heart_broad, 3=cerebrovascular)
#   GNDR_CD  TEXT    -- 性別コード(既存TBL_CLAIMの符号体系に合わせる)
#   CHN_CD   TEXT    -- チャネル(既存の任意1値に固定)
#   BAS_YM   TEXT    -- 基準年月(既存の符号体系に合わせ '202601' 等)
#   ISSUE_AGE INTEGER-- 加入年齢(30/40/50/60)
#   DUR      INTEGER -- デュレーション(経過年 or 経過月。既存TBL_CLAIMの粒度に合わせる)
#   ASSM_RT  REAL    -- 仮定率
#   PRIMARY KEY (SCN_CD, PROD_GRP, BNFT_Q, GNDR_CD, CHN_CD, BAS_YM, ISSUE_AGE, DUR)
#
# 【注意】
#   - 既存TBL_CLAIMの実スキーマ(列名・キー粒度・月次/年次)を必ず実物で確認し、
#     上記案を実スキーマに寄せて修正すること
#   - 既存DBはバックアップを取ってから変更。DROP/DELETEは新テーブルのみに限定
#   - モデルポイント定義(TBL_PROD_MAP等へのBELDEMO商品群の登録)が必要なら同時に投入
```

**受入基準:**
- [ ] DB変更前バックアップの存在
- [ ] ロード件数 = 5シナリオ × 3給付 × 2性 × 4加入年齢 × デュレーション数、と一致
- [ ] 既存テーブルのレコード数・チェックサムが変更前後で不変

---

## 5. FMS層 — 改修(4モジュール、最小侵襲)

対象: `ValidationTools/BoosterFMS/Scenario_Model_BELDemo/` 配下(コピー)のみ。

### 5.1 `General_Modules/__import_GParams.txt` / `A04_Set_Param.txt`

- [ ] グローバルパラメータに以下を追加:
  - `GParam.SCN_CD`(現在実行中のシナリオコード)
  - `GParam.SCN_List`(実行シナリオ配列: BASE, UP50, DN50, ICS_T, ICS_C)
  - `GParam.TBL_CLAIM_SCN`(シナリオ率テーブル名)
- コメントは日本語で「BELデモ用シナリオパラメータ」等の見出しを付け、改修箇所を検索可能にする(推奨マーカー: `' [BELDEMO]`)

### 5.2 `IXP_Prot/A01_Main.txt`

- [ ] Cellループの**外側**にシナリオループを追加する(疑似コード):

```vb
' [BELDEMO] シナリオループ: SCN_Listの各シナリオについて全Cellを計算する
For scn_i = 1 To UBound(GParam.SCN_List)
    GParam.SCN_CD = GParam.SCN_List(scn_i)
    ' --- 以下、既存のCellループ(Import_Cell_Data → 計算 → Output)をそのまま実行 ---
Next scn_i
```

- 既存の `Map_Scn_Idx` 機構が金利等の経済シナリオ用に使われている場合は**流用せず**、独立したループとして追加する(役割の混線を避ける)。`Map_Scn_Idx` の実装を読んだ上で判断し、判断根拠をコミットメッセージに残すこと

### 5.3 `IXP_Prot/B05_Import_Assumption.txt`

- [ ] `Import_claim_Ratio` の参照テーブルを `TBL_CLAIM` → `GParam.TBL_CLAIM_SCN` に切替え
- [ ] WHERE句に `SCN_CD = GParam.SCN_CD` と `ISSUE_AGE = MP.加入年齢`(既存MPの該当フィールド)を追加
- [ ] `Import_Lapse_Ratio` / `Import_Expense_Ratio` / `Import_commission` は**無変更**
- [ ] 既知の懸念: 解析メモでコード末尾に `Next t` の記述漏れらしき箇所が指摘されている。実物を確認し、実害があれば修正(修正した場合は原本との差異として記録)、なければ「確認済み・実害なし」とメモを残す

### 5.4 `IXP_Prot/O01_Set_Output.txt`

- [ ] 出力レコードに `SCN_CD` 列を追加し、シナリオ×Cell×MP別のPVが識別可能な形にする
- [ ] 出力先(テーブル/ファイル)のパスを `output/bel_demo/` 配下に向ける(既存出力を汚さない)

### 5.5 FMS改修の全体受入基準

- [ ] `C01`〜`C04`(計算コア)と `C09_Initialize` に差分がないこと(`diff` で機械確認)
- [ ] 改修行にはすべて `' [BELDEMO]` マーカーが付いており、`grep` で改修箇所が列挙できること
- [ ] BASE 1シナリオ・MP01 1点のみの疎通実行が正常終了すること
- [ ] **導入負担の実測記録(論文§9.2用 — 必須):** 以下を `docs/bel_demo_effort_log.md` に記録する
  - 改修モジュール数とモジュール名(想定: 4)
  - 改修行数(`diff` の追加/変更行数を機械集計。`' [BELDEMO]` マーカー行数と突合)
  - 作業工数(①ガバナンス ②率生成 ③FMS改修 ④パイプライン検証 ⑤集計、の工程別人日。Claude Code使用時はその旨も併記)
  - 計算時間(1シナリオの率生成所要時間、FMS 1シナリオ実行所要時間)
  - この記録は「導入は容易」という論文の主張を測定値で裏付けるエビデンスになるため、作業と同時進行で記録する(後からの推定は不可)

---

## 6. Python層② — 集計・図表生成

**ファイル名:** `ScaleBB/Research/scripts/bel_demo/aggregate_fms_results.py`

```python
# 【目的】FMSのシナリオ別出力を集計し、論文§8の一表と図を生成する
#
# 【入力】FMS出力(SCN_CD × Cell × MP 別のPV)
#
# 【出力1】output/bel_demo/bel_sensitivity_table.csv
#   行: MP01〜MP08 + 合計(9行)
#   列: BASE_PV, UP50_PV, UP50_pct, DN50_PV, DN50_pct,
#       ICS_T_PV, ICS_T_pct, ICS_C_PV, ICS_C_pct
#   (pct列はBASE比の変化率%)
#
# 【出力2】output/bel_demo/bel_sensitivity_bar.png
#   横軸: モデルポイント、縦軸: BASE比変化率%、シナリオ別色分けの棒グラフ
#   キャプション用に「加入年齢が若いほどTrend shockの影響が大きい」等の
#   構造的観察が読み取れるよう、加入年齢順に並べる
```

---

## 7. 検証(受入基準の総括)

| # | 検証項目 | 基準 | 不合格時の対応 |
|---|---|---|---|
| V1a | **パイプライン検証・率レベル(厳密)** | 独立スクリプトが率サーフェス(`rate_surface_*.csv`)から世代対角線を再導出し、単位換算(per 100k→小数)を独立に適用した結果が、DB内 `TBL_CLAIM_SCN` の全レコードと**完全一致**(許容誤差 1e-12) | 世代対角線のoff-by-one・単位換算・キーの取り違えを特定して修正。FMSを介さないため原因は必ず配管側にある |
| V1b | **パイプライン検証・PVレベル** | BASEシナリオについて、独立実装の簡易Python計算(下記V1補)とFMS出力PVが**全8MPで±1%以内** | 差分原因(端数処理・月次/年次換算・脱退控除の順序・期始期末の扱い)を特定し `docs/bel_demo_reconciliation.md` に記録(社内QA文書。論文では引用しない) |
| V2 | 方向性 | L上昇→罹患率低下→給付PV減少の単調性が全MPで成立 | 率テーブルの符号・対角線読出しを疑う |
| V3 | 合成整合 | ICS_C ≒ ICS_T × 1.125 からの乖離が説明可能(脱退相互作用分のみ) | 乖離要因を分解して注記 |
| V4 | 再現性 | クリーン状態から `README` のコマンド列で一発再現 | パイプライン修正 |

**V1補 — 検証の位置づけとスクリプト**

V1は **FMS Booster の妥当性検証ではない**(FMSは保険会社での導入実績を持つ検証済みツールであり、妥当性は前提とする)。検証対象は、本デモで新規に作るパイプライン部分 — ①単位換算(per 100k→小数)、②世代対角線のデュレーション展開、③月次/年次の粒度換算、④TBL_CLAIM_SCN投入とWHERE句改修 — に限定する。V1aが①②を厳密に、V1bが③④を含む統合経路を検証する分担。この検証は工程内の品質保証であり、**論文本文では言及しない**(論文側は「実務検証済みモデル上のデモ」という框組みのみ)。

**ファイル名:** `ScaleBB/Research/scripts/bel_demo/verify_pipeline_rates.py`(V1a用)

```python
# 【目的】率サーフェスから世代対角線と単位換算を独立に再導出し、
#         DB内 TBL_CLAIM_SCN の全レコードと突合する(パイプライン検証・率レベル)
# 【検証式】expected = rate_surface[x0 + dur, 2026 + dur] / 100_000
#           全 (SCN, BNFT_Q, GNDR, ISSUE_AGE, DUR) について DB値との差が 1e-12 以内
# 【出力】output/bel_demo/verify_pipeline_rates.csv(不一致レコードの一覧。0件で合格)
# 【注意】build_scenario_claim_rates.py の関数をimportせず、対角線抽出・単位換算を
#         本スクリプト内で独立に実装すること(同じバグを共有しないため)
```

**ファイル名:** `ScaleBB/Research/scripts/bel_demo/verify_bel_standalone.py`(V1b用)

```python
# 【目的】FMSと独立に、同一仮定からBELを簡易計算しクロスチェックする(パイプライン検証・PVレベル)
# 【計算式】
#   BEL(x0) = Σ_t  v^t · S(t) · q_dis(x0+t, 2026+t) · SA
#   S(t)    = Π_{s<t} (1 − q_dis − q_death − q_lapse)   ※独立近似、FMS側の脱退順序と要照合
# 【出力】output/bel_demo/verify_standalone_vs_fms.csv(MP別のFMS PV・独立PV・乖離%)
# 【副次的役割】7/24のフォールバック発動時は本スクリプトが主計算に昇格する
```

---

## 8. 作業順序とフォールバック判断点

| 順 | 作業 | 完了目安 |
|---|---|---|
| ① | ガバナンス(§0): モデルコピー・CLAUDE.md更新 | 7/16 |
| ② | `build_scenario_claim_rates.py`(BASEのみ先行)＋既存TBL_CLAIM実スキーマ確認 | 7/18 |
| ③ | FMS改修4点 ＋ BASE 1本・MP01 1点の疎通 | 7/22 |
| ④ | パイプライン検証 V1a(率レベル・全件突合)＋V1b(PVレベル・BASE全8MP) | **7/24 ★判断点** |
| ⑤ | 残り4シナリオのロード・実行・集計・一表/図の生成 | 7/28 |
| ⑥ | V2〜V4検証、README整備、論文§8の本文1〜2段落ドラフト | 7/31 |

**★フォールバック判断(7/24):** ④の時点でV1bが収束しない、またはFMSデバッグが残工数を圧迫すると判断した場合は、FMS版を「今後の検証」に回し、`verify_bel_standalone.py` を主計算に昇格させた**簡易Python版**で§8を書く(V1a合格が前提。率レベルが検証済みなら簡易版の信頼性も担保される)。判断基準: 7/24時点でV1b未達 かつ 原因が2営業日で解消見込みなし。

---

## 9. 成果物一覧(完成時)

```
ScaleBB/Research/scripts/bel_demo/
├── build_scenario_claim_rates.py   — シナリオ率生成
├── load_scenario_to_db.py          — DB_ASSUMPロード
├── verify_pipeline_rates.py        — パイプライン検証・率レベル(V1a)
├── verify_bel_standalone.py        — パイプライン検証・PVレベル(V1b、フォールバック時は主計算)
├── aggregate_fms_results.py        — 集計・図表生成
└── README.md                       — 再現手順(コマンド列)

ScaleBB/Research/data/processed/bel_demo/
├── scn_claim_rates.csv / scn_mortality_rates.csv
└── rate_surface_*.csv(検算用)

ScaleBB/Research/output/bel_demo/
├── bel_sensitivity_table.csv       — 論文§8の一表
├── bel_sensitivity_bar.png         — 論文§8の図
├── verify_pipeline_rates.csv       — V1a検証結果(不一致レコード一覧。0件で合格)
└── verify_standalone_vs_fms.csv    — V1b検証結果

ScaleBB/Research/docs/
├── bel_demo_reconciliation.md      — V1b乖離の原因記録(社内QA文書。論文では引用しない)
└── bel_demo_effort_log.md          — 導入負担の実測記録(改修行数・工数・計算時間。論文§9.2のエビデンス)

ValidationTools/BoosterFMS/
├── Base_Model_v251208/             — 原本(無改変)
├── Scenario_Model_BELDemo/         — 改修コピー(' [BELDEMO]マーカー付き)
└── CLAUDE.md                       — 方針更新済み
```
