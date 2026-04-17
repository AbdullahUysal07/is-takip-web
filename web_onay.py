import streamlit as st
import httpx
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="FLU DİJİTAL | Workspace", 
    page_icon="🚀", 
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

# --- TASARIM RENKLERİ (web_app.py ile uyumlu) ---
T_CARD = "#ffffff"        
T_TEXT = "#202124"
T_MUTED = "#5f6368"
T_BORDER = "#dadce0"
T_PRIMARY = "#1a73e8"

# --- GELİŞMİŞ CSS (Workspace Tasarımı) ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}

    /* Sidebar Düzenlemesi */
    section[data-testid="stSidebar"] {{ background-color: #F8F9FA !important; border-right: 1px solid {T_BORDER}; }}

    /* İstatistik Kartları */
    .stat-card {{
        background: {T_CARD}; 
        border: 1px solid {T_BORDER}; 
        border-radius: 12px; 
        padding: 20px; 
        text-align: left; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }}
    .stat-val {{ font-size: 32px; font-weight: 700; color: {T_PRIMARY}; }}
    .stat-label {{ font-size: 13px; color: {T_MUTED}; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; }}

    /* Görev Kartları */
    div[data-testid="stExpander"], div.stElementContainer > div[style*="border: 1px solid"] {{
        border-radius: 10px !important;
        border: 1px solid {T_BORDER} !important;
        background-color: white !important;
    }}

    /* Kaydet Butonu */
    button[kind="primary"] {{
        background-color: {T_PRIMARY} !important;
        border-radius: 25px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 6px rgba(26, 115, 232, 0.2) !important;
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
        st.error("Sunucuya bağlanılamadı. Sayfayı yenileyin.")
        st.stop()

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown(f"<h1 style='color:{T_PRIMARY}; font-size: 24px; font-weight: 800;'>FLU DİJİTAL</h1>", unsafe_allow_html=True)
        st.caption("Workspace / Çalışma Alanı")
        st.write("---")
        menu = st.radio("MENÜ", ["📊 Dashboard", "📝 Görevlerim", "🌐 Şirket Akışı", "🗓️ Gelecek Planlarım"])
        st.write("---")
        st.markdown(f"👤 **{user_name}**")
        st.caption("Aktif Oturum Açık")

    # --- 1. DASHBOARD ---
    if menu == "📊 Dashboard":
        st.markdown(f"<h2 style='font-weight:700; color:{T_TEXT};'>Hoş Geldin, {user_name.split()[0]} 👋</h2>", unsafe_allow_html=True)
        st.write(f"Bugün **{datetime.now().strftime('%d %B %Y')}**. İşte senin için hazırladığımız özet.")
        st.write("")

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="stat-card"><div class="stat-label">Bugünkü İşlerin</div><div class="stat-val">{my_total}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="stat-card"><div class="stat-label">Tamamlanan</div><div class="stat-val">{my_done}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="stat-card"><div class="stat-label">Ekip Başarısı</div><div class="stat-val">{team_done}</div></div>', unsafe_allow_html=True)
        with c4:
            perf = int((my_done/my_total)*100) if my_total > 0 else 100
            st.markdown(f'<div class="stat-card"><div class="stat-label">Performans</div><div class="stat-val">%{perf}</div></div>', unsafe_allow_html=True)

        st.write("---")
        st.markdown("##### 📈 Şirket Geneli Günlük İlerleme")
        team_total = len(team_today)
        team_perc = (team_done / team_total) if team_total > 0 else 0
        st.progress(team_perc)

    # --- 2. GÖREVLERİM ---
    elif menu == "📝 Görevlerim":
        st.markdown(f"<h2 style='font-weight:700;'>Günlük Görev Listen</h2>", unsafe_allow_html=True)
        st.write("Aşağıdaki listeden işlerini takip edebilir ve durumlarını güncelleyebilirsin.")
        st.write("")
        
        col1, col2 = st.columns(2)
        todo = [t for t in my_tasks if t.get("durum") != "tamamlandi"]
        done = [t for t in my_tasks if t.get("durum") == "tamamlandi"]
        
        with col1:
            st.markdown("##### ⏳ Bekleyen İşlerin")
            for t in todo:
                saat = t.get("deadline","").split("T")[1][:5]
                with st.container(border=True):
                    c_txt, c_check = st.columns([4, 1])
                    c_txt.markdown(f"**{t['is_tanimi']}**")
                    c_txt.caption(f"⏰ Teslim: {saat}")
                    if t.get("notlar"): c_txt.info(f"📌 **Not:** {t['notlar']}")
                    if t.get("dosya_url"): c_txt.link_button("📎 Dosya Eki", t["dosya_url"])
                    c_check.checkbox("Bitti", key=t['id'])
                
        with col2:
            st.markdown("##### ✅ Tamamladıkların")
            for t in done:
                with st.container(border=True):
                    st.markdown(f"<div style='opacity:0.6; text-decoration: line-through;'><b>{t['is_tanimi']}</b></div>", unsafe_allow_html=True)
                    st.caption("Görev başarıyla tamamlandı.")
                    if t.get("dosya_url"): st.link_button("📎 Dosyayı Aç", t["dosya_url"])
        
        st.write("")
        if st.button("🚀 Değişiklikleri Sisteme Kaydet", type="primary", use_container_width=True):
            for t in my_tasks:
                ns = "tamamlandi" if st.session_state.get(t['id']) else "bekliyor"
                if t['durum'] != ns: httpx.patch(f"{SUPABASE_URL}?id=eq.{t['id']}", headers=HEADERS, json={"durum": ns})
            st.success("Tüm değişiklikler buluta kaydedildi!")
            st.rerun()

    # --- 3. ŞİRKET AKIŞI ---
    elif menu == "🌐 Şirket Akışı":
        st.markdown("<h2 style='font-weight:700;'>Şirket Radarı</h2>", unsafe_allow_html=True)
        st.write("Ekip arkadaşlarının bugünkü aksiyonlarını buradan takip edebilirsin.")
        st.write("")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### ✔️ Bitenler")
            for b in [t for t in team_today if t.get("durum") == "tamamlandi"]:
                with st.container(border=True):
                    st.markdown(f"**{b['personel_ad']}**")
                    st.write(b["is_tanimi"])
                    st.caption(f"⏰ {b.get('deadline','').split('T')[1][:5]}")

        with c2:
            st.markdown("##### ⏳ Devam Edenler")
            for d in [t for t in team_today if t.get("durum") != "tamamlandi"]:
                with st.container(border=True):
                    st.markdown(f"**{d['personel_ad']}**")
                    st.write(d["is_tanimi"])
                    st.caption(f"⏰ {d.get('deadline','').split('T')[1][:5]}")

    # --- 4. GELECEK PLANLARIM ---
    elif menu == "🗓️ Gelecek Planlarım":
        st.markdown("<h2 style='font-weight:700;'>Gelecek Ajandası</h2>", unsafe_allow_html=True)
        st.write("Önümüzdeki günlerde seni bekleyen görevler.")
        st.write("")
        
        future_tasks = [t for t in data if t.get("deadline", "").split("T")[0] > today_str and t.get("personel_ad") == user_name]
        future_tasks.sort(key=lambda x: x.get("deadline", ""))
        
        if not future_tasks:
            st.info("Harika! Önümüzdeki günler için henüz tanımlanmış bir işin yok.")
        else:
            for ft in future_tasks:
                dv = datetime.strptime(ft['deadline'].split('T')[0], '%Y-%m-%d').strftime('%d.%m.%Y')
                with st.container(border=True):
                    st.markdown(f"📅 **{dv}** | ⏰ **{ft.get('deadline','').split('T')[1][:5]}**")
                    st.write(ft["is_tanimi"])
                    if ft.get("notlar"): st.caption(f"Not: {ft['notlar']}")

if __name__ == "__main__":
    main()
