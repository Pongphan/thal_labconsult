from __future__ import annotations

import pandas as pd
import streamlit as st
from thalab.core import DEFAULT_THRESHOLDS, SCREENING_COLUMNS, analyze_dataframe, analyze_screening, example_screening_dataframe
from thalab.ml import ml_feature_matrix, phenotype_similarity
from thalab.reporting import screening_report_markdown, to_json_bytes
from thalab.styles import clinical_box, current_language, disclaimer, hero, inject_css, metric_card, pills, production_footer, section, top_navigation
from thalab.viz import batch_mcv_hba2_scatter, batch_risk_distribution, cbc_reference_bars, diagnostic_waterfall, hb_fraction_donut, hplc_chromatogram, mcv_hba2_quadrant, population_sankey, reflex_sankey, risk_gauge, score_heatmap, score_radar


OPTION_LABELS_TH = {
    "Single patient consult": "ปรึกษารายบุคคล",
    "Batch CSV dashboard": "แดชบอร์ด CSV หลายราย",
    "Female": "หญิง",
    "Male": "ชาย",
    "Other/Not specified": "อื่นๆ / ไม่ระบุ",
    "Negative": "ลบ",
    "Positive": "บวก",
    "HPLC": "HPLC",
    "CZE": "CZE",
}


RESULT_TEXT_TH = {
    "Critical review": "ต้องทบทวนเร่งด่วน",
    "High": "ความเสี่ยงสูง",
    "Moderate": "ความเสี่ยงปานกลาง",
    "Low / inconclusive": "ความเสี่ยงต่ำ / ยังสรุปไม่ได้",
    "Suspected α-thalassemia / HbH Disease Spectrum": "สงสัยกลุ่ม α-thalassemia / HbH disease",
    "Suspected Hb E / β-globin structural variant pattern": "สงสัย Hb E / ความผิดปกติของ β-globin",
    "Suspected Beta-Thalassemia Trait with or without alpha-thalassemia": "สงสัยพาหะ β-thalassemia ร่วม/ไม่ร่วม α-thalassemia",
    "Suspected Beta-Thalassemia or HPFH": "สงสัย β-thalassemia หรือ HPFH",
    "Normal Hb Typing Pattern (AA)": "รูปแบบ Hb typing ปกติ (AA)",
    "β-thalassemia trait / HBB variant pattern": "รูปแบบพาหะ β-thalassemia / HBB variant",
    "α-thalassemia carrier / HbH-spectrum pattern": "รูปแบบพาหะ α-thalassemia / HbH spectrum",
    "HbE / β-globin structural variant pattern": "รูปแบบ HbE / β-globin structural variant",
    "Iron deficiency or mixed microcytosis pattern": "รูปแบบขาดธาตุเหล็กหรือ microcytosis แบบผสม",
}


def tx(en: str, th: str | None = None) -> str:
    return th if current_language() == "th" and th is not None else en


def option_label(option: str) -> str:
    return tx(option, OPTION_LABELS_TH.get(option, option))


def clinical_text(text: str) -> str:
    if current_language() != "th":
        return text
    return RESULT_TEXT_TH.get(text, text)


def safe_float(row: dict, key: str, default: float = float("nan")) -> float:
    try:
        value = row.get(key, default)
        if pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def is_positive(row: dict, key: str) -> bool:
    return str(row.get(key, "")).strip().lower() in {"positive", "pos", "+", "detected", "present", "true", "1"}


def is_known(value: float) -> bool:
    return not pd.isna(value)


def add_differential(
    items: list[dict[str, str]],
    condition: str,
    condition_th: str,
    likelihood: str,
    likelihood_th: str,
    pattern: str,
    pattern_th: str,
    next_step: str,
    next_step_th: str,
    level: str,
) -> None:
    items.append(
        {
            "condition": condition,
            "condition_th": condition_th,
            "likelihood": likelihood,
            "likelihood_th": likelihood_th,
            "pattern": pattern,
            "pattern_th": pattern_th,
            "next_step": next_step,
            "next_step_th": next_step_th,
            "level": level,
        }
    )


