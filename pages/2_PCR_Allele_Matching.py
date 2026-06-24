from __future__ import annotations

import math
from typing import Iterable, Sequence

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from thalab.genetics import (
    ALPHA_GENOTYPES,
    BETA_GENOTYPES,
    allele_dataframe,
    match_pcr_bands,
    pcr_template,
    punnett,
    summarize_risk,
)
from thalab.styles import (
    clinical_box,
    disclaimer,
    hero,
    inject_css,
    metric_card,
    section,
    sidebar_brand,
)
from thalab.viz import (
    allele_method_bar,
    allele_sunburst,
    pcr_confidence_lollipop,
    punnett_heatmap,
    punnett_sunburst,
    risk_probability_bar,
    virtual_gel,
)


# -----------------------------------------------------------------------------
# Page configuration and design system
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="PCR Allele Matching | Thal Lab Consult",
    page_icon="🧬",
    layout="wide",
)

inject_css()
sidebar_brand("PCR allele matching")


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

SEVERITY_SCORE = {
    "none": 0,
    "normal": 0,
    "low": 1,
    "carrier": 1,
    "moderate": 2,
    "intermediate": 2,
    "high": 3,
    "severe": 3,
    "critical": 4,
    "lethal": 4,
}


def inject_expert_css() -> None:
    """Additional page-local CSS for a hematology command-center feel."""
    st.markdown(
        """
        <style>
        div[data-testid="stTabs"] button[role="tab"] {
            border-radius: 999px !important;
            border: 1px solid rgba(255,255,255,0.13) !important;
            padding: .58rem 1.08rem !important;
            background: linear-gradient(135deg, rgba(179,18,55,.22), rgba(123,97,255,.12));
            margin-right: .35rem;
        }
        div[data-testid="stTabs"] button[aria-selected="true"] {
            background: linear-gradient(135deg, #B31237, #7B61FF) !important;
            color: #fff !important;
            box-shadow: 0 0 26px rgba(227,52,85,.30);
        }
        .molecular-hero {
            padding: 1rem 1.15rem;
            border: 1px solid rgba(255,255,255,.14);
            border-radius: 24px;
            background:
              radial-gradient(circle at top left, rgba(255,200,87,.18), transparent 32%),
              radial-gradient(circle at top right, rgba(77,225,255,.16), transparent 30%),
              linear-gradient(145deg, rgba(41,6,19,.95), rgba(16,2,9,.82));
            box-shadow: 0 18px 60px rgba(0,0,0,.33);
            margin-bottom: .8rem;
        }
        .molecular-hero h3 { margin: 0 0 .35rem 0; letter-spacing: -.02em; }
        .molecular-hero p { margin: 0; color: rgba(255,255,255,.76); }
        .pcr-stepper {
            display: grid;
            grid-template-columns: repeat(4, minmax(120px, 1fr));
            gap: .7rem;
            margin: .4rem 0 1.1rem 0;
        }
        .pcr-step {
            border-radius: 18px;
            padding: .82rem .9rem;
            border: 1px solid rgba(255,255,255,.13);
            background: linear-gradient(135deg, rgba(255,255,255,.07), rgba(255,255,255,.025));
        }
        .pcr-step b { color: #fff; display: block; margin-bottom: .25rem; }
        .pcr-step span { color: rgba(255,255,255,.68); font-size: .86rem; }
        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: .42rem;
            border-radius: 999px;
            padding: .38rem .68rem;
            border: 1px solid rgba(255,255,255,.13);
            margin: .15rem .2rem .15rem 0;
            font-size: .86rem;
            background: rgba(255,255,255,.055);
        }
        .pill-high { background: rgba(227,52,85,.16); color: #FFD6DE; }
        .pill-moderate { background: rgba(255,200,87,.16); color: #FFE7A8; }
        .pill-low { background: rgba(44,234,163,.15); color: #C9FFE9; }
        .glass-panel {
            border: 1px solid rgba(255,255,255,.13);
            border-radius: 24px;
            padding: 1rem 1.1rem;
            background: linear-gradient(145deg, rgba(59,13,29,.78), rgba(21,4,12,.64));
            box-shadow: inset 0 1px 0 rgba(255,255,255,.08), 0 14px 42px rgba(0,0,0,.26);
            margin-bottom: .7rem;
        }
        .glass-panel h4 { margin-top: 0; margin-bottom: .35rem; }
        .glass-panel p { margin-bottom: 0; color: rgba(255,255,255,.68); }
        .mini-caption { color: rgba(255,255,255,.62); font-size: .84rem; margin-top: -.2rem; }
        .dataframe th { font-size: 12px !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _theme_layout(fig: go.Figure, title: str | None = None, height: int = 430) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        height=height,
        paper_bgcolor=HEM_COLORS["paper"],
        plot_bgcolor="rgba(17,4,10,0.68)",
        margin=dict(l=35, r=25, t=72 if title else 40, b=38),
        title=dict(text=title or "", x=0.02, xanchor="left", font=dict(size=20, color="white")),
        font=dict(family="Inter, Segoe UI, Arial", color="rgba(255,255,255,0.88)"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0)",
        ),
        hoverlabel=dict(bgcolor="#1A0710", bordercolor="rgba(255,255,255,.18)", font_size=12),
    )
    fig.update_xaxes(gridcolor=HEM_COLORS["grid"], zerolinecolor=HEM_COLORS["grid"])
    fig.update_yaxes(gridcolor=HEM_COLORS["grid"], zerolinecolor=HEM_COLORS["grid"])
    return fig


def _safe_col(df: pd.DataFrame, candidates: Sequence[str], fallback: str | None = None) -> str | None:
    for col in candidates:
        if col in df.columns:
            return col
    return fallback


def _as_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    return series.astype(str).str.lower().isin(["true", "1", "yes", "y", "positive", "detected", "pos"])


def _num(series: pd.Series, default: float = np.nan) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(default)


def _html_badge(label: str, level: str = "low") -> str:
    return f'<span class="status-pill pill-{level}">{label}</span>'


def workflow_stepper() -> None:
    st.markdown(
        """
        <div class="pcr-stepper">
            <div class="pcr-step"><b>1 · Panel design</b><span>Targeted α/β variant knowledge base</span></div>
            <div class="pcr-step"><b>2 · Band review</b><span>Editable PCR/gap-PCR/ARMS call sheet</span></div>
            <div class="pcr-step"><b>3 · Evidence fusion</b><span>Band tolerance, operator call, confidence</span></div>
            <div class="pcr-step"><b>4 · Counseling view</b><span>Gamete, offspring genotype, risk class</span></div>
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


def prepare_matched_table(input_df: pd.DataFrame, tolerance_bp: int) -> pd.DataFrame:
    matched = match_pcr_bands(input_df, tolerance_bp=tolerance_bp).copy()
    if "detected" not in matched.columns:
        matched["detected"] = False
    matched["detected"] = _as_bool(matched["detected"])
    if "confidence" not in matched.columns:
        matched["confidence"] = np.where(matched["detected"], 0.85, 0.15)
    matched["confidence"] = _num(matched["confidence"], 0).clip(0, 1)
    if "sample_id" not in matched.columns:
        matched["sample_id"] = "Sample"
    if "variant_class" not in matched.columns:
        matched["variant_class"] = "Unknown"
    if "common_name" not in matched.columns:
        matched["common_name"] = matched.get("target_code", pd.Series(["Unknown"] * len(matched)))
    if "system" not in matched.columns:
        # Infer from variant text when the knowledge table was not joined by the backend.
        text = matched["variant_class"].astype(str).str.lower() + " " + matched["common_name"].astype(str).str.lower()
        matched["system"] = np.where(text.str.contains("alpha|hba|--|-α|sea|thai", regex=True), "alpha", "beta")
    if "expected_bp" not in matched.columns:
        matched["expected_bp"] = np.nan
    if "observed_bp" not in matched.columns:
        matched["observed_bp"] = matched["expected_bp"]
    matched["expected_bp"] = _num(matched["expected_bp"])
    matched["observed_bp"] = _num(matched["observed_bp"])
    matched["delta_bp"] = (matched["observed_bp"] - matched["expected_bp"]).abs()
    matched["qc_status"] = np.select(
        [
            matched["detected"] & (matched["confidence"] >= 0.85),
            matched["detected"] & (matched["confidence"] >= 0.65),
            matched["detected"],
        ],
        ["Strong positive", "Review", "Low-confidence"],
        default="Not detected",
    )
    return matched


# -----------------------------------------------------------------------------
# Visualizations: Allele knowledge base
# -----------------------------------------------------------------------------


def panel_coverage_treemap(db: pd.DataFrame) -> go.Figure:
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
        root_color="rgba(255,255,255,.06)",
    )
    return _theme_layout(fig, "Molecular panel coverage map", 520)


