# app.py — Interface Streamlit — Yas Prospect Copilot
# 3 onglets : Recherche & Scoring | Pipeline | Handoff

import streamlit as st
import pandas as pd

from database import bootstrap, search_entreprises, get_pipeline, \
                     get_converted_entreprises, update_statut, save_message, \
                     get_stats, get_entreprise_by_id
from llm      import generer_message_prospect, generer_relance, \
                     groq_disponible, get_message_simule
from webhook  import envoyer_handoff

# ── Configuration page ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Yas Prospect Copilot",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Bootstrap base de données au démarrage ────────────────────────────────────
bootstrap()

# ══════════════════════════════════════════════════════════════════════════════
# BIBLIOTHÈQUE D'ICÔNES SVG (Lucide Icons — MIT License)
# Chaque fonction retourne un <svg> inline prêt à coller dans du HTML.
# ══════════════════════════════════════════════════════════════════════════════

def icon(name: str, size: int = 16, color: str = "currentColor", extra: str = "") -> str:
    """Retourne un SVG Lucide inline selon le nom d'icône."""
    base = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round" '
        f'style="vertical-align:middle;{extra}">'
    )
    paths = {
        # Navigation & UI
        "search":        '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
        "filter":        '<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>',
        "chevron-right": '<polyline points="9 18 15 12 9 6"/>',
        "arrow-right":   '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>',
        "settings":      '<circle cx="12" cy="12" r="3"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M4.93 4.93a10 10 0 0 0 0 14.14"/>',
        "x":             '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
        "check":         '<polyline points="20 6 9 20 4 14"/>',
        "clock":         '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
        "refresh-cw":    '<polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>',
        "lock":          '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
        "external-link": '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>',
        # Prospects & Business
        "building":      '<rect x="4" y="2" width="16" height="20" rx="2" ry="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01M16 6h.01M8 10h.01M16 10h.01M8 14h.01M16 14h.01"/>',
        "users":         '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
        "user":          '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
        "briefcase":     '<rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
        "trending-up":   '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
        "bar-chart":     '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',
        "target":        '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
        "star":          '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
        "award":         '<circle cx="12" cy="8" r="6"/><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"/>',
        # Communication
        "mail":          '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>',
        "send":          '<line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>',
        "message-square":'<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
        "upload":        '<polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/>',
        "bell":          '<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>',
        # Données & score
        "cpu":           '<rect x="9" y="9" width="6" height="6"/><path d="M20 14h1M20 10h1M4 14H3M4 10H3M14 4V3M10 4V3M14 20v1M10 20v1M20 4v16H4V4z"/>',
        "zap":           '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
        "activity":      '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
        "percent":       '<line x1="19" y1="5" x2="5" y2="19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>',
        # Localisation & industrie
        "map-pin":       '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
        "factory":       '<path d="M2 20a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8l-7 5V8l-7 5V4a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"/><path d="M17 18h1"/><path d="M12 18h1"/><path d="M7 18h1"/>',
        "globe":         '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
        "credit-card":   '<rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/>',
        "wifi":          '<path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><line x1="12" y1="20" x2="12.01" y2="20"/>',
        # Actions
        "plus-circle":   '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/>',
        "trash-2":       '<polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>',
        "edit":          '<path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>',
        # Status
        "circle":        '<circle cx="12" cy="12" r="10"/>',
        "check-circle":  '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
        "x-circle":      '<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>',
        "alert-triangle": '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/> <line x1="12" y1="9" x2="12" y2="13"/> <line x1="12" y1="17" x2="12.01" y2="17"/>',
        "info":          '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>',
        # Divers
        "radio":         '<circle cx="12" cy="12" r="2"/><path d="M16.24 7.76a6 6 0 0 1 0 8.49m-8.48-.01a6 6 0 0 1 0-8.49m11.31-2.82a10 10 0 0 1 0 14.14m-14.14 0a10 10 0 0 1 0-14.14"/>',
        "layers":        '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
        "handshake":     '<path d="M20.42 4.58a5.4 5.4 0 0 0-7.65 0l-.77.78-.77-.78a5.4 5.4 0 0 0-7.65 0C1.46 6.7 1.33 10.28 4 13l8 8 8-8c2.67-2.72 2.54-6.3.42-8.42z"/>',
        "clipboard":     '<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>',
        "flame":         '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>',
        "snowflake":     '<line x1="2" y1="12" x2="22" y2="12"/><line x1="12" y1="2" x2="12" y2="22"/><path d="m20 16-4-4 4-4"/><path d="m4 8 4 4-4 4"/><path d="m16 4-4 4-4-4"/><path d="m8 20 4-4 4 4"/>',
        "timer":         '<line x1="10" y1="2" x2="14" y2="2"/><circle cx="12" cy="14" r="8"/><polyline points="12 6 12 14 16 16"/>',
    }
    body = paths.get(name, '<circle cx="12" cy="12" r="4"/>')
    return f"{base}{body}</svg>"


def ic(name: str, size: int = 15, color: str = "currentColor") -> str:
    """Shorthand pour icon() utilisé dans les f-strings HTML."""
    return icon(name, size, color)


