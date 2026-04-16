import streamlit as st
import httpx
from datetime import datetime
import random

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="FLU DİJİTAL | Çalışan Portalı", 
    page_icon="💎", 
    layout="centered",
    initial_sidebar_state="expanded" 
)

# --- VERİTABANI AYARLARI ---
SUPABASE_URL = "https://fxohhhqrhybbqqwqxejc.supabase.co/rest/v1/gorevler"
ANON_KEY = "sb_publishable_Gr83hViFqzpLLHW3Ib-iaQ_cIuQ3fe8"
HEADERS = {
    "apikey": ANON_KEY, 
    "Authorization": f"Bearer {ANON_KEY}", 
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- ÖZEL TASARIM (GÖRÜNÜRLÜK GARANTİLİ CSS) ---
st.markdown("""
<style>
    /* Genel Arka Plan */
    .stApp { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}

    /* Hoşgeldin Kartı */
    .welcome-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 30px; border-radius: 16px; color: white; text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin-bottom: 20px;
    }
    .welcome-card h1 { color: #ffffff !important; font-weight: 800; font-size: 28px; margin-bottom: 5px;}
    .welcome-card p { font-size: 16px; color: #94a3b8; }

    /* Görev Kartları */
    .task-card {
        background: #ffffff; border-radius: 12px; padding: 16px 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-left: 6px solid #3b82f6;
        margin-bottom: 12px;
    }
    .task-completed { border-left-color: #10b981; background: #f0fdf4; }
    .task-title { font-size: 17px; font-weight: 700; color: #1e293b; margin-bottom: 4px; }
    .task-meta { font-size: 13px; color: #64748b; font-weight: 600; }
    
    /* Radar Kartları */
    .feed-card {
        background: #ffffff; padding: 12px; border-radius: 10px; margin-bottom: 8px;
        border-left: 4px solid #f59e0b; box-shadow: 0 1px 5px rgba(0,0,0,0.05);
    }
    .feed-ongoing { border-left-color: #3b82f6; }
    
    /* Not Alanı */
    .task-note { background: #fffbeb; padding: 10px; border-radius: 8px; font-size: 12.5px; color: #92400e; border: 1px solid #fde68a; margin-top: 10px; }
    
    /* MENÜ YAZILARINI DÜZELTEN KRİTİK CSS */
    section[data-testid="stSidebar"] .st-emotion-cache-16idsys p { color: #1e293b !important; font-weight: 600 !important; }
    section[data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e2e8f0; }

    /* Progress Bar Etiketi */
    .progress-label { font-size: 14px; font-weight: 700; color: #475569; margin-bottom: 5px; display: block; }
</style>
""", unsafe_allow_html=True)

# Motivasyon Havuzu
MOTIVASYON_BITEN = ["Müthişsin {isim}!", "Eline sağlık {isim}!", "Gurur duyuyoruz {isim}!"]
MOTIVASYON_DEVAM = ["Kolay gelsin {isim}!", "Başarılar {isim}!", "İyi çalışmalar {isim}!"]

def main():
    # 1. Giriş Kontrolü
    query_params = st.query_params
    token = query_params.get("id")

    if not token:
        st.markdown('<div class="welcome-card"><h1>Bağlantı Hatası</h1><p>Lütfen yöneticinizin size ilettiği özel linki kullanın.</p></div>', unsafe_allow_html=True)
        st.stop()

    # 2. Veri Senkronizasyonu
    try:
        resp = httpx.get(SUPABASE_URL, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        all_tasks = resp.json()
        
        user_entry = [t for t in all_tasks if t.get("magic_token") == token]
        if not user_entry:
            st.error("Giriş anahtarı sistemde bulunamadı.")
            st.stop()
        
        current_user = user_entry[0]["personel_ad"]
        today_str = datetime.now().strftime("%Y-%m-%d")

        # Filtreleme Mantığı (İstediğin Kurallar)
        my_tasks_today = [t for t in all_tasks if t.get("personel_ad") == current_user and t.get("deadline", "").startswith(today_str)]
        radar_tasks_today = [t for t in all_tasks if t.get("deadline", "").startswith(today_str)]
        future_tasks = [t for t in all_tasks if t.get("deadline", "").split("T")[0] > today_str]
        future_tasks.sort(key=lambda x: x.get("deadline", ""))

    except Exception as e:
        st.error("Veri bağlantısı kurulamadı. Lütfen internetinizi kontrol edin.")
        st.stop()

    # 3. ÜST SABİT PANEL (Hoşgeldin ve İlerleme)
    st.markdown(f"""
        <div class="welcome-card">
            <h1>Hoş Geldin, {current_user}! 👋</h1>
            <p>FLU D