def panel_method_heatmap(db: pd.DataFrame) -> go.Figure:
    pivot = pd.crosstab(db["variant_class"], [db["system"], db["method"]])
    x = [f"{a} · {b}" for a, b in pivot.columns]
    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=x,
            y=pivot.index,
            colorscale=[[0, "rgba(255,255,255,.05)"], [0.5, HEM_COLORS["amber"]], [1, HEM_COLORS["blood2"]]],
            hovertemplate="Variant class: %{y}<br>Panel/method: %{x}<br>Targets: %{z}<extra></extra>",
            showscale=True,
            colorbar=dict(title="Targets"),
        )
    )
    fig.update_traces(xgap=3, ygap=3)
    return _theme_layout(fig, "Panel density heatmap", 420)


def allele_lollipop(db: pd.DataFrame) -> go.Figure:
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
                marker=dict(size=12, color=color_map.get(system, HEM_COLORS["plasma"]), line=dict(color="white", width=1)),
                name=str(system),
                hovertemplate="%{y}<br>Expected size: %{x:.0f} bp<extra></extra>",
            )
        )
    fig.update_xaxes(title="Expected amplicon size (bp)")
    fig.update_yaxes(title="Target", automargin=True)
    return _theme_layout(fig, "Amplicon-size lollipop panel", 620)


