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

# --- ÖZEL TASARIM (KESİN MOBİL UYUMLU CSS) ---
st.markdown("""
<style>
    /* Temel Ayarlar */
    .stApp { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
    
    /* Menü Butonu ve Header */
    header[data-testid="stHeader"] { background-color: transparent !important; }
    button[data-testid="stSidebarCollapseButton"] {
        background-color: #1e293b !important;
        color: white !important;
        border-radius: 8px !important;
        margin: 10px !important;
    }

    /* Hoşgeldin Kartı */
    .welcome-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 25px; border-radius: 16px; color: white; text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin-bottom: 20px;
    }
    .welcome-card h1 { color: #ffffff !important; font-weight: 800; font-size: 24px !important; margin: 0;}
    
    /* Görev ve Radar Kartları */
    .task-card {
        background: #ffffff; border-radius: 12px; padding: 16px 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-left: 6px solid #3b82f6;
        margin-bottom: 12px;
    }
    .task-completed { border-left-color: #10b981; background: #f0fdf4; }
    .task-title { font-size: 16px; font-weight: 700; color: #1e293b; margin-bottom: 4px; }
    .card-meta { font-size: 12px; color: #64748b; font-weight: 600; margin-bottom: 8px; display: block; }
    
    /* Radar Özel */
    .radar-card {
        background: #ffffff; padding: 12px; border-radius: 10px; margin-bottom: 10px;
        border-left: 4px solid #f59e0b; box-shadow: 0 1px 5px rgba(0,0,0,0.05);
    }
    .radar-ongoing { border-left-color: #3b82f6; }
    .motto-text { color: #d35400; font-size: 11.5px; font-weight: bold; background: #fff3e0; padding: 3px 8px; border-radius: 4px; display: inline-block; margin-top: 5px;}
    .motto-ongoing { color: #2563eb; background: #eff6ff; }

    /* Not Alanı */
    .task-note { background: #fff8e1; padding: 10px; border-radius: 8px; font-size: 12.5px; color: #92400e; border: 1px solid #fde68a; margin-top: 10px; }
    
    /* Sidebar Yazıları */
    [data-testid="stSidebarNav"] span { color: #1e293b !important; font-weight: 600 !important; }
    section[data-testid="stSidebar"] { background-color: #ffffff !important; }

    /* Kaydet Butonu Tasarımı */
    div.stButton > button:first-child {
        background: linear-gradient(to right, #11998e, #38ef7d) !important;
        color: white !important; font-weight: bold !important; border: none !important;
        border-radius: 12px !important; padding: 12px 24px !important;
        width: 100% !important; box-shadow: 0 4px 15px rgba(46, 204, 113, 0.3) !important;
        font-size: 16px !important;
    }
</style>
""", unsafe_allow_html=True)

MOTIVASYON_BITEN = ["Müthişsin {isim}!", "Eline sağlık {isim}!", "Harikasın {isim}!"]
MOTIVASYON_DEVAM = ["Kolay gelsin {isim}!", "Başarılar {isim}!", "İyi çalışmalar {isim}!"]