def hematology_differentials(row: dict, thresholds: dict[str, float]) -> list[dict[str, str]]:
    hb = safe_float(row, "hb_g_dl")
    hct = safe_float(row, "hct_percent")
    rbc = safe_float(row, "rbc_10e12_l")
    mcv = safe_float(row, "mcv_fl")
    mch = safe_float(row, "mch_pg")
    rdw = safe_float(row, "rdw_percent")
    retic = safe_float(row, "retic_percent")
    ferritin = safe_float(row, "ferritin_ng_ml")
    hba2e = safe_float(row, "hba2e_percent")
    hbe = safe_float(row, "hbe_percent")
    sex = str(row.get("sex", "Female"))

    hb_cutoff = 13.0 if sex == "Male" else 12.0
    hct_cutoff = 40.0 if sex == "Male" else 36.0
    ferritin_low_cutoff = 30.0 if sex == "Male" else 15.0
    ferritin_high_cutoff = 400.0 if sex == "Male" else 150.0
    mcv_low_cutoff = thresholds.get("mcv_microcytosis", DEFAULT_THRESHOLDS["mcv_microcytosis"])
    mch_low_cutoff = thresholds.get("mch_hypochromia", DEFAULT_THRESHOLDS["mch_hypochromia"])

    anemia = (is_known(hb) and hb < hb_cutoff) or (is_known(hct) and hct < hct_cutoff)
    erythrocytosis = (is_known(hb) and hb > (16.5 if sex == "Male" else 16.0)) or (is_known(hct) and hct > (49.0 if sex == "Male" else 48.0))
    micro = is_known(mcv) and mcv < mcv_low_cutoff
    macro = is_known(mcv) and mcv >= 100.0
    hypo = is_known(mch) and mch < mch_low_cutoff
    rdw_high = is_known(rdw) and rdw > thresholds.get("rdw_high", DEFAULT_THRESHOLDS["rdw_high"])
    retic_high = is_known(retic) and retic >= 2.5
    retic_low = is_known(retic) and retic < 0.5
    ferritin_low = is_known(ferritin) and ferritin < ferritin_low_cutoff
    ferritin_high = is_known(ferritin) and ferritin > ferritin_high_cutoff
    hba2e_high = is_known(hba2e) and hba2e >= thresholds.get("hba2_beta_trait", DEFAULT_THRESHOLDS["hba2_beta_trait"])
    dcip_pos = is_positive(row, "dcip")
    hbe_present = (is_known(hbe) and hbe >= DEFAULT_THRESHOLDS["hbe_present"]) or (dcip_pos and is_known(hba2e) and hba2e > 10.0)

    items: list[dict[str, str]] = []

    if anemia and ferritin_low:
        add_differential(
            items,
            "Iron deficiency anemia or mixed iron deficiency",
            "โลหิตจางจากการขาดธาตุเหล็ก หรือภาวะขาดธาตุเหล็กร่วม",
            "High support" if micro or hypo or rdw_high else "Consider",
            "สนับสนุนมาก" if micro or hypo or rdw_high else "ควรพิจารณา",
            f"Ferritin {ferritin:g} ng/mL with {'microcytosis/hypochromia' if micro or hypo else 'anemia'}; RDW {'high' if rdw_high else 'not high'}.",
            f"Ferritin {ferritin:g} ng/mL ร่วมกับ{'เม็ดเลือดแดงเล็ก/ซีด' if micro or hypo else 'ภาวะซีด'}; RDW {'สูง' if rdw_high else 'ไม่สูง'}.",
            "Correlate with iron/TIBC/transferrin saturation, CRP, menstrual/GI blood-loss history, and repeat HbA2 after iron repletion if borderline.",
            "ตรวจ iron/TIBC/transferrin saturation, CRP, ประวัติเลือดออกประจำเดือน/ทางเดินอาหาร และพิจารณา HbA2 ซ้ำหลังแก้ภาวะขาดธาตุเหล็กหากค่าก้ำกึ่ง.",
            "danger",
        )

    if anemia and macro:
        add_differential(
            items,
            "Macrocytic anemia: B12/folate, liver-thyroid disease, medication, marrow stress",
            "โลหิตจางเม็ดเลือดแดงโต: B12/folate, ตับ-ไทรอยด์, ยา, หรือไขกระดูก",
            "High support" if mcv >= 105.0 or rdw_high else "Consider",
            "สนับสนุนมาก" if mcv >= 105.0 or rdw_high else "ควรพิจารณา",
            f"MCV {mcv:g} fL with anemia; reticulocyte {'elevated' if retic_high else 'not elevated/unknown'}.",
            f"MCV {mcv:g} fL ร่วมกับภาวะซีด; reticulocyte {'สูง' if retic_high else 'ไม่สูง/ไม่ทราบ'}.",
            "Review smear, B12, folate, reticulocyte index, TSH, liver tests, alcohol/medication exposure, and marrow evaluation if persistent.",
            "ทบทวนสเมียร์, B12, folate, reticulocyte index, TSH, liver test, ประวัติแอลกอฮอล์/ยา และพิจารณาประเมินไขกระดูกหากยังผิดปกติ.",
            "high",
        )

    if anemia and retic_high:
        add_differential(
            items,
            "Hemolysis or recent blood loss pattern",
            "รูปแบบที่อาจเข้าได้กับ hemolysis หรือเสียเลือดเร็วๆ นี้",
            "High support" if retic >= 3.0 else "Consider",
            "สนับสนุนมาก" if retic >= 3.0 else "ควรพิจารณา",
            f"Reticulocyte {retic:g}% is elevated in an anemic sample.",
            f"Reticulocyte {retic:g}% สูงในตัวอย่างที่มีภาวะซีด.",
            "Add bilirubin, LDH, haptoglobin, DAT, urine hemoglobin, and smear review for schistocytes/spherocytes.",
            "เพิ่ม bilirubin, LDH, haptoglobin, DAT, urine hemoglobin และทบทวนสเมียร์หา schistocytes/spherocytes.",
            "danger",
        )

    if anemia and retic_low and not ferritin_low:
        add_differential(
            items,
            "Hypoproliferative anemia: renal/endocrine/marrow suppression pattern",
            "โลหิตจางแบบสร้างเม็ดเลือดต่ำ: ไต/ต่อมไร้ท่อ/ไขกระดูกถูกกด",
            "Consider",
            "ควรพิจารณา",
            f"Reticulocyte {retic:g}% is low without a low ferritin pattern.",
            f"Reticulocyte {retic:g}% ต่ำ โดยไม่มีรูปแบบ ferritin ต่ำ.",
            "Correlate with WBC/platelets, creatinine/eGFR, EPO context, TSH, inflammatory markers, and medication/toxin history.",
            "ประเมินร่วมกับ WBC/platelets, creatinine/eGFR, บริบท EPO, TSH, inflammatory markers และประวัติยา/สารพิษ.",
            "moderate",
        )

    if anemia and ferritin_high and not retic_high:
        add_differential(
            items,
            "Anemia of inflammation/chronic disease or iron sequestration",
            "โลหิตจางจากการอักเสบ/โรคเรื้อรัง หรือการกักเก็บธาตุเหล็ก",
            "Consider",
            "ควรพิจารณา",
            f"Ferritin {ferritin:g} ng/mL is high with anemia and no reticulocytosis signal.",
            f"Ferritin {ferritin:g} ng/mL สูง ร่วมกับภาวะซีดและไม่มีสัญญาณ reticulocytosis.",
            "Check CRP/ESR, transferrin saturation, renal profile, liver profile, and clinical inflammatory or malignant disease context.",
            "ตรวจ CRP/ESR, transferrin saturation, renal profile, liver profile และบริบทโรคอักเสบหรือมะเร็ง.",
            "moderate",
        )

    if micro and ferritin_high and rdw_high and not hba2e_high and not hbe_present:
        add_differential(
            items,
            "Sideroblastic anemia, lead/toxin exposure, or complex microcytosis",
            "sideroblastic anemia, การสัมผัสตะกั่ว/สารพิษ หรือ microcytosis ซับซ้อน",
            "Consider",
            "ควรพิจารณา",
            f"Microcytosis with high ferritin ({ferritin:g} ng/mL), high RDW, and no strong HbA2/HbE signal.",
            f"เม็ดเลือดแดงเล็ก ร่วมกับ ferritin สูง ({ferritin:g} ng/mL), RDW สูง และไม่มีสัญญาณ HbA2/HbE ชัด.",
            "Review smear, lead level when relevant, B6/drug/alcohol exposure, iron saturation, and hematology referral if unexplained.",
            "ทบทวนสเมียร์, ตรวจระดับตะกั่วเมื่อมีความเสี่ยง, ประวัติ B6/ยา/แอลกอฮอล์, iron saturation และส่งปรึกษาโลหิตวิทยาหากยังไม่ชัด.",
            "moderate",
        )

    if anemia and rdw_high and not micro and not macro:
        add_differential(
            items,
            "Mixed or evolving anemia with normocytic indices",
            "โลหิตจางแบบผสมหรือระยะเริ่มต้นที่ MCV ยังปกติ",
            "Consider",
            "ควรพิจารณา",
            f"RDW {rdw:g}% is high while MCV remains in the normocytic range.",
            f"RDW {rdw:g}% สูง ขณะที่ MCV ยังอยู่ในช่วง normocytic.",
            "Consider combined iron/B12/folate deficiency, recent treatment response, renal/inflammatory disease, and smear morphology.",
            "พิจารณาการขาด iron/B12/folate ร่วมกัน, การตอบสนองหลังรักษา, โรคไต/อักเสบ และลักษณะสเมียร์.",
            "moderate",
        )

    if erythrocytosis:
        add_differential(
            items,
            "Erythrocytosis or polycythemia pattern",
            "รูปแบบเม็ดเลือดแดงสูงหรือ polycythemia",
            "High support" if (is_known(rbc) and rbc > 6.0) else "Consider",
            "สนับสนุนมาก" if (is_known(rbc) and rbc > 6.0) else "ควรพิจารณา",
            f"Hb/Hct {hb:g} g/dL / {hct:g}% exceed sex-adjusted screening thresholds.",
            f"Hb/Hct {hb:g} g/dL / {hct:g}% สูงกว่าเกณฑ์คัดกรองตามเพศ.",
            "Repeat CBC when hydrated, assess oxygen saturation/smoking/sleep apnea, EPO level, and JAK2 testing if persistent.",
            "ตรวจ CBC ซ้ำเมื่อ hydration เหมาะสม, ประเมิน O2 saturation/สูบบุหรี่/sleep apnea, ระดับ EPO และ JAK2 หากยังสูงต่อเนื่อง.",
            "high",
        )

    if dcip_pos and not hbe_present:
        add_differential(
            items,
            "Possible unstable hemoglobin or non-E structural variant",
            "อาจเป็น unstable hemoglobin หรือ structural variant อื่นที่ไม่ใช่ HbE",
            "Consider",
            "ควรพิจารณา",
            "DCIP is positive without a clearly increased HbE fraction.",
            "DCIP เป็นบวกโดย HbE fraction ยังไม่สูงชัด.",
            "Confirm with HPLC/CZE peak review, heat/isopropanol stability testing if available, and targeted sequencing when clinically indicated.",
            "ยืนยันด้วยการทบทวน peak ของ HPLC/CZE, heat/isopropanol stability test หากมี และ sequencing เมื่อมีข้อบ่งชี้.",
            "moderate",
        )

    if not items:
        add_differential(
            items,
            "No strong non-thalassemia hematology signal from supplied CBC/iron/Hb data",
            "ยังไม่พบสัญญาณโรคโลหิตวิทยาอื่นที่ชัดจาก CBC/iron/Hb ที่กรอก",
            "Low support",
            "สนับสนุนน้อย",
            "Current supplied values do not strongly trigger the broader anemia, hemolysis, macrocytosis, or erythrocytosis rules.",
            "ค่าที่กรอกยังไม่กระตุ้นเกณฑ์ภาวะซีดชนิดอื่น, hemolysis, macrocytosis หรือ erythrocytosis อย่างชัดเจน.",
            "Continue interpretation with clinical context, smear review, and repeat testing when symptoms or family/population risk remain.",
            "แปลผลร่วมกับอาการ, สเมียร์ และตรวจซ้ำเมื่อยังมีอาการหรือความเสี่ยงจากครอบครัว/ประชากร.",
            "info",
        )

    return items


