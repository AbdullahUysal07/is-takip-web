import streamlit as st
import httpx
from datetime import datetime

# --- SAYFA AYARLARI ---
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

# --- SABİT MATERIAL TASARIM RENKLERİ (GMAIL LIGHT) ---
T_CARD = "#ffffff"        
T_TEXT = "#202124"
T_MUTED = "#5f6368"
T_BORDER = "#dadce0"
T_PRIMARY = "#1a73e8"
T_DONE_BG = "#f8f9fa"

# --- GÜVENLİ CSS ---
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

    /* Başlıklar */
    .custom-h {{ color: {T_TEXT}; font-family: 'Roboto', sans-serif; font-weight: 500; margin-bottom: 0px; padding-bottom: 0px; }}
    
    /* Vurgulu Kaydet Butonu (Primary Button) */
    button[kind="primary"] {{
        background-color: {T_PRIMARY} !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 14px 24px !important;
        border-radius: 8px !important;
        border: none !important;
        font-size: 16px !important;
        box-shadow: 0 2px 6px rgba(26, 115, 232, 0.3) !important;
        transition: all 0.2s ease;
    }}
    button[kind="primary"]:hover {{
        background-color: #1557b0 !important;
        box-shadow: 0 4px 10px rgba(26, 115, 232, 0.4) !important;
    }}
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
        st.write("---")
        menu = st.radio("MENÜ", ["📥 Ana Sayfa", "📝 Görevlerim", "🌐 Şirket Radarı", "🗓️ Gelecek İşler"])
        st.write("---")
        st.caption(f"👤 {user_name}")

    # --- DASHBOARD ---
    if menu == "📥 Ana Sayfa":
        st.markdown(f"<h2 class='custom-h'>Hoş Geldin, {user_name}</h2>", unsafe_allow_html=True)
        st.caption(f"{datetime.now().strftime('%d.%m.%Y')} • İşte çalışma masanın güncel özeti.")
        st.write("---")

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
        st.write("")
        
        col1, col2 = st.columns(2)
        todo = [t for t in my_tasks if t.get("durum") != "tamamlandi"]
        done = [t for t in my_tasks if t.get("durum") == "tamamlandi"]
        
        with col1:
            st.write("⏳ Bekleyenler")
            for t in todo:
                saat = t.get("deadline","").split("T")[1][:5]
                # Dosya linki varsa şık bir buton oluşturur
                file_link = f'<div style="margin-top: 8px; margin-bottom: 8px;"><a href="{t["dosya_url"]}" target="_blank" style="text-decoration: none; color: {T_PRIMARY}; font-size: 12px; font-weight: bold; background: #e8f0fe; padding: 4px 8px; border-radius: 4px; display: inline-block;">📎 Eki İndir / Görüntüle</a></div>' if t.get("dosya_url") else ''
                
                with st.container(border=True):
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 14px; font-weight: 500; color: {T_TEXT};">{t["is_tanimi"]}</span>
                        <span style="font-size: 12px; font-weight: 500; color: {T_PRIMARY};">{saat}</span>
                    </div>
                    {f'<div style="font-size: 13px; color: {T_MUTED}; margin-bottom: 12px;"><b>Yönetici Notu:</b> {t["notlar"]}</div>' if t.get("notlar") else ''}
                    {file_link}
                    """, unsafe_allow_html=True)
                    st.checkbox("Tamamlandı", key=t['id'])
                
        with col2:
            st.write("✔️ Bitenler")
            for t in done:
                file_link = f'<div style="margin-top: 8px;"><a href="{t["dosya_url"]}" target="_blank" style="text-decoration: none; color: {T_MUTED}; font-size: 12px; font-weight: bold; background: #f1f3f4; padding: 4px 8px; border-radius: 4px; display: inline-block;">📎 Eki Aç</a></div>' if t.get("dosya_url") else ''
                with st.container(border=True):
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; opacity: 0.6;">
                        <span style="font-size: 14px; font-weight: 500; color: {T_MUTED}; text-decoration: line-through;">{t["is_tanimi"]}</span>
                        <span style="font-size: 12px; font-weight: 500; color: {T_MUTED};">Tamamlandı</span>
                    </div>
                    {file_link}
                    """, unsafe_allow_html=True)
        
        st.write("---")
        if st.button("🚀 Değişiklikleri Kaydet", type="primary", use_container_width=True):
            for t in my_tasks:
                ns = "tamamlandi" if st.session_state.get(t['id']) else "bekliyor"
                if t['durum'] != ns: httpx.patch(f"{SUPABASE_URL}?id=eq.{t['id']}", headers=HEADERS, json={"durum": ns})
            st.rerun()

    # --- ŞİRKET RADARI ---
    elif menu == "🌐 Şirket Radarı":
        st.markdown("<h3 class='custom-h'>Şirket Radarı</h3>", unsafe_allow_html=True)
        st.caption("Ekipteki diğer çalışma arkadaşların neler yapıyor?")
        st.write("")
        
        c1, c2 = st.columns(2)
        with c1:
            st.write("✔️ Tamamlanan İşler")
            for b in [t for t in team_today if t.get("durum") == "tamamlandi"]:
                saat = b.get("deadline","").split("T")[1][:5]
                file_link = f'<div style="margin-top: 8px;"><a href="{b["dosya_url"]}" target="_blank" style="text-decoration: none; color: {T_PRIMARY}; font-size: 11px; font-weight: bold; background: #e8f0fe; padding: 4px 8px; border-radius: 4px; display: inline-block;">📎 Ek</a></div>' if b.get("dosya_url") else ''
                with st.container(border=True):
                    st.markdown(f"""
                    <div style="opacity: 0.7;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <span style="font-size: 14px; font-weight: 500; color: {T_TEXT};">{b["is_tanimi"]}</span>
                            <span style="font-size: 12px; font-weight: 500; color: {T_MUTED};">{saat}</span>
                        </div>
                        <div style="font-size: 11px; color: {T_MUTED};">👤 {b["personel_ad"]}</div>
                        {file_link}
                    </div>
                    """, unsafe_allow_html=True)
                    
        with c2:
            st.write("⏳ Üzerinde Çalışılanlar")
            for d in [t for t in team_today if t.get("durum") != "tamamlandi"]:
                saat = d.get("deadline","").split("T")[1][:5]
                file_link = f'<div style="margin-top: 8px;"><a href="{d["dosya_url"]}" target="_blank" style="text-decoration: none; color: {T_PRIMARY}; font-size: 11px; font-weight: bold; background: #e8f0fe; padding: 4px 8px; border-radius: 4px; display: inline-block;">📎 Ek</a></div>' if d.get("dosya_url") else ''
                with st.container(border=True):
                    st.markdown(f"""
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <span style="font-size: 14px; font-weight: 500; color: {T_TEXT};">{d["is_tanimi"]}</span>
                            <span style="font-size: 12px; font-weight: 500; color: {T_PRIMARY};">{saat}</span>
                        </div>
                        <div style="font-size: 11px; color: {T_MUTED};">👤 {d["personel_ad"]}</div>
                        {file_link}
                    </div>
                    """, unsafe_allow_html=True)

    # --- GELECEK İŞLER ---
    elif menu == "🗓️ Gelecek İşler":
        st.markdown("<h3 class='custom-h'>Gelecek Planları</h3>", unsafe_allow_html=True)
        st.caption("Önümüzdeki günler için tanımlanan iş listesi.")
        st.write("")
        
        future_tasks = [t for t in data if t.get("deadline", "").split("T")[0] > today_str]
        future_tasks.sort(key=lambda x: x.get("deadline", ""))
        
        for ft in future_tasks:
            dv = datetime.strptime(ft['deadline'].split('T')[0], '%Y-%m-%d').strftime('%d.%m.%Y')
            saat = ft.get("deadline", "").split("T")[1][:5]
            file_link = f'<div style="margin-top: 8px;"><a href="{ft["dosya_url"]}" target="_blank" style="text-decoration: none; color: {T_PRIMARY}; font-size: 11px; font-weight: bold; background: #e8f0fe; padding: 4px 8px; border-radius: 4px; display: inline-block;">📎 Ek</a></div>' if ft.get("dosya_url") else ''
            with st.container(border=True):
                st.markdown(f"""
                <div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span style="font-size: 14px; font-weight: 500; color: {T_TEXT};">{ft["is_tanimi"]}</span>
                        <span style="font-size: 12px; font-weight: 500; color: {T_PRIMARY};">{dv} - {saat}</span>
                    </div>
                    <div style="font-size: 11px; color: {T_MUTED};">👤 {ft["personel_ad"]}</div>
                    {file_link}
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
