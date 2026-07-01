from __future__ import annotations

import pandas as pd
import streamlit as st
from thalab.core import DEFAULT_THRESHOLDS, SCREENING_COLUMNS, analyze_dataframe, analyze_screening, example_screening_dataframe
from thalab.ml import ml_feature_matrix, phenotype_similarity
from thalab.reporting import screening_report_markdown, to_json_bytes
from thalab.styles import clinical_box, disclaimer, hero, inject_css, metric_card, pills, production_footer, section, top_navigation
from thalab.viz import batch_mcv_hba2_scatter, batch_risk_distribution, cbc_reference_bars, diagnostic_waterfall, hb_fraction_donut, hplc_chromatogram, mcv_hba2_quadrant, population_sankey, reflex_sankey, risk_gauge, score_heatmap, score_radar

st.set_page_config(page_title="Screening Test | Thal Lab Consult", page_icon="🧪", layout="wide", initial_sidebar_state="collapsed")
inject_css()
top_navigation("Laboratory screening")

hero("ThalLink: Thalassemia Laboratory Intelligence Platform", "Expert consult dashboard for CBC indices, iron status, Hb fractions, OF/DCIP/HbH inclusion, phenotype scoring, and molecular reflex planning.", "CBC + Hb typing + reflex visualization")
disclaimer()

section("Screening control cards", "Set local SOP thresholds directly on the page. This replaces the old sidebar control panel.")
with st.container(border=True):
    st.markdown("**⚙️ Threshold profile**")
    tc1, tc2, tc3 = st.columns(3)
    with tc1:
        hba2_thr = st.slider("HbA2 threshold for β-thal trait (%)", 3.0, 4.5, float(DEFAULT_THRESHOLDS["hba2_beta_trait"]), .1)
    with tc2:
        mcv_thr = st.slider("MCV microcytosis threshold (fL)", 70.0, 85.0, float(DEFAULT_THRESHOLDS["mcv_microcytosis"]), .5)
    with tc3:
        mch_thr = st.slider("MCH hypochromia threshold (pg)", 24.0, 29.0, float(DEFAULT_THRESHOLDS["mch_hypochromia"]), .5)
    thresholds = {**DEFAULT_THRESHOLDS, "hba2_beta_trait": hba2_thr, "mcv_microcytosis": mcv_thr, "mch_hypochromia": mch_thr}
    pills(["in-page settings", "local SOP adjustable", "no sidebar", "review before sign-out"], "blue")

with st.container(border=True):
    st.markdown("**🧭 Select input workflow**")
    mode = st.radio("Input mode", ["Single patient consult", "Batch CSV dashboard"], horizontal=True, label_visibility="collapsed")

