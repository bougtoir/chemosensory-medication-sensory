# PROTOCOL_DISTRIBUTION_FREEZE_RECONCILIATION

研究番号 2025-0057「味蕾関連遺伝子多型が処方変更に与える影響の解明」（ToMMo分担研究）

本文書は、A. 正式なToMMo研究計画・申請書、B. 分譲予定データ（データセット仕様＋研究計画記載の味蕾関連SNP）、C. 旧セッションのfrozen scientific decisions（`CHEMOSENSORY_TOMMO_LEGACY_SESSION_HANDOFF.zip`）の3者を照合した記録である。本文書は `reconciliation/build_reconciliation.py` で `reconciliation/RECONCILIATION_CLASSIFICATION.csv` と同時に生成され、各項目には7ラベルのいずれか1つだけが付く（不正ラベル・重複IDでビルド失敗）。

## 0. 位置づけと時系列

```
old freeze（旧handoff, 〜98/99）
→ protocol/data reconciliation（本文書, DRY_REPRODUCTION_AUDIT.md）
→ final pre-receipt freeze（未実施）
→ independent timestamp（未実施）
→ ToMMo data receipt（未受領）
→ offline validation（未実施）
```

- 参加者レベルToMMoデータは受領しておらず、本作業では一切読んでいない（DRY_REPRODUCTION_AUDIT.md §E）。
- 旧handoffの `98_FINAL_OPENING_DECISION_V2.md`「OPEN PRIMARY DATA WITH RESTRICTIONS」は旧セッション時点の historical gate decision として保存する。本セッションでは参加者レベル解析を開始する根拠にしない（AU2, GA5）。
- 本文書は新しい科学的分析を追加しない。最終freezeで決めるべき点は各行の「final-freeze action」に列挙するにとどめる。

## 1. 入力文書

{{DOC_TABLE}}

### 1.1 版の扱い（未解決）

添付の研究計画書・申請書は、公開wipの2026-03-13提出版・2026-06-13修正版のいずれともバイト一致しない。添付版を最上位制約として扱い、2026-06-13修正版で結論が変わる行は別欄「if 06-13 revision governs」に記録した（置換はしていない）。どちらが承認版かはユーザー確認待ち。

| 論点 | 添付計画書 | 06-13修正版 |
|---|---|---|
| 両wave参加者への限定 | {{PLAN_BOTH_WAVES}} | {{REV_BOTH_WAVES}} |
| 候補薬剤カテゴリを主たる解析対象として列挙 | no | {{REV_CATEGORIES}} |
| GWASを候補領域解析へ置換 | no（GWASを探索的に記載） | {{REV_GWAS}} |
| 医科レセプト・介護保険への言及 | {{PLAN_CLAIMS}} | — |

## 2. 分譲予定データの範囲（データセット仕様より機械集計）

- release: {{DS_RELEASE}}
- sheets: {{DS_SHEETS}}; 非空行 {{DS_NONEMPTY_ROWS}}
- 分譲対象（=1）: {{DS_SELECTED}}
- 分譲対象外（=0）: {{DS_NOT_SELECTED}}
- 服薬: 商品名・成分 {{DS_MEDICATION_NAME_ROWS}} 行、KEDD ID {{DS_KEDD_ID_ROWS}} 行、Drug ID {{DS_DRUG_ID_ROWS}} 行、入手方法（処方箋）{{DS_PRESCRIPTION_SOURCE_ROWS}} 行、使用期間 {{DS_DURATION_ROWS}} 行、使用頻度 {{DS_FREQUENCY_ROWS}} 行、1回使用量 {{DS_DOSE_ROWS}} 行
- 自己申告味覚項目 {{DS_TASTE_ROWS}} 行、FFQ関連 {{DS_FFQ_ROWS}} 行
- レセプト {{DS_CLAIMS_ROWS}} 行、ancestry主成分 {{DS_ANCESTRY_PC_ROWS}} 行（メタボロームは上記のとおり全て分譲対象外）
- 遺伝子型: データセット仕様外。研究計画記載の味蕾関連遺伝子のSNPのみ（{{N_APPROVED}}遺伝子: {{APPROVED_GENES}}; 根拠: {{APPROVED_SOURCE}}）。06-13修正版申請書の遺伝子別紙との差: {{REV_GENE_DIFF}}。全ゲノム・genome-wide SNPは前提にしない。
- 計画書本文の遺伝子行から機械抽出した遺伝子: {{PLAN_GENE_LINE_GENES}}。誤記: {{PLAN_GENE_TYPO}}

### 2.1 旧freezeの遺伝子と承認遺伝子の対応

