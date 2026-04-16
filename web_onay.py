import streamlit as st
import httpx
from datetime import datetime
import random

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="FlowDesk | Çalışan Portalı", 
    page_icon="💎", 
    layout="wide", # Kanban görünümü için geniş ekran
    initial_sidebar_state="collapsed" # Mobil donma sorunu için kapalı başlar
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

# --- FLOWDESK PREMIUM TASARIM (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    .stApp { background-color: #f5f6f8; font-family: 'Inter', sans-serif; }
    header {visibility: hidden;} .stDeployButton {display:none;}

    /* Sidebar Tasarımı */
    section[data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e2e8f0; }
    [data-testid="stSidebarNav"] span { color: #1e293b !important; font-weight: 600; }

    /* Üst Başlık Alanı */
    .header-area { display: flex; justify-content: space-between; align-items: center; padding: 20px 0; margin-bottom: 20px; }
    .header-title { font-size: 26px; font-weight: 700; color: #1e293b; }

    /* Kanban Sütun Başlıkları */
    .column-header { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; }
    .dot { width: 10px; height: 10px; border-radius: 50%; }
    .dot-todo { background-color: #1e293b; }
    .dot-ongoing { background-color: #2a62ff; }
    .column-title { font-size: 18px; font-weight: 700; color: #1e293b; }
    .task-count { background: #e2e8f0; padding: 2px 8px; border-radius: 10px; font-size: 12px; font-weight: 700; color: #64748b; }

    /* Görev Kartları */
    .task-card {
        background: #ffffff; border-radius: 12px; padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03); border: 1px solid #e2e8f0;
        margin-bottom: 15px; position: relative;
    }
    .task-tag { 
        font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 6px; 
        display: inline-block; margin-bottom: 10px; text-transform: uppercase;
    }
    /* Dinamik Etiket Renkleri */
    .tag-design { background: #fdecf3; color: #e94e96; }
    .tag-seo { background: #ebf7ff; color: #2664b7; }
    .tag-content { background: #ebfef6; color: #1e8e5d; }
    .tag-photo { background: #fff9ec; color: #d35400; }

    .task-title { font-size: 15px; font-weight: 600; color: #1e293b; margin-bottom: 15px; line-height: 1.4; }
    
    .task-footer { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f1f5f9; padding-top: 12px; }
    .task-date { font-size: 12px; color: #94a3b8; font-weight: 600; }
    .user-avatar { 
        width: 28px; height: 28px; background: #e0e1fe; color: #5365fd; 
        border-radius: 50%; display: flex; align-items: center; justify-content: center;
        font-size: 11px; font-weight: 700;
    }

    /* Kaydet Butonu - FlowDesk Mavi */
    div.stButton > button:first-child {
        background-color: #2a62ff !important; color: white !important;
        border-radius: 10px !important; border: none !important;
        font-weight: 700 !important; width: 100%; height: 45px;
    }
</style>
""", unsafe_allow_html=True)

# Motivasyon Mesajları
MOTIVASYON = ["Müthişsin!", "Harika gidiyorsun!", "Eline sağlık!", "İyi çalışmalar!"]

def main():
    token = st.query_params.get("id")
    if not token:
        st.error("Lütfen geçerli bir erişim linki kullanın.")
        st.stop()

    # VERİ ÇEKME
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(SUPABASE_URL, headers=HEADERS)
            data = r.json()
        
        user_row = [t for t in data if t.get("magic_token") == token]
        if not user_row: st.stop()
        
        user_name = user_row[0]["personel_ad"]
        today = datetime.now().strftime("%Y-%m-%d")

        # Filtreleme Mantığı
        my_tasks = [t for t in data if t.get("personel_ad") == user_name and t.get("deadline", "").startswith(today)]
        radar_tasks = [t for t in data if t.get("deadline", "").startswith(today)]
        future_tasks = [t for t in data if t.get("deadline", "").split("T")[0] > today]
    except:
        st.error("Sistem şu an meşgul. Lütfen Safari'deyseniz sayfayı yenileyin.")
        st.stop()

    # --- YAN MENÜ ---
    with st.sidebar:
        st.markdown("## 💎 FlowDesk")
        st.caption("Ajans Yönetim Platformu")
        st.write("---")
        menu = st.radio("MENÜ", ["📊 Görev Panosu", "🌐 Şirket Radarı", "📅 Gelecek İşler"])
        st.write("---")
        st.markdown(f"**Kullanıcı:** {user_name}")

    # --- ANA HEADER ---
    st.markdown(f'<div class="header-area"><div class="header-title">{menu}</div></div>', unsafe_allow_html=True)

    # 1. SEKME: GÖREV PANOSU (Kendi İşleri - Kanban Görünümü)
    if menu == "📊 Görev Panosu":
        todo = [t for t in my_tasks if t.get("durum") != "tamamlandi"]
        done = [t for t in my_tasks if t.get("durum") == "tamamlandi"]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f'<div class="column-header"><div class="dot dot-todo"></div><div class="column-title">Yapılacak</div><div class="task-count">{len(todo)}</div></div>', unsafe_allow_html=True)
            for t in todo:
                tag_class = random.choice(["design", "seo", "content", "photo"])
                saat = t.get("deadline", "").split("T")[1][:5]
                st.markdown(f"""
                <div class="task-card">
                    <div class="task-tag tag-{tag_class}">{tag_class}</div>
                    <div class="task-title">{t['is_tanimi']}</div>
                    <div class="task-footer">
                        <div class="task-date">⏰ {saat}</div>
                        <div class="user-avatar">{user_name[:2].upper()}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.checkbox("Tamamla", key=t['id'])

        with col2:
            st.markdown(f'<div class="column-header"><div class="dot dot-ongoing"></div><div class="column-title">Bitenler</div><div class="task-count">{len(done)}</div></div>', unsafe_allow_html=True)
            for t in done:
                st.markdown(f"""
                <div class="task-card" style="opacity: 0.7;">
                    <div class="task-tag tag-content">DONE</div>
                    <div class="task-title"><s>{t['is_tanimi']}</s></div>
                    <div class="task-footer">
                        <div class="task-date">✅ Tamamlandı</div>
                        <div class="user-avatar">{user_name[:2].upper()}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.write("---")
        if st.button("🚀 Değişiklikleri Sisteme İşle"):
            for t in my_tasks:
                new_status = "tamamlandi" if st.session_state.get(t['id']) else "bekliyor"
                if t['durum'] != new_status:
                    httpx.patch(f"{SUPABASE_URL}?id=eq.{t['id']}", headers=HEADERS, json={"durum": new_status})
            st.balloons()
            st.rerun()

    # 2. SEKME: ŞİRKET RADARI
    elif menu == "🌐 Şirket Radarı":
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### 🏆 Şampiyonlar")
            bitenler = [t for t in radar_tasks if t.get("durum") == "tamamlandi"]
            for b in bitenler:
                saat = b.get("deadline","").split("T")[1][:5]
                tarih = datetime.strptime(b.get("deadline","").split("T")[0], "%Y-%m-%d").strftime("%d.%m")
                st.markdown(f'<div class="task-card"><div class="task-date">📅 {tarih} | ⏰ {saat}</div><b>{b["personel_ad"]}</b><br><small>{b["is_tanimi"]}</small><br><div class="motto-text" style="color:#d35400; font-size:11px; font-weight:bold;">{random.choice(MOTIVASYON)}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown("##### ⏳ Sahada Ter Dökenler")
            devamlar = [t for t in radar_tasks if t.get("durum") != "tamamlandi"]
            for d in devamlar:
                saat = d.get("deadline","").split("T")[1][:5]
                tarih = datetime.strptime(d.get("deadline","").split("T")[0], "%Y-%m-%d").strftime("%d.%m")
                st.markdown(f'<div class="task-card" style="border-left-color:#2a62ff;"><div class="task-date">📅 {tarih} | ⏰ {saat}</div><b>{d["personel_ad"]}</b><br><small>{d["is_tanimi"]}</small></div>', unsafe_allow_html=True)

    # 3. SEKME: GELECEK İŞLER
    elif menu == "📅 Gelecek İşler":
        for ft in future_tasks:
            dv = datetime.strptime(ft['deadline'].split('T')[0], '%Y-%m-%d').strftime('%d.%m.%Y')
            saat = ft.get("deadline", "").split("T")[1][:5]
            st.markdown(f'<div class="task-card"><div class="task-date">📅 {dv} | ⏰ {saat} | 👤 {ft["personel_ad"]}</div><div class="task-title">{ft["is_tanimi"]}</div></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
