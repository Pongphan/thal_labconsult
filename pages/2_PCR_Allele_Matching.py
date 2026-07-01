from __future__ import annotations

import html
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
            --pcr-border: var(--glass-border);
            --pcr-soft-border: var(--glass-border);
            --pcr-panel-bg: var(--glass-bg);
            --pcr-step-bg: var(--glass-bg-soft);
            --pcr-hero-bg: var(--glass-bg-strong);
            --pcr-heading: var(--heading);
            --pcr-text: var(--secondary-text);
            --pcr-muted: var(--soft-text);
            --pcr-shadow: var(--card-shadow);
            --pcr-tab-bg: rgba(255,255,255,.48);
        }
        div[data-testid="stTabs"] button[role="tab"] {
            border-radius: var(--radius-sm) !important;
            border: 1px solid var(--pcr-soft-border) !important;
            padding: .58rem 1.08rem !important;
            background: var(--pcr-tab-bg);
            color: var(--pcr-heading);
            margin-right: .35rem;
            box-shadow: inset 0 1px 0 var(--glass-highlight);
        }
        div[data-testid="stTabs"] button[aria-selected="true"] {
            background: linear-gradient(135deg, var(--accent-1), var(--accent-2) 58%, var(--accent-3)) !important;
            color: #fff !important;
            box-shadow: 0 14px 34px rgba(15,127,143,.20) !important;
        }
        .molecular-hero {
            padding: 1rem 1.15rem;
            border: 1px solid var(--pcr-border);
            border-radius: var(--radius);
            background: var(--pcr-hero-bg);
            box-shadow: var(--glass-shadow), inset 0 1px 0 var(--glass-highlight);
            backdrop-filter: blur(22px) saturate(1.25);
            -webkit-backdrop-filter: blur(22px) saturate(1.25);
            margin-bottom: .8rem;
        }
        .molecular-hero h3 { margin: 0 0 .35rem 0; letter-spacing: 0; color: var(--pcr-heading); }
        .molecular-hero p { margin: 0; color: var(--pcr-text); }
        .pcr-stepper {
            display: grid;
            grid-template-columns: repeat(3, minmax(120px, 1fr));
            gap: .7rem;
            margin: .4rem 0 1.1rem 0;
        }
        .pcr-step {
            border-radius: var(--radius);
            padding: .82rem .9rem;
            border: 1px solid var(--pcr-soft-border);
            background: var(--pcr-step-bg);
            box-shadow: var(--glass-shadow), inset 0 1px 0 var(--glass-highlight);
            backdrop-filter: blur(18px) saturate(1.2);
            -webkit-backdrop-filter: blur(18px) saturate(1.2);
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
            box-shadow: inset 0 1px 0 var(--glass-highlight);
        }
        .pill-high { background: rgba(227,52,85,.16); color: #8D0718; }
        .pill-moderate { background: rgba(255,200,87,.24); color: #765006; }
        .pill-low { background: rgba(44,234,163,.18); color: #07513E; }
        .glass-panel {
            border: 1px solid var(--pcr-soft-border);
            border-radius: var(--radius);
            padding: 1rem 1.1rem;
            background: var(--pcr-panel-bg);
            box-shadow: var(--glass-shadow), inset 0 1px 0 var(--glass-highlight);
            backdrop-filter: blur(22px) saturate(1.25);
            -webkit-backdrop-filter: blur(22px) saturate(1.25);
            margin-bottom: .7rem;
        }
        .glass-panel h4 { margin-top: 0; margin-bottom: .35rem; color: var(--pcr-heading); }
        .glass-panel p { margin-bottom: 0; color: var(--pcr-text); }
        .mini-caption { color: var(--pcr-muted); font-size: .84rem; margin-top: -.2rem; }
        .coverage-summary {
            display: grid;
            grid-template-columns: repeat(4, minmax(130px, 1fr));
            gap: .65rem;
            margin: .15rem 0 .85rem;
        }
        .coverage-summary__item {
            border: 1px solid var(--pcr-soft-border);
            border-radius: var(--radius);
            padding: .82rem .9rem;
            background: var(--pcr-step-bg);
            box-shadow: var(--glass-shadow), inset 0 1px 0 var(--glass-highlight);
            backdrop-filter: blur(18px) saturate(1.18);
            -webkit-backdrop-filter: blur(18px) saturate(1.18);
        }
        .coverage-summary__label {
            color: var(--pcr-muted);
            font-size: .76rem;
            font-weight: 800;
            letter-spacing: 0;
            text-transform: uppercase;
        }
        .coverage-summary__value {
            color: var(--pcr-heading);
            font-size: 1.35rem;
            font-weight: 850;
            line-height: 1.15;
            margin-top: .18rem;
        }
        .coverage-summary__caption {
            color: var(--pcr-text);
            font-size: .82rem;
            margin-top: .25rem;
            overflow-wrap: anywhere;
        }
        .dataframe th { font-size: 12px !important; }

        @media (prefers-color-scheme: dark) {
            :root {
                --pcr-border: var(--glass-border);
                --pcr-soft-border: var(--glass-border);
                --pcr-panel-bg: var(--glass-bg);
                --pcr-step-bg: var(--glass-bg-soft);
                --pcr-hero-bg: var(--glass-bg-strong);
                --pcr-heading: var(--heading);
                --pcr-text: var(--secondary-text);
                --pcr-muted: var(--soft-text);
                --pcr-shadow: var(--card-shadow);
                --pcr-tab-bg: rgba(255,255,255,.07);
            }
            .pill-high { color: #FFD6DE; }
            .pill-moderate { color: #FFE7A8; }
            .pill-low { color: #C9FFE9; }
        }
        @media (max-width: 900px) {
            .coverage-summary {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }
        @media (max-width: 560px) {
            .coverage-summary {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _theme_layout(fig: go.Figure, title: str | None = None, height: int = 430) -> go.Figure:
    dark = current_theme_type() == "dark"
    text = "#F5FAFC" if dark else "#17212B"
    grid = "rgba(255,255,255,0.12)" if dark else "rgba(36,48,63,.12)"
    plot_bg = "rgba(255,255,255,.04)" if dark else "rgba(255,255,255,.22)"
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
            bgcolor="rgba(16,24,32,.92)" if dark else "rgba(255,255,255,.92)",
            bordercolor="rgba(255,255,255,.18)" if dark else "rgba(36,48,63,.16)",
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
            "treemap_grid": "rgba(255,255,255,.46)",
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
        "treemap_grid": "rgba(36,48,63,.30)",
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


def _escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def coverage_map_summary(db: pd.DataFrame) -> None:
    if db.empty:
        st.markdown(
            """
            <div class="coverage-summary">
                <div class="coverage-summary__item">
                    <div class="coverage-summary__label">Active targets</div>
                    <div class="coverage-summary__value">0</div>
                    <div class="coverage-summary__caption">No targets match the current filters</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    system_counts = db["system"].fillna("unknown").astype(str).value_counts()
    method_counts = db["method"].fillna("unknown").astype(str).value_counts()
    class_counts = db["variant_class"].fillna("unknown").astype(str).value_counts()
    top_method = method_counts.index[0] if not method_counts.empty else "unknown"
    top_method_count = int(method_counts.iloc[0]) if not method_counts.empty else 0
    top_class = class_counts.index[0] if not class_counts.empty else "unknown"
    top_class_count = int(class_counts.iloc[0]) if not class_counts.empty else 0
    system_caption = " / ".join(f"{_escape(system)} {int(count)}" for system, count in system_counts.items())

    st.markdown(
        f"""
        <div class="coverage-summary">
            <div class="coverage-summary__item">
                <div class="coverage-summary__label">Active targets</div>
                <div class="coverage-summary__value">{len(db)}</div>
                <div class="coverage-summary__caption">{_escape(db["target_code"].nunique())} unique target codes</div>
            </div>
            <div class="coverage-summary__item">
                <div class="coverage-summary__label">Globin balance</div>
                <div class="coverage-summary__value">{len(system_counts)}</div>
                <div class="coverage-summary__caption">{system_caption}</div>
            </div>
            <div class="coverage-summary__item">
                <div class="coverage-summary__label">Largest method</div>
                <div class="coverage-summary__value">{_escape(top_method_count)}</div>
                <div class="coverage-summary__caption">{_escape(top_method)}</div>
            </div>
            <div class="coverage-summary__item">
                <div class="coverage-summary__label">Largest class</div>
                <div class="coverage-summary__value">{_escape(top_class_count)}</div>
                <div class="coverage-summary__caption">{_escape(top_class)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


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
    work = db.copy()
    if work.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No molecular targets match the current filters.",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color=neutral["muted_text"]),
        )
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        return _theme_layout(fig, "Molecular panel coverage map", 340)

    label_col = _safe_col(work, ["common_name", "target_code", "variant_class"], "variant_class")
    code_col = _safe_col(work, ["target_code", "common_name"], label_col)
    work["_target_label"] = (
        work[label_col].fillna("Unknown target").astype(str)
        + " ["
        + work[code_col].fillna("NA").astype(str)
        + "]"
    )
    work["_target_count"] = 1
    hover_data: dict[str, bool | str] = {
        "_target_count": False,
        "system": True,
        "variant_class": True,
        "method": True,
        "target_code": True,
    }
    if "expected_bp" in work.columns:
        hover_data["expected_bp"] = ":.0f"

    fig = px.treemap(
        work,
        path=["system", "variant_class", "method", "_target_label"],
        values="_target_count",
        color="system",
        color_discrete_map={
            "alpha": HEM_COLORS["cyan"],
            "beta": HEM_COLORS["blood2"],
            "(?)": neutral["muted_fill"],
        },
        hover_data=hover_data,
    )
    fig.update_traces(
        branchvalues="total",
        marker=dict(
            cornerradius=5,
            line=dict(color=neutral["treemap_grid"], width=2.2),
        ),
        pathbar=dict(
            textfont=dict(color=neutral["text"], size=12),
            thickness=28,
        ),
        selector=dict(type="treemap"),
        textinfo="label+value+percent parent",
        texttemplate="<b>%{label}</b><br>%{value} targets<br>%{percentParent:.0%} of parent",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Targets: %{value}<br>"
            "Share of panel: %{percentRoot:.1%}<br>"
            "Share of parent: %{percentParent:.1%}"
            "<extra></extra>"
        ),
        root_color=neutral["root"],
        tiling=dict(packing="squarify", pad=4),
        maxdepth=4,
    )
    fig.update_layout(
        uniformtext=dict(minsize=11, mode="hide"),
        colorway=[HEM_COLORS["cyan"], HEM_COLORS["blood2"], HEM_COLORS["plasma"], HEM_COLORS["green"]],
    )
    return _theme_layout(fig, "Molecular panel coverage map", 560)


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


def _default_genotype_index(system: str, parent: int, labels: list[str]) -> int:
    if not labels:
        return 0
    if system == "alpha":
        default_index = 3 if parent == 1 else 1
    else:
        default_index = 1 if parent == 1 else 2
    return min(default_index, len(labels) - 1)


def select_parent_genotypes(system: str, genotype_db: dict[str, list[str]]) -> tuple[str, str, list[str], list[str]]:
    labels = list(genotype_db.keys())
    system_label = system.title()
    st.markdown(f"#### {system_label}-globin")
    p1_label = st.selectbox(
        f"{system_label} parent 1 genotype",
        labels,
        index=_default_genotype_index(system, 1, labels),
        key=f"{system}_parent1_genotype",
    )
    p2_label = st.selectbox(
        f"{system_label} parent 2 genotype",
        labels,
        index=_default_genotype_index(system, 2, labels),
        key=f"{system}_parent2_genotype",
    )
    return p1_label, p2_label, genotype_db[p1_label], genotype_db[p2_label]


def render_couple_risk_results(
    system: str,
    p1_label: str,
    p2_label: str,
    p1: list[str],
    p2: list[str],
) -> pd.DataFrame:
    system_label = system.title()
    result = punnett(p1, p2, system).copy()
    risk = summarize_risk(result)
    high_risk = float(risk.get("critical", 0) + risk.get("high", 0))

    section(
        f"{system_label}-globin offspring risk",
        f"Predicted offspring outcomes from the selected {system}-globin parental genotypes.",
    )

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

    st.markdown('<div style="height: 0.85rem;"></div>', unsafe_allow_html=True)
    with st.expander(f"{system_label}-globin offspring genotype evidence table", expanded=True):
        risk_table = genotype_evidence_table(result)
        st.dataframe(risk_table, use_container_width=True, hide_index=True)
        st.download_button(
            f"Download {system}-globin couple-risk table",
            result.to_csv(index=False).encode("utf-8"),
            f"{system}_globin_couple_risk_expert.csv",
            "text/csv",
            use_container_width=True,
            key=f"{system}_risk_download",
        )

    donut_col, sunburst_col = st.columns([1, 1])
    with donut_col:
        st.plotly_chart(risk_probability_donut(result), use_container_width=True, theme=None)
    with sunburst_col:
        st.plotly_chart(genotype_outcome_sunburst(result), use_container_width=True, theme=None)

    if high_risk > 0:
        clinical_box(
            f"<b>Genetic counseling alert:</b> selected {system}-globin parental genotypes produce {high_risk:.0f}% high/critical offspring risk in this simplified Mendelian model. Confirm genotype calls, verify phase, and refer for formal genetic counseling before clinical action.",
            "danger",
        )
    else:
        clinical_box(
            f"No high/critical offspring-risk class was generated from the selected {system}-globin genotype pair. This does not exclude variants outside the selected panel, compound heterozygosity not represented in the demonstration database, or non-thalassemia hemoglobinopathies.",
            "success",
        )

    return result


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

    coverage_map_summary(view)
    st.plotly_chart(panel_coverage_treemap(view), use_container_width=True, theme=None)

    c3, c4 = st.columns([1, 1])
    with c3:
        st.plotly_chart(allele_lollipop(view if len(view) else db), use_container_width=True, theme=None)
    with c4:
        # Keep original project visual for compatibility, but place it as a secondary view.
        try:
            st.plotly_chart(allele_method_bar(view if len(view) else db), use_container_width=True, theme=None)
        except Exception:
            st.plotly_chart(panel_coverage_treemap(view), use_container_width=True, theme=None)

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
        "Review confirmed or inferred parental genotypes across alpha- and beta-globin systems. The board converts gamete combinations into offspring genotype, phenotype, and risk-class visual analytics.",
    )

    alpha_inputs, beta_inputs = st.columns(2)
    with alpha_inputs:
        alpha_p1_label, alpha_p2_label, alpha_p1, alpha_p2 = select_parent_genotypes("alpha", ALPHA_GENOTYPES)
    with beta_inputs:
        beta_p1_label, beta_p2_label, beta_p1, beta_p2 = select_parent_genotypes("beta", BETA_GENOTYPES)

    render_couple_risk_results("alpha", alpha_p1_label, alpha_p2_label, alpha_p1, alpha_p2)
    st.divider()
    render_couple_risk_results("beta", beta_p1_label, beta_p2_label, beta_p1, beta_p2)


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