{{GENE_TABLE}}

## 3. 照合結果の要点

1. **主要目的変数**: 承認計画の目的変数は ph1→ph2 の処方変更（用量変更、同一治療目的薬のswitch・追加・削除）。旧freezeは現在曝露（O1）を主要、cross-wave transition（O3）を二次とし（`74` rule 3）、この順位は承認計画に反するため SUPERSEDED とし、O3 を確認的目的変数へ移した（SAP-O1, SAP-O3, RW3）。2週間調査票の限界（adherence・意図・味覚駆動は測れない）は維持（RW2, TM1）。
2. **主要予測**: F-PRIMARY は `62`（`82` rule 1で正）に従い P01, P02, P05。`82` 表・`README_HANDOFF.md`・`LOCK_STATUS.md` の「P01, P02, P05, P10」は62と矛盾する記載誤り（HI1）。P10 は TAS2R4 が承認外のため REQUIRES PROTOCOL AMENDMENT。P01 を P10 で救済しない規則は不変。
3. **承認外遺伝子**: TAS2R19（P06）、TRPA1（P09, N11）、TAS2R4（P10）は削除・置換せず REQUIRES PROTOCOL AMENDMENT として保持し、検定分母から除外して列挙する。
4. **共変量**: genome-wide ancestry PC と血縁QCは分譲データで算出不能（SAP-COV2, SAP-QC2）。承認計画が要求する既往歴・併存疾患・生活習慣・社会経済指標の調整により旧共変量集合は SUPERSEDED（SAP-COV1, S8）。
5. **薬剤同定**: KEDD ID・Drug ID が分譲仕様にあるため structured ID を優先し、自由記載はbrand/剤形/経路補完とQCに用いる（PA2）。parser v1.0.0 と実文字列QCゲートは維持（PA1, PA3）。
6. **claims**: 計画書は医科レセプトに言及するが分譲予定データに無い。受領manifestで確認されるまで主解析の前提にしない（RS1, S6）。
7. **直接の味覚表現型**: 心理物理学的測定は無い（RS2）。ただし自己申告の味覚項目が分譲仕様にあり、旧freezeの「味覚表現型なし」という前提は事実として不正確。利用するかは最終freezeで事前規定する。
8. **contrast定義の不一致**: C1–C5 は `25`（script 09出力）と `72` で別の対比を指す。family（F-CONTRAST）は維持し、凍結対象の定義を最終freezeで結果を見る前に記録する。
9. **gradient**: F-GRADIENT の1-df検定は G と Y の対象が `95` で一意に規定されていない。最終freezeで一意化する。
10. **calibration**: 承認範囲外・測定不能の予測が分母から外れるため評価点は最大8。power不足を事前に明記する（CA1）。
11. **研究アーク**: sensory plasticity、食育/sensory conditioning、medication-response modification、health-economic・global-health benefit、免疫媒介は ToMMo で検証できない将来仮説（FH1–FH6）。本研究の到達点は「chemosensory genotype と報告薬剤曝露・処方変更の population-level 関連」であり、介入効果は結論しない。

## 4. ラベル集計

{{LABEL_COUNTS}}

ラベルの使い方: 検定でない手続き・規則項目では、KEEP AS CONFIRMATORY は「確認的解析を拘束する規則として維持」、KEEP AS SECONDARY は「支持的・記録的項目として維持」を意味する。SUPERSEDED BY APPROVED-PROTOCOL REQUIREMENT は、承認計画（または承認された分譲構造）の要件により旧規定が置き換わる項目に限る。

## 5. 分類表（全{{N_ITEMS}}項目）

{{CLASSIFICATION_TABLE}}

## 6. 最終 pre-receipt freeze へ持ち越す決定事項

1. 承認版（添付版 / 06-13修正版）の確定。
2. 処方変更目的変数（用量変更・有効成分変更・同一治療目的内switch・追加・削除）の操作的定義と、KEDD/Drug ID→成分→治療目的クラス対応表。
3. P01/P02/P05 の主要検定に用いる目的変数（O1/O3）の対応。
4. C1–C5 の凍結定義と遺伝子割当。
5. F-GRADIENT の G と Y の一意化。
6. ancestry PC を用いない共変量集合（分譲項目名で列挙）。
7. FFQ triangulation と自己申告味覚項目の扱い（使う場合は変数・方向・家族を事前規定）。
8. calibration の最小評価点数。
9. 82表・README・LOCK_STATUS の F-PRIMARY 記載誤りの errata 化。
10. 完全オフライン解析コードの凍結と独立timestamp。
