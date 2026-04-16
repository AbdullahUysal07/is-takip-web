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

# --- ÖZEL TASARIM (GÖRÜNÜRLÜK GARANTİLİ CSS) ---
st.markdown("""
<style>
    /* Genel Arka Plan */
    .stApp { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}

    /* Hoşgeldin Kartı */
    .welcome-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 30px; border-radius: 16px; color: white; text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin-bottom: 20px;
    }
    .welcome-card h1 { color: #ffffff !important; font-weight: 800; font-size: 28px; margin-bottom: 5px;}
    .welcome-card p { font-size: 16px; color: #94a3b8; }

    /* Görev Kartları */
    .task-card {
        background: #ffffff; border-radius: 12px; padding: 16px 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-left: 6px solid #3b82f6;
        margin-bottom: 12px;
    }
    .task-completed { border-left-color: #10b981; background: #f0fdf4; }
    .task-title { font-size: 17px; font-weight: 700; color: #1e293b; margin-bottom: 4px; }
    .task-meta { font-size: 13px; color: #64748b; font-weight: 600; }
    
    /* Radar Kartları */
    .feed-card {
        background: #ffffff; padding: 12px; border-radius: 10px; margin-bottom: 8px;
        border-left: 4px solid #f59e0b; box-shadow: 0 1px 5px rgba(0,0,0,0.05);
    }
    .feed-ongoing { border-left-color: #3b82f6; }
    
    /* Not Alanı */
    .task-note { background: #fffbeb; padding: 10px; border-radius: 8px; font-size: 12.5px; color: #92400e; border: 1px solid #fde68a; margin-top: 10px; }
    
    /* MENÜ YAZILARINI DÜZELTEN KRİTİK CSS */
    section[data-testid="stSidebar"] .st-emotion-cache-16idsys p { color: #1e293b !important; font-weight: 600 !important; }
    section[data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e2e8f0; }

    /* Progress Bar Etiketi */
    .progress-label { font-size: 14px; font-weight: 700; color: #475569; margin-bottom: 5px; display: block; }
</style>
""", unsafe_allow_html=True)

# Motivasyon Havuzu
MOTIVASYON_BITEN = ["Müthişsin {isim}!", "Eline sağlık {isim}!", "Gurur duyuyoruz {isim}!"]
MOTIVASYON_DEVAM = ["Kolay gelsin {isim}!", "Başarılar {isim}!", "İyi çalışmalar {isim}!"]

