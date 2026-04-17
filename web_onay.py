import streamlit as st
import httpx
from datetime import datetime

# --- SAYFA AYARLARI (En güvenli haliyle bırakıldı) ---
st.set_page_config(
    page_title="FLU DİJİTAL | Workspace", 
    page_icon="✉️", 
    layout="wide"
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

# --- TEMA VE RENK AYARLARI (Sadece Kartlar İçin) ---
if "theme" not in st.session_state:
    st.session_state.theme = "Day"

if st.session_state.theme == "Night":
    T_CARD = "#303134"
    T_TEXT = "#ffffff"
    T_MUTED = "#9aa0a6"
    T_BORDER = "#5f6368"
    T_PRIMARY = "#8ab4f8"
    T_DONE_BG = "rgba(138, 180, 248, 0.08)"
else:
    T_CARD = "#ffffff"        
    T_TEXT = "#202124"
    T_MUTED = "#5f6368"
    T_BORDER = "#dadce0"
    T_PRIMARY = "#1a73e8"
    T_DONE_BG = "#f8f9fa"

# --- GÜVENLİ CSS (Sadece bizim ürettiğimiz kartları etkiler) ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
    
    /* İstatistik Kartları */
    .stat-card {{
        background: {T_CARD}; border: 1px solid {T_BORDER}; border-radius: 8px; 
        padding: 16px; text-align: left; margin-bottom: 15px; font-family: 'Roboto', sans-serif;
    }}
    .stat-val {{ font-size: 28px; font-weight: 400; color: {T_PRIMARY}; line-height: 1.2; }}
    .stat-label {{ font-size: 12px; color: {T_MUTED}; font-weight: 500; letter-spacing: 0.5px; }}

    /* Görev Kartları */
    .material-card {{
        background: {T_CARD}; border: 1px solid {T_BORDER}; border-radius: 8px; 
        padding: 14px 16px; margin-bottom: 10px; font-family: 'Roboto', sans-serif;
        display: flex; flex-direction: column; justify-content: center;
    }}
    .material-card-done {{ background: {T_DONE_BG}; border-color: {T_BORDER}; opacity: 0.8; }}
    
    .card-top {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }}
    .card-title {{ font-size: 14px; font-weight: 500; color: {T_TEXT}; }}
    .card-time {{ font-size: 12px; font-weight: 500; color: {T_PRIMARY}; }}
    .card-desc {{ font-size: 13px; color: {T_MUTED}; margin-top: 4px; }}
    .card-label {{ font-size: 11px; color: {T_MUTED}; margin-top: 8px; }}
    
    /* Sadece kendi başlıklarımızı stillendiriyoruz */
    .custom-h {{ color: {T_TEXT}; font-family: 'Roboto', sans-serif; font-weight: 500; }}