def render_hematology_differentials(row: dict, thresholds: dict[str, float]) -> None:
    items = hematology_differentials(row, thresholds)
    section(
        tx("Other Hematology Differential Review", "วิเคราะห์โรคทางโลหิตวิทยาอื่นๆ"),
        tx(
            "Rule-based screening clues beyond thalassemia. These are prompts for follow-up testing, not final diagnoses.",
            "ข้อบ่งชี้เชิงคัดกรองนอกเหนือจากธาลัสซีเมีย ใช้เป็นแนวทางตรวจต่อ ไม่ใช่การวินิจฉัยสุดท้าย.",
        ),
    )
    clinical_box(
        tx(
            "Use this block to avoid anchoring on thalassemia when CBC, iron status, and reticulocyte patterns suggest another hematologic process.",
            "ส่วนนี้ช่วยลดการยึดติดกับธาลัสซีเมียเพียงอย่างเดียว เมื่อ CBC, iron status และ reticulocyte ชี้ไปที่กระบวนการทางโลหิตวิทยาอื่น.",
        ),
        "warn",
    )

    priority = [item for item in items if item["level"] != "info"][:3] or items[:1]
    cols = st.columns(len(priority))
    for col, item in zip(cols, priority):
        with col:
            metric_card(
                tx(item["condition"], item["condition_th"]),
                tx(item["likelihood"], item["likelihood_th"]),
                tx(item["pattern"], item["pattern_th"]),
                item["level"],
            )

    table = pd.DataFrame(
        [
            {
                tx("Condition", "ภาวะที่พิจารณา"): tx(item["condition"], item["condition_th"]),
                tx("Likelihood", "น้ำหนักหลักฐาน"): tx(item["likelihood"], item["likelihood_th"]),
                tx("Triggering pattern", "รูปแบบที่เข้าเกณฑ์"): tx(item["pattern"], item["pattern_th"]),
                tx("Suggested follow-up", "ตรวจ/ประเมินต่อ"): tx(item["next_step"], item["next_step_th"]),
            }
            for item in items
        ]
    )
    st.dataframe(table, width="stretch", hide_index=True)