def patient_form() -> dict:
    with st.form("patient_form"):
        section("Patient/specimen metadata")
        c1,c2,c3 =st.columns(3)
        with c1:
            sample_id=st.text_input("Sample ID","CASE-EXPERT-001")
        with c2:
            sex=st.selectbox("Sex",["Female","Male","Other/Not specified"])
        with c3:
            age=st.number_input("Age",0,120,24)     
        
        c1,c2 =st.columns(2)
        with c1:
            pregnant=st.checkbox("Pregnant / antenatal screening"); transfusion_recent=st.checkbox("Recent transfusion")
        with c2:
            family_history=st.checkbox("Family history / partner carrier known"); smear_target_cells=st.checkbox("Target cells on smear")
        
        section("Complete blood count (CBC) and iron status")
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
        with b4: oft=st.selectbox("Osmotic fragility test",["Negative","Positive"],index=1)
        with b5: dcip=st.selectbox("DCIP for HbE/unstable Hb",["Negative","Positive"])

        hbh_inclusion = "Negative" 

        section("Hemoglobin Typing Results")
        
        # ใช้ Tabs แทน เพื่อให้สลับหน้าจอได้ทันทีโดยไม่ต้องรันแอปใหม่
        tab_hplc, tab_cze = st.tabs(["🧪 หลักการ HPLC", "🧪 หลักการ CZE"])
        
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
        hb_method = st.radio("ยืนยันวิธีที่ใช้ในการวิเคราะห์ผล:", ["HPLC", "CZE"], horizontal=True)
        
        st.form_submit_button("Run expert consult", type="primary")

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
    
    section("Consult summary")
    
    st.markdown("#### 🩸 Complete Blood Count (CBC) & Iron Status")
    
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
            "ซีด (Anemia)" if is_anemia else "ปกติ (Normal)", 
            "danger" if is_anemia else "info"
        )
    
    with c2:
        # 2. กล่อง RDW 
        rdw = row["rdw_percent"]
        is_high_rdw = rdw > 14.5
        
        metric_card(
            "RDW", 
            f"{rdw}%", 
            "Anisocytosis (ค่าสูงกว่าปกติ)" if is_high_rdw else "ปกติ (Normal)", 
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
            mcv_interp = "Macrocytosis"
            mcv_lvl = "high"
        elif mcv < mcv_thr and mchc < mchc_thr:
            mcv_interp = "Microcytic Hypochromic"
            mcv_lvl = "danger"
        elif mcv < mcv_thr:
            mcv_interp = "Microcytic"
            mcv_lvl = "high"
        elif mchc < mchc_thr:
            mcv_interp = "Hypochromic"
            mcv_lvl = "high"
        else:
            mcv_interp = "Normocytic Normochromic"
            mcv_lvl = "info"
            
        metric_card(
            "MCV / MCHC", 
            f"{mcv} fL / {mchc} g/dL", 
            mcv_interp, 
            mcv_lvl
        )
        
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
            screen_interp = "Suspected Hb E with or without α-thal and/or β-thal"
            screen_lvl = "danger"
        elif of_is_pos and not dcip_is_pos:
            # กรณี + , -
            screen_interp = "Suspected α-thal and/or β-thal"
            screen_lvl = "high"
        elif not of_is_pos and dcip_is_pos:
            # กรณี - , +
            screen_interp = "Suspected Hb E trait"
            screen_lvl = "high"
        else:
            # กรณี - , -
            screen_interp = "Non-thalassemia or non-clinically important thalassemia"
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
            fe_interp = "Diagnosis Iron Profile"
            fe_lvl = "danger"
        elif ferr_low:
            fe_interp = "ระดับ Ferritin ต่ำ"
            fe_lvl = "danger"
        elif ferr_high:
            fe_interp = "ระดับ Ferritin สูง"
            fe_lvl = "high"
        elif (not is_mcv_normal) or (not is_mch_normal) or (not is_dcip_normal):
            fe_interp = "ระดับ Ferritin ปกติ (สงสัยพาหะธาลัสซีเมีย/HbE)"
            fe_lvl = "high"
        else:
            fe_interp = "ระดับ Ferritin ปกติ"
            fe_lvl = "info"
            
        metric_card(
            "Ferritin", 
            f"{ferr} ng/mL", 
            fe_interp, 
            fe_lvl
        )
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🧬 Hemoglobin Typing Results")
    
    t1, t2 = st.columns(2)
    with t1:
        # 1. Risk Class
        r_class = result.consult_risk
        r_lvl = "danger" if r_class == "Critical review" else "high" if r_class == "High" else "moderate" if r_class == "Moderate" else "low"
        
        metric_card(
            "Risk Class", 
            r_class, 
            f"Pattern: {result.top_pattern}", 
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
            ee_interp = "EE score <= 60 : Suspected Homozygous HbE"
            ee_lvl = "info"
        else:
            ee_interp = "EE score > 60 : Suspected Beta 0 Thalassemia/HbE"
            ee_lvl = "danger"
            
        metric_card(
            "EE Score", 
            f"{ee_calc:.2f}", 
            ee_interp, 
            ee_lvl
        )
   
    st.markdown("---")
    section("Partner Screening & Fetal Risk Assessment","ผลเบื้องต้นเพื่อคัดกรองความเสี่ยงโรคธาลัสซีเมียชนิดรุนแรงที่มีโอกาสเป็นในทารก หากทั้งคู่มีความเสี่ยงสูงควรส่งตรวจยืนยันด้วย Hb Typing (HPLC/CZE) และ DNA analysis ของทั้งคู่")
    with st.container(border=True):
        c_partner1, c_partner2 = st.columns(2)
        with c_partner1:
            pat_sex = row.get("sex", "Unknown")
            st.markdown(f"**Current Patient ({pat_sex})**")
            st.info(f"OF Test: {row['oft']}  \nDCIP Test: {row['dcip']}")
            
        with c_partner2:
            st.markdown("**Partner**")
            p_of = st.radio("Partner OF Test", ["Negative", "Positive"], horizontal=True)
            p_dcip = st.radio("Partner DCIP Test", ["Negative", "Positive"], horizontal=True)
            
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
                "High Risk Fetus 🚨", 
                " / ".join(risks), 
                "Recommended: Proceed to full Hb Typing (HPLC/CZE) & DNA analysis for both partners.", 
                "danger"
            )
        else:
            metric_card(
                "Low Risk 🟢", 
                "No severe thalassemia risk detected", 
                "Routine ANC care. No further thalassemia testing required unless clinically indicated.", 
                "info"
            )

    section("Screening visual analytics")
    t1,t2,t3=st.tabs(["Visual consult board","Analytical pattern","Reflex pathway"]); scores={"β-thal trait":result.beta_trait_score,"α-thal/HbH":result.alpha_trait_score,"HbE/variant":result.hbe_score,"Iron deficiency":result.iron_deficiency_score}
    with t1:
        st.plotly_chart(score_radar(scores), use_container_width=True)
        # อัปเดตให้ส่งค่า Bart, HbH, HbCS เข้าไปด้วย
        st.plotly_chart(hb_fraction_donut(row["hba_percent"], row["hba2e_percent"], row["hbf_percent"], row["hbe_percent"], row.get("bart_percent", 0), row.get("hbh_percent", 0), row.get("hbcs_percent", 0)), use_container_width=True)
        st.plotly_chart(cbc_reference_bars(row), use_container_width=True)
    
    with t2:
        # อัปเดตให้ส่งค่า Bart, HbH, HbCS และ Method เข้าไปด้วย
        st.plotly_chart(hplc_chromatogram(row["hba_percent"], row["hba2e_percent"], row["hbf_percent"], row["hbe_percent"], row.get("bart_percent", 0), row.get("hbh_percent", 0), row.get("hbcs_percent", 0), row.get("hb_method", "HPLC")), use_container_width=True)
        
    with t3: st.plotly_chart(reflex_sankey(result), use_container_width=True)
    section("Download consult report")
    report_md=screening_report_markdown(result); c1,c2=st.columns(2)
    with c1: st.download_button("Download Markdown report", report_md.encode("utf-8"), f"{result.sample_id}_thal_consult.md", "text/markdown")
    with c2: st.download_button("Download structured JSON", to_json_bytes(result), f"{result.sample_id}_thal_consult.json", "application/json")
else:
    section("Batch CSV dashboard")
    st.markdown("Upload a CSV with the screening columns below, or use the built-in expert demo dataset.")
    with st.expander("Required/recommended columns"): pills(SCREENING_COLUMNS,"blue")
    template=example_screening_dataframe(); st.download_button("Download example screening CSV", template.to_csv(index=False).encode("utf-8"), "example_thalassemia_screening.csv", "text/csv")
    uploaded=st.file_uploader("Upload screening CSV", type=["csv"]); df=pd.read_csv(uploaded) if uploaded is not None else template; results=analyze_dataframe(df, thresholds)
    ml_results = phenotype_similarity(df)
    results = results.merge(ml_results, on="sample_id", how="left")
    k1,k2,k3,k4=st.columns(4)
    with k1: metric_card("Samples", str(len(results)), "Rows interpreted", "info")
    with k2: metric_card("High/Critical", str(int(results["consult_risk"].isin(["High","Critical review"]).sum())), "Reflex-priority samples", "high")
    with k3: metric_card("ML-ready features", str(len(ml_feature_matrix(df).columns)-1), "Exportable numeric inputs", "moderate")
    with k4: metric_card("Dominant pattern", str(results["top_pattern"].mode().iloc[0]), "Most frequent top pattern", "low")
    st.dataframe(results, use_container_width=True, hide_index=True); st.download_button("Download interpreted batch CSV", results.to_csv(index=False).encode("utf-8"), "thalassemia_screening_interpreted.csv", "text/csv")
    with st.expander("Download/view ML feature matrix", expanded=False):
        features = ml_feature_matrix(df)
        st.dataframe(features, use_container_width=True, hide_index=True)
        st.download_button("Download ML feature matrix CSV", features.to_csv(index=False).encode("utf-8"), "thalassemia_ml_feature_matrix.csv", "text/csv")
    v1,v2=st.columns(2)
    with v1: st.plotly_chart(batch_risk_distribution(results), use_container_width=True)
    with v2: st.plotly_chart(score_heatmap(results), use_container_width=True)
    st.plotly_chart(batch_mcv_hba2_scatter(results), use_container_width=True); st.plotly_chart(population_sankey(results), use_container_width=True)

production_footer()
