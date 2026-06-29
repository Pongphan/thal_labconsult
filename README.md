# ThalLink — Real‑World Thalassemia Laboratory Intelligence

A production-oriented Streamlit web application for thalassemia screening interpretation, ML-ready feature export, PCR allele matching, virtual gel review, and couple reproductive-risk visualization.

## What was upgraded

### 1. No-sidebar application shell
- The native Streamlit sidebar and auto page navigation are disabled/hidden.
- Every workspace uses clickable card navigation directly under the page hero.
- The UI is suitable for clinical workstations, tablets, and teaching demonstrations where sidebar navigation is distracting.

### 2. Card-based real-world UX
- Command-center landing page with full-card module launcher links.
- Page-level navigation cards for Command Center, Laboratory Screening, and PCR Allele Matching are rendered immediately below each page hero.
- Navigation uses `st.page_link`, so clicking a card opens the selected workspace in the same browser tab rather than a new tab.
- In-page threshold control cards replaced the previous sidebar sliders.
- Production-readiness cards highlight governance, ML deployment, and LIS/LIMS integration.

### 3. Laboratory Screening Test workspace
- Single-patient consult form.
- Batch CSV dashboard.
- CBC, iron profile, OF/DCIP, HbH inclusion, HbA/HbA2/HbA2E/HbF/HbE interpretation.
- Explainable scores for β-thalassemia trait, α-thalassemia/HbH pattern, HbE/β-globin structural variants, and iron deficiency or mixed microcytosis.
- Plotly analytics: radar, HPLC-like chromatogram, Hb fraction donut, CBC reference bars, reflex Sankey, batch heatmap, and phenotype scatter.
- Downloadable Markdown, JSON, interpreted batch CSV, and ML feature matrix CSV.

### 4. ML-ready layer
- `thalab/ml.py` provides a clean feature matrix for downstream model training/deployment.
- A transparent prototype-similarity layer is included for UI validation and model-replacement planning.
- This layer is **not a calibrated diagnostic ML model**. Replace it with a locally trained and externally validated classifier/regressor when molecular-confirmed labels are available.

### 5. PCR Allele Matching workspace
- α/β-globin allele knowledge base.
- PCR / gap-PCR / ARMS-PCR call-sheet upload and direct editing.
- Band-size tolerance control, allele-call confidence scoring, QC flags, and virtual gel visualization.
- Couple genotype-risk board for α- and β-globin reproductive-risk consultation.

## Installation

```bash
cd thal_labconsult
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

From the repository root you can also run:

```bash
pip install -r thal_labconsult/requirements.txt
streamlit run thal_labconsult/app.py
```

## Streamlit Community Cloud deployment

- Repository: select this repository.
- Main file path: `thal_labconsult/app.py`
- Dependency file: Streamlit will install `thal_labconsult/requirements.txt`.
- Config file: `.streamlit/config.toml` is kept at the repository root, which is where Streamlit Community Cloud reads app configuration for subdirectory apps.

## Data examples

- `data/example_screening.csv`
- `data/example_pcr_panel.csv`

## Main files

```text
app.py                                  # Card-based command center
pages/1_Laboratory_Screening_Test.py    # Screening + ML-ready feature export
pages/2_PCR_Allele_Matching.py          # PCR allele matching + couple risk
thalab/core.py                          # Screening logic and robust import aliases
thalab/ml.py                            # ML-ready feature matrix + prototype similarity
thalab/genetics.py                      # Allele database, PCR matching, Punnett models
thalab/styles.py                        # No-sidebar design system + same-tab card navigation
thalab/viz.py                           # Plotly visual analytics
.streamlit/config.toml                  # Repository-root theme configuration for Streamlit Cloud
```

## Production validation notes

Before clinical deployment, replace demo thresholds and interpretation text with local SOP-approved values, validate against the local analyzer/HPLC/capillary electrophoresis platform, replace the demo molecular panel with a validated laboratory panel, verify PCR band-size tolerance windows, add authentication/audit trail/LIS integration/report sign-off, and have all report language reviewed by qualified hematology laboratory professionals.