def main():
    # 1. Giriş Kontrolü
    query_params = st.query_params
    token = query_params.get("id")

    if not token:
        st.markdown('<div class="welcome-card"><h1>Bağlantı Hatası</h1><p>Lütfen yöneticinizin size ilettiği özel linki kullanın.</p></div>', unsafe_allow_html=True)
        st.stop()

    # 2. Veri Senkronizasyonu
    try:
        resp = httpx.get(SUPABASE_URL, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        all_tasks = resp.json()
        
        user_entry = [t for t in all_tasks if t.get("magic_token") == token]
        if not user_entry:
            st.error("Giriş anahtarı sistemde bulunamadı.")
            st.stop()
        
        current_user = user_entry[0]["personel_ad"]
        today_str = datetime.now().strftime("%Y-%m-%d")

        # Filtreleme Mantığı (İstediğin Kurallar)
        my_tasks_today = [t for t in all_tasks if t.get("personel_ad") == current_user and t.get("deadline", "").startswith(today_str)]
        radar_tasks_today = [t for t in all_tasks if t.get("deadline", "").startswith(today_str)]
        future_tasks = [t for t in all_tasks if t.get("deadline", "").split("T")[0] > today_str]
        future_tasks.sort(key=lambda x: x.get("deadline", ""))

    except Exception as e:
        st.error("Veri bağlantısı kurulamadı. Lütfen internetinizi kontrol edin.")
        st.stop()

    # 3. ÜST SABİT PANEL (Hoşgeldin ve İlerleme)
    st.markdown(f"""
        <div class="welcome-card">
            <h1>Hoş Geldin, {current_user}! 👋</h1>
            <p>FLU DİJİTAL | {datetime.now().strftime('%d.%m.%Y')}</p>
        </div>
    """, unsafe_allow_html=True)

    my_total = len(my_tasks_today)
    my_done = sum(1 for t in my_tasks_today if t.get("durum") == "tamamlandi")
    prog = my_done / my_total if my_total > 0 else 0
    
    st.markdown(f'<span class="progress-label">Günlük Hedef Tamamlanma Oranı: %{int(prog*100)}</span>', unsafe_allow_html=True)
    st.progress(prog)
    
    # Başarı Balonları
    if st.session_state.get("success_notif"):
        st.success(st.session_state.get("success_notif"))
        st.balloons()
        del st.session_state["success_notif"]

    st.write("---")

    # 4. SOL MENÜ (Navigasyon)
    with st.sidebar:
        st.markdown("### 💎 FLU DİJİTAL")
        st.write("Profesyonel İş Takip Paneli")
        tab = st.radio(
            "Gideceğiniz Sekme:",
            ["📋 Yapılacaklar Listem", "🌐 Canlı Şirket Radarı", "📅 Gelecek Tarihli İşler"],
            index=0
        )
        st.write("---")
        st.caption("v2.2 Güvenli Sürüm")

    # 5. SEKMELERİN İÇERİĞİ

    # --- SEKME 1: YAPILACAKLAR (Yalnızca Kendi İşleri) ---
    if tab == "📋 Yapılacaklar Listem":
        st.subheader("📌 Bugün Tamamlaman Gerekenler")
        if not my_tasks_today:
            st.info("Bugün için atanmış bir göreviniz bulunmuyor. Harika bir gün dileriz!")
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
                    <div class="task-title">{t_title}</div>
                    <div class="task-meta">⏰ Hedef Saat: {saat}</div>
                    {n_html}
                </div>
                """, unsafe_allow_html=True)
            
            st.write("")
            if st.button("🚀 Değişiklikleri Kaydet", type="primary", use_container_width=True):
                with st.spinner("Veriler işleniyor..."):
                    for t in my_tasks_today:
                        new_stat = "tamamlandi" if st.session_state.get(t["id"]) else "bekliyor"
                        if t["durum"] != new_stat:
                            httpx.patch(f"{SUPABASE_URL}?id=eq.{t['id']}", headers=HEADERS, json={"durum": new_stat})
                    st.session_state["success_notif"] = "Görevlerin başarıyla güncellendi!"
                    st.rerun()

    # --- SEKME 2: ŞİRKET RADARI (Herkesin İşleri) ---
    elif tab == "🌐 Canlı Şirket Radarı":
        st.subheader("📡 Bugün Ekipte Neler Oluyor?")
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("##### 🏆 Tamamlananlar")
            done_today = [t for t in radar_tasks_today if t.get("durum") == "tamamlandi"]
            if not done_today:
                st.caption("Henüz biten iş yok.")
            else:
                for d in reversed(done_today):
                    f_name = d['personel_ad'].split()[0]
                    motto = random.choice(MOTIVASYON_BITEN).format(isim=f_name)
                    st.markdown(f"""
                    <div class="feed-card">
                        <b>{d['personel_ad']}</b><br>
                        <span style="font-size:12px;">{d['is_tanimi'][:30]}...</span><br>
                        <small style="color:#d35400; font-weight:bold;">{motto}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
        with col2: # Önceki koddaki col2 hatası düzeltildi
            st.markdown("##### ⏳ Devam Edenler")
            ongoing_today = [t for t in radar_tasks_today if t.get("durum") != "tamamlandi"]
            if not ongoing_today:
                st.caption("Aktif bekleyen iş yok.")
            else:
                for o in ongoing_today:
                    f_name = o['personel_ad'].split()[0]
                    motto = random.choice(MOTIVASYON_DEVAM).format(isim=f_name)
                    st.markdown(f"""
                    <div class="feed-card feed-ongoing">
                        <b>{o['personel_ad']}</b><br>
                        <span style="font-size:12px;">{o['is_tanimi'][:30]}...</span><br>
                        <small style="color:#2563eb; font-weight:bold;">{motto}</small>
                    </div>
                    """, unsafe_allow_html=True)

    # --- SEKME 3: GELECEK İŞLER (Herkesin Gelecek İşleri) ---
    elif tab == "📅 Gelecek Tarihli İşler":
        st.subheader("🔮 İleri Tarihli Planlamalar")
        if not future_tasks:
            st.info("Gelecek tarihler için henüz bir görev ataması yapılmamış.")
        else:
            for ft in future_tasks:
                date_val = datetime.strptime(ft['deadline'].split('T')[0], '%Y-%m-%d').strftime('%d.%m.%Y')
                time_val = ft['deadline'].split('T')[1][:5]
                
                st.markdown(f"""
                <div class="task-card">
                    <div class="task-title">{ft['is_tanimi']}</div>
                    <div class="task-meta">📅 {date_val} | ⏰ {time_val} | 👤 {ft['personel_ad']}</div>
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
