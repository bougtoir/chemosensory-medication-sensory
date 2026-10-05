# CHEMOSENSORY / ToMMo — legacy session handoff

## 1. 中心仮説
古代の化学感受性（苦味・甘味・刺激）遺伝子多型が、現代医薬品の
orosensory 曝露パターンを通じて、集団レベルの服薬行動（報告された
医薬品曝露・剤形選択・cross-wave 変化）を予測するか。
S1=感覚表現型（このコホートでは未測定・推論のみ）、S2=行動、
S3=薬理学的感受性（探索のみ）。

## 2. 時系列
1. **dry evidence（Stage 0–2）**: 79研究・BitterDB・PubChem・
   エビデンスグラフ → 凍結予測v1 → CONDITIONAL GO（docs/17）
2. **prediction expansion + feasibility（21–36, 13_v2）**: 方向予測12・
   陰性対照12・コントラスト5、ToMMo公開メタ監査 →
   CONDITIONAL GO TO PRIMARY VALIDATION（36）
3. **pre-opening lock（60–90）**: パーサー凍結・観測可能性・SAP・
   解釈行列 → OPEN WITH RESTRICTIONS（89）
4. **amendments（91–99）**: P01/P10分離・実文字列QCゲート・
   形式勾配検定・連続較正 → 判定v2 OPEN PRIMARY DATA WITH
   RESTRICTIONS（98）

## 3. 現行最新版（これを読む）
- 判定: `98_FINAL_OPENING_DECISION_V2.md`（89はsuperseded、監査用に保持）
- ハンドオフ: `99_PRIMARY_VALIDATION_HANDOFF_V2.md`
- 予測パネル: `13_LOCKED_PREDICTIONS_v2_FINAL.csv`
- パーサー版: `94_MEDICATION_PARSER_FINAL_VERSION.txt`（v1.0.0、
  実文字列QC保留）

## 4. immutable / frozen
- `13_LOCKED_PREDICTIONS_v2_FINAL.csv` および 60–90番台・91–99番台の
  全freezeファイル：修正は `88_AMENDMENT_POLICY_FINAL.md` のみ経由。
  frozen入力のSHA-256は `60` と `97` に記録。

## 5. Primary confirmatory
- F-PRIMARY: P01, P02, P05, P10（`62`）。各予測は独立評価。
- F-GRADIENT: G×E 1自由度交互作用検定（`95`）— 一般機序の主検定。

## 6. Secondary confirmatory
- F-SECONDARY: 残りの方向予測（BH-FDR q=0.10）
- F-CONTRAST: C1–C5 剤形・経路コントラスト（Holm）
- 副次: カテゴリEXモデル、順序制限検定、cross-wave解析、S1–S10感度

## 7. Negative control
- N01–N12（`79`）：経路・マスキング・受容体ミスマッチ・行動対照。
  結果を見て差し替えない。

## 8. Exploratory
- S3（薬理学的感受性）関連、`82` F-EXPLORATORY に属するすべて。
  無補正p＋exploratoryラベルのみ。

## 9. 変更してはいけない項目（`88`, `LOCK_STATUS.md`）
- 予測の追加・削除・順序変更、閾値の引き下げ、対照の差し替え、
  禁止アウトカム用語（`78`）、`85` 解釈パターンの事後変更、
  P01をP10で救済すること、実文字列QCゲートのスキップ。

## 10. 新規セッションの推奨読了順
1. `99_PRIMARY_VALIDATION_HANDOFF_V2.md`
2. `98_FINAL_OPENING_DECISION_V2.md`
3. `LOCK_STATUS.md`（本ZIP内）
4. `13_LOCKED_PREDICTIONS_v2_FINAL.csv` + `62` + `72`
5. `83` + `82` + `85` + `95` + `96`
6. `91`–`96`（修正履歴）、`60`/`97`（ハッシュ台帳）
7. 必要に応じてdry証拠（03–12, 21–36, docs/17）

## 11. ToMMo participant-level dataは本ZIPに含まれない
個票データは一切含まれない。含まれるToMMo関連物は公開質問票由来の
メタデータ監査と、印刷例文字列のみ（93）。

## 12. ToMMo実データはオフライン環境でのみ解析
アクセス申請後、genotype-blindの規定手順（`87`, `99` §opening order）
に従って実行すること。本ZIPの内容を成果物と見なして改変しない。