# ── CSS personnalisé — Design Naturel & Moderne ───────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Variables couleurs ── */
:root {
    --vert-foret:   #1B4332;
    --vert-sauge:   #52796F;
    --vert-clair:   #84A98C;
    --vert-pale:    #CAD2C5;
    --beige-chaud:  #F8F5F0;
    --beige-sombre: #EDE8E1;
    --or-doux:      #D4A017;
    --or-pale:      #F9E8A0;
    --ardoise:      #2D3748;
    --gris-doux:    #718096;
    --blanc:        #FEFEFE;
    --rouge-doux:   #C53030;
    --rouge-pale:   #FED7D7;
}

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── Fond principal ── */
.stApp {
    background: linear-gradient(135deg, #F8F5F0 0%, #EDE8E1 100%) !important;
}

/* ── En-tête héro ── */
.hero-header {
    background: linear-gradient(135deg, #1B4332 0%, #52796F 60%, #84A98C 100%);
    border-radius: 20px;
    padding: 40px 48px;
    margin-bottom: 28px;
    box-shadow: 0 8px 32px rgba(27,67,50,0.25);
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    background: rgba(255,255,255,0.06);
    border-radius: 50%;
}
.hero-header::after {
    content: '';
    position: absolute;
    bottom: -60px; left: 10%;
    width: 300px; height: 300px;
    background: rgba(255,255,255,0.04);
    border-radius: 50%;
}
.hero-top {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 10px;
}
.hero-icon-wrap {
    background: rgba(255,255,255,0.15);
    border-radius: 14px;
    padding: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 700;
    color: #FEFEFE;
    margin: 0;
    letter-spacing: -0.5px;
}
.hero-subtitle {
    font-size: 1rem;
    color: rgba(255,255,255,0.72);
    margin: 0 0 12px 0;
    font-weight: 400;
    letter-spacing: 0.3px;
}
.hero-badges {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(212,160,23,0.22);
    color: #F9E8A0;
    border: 1px solid rgba(212,160,23,0.4);
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.76rem;
    font-weight: 600;
    letter-spacing: 0.6px;
    text-transform: uppercase;
}
.hero-badge-alt {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255,255,255,0.12);
    color: rgba(255,255,255,0.85);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.76rem;
    font-weight: 500;
    letter-spacing: 0.3px;
}

/* ── Cartes métriques ── */
.metric-card {
    background: var(--blanc);
    border-radius: 16px;
    padding: 22px 24px;
    text-align: center;
    box-shadow: 0 2px 16px rgba(27,67,50,0.08);
    border: 1px solid rgba(82,121,111,0.12);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: linear-gradient(90deg, #1B4332, #52796F);
    border-radius: 16px 16px 0 0;
}
.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 24px rgba(27,67,50,0.15);
}
.metric-icon-wrap {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #D1FAE5, #A7F3D0);
    border-radius: 12px;
    width: 44px; height: 44px;
    margin: 0 auto 10px auto;
}
.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--vert-foret);
    line-height: 1.1;
}
.metric-label {
    font-size: 0.8rem;
    color: var(--gris-doux);
    font-weight: 500;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}