# -----------------------------------------------------------------------------
# Visualizations: PCR workspace
# -----------------------------------------------------------------------------


def pcr_command_gauge(matched: pd.DataFrame, confidence_cutoff: float) -> go.Figure:
    detected = matched[matched["detected"]]
    strong = int((detected["confidence"] >= confidence_cutoff).sum())
    total = max(len(matched), 1)
    value = strong / total * 100
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=value,
            number={"suffix": "%", "font": {"size": 48}},
            delta={"reference": 25, "suffix": "%", "increasing": {"color": HEM_COLORS["marrow"]}},
            title={"text": "Strong target-positive calls"},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "rgba(255,255,255,.6)"},
                "bar": {"color": HEM_COLORS["blood2"]},
                "bgcolor": "rgba(255,255,255,.06)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 20], "color": "rgba(44,234,163,.20)"},
                    {"range": [20, 60], "color": "rgba(255,200,87,.22)"},
                    {"range": [60, 100], "color": "rgba(227,52,85,.25)"},
                ],
                "threshold": {"line": {"color": HEM_COLORS["plasma"], "width": 4}, "thickness": 0.8, "value": value},
            },
        )
    )
    return _theme_layout(fig, "PCR call command gauge", 330)


def expert_virtual_gel(matched: pd.DataFrame) -> go.Figure:
    plot_df = matched.copy()
    sample_col = "sample_id"
    plot_df[sample_col] = plot_df[sample_col].astype(str)
    samples = list(plot_df[sample_col].dropna().unique()) or ["Sample"]
    sample_index = {s: i + 1 for i, s in enumerate(samples)}
    plot_df["_x"] = plot_df[sample_col].map(sample_index)
    plot_df["_bp_plot"] = np.where(plot_df["observed_bp"].notna(), plot_df["observed_bp"], plot_df["expected_bp"])
    plot_df["_bp_plot"] = _num(plot_df["_bp_plot"], 100).clip(lower=30)
    plot_df["_band_alpha"] = np.where(plot_df["detected"], 0.95, 0.18)
    max_bp = max(float(plot_df["_bp_plot"].max()), 1000.0)
    min_bp = max(30.0, min(float(plot_df["_bp_plot"].min()), 80.0))

    fig = go.Figure()

    # Lane backgrounds
    for s, x in sample_index.items():
        fig.add_shape(
            type="rect",
            x0=x - 0.38,
            x1=x + 0.38,
            y0=min_bp * 0.75,
            y1=max_bp * 1.18,
            line=dict(color="rgba(255,255,255,.08)", width=1),
            fillcolor="rgba(255,255,255,.035)",
            layer="below",
        )

    # Ladder guides
    ladder = np.array([100, 200, 300, 500, 750, 1000, 1500, 2000, 3000, 5000])
    ladder = ladder[(ladder >= min_bp) & (ladder <= max_bp * 1.15)]
    for bp in ladder:
        fig.add_hline(y=bp, line_width=1, line_dash="dot", line_color="rgba(255,255,255,.10)")
        fig.add_annotation(
            x=0.38,
            y=bp,
            text=f"{int(bp)} bp",
            showarrow=False,
            font=dict(size=10, color="rgba(255,255,255,.42)"),
            xanchor="right",
        )

    # Glow trace for detected bands
    detected = plot_df[plot_df["detected"]].copy()
    not_detected = plot_df[~plot_df["detected"]].copy()
    if len(detected):
        fig.add_trace(
            go.Scatter(
                x=detected["_x"],
                y=detected["_bp_plot"],
                mode="markers",
                marker=dict(
                    symbol="line-ew",
                    size=np.clip(detected["confidence"] * 56, 22, 58),
                    color=detected["confidence"],
                    colorscale=[[0, HEM_COLORS["amber"]], [1, HEM_COLORS["cyan"]]],
                    cmin=0,
                    cmax=1,
                    line=dict(color="rgba(255,255,255,.92)", width=2),
                    colorbar=dict(title="Confidence"),
                ),
                name="Detected band",
                customdata=np.stack(
                    [
                        detected["common_name"].astype(str),
                        detected["variant_class"].astype(str),
                        (detected["confidence"] * 100).round(1),
                        detected["delta_bp"].round(1),
                    ],
                    axis=-1,
                ),
                hovertemplate=(
                    "Sample lane: %{x}<br>Band: %{y:.0f} bp<br>Allele: %{customdata[0]}"
                    "<br>Class: %{customdata[1]}<br>Confidence: %{customdata[2]}%"
                    "<br>|Δbp|: %{customdata[3]}<extra></extra>"
                ),
            )
        )
    if len(not_detected):
        fig.add_trace(
            go.Scatter(
                x=not_detected["_x"],
                y=not_detected["_bp_plot"],
                mode="markers",
                marker=dict(symbol="line-ew", size=20, color="rgba(255,255,255,.18)", line=dict(width=1, color="rgba(255,255,255,.28)")),
                name="Not detected / background",
                hovertemplate="Sample lane: %{x}<br>Expected/observed: %{y:.0f} bp<extra></extra>",
            )
        )

    fig.update_xaxes(
        tickmode="array",
        tickvals=list(sample_index.values()),
        ticktext=samples,
        title="Sample lane",
        range=[0.25, len(samples) + 0.75],
    )
    fig.update_yaxes(
        type="log",
        autorange="reversed",
        title="Fragment size (bp, log migration)",
    )
    fig.add_annotation(
        x=0.01,
        y=1.06,
        xref="paper",
        yref="paper",
        text="Ladder-like guides are visual aids. Use validated gel-analysis software for final sizing.",
        showarrow=False,
        align="left",
        font=dict(size=12, color="rgba(255,255,255,.58)"),
    )
    return _theme_layout(fig, "Interactive virtual gel electrophoresis", 620)


