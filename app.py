# app.py — CibleNet — Interface Streamlit
# Sidebar sticky + 8 pages : Dashboard | Scoring | Pipeline | Messages
#                             Import Excel | Export Excel | Scraping | LinkedIn

import streamlit as st
import pandas as pd
import io
from datetime import date

from database import (
    bootstrap, search_entreprises, get_pipeline,
    get_converted_entreprises, update_statut, save_message,
    get_stats, get_entreprise_by_id, get_all_entreprises,
    get_connection,
)
from llm      import generer_message_prospect, generer_relance, groq_disponible, get_message_simule
from notifier import envoyer_gmail, envoyer_whatsapp, envoyer_sms, canaux_actifs
from scoring  import score_prospect

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CibleNet",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)
bootstrap()

# ══════════════════════════════════════════════════════════════════════════════
# ICONES SVG LUCIDE (MIT License)
# ══════════════════════════════════════════════════════════════════════════════

def icon(name: str, size: int = 16, color: str = "currentColor") -> str:
    base = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;">'
    )
    paths = {
        "home":           '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
        "target":         '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
        "clipboard":      '<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>',
        "message-square": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
        "upload":         '<polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/>',
        "download":       '<polyline points="8 17 12 21 16 17"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.88 18.09A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.83"/>',
        "globe":          '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
        "linkedin":       '<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/>',
        "radio":          '<circle cx="12" cy="12" r="2"/><path d="M16.24 7.76a6 6 0 0 1 0 8.49m-8.48-.01a6 6 0 0 1 0-8.49m11.31-2.82a10 10 0 0 1 0 14.14m-14.14 0a10 10 0 0 1 0-14.14"/>',
        "building":       '<rect x="4" y="2" width="16" height="20" rx="2" ry="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01M16 6h.01M8 10h.01M16 10h.01M8 14h.01M16 14h.01"/>',
        "flame":          '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>',
        "check-circle":   '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
        "percent":        '<line x1="19" y1="5" x2="5" y2="19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>',
        "bar-chart":      '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',
        "activity":       '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
        "zap":            '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
        "snowflake":      '<line x1="2" y1="12" x2="22" y2="12"/><line x1="12" y1="2" x2="12" y2="22"/><path d="m20 16-4-4 4-4"/><path d="m4 8 4 4-4 4"/><path d="m16 4-4 4-4-4"/><path d="m8 20 4-4 4 4"/>',
        "trending-up":    '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
        "mail":           '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>',
        "send":           '<line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>',
        "refresh-cw":     '<polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>',
        "circle":         '<circle cx="12" cy="12" r="10"/>',
        "x-circle":       '<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>',
        "timer":          '<line x1="10" y1="2" x2="14" y2="2"/><circle cx="12" cy="14" r="8"/><polyline points="12 6 12 14 16 16"/>',
        "clock":          '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
        "search":         '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
        "layers":         '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
        "map-pin":        '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
        "users":          '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
        "factory":        '<path d="M2 20a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8l-7 5V8l-7 5V4a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"/>',
        "credit-card":    '<rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/>',
        "briefcase":      '<rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
        "edit":           '<path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>',
        "check":          '<polyline points="20 6 9 20 4 14"/>',
        "info":           '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>',
        "alert-triangle": '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
        "handshake":      '<path d="M20.42 4.58a5.4 5.4 0 0 0-7.65 0l-.77.78-.77-.78a5.4 5.4 0 0 0-7.65 0C1.46 6.7 1.33 10.28 4 13l8 8 8-8c2.67-2.72 2.54-6.3.42-8.42z"/>',
        "wifi":           '<path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><line x1="12" y1="20" x2="12.01" y2="20"/>',
        "star":           '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
        "lock":           '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
        "database":       '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>',
        "table":          '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M3 15h18M9 3v18"/>',
        "settings":       '<circle cx="12" cy="12" r="3"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M4.93 4.93a10 10 0 0 0 0 14.14"/>',
    }
    body = paths.get(name, '<circle cx="12" cy="12" r="4"/>')
    return f"{base}{body}</svg>"

def ic(name, size=15, color="currentColor"):
    return icon(name, size, color)

