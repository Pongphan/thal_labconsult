# Thalassemia Laboratory Consult — Expert Streamlit Edition

A complete expert-level Streamlit web application for laboratory consultation in thalassemia screening and PCR allele matching.

## Main modules

### Page 1 — Laboratory Screening Test
- Hematology card-based UI with blood/plasma/marrow visual theme.
- Single-patient consult form and batch CSV dashboard.
- CBC, iron profile, OF/DCIP, HbH inclusion, HbA/HbA2/HbF/HbE fields.
- Explainable weighted scores for β-thalassemia trait, α-thalassemia/HbH pattern, HbE/β-globin structural variants, and iron deficiency/mixed microcytosis.
- Plotly visual analytics: consult gauge, radar, Hb donut, HPLC-like chromatogram, MCV–HbA2 quadrant, CBC reference bullet bars, evidence waterfall, reflex Sankey, batch heatmap, and phenotype map.

### Page 2 — PCR for Allele Matching
- Built-in α/β-globin allele knowledge base.
- Gap-PCR / ARMS-PCR / sequencing-ready demo target database.
- PCR band/call CSV upload, band-size tolerance control, allele-call confidence scoring, virtual PCR gel viewer, confidence lollipop, and couple genotype-risk engine.

## Installation

```bash
cd thalassemia_lab_consult_expert_streamlit
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Data examples
- `data/example_screening.csv`
- `data/example_pcr_panel.csv`

## Production notes
This project is laboratory decision support. Before clinical or public-health use: replace demo thresholds with local SOP thresholds, validate against local analyzer/HPLC/capillary electrophoresis platforms, replace the demo allele database with the validated local molecular panel, validate PCR band-size windows, add authentication/audit trail/LIMS integration/report sign-off, and review interpretation statements by a qualified hematology laboratory professional.
