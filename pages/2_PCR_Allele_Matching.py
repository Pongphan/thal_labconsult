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
    tx,
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
        .pcr-step span { color: var(--pcr-text); font-size: .94rem; }
        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: .42rem;
            border-radius: 999px;
            padding: .38rem .68rem;
            border: 1px solid var(--pcr-soft-border);
            margin: .15rem .2rem .15rem 0;
            font-size: .94rem;
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
        .mini-caption { color: var(--pcr-muted); font-size: .92rem; margin-top: -.2rem; }
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
            font-size: .82rem;
            font-weight: 800;
            letter-spacing: 0;
            text-transform: uppercase;
        }
        .coverage-summary__value {
            color: var(--pcr-heading);
            font-size: 1.5rem;
            font-weight: 850;
            line-height: 1.15;
            margin-top: .18rem;
        }
        .coverage-summary__caption {
            color: var(--pcr-text);
            font-size: .92rem;
            margin-top: .25rem;
            overflow-wrap: anywhere;
        }
        .dataframe th { font-size: .92rem !important; }

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
        f"""
        <div class="pcr-stepper">
            <div class="pcr-step"><b>1 · {tx("Panel design", "ออกแบบ panel")}</b><span>{tx("Targeted α/β variant knowledge base", "ฐานข้อมูล targeted α/β variant")}</span></div>
            <div class="pcr-step"><b>2 · {tx("Risk modeling", "จำลองความเสี่ยง")}</b><span>{tx("Parental gametes and offspring genotypes", "gametes ของพ่อแม่และ genotype ของบุตร")}</span></div>
            <div class="pcr-step"><b>3 · {tx("Counseling view", "มุมมองให้คำปรึกษา")}</b><span>{tx("Phenotype and reproductive-risk classes", "phenotype และระดับ reproductive risk")}</span></div>
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
            f"""
            <div class="coverage-summary">
                <div class="coverage-summary__item">
                    <div class="coverage-summary__label">{tx("Active targets", "Targets ที่แสดง")}</div>
                    <div class="coverage-summary__value">0</div>
                    <div class="coverage-summary__caption">{tx("No targets match the current filters", "ไม่มี target ที่ตรงกับ filter ปัจจุบัน")}</div>
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
                <div class="coverage-summary__label">{tx("Active targets", "Targets ที่แสดง")}</div>
                <div class="coverage-summary__value">{len(db)}</div>
                <div class="coverage-summary__caption">{_escape(db["target_code"].nunique())} {tx("unique target codes", "target codes ไม่ซ้ำ")}</div>
            </div>
            <div class="coverage-summary__item">
                <div class="coverage-summary__label">{tx("Globin balance", "สมดุล globin")}</div>
                <div class="coverage-summary__value">{len(system_counts)}</div>
                <div class="coverage-summary__caption">{system_caption}</div>
            </div>
            <div class="coverage-summary__item">
                <div class="coverage-summary__label">{tx("Largest method", "Method ที่มากสุด")}</div>
                <div class="coverage-summary__value">{_escape(top_method_count)}</div>
                <div class="coverage-summary__caption">{_escape(top_method)}</div>
            </div>
            <div class="coverage-summary__item">
                <div class="coverage-summary__label">{tx("Largest class", "Class ที่มากสุด")}</div>
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
    treemap_text_colors = []
    for node_id, parent_id in zip(fig.data[0].ids, fig.data[0].parents):
        key = str(node_id or parent_id).lower()
        if key == "alpha" or key.startswith("alpha/"):
            treemap_text_colors.append("#000000")
        elif key == "beta" or key.startswith("beta/"):
            treemap_text_colors.append("#FFFFFF")
        else:
            treemap_text_colors.append(neutral["text"])

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
        textfont=dict(color=treemap_text_colors, size=12),
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
        uniformtext=dict(minsize=10, mode="show"),
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
        tx(f"{system_label} parent 1 genotype", f"{system_label} genotype ของคนที่ 1"),
        labels,
        index=_default_genotype_index(system, 1, labels),
        key=f"{system}_parent1_genotype",
    )
    p2_label = st.selectbox(
        tx(f"{system_label} parent 2 genotype", f"{system_label} genotype ของคนที่ 2"),
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
        tx(f"{system_label}-globin offspring risk", f"ความเสี่ยงบุตรในระบบ {system_label}-globin"),
        tx(
            f"Predicted offspring outcomes from the selected {system}-globin parental genotypes.",
            f"คาดการณ์ผลลัพธ์ของบุตรจาก parental genotypes ของ {system}-globin ที่เลือก.",
        ),
    )

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        metric_card(tx("Parent 1 gametes", "Gametes คนที่ 1"), " / ".join(map(str, p1)), p1_label, "info")
    with k2:
        metric_card(tx("Parent 2 gametes", "Gametes คนที่ 2"), " / ".join(map(str, p2)), p2_label, "info")
    with k3:
        metric_card(tx("High/Critical", "สูง/วิกฤต"), f"{high_risk:.0f}%", tx("Offspring probability", "โอกาสในบุตร"), "high" if high_risk else "low")
    with k4:
        metric_card(tx("Outcomes", "ผลลัพธ์"), str(result.shape[0]), tx("Gamete combinations", "ชุด gamete combinations"), "moderate")
    with k5:
        metric_card(tx("Risk classes", "ระดับความเสี่ยง"), str(len(risk)), tx("Phenotype groups", "กลุ่ม phenotype"), "info")

    st.markdown('<div style="height: 0.85rem;"></div>', unsafe_allow_html=True)
    with st.expander(tx(f"{system_label}-globin offspring genotype evidence table", f"ตารางหลักฐาน genotype ของบุตรในระบบ {system_label}-globin"), expanded=True):
        risk_table = genotype_evidence_table(result)
        st.dataframe(risk_table, width='stretch', hide_index=True)
        st.download_button(
            tx(f"Download {system}-globin couple-risk table", f"ดาวน์โหลดตาราง couple-risk ของ {system}-globin"),
            result.to_csv(index=False).encode("utf-8"),
            f"{system}_globin_couple_risk_expert.csv",
            "text/csv",
            width='stretch',
            key=f"{system}_risk_download",
        )

    donut_col, sunburst_col = st.columns([1, 1])
    with donut_col:
        st.plotly_chart(risk_probability_donut(result), width='stretch', theme=None)
    with sunburst_col:
        st.plotly_chart(genotype_outcome_sunburst(result), width='stretch', theme=None)

    if high_risk > 0:
        clinical_box(
            tx(
                f"<b>Genetic counseling alert:</b> selected {system}-globin parental genotypes produce {high_risk:.0f}% high/critical offspring risk in this simplified Mendelian model. Confirm genotype calls, verify phase, and refer for formal genetic counseling before clinical action.",
                f"<b>แจ้งเตือน genetic counseling:</b> parental genotypes ของ {system}-globin ที่เลือกให้ความเสี่ยงสูง/วิกฤตในบุตร {high_risk:.0f}% ตาม Mendelian model แบบย่อ ควรยืนยัน genotype, phase และส่งปรึกษาพันธุศาสตร์ก่อนใช้ทางคลินิก.",
            ),
            "danger",
        )
    else:
        clinical_box(
            tx(
                f"No high/critical offspring-risk class was generated from the selected {system}-globin genotype pair. This does not exclude variants outside the selected panel, compound heterozygosity not represented in the demonstration database, or non-thalassemia hemoglobinopathies.",
                f"ไม่พบ risk class สูง/วิกฤตจาก genotype pair ของ {system}-globin ที่เลือก อย่างไรก็ตามยังไม่ตัด variants นอก panel, compound heterozygosity ที่ไม่ได้อยู่ในฐานข้อมูลตัวอย่าง หรือ hemoglobinopathies อื่นที่ไม่ใช่ธาลัสซีเมีย.",
            ),
            "success",
        )

    return result


