from __future__ import annotations

import streamlit as st


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --blood-950:#210106; --blood-900:#3F0208; --blood-800:#650512; --blood-700:#8D0718;
            --blood-600:#B11226; --blood-500:#D7263D; --blood-400:#EF476F; --plasma-50:#FFF8F8;
            --plasma-100:#FFF1F2; --plasma-200:#FFE3E8; --marrow-100:#FFE9D6; --platelet:#F7B801;
            --oxygen:#11A8CD; --teal:#0E6B5A; --violet:#6D40D8; --ink:#24131A; --muted:#7B6570;
            --good:#0E8F68; --warn:#E8890C; --danger:#C91832;
        }
        html, body, [class*="css"] { font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
        .main .block-container { padding-top: 1.05rem; padding-bottom: 3.5rem; max-width: 1540px; }
        [data-testid="stSidebar"] { background: linear-gradient(180deg, #210106 0%, #650512 56%, #100003 100%); }
        [data-testid="stSidebar"] * { color: #fff7f7 !important; }
        [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.18); }
        .hero-card { position: relative; overflow: hidden; background: radial-gradient(circle at 7% 18%, rgba(255,255,255,.28), transparent 26%), radial-gradient(circle at 88% 8%, rgba(247,184,1,.30), transparent 23%), linear-gradient(135deg, #3F0208 0%, #8D0718 44%, #D7263D 72%, #F7B801 128%); border-radius: 32px; padding: 2.25rem 2.35rem; color: white; box-shadow: 0 32px 80px rgba(63,2,8,.28); margin-bottom: 1.3rem; border: 1px solid rgba(255,255,255,.18); }
        .hero-card:after { content:""; position:absolute; inset:auto -90px -140px auto; width:360px; height:360px; border-radius:50%; background: radial-gradient(circle, rgba(255,255,255,.20), transparent 62%); }
        .hero-eyebrow { text-transform: uppercase; letter-spacing: .14rem; font-weight: 850; opacity:.86; font-size:.78rem; }
        .hero-title { font-size: clamp(2.15rem, 5vw, 4.7rem); font-weight: 950; line-height:.98; margin:.42rem 0 .8rem 0; max-width: 1060px; }
        .hero-subtitle { font-size: 1.08rem; max-width: 960px; line-height:1.58; opacity:.95; }
        .glass-card { background: rgba(255, 250, 250, .86); border: 1px solid rgba(177,18,38,.12); border-radius: 24px; padding: 1.15rem 1.25rem; box-shadow: 0 16px 42px rgba(63,2,8,.075); margin-bottom: 1rem; backdrop-filter: blur(12px); }
        .dense-card { background: linear-gradient(180deg, #FFFDFD, #FFF3F5); border: 1px solid rgba(215,38,61,.12); border-radius: 22px; padding: 1rem 1.1rem; box-shadow: 0 10px 26px rgba(63,2,8,.07); min-height: 128px; }
        .metric-card { border-radius: 24px; padding: 1.05rem 1.1rem; background: linear-gradient(150deg, rgba(255,255,255,.95), rgba(255,236,239,.88)); border: 1px solid rgba(215,38,61,.14); box-shadow: 0 18px 44px rgba(63,2,8,.085); min-height: 136px; }
        .metric-label { font-size:.76rem; color:#7B6570; text-transform:uppercase; letter-spacing:.08rem; font-weight:850; }
        .metric-value { font-size:2.05rem; line-height:1.05; font-weight:950; color:#3F0208; margin:.35rem 0 .25rem; }
        .metric-caption { color:#614A55; font-size:.9rem; line-height:1.38; }
        .metric-card.high { border-left: 9px solid var(--danger); } .metric-card.moderate { border-left: 9px solid var(--warn); } .metric-card.low { border-left: 9px solid var(--good); } .metric-card.info { border-left: 9px solid var(--oxygen); }
        .section-title { font-size:1.35rem; font-weight:920; color:#3F0208; margin: 1.45rem 0 .7rem; letter-spacing:-.02em; }
        .subtle { color:#7B6570; font-size:.93rem; }
        .pill-row { display:flex; flex-wrap:wrap; gap:.45rem; margin:.35rem 0 .8rem; }
        .pill { display:inline-flex; align-items:center; border-radius:999px; padding:.38rem .68rem; font-weight:800; font-size:.79rem; border:1px solid rgba(215,38,61,.16); background:#fff; color:#650512; box-shadow: 0 6px 16px rgba(63,2,8,.06); }
        .pill.red { background:#FFE3E8; color:#8D0718; } .pill.gold { background:#FFF1C7; color:#815705; } .pill.green { background:#DEF7EC; color:#07513E; } .pill.blue { background:#E1F5FA; color:#075B70; } .pill.violet { background:#EEE7FF; color:#4C2AB0; }
        .warn-box { border-left: 7px solid #E8890C; background:#FFF6E5; padding:1rem 1.1rem; border-radius:16px; color:#4B2C00; margin:.8rem 0; }
        .danger-box { border-left: 7px solid #C91832; background:#FFE4E8; padding:1rem 1.1rem; border-radius:16px; color:#5B0610; margin:.8rem 0; }
        .success-box { border-left: 7px solid #0E8F68; background:#E8F8F1; padding:1rem 1.1rem; border-radius:16px; color:#073B2E; margin:.8rem 0; }
        .flow-step { display:flex; gap:.85rem; align-items:flex-start; padding:.8rem .9rem; border-radius:18px; background:#FFF8F8; border:1px dashed rgba(177,18,38,.25); margin:.45rem 0; }
        .flow-index { width:28px; height:28px; border-radius:999px; background:#8D0718; color:#fff; display:inline-flex; align-items:center; justify-content:center; font-weight:900; flex:0 0 auto; }
        .stTabs [data-baseweb="tab-list"] { gap: .55rem; }
        .stTabs [data-baseweb="tab"] { border-radius: 999px; padding: .6rem 1rem; background:#FFF1F2; border:1px solid rgba(215,38,61,.12); font-weight:800; }
        .stTabs [aria-selected="true"] { background: linear-gradient(135deg,#650512,#D7263D)!important; color:white!important; }
        button[kind="primary"] { border-radius:999px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, eyebrow: str = "Expert hematology decision support") -> None:
    st.markdown(f"""<div class="hero-card"><div class="hero-eyebrow">{eyebrow}</div><div class="hero-title">{title}</div><div class="hero-subtitle">{subtitle}</div></div>""", unsafe_allow_html=True)


def section(title: str, caption: str | None = None) -> None:
    st.markdown(f'<h2 class="section-title">{title}</h2>', unsafe_allow_html=True)
    if caption:
        st.markdown(f'<div class="subtle">{caption}</div>', unsafe_allow_html=True)


def metric_card(label: str, value: str, caption: str = "", level: str = "info") -> None:
    st.markdown(f"""<div class="metric-card {level}"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-caption">{caption}</div></div>""", unsafe_allow_html=True)


def clinical_box(text: str, level: str = "warn") -> None:
    cls = {"warn": "warn-box", "danger": "danger-box", "success": "success-box"}.get(level, "warn-box")
    st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)


def pills(items: list[str], color: str = "red") -> None:
    html = '<div class="pill-row">' + "".join([f'<span class="pill {color}">{i}</span>' for i in items]) + "</div>"
    st.markdown(html, unsafe_allow_html=True)


def disclaimer() -> None:
    st.markdown("""<div class="warn-box"><b>Laboratory decision support only.</b> Interpretive statements should be reviewed by a qualified hematology laboratory professional. CBC indices and Hb fractions can suggest carrier states, but confirmatory Hb analysis, iron studies, and/or molecular testing are required in clinically important or reproductive-risk settings.</div>""", unsafe_allow_html=True)


def sidebar_brand(active: str) -> None:
    with st.sidebar:
        st.markdown("# 🩸 Thal Lab Consult")
        st.caption("Expert laboratory consult workspace")
        st.markdown("---")
        st.page_link("app.py", label="Command center", icon="🏠")
        st.page_link("pages/1_Laboratory_Screening_Test.py", label="Laboratory screening", icon="🧪")
        st.page_link("pages/2_PCR_Allele_Matching.py", label="PCR allele matching", icon="🧬")
        st.markdown("---")
        st.caption(f"Active module: {active}")
