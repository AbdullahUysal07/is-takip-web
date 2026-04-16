import streamlit as st
import httpx
from datetime import datetime
import time

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="FlowDesk | Çalışan Portalı", 
    page_icon="💎", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- VERİTABANI AYARLARI (SUPABASE) ---
SUPABASE_URL = "https://fxohhhqrhybbqqwqxejc.supabase.co/rest/v1/gorevler"
ANON_KEY = "sb_publishable_Gr83hViFqzpLLHW3Ib-iaQ_cIuQ3fe8"
HEADERS = {
    "apikey": ANON_KEY, 
    "Authorization": f"Bearer {ANON_KEY}", 
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- ÖZEL CSS (BAŞTAN ÇIKARICI ARAYÜZ) ---
st.markdown("""
<style>
    /* Ana Arka Plan ve Yazı Tipi */
    .stApp {
        background-color: #f4f7f6;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Üst Menü ve Alt Bilgiyi Gizle */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Hoşgeldin Kartı (Gradient) */
    .welcome-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 30px;
        border-radius: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        margin-bottom: 30px;
    }
    .welcome-card h1 { color: white !important; font-weight: 800; font-size: 32px; margin-bottom: 5px;}
    .welcome-card p { font-size: 18px; opacity: 0.9; }

    /* Görev Kartları */
    .task-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border-left: 6px solid #3498db;
        transition: transform 0.2s ease-in-out;
    }
    .task-card:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,0,0,0.1); }
    
    /* Tamamlanmış Görev Kartı */
    .task-completed {
        border-left: 6px solid #2ecc71;
        opacity: 0.7;
    }
    .task-title { font-size: 18px; font-weight: 700; color: #2c3e50; margin-bottom: 5px;}
    .task-time { font-size: 14px; color: #7f8c8d; font-weight: 600; margin-bottom: 10px;}
    .task-note { background-color: #fff3cd; padding: 10px; border-radius: 8px; font-size: 14px; color: #856404; border-left: 3px solid #ffeeba;}
</style>
""", unsafe_allow_html=True)

# --- FONKSİYONLAR ---
def update_task_status(task_id, is_checked):
    yeni_durum = "tamamlandi" if is_checked else "bekliyor"
    try:
        httpx.patch(
            f"{SUPABASE_URL}?id=eq.{task_id}", 
            headers=HEADERS, 
            json={"durum": yeni_durum}
        )
    except Exception as e:
        st.error("Bağlantı hatası oluştu.")

# --- ANA MANTIK ---
def main():
    # 1. Linkteki ID'yi (Token) Al
    query_params = st.query_params
    token = query_params.get("id")

    if not token:
        st.markdown('<div class="welcome-card"><h1>Görev Bulunamadı</h1><p>Lütfen yöneticinizin gönderdiği geçerli bir linke tıklayın.</p></div>', unsafe_allow_html=True)
        st.stop()

    # 2. Token'a ait ilk görevi bul (Personeli ve Tarihi öğrenmek için)
    with st.spinner('Görevleriniz yükleniyor...'):
        try:
            r = httpx.get(f"{SUPABASE_URL}?magic_token=eq.{token}", headers=HEADERS)
            ilk_gorev_list = r.json()
        except:
            st.error("Sunucuya bağlanılamadı.")
            st.stop()

    if not ilk_gorev_list:
        st.error("Bu link geçersiz veya görev silinmiş.")
        st.stop()

    ilk_gorev = ilk_gorev_list[0]
    personel = ilk_gorev["personel_ad"]
    tarih_tam = ilk_gorev["deadline"]
    tarih_gun = tarih_tam.split("T")[0] # Sadece YYYY-MM-DD kısmını al

    # 3. Aynı Personelin, Aynı Gündeki TÜM görevlerini çek
    try:
        r_tum = httpx.get(f"{SUPABASE_URL}?personel_ad=eq.{personel}&deadline=like.{tarih_gun}%", headers=HEADERS)
        tum_gorevler = r_tum.json()
    except:
        st.error("Tüm görevler çekilemedi.")
        st.stop()

    # İstatistikleri Hesapla
    toplam_gorev = len(tum_gorevler)
    tamamlanan = sum(1 for g in tum_gorevler if g.get("durum") == "tamamlandi")
    ilerleme = tamamlanan / toplam_gorev if toplam_gorev > 0 else 0

    # 4. ARAYÜZ (GÖRSEL ŞÖLEN)
    
    # Hoşgeldin Kartı
    tarih_formatli = datetime.strptime(tarih_gun, "%Y-%m-%d").strftime("%d.%m.%Y")
    st.markdown(f"""
        <div class="welcome-card">
            <h1>Hoş Geldin, {personel}! 👋</h1>
            <p>📅 {tarih_formatli} Tarihli Çalışma Masan</p>
        </div>
    """, unsafe_allow_html=True)

    # İlerleme Çubuğu
    st.markdown(f"**Günlük İlerleme:** {tamamlanan} / {toplam_gorev} Görev Tamamlandı")
    st.progress(ilerleme)

    if ilerleme == 1.0:
        st.success("🎉 Harika iş çıkardın! Bugünlük tüm görevlerini tamamladın.")
        st.balloons() # %100 olunca balonlar uçar

    st.write("---")
    st.markdown("### 📋 Yapılacaklar Listen")

    # Görevleri Listele
    for g in tum_gorevler:
        task_id = g["id"]
        is_tamam = (g.get("durum") == "tamamlandi")
        saat = g["deadline"].split("T")[1][:5]
        yonetici_notu = g.get("notlar", "")

        # Kart Tasarımı
        css_class = "task-card task-completed" if is_tamam else "task-card"
        
        with st.container():
            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([0.1, 0.9])
            
            with col1:
                # Checkbox durumu değiştiğinde update_task_status fonksiyonunu tetikler
                st.checkbox(
                    " ", 
                    value=is_tamam, 
                    key=task_id, 
                    on_change=update_task_status, 
                    args=(task_id, not is_tamam) 
                )
            
            with col2:
                st.markdown(f'<div class="task-title">{g["is_tanimi"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="task-time">⏰ Hedef Saat: {saat}</div>', unsafe_allow_html=True)
                
                # Eğer yönetici masaüstü programından bir not girdiyse, burada şık bir uyarı olarak görünür
                if yonetici_notu:
                    st.markdown(f'<div class="task-note">📌 <b>Yönetici Notu:</b> {yonetici_notu}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