def pcr_confidence_heatmap(matched: pd.DataFrame) -> go.Figure:
    label_col = "common_name"
    work = matched.copy()
    work["_label"] = work[label_col].astype(str).str.slice(0, 42)
    pivot = work.pivot_table(index="_label", columns="sample_id", values="confidence", aggfunc="max", fill_value=0)
    detected = work.pivot_table(index="_label", columns="sample_id", values="detected", aggfunc="max", fill_value=False)
    z = pivot.values * 100
    text = np.where(detected.reindex_like(pivot).values, "Detected", "Not detected")
    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=pivot.columns.astype(str),
            y=pivot.index.astype(str),
            colorscale=[[0, "rgba(255,255,255,.04)"], [0.35, HEM_COLORS["amber"]], [0.75, HEM_COLORS["marrow"]], [1, HEM_COLORS["cyan"]]],
            text=text,
            hovertemplate="Sample: %{x}<br>Target: %{y}<br>Confidence: %{z:.1f}%<br>%{text}<extra></extra>",
            colorbar=dict(title="Confidence %"),
        )
    )
    fig.update_traces(xgap=3, ygap=3)
    fig.update_xaxes(title="Sample")
    fig.update_yaxes(title="Allele target", automargin=True)
    return _theme_layout(fig, "Allele-call confidence matrix", max(430, min(760, 220 + len(pivot) * 22)))