st.set_page_config(page_title="Screening Test | Thal Lab Consult", page_icon="🧪", layout="wide", initial_sidebar_state="collapsed")
inject_css()
top_navigation("Laboratory screening")

hero(
    tx("ThalLink: Thalassemia Laboratory Intelligence Platform", "ThalLink: แพลตฟอร์มวิเคราะห์ธาลัสซีเมียทางห้องปฏิบัติการ"),
    tx(
        "Expert consult dashboard for CBC indices, iron status, Hb fractions, OF/DCIP/HbH inclusion, phenotype scoring, and molecular reflex planning.",
        "แดชบอร์ดช่วยปรึกษาผล CBC, iron status, Hb fractions, OF/DCIP/HbH inclusion, phenotype scoring และแผนตรวจ molecular reflex.",
    ),
    tx("CBC + Hb typing + reflex visualization", "CBC + Hb typing + ภาพรวม reflex testing"),
)
disclaimer()

section(
    tx("Screening control cards", "ตั้งค่าเกณฑ์คัดกรอง"),
    tx("Set local SOP thresholds directly on the page. This replaces the old sidebar control panel.", "ปรับ threshold ตาม SOP ของห้องปฏิบัติการได้จากหน้านี้โดยตรง."),
)
with st.container(border=True):
    st.markdown(f"**{tx('Threshold profile', 'ชุดเกณฑ์ Threshold')}**")
    tc1, tc2, tc3 = st.columns(3)
    with tc1:
        hba2_thr = st.slider(tx("HbA2 threshold for β-thal trait (%)", "เกณฑ์ HbA2 สำหรับพาหะ β-thal (%)"), 3.0, 4.5, float(DEFAULT_THRESHOLDS["hba2_beta_trait"]), .1)
    with tc2:
        mcv_thr = st.slider(tx("MCV microcytosis threshold (fL)", "เกณฑ์ MCV เม็ดเลือดแดงเล็ก (fL)"), 70.0, 85.0, float(DEFAULT_THRESHOLDS["mcv_microcytosis"]), .5)
    with tc3:
        mch_thr = st.slider(tx("MCH hypochromia threshold (pg)", "เกณฑ์ MCH เม็ดเลือดแดงซีด (pg)"), 24.0, 29.0, float(DEFAULT_THRESHOLDS["mch_hypochromia"]), .5)
    thresholds = {**DEFAULT_THRESHOLDS, "hba2_beta_trait": hba2_thr, "mcv_microcytosis": mcv_thr, "mch_hypochromia": mch_thr}

with st.container(border=True):
    st.markdown(f"**{tx('Select input workflow', 'เลือกรูปแบบการใช้งาน')}**")
    mode = st.radio(tx("Input mode", "โหมดข้อมูล"), ["Single patient consult", "Batch CSV dashboard"], horizontal=True, label_visibility="collapsed", format_func=option_label)

