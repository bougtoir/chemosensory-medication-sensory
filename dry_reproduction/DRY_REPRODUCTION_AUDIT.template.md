# DRY_REPRODUCTION_AUDIT

旧handoffのdry解析（evidence synthesis → prediction freeze → negative controls → gate）を、保存済みの検索出力・生データから独立に再実行し、凍結済み成果物と照合した記録。本文書は `dry_reproduction/run_dry_reproduction_audit.py --render` により `dry_reproduction/results/` の機械可読出力（`dry_reproduction_checks.csv`, `file_comparison.csv`, `summary.json`）から生成される。数値の手書きは無い。

**参加者レベルToMMoデータは一切使用していない**（§E）。ToMMo関連で読んだのは公開調査票メタデータ（`data/raw/tommo_public/`, {{tommo_public_ok}}/{{tommo_public_rows}} ハッシュ一致）のみ。

## 判定の要約

| 項目 | 結果 |
|---|---|
| checks 総数 | {{n_checks}} |
| status 内訳 | {{status_counts}} |
| オフライン再実行（scripts 04–10）exit code | {{offline_returncodes}} |
| オフライン再生成ターゲット | {{offline_exact}}/{{offline_targets}} byte/semantic一致; 不一致: {{offline_nonexact}} |
| 不一致の原因 | 凍結search poolに無いanchor PMID 27569025（§C）。これを加えた再実行では 03={{aug_inventory}}, 05={{aug_drug}} |
| evidence score P01–P12 再計算 | 不一致: {{score_recomputed_mismatch}}（13_v2_FINAL との不一致: {{score_final_mismatch}}; tier不一致: {{tier_mismatch}}） |
| 再計算スコア | {{score_table}} |
| negative controls N01–N12 | ID一致 {{nc_ids_equal}}; gene不一致 {{nc_gene_mismatch}}; drug不一致 {{nc_drug_mismatch}}; class label の改称: {{nc_class_relabels}} |
| gate（score≥9の件数） | 36記載 {{gate_36_stated}} → 再計算 {{gate_hi_n}}（{{gate_hi_ids}}）; 61 errata の訂正値 {{gate_61_corrected}} |
| 予測階層 | 62/23/13_v2_FINAL: {{hier_62_confirmatory_status}}; 82表/README/LOCK_STATUS: {{hier_82_F_PRIMARY}}（矛盾: {{hier_inconsistent_sources}}） |
| parser v{{parser_version}} gold corpus | {{parser_acc}}; 失敗: {{parser_fail_strings}}; 凍結出力と意味的一致 {{parser_semantic_equal}} |
| 実ToMMo文字列 parser gate（92） | NOT_RUN（受領前・参加者データ禁止のため） |
| pytest（凍結パッケージ） | {{pytest_frozen}} |
| pytest（オフライン再生成ツリー） | {{pytest_regen}}（{{pytest_regen_failed}}） |
| live再取得から13_v2_FINAL等の再生成 | {{live_pred_status}} |

結論: locked prediction table（`13_LOCKED_PREDICTIONS_v2_FINAL.csv`）、evidence score、negative-control表、gate の定量部分は、参加者レベルデータなしに再生成できた。完全なbyte再現を妨げたのは (1) 凍結search poolの組立て手順（seed/anchor層、行順）がどのスクリプトにも記述されていないこと、(2) anchor XML の台帳不備、の2点で、科学的出力（スコア・予測・対照）には影響しない。文書間の不一致（階層、contrast定義、件数記載、ラベル）は §G に列挙し、どれも黙って正規化していない。

## A. 入力とマニフェスト

- `HANDOFF_MANIFEST.csv`: {{manifest_ok}}/{{manifest_rows}} SHA-256一致、不一致 {{manifest_bad}}、欠落 {{manifest_missing}}（{{manifest_missing_files}}）。
- `60_PREOPENING_INPUT_MANIFEST.md`: 一致 {{m60_match}}/{{m60_rows}}、後続世代により置換 {{m60_superseded}}、説明不能 {{m60_unexplained}}（{{m60_unexplained_files}}）。60は13_v2_FINALを{{m60_stated_rows}}行と記載するが実ファイルは{{v2_rows}}行（ハッシュは一致; 記載誤り）。
- `97_PREOPENING_AMENDMENT_MANIFEST.md`: {{m97_match}}/{{m97_rows}} 一致。
- 添付ZIP: {{zip_files}} files、gitブランチと共通 {{zip_common}}、内容不一致 {{zip_mismatch}}。ZIPに無いディレクトリ: {{zip_only_repo_dirs}}。ZIPは文書レベルのhandoffであり、スクリプト・テスト・生データはgitブランチ `devin/1791087629-chemosensory-med-sensory` 側にのみ存在する（ZIP単独では再現不能）。

## B. 生データ（凍結スナップショット）

| source | 台帳行 | 一致 | 備考 |
|---|---|---|---|
| PubMed stage-1 query XML | {{pubmed_R1_rows}} | {{pubmed_R1_ok}} | schema異常行: {{pubmed_R1_schema_rows}} |
| PubMed seed/anchor XML | {{pubmed_R2_rows}} | {{pubmed_R2_ok}} | schema異常行: {{pubmed_R2_schema_rows}}（`seed_ledger.csv` に別スキーマで追記）; 台帳に無いXML: {{pubmed_unledgered}} |
| BitterDB receptor pages | {{bitterdb_ledger_rows}} | {{bitterdb_ledger_ok}} | script再パースと台帳一致 {{bitterdb_ledger_script_match}} |
| PubChem JSON | {{pubchem_rows}} | {{pubchem_sha_ok}} | property一致 {{pubchem_props_ok}}; 取得失敗（凍結時点から）: {{pubchem_fail}} |

