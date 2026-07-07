from __future__ import annotations

import streamlit as st

from thalab.core import analyze_dataframe, example_screening_dataframe
from thalab.styles import (
    disclaimer,
    hero,
    inject_css,
    metric_card,
    module_launch_card,
    production_footer,
    section,
    top_navigation,
    tx,
)
from thalab.viz import batch_mcv_hba2_scatter, population_sankey, thalassemia_spectrum_chart

st.set_page_config(
    page_title="ThalLink",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject_css()
top_navigation("Command center")

hero(
    tx("ThalLink: Thalassemia Laboratory Intelligence Platform", "ThalLink: แพลตฟอร์มวิเคราะห์ธาลัสซีเมียทางห้องปฏิบัติการ"),
    tx(
        "A hematology-focused Streamlit application for thalassemia screening interpretation, reflex-test planning, molecular panel intelligence, and reproductive-risk consultation.",
        "แอป Streamlit สำหรับแปลผลคัดกรองธาลัสซีเมีย วางแผน reflex test วิเคราะห์ molecular panel และให้คำปรึกษาความเสี่ยงการมีบุตร.",
    ),
    tx("Expert web application blueprint", "ต้นแบบเว็บแอปผู้เชี่ยวชาญ"),
)

disclaimer()

c1, c2, c3, c4 = st.columns(4)

with c1:
    # REPLACED: Removed the undefined 'row' and 'result' calls.
    # Added a static metric card that fits the theme of the Command Center.
    metric_card(
        tx("Interpretive Engine", "ระบบแปลผล"), 
        tx("Active", "พร้อมใช้งาน"), 
        tx("Rule-based diagnostic pathways", "เส้นทางวินิจฉัยแบบ rule-based"), 
        "info"
    )

with c2:
    metric_card(tx("Modules", "โมดูล"), "2", tx("Screening consult + PCR allele matching", "Screening consult + PCR allele matching"), "high")
with c3:
    metric_card(tx("Visual layers", "ชั้นข้อมูลภาพ"), "10+", tx("Gauge, radar, Sankey, HPLC, panel and risk charts", "Gauge, radar, Sankey, HPLC, panel และ risk charts"), "moderate")
with c4:
    metric_card(tx("Batch ready", "รองรับ Batch"), "CSV", tx("Population dashboard + downloads", "Population dashboard + ดาวน์โหลดผล"), "low")

section(
    tx("Clinical laboratory workflow", "Workflow ทางห้องปฏิบัติการ"),
    tx("The app follows a practical sequence: screen, interpret, reflex, genotype, and counsel.", "แอปเรียง workflow แบบใช้งานจริง: คัดกรอง แปลผล ตรวจต่อ genotype และให้คำปรึกษา."),
)
st.markdown(
    f"""
<div class="glass-card">
  <div class="flow-step"><span class="flow-index">1</span><div><b>{tx("Screening layer:", "ชั้นคัดกรอง:")}</b> {tx("CBC indices, smear clues, OF/DCIP, ferritin, HbA/HbA2/HbF/HbE fractions.", "CBC indices, smear clues, OF/DCIP, ferritin และ HbA/HbA2/HbF/HbE fractions.")}</div></div>
  <div class="flow-step"><span class="flow-index">2</span><div><b>{tx("Interpretive engine:", "ระบบแปลผล:")}</b> {tx("Explainable laboratory rules for β-thalassemia trait, α-thalassemia/HbH pattern, HbE, and iron deficiency or mixed microcytosis.", "กฎแปลผลที่อธิบายได้สำหรับ β-thalassemia trait, α-thalassemia/HbH pattern, HbE และ iron deficiency/mixed microcytosis.")}</div></div>
  <div class="flow-step"><span class="flow-index">3</span><div><b>{tx("Reflex planning:", "วางแผนตรวจต่อ:")}</b> {tx("HBB panel/sequencing, HBA1/HBA2 deletion-duplication, HbE confirmation, and partner testing.", "HBB panel/sequencing, HBA1/HBA2 deletion-duplication, HbE confirmation และ partner testing.")}</div></div>
  <div class="flow-step"><span class="flow-index">4</span><div><b>{tx("Molecular module:", "โมดูล molecular:")}</b> {tx("Targeted PCR/gap-PCR/ARMS-PCR panel intelligence and Punnett risk modeling.", "วิเคราะห์ targeted PCR/gap-PCR/ARMS-PCR panel และ Punnett risk modeling.")}</div></div>
</div>
""",
    unsafe_allow_html=True,
)

section(
    tx("Thalassemia topic", "หัวข้อธาลัสซีเมีย"),
    tx("A compact knowledge view of the disorders this dashboard is designed to screen, interpret, and escalate.", "สรุปความรู้ย่อของกลุ่มโรคที่แดชบอร์ดนี้ใช้คัดกรอง แปลผล และส่งตรวจต่อ."),
)
st.markdown(
    f"""
<div class="glass-card">
  <div class="flow-step"><span class="flow-index">α</span><div><b>{tx("Alpha-thalassemia:", "Alpha-thalassemia:")}</b> {tx("Reduced α-globin production ranges from silent carrier states to HbH disease and Hb Bart's hydrops fetalis.", "การสร้าง α-globin ลดลงได้ตั้งแต่ silent carrier จนถึง HbH disease และ Hb Bart's hydrops fetalis.")}</div></div>
  <div class="flow-step"><span class="flow-index">β</span><div><b>{tx("Beta-thalassemia and HbE:", "Beta-thalassemia และ HbE:")}</b> {tx("HBB variants can produce elevated HbA2, HbE fractions, increased HbF, microcytosis, anemia, and compound reproductive risk.", "HBB variants ทำให้ HbA2/HbE/HbF สูง เม็ดเลือดแดงเล็ก ซีด และมีความเสี่ยงแบบ compound ในคู่สมรสได้.")}</div></div>
  <div class="flow-step"><span class="flow-index">!</span><div><b>{tx("Why it matters:", "ความสำคัญ:")}</b> {tx("Screening signals guide reflex Hb analysis, iron review, molecular confirmation, partner testing, and prenatal counseling when severe genotype combinations are possible.", "สัญญาณจากการคัดกรองช่วยนำไปสู่ Hb analysis, iron review, molecular confirmation, partner testing และ prenatal counseling เมื่อมีโอกาสเกิด genotype รุนแรง.")}</div></div>
</div>
""",
    unsafe_allow_html=True,
)
st.plotly_chart(thalassemia_spectrum_chart(), width='stretch')

section(
    tx("Embedded demo population", "ชุดข้อมูลตัวอย่างในระบบ"),
    tx("Use the built-in data to verify dashboard behavior before uploading local laboratory data.", "ใช้ข้อมูลตัวอย่างเพื่อตรวจพฤติกรรมแดชบอร์ดก่อนอัปโหลดข้อมูลห้องปฏิบัติการจริง."),
)

st.markdown(
    tx(
    """
🟢 Normal (Minimal/None) - Normal genotype / No evidence of thalassemia  
🟡 Carrier (Low Risk) - Silent carrier, α-thalassemia carrier, β-thalassemia trait, HbE trait  
🟠 Moderate Risk - Thalassemia trait or Homozygous HbE  
🔴 High Risk - HbH disease, HbH-Constant Spring disease, β-thalassemia intermedia  
⚫ Critical Risk - Hb Bart's hydrops fetalis, HbE/β⁰-thalassemia , Homozygous β-thalassemia
""",
    """
🟢 ปกติ (Minimal/None) - genotype ปกติ / ไม่พบหลักฐานธาลัสซีเมีย  
🟡 พาหะ (Low Risk) - silent carrier, α-thalassemia carrier, β-thalassemia trait, HbE trait  
🟠 เสี่ยงปานกลาง - Thalassemia trait หรือ Homozygous HbE  
🔴 เสี่ยงสูง - HbH disease, HbH-Constant Spring disease, β-thalassemia intermedia  
⚫ วิกฤต - Hb Bart's hydrops fetalis, HbE/β⁰-thalassemia, Homozygous β-thalassemia
""",
    )
)

demo = analyze_dataframe(example_screening_dataframe())

st.plotly_chart(population_sankey(demo), width='stretch')

section(tx("Platform Roadmap", "แผนพัฒนาแพลตฟอร์ม"))
p1, p2, p3 = st.columns(3)
with p1:
    st.markdown(
        f'<div class="production-card"><div class="nav-icon">🔐</div><div class="nav-title">{tx("Clinical governance", "Clinical governance")}</div><div class="nav-caption">{tx("Add role-based login, audit trail, report sign-off, reviewer identity, versioned thresholds, and SOP-controlled interpretation text.", "เพิ่ม role-based login, audit trail, report sign-off, reviewer identity, versioned thresholds และข้อความแปลผลที่ควบคุมด้วย SOP.")}</div></div>',
        unsafe_allow_html=True,
    )
with p2:
    st.markdown(
        f'<div class="production-card"><div class="nav-icon">🧠</div><div class="nav-title">{tx("ML integration path", "เส้นทางเชื่อมต่อ ML")}</div><div class="nav-caption">{tx("Use the current feature schema as an ML input layer, then validate models against local HPLC/capillary electrophoresis and molecular-confirmed labels.", "ใช้ feature schema ปัจจุบันเป็น input layer สำหรับ ML แล้ว validate กับผล HPLC/capillary electrophoresis และ molecular-confirmed labels ของห้องปฏิบัติการ.")}</div></div>',
        unsafe_allow_html=True,
    )
with p3:
    st.markdown(
        f'<div class="production-card"><div class="nav-icon">🔗</div><div class="nav-title">{tx("LIS/LIMS readiness", "ความพร้อม LIS/LIMS")}</div><div class="nav-caption">{tx("Map sample IDs, instrument exports, QC flags, allele nomenclature, and structured JSON/CSV outputs to the laboratory information workflow.", "เชื่อม sample IDs, instrument exports, QC flags, allele nomenclature และ structured JSON/CSV outputs เข้ากับ workflow ของระบบสารสนเทศห้องปฏิบัติการ.")}</div></div>',
        unsafe_allow_html=True,
    )

contributors_col, advisors_col = st.columns((3, 2))
with contributors_col:
    st.markdown(
        f"""
<div class="production-card">
  <div class="nav-icon">👥</div>
  <div class="nav-title">{tx("Contributors", "ผู้ร่วมพัฒนา")}</div>
  <div class="nav-caption">
    <ul style="margin:.35rem 0 0 1.1rem; padding:0; line-height:1.75;">
      <li>นางสาวจารวดี หมื่นจัก</li>
      <li>นักศึกษาระดับบัณฑิตศึกษา บัณฑิตวิทยาลัย มหาวิทยาลัยวลัยลักษณ์</li>
      <li>นางสาวณัฐธิดา คำพีระเมา</li>
      <li>นักศึกษาระดับบัณฑิตศึกษา บัณฑิตวิทยาลัย มหาวิทยาลัยวลัยลักษณ์</li>
      <li>นางสาวณีรนุช ธนภัคพสิษฐ์</li>
      <li>นักศึกษาหลักสูตรเทคนิคการแพทย์ สำนักวิชาสหเวชศาสตร์ มหาวิทยาลัยวลัยลักษณ์</li>
    </ul>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
with advisors_col:
    st.markdown(
        f"""
<div class="production-card">
  <div class="nav-icon">🎓</div>
  <div class="nav-title">{tx("Project advisors", "อาจารย์ที่ปรึกษาโครงการ")}</div>
  <div class="nav-caption">
    <ul style="margin:.35rem 0 0 1.1rem; padding:0; line-height:1.75;">
      <li>ผศ.ดร.เพ็ญโฉม พงศ์พนิตานนท์</li>
      <li>อาจารย์ประจำหลักสูตรเทคนิคการแพทย์ สำนักวิชาสหเวชศาสตร์ มหาวิทยาลัยวลัยลักษณ์</li>
      <li>รศ.ดร.มานิตย์ นุ้ยนุ่น</li>
      <li>อาจารย์ประจำหลักสูตรเทคนิคการแพทย์ สำนักวิชาสหเวชศาสตร์ มหาวิทยาลัยวลัยลักษณ์</li>
    </ul>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

production_footer()
