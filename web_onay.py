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
    # --- KRİTİK ONARIM: ANTİ-CACHE (ÖNBELLEK KIRICI) SİSTEMİ ---
    if "magic_token" not in st.session_state:
        st.session_state.magic_token = None

    # URL parametrelerini oku
    q_params = st.query_params
    
    # EĞER URL'DE BİR ID VARSA: Hafızayı zorla güncelle (Safari Önbellek Fix)
    if "id" in q_params:
        yeni_id = q_params["id"]
        # Eğer hafızadaki ID ile URL'deki farklıysa veya hafıza boşsa, URL'dekini mühürle
        if st.session_state.magic_token != yeni_id:
            st.session_state.magic_token = yeni_id

    # Token kontrolü ve st.stop() bariyeri
    token = st.session_state.magic_token
    
    if not token:
        st.markdown("<h2 style='text-align:center; color:#1a73e8;'>TASKLY Workspace</h2>", unsafe_allow_html=True)
        st.warning("Oturum bilgisi doğrulanamadı.")
        st.info("Lütfen linkteki 8 haneli kodu aşağıya girin veya linke tekrar tıklayın.")
        manual_id = st.text_input("Giriş Kodu", placeholder="Örn: a1b2c3d4").strip()
        if st.button("Sisteme Giriş Yap", type="primary", use_container_width=True):
            if manual_id:
                st.session_state.magic_token = manual_id
                st.rerun()
        st.stop() # Güvenli durdurma

    # --- VERİ ÇEKME ---
    try:
        with httpx.Client(timeout=20.0) as client:
            r = client.get(SUPABASE_URL, headers=HEADERS)
            data = r.json()
        
        user_row = [t for t in data if t.get("magic_token") == token]
        if not user_row: 
            st.error("Kod geçersiz veya süresi dolmuş.")
            if st.button("Oturumu Sıfırla"):
                st.session_state.magic_token = None
                st.query_params.clear()
                st.rerun()
            st.stop()
        
        user_name = user_row[0]["personel_ad"]
        today_str = datetime.now().strftime("%Y-%m-%d")

        # Filtrelemeler
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
                # 👇 DİKKAT: Bu satırlar 'with c1:'den daha sağda olmalı!
                st.markdown(f'<div class="stat-card"><div class="stat-label">İşlerin</div><div class="stat-val">{my_total}</div></div>', unsafe_allow_html=True)
                if st.button("📂 İşlerime Git", use_container_width=True):
                    st.session_state.nav_menu = "📝 Görevlerim"
                    st.rerun()
            
            # c2, c3 ve c4'ü de aynı şekilde hizala
            with c2: st.markdown(f'<div class="stat-card"><div class="stat-label">Biten</div><div class="stat-val">{my_done}</div></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="stat-card"><div class="stat-label">Ekip</div><div class="stat-val">{team_done}</div></div>', unsafe_allow_html=True)
            with c4:
                perf = int((my_done/my_total)*100) if my_total > 0 else 100
                st.markdown(f'<div class="stat-card"><div class="stat-label">Verim</div><div class="stat-val">%{perf}</div></div>', unsafe_allow_html=True)
        # --- GÖREVLERİM ---
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

        # --- 2. ŞİRKET RADARI ---
        elif menu == "🌐 Şirket Radarı":
            st.markdown("## Şirket Radarı")
            for b in team_today:
                with st.container(border=True):
                    c_info, c_status = st.columns([4, 1])
                    t_saat = b.get('deadline', '').replace('T', ' | ')
                    d_metin = "✅ Tamamlandı" if b['durum'] == 'tamamlandi' else "⏳ Çalışılıyor"
                    d_renk = "green" if b['durum'] == 'tamamlandi' else "orange"
                    c_info.markdown(f"**{b['personel_ad']}**")
                    c_info.write(f"📄 {b['is_tanimi']}")
                    c_info.caption(f"📅 {t_saat}")
                    c_status.markdown(f"<p style='color:{d_renk}; font-weight:bold; font-size:11px;'>{d_metin}</p>", unsafe_allow_html=True)

        # --- 3. GELECEK PLANLARIM ---
        elif menu == "🗓️ Gelecek Planlarım":
            st.markdown("## Şirket Gelecek Ajandası")
            f_all = [t for t in data if t.get("deadline", "").split("T")[0] > today_str]
            f_all.sort(key=lambda x: x.get("deadline", ""))
            for ft in f_all:
                with st.container(border=True):
                    col_d, col_c = st.columns([1, 4])
                    d_obj = datetime.strptime(ft['deadline'][:10], "%Y-%m-%d")
                    col_d.markdown(f"""
                        <div style="background:#f1f3f4; border-radius:8px; padding:10px; text-align:center; border-left:5px solid {T_PRIMARY};">
                            <div style="font-size:10px; color:{T_MUTED};">{d_obj.strftime('%b').upper()}</div>
                            <div style="font-size:20px; font-weight:bold; color:{T_PRIMARY};">{d_obj.day}</div>
                            <div style="font-size:10px; color:{T_TEXT};">{ft['deadline'][11:16]}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    col_c.markdown(f"**{ft['is_tanimi']}**")
                    col_c.caption(f"👤 Sorumlu: {ft['personel_ad']}")

    except Exception as e:
        st.error("Bağlantı güncelleniyor, lütfen bekleyin...")

if __name__ == "__main__":
    main()
