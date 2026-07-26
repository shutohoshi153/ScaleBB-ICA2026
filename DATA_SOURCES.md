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

## 免責

本リポジトリの派生データ・解析結果はいずれも本研究の著者によるものであり、
上記各提供元の見解を示すものではない。
