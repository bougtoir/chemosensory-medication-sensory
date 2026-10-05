# DRY_REPRODUCTION_AUDIT

旧handoffのdry解析（evidence synthesis → prediction freeze → negative controls → gate）を、保存済みの検索出力・生データから独立に再実行し、凍結済み成果物と照合した記録。本文書は `dry_reproduction/run_dry_reproduction_audit.py --render` により `dry_reproduction/results/` の機械可読出力（`dry_reproduction_checks.csv`, `file_comparison.csv`, `summary.json`）から生成される。数値の手書きは無い。

**参加者レベルToMMoデータは一切使用していない**（§E）。ToMMo関連で読んだのは公開調査票メタデータ（`data/raw/tommo_public/`, 10/10 ハッシュ一致）のみ。

## 判定の要約

| 項目 | 結果 |
|---|---|
| checks 総数 | 89 |
| status 内訳 | AUDIT_ONLY=3; DIFFERENT=2; DISCREPANCY=10; DISCREPANCY (errata 61)=1; DISCREPANCY (label only)=1; EXACT=25; FAIL=1; INCOMPLETE_HANDOFF=1; NOT_RUN=1; PASS=40; SEMANTIC_MATCH=1; SEMANTIC_MATCH_ORDERED=1; SEMANTIC_MATCH_UNORDERED=1; SOURCE_DRIFT=1 |
| オフライン再実行（scripts 04–10）exit code | 04_curate_evidence=0, 05_evidence_graph=0, 06_meta_analysis=0, 07_matrices_predictions=0, 08_figures=0, 09_expansion=0, 10_power_assessment=0 |
| オフライン再生成ターゲット | 21/23 byte/semantic一致; 不一致: 03_STUDY_INVENTORY.csv, 05_DRUG_SENSORY_EVIDENCE.csv |
| 不一致の原因 | 凍結search poolに無いanchor PMID 27569025（§C）。これを加えた再実行では 03=SEMANTIC_MATCH_UNORDERED, 05=SEMANTIC_MATCH_ORDERED |
| evidence score P01–P12 再計算 | 不一致: none（13_v2_FINAL との不一致: none; tier不一致: none） |
| 再計算スコア | P01=15; P02=14; P03=12; P04=11; P05=9; P06=11; P07=12; P08=7; P09=10; P10=6; P11=7; P12=10 |
| negative controls N01–N12 | ID一致 True; gene不一致 none; drug不一致 none; class label の改称: adherence->behavioral; mismatch->receptor-mismatch; published_null->receptor-mismatch |
| gate（score≥9の件数） | 36記載 8 → 再計算 9（P01, P02, P03, P04, P05, P06, P07, P09, P12）; 61 errata の訂正値 9 |
| 予測階層 | 62/23/13_v2_FINAL: P01, P02, P05; 82表/README/LOCK_STATUS: P01, P02, P05, P10（矛盾: 82.F-PRIMARY, README_HANDOFF.F-PRIMARY, LOCK_STATUS.F-PRIMARY） |
| parser v1.0.0 gold corpus | generic_name=145/146; formulation=145/146; route=145/146; oral_sensory_exposure=145/146; taste_masking=146/146; 失敗: オオサカ堂 ビタミンC; 凍結出力と意味的一致 True |
| 実ToMMo文字列 parser gate（92） | NOT_RUN（受領前・参加者データ禁止のため） |
| pytest（凍結パッケージ） | 10 passed, 0 failed |
| pytest（オフライン再生成ツリー） | 8 passed, 2 failed（tests/test_outputs.py::test_inventory_covers_all_evidence_pmids; tests/test_outputs.py::test_references_have_no_orphans） |
| live再取得から13_v2_FINAL等の再生成 | 11_RECEPTOR_DRUG_MATRIX.csv=EXACT; 23_CANDIDATE_PREDICTIONS_ALL.csv=EXACT; 26_NEGATIVE_CONTROLS.csv=EXACT; 13_LOCKED_PREDICTIONS_v2_FINAL.csv=EXACT |

