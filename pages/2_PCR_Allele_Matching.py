from __future__ import annotations

from typing import Sequence

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from thalab.genetics import (
    ALPHA_GENOTYPES,
    BETA_GENOTYPES,
    allele_dataframe,
    punnett,
    summarize_risk,
)
from thalab.styles import (
    clinical_box,
    current_theme_type,
    disclaimer,
    hero,
    inject_css,
    metric_card,
    section,
    production_footer,
    top_navigation,
)
from thalab.viz import (
    allele_method_bar,
    risk_probability_bar,
)


# -----------------------------------------------------------------------------
# Page configuration and design system
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="PCR Allele Matching | Thal Lab Consult",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
top_navigation("PCR allele matching")


HEM_COLORS = {
    "bg": "#11040A",
    "card": "rgba(36, 8, 18, 0.78)",
    "card2": "rgba(59, 13, 29, 0.72)",
    "blood": "#B31237",
    "blood2": "#E43455",
    "plasma": "#FFC857",
    "marrow": "#F85E7B",
    "cyan": "#4DE1FF",
    "blue": "#7B61FF",
    "green": "#2CEAA3",
    "amber": "#F9A03F",
    "muted": "#BFA7B1",
    "grid": "rgba(255,255,255,0.11)",
    "paper": "rgba(0,0,0,0)",
}

