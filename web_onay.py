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

# --- MOBİL VE MASAÜSTÜ İÇİN ÖZEL CSS ---
st.markdown("""
<style>
    /* Genel Arka Plan */
    .stApp { background-color: #f8fafc; font-family: 'Inter', sans-serif; }

    /* Mobilde Menü Butonunu (>) Görünür ve Basılabilir Yap */
    button[data-testid="stSidebarCollapseButton"] {
        background-color: #3b82f6 !important;
        color: white !important;
        border-radius: 50% !important;
        top: 15px !important;
        left: 15px !important;
        width: 50px !important;
        height: 50px !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4) !important;
        z-index: 999999 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Header ve Footer Temizliği */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {height: 60px !important; background: transparent !important;}

    /* Hoşgeldin Kartı - Mobilde Taşma Yapmaz */
    .welcome-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 20px; border-radius: 16px; color: white; text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin-bottom: 20px;
        margin-top: 10px;
    }
    .welcome-card h1 { color: #ffffff !important; font-weight: 800; font-size: 22px !important; margin: 0;}
    
    /* Kart Tasarımları */
    .task-card {
        background: #ffffff; border-radius: 12px; padding: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); border-left: 5px solid #3b82f6;
        margin-bottom: 10px;
    }
    .task-completed { border-left-color: #10b981; background: #f0fdf4; }
    .task-title { font-size: 15px; font-weight: 700; color: #1e293b; line-height: 1.4; }
    
    .feed-card {
        background: #ffffff; padding: 12px; border-radius: 10px; margin-bottom: 8px;
        border-left: 4px solid #f59e0b; box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    .feed-ongoing { border-left-color: #3b82f6; }

    /* Yan Menü (Sidebar) Düzenlemeleri */
    section[data-testid="stSidebar"] { 
        background-color: #ffffff !important; 
        border-right: 1px solid #e2e8f0;
    }
    section[data-testid="stSidebar"] .st-emotion-cache-16idsys p {
        color: #1e293b !important; font-weight: 600 !important;
    }

    /* Kaydet Butonu */
    button[kind="primary"] {
        background: linear-gradient(to right, #11998e, #38ef7d) !important;
        color: white !important; font-weight: bold !important; border-radius: 12px !important;
        height: 50px !important; width: 100% !important; border: none !important;
    }

    /* Telefon Ekranları İçin İnce Ayarlar */
    @media (max-width: 768px) {
        .stApp { padding: 5px; }
        .welcome-card { margin-top: 50px; }
        .task-title { font-size: 14px; }
    }
</style>
""", unsafe_allow_html=True)

MOTIVASYON_BITEN = ["Müthişsin {isim}!", "Eline sağlık {isim}!", "Harikasın {isim}!"]
MOTIVASYON_DEVAM = ["Kolay gelsin {isim}!", "Başarılar {isim}!", "İyi çalışmalar {isim}!"]

