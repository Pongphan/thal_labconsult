from __future__ import annotations

import pandas as pd
import streamlit as st
from thalab.core import DEFAULT_THRESHOLDS, SCREENING_COLUMNS, analyze_dataframe, analyze_screening, example_screening_dataframe
from thalab.reporting import screening_report_markdown, to_json_bytes
from thalab.styles import clinical_box, disclaimer, hero, inject_css, metric_card, pills, section, sidebar_brand
from thalab.viz import batch_mcv_hba2_scatter, batch_risk_distribution, cbc_reference_bars, diagnostic_waterfall, hb_fraction_donut, hplc_chromatogram, mcv_hba2_quadrant, population_sankey, reflex_sankey, risk_gauge, score_heatmap, score_radar

st.set_page_config(page_title="Screening Test | Thal Lab Consult", page_icon="🧪", layout="wide")
inject_css(); sidebar_brand("Laboratory screening")

with st.sidebar:
    st.markdown("### ⚙️ Threshold profile")
    hba2_thr = st.slider("HbA2 threshold for β-thal trait (%)", 3.0, 4.5, float(DEFAULT_THRESHOLDS["hba2_beta_trait"]), .1)
    mcv_thr = st.slider("MCV microcytosis threshold (fL)", 70.0, 85.0, float(DEFAULT_THRESHOLDS["mcv_microcytosis"]), .5)
    mch_thr = st.slider("MCH hypochromia threshold (pg)", 24.0, 29.0, float(DEFAULT_THRESHOLDS["mch_hypochromia"]), .5)
    thresholds = {**DEFAULT_THRESHOLDS, "hba2_beta_trait": hba2_thr, "mcv_microcytosis": mcv_thr, "mch_hypochromia": mch_thr}

hero("Page 1 — Laboratory Screening Test", "Expert consult dashboard for CBC indices, iron status, Hb fractions, OF/DCIP/HbH inclusion, phenotype scoring, and molecular reflex planning.", "CBC + Hb typing + reflex visualization")
disclaimer()
mode = st.segmented_control("Input mode", ["Single patient consult", "Batch CSV dashboard"], default="Single patient consult")

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
        
        c1,c2,c3 =st.columns(3)
        with c1:
            pregnant=st.checkbox("Pregnant / antenatal screening"); transfusion_recent=st.checkbox("Recent transfusion")
        with c2:
            family_history=st.checkbox("Family history / partner carrier known"); smear_target_cells=st.checkbox("Target cells on smear")
        with c3:
            hbh_inclusion=st.selectbox("HbH inclusion body",["Negative","Positive"])
        

        section("Complete blood count (CBC) and iron status")
        a1,a2,a3,a4,a5,a6=st.columns(6)
        with a1: hb=st.number_input("Hb (g/dL)",0.0,25.0,11.2,.1)
        with a2: rbc=st.number_input("RBC (10¹²/L)",0.0,10.0,5.8,.1)
        with a3: hct=st.number_input("Hct (%)",0.0,80.0,35.0,.1)
        with a4: mcv=st.number_input("MCV (fL)",30.0,130.0,67.0,.1)
        with a5: mch=st.number_input("MCH (pg)",5.0,45.0,20.5,.1)
        with a6: mchc=st.number_input("MCHC (g/dL)",20.0,45.0,31.2,.1)
        
        b1,b2,b3,b4,b5,b6 =st.columns(6)
        with b1: ferritin=st.number_input("Ferritin (ng/mL)",0.0,2000.0,85.0,1.0)
        with b2: rdw=st.number_input("RDW (%)",5.0,35.0,14.2,.1)
        with b3: retic=st.number_input("Reticulocyte (%)",0.0,30.0,1.2,.1)
        with b4: oft=st.selectbox("Osmotic fragility test",["Negative","Positive"],index=1)
        with b5: dcip=st.selectbox("DCIP for HbE/unstable Hb",["Negative","Positive"])
        with b6: hbe=st.number_input("HbE (%)",0.0,100.0,0.5,.1) 

        section("Hemoglobin Typing")
        c1,c2,c3 =st.columns(3)
        with c1: hba=st.number_input("HbA (%)",0.0,100.0,94.0,.1)
        with c2: hba2e =st.number_input("HbA2/E (%)",0.0,100.0,5.1,.1)
        with c3: hbf=st.number_input("HbF (%)",0.0,100.0,1.2,.1)
        
        st.form_submit_button("Run expert consult", type="primary")
    return {"sample_id":sample_id,"age":age,"sex":sex,"hb_g_dl":hb,"rbc_10e12_l":rbc,"hct_percent":hct,"mcv_fl":mcv,"mch_pg":mch,"mchc_g_dl":mchc,"rdw_percent":rdw,"retic_percent":retic,"ferritin_ng_ml":ferritin,"hba_percent":hba,"hba2e_percent":hba2e,"hbf_percent":hbf,"hbe_percent":hbe,"oft":oft,"dcip":dcip,"hbh_inclusion":hbh_inclusion,"transfusion_recent":transfusion_recent,"pregnant":pregnant,"smear_target_cells":smear_target_cells,"family_history":family_history}

