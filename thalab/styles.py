from __future__ import annotations

import html
from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class PageSpec:
    key: str
    title: str
    path: str
    icon: str
    caption: str
    badge: str


PAGES: tuple[PageSpec, ...] = (
    PageSpec(
        key="Command center",
        title="Command Center",
        path="app.py",
        icon="🏠",
        caption="Executive overview, workflow map, population demo, and module launcher.",
        badge="Home",
    ),
    PageSpec(
        key="Laboratory screening",
        title="Laboratory Screening",
        path="pages/1_Laboratory_Screening_Test.py",
        icon="🧪",
        caption="CBC, iron status, Hb typing, OF/DCIP/HbH inclusion, and reflex planning.",
        badge="Screen",
    ),
    PageSpec(
        key="PCR allele matching",
        title="PCR Allele Matching",
        path="pages/2_PCR_Allele_Matching.py",
        icon="🧬",
        caption="α/β-globin allele panel intelligence and couple-risk modeling.",
        badge="Genotype",
    ),
)


def current_theme_type() -> str:
    """Return Streamlit's active browser theme with a safe light fallback."""
    try:
        theme_type = str(st.context.theme.type).lower()
    except (AttributeError, RuntimeError):
        theme_type = "light"
    return theme_type if theme_type in {"light", "dark"} else "light"


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --blood-950:#210106; --blood-900:#3F0208; --blood-800:#650512; --blood-700:#8D0718;
            --blood-600:#B11226; --blood-500:#D7263D; --blood-400:#EF476F; --plasma-50:#FFF8F8;
            --plasma-100:#FFF1F2; --plasma-200:#FFE3E8; --marrow-100:#FFE9D6; --platelet:#F7B801;
            --oxygen:#11A8CD; --teal:#0E6B5A; --violet:#6D40D8; --ink:#24131A; --muted:#7B6570;
            --good:#0E8F68; --warn:#E8890C; --danger:#C91832; --paper:#FFFDFD;
            --app-bg:
                radial-gradient(circle at 0% 0%, rgba(215,38,61,.10), transparent 28%),
                radial-gradient(circle at 100% 12%, rgba(247,184,1,.11), transparent 25%),
                linear-gradient(180deg, #fffafa 0%, #fff8f8 58%, #fff 100%);
            --surface:rgba(255,255,255,.82); --surface-strong:#FFFDFD; --surface-soft:#FFF3F5;
            --surface-muted:#FFF8F8; --card-border:rgba(177,18,38,.14);
            --card-shadow:rgba(63,2,8,.085); --heading:#3F0208; --body-text:#24131A;
            --secondary-text:#654D58; --soft-text:#7B6570; --inverse-text:#FFFFFF;
            --code-bg:#FFE3E8; --code-text:#8D0718;
            color-scheme: light dark;
        }
        html, body, [class*="css"] {
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }
        body {
            background: var(--app-bg);
        }
        [data-testid="stAppViewContainer"] { background: var(--app-bg); color: var(--body-text); }
        .main .block-container { padding-top: 1.0rem; padding-bottom: 3.5rem; max-width: 1540px; }

        /* Real no-sidebar shell: native Streamlit sidebar and auto page navigation are hidden. */
        [data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="collapsedControl"] {
            display: none !important; visibility: hidden !important; width: 0 !important; min-width: 0 !important;
        }
        section[data-testid="stSidebar"] { display:none !important; }
        button[title="View fullscreen"] { border-radius: 999px !important; }

        .app-topbar {
            position: relative;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin: .15rem 0 .9rem 0;
            padding: .85rem 1rem;
            border: 1px solid rgba(177,18,38,.11);
            border-radius: 26px;
            background: rgba(255,255,255,.78);
            box-shadow: 0 18px 46px rgba(63,2,8,.075);
            backdrop-filter: blur(18px);
        }
        .brand-lockup { display:flex; align-items:center; gap:.78rem; }
        .brand-mark {
            width: 46px; height: 46px; border-radius: 17px;
            display:inline-flex; align-items:center; justify-content:center;
            background: linear-gradient(135deg, #3F0208, #D7263D 68%, #F7B801 130%);
            box-shadow: 0 14px 34px rgba(177,18,38,.28); color:white; font-size: 1.35rem;
        }
        .brand-title { font-weight: 950; color: var(--blood-900); line-height:1.08; letter-spacing:-.03em; font-size:1.12rem; }
        .brand-caption { color: var(--muted); font-size: .82rem; margin-top:.12rem; }
        .active-module-badge {
            display:inline-flex; align-items:center; gap:.4rem; border-radius:999px;
            padding:.45rem .75rem; color:#fff; font-weight:850; font-size:.82rem;
            background: linear-gradient(135deg, var(--blood-800), var(--blood-500));
            box-shadow: 0 10px 24px rgba(177,18,38,.22);
            white-space: nowrap;
        }
        .topbar-status { display:flex; align-items:center; justify-content:flex-end; gap:.5rem; flex-wrap:wrap; }
        .theme-auto-badge {
            display:inline-flex; align-items:center; gap:.4rem; border-radius:999px;
            padding:.42rem .7rem; border:1px solid var(--card-border);
            color:var(--secondary-text); background:var(--surface-soft);
            font-weight:800; font-size:.76rem; white-space:nowrap;
        }
        .theme-auto-badge:before { content:"◐"; color:var(--blood-500); font-size:.95rem; }

        .hero-card {
            position: relative; overflow: hidden;
            background: radial-gradient(circle at 7% 18%, rgba(255,255,255,.28), transparent 26%),
                        radial-gradient(circle at 88% 8%, rgba(247,184,1,.30), transparent 23%),
                        linear-gradient(135deg, #3F0208 0%, #8D0718 44%, #D7263D 72%, #F7B801 128%);
            border-radius: 32px; padding: 2.25rem 2.35rem; color: white;
            box-shadow: 0 32px 80px rgba(63,2,8,.28); margin-bottom: .9rem;
            border: 1px solid rgba(255,255,255,.18);
        }
        .hero-card:after { content:""; position:absolute; inset:auto -90px -140px auto; width:360px; height:360px; border-radius:50%; background: radial-gradient(circle, rgba(255,255,255,.20), transparent 62%); }
        .hero-eyebrow { text-transform: uppercase; letter-spacing: .14rem; font-weight: 850; opacity:.86; font-size:.78rem; }
        .hero-title { font-size: clamp(2.15rem, 5vw, 4.7rem); font-weight: 950; line-height:.98; margin:.42rem 0 .8rem 0; max-width: 1060px; }
        .hero-subtitle { font-size: 1.08rem; max-width: 960px; line-height:1.58; opacity:.95; }

        .nav-under-hero { margin: .1rem 0 1.15rem 0; }
        .nav-strip-label {
            display:flex; align-items:center; gap:.45rem; margin:.05rem 0 .6rem 0;
            color:#650512; font-weight:920; letter-spacing:-.01em;
        }
        .nav-strip-label span {
            display:inline-flex; border-radius:999px; padding:.24rem .56rem;
            background:#FFE3E8; color:#8D0718; font-size:.76rem; text-transform:uppercase; letter-spacing:.08rem;
        }
        .nav-card-current {
            display:block; width:100%; min-height: 172px;
            border: 1px solid rgba(177,18,38,.34);
            border-radius: 26px;
            padding: 1.05rem 1.1rem;
            background:
              radial-gradient(circle at 90% 10%, rgba(247,184,1,.20), transparent 32%),
              linear-gradient(135deg, #3F0208, #8D0718 54%, #D7263D 100%);
            color: white;
            box-shadow: 0 22px 58px rgba(177,18,38,.16);
            margin-bottom: .45rem;
        }
        .nav-card-current .nav-caption, .nav-card-current .nav-title { color:white; }
        .nav-icon { font-size: 2rem; margin-bottom: .45rem; }
        .nav-title { color: var(--blood-900); font-weight: 950; font-size: 1.05rem; letter-spacing:-.02em; margin-bottom:.28rem; }
        .nav-caption { color:#654D58; line-height:1.43; font-size:.9rem; min-height: 3.8rem; }
        .nav-badge {
            display:inline-flex; border: 1px solid rgba(177,18,38,.14); border-radius:999px;
            padding:.24rem .55rem; font-weight:850; font-size:.72rem;
            color: var(--blood-800); background: white; margin-bottom:.4rem;
        }
        .nav-card-current .nav-badge { background: rgba(255,255,255,.15); color: white; border-color: rgba(255,255,255,.22); }

        /* Streamlit page links are transformed into full clickable navigation cards.
           st.page_link navigates in the same browser tab by default. */
        div[data-testid="stPageLink"] { height: 100%; }
        div[data-testid="stPageLink"] a {
            display: block !important;
            width: 100% !important;
            min-height: 172px !important;
            white-space: normal !important;
            text-align: left !important;
            border: 1px solid rgba(177,18,38,.12) !important;
            border-radius: 26px !important;
            padding: 1.05rem 1.1rem !important;
            background:
              radial-gradient(circle at 12% 0%, rgba(215,38,61,.10), transparent 36%),
              linear-gradient(180deg, rgba(255,255,255,.96), rgba(255,242,244,.88)) !important;
            box-shadow: 0 18px 46px rgba(63,2,8,.075) !important;
            color: var(--blood-900) !important;
            font-weight: 850 !important;
            line-height: 1.36 !important;
            transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease !important;
        }
        div[data-testid="stPageLink"] a:hover {
            transform: translateY(-3px);
            border-color: rgba(177,18,38,.42) !important;
            box-shadow: 0 24px 62px rgba(177,18,38,.15) !important;
            text-decoration: none !important;
        }
        div[data-testid="stPageLink"] a p, div[data-testid="stPageLink"] a span {
            white-space: normal !important;
        }
        div[data-testid="stPageLink"] a code {
            border-radius:999px; padding:.17rem .42rem; background:#FFE3E8; color:#8D0718; font-weight:850;
        }

        .glass-card { background: rgba(255, 250, 250, .86); border: 1px solid rgba(177,18,38,.12); border-radius: 24px; padding: 1.15rem 1.25rem; box-shadow: 0 16px 42px rgba(63,2,8,.075); margin-bottom: 1rem; backdrop-filter: blur(12px); }
        .dense-card { background: linear-gradient(180deg, #FFFDFD, #FFF3F5); border: 1px solid rgba(215,38,61,.12); border-radius: 22px; padding: 1rem 1.1rem; box-shadow: 0 10px 26px rgba(63,2,8,.07); min-height: 132px; }
        .production-card {
            position: relative; overflow: hidden; border: 1px solid rgba(177,18,38,.12); border-radius: 26px;
            padding: 1.05rem 1.1rem; background: radial-gradient(circle at 12% 0%, rgba(215,38,61,.10), transparent 36%), linear-gradient(180deg, rgba(255,255,255,.96), rgba(255,242,244,.88));
            box-shadow: 0 18px 46px rgba(63,2,8,.075); min-height: 176px; margin-bottom: .45rem;
        }
        .production-card .nav-title { color: var(--blood-900); }
        .production-card .nav-caption { min-height:auto; }
        .metric-card { border-radius: 24px; padding: 1.05rem 1.1rem; background: linear-gradient(150deg, rgba(255,255,255,.95), rgba(255,236,239,.88)); border: 1px solid rgba(215,38,61,.14); box-shadow: 0 18px 44px rgba(63,2,8,.085); min-height: 136px; }
        .metric-label { font-size:.76rem; color:#7B6570; text-transform:uppercase; letter-spacing:.08rem; font-weight:850; }
        .metric-value { font-size:2.05rem; line-height:1.05; font-weight:950; color:#3F0208; margin:.35rem 0 .25rem; overflow-wrap:anywhere; }
        .metric-caption { color:#614A55; font-size:.9rem; line-height:1.38; }
        .metric-card.high { border-left: 9px solid var(--danger); } .metric-card.moderate { border-left: 9px solid var(--warn); } .metric-card.low { border-left: 9px solid var(--good); } .metric-card.info { border-left: 9px solid var(--oxygen); } .metric-card.danger { border-left: 9px solid var(--danger); }
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
        button[kind="primary"], .stDownloadButton button, .stButton button { border-radius:999px !important; font-weight:850 !important; }
        .stDataFrame, div[data-testid="stDataFrame"] { border-radius: 22px; overflow: hidden; }
        .footer-note { color: #806873; font-size: .82rem; text-align:center; margin: 2rem 0 .4rem; }

        /* Shared semantic colors. The media query follows the browser/OS preference
           automatically; Streamlit's native widgets use the paired config.toml themes. */
        .app-topbar {
            background: var(--surface);
            border-color: var(--card-border);
            box-shadow: 0 18px 46px var(--card-shadow);
        }
        .brand-title, .nav-title, .production-card .nav-title,
        .metric-value, .section-title { color: var(--heading); }
        .brand-caption, .nav-caption, .metric-caption { color: var(--secondary-text); }
        .nav-strip-label, .pill { color: var(--heading); }
        div[data-testid="stPageLink"] a {
            background:
              radial-gradient(circle at 12% 0%, rgba(215,38,61,.10), transparent 36%),
              linear-gradient(180deg, var(--surface-strong), var(--surface-soft)) !important;
            border-color: var(--card-border) !important;
            box-shadow: 0 18px 46px var(--card-shadow) !important;
            color: var(--heading) !important;
        }
        div[data-testid="stPageLink"] a code {
            background: var(--code-bg); color: var(--code-text);
        }
        .glass-card {
            background: var(--surface);
            border-color: var(--card-border);
            box-shadow: 0 16px 42px var(--card-shadow);
            color: var(--body-text);
        }
        .dense-card {
            background: linear-gradient(180deg, var(--surface-strong), var(--surface-soft));
            border-color: var(--card-border); box-shadow: 0 10px 26px var(--card-shadow);
            color: var(--body-text);
        }
        .production-card {
            background:
              radial-gradient(circle at 12% 0%, rgba(215,38,61,.10), transparent 36%),
              linear-gradient(180deg, var(--surface-strong), var(--surface-soft));
            border-color: var(--card-border); box-shadow: 0 18px 46px var(--card-shadow);
            color: var(--body-text);
        }
        .metric-card {
            background: linear-gradient(150deg, var(--surface-strong), var(--surface-soft));
            border-color: var(--card-border); box-shadow: 0 18px 44px var(--card-shadow);
        }
        .metric-label, .subtle, .footer-note { color: var(--soft-text); }
        .pill { background: var(--surface-strong); border-color: var(--card-border); box-shadow: 0 6px 16px var(--card-shadow); }
        .flow-step { background: var(--surface-muted); border-color: var(--card-border); color: var(--body-text); }
        .stTabs [data-baseweb="tab"] { background: var(--surface-soft); border-color: var(--card-border); color: var(--body-text); }

        @media (prefers-color-scheme: dark) {
            :root {
                --ink:#FFF4F6; --muted:#CDB7BF; --paper:#16090E;
                --app-bg:
                    radial-gradient(circle at 0% 0%, rgba(215,38,61,.18), transparent 30%),
                    radial-gradient(circle at 100% 12%, rgba(109,64,216,.14), transparent 28%),
                    linear-gradient(180deg, #11070B 0%, #16090E 58%, #0D0508 100%);
                --surface:rgba(35,15,23,.86); --surface-strong:#241018; --surface-soft:#30131E;
                --surface-muted:#1C0C12; --card-border:rgba(255,220,228,.15);
                --card-shadow:rgba(0,0,0,.34); --heading:#FFF4F6; --body-text:#F9EDEF;
                --secondary-text:#D8C1C8; --soft-text:#BFA7B1; --inverse-text:#FFFFFF;
                --code-bg:#451725; --code-text:#FFD3DD;
            }
            .brand-mark { box-shadow: 0 14px 34px rgba(239,71,111,.24); }
            .nav-strip-label span { background:#451725; color:#FFD3DD; }
            .nav-card-current {
                border-color:rgba(255,220,228,.18);
                background:
                  radial-gradient(circle at 90% 10%, rgba(247,184,1,.18), transparent 32%),
                  linear-gradient(135deg, #2B0912, #650512 54%, #B11226 100%);
            }
            div[data-testid="stPageLink"] a:hover {
                border-color:rgba(239,71,111,.48) !important;
                box-shadow:0 24px 62px rgba(0,0,0,.42) !important;
            }
            .pill.red { background:#451725; color:#FFD3DD; }
            .pill.gold { background:#44330C; color:#FFE49A; }
            .pill.green { background:#103C31; color:#BDF4DF; }
            .pill.blue { background:#0D3541; color:#BFEFFA; }
            .pill.violet { background:#2C1D54; color:#DCCFFF; }
            .warn-box { background:#3D2A08; color:#FFE6AB; }
            .danger-box { background:#45121B; color:#FFD5DC; }
            .success-box { background:#0D342A; color:#C6F5E5; }
            .flow-index { background:#D7263D; }
        }
        @media (max-width: 900px) {
            .app-topbar { align-items:flex-start; flex-direction: column; }
            .topbar-status { justify-content:flex-start; }
            .active-module-badge { white-space: normal; }
            .nav-caption { min-height: auto; }
            div[data-testid="stPageLink"] a, .nav-card-current { min-height: auto !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _e(text: str) -> str:
    return html.escape(str(text), quote=True)


def _is_active(page: PageSpec, active: str) -> bool:
    active_clean = active.strip().lower()
    return page.key.strip().lower() == active_clean or page.title.strip().lower() == active_clean


def top_navigation(active: str) -> None:
    """Render only the brand/status bar. The card navigation is rendered under the page hero."""
    st.session_state["_thal_active_nav"] = active
    st.markdown(
        f"""
        <div class="app-topbar">
          <div class="brand-lockup">
            <div class="brand-mark">🩸</div>
            <div><div class="brand-title">ThalLink Laboratory Intelligence</div><div class="brand-caption"></div></div>
          </div>
          <div class="topbar-status">
            <div class="theme-auto-badge">Auto theme · browser/OS</div>
            <div class="active-module-badge">Active · {_e(active)}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_card_navigation(active: str | None = None) -> None:
    """Clickable page cards rendered directly beneath the hero area.

    Non-active cards are Streamlit page links, which open in the same tab. The active
    page is shown as a highlighted card to avoid a redundant self-navigation click.
    """
    active = active or st.session_state.get("_thal_active_nav", "Command center")

    cols = st.columns(len(PAGES))
    for col, page in zip(cols, PAGES):
        with col:
            if _is_active(page, active):
                st.markdown(
                    f"""
                    <div class="nav-card-current">
                      <span class="nav-badge">Current · {_e(page.badge)}</span>
                      <div class="nav-icon">{_e(page.icon)}</div>
                      <div class="nav-title">{_e(page.title)}</div>
                      <div class="nav-caption">{_e(page.caption)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                label = f"**{page.title}**  \n{page.caption}  \n\n`{page.badge}`"
                st.page_link(page.path, label=label, icon=page.icon, use_container_width=True)


def module_launch_card(title: str, body: str, bullets: list[str], page_path: str, icon: str, cta: str) -> None:
    """Render a full-card navigation link for module launch areas."""
    bullet_text = "  \n".join(f"• {item}" for item in bullets)
    label = f"**{title}**  \n{body}  \n\n{bullet_text}  \n\n**{cta} →**"
    st.page_link(page_path, label=label, icon=icon, use_container_width=True)


def hero(title: str, subtitle: str, eyebrow: str = "Expert hematology decision support", show_navigation: bool = True) -> None:
    st.markdown(
        f"""<div class="hero-card"><div class="hero-eyebrow">{_e(eyebrow)}</div><div class="hero-title">{_e(title)}</div><div class="hero-subtitle">{_e(subtitle)}</div></div>""",
        unsafe_allow_html=True,
    )
    if show_navigation:
        page_card_navigation()


def section(title: str, caption: str | None = None) -> None:
    st.markdown(f'<h2 class="section-title">{_e(title)}</h2>', unsafe_allow_html=True)
    if caption:
        st.markdown(f'<div class="subtle">{_e(caption)}</div>', unsafe_allow_html=True)


def metric_card(label: str, value: str, caption: str = "", level: str = "info") -> None:
    safe_level = level if level in {"info", "high", "moderate", "low", "danger"} else "info"
    st.markdown(
        f"""<div class="metric-card {safe_level}"><div class="metric-label">{_e(label)}</div><div class="metric-value">{_e(value)}</div><div class="metric-caption">{_e(caption)}</div></div>""",
        unsafe_allow_html=True,
    )


def clinical_box(text: str, level: str = "warn") -> None:
    cls = {"warn": "warn-box", "danger": "danger-box", "success": "success-box"}.get(level, "warn-box")
    st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)


def pills(items: list[str], color: str = "red") -> None:
    html_out = '<div class="pill-row">' + "".join([f'<span class="pill {color}">{_e(i)}</span>' for i in items]) + "</div>"
    st.markdown(html_out, unsafe_allow_html=True)


def disclaimer() -> None:
    st.markdown(
        """<div class="warn-box"><b>Laboratory decision support only.</b> Interpretive statements should be reviewed by a qualified hematology laboratory professional. CBC indices and Hb fractions can suggest carrier states, but confirmatory Hb analysis, iron studies, and/or molecular testing are required in clinically important or reproductive-risk settings.</div>""",
        unsafe_allow_html=True,
    )


def production_footer() -> None:
    st.markdown(
        '<div class="footer-note">ThalLink is designed as a validated-laboratory decision-support interface. Confirm local cutoffs, molecular panels, QC rules, and reporting language before production sign-out.</div>',
        unsafe_allow_html=True,
    )


# Backward-compatible name. It no longer uses st.sidebar.
def sidebar_brand(active: str) -> None:
    top_navigation(active)