def pcr_call_sankey(matched: pd.DataFrame) -> go.Figure:
    work = matched.copy()
    work["status"] = np.where(work["detected"], "Detected", "Not detected")
    levels = ["sample_id", "system", "variant_class", "status"]
    nodes: list[str] = []
    node_index: dict[str, int] = {}
    sources: list[int] = []
    targets: list[int] = []
    values: list[int] = []

    def idx(label: str) -> int:
        if label not in node_index:
            node_index[label] = len(nodes)
            nodes.append(label)
        return node_index[label]

    for left, right in zip(levels[:-1], levels[1:]):
        counts = work.groupby([left, right], dropna=False).size().reset_index(name="n")
        for row in counts.itertuples(index=False):
            lval = f"{left}: {getattr(row, left)}"
            rval = f"{right}: {getattr(row, right)}"
            sources.append(idx(lval))
            targets.append(idx(rval))
            values.append(int(row.n))

    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",
                node=dict(
                    pad=18,
                    thickness=16,
                    line=dict(color="rgba(255,255,255,.18)", width=1),
                    label=[n.split(": ", 1)[-1] for n in nodes],
                    color="rgba(227,52,85,.65)",
                ),
                link=dict(
                    source=sources,
                    target=targets,
                    value=values,
                    color="rgba(255,200,87,.22)",
                ),
            )
        ]
    )
    return _theme_layout(fig, "Sample → globin system → variant class → call status", 480)


def tolerance_sensitivity(input_df: pd.DataFrame, selected_tolerance: int) -> go.Figure:
    rows = []
    for tol in range(5, 105, 5):
        try:
            tmp = prepare_matched_table(input_df, tol)
            rows.append(
                {
                    "tolerance": tol,
                    "detected": int(tmp["detected"].sum()),
                    "median_confidence": float(tmp["confidence"].median() * 100),
                }
            )
        except Exception:
            continue
    sens = pd.DataFrame(rows)
    if sens.empty:
        sens = pd.DataFrame({"tolerance": [selected_tolerance], "detected": [0], "median_confidence": [0]})
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=sens["tolerance"],
            y=sens["detected"],
            mode="lines+markers",
            name="Detected calls",
            line=dict(width=4, color=HEM_COLORS["blood2"]),
            marker=dict(size=8),
            yaxis="y",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=sens["tolerance"],
            y=sens["median_confidence"],
            mode="lines+markers",
            name="Median confidence",
            line=dict(width=3, color=HEM_COLORS["cyan"], dash="dot"),
            marker=dict(size=7),
            yaxis="y2",
        )
    )
    fig.add_vline(x=selected_tolerance, line_color=HEM_COLORS["plasma"], line_dash="dash", annotation_text="selected")
    fig.update_layout(
        yaxis=dict(title="Detected calls"),
        yaxis2=dict(title="Median confidence %", overlaying="y", side="right", range=[0, 105]),
    )
    fig.update_xaxes(title="Band-size tolerance window (bp)")
    return _theme_layout(fig, "Tolerance sensitivity curve", 420)


def pcr_delta_bp_plot(matched: pd.DataFrame) -> go.Figure:
    work = matched.copy()
    work = work[np.isfinite(work["delta_bp"])].copy()
    if work.empty:
        work = matched.copy()
        work["delta_bp"] = 0
    work = work.sort_values("delta_bp", ascending=False).head(40)
    fig = px.bar(
        work,
        x="delta_bp",
        y="common_name",
        color="qc_status",
        orientation="h",
        hover_data=["sample_id", "expected_bp", "observed_bp", "confidence"],
        color_discrete_map={
            "Strong positive": HEM_COLORS["cyan"],
            "Review": HEM_COLORS["amber"],
            "Low-confidence": HEM_COLORS["marrow"],
            "Not detected": "rgba(255,255,255,.28)",
        },
    )
    fig.update_yaxes(title="Target", automargin=True, categoryorder="total ascending")
    fig.update_xaxes(title="Absolute size deviation |observed − expected| bp")
    return _theme_layout(fig, "Band-size deviation review", 520)


# -----------------------------------------------------------------------------
# Visualizations: couple genotype risk
# -----------------------------------------------------------------------------


def _risk_col(result: pd.DataFrame) -> str | None:
    return _safe_col(result, ["risk_class", "risk_level", "severity", "risk", "clinical_risk"], None)


