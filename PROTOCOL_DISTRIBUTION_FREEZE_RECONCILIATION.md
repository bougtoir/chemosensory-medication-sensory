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

| role | file | bytes | SHA-256 |
|---|---|---|---|
| plan | tommo研究計画.docx | 156273 | `c81cdef22d61a732f8053b83dcddb439e8824207a2692e5bc4280275ae1988cd` |
| application | tommo申請書.docx | 36179 | `9cd2b24324c905d28024f68bdc40df4570e74bcb2c414033fefefed010f2b9f6` |
| dataset | tommoデータセット.xlsx | 748338 | `f77fb87cb76f631b01f7c04b6a66e1667074a11b6f56d38e17cf442a2f34d465` |
| revised_plan | 004_keikaku_2025-0057_20260613_修正版.docx | 131470 | `055a277e6f0b1284beb0fe43cc19c6fa5d506747f66aa0ce1ea55464d4ec116d` |
| revised_application | 003_shinsei_2025-0057_20260613_修正版.docx | 29487 | `c2ca53c4b69e61c65813a8183d5e4f3633a169c549c5f1ca3856d8731b295af8` |

### 1.1 版の扱い（未解決）

添付の研究計画書・申請書は、公開wipの2026-03-13提出版・2026-06-13修正版のいずれともバイト一致しない。添付版を最上位制約として扱い、2026-06-13修正版で結論が変わる行は別欄「if 06-13 revision governs」に記録した（置換はしていない）。どちらが承認版かはユーザー確認待ち。

| 論点 | 添付計画書 | 06-13修正版 |
|---|---|---|
| 両wave参加者への限定 | no | yes |
| 候補薬剤カテゴリを主たる解析対象として列挙 | no | yes |
| GWASを候補領域解析へ置換 | no（GWASを探索的に記載） | yes |
| 医科レセプト・介護保険への言及 | yes | — |

## 2. 分譲予定データの範囲（データセット仕様より機械集計）

- release: リリース 3.1.1 地域住民・三世代コホート 宮城（20歳以上）ベースライン・第2段階調査 86K
- sheets: 分譲対象, 参考資料 基本情報, コホート種別情報, 健康調査情報 検体検査情報, 調査票情報, 生理機能検査情報, 第1･2段階データ収集状況; 非空行 8128
- 分譲対象（=1）: 対象情報 / 基本情報 / demographics.{utf8|sjis}.csv; コホート種別情報 / cohort_profile.{utf8|sjis}.csv; 健康調査情報 / ベースライン調査期間 / 検体検査情報 / laboratory_test.ph1.{utf8|sjis}.csv; (第1段階調査期間) / 調査票情報 / 調査票（生活・食） / 調査票（生活） / qa_lifestyle.ph1.{utf8|sjis}.csv; 調査票（食） / qa_ffq.ph1.{utf8|sjis}.csv; 生理機能検査情報 / physiological_test.ph1.{utf8|sjis}.csv; 第2段階調査期間 / 検体検査情報 / laboratory_test.ph2.{utf8|sjis}.csv; 調査票情報 / 調査票（生活・食） / 調査票（生活） / qa_lifestyle.ph2.{utf8|sjis}.csv; 調査票（食） / qa_ffq.ph2.{utf8|sjis}.csv; 生理機能検査情報 / physiological_test.ph2.{utf8|sjis}.csv
- 分譲対象外（=0）: メタボローム情報 / MS (GC-MS) メタボローム解析 / 半定量; MS (LC-MS) メタボローム解析 / AbsoluteIDQ p180キットによる定量; MxP Quant 500キットによる定量; 内部標準法による定量; 半定量（高速液体クロマトグラフ、C18カラム）; 半定量（高速液体クロマトグラフ、HILICカラム）; 半定量（超高速液体クロマトグラフ）; NMRメタボローム解析 / 定量
- 服薬: 商品名・成分 270 行、KEDD ID 90 行、Drug ID 90 行、入手方法（処方箋）90 行、使用期間 180 行、使用頻度 180 行、1回使用量 180 行
- 自己申告味覚項目 18 行、FFQ関連 741 行
- レセプト 0 行、ancestry主成分 0 行（メタボロームは上記のとおり全て分譲対象外）
- 遺伝子型: データセット仕様外。研究計画記載の味蕾関連遺伝子のSNPのみ（20遺伝子: GNAT3, GNG13, ITPR3, OTOP1, PLCB2, SCNN1A, SCNN1B, SCNN1D, SCNN1G, TAS1R1, TAS1R2, TAS1R3, TAS2R10, TAS2R14, TAS2R16, TAS2R38, TAS2R46, TAS2R8, TAS2R9, TRPM5; 根拠: attached plan gene line + TAS2R8 restored from typo 'AS2R8'）。06-13修正版申請書の遺伝子別紙との差: {"only_revised": [], "only_attached": []}。全ゲノム・genome-wide SNPは前提にしない。
- 計画書本文の遺伝子行から機械抽出した遺伝子: GNAT3, GNG13, ITPR3, OTOP1, PLCB2, SCNN1A, SCNN1B, SCNN1D, SCNN1G, TAS1R1, TAS1R2, TAS1R3, TAS2R10, TAS2R14, TAS2R16, TAS2R38, TAS2R46, TAS2R9, TRPM5。誤記: yes（本文に『TTAS2R群（AS2R8, …』と記載、TAS2R8 が誤記）