/* ── Badges score ── */
.score-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 14px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.84rem;
    letter-spacing: 0.3px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.score-high {
    background: linear-gradient(135deg, #D1FAE5, #A7F3D0);
    color: #065F46;
    border: 1px solid #6EE7B7;
}
.score-medium {
    background: linear-gradient(135deg, #FEF3C7, #FDE68A);
    color: #92400E;
    border: 1px solid #FCD34D;
}
.score-low {
    background: linear-gradient(135deg, #FEE2E2, #FECACA);
    color: #991B1B;
    border: 1px solid #FCA5A5;
}

/* ── Onglets (tabs) ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: transparent;
    border-bottom: 2px solid rgba(82,121,111,0.2);
    padding-bottom: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 10px 10px 0 0;
    padding: 10px 24px;
    font-weight: 500;
    font-size: 0.9rem;
    color: var(--gris-doux) !important;
    border: none;
    transition: all 0.2s ease;
}
.stTabs [data-baseweb="tab"]:hover {
    background: rgba(82,121,111,0.08);
    color: var(--vert-sauge) !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(180deg, rgba(82,121,111,0.12) 0%, transparent 100%) !important;
    color: var(--vert-foret) !important;
    font-weight: 700 !important;
    border-bottom: 3px solid var(--vert-foret) !important;
}
.tab-label {
    display: inline-flex;
    align-items: center;
    gap: 7px;
}

/* ── Boutons ── */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 8px 18px !important;
    transition: all 0.2s ease !important;
    border: 1.5px solid transparent !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 6px !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1B4332, #52796F) !important;
    color: white !important;
    box-shadow: 0 4px 14px rgba(27,67,50,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(27,67,50,0.4) !important;
}
.stButton > button[kind="secondary"] {
    background: white !important;
    color: var(--vert-foret) !important;
    border-color: rgba(82,121,111,0.4) !important;
}
.stButton > button[kind="secondary"]:hover {
    background: var(--beige-sombre) !important;
    border-color: var(--vert-sauge) !important;
}

/* ── Cartes Kanban ── */
.kanban-header {
    background: linear-gradient(135deg, var(--beige-sombre), var(--beige-chaud));
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 12px;
    border: 1px solid rgba(82,121,111,0.15);
}
.kanban-header h4 {
    margin: 0;
    color: var(--vert-foret);
    font-size: 0.88rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 8px;
}
.kanban-count {
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 0.78rem;
    font-weight: 700;
    margin-left: auto;
}

/* ── Section titre ── */
.section-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--vert-foret);
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-divider {
    height: 2px;
    background: linear-gradient(90deg, var(--vert-sauge), transparent);
    border-radius: 2px;
    margin: 8px 0 20px 0;
}

/* ── Filtre section ── */
.filter-section {
    background: white;
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px rgba(27,67,50,0.06);
    border: 1px solid rgba(82,121,111,0.1);
}

/* ── Dataframe ── */
.stDataFrame {
    border-radius: 12px !important;
    overflow: hidden;
    box-shadow: 0 2px 16px rgba(27,67,50,0.08) !important;
}

/* ── Carte détail prospect ── */
.detail-card {
    background: white;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 20px rgba(27,67,50,0.1);
    border: 1px solid rgba(82,121,111,0.12);
    height: 100%;
}

/* ── Info tags ── */
.info-tag {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: var(--beige-sombre);
    color: var(--ardoise);
    border-radius: 8px;
    padding: 4px 11px;
    font-size: 0.82rem;
    font-weight: 500;
    margin: 3px 3px 3px 0;
    border: 1px solid rgba(82,121,111,0.15);
}
.info-tag.good {
    background: #D1FAE5;
    color: #065F46;
    border-color: #6EE7B7;
}
.info-tag.bad {
    background: #FEE2E2;
    color: #991B1B;
    border-color: #FCA5A5;
}
.info-tag.signal {
    background: linear-gradient(135deg,#FEF3C7,#FDE68A);
    color: #92400E;
    border-color: #FCD34D;
}

/* ── Vide state ── */
.empty-state {
    text-align: center;
    padding: 40px 24px;
    background: white;
    border-radius: 16px;
    border: 2px dashed rgba(82,121,111,0.3);
}
.empty-state-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: var(--beige-sombre);
    border-radius: 50%;
    width: 64px; height: 64px;
    margin: 0 auto 16px auto;
}
.empty-state-text {
    color: var(--gris-doux);
    font-weight: 500;
    font-size: 0.95rem;
}
.empty-state-sub {
    color: var(--gris-doux);
    font-size: 0.84rem;
    opacity: 0.7;
    margin-top: 6px;
}

/* ── Handoff card ── */
.handoff-card {
    background: white;
    border-radius: 18px;
    padding: 28px;
    margin-bottom: 18px;
    box-shadow: 0 4px 24px rgba(27,67,50,0.1);
    border: 1px solid rgba(82,121,111,0.15);
    border-top: 4px solid #52796F;
}

/* ── Impact metrics ── */
.impact-card {
    background: linear-gradient(135deg, #1B4332 0%, #52796F 100%);
    border-radius: 16px;
    padding: 24px 20px;
    text-align: center;
    color: white;
    box-shadow: 0 4px 20px rgba(27,67,50,0.25);
}
.impact-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: rgba(255,255,255,0.15);
    border-radius: 12px;
    width: 48px; height: 48px;
    margin: 0 auto 12px auto;
}
.impact-value {
    font-size: 1.9rem;
    font-weight: 700;
    color: #F9E8A0;
    line-height: 1;
}
.impact-label {
    font-size: 0.8rem;
    opacity: 0.82;
    margin-top: 6px;
    text-transform: uppercase;
    letter-spacing: 0.7px;
}

/* ── Alerte ── */
.stAlert { border-radius: 12px !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--beige-sombre); }
::-webkit-scrollbar-thumb { background: var(--vert-clair); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--vert-sauge); }

/* ── Text area ── */
.stTextArea textarea {
    border-radius: 10px !important;
    border-color: rgba(82,121,111,0.3) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    border-radius: 10px !important;
    border-color: rgba(82,121,111,0.3) !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    border-radius: 10px !important;
    background: var(--beige-sombre) !important;
    font-weight: 600 !important;
    color: var(--vert-foret) !important;
}

/* ── Caption ── */
.stCaption { color: var(--gris-doux) !important; font-size: 0.82rem !important; }

/* ── Divider ── */
hr { border-color: rgba(82,121,111,0.2) !important; margin: 20px 0 !important; }

