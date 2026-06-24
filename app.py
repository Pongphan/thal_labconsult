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
from thalab.viz import batch_mcv_hba2_scatter, population_sankey

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
    "A hematology-focused Streamlit application for thalassemia screening interpretation, reflex-test planning, PCR allele matching, virtual gel review, and reproductive-risk consultation.",
    "Expert web application blueprint",
)

disclaimer()

c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("Navigation", "Cards", "No sidebar dependency", "info")
with c2:
    metric_card("Modules", "2", "Screening consult + PCR allele matching", "high")
with c3:
    metric_card("Visual layers", "12+", "Gauge, radar, Sankey, HPLC, gel, heatmap", "moderate")
with c4:
    metric_card("Batch ready", "CSV", "Population dashboard + downloads", "low")

section("Open a workspace", "Choose a module using the cards below. Each page also contains the same card navigation shell.")
col_a, col_b = st.columns(2)
with col_a:
    module_launch_card(
        "Laboratory Screening Test",
        "Single-patient and batch CSV consult dashboard for front-line thalassemia screening and reflex-test decision support.",
        [
            "CBC indices, Mentzer index, ferritin, OF/DCIP, HbH inclusion",
            "HbA/HbA2/HbF/HbE fraction interpretation",
            "Phenotype scores, HPLC-like plot, radar, and reflex Sankey",
        ],
        "pages/1_Laboratory_Screening_Test.py",
        "🧪",
        "Launch laboratory screening",
    )
with col_b:
    module_launch_card(
        "PCR Allele Matching",
        "Molecular hematology workspace for α/β-globin allele panels, PCR band review, confidence scoring, and couple-risk counseling.",
        [
            "Gap-PCR / ARMS-PCR / sequencing-ready target knowledge base",
            "Editable band-call sheet, virtual gel, tolerance sensitivity",
            "Punnett risk board for α- and β-globin genotype combinations",
        ],
        "pages/2_PCR_Allele_Matching.py",
        "🧬",
        "Launch PCR allele matching",
    )

section("Clinical laboratory workflow", "The app follows a practical sequence: screen, interpret, reflex, genotype, and counsel.")
st.markdown(
    """
<div class="glass-card">
  <div class="flow-step"><span class="flow-index">1</span><div><b>Screening layer:</b> CBC indices, smear clues, OF/DCIP, ferritin, HbA/HbA2/HbF/HbE fractions.</div></div>
  <div class="flow-step"><span class="flow-index">2</span><div><b>Interpretive engine:</b> explainable laboratory rules for β-thalassemia trait, α-thalassemia/HbH pattern, HbE, and iron deficiency or mixed microcytosis.</div></div>
  <div class="flow-step"><span class="flow-index">3</span><div><b>Reflex planning:</b> HBB panel/sequencing, HBA1/HBA2 deletion-duplication, HbE confirmation, and partner testing.</div></div>
  <div class="flow-step"><span class="flow-index">4</span><div><b>Molecular module:</b> targeted PCR/gap-PCR/ARMS-PCR matching, virtual gel, allele confidence, and Punnett risk modeling.</div></div>
</div>
""",
    unsafe_allow_html=True,
)

section("Embedded demo population", "Use the built-in data to verify dashboard behavior before uploading local laboratory data.")
demo = analyze_dataframe(example_screening_dataframe())
left, right = st.columns([1.1, 0.9])
with left:
    st.plotly_chart(population_sankey(demo), use_container_width=True)
with right:
    st.plotly_chart(batch_mcv_hba2_scatter(demo), use_container_width=True)

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
