import streamlit as st
import httpx
from datetime import datetime
import random

# --- SAYFA AYARLARI (Safari uyumu için optimize edildi) ---
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

# --- SAFARI VE MOBIL DOSTU CSS ---
st.markdown("""
<style>
    /* Genel Arka Plan - Safari için hafifletildi */
    .stApp { background-color: #f8fafc; }
    
    /* Hoşgeldin Kartı */
    .welcome-card {
        background: #1e293b;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 20px; border-radius: 12px; color: white; text-align: center;
        margin-bottom: 20px;
    }
    .welcome-card h1 { color: #ffffff !important; font-size: 20px !important; margin: 0; }
    
    /* Görev Kartları */
    .task-card {
        background: #ffffff; border-radius: 10px; padding: 15px;
        border-left: 5px solid #3b82f6; margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .task-completed { border-left-color: #10b981; background: #f0fdf4; }
    .task-title { font-size: 15px; font-weight: 700; color: #1e293b; }
    
    /* Radar ve Gelecek İşler Meta Veri */
    .meta-data { font-size: 11px; color: #64748b; font-weight: 700; margin-bottom: 4px; display: block; }
    
    /* Radar Kartları */
    .radar-box {
        background: #ffffff; padding: 10px; border-radius: 8px; margin-bottom: 8px;
        border-left: 4px solid #f59e0b; border-bottom: 1px solid #e2e8f0;
    }
    .radar-blue { border-left-color: #3b82f6; }
    .motto-box { font-size: 10px; font-weight: bold; padding: 2px 6px; border-radius: 4px; margin-top: 5px; display: inline-block; }

    /* Buton Tasarımı - KESİN GRADYAN */
    div.stButton > button:first-child {
        background: linear-gradient(to right, #11998e, #38ef7d) !important;
        color: white !important; font-weight: bold !important; border-radius: 10px !important;
        width: 100% !important; border: none !important; height: 48px;
        font-size: 16px !important; margin-top: 10px;
    }

    /* Sidebar Yazı Rengi */
    [data-testid="stSidebarNav"] span { color: #1e293b !important; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

MOTIVASYON_BITEN = ["Müthişsin {isim}!", "Eline sağlık!", "Harikasın!"]
MOTIVASYON_DEVAM = ["Kolay gelsin!", "Başarılar!", "Odaklan {isim}!"]

def main():
    token = st.query_params.get("id")
    if not token:
        st.error("Link hatası! Lütfen size iletilen linki tam kopyalayın.")
        st.stop()

    # VERİ ÇEKME (Safari dostu kısa timeout)
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(SUPABASE_URL, headers=HEADERS)
            data = r.json()
        
        user_data = [t for t in data if t.get("magic_token") == token]
        if not user_data:
            st.warning("Giriş başarısız.")
            st.stop()
        
        user = user_data[0]["personel_ad"]
        today = datetime.now().strftime("%Y-%m-%d")

        # Görünürlük Kuralları
        my_tasks = [t for t in data if t.get("personel_ad") == user and t.get("deadline", "").startswith(today)]
        radar_tasks = [t for t in data if t.get("deadline", "").startswith(today)]
        future_tasks = [t for t in data if t.get("deadline", "").split("T")[0] > today]
        future_tasks.sort(key=lambda x: x.get("deadline", ""))
    except:
        st.error("Bağlantı kurulamadı. Lütfen yenileyin.")
        st.stop()

    # --- ÜST PANEL ---
    st.markdown(f'<div class="welcome-card"><h1>Hoş Geldin, {user}! 👋</h1></div>', unsafe_allow_html=True)

    done = sum(1 for t in my_tasks if t.get("durum") == "tamamlandi")
    total = len(my_tasks)
    prog = done / total if total > 0 else 0
    st.progress(prog)
    st.write(f"📊 **Bugünkü Hedef İlerlemen:** %{int(prog*100)}")

    if st.session_state.get("saved"):
        st.success("Başarıyla Kaydedildi! 🎉")
        st.balloons()
        del st.session_state["saved"]

    # --- MENÜ ---
    with st.sidebar:
        st.markdown("### 🧭 Menü")
        tab = st.radio("SEKMELER", ["📋 Yapılacaklar", "🌐 Şirket Radarı", "📅 Gelecek İşler"])

    # --- İÇERİK ---

    # 1. SEKME: YAPILACAKLAR (Kendi İşlerim)
    if tab == "📋 Yapılacaklar":
        st.subheader("📌 Senin Görevlerin")
        if not my_tasks:
            st.info("Bugün için atanmış işin bulunmuyor.")
        else:
            for t in my_tasks:
                tid = t["id"]
                is_done = st.checkbox(" ", value=(t.get("durum") == "tamamlandi"), key=tid)
                c_class = "task-card task-completed" if is_done else "task-card"
                saat = t.get("deadline", "").split("T")[1][:5]
                t_title = f"<s>{t['is_tanimi']}</s>" if is_done else t['is_tanimi']
                
                st.markdown(f"""
                <div class="{c_class}">
                    <span class="meta-data">⏰ Hedef Saat: {saat}</span>
                    <div class="task-title">{t_title}</div>
                    {'<div class="task-note">📌 ' + t["notlar"] + '</div>' if t.get("notlar") else ""}
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("🚀 Değişiklikleri Kaydet"):
                for t in my_tasks:
                    ns = "tamamlandi" if st.session_state.get(t["id"]) else "bekliyor"
                    if t["durum"] != ns:
                        httpx.patch(f"{SUPABASE_URL}?id=eq.{t['id']}", headers=HEADERS, json={"durum": ns})
                st.session_state["saved"] = True
                st.rerun()

    # 2. SEKME: ŞİRKET RADARI (Herkesin İşleri + Tarih/Saat)
    elif tab == "🌐 Şirket Radarı":
        st.subheader("📡 Ekip Akışı")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### 🏆 Şampiyonlar")
            bitenler = [t for t in radar_tasks if t.get("durum") == "tamamlandi"]
            for d in reversed(bitenler):
                saat = d.get("deadline","").split("T")[1][:5]
                tarih = datetime.strptime(d.get("deadline","").split("T")[0], "%Y-%m-%d").strftime("%d.%m")
                motto = random.choice(MOTIVASYON_BITEN).format(isim=d['personel_ad'].split()[0])
                st.markdown(f"""
                <div class="radar-box">
                    <span class="meta-data">📅 {tarih} | ⏰ {saat}</span>
                    <b>{d["personel_ad"]}</b><br>
                    <small>{d["is_tanimi"]}</small><br>
                    <div class="motto-box" style="color:#d35400; background:#fff3e0;">{motto}</div>
                </div>
                """, unsafe_allow_html=True)
        with c2:
            st.markdown("##### ⏳ Çalışanlar")
            devamlar = [t for t in radar_tasks if t.get("durum") != "tamamlandi"]
            for o in devamlar:
                saat = o.get("deadline","").split("T")[1][:5]
                tarih = datetime.strptime(o.get("deadline","").split("T")[0], "%Y-%m-%d").strftime("%d.%m")
                motto = random.choice(MOTIVASYON_DEVAM).format(isim=o['personel_ad'].split()[0])
                st.markdown(f"""
                <div class="radar-box radar-blue">
                    <span class="meta-data">📅 {tarih} | ⏰ {saat}</span>
                    <b>{o["personel_ad"]}</b><br>
                    <small>{o["is_tanimi"]}</small><br>
                    <div class="motto-box" style="color:#2980b9; background:#ebf5fb;">{motto}</div>
                </div>
                """, unsafe_allow_html=True)

    # 3. SEKME: GELECEK İŞLER (Herkesin Planları)
    elif tab == "📅 Gelecek İşler":
        st.subheader("📅 İleri Tarihli Planlar")
        if not future_tasks:
            st.info("Planlanmış bir iş bulunmuyor.")
        else:
            for ft in future_tasks:
                dv = datetime.strptime(ft['deadline'].split('T')[0], '%Y-%m-%d').strftime('%d.%m.%Y')
                saat = ft.get("deadline", "").split("T")[1][:5]
                st.markdown(f"""
                <div class="task-card">
                    <span class="meta-data">📅 {dv} | ⏰ {saat} | 👤 {ft["personel_ad"]}</span>
                    <div class="task-title">{ft["is_tanimi"]}</div>
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