def _gamete_cols(result: pd.DataFrame) -> tuple[str, str]:
    p1 = _safe_col(result, ["parent1_gamete", "p1_gamete", "gamete_1", "parent_1", "p1"], None)
    p2 = _safe_col(result, ["parent2_gamete", "p2_gamete", "gamete_2", "parent_2", "p2"], None)
    if p1 is None or p2 is None:
        object_cols = list(result.select_dtypes(include="object").columns)
        p1 = p1 or (object_cols[0] if object_cols else result.columns[0])
        p2 = p2 or (object_cols[1] if len(object_cols) > 1 else result.columns[min(1, len(result.columns) - 1)])
    return p1, p2


def expert_punnett_heatmap(result: pd.DataFrame, system: str) -> go.Figure:
    work = result.copy()
    p1_col, p2_col = _gamete_cols(work)
    geno_col = _safe_col(work, ["offspring_genotype", "genotype", "child_genotype"], work.columns[-1])
    pheno_col = _safe_col(work, ["phenotype", "offspring_phenotype", "clinical_phenotype"], geno_col)
    risk_col = _risk_col(work)
    if risk_col is None:
        work["_risk_score"] = 1
        work["_risk_text"] = "review"
    else:
        work["_risk_text"] = work[risk_col].astype(str)
        work["_risk_score"] = work["_risk_text"].str.lower().map(SEVERITY_SCORE).fillna(1)
    gametes1 = list(pd.unique(work[p1_col].astype(str)))
    gametes2 = list(pd.unique(work[p2_col].astype(str)))
    z = np.zeros((len(gametes1), len(gametes2)))
    text = [["" for _ in gametes2] for __ in gametes1]
    hover = [["" for _ in gametes2] for __ in gametes1]
    for i, g1 in enumerate(gametes1):
        for j, g2 in enumerate(gametes2):
            sub = work[(work[p1_col].astype(str) == g1) & (work[p2_col].astype(str) == g2)]
            if sub.empty:
                continue
            row = sub.iloc[0]
            z[i, j] = row["_risk_score"]
            text[i][j] = f"{row[geno_col]}<br><span style='font-size:11px'>{row[pheno_col]}</span>"
            hover[i][j] = f"Parent 1 gamete: {g1}<br>Parent 2 gamete: {g2}<br>Genotype: {row[geno_col]}<br>Phenotype: {row[pheno_col]}<br>Risk: {row['_risk_text']}"
    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=gametes2,
            y=gametes1,
            text=text,
            texttemplate="%{text}",
            hovertext=hover,
            hovertemplate="%{hovertext}<extra></extra>",
            colorscale=[
                [0, "rgba(44,234,163,.45)"],
                [0.25, "rgba(44,234,163,.70)"],
                [0.5, "rgba(255,200,87,.78)"],
                [0.75, "rgba(248,94,123,.84)"],
                [1, "rgba(179,18,55,.96)"],
            ],
            zmin=0,
            zmax=4,
            showscale=True,
            colorbar=dict(title="Risk score", tickvals=[0, 1, 2, 3, 4], ticktext=["none", "low", "mod", "high", "crit"]),
        )
    )
    fig.update_xaxes(title="Parent 2 gamete")
    fig.update_yaxes(title="Parent 1 gamete")
    return _theme_layout(fig, f"{system.capitalize()}-globin Punnett risk matrix", 500)


def genotype_outcome_sunburst(result: pd.DataFrame) -> go.Figure:
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
    fig.update_traces(insidetextorientation="radial", marker=dict(line=dict(color="rgba(255,255,255,.15)", width=1)))
    return _theme_layout(fig, "Offspring genotype hierarchy", 520)


def risk_probability_donut(result: pd.DataFrame) -> go.Figure:
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
                marker=dict(line=dict(color="rgba(255,255,255,.18)", width=1)),
            )
        ]
    )
    fig.add_annotation(text="Risk<br>probability", x=0.5, y=0.5, showarrow=False, font=dict(size=18, color="white"))
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
    "Page 2 — PCR for Allele Matching",
    "A molecular hematology command center for α/β-globin PCR panels, gel-band review, allele-confidence scoring, and reproductive-risk visualization.",
    "Molecular confirmation + genotype-risk engine",
)
disclaimer()
workflow_stepper()

