#!/usr/bin/env python3
"""Deterministic Japanese medication-string parser.

Input: free-text medication records (brand/generic names with Japanese
formulation suffixes, e.g. "アダラートCR錠 20mg", "メルカゾール錠5mg").
Output fields per 71 spec: raw_text retained; normalized fields +
formulation/route/oral-sensory-exposure/taste-masking classification
per the frozen dictionaries (66/67/68).

No genotype or outcome data anywhere near this module.
"""
import re
import unicodedata

VERSION = "1.0.0"

# ------------------------------------------------------------------
# normalization
# ------------------------------------------------------------------
def normalize(text: str) -> str:
    t = unicodedata.normalize("NFKC", str(text))
    # common long-vowel / katakana variants
    t = t.replace("ｰ", "ー").replace("‐", "-").replace("−", "-")
    t = re.sub(r"[（(]", "(", t)
    t = re.sub(r"[）)]", ")", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

# ------------------------------------------------------------------
# formulation dictionary (66_FORMULATION_DICTIONARY_FINAL.csv mirror)
# ------------------------------------------------------------------
FORMULATION_RULES = [
    # (regex, formulation, release_type, route_hint)
    (r"OD錠|口腔内崩壊錠|オーラリー|口腔内速崩", "OD tablet", "IR", "oral"),
    (r"腸溶錠|腸溶性|EC錠", "enteric-coated tablet", "EC", "oral"),
    (r"CR錠|徐放錠|持続性|SR錠|L錠|R錠", "controlled-release tablet", "CR", "oral"),
    (r"フィルムコーティング錠|FC錠|コーティング錠", "film-coated tablet", "IR", "oral"),
    (r"糖衣錠|糖衣", "sugar-coated tablet", "IR", "oral"),
    (r"チュアブル錠|チュアブル", "chewable tablet", "IR", "oral"),
    (r"舌下錠|舌下|バッカル", "sublingual/buccal", "IR", "sublingual"),
    (r"トローチ", "lozenge", "IR", "oral"),
    (r"ドライシロップ", "dry syrup", "IR", "oral"),
    (r"シロップ|内服液|内用液|内服薬|液剤|エリキシル|懸濁液|懸濁用", "syrup/suspension", "IR", "oral"),
    (r"細粒", "fine granules", "IR", "oral"),
    (r"顆粒", "granules", "IR", "oral"),
    (r"散剤|散", "powder", "IR", "oral"),
    (r"カプセル", "capsule", "IR", "oral"),
    (r"錠剤|錠", "tablet (unspecified coating)", "IR", "oral"),
    (r"貼付|パップ|テープ|パッチ|TTS", "transdermal", "TD", "transdermal"),
    (r"吸入|インヘラー|エアゾール|点鼻", "inhaled/intranasal", "IR", "inhaled"),
    (r"点眼", "ophthalmic", "IR", "topical"),
    (r"坐剤|座薬", "rectal", "IR", "rectal"),
    (r"注射|注", "injection", "IV", "parenteral"),
    (r"軟膏|クリーム|外用|ローション|ゲル", "topical", "IR", "topical"),
]

ROUTE_MAP = {
    "oral solution": "oral", "syrup/suspension": "oral", "dry syrup": "oral",
    "powder": "oral", "fine granules": "oral", "granules": "oral",
    "chewable tablet": "oral", "OD tablet": "oral",
    "tablet (unspecified coating)": "oral", "film-coated tablet": "oral",
    "sugar-coated tablet": "oral", "enteric-coated tablet": "oral",
    "controlled-release tablet": "oral", "capsule": "oral",
    "lozenge": "oral", "sublingual/buccal": "sublingual",
    "inhaled/intranasal": "inhaled", "transdermal": "transdermal",
    "topical": "topical", "ophthalmic": "topical", "rectal": "rectal",
    "injection": "parenteral", "unknown": "unknown",
}

# oral sensory exposure classes (67 freeze)
EXPOSURE_CLASS = {
    "syrup/suspension": 3, "dry syrup": 3, "oral solution": 3,
    "powder": 3, "fine granules": 3, "granules": 3,
    "chewable tablet": 3, "lozenge": 3,
    "OD tablet": 2, "tablet (unspecified coating)": 2,
    "sublingual/buccal": 2,
    "film-coated tablet": 1, "sugar-coated tablet": 1,
    "capsule": 1, "enteric-coated tablet": 1,
    "controlled-release tablet": 1,
    "inhaled/intranasal": 1,  # flagged: partial oropharyngeal exposure
    "transdermal": 0, "topical": 0, "ophthalmic": 0, "rectal": 0,
    "injection": 0, "unknown": None,
}

MASKING_CLASS = {
    "syrup/suspension": "UNMASKED", "dry syrup": "UNMASKED",
    "oral solution": "UNMASKED", "powder": "UNMASKED",
    "fine granules": "UNMASKED", "granules": "UNMASKED",
    "chewable tablet": "UNMASKED", "lozenge": "UNMASKED",
    "OD tablet": "UNMASKED", "tablet (unspecified coating)": "UNKNOWN",
    "sublingual/buccal": "UNMASKED",
    "film-coated tablet": "PARTIALLY MASKED",
    "sugar-coated tablet": "STRONGLY MASKED",
    "capsule": "STRONGLY MASKED",
    "enteric-coated tablet": "STRONGLY MASKED",
    "controlled-release tablet": "PARTIALLY MASKED",
    "inhaled/intranasal": "PARTIALLY MASKED",
    "transdermal": "STRONGLY MASKED", "topical": "STRONGLY MASKED",
    "ophthalmic": "STRONGLY MASKED", "rectal": "STRONGLY MASKED",
    "injection": "STRONGLY MASKED", "unknown": "UNKNOWN",
}

STRENGTH_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*(mg|μg|ug|mcg|g|mL|ml|%|単位|IU|錠|本|包|枚|吸入|噴霧)", re.I)

# brands whose formulation is inherent (no suffix on label)
BRAND_FORMULATION = {
    "ユニフィル": "controlled-release tablet",
    "ニトロダーム": "transdermal",
    "フェントス": "transdermal",
}

# known brand->generic seed map (extendable, public formulary knowledge)
BRAND_TO_GENERIC = {
    "アダラート": "nifedipine", "メルカゾール": "thiamazole (methimazole)",
    "プロパジール": "propylthiouracil", "チウラジール": "propylthiouracil",
    "ジスロマック": "azithromycin", "クラビット": "levofloxacin",
    "タリビット": "ofloxacin", "オゼックス": "tosufloxacin",
    "サワシリン": "amoxicillin", "ケフラール": "cefalexin",
    "フロモックス": "cefcapene", "セフゾン": "cefdinir",
    "オラセフ": "cefalexin", "メイアクト": "cefditoren",
    "ミノマイシン": "minocycline", "ビブラマイシン": "doxycycline",
    "エリスロシン": "erythromycin", "クラリス": "clarithromycin",
    "クラリシッド": "clarithromycin", "ダラシン": "clindamycin",
    "ポニカ": "ibuprofen", "カロナール": "acetaminophen",
    "ロキソニン": "loxoprofen", "セルセプト": "mycophenolate",
    "ブルフェン": "ibuprofen", "イブ": "ibuprofen",
    "ポララミン": "chlorpheniramine", "プールワン": "d-chlorpheniramine",
    "ペリアクチン": "cyproheptadine", "アレジオン": "epinastine",
    "アレグラ": "fexofenadine", "ザジテン": "ketotifen",
    "ムコダイン": "carbocisteine", "テオドール": "theophylline",
    "テオフィル": "theophylline", "ユニフィル": "theophylline",
    "キプレス": "montelukast", "シングレア": "montelukast",
    "ノイロトロピン": "neurotropin", "リリカ": "pregabalin",
    "アスピリン": "aspirin", "バイアスピリン": "aspirin",
    "タケキャブ": "vonoprazan", "ネキシウム": "esomeprazole",
    "オメプラゾール": "omeprazole", "オメプラール": "omeprazole",
    "パリエット": "rabeprazole", "ガスター": "famotidine",
    "ザンタック": "ranitidine", "アシノン": "nizatidine",
    "マイスリー": "zolpidem", "ルネスタ": "eszopiclone",
    "デエビゴ": "lemborexant", "ベルソムラ": "suvorexant",
    "ジェイゾロフト": "sertraline", "パキシル": "paroxetine",
    "レクサプロ": "escitalopram", "サインバルタ": "duloxetine",
    "ヒルナミン": "chlorpromazine", "セレネース": "haloperidol",
    "ジプレキサ": "olanzapine", "リスパダール": "risperidone",
    "エビリファイ": "aripiprazole", "セロクエル": "quetiapine",
    "ノバスカー": "amlodipine", "ノルバスク": "amlodipine",
    "ブロプレス": "candesartan", "ディオバン": "valsartan",
    "ニューロタン": "losartan", "オルメテック": "olmesartan",
    "メインテート": "bisoprolol", "テノーミン": "atenolol",
    "インデラル": "propranolol", "セレクトール": "celiprolol",
    "ワーファリン": "warfarin", "プラザキサ": "dabigatran",
    "イグザレルト": "rivaroxaban", "エリキュース": "apixaban",
    "リクシアナ": "edoxaban", "プレタール": "cilostazol",
    "リピトール": "atorvastatin", "クレストール": "rosuvastatin",
    "リバロ": "pitavastatin", "メバロチン": "pravastatin",
    "ゼチーア": "ezetimibe", "アクトス": "pioglitazone",
    "メトグルコ": "metformin", "グルコバイ": "metformin",
    "ジャヌビア": "sitagliptin", "スイニー": "teneligliptin",
    "フォシーガ": "dapagliflozin", "ジャディアンス": "empagliflozin",
    "ソセオ": "insulin", "ノボラピッド": "insulin aspart",
    "ランタス": "insulin glargine", "ヒューマリン": "insulin",
    "フェキソフェナジン": "fexofenadine", "アザレア": "tranexamic acid",
    "トラネキサム": "tranexamic acid", "カルバブ": "potassium chloride",
    "グルコンサンK": "potassium chloride", "K-ジスペンシング": "potassium chloride",
    "ボルタレン": "diclofenac", "セレコックス": "celecoxib",
    "モービック": "meloxicam", "エテルネブ": "ethambutol",
    "イスコチン": "isoniazid", "アリセプト": "donepezil",
    "メニエール": "isosorbide", "ニトロダーム": "nitroglycerin",
    "フランドル": "isosorbide", "アンタベース": "disulfiram",
    "ビーエフ": "as needed", "バイアグラ": "sildenafil",
    "ケイツー": "vitamin K", "メチコバール": "mecobalamin",
    "フェロミア": "iron", "インシード": "iron",
    "カルタ": "diltiazem", "ヘルベッサー": "diltiazem",
    "パセトシン": "amoxicillin", "プレドニン": "prednisolone",
    "デカドロン": "dexamethasone", "ザイロリック": "allopurinol",
    "トラムール": "tramadol", "トラマール": "tramadol",
    "デベルザ": "meclizine", "トラベルミン": "dimenhydrinate",
    "ドンペリドン": "domperidone", "ナウゼリン": "domperidone",
    "パタノール": "olopatadine", "フェントス": "fentanyl",
    "デュロテップ": "fentanyl", "ビタミン": "vitamin",
    "オメドール": "donepezil", "メニエール": "isosorbide",
    "ガスター": "famotidine",
    "ワソラン": "verapamil", "コニール": "benidipine",
    "カルスロット": "manidipine", "アテレック": "cilnidipine",
    "デタントール": "bunazosin", "ミニプレス": "prazosin",
    "ハルナール": "tamsulosin", "ユリーフ": "silodosin",
    "フリバス": "naftopidil", "ザルティア": "tadalafil",
    "デュタステリド": "dutasteride", "アボルブ": "dutasteride",
    "プロペシア": "finasteride", "フィナステリド": "finasteride",
}

GENERIC_NAMES = {
    "methimazole","thiamazole","propylthiouracil","ofloxacin","levofloxacin",
    "ciprofloxacin","quinine","quinidine","chloramphenicol","clindamycin",
    "erythromycin","clarithromycin","azithromycin","amoxicillin","ampicillin",
    "cefalexin","cefdinir","acetaminophen","ibuprofen","loxoprofen",
    "diclofenac","celecoxib","theophylline","caffeine","chlorpheniramine",
    "fexofenadine","loratadine","cetirizine","diphenhydramine","promethazine",
    "famotidine","ranitidine","omeprazole","esomeprazole","rabeprazole",
    "vonoprazan","nifedipine","amlodipine","diltiazem","verapamil",
    "atenolol","bisoprolol","propranolol","losartan","valsartan",
    "candesartan","olmesartan","warfarin","dabigatran","rivaroxaban",
    "apixaban","atorvastatin","rosuvastatin","metformin","sitagliptin",
    "insulin","colchicine","dapsone","griseofulvin","haloperidol",
    "dextromethorphan","potassium chloride","carisoprodol","finasteride",
    "dutasteride","thiamine","hydrocortisone","prednisolone","prednisone",
    "dexamethasone","allopurinol","tramadol","codeine","morphine",
    "montelukast","ketotifen","epinastine","carbocisteine","doxycycline",
    "minocycline","isoniazid","ethambutol","rifampicin","pyrazinamide",
    "hydroxychloroquine","chloroquine","meclizine","dimenhydrinate",
    "carbimazole","goitrin","saccharin","acesulfame","sucralose",
}

def parse(raw: str) -> dict:
    t = normalize(raw)
    # strength / unit
    strengths = STRENGTH_RE.findall(t)
    strength = " ".join(f"{a}{b}" for a, b in strengths) if strengths else ""
    # strip strength/number tokens and %, company parens for name core
    core = STRENGTH_RE.sub(" ", t)
    core = re.sub(r"\(.*?\)", "", core)
    core = re.sub(r"\d+(?:\.\d+)?", "", core)
    core = re.sub(r"製薬|ファーマ|薬品|株式会社|＜.*?＞", "", core).strip()
    # formulation
    formulation = "unknown"; release = "IR"; route_hint = "oral"
    # brand-inherent formulation takes precedence (e.g. ユニフィル is always CR)
    brand_form = next((f for b, f in BRAND_FORMULATION.items()
                       if core.startswith(b)), None)
    for rx, form, rel, rt in FORMULATION_RULES:
        if brand_form is None and re.search(rx, core):
            formulation = form; release = rel; route_hint = rt
            core_name = re.sub(rx, "", core).strip()
            break
    else:
        core_name = core
    if brand_form is not None:
        formulation = brand_form
        for rx, form, rel, rt in FORMULATION_RULES:
            if formulation == form:
                release = rel; route_hint = rt
        core_name = re.sub(r"錠剤|錠|LA|SR|徐放|持続|腸溶|配合|OD|D|S$", "", core).strip()
    # strength suffix eaten the formulation cue (e.g. ガスター10錠)
    if formulation == "unknown" and re.search(r"錠", t):
        formulation = "tablet (unspecified coating)"
        route_hint = "oral"
    core_name = core_name.strip()
    # brand / generic resolution
    generic = ""
    brand = core_name
    for b, g in sorted(BRAND_TO_GENERIC.items(), key=lambda kv: -len(kv[0])):
        if core_name.startswith(b):
            generic = g; brand = b; break
    if not generic:
        low = core_name.lower().replace("錠","").strip()
        for g in GENERIC_NAMES:
            if low == g or low.startswith(g):
                generic = g; break
    conf = 0.9 if generic else (0.6 if formulation != "unknown" else 0.3)
    review = "YES" if (not generic or formulation == "unknown") else ""
    return dict(
        raw_text=raw, normalized_text=t,
        brand_name=brand, generic_name=generic, active_ingredient=generic,
        strength=strength, unit="", dose="",
        ATC_code="", drug_class="",
        formulation=formulation, release_type=release,
        route=ROUTE_MAP.get(formulation, route_hint),
        oral_sensory_exposure=EXPOSURE_CLASS.get(formulation),
        taste_masking=MASKING_CLASS.get(formulation, "UNKNOWN"),
        combination_drug="YES" if ("配合" in t or "/" in core_name or "合" in core_name[-2:]) else "",
        OTC_flag="", supplement_flag="",
        confidence=conf, manual_review_flag=review,
    )


if __name__ == "__main__":
    import csv, sys
    r = csv.reader(sys.stdin)
    w = None
    for row in r:
        out = parse(row[0])
        if w is None:
            w = csv.DictWriter(sys.stdout, fieldnames=list(out))
            w.writeheader()
        w.writerow(out)