### 2.1 旧freezeの遺伝子と承認遺伝子の対応

| legacy gene | in approved 20-gene list | used by |
|---|---|---|
| TAS1R2 | yes | P08, N10 |
| TAS2R19 | **no** | P06 |
| TAS2R38 | yes | P01, P02, P03, P04, P07, P12, N01, N02, N03, N04, N05, N06, N08, N09, N12 |
| TAS2R4 | **no** | P10 |
| TAS2R43 | **no** | P11 |
| TAS2R46 | yes | P11 |
| TAS2R9 | yes | P05, N07 |
| TRPA1 | **no** | P09, N11 |

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

| label | n |
|---|---|
| KEEP AS CONFIRMATORY | 38 |
| KEEP AS SECONDARY | 31 |
| KEEP AS NEGATIVE CONTROL | 12 |
| KEEP AS EXPLORATORY | 4 |
| UNTESTABLE WITH DISTRIBUTED DATA | 18 |
| REQUIRES PROTOCOL AMENDMENT | 7 |
| SUPERSEDED BY APPROVED-PROTOCOL REQUIREMENT | 8 |
| total | 118 |

ラベルの使い方: 検定でない手続き・規則項目では、KEEP AS CONFIRMATORY は「確認的解析を拘束する規則として維持」、KEEP AS SECONDARY は「支持的・記録的項目として維持」を意味する。SUPERSEDED BY APPROVED-PROTOCOL REQUIREMENT は、承認計画（または承認された分譲構造）の要件により旧規定が置き換わる項目に限る。

## 5. 分類表（全118項目）