st.markdown(
    """
    <div class="molecular-hero">
      <h3>Expert visualization upgrade</h3>
      <p>This page emphasizes laboratory usability: editable PCR input, QC-first call review, interactive virtual gel, allele-confidence matrix, tolerance sensitivity, and counseling-ready Punnett visual analytics.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Global data objects
db = cached_allele_database()

tabs = st.tabs(["🧬 Panel intelligence", "🧫 PCR gel workspace", "👪 Couple genotype risk", "📤 Export report"])


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

    c1, c2 = st.columns([1.12, 0.88])
    with c1:
        st.plotly_chart(panel_coverage_treemap(view if len(view) else db), use_container_width=True, theme=None)
    with c2:
        st.plotly_chart(panel_method_heatmap(view if len(view) else db), use_container_width=True, theme=None)

    c3, c4 = st.columns([1, 1])
    with c3:
        st.plotly_chart(allele_lollipop(view if len(view) else db), use_container_width=True, theme=None)
    with c4:
        # Keep original project visual for compatibility, but place it as a secondary view.
        try:
            st.plotly_chart(allele_method_bar(view if len(view) else db), use_container_width=True, theme=None)
        except Exception:
            st.plotly_chart(panel_method_heatmap(view if len(view) else db), use_container_width=True, theme=None)

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
# Tab 2: PCR band matching workspace
# -----------------------------------------------------------------------------
with tabs[1]:
    section(
        "PCR band/call matching workspace",
        "Upload gel-review output or ARMS-PCR call sheet, edit it directly in the app, then review confidence, band-size deviation, tolerance sensitivity, and virtual gel pattern.",
    )

    template = pcr_template()
    top_a, top_b, top_c = st.columns([1, 1, 1])
    with top_a:
        uploaded = st.file_uploader("Upload PCR band/call CSV", type=["csv"], key="pcr_upload")
    with top_b:
        tolerance = st.slider("Band-size tolerance (bp)", 5, 100, 25, 5)
    with top_c:
        confidence_cutoff = st.slider("Strong-call confidence cutoff", 0.50, 0.99, 0.85, 0.01)

    raw_df = pd.read_csv(uploaded) if uploaded is not None else template.copy()

    with st.expander("Input table editor", expanded=False):
        st.caption("Edit sample IDs, observed band sizes, and operator calls before matching. Keep target codes consistent with the allele knowledge base.")
        edited_df = st.data_editor(raw_df, use_container_width=True, hide_index=True, num_rows="dynamic")
        st.download_button(
            "⬇️ Download PCR input template",
            template.to_csv(index=False).encode("utf-8"),
            "pcr_band_matching_template.csv",
            "text/csv",
            use_container_width=True,
        )

    matched = prepare_matched_table(edited_df, tolerance_bp=tolerance)
    samples = sorted(matched["sample_id"].astype(str).unique())
    selected_samples = st.multiselect("Focus samples", samples, default=samples)
    matched_view = matched[matched["sample_id"].astype(str).isin(selected_samples)].copy() if selected_samples else matched.copy()

    detected = matched_view[matched_view["detected"]]
    strong = detected[detected["confidence"] >= confidence_cutoff]
    review = matched_view[(matched_view["detected"]) & (matched_view["confidence"] < confidence_cutoff)]
    low_conf = int((matched_view["confidence"] < 0.65).sum())
    median_conf = float(matched_view["confidence"].median() * 100) if len(matched_view) else 0
    max_delta = float(matched_view["delta_bp"].replace([np.inf, -np.inf], np.nan).max()) if len(matched_view) else 0
    max_delta = 0 if math.isnan(max_delta) else max_delta

    q1, q2, q3, q4, q5 = st.columns(5)
    with q1:
        metric_card("Rows reviewed", str(len(matched_view)), "PCR targets/lane calls", "info")
    with q2:
        metric_card("Detected", str(len(detected)), "Target-positive calls", "high" if len(detected) else "low")
    with q3:
        metric_card("Strong calls", str(len(strong)), f"≥ {confidence_cutoff:.0%} confidence", "high" if len(strong) else "moderate")
    with q4:
        metric_card("Median confidence", f"{median_conf:.0f}%", "Across reviewed rows", "moderate")
    with q5:
        metric_card("Max Δbp", f"{max_delta:.0f}", "Largest size deviation", "high" if max_delta > tolerance else "low")

    badges = []
    badges.append(_html_badge(f"±{tolerance} bp tolerance", "moderate"))
    badges.append(_html_badge(f"{len(review)} calls need review", "moderate" if len(review) else "low"))
    badges.append(_html_badge(f"{low_conf} low-confidence rows", "high" if low_conf else "low"))
    badges.append(_html_badge(f"{len(samples)} sample lane(s)", "low"))
    st.markdown("".join(badges), unsafe_allow_html=True)

    left, right = st.columns([1.08, 0.92])
    with left:
        st.plotly_chart(expert_virtual_gel(matched_view), use_container_width=True, theme=None)
    with right:
        st.plotly_chart(pcr_command_gauge(matched_view, confidence_cutoff), use_container_width=True, theme=None)
        st.plotly_chart(tolerance_sensitivity(edited_df, tolerance), use_container_width=True, theme=None)

    h1, h2 = st.columns([1.02, 0.98])
    with h1:
        st.plotly_chart(pcr_confidence_heatmap(matched_view), use_container_width=True, theme=None)
    with h2:
        st.plotly_chart(pcr_delta_bp_plot(matched_view), use_container_width=True, theme=None)

    try:
        st.plotly_chart(pcr_call_sankey(matched_view), use_container_width=True, theme=None)
    except Exception:
        st.plotly_chart(pcr_confidence_lollipop(matched_view), use_container_width=True, theme=None)

    st.subheader("Molecular call review table")
    display_cols = [
        c
        for c in [
            "sample_id",
            "target_code",
            "common_name",
            "system",
            "variant_class",
            "method",
            "expected_bp",
            "observed_bp",
            "delta_bp",
            "detected",
            "confidence",
            "qc_status",
        ]
        if c in matched_view.columns
    ]
    st.dataframe(
        matched_view[display_cols] if display_cols else matched_view,
        use_container_width=True,
        hide_index=True,
        column_config={
            "confidence": st.column_config.ProgressColumn("confidence", min_value=0, max_value=1, format="%.2f"),
            "detected": st.column_config.CheckboxColumn("detected"),
        },
    )
    st.download_button(
        "⬇️ Download PCR matching results",
        matched_view.to_csv(index=False).encode("utf-8"),
        "pcr_allele_matching_results_expert.csv",
        "text/csv",
        use_container_width=True,
    )

    if len(strong):
        summary_lines = [
            f"• {r.sample_id}: {r.common_name} ({r.variant_class}, {r.confidence*100:.0f}% confidence)"
            for r in strong.itertuples()
        ]
        clinical_box("<b>Strong detected allele summary</b><br>" + "<br>".join(summary_lines), "warn")
    elif len(detected):
        clinical_box(
            "Detected targets are present, but none reached the selected strong-call confidence cutoff. Review lane quality, primer specificity, controls, and repeat criteria before reporting.",
            "warn",
        )
    else:
        clinical_box(
            "No target-positive PCR calls were detected in the current table. Review control lanes, input formatting, and whether the uploaded assay covers the suspected variant.",
            "success",
        )


# -----------------------------------------------------------------------------
# Tab 3: Couple genotype risk
# -----------------------------------------------------------------------------
with tabs[2]:
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

    r1, r2 = st.columns([1.12, 0.88])
    with r1:
        st.plotly_chart(expert_punnett_heatmap(result, system), use_container_width=True, theme=None)
    with r2:
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
# Tab 4: Export/report area
# -----------------------------------------------------------------------------
with tabs[3]:
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
            {"Module": "PCR matching", "Export": "CSV", "Purpose": "Per-lane allele calls, confidence, and QC status"},
            {"Module": "Virtual gel", "Export": "Plotly image from browser", "Purpose": "Visual review of band positions and lane patterns"},
            {"Module": "Couple risk", "Export": "CSV", "Purpose": "Punnett genotype/phenotype/risk evidence table"},
            {"Module": "Consult note", "Export": "HTML/PDF extension recommended", "Purpose": "Molecular interpretation and genetic-counseling prompt"},
        ]
    )
    st.dataframe(report_items, use_container_width=True, hide_index=True)

    st.markdown(
        """
        **Suggested next enhancement:** add a one-click molecular consult report generator with these sections: sample metadata, assay panel, positive/negative controls, PCR call table, gel visualization, allele interpretation, reproductive-risk summary, limitations, and sign-out block.
        """
    )