結論: locked prediction table（`13_LOCKED_PREDICTIONS_v2_FINAL.csv`）、evidence score、negative-control表、gate の定量部分は、参加者レベルデータなしに再生成できた。完全なbyte再現を妨げたのは (1) 凍結search poolの組立て手順（seed/anchor層、行順）がどのスクリプトにも記述されていないこと、(2) anchor XML の台帳不備、の2点で、科学的出力（スコア・予測・対照）には影響しない。文書間の不一致（階層、contrast定義、件数記載、ラベル）は §G に列挙し、どれも黙って正規化していない。

## A. 入力とマニフェスト

- `HANDOFF_MANIFEST.csv`: 76/77 SHA-256一致、不一致 0、欠落 1（preopening_lock_60-90.zip）。
- `60_PREOPENING_INPUT_MANIFEST.md`: 一致 24/35、後続世代により置換 11、説明不能 0（none）。60は13_v2_FINALを23行と記載するが実ファイルは24行（ハッシュは一致; 記載誤り）。
- `97_PREOPENING_AMENDMENT_MANIFEST.md`: 18/18 一致。
- 添付ZIP: 78 files、gitブランチと共通 77、内容不一致 none。ZIPに無いディレクトリ: 09_META_ANALYSIS, data, docs, evidence, figures, prediction, scripts, tests。ZIPは文書レベルのhandoffであり、スクリプト・テスト・生データはgitブランチ `devin/1791087629-chemosensory-med-sensory` 側にのみ存在する（ZIP単独では再現不能）。

## B. 生データ（凍結スナップショット）

| source | 台帳行 | 一致 | 備考 |
|---|---|---|---|
| PubMed stage-1 query XML | 20 | 20 | schema異常行: none |
| PubMed seed/anchor XML | 11 | 11 | schema異常行: SEED_27569025.xml（`seed_ledger.csv` に別スキーマで追記）; 台帳に無いXML: SEED_extra_anchors.xml |
| BitterDB receptor pages | 236 | 236 | script再パースと台帳一致 236 |
| PubChem JSON | 197 | 197 | property一致 197; 取得失敗（凍結時点から）: nifedipine retard |

凍結原本（`data/raw/`）は読み取りのみで、上書きしていない。

## C. PubMed search pool

- stage-1 XML の和集合 4396 PMID、台帳記載XML（stage-1＋seed）5112、全保存XML 5126、凍結 `evidence/search_pool.csv` 5125。
- 全保存XML vs 凍結pool: 凍結のみ none、XMLのみ 27569025。台帳記載XMLのみでは凍結のみ 14 件（`SEED_extra_anchors.xml` が台帳外のため）。
- anchor PMID 27569025 は `SEED_27569025.xml` にあり、凍結 `03_STUDY_INVENTORY.csv` には含まれるが凍結 search pool には含まれない（False）。凍結poolで04を再実行すると03が78行（凍結79行）になり、05の5セルが変わる。27569025を加えると両者とも凍結値と一致する。
- 再現は集合レベル。凍結poolの行順・行メタデータの組立て手順はどのスクリプトにも記述されていない。

## D. BitterDB / PubChem

- BitterDB: 全236ページを script 02 のロジックで再パースすると 1777 edges（非ヒト/表記揺れ受容体を含む）。凍結 `evidence/bitterdb_human_receptors.csv`（26 receptor IDs）で絞ると 1108 edges で凍結 1108 と集合一致（True）。ligandを持つ受容体 23。
- 凍結 compound 表は human 絞込み前の全ページ由来（再導出 684 = 凍結 684; human-only なら 645）。この非対称は凍結時の仕様であり、downstream（11/23/13）の再生成結果は一致。
- PubChem: 197 JSON、property・SHA-256とも全一致。

## E. 参加者レベルデータの除外

- 追跡対象の data ルート: data/raw/bitterdb, data/raw/pubchem, data/raw/pubmed, data/raw/tommo_public。
- 参加者レベル形式の拡張子（VCF/BGEN/PLINK/parquet 等）: none。
- オフライン再実行はプロキシを不通アドレスに向けた隔離コピーで実行し、ネットワークスクリプト（01–03）を含まない（違反: none）。
- 本監査は genotype × medication の関連推定、genotype 頻度、medication 件数のいずれも計算していない。

