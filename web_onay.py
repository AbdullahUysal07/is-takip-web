import streamlit as st
import httpx
from datetime import datetime
import random

# --- SAYFA AYARLARI (Mobil için 'auto' yapıldı, beyaz ekran sorunu çözüldü) ---
st.set_page_config(
    page_title="FLU DİJİTAL | Workspace", 
    page_icon="✉️", 
    layout="wide",
    initial_sidebar_state="auto" 
)

# --- TEMA YÖNETİMİ ---
if "theme" not in st.session_state:
    st.session_state.theme = "Day"

# --- VERİTABANI AYARLARI ---
SUPABASE_URL = "https://fxohhhqrhybbqqwqxejc.supabase.co/rest/v1/gorevler"
ANON_KEY = "sb_publishable_Gr83hViFqzpLLHW3Ib-iaQ_cIuQ3fe8"
HEADERS = {
    "apikey": ANON_KEY, 
    "Authorization": f"Bearer {ANON_KEY}", 
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- GMAIL / MATERIAL DESIGN RENK PALETİ ---
if st.session_state.theme == "Night":
    T_BG = "#202124"          # Google Koyu Gri Arka Plan
    T_SIDEBAR = "#28292c"     
    T_CARD = "#303134"        
    T_TEXT = "#ffffff"        # TAM BEYAZ (Gece modu okunabilirliği)
    T_MUTED = "#9aa0a6"       
    T_BORDER = "#5f6368"      
    T_PRIMARY = "#8ab4f8"     
    T_BTN_TEXT = "#202124"    
    T_DONE_BG = "rgba(138, 180, 248, 0.08)"
else:
    T_BG = "#ffffff"          
    T_SIDEBAR = "#f6f8fc"     
    T_CARD = "#ffffff"        
    T_TEXT = "#202124"        
    T_MUTED = "#5f6368"       
    T_BORDER = "#dadce0"      
    T_PRIMARY = "#1a73e8"     
    T_BTN_TEXT = "#ffffff"
    T_DONE_BG = "#f8f9fa"

# --- MATERIAL DESIGN CSS (MOBİL UYUMLU & TEMA FİXLİ) ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
    
    /* Genel Uygulama Ayarları */
    .stApp {{ background-color: {T_BG}; font-family: 'Roboto', sans-serif; transition: all 0.2s ease; }}
    
    /* Metin Renklerini Zorla (Gece modunda siyah kalmaması için) */
    .stApp p, .stApp span, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp label {{
        color: {T_TEXT} !important;
    }}
    
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} .stDeployButton {{display:none;}}

    /* MOBİL MENÜ BUTONU (Sol üstteki 3 çizgi / ok işareti) */
    [data-testid="collapsedControl"] {{
        background-color: transparent !important;
        z-index: 999999 !important;
    }}
    [data-testid="collapsedControl"] button, button[data-testid="stSidebarCollapseButton"] {{
        background-color: {T_CARD} !important; 
        border: 1px solid {T_BORDER} !important;
        border-radius: 50% !important; 
        box-shadow: 0 2px 6px rgba(0,0,0,0.1) !important;
        color: {T_TEXT} !important;
    }}
    [data-testid="collapsedControl"] svg, button[data-testid="stSidebarCollapseButton"] svg {{
        fill: {T_TEXT} !important; 
        color: {T_TEXT} !important;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{ background-color: {T_SIDEBAR} !important; border-right: none !important; }}
    div[data-testid="stSidebar"] div[role="radiogroup"] label p {{ font-weight: 500; font-size: 14px; }}
    div[data-testid="stSidebar"] div[data-testid="stCaptionContainer"] p {{ color: {T_MUTED} !important; }}

    /* Başlık Alanı */
    .material-header {{
        border-bottom: 1px solid {T_BORDER}; padding-bottom: 16px; margin-bottom: 24px; margin-top: 10px;
    }}
    .material-header h1 {{ font-size: 26px !important; font-weight: 400; margin: 0; }}
    .material-header p {{ color: {T_MUTED} !important; font-size: 13px; font-weight: 500; margin-top: 4px; }}

    /* İstatistik Kartları */
    .stat-card {{
        background: {T_CARD}; border: 1px solid {T_BORDER}; border-radius: 8px; 
        padding: 16px; text-align: left; margin-bottom: 10px;
    }}
    .stat-val {{ font-size: 28px; font-weight: 400; color: {T_PRIMARY} !important; line-height: 1.2; }}
    .stat-label {{ font-size: 12px; color: {T_MUTED} !important; font-weight: 500; letter-spacing: 0.5px; }}

    /* Görev Kartları */
    .material-card {{
        background: {T_CARD}; border: 1px solid {T_BORDER}; border-radius: 8px; 
        padding: 14px 16px; margin-bottom: 8px;
        display: flex; flex-direction: column; justify-content: center;
    }}
    .material-card-done {{ background: {T_DONE_BG}; border-color: {T_BORDER}; opacity: 0.8; }}
    
    .card-top {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }}
    .card-title {{ font-size: 14px; font-weight: 500; color: {T_TEXT} !important; }}
    .card-time {{ font-size: 12px; font-weight: 500; color: {T_PRIMARY} !important; }}
    .card-desc {{ font-size: 13px; color: {T_MUTED} !important; margin-top: 4px; }}
    
    .card-label {{ 
        font-size: 11px; background: {T_SIDEBAR}; color: {T_MUTED} !important; 
        padding: 2px 6px; border-radius: 4px; border: 1px solid {T_BORDER}; display: inline-block; margin-top: 8px;
    }}

    /* Alt Başlıklar */
    h3 {{ font-size: 16px !important; font-weight: 500 !important; color: {T_MUTED} !important; border-bottom: 1px solid {T_BORDER}; padding-bottom: 8px; margin-bottom: 16px; }}
    h5 {{ font-size: 14px !important; font-weight: 500 !important; margin-bottom: 12px; }}

    /* Aksiyon Butonu */
    div.stButton > button:first-child {{
        background-color: {T_PRIMARY} !important; color: {T_BTN_TEXT} !important;
        font-weight: 500 !important; border-radius: 24px !important; 
        border: none !important; padding: 10px 24px !important; font-size: 14px !important;
        width: 100%;
    }}
    div.stButton > button:first-child p {{ color: {T_BTN_TEXT} !important; }}
