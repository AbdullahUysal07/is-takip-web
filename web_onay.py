import streamlit as st
import httpx
from datetime import datetime, timedelta
import random

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="FlowDesk Ultra | Portal", 
    page_icon="💎", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- TEMA YÖNETİMİ ---
if "theme" not in st.session_state:
    st.session_state.theme = "Night"  # Ana olarak gece modu aktif

# --- VERİTABANI AYARLARI ---
SUPABASE_URL = "https://fxohhhqrhybbqqwqxejc.supabase.co/rest/v1/gorevler"
ANON_KEY = "sb_publishable_Gr83hViFqzpLLHW3Ib-iaQ_cIuQ3fe8"
HEADERS = {
    "apikey": ANON_KEY, 
    "Authorization": f"Bearer {ANON_KEY}", 
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- DİNAMİK RENK PALETİ ---
if st.session_state.theme == "Night":
    T_BG = "#0b0f19"
    T_CARD = "#161b26"
    T_TEXT = "#f8fafc"
    T_TEXT_MUTED = "#94a3b8"
    T_BORDER = "rgba(255,255,255,0.05)"
    T_SIDEBAR = "#0b0f19"
    T_STAT_BG = "#1e293b"
else:
    T_BG = "#f8fafc"
    T_CARD = "#ffffff"
    T_TEXT = "#1e293b"
    T_TEXT_MUTED = "#64748b"
    T_BORDER = "#e2e8f0"
    T_SIDEBAR = "#ffffff"
    T_STAT_BG = "#ffffff"

# --- ULTRA PREMIUM CSS ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    .stApp {{ background-color: {T_BG}; font-family: 'Inter', sans-serif; transition: all 0.3s ease; }}
    
    /* Mobil Menü Butonu */
    button[data-testid="stSidebarCollapseButton"] {{
        background-color: #2a62ff !important;
        color: white !important;
        border-radius: 50% !important;
        top: 15px !important;
    }}

    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} .stDeployButton {{display:none;}}

    /* Hero Card */
    .hero-card {{
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 40px; border-radius: 24px; color: white; text-align: center;
        box-shadow: 0 15px 35px rgba(0,0,0,0.3); margin-bottom: 30px;
        border: 1px solid rgba(255,255,255,0.1);
    }}
    .hero-card h1 {{ color: #ffffff !important; font-size: 28px !important; font-weight: 800; margin: 0; }}

    /* Stat Grid */
    .stat-box {{
        background: {T_STAT_BG}; padding: 25px; border-radius: 20px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid {T_BORDER};
        text-align: center; color: {T_TEXT};
    }}
    .stat-value {{ font-size: 28px; font-weight: 800; color: #2a62ff; }}
    .stat-desc {{ font-size: 11px; color: {T_TEXT_MUTED}; font-weight: 700; text-transform: uppercase; }}

    /* Flow Kartlar */
    .flow-card {{
        background: {T_CARD}; border-radius: 16px; padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); border: 1px solid {T_BORDER};
        margin-bottom: 15px; border-left: 6px solid #2a62ff; color: {T_TEXT};
    }}
    .card-title {{ font-size: 16px; font-weight: 700; color: {T_TEXT}; margin-bottom: 8px; }}
    .card-meta {{ font-size: 11px; color: {T_TEXT_MUTED}; font-weight: 700; }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{ background-color: {T_SIDEBAR} !important; border-right: 1px solid {T_BORDER}; }}
    [data-testid="stSidebarNav"] span {{ color: {T_TEXT} !important; font-weight: 700; }}

    /* Kaydet Butonu */
    div.stButton > button:first-child {{
        background: linear-gradient(to right, #11998e, #38ef7d) !important;
        color: white !important; font-weight: bold !important; border-radius: 12px !important;
        width: 100% !important; border: none !important; height: 48px;
    }}
    
    /* Tema Seçici */
    .theme-toggle {{
        padding: 10px; border-radius: 10px; background: {T_CARD};
        border: 1px solid {T_BORDER}; text-align: center; margin-bottom: 20px;
    }}
</style>
""", unsafe_allow_html=True)

MOTTOLAR = ["Odaklan, Başar, Kutla! 🚀", "Göz alıcı bir çalışma günü dileriz.", "Bugünün yıldızı sensin! ✨"]

def main():
    token = st.query_params.get("id")
    if not token:
        st.markdown('<div class="hero-card"><h1>FLU DİJİTAL</h1><p>Giriş bekleniyor...</p></div>', unsafe_allow_html=True)
        st.stop()

    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(SUPABASE_URL, headers=HEADERS)
            data = r.json()
        
        user_row = [t for t in data if t.get("magic_token") == token]
        if not user_row: st.stop()
        
        user_name = user_row[0]["personel_ad"]
        today_str = datetime.now().strftime("%Y-%m-%d")

        my_tasks = [t for t in data if t.get("personel_ad") == user_name and t.get("deadline", "").startswith(today_str)]
        my_done = sum(1 for t in my_tasks if t.get("durum") == "tamamlandi")
        my_total = len(my_tasks)
        
        team_today = [t for t in data if t.get("deadline", "").startswith(today_str)]
        team_done = sum(1 for t in team_today if t.get("durum") == "tamamlandi")
    except:
        st.error("Bağlantı hatası.")
        st.stop()

    # --- SIDEBAR (Tema ve Menü) ---
    with st.sidebar:
        st.markdown(f"## 💎 FlowDesk v3.5")
        
        # Tema Değiştirici
        theme_icon = "🌙" if st.session_state.theme == "Night" else "☀️"
        if st.button(f"{theme_icon} Temayı Değiştir"):
            st.session_state.theme = "Day" if st.session_state.theme == "Night" else "Night"
            st.rerun()
            
        st.write("---")
        menu = st.radio("ANA MENÜ", ["🚀 Dashboard", "📋 Görevlerim", "🌐 Şirket Radarı", "📅 Gelecek İşler"])
        st.write("---")
        st.caption(f"Kullanıcı: {user_name}")

    # --- 1. DASHBOARD ---
    if menu == "🚀 Dashboard":
        st.markdown(f"""
            <div class="hero-card">
                <h1>Merhaba, {user_name}! 👋</h1>
                <div style="color: #38ef7d; font-weight:700; margin-top:10px;">{random.choice(MOTTOLAR)}</div>
            </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="stat-box"><div class="stat-value">{my_total}</div><div class="stat-desc">Toplam İş</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="stat-box"><div class="stat-value">{my_done}</div><div class="stat-desc">Biten İş</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="stat-box"><div class="stat-value">{team_done}</div><div class="stat-desc">Ekip Başarısı</div></div>', unsafe_allow_html=True)
        with c4:
            perf = int((my_done/my_total)*100) if my_total > 0 else 100
            st.markdown(f'<div class="stat-box"><div class="stat-value">%{perf}</div><div class="stat-desc">Verimlilik</div></div>', unsafe_allow_html=True)

        st.write("---")
        
        st.markdown(f"### 🔍 Günlük Analiz")
        team_total = len(team_today)
        team_perc = (team_done / team_total) if team_total > 0 else 0
        st.write(f"Şirket İlerleme Oranı: %{int(team_perc*100)}")
        st.progress(team_perc)

    # --- 2. GÖREVLERİM ---
    elif menu == "📋 Görevlerim":
        st.subheader("📋 Görev Panosu")
        col1, col2 = st.columns(2)
        todo = [t for t in my_tasks if t.get("durum") != "tamamlandi"]
        done = [t for t in my_tasks if t.get("durum") == "tamamlandi"]
        
        with col1:
            st.markdown("##### ⏳ Bekleyenler")
            for t in todo:
                saat = t.get("deadline","").split("T")[1][:5]
                st.markdown(f'<div class="flow-card"><span class="card-meta">⏰ Hedef: {saat}</span><div class="card-title">{t["is_tanimi"]}</div></div>', unsafe_allow_html=True)
                st.checkbox("Tamamlandı", key=t['id'])
        with col2:
            st.markdown("##### ✅ Bitenler")
            for t in done:
                st.markdown(f'<div class="flow-card" style="border-left-color:#10b981; opacity:0.6;"><div class="card-title"><s>{t["is_tanimi"]}</s></div><div class="card-meta">✨ Tamamlandı</div></div>', unsafe_allow_html=True)
        
        if st.button("🚀 Değişiklikleri Kaydet"):
            for t in my_tasks:
                ns = "tamamlandi" if st.session_state.get(t['id']) else "bekliyor"
                if t['durum'] != ns: httpx.patch(f"{SUPABASE_URL}?id=eq.{t['id']}", headers=HEADERS, json={"durum": ns})
            st.rerun()

    # --- 3. RADAR & GELECEK ---
    elif menu == "🌐 Şirket Radarı":
        st.subheader("🌐 Şirket Akışı")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### 🏆 Bitenler")
            for b in [t for t in team_today if t.get("durum") == "tamamlandi"]:
                saat = b.get("deadline","").split("T")[1][:5]
                st.markdown(f'<div class="flow-card" style="border-left-color:#f59e0b;"><span class="card-meta">⏰ {saat}</span><br><b>{b["personel_ad"]}</b><br><small>{b["is_tanimi"]}</small></div>', unsafe_allow_html=True)
        with c2:
            st.markdown("##### ⏳ Devam Edenler")
            for d in [t for t in team_today if t.get("durum") != "tamamlandi"]:
                saat = d.get("deadline","").split("T")[1][:5]
                st.markdown(f'<div class="flow-card"><span class="card-meta">⏰ {saat}</span><br><b>{d["personel_ad"]}</b><br><small>{d["is_tanimi"]}</small></div>', unsafe_allow_html=True)

    elif menu == "📅 Gelecek İşler":
        for ft in [t for t in data if t.get("deadline", "").split("T")[0] > today_str]:
            dv = datetime.strptime(ft['deadline'].split('T')[0], '%Y-%m-%d').strftime('%d.%m.%Y')
            st.markdown(f'<div class="flow-card"><span class="card-meta">📅 {dv} | 👤 {ft["personel_ad"]}</span><br>{ft["is_tanimi"]}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