## F. live 再取得（凍結入力の再現とは別物）

- 2026-10-04 に scripts 01–03 を別チェックアウトで未改変のまま実行し、新しいスナップショットとして `data/raw_live_20261004/`（`LEDGER.csv`: URL、クエリ、取得UTC、サイズ、SHA-256、利用条件。PubMed XML は gzip、展開後SHA-256も記録）に保存した。凍結 `data/raw/` は上書きしていない。
- PubMed stage-1: 4397 PMID（凍結比 +3 / −2）= SOURCE_DRIFT（索引の増減）。seed/anchor層は01が再取得しないため凍結XMLを使用。
- BitterDB: 1777 edges（human 絞込み後 1108; 凍結比 +0 / −0）。
- PubChem: 成功 197、値変化 none、新規 none。
- live 入力からの再生成: 11_RECEPTOR_DRUG_MATRIX.csv=EXACT; 23_CANDIDATE_PREDICTIONS_ALL.csv=EXACT; 26_NEGATIVE_CONTROLS.csv=EXACT; 13_LOCKED_PREDICTIONS_v2_FINAL.csv=EXACT。
- 公開ミラーには第三者の生レコードを出さない（`data` は sync 除外）。

## G. 不一致一覧（黙って正規化しない）

1. **予測階層**: `62`（82 rule 1 で正）・`23`・`13_v2_FINAL` は primary = P01, P02, P05。`82` 表・`README_HANDOFF.md`・`LOCK_STATUS.md` は F-PRIMARY = P01, P02, P05, P10。`91` は P10 を secondary とする（P10=secondary）。82 rule 1 により 62 を正とし、他は記載誤りとして reconciliation（HI1）で扱う。
2. **gate件数**: `36` は score≥9 を 8 件と記載、再計算 9 件。`61` errata が 9 に訂正済みで、予測パネル自体は不変。
3. **contrast定義**: C1–C5 の定義が `25`（script 09出力）と `72` で 5/5 件異なる: C1: 25='erythromycin oral suspension vs enteric/film-coated tablet' / 72='EX3 vs EX1 within TAS2R38-ligand drugs' ; C2: 25='acetaminophen liquid/syrup vs film tablet' / 72='oral liquid vs parenteral same drug' ; C3: 25='theophylline elixir vs sustained-release tablet' / 72='suspension vs tablet erythromycin' ; C4: 25='potassium chloride oral liquid/drops vs extended-release tablet' / 72='OD vs standard tablet' ; C5: 25='insulin (route contrast) none vs parenteral' / 72='enteric vs non-enteric same ingredient'。
4. **negative-control class label**: adherence->behavioral; mismatch->receptor-mismatch; published_null->receptor-mismatch（36本文: 12 controls across 4 classes (route, masking, mismatch, adherence)）。ID・gene・drugは一致。
5. **マニフェスト**: `preopening_lock_60-90.zip` 欠落、60 の行数記載（23→実24）。
6. **PubMed台帳**: `SEED_extra_anchors.xml` が台帳外、`SEED_27569025.xml` 行が別スキーマ、anchor 27569025 が凍結poolに無い。
7. **再生成ツリーのpytest**: 03が78行になるため inventory/参考文献の整合テスト2件が失敗。参考文献削除や科学的出力の変更では直さず、原因（anchor）を記録するにとどめる。
8. **parser**: gold 146件中 `オオサカ堂 ビタミンC` のみ失敗（凍結時と同じ）。実ToMMo文字列ゲートは未実施。

## H. 状態区分

- EXACT / SEMANTIC_MATCH: 凍結値と一致（byte または正規化後）。
- DIFFERENT: 凍結入力からの再実行で値が異なる（原因は §C）。
- DISCREPANCY: 文書・台帳間の不一致。
- SOURCE_DRIFT: live 再取得での公開元変化。
- AUDIT_ONLY: 計算で再現できない判断（gate verdict 等）または非科学的成果物（図）。
- INCOMPLETE_HANDOFF: ZIP単独では再現不能。
- NOT_RUN: 参加者データが必要なため実施しない。
- FAIL: テスト失敗（原因記録済み）。