def patient_form() -> dict:
    with st.form("patient_form"):
        section(tx("Patient/specimen metadata", "ข้อมูลผู้ป่วย/สิ่งส่งตรวจ"))
        c1,c2,c3 =st.columns(3)
        with c1:
            sample_id=st.text_input("Sample ID","CASE-EXPERT-001")
        with c2:
            sex=st.selectbox(tx("Sex", "เพศ"),["Female","Male","Other/Not specified"], format_func=option_label)
        with c3:
            age=st.number_input(tx("Age", "อายุ"),0,120,24)     
        
        c1,c2 =st.columns(2)
        with c1:
            pregnant=st.checkbox(tx("Pregnant / antenatal screening", "ตั้งครรภ์ / คัดกรองฝากครรภ์")); transfusion_recent=st.checkbox(tx("Recent transfusion", "ได้รับเลือดเร็วๆ นี้"))
        with c2:
            family_history=st.checkbox(tx("Family history / partner carrier known", "มีประวัติครอบครัว / คู่เป็นพาหะ")); smear_target_cells=st.checkbox(tx("Target cells on smear", "พบ target cells ในสเมียร์"))
        
        section(tx("Complete blood count (CBC) and iron status", "Complete blood count (CBC) และสถานะธาตุเหล็ก"))
        a1,a2,a3,a4,a5,a6=st.columns(6)
        with a1: hb=st.number_input("Hb (g/dL)",0.0,25.0,11.2,.1)
        with a2: rbc=st.number_input("RBC (10¹²/L)",0.0,10.0,5.8,.1)
        with a3: hct=st.number_input("Hct (%)",0.0,80.0,35.0,.1)
        with a4: mcv=st.number_input("MCV (fL)",30.0,130.0,67.0,.1)
        with a5: mch=st.number_input("MCH (pg)",5.0,45.0,20.5,.1)
        with a6: mchc=st.number_input("MCHC (g/dL)",20.0,45.0,31.2,.1)
        
        b1,b2,b3,b4,b5 =st.columns(5)
        with b1: ferritin=st.number_input("Ferritin (ng/mL)",0.0,2000.0,85.0,1.0)
        with b2: rdw=st.number_input("RDW (%)",5.0,35.0,14.2,.1)
        with b3: retic=st.number_input("Reticulocyte (%)",0.0,30.0,1.2,.1)
        with b4: oft=st.selectbox(tx("Osmotic fragility test", "Osmotic fragility test"),["Negative","Positive"],index=1, format_func=option_label)
        with b5: dcip=st.selectbox(tx("DCIP for HbE/unstable Hb", "DCIP สำหรับ HbE/unstable Hb"),["Negative","Positive"], format_func=option_label)

        hbh_inclusion = "Negative" 

        section(tx("Hemoglobin Typing Results", "ผล Hemoglobin Typing"))
        
        # ใช้ Tabs แทน เพื่อให้สลับหน้าจอได้ทันทีโดยไม่ต้องรันแอปใหม่
        tab_hplc, tab_cze = st.tabs([tx("HPLC input", "กรอกผล HPLC"), tx("CZE input", "กรอกผล CZE")])
        
        with tab_hplc:
            hplc_c1, hplc_c2, hplc_c3 = st.columns(3)
            with hplc_c1: hplc_hba = st.number_input("HbA (%)", 0.0, 100.0, 94.0, 0.1, key="hplc_hba")
            with hplc_c2: hplc_hba2e = st.number_input("HbA2/E (%)", 0.0, 100.0, 5.1, 0.1, key="hplc_hba2e")
            with hplc_c3: hplc_hbf = st.number_input("HbF (%)", 0.0, 100.0, 1.2, 0.1, key="hplc_hbf")
            
            hplc_c4, hplc_c5, hplc_c6 = st.columns(3)
            with hplc_c4: hplc_bart = st.number_input("Bart (%)", 0.0, 100.0, 0.0, 0.1, key="hplc_bart")
            with hplc_c5: hplc_hbh = st.number_input("HbH (%)", 0.0, 100.0, 0.0, 0.1, key="hplc_hbh")
            with hplc_c6: hplc_hbcs = st.number_input("HbCS (%)", 0.0, 100.0, 0.0, 0.1, key="hplc_hbcs")
            
        with tab_cze:
            cze_c1, cze_c2, cze_c3, cze_c4 = st.columns(4)
            with cze_c1: cze_hba = st.number_input("HbA (%)", 0.0, 100.0, 94.0, 0.1, key="cze_hba")
            with cze_c2: cze_hba2 = st.number_input("HbA2 (%)", 0.0, 100.0, 2.5, 0.1, key="cze_hba2")
            with cze_c3: cze_hbe = st.number_input("HbE (%)", 0.0, 100.0, 0.0, 0.1, key="cze_hbe")
            with cze_c4: cze_hbf = st.number_input("HbF (%)", 0.0, 100.0, 1.2, 0.1, key="cze_hbf")
            
            cze_c5, cze_c6, cze_c7 = st.columns(3)
            with cze_c5: cze_bart = st.number_input("Bart (%)", 0.0, 100.0, 0.0, 0.1, key="cze_bart")
            with cze_c6: cze_hbh = st.number_input("HbH (%)", 0.0, 100.0, 0.0, 0.1, key="cze_hbh")
            with cze_c7: cze_hbcs = st.number_input("HbCS (%)", 0.0, 100.0, 0.0, 0.1, key="cze_hbcs")

        st.markdown("---")
        # ปุ่มนี้เอาไว้ดึงค่าที่ถูกต้องไปรัน 
        hb_method = st.radio(tx("Confirm hemoglobin-analysis method:", "ยืนยันวิธีที่ใช้ในการวิเคราะห์ผล:"), ["HPLC", "CZE"], horizontal=True, format_func=option_label)
        
        st.form_submit_button(tx("Run expert consult", "เริ่มวิเคราะห์ผล"), type="primary")

    # ขั้นตอนเลือกดึงค่าตามที่ผู้ใช้เลือก (ทำงานหลังจากกดปุ่ม Submit)
    if hb_method == "HPLC":
        hba, hba2e, hbf = hplc_hba, hplc_hba2e, hplc_hbf
        hbe = 0.0
        bart, hbh, hbcs = hplc_bart, hplc_hbh, hplc_hbcs
    else:
        hba, hba2e, hbe, hbf = cze_hba, cze_hba2, cze_hbe, cze_hbf
        bart, hbh, hbcs = cze_bart, cze_hbh, cze_hbcs
        
    return {
        "sample_id": sample_id, "age": age, "sex": sex, "hb_g_dl": hb, "rbc_10e12_l": rbc,
        "hct_percent": hct, "mcv_fl": mcv, "mch_pg": mch, "mchc_g_dl": mchc, "rdw_percent": rdw,
        "retic_percent": retic, "ferritin_ng_ml": ferritin, "hba_percent": hba, 
        "hba2e_percent": hba2e, "hbf_percent": hbf, "hbe_percent": hbe, 
        "bart_percent": bart, "hbh_percent": hbh, "hbcs_percent": hbcs,
        "oft": oft, "dcip": dcip, "hbh_inclusion": hbh_inclusion, 
        "transfusion_recent": transfusion_recent, "pregnant": pregnant, 
        "smear_target_cells": smear_target_cells, "family_history": family_history,
        "hb_method": hb_method
    }

