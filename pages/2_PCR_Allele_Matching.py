from __future__ import annotations

import pandas as pd
import streamlit as st
from thalab.genetics import ALPHA_GENOTYPES, BETA_GENOTYPES, allele_dataframe, match_pcr_bands, pcr_template, punnett, summarize_risk
from thalab.styles import clinical_box, disclaimer, hero, inject_css, metric_card, section, sidebar_brand
from thalab.viz import allele_method_bar, allele_sunburst, pcr_confidence_lollipop, punnett_heatmap, punnett_sunburst, risk_probability_bar, virtual_gel

st.set_page_config(page_title="PCR Allele Matching | Thal Lab Consult", page_icon="🧬", layout="wide")
inject_css(); sidebar_brand("PCR allele matching")
hero("Page 2 — PCR for Allele Matching", "Expert molecular workspace for α/β-globin targeted PCR, gap-PCR, ARMS-PCR band review, allele-confidence scoring, virtual gel visualization, and couple reproductive-risk analysis.", "Molecular confirmation + genotype-risk engine")
disclaimer()

tabs = st.tabs(["Allele knowledge base", "PCR band matching", "Couple genotype risk"])
with tabs[0]:
    section("Expert allele knowledge base", "The built-in panel is a demonstration-ready Southeast Asia–oriented target set. Replace or extend it with your validated laboratory SOP panel before production use.")
    db=allele_dataframe(); c1,c2,c3,c4=st.columns(4)
    with c1: metric_card("Total targets", str(len(db)), "α/β globin targets", "info")
    with c2: metric_card("α-globin", str(int((db["system"]=="alpha").sum())), "HBA deletion + nondeletional targets", "moderate")
    with c3: metric_card("β-globin", str(int((db["system"]=="beta").sum())), "HBB structural/β0/β+ targets", "high")
    with c4: metric_card("Panel type", "Targeted", "Gap-PCR / ARMS / sequencing-ready", "low")
    left,right=st.columns([1.1,.9])
    with left: st.plotly_chart(allele_sunburst(db), use_container_width=True)
    with right: st.plotly_chart(allele_method_bar(db), use_container_width=True)
    f1,f2,f3=st.columns(3)
    with f1: sys_filter=st.multiselect("System", sorted(db["system"].unique()), default=sorted(db["system"].unique()))
    with f2: class_filter=st.multiselect("Variant class", sorted(db["variant_class"].unique()), default=sorted(db["variant_class"].unique()))
    with f3: method_filter=st.multiselect("Method", sorted(db["method"].unique()), default=sorted(db["method"].unique()))
    view=db[db["system"].isin(sys_filter)&db["variant_class"].isin(class_filter)&db["method"].isin(method_filter)]
    st.dataframe(view, use_container_width=True, hide_index=True); st.download_button("Download allele knowledge base CSV", db.to_csv(index=False).encode("utf-8"), "thalassemia_allele_knowledge_base.csv", "text/csv")

with tabs[1]:
    section("PCR band/call matching", "Upload gel-review output, ARMS-PCR call sheet, or use the built-in example. Matching uses target code, expected bp, operator call, and configurable band tolerance.")
    template=pcr_template(); st.download_button("Download PCR input template", template.to_csv(index=False).encode("utf-8"), "pcr_band_matching_template.csv", "text/csv")
    uploaded=st.file_uploader("Upload PCR band/call CSV", type=["csv"], key="pcr_upload"); tolerance=st.slider("Band-size tolerance (bp)",5,100,25,5)
    pcr_df=pd.read_csv(uploaded) if uploaded is not None else template; matched=match_pcr_bands(pcr_df,tolerance_bp=tolerance); detected_n=int(matched.get("detected",pd.Series(dtype=bool)).sum())
    c1,c2,c3,c4=st.columns(4)
    with c1: metric_card("Rows reviewed", str(len(matched)), "PCR targets/lane calls", "info")
    with c2: metric_card("Detected", str(detected_n), "Operator-positive or band matched", "high" if detected_n else "low")
    with c3: metric_card("Median confidence", f"{matched['confidence'].median()*100:.0f}%", "Allele-call confidence", "moderate")
    with c4: metric_card("Tolerance", f"±{tolerance} bp", "Band-size window", "info")
    st.dataframe(matched, use_container_width=True, hide_index=True); st.download_button("Download PCR matching results", matched.to_csv(index=False).encode("utf-8"), "pcr_allele_matching_results.csv", "text/csv")
    v1,v2=st.columns([1.1,.9])
    with v1: st.plotly_chart(virtual_gel(matched), use_container_width=True)
    with v2: st.plotly_chart(pcr_confidence_lollipop(matched), use_container_width=True)
    detected=matched[matched["detected"]==True]
    if len(detected): clinical_box("<b>Detected allele summary</b><br>"+"<br>".join([f"• {r.sample_id}: {r.common_name} ({r.variant_class}, {r.confidence*100:.0f}% confidence)" for r in detected.itertuples()]), "warn")
    else: clinical_box("No target-positive PCR calls were detected in the current table. Review control lanes and upload formatting before final reporting.", "success")

with tabs[2]:
    section("Couple genotype reproductive-risk engine", "Select inferred/confirmed parental genotypes. The engine computes 2×2 gamete combinations, phenotype class, and offspring-risk probabilities.")
    system=st.radio("Globin system", ["alpha","beta"], horizontal=True); genotype_db=ALPHA_GENOTYPES if system=="alpha" else BETA_GENOTYPES
    c1,c2=st.columns(2)
    with c1: p1_label=st.selectbox("Parent 1 genotype", list(genotype_db.keys()), index=3 if system=="alpha" else 1)
    with c2: p2_label=st.selectbox("Parent 2 genotype", list(genotype_db.keys()), index=1 if system=="alpha" else 2)
    p1,p2=genotype_db[p1_label],genotype_db[p2_label]; result=punnett(p1,p2,system); risk=summarize_risk(result); high_risk=risk.get("critical",0)+risk.get("high",0)
    k1,k2,k3,k4=st.columns(4)
    with k1: metric_card("Parent 1 gametes", " / ".join(p1), p1_label, "info")
    with k2: metric_card("Parent 2 gametes", " / ".join(p2), p2_label, "info")
    with k3: metric_card("High/Critical risk", f"{high_risk:.0f}%", "Offspring probability", "high" if high_risk else "low")
    with k4: metric_card("Genotype outcomes", str(result["offspring_genotype"].nunique()), "Unique offspring genotypes", "moderate")
    st.dataframe(result, use_container_width=True, hide_index=True); st.download_button("Download couple-risk table", result.to_csv(index=False).encode("utf-8"), f"{system}_globin_couple_risk.csv", "text/csv")
    a,b=st.columns([1.1,.9])
    with a: st.plotly_chart(punnett_heatmap(result,p1,p2,system), use_container_width=True)
    with b: st.plotly_chart(risk_probability_bar(result), use_container_width=True)
    st.plotly_chart(punnett_sunburst(result), use_container_width=True)
    if high_risk>0: clinical_box(f"<b>Genetic counseling alert:</b> selected parental genotypes produce {high_risk:.0f}% high/critical offspring risk in this simplified Mendelian model. Confirm genotype calls and refer for formal counseling before clinical action.", "danger")
    else: clinical_box("No high/critical offspring-risk class was generated from the selected genotype pair. This does not exclude other hemoglobinopathies outside the selected panel.", "success")