# -----------------------------------------------------------------------------
# Page body
# -----------------------------------------------------------------------------

inject_expert_css()
hero(
    tx("ThalLink: Thalassemia Laboratory Intelligence Platform", "ThalLink: แพลตฟอร์มวิเคราะห์ธาลัสซีเมียทางห้องปฏิบัติการ"),
    tx(
        "A molecular hematology command center for α/β-globin panel intelligence and reproductive-risk visualization.",
        "ศูนย์วิเคราะห์ molecular hematology สำหรับ α/β-globin panel และภาพรวมความเสี่ยงการมีบุตร.",
    ),
    tx("Molecular confirmation + genotype-risk engine", "Molecular confirmation + genotype-risk engine"),
)
disclaimer()
workflow_stepper()

st.markdown(
    f"""
    <div class="molecular-hero">
      <h3>{tx("Molecular panel and counseling workspace", "พื้นที่ทำงาน molecular panel และ counseling")}</h3>
      <p>{tx("Review α/β-globin target coverage, laboratory methods, allele nomenclature, and counseling-ready reproductive-risk analytics.", "ทบทวน target coverage ของ α/β-globin, วิธีตรวจ, allele nomenclature และ reproductive-risk analytics ที่พร้อมใช้ให้คำปรึกษา.")}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Global data objects
db = cached_allele_database()

tabs = st.tabs([
    tx("Panel intelligence", "ข้อมูล panel"),
    tx("Couple genotype risk", "ความเสี่ยงคู่สมรส"),
    tx("Export report", "ส่งออกรายงาน"),
])


# -----------------------------------------------------------------------------
# Tab 1: Allele knowledge base
# -----------------------------------------------------------------------------
with tabs[0]:
    section(
        tx("Molecular panel intelligence", "ข้อมูล molecular panel"),
        tx(
            "Explore whether the current α/β-globin panel is balanced across variant systems, variant classes, and laboratory methods before reviewing patient bands.",
            "สำรวจว่า panel α/β-globin ปัจจุบันครอบคลุม variant systems, variant classes และวิธีตรวจได้สมดุลหรือไม่ก่อนทบทวน band ของผู้ป่วย.",
        ),
    )

    total_targets = len(db)
    alpha_n = int((db["system"].astype(str).str.lower() == "alpha").sum())
    beta_n = int((db["system"].astype(str).str.lower() == "beta").sum())
    methods_n = db["method"].nunique(dropna=True)
    classes_n = db["variant_class"].nunique(dropna=True)

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        metric_card(tx("Total targets", "Targets ทั้งหมด"), str(total_targets), tx("Validated panel entries", "รายการ panel ที่ validate แล้ว"), "info")
    with m2:
        metric_card("α-globin", str(alpha_n), "HBA deletion/nondeletion", "moderate")
    with m3:
        metric_card("β-globin", str(beta_n), "HBB β0/β+/structural", "high")
    with m4:
        metric_card(tx("Methods", "วิธีตรวจ"), str(methods_n), "Gap-PCR / ARMS / sequencing", "low")
    with m5:
        metric_card(tx("Classes", "Classes"), str(classes_n), tx("Variant categories", "กลุ่ม variant"), "info")

    control_left, control_right = st.columns([1.2, 0.8])
    with control_left:
        search = st.text_input(tx("Search target, allele, method, or class", "ค้นหา target, allele, method หรือ class"), value="", placeholder="e.g., HbE, SEA, CD41/42, gap-PCR")
    with control_right:
        sort_mode = st.selectbox(tx("Prioritize table by", "จัดลำดับตารางตาม"), ["system", "variant_class", "method", "common_name"], index=1)

    f1, f2, f3 = st.columns(3)
    with f1:
        sys_filter = st.multiselect(tx("Globin system", "ระบบ globin"), sorted(db["system"].dropna().astype(str).unique()), default=sorted(db["system"].dropna().astype(str).unique()))
    with f2:
        class_filter = st.multiselect(tx("Variant class", "Variant class"), sorted(db["variant_class"].dropna().astype(str).unique()), default=sorted(db["variant_class"].dropna().astype(str).unique()))
    with f3:
        method_filter = st.multiselect(tx("Method", "วิธีตรวจ"), sorted(db["method"].dropna().astype(str).unique()), default=sorted(db["method"].dropna().astype(str).unique()))

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
    st.plotly_chart(panel_coverage_treemap(view), width='stretch', theme=None)

    c3, c4 = st.columns([1, 1])
    with c3:
        st.plotly_chart(allele_lollipop(view if len(view) else db), width='stretch', theme=None)
    with c4:
        # Keep original project visual for compatibility, but place it as a secondary view.
        try:
            st.plotly_chart(allele_method_bar(view if len(view) else db), width='stretch', theme=None)
        except Exception:
            st.plotly_chart(panel_coverage_treemap(view), width='stretch', theme=None)

    molecular_panel(
        tx("Usability note", "หมายเหตุการใช้งาน"),
        tx(
            "Before adopting this page in a production laboratory, replace the demonstration allele panel with your locally validated SOP panel, positive controls, primer lot information, and reporting nomenclature.",
            "ก่อนใช้ในห้องปฏิบัติการจริง ให้เปลี่ยน demonstration allele panel เป็น SOP panel ที่ validate ในพื้นที่ พร้อม positive controls, primer lot information และ reporting nomenclature.",
        ),
    )
    st.dataframe(view, width='stretch', hide_index=True)
    st.download_button(
        tx("Download filtered allele knowledge base CSV", "ดาวน์โหลด allele knowledge base CSV ที่กรองแล้ว"),
        view.to_csv(index=False).encode("utf-8"),
        "thalassemia_filtered_allele_knowledge_base.csv",
        "text/csv",
        width='stretch',
    )


# -----------------------------------------------------------------------------
# Tab 2: Couple genotype risk
# -----------------------------------------------------------------------------
with tabs[1]:
    section(
        tx("Couple genotype reproductive-risk board", "บอร์ดประเมินความเสี่ยง genotype ของคู่สมรส"),
        tx(
            "Review confirmed or inferred parental genotypes across alpha- and beta-globin systems. The board converts gamete combinations into offspring genotype, phenotype, and risk-class visual analytics.",
            "ทบทวน parental genotypes ทั้ง alpha- และ beta-globin ที่ยืนยันหรือคาดการณ์ แล้วแปลง gamete combinations เป็น genotype, phenotype และ risk class ของบุตร.",
        ),
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
        tx("Export-ready molecular consult package", "ชุดข้อมูล molecular consult พร้อมส่งออก"),
        tx(
            "This tab summarizes which objects should be reviewed before integrating the page into a laboratory report workflow.",
            "แท็บนี้สรุปรายการที่ควรทบทวนก่อนเชื่อมเข้ากับ workflow รายงานของห้องปฏิบัติการ.",
        ),
    )

    molecular_panel(
        tx("Recommended production hardening", "ข้อแนะนำก่อนใช้งานจริง"),
        tx(
            "Add laboratory-specific primer panels, control-lane QC rules, local HGVS/HbVar nomenclature, audit logs, user authentication, and LIS/LIMS export fields before clinical deployment.",
            "เพิ่ม primer panels เฉพาะห้องปฏิบัติการ, control-lane QC rules, local HGVS/HbVar nomenclature, audit logs, user authentication และ LIS/LIMS export fields ก่อนใช้ทางคลินิก.",
        ),
    )

    report_items = pd.DataFrame(
        [
            {
                tx("Module", "โมดูล"): tx("Allele panel", "Allele panel"),
                "Export": "CSV",
                tx("Purpose", "วัตถุประสงค์"): tx("Validated target list and method coverage", "รายการ target ที่ validate แล้วและ method coverage"),
            },
            {
                tx("Module", "โมดูล"): tx("Couple risk", "ความเสี่ยงคู่สมรส"),
                "Export": "CSV",
                tx("Purpose", "วัตถุประสงค์"): tx("Punnett genotype/phenotype/risk evidence table", "ตารางหลักฐาน genotype/phenotype/risk จาก Punnett"),
            },
            {
                tx("Module", "โมดูล"): tx("Consult note", "Consult note"),
                "Export": tx("HTML/PDF extension recommended", "แนะนำต่อยอด HTML/PDF"),
                tx("Purpose", "วัตถุประสงค์"): tx("Molecular interpretation and genetic-counseling prompt", "คำแปลผล molecular และ prompt สำหรับ genetic counseling"),
            },
        ]
    )
    st.dataframe(report_items, width='stretch', hide_index=True)

    st.markdown(
        tx(
            "**Suggested next enhancement:** add a one-click molecular consult report generator with these sections: assay panel, allele interpretation, reproductive-risk summary, limitations, and sign-out block.",
            "**ข้อเสนอแนะต่อไป:** เพิ่มตัวสร้าง molecular consult report แบบคลิกเดียว โดยมีส่วน assay panel, allele interpretation, reproductive-risk summary, limitations และ sign-out block.",
        )
    )



production_footer()