# ══════════════════════════════════════════════════════════════════════════════
# CSS GLOBAL
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
:root {
    --vert-foret:#1B4332; --vert-sauge:#52796F; --vert-clair:#84A98C;
    --beige-chaud:#F8F5F0; --beige-sombre:#EDE8E1;
    --or-pale:#F9E8A0; --ardoise:#2D3748; --gris-doux:#718096; --blanc:#FEFEFE;
}
html,body,[class*="css"]{ font-family:'Inter',sans-serif !important; }
.stApp{ background:linear-gradient(135deg,#F8F5F0 0%,#EDE8E1 100%) !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#1B4332 0%,#2D5A45 55%,#3D7A5E 100%) !important;
    border-right:none !important;
    box-shadow:4px 0 20px rgba(27,67,50,0.3) !important;
}
[data-testid="stSidebar"] > div:first-child{ padding-top:0 !important; }

/* Boutons navigation sidebar */
[data-testid="stSidebar"] .stButton > button {
    background:transparent !important;
    color:rgba(255,255,255,0.85) !important;
    border:1px solid transparent !important;
    border-radius:10px !important;
    padding:9px 14px !important;
    font-size:0.87rem !important;
    font-weight:500 !important;
    text-align:left !important;
    width:100% !important;
    justify-content:flex-start !important;
    box-shadow:none !important;
    transition:background 0.15s,border-color 0.15s !important;
}
[data-testid="stSidebar"] .stButton > button:hover{
    background:rgba(255,255,255,0.12) !important;
    color:#fff !important;
    border-color:rgba(255,255,255,0.2) !important;
    transform:none !important;
    box-shadow:none !important;
}
[data-testid="stSidebar"] .stButton > button:focus{
    box-shadow:none !important; outline:none !important;
}
[data-testid="stSidebar"] .stButton > button p{
    color:inherit !important; font-size:inherit !important;
    font-weight:inherit !important; margin:0 !important;
}
/* Etat actif via classe injectée dynamiquement */
[data-testid="stSidebar"] .nav-actif .stButton > button{
    background:rgba(255,255,255,0.18) !important;
    color:#fff !important;
    font-weight:700 !important;
    border-color:rgba(255,255,255,0.3) !important;
}
[data-testid="stSidebar"] .nav-actif .stButton > button p{
    font-weight:700 !important; color:#fff !important;
}

/* ── Hero ── */
.hero-header{
    background:linear-gradient(135deg,#1B4332 0%,#52796F 60%,#84A98C 100%);
    border-radius:18px; padding:30px 38px; margin-bottom:22px;
    box-shadow:0 8px 32px rgba(27,67,50,0.22); position:relative; overflow:hidden;
}
.hero-title{ font-size:1.85rem; font-weight:700; color:#FEFEFE; margin:0; letter-spacing:-0.4px; }
.hero-subtitle{ font-size:0.92rem; color:rgba(255,255,255,0.72); margin:4px 0 12px; }
.hero-badges{ display:flex; gap:8px; flex-wrap:wrap; }
.hero-badge{
    display:inline-flex; align-items:center; gap:5px;
    background:rgba(212,160,23,0.22); color:#F9E8A0;
    border:1px solid rgba(212,160,23,0.4); border-radius:20px;
    padding:4px 12px; font-size:0.73rem; font-weight:600;
    letter-spacing:0.5px; text-transform:uppercase;
}
.hero-badge-alt{
    display:inline-flex; align-items:center; gap:5px;
    background:rgba(255,255,255,0.12); color:rgba(255,255,255,0.85);
    border:1px solid rgba(255,255,255,0.2); border-radius:20px;
    padding:4px 12px; font-size:0.73rem; font-weight:500;
}

/* ── Metric card ── */
.metric-card{
    background:#fff; border-radius:14px; padding:18px 20px; text-align:center;
    box-shadow:0 2px 14px rgba(27,67,50,0.08); border:1px solid rgba(82,121,111,0.12);
    transition:transform 0.2s,box-shadow 0.2s; position:relative; overflow:hidden;
}
.metric-card::before{
    content:''; position:absolute; top:0; left:0; right:0; height:3px;
    background:linear-gradient(90deg,#1B4332,#52796F); border-radius:14px 14px 0 0;
}
.metric-card:hover{ transform:translateY(-3px); box-shadow:0 6px 22px rgba(27,67,50,0.14); }
.metric-icon-wrap{
    display:inline-flex; align-items:center; justify-content:center;
    background:linear-gradient(135deg,#D1FAE5,#A7F3D0);
    border-radius:11px; width:42px; height:42px; margin:0 auto 9px;
}
.metric-value{ font-size:1.85rem; font-weight:700; color:#1B4332; line-height:1.1; }
.metric-label{ font-size:0.76rem; color:#718096; font-weight:500; margin-top:3px;
    text-transform:uppercase; letter-spacing:0.5px; }

/* ── Score badges ── */
.score-badge{
    display:inline-flex; align-items:center; gap:5px; padding:4px 12px;
    border-radius:20px; font-weight:700; font-size:0.81rem;
    box-shadow:0 2px 8px rgba(0,0,0,0.07);
}
.score-high  { background:linear-gradient(135deg,#D1FAE5,#A7F3D0); color:#065F46; border:1px solid #6EE7B7; }
.score-medium{ background:linear-gradient(135deg,#FEF3C7,#FDE68A); color:#92400E; border:1px solid #FCD34D; }
.score-low   { background:linear-gradient(135deg,#FEE2E2,#FECACA); color:#991B1B; border:1px solid #FCA5A5; }

/* ── Section titre ── */
.section-title{ font-size:1.18rem; font-weight:700; color:#1B4332;
    margin-bottom:4px; display:flex; align-items:center; gap:10px; }
.section-divider{ height:2px; background:linear-gradient(90deg,#52796F,transparent);
    border-radius:2px; margin:6px 0 18px; }

/* ── Filtre ── */
.filter-section{ background:#fff; border-radius:14px; padding:16px 20px;
    margin-bottom:18px; box-shadow:0 2px 10px rgba(27,67,50,0.06);
    border:1px solid rgba(82,121,111,0.1); }

/* ── Detail card ── */
.detail-card{ background:#fff; border-radius:14px; padding:20px;
    box-shadow:0 4px 18px rgba(27,67,50,0.09); border:1px solid rgba(82,121,111,0.12); }

/* ── Info tag ── */
.info-tag{ display:inline-flex; align-items:center; gap:4px;
    background:#EDE8E1; color:#2D3748; border-radius:7px; padding:3px 9px;
    font-size:0.79rem; font-weight:500; margin:2px 2px 2px 0;
    border:1px solid rgba(82,121,111,0.14); }
.info-tag.good{ background:#D1FAE5; color:#065F46; border-color:#6EE7B7; }
.info-tag.bad { background:#FEE2E2; color:#991B1B; border-color:#FCA5A5; }
.info-tag.signal{ background:linear-gradient(135deg,#FEF3C7,#FDE68A); color:#92400E; border-color:#FCD34D; }

/* ── Empty state ── */
.empty-state{ text-align:center; padding:40px 24px; background:#fff;
    border-radius:14px; border:2px dashed rgba(82,121,111,0.28); }
.empty-state-icon{ display:inline-flex; align-items:center; justify-content:center;
    background:#EDE8E1; border-radius:50%; width:60px; height:60px; margin:0 auto 14px; }
.empty-state-text{ color:#718096; font-weight:500; font-size:0.93rem; }
.empty-state-sub{ color:#718096; font-size:0.82rem; opacity:0.7; margin-top:5px; }

/* ── Kanban ── */
.kanban-header{ background:linear-gradient(135deg,#EDE8E1,#F8F5F0);
    border-radius:10px; padding:10px 13px; margin-bottom:10px;
    border:1px solid rgba(82,121,111,0.14); }
.kanban-header h4{ margin:0; color:#1B4332; font-size:0.84rem; font-weight:700;
    display:flex; align-items:center; gap:7px; }
.kanban-count{ border-radius:8px; padding:2px 7px; font-size:0.74rem;
    font-weight:700; margin-left:auto; }

/* ── Handoff card ── */
.handoff-card{ background:#fff; border-radius:16px; padding:24px; margin-bottom:14px;
    box-shadow:0 4px 22px rgba(27,67,50,0.09); border:1px solid rgba(82,121,111,0.14);
    border-top:4px solid #52796F; }

/* ── Impact card ── */
.impact-card{ background:linear-gradient(135deg,#1B4332 0%,#52796F 100%);
    border-radius:14px; padding:20px 16px; text-align:center; color:#fff;
    box-shadow:0 4px 18px rgba(27,67,50,0.22); }
.impact-value{ font-size:1.75rem; font-weight:700; color:#F9E8A0; line-height:1; }
.impact-label{ font-size:0.76rem; opacity:0.82; margin-top:5px; text-transform:uppercase; letter-spacing:0.6px; }

/* ── Buttons ── */
.stButton > button{ border-radius:9px !important; font-weight:600 !important;
    font-size:0.87rem !important; padding:7px 16px !important;
    transition:all 0.2s !important; border:1.5px solid transparent !important; }
.stButton > button[kind="primary"]{
    background:linear-gradient(135deg,#1B4332,#52796F) !important;
    color:#fff !important; box-shadow:0 4px 12px rgba(27,67,50,0.28) !important; }
.stButton > button[kind="primary"]:hover{ transform:translateY(-2px) !important; }
.stButton > button[kind="secondary"]{
    background:#fff !important; color:#1B4332 !important;
    border-color:rgba(82,121,111,0.4) !important; }

/* ── Misc ── */
.stAlert{ border-radius:11px !important; }
.stDataFrame{ border-radius:11px !important; overflow:hidden; }
.stTextArea textarea{ border-radius:9px !important; font-family:'Inter',sans-serif !important; font-size:0.87rem !important; }
.stSelectbox > div > div{ border-radius:9px !important; }
.streamlit-expanderHeader{ border-radius:9px !important; background:#EDE8E1 !important; font-weight:600 !important; }
hr{ border-color:rgba(82,121,111,0.18) !important; margin:16px 0 !important; }
.stProgress > div > div{ background:linear-gradient(90deg,#1B4332,#52796F) !important; border-radius:3px !important; }
::-webkit-scrollbar{ width:5px; height:5px; }
::-webkit-scrollbar-track{ background:#EDE8E1; }
::-webkit-scrollbar-thumb{ background:#84A98C; border-radius:3px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS VISUELS
# ══════════════════════════════════════════════════════════════════════════════

def badge_score(score):
    if score >= 75:
        return f'<span class="score-badge score-high">{ic("flame",13,"#065F46")} {score}/100 — Haute priorite</span>'
    elif score >= 50:
        return f'<span class="score-badge score-medium">{ic("zap",13,"#92400E")} {score}/100 — Priorite moyenne</span>'
    else:
        return f'<span class="score-badge score-low">{ic("snowflake",13,"#991B1B")} {score}/100 — Faible priorite</span>'

def badge_score_compact(score):
    if score >= 75:
        return f'<span class="score-badge score-high">{ic("flame",12,"#065F46")} {score}/100</span>'
    elif score >= 50:
        return f'<span class="score-badge score-medium">{ic("zap",12,"#92400E")} {score}/100</span>'
    else:
        return f'<span class="score-badge score-low">{ic("snowflake",12,"#991B1B")} {score}/100</span>'

STATUT_CONFIG = {
    "Nouveau":              ("circle",       "#52796F"),
    "Score":                ("bar-chart",    "#D4A017"),
    "Contacte":             ("mail",         "#2B6CB0"),
    "Relance":              ("refresh-cw",   "#9C4221"),
    "Converti":             ("check-circle", "#065F46"),
    "Non interesse":        ("x-circle",     "#991B1B"),
    "A relancer plus tard": ("timer",        "#6B46C1"),
    "Scor\u00e9":           ("bar-chart",    "#D4A017"),
    "Contact\u00e9":        ("mail",         "#2B6CB0"),
    "Relanc\u00e9":         ("refresh-cw",   "#9C4221"),
    "Non int\u00e9ress\u00e9":   ("x-circle","#991B1B"),
    "\u00c0 relancer plus tard": ("timer",   "#6B46C1"),
}

def label_statut(statut):
    cfg = STATUT_CONFIG.get(statut, ("circle","#718096"))
    return f'<span style="display:inline-flex;align-items:center;gap:5px;">{ic(cfg[0],13,cfg[1])} {statut}</span>'

def afficher_detail_score(entreprise):
    score   = entreprise["score"]
    reasons = entreprise.get("score_reasons","")
    st.markdown(badge_score(score), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<span style="font-weight:600;color:#1B4332;display:flex;align-items:center;gap:6px;">{ic("layers",14,"#52796F")} Detail du score ICP</span>', unsafe_allow_html=True)
    if reasons:
        for r in reasons.split(" | "):
            st.markdown(f'<div style="display:flex;align-items:flex-start;gap:6px;margin:3px 0;font-size:0.84rem;color:#2D3748;">{ic("check",12,"#52796F")} {r}</div>', unsafe_allow_html=True)
    st.progress(score / 100)

# ══════════════════════════════════════════════════════════════════════════════
# IMPORT / EXPORT EXCEL
# ══════════════════════════════════════════════════════════════════════════════

def _detecter_colonne(df_cols, candidats):
    def norm(s): return s.lower().replace(" ","").replace("_","").replace("-","")
    norms = {norm(c): c for c in df_cols}
    for cand in candidats:
        if norm(cand) in norms:
            return norms[norm(cand)]
    return None

def _imputer_dataframe(df):
    rapports = []
    for col in df.columns:
        nb = df[col].isna().sum()
        if nb == 0:
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            med = df[col].median()
            if pd.isna(med): med = 0
            df[col] = df[col].fillna(med)
            rapports.append(f"'{col}' : {nb} valeur(s) manquante(s) remplacee(s) par la mediane ({int(med)})")
        else:
            DEFAULTS = {
                "secteur":"Autre","activite":"Autre","sector":"Autre",
                "localisation":"Lome","ville":"Lome","city":"Lome",
                "signalcroissance":"","signal":"",
                "siteweb":"false","paiementenlignefalse":"false",
            }
            col_norm = col.lower().replace(" ","").replace("_","")
            default = DEFAULTS.get(col_norm)
            if default is None:
                m = df[col].dropna().mode()
                default = str(m.iloc[0]) if len(m) > 0 else ""
            df[col] = df[col].fillna(default)
            rapports.append(f"'{col}' : {nb} valeur(s) manquante(s) remplacee(s) par '{default if default else '(vide)'}'")
    return df, rapports

def importer_excel(fichier):
    try:
        df = pd.read_excel(fichier, engine="openpyxl")
    except Exception as e:
        return 0, 0, [f"Erreur lecture : {e}"], []
    if df.empty:
        return 0, 0, ["Fichier vide."], []

    df.columns = [str(c).strip().lower().replace(" ","_") for c in df.columns]
    cols = list(df.columns)

    MAPPING = {
        "nom":               ["nom","name","entreprise","company","raison_sociale","societe","etablissement"],
        "secteur":           ["secteur","sector","activite","activite_principale","industrie","domaine","metier"],
        "localisation":      ["localisation","ville","city","location","adresse","region","zone"],
        "effectif":          ["effectif","employees","salaries","nb_employes","taille","headcount","staff"],
        "signal_croissance": ["signal_croissance","signal","croissance","growth","actualite","recrutement"],
        "site_web":          ["site_web","site","website","url","web"],
        "paiement_en_ligne": ["paiement_en_ligne","paiement","payment","ecommerce"],
    }

    col_map = {}
    for cible, candidats in MAPPING.items():
        t = _detecter_colonne(cols, candidats)
        if t:
            col_map[cible] = t

    if "nom" not in col_map:
        for c in cols:
            if not pd.api.types.is_numeric_dtype(df[c]):
                col_map["nom"] = c
                break
        if "nom" not in col_map:
            return 0, 0, ["Impossible de detecter la colonne des noms. Colonnes trouvees : " + ", ".join(cols)], []

    cols_utiles = list(col_map.values())
    df_work = df[cols_utiles].copy().rename(columns={v: k for k, v in col_map.items()})
    df_work, rapports = _imputer_dataframe(df_work)

    conn   = get_connection()
    cursor = conn.cursor()
    max_id = cursor.execute("SELECT MAX(id) FROM entreprises").fetchone()[0] or 0

    eff_med = 20
    if "effectif" in df_work.columns and pd.api.types.is_numeric_dtype(df_work["effectif"]):
        med = df_work["effectif"].median()
        if not pd.isna(med):
            eff_med = int(med)

    importes, ignores, erreurs = 0, 0, []

    for idx, row in df_work.iterrows():
        nom = str(row.get("nom","")).strip()
        if not nom or nom.lower() in ["nan","none",""]:
            ignores += 1
            continue
        if cursor.execute("SELECT id FROM entreprises WHERE LOWER(TRIM(nom))=LOWER(TRIM(?))",(nom,)).fetchone():
            ignores += 1
            continue

        def vt(c, d=""): v=str(row.get(c,d) or d).strip(); return d if v.lower() in ["nan","none",""] else v
        def vb(c): return str(row.get(c,"false")).lower().strip() in ["true","1","oui","yes","vrai","x"]

        try:
            eff_raw = row.get("effectif", eff_med)
            effectif = int(float(str(eff_raw))) if str(eff_raw).lower() not in ["nan","none",""] else eff_med
            effectif = max(1, min(effectif, 9999))
        except:
            effectif = eff_med

        prospect = {
            "nom": nom, "secteur": vt("secteur","Autre"),
            "localisation": vt("localisation","Lome"),
            "effectif": effectif, "signal_croissance": vt("signal_croissance",""),
            "site_web": vb("site_web"), "paiement_en_ligne": vb("paiement_en_ligne"),
        }
        try:
            score, reasons, _ = score_prospect(prospect)
        except Exception as e:
            erreurs.append(f"Ligne {idx+2} ({nom}) : scoring - {e}")
            score, reasons = 0, ""

        max_id += 1
        try:
            cursor.execute("""
                INSERT INTO entreprises
                    (id,nom,secteur,localisation,effectif,signal_croissance,
                     site_web,paiement_en_ligne,score,score_reasons,statut)
                VALUES (?,?,?,?,?,?,?,?,?,?,'Nouveau')
            """,(max_id,prospect["nom"],prospect["secteur"],prospect["localisation"],
                 prospect["effectif"],prospect["signal_croissance"],
                 prospect["site_web"],prospect["paiement_en_ligne"],score,reasons))
            importes += 1
        except Exception as e:
            erreurs.append(f"Ligne {idx+2} ({nom}) : insertion - {e}")
            ignores += 1

    conn.commit()
    conn.close()
    return importes, ignores, erreurs, rapports

def exporter_excel(data, colonnes=None):
    df = pd.DataFrame(data)
    if colonnes:
        df = df[[c for c in colonnes if c in df.columns]]
    renommage = {
        "id":"ID","nom":"Entreprise","secteur":"Secteur","localisation":"Ville",
        "effectif":"Effectif","signal_croissance":"Signal","site_web":"Site web",
        "paiement_en_ligne":"Paiement","score":"Score ICP","score_reasons":"Detail score",
        "statut":"Statut","date_contact":"Date contact","message_genere":"Message",
    }
    df = df.rename(columns={k:v for k,v in renommage.items() if k in df.columns})
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Prospects")
        ws = writer.sheets["Prospects"]
        for cc in ws.columns:
            w = max((len(str(c.value or "")) for c in cc), default=8)
            ws.column_dimensions[cc[0].column_letter].width = min(w+4, 50)
    buf.seek(0)
    return buf.read()

def generer_template_excel():
    df = pd.DataFrame([{
        "nom":"Exemple SA","secteur":"Banque","localisation":"Lome","effectif":80,
        "signal_croissance":"Ouverture d'une nouvelle agence","site_web":"true","paiement_en_ligne":"false"
    }])
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Prospects")
    buf.seek(0)
    return buf.read()

# ══════════════════════════════════════════════════════════════════════════════
# PAGES — definition
# ══════════════════════════════════════════════════════════════════════════════
PAGES = [
    ("dashboard", "Dashboard",           "home"),
    ("scoring",   "Recherche & Scoring", "target"),
    ("pipeline",  "Pipeline",            "clipboard"),
    ("messages",  "Messages & Relances", "message-square"),
    ("import",    "Import Excel",        "upload"),
    ("export",    "Export Excel",        "download"),
    ("scraping",  "Scraping Annuaires",  "globe"),
    ("linkedin",  "LinkedIn",            "linkedin"),
]

if "page_active" not in st.session_state:
    st.session_state["page_active"] = "dashboard"

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    stats = get_stats()

    # Logo
    st.markdown(f"""
    <div style="padding:20px 14px 12px;border-bottom:1px solid rgba(255,255,255,0.14);margin-bottom:4px;">
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="background:rgba(255,255,255,0.15);border-radius:9px;padding:7px;display:inline-flex;">
                {icon("radio",21,"white")}
            </div>
            <div>
                <div style="font-size:1.02rem;font-weight:700;color:#FFFFFF;line-height:1.15;">CibleNet</div>
                <div style="font-size:0.68rem;color:rgba(255,255,255,0.52);letter-spacing:0.2px;">Copilot Commercial</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    st.markdown(f"""
    <div style="padding:10px 12px 4px;">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:7px;">
            <div style="background:rgba(255,255,255,0.1);border-radius:9px;padding:9px 6px;text-align:center;">
                <div style="font-size:1.4rem;font-weight:700;color:#F9E8A0;line-height:1;">{stats['total']}</div>
                <div style="font-size:0.62rem;color:rgba(255,255,255,0.52);text-transform:uppercase;letter-spacing:0.5px;margin-top:2px;">Prospects</div>
            </div>
            <div style="background:rgba(255,255,255,0.1);border-radius:9px;padding:9px 6px;text-align:center;">
                <div style="font-size:1.4rem;font-weight:700;color:#A7F3D0;line-height:1;">{stats['convertis']}</div>
                <div style="font-size:0.62rem;color:rgba(255,255,255,0.52);text-transform:uppercase;letter-spacing:0.5px;margin-top:2px;">Convertis</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="border-top:1px solid rgba(255,255,255,0.11);margin:10px 0 6px;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 12px 5px;font-size:0.62rem;font-weight:700;color:rgba(255,255,255,0.35);text-transform:uppercase;letter-spacing:1.1px;">Navigation</div>', unsafe_allow_html=True)

    # Boutons navigation
    page_active = st.session_state["page_active"]

    # Injecter CSS icones via mask pour chaque bouton
    nav_css = ""
    ICO_PATHS = {
        "dashboard": "M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z M9 22V12h6v10",
        "scoring":   "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z M12 12m-2 0a2 2 0 1 0 4 0 2 2 0 0 0-4 0",
        "pipeline":  "M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2 M8 2h8v4H8z",
        "messages":  "M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z",
        "import":    "M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4 M7 10l5 5 5-5 M12 15V3",
        "export":    "M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4 M17 8l-5-5-5 5 M12 3v12",
        "scraping":  "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z M2 12h20 M12 2a15 15 0 0 1 4 10 15 15 0 0 1-4 10 15 15 0 0 1-4-10 15 15 0 0 1 4-10z",
        "linkedin":  "M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-4 0v7h-4v-7a6 6 0 0 1 6-6z M2 9h4v12H2z M4 6a2 2 0 1 0 0-4 2 2 0 0 0 0 4z",
    }
    for key, label, _ in PAGES:
        path_d = ICO_PATHS.get(key,"M12 12m-2 0a2 2 0 1 0 4 0 2 2 0 0 0-4 0")
        svg_uri = (
            "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
            "width='16' height='16' viewBox='0 0 24 24' fill='none' "
            "stroke='white' stroke-width='2' stroke-linecap='round' "
            f"stroke-linejoin='round'%3E%3Cpath d='{path_d}'/%3E%3C/svg%3E"
        )
        nav_css += f"""
        [data-testid="stSidebar"] div[data-testid="stVerticalBlock"] > div:has(button[data-testid*="nav_{key}"]) button::before {{
            content:''; display:inline-block; width:15px; height:15px; flex-shrink:0;
            background-color:rgba(255,255,255,0.8);
            -webkit-mask:url("{svg_uri}") center/contain no-repeat;
            mask:url("{svg_uri}") center/contain no-repeat;
            margin-right:8px;
        }}"""
        if key == page_active:
            nav_css += f"""
        [data-testid="stSidebar"] div[data-testid="stVerticalBlock"] > div:has(button[data-testid*="nav_{key}"]) button {{
            background:rgba(255,255,255,0.18) !important;
            color:#fff !important; font-weight:700 !important;
            border-color:rgba(255,255,255,0.3) !important;
        }}
        [data-testid="stSidebar"] div[data-testid="stVerticalBlock"] > div:has(button[data-testid*="nav_{key}"]) button::before {{
            background-color:#fff !important;
        }}"""

    st.markdown(f"<style>{nav_css}</style>", unsafe_allow_html=True)

    for key, label, _ in PAGES:
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state["page_active"] = key
            st.rerun()

    # Bas sidebar
    st.markdown('<div style="border-top:1px solid rgba(255,255,255,0.11);margin:8px 0;"></div>', unsafe_allow_html=True)

    groq_ok   = groq_disponible()
    dot_color = "#A7F3D0" if groq_ok else "#FCD34D"
    st.markdown(f"""
    <div style="padding:5px 12px;font-size:0.74rem;color:rgba(255,255,255,0.62);display:flex;align-items:center;gap:7px;">
        <div style="width:6px;height:6px;background:{dot_color};border-radius:50%;box-shadow:0 0 5px {dot_color};flex-shrink:0;"></div>
        {"IA active — Groq" if groq_ok else "Mode simulation"}
    </div>
    """, unsafe_allow_html=True)

    actifs_canaux = canaux_actifs()
    canaux_html = "".join(
        f'<span style="font-size:0.68rem;background:rgba(255,255,255,0.1);color:rgba(255,255,255,0.72);border-radius:5px;padding:2px 7px;margin:2px;display:inline-block;">{c}</span>'
        for c, ok in actifs_canaux.items() if ok
    )
    if canaux_html:
        st.markdown(f'<div style="padding:3px 12px 10px;line-height:1.9;">{canaux_html}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CONTENU PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
page = st.session_state.get("page_active","dashboard")

PAGE_META = {
    "dashboard": ("home",          "Dashboard",           "Vue d'ensemble de votre pipeline commercial"),
    "scoring":   ("target",        "Recherche & Scoring", "Identifiez et qualifiez vos meilleurs prospects"),
    "pipeline":  ("clipboard",     "Pipeline commercial", "Suivez chaque prospect de la decouverte a la conversion"),
    "messages":  ("message-square","Messages & Relances", "Generez et envoyez des messages personnalises"),
    "import":    ("upload",        "Import Excel",        "Importez votre liste de prospects depuis un fichier Excel"),
    "export":    ("download",      "Export Excel",        "Exportez vos prospects scores et leurs messages"),
    "scraping":  ("globe",         "Scraping Annuaires",  "Collectez des prospects depuis les annuaires togolais"),
    "linkedin":  ("linkedin",      "LinkedIn",            "Prospection LinkedIn — fonctionnalite a venir"),
}
meta = PAGE_META.get(page, PAGE_META["dashboard"])

# Hero header
st.markdown(f"""
<div class="hero-header">
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:5px;">
        <div style="background:rgba(255,255,255,0.15);border-radius:11px;padding:9px;display:inline-flex;">
            {icon(meta[0],26,"white")}
        </div>
        <div>
            <div class="hero-title">{meta[1]}</div>
            <div class="hero-subtitle">{meta[2]}</div>
        </div>
    </div>
    <div class="hero-badges">
        <span class="hero-badge">{ic("star",11,"#F9E8A0")} Opticom Business · Lome, Togo</span>
        <span class="hero-badge-alt">{ic("wifi",11,"#F9E8A0")} Fibre Pro · Flotte Mobile · API SMS</span>
        <span class="hero-badge-alt">{ic("activity",11,"rgba(255,255,255,0.75)")} Scoring ICP automatique</span>
    </div>
</div>
""", unsafe_allow_html=True)

if not groq_disponible():
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:9px;background:#FEF3C7;color:#92400E;
                border:1px solid #FCD34D;border-left:4px solid #D97706;border-radius:10px;
                padding:11px 15px;font-size:0.87rem;font-weight:500;margin-bottom:14px;">
        {icon("alert-triangle",15,"#D97706")}
        Aucune cle API Groq — les messages seront generes depuis les donnees simulees.
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE : DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
if page == "dashboard":
    m1,m2,m3,m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-icon-wrap">{ic("building",20,"#1B4332")}</div><div class="metric-value">{stats["total"]}</div><div class="metric-label">Prospects</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="metric-icon-wrap" style="background:linear-gradient(135deg,#FEF3C7,#FDE68A);">{ic("flame",20,"#065F46")}</div><div class="metric-value">{stats["haute_priorite"]}</div><div class="metric-label">Haute priorite</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><div class="metric-icon-wrap">{ic("check-circle",20,"#065F46")}</div><div class="metric-value">{stats["convertis"]}</div><div class="metric-label">Convertis</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card"><div class="metric-icon-wrap">{ic("percent",20,"#1B4332")}</div><div class="metric-value">{stats["taux_conversion"]}%</div><div class="metric-label">Taux conversion</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([3,2])

    with col_l:
        st.markdown(f'<div class="section-title">{ic("bar-chart",17,"#1B4332")} Repartition par statut</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        if stats["par_statut"]:
            df_s = pd.DataFrame([(s,n) for s,n in stats["par_statut"].items()], columns=["Statut","Nombre"]).sort_values("Nombre",ascending=False)
            st.dataframe(df_s, use_container_width=True, hide_index=True)

    with col_r:
        st.markdown(f'<div class="section-title">{ic("activity",17,"#1B4332")} Impact mesure</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="impact-card" style="background:linear-gradient(135deg,#4A5568,#718096);margin-bottom:8px;"><div class="impact-value">Plusieurs heures/jour</div><div class="impact-label">Avant CibleNet</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="impact-card" style="margin-bottom:8px;"><div class="impact-value">15 min/jour</div><div class="impact-label">Avec CibleNet</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="impact-card" style="background:linear-gradient(135deg,#92400E,#D97706);"><div class="impact-value">94 %</div><div class="impact-label">Gain productivite</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{ic("flame",17,"#1B4332")} Top 5 haute priorite</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    top5 = [e for e in get_all_entreprises() if e["score"] >= 75][:5]
    if top5:
        df_top = pd.DataFrame(top5)[["nom","secteur","localisation","effectif","score","statut"]]
        df_top.columns = ["Entreprise","Secteur","Ville","Effectif","Score ICP","Statut"]
        st.dataframe(df_top, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE : RECHERCHE & SCORING
# ─────────────────────────────────────────────────────────────────────────────
elif page == "scoring":
    SECTEURS     = ["(Tous)","Banque","Assurance","Logistique","Education","Informatique","Commerce","Industrie","Agroalimentaire","Conseil","Sante","Telecom"]
    LOCALISATIONS= ["(Toutes)","Lome","Kara","Tsevie","Kpalime","Sokode"]
    TRANCHES     = {"(Tous)":(0,9999),"TPE 1-9":(1,9),"PME 10-49":(10,49),"ETI 50-250":(50,250),"Grande 250+":(251,9999)}

    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    fc1,fc2,fc3,fc4 = st.columns([2,2,2,1])
    with fc1: sec_f = st.selectbox("Secteur", SECTEURS)
    with fc2: vil_f = st.selectbox("Ville",   LOCALISATIONS)
    with fc3: tra_f = st.selectbox("Taille",  list(TRANCHES.keys()))
    with fc4:
        st.markdown("<br>", unsafe_allow_html=True)
        rech = st.button("Rechercher", use_container_width=True, type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

    if "res_search" not in st.session_state or rech:
        emin, emax = TRANCHES[tra_f]
        st.session_state["res_search"] = search_entreprises(
            secteur      = "" if "(Tous)" in sec_f else sec_f,
            localisation = "" if "(Toutes)" in vil_f else vil_f,
            effectif_min = emin, effectif_max = emax,
        )

    resultats = st.session_state.get("res_search",[])
    if not resultats:
        st.markdown(f'<div class="empty-state"><div class="empty-state-icon">{icon("search",26,"#718096")}</div><div class="empty-state-text">Aucune entreprise trouvee</div><div class="empty-state-sub">Elargissez les criteres.</div></div>', unsafe_allow_html=True)
    else:
        haute = sum(1 for e in resultats if e["score"]>=75)
        st.markdown(f'<div style="font-size:0.81rem;color:#718096;margin-bottom:7px;">{ic("layers",12,"#718096")} <strong>{len(resultats)}</strong> entreprise(s) — <strong>{haute}</strong> haute priorite — cliquez pour le detail</div>', unsafe_allow_html=True)
        df = pd.DataFrame(resultats)[["nom","secteur","localisation","effectif","score","statut"]]
        df.columns = ["Entreprise","Secteur","Ville","Effectif","Score ICP","Statut"]
        ev = st.dataframe(df, use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")
        rows = ev.selection.get("rows",[])
        if rows:
            e = resultats[rows[0]]
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f'<div class="section-title">{ic("target",18,"#1B4332")} Fiche — {e["nom"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            d1,d2 = st.columns(2)
            with d1:
                st.markdown('<div class="detail-card">', unsafe_allow_html=True)
                afficher_detail_score(e)
                st.markdown('</div>', unsafe_allow_html=True)
            with d2:
                st.markdown('<div class="detail-card">', unsafe_allow_html=True)
                sig = e.get("signal_croissance","")
                sig_html = f'<span class="info-tag signal">{ic("trending-up",12,"#92400E")} {sig}</span>' if sig else ""
                sw = "good" if e.get("site_web") else "bad"
                pe = "good" if e.get("paiement_en_ligne") else "bad"
                st.markdown(f"""
                <span class="info-tag">{ic("factory",12)} {e["secteur"]}</span>
                <span class="info-tag">{ic("users",12)} {e["effectif"]} sal.</span>
                <span class="info-tag">{ic("map-pin",12)} {e["localisation"]}</span>
                <span class="info-tag {sw}">{ic("globe",12)} {"Site web" if e.get("site_web") else "Sans site"}</span>
                <span class="info-tag {pe}">{ic("credit-card",12)} {"Paiement en ligne" if e.get("paiement_en_ligne") else "Sans paiement"}</span>
                {sig_html}
                <br><br><div style="font-size:0.86rem;">Statut : {label_statut(e["statut"])}</div>
                """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE : PIPELINE
# ─────────────────────────────────────────────────────────────────────────────
elif page == "pipeline":
    for k,v in [("prospect_actif_id",None),("message_affiche",None),("feedback",None)]:
        if k not in st.session_state: st.session_state[k] = v

    if st.session_state["feedback"]:
        fb = st.session_state["feedback"]
        (st.success if fb["type"]=="success" else st.warning if fb["type"]=="warning" else st.error)(fb["msg"])
        st.session_state["feedback"] = None

    pipeline = get_pipeline()
    STAT_ACT  = ["Nouveau","Scor\u00e9","Contact\u00e9","Relanc\u00e9"]
    STAT_FERM = ["Converti","Non int\u00e9ress\u00e9","\u00c0 relancer plus tard"]
    COULEURS  = {"Nouveau":"#52796F","Scor\u00e9":"#D4A017","Contact\u00e9":"#2B6CB0","Relanc\u00e9":"#9C4221"}

    kcols = st.columns(len(STAT_ACT))
    for col, statut in zip(kcols, STAT_ACT):
        with col:
            pros = pipeline.get(statut,[])
            clr  = COULEURS.get(statut,"#52796F")
            cfg  = STATUT_CONFIG.get(statut,("circle",clr))
            st.markdown(f'<div class="kanban-header" style="border-left:4px solid {clr};"><h4>{ic(cfg[0],13,clr)} {statut}<span class="kanban-count" style="background:{clr}18;color:{clr};">{len(pros)}</span></h4></div>', unsafe_allow_html=True)
            for p in pros:
                with st.container(border=True):
                    st.markdown(f"**{p['nom']}**")
                    st.markdown(badge_score_compact(p["score"]), unsafe_allow_html=True)
                    st.markdown(f'<div style="font-size:0.77rem;color:#718096;margin:2px 0 5px;">{ic("map-pin",10,"#718096")} {p["secteur"]} · {p.get("localisation","")}</div>', unsafe_allow_html=True)
                    if st.button("Gerer", key=f"sel_{p['id']}", use_container_width=True):
                        st.session_state["prospect_actif_id"] = p["id"]
                        st.session_state["message_affiche"]   = None
                        st.rerun()

    with st.expander("Prospects clotures"):
        fc = st.columns(len(STAT_FERM))
        for col, statut in zip(fc, STAT_FERM):
            with col:
                pros = pipeline.get(statut,[])
                cfg  = STATUT_CONFIG.get(statut,("circle","#718096"))
                st.markdown(f'<div style="font-weight:600;font-size:0.83rem;display:flex;align-items:center;gap:5px;margin-bottom:7px;">{ic(cfg[0],12,cfg[1])} {statut} ({len(pros)})</div>', unsafe_allow_html=True)
                for p in pros:
                    st.markdown(f'<div style="font-size:0.81rem;padding:3px 0;border-bottom:1px solid rgba(82,121,111,0.1);">{ic("building",11,"#718096")} {p["nom"]} {badge_score_compact(p["score"])}</div>', unsafe_allow_html=True)

    st.divider()

    actif_id = st.session_state.get("prospect_actif_id")
    if not actif_id:
        st.markdown(f'<div class="empty-state"><div class="empty-state-icon">{icon("target",26,"#718096")}</div><div class="empty-state-text">Aucun prospect selectionne</div><div class="empty-state-sub">Cliquez sur <strong>Gerer</strong> pour acceder aux actions.</div></div>', unsafe_allow_html=True)
    else:
        entreprise = get_entreprise_by_id(actif_id)
        if not entreprise:
            st.error("Prospect introuvable.")
        else:
            st.markdown(f'<div class="section-title">{ic("briefcase",18,"#1B4332")} Actions — {entreprise["nom"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            p1,p2 = st.columns(2)
            with p1:
                st.markdown('<div class="detail-card">', unsafe_allow_html=True)
                afficher_detail_score(entreprise)
                st.markdown(f'<br><div style="font-size:0.86rem;">Statut : {label_statut(entreprise["statut"])}</div>', unsafe_allow_html=True)
                if entreprise.get("date_contact"):
                    st.markdown(f'<div style="font-size:0.8rem;color:#718096;margin-top:5px;">{ic("clock",11,"#718096")} Contact : {entreprise["date_contact"]}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with p2:
                st.markdown(f'<div class="detail-card"><div style="font-weight:700;font-size:0.88rem;color:#1B4332;margin-bottom:13px;">{ic("zap",15,"#52796F")} Actions disponibles</div>', unsafe_allow_html=True)

                if st.button("Generer un message de contact", use_container_width=True, key="btn_gen", type="primary"):
                    with st.spinner("Generation en cours..."):
                        try:
                            if groq_disponible():
                                msg, fb = generer_message_prospect(entreprise)
                                note = " (cle backup)" if fb else ""
                            else:
                                msg  = get_message_simule(entreprise,"premier_contact")
                                note = " (simule)"
                            save_message(actif_id, msg)
                            st.session_state["message_affiche"] = msg
                            st.session_state["feedback"] = {"type":"success","msg":f"Message genere{note}"}
                        except Exception as e:
                            st.session_state["feedback"] = {"type":"error","msg":str(e)}
                    st.rerun()

                if entreprise["statut"] in ["Contact\u00e9","Contacte"]:
                    if st.button("Generer la relance J+3", use_container_width=True, key="btn_rel"):
                        with st.spinner("Relance en cours..."):
                            try:
                                if groq_disponible():
                                    msg, fb = generer_relance(entreprise)
                                    note = " (cle backup)" if fb else ""
                                else:
                                    msg  = get_message_simule(entreprise,"relance")
                                    note = " (simule)"
                                save_message(actif_id, msg)
                                update_statut(actif_id,"Relanc\u00e9")
                                st.session_state["message_affiche"] = msg
                                st.session_state["feedback"] = {"type":"success","msg":f"Relance generee{note}"}
                            except Exception as e:
                                st.session_state["feedback"] = {"type":"error","msg":str(e)}
                        st.rerun()

                if entreprise["statut"] not in ["Converti","Non int\u00e9ress\u00e9"]:
                    if st.button("Marquer comme converti", use_container_width=True, key="btn_conv", type="primary"):
                        update_statut(actif_id,"Converti")
                        st.session_state["feedback"] = {"type":"success","msg":f"{entreprise['nom']} converti !"}
                        st.session_state["prospect_actif_id"] = None
                        st.rerun()
                    if st.button("Non interesse", use_container_width=True, key="btn_non"):
                        update_statut(actif_id,"Non int\u00e9ress\u00e9")
                        st.session_state["feedback"] = {"type":"warning","msg":f"{entreprise['nom']} classe non interesse."}
                        st.session_state["prospect_actif_id"] = None
                        st.rerun()
                    if entreprise["statut"] != "\u00c0 relancer plus tard":
                        if st.button("A relancer plus tard", use_container_width=True, key="btn_nurt"):
                            update_statut(actif_id,"\u00c0 relancer plus tard")
                            st.session_state["feedback"] = {"type":"warning","msg":f"{entreprise['nom']} en nurture."}
                            st.session_state["prospect_actif_id"] = None
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            msg_aff = st.session_state.get("message_affiche") or entreprise.get("message_genere")
            if msg_aff:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f'<div style="font-weight:600;font-size:0.88rem;color:#1B4332;margin-bottom:4px;">{ic("edit",14,"#52796F")} Message — modifiable avant envoi</div>', unsafe_allow_html=True)
                mk = f"msg_edit_{actif_id}"
                if mk not in st.session_state: st.session_state[mk] = msg_aff
                msg_ed = st.text_area("", value=st.session_state[mk], height=140, key=mk, label_visibility="collapsed")
                sc1,sc2 = st.columns([1,2])
                with sc1:
                    if st.button("Sauvegarder", key=f"sv_{actif_id}", use_container_width=True):
                        if msg_ed.strip():
                            save_message(actif_id, msg_ed.strip())
                            st.session_state["message_affiche"] = msg_ed.strip()
                            st.session_state["feedback"] = {"type":"success","msg":"Message sauvegarde."}
                            st.rerun()
                with sc2:
                    nb = len(msg_ed.split())
                    col = "#065F46" if nb<=100 else "#C53030"
                    st.markdown(f'<div style="font-size:0.77rem;color:{col};margin-top:7px;display:flex;align-items:center;gap:4px;">{nb} mot(s) {ic("check-circle",11,"#065F46") if nb<=100 else ic("alert-triangle",11,"#C53030")}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE : MESSAGES & RELANCES
# ─────────────────────────────────────────────────────────────────────────────
elif page == "messages":
    actifs = canaux_actifs()
    canal_labels = {
        "gmail":    ("Gmail",    "mail",          "#EA4335"),
        "whatsapp": ("WhatsApp", "message-square","#25D366"),
        "sms":      ("SMS",      "send",          "#6B46C1"),
    }
    badges = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:5px;background:{color+"18" if actifs.get(k) else "#F7FAFC"};color:{color if actifs.get(k) else "#718096"};border:1px solid {color+"55" if actifs.get(k) else "#E2E8F0"};border-radius:18px;padding:3px 11px;font-size:0.75rem;font-weight:600;margin:3px;">{ic("check-circle",11,color) if actifs.get(k) else ic("settings",11,"#718096")} {label}</span>'
        for k,(label,ico,color) in canal_labels.items()
    )
    st.markdown(f'<div style="margin-bottom:14px;">{badges}</div>', unsafe_allow_html=True)

    if "hf" not in st.session_state: st.session_state["hf"] = None
    if st.session_state["hf"]:
        fb = st.session_state["hf"]
        (st.success if fb["type"]=="success" else st.error)(fb["msg"])
        st.session_state["hf"] = None

    convertis = get_converted_entreprises()
    if not convertis:
        st.markdown(f'<div class="empty-state"><div class="empty-state-icon">{icon("handshake",26,"#718096")}</div><div class="empty-state-text">Aucun prospect converti</div><div class="empty-state-sub">Convertissez un prospect dans le Pipeline pour le transmettre ici.</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="display:inline-flex;align-items:center;gap:7px;background:linear-gradient(135deg,#D1FAE5,#A7F3D0);color:#065F46;border-radius:10px;padding:9px 14px;font-weight:700;margin-bottom:18px;border:1px solid #6EE7B7;font-size:0.88rem;">{ic("check-circle",14,"#065F46")} {len(convertis)} prospect(s) converti(s)</div>', unsafe_allow_html=True)
        for e in convertis:
            st.markdown('<div class="handoff-card">', unsafe_allow_html=True)
            h1,h2 = st.columns([3,1])
            with h1:
                st.markdown(f'<div style="font-size:1.05rem;font-weight:700;color:#1B4332;margin-bottom:7px;">{ic("building",15,"#52796F")} {e["nom"]}</div>', unsafe_allow_html=True)
                st.markdown(badge_score(e["score"]), unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                cc1,cc2,cc3 = st.columns(3)
                cc1.markdown(f'<span class="info-tag">{ic("factory",11)} {e["secteur"]}</span>', unsafe_allow_html=True)
                cc2.markdown(f'<span class="info-tag">{ic("users",11)} {e["effectif"]} sal.</span>', unsafe_allow_html=True)
                cc3.markdown(f'<span class="info-tag">{ic("map-pin",11)} {e["localisation"]}</span>', unsafe_allow_html=True)
                if e.get("message_genere"):
                    with st.expander("Message envoye"):
                        st.text(e["message_genere"])
            with h2:
                st.markdown("<br>", unsafe_allow_html=True)
                ek = f"hm_{e['id']}"
                if ek not in st.session_state: st.session_state[ek] = e.get("message_genere","")
                msg_f = st.text_area("", value=st.session_state[ek], height=110, key=ek, label_visibility="collapsed")
                if actifs.get("gmail"):
                    if st.button("Envoyer Gmail", key=f"gm_{e['id']}", use_container_width=True, type="primary"):
                        with st.spinner("Envoi..."):
                            ok, det = envoyer_gmail(e, msg_f, "handoff")
                        st.session_state["hf"] = {"type":"success" if ok else "error","msg":f"Gmail : {det}"}
                        st.rerun()
                if actifs.get("whatsapp"):
                    if st.button("Envoyer WhatsApp", key=f"wa_{e['id']}", use_container_width=True):
                        with st.spinner("Envoi..."):
                            ok, det = envoyer_whatsapp(e, msg_f, "handoff")
                        st.session_state["hf"] = {"type":"success" if ok else "error","msg":f"WhatsApp : {det}"}
                        st.rerun()
                if actifs.get("sms"):
                    if st.button("Envoyer SMS", key=f"sm_{e['id']}", use_container_width=True):
                        with st.spinner("Envoi..."):
                            ok, det = envoyer_sms(e, msg_f, "handoff")
                        st.session_state["hf"] = {"type":"success" if ok else "error","msg":f"SMS : {det}"}
                        st.rerun()
                if not any(actifs.values()):
                    st.warning("Aucun canal configure dans .env")
            st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE : IMPORT EXCEL
# ─────────────────────────────────────────────────────────────────────────────
elif page == "import":
    col_main, col_info = st.columns([3,2])
    with col_main:
        st.markdown(f'<div class="section-title">{ic("download",16,"#1B4332")} Template Excel</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.86rem;color:#718096;margin-bottom:10px;">Telechargez le template, remplissez-le et importez-le.</div>', unsafe_allow_html=True)
        st.download_button(
            "Telecharger le template Excel",
            data=generer_template_excel(),
            file_name="template_prospects_opticom.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">{ic("upload",16,"#1B4332")} Importer un fichier</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        fichier = st.file_uploader("Glissez votre fichier Excel ici (.xlsx)", type=["xlsx"])
        if fichier:
            st.markdown(f'<div style="font-size:0.84rem;color:#718096;margin-bottom:7px;">{ic("table",13,"#065F46")} Fichier detecte : <strong>{fichier.name}</strong></div>', unsafe_allow_html=True)
            try:
                dfp = pd.read_excel(fichier, engine="openpyxl", nrows=5)
                st.markdown(f'<div style="font-size:0.81rem;font-weight:600;color:#1B4332;margin-bottom:5px;">{ic("table",12,"#52796F")} Apercu (5 premieres lignes)</div>', unsafe_allow_html=True)
                st.dataframe(dfp, use_container_width=True, hide_index=True)
                fichier.seek(0)
            except Exception as e:
                st.warning(f"Impossible d'afficher l'apercu : {e}")
                fichier.seek(0)
            if st.button("Lancer l'import et scorer", type="primary", use_container_width=True):
                with st.spinner("Import, detection des colonnes et scoring..."):
                    nb_i, nb_ig, errs, raps = importer_excel(fichier)
                if nb_i > 0:
                    st.success(f"{nb_i} prospect(s) importe(s) et score(s) !")
                if nb_ig > 0:
                    st.info(f"{nb_ig} ligne(s) ignoree(s) (doublons ou vides).")
                if raps:
                    with st.expander(f"Rapport imputation — {len(raps)} colonne(s) traitee(s)"):
                        st.markdown(f'<div style="font-size:0.81rem;color:#92400E;margin-bottom:7px;">{ic("info",12,"#D97706")} Valeurs manquantes comblee automatiquement (mediane pour nombres, mode/defaut pour texte).</div>', unsafe_allow_html=True)
                        for r in raps:
                            st.markdown(f'<div style="font-size:0.81rem;color:#2D3748;padding:3px 0;border-bottom:1px solid rgba(82,121,111,0.1);">{ic("check",11,"#52796F")} {r}</div>', unsafe_allow_html=True)
                if errs:
                    st.warning("Erreurs :")
                    for err in errs: st.markdown(f"- {err}")
                if nb_i == 0 and not errs:
                    st.warning("Aucun nouveau prospect importe.")

    with col_info:
        st.markdown(f'<div class="section-title">{ic("info",16,"#1B4332")} Colonnes acceptees</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        colonnes_doc = [
            ("nom / name / entreprise / company",        "Obligatoire", "Nom de l'entreprise"),
            ("secteur / activite / industrie / domaine", "Optionnel",   "Banque, Logistique..."),
            ("localisation / ville / city",              "Optionnel",   "Lome, Kara, Tsevie..."),
            ("effectif / employees / salaries",          "Optionnel",   "Nb salaries — mediane si manquant"),
            ("signal_croissance / signal / actualite",   "Optionnel",   "Ex : Recrutement en cours"),
            ("site_web / website / url",                 "Optionnel",   "true / false"),
            ("paiement_en_ligne / paiement",             "Optionnel",   "true / false"),
        ]
        for cn, st_col, desc in colonnes_doc:
            obl = st_col == "Obligatoire"
            couleur = "#065F46" if obl else "#718096"
            ico_s = ic("check-circle",11,"#065F46") if obl else ic("circle",10,"#CBD5E0")
            st.markdown(f"""
            <div style="display:flex;align-items:flex-start;gap:7px;padding:7px 0;border-bottom:1px solid rgba(82,121,111,0.09);">
                <code style="background:#F0FFF4;color:#065F46;padding:2px 7px;border-radius:5px;font-size:0.77rem;flex-shrink:0;">{cn}</code>
                <div>
                    <div style="font-size:0.76rem;color:{couleur};font-weight:600;display:flex;align-items:center;gap:3px;">{ico_s} {st_col}</div>
                    <div style="font-size:0.78rem;color:#718096;">{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div style="background:#FEF3C7;border-radius:10px;padding:12px 14px;border:1px solid #FCD34D;"><div style="font-weight:600;color:#92400E;font-size:0.84rem;margin-bottom:5px;">{ic("zap",13,"#D97706")} Scoring automatique</div><div style="font-size:0.8rem;color:#92400E;">Chaque prospect est score selon les criteres ICP Opticom Business des l\'import.</div></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE : EXPORT EXCEL
# ─────────────────────────────────────────────────────────────────────────────
elif page == "export":
    tous = get_all_entreprises()
    if not tous:
        st.warning("Aucun prospect en base.")
    else:
        col_opt, col_prev = st.columns([2,3])
        with col_opt:
            st.markdown('<div class="filter-section">', unsafe_allow_html=True)
            st.markdown(f'<div style="font-weight:600;font-size:0.88rem;color:#1B4332;margin-bottom:11px;">{ic("settings",14,"#52796F")} Options export</div>', unsafe_allow_html=True)
            filtre_statut  = st.multiselect("Filtrer par statut", list(STATUT_CONFIG.keys()), default=[])
            filtre_score   = st.slider("Score minimum", 0, 100, 0, step=5)
            incl_msg       = st.checkbox("Inclure les messages generes", value=True)
            cols_exp = ["id","nom","secteur","localisation","effectif","signal_croissance",
                        "site_web","paiement_en_ligne","score","score_reasons","statut","date_contact"]
            if incl_msg: cols_exp.append("message_genere")
            st.markdown('</div>', unsafe_allow_html=True)

            data_exp = tous
            if filtre_statut: data_exp = [e for e in data_exp if e["statut"] in filtre_statut]
            if filtre_score>0: data_exp = [e for e in data_exp if e["score"] >= filtre_score]
            st.markdown(f'<div style="font-size:0.84rem;color:#718096;margin-bottom:10px;">{ic("database",12,"#718096")} <strong>{len(data_exp)}</strong> prospect(s)</div>', unsafe_allow_html=True)
            if data_exp:
                st.download_button(
                    f"Telecharger Excel ({len(data_exp)} lignes)",
                    data=exporter_excel(data_exp, cols_exp),
                    file_name=f"prospects_opticom_{date.today().isoformat()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True, type="primary",
                )
            else:
                st.warning("Aucun prospect avec ces filtres.")
        with col_prev:
            st.markdown(f'<div style="font-weight:600;font-size:0.88rem;color:#1B4332;margin-bottom:9px;">{ic("table",14,"#52796F")} Apercu</div>', unsafe_allow_html=True)
            if data_exp:
                dfv = pd.DataFrame(data_exp)[["nom","secteur","localisation","effectif","score","statut"]]
                dfv.columns = ["Entreprise","Secteur","Ville","Effectif","Score ICP","Statut"]
                st.dataframe(dfv, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE : SCRAPING ANNUAIRES
# ─────────────────────────────────────────────────────────────────────────────
elif page == "scraping":
    try:
        from scraper import scraper_prospects
        scraper_ok = True
    except ImportError:
        scraper_ok = False

    if not scraper_ok:
        st.error("beautifulsoup4 non installe. Lancez : pip install beautifulsoup4")
    else:
        col_f, col_r = st.columns([2,3])
        with col_f:
            st.markdown('<div class="filter-section">', unsafe_allow_html=True)
            st.markdown(f'<div style="font-weight:600;font-size:0.88rem;color:#1B4332;margin-bottom:12px;">{ic("settings",14,"#52796F")} Parametres</div>', unsafe_allow_html=True)
            sec_scrap  = st.text_input("Secteur / mot-cle", placeholder="ex: banque, logistique...")
            vil_scrap  = st.selectbox("Ville cible", ["Lome","Kara","Tsevie","Kpalime","Toutes"])
            src_scrap  = st.multiselect("Sources", ["yellotogo","togo_annuaire"], default=["yellotogo","togo_annuaire"])
            nb_pages   = st.slider("Pages par source", 1, 5, 2)
            st.markdown('</div>', unsafe_allow_html=True)
            lancer = st.button("Lancer le scraping", type="primary", use_container_width=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background:#fff;border-radius:11px;padding:14px;border:1px solid rgba(82,121,111,0.14);">
                <div style="font-weight:600;color:#1B4332;font-size:0.84rem;margin-bottom:9px;">{ic("globe",13,"#52796F")} Sources disponibles</div>
                <div style="font-size:0.8rem;color:#2D3748;margin-bottom:6px;">{ic("check-circle",11,"#065F46")} <strong>yellotogo.com</strong><br><span style="color:#718096;padding-left:18px;">Annuaire entreprises togolaises</span></div>
                <div style="font-size:0.8rem;color:#2D3748;">{ic("check-circle",11,"#065F46")} <strong>togo-annuaire.com</strong><br><span style="color:#718096;padding-left:18px;">Repertoire professionnel Togo</span></div>
            </div>
            """, unsafe_allow_html=True)

        with col_r:
            if lancer:
                if not src_scrap:
                    st.warning("Selectionnez au moins une source.")
                else:
                    logs, log_zone = [], st.empty()
                    def cb(msg):
                        logs.append(msg)
                        log_zone.markdown("".join(f'<div style="background:#fff;border-radius:9px;padding:10px 14px;border-left:4px solid #52796F;box-shadow:0 2px 10px rgba(27,67,50,0.05);margin-bottom:6px;font-size:0.85rem;">{m}</div>' for m in logs), unsafe_allow_html=True)
                    vp = "" if vil_scrap=="Toutes" else vil_scrap
                    with st.spinner("Scraping en cours..."):
                        res_sc = scraper_prospects(secteur=sec_scrap, ville=vp, sources=src_scrap, max_pages=nb_pages, callback=cb)
                    st.session_state["res_scraping"] = res_sc

            res_sc = st.session_state.get("res_scraping",[])
            if res_sc:
                h = sum(1 for r in res_sc if r["score"]>=75)
                st.markdown(f'<div style="display:flex;gap:10px;margin-bottom:14px;flex-wrap:wrap;"><div style="background:#D1FAE5;color:#065F46;border-radius:9px;padding:9px 14px;font-weight:700;font-size:0.87rem;border:1px solid #6EE7B7;">{ic("database",13,"#065F46")} {len(res_sc)} prospect(s)</div><div style="background:#FEF3C7;color:#92400E;border-radius:9px;padding:9px 14px;font-weight:700;font-size:0.87rem;border:1px solid #FCD34D;">{ic("flame",13,"#92400E")} {h} haute priorite</div></div>', unsafe_allow_html=True)
                dfs = pd.DataFrame(res_sc)[["nom","secteur","localisation","effectif","score","statut"]]
                dfs.columns = ["Entreprise","Secteur","Ville","Effectif","Score ICP","Statut"]
                st.dataframe(dfs, use_container_width=True, hide_index=True)
                ca, cb2 = st.columns(2)
                with ca:
                    if st.button("Importer dans le pipeline", type="primary", use_container_width=True):
                        conn = get_connection(); cur = conn.cursor()
                        mid = cur.execute("SELECT MAX(id) FROM entreprises").fetchone()[0] or 0
                        nb_ok = 0
                        for p in res_sc:
                            nm = p.get("nom","").strip()
                            if not nm: continue
                            if cur.execute("SELECT id FROM entreprises WHERE LOWER(nom)=LOWER(?)",(nm,)).fetchone(): continue
                            mid += 1
                            cur.execute("INSERT INTO entreprises (id,nom,secteur,localisation,effectif,signal_croissance,site_web,paiement_en_ligne,score,score_reasons,statut) VALUES (?,?,?,?,?,?,?,?,?,?,'Nouveau')",
                                (mid,nm,p.get("secteur","Autre"),p.get("localisation","Lome"),p.get("effectif",15),p.get("signal_croissance",""),p.get("site_web",False),p.get("paiement_en_ligne",False),p.get("score",0),p.get("score_reasons","")))
                            nb_ok += 1
                        conn.commit(); conn.close()
                        st.success(f"{nb_ok} prospect(s) importes !")
                        st.session_state["res_scraping"] = []
                        st.rerun()
                with cb2:
                    st.download_button("Exporter en Excel", data=exporter_excel(res_sc),
                        file_name=f"scraping_{date.today().isoformat()}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True)
            elif not lancer:
                st.markdown(f'<div class="empty-state"><div class="empty-state-icon">{icon("globe",28,"#718096")}</div><div class="empty-state-text">Aucun resultat</div><div class="empty-state-sub">Configurez les parametres et lancez.</div></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE : LINKEDIN
# ─────────────────────────────────────────────────────────────────────────────
elif page == "linkedin":
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0A66C2 0%,#0D4F96 100%);border-radius:16px;padding:38px;text-align:center;box-shadow:0 8px 30px rgba(10,102,194,0.28);">
        <div style="display:inline-flex;align-items:center;justify-content:center;background:rgba(255,255,255,0.15);border-radius:14px;padding:14px;margin-bottom:14px;">
            {icon("linkedin",44,"white")}
        </div>
        <h2 style="color:#fff;font-size:1.7rem;font-weight:700;margin:0 0 8px;">Prospection LinkedIn</h2>
        <p style="color:rgba(255,255,255,0.78);font-size:0.95rem;max-width:480px;margin:0 auto 18px;">
            Fonctionnalite en cours de developpement — scraping LinkedIn bloque par les CGU de la plateforme.
        </p>
        <div style="display:flex;gap:7px;justify-content:center;flex-wrap:wrap;">
            <span style="display:inline-flex;align-items:center;gap:5px;background:rgba(255,255,255,0.14);color:#fff;border:1px solid rgba(255,255,255,0.28);border-radius:18px;padding:5px 13px;font-size:0.78rem;font-weight:600;">{ic("lock",13,"white")} CGU LinkedIn</span>
            <span style="display:inline-flex;align-items:center;gap:5px;background:rgba(255,255,255,0.14);color:#fff;border:1px solid rgba(255,255,255,0.28);border-radius:18px;padding:5px 13px;font-size:0.78rem;font-weight:600;">{ic("alert-triangle",13,"white")} Risque ban de compte</span>
            <span style="display:inline-flex;align-items:center;gap:5px;background:rgba(255,255,255,0.14);color:#fff;border:1px solid rgba(255,255,255,0.28);border-radius:18px;padding:5px 13px;font-size:0.78rem;font-weight:600;">{ic("credit-card",13,"white")} API officielle payante</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{ic("check-circle",17,"#1B4332")} Alternatives recommandees</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    a1,a2,a3 = st.columns(3)
    with a1:
        st.markdown(f'<div class="detail-card" style="text-align:center;"><div style="margin:0 auto 10px;width:42px;height:42px;background:linear-gradient(135deg,#D1FAE5,#A7F3D0);border-radius:10px;display:flex;align-items:center;justify-content:center;">{icon("upload",20,"#065F46")}</div><div style="font-weight:700;color:#1B4332;margin-bottom:5px;">Import Excel</div><div style="font-size:0.82rem;color:#718096;">Exportez vos contacts LinkedIn manuellement et importez-les via notre outil.</div></div>', unsafe_allow_html=True)
    with a2:
        st.markdown(f'<div class="detail-card" style="text-align:center;"><div style="margin:0 auto 10px;width:42px;height:42px;background:linear-gradient(135deg,#D1FAE5,#A7F3D0);border-radius:10px;display:flex;align-items:center;justify-content:center;">{icon("globe",20,"#065F46")}</div><div style="font-weight:700;color:#1B4332;margin-bottom:5px;">Scraping Annuaires</div><div style="font-size:0.82rem;color:#718096;">Annuaires togolais legaux, rapides et adaptes au marche local.</div></div>', unsafe_allow_html=True)
    with a3:
        st.markdown(f'<div class="detail-card" style="text-align:center;"><div style="margin:0 auto 10px;width:42px;height:42px;background:linear-gradient(135deg,#DBEAFE,#BFDBFE);border-radius:10px;display:flex;align-items:center;justify-content:center;">{icon("briefcase",20,"#1D4ED8")}</div><div style="font-weight:700;color:#1B4332;margin-bottom:5px;">PhantomBuster</div><div style="font-size:0.82rem;color:#718096;">Outil SaaS (~50$/mois) automatisant LinkedIn legalement.</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Aller vers Import Excel", type="primary"):
        st.session_state["page_active"] = "import"
        st.rerun()