## I. 全チェック

| ID | component | check | status | observed | expected/note |
|---|---|---|---|---|---|
| M1 | manifest | HANDOFF_MANIFEST.csv SHA-256 vs files | **DISCREPANCY** | 76 match, 0 mismatch, 1 missing (preopening_lock_60-90.zip) | 77 match |
| M2 | manifest | 97 amendment manifest prefixes vs current files | **PASS** | 18/18 match | 18 |
| M3 | manifest | 60 pre-opening manifest hashes vs current files | **PASS** | 24 unchanged, 11 changed and re-hashed in 97, 0 changed without manifest entry (none) | unchanged or superseded via 97 |
| M4 | manifest | 60 stated row count of 13_LOCKED_PREDICTIONS_v2_FINAL.csv | **DISCREPANCY** | stated 23 | actual 24 — clerical; hash matches the 24-row file |
| R1 | raw/pubmed | search_ledger.csv hashes vs stored XML | **PASS** | 20/20 | 20 — rows in a different column schema: none |
| R2 | raw/pubmed | seed_ledger.csv hashes vs stored XML | **PASS** | 11/11 | 11 — rows in a different column schema: SEED_27569025.xml |
| R3 | raw/pubmed | XML files without ledger entry | **DISCREPANCY** | SEED_extra_anchors.xml | none |
| R4 | raw/bitterdb | bitterdb_ledger sha256_16 vs stored HTML | **PASS** | 236/236 | 236 |
| R5 | raw/pubchem | ledger ok rows with stored JSON | **PASS** | 197/197 | 197 — ledger failures retained: nifedipine retard |
| R6 | raw/tommo_public | public questionnaire ledger (bytes+SHA-256) | **PASS** | 10/10 | 10 — public blank questionnaires only |
| P1 | search_pool | Stage-1 query XML (20 files) -> unique PMIDs | **AUDIT_ONLY** | 4396 |  — subset of frozen pool |
| P2 | search_pool | Stage-1 + ledgered seed XML vs frozen evidence/search_pool.csv | **DISCREPANCY** | ledgered=5112, frozen=5125, only-frozen=14, only-ledgered=1 | identical PMID sets |
| P2b | search_pool | all stored XML (incl. unledgered SEED_extra_anchors.xml) vs frozen pool | **DISCREPANCY** | all=5126, only-frozen=[none], only-XML=[27569025] | identical PMID sets — set-level only; frozen row order and per-row metadata assembly are not encoded in any script |
| P3 | search_pool | anchor PMID 27569025 present in frozen pool | **DISCREPANCY** | False | True — unledgered XML content: SEED_extra_anchors.xml: [1562204, 2185626, 3797487, 6847015, 7148734, 10761934, 10761935, 12595690, 14997422, 15759003, 16636110, 20534469, 20551074, 21940398, 22218679, 23632915, 24413990, 26406243, 27138342, 27711175, 29982450, 30357384, 31006818, 32453275, 36894246, 36929150, 37685855, 39123846, 39535052, 39952694, 41485871, 42162282, 42605530, 42783596] |
| B1 | bitterdb | 02_bitterdb_scrape.py parse logic applied to stored HTML vs stored ledger | **PASS** | 236/236 ledger rows reproduced | 236 — script logic yields 1777 edges (non-human pages pass the 'human' regex) |
| B2 | bitterdb | edges after frozen human-receptor mapping vs frozen ligand table | **PASS** | 1108 edges / 26 receptor ids | 1108 edges — requires evidence/bitterdb_human_receptors.csv (curation step not encoded in 02) |
| B3 | bitterdb | compound table re-derived with 02 logic (unfiltered pages) | **PASS** | 684 | 684 — frozen compound table was NOT human-filtered; human-only compounds = 645 |
| C1 | pubchem | drug_chemical_space.csv properties re-derived from stored JSON | **PASS** | props 197/197, sha 197/197 | 197 |
| O0 | offline rerun | scripts 04-10 exit codes (network blocked) | **PASS** | 04_curate_evidence=0, 05_evidence_graph=0, 06_meta_analysis=0, 07_matrices_predictions=0, 08_figures=0, 09_expansion=0, 10_power_assessment=0 | all 0 |
| O-03_STUDY_INVENTORY.csv | offline rerun | regenerate 03_STUDY_INVENTORY.csv | **DIFFERENT** |  | byte-identical — shape (79, 7) vs (78, 7); pmid only-frozen=['27569025'] only-regenerated=[] |
| O-04_VARIANT_EVIDENCE.csv | offline rerun | regenerate 04_VARIANT_EVIDENCE.csv | **EXACT** |  | byte-identical |
| O-05_DRUG_SENSORY_EVIDENCE.csv | offline rerun | regenerate 05_DRUG_SENSORY_EVIDENCE.csv | **DIFFERENT** |  | byte-identical — shape (17, 14) vs (17, 14); pmid only-frozen=[] only-regenerated=[]; differing cells=5 |
| O-06_PLASTICITY_EVIDENCE.csv | offline rerun | regenerate 06_PLASTICITY_EVIDENCE.csv | **EXACT** |  | byte-identical |
| O-evidence/sensory_behavior_evidence.csv | offline rerun | regenerate evidence/sensory_behavior_evidence.csv | **EXACT** |  | byte-identical |
| O-evidence/extraoral_evidence.csv | offline rerun | regenerate evidence/extraoral_evidence.csv | **EXACT** |  | byte-identical |
| O-evidence/evolution_evidence.csv | offline rerun | regenerate evidence/evolution_evidence.csv | **EXACT** |  | byte-identical |
| O-07_EVIDENCE_GRAPH.csv | offline rerun | regenerate 07_EVIDENCE_GRAPH.csv | **EXACT** |  | byte-identical |
| O-08_EVIDENCE_GRAPH.json | offline rerun | regenerate 08_EVIDENCE_GRAPH.json | **EXACT** |  | byte-identical |
| O-09_META_ANALYSIS/meta_results.json | offline rerun | regenerate 09_META_ANALYSIS/meta_results.json | **EXACT** |  | byte-identical |
| O-09_META_ANALYSIS/tas2r38_prop_meta_input.csv | offline rerun | regenerate 09_META_ANALYSIS/tas2r38_prop_meta_input.csv | **EXACT** |  | byte-identical |
| O-09_META_ANALYSIS/README.md | offline rerun | regenerate 09_META_ANALYSIS/README.md | **EXACT** |  | byte-identical |
| O-11_RECEPTOR_DRUG_MATRIX.csv | offline rerun | regenerate 11_RECEPTOR_DRUG_MATRIX.csv | **EXACT** |  | byte-identical |
| O-12_VARIANT_FUNCTION_MATRIX.csv | offline rerun | regenerate 12_VARIANT_FUNCTION_MATRIX.csv | **EXACT** |  | byte-identical |
| O-13_LOCKED_PREDICTIONS.csv | offline rerun | regenerate 13_LOCKED_PREDICTIONS.csv | **EXACT** |  | byte-identical |
| O-23_CANDIDATE_PREDICTIONS_ALL.csv | offline rerun | regenerate 23_CANDIDATE_PREDICTIONS_ALL.csv | **EXACT** |  | byte-identical |
| O-24_PREDICTION_EVIDENCE_AUDIT.csv | offline rerun | regenerate 24_PREDICTION_EVIDENCE_AUDIT.csv | **EXACT** |  | byte-identical |
| O-25_FORMULATION_ROUTE_CONTRASTS.csv | offline rerun | regenerate 25_FORMULATION_ROUTE_CONTRASTS.csv | **EXACT** |  | byte-identical |
| O-26_NEGATIVE_CONTROLS.csv | offline rerun | regenerate 26_NEGATIVE_CONTROLS.csv | **EXACT** |  | byte-identical |
| O-13_LOCKED_PREDICTIONS_v2_PRELIMINARY.csv | offline rerun | regenerate 13_LOCKED_PREDICTIONS_v2_PRELIMINARY.csv | **EXACT** |  | byte-identical |
| O-31_TOMMO_PREDICTION_TESTABILITY_MATRIX.csv | offline rerun | regenerate 31_TOMMO_PREDICTION_TESTABILITY_MATRIX.csv | **EXACT** |  | byte-identical |
| O-33_ALTERNATIVE_EXPLANATION_AUDIT.csv | offline rerun | regenerate 33_ALTERNATIVE_EXPLANATION_AUDIT.csv | **EXACT** |  | byte-identical |
| O-13_LOCKED_PREDICTIONS_v2_FINAL.csv | offline rerun | regenerate 13_LOCKED_PREDICTIONS_v2_FINAL.csv | **EXACT** |  | byte-identical |
| O-figures | offline rerun | figures/*.png (08_figures.py) | **AUDIT_ONLY** | 7/7 byte-identical |  — rasters are not scientific inputs to locks |
| O-power | offline rerun | 10_power_assessment.py power values vs 73 table | **PASS** | 9/9 values found in 73 | 9 |
| A-03_STUDY_INVENTORY.csv | anchor-augmented rerun | 04 with SEED_27569025 appended to pool: 03_STUDY_INVENTORY.csv | **SEMANTIC_MATCH_UNORDERED** |  | byte-identical — same rows, different row order; exit=0 |
| A-05_DRUG_SENSORY_EVIDENCE.csv | anchor-augmented rerun | 04 with SEED_27569025 appended to pool: 05_DRUG_SENSORY_EVIDENCE.csv | **SEMANTIC_MATCH_ORDERED** |  | byte-identical — values equal after numeric normalisation; exit=0 |
| S1 | evidence score | G+H+R+V+Rep+F+O-A recomputed from components (23) | **PASS** | P01=15; P02=14; P03=12; P04=11; P05=9; P06=11; P07=12; P08=7; P09=10; P10=6; P11=7; P12=10 | equal to evidence_score column |
| S2 | evidence score | component ranges per rubric 21 | **PASS** | none | none |
| S3 | evidence score | 13_v2_FINAL evidence_score equals 23 | **PASS** | none | none |
| S4 | evidence score | 13_v2_FINAL evidence_tier equals 23 tier | **PASS** | none | none |
| G1 | gate | count of directional predictions with score>=9 vs 36 | **DISCREPANCY (errata 61)** | recomputed 9 (P01, P02, P03, P04, P05, P06, P07, P09, P12) | 36 states 8 (P01–P07, P09, P12) — 61 corrects to 9: consistent |
| G2 | gate | number of directional predictions vs 36 | **PASS** | 12 | 12 |
| H-23.primary | hierarchy | primary set according to 23.primary | **PASS** | P01, P02, P05 | P01, P02, P05 — 62 is the declared source of truth (82 rule 1) |
| H-13_v2_FINAL.primary_or_secondary | hierarchy | primary set according to 13_v2_FINAL.primary_or_secondary | **PASS** | P01, P02, P05 | P01, P02, P05 — 62 is the declared source of truth (82 rule 1) |
| H-62.confirmatory_status | hierarchy | primary set according to 62.confirmatory_status | **PASS** | P01, P02, P05 | P01, P02, P05 — 62 is the declared source of truth (82 rule 1) |
| H-82.F-PRIMARY | hierarchy | primary set according to 82.F-PRIMARY | **DISCREPANCY** | P01, P02, P05, P10 | P01, P02, P05 — 62 is the declared source of truth (82 rule 1) |
| H-README_HANDOFF.F-PRIMARY | hierarchy | primary set according to README_HANDOFF.F-PRIMARY | **DISCREPANCY** | P01, P02, P05, P10 | P01, P02, P05 — 62 is the declared source of truth (82 rule 1) |
| H-LOCK_STATUS.F-PRIMARY | hierarchy | primary set according to LOCK_STATUS.F-PRIMARY | **DISCREPANCY** | P01, P02, P05, P10 | P01, P02, P05 — 62 is the declared source of truth (82 rule 1) |
| H-91.P10_status | hierarchy | primary set according to 91.P10_status | **PASS** | P10=secondary | P01, P02, P05 — 62 is the declared source of truth (82 rule 1) |
| N1 | negative controls | control IDs identical across 26, 79, 13_v2_FINAL | **PASS** | 12 | 12 |
| N2 | negative controls | genotype per control identical across 26/79/13_v2_FINAL | **PASS** | none | none |
| N3 | negative controls | exposure (first token) identical across 26/79/13_v2_FINAL | **PASS** | none | none |
| N4 | negative controls | class labels 26 (regenerated by 09) vs 79 (final) | **DISCREPANCY (label only)** | adherence->behavioral; mismatch->receptor-mismatch; published_null->receptor-mismatch | identical — 26 classes: adherence, masking, mismatch, published_null, route / 79 classes: behavioral, masking, receptor-mismatch, route / 36 text: 12 controls across 4 classes (route, masking, mismatch, adherence) |
| N6 | contrasts | C1-C5 definitions in 25 (script 09) vs 72 (observability) | **DISCREPANCY** | 5/5 differ | same contrast per ID — C1: 25='erythromycin oral suspension vs enteric/film-coated tablet' / 72='EX3 vs EX1 within TAS2R38-ligand drugs' ; C2: 25='acetaminophen liquid/syrup vs film tablet' / 72='oral liquid vs parenteral same drug' ; C3: 25='theophylline elixir vs sustained-release tablet' / 72='suspension vs tablet erythromycin' ; C4: 25='potassium chloride oral liquid/drops vs extended-release tablet' / 72='OD vs standard tablet' ; C5: 25='insulin (route contrast) none vs parenteral' / 72='enteric vs non-enteric same ingredient' |
| N5 | contrasts | C1-C5 present | **PASS** | C1, C2, C3, C4, C5 | C1..C5 |
| V-docs/17 | gate | verdict of docs/17 recorded in LOCK_STATUS chain | **PASS** | CONDITIONAL GO | present — verdicts are judgments; inputs re-derived in G1/G2/N*/S* |
| V-36 | gate | verdict of 36 recorded in LOCK_STATUS chain | **PASS** | CONDITIONAL GO TO PRIMARY VALIDATION | present — verdicts are judgments; inputs re-derived in G1/G2/N*/S* |
| V-89 | gate | verdict of 89 recorded in LOCK_STATUS chain | **PASS** | OPEN WITH RESTRICTIONS | present — verdicts are judgments; inputs re-derived in G1/G2/N*/S* |
| V-98 | gate | verdict of 98 recorded in LOCK_STATUS chain | **PASS** | OPEN PRIMARY DATA WITH RESTRICTIONS | present — verdicts are judgments; inputs re-derived in G1/G2/N*/S* |
| V-chain | gate | historical gate chain (judgment, not computable) | **AUDIT_ONLY** | 17: CONDITIONAL GO -> 36: CONDITIONAL GO TO PRIMARY VALIDATION -> 89: OPEN WITH RESTRICTIONS -> 98: OPEN PRIMARY DATA WITH RESTRICTIONS |  |
| V-17B | gate | docs/17 domain B receptor count vs frozen BitterDB ligand table | **PASS** | 23 | 23 — '76 drug edges' not re-derivable: definition not encoded in any script |
| X1 | parser | medication_parser.py SHA-256 vs 94 | **PASS** | c722341a04419e32b8e999411d5fb4977e809fbbc3038ad519481676a5fa99de | c722341a04419e32b8e999411d5fb4977e809fbbc3038ad519481676a5fa99de |
| X2 | parser | rerun on gold corpus vs frozen validation_output.csv | **SEMANTIC_MATCH** | True | True — integer vs float exposure codes normalised |
| X3 | parser | accuracy vs gold labels vs 69 table | **PASS** | generic_name=145/146; formulation=145/146; route=145/146; oral_sensory_exposure=145/146; taste_masking=146/146 | generic_name=145/146; route=145/146; formulation=145/146; oral_sensory_exposure=145/146; taste_masking=146/146 |
| X4 | parser | real ToMMo-string validation (92) | **NOT_RUN** | requires delivered ToMMo strings |  — mandatory gate before any association run; out of scope here |
| T1 | tests | pytest on frozen package | **PASS** | 10 passed, 0 failed | 0 failed |
| T2 | tests | pytest on offline-regenerated package | **FAIL** | 8 passed, 2 failed | 0 failed — tests/test_outputs.py::test_inventory_covers_all_evidence_pmids; tests/test_outputs.py::test_references_have_no_orphans |
| E1 | exclusion | tracked data/ roots | **PASS** | data/raw/bitterdb, data/raw/pubchem, data/raw/pubmed, data/raw/tommo_public | public sources only |
| E2 | exclusion | genotype/participant-type files in package | **PASS** | none | none |
| E3 | exclusion | network calls in offline scripts 04-10 | **PASS** | none | none — offline stages also run with a dead proxy |
| Z1 | handoff zip | files in ZIP identical to package | **PASS** | 77 common, 0 differ | 0 differ |
| Z2 | handoff zip | package directories absent from ZIP | **INCOMPLETE_HANDOFF** | 09_META_ANALYSIS, data, docs, evidence, figures, prediction, scripts, tests | none — ZIP is a document-level handoff; scripts/tests/raw sources exist only in the git branch, so ZIP-only reproduction is impossible |
| L1 | live re-acquisition | live Stage-1 PubMed pool vs frozen Stage-1 XML | **SOURCE_DRIFT** | 4397 PMIDs (+3 / -2) | 4396 PMIDs — PubMed index growth since freeze; frozen seed/anchor layer not re-queried by 01 |
| L2 | live re-acquisition | live BitterDB human edges (frozen receptor mapping) vs frozen | **PASS** | 1108 (+0 / -0); raw script output 1777 | 1108 |
| L3 | live re-acquisition | live PubChem properties vs frozen | **PASS** | 197 resolved; changed: none; new: none | 197 resolved |
| L-11_RECEPTOR_DRUG_MATRIX.csv | live re-acquisition | pipeline on live BitterDB/PubChem + frozen pool: 11_RECEPTOR_DRUG_MATRIX.csv | **EXACT** |  | frozen — ; exits=[0] |
| L-23_CANDIDATE_PREDICTIONS_ALL.csv | live re-acquisition | pipeline on live BitterDB/PubChem + frozen pool: 23_CANDIDATE_PREDICTIONS_ALL.csv | **EXACT** |  | frozen — ; exits=[0] |
| L-26_NEGATIVE_CONTROLS.csv | live re-acquisition | pipeline on live BitterDB/PubChem + frozen pool: 26_NEGATIVE_CONTROLS.csv | **EXACT** |  | frozen — ; exits=[0] |
| L-13_LOCKED_PREDICTIONS_v2_FINAL.csv | live re-acquisition | pipeline on live BitterDB/PubChem + frozen pool: 13_LOCKED_PREDICTIONS_v2_FINAL.csv | **EXACT** |  | frozen — ; exits=[0] |

## J. ファイル比較

| run | file | status | note |
|---|---|---|---|
| offline | `03_STUDY_INVENTORY.csv` | DIFFERENT | shape (79, 7) vs (78, 7); pmid only-frozen=['27569025'] only-regenerated=[] |
| offline | `05_DRUG_SENSORY_EVIDENCE.csv` | DIFFERENT | shape (17, 14) vs (17, 14); pmid only-frozen=[] only-regenerated=[]; differing cells=5 |

## K. 再実行方法

```bash
cd chemosensory_medication_sensory
python3 dry_reproduction/run_dry_reproduction_audit.py \
  --live-dir <scripts 01-03 を実行した別チェックアウト> \
  --handoff-zip CHEMOSENSORY_TOMMO_LEGACY_SESSION_HANDOFF.zip --render
python3 -m pytest tests/ -q
```

依存: python3, pandas, numpy, scipy, statsmodels, matplotlib, pytest。PYTHONHASHSEED=0、MPLBACKEND=Agg、プロキシ遮断で実行。