</style>
""", unsafe_allow_html=True)

def main():
    token = st.query_params.get("id")
    if not token:
        st.markdown(f'<div class="material-header"><h1>FLU DİJİTAL</h1><p>Geçerli bir oturum bulunamadı. Lütfen size iletilen linke tıklayın.</p></div>', unsafe_allow_html=True)
        st.stop()

    # --- VERİ ÇEKME ---
    try:
        with httpx.Client(timeout=15.0) as client:
            r = client.get(SUPABASE_URL, headers=HEADERS)
            data = r.json()
        
        user_row = [t for t in data if t.get("magic_token") == token]
        if not user_row: 
            st.error("Link geçersiz veya süresi dolmuş.")
            st.stop()
        
        user_name = user_row[0]["personel_ad"]
        today_str = datetime.now().strftime("%Y-%m-%d")

        my_tasks = [t for t in data if t.get("personel_ad") == user_name and t.get("deadline", "").startswith(today_str)]
        my_done = sum(1 for t in my_tasks if t.get("durum") == "tamamlandi")
        my_total = len(my_tasks)
        
        team_today = [t for t in data if t.get("deadline", "").startswith(today_str)]
        team_done = sum(1 for t in team_today if t.get("durum") == "tamamlandi")
    except:
        st.error("Sunucuya bağlanılamadı. Lütfen internetinizi kontrol edip sayfayı yenileyin.")
        st.stop()

    # --- YAN MENÜ (SIDEBAR) ---
    with st.sidebar:
        theme_icon = "🌙 Gece Modu" if st.session_state.theme == "Day" else "☀️ Gündüz Modu"
        if st.button(theme_icon):
            st.session_state.theme = "Night" if st.session_state.theme == "Day" else "Day"
            st.rerun()
            
        st.write("")
        menu = st.radio("MENÜ", ["📥 Ana Sayfa", "📝 Görevlerim", "🌐 Şirket Radarı", "🗓️ Gelecek İşler"])
        st.write("---")
        st.caption(f"👤 {user_name}")

    # --- DASHBOARD ---
    if menu == "📥 Ana Sayfa":
        st.markdown(f"""
            <div class="material-header">
                <h1>Hoş Geldin, {user_name}</h1>
                <p>{datetime.now().strftime('%d.%m.%Y')} • İşte güncel çalışma özetin.</p>
            </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="stat-card"><div class="stat-val">{my_total}</div><div class="stat-label">SANA ATANAN İŞ</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="stat-card"><div class="stat-val">{my_done}</div><div class="stat-label">TAMAMLANAN</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="stat-card"><div class="stat-val">{team_done}</div><div class="stat-label">ŞİRKET GENELİ BİTEN</div></div>', unsafe_allow_html=True)
        with c4:
            perf = int((my_done/my_total)*100) if my_total > 0 else 100
            st.markdown(f'<div class="stat-card"><div class="stat-val">%{perf}</div><div class="stat-label">VERİMLİLİK</div></div>', unsafe_allow_html=True)

        st.write("")
        st.markdown("### 📊 Genel İlerleme")
        team_total = len(team_today)
        team_perc = (team_done / team_total) if team_total > 0 else 0
        st.caption(f"Şirket İlerleme Oranı: %{int(team_perc*100)}")
        st.progress(team_perc)

    # --- GÖREVLERİM ---
    elif menu == "📝 Görevlerim":
        st.markdown(f'<div class="material-header"><h1>Görevlerin</h1><p>Bugün sana atanmış işler listesi.</p></div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        todo = [t for t in my_tasks if t.get("durum") != "tamamlandi"]
        done = [t for t in my_tasks if t.get("durum") == "tamamlandi"]
        
        with col1:
            st.markdown("##### ⏳ Bekleyenler")
            for t in todo:
                saat = t.get("deadline","").split("T")[1][:5]
                st.markdown(f"""
                <div class="material-card">
                    <div class="card-top">
                        <div class="card-title">{t["is_tanimi"]}</div>
                        <div class="card-time">{saat}</div>
                    </div>
                    {f'<div class="card-desc">{t["notlar"]}</div>' if t.get("notlar") else ''}
                </div>
                """, unsafe_allow_html=True)
                st.checkbox("Tamamlandı", key=t['id'])
        with col2:
            st.markdown("##### ✔️ Bitenler")
            for t in done:
                st.markdown(f"""
                <div class="material-card material-card-done">
                    <div class="card-top">
                        <div class="card-title" style="text-decoration: line-through; color: {T_MUTED} !important;">{t["is_tanimi"]}</div>
                        <div class="card-time" style="color: {T_MUTED} !important;">Tamamlandı</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.write("")
        if st.button("Değişiklikleri Kaydet"):
            for t in my_tasks:
                ns = "tamamlandi" if st.session_state.get(t['id']) else "bekliyor"
                if t['durum'] != ns: httpx.patch(f"{SUPABASE_URL}?id=eq.{t['id']}", headers=HEADERS, json={"durum": ns})
            st.rerun()

    # --- ŞİRKET RADARI ---
    elif menu == "🌐 Şirket Radarı":
        st.markdown(f'<div class="material-header"><h1>Şirket Radarı</h1><p>Ekipteki diğer çalışma arkadaşların neler yapıyor?</p></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### ✔️ Tamamlanan İşler")
            for b in [t for t in team_today if t.get("durum") == "tamamlandi"]:
                saat = b.get("deadline","").split("T")[1][:5]
                st.markdown(f"""
                <div class="material-card material-card-done">
                    <div class="card-top">
                        <div class="card-title">{b["is_tanimi"]}</div>
                        <div class="card-time" style="color: {T_MUTED} !important;">{saat}</div>
                    </div>
                    <div><span class="card-label">👤 {b["personel_ad"]}</span></div>
                </div>
                """, unsafe_allow_html=True)
        with c2:
            st.markdown("##### ⏳ Üzerinde Çalışılanlar")
            for d in [t for t in team_today if t.get("durum") != "tamamlandi"]:
                saat = d.get("deadline","").split("T")[1][:5]
                st.markdown(f"""
                <div class="material-card">
                    <div class="card-top">
                        <div class="card-title">{d["is_tanimi"]}</div>
                        <div class="card-time">{saat}</div>
                    </div>
                    <div><span class="card-label">👤 {d["personel_ad"]}</span></div>
                </div>
                """, unsafe_allow_html=True)

    # --- GELECEK İŞLER ---
    elif menu == "🗓️ Gelecek İşler":
        st.markdown(f'<div class="material-header"><h1>Gelecek Planları</h1><p>Önümüzdeki günler için tanımlanan iş listesi.</p></div>', unsafe_allow_html=True)
        future_tasks = [t for t in data if t.get("deadline", "").split("T")[0] > today_str]
        future_tasks.sort(key=lambda x: x.get("deadline", ""))
        
        for ft in future_tasks:
            dv = datetime.strptime(ft['deadline'].split('T')[0], '%Y-%m-%d').strftime('%d.%m.%Y')
            saat = ft.get("deadline", "").split("T")[1][:5]
            st.markdown(f"""
            <div class="material-card">
                <div class="card-top">
                    <div class="card-title">{ft["is_tanimi"]}</div>
                    <div class="card-time">{dv} - {saat}</div>
                </div>
                <div><span class="card-label">👤 {ft["personel_ad"]}</span></div>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