if mode == "Single patient consult":
    row = patient_form()
    result = analyze_screening(row, thresholds)
    
    section(tx("Consult summary", "สรุปผล Consult"))
    
    st.markdown(f"#### {tx('Complete Blood Count (CBC) & Iron Status', 'Complete Blood Count (CBC) และสถานะธาตุเหล็ก')}")
    
    # --- CBC แถวที่ 1 ---
    c1, c2, c3 = st.columns(3)
    
    with c1:
        # 1. กล่องบอกค่า Hb/Hct และประเมินภาวะซีด
        hb = row["hb_g_dl"]
        hct = row["hct_percent"]
        sex = row.get("sex", "Female")
        # กำหนดเกณฑ์ Hb (ปรับเลขได้ตามมาตรฐานของ Lab)
        hb_cutoff = 13.0 if sex == "Male" else 12.0
        is_anemia = hb < hb_cutoff
        
        metric_card(
            "Hb / Hct", 
            f"{hb} g/dL / {hct}%", 
            tx("Anemia", "ซีด") if is_anemia else tx("Normal", "ปกติ"), 
            "danger" if is_anemia else "info"
        )
    
    with c2:
        # 2. กล่อง RDW 
        rdw = row["rdw_percent"]
        is_high_rdw = rdw > 14.5
        
        metric_card(
            "RDW", 
            f"{rdw}%", 
            tx("Anisocytosis (high)", "Anisocytosis (สูงกว่าปกติ)") if is_high_rdw else tx("Normal", "ปกติ"), 
            "high" if is_high_rdw else "info"
        )

    with c3:
        # 3. กล่อง MCV/MCHC
        mcv = row["mcv_fl"]
        mchc = row["mchc_g_dl"]
        mcv_thr = thresholds.get("mcv_microcytosis", 80.0)
        mchc_thr = 32.0 # เกณฑ์ Hypochromic MCHC มักจะใช้ < 32 g/dL
        
        # เพิ่มเงื่อนไข Macrocytosis (MCV > 100)
        if mcv > 100.0:
            mcv_interp = tx("Macrocytosis", "เม็ดเลือดแดงโต")
            mcv_lvl = "high"
        elif mcv < mcv_thr and mchc < mchc_thr:
            mcv_interp = tx("Microcytic Hypochromic", "เม็ดเลือดแดงเล็กและซีด")
            mcv_lvl = "danger"
        elif mcv < mcv_thr:
            mcv_interp = tx("Microcytic", "เม็ดเลือดแดงเล็ก")
            mcv_lvl = "high"
        elif mchc < mchc_thr:
            mcv_interp = tx("Hypochromic", "เม็ดเลือดแดงซีด")
            mcv_lvl = "high"
        else:
            mcv_interp = tx("Normocytic Normochromic", "ขนาดและสีเม็ดเลือดแดงปกติ")
            mcv_lvl = "info"
            
        metric_card(
            "MCV / MCHC", 
            f"{mcv} fL / {mchc} g/dL", 
            mcv_interp, 
            mcv_lvl
        )

    st.write("<br>", unsafe_allow_html=True)  # เพิ่มบรรทัดว่างระหว่างแถว
            
    # --- CBC แถวที่ 2 ---
    c4, c5 = st.columns(2)
    with c4:
        # 4. แปลผล MCV หรือ OF คู่กับ DCIP (ตามเกณฑ์ใหม่)
        oft = row["oft"]
        dcip = row["dcip"]
        
        # OF pos = ตรวจ OF ได้ Positive "หรือ" MCV ต่ำ
        mcv_pos = (mcv < mcv_thr)
        of_is_pos = (oft == "Positive") or mcv_pos
        dcip_is_pos = (dcip == "Positive")
        
        # แปลผลตามตาราง
        if of_is_pos and dcip_is_pos:
            # กรณี + , +
            screen_interp = tx("Suspected Hb E with or without α-thal and/or β-thal", "สงสัย Hb E ร่วม/ไม่ร่วม α-thal และ/หรือ β-thal")
            screen_lvl = "danger"
        elif of_is_pos and not dcip_is_pos:
            # กรณี + , -
            screen_interp = tx("Suspected α-thal and/or β-thal", "สงสัย α-thal และ/หรือ β-thal")
            screen_lvl = "high"
        elif not of_is_pos and dcip_is_pos:
            # กรณี - , +
            screen_interp = tx("Suspected Hb E trait", "สงสัยพาหะ Hb E")
            screen_lvl = "high"
        else:
            # กรณี - , -
            screen_interp = tx("Non-thalassemia or non-clinically important thalassemia", "ไม่เข้าได้กับธาลัสซีเมียสำคัญทางคลินิก หรือไม่ใช่ธาลัสซีเมีย")
            screen_lvl = "info"
            
        # สร้างข้อความแสดงผลบรรทัดรองให้เห็นชัดเจนว่าแต่ละฝั่งเป็น + หรือ -
        txt_of = "+" if of_is_pos else "-"
        txt_dcip = "+" if dcip_is_pos else "-"
        
        metric_card(
            "Screening (MCV/OF & DCIP)", 
            f"MCV/OF: {txt_of} | DCIP: {txt_dcip}", 
            screen_interp, 
            screen_lvl
        )
        
    with c5:
                # 5. กล่อง Ferritin (คิดร่วมกับ MCV, MCH, DCIP)
        ferr = row["ferritin_ng_ml"]
        sex = row.get("sex", "Female")
        hb = row["hb_g_dl"]
        mch = row["mch_pg"]
        mcv = row["mcv_fl"]
        dcip = row["dcip"]
        
        # ดึงค่า Threshold พื้นฐานจากระบบ
        mcv_thr = thresholds.get("mcv_microcytosis", 80.0)
        mch_thr = thresholds.get("mch_hypochromia", 27.0)
        
        # กำหนดเกณฑ์ Hb ตัดสินภาวะซีด (Anemia) โดยอิงตามเพศ
        hb_cutoff = 13.0 if sex == "Male" else 12.0
        is_hb_low = hb < hb_cutoff
        
        # กำหนดเกณฑ์ Ferritin สูง/ต่ำ ตามเพศ (อ้างอิงจากตาราง)
        if sex == "Male":
            ferr_low = ferr < 30
            ferr_high = ferr > 400
        else:
            ferr_low = ferr < 13
            ferr_high = ferr > 150
            
        # ตรวจสอบว่าดัชนีอื่นๆ ปกติหรือไม่
        is_mcv_normal = mcv >= mcv_thr
        is_mch_normal = mch >= mch_thr
        is_dcip_normal = (dcip == "Negative")
        
        # ตรรกะการประเมินและการแสดงผลข้อความ
        if ferr_low and is_hb_low and is_mcv_normal and is_mch_normal and is_dcip_normal:
            fe_interp = tx("Iron profile review recommended", "แนะนำประเมิน Iron profile")
            fe_lvl = "danger"
        elif ferr_low:
            fe_interp = tx("Low ferritin", "ระดับ Ferritin ต่ำ")
            fe_lvl = "danger"
        elif ferr_high:
            fe_interp = tx("High ferritin", "ระดับ Ferritin สูง")
            fe_lvl = "high"
        elif (not is_mcv_normal) or (not is_mch_normal) or (not is_dcip_normal):
            fe_interp = tx("Ferritin normal (suspected thalassemia/HbE carrier)", "ระดับ Ferritin ปกติ (สงสัยพาหะธาลัสซีเมีย/HbE)")
            fe_lvl = "high"
        else:
            fe_interp = tx("Ferritin normal", "ระดับ Ferritin ปกติ")
            fe_lvl = "info"
            
        metric_card(
            "Ferritin", 
            f"{ferr} ng/mL", 
            fe_interp, 
            fe_lvl
        )
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"#### {tx('Hemoglobin Typing Results', 'ผล Hemoglobin Typing')}")
    
    t1, t2 = st.columns(2)
    with t1:
        # 1. Risk Class
        r_class = result.consult_risk
        r_lvl = "danger" if r_class == "Critical review" else "high" if r_class == "High" else "moderate" if r_class == "Moderate" else "low"
        
        metric_card(
            tx("Risk Class", "ระดับความเสี่ยง"), 
            clinical_text(r_class), 
            f"{tx('Pattern', 'รูปแบบ')}: {clinical_text(result.top_pattern)}", 
            r_lvl
        )
        
    with t2:
        import math
        
        # 2. EE Score (สูตร: 7.3*HbA2 + HbF)
        # ระบบจะพยายามดึงค่า A2/E ออกมาใช้ แต่ถ้าไม่มีก็จะดึงค่า A2 ธรรมดา
        hba2_val = row.get("hba2e_percent", 0.0)
        if math.isnan(hba2_val) or hba2_val == 0:
            hba2_val = row.get("hba2_percent", 0.0)
            
        hbf_val = row.get("hbf_percent", 0.0)
        
        # ป้องกันกรณีผู้ใช้ไม่ได้กรอก (เป็นค่าว่าง) ให้มองเป็น 0
        if math.isnan(hba2_val): hba2_val = 0.0
        if math.isnan(hbf_val): hbf_val = 0.0
        
        # คำนวณสูตร
        ee_calc = (7.3 * hba2_val) + hbf_val
        
        # แปลผลตามเกณฑ์
        if ee_calc <= 60:
            ee_interp = tx("EE score <= 60 : Suspected Homozygous HbE", "EE score <= 60 : สงสัย Homozygous HbE")
            ee_lvl = "info"
        else:
            ee_interp = tx("EE score > 60 : Suspected Beta 0 Thalassemia/HbE", "EE score > 60 : สงสัย Beta 0 Thalassemia/HbE")
            ee_lvl = "danger"
            
        metric_card(
            "EE Score", 
            f"{ee_calc:.2f}", 
            ee_interp, 
            ee_lvl
        )
   
    render_hematology_differentials(row, thresholds)

    st.markdown("---")
    section(
        tx("Partner Screening & Fetal Risk Assessment", "คัดกรองคู่สมรสและประเมินความเสี่ยงทารก"),
        tx(
            "Initial screening for severe thalassemia risk in offspring. If both partners are high risk, confirm with Hb Typing (HPLC/CZE) and DNA analysis for both partners.",
            "ผลเบื้องต้นเพื่อคัดกรองความเสี่ยงโรคธาลัสซีเมียชนิดรุนแรงที่มีโอกาสเป็นในทารก หากทั้งคู่มีความเสี่ยงสูงควรส่งตรวจยืนยันด้วย Hb Typing (HPLC/CZE) และ DNA analysis ของทั้งคู่",
        ),
    )
    with st.container(border=True):
        c_partner1, c_partner2 = st.columns(2)
        with c_partner1:
            pat_sex = row.get("sex", "Unknown")
            st.markdown(f"**{tx('Current Patient', 'ผู้ป่วยปัจจุบัน')} ({option_label(pat_sex)})**")
            st.info(f"OF Test: {option_label(row['oft'])}  \nDCIP Test: {option_label(row['dcip'])}")
            
        with c_partner2:
            st.markdown(f"**{tx('Partner', 'คู่สมรส')}**")
            p_of = st.radio(tx("Partner OF Test", "OF Test ของคู่สมรส"), ["Negative", "Positive"], horizontal=True, format_func=option_label)
            p_dcip = st.radio(tx("Partner DCIP Test", "DCIP Test ของคู่สมรส"), ["Negative", "Positive"], horizontal=True, format_func=option_label)
            
        p1_of_pos = (row["oft"] == "Positive")
        p1_dcip_pos = (row["dcip"] == "Positive")
        p2_of_pos = (p_of == "Positive")
        p2_dcip_pos = (p_dcip == "Positive")
        
        risks = []
        if (p1_of_pos and not p1_dcip_pos) and (p2_of_pos and not p2_dcip_pos):
            risks = ["Hb Bart's hydrops fetalis (α-thal 1 / α-thal 1)", "Homozygous β-thalassemia"]
        elif ((p1_of_pos and not p1_dcip_pos) and (not p2_of_pos and p2_dcip_pos)) or \
             ((not p1_of_pos and p1_dcip_pos) and (p2_of_pos and not p2_dcip_pos)):
            risks = ["β-thalassemia / Hb E disease"]
        elif (p1_of_pos and p1_dcip_pos) or (p2_of_pos and p2_dcip_pos):
            if (p1_of_pos or p1_dcip_pos) and (p2_of_pos or p2_dcip_pos): 
                 risks = [
                     "β-thalassemia / Hb E disease", 
                     "Hb Bart's hydrops fetalis (α-thal 1 / α-thal 1)", 
                     "Homozygous β-thalassemia"
                 ]
                 
        if risks:
            metric_card(
                tx("High Risk Fetus", "ทารกมีความเสี่ยงสูง"), 
                " / ".join(risks), 
                tx("Recommended: Proceed to full Hb Typing (HPLC/CZE) & DNA analysis for both partners.", "แนะนำส่งตรวจ Hb Typing (HPLC/CZE) และ DNA analysis ของทั้งคู่."), 
                "danger"
            )
        else:
            metric_card(
                tx("Low Risk", "ความเสี่ยงต่ำ"), 
                tx("No severe thalassemia risk detected", "ไม่พบความเสี่ยงธาลัสซีเมียชนิดรุนแรงจากการคัดกรอง"), 
                tx("Routine ANC care. No further thalassemia testing required unless clinically indicated.", "ดูแลตาม ANC ปกติ และไม่จำเป็นต้องตรวจธาลัสซีเมียต่อ เว้นแต่มีข้อบ่งชี้ทางคลินิก."), 
                "info"
            )

    section(tx("Screening visual analytics", "ภาพรวมเชิงวิเคราะห์"))
    t1,t2,t3=st.tabs([tx("Visual consult board", "บอร์ดภาพรวม"),tx("Analytical pattern", "รูปแบบวิเคราะห์"),tx("Reflex pathway", "เส้นทางตรวจต่อ")]); scores={"β-thal trait":result.beta_trait_score,"α-thal/HbH":result.alpha_trait_score,"HbE/variant":result.hbe_score,"Iron deficiency":result.iron_deficiency_score}
    with t1:
        st.plotly_chart(score_radar(scores), width='stretch')
        # อัปเดตให้ส่งค่า Bart, HbH, HbCS เข้าไปด้วย
        st.plotly_chart(hb_fraction_donut(row["hba_percent"], row["hba2e_percent"], row["hbf_percent"], row["hbe_percent"], row.get("bart_percent", 0), row.get("hbh_percent", 0), row.get("hbcs_percent", 0)), width='stretch')
        st.plotly_chart(cbc_reference_bars(row), width='stretch')
    
    with t2:
        # อัปเดตให้ส่งค่า Bart, HbH, HbCS และ Method เข้าไปด้วย
        st.plotly_chart(hplc_chromatogram(row["hba_percent"], row["hba2e_percent"], row["hbf_percent"], row["hbe_percent"], row.get("bart_percent", 0), row.get("hbh_percent", 0), row.get("hbcs_percent", 0), row.get("hb_method", "HPLC")), width='stretch')
        
    with t3: st.plotly_chart(reflex_sankey(result), width='stretch')

    section(tx("Evidence and recommendations", "หลักฐานและคำแนะนำ"))
    ev_col, rec_col = st.columns(2)
    with ev_col:
        with st.container(border=True):
            st.markdown(f"**{tx('Evidence', 'หลักฐาน')}**")
            for item in result.evidence:
                st.markdown(f"- {item}")
    with rec_col:
        with st.container(border=True):
            st.markdown(f"**{tx('Recommendations', 'คำแนะนำ')}**")
            for item in result.recommendations:
                st.markdown(f"- {item}")
            if result.caveats:
                st.markdown(f"**{tx('Caveats', 'ข้อควรระวัง')}**")
                for item in result.caveats:
                    st.markdown(f"- {item}")
    
    section(tx("Download consult report", "ดาวน์โหลดรายงาน consult"))
    report_md=screening_report_markdown(result); c1,c2=st.columns(2)
    with c1: st.download_button(tx("Download Markdown report", "ดาวน์โหลดรายงาน Markdown"), report_md.encode("utf-8"), f"{result.sample_id}_thal_consult.md", "text/markdown")
    with c2: st.download_button(tx("Download structured JSON", "ดาวน์โหลด JSON"), to_json_bytes(result), f"{result.sample_id}_thal_consult.json", "application/json")