def main():
    # 1. Giriş Kontrolü
    token = st.query_params.get("id")
    if not token:
        st.markdown('<div class="welcome-card"><h1>Giriş Yapılamadı</h1><p>Lütfen size özel gönderilen linki kullanın.</p></div>', unsafe_allow_html=True)
        st.stop()

    # 2. Veri Çekme
    try:
        resp = httpx.get(SUPABASE_URL, headers=HEADERS, timeout=10)
        all_tasks = resp.json()
        
        user_entry = [t for t in all_tasks if t.get("magic_token") == token]
        if not user_entry:
            st.error("Giriş anahtarı geçersiz.")
            st.stop()
        
        current_user = user_entry[0]["personel_ad"]
        today_str = datetime.now().strftime("%Y-%m-%d")

        # Filtreleme (Senin istediğin 3 altın kural)
        my_tasks_today = [t for t in all_tasks if t.get("personel_ad") == current_user and t.get("deadline", "").startswith(today_str)]
        radar_tasks_today = [t for t in all_tasks if t.get("deadline", "").startswith(today_str)]
        future_all_tasks = [t for t in all_tasks if t.get("deadline", "").split("T")[0] > today_str]
        future_all_tasks.sort(key=lambda x: x.get("deadline", ""))

    except:
        st.error("Veri bağlantısı kurulamadı. Sayfayı yenileyin.")
        st.stop()

    # --- ÜST PANEL ---
    st.markdown(f'<div class="welcome-card"><h1>Hoş Geldin, {current_user}! 👋</h1><p>FLU DİJİTAL | {datetime.now().strftime("%d.%m.%Y")}</p></div>', unsafe_allow_html=True)

    my_total = len(my_tasks_today)
    my_done = sum(1 for t in my_tasks_today if t.get("durum") == "tamamlandi")
    prog = my_done / my_total if my_total > 0 else 0
    st.progress(prog)
    st.write(f"📊 **Bugünkü İlerleme Durumun:** %{int(prog*100)}")

    if st.session_state.get("done_msg"):
        st.success(st.session_state["done_msg"])
        st.balloons()
        del st.session_state["done_msg"]

    st.write("---")

    # --- YAN MENÜ ---
    with st.sidebar:
        st.markdown("### 💎 FLU DİJİTAL")
        tab = st.radio("MENÜ", ["📋 Yapılacaklar Listem", "🌐 Canlı Şirket Radarı", "📅 Gelecek Tarihli İşler"])
        st.write("---")
        st.caption("Menü sol üstteki butondan yönetilebilir.")

    # --- İÇERİK SEKMELERİ ---

    # SEKME 1: Yapılacaklar Listem (Yalnızca Kendi İşleri)
    if tab == "📋 Yapılacaklar Listem":
        st.subheader("📌 Senin Bugünkü Görevlerin")
        if not my_tasks_today:
            st.info("Bugün için bekleyen bir görevin yok. ☕")
        else:
            for t in my_tasks_today:
                tid = t["id"]
                is_done = st.checkbox(" ", value=(t.get("durum") == "tamamlandi"), key=tid)
                c_class = "task-card task-completed" if is_done else "task-card"
                saat = t.get("deadline", "").split("T")[1][:5]
                t_title = f"<s>{t['is_tanimi']}</s> 🏆" if is_done else t['is_tanimi']
                n_html = f'<div class="task-note">📌 <b>Not:</b> {t["notlar"]}</div>' if t.get("notlar") else ""
                
                st.markdown(f"""
                <div class="{c_class}">
                    <span class="card-meta">⏰ Hedef Saat: {saat}</span>
                    <div class="task-title">{t_title}</div>
                    {n_html}
                </div>
                """, unsafe_allow_html=True)
            
            st.write("---")
            if st.button("🚀 Değişiklikleri Kaydet"):
                with st.spinner("Kaydediliyor..."):
                    for t in my_tasks_today:
                        new_s = "tamamlandi" if st.session_state.get(t["id"]) else "bekliyor"
                        if t["durum"] != new_s:
                            httpx.patch(f"{SUPABASE_URL}?id=eq.{t['id']}", headers=HEADERS, json={"durum": new_s})
                    st.session_state["done_msg"] = "Harika! Görevlerin başarıyla güncellendi."
                    st.rerun()

    # SEKME 2: Canlı Şirket Radarı (Herkesin Bugünkü İşleri)
    elif tab == "🌐 Canlı Şirket Radarı":
        st.subheader("📡 Bugün Ekipte Neler Oluyor?")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 🏆 Şampiyonlar")
            done_today = [t for t in radar_tasks_today if t.get("durum") == "tamamlandi"]
            if not done_today: st.caption("Henüz biten iş yok.")
            for d in reversed(done_today):
                f_name = d['personel_ad'].split()[0]
                tarih = datetime.strptime(d.get("deadline","").split("T")[0], "%Y-%m-%d").strftime("%d.%m")
                saat = d.get("deadline", "").split("T")[1][:5]
                motto = random.choice(MOTIVASYON_BITEN).format(isim=f_name)
                st.markdown(f"""
                <div class="radar-card">
                    <span class="card-meta">📅 {tarih} | ⏰ {saat}</span>
                    <b>{d['personel_ad']}</b><br>
                    <small>{d['is_tanimi']}</small><br>
                    <div class="motto-text">{motto}</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("##### ⏳ Devam Edenler")
            on_today = [t for t in radar_tasks_today if t.get("durum") != "tamamlandi"]
            if not on_today: st.caption("Aktif bekleyen iş yok.")
            for o in on_today:
                f_name = o['personel_ad'].split()[0]
                tarih = datetime.strptime(o.get("deadline","").split("T")[0], "%Y-%m-%d").strftime("%d.%m")
                saat = o.get("deadline", "").split("T")[1][:5]
                motto = random.choice(MOTIVASYON_DEVAM).format(isim=f_name)
                st.markdown(f"""
                <div class="radar-card radar-ongoing">
                    <span class="card-meta">📅 {tarih} | ⏰ {saat}</span>
                    <b>{o['personel_ad']}</b><br>
                    <small>{o['is_tanimi']}</small><br>
                    <div class="motto-text motto-ongoing">{motto}</div>
                </div>
                """, unsafe_allow_html=True)

    # SEKME 3: Gelecek İşler (Herkesin İleri Tarihli İşleri)
    elif tab == "📅 Gelecek Tarihli İşler":
        st.subheader("📅 Planlanan Gelecek İşler")
        if not future_all_tasks:
            st.info("İleri tarihli bir görev bulunmuyor.")
        else:
            for ft in future_all_tasks:
                dv = datetime.strptime(ft['deadline'].split('T')[0], '%Y-%m-%d').strftime('%d.%m.%Y')
                saat = ft.get("deadline", "").split("T")[1][:5]
                st.markdown(f"""
                <div class="task-card">
                    <span class="card-meta">📅 Tarih: {dv} | ⏰ Saat: {saat}</span>
                    <div class="task-title">{ft['is_tanimi']}</div>
                    <small style="color:#64748b;">👤 Personel: {ft['personel_ad']}</small>
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