def inject_expert_css() -> None:
    """Additional page-local CSS for a hematology command-center feel."""
    st.markdown(
        """
        <style>
        :root {
            --pcr-border: rgba(63,2,8,.14);
            --pcr-soft-border: rgba(177,18,38,.13);
            --pcr-panel-bg: linear-gradient(145deg, rgba(255,255,255,.92), rgba(255,241,244,.84));
            --pcr-step-bg: linear-gradient(135deg, rgba(255,255,255,.96), rgba(255,236,240,.74));
            --pcr-hero-bg:
              radial-gradient(circle at top left, rgba(255,200,87,.20), transparent 32%),
              radial-gradient(circle at top right, rgba(77,225,255,.13), transparent 30%),
              linear-gradient(145deg, rgba(255,253,253,.98), rgba(255,235,240,.91));
            --pcr-heading: #3F0208;
            --pcr-text: #4F3640;
            --pcr-muted: #7B6570;
            --pcr-shadow: rgba(63,2,8,.11);
            --pcr-tab-bg: linear-gradient(135deg, rgba(179,18,55,.10), rgba(123,97,255,.08));
        }
        div[data-testid="stTabs"] button[role="tab"] {
            border-radius: 999px !important;
            border: 1px solid var(--pcr-soft-border) !important;
            padding: .58rem 1.08rem !important;
            background: var(--pcr-tab-bg);
            color: var(--pcr-heading);
            margin-right: .35rem;
        }
        div[data-testid="stTabs"] button[aria-selected="true"] {
            background: linear-gradient(135deg, #B31237, #7B61FF) !important;
            color: #fff !important;
            box-shadow: 0 0 26px rgba(227,52,85,.30);
        }
        .molecular-hero {
            padding: 1rem 1.15rem;
            border: 1px solid var(--pcr-border);
            border-radius: 24px;
            background: var(--pcr-hero-bg);
            box-shadow: 0 18px 60px var(--pcr-shadow);
            margin-bottom: .8rem;
        }
        .molecular-hero h3 { margin: 0 0 .35rem 0; letter-spacing: -.02em; color: var(--pcr-heading); }
        .molecular-hero p { margin: 0; color: var(--pcr-text); }
        .pcr-stepper {
            display: grid;
            grid-template-columns: repeat(3, minmax(120px, 1fr));
            gap: .7rem;
            margin: .4rem 0 1.1rem 0;
        }
        .pcr-step {
            border-radius: 18px;
            padding: .82rem .9rem;
            border: 1px solid var(--pcr-soft-border);
            background: var(--pcr-step-bg);
        }
        .pcr-step b { color: var(--pcr-heading); display: block; margin-bottom: .25rem; }
        .pcr-step span { color: var(--pcr-text); font-size: .86rem; }
        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: .42rem;
            border-radius: 999px;
            padding: .38rem .68rem;
            border: 1px solid var(--pcr-soft-border);
            margin: .15rem .2rem .15rem 0;
            font-size: .86rem;
            background: var(--pcr-step-bg);
        }
        .pill-high { background: rgba(227,52,85,.16); color: #8D0718; }
        .pill-moderate { background: rgba(255,200,87,.24); color: #765006; }
        .pill-low { background: rgba(44,234,163,.18); color: #07513E; }
        .glass-panel {
            border: 1px solid var(--pcr-soft-border);
            border-radius: 24px;
            padding: 1rem 1.1rem;
            background: var(--pcr-panel-bg);
            box-shadow: inset 0 1px 0 rgba(255,255,255,.24), 0 14px 42px var(--pcr-shadow);
            margin-bottom: .7rem;
        }
        .glass-panel h4 { margin-top: 0; margin-bottom: .35rem; color: var(--pcr-heading); }
        .glass-panel p { margin-bottom: 0; color: var(--pcr-text); }
        .mini-caption { color: var(--pcr-muted); font-size: .84rem; margin-top: -.2rem; }
        .dataframe th { font-size: 12px !important; }

        @media (prefers-color-scheme: dark) {
            :root {
                --pcr-border: rgba(255,255,255,.14);
                --pcr-soft-border: rgba(255,255,255,.13);
                --pcr-panel-bg: linear-gradient(145deg, rgba(59,13,29,.78), rgba(21,4,12,.64));
                --pcr-step-bg: linear-gradient(135deg, rgba(255,255,255,.07), rgba(255,255,255,.025));
                --pcr-hero-bg:
                  radial-gradient(circle at top left, rgba(255,200,87,.18), transparent 32%),
                  radial-gradient(circle at top right, rgba(77,225,255,.16), transparent 30%),
                  linear-gradient(145deg, rgba(41,6,19,.95), rgba(16,2,9,.82));
                --pcr-heading: #FFFFFF;
                --pcr-text: rgba(255,255,255,.76);
                --pcr-muted: rgba(255,255,255,.62);
                --pcr-shadow: rgba(0,0,0,.33);
                --pcr-tab-bg: linear-gradient(135deg, rgba(179,18,55,.22), rgba(123,97,255,.12));
            }
            .pill-high { color: #FFD6DE; }
            .pill-moderate { color: #FFE7A8; }
            .pill-low { color: #C9FFE9; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _theme_layout(fig: go.Figure, title: str | None = None, height: int = 430) -> go.Figure:
    dark = current_theme_type() == "dark"
    text = "rgba(255,255,255,0.88)" if dark else "#2F1720"
    grid = "rgba(255,255,255,0.11)" if dark else "rgba(63,2,8,.11)"
    plot_bg = "rgba(17,4,10,0.68)" if dark else "rgba(255,248,250,.72)"
    fig.update_layout(
        template="plotly_dark" if dark else "plotly_white",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=plot_bg,
        margin=dict(l=35, r=25, t=72 if title else 40, b=38),
        title=dict(text=title or "", x=0.02, xanchor="left", font=dict(size=20, color=text)),
        font=dict(family="Inter, Segoe UI, Arial", color=text),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0)",
        ),
        hoverlabel=dict(
            bgcolor="#1A0710" if dark else "#FFF8FA",
            bordercolor="rgba(255,255,255,.18)" if dark else "rgba(63,2,8,.18)",
            font=dict(color=text, size=12),
        ),
    )
    fig.update_xaxes(gridcolor=grid, zerolinecolor=grid)
    fig.update_yaxes(gridcolor=grid, zerolinecolor=grid)
    return fig


def _chart_neutrals() -> dict[str, str]:
    if current_theme_type() == "dark":
        return {
            "root": "rgba(255,255,255,.06)",
            "border": "rgba(255,255,255,.18)",
            "strong_border": "rgba(255,255,255,.92)",
            "soft_fill": "rgba(255,255,255,.035)",
            "muted_fill": "rgba(255,255,255,.18)",
            "muted_text": "rgba(255,255,255,.58)",
            "guide": "rgba(255,255,255,.10)",
            "gauge_bg": "rgba(255,255,255,.06)",
            "tick": "rgba(255,255,255,.60)",
            "text": "white",
        }
    return {
        "root": "rgba(63,2,8,.05)",
        "border": "rgba(63,2,8,.18)",
        "strong_border": "rgba(63,2,8,.78)",
        "soft_fill": "rgba(177,18,38,.035)",
        "muted_fill": "rgba(63,2,8,.16)",
        "muted_text": "rgba(63,2,8,.62)",
        "guide": "rgba(63,2,8,.10)",
        "gauge_bg": "rgba(177,18,38,.05)",
        "tick": "rgba(63,2,8,.62)",
        "text": "#2F1720",
    }


def _safe_col(df: pd.DataFrame, candidates: Sequence[str], fallback: str | None = None) -> str | None:
    for col in candidates:
        if col in df.columns:
            return col
    return fallback


def _num(series: pd.Series, default: float = np.nan) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(default)


def workflow_stepper() -> None:
    st.markdown(
        """
        <div class="pcr-stepper">
            <div class="pcr-step"><b>1 · Panel design</b><span>Targeted α/β variant knowledge base</span></div>
            <div class="pcr-step"><b>2 · Risk modeling</b><span>Parental gametes and offspring genotypes</span></div>
            <div class="pcr-step"><b>3 · Counseling view</b><span>Phenotype and reproductive-risk classes</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def molecular_panel(title: str, body: str) -> None:
    st.markdown(f'<div class="glass-panel"><h4>{title}</h4><p>{body}</p></div>', unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Data preparation helpers
# -----------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def cached_allele_database() -> pd.DataFrame:
    db = allele_dataframe().copy()
    for col in ["system", "variant_class", "method", "common_name", "target_code"]:
        if col not in db.columns:
            db[col] = "Unknown"
    return db


# -----------------------------------------------------------------------------
# Visualizations: Allele knowledge base
# -----------------------------------------------------------------------------


def panel_coverage_treemap(db: pd.DataFrame) -> go.Figure:
    neutral = _chart_neutrals()
    label_col = _safe_col(db, ["common_name", "target_code", "variant_class"], "variant_class")
    fig = px.treemap(
        db,
        path=["system", "variant_class", "method", label_col],
        values=None,
        color="system",
        color_discrete_map={"alpha": HEM_COLORS["cyan"], "beta": HEM_COLORS["blood2"]},
        hover_data=[c for c in ["target_code", "expected_bp", "clinical_relevance"] if c in db.columns],
    )
    fig.update_traces(
        marker=dict(cornerradius=7),
        textinfo="label+value",
        root_color=neutral["root"],
    )
    return _theme_layout(fig, "Molecular panel coverage map", 520)


def allele_lollipop(db: pd.DataFrame) -> go.Figure:
    neutral = _chart_neutrals()
    bp_col = _safe_col(db, ["expected_bp", "amplicon_bp", "bp"], None)
    label_col = _safe_col(db, ["common_name", "target_code"], "variant_class")
    plot_df = db.copy()
    if bp_col is None or plot_df[bp_col].isna().all():
        plot_df["_bp"] = np.arange(len(plot_df)) * 70 + 120
        bp_col = "_bp"
    plot_df[bp_col] = _num(plot_df[bp_col])
    plot_df = plot_df.sort_values(bp_col).tail(35)
    fig = go.Figure()
    color_map = {"alpha": HEM_COLORS["cyan"], "beta": HEM_COLORS["blood2"]}
    for system, g in plot_df.groupby("system", dropna=False):
        fig.add_trace(
            go.Scatter(
                x=g[bp_col],
                y=g[label_col].astype(str),
                mode="markers+lines",
                line=dict(width=2, color=color_map.get(system, HEM_COLORS["plasma"])),
                marker=dict(size=12, color=color_map.get(system, HEM_COLORS["plasma"]), line=dict(color=neutral["strong_border"], width=1)),
                name=str(system),
                hovertemplate="%{y}<br>Expected size: %{x:.0f} bp<extra></extra>",
            )
        )
    fig.update_xaxes(title="Expected amplicon size (bp)")
    fig.update_yaxes(title="Target", automargin=True)
    return _theme_layout(fig, "Amplicon-size lollipop panel", 620)


# -----------------------------------------------------------------------------
# Visualizations: couple genotype risk
# -----------------------------------------------------------------------------


def _risk_col(result: pd.DataFrame) -> str | None:
    return _safe_col(result, ["risk_class", "risk_level", "severity", "risk", "clinical_risk"], None)


def genotype_outcome_sunburst(result: pd.DataFrame) -> go.Figure:
    neutral = _chart_neutrals()
    work = result.copy()
    geno_col = _safe_col(work, ["offspring_genotype", "genotype", "child_genotype"], work.columns[-1])
    pheno_col = _safe_col(work, ["phenotype", "offspring_phenotype", "clinical_phenotype"], geno_col)
    risk_col = _risk_col(work)
    if risk_col is None:
        work["risk_class"] = "review"
        risk_col = "risk_class"
    count = work.groupby([risk_col, pheno_col, geno_col], dropna=False).size().reset_index(name="count")
    fig = px.sunburst(
        count,
        path=[risk_col, pheno_col, geno_col],
        values="count",
        color=risk_col,
        color_discrete_map={
            "none": HEM_COLORS["green"],
            "low": HEM_COLORS["green"],
            "carrier": HEM_COLORS["green"],
            "moderate": HEM_COLORS["amber"],
            "high": HEM_COLORS["marrow"],
            "critical": HEM_COLORS["blood2"],
            "lethal": HEM_COLORS["blood"],
        },
    )
    fig.update_traces(insidetextorientation="radial", marker=dict(line=dict(color=neutral["border"], width=1)))
    return _theme_layout(fig, "Offspring genotype hierarchy", 520)


def risk_probability_donut(result: pd.DataFrame) -> go.Figure:
    neutral = _chart_neutrals()
    work = result.copy()
    risk_col = _risk_col(work)
    if risk_col is None:
        work["risk_class"] = "review"
        risk_col = "risk_class"
    if "probability" in work.columns:
        agg = work.groupby(risk_col, dropna=False)["probability"].sum().reset_index(name="probability")
    else:
        agg = work.groupby(risk_col, dropna=False).size().reset_index(name="probability")
        agg["probability"] = agg["probability"] / agg["probability"].sum() * 100
    if agg["probability"].max() <= 1.1:
        agg["probability"] *= 100
    fig = go.Figure(
        data=[
            go.Pie(
                labels=agg[risk_col].astype(str),
                values=agg["probability"],
                hole=0.58,
                textinfo="label+percent",
                marker=dict(line=dict(color=neutral["border"], width=1)),
            )
        ]
    )
    fig.add_annotation(text="Risk<br>probability", x=0.5, y=0.5, showarrow=False, font=dict(size=18, color=neutral["text"]))
    return _theme_layout(fig, "Offspring-risk distribution", 440)


def genotype_evidence_table(result: pd.DataFrame) -> pd.DataFrame:
    keep = [
        c
        for c in [
            "parent1_gamete",
            "parent2_gamete",
            "offspring_genotype",
            "phenotype",
            "risk_class",
            "risk_level",
            "probability",
        ]
        if c in result.columns
    ]
    return result[keep] if keep else result


# -----------------------------------------------------------------------------
# Page body
# -----------------------------------------------------------------------------

inject_expert_css()
hero(
    "ThalLink: Thalassemia Laboratory Intelligence Platform",
    "A molecular hematology command center for α/β-globin panel intelligence and reproductive-risk visualization.",
    "Molecular confirmation + genotype-risk engine",
)
disclaimer()
workflow_stepper()

st.markdown(
    """
    <div class="molecular-hero">
      <h3>Molecular panel and counseling workspace</h3>
      <p>Review α/β-globin target coverage, laboratory methods, allele nomenclature, and counseling-ready reproductive-risk analytics.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Global data objects
db = cached_allele_database()

tabs = st.tabs(["🧬 Panel intelligence", "👪 Couple genotype risk", "📤 Export report"])


# -----------------------------------------------------------------------------
# Tab 1: Allele knowledge base
# -----------------------------------------------------------------------------
with tabs[0]:
    section(
        "Molecular panel intelligence",
        "Explore whether the current α/β-globin panel is balanced across variant systems, variant classes, and laboratory methods before reviewing patient bands.",
    )

    total_targets = len(db)
    alpha_n = int((db["system"].astype(str).str.lower() == "alpha").sum())
    beta_n = int((db["system"].astype(str).str.lower() == "beta").sum())
    methods_n = db["method"].nunique(dropna=True)
    classes_n = db["variant_class"].nunique(dropna=True)

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        metric_card("Total targets", str(total_targets), "Validated panel entries", "info")
    with m2:
        metric_card("α-globin", str(alpha_n), "HBA deletion/nondeletion", "moderate")
    with m3:
        metric_card("β-globin", str(beta_n), "HBB β0/β+/structural", "high")
    with m4:
        metric_card("Methods", str(methods_n), "Gap-PCR / ARMS / sequencing", "low")
    with m5:
        metric_card("Classes", str(classes_n), "Variant categories", "info")

    control_left, control_right = st.columns([1.2, 0.8])
    with control_left:
        search = st.text_input("Search target, allele, method, or class", value="", placeholder="e.g., HbE, SEA, CD41/42, gap-PCR")
    with control_right:
        sort_mode = st.selectbox("Prioritize table by", ["system", "variant_class", "method", "common_name"], index=1)

    f1, f2, f3 = st.columns(3)
    with f1:
        sys_filter = st.multiselect("Globin system", sorted(db["system"].dropna().astype(str).unique()), default=sorted(db["system"].dropna().astype(str).unique()))
    with f2:
        class_filter = st.multiselect("Variant class", sorted(db["variant_class"].dropna().astype(str).unique()), default=sorted(db["variant_class"].dropna().astype(str).unique()))
    with f3:
        method_filter = st.multiselect("Method", sorted(db["method"].dropna().astype(str).unique()), default=sorted(db["method"].dropna().astype(str).unique()))

    view = db[
        db["system"].astype(str).isin(sys_filter)
        & db["variant_class"].astype(str).isin(class_filter)
        & db["method"].astype(str).isin(method_filter)
    ].copy()
    if search.strip():
        query = search.strip().lower()
        mask = view.astype(str).apply(lambda col: col.str.lower().str.contains(query, na=False)).any(axis=1)
        view = view[mask]
    if sort_mode in view.columns:
        view = view.sort_values([sort_mode])

    st.plotly_chart(panel_coverage_treemap(view if len(view) else db), use_container_width=True, theme=None)

    c3, c4 = st.columns([1, 1])
    with c3:
        st.plotly_chart(allele_lollipop(view if len(view) else db), use_container_width=True, theme=None)
    with c4:
        # Keep original project visual for compatibility, but place it as a secondary view.
        try:
            st.plotly_chart(allele_method_bar(view if len(view) else db), use_container_width=True, theme=None)
        except Exception:
            st.plotly_chart(panel_coverage_treemap(view if len(view) else db), use_container_width=True, theme=None)

    molecular_panel(
        "Usability note",
        "Before adopting this page in a production laboratory, replace the demonstration allele panel with your locally validated SOP panel, positive controls, primer lot information, and reporting nomenclature.",
    )
    st.dataframe(view, use_container_width=True, hide_index=True)
    st.download_button(
        "⬇️ Download filtered allele knowledge base CSV",
        view.to_csv(index=False).encode("utf-8"),
        "thalassemia_filtered_allele_knowledge_base.csv",
        "text/csv",
        use_container_width=True,
    )


# -----------------------------------------------------------------------------
# Tab 2: Couple genotype risk
# -----------------------------------------------------------------------------
with tabs[1]:
    section(
        "Couple genotype reproductive-risk board",
        "Select confirmed or inferred parental genotypes. The board converts gamete combinations into offspring genotype, phenotype, and risk-class visual analytics.",
    )

    system = st.radio("Globin system", ["alpha", "beta"], horizontal=True)
    genotype_db = ALPHA_GENOTYPES if system == "alpha" else BETA_GENOTYPES
    genotype_labels = list(genotype_db.keys())

    c1, c2 = st.columns(2)
    with c1:
        default_p1 = min(3, len(genotype_labels) - 1) if system == "alpha" else min(1, len(genotype_labels) - 1)
        p1_label = st.selectbox("Parent 1 genotype", genotype_labels, index=default_p1)
    with c2:
        default_p2 = min(1, len(genotype_labels) - 1) if system == "alpha" else min(2, len(genotype_labels) - 1)
        p2_label = st.selectbox("Parent 2 genotype", genotype_labels, index=default_p2)

    p1, p2 = genotype_db[p1_label], genotype_db[p2_label]
    result = punnett(p1, p2, system).copy()
    risk = summarize_risk(result)
    high_risk = float(risk.get("critical", 0) + risk.get("high", 0))
    any_risk = sum(v for v in risk.values()) if risk else 0

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        metric_card("Parent 1 gametes", " / ".join(map(str, p1)), p1_label, "info")
    with k2:
        metric_card("Parent 2 gametes", " / ".join(map(str, p2)), p2_label, "info")
    with k3:
        metric_card("High/Critical", f"{high_risk:.0f}%", "Offspring probability", "high" if high_risk else "low")
    with k4:
        metric_card("Outcomes", str(result.shape[0]), "Gamete combinations", "moderate")
    with k5:
        metric_card("Risk classes", str(len(risk)), "Phenotype groups", "info")

    st.plotly_chart(risk_probability_donut(result), use_container_width=True, theme=None)

    r3, r4 = st.columns([1, 1])
    with r3:
        try:
            st.plotly_chart(risk_probability_bar(result), use_container_width=True, theme=None)
        except Exception:
            st.plotly_chart(risk_probability_donut(result), use_container_width=True, theme=None)
    with r4:
        st.plotly_chart(genotype_outcome_sunburst(result), use_container_width=True, theme=None)

    with st.expander("Offspring genotype evidence table", expanded=True):
        risk_table = genotype_evidence_table(result)
        st.dataframe(risk_table, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ Download couple-risk table",
            result.to_csv(index=False).encode("utf-8"),
            f"{system}_globin_couple_risk_expert.csv",
            "text/csv",
            use_container_width=True,
        )

    if high_risk > 0:
        clinical_box(
            f"<b>Genetic counseling alert:</b> selected parental genotypes produce {high_risk:.0f}% high/critical offspring risk in this simplified Mendelian model. Confirm genotype calls, verify phase, and refer for formal genetic counseling before clinical action.",
            "danger",
        )
    else:
        clinical_box(
            "No high/critical offspring-risk class was generated from the selected genotype pair. This does not exclude variants outside the selected panel, compound heterozygosity not represented in the demonstration database, or non-thalassemia hemoglobinopathies.",
            "success",
        )


# -----------------------------------------------------------------------------
# Tab 3: Export/report area
# -----------------------------------------------------------------------------
with tabs[2]:
    section(
        "Export-ready molecular consult package",
        "This tab summarizes which objects should be reviewed before integrating the page into a laboratory report workflow.",
    )

    molecular_panel(
        "Recommended production hardening",
        "Add laboratory-specific primer panels, control-lane QC rules, local HGVS/HbVar nomenclature, audit logs, user authentication, and LIS/LIMS export fields before clinical deployment.",
    )

    report_items = pd.DataFrame(
        [
            {"Module": "Allele panel", "Export": "CSV", "Purpose": "Validated target list and method coverage"},
            {"Module": "Couple risk", "Export": "CSV", "Purpose": "Punnett genotype/phenotype/risk evidence table"},
            {"Module": "Consult note", "Export": "HTML/PDF extension recommended", "Purpose": "Molecular interpretation and genetic-counseling prompt"},
        ]
    )
    st.dataframe(report_items, use_container_width=True, hide_index=True)

    st.markdown(
        """
        **Suggested next enhancement:** add a one-click molecular consult report generator with these sections: assay panel, allele interpretation, reproductive-risk summary, limitations, and sign-out block.
        """
    )



production_footer()