else:
    section(tx("Batch CSV dashboard", "แดชบอร์ด CSV หลายราย"))
    st.markdown(tx("Upload a CSV with the screening columns below, or use the built-in expert demo dataset.", "อัปโหลด CSV ตามคอลัมน์ด้านล่าง หรือใช้ชุดข้อมูลตัวอย่างในระบบ."))
    with st.expander(tx("Required/recommended columns", "คอลัมน์ที่ต้องมี/แนะนำ")): pills(SCREENING_COLUMNS,"blue")
    template=example_screening_dataframe(); st.download_button(tx("Download example screening CSV", "ดาวน์โหลด CSV ตัวอย่าง"), template.to_csv(index=False).encode("utf-8"), "example_thalassemia_screening.csv", "text/csv")
    uploaded=st.file_uploader(tx("Upload screening CSV", "อัปโหลด screening CSV"), type=["csv"]); df=pd.read_csv(uploaded) if uploaded is not None else template; results=analyze_dataframe(df, thresholds)
    ml_results = phenotype_similarity(df)
    results = results.merge(ml_results, on="sample_id", how="left")
    k1,k2,k3,k4=st.columns(4)
    with k1: metric_card(tx("Samples", "จำนวนตัวอย่าง"), str(len(results)), tx("Rows interpreted", "จำนวนแถวที่แปลผล"), "info")
    with k2: metric_card(tx("High/Critical", "สูง/วิกฤต"), str(int(results["consult_risk"].isin(["High","Critical review"]).sum())), tx("Reflex-priority samples", "ตัวอย่างที่ควรตรวจต่อก่อน"), "high")
    with k3: metric_card(tx("ML-ready features", "ตัวแปรพร้อมใช้กับ ML"), str(len(ml_feature_matrix(df).columns)-1), tx("Exportable numeric inputs", "ตัวแปรตัวเลขที่ export ได้"), "moderate")
    with k4: metric_card(tx("Dominant pattern", "รูปแบบที่พบบ่อยสุด"), clinical_text(str(results["top_pattern"].mode().iloc[0])), tx("Most frequent top pattern", "Top pattern ที่พบบ่อยที่สุด"), "low")
    st.dataframe(results, width='stretch', hide_index=True); st.download_button(tx("Download interpreted batch CSV", "ดาวน์โหลด CSV ที่แปลผลแล้ว"), results.to_csv(index=False).encode("utf-8"), "thalassemia_screening_interpreted.csv", "text/csv")
    with st.expander(tx("Download/view ML feature matrix", "ดาวน์โหลด/ดู ML feature matrix"), expanded=False):
        features = ml_feature_matrix(df)
        st.dataframe(features, width='stretch', hide_index=True)
        st.download_button(tx("Download ML feature matrix CSV", "ดาวน์โหลด ML feature matrix CSV"), features.to_csv(index=False).encode("utf-8"), "thalassemia_ml_feature_matrix.csv", "text/csv")
    v1,v2=st.columns(2)
    with v1: st.plotly_chart(batch_risk_distribution(results), width='stretch')
    with v2: st.plotly_chart(score_heatmap(results), width='stretch')
    st.plotly_chart(batch_mcv_hba2_scatter(results), width='stretch'); st.plotly_chart(population_sankey(results), width='stretch')

production_footer()
