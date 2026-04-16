import streamlit as st
import httpx
from datetime import datetime
import random

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="FlowDesk | Çalışan Portalı", 
    page_icon="💎", 
    layout="wide",
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

# --- PREMIUM TASARIM (KESİN MOBİL UYUMLU CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    .stApp { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
    
    /* Mobil Menü Butonu (Sol üstteki > işaretini görünür yap) */
    button[data-testid="stSidebarCollapseButton"] {
        background-color: #2a62ff !important;
        color: white !important;
        border-radius: 8px !important;
        top: 10px !important;
        left: 10px !important;
        z-index: 99999;
    }

    /* Header & Footer Gizle */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} .stDeployButton {display:none;}
    header { background: transparent !important; }

    /* Dashboard Hoşgeldin Kartı */
    .dashboard-hero {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 30px; border-radius: 20px; color: white; text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15); margin-bottom: 25px;
    }
    .dashboard-hero h1 { color: #ffffff !important; font-size: 28px !important; font-weight: 800; margin: 0; }
    .dashboard-hero p { color: #94a3b8; font-size: 16px; margin-top: 5px; }

    /* İstatistik Kartları */
    .stat-container { display: flex; gap: 15px; margin-bottom: 25px; flex-wrap: wrap; }
    .stat-card {
        background: white; padding: 20px; border-radius: 15px; flex: 1;
        min-width: 150px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0; text-align: center;
    }
    .stat-val { font-size: 24px; font-weight: 800; color: #2a62ff; }
    .stat-label { font-size: 12px; color: #64748b; font-weight: 700; text-transform: uppercase; }

    /* Kanban & Radar Kartları */
    .flow-card {
        background: #ffffff; border-radius: 12px; padding: 18px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04); border: 1px solid #e2e8f0;
        margin-bottom: 12px; border-left: 5px solid #2a62ff;
    }
    .card-tag { 
        font-size: 10px; font-weight: 800; padding: 3px 8px; border-radius: 5px; 
        text-transform: uppercase; margin-bottom: 10px; display: inline-block;
    }
    .tag-blue { background: #ebf7ff; color: #2664b7; }
    .tag-green { background: #ebfef6; color: #1e8e5d; }
    .tag-orange { background: #fff9ec; color: #d35400; }

    .card-title { font-size: 15px; font-weight: 700; color: #1e293b; line-height: 1.4; margin-bottom: 12px; }
    
    .card-footer { 
        display: flex; justify-content: space-between; align-items: center; 
        border-top: 1px solid #f1f5f9; padding-top: 10px; margin-top: 10px;
    }
    .card-meta { font-size: 11px; color: #94a3b8; font-weight: 700; }
    .avatar { 
        width: 26px; height: 26px; background: #e0e1fe; color: #5365fd; 
        border-radius: 50%; display: flex; align-items: center; justify-content: center;
        font-size: 10px; font-weight: 800;
    }

    /* Sidebar Stil */
    section[data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e2e8f0; }
    [data-testid="stSidebarNav"] span { color: #1e293b !important; font-weight: 700; }

    /* Kaydet Butonu */
    div.stButton > button:first-child {
        background-color: #2a62ff !important; color: white !important;
        border-radius: 10px !important; border: none !important;
        font-weight: 700 !important; width: 100%; height: 48px;
    }
</style>
""", unsafe_allow_html=True)

MOTIVASYON_BITEN = ["Müthişsin!", "Eline sağlık!", "Harika gidiyorsun!"]

def main():
    # 1. URL KONTROL
    token = st.query_params.get("id")
    if not token:
        st.markdown('<div class="dashboard-hero"><h1>FLU DİJİTAL</h1><p>Lütfen size özel link ile giriş yapın.</p></div>', unsafe_allow_html=True)
        st.stop()

    # 2. VERİ SENKRONİZASYONU
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(SUPABASE_URL, headers=HEADERS)
            data = r.json()
        
        user_row = [t for t in data if t.get("magic_token") == token]
        if not user_row: st.stop()
        
        user_name = user_row[0]["personel_ad"]
        today = datetime.now().strftime("%Y-%m-%d")

        # Gruplandırma
        my_today = [t for t in data if t.get("personel_ad") == user_name and t.get("deadline", "").startswith(today)]
        all_today = [t for t in data if t.get("deadline", "").startswith(today)]
        all_future = [t for t in data if t.get("deadline", "").split("T")[0] > today]
        all_future.sort(key=lambda x: x.get("deadline", ""))
    except:
        st.error("Bağlantı hatası. Lütfen sayfayı yenileyin.")
        st.stop()

    # --- SIDEBAR NAVİGASYON ---
    with st.sidebar:
        st.markdown("## 💎 FlowDesk")
        st.caption("Ajans Yönetim Platformu")
        st.write("---")
        menu = st.radio("MENÜ", ["📊 Dashboard", "📋 Görev Panosu", "🌐 Şirket Radarı", "📅 Gelecek İşler"])
        st.write("---")
        st.info(f"Oturum: {user_name}")

    # --- 1. DASHBOARD (GİRİŞ EKRANI) ---
    if menu == "📊 Dashboard":
        st.markdown(f"""
            <div class="dashboard-hero">
                <h1>Hoş Geldin, {user_name}! 👋</h1>
                <p>Bugün harika işler çıkarmaya hazır mısın?</p>
            </div>
        """, unsafe_allow_html=True)
        
        # İstatistikler
        done_count = sum(1 for t in my_today if t.get("durum") == "tamamlandi")
        total_count = len(my_today)
        remaining = total_count - done_count
        prog = done_count / total_count if total_count > 0 else 0
        
        st.markdown(f"""
            <div class="stat-container">
                <div class="stat-card"><div class="stat-val">{total_count}</div><div class="stat-label">Toplam İş</div></div>
                <div class="stat-card"><div class="stat-val">{done_count}</div><div class="stat-label">Tamamlanan</div></div>
                <div class="stat-card"><div class="stat-val">{remaining}</div><div class="stat-label">Bekleyen</div></div>
            </div>
        """, unsafe_allow_html=True)
        
        st.write(f"**Günlük Genel İş Durumu: %{int(prog*100)}**")
        st.progress(prog)

    # --- 2. GÖREV PANOSU (KENDİ İŞLERİ) ---
    elif menu == "📋 Görev Panosu":
        st.subheader("📌 Bugün Tamamlaman Gerekenler")
        todo = [t for t in my_today if t.get("durum") != "tamamlandi"]
        done = [t for t in my_today if t.get("durum") == "tamamlandi"]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### ⏳ Yapılacaklar")
            for t in todo:
                saat = t.get("deadline","").split("T")[1][:5]
                st.markdown(f"""
                    <div class="flow-card">
                        <div class="card-tag tag-blue">ACTIVE</div>
                        <div class="card-title">{t['is_tanimi']}</div>
                        <div class="card-footer">
                            <div class="card-meta">⏰ Hedef: {saat}</div>
                            <div class="avatar">{user_name[:2].upper()}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                st.checkbox("Tamamlandı olarak işaretle", key=t['id'])
        
        with col2:
            st.markdown("##### ✅ Bitenler")
            for t in done:
                st.markdown(f"""
                    <div class="flow-card" style="border-left-color:#10b981; opacity:0.8;">
                        <div class="card-tag tag-green">DONE</div>
                        <div class="card-title"><s>{t['is_tanimi']}</s></div>
                        <div class="card-footer">
                            <div class="card-meta">✨ Görev Tamamlandı</div>
                            <div class="avatar">{user_name[:2].upper()}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        st.write("---")
        if st.button("🚀 Değişiklikleri Kaydet"):
            for t in my_today:
                new_s = "tamamlandi" if st.session_state.get(t['id']) else "bekliyor"
                if t['durum'] != new_s:
                    httpx.patch(f"{SUPABASE_URL}?id=eq.{t['id']}", headers=HEADERS, json={"durum": new_s})
            st.balloons()
            st.rerun()

    # --- 3. ŞİRKET RADARI (HERKES + DETAYLAR) ---
    elif menu == "🌐 Şirket Radarı":
        st.subheader("📡 Ekip Akışı")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### 🏆 Şampiyonlar")
            bitenler = [t for t in all_today if t.get("durum") == "tamamlandi"]
            for b in reversed(bitenler):
                tarih = datetime.strptime(b.get("deadline","").split("T")[0], "%Y-%m-%d").strftime("%d.%m")
                saat = b.get("deadline","").split("T")[1][:5]
                st.markdown(f"""
                    <div class="flow-card" style="border-left-color:#f59e0b;">
                        <div class="card-meta">📅 {tarih} | ⏰ {saat}</div>
                        <div class="card-title" style="margin-top:5px;"><b>{b['personel_ad']}</b>: {b['is_tanimi']}</div>
                        <div class="card-footer" style="border:none; padding:0;">
                            <small style="color:#d35400; font-weight:bold;">{random.choice(MOTIVASYON_BITEN)}</small>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        with c2:
            st.markdown("##### ⏳ Çalışanlar")
            devamlar = [t for t in all_today if t.get("durum") != "tamamlandi"]
            for o in devamlar:
                tarih = datetime.strptime(o.get("deadline","").split("T")[0], "%Y-%m-%d").strftime("%d.%m")
                saat = o.get("deadline","").split("T")[1][:5]
                st.markdown(f"""
                    <div class="flow-card" style="border-left-color:#2a62ff;">
                        <div class="card-meta">📅 {tarih} | ⏰ {saat}</div>
                        <div class="card-title" style="margin-top:5px;"><b>{o['personel_ad']}</b>: {o['is_tanimi']}</div>
                    </div>
                """, unsafe_allow_html=True)

    # --- 4. GELECEK İŞLER ---
    elif menu == "📅 Gelecek İşler":
        st.subheader("📅 İleri Tarihli Planlar")
        for ft in all_future:
            dv = datetime.strptime(ft['deadline'].split('T')[0], '%Y-%m-%d').strftime('%d.%m.%Y')
            saat = ft.get("deadline", "").split("T")[1][:5]
            st.markdown(f"""
                <div class="flow-card">
                    <div class="card-tag tag-orange">FUTURE</div>
                    <div class="card-title">{ft['is_tanimi']}</div>
                    <div class="card-footer">
                        <div class="card-meta">📅 {dv} | ⏰ {saat} | 👤 {ft['personel_ad']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
