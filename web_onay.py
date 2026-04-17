import streamlit as st
import httpx
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="FLU DİJİTAL | Workspace", 
    page_icon="✉️", 
    layout="wide"
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

# --- GÜVENLİ RENK PALETİ ---
if st.session_state.theme == "Night":
    bg_color = "#202124"
    text_color = "#ffffff"
    card_bg = "#303134"
    border_color = "#5f6368"
    accent_color = "#8ab4f8"
else:
    bg_color = "#ffffff"
    text_color = "#202124"
    card_bg = "#ffffff"
    border_color = "#dadce0"
    accent_color = "#1a73e8"

# --- %100 GÜVENLİ CSS (SADECE KARTLARI ETKİLER) ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
    
    .stApp {{ background-color: {bg_color}; font-family: 'Roboto', sans-serif; }}
    .stApp p, .stApp span, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp label {{ color: {text_color} !important; }}
    
    /* GMAIL TASARIM KARTLARI */
    .material-header {{ border-bottom: 1px solid {border_color}; padding-bottom: 15px; margin-bottom: 25px; margin-top: 10px; }}
    .material-header h1 {{ font-size: 26px !important; margin: 0; color: {text_color}; }}
    .material-header p {{ opacity: 0.7; font-size: 13px; margin-top: 5px; }}
    
    .stat-card {{ background: {card_bg}; border: 1px solid {border_color}; border-radius: 8px; padding: 15px; text-align: center; margin-bottom: 10px; }}
    .stat-val {{ font-size: 26px; font-weight: bold; color: {accent_color}; line-height: 1.2; }}
    .stat-label {{ font-size: 11px; opacity: 0.7; margin-top: 5px; }}
    
    .material-card {{ background: {card_bg}; border: 1px solid {border_color}; border-radius: 8px; padding: 15px; margin-bottom: 10px; display: flex; flex-direction: column; }}
    .card-top {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }}
    .card-title {{ font-weight: bold; font-size: 14px; color: {text_color}; }}
    .card-time {{ font-size: 12px; color: {accent_color}; font-weight: bold; }}
    .card-desc {{ font-size: 12px; opacity: 0.8; margin-top: 5px; }}
    
    /* Streamlit Butonlarını Yuvarlak Yapma */
    div.stButton > button:first-child {{
        border-radius: 20px !important; border: 1px solid {accent_color} !important; color: {text_color} !important; background: transparent !important; width: 100%;
    }}
</style>
""", unsafe_allow_html=True)

def main():
    token = st.query_params.get("id")
    if not token:
        st.markdown(f'<div class="material-header"><h1>FLU DİJİTAL</h1><p>Geçerli bir oturum bulunamadı.</p></div>', unsafe_allow_html=True)
        st.stop()

    # --- VERİ ÇEKME ---
    try:
        with httpx.Client(timeout=10.0) as client:
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
        st.error("Sunucuya bağlanılamadı. Lütfen sayfayı yenileyin.")
        st.stop()

    # --- YAN MENÜ ---
    with st.sidebar:
        theme_icon = "🌙 Gece Modu" if st.session_state.theme == "Day" else "☀️ Gündüz Modu"
        if st.button(theme_icon):
            st.session_state.theme = "Night" if st.session_state.theme == "Day" else "Day"
            st.rerun()
            
        st.write("---")
        menu = st.radio("MENÜ", ["📥 Ana Sayfa", "📝 Görevlerim", "🌐 Şirket Radarı", "🗓️ Gelecek İşler"])
        st.write("---")
        st.caption(f"👤 Aktif Kullanıcı: {user_name}")

    # --- DASHBOARD ---
    if menu == "📥 Ana Sayfa":
        st.markdown(f"""
            <div class="material-header">
                <h1>Hoş Geldin, {user_name}</h1>
                <p>{datetime.now().strftime('%d.%m.%Y')} • İşte çalışma masanın güncel özeti.</p>
            </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="stat-card"><div class="stat-val">{my_total}</div><div class="stat-label">SANA ATANAN İŞ</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="stat-card"><div class="stat-val">{my_done}</div><div class="stat-label">TAMAMLANAN</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="stat-card"><div class="stat-val">{team_done}</div><div class="stat-label">ŞİRKET BİTEN</div></div>', unsafe_allow_html=True)
        with c4:
            perf = int((my_done/my_total)*100) if my_total > 0 else 100
            st.markdown(f'<div class="stat-card"><div class="stat-val">%{perf}</div><div class="stat-label">VERİMLİLİK</div></div>', unsafe_allow_html=True)

        st.write("")
        st.markdown(f"<span style='font-size:14px; font-weight:500;'>Şirket Geneli İlerleme Durumu</span>", unsafe_allow_html=True)
        team_total = len(team_today)
        team_perc = (team_done / team_total) if team_total > 0 else 0
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
                st.checkbox("Tamamlandı olarak işaretle", key=t['id'])
                
        with col2:
            st.markdown("##### ✔️ Bitenler")
            for t in done:
                st.markdown(f"""
                <div class="material-card" style="opacity: 0.6;">
                    <div class="card-top">
                        <div class="card-title" style="text-decoration: line-through;">{t["is_tanimi"]}</div>
                        <div class="card-time">Tamamlandı</div>
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
                <div class="material-card" style="opacity: 0.6;">
                    <div class="card-top">
                        <div class="card-title">{b["is_tanimi"]}</div>
                        <div class="card-time">{saat}</div>
                    </div>
                    <div class="card-desc">👤 {b["personel_ad"]}</div>
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
                    <div class="card-desc">👤 {d["personel_ad"]}</div>
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
                <div class="card-desc">👤 {ft["personel_ad"]}</div>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