| ID | source | item | legacy status | **classification** | rationale | if 06-13 revision governs | final-freeze action |
|---|---|---|---|---|---|---|---|
| P01 | 13_v2_FINAL/62/91 | TAS2R38 PAV/AVI diplotype × propylthiouracil (PTU) | primary (F-PRIMARY) | **KEEP AS CONFIRMATORY** | TAS2R38は承認20遺伝子に含まれる。薬剤はDrug ID/KEDD ID→自由記載で同定可能。疎ならn<200で PRE-SPECIFIED BUT UNTESTABLE（73/74/91）。P10による救済禁止。 | 06-13修正版が承認版の場合: 同版は5薬剤カテゴリ（Ca拮抗薬/ARB・スタチン・NSAIDs・消化器用薬・メトホルミン）を『主たる解析対象』と明記し、本予測の薬剤はその列挙外。confirmatory/secondary維持には同版との整合（列挙外薬剤を事前規定済み仮説として扱えるか）の確認が必要。 | frozen outcome（曝露）とプロトコル目的変数（処方変更）の対応を最終freezeで固定。TAS2R38 3SNPの分譲manifest確認。 |
| P02 | 13_v2_FINAL/62 | TAS2R38 diplotype × methimazole (thiamazole) | primary (F-PRIMARY) | **KEEP AS CONFIRMATORY** | 承認遺伝子・分譲薬剤項目で検証可能。 | 06-13修正版が承認版の場合: 同版は5薬剤カテゴリ（Ca拮抗薬/ARB・スタチン・NSAIDs・消化器用薬・メトホルミン）を『主たる解析対象』と明記し、本予測の薬剤はその列挙外。confirmatory/secondary維持には同版との整合（列挙外薬剤を事前規定済み仮説として扱えるか）の確認が必要。 | 同上。 |
| P03 | 13_v2_FINAL/62/72 | TAS2R38 × chloramphenicol (capsule/suspension) | secondary; 72: PRE-SPECIFIED BUT UNTESTABLE（国内経口使用ほぼ無し） | **KEEP AS SECONDARY** | 範囲内（承認遺伝子・薬剤項目あり）。検証可否は受領後の genotype-blind 件数で frozen floor により判定。 | 06-13修正版が承認版の場合: 同版は5薬剤カテゴリ（Ca拮抗薬/ARB・スタチン・NSAIDs・消化器用薬・メトホルミン）を『主たる解析対象』と明記し、本予測の薬剤はその列挙外。confirmatory/secondary維持には同版との整合（列挙外薬剤を事前規定済み仮説として扱えるか）の確認が必要。 | 件数floor判定のみ。代替薬への置換禁止。 |
| P04 | 13_v2_FINAL/62 | TAS2R38 × chlorpheniramine (syrup vs tablet) | secondary | **KEEP AS SECONDARY** | 範囲内。 | 06-13修正版が承認版の場合: 同版は5薬剤カテゴリ（Ca拮抗薬/ARB・スタチン・NSAIDs・消化器用薬・メトホルミン）を『主たる解析対象』と明記し、本予測の薬剤はその列挙外。confirmatory/secondary維持には同版との整合（列挙外薬剤を事前規定済み仮説として扱えるか）の確認が必要。 | — |
| P05 | 13_v2_FINAL/62/63/64 | TAS2R9 V187A (rs3741845) × ofloxacin | primary (F-PRIMARY) | **KEEP AS CONFIRMATORY** | TAS2R9は承認遺伝子。rs3741845 不在時のproxyはTAS2R9分譲領域内のSNPに限る（64のproxy規則をこの範囲に限定）。 | 06-13修正版が承認版の場合: 同版は5薬剤カテゴリ（Ca拮抗薬/ARB・スタチン・NSAIDs・消化器用薬・メトホルミン）を『主たる解析対象』と明記し、本予測の薬剤はその列挙外。confirmatory/secondary維持には同版との整合（列挙外薬剤を事前規定済み仮説として扱えるか）の確認が必要。 | 分譲SNP manifestで rs3741845 または領域内proxyを確認。 |
| P06 | 13_v2_FINAL/63 | TAS2R19 R299C (rs10772420) × quinine/quinidine | secondary; 72: PRE-SPECIFIED BUT UNTESTABLE | **REQUIRES PROTOCOL AMENDMENT** | TAS2R19 は承認20遺伝子に含まれない（申請範囲外）。履歴として保持し、実行しない。 |  | 遺伝子追加の計画変更が承認されない限りUNTESTABLEとして分母外に列挙。 |
| P07 | 13_v2_FINAL/62 | TAS2R38 × liquid oral medications (EX3 aggregate) | secondary | **KEEP AS SECONDARY** | 範囲内（薬剤項目＋剤形分類）。 | 06-13修正版が承認版の場合: 同版は5薬剤カテゴリ（Ca拮抗薬/ARB・スタチン・NSAIDs・消化器用薬・メトホルミン）を『主たる解析対象』と明記し、本予測の薬剤はその列挙外。confirmatory/secondary維持には同版との整合（列挙外薬剤を事前規定済み仮説として扱えるか）の確認が必要。 | — |
| P08 | 13_v2_FINAL/63 | TAS1R2 rs12033832 × sweetened formulations | secondary; 72: CONDITIONALLY TESTABLE | **KEEP AS SECONDARY** | TAS1R2は承認遺伝子。甘味剤含有は剤形proxyのみ。 | 06-13修正版が承認版の場合: 同版は5薬剤カテゴリ（Ca拮抗薬/ARB・スタチン・NSAIDs・消化器用薬・メトホルミン）を『主たる解析対象』と明記し、本予測の薬剤はその列挙外。confirmatory/secondary維持には同版との整合（列挙外薬剤を事前規定済み仮説として扱えるか）の確認が必要。 | rs12033832 の分譲確認。 |
| P09 | 13_v2_FINAL/63 | TRPA1 rs11988795 × chemesthetic oral liquids (ibuprofen susp.) | secondary | **REQUIRES PROTOCOL AMENDMENT** | TRPA1 は承認20遺伝子に含まれない。 |  | 計画変更なしではUNTESTABLEとして列挙。 |
| P10 | 13_v2_FINAL/62/91 | TAS2R4 differential-activation variant × thiourea class in AVI carriers | secondary (62/91); 82・README・LOCK_STATUSはF-PRIMARYと記載 | **REQUIRES PROTOCOL AMENDMENT** | TAS2R4 は承認20遺伝子に含まれず、63でも UNRESOLVED。62/91（82 rule 1で正）では secondary。P01救済は禁止のまま。 |  | F-PRIMARYは P01, P02, P05 と明記（82表・README・LOCK_STATUSの記載矛盾を最終freezeで訂正記録）。 |
| P11 | 13_v2_FINAL/72 | TAS2R43/TAS2R46 × acesulfame-K sweetened formulations | secondary; 72: PRE-SPECIFIED BUT UNTESTABLE | **UNTESTABLE WITH DISTRIBUTED DATA** | 甘味剤（Ace-K）の同定項目が分譲薬剤項目に無い。TAS2R43も承認外（TAS2R46のみ承認）。 |  | UNTESTABLEとして分母外に列挙。 |
| P12 | 13_v2_FINAL/62 | TAS2R38 × erythromycin suspension vs enteric/film tablet | secondary | **KEEP AS SECONDARY** | 範囲内。 | 06-13修正版が承認版の場合: 同版は5薬剤カテゴリ（Ca拮抗薬/ARB・スタチン・NSAIDs・消化器用薬・メトホルミン）を『主たる解析対象』と明記し、本予測の薬剤はその列挙外。confirmatory/secondary維持には同版との整合（列挙外薬剤を事前規定済み仮説として扱えるか）の確認が必要。 | — |
| N01 | 79 | route: TAS2R38 × insulin (parenteral) → null | control | **KEEP AS NEGATIVE CONTROL** | 範囲内。 |  | — |
| N02 | 79 | route: TAS2R38 × gentamicin (parenteral) → null | control; 72: UNTESTABLE（外来稀） | **KEEP AS NEGATIVE CONTROL** | 範囲内（件数floorで判定）。 |  | — |
| N03 | 79 | route: TAS2R38 × remdesivir (IV) → null | control; 72: UNTESTABLE（入院のみ） | **KEEP AS NEGATIVE CONTROL** | 範囲内（件数floorで判定）。 |  | — |
| N04 | 79 | route: TAS2R38 × fentanyl patch (transdermal) → null | control | **KEEP AS NEGATIVE CONTROL** | 範囲内。 |  | — |
| N05 | 79 | masking: TAS2R38 × omeprazole enteric-coated → null/attenuated | control | **KEEP AS NEGATIVE CONTROL** | 範囲内。 |  | — |
| N06 | 79 | masking: TAS2R38 × erythromycin enteric/film tablet → attenuated | control | **KEEP AS NEGATIVE CONTROL** | 範囲内（P12と対）。 |  | — |
| N07 | 79 | receptor-mismatch: TAS2R9 × PROP/thiourea → null | control | **KEEP AS NEGATIVE CONTROL** | TAS2R9承認。 |  | — |
| N08 | 79 | receptor-mismatch: TAS2R38 × ofloxacin → null | control | **KEEP AS NEGATIVE CONTROL** | 範囲内。 |  | — |
| N09 | 79 | receptor-mismatch: TAS2R38 × clindamycin liquid → null | control; 72: UNTESTABLE | **KEEP AS NEGATIVE CONTROL** | 範囲内（件数floorで判定）。 |  | — |
| N10 | 79 | receptor-mismatch: TAS1R2 × quinine → null | control; 72: UNTESTABLE | **KEEP AS NEGATIVE CONTROL** | TAS1R2承認。 |  | — |
| N11 | 79 | masking: TRPA1 × ibuprofen film-coated tablet → attenuated | control | **REQUIRES PROTOCOL AMENDMENT** | TRPA1は承認外。 |  | 計画変更なしではUNTESTABLEとして列挙。 |
| N12 | 79 | behavioral: TAS2R38 × supplement/health-food use → null | control | **KEEP AS NEGATIVE CONTROL** | 服薬項目は『お薬・サプリメント等』を含み構成可能。 |  | — |
| C1 | 25/72 | formulation contrast C1 | F-CONTRAST (Holm) | **KEEP AS SECONDARY** | 範囲内。ただし25（script 09出力: erythromycin suspension vs enteric tab）と72（EX3 vs EX1 within TAS2R38-ligand drugs）で定義が不一致。 | 06-13修正版が承認版の場合: 同版は5薬剤カテゴリ（Ca拮抗薬/ARB・スタチン・NSAIDs・消化器用薬・メトホルミン）を『主たる解析対象』と明記し、本予測の薬剤はその列挙外。confirmatory/secondary維持には同版との整合（列挙外薬剤を事前規定済み仮説として扱えるか）の確認が必要。 | どちらの定義が凍結対象かを最終freezeで記録（結果を見る前）。 |
| C2 | 25/72 | formulation/route contrast C2 | F-CONTRAST | **KEEP AS SECONDARY** | 25: acetaminophen liquid vs film tablet（根拠受容体TAS2R39は承認外）／72: oral liquid vs parenteral same drug。定義不一致・遺伝子割当未規定。 | 06-13修正版が承認版の場合: 同版は5薬剤カテゴリ（Ca拮抗薬/ARB・スタチン・NSAIDs・消化器用薬・メトホルミン）を『主たる解析対象』と明記し、本予測の薬剤はその列挙外。confirmatory/secondary維持には同版との整合（列挙外薬剤を事前規定済み仮説として扱えるか）の確認が必要。 | 遺伝子割当がTAS2R39を要する場合はREQUIRES PROTOCOL AMENDMENTへ移す旨を最終freezeで判断。 |
| C3 | 25/72 | formulation contrast C3 | F-CONTRAST | **KEEP AS SECONDARY** | 25: theophylline elixir vs SR tablet／72: erythromycin suspension vs tablet。定義不一致。 | 06-13修正版が承認版の場合: 同版は5薬剤カテゴリ（Ca拮抗薬/ARB・スタチン・NSAIDs・消化器用薬・メトホルミン）を『主たる解析対象』と明記し、本予測の薬剤はその列挙外。confirmatory/secondary維持には同版との整合（列挙外薬剤を事前規定済み仮説として扱えるか）の確認が必要。 | 同上。 |
| C4 | 25/72 | formulation contrast C4 | F-CONTRAST | **KEEP AS SECONDARY** | 25: KCl liquid vs ER tablet／72: OD vs standard tablet。定義不一致。 | 06-13修正版が承認版の場合: 同版は5薬剤カテゴリ（Ca拮抗薬/ARB・スタチン・NSAIDs・消化器用薬・メトホルミン）を『主たる解析対象』と明記し、本予測の薬剤はその列挙外。confirmatory/secondary維持には同版との整合（列挙外薬剤を事前規定済み仮説として扱えるか）の確認が必要。 | 同上。 |
| C5 | 25/72 | route/release contrast C5 | F-CONTRAST | **KEEP AS SECONDARY** | 25: insulin route contrast／72: enteric vs non-enteric same ingredient。定義不一致。 |  | 同上。 |
| GR1 | 95/83§4-G/80 | formal 1-df genotype × ordinal exposure (EX0–EX3) interaction β3 | F-GRADIENT, principal mechanistic test | **KEEP AS CONFIRMATORY** | 分譲データ（薬剤項目＋剤形）で構成可能。G（どの遺伝子型）とY（どの薬剤集合）が95で一意に規定されていない。 |  | G/Y の一意化と、共変量からancestry PCを除く扱い（GR/SAP-COV2参照）を最終freezeで固定。parser実文字列QC合格が前提。 |
| GR2 | 95/80 | categorical-E secondary model and order-restricted /β_EX3/≥…≥/β_EX0/ | secondary within F-GRADIENT | **KEEP AS SECONDARY** | 範囲内。 |  | — |
| GR3 | 80 | descriptive ordered-gradient table (G1/S1/G→E/G→F/G→T/control) | descriptive | **KEEP AS SECONDARY** | S1（知覚）は UNMEASURED のまま。 |  | — |
| CA1 | 96/81 | continuous calibration: Spearman(evidence score, signed Z_i), ≥10,000 permutations, seed 42 | F-CALIBRATION | **KEEP AS CONFIRMATORY** | 範囲内。ただしP06/P09/P10/P11が分母外となるため評価可能点は最大8（P01–P05,P07,P08,P12）で、受領前にpowerが低いことを明記。 |  | 最小評価点数（UNDEFINED扱いの閾値）を最終freezeで明記。 |
| CA2 | 32/81 | binary supported/not-supported calibration | secondary within F-CALIBRATION (82 rule 4) | **KEEP AS SECONDARY** | 範囲内。 |  | — |
| RB1 | 21/23 | evidence-score rubric G+H+R+V+Rep+F+O−A and frozen scores P01–P12 | frozen input to calibration | **KEEP AS CONFIRMATORY** | DRY_REPRODUCTION_AUDITで全12点を再計算し一致。 |  | 変更不可。 |
| HI1 | 62 (+82 rule 1) | prediction hierarchy: primary = P01, P02, P05; others secondary; N01–N12 control | frozen | **KEEP AS CONFIRMATORY** | 62が正（82 rule 1）。82表・README_HANDOFF・LOCK_STATUSの『F-PRIMARY = P01, P02, P05, P10』は62と矛盾する記載誤り。 |  | 最終freezeで訂正をerrataとして記録（履歴ファイルは書換えない）。 |
| SAP-POP | 83§1 | analysis population: genotyped, wave-1 medication answered; wave-2 analyses in both-wave subset | frozen | **SUPERSEDED BY APPROVED-PROTOCOL REQUIREMENT** | 承認計画は登録時20歳以上と重大欠測除外を要求（旧定義に年齢条件なし）。 | 06-13修正版ではさらにベースライン・第2段階の両方参加者に限定。 | 20歳以上（＋承認版により両wave参加）を最終freezeに記載。 |
| SAP-G | 83§2/63/65 | genotype coding: TAS2R38 PAV dosage, other effect-allele dosage | frozen | **KEEP AS CONFIRMATORY** | 承認遺伝子に限り適用。 |  | — |
| SAP-O1 | 83§3 | O1 exposure presence (drug/class), binary | primary outcome | **KEEP AS SECONDARY** | 承認計画の目的変数は処方変更（用量変更・薬剤変更: switch/addition/deletion）であり、現在使用は主要目的変数になり得ない。O1自体はwave別横断指標として保持。 |  | P01/P02/P05 の主要検定をどの目的変数で行うかを最終freezeで固定。 |
| SAP-O2 | 83§3 | O2 EX3 vs EX1 within drug | primary-family outcome | **KEEP AS SECONDARY** | 範囲内（剤形）。 |  | — |
| SAP-O3 | 83§3/74/78 | O3 cross-wave (ph1→ph2) reported-exposure transition/discordance | secondary | **KEEP AS CONFIRMATORY** | 承認計画の目的変数（処方変更）に対応するため主要へ格上げ。用語は78に従い『reported exposure transition』（adherence/意図/味覚駆動とは呼ばない）。 |  | 用量変更・有効成分変更・同一治療目的内switch・追加・削除の操作的定義を最終freezeで規定。 |
| SAP-O4 | 83§3 | O4 EX3 share (ordinal/continuous) | frozen | **KEEP AS SECONDARY** | 範囲内。 |  | — |
| SAP-M1 | 83§4 | O1/O2 logistic; O3 logistic with participant-clustered SE; O4 linear/ordinal; OR+95%CI; sign check before p | frozen | **KEEP AS CONFIRMATORY** | 範囲内。 |  | — |
| SAP-COV1 | 83§4/95 | legacy covariate set: age + sex + wave + 10 ancestry PCs (+indication proxy) | frozen | **SUPERSEDED BY APPROVED-PROTOCOL REQUIREMENT** | 承認計画は年齢・性別・既往歴・併存疾患・生活習慣・社会経済指標の調整を要求。 |  | 共変量集合を分譲項目名で最終freeze。 |
| SAP-COV2 | 83§4/95 | 10 genome-wide ancestry principal components | frozen covariate | **UNTESTABLE WITH DISTRIBUTED DATA** | 分譲は候補遺伝子領域SNPのみでPC算出不可、PC変数もデータセット仕様に無い。 |  | 代替（例: 出生地コード）を採る場合は最終freezeで明記。 |
| SAP-QC1 | 83§2/87 | genotype QC: MAF, HWE, missingness (genotype-blind) | frozen | **KEEP AS CONFIRMATORY** | 範囲内（分譲SNPに対して）。 |  | — |
| SAP-QC2 | 83§2/87 | genotype QC: relatedness and ancestry PCs | frozen | **UNTESTABLE WITH DISTRIBUTED DATA** | genome-wide SNP・血縁ID がデータセット仕様に無い。 |  | — |
| SAP-EST | 83§5 | estimand: population-average genotype-associated difference in past-two-week reported exposure; not adherence/perception | frozen | **KEEP AS CONFIRMATORY** | 範囲内。 |  | 処方変更目的変数への拡張時も同じ否定条件を維持。 |
| SAP-MISS | 83§6 | complete-case; MI only as sensitivity | frozen | **KEEP AS CONFIRMATORY** | 範囲内。 |  | — |
| SAP-ORDER | 83§7 | ordered execution: genotype-blind QC → analysis-set lock → primary → gradient → controls → contrasts → calibration → 85 | frozen | **KEEP AS CONFIRMATORY** | 範囲内。前段に final pre-receipt freeze → independent timestamp → receipt を追加。 |  | — |
| SAP-SW | 83§8 | software freeze | frozen | **KEEP AS CONFIRMATORY** | 範囲内。 |  | — |
| S1 | 84 | unspecified-tablet EX2→EX1 reclassification | sensitivity | **KEEP AS SECONDARY** | 範囲内。 |  | — |
| S2 | 84/64 | P05 proxy-variant swap | sensitivity | **KEEP AS SECONDARY** | proxyはTAS2R9分譲領域内に限る。 |  | — |
| S3 | 84/65 | A49P-only TAS2R38 fallback | sensitivity | **KEEP AS SECONDARY** | 範囲内。 |  | — |
| S4 | 84 | age ≥40 subset | sensitivity | **KEEP AS SECONDARY** | 範囲内。 |  | — |
| S5 | 84 | prescription-only exposures (入手方法=処方箋) | sensitivity | **KEEP AS SECONDARY** | 入手方法項目が分譲仕様に存在。 |  | — |
| S6 | 84/75 | claims-defined exposure replication | sensitivity (conditional) | **UNTESTABLE WITH DISTRIBUTED DATA** | 承認計画は医科レセプト・介護保険の利用に言及するが、分譲予定データセット仕様に含まれない。 |  | 受領manifestで確認されるまでNOT RUN。 |
| S7 | 84 | TAS2R38 allelic vs diplotype coding | sensitivity | **KEEP AS SECONDARY** | 範囲内。 |  | — |
| S8 | 84 | add smoking + alcohol to models | sensitivity | **SUPERSEDED BY APPROVED-PROTOCOL REQUIREMENT** | 承認計画は生活習慣の調整を主解析で要求するため、感度解析から主モデル共変量へ移る。 |  | — |
| S9 | 84 | E-value | sensitivity | **KEEP AS SECONDARY** | 範囲内。 |  | — |
| S10 | 84 | multiple imputation (MAR) | sensitivity | **KEEP AS SECONDARY** | 範囲内。 |  | — |
| MT-P | 82 | F-PRIMARY Holm α=0.05 | frozen | **KEEP AS CONFIRMATORY** | 構成は62に従い P01, P02, P05。 |  | — |
| MT-S | 82 | F-SECONDARY BH q=0.10 | frozen | **KEEP AS SECONDARY** | 分母は承認範囲内の secondary 予測のみ（P06/P09/P10/P11は分母外として列挙）。 |  | — |
| MT-N | 82 | F-CONTROL descriptive | frozen | **KEEP AS NEGATIVE CONTROL** | N11は分母外として列挙。 |  | — |
| MT-C | 82 | F-CONTRAST Holm α=0.05 | frozen | **KEEP AS SECONDARY** | C1–C5定義の確定が前提。 |  | — |
| MT-G | 82/95 | F-GRADIENT single test α=0.05 | frozen | **KEEP AS CONFIRMATORY** | 範囲内。 |  | — |
| MT-CAL | 82/96 | F-CALIBRATION single test α=0.05 | frozen | **KEEP AS CONFIRMATORY** | 範囲内。 |  | — |
| MT-X | 82 | F-EXPLORATORY unadjusted, labelled | frozen | **KEEP AS EXPLORATORY** | 範囲内。 |  | — |
| MT-R2 | 82 rule 2 | UNDEFINED tests removed from denominator before correction and listed | frozen | **KEEP AS CONFIRMATORY** | 範囲内。 |  | — |
| PA1 | 71/94 | medication parser v1.0.0 (SHA-256 c722341a…) for formulation/route/EX class | frozen | **KEEP AS CONFIRMATORY** | 範囲内。再実行でgold 146件の出力が凍結結果と一致。 |  | — |
| PA2 | 72 | free text as the primary basis of active-ingredient identification | frozen premise | **SUPERSEDED BY APPROVED-PROTOCOL REQUIREMENT** | 分譲仕様に KEDD ID・Drug ID（45 slot×ph1/ph2）があるため、成分同定は structured ID 優先、自由記載はbrand/剤形/経路補完とQCへ（本セッション指示）。 |  | ID→成分→同一治療目的クラスの対応表を最終freezeで凍結。 |
| PA3 | 92/87/98-R1 | real ToMMo-string parser QC gate (300–500 genotype-blind strings) before any association | required gate | **KEEP AS CONFIRMATORY** | 範囲内。受領後・genotype非結合で実施。 |  | — |
| PA4 | 69 | formulary gold-corpus validation 145/146 (known failure: オオサカ堂 ビタミンC) | frozen | **KEEP AS CONFIRMATORY** | 再計算で一致。 |  | — |
| PA5 | 66/67/68 | formulation dictionary, EX0–EX3 oral-sensory exposure classes, taste-masking table | frozen | **KEEP AS CONFIRMATORY** | 範囲内。 |  | — |
| GT1 | 63/65 | TAS2R38 rs713598/rs1726866/rs10246939 → PAV/AVI haplotype | READY_WITH_TRANSFORMATION | **KEEP AS CONFIRMATORY** | 承認遺伝子。 |  | 分譲manifest確認。 |
| GT2 | 63 | TAS2R19 rs10772420 | READY | **REQUIRES PROTOCOL AMENDMENT** | 承認外遺伝子。 |  | — |
| GT3 | 63 | TRPA1 rs11988795 | READY | **REQUIRES PROTOCOL AMENDMENT** | 承認外遺伝子。 |  | — |
| GT4 | 63 | TAS1R2 rs12033832 | READY | **KEEP AS CONFIRMATORY** | 承認遺伝子（P08/N10で使用）。 |  | 分譲manifest確認。 |
| GT5 | 63/64 | TAS2R9 rs3741845 (+pre-specified proxy) | READY_WITH_PRESPECIFIED_PROXY | **KEEP AS CONFIRMATORY** | 承認遺伝子。proxyは領域内に限る。 |  | 分譲manifest確認。 |
| GT6 | 63 | TAS2R4 differential-activation variant | UNRESOLVED | **REQUIRES PROTOCOL AMENDMENT** | 承認外遺伝子かつ変異未特定。 |  | — |
| RW1 | 74 rule 1 | unit = participant × wave exposure state | frozen | **KEEP AS CONFIRMATORY** | 範囲内。 |  | — |
| RW2 | 74 rule 2/78 | two-week instrument cannot measure adherence/persistence/discontinuation/switching intent | frozen | **KEEP AS CONFIRMATORY** | 範囲内（処方変更目的変数にも適用）。 |  | — |
| RW3 | 74 rule 3 | cross-wave analyses secondary/supportive, never primary | frozen | **SUPERSEDED BY APPROVED-PROTOCOL REQUIREMENT** | 承認計画の目的変数はph1→ph2の処方変更であり、縦断変化を主要とする必要がある。 | 06-13修正版は両wave参加者限定を明記（同趣旨）。 | — |
| RW4 | 74 rule 4/73/91 | sparse-cell floor n<200 → PRE-SPECIFIED BUT UNTESTABLE; no merging/rescue | frozen | **KEEP AS CONFIRMATORY** | 範囲内。 |  | — |
| RW5 | 74 rule 5 | repeated measures with GEE / clustered SE | frozen | **KEEP AS CONFIRMATORY** | 範囲内。 |  | — |
| RW6 | 74 rule 6/76/77 | wave-varying indication confounding; DAG-based indication proxies | frozen | **KEEP AS CONFIRMATORY** | 範囲内（疾患・治療関連の調査票項目が分譲仕様にある）。 |  | — |
| PW1 | 73/10_power_assessment.py | pre-analysis power assessment (seed 42; rare drug × rare variant MARGINAL) | frozen | **KEEP AS SECONDARY** | 再実行で9シナリオ全一致。floor値はRW4で拘束。 | 06-13修正版の想定標本数（両時点服薬記録 約20,000–25,000）は旧前提と別に記録。 | — |
| TM1 | 78 | outcome terminology freeze (reported exposure; banned: adherence, persistence, taste-driven, preference) | frozen | **KEEP AS CONFIRMATORY** | 範囲内。 |  | — |
| IN1 | 85 | interpretation matrix A–E with pre-registered assignment order | frozen | **KEEP AS CONFIRMATORY** | 範囲内。 |  | — |
| IN2 | 16/75/85 rule 4 | claim ceiling Level 4; Level-5 causal claims banned | frozen | **KEEP AS CONFIRMATORY** | 範囲内。 |  | — |
| IN3 | 86 | journal decision tree | frozen | **KEEP AS SECONDARY** | 出版判断であり検定ではない。 |  | — |
| AU1 | 87 | analysis authorization matrix (allowed/conditional/forbidden operations) | frozen | **KEEP AS CONFIRMATORY** | 範囲内。 |  | — |
| AU2 | 87/89/98 | 'explicit OPEN decision (89/98)' as trigger for genotype–outcome operations | frozen trigger | **SUPERSEDED BY APPROVED-PROTOCOL REQUIREMENT** | 本セッションの順序（reconciliation → final pre-receipt freeze → independent timestamp → receipt → offline validation）と承認範囲に置換。歴史的OPENは参加者レベル解析の許可にならない。 |  | — |
| AM1 | 88 | amendment policy | frozen | **KEEP AS CONFIRMATORY** | 範囲内。 |  | — |
| GA1 | docs/17 | Stage 0–2 GO/NO-GO: CONDITIONAL GO | historical | **KEEP AS SECONDARY** | 再現可能な定量入力を監査（DRY_REPRODUCTION_AUDIT）。条件は後続lockに継承。 |  | — |
| GA2 | 36 | feasibility gate: CONDITIONAL GO TO PRIMARY VALIDATION | historical | **KEEP AS SECONDARY** | 件数記載の誤り（8→9）は61で訂正済み。条件1の遺伝子リストにTAS2R19/TRPA1を含む（承認外）。 |  | — |
| GA3 | 61 | pre-opening errata E1 (9 predictions with score ≥9) | errata | **KEEP AS CONFIRMATORY** | 再計算で9件（P01–P07, P09, P12）を確認。 |  | — |
| GA4 | 89 | final opening decision v1: OPEN WITH RESTRICTIONS | superseded by 98 | **SUPERSEDED BY APPROVED-PROTOCOL REQUIREMENT** | 98で置換済み、かつAU2に従い認可効力なし。 |  | — |
| GA5 | 98 | final opening decision v2: OPEN PRIMARY DATA WITH RESTRICTIONS | historical gate | **SUPERSEDED BY APPROVED-PROTOCOL REQUIREMENT** | historical gate decision。本セッションでは参加者レベル解析を開始する根拠にしない（AU2）。 |  | — |
| GA6 | 98 restrictions 1–6 | binding restrictions: parser gate, variant availability/floors, P01/P10 separation, denominator reporting, instrument/claims limits, no isolated-association framing | binding | **KEEP AS CONFIRMATORY** | 範囲内。 |  | — |
| RS1 | 75 | claims (医科レセプト) / dispensing linkage module | secondary optional | **UNTESTABLE WITH DISTRIBUTED DATA** | 承認計画の必要性欄は医科レセプト・介護保険に言及するが、分譲予定データセット仕様（xlsx）に無い。 |  | 受領manifestで確認されるまで主解析の前提にしない。 |
| RS2 | 75/80 | G → S1 direct sensory (psychophysical) phenotype | banned (no taste phenotype assumed) | **UNTESTABLE WITH DISTRIBUTED DATA** | 心理物理学的味覚測定は分譲に無い。ただし分譲仕様には自己申告の味覚項目（ph1: 甘・塩・酸・苦・うま味を感じない、常に口の中が苦い等／ph2: 味を感じにくい 1項目）があり、旧freezeの『味覚表現型なし』という前提は事実として不正確。 |  | 自己申告味覚項目を使うかは最終freezeで事前規定するまで解析しない（本文書では新規解析を追加しない）。 |
| RS3 | docs/17 condition 5 | pediatric-style rejection endpoints | conditional | **UNTESTABLE WITH DISTRIBUTED DATA** | 解析対象は20歳以上。 |  | — |
| RS4 | 75/84 S8/docs/27 | FFQ ph1/ph2 (coffee/tea/alcohol etc.) use | covariate / sensitivity only | **KEEP AS SECONDARY** | 分譲仕様にFFQ ph1/ph2あり。旧freezeに変数レベルのtriangulation仕様は無い。 |  | 限定したchemosensory phenotypeのsecondary triangulationとして変数・方向・検定を最終freezeで規定。 |
| RS5 | keikaku 統計解析 | regularized regression / gradient boosting with internal cross-validation | not in legacy freeze (protocol) | **KEEP AS EXPLORATORY** | 承認計画に記載。旧freezeの検定階層外なので確認的主張には使わない。 |  | — |
| RS6 | keikaku 統計解析 | external validation | not in legacy freeze (protocol) | **UNTESTABLE WITH DISTRIBUTED DATA** | 外部コホートは分譲に無い。 |  | — |
| RS7 | keikaku 統計解析 | survival analysis of prescription change | not in legacy freeze (protocol) | **UNTESTABLE WITH DISTRIBUTED DATA** | 2時点の横断調査で日付付き処方イベントが無い。 |  | — |
| RS8 | keikaku 統計解析 | genome-wide association (GWAS) | not in legacy freeze (protocol, exploratory) | **UNTESTABLE WITH DISTRIBUTED DATA** | 分譲は候補遺伝子領域SNPのみ。 | 06-13修正版はGWASを候補遺伝子領域解析に置換済み（整合）。 | — |
| RS9 | keikaku 統計解析 | candidate-region association across the 20 approved genes | not in legacy freeze (protocol) | **KEEP AS EXPLORATORY** | 承認範囲内。旧予測にない遺伝子・SNPはF-EXPLORATORY。 |  | — |
| RS10 | keikaku 目的変数 | tolerability auxiliary indicators (adverse events, laboratory values) | not in legacy freeze (protocol) | **KEEP AS EXPLORATORY** | laboratory_test ph1/ph2は分譲仕様にある。有害事象項目は未確認。 |  | — |
| RS11 | keikaku 主研究への統合 | providing genotype–prescription-change estimates to the main study (immune profile / clinical outcome) | out of legacy scope | **UNTESTABLE WITH DISTRIBUTED DATA** | 免疫・臨床転帰データはToMMo分譲に無い。本研究は推定値の提供まで。 |  | — |
| RS12 | keikaku 情報 | metabolomics | not used | **UNTESTABLE WITH DISTRIBUTED DATA** | 分譲仕様に含まれない。 |  | — |
| FH1 | research arc | acquired sensory plasticity of chemosensory phenotype | future hypothesis | **UNTESTABLE WITH DISTRIBUTED DATA** | ToMMo分譲で検証不能。 |  | — |
| FH2 | research arc | 食育 / sensory conditioning intervention | future hypothesis | **UNTESTABLE WITH DISTRIBUTED DATA** | 介入データ無し。 |  | — |
| FH3 | research arc | modification of medication response by adjusting sensory phenotype | future hypothesis | **UNTESTABLE WITH DISTRIBUTED DATA** | 介入データ無し。 |  | — |
| FH4 | research arc | health-economic benefit (wider use of inexpensive/off-patent drugs) | future hypothesis | **UNTESTABLE WITH DISTRIBUTED DATA** | 費用データ無し。 |  | — |
| FH5 | research arc | global-health benefit | future hypothesis | **UNTESTABLE WITH DISTRIBUTED DATA** | 検証不能。 |  | — |
| FH6 | research arc / keikaku | immune mediation of chemosensory–drug association | future hypothesis | **UNTESTABLE WITH DISTRIBUTED DATA** | 免疫データ無し。 |  | — |

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
