import streamlit as st
import httpx
from datetime import datetime, timedelta
import random

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="FLU DİJİTAL | Workspace", 
    page_icon="✉️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- TEMA YÖNETİMİ ---
if "theme" not in st.session_state:
    st.session_state.theme = "Day"  # Gmail sadeliği için varsayılan Gündüz Modu

# --- VERİTABANI AYARLARI ---
SUPABASE_URL = "https://fxohhhqrhybbqqwqxejc.supabase.co/rest/v1/gorevler"
ANON_KEY = "sb_publishable_Gr83hViFqzpLLHW3Ib-iaQ_cIuQ3fe8"
HEADERS = {
    "apikey": ANON_KEY, 
    "Authorization": f"Bearer {ANON_KEY}", 
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- GMAIL / MATERIAL DESIGN RENK PALETİ (OKUNABİLİRLİK FİX) ---
if st.session_state.theme == "Night":
    T_BG = "#202124"          # Google Koyu Gri Arka Plan
    T_SIDEBAR = "#28292c"     # Sidebar için bir tık açık koyu gri
    T_CARD = "#2d2e30"        # Koyu Kart Rengi
    T_TEXT = "#ffffff"        # TAM BEYAZ (Okunabilirlik için)
    T_MUTED = "#9aa0a6"       # Soluk Gri Metin
    T_BORDER = "#5f6368"      # Koyu Çizgi
    T_PRIMARY = "#8ab4f8"     # Google Açık Mavi (Dark mode uyumlu)
    T_BTN_TEXT = "#202124"    # Buton içi koyu metin
    T_DONE_BG = "rgba(138, 180, 248, 0.08)"
else:
    T_BG = "#ffffff"          # Saf Beyaz
    T_SIDEBAR = "#f6f8fc"     # Gmail Sidebar Grisi
    T_CARD = "#ffffff"        
    T_TEXT = "#202124"        # Koyu Metin
    T_MUTED = "#5f6368"       # Soluk Metin
    T_BORDER = "#dadce0"      # İnce Gri Çizgi
    T_PRIMARY = "#1a73e8"     # Orijinal Google Mavisi
    T_BTN_TEXT = "#ffffff"
    T_DONE_BG = "#f8f9fa"

# --- MATERIAL DESIGN CSS (GÜÇLENDİRİLMİŞ METİN RENKLERİ) ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
    
    .stApp {{ background-color: {T_BG}; font-family: 'Roboto', sans-serif; transition: all 0.2s ease; }}
    
    /* STREAMLIT VARSAYILAN METİNLERİNİ EZME (Gece modu okunabilirliği için hayati önem taşır) */
    .stApp p, .stApp span, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp label {{
        color: {T_TEXT} !important;
    }}
    
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} .stDeployButton {{display:none;}}

    /* Mobil Menü Butonu */
    button[data-testid="stSidebarCollapseButton"] {{
        background-color: transparent !important; color: {T_MUTED} !important;
        border-radius: 50% !important; top: 10px !important;
    }}
    button[data-testid="stSidebarCollapseButton"] svg {{ fill: {T_TEXT} !important; color: {T_TEXT} !important; }}
    button[data-testid="stSidebarCollapseButton"]:hover {{ background-color: rgba(138, 180, 248, 0.1) !important; }}

    /* Sidebar (Gmail Sol Menü Mantığı) */
    section[data-testid="stSidebar"] {{ background-color: {T_SIDEBAR} !important; border-right: none !important; }}
    div[data-testid="stSidebar"] div[role="radiogroup"] label p {{ font-weight: 500; font-size: 14px; }}
    div[data-testid="stSidebar"] div[data-testid="stCaptionContainer"] p {{ color: {T_MUTED} !important; }}

    /* Başlık Alanı (Hero) */
    .material-header {{
        border-bottom: 1px solid {T_BORDER}; padding-bottom: 16px; margin-bottom: 24px; margin-top: 10px;
    }}
    .material-header h1 {{ font-size: 26px !important; font-weight: 400; margin: 0; }}
    .material-header p {{ color: {T_MUTED} !important; font-size: 13px; font-weight: 500; margin-top: 4px; }}

    /* İstatistik Kartları */
    .stat-card {{
        background: {T_CARD}; border: 1px solid {T_BORDER}; border-radius: 8px; 
        padding: 16px; text-align: left;
    }}
    .stat-val {{ font-size: 28px; font-weight: 400; color: {T_PRIMARY} !important; line-height: 1.2; }}
    .stat-label {{ font-size: 12px; color: {T_MUT
