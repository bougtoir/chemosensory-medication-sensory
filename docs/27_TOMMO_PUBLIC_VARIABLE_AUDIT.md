# 27 — ToMMo Public Variable Audit (public documents only)

Sources inspected (all public, no application required):

1. Questionnaire page — https://www.megabank.tohoku.ac.jp/researchers/biobankcohort/questionnaire
   (item lists + direct PDF links; retrieved 2026-10-04 UTC)
2. Baseline lifestyle questionnaire v3 PDF —
   `dbtmm.megabank.tohoku.ac.jp/doc/cohort_study/baseline_study/questionnaire/baseline_lifestyle_questionnaire_v3.pdf`
   (raw persisted: `data/raw/tommo_public/`)
3. Phase-2 lifestyle questionnaire v4 PDF (same dir, persisted)
4. Baseline & phase-2 food frequency questionnaire PDFs (persisted)
5. dbTMM front page + release notes — https://dbtmm.megabank.tohoku.ac.jp/
   (public catalog; states release 2.3.4 added 服薬情報 / 医科レセプト情報
   for the health-checkup sub-cohort)
6. Specimen & data collection page — https://www.megabank.tohoku.ac.jp/english/sample/

No participant-level data was accessed. All findings below cite the PDFs.

## Medication section (調査票「生活」【５】薬・サプリメント・健康食品)

- **① Screening:** "過去２週間に、お薬・サプリメント・健康食品を使用したことが
  ありますか" — includes 貼付薬/塗り薬/吸入薬 explicitly; OTC/drugstore items
  explicitly included. (CONFIRMED, waves 1 and 2.)
- **② Free-text table per drug:** columns = 商品名や成分等 / 入手方法
  (処方箋 or それ以外) / 使用期間 (year·month + duration) / 使用頻度
  (per week·day, incl. 頓用 PRN) / 1回の使用量 (units incl.
  錠・本・包, ml・mg, 枚・吸入, 噴霧・単位).
- **Worked example printed on the form:** 「アダラート CR 錠 20mg」—
  i.e., brand names are captured WITH formulation suffixes.
- お薬手帳 (medication notebook) copies may be attached by participants.
- Overflow rows on an additional page (rows numbered up to ㉖ visible).

Implication: exact product name, dose, frequency, source (Rx vs OTC),
start period, and duration are CONFIRMED; **formulation and route are
LIKELY — encoded inside brand names and unit categories rather than a
dedicated field** (e.g. "○○細粒/シロップ/OD錠/CR錠/貼付剤" parseable
from free text).

## Dietary (調査票「食」FFQ, waves 1–2)

Confirmed direct items include: コーヒー（缶コーヒー以外）, 紅茶,
ウーロン茶, 緑茶類, 野菜類/果物, 魚介類/肉類, みそ汁, plus a sugar-use
item ("紅茶やコーヒーを飲む人は、砂糖やミルクを入れますか？").
Alcohol: type-by-type frequency + amount, flushing question
(「酒を飲むと、顔が赤くなりますか」), 酒の強さ (self-rated strength).
Smoking: status/history items. No dedicated taste-preference or
bitter-food items observed.

## Sensory/physiology subcohort

Community Support Center participants (~26K) underwent physiological
exams (audiometry, vision, oral health, carotid US, bone density, ECG,
respiratory). **No publicly documented taste/olfactory phenotype or
sensory-receptor addon** — treat as LIKELY UNAVAILABLE.

## Claims linkage

dbTMM release notes state 服薬情報・医科レセプト情報 were added in
v2.3.4 for the health-checkup sub-cohort — availability is via the
restricted dbTMM catalog; usable only through a proper application, not
assumed by this plan.