</style>
""", unsafe_allow_html=True)

def main():
    token = st.query_params.get("id")
    if not token:
        st.warning("Geçerli bir oturum bulunamadı. Lütfen size iletilen linke tıklayın.")
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
        st.error("Sunucuya bağlanılamadı. İnternetinizi kontrol edip sayfayı yenileyin.")
        st.stop()

    # --- YAN MENÜ ---
    with st.sidebar:
        st.title("FLU DİJİTAL")
        theme_icon = "🌙 Kartları Gece Modu Yap" if st.session_state.theme == "Day" else "☀️ Kartları Gündüz Modu Yap"
        if st.button(theme_icon):
            st.session_state.theme = "Night" if st.session_state.theme == "Day" else "Day"
            st.rerun()
            
        st.write("---")
        menu = st.radio("MENÜ", ["📥 Ana Sayfa", "📝 Görevlerim", "🌐 Şirket Radarı", "🗓️ Gelecek İşler"])
        st.write("---")
        st.caption(f"👤 {user_name}")

    # --- DASHBOARD ---
    if menu == "📥 Ana Sayfa":
        st.markdown(f"<h2 class='custom-h'>Hoş Geldin, {user_name}</h2>", unsafe_allow_html=True)
        st.caption(f"{datetime.now().strftime('%d.%m.%Y')} • İşte çalışma masanın güncel özeti.")
        st.write("")

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="stat-card"><div class="stat-val">{my_total}</div><div class="stat-label">SANA ATANAN İŞ</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="stat-card"><div class="stat-val">{my_done}</div><div class="stat-label">TAMAMLANAN</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="stat-card"><div class="stat-val">{team_done}</div><div class="stat-label">ŞİRKET GENELİ BİTEN</div></div>', unsafe_allow_html=True)
        with c4:
            perf = int((my_done/my_total)*100) if my_total > 0 else 100
            st.markdown(f'<div class="stat-card"><div class="stat-val">%{perf}</div><div class="stat-label">VERİMLİLİK</div></div>', unsafe_allow_html=True)

        st.write("---")
        st.markdown("##### 📊 Şirket Geneli İlerleme Durumu")
        team_total = len(team_today)
        team_perc = (team_done / team_total) if team_total > 0 else 0
        st.progress(team_perc)

    # --- GÖREVLERİM ---
    elif menu == "📝 Görevlerim":
        st.markdown("<h3 class='custom-h'>Görevlerin</h3>", unsafe_allow_html=True)
        st.caption("Bugün sana atanmış işler listesi.")
        
        col1, col2 = st.columns(2)
        todo = [t for t in my_tasks if t.get("durum") != "tamamlandi"]
        done = [t for t in my_tasks if t.get("durum") == "tamamlandi"]
        
        with col1:
            st.write("⏳ Bekleyenler")
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
            st.write("✔️ Bitenler")
            for t in done:
                st.markdown(f"""
                <div class="material-card material-card-done">
                    <div class="card-top">
                        <div class="card-title" style="text-decoration: line-through; color: {T_MUTED};">{t["is_tanimi"]}</div>
                        <div class="card-time" style="color: {T_MUTED};">Tamamlandı</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.write("---")
        if st.button("🚀 Değişiklikleri Kaydet", use_container_width=True):
            for t in my_tasks:
                ns = "tamamlandi" if st.session_state.get(t['id']) else "bekliyor"
                if t['durum'] != ns: httpx.patch(f"{SUPABASE_URL}?id=eq.{t['id']}", headers=HEADERS, json={"durum": ns})
            st.rerun()

    # --- ŞİRKET RADARI ---
    elif menu == "🌐 Şirket Radarı":
        st.markdown("<h3 class='custom-h'>Şirket Radarı</h3>", unsafe_allow_html=True)
        st.caption("Ekipteki diğer çalışma arkadaşların neler yapıyor?")
        
        c1, c2 = st.columns(2)
        with c1:
            st.write("✔️ Tamamlanan İşler")
            for b in [t for t in team_today if t.get("durum") == "tamamlandi"]:
                saat = b.get("deadline","").split("T")[1][:5]
                st.markdown(f"""
                <div class="material-card material-card-done">
                    <div class="card-top">
                        <div class="card-title">{b["is_tanimi"]}</div>
                        <div class="card-time" style="color: {T_MUTED};">{saat}</div>
                    </div>
                    <div class="card-label">👤 {b["personel_ad"]}</div>
                </div>
                """, unsafe_allow_html=True)
        with c2:
            st.write("⏳ Üzerinde Çalışılanlar")
            for d in [t for t in team_today if t.get("durum") != "tamamlandi"]:
                saat = d.get("deadline","").split("T")[1][:5]
                st.markdown(f"""
                <div class="material-card">
                    <div class="card-top">
                        <div class="card-title">{d["is_tanimi"]}</div>
                        <div class="card-time">{saat}</div>
                    </div>
                    <div class="card-label">👤 {d["personel_ad"]}</div>
                </div>
                """, unsafe_allow_html=True)

    # --- GELECEK İŞLER ---
    elif menu == "🗓️ Gelecek İşler":
        st.markdown("<h3 class='custom-h'>Gelecek Planları</h3>", unsafe_allow_html=True)
        st.caption("Önümüzdeki günler için tanımlanan iş listesi.")
        
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
                <div class="card-label">👤 {ft["personel_ad"]}</div>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