/* ── Progress bar ── */
.stProgress > div > div {
    background: linear-gradient(90deg, #1B4332, #52796F) !important;
    border-radius: 4px !important;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS VISUELS
# ══════════════════════════════════════════════════════════════════════════════

def badge_score(score: int) -> str:
    if score >= 75:
        cls = "score-high"
        svg = ic("flame", 14, "#065F46")
        label = "Haute priorité"
    elif score >= 50:
        cls = "score-medium"
        svg = ic("zap", 14, "#92400E")
        label = "Priorité moyenne"
    else:
        cls = "score-low"
        svg = ic("snowflake", 14, "#991B1B")
        label = "Faible priorité"
    return f'<span class="score-badge {cls}">{svg} {score}/100 — {label}</span>'


def badge_score_compact(score: int) -> str:
    """Version courte sans label textuel pour les tableaux."""
    if score >= 75:
        cls, svg = "score-high", ic("flame", 13, "#065F46")
    elif score >= 50:
        cls, svg = "score-medium", ic("zap", 13, "#92400E")
    else:
        cls, svg = "score-low", ic("snowflake", 13, "#991B1B")
    return f'<span class="score-badge {cls}">{svg} {score}/100</span>'


STATUT_CONFIG = {
    "Nouveau":              ("circle",        "#52796F"),
    "Scoré":                ("bar-chart",     "#D4A017"),
    "Contacté":             ("mail",          "#2B6CB0"),
    "Relancé":              ("refresh-cw",    "#9C4221"),
    "Converti":             ("check-circle",  "#065F46"),
    "Non intéressé":        ("x-circle",      "#991B1B"),
    "À relancer plus tard": ("timer",         "#6B46C1"),
}

def label_statut(statut: str) -> str:
    cfg = STATUT_CONFIG.get(statut, ("circle", "#718096"))
    svg = ic(cfg[0], 14, cfg[1])
    return f'<span style="display:inline-flex;align-items:center;gap:5px;">{svg} {statut}</span>'


def afficher_detail_score(entreprise: dict):
    """Détail du score ICP avec barre de progression."""
    score   = entreprise["score"]
    reasons = entreprise.get("score_reasons", "")

    st.markdown(badge_score(score), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<span style="font-weight:600;color:#1B4332;display:flex;align-items:center;gap:6px;">'
        f'{ic("layers", 15, "#52796F")} Détail du score ICP</span>',
        unsafe_allow_html=True
    )

    if reasons:
        for r in reasons.split(" | "):
            st.markdown(
                f'<div style="display:flex;align-items:flex-start;gap:6px;'
                f'margin:4px 0;font-size:0.86rem;color:#2D3748;">'
                f'{ic("check", 13, "#52796F")} {r}</div>',
                unsafe_allow_html=True
            )
    else:
        st.info("Aucun détail disponible.")

    st.progress(score / 100)


# ══════════════════════════════════════════════════════════════════════════════
# EN-TÊTE PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
radio_svg = icon("radio", 36, "white")
wifi_svg  = icon("wifi",  18, "#F9E8A0")
star_svg  = icon("star",  14, "#F9E8A0")
act_svg   = icon("activity", 14, "rgba(255,255,255,0.75)")
users_svg = icon("users",    14, "rgba(255,255,255,0.75)")

st.markdown(f"""
<div class="hero-header">
    <div class="hero-top">
        <div class="hero-icon-wrap">{radio_svg}</div>
        <div>
            <div class="hero-title">Yas Prospect Copilot</div>
        </div>
    </div>
    <div class="hero-subtitle">
        Identifiez · Qualifiez · Contactez · Convertissez vos prospects B2B au Togo
    </div>
    <div class="hero-badges">
        <span class="hero-badge">{star_svg} Yas Business · Lomé, Togo</span>
        <span class="hero-badge-alt">{wifi_svg} Fibre Pro · Flotte Mobile · API SMS</span>
        <span class="hero-badge-alt">{act_svg} Scoring ICP automatique</span>
        <span class="hero-badge-alt">{users_svg} Pipeline commercial intégré</span>
    </div>
</div>
""", unsafe_allow_html=True)

if not groq_disponible():
    st.markdown(f"""
    <div style="
        display:flex; align-items:center; gap:10px;
        background:#FEF3C7; color:#92400E;
        border:1px solid #FCD34D; border-left:4px solid #D97706;
        border-radius:12px; padding:14px 18px;
        font-size:0.9rem; font-weight:500;
        margin-bottom:8px;
    ">
        {icon('alert-triangle', 18, '#D97706')}
        <span>
            Aucune clé API Groq configurée —
            les messages seront générés depuis les <strong>données simulées</strong>.
        </span>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MÉTRIQUES GLOBALES
# ══════════════════════════════════════════════════════════════════════════════
stats = get_stats()
m1, m2, m3, m4 = st.columns(4)

with m1:
    svg_b = icon("building", 22, "#1B4332")
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon-wrap">{svg_b}</div>
        <div class="metric-value">{stats["total"]}</div>
        <div class="metric-label">Prospects identifiés</div>
    </div>""", unsafe_allow_html=True)

with m2:
    svg_f = icon("flame", 22, "#065F46")
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon-wrap" style="background:linear-gradient(135deg,#FEF3C7,#FDE68A);">{svg_f}</div>
        <div class="metric-value">{stats["haute_priorite"]}</div>
        <div class="metric-label">Haute priorité (≥ 75)</div>
    </div>""", unsafe_allow_html=True)

with m3:
    svg_c = icon("check-circle", 22, "#065F46")
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon-wrap">{svg_c}</div>
        <div class="metric-value">{stats["convertis"]}</div>
        <div class="metric-label">Convertis</div>
    </div>""", unsafe_allow_html=True)

with m4:
    svg_p = icon("percent", 22, "#1B4332")
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon-wrap">{svg_p}</div>
        <div class="metric-value">{stats["taux_conversion"]}%</div>
        <div class="metric-label">Taux de conversion</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ONGLETS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs([
    "  Recherche & Scoring  ",
    "  Pipeline commercial  ",
    "  Handoff Discord  ",
])

# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 1 — RECHERCHE & SCORING
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown(
        f'<div class="section-title">{ic("search", 20, "#1B4332")} Rechercher & scorer des prospects</div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── Filtres ───────────────────────────────────────────────────────────────
    SECTEURS = [
        "(Tous les secteurs)",
        "Banque", "Assurance", "Logistique", "Éducation",
        "Informatique", "Commerce", "Industrie", "Agroalimentaire", "Conseil",
    ]
    LOCALISATIONS = ["(Toutes les villes)", "Lomé", "Kara", "Tsevié", "Kpalimé", "Autres"]
    TRANCHES = {
        "(Tous les effectifs)": (0, 9999),
        "TPE — 1 à 9 sal.":     (1, 9),
        "PME — 10 à 49 sal.":   (10, 49),
        "ETI — 50 à 250 sal.":  (50, 250),
        "Grande — 250+ sal.":   (251, 9999),
    }

    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    f_col1, f_col2, f_col3, f_col4 = st.columns([2, 2, 2, 1])
    with f_col1:
        secteur_filtre = st.selectbox("Secteur d'activité", SECTEURS)
    with f_col2:
        ville_filtre   = st.selectbox("Ville / Zone", LOCALISATIONS)
    with f_col3:
        tranche_filtre = st.selectbox("Taille d'entreprise", list(TRANCHES.keys()))
    with f_col4:
        st.markdown("<br>", unsafe_allow_html=True)
        rechercher = st.button("Rechercher", use_container_width=True, type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Logique de recherche ──────────────────────────────────────────────────
    if "resultats_recherche" not in st.session_state or rechercher:
        eff_min, eff_max = TRANCHES[tranche_filtre]
        resultats = search_entreprises(
            secteur      = "" if "(Tous"   in secteur_filtre else secteur_filtre,
            localisation = "" if "(Toutes" in ville_filtre   else ville_filtre,
            effectif_min = eff_min,
            effectif_max = eff_max,
        )
        st.session_state["resultats_recherche"] = resultats

    resultats = st.session_state.get("resultats_recherche", [])

    # ── Résultats ─────────────────────────────────────────────────────────────
    if not resultats:
        st.markdown(f"""
        <div class="empty-state">
            <div class="empty-state-icon">{icon("search", 28, "#718096")}</div>
            <div class="empty-state-text">Aucune entreprise trouvée</div>
            <div class="empty-state-sub">Élargissez les critères de recherche pour obtenir des résultats.</div>
        </div>""", unsafe_allow_html=True)
    else:
        total_haute = sum(1 for e in resultats if e["score"] >= 75)
        st.markdown(
            f'<div style="font-size:0.82rem;color:#718096;display:flex;align-items:center;'
            f'gap:6px;margin-bottom:8px;">'
            f'{ic("layers",13,"#718096")} '
            f'<span><strong>{len(resultats)}</strong> entreprise(s) trouvée(s) — '
            f'<strong>{total_haute}</strong> haute(s) priorité — '
            f'Cliquez sur une ligne pour afficher le détail du score ICP</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        df = pd.DataFrame(resultats)[
            ["nom", "secteur", "localisation", "effectif", "score", "statut"]
        ]
        df.columns = ["Entreprise", "Secteur", "Ville", "Effectif (sal.)", "Score ICP", "Statut"]

        event = st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
        )

        # ── Détail score au clic ──────────────────────────────────────────────
        selected_rows = event.selection.get("rows", [])
        if selected_rows:
            idx        = selected_rows[0]
            entreprise = resultats[idx]

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                f'<div class="section-title">'
                f'{ic("target", 20, "#1B4332")} Fiche prospect — {entreprise["nom"]}'
                f'</div>',
                unsafe_allow_html=True
            )
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

            d_col1, d_col2 = st.columns([1, 1])

            with d_col1:
                st.markdown('<div class="detail-card">', unsafe_allow_html=True)
                st.markdown(
                    f'<div style="font-weight:700;font-size:0.9rem;color:#1B4332;'
                    f'margin-bottom:14px;display:flex;align-items:center;gap:6px;">'
                    f'{ic("bar-chart",16,"#52796F")} Score de qualification ICP</div>',
                    unsafe_allow_html=True
                )
                afficher_detail_score(entreprise)
                st.markdown('</div>', unsafe_allow_html=True)

            with d_col2:
                st.markdown('<div class="detail-card">', unsafe_allow_html=True)
                st.markdown(
                    f'<div style="font-weight:700;font-size:0.9rem;color:#1B4332;'
                    f'margin-bottom:14px;display:flex;align-items:center;gap:6px;">'
                    f'{ic("briefcase",16,"#52796F")} Informations entreprise</div>',
                    unsafe_allow_html=True
                )

                sw_cls  = "good" if entreprise.get("site_web")          else "bad"
                pe_cls  = "good" if entreprise.get("paiement_en_ligne") else "bad"
                sw_lbl  = "Site web actif"    if entreprise.get("site_web")          else "Sans site web"
                pe_lbl  = "Paiement en ligne" if entreprise.get("paiement_en_ligne") else "Pas de paiement en ligne"
                sw_ico  = ic("globe",      13, "#065F46" if entreprise.get("site_web")          else "#991B1B")
                pe_ico  = ic("credit-card",13, "#065F46" if entreprise.get("paiement_en_ligne") else "#991B1B")

                signal     = entreprise.get("signal_croissance", "")
                signal_html = (
                    f'<span class="info-tag signal">'
                    f'{ic("trending-up",13,"#92400E")} {signal}</span>'
                ) if signal else ""

                st.markdown(f"""
                <span class="info-tag">{ic("factory",   13)} {entreprise['secteur']}</span>
                <span class="info-tag">{ic("users",     13)} {entreprise['effectif']} salariés</span>
                <span class="info-tag">{ic("map-pin",   13)} {entreprise['localisation']}</span>
                <span class="info-tag {sw_cls}">{sw_ico} {sw_lbl}</span>
                <span class="info-tag {pe_cls}">{pe_ico} {pe_lbl}</span>
                {signal_html}
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(
                    f'<div style="font-size:0.88rem;">Statut : {label_statut(entreprise["statut"])}</div>',
                    unsafe_allow_html=True
                )
                st.markdown('</div>', unsafe_allow_html=True)

            # ── Comparaison rapide ────────────────────────────────────────────
            bas = next((e for e in resultats if e["score"] <= 20), None)
            if bas:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(
                    f'<div style="font-weight:600;font-size:0.9rem;color:#1B4332;'
                    f'display:flex;align-items:center;gap:6px;">'
                    f'{ic("layers",15,"#52796F")} Comparaison — Haute priorité vs Hors cible</div>',
                    unsafe_allow_html=True
                )
                cmp_col1, cmp_col2 = st.columns(2)
                with cmp_col1:
                    st.markdown(f"**{entreprise['nom']}**")
                    st.markdown(badge_score_compact(entreprise["score"]), unsafe_allow_html=True)
                with cmp_col2:
                    st.markdown(f"**{bas['nom']}**")
                    st.markdown(badge_score_compact(bas["score"]), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 2 — PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown(
        f'<div class="section-title">{ic("clipboard", 20, "#1B4332")} Pipeline commercial</div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── Session state ─────────────────────────────────────────────────────────
    for key, val in [
        ("prospect_actif_id", None),
        ("message_affiche",   None),
        ("feedback",          None),
    ]:
        if key not in st.session_state:
            st.session_state[key] = val

    # ── Feedback ─────────────────────────────────────────────────────────────
    if st.session_state["feedback"]:
        fb = st.session_state["feedback"]
        if fb["type"] == "success":
            st.success(fb["msg"])
        elif fb["type"] == "warning":
            st.warning(fb["msg"])
        else:
            st.error(fb["msg"])
        st.session_state["feedback"] = None

    pipeline = get_pipeline()

    STATUTS_ACTIFS = ["Nouveau", "Scoré", "Contacté", "Relancé"]
    STATUTS_FERMES = ["Converti", "Non intéressé", "À relancer plus tard"]

    COULEURS_KANBAN = {
        "Nouveau":  "#52796F",
        "Scoré":    "#D4A017",
        "Contacté": "#2B6CB0",
        "Relancé":  "#9C4221",
    }

    st.markdown(
        f'<div style="font-weight:700;font-size:0.95rem;color:#1B4332;'
        f'display:flex;align-items:center;gap:6px;margin-bottom:14px;">'
        f'{ic("layers",17,"#52796F")} Prospects en cours de traitement</div>',
        unsafe_allow_html=True
    )
    k_cols = st.columns(len(STATUTS_ACTIFS))

    for col, statut in zip(k_cols, STATUTS_ACTIFS):
        with col:
            prospects_statut = pipeline.get(statut, [])
            couleur = COULEURS_KANBAN.get(statut, "#52796F")
            cfg = STATUT_CONFIG.get(statut, ("circle", couleur))
            svg = ic(cfg[0], 14, couleur)
            st.markdown(f"""
            <div class="kanban-header" style="border-left: 4px solid {couleur};">
                <h4>{svg} {statut}
                    <span class="kanban-count"
                          style="background:{couleur}18;color:{couleur};">
                        {len(prospects_statut)}
                    </span>
                </h4>
            </div>""", unsafe_allow_html=True)

            for p in prospects_statut:
                with st.container(border=True):
                    st.markdown(f"**{p['nom']}**")
                    st.markdown(badge_score_compact(p["score"]), unsafe_allow_html=True)
                    st.markdown(
                        f'<div style="font-size:0.8rem;color:#718096;margin:2px 0 6px 0;">'
                        f'{ic("map-pin",11,"#718096")} {p["secteur"]} · {p.get("localisation","")}'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    if st.button("Gérer", key=f"select_{p['id']}", use_container_width=True):
                        st.session_state["prospect_actif_id"] = p["id"]
                        st.session_state["message_affiche"]   = None
                        st.rerun()

    # ── Prospects clôturés ────────────────────────────────────────────────────
    with st.expander("▸  Prospects clôturés — Converti / Non intéressé / À relancer"):
        f_cols = st.columns(len(STATUTS_FERMES))
        for col, statut in zip(f_cols, STATUTS_FERMES):
            with col:
                prospects_statut = pipeline.get(statut, [])
                cfg = STATUT_CONFIG.get(statut, ("circle", "#718096"))
                svg = ic(cfg[0], 13, cfg[1])
                st.markdown(
                    f'<div style="font-weight:600;font-size:0.86rem;'
                    f'display:flex;align-items:center;gap:5px;margin-bottom:8px;">'
                    f'{svg} {statut} ({len(prospects_statut)})</div>',
                    unsafe_allow_html=True
                )
                for p in prospects_statut:
                    st.markdown(
                        f'<div style="font-size:0.84rem;padding:4px 0;'
                        f'border-bottom:1px solid rgba(82,121,111,0.1);">'
                        f'{ic("building",12,"#718096")} {p["nom"]} '
                        f'&nbsp;{badge_score_compact(p["score"])}</div>',
                        unsafe_allow_html=True
                    )

    st.divider()

    # ── Panneau de gestion du prospect actif ──────────────────────────────────
    actif_id = st.session_state.get("prospect_actif_id")

    if not actif_id:
        st.markdown(f"""
        <div class="empty-state">
            <div class="empty-state-icon">{icon("target", 28, "#718096")}</div>
            <div class="empty-state-text">Aucun prospect sélectionné</div>
            <div class="empty-state-sub">
                Cliquez sur <strong>Gérer</strong> sur une carte prospect pour accéder aux actions disponibles.
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        entreprise = get_entreprise_by_id(actif_id)
        if not entreprise:
            st.error("Prospect introuvable en base de données.")
        else:
            st.markdown(
                f'<div class="section-title">'
                f'{ic("briefcase", 20, "#1B4332")} Actions — {entreprise["nom"]}'
                f'</div>',
                unsafe_allow_html=True
            )
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

            p_col1, p_col2 = st.columns([1, 1])

            with p_col1:
                st.markdown('<div class="detail-card">', unsafe_allow_html=True)
                afficher_detail_score(entreprise)
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(
                    f'<div style="font-size:0.88rem;">Statut : {label_statut(entreprise["statut"])}</div>',
                    unsafe_allow_html=True
                )
                if entreprise.get("date_contact"):
                    st.markdown(
                        f'<div style="font-size:0.82rem;color:#718096;margin-top:6px;'
                        f'display:flex;align-items:center;gap:5px;">'
                        f'{ic("clock",12,"#718096")} Dernier contact : {entreprise["date_contact"]}</div>',
                        unsafe_allow_html=True
                    )
                st.markdown('</div>', unsafe_allow_html=True)

            with p_col2:
                st.markdown('<div class="detail-card">', unsafe_allow_html=True)
                st.markdown(
                    f'<div style="font-weight:700;font-size:0.9rem;color:#1B4332;'
                    f'margin-bottom:16px;display:flex;align-items:center;gap:6px;">'
                    f'{ic("zap",16,"#52796F")} Actions disponibles</div>',
                    unsafe_allow_html=True
                )

                # Générer message de contact
                if st.button(
                    "Générer un message de contact",
                    use_container_width=True,
                    key="btn_generer",
                    type="primary",
                ):
                    with st.spinner("Rédaction du message personnalisé en cours…"):
                        try:
                            if groq_disponible():
                                msg, fallback = generer_message_prospect(entreprise)
                                note = " *(via clé backup)*" if fallback else ""
                            else:
                                msg  = get_message_simule(entreprise, "premier_contact")
                                note = " *(données simulées)*"
                            save_message(actif_id, msg)
                            st.session_state["message_affiche"] = msg
                            st.session_state["feedback"] = {
                                "type": "success",
                                "msg": f"Message généré — statut passé à 'Contacté'{note}"
                            }
                        except Exception as e:
                            st.session_state["feedback"] = {
                                "type": "error",
                                "msg": f"Erreur de génération : {e}"
                            }
                    st.rerun()

                # Relance J+3
                if entreprise["statut"] == "Contacté":
                    if st.button(
                        "Générer la relance J+3",
                        use_container_width=True,
                        key="btn_relancer",
                    ):
                        with st.spinner("Rédaction de la relance J+3…"):
                            try:
                                if groq_disponible():
                                    msg, fallback = generer_relance(entreprise)
                                    note = " *(via clé backup)*" if fallback else ""
                                else:
                                    msg  = get_message_simule(entreprise, "relance")
                                    note = " *(données simulées)*"
                                save_message(actif_id, msg)
                                update_statut(actif_id, "Relancé")
                                st.session_state["message_affiche"] = msg
                                st.session_state["feedback"] = {
                                    "type": "success",
                                    "msg": f"Relance J+3 générée — statut passé à 'Relancé'{note}"
                                }
                            except Exception as e:
                                st.session_state["feedback"] = {
                                    "type": "error",
                                    "msg": f"Erreur de relance : {e}"
                                }
                        st.rerun()

                # Marquer comme converti
                if entreprise["statut"] not in ["Converti", "Non intéressé"]:
                    if st.button(
                        "Marquer comme converti",
                        use_container_width=True,
                        key="btn_convertir",
                        type="primary",
                    ):
                        update_statut(actif_id, "Converti")
                        st.session_state["feedback"] = {
                            "type": "success",
                            "msg": f"{entreprise['nom']} converti avec succès — transmettez-le via l'onglet Handoff."
                        }
                        st.session_state["prospect_actif_id"] = None
                        st.rerun()

                # Non intéressé
                if entreprise["statut"] not in ["Converti", "Non intéressé"]:
                    if st.button(
                        "Non intéressé",
                        use_container_width=True,
                        key="btn_noninteresse",
                    ):
                        update_statut(actif_id, "Non intéressé")
                        st.session_state["feedback"] = {
                            "type": "warning",
                            "msg": f"{entreprise['nom']} classé comme non intéressé."
                        }
                        st.session_state["prospect_actif_id"] = None
                        st.rerun()

                # À relancer plus tard
                if entreprise["statut"] not in ["Converti", "Non intéressé", "À relancer plus tard"]:
                    if st.button(
                        "À relancer plus tard",
                        use_container_width=True,
                        key="btn_nurture",
                    ):
                        update_statut(actif_id, "À relancer plus tard")
                        st.session_state["feedback"] = {
                            "type": "warning",
                            "msg": f"{entreprise['nom']} mis en nurture — relance programmée."
                        }
                        st.session_state["prospect_actif_id"] = None
                        st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

            # ── Message généré ────────────────────────────────────────────────
            msg_affiche = (
                st.session_state.get("message_affiche")
                or entreprise.get("message_genere")
            )
            if msg_affiche:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(
                    f'<div style="font-weight:600;font-size:0.9rem;color:#1B4332;'
                    f'margin-bottom:8px;display:flex;align-items:center;gap:6px;">'
                    f'{ic("mail",15,"#52796F")} Message généré par Yas Copilot</div>',
                    unsafe_allow_html=True
                )
                st.text_area(
                    "",
                    value=msg_affiche,
                    height=150,
                    disabled=True,
                    key="msg_display",
                    label_visibility="collapsed",
                )


# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 3 — HANDOFF
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown(
        f'<div class="section-title">'
        f'{ic("send", 20, "#1B4332")} Handoff — Transmission au responsable commercial'
        f'</div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-size:0.82rem;color:#718096;display:flex;align-items:center;'
        f'gap:6px;margin-bottom:12px;">'
        f'{ic("bell",13,"#718096")} '
        f'Les prospects convertis sont transmis automatiquement au responsable commercial '
        f'via le webhook Discord de Yas Business.'
        f'</div>',
        unsafe_allow_html=True
    )

    if "handoff_feedback" not in st.session_state:
        st.session_state["handoff_feedback"] = None

    if st.session_state["handoff_feedback"]:
        fb = st.session_state["handoff_feedback"]
        if fb["type"] == "success":
            st.success(fb["msg"])
        else:
            st.error(fb["msg"])
        st.session_state["handoff_feedback"] = None

    convertis = get_converted_entreprises()

    if not convertis:
        st.markdown(f"""
        <div class="empty-state">
            <div class="empty-state-icon">{icon("handshake", 28, "#718096")}</div>
            <div class="empty-state-text">Aucun prospect converti pour le moment</div>
            <div class="empty-state-sub">
                Retournez dans l'onglet <strong>Pipeline commercial</strong> et marquez
                un prospect comme converti pour pouvoir le transmettre ici.
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        nb = len(convertis)
        st.markdown(f"""
        <div style="display:inline-flex;align-items:center;gap:8px;
                    background:linear-gradient(135deg,#D1FAE5,#A7F3D0);
                    color:#065F46;border-radius:12px;padding:10px 18px;
                    font-weight:700;margin-bottom:20px;
                    border:1px solid #6EE7B7;font-size:0.92rem;">
            {ic("check-circle", 16, "#065F46")}
            {nb} prospect(s) converti(s) — prêt(s) pour transmission à l'équipe commerciale
        </div>""", unsafe_allow_html=True)

        for entreprise in convertis:
            st.markdown('<div class="handoff-card">', unsafe_allow_html=True)
            h_col1, h_col2 = st.columns([3, 1])

            with h_col1:
                st.markdown(
                    f'<div style="font-size:1.2rem;font-weight:700;color:#1B4332;'
                    f'margin-bottom:8px;display:flex;align-items:center;gap:8px;">'
                    f'{ic("building",18,"#52796F")} {entreprise["nom"]}</div>',
                    unsafe_allow_html=True
                )
                st.markdown(badge_score(entreprise["score"]), unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

                c1, c2, c3 = st.columns(3)
                c1.markdown(
                    f'<span class="info-tag">{ic("factory",13)} {entreprise["secteur"]}</span>',
                    unsafe_allow_html=True
                )
                c2.markdown(
                    f'<span class="info-tag">{ic("users",13)} {entreprise["effectif"]} sal.</span>',
                    unsafe_allow_html=True
                )
                c3.markdown(
                    f'<span class="info-tag">{ic("map-pin",13)} {entreprise["localisation"]}</span>',
                    unsafe_allow_html=True
                )

                if entreprise.get("score_reasons"):
                    with st.expander("▸  Raisons du score ICP"):
                        for r in entreprise["score_reasons"].split(" | "):
                            st.markdown(
                                f'<div style="display:flex;align-items:flex-start;'
                                f'gap:6px;font-size:0.86rem;margin:3px 0;">'
                                f'{ic("check",12,"#52796F")} {r}</div>',
                                unsafe_allow_html=True
                            )

                if entreprise.get("message_genere"):
                    with st.expander("▸  Message de contact envoyé"):
                        st.text(entreprise["message_genere"])

            with h_col2:
                st.markdown("<br><br>", unsafe_allow_html=True)
                if st.button(
                    "Transmettre à Discord",
                    key=f"handoff_{entreprise['id']}",
                    use_container_width=True,
                    type="primary",
                ):
                    with st.spinner("Transmission en cours via webhook Discord…"):
                        ok, detail = envoyer_handoff(entreprise)
                    if ok:
                        st.session_state["handoff_feedback"] = {
                            "type": "success",
                            "msg": f"{entreprise['nom']} transmis avec succès au responsable commercial via Discord !"
                        }
                    else:
                        st.session_state["handoff_feedback"] = {
                            "type": "error",
                            "msg": f"Échec de transmission Discord : {detail}"
                        }
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    # ── Impact mesuré ─────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="section-title">'
        f'{ic("activity", 20, "#1B4332")} Impact mesuré — Yas Prospect Copilot'
        f'</div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    g_col1, g_col2, g_col3 = st.columns(3)

    with g_col1:
        svg_t = icon("clock", 26, "white")
        st.markdown(f"""
        <div class="impact-card" style="background:linear-gradient(135deg,#4A5568,#718096);">
            <div class="impact-icon">{svg_t}</div>
            <div class="impact-value">4 h / jour</div>
            <div class="impact-label">Avant Yas Copilot — Travail manuel</div>
        </div>""", unsafe_allow_html=True)

    with g_col2:
        svg_z = icon("zap", 26, "white")
        st.markdown(f"""
        <div class="impact-card">
            <div class="impact-icon">{svg_z}</div>
            <div class="impact-value">15 min / jour</div>
            <div class="impact-label">Avec Yas Copilot — Processus automatisé</div>
        </div>""", unsafe_allow_html=True)

    with g_col3:
        svg_a = icon("trending-up", 26, "white")
        st.markdown(f"""
        <div class="impact-card" style="background:linear-gradient(135deg,#92400E,#D97706);">
            <div class="impact-icon">{svg_a}</div>
            <div class="impact-value">94 %</div>
            <div class="impact-label">Gain de productivité commerciale</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-size:0.82rem;color:#718096;display:flex;align-items:center;'
        f'gap:6px;margin-top:8px;">'
        f'{ic("info",12,"#718096")} '
        f'Mesure réalisée sur 12 prospects traités à Lomé : '
        f'recherche ICP + qualification + message personnalisé + handoff Discord en 15 minutes.'
        f'</div>',
        unsafe_allow_html=True
    )
