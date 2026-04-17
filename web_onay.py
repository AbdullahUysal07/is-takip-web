import streamlit as st
import httpx
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="TASKLY | Workspace", 
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

# --- TASARIM RENKLERİ ---
T_CARD = "#ffffff"        
T_TEXT = "#202124"
T_MUTED = "#5f6368"
T_BORDER = "#dadce0"
T_PRIMARY = "#1a73e8"

# --- GELİŞMİŞ CSS ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600;700&display=swap');
    html, body, [class*="css"] {{ font-family: 'Segoe UI', sans-serif; }}
    section[data-testid="stSidebar"] {{ background-color: #F8F9FA !important; border-right: 1px solid {T_BORDER}; }}
    .stat-card {{ background: {T_CARD}; border: 1px solid {T_BORDER}; border-radius: 12px; padding: 20px; text-align: left; }}
    .stat-val {{ font-size: 32px; font-weight: 700; color: {T_PRIMARY}; }}
    .stat-label {{ font-size: 13px; color: {T_MUTED}; font-weight: 600; text-transform: uppercase; }}
    .stButton > button {{ border-radius: 20px !important; font-size: 12px !important; }}
</style>
""", unsafe_allow_html=True)

def main():
    # --- ONARIM: MOBİL OTURUM HAFIZASI (SESSION STATE) ---
    if "magic_token" not in st.session_state:
        st.session_state.magic_token = None

    # URL'den ID'yi yakala (Sadece ilk girişte veya hafıza boşsa)
    q_params = st.query_params
    if "id" in q_params:
        st.session_state.magic_token = q_params["id"]

    # Eğer hala token yoksa (Link bozuksa veya mobil parametreyi sildiyse)
    if not st.session_state.magic_token:
        st.markdown("<h2 style='text-align:center; color:#1a73e8;'>TASKLY Workspace</h2>", unsafe_allow_html=True)
        st.warning("Oturum bilgisi linkten okunamadı.")
        m_token = st.text_input("Size iletilen 8 haneli kodu girin:", placeholder="Örn: a1b2c3d4").strip()
        if st.button("Giriş Yap", type="primary", use_container_width=True):
            if m_token:
                st.session_state.magic_token = m_token
                st.rerun()
        st.stop()

    # Artık 'token' verisini URL'den değil, güvenli hafızadan alıyoruz.
    token = st.session_state.magic_token

    # --- VERİ ÇEKME ---
    try:
        # Mobil şebeke dalgalanmaları için timeout 20 saniyeye çıkarıldı (Hız için kritik)
        with httpx.Client(timeout=20.0) as client:
            r = client.get(SUPABASE_URL, headers=HEADERS)
            data = r.json()
        
        user_row = [t for t in data if t.get("magic_token") == token]
        if not user_row: 
            st.error("Kod geçersiz. Lütfen linki veya kodu kontrol edin.")
            if st.button("Sıfırla ve Tekrar Dene"):
                st.session_state.magic_token = None
                st.rerun()
            st.stop()
        
        user_name = user_row[0]["personel_ad"]
        today_str = datetime.now().strftime("%Y-%m-%d")

        # Veri filtreleme
        my_tasks = [t for t in data if t.get("personel_ad") == user_name and t.get("deadline", "").startswith(today_str)]
        my_done = sum(1 for t in my_tasks if t.get("durum") == "tamamlandi")
        my_total = len(my_tasks)
        team_today = [t for t in data if t.get("deadline", "").startswith(today_str)]
        team_done = sum(1 for t in team_today if t.get("durum") == "tamamlandi")

        # --- YAN MENÜ ---
        with st.sidebar:
            st.markdown(f"<h1 style='color:{T_PRIMARY}; font-size: 24px; font-weight: 800;'>TASKLY</h1>", unsafe_allow_html=True)
            st.write("---")
            menu = st.radio("MENÜ", ["📊 Dashboard", "📝 Görevlerim", "🌐 Şirket Radarı", "🗓️ Gelecek Planlarım"], key="nav_menu")
            st.write("---")
            st.markdown(f"👤 **{user_name}**")

        # --- 1. DASHBOARD ---
        if menu == "📊 Dashboard":
            st.markdown(f"## Hoş Geldin, {user_name.split()[0]} 👋")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f'<div class="stat-card"><div class="stat-label">İşlerin</div><div class="stat-val">{my_total}</div></div>', unsafe_allow_html=True)
                if st.button("📂 İşlerime Git", use_container_width=True):
                    st.session_state.nav_menu = "📝 Görevlerim"
                    st.rerun()
            with c2: st.markdown(f'<div class="stat-card"><div class="stat-label">Biten</div><div class="stat-val">{my_done}</div></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="stat-card"><div class="stat-label">Ekip</div><div class="stat-val">{team_done}</div></div>', unsafe_allow_html=True)
            with c4:
                perf = int((my_done/my_total)*100) if my_total > 0 else 100
                st.markdown(f'<div class="stat-card"><div class="stat-label">Verim</div><div class="stat-val">%{perf}</div></div>', unsafe_allow_html=True)
            st.write("---")
            st.progress((team_done / len(team_today)) if len(team_today) > 0 else 0)

        # --- 2. GÖREVLERİM ---
        elif menu == "📝 Görevlerim":
            st.markdown("## Günlük Görevlerin")
            col1, col2 = st.columns(2)
            todo = [t for t in my_tasks if t.get("durum") != "tamamlandi"]
            done = [t for t in my_tasks if t.get("durum") == "tamamlandi"]
            with col1:
                st.subheader("⏳ Bekleyen")
                for t in todo:
                    with st.container(border=True):
                        st.markdown(f"**{t['is_tanimi']}**")
                        st.caption(f"⏰ {t.get('deadline','')[11:16]}")
                        if t.get("notlar"): st.info(f"📌 {t['notlar']}")
                        if t.get("dosya_url"): st.link_button("📎 Dosya", t["dosya_url"])
                        st.checkbox("Bitti", key=t['id'])
            with col2:
                st.subheader("✅ Tamamlanan")
                for t in done:
                    with st.container(border=True):
                        st.markdown(f"<div style='opacity:0.5; text-decoration:line-through;'>{t['is_tanimi']}</div>", unsafe_allow_html=True)

            if st.button("🚀 Kaydet", type="primary", use_container_width=True):
                for t in my_tasks:
                    ns = "tamamlandi" if st.session_state.get(t['id']) else "bekliyor"
                    if t['durum'] != ns: httpx.patch(f"{SUPABASE_URL}?id=eq.{t['id']}", headers=HEADERS, json={"durum": ns})
                st.rerun()

        # --- 3. ŞİRKET RADARI ---
        elif menu == "🌐 Şirket Radarı":
            st.markdown("## Şirket Radarı")
            for b in team_today:
                with st.container(border=True):
                    c_i, c_s = st.columns([4, 1])
                    t_s = b.get('deadline', '').replace('T', ' | ')
                    d_m = "✅ Bitti" if b['durum'] == 'tamamlandi' else "⏳ Devam"
                    d_r = "green" if b['durum'] == 'tamamlandi' else "orange"
                    c_i.markdown(f"**{b['personel_ad']}**")
                    c_i.write(f"📄 {b['is_tanimi']}")
                    c_i.caption(f"📅 {t_s}")
                    c_s.markdown(f"<p style='color:{d_r}; font-weight:bold; font-size:11px;'>{d_m}</p>", unsafe_allow_html=True)

        # --- 4. GELECEK PLANLARIM ---
        elif menu == "🗓️ Gelecek Planlarım":
            st.markdown("## Şirket Gelecek Ajandası")
            f_all = [t for t in data if t.get("deadline", "").split("T")[0] > today_str]
            f_all.sort(key=lambda x: x.get("deadline", ""))
            for ft in f_all:
                with st.container(border=True):
                    c_d, c_c = st.columns([1, 4])
                    d_o = datetime.strptime(ft['deadline'][:10], "%Y-%m-%d")
                    c_d.markdown(f"<div style='text-align:center; background:#f1f3f4; padding:5px; border-radius:5px;'><b>{d_o.day}</b><br><small>{d_o.strftime('%b')}</small></div>", unsafe_allow_html=True)
                    c_c.markdown(f"**{ft['is_tanimi']}**")
                    c_c.caption(f"👤 {ft['personel_ad']} | ⏰ {ft['deadline'][11:16]}")

    except Exception as e:
        st.error(f"Veri bağlantısı kurulamadı. Lütfen sayfayı yenileyin.")

if __name__ == "__main__":
    main()
