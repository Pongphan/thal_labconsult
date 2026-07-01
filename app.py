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
    top_navigation
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
    "ThalLink: Thalassemia Laboratory Intelligence Platform",
    "A hematology-focused Streamlit application for thalassemia screening interpretation, reflex-test planning, molecular panel intelligence, and reproductive-risk consultation.",
    "Expert web application blueprint",
)

disclaimer()

c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("Navigation", "Cards", "No sidebar dependency", "info")
with c2:
    metric_card("Modules", "2", "Screening consult + PCR allele matching", "high")
with c3:
    metric_card("Visual layers", "10+", "Gauge, radar, Sankey, HPLC, panel and risk charts", "moderate")
with c4:
    metric_card("Batch ready", "CSV", "Population dashboard + downloads", "low")

section("Clinical laboratory workflow", "The app follows a practical sequence: screen, interpret, reflex, genotype, and counsel.")
st.markdown(
    """
<div class="glass-card">
  <div class="flow-step"><span class="flow-index">1</span><div><b>Screening layer:</b> CBC indices, smear clues, OF/DCIP, ferritin, HbA/HbA2/HbF/HbE fractions.</div></div>
  <div class="flow-step"><span class="flow-index">2</span><div><b>Interpretive engine:</b> explainable laboratory rules for β-thalassemia trait, α-thalassemia/HbH pattern, HbE, and iron deficiency or mixed microcytosis.</div></div>
  <div class="flow-step"><span class="flow-index">3</span><div><b>Reflex planning:</b> HBB panel/sequencing, HBA1/HBA2 deletion-duplication, HbE confirmation, and partner testing.</div></div>
  <div class="flow-step"><span class="flow-index">4</span><div><b>Molecular module:</b> targeted PCR/gap-PCR/ARMS-PCR panel intelligence and Punnett risk modeling.</div></div>
</div>
""",
    unsafe_allow_html=True,
)

section("Thalassemia topic", "A compact knowledge view of the disorders this dashboard is designed to screen, interpret, and escalate.")
st.markdown(
    """
<div class="glass-card">
  <div class="flow-step"><span class="flow-index">α</span><div><b>Alpha-thalassemia:</b> reduced α-globin production ranges from silent carrier states to HbH disease and Hb Bart's hydrops fetalis.</div></div>
  <div class="flow-step"><span class="flow-index">β</span><div><b>Beta-thalassemia and HbE:</b> HBB variants can produce elevated HbA2, HbE fractions, increased HbF, microcytosis, anemia, and compound reproductive risk.</div></div>
  <div class="flow-step"><span class="flow-index">!</span><div><b>Why it matters:</b> screening signals guide reflex Hb analysis, iron review, molecular confirmation, partner testing, and prenatal counseling when severe genotype combinations are possible.</div></div>
</div>
""",
    unsafe_allow_html=True,
)
st.plotly_chart(thalassemia_spectrum_chart(), use_container_width=True)

section("Embedded demo population", "Use the built-in data to verify dashboard behavior before uploading local laboratory data.")

st.markdown(
    """
🟢 Normal (Minimal/None) - Normal genotype / No evidence of thalassemia  
🟡 Carrier (Low Risk) - Silent carrier, α-thalassemia carrier, β-thalassemia trait, HbE trait  
🟠 Moderate Risk - Thalassemia trait or Homozygous HbE  
🔴 High Risk - HbH disease, HbH-Constant Spring disease, β-thalassemia intermedia  
⚫ Critical Risk - Hb Bart's hydrops fetalis, HbE/β⁰-thalassemia , Homozygous β-thalassemia
"""
)

demo = analyze_dataframe(example_screening_dataframe())

st.plotly_chart(population_sankey(demo), use_container_width=True)

section("Platform Roadmap")
p1, p2, p3 = st.columns(3)
with p1:
    st.markdown(
        '<div class="production-card"><div class="nav-icon">🔐</div><div class="nav-title">Clinical governance</div><div class="nav-caption">Add role-based login, audit trail, report sign-off, reviewer identity, versioned thresholds, and SOP-controlled interpretation text.</div></div>',
        unsafe_allow_html=True,
    )
with p2:
    st.markdown(
        '<div class="production-card"><div class="nav-icon">🧠</div><div class="nav-title">ML integration path</div><div class="nav-caption">Use the current feature schema as an ML input layer, then validate models against local HPLC/capillary electrophoresis and molecular-confirmed labels.</div></div>',
        unsafe_allow_html=True,
    )
with p3:
    st.markdown(
        '<div class="production-card"><div class="nav-icon">🔗</div><div class="nav-title">LIS/LIMS readiness</div><div class="nav-caption">Map sample IDs, instrument exports, QC flags, allele nomenclature, and structured JSON/CSV outputs to the laboratory information workflow.</div></div>',
        unsafe_allow_html=True,
    )

production_footer()
