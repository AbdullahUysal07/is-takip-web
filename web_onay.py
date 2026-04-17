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
    button[kind="primary"] {{ background-color: {T_PRIMARY} !important; border-radius: 25px !important; padding: 0.6rem 2rem !important; font-weight: 600 !important; }}
</style>
""", unsafe_allow_html=True)

def main():
    # --- CERRAHİ MÜDAHALE: MOBİL UYUMLU TOKEN OKUMA ---
    token = None
    # 1. Yöntem: URL'den oku
    if "id" in st.query_params:
        token = st.query_params["id"]
    
    # 2. Yöntem: Eğer URL'den gelmezse (Mobil hata payı), manuel giriş alanı göster
    if not token:
        st.markdown("<h2 style='text-align:center;'>🚀 Workspace Giriş</h2>", unsafe_allow_html=True)
        st.info("Mobil tarayıcınız oturum bilgisini linkten okuyamadı. Lütfen size iletilen linkteki 8 haneli kodu aşağıya girin.")
        token_input = st.text_input("Giriş Kodu (Örn: a1b2c3d4)", "").strip()
        if st.button("Sisteme Giriş Yap", type="primary"):
            if token_input:
                st.query_params["id"] = token_input
                st.rerun()
        st.stop() # Kod girilene kadar aşağıyı çalıştırma

    # --- VERİ ÇEKME (Mevcut yapınla aynı) ---
    try:
        with httpx.Client(timeout=15.0) as client: # Mobil internet için timeout artırıldı
            r = client.get(SUPABASE_URL, headers=HEADERS)
            data = r.json()
        
        user_row = [t for t in data if t.get("magic_token") == token]
        if not user_row: 
            st.error("Kod geçersiz veya süresi dolmuş. Lütfen linki kontrol edin.")
            if st.button("Geri Dön"):
                st.query_params.clear()
                st.rerun()
            st.stop()
        
        # ... (Geri kalan kod yapın tamamen aynı kalsın) ...
        user_name = user_row[0]["personel_ad"]
        today_str = datetime.now().strftime("%Y-%m-%d")

        my_tasks = [t for t in data if t.get("personel_ad") == user_name and t.get("deadline", "").startswith(today_str)]
        my_done = sum(1 for t in my_tasks if t.get("durum") == "tamamlandi")
        my_total = len(my_tasks)
        team_today = [t for t in data if t.get("deadline", "").startswith(today_str)]
        team_done = sum(1 for t in team_today if t.get("durum") == "tamamlandi")

        # --- SIDEBAR & DASHBOARD (Görsel tasarımı koru) ---
        with st.sidebar:
            st.markdown(f"<h1 style='color:{T_PRIMARY}; font-size: 24px; font-weight: 800;'>FLU DİJİTAL</h1>", unsafe_allow_html=True)
            st.write("---")
            menu = st.radio("MENÜ", ["📊 Dashboard", "📝 Görevlerim", "🌐 Şirket Akışı", "🗓️ Gelecek Planlarım"])
            st.write("---")
            st.markdown(f"👤 **{user_name}**")

        if menu == "📊 Dashboard":
            st.markdown(f"## Hoş Geldin, {user_name.split()[0]} 👋")
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.markdown(f'<div class="stat-card"><div class="stat-label">İşlerin</div><div class="stat-val">{my_total}</div></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="stat-card"><div class="stat-label">Biten</div><div class="stat-val">{my_done}</div></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="stat-card"><div class="stat-label">Ekip</div><div class="stat-val">{team_done}</div></div>', unsafe_allow_html=True)
            with c4:
                perf = int((my_done/my_total)*100) if my_total > 0 else 100
                st.markdown(f'<div class="stat-card"><div class="stat-label">Verim</div><div class="stat-val">%{perf}</div></div>', unsafe_allow_html=True)
            st.write("---")
            st.progress((team_done / len(team_today)) if len(team_today) > 0 else 0)

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

        elif menu == "🌐 Şirket Akışı":
            st.markdown("## Şirket Radarı")
            for b in team_today:
                with st.container(border=True):
                    st.write(f"{'✅' if b['durum'] == 'tamamlandi' else '⏳'} **{b['personel_ad']}**: {b['is_tanimi']}")

        elif menu == "🗓️ Gelecek Planlarım":
            st.markdown("## Ajanda")
            future = [t for t in data if t.get("deadline", "").split("T")[0] > today_str and t.get("personel_ad") == user_name]
            for ft in future:
                with st.container(border=True):
                    st.write(f"📅 **{ft['deadline'][:10]}** | {ft['is_tanimi']}")

    except Exception as e:
        st.error(f"Sistem Hatası: {e}")

if __name__ == "__main__":
    main()