凍結原本（`data/raw/`）は読み取りのみで、上書きしていない。

## C. PubMed search pool

- stage-1 XML の和集合 {{pool_stage1}} PMID、台帳記載XML（stage-1＋seed）{{pool_ledgered}}、全保存XML {{pool_all_xml}}、凍結 `evidence/search_pool.csv` {{pool_frozen}}。
- 全保存XML vs 凍結pool: 凍結のみ {{pool_all_only_frozen}}、XMLのみ {{pool_all_only_xml}}。台帳記載XMLのみでは凍結のみ {{pool_only_frozen}} 件（`SEED_extra_anchors.xml` が台帳外のため）。
- anchor PMID 27569025 は `SEED_27569025.xml` にあり、凍結 `03_STUDY_INVENTORY.csv` には含まれるが凍結 search pool には含まれない（{{pool_anchor_in_frozen}}）。凍結poolで04を再実行すると03が78行（凍結79行）になり、05の5セルが変わる。27569025を加えると両者とも凍結値と一致する。
- 再現は集合レベル。凍結poolの行順・行メタデータの組立て手順はどのスクリプトにも記述されていない。

## D. BitterDB / PubChem

- BitterDB: 全236ページを script 02 のロジックで再パースすると {{bitterdb_naive_edges}} edges（非ヒト/表記揺れ受容体を含む）。凍結 `evidence/bitterdb_human_receptors.csv`（{{bitterdb_human_ids}} receptor IDs）で絞ると {{bitterdb_filtered_edges}} edges で凍結 {{bitterdb_frozen_edges}} と集合一致（{{bitterdb_edge_sets_equal}}）。ligandを持つ受容体 {{bitterdb_receptors_with_ligands}}。
- 凍結 compound 表は human 絞込み前の全ページ由来（再導出 {{bitterdb_compounds_regen}} = 凍結 {{bitterdb_compounds_frozen}}; human-only なら {{bitterdb_compounds_human_only}}）。この非対称は凍結時の仕様であり、downstream（11/23/13）の再生成結果は一致。
- PubChem: {{pubchem_json}} JSON、property・SHA-256とも全一致。

## E. 参加者レベルデータの除外

- 追跡対象の data ルート: {{excl_data_roots}}。
- 参加者レベル形式の拡張子（VCF/BGEN/PLINK/parquet 等）: {{excl_bad_ext}}。
- オフライン再実行はプロキシを不通アドレスに向けた隔離コピーで実行し、ネットワークスクリプト（01–03）を含まない（違反: {{excl_network_in_offline}}）。
- 本監査は genotype × medication の関連推定、genotype 頻度、medication 件数のいずれも計算していない。

## F. live 再取得（凍結入力の再現とは別物）

- 2026-10-04 に scripts 01–03 を別チェックアウトで未改変のまま実行し、新しいスナップショットとして `data/raw_live_20261004/`（`LEDGER.csv`: URL、クエリ、取得UTC、サイズ、SHA-256、利用条件。PubMed XML は gzip、展開後SHA-256も記録）に保存した。凍結 `data/raw/` は上書きしていない。
- PubMed stage-1: {{live_pool}} PMID（凍結比 +{{live_pool_vs_stage1_added}} / −{{live_pool_vs_stage1_removed}}）= SOURCE_DRIFT（索引の増減）。seed/anchor層は01が再取得しないため凍結XMLを使用。
- BitterDB: {{live_edges}} edges（human 絞込み後 {{live_edges_human}}; 凍結比 +{{live_edges_added}} / −{{live_edges_removed}}）。
- PubChem: 成功 {{live_pubchem_ok}}、値変化 {{live_pubchem_changed}}、新規 {{live_pubchem_new}}。
- live 入力からの再生成: {{live_pred_status}}。
- 公開ミラーには第三者の生レコードを出さない（`data` は sync 除外）。

## G. 不一致一覧（黙って正規化しない）

1. **予測階層**: `62`（82 rule 1 で正）・`23`・`13_v2_FINAL` は primary = P01, P02, P05。`82` 表・`README_HANDOFF.md`・`LOCK_STATUS.md` は F-PRIMARY = P01, P02, P05, P10。`91` は P10 を secondary とする（{{hier_91_P10_status}}）。82 rule 1 により 62 を正とし、他は記載誤りとして reconciliation（HI1）で扱う。
2. **gate件数**: `36` は score≥9 を {{gate_36_stated}} 件と記載、再計算 {{gate_hi_n}} 件。`61` errata が {{gate_61_corrected}} に訂正済みで、予測パネル自体は不変。
3. **contrast定義**: C1–C5 の定義が `25`（script 09出力）と `72` で {{contrast_def_mismatch_n}}/{{contrast_n}} 件異なる: {{contrast_def_mismatch}}。
4. **negative-control class label**: {{nc_class_relabels}}（36本文: {{nc_36_text}}）。ID・gene・drugは一致。
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

{{RESULTS_TABLE}}

## J. ファイル比較

{{FILE_TABLE}}

## K. 再実行方法

```bash
cd chemosensory_medication_sensory
python3 dry_reproduction/run_dry_reproduction_audit.py \
  --live-dir <scripts 01-03 を実行した別チェックアウト> \
  --handoff-zip CHEMOSENSORY_TOMMO_LEGACY_SESSION_HANDOFF.zip --render
python3 -m pytest tests/ -q
```

依存: python3, pandas, numpy, scipy, statsmodels, matplotlib, pytest。PYTHONHASHSEED=0、MPLBACKEND=Agg、プロキシ遮断で実行。