def main():
    # 1. URL Parametresini Güvenli Oku
    token = st.query_params.get("id")

    if not token:
        st.markdown('<div class="welcome-card"><h1>FLU DİJİTAL</h1><p>Lütfen size iletilen özel linke tıklayın.</p></div>', unsafe_allow_html=True)
        st.info("Eğer linke tıkladıysanız ve bu mesajı görüyorsanız, linkin sonundaki ID kısmını kontrol edin.")
        st.stop()

    # 2. Veri Çekme (Hızlı ve Güvenli)
    try:
        resp = httpx.get(SUPABASE_URL, headers=HEADERS, timeout=10)
        all_tasks = resp.json()
        
        user_entry = [t for t in all_tasks if t.get("magic_token") == token]
        if not user_entry:
            st.warning("Geçersiz veya süresi dolmuş bir link.")
            st.stop()
        
        current_user = user_entry[0]["personel_ad"]
        today_str = datetime.now().strftime("%Y-%m-%d")

        # Filtreleme
        my_tasks_today = [t for t in all_tasks if t.get("personel_ad") == current_user and t.get("deadline", "").startswith(today_str)]
        radar_tasks_today = [t for t in all_tasks if t.get("deadline", "").startswith(today_str)]
        future_tasks = [t for t in all_tasks if t.get("deadline", "").split("T")[0] > today_str]
        future_tasks.sort(key=lambda x: x.get("deadline", ""))

    except:
        st.error("Bağlantı sağlanamadı. Lütfen sayfayı yenileyin.")
        st.stop()

    # --- ÜST PANEL ---
    st.markdown(f'<div class="welcome-card"><h1>Hoş Geldin, {current_user}! 👋</h1><p>{datetime.now().strftime("%d.%m.%Y")}</p></div>', unsafe_allow_html=True)

    my_total = len(my_tasks_today)
    my_done = sum(1 for t in my_tasks_today if t.get("durum") == "tamamlandi")
    prog = my_done / my_total if my_total > 0 else 0
    st.progress(prog)
    st.write(f"📊 **Hedef İlerleme Oranı:** %{int(prog*100)}")

    if st.session_state.get("success_msg"):
        st.success(st.session_state["success_msg"])
        st.balloons()
        del st.session_state["success_msg"]

    # --- YAN MENÜ ---
    with st.sidebar:
        st.markdown("### 💎 FLU DİJİTAL")
        st.write("---")
        tab = st.radio("Sekme Seçin:", ["📋 Yapılacaklar Listem", "🌐 Canlı Şirket Radarı", "📅 Gelecek Tarihli İşler"])
        st.write("---")
        st.caption("Menü kapalıysa sol üstteki mavi butona basın.")

    # --- İÇERİK ---
    if tab == "📋 Yapılacaklar Listem":
        st.subheader("📌 Bugünün Görevleri")
        if not my_tasks_today:
            st.info("Bugün için bekleyen görevin yok. Keyfini çıkar! ☕")
        else:
            for t in my_tasks_today:
                tid = t["id"]
                is_done = st.checkbox(" ", value=(t.get("durum") == "tamamlandi"), key=tid)
                c_class = "task-card task-completed" if is_done else "task-card"
                saat = t.get("deadline", "").split("T")[1][:5]
                t_title = f"<s>{t['is_tanimi']}</s> 🏆" if is_done else t['is_tanimi']
                n_html = f'<div class="task-note">📌 {t["notlar"]}</div>' if t.get("notlar") else ""
                st.markdown(f'<div class="{c_class}"><div class="task-title">{t_title}</div><small style="color:gray;">⏰ Hedef: {saat}</small>{n_html}</div>', unsafe_allow_html=True)
            
            st.write("---")
            if st.button("🚀 Değişiklikleri Kaydet", type="primary"):
                for t in my_tasks_today:
                    new_s = "tamamlandi" if st.session_state.get(t["id"]) else "bekliyor"
                    if t["durum"] != new_s:
                        httpx.patch(f"{SUPABASE_URL}?id=eq.{t['id']}", headers=HEADERS, json={"durum": new_s})
                st.session_state["success_msg"] = "Başarıyla güncellendi!"
                st.rerun()

    elif tab == "🌐 Canlı Şirket Radarı":
        st.subheader("📡 Ekip Akışı")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### 🏆 Şampiyonlar")
            done_today = [t for t in radar_tasks_today if t.get("durum") == "tamamlandi"]
            if not done_today: st.caption("Henüz biten iş yok.")
            for d in reversed(done_today):
                f_name = d['personel_ad'].split()[0]
                saat = d.get("deadline", "").split("T")[1][:5]
                motto = random.choice(MOTIVASYON_BITEN).format(isim=f_name)
                st.markdown(f'<div class="feed-card"><small style="color:gray;">⏰ {saat}</small><br><b>{d["personel_ad"]}</b><br><small>{d["is_tanimi"]}</small><br><b style="color:#d35400;">{motto}</b></div>', unsafe_allow_html=True)
        with c2:
            st.markdown("##### ⏳ Çalışanlar")
            on_today = [t for t in radar_tasks_today if t.get("durum") != "tamamlandi"]
            if not on_today: st.caption("Aktif bekleyen iş yok.")
            for o in on_today:
                f_name = o['personel_ad'].split()[0]
                saat = o.get("deadline", "").split("T")[1][:5]
                motto = random.choice(MOTIVASYON_DEVAM).format(isim=f_name)
                st.markdown(f'<div class="feed-card feed-ongoing"><small style="color:gray;">⏰ {saat}</small><br><b>{o["personel_ad"]}</b><br><small>{o["is_tanimi"]}</small><br><b style="color:#2563eb;">{motto}</b></div>', unsafe_allow_html=True)

    elif tab == "📅 Gelecek Tarihli İşler":
        st.subheader("📅 Gelecek Planları")
        if not future_tasks:
            st.info("Planlanmış gelecek iş bulunmuyor.")
        else:
            for ft in future_tasks:
                dv = datetime.strptime(ft['deadline'].split('T')[0], '%Y-%m-%d').strftime('%d.%m.%Y')
                st.markdown(f'<div class="task-card"><div class="task-title">{ft["is_tanimi"]}</div><small style="color:gray;">📅 {dv} | 👤 {ft["personel_ad"]}</small></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
