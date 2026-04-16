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

# --- ÖZEL TASARIM (CSS) ---
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}

    .welcome-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 30px; border-radius: 16px; color: white; text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin-bottom: 20px;
    }
    .welcome-card h1 { color: #ffffff !important; font-weight: 800; font-size: 28px; margin-bottom: 5px;}
    
    .task-card {
        background: #ffffff; border-radius: 12px; padding: 16px 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-left: 6px solid #3b82f6;
        margin-bottom: 12px;
    }
    .task-completed { border-left-color: #10b981; background: #f0fdf4; }
    .task-title { font-size: 17px; font-weight: 700; color: #1e293b; margin-bottom: 4px; }
    
    .feed-card {
        background: #ffffff; padding: 12px; border-radius: 10px; margin-bottom: 8px;
        border-left: 4px solid #f59e0b; box-shadow: 0 1px 5px rgba(0,0,0,0.05);
    }
    .feed-ongoing { border-left-color: #3b82f6; }
    .task-note { background: #fffbeb; padding: 10px; border-radius: 8px; font-size: 12.5px; color: #92400e; border: 1px solid #fde68a; margin-top: 10px; }
    
    /* Yan Menü Yazılarını Netleştiren CSS */
    [data-testid="stSidebarNav"] span { color: #1e293b !important; font-weight: 600 !important; }
    section[data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e2e8f0; }
    
    button[kind="primary"] {
        background: linear-gradient(to right, #11998e, #38ef7d) !important;
        color: white !important; font-weight: bold !important; border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

MOTIVASYON_BITEN = ["Müthişsin {isim}!", "Eline sağlık {isim}!", "Harikasın {isim}!"]
MOTIVASYON_DEVAM = ["Kolay gelsin {isim}!", "Başarılar {isim}!", "İyi çalışmalar {isim}!"]

def main():
    query_params = st.query_params
    token = query_params.get("id")

    if not token:
        st.markdown('<div class="welcome-card"><h1>Bağlantı Hatası</h1><p>Lütfen geçerli bir link kullanın.</p></div>', unsafe_allow_html=True)
        st.stop()

    try:
        resp = httpx.get(SUPABASE_URL, headers=HEADERS)
        all_tasks = resp.json()
        
        user_entry = [t for t in all_tasks if t.get("magic_token") == token]
        if not user_entry:
            st.error("Giriş anahtarı geçersiz.")
            st.stop()
        
        current_user = user_entry[0]["personel_ad"]
        today_str = datetime.now().strftime("%Y-%m-%d")

        # Görünürlük Filtreleri
        my_tasks_today = [t for t in all_tasks if t.get("personel_ad") == current_user and t.get("deadline", "").startswith(today_str)]
        radar_tasks_today = [t for t in all_tasks if t.get("deadline", "").startswith(today_str)]
        future_tasks = [t for t in all_tasks if t.get("deadline", "").split("T")[0] > today_str]
        future_tasks.sort(key=lambda x: x.get("deadline", ""))

    except:
        st.error("Veri bağlantı hatası.")
        st.stop()

    # --- ÜST SABİT PANEL ---
    st.markdown(f'<div class="welcome-card"><h1>Hoş Geldin, {current_user}! 👋</h1><p>FLU DİJİTAL Portal | {datetime.now().strftime("%d.%m.%Y")}</p></div>', unsafe_allow_html=True)

    my_total = len(my_tasks_today)
    my_done = sum(1 for t in my_tasks_today if t.get("durum") == "tamamlandi")
    prog = my_done / my_total if my_total > 0 else 0
    st.progress(prog)
    st.write(f"**Günlük Tamamlanma Oranın:** %{int(prog*100)}")

    if st.session_state.get("success_msg"):
        st.success(st.session_state["success_msg"])
        st.balloons()
        del st.session_state["success_msg"]

    st.write("---")

    # --- YAN MENÜ ---
    with st.sidebar:
        st.markdown("### 💎 FLU DİJİTAL")
        tab = st.radio("Sekme Seçin:", ["📋 Yapılacaklar Listem", "🌐 Canlı Şirket Radarı", "📅 Gelecek Tarihli İşler"])
        st.write("---")
        st.caption("v2.2 Güvenli Sürüm")

    # --- İÇERİK ---
    if tab == "📋 Yapılacaklar Listem":
        st.subheader("📌 Senin Bugünlük Görevlerin")
        if not my_tasks_today:
            st.info("Bugün için atanmış göreviniz bulunmuyor.")
        else:
            for t in my_tasks_today:
                tid = t["id"]
                is_done = st.checkbox(" ", value=(t.get("durum") == "tamamlandi"), key=tid)
                c_class = "task-card task-completed" if is_done else "task-card"
                saat = t.get("deadline", "").split("T")[1][:5]
                t_title = f"<s>{t['is_tanimi']}</s> 🏆" if is_done else t['is_tanimi']
                n_html = f'<div class="task-note">📌 <b>Yönetici Notu:</b> {t["notlar"]}</div>' if t.get("notlar") else ""
                st.markdown(f'<div class="{c_class}"><div class="task-title">{t_title}</div><small>⏰ Hedef: {saat}</small>{n_html}</div>', unsafe_allow_html=True)

    elif tab == "🌐 Canlı Şirket Radarı":
        st.subheader("📡 Ekipte Bugün Neler Oluyor?")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### 🏆 Tamamlananlar")
            done_today = [t for t in radar_tasks_today if t.get("durum") == "tamamlandi"]
            for d in reversed(done_today):
                m = random.choice(MOTIVASYON_BITEN).format(isim=d['personel_ad'].split()[0])
                st.markdown(f'<div class="feed-card"><b>{d["personel_ad"]}</b><br><small>{d["is_tanimi"][:30]}...</small><br><b style="color:#d35400;">{m}</b></div>', unsafe_allow_html=True)
        with col2:
            st.markdown("##### ⏳ Devam Edenler")
            on_today = [t for t in radar_tasks_today if t.get("durum") != "tamamlandi"]
            for o in on_today:
                m = random.choice(MOTIVASYON_DEVAM).format(isim=o['personel_ad'].split()[0])
                st.markdown(f'<div class="feed-card feed-ongoing"><b>{o["personel_ad"]}</b><br><small>{o["is_tanimi"][:30]}...</small><br><b style="color:#2563eb;">{m}</b></div>', unsafe_allow_html=True)

    elif tab == "📅 Gelecek Tarihli İşler":
        st.subheader("📅 Tüm Gelecek Planlamaları")
        if not future_tasks:
            st.info("İleri tarihli görev bulunmuyor.")
        else:
            for ft in future_tasks:
                dv = datetime.strptime(ft['deadline'].split('T')[0], '%Y-%m-%d').strftime('%d.%m.%Y')
                st.markdown(f'<div class="task-card"><div class="task-title">{ft["is_tanimi"]}</div><small>📅 {dv} | 👤 {ft["personel_ad"]}</small></div>', unsafe_allow_html=True)

    # --- KAYDET ---
    if tab in ["📋 Yapılacaklar Listem", "📅 Gelecek Tarihli İşler"]:
        st.write("---")
        if st.button("🚀 Değişiklikleri Kaydet", type="primary", use_container_width=True):
            for t in (my_tasks_today + future_tasks):
                new_s = "tamamlandi" if st.session_state.get(t["id"]) else "bekliyor"
                if t["durum"] != new_s:
                    httpx.patch(f"{SUPABASE_URL}?id=eq.{t['id']}", headers=HEADERS, json={"durum": new_s})
            st.session_state["success_msg"] = "Başarıyla kaydedildi!"
            st.rerun()

if __name__ == "__main__":
    main()