if mode == "Single patient consult":
    row = patient_form()
    result = analyze_screening(row, thresholds)
    
    section("Consult summary")
    
    # 🌟 Swapped Layout: Expert Verdict on the LEFT, Key Findings on the RIGHT
    col_verdict, col_evidence = st.columns([0.9, 1.1])
    
    with col_verdict:
        st.markdown("#### 📋 Expert Verdict")
        level = "danger" if result.consult_risk == "Critical review" else "high" if result.consult_risk == "High" else "moderate" if result.consult_risk == "Moderate" else "low"
        v1, v2 = st.columns(2)
        with v1:
            metric_card(
                "Risk Class", 
                result.consult_risk, 
                f"Pattern: {result.top_pattern}", 
                level
            )
        with v2:
            # Reflex priority decision based on the internal triage rules
            #  โค้ดแก้ไขใหม่ (เปลี่ยนไปอิงตามค่า consult_score แบบเดียวกับที่โค้ดดั้งเดิมใช้)
            reflex_action = "Molecular testing" if result.consult_score >= 45 or row["hba2e_percent"] >= 4.0 else "Routine review"
            metric_card(
                "Reflex Priority", 
                reflex_action, 
                "Recommended next step", 
                level
            )
            
    with col_evidence:
        st.markdown("#### 🔍 Key Laboratory Findings")
        m1, m2 = st.columns(2)
        with m1:
            # Primary screening indicator
            mcv_val = row["mcv_fl"]
            mcv_status = "🔴 Microcytosis (<80 fL)" if mcv_val < 80 else "🟢 Normal (≥80 fL)"
            metric_card(
                "Mean Corpuscular Volume", 
                f"{mcv_val} fL", 
                mcv_status, 
                "danger" if mcv_val < 80 else "info"
            )
        with m2:
            # HbA2/E value relative to cutoff
            hba2_val = row["hba2e_percent"]
            hba2_thr = thresholds.get("hba2_cutoff", 3.5)
            hba2_status = f"🔺 Elevated (>{hba2_thr}%) • Suspect β-Trait" if hba2_val > hba2_thr else "🟢 Normal range"
            metric_card(
                "Observed HbA2/E", 
                f"{hba2_val}%", 
                hba2_status, 
                "high" if hba2_val > hba2_thr else "low"
            )


    st.markdown("---")

    section("Stunning screening visual analytics")
    t1,t2,t3=st.tabs(["Visual consult board","Analytical pattern","Reflex pathway"]); scores={"β-thal trait":result.beta_trait_score,"α-thal/HbH":result.alpha_trait_score,"HbE/variant":result.hbe_score,"Iron deficiency":result.iron_deficiency_score}
    with t1:
        st.plotly_chart(score_radar(scores), use_container_width=True)
        st.plotly_chart(hb_fraction_donut(row["hba_percent"],row["hba2e_percent"],row["hbf_percent"],row["hbe_percent"]), use_container_width=True)
        st.plotly_chart(cbc_reference_bars(row), use_container_width=True)
    
    with t2:
        st.plotly_chart(hplc_chromatogram(row["hba_percent"],row["hba2e_percent"],row["hbf_percent"],row["hbe_percent"]), use_container_width=True)
        
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
    k1,k2,k4=st.columns(3)
    with k1: metric_card("Samples", str(len(results)), "Rows interpreted", "info")
    with k2: metric_card("High/Critical", str(int(results["consult_risk"].isin(["High","Critical review"]).sum())), "Reflex-priority samples", "high")
    with k4: metric_card("Dominant pattern", str(results["top_pattern"].mode().iloc[0]), "Most frequent top pattern", "low")
    st.dataframe(results, use_container_width=True, hide_index=True); st.download_button("Download interpreted batch CSV", results.to_csv(index=False).encode("utf-8"), "thalassemia_screening_interpreted.csv", "text/csv")
    v1,v2=st.columns(2)
    with v1: st.plotly_chart(batch_risk_distribution(results), use_container_width=True)
    with v2: st.plotly_chart(score_heatmap(results), use_container_width=True)
    st.plotly_chart(batch_mcv_hba2_scatter(results), use_container_width=True); st.plotly_chart(population_sankey(results), use_container_width=True)
