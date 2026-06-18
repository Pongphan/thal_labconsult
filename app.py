from __future__ import annotations

import streamlit as st
from thalab.core import analyze_dataframe, example_screening_dataframe
from thalab.styles import disclaimer, hero, inject_css, metric_card, pills, section, sidebar_brand
from thalab.viz import batch_mcv_hba2_scatter, population_sankey

st.set_page_config(page_title="Thal Lab Consult Expert", page_icon="🩸", layout="wide")
inject_css()
sidebar_brand("Command center")

hero(
    "Thalassemia Laboratory Consult — Expert Edition",
    "A hematology-focused Streamlit application for thalassemia screening interpretation, reflex-test planning, PCR allele matching, virtual gel review, and reproductive-risk consultation.",
    "Expert web application blueprint",
)
disclaimer()

c1, c2, c3, c4 = st.columns(4)
with c1: metric_card("Modules", "2", "Screening consult + PCR allele matching", "info")
with c2: metric_card("Visual layers", "12+", "Gauge, radar, Sankey, HPLC, gel, heatmap", "high")
with c3: metric_card("Allele targets", "18", "α- and β-globin demo knowledge base", "moderate")
with c4: metric_card("Batch ready", "CSV", "Population dashboard + downloads", "low")

section("Clinical laboratory workflow", "The app follows a practical sequence: screen, interpret, reflex, genotype, and counsel.")
st.markdown("""
<div class="glass-card">
  <div class="flow-step"><span class="flow-index">1</span><div><b>Screening layer:</b> CBC indices, smear clues, OF/DCIP, ferritin, HbA/HbA2/HbF/HbE fractions.</div></div>
  <div class="flow-step"><span class="flow-index">2</span><div><b>Interpretive engine:</b> weighted laboratory rules for β-thalassemia trait, α-thalassemia/HbH pattern, HbE, and iron deficiency.</div></div>
  <div class="flow-step"><span class="flow-index">3</span><div><b>Reflex planning:</b> HBB panel/sequencing, HBA1/HBA2 deletion-duplication, HbE confirmation, partner testing.</div></div>
  <div class="flow-step"><span class="flow-index">4</span><div><b>PCR allele module:</b> targeted PCR/gap-PCR/ARMS-PCR matching, virtual gel, allele confidence, and Punnett risk modeling.</div></div>
</div>
""", unsafe_allow_html=True)

section("Embedded demo population")
demo = analyze_dataframe(example_screening_dataframe())
left, right = st.columns([1.1, .9])
with left: st.plotly_chart(population_sankey(demo), use_container_width=True)
with right: st.plotly_chart(batch_mcv_hba2_scatter(demo), use_container_width=True)

section("Open a module")
col_a, col_b = st.columns(2)
with col_a:
    st.markdown('<div class="dense-card"><h3>🧪 Page 1 — Laboratory Screening Test</h3><p>CBC/Hb typing consult dashboard, single-patient and batch CSV modes, HPLC-like visualization, phenotype radar, MCV–HbA2 quadrant, and reflex Sankey workflow.</p></div>', unsafe_allow_html=True)
    st.page_link("pages/1_Laboratory_Screening_Test.py", label="Go to laboratory screening", icon="🧪")
with col_b:
    st.markdown('<div class="dense-card"><h3>🧬 Page 2 — PCR for Allele Matching</h3><p>Allele knowledge base, PCR band matching, virtual gel viewer, confidence lollipop plot, and α/β-globin couple-risk Punnett engine.</p></div>', unsafe_allow_html=True)
    st.page_link("pages/2_PCR_Allele_Matching.py", label="Go to PCR allele matching", icon="🧬")

section("Design emphasis")
pills(["hematology color system", "card layout", "explainable scoring", "stunning Plotly analytics", "downloadable report", "batch-ready"], "red")
st.caption("For production deployment, validate all thresholds against local SOPs, instrument platform behavior, and population-specific allele frequencies.")
