import streamlit as st
import httpx
from datetime import datetime
import random

# --- SAYFA AYARLARI (Mobil donma sorunu için collapsed ve auto kullanıldı) ---
st.set_page_config(
    page_title="FLU DİJİTAL | Portal", 
    page_icon="💎", 
    layout="centered",
    initial_sidebar_state="collapsed"
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

# --- MOBİL STABİLİTE CSS (Sade ve Güçlü) ---
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
    
    /* Hoşgeldin Kartı */
    .welcome-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 20px; border-radius: 12px; color: white; text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 20px;
    }
    .welcome-card h1 { color: #ffffff !important; font-size: 22px !important; margin: 0; }
    
    /* Görev Kartları */
    .task-card {
        background: #ffffff; border-radius: 10px; padding: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); border-left: 5px solid #3b82f6;
        margin-bottom: 10px;
    }
    .task-completed { border-left-color: #10b981; background: #f0fdf4; }
    .task-title { font-size: 15px; font-weight: 700; color: #1e293b; margin-bottom: 3px; }
    
    /* Radar Kart Bilgileri (Tarih/Saat) */
    .meta-info { font-size: 11px; color: #64748b; font-weight: 700; margin-bottom: 5px; display: block; }
    
    /* Radar Özel Kartlar */
    .radar-box {
        background: #ffffff; padding: 12px; border-radius: 8px; margin-bottom: 8px;
        border-left: 4px solid #f59e0b; border-bottom: 1px solid #e2e8f0;
    }
    .radar-blue { border-left-color: #3b82f6; }
    .motto { font-size: 11px; font-weight: bold; padding: 3px 6px; border-radius: 4px; margin-top: 5px; display: inline-block; }

    /* Buton */
    div.stButton > button:first-child {
        background: linear-gradient(to right, #11998e, #38ef7d) !important;
        color: white !important; font-weight: bold !important; border-radius: 10px !important;
        width: 100% !important; border: none !important; height: 45px;
    }

    /* Gizli Sidebar Yazı Rengi */
    [data-testid="stSidebarNav"] span { color: #1e293b !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

MOTIVASYON_BITEN = ["Müthişsin {isim}!", "Eline sağlık!", "Harikasın!"]
MOTIVASYON_DEVAM = ["Kolay gelsin!", "Başarılar!", "İyi çalışmalar!"]

def main():
    # URL Parametresi
    token = st.query_params.get("id")
    if not token:
        st.warning("Lütfen geçerli bir bağlantı ile giriş yapın.")
        st.stop()

    # Veri Çekme
    try:
        with httpx.Client(timeout=15.0) as client:
            r = client.get(SUPABASE_URL, headers=HEADERS)
            data = r.json()
        
        user_data = [t for t in data if t.get("magic_token") == token]
        if not user_data:
            st.error("Bağlantı geçersiz.")
            st.stop()
        
        user = user_data[0]["personel_ad"]
        today = datetime.now().strftime("%Y-%m-%d")

        # Filtreleme
        my_tasks = [t for t in data if t.get("personel_ad") == user and t.get("deadline", "").startswith(today)]
        radar_tasks = [t for t in data if t.get("deadline", "").startswith(today)]
        future_tasks = [t for t in data if t.get("deadline", "").split("T")[0] > today]
        future_tasks.sort(key=lambda x: x.get("deadline", ""))
    except:
        st.error("Veri alınamadı, lütfen sayfayı yenileyin.")
        st.stop()

    # --- ÜST PANEL ---
    st.markdown(f'<div class="welcome-card"><h1>Hoş Geldin, {user}! 👋</h1></div>', unsafe_allow_html=True)

    done = sum(1 for t in my_tasks if t.get("durum") == "tamamlandi")
    total = len(my_tasks)
    prog = done / total if total > 0 else 0
    st.progress(prog)
    st.write(f"📊 **İlerleme:** %{int(prog*100)}")

    if st.session_state.get("saved"):
        st.success("Kaydedildi!")
        st.balloons()
        del st.session_state["saved"]

    # --- MENÜ ---
    with st.sidebar:
        st.markdown("### 💎 FLU DİJİTAL")
        tab = st.radio("SEKMELER", ["📋 Yapılacaklar", "🌐 Şirket Radarı", "📅 Gelecek İşler"])

    # --- İÇERİK ---
    if tab == "📋 Yapılacaklar":
        st.subheader("Bugünün Görevleri")
        if not my_tasks:
            st.info("Bugün görevin yok.")
        else:
            for t in my_tasks:
                tid = t["id"]
                is_done = st.checkbox(" ", value=(t.get("durum") == "tamamlandi"), key=tid)
                c_class = "task-card task-completed" if is_done else "task-card"
                saat = t.get("deadline", "").split("T")[1][:5]
                t_title = f"<s>{t['is_tanimi']}</s>" if is_done else t['is_tanimi']
                st.markdown(f'<div class="{c_class}"><span class="meta-info">⏰ Hedef: {saat}</span><div class="task-title">{t_title}</div></div>', unsafe_allow_html=True)
            
            if st.button("🚀 Değişiklikleri Kaydet"):
                for t in my_tasks:
                    ns = "tamamlandi" if st.session_state.get(t["id"]) else "bekliyor"
                    if t["durum"] != ns:
                        httpx.patch(f"{SUPABASE_URL}?id=eq.{t['id']}", headers=HEADERS, json={"durum": ns})
                st.session_state["saved"] = True
                st.rerun()

    elif tab == "🌐 Şirket Radarı":
        st.subheader("Ekip Akışı")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### 🏆 Şampiyonlar")
            bitenler = [t for t in radar_tasks if t.get("durum") == "tamamlandi"]
            for d in reversed(bitenler):
                saat = d.get("deadline","").split("T")[1][:5]
                tarih = datetime.strptime(d.get("deadline","").split("T")[0], "%Y-%m-%d").strftime("%d.%m")
                st.markdown(f'<div class="radar-box"><span class="meta-info">📅 {tarih} | ⏰ {saat}</span><b>{d["personel_ad"]}</b><br><small>{d["is_tanimi"]}</small></div>', unsafe_allow_html=True)
        with c2:
            st.markdown("##### ⏳ Çalışanlar")
            devamlar = [t for t in radar_tasks if t.get("durum") != "tamamlandi"]
            for o in devamlar:
                saat = o.get("deadline","").split("T")[1][:5]
                tarih = datetime.strptime(o.get("deadline","").split("T")[0], "%Y-%m-%d").strftime("%d.%m")
                st.markdown(f'<div class="radar-box radar-blue"><span class="meta-info">📅 {tarih} | ⏰ {saat}</span><b>{o["personel_ad"]}</b><br><small>{o["is_tanimi"]}</small></div>', unsafe_allow_html=True)

    elif tab == "📅 Gelecek İşler":
        st.subheader("İleri Tarihli Planlar")
        for ft in future_tasks:
            dv = datetime.strptime(ft['deadline'].split('T')[0], '%Y-%m-%d').strftime('%d.%m.%Y')
            st.markdown(f'<div class="task-card"><span class="meta-info">📅 {dv} | 👤 {ft["personel_ad"]}</span><div class="task-title">{ft["is_tanimi"]}</div></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
