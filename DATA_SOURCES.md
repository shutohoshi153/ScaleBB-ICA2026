**日本語** | [English](DATA_SOURCES.en.md)

# データ出典 / Data Sources

本リポジトリに同梱する第三者提供データの出典と利用条件をまとめる。
リポジトリ本体のライセンス（`LICENSE`）は本ページに掲げる第三者データには及ばない。
各データの利用条件は、それぞれの提供元の定めに従う。

The third-party data bundled in this repository is credited below.
The repository's own license does not extend to these datasets; each remains
subject to the terms of its provider.

---

## 1. 全国がん登録 罹患数・率（国立がん研究センター）

**和文出典表記:**

> 国立がん研究センターがん情報サービス「がん統計」（全国がん登録）

**English citation:**

> Cancer Statistics. Cancer Information Service, National Cancer Center, Japan
> (National Cancer Registry, Ministry of Health, Labour and Welfare)

| 項目 | 内容 |
| --- | --- |
| 該当ファイル | `reproduction/generational/KDB/data/RowData/cancer_incidenceNCR(2016-2023).xls` |
| 状態 | 提供元からダウンロードした**原本のまま**（改変なし） |
| 用途 | 真の罹患率としての A-tier ベンチマーク（§3.3・generational README §1） |
| 利用条件 | 出典明記により転載可。事前申請は不要。改変のない原文の状態での利用が条件 |
| 提供元の窓口 | https://ganjoho.jp/aboutus/attention/copyright.html |

**派生物について:** 本パッケージの `reproduction/generational/KDB/scripts/build_cancer_registry_panel.py`
は、上記原本を年齢階級・性別のパネル形式へ変換して `data/processed/incidence_panel.csv`
（`rate_type='registry'` の行）を生成する。この変換および変換後の数値は本研究の著者による
ものであり、国立がん研究センターはその内容について責任を負わない。原本の数値は上記 `.xls`
を参照されたい。

*Derived data:* rows with `rate_type='registry'` in `data/processed/incidence_panel.csv`
are produced by the authors' script from the original file above. The National Cancer
Center is not responsible for the processed figures.

---

## 2. 標準生命表（公益社団法人 日本アクチュアリー会）

**出典表記:**

> 公益社団法人日本アクチュアリー会「標準生命表1996」「標準生命表2007」「標準生命表2018」

| 項目 | 内容 |
| --- | --- |
| 該当ファイル | `reproduction/generational/KDB/data/lifetable/seimeihyo960718.xlsx` |
| 収録内容 | 生保標準生命表 1996（死亡保険用・年金開始後用）、生保標準生命表 2007（死亡保険用・年金開始後用）、第三分野標準生命表 2007、生保標準生命表 2018（死亡保険用）、第三分野標準生命表 2018 の 7 系統 |
| 加工前の原データ | 上記 7 系統の標準生命表（日本アクチュアリー会公表）。同梱ファイルは、これら公表値を検証スクリプトが読める単一ブックに束ねたものである |
| 用途 | 入力死亡率データの妥当性検証のみ（generational README §4.3）。予定率表の生成経路には使用しない |

---

## 3. 人口動態調査（厚生労働省 / e-Stat）

**出典表記:**

> 厚生労働省「人口動態調査」（政府統計の総合窓口 e-Stat）

| 項目 | 内容 |
| --- | --- |
| 該当ファイル | `reproduction/backtest/data/raw/5-15_死因_性_5歳階級_年次_死亡数率__0003411659.csv`（統計表 ID 0003411659、死因・性・5歳階級別 死亡数および死亡率、1950–2024） |
| 派生ファイル | `reproduction/backtest/data/prebuilt_disease_panel_mortality.csv`、`reproduction/generational/KDB/data/processed/mortality_apc_panel.*`、`incidence_panel.csv` の `rate_type='mortality'` 行 |
| 用途 | 本研究の主入力（死因別死亡率）。§3.1–§3.4 の全パイプライン |
| 利用条件 | 政府標準利用規約（第2.0版）に基づき、出典明示のうえ複製・翻案・商用利用が可能 |

## 4. 患者調査（厚生労働省 / e-Stat）

**出典表記:**

> 厚生労働省「患者調査」（政府統計の総合窓口 e-Stat）

| 項目 | 内容 |
| --- | --- |
| 派生ファイル | `reproduction/generational/KDB/data/processed/incidence_panel.csv` の `rate_type='initial_visit'` / `'discharge'` 行、`los_panel.csv`（各行の `source_table` 列に元統計表 ID を保持） |
| 用途 | 受療率・平均在院日数に基づく発生率プロキシ（B/C-tier 参照系列） |
| 利用条件 | 政府標準利用規約（第2.0版）に基づき、出典明示のうえ複製・翻案・商用利用が可能 |
| 備考 | 容量削減のため e-Stat 生データ本体は同梱していない（構築済みパネルのみを同梱） |

---

## 5. イールド・カーブ作成ツール（金融庁）

**出典表記:**

> 金融庁「経済価値ベースのソルベンシー規制におけるイールド・カーブ作成ツール」（2026 年 3 月末基準日版）

**English citation:**

> Financial Services Agency of Japan, *Yield curve creation tool for the economic
> value-based solvency regulation*, version for the 31 March 2026 valuation date

| 項目 | 内容 |
| --- | --- |
| 該当ファイル | `ScaleBB/Research/data/external/fsa_esr/esr_yield_curve_tool_20260331.xlsx`（本パッケージには同梱しない） |
| 提供元 | https://www.fsa.go.jp/policy/economic_value-based_solvency/20260323/20260323.html（ESR 総合ページからリンクされる常設ページ。基準日ごとにファイルが差し替わる） |
| 版の特定 | ブック内の基準日表記は「2026年3月末」。ファイルの更新日時は 2026-04-06。ローカル取得日は 2026-07-28 |
| 用途 | §8 の BEL 感応度デモの割引率カーブ（パラメータシートの JPY 行から LOT・収束年限・UFR・ゼロクーポン金利を読み取り、Smith-Wilson 補外を再現） |
| 利用条件 | 金融庁ウェブサイトの利用規約（https://www.fsa.go.jp/rules/index.html ）に従う。政府標準利用規約準拠で、出典明示のうえ複製・翻案・商用利用が可能 |

**派生物について:** `ScaleBB/Research/scripts/bel_demo/build_esr_discount_curve.py` は、上記ツールの
パラメータを読み取った上で Smith-Wilson 法のロジックを**独自に再現**して
`esr_jpy_spot_curve_20260331.csv` を生成する。ツール自体の SW シートと実装が同一であることまでは
検証していない。この再現結果について金融庁は責任を負わない。

---

## 免責

本リポジトリの派生データ・解析結果はいずれも本研究の著者によるものであり、
上記各提供元の見解を示すものではない。
