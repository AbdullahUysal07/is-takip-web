import streamlit as st
import httpx
from datetime import datetime
import random

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="FLU DİJİTAL | Çalışan Portalı", 
    page_icon="💎", 
    layout="centered",
    initial_sidebar_state="auto" # Mobil cihazlarda daha akıllı davranması için
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

# --- ÖZEL TASARIM (MOBİL UYUMLU CSS) ---
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}

    /* Hoşgeldin Kartı */
    .welcome-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 25px; border-radius: 16px; color: white; text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin-bottom: 20px;
    }
    .welcome-card h1 { color: #ffffff !important; font-weight: 800; font-size: 24px; margin-bottom: 5px;}
    
    /* Görev Kartları */
    .task-card {
        background: #ffffff; border-radius: 12px; padding: 16px 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-left: 6px solid #3b82f6;
        margin-bottom: 12px;
    }
    .task-completed { border-left-color: #10b981; background: #f0fdf4; }
    .task-title { font-size: 16px; font-weight: 700; color: #1e293b; margin-bottom: 4px; }
    
    /* Radar Kartları (Tarih/Saatli) */
    .feed-card {
        background: #ffffff; padding: 12px; border-radius: 10px; margin-bottom: 10px;
        border-left: 4px solid #f59e0b; box-shadow: 0 1px 5px rgba(0,0,0,0.05);
    }
    .feed-ongoing { border-left-color: #3b82f6; }
    .feed-time-info { font-size: 11px; color: #64748b; font-weight: bold; margin-bottom: 5px; display: block;}
    
    /* Yan Menü (Sidebar) Yazı Ayarları */
    [data-testid="stSidebarNav"] span { color: #1e293b !important; font-weight: 600 !important; }
    section[data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e2e8f0; }

    /* Buton Tasarımı */
    button[kind="primary"] {
        background: linear-gradient(to right, #11998e, #38ef7d) !important;
        color: white !important; font-weight: bold !important; border-radius: 12px !important;
        padding: 10px 20px !important; width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

MOTIVASYON_BITEN = ["Müthişsin {isim}!", "Eline sağlık {isim}!", "Harikasın {isim}!"]
MOTIVASYON_DEVAM = ["Kolay gelsin {isim}!", "Başarılar {isim}!", "İyi çalışmalar {isim}!"]

def main():
    query_params = st.query_params
    token = query_params.get("id")

    if not token:
        st.markdown('<div class="welcome-card"><h1>Bağlantı Hatası</h1><p>Lütfen yöneticinizin size verdiği linkle girin.</p></div>', unsafe_allow_html=True)
        st.stop()

    # VERİ ÇEKME
    try:
        resp = httpx.get(SUPABASE_URL, headers=HEADERS, timeout=10)
        all_tasks = resp.json()
        
        user_entry = [t for t in all_tasks if t.get("magic_token") == token]
        if not user_entry:
            st.error("Giriş anahtarı geçersiz.")
            st.stop()
        
        current_user = user_entry[0]["personel_ad"]
        today_str = datetime.now().strftime("%Y-%m-%d")

        # Filtreleme
        my_tasks_today = [t for t in all_tasks if t.get("personel_ad") == current_user and t.get("deadline", "").startswith(today_str)]
        radar_tasks_today = [t for t in all_tasks if t.get("deadline", "").startswith(today_str)]
        future_tasks = [t for t in all_tasks if t.get("deadline", "").split("T")[0] > today_str]
        future_tasks.sort(key=lambda x: x.get("deadline", ""))

    except Exception as e:
        st.error("Sistem şu an meşgul, lütfen sayfayı yenileyin.")
        st.stop()

    # --- ÜST PANEL ---
    st.markdown(f'<div class="welcome-card"><h1>Hoş Geldin, {current_user}! 👋</h1><p>FLU DİJİTAL | {datetime.now().strftime("%d.%m.%Y")}</p></div>', unsafe_allow_html=True)

    my_total = len(my_tasks_today)
    my_done = sum(1 for t in my_tasks_today if t.get("durum") == "tamamlandi")
    prog = my_done / my_total if my_total > 0 else 0
    st.progress(prog)
    st.write(f"📊 **Bugünkü Hedef İlerlemen:** %{int(prog*100)}")

    if st.session_state.get("success_msg"):
        st.success(st.session_state["success_msg"])
        st.balloons()
        del st.session_state["success_msg"]

    st.write("---")

    # --- YAN MENÜ ---
    with st.sidebar:
        st.markdown("### 💎 FLU DİJİTAL")
        tab = st.radio("Menü Seçenekleri:", ["📋 Yapılacaklar Listem", "🌐 Canlı Şirket Radarı", "📅 Gelecek Tarihli İşler"])
        st.write("---")
        st.caption("Ekranda menü görünmüyorsa sol üstteki '>' işaretine basın.")

    # --- İÇERİK SEKMELERİ ---

    # 1. SEKME: YAPILACAKLAR
    if tab == "📋 Yapılacaklar Listem":
        st.subheader("📌 Bugün Tamamlaman Gerekenler")
        if not my_tasks_today:
            st.info("Bugün için bekleyen görevin yok. Dinlenebilirsin! ☕")
        else:
            for t in my_tasks_today:
                tid = t["id"]
                is_done = st.checkbox(" ", value=(t.get("durum") == "tamamlandi"), key=tid)
                c_class = "task-card task-completed" if is_done else "task-card"
                saat = t.get("deadline", "").split("T")[1][:5]
                t_title = f"<s>{t['is_tanimi']}</s> 🏆" if is_done else t['is_tanimi']
                n_html = f'<div class="task-note">📌 <b>Not:</b> {t["notlar"]}</div>' if t.get("notlar") else ""
                st.markdown(f'<div class="{c_class}"><div class="task-title">{t_title}</div><small>⏰ Hedef: {saat}</small>{n_html}</div>', unsafe_allow_html=True)
            
            st.write("---")
            if st.button("🚀 Değişiklikleri Kaydet", type="primary"):
                for t in my_tasks_today:
                    new_s = "tamamlandi" if st.session_state.get(t["id"]) else "bekliyor"
                    if t["durum"] != new_s:
                        httpx.patch(f"{SUPABASE_URL}?id=eq.{t['id']}", headers=HEADERS, json={"durum": new_s})
                st.session_state["success_msg"] = "Başarıyla kaydedildi!"
                st.rerun()

    # 2. SEKME: ŞİRKET RADARI (Tarih ve Saat Eklendi)
    elif tab == "🌐 Canlı Şirket Radarı":
        st.subheader("📡 Ekip Akış Radarı")
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("##### 🏆 Tamamlananlar")
            done_today = [t for t in radar_tasks_today if t.get("durum") == "tamamlandi"]
            for d in reversed(done_today):
                f_name = d['personel_ad'].split()[0]
                saat = d.get("deadline", "").split("T")[1][:5]
                tarih = datetime.strptime(d.get("deadline","").split("T")[0], "%Y-%m-%d").strftime("%d.%m")
                motto = random.choice(MOTIVASYON_BITEN).format(isim=f_name)
                st.markdown(f"""
                <div class="feed-card">
                    <span class="feed-time-info">📅 {tarih} | ⏰ {saat}</span>
                    <b>{d['personel_ad']}</b><br>
                    <small>{d['is_tanimi']}</small><br>
                    <b style="color:#d35400;">{motto}</b>
                </div>
                """, unsafe_allow_html=True)
        
        with c2:
            st.markdown("##### ⏳ Devam Edenler")
            on_today = [t for t in radar_tasks_today if t.get("durum") != "tamamlandi"]
            for o in on_today:
                f_name = o['personel_ad'].split()[0]
                saat = o.get("deadline", "").split("T")[1][:5]
                tarih = datetime.strptime(o.get("deadline","").split("T")[0], "%Y-%m-%d").strftime("%d.%m")
                motto = random.choice(MOTIVASYON_DEVAM).format(isim=f_name)
                st.markdown(f"""
                <div class="feed-card feed-ongoing">
                    <span class="feed-time-info">📅 {tarih} | ⏰ {saat}</span>
                    <b>{o['personel_ad']}</b><br>
                    <small>{o['is_tanimi']}</small><br>
                    <b style="color:#2563eb;">{motto}</b>
                </div>
                """, unsafe_allow_html=True)

    # 3. SEKME: GELECEK İŞLER (Kaydet Butonu Kaldırıldı)
    elif tab == "📅 Gelecek Tarihli İşler":
        st.subheader("📅 Gelecek Günlerin Planı")
        if not future_tasks:
            st.info("Gelecek günler için henüz görev atanmamış.")
        else:
            for ft in future_tasks:
                dv = datetime.strptime(ft['deadline'].split('T')[0], '%Y-%m-%d').strftime('%d.%m.%Y')
                st.markdown(f'<div class="task-card"><div class="task-title">{ft["is_tanimi"]}</div><small>📅 {dv} | 👤 {ft["personel_ad"]}</small></div>', unsafe_allow_html=True)
            st.caption("Not: Gelecek tarihli işleri bugüne gelmeden tamamlayamazsınız.")

if __name__ == "__main__":
    main()
