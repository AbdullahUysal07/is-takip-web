import streamlit as st
import httpx
from datetime import datetime

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
    /* Ana Arka Plan ve Temizleme */
    .stApp { background-color: #f8f9fa; font-family: 'Inter', sans-serif; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}

    /* Hoşgeldin Kartı (Premium Gradient) */
    .welcome-card {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        padding: 35px;
        border-radius: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 15px 30px rgba(0,0,0,0.15);
        margin-bottom: 30px;
    }
    .welcome-card h1 { color: #ffffff !important; font-weight: 800; font-size: 34px; margin-bottom: 5px;}
    .welcome-card p { font-size: 18px; color: #d1d8e0; margin-top: 0;}

    /* Streamlit varsayılan checkbox etiketini gizleme */
    div[data-testid="stCheckbox"] label span p { display: none; }
    
    /* Görev Kartları */
    .task-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.04);
        margin-bottom: 15px;
        border-left: 6px solid #3498db;
        transition: all 0.3s ease;
    }
    .task-card:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,0,0,0.1); }
    
    /* Tamamlanmış Görev Kartı */
    .task-completed { border-left: 6px solid #2ecc71; background: #fbfdfc; opacity: 0.9; }
    
    .task-title { font-size: 18px; font-weight: 700; color: #2c3e50; margin-bottom: 5px; transition: all 0.2s;}
    .task-time { font-size: 13px; color: #7f8c8d; font-weight: 600; margin-bottom: 8px;}
    .task-note { background-color: #fff8e1; padding: 12px; border-radius: 8px; font-size: 14px; color: #b78a00; border-left: 4px solid #ffc107; margin-top: 10px;}
    
    /* Modern Buton */
    button[kind="primary"] {
        background: linear-gradient(to right, #11998e, #38ef7d) !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px !important;
        box-shadow: 0 4px 15px rgba(46, 204, 113, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    button[kind="primary"]:hover { transform: scale(1.02) !important; }
</style>
""", unsafe_allow_html=True)

# --- ANA MANTIK ---
def main():
    query_params = st.query_params
    token = query_params.get("id")

    if not token:
        st.markdown('<div class="welcome-card"><h1>Görev Bulunamadı</h1><p>Lütfen yöneticinizin gönderdiği geçerli bir linke tıklayın.</p></div>', unsafe_allow_html=True)
        st.stop()

    with st.spinner('Çalışma masanız hazırlanıyor...'):
        try:
            r = httpx.get(SUPABASE_URL, headers=HEADERS, params={"magic_token": f"eq.{token}"})
            r.raise_for_status()
            ilk_gorev_list = r.json()
        except Exception as e:
            st.error(f"Veritabanına bağlanılamadı.")
            st.stop()

    if not ilk_gorev_list:
        st.error("Bu link geçersiz veya görev yöneticiniz tarafından silinmiş.")
        st.stop()

    ilk_gorev = ilk_gorev_list[0]
    personel = ilk_gorev["personel_ad"]
    tarih_tam = ilk_gorev["deadline"]
    tarih_gun = tarih_tam.split("T")[0] 

    try:
        r_tum = httpx.get(SUPABASE_URL, headers=HEADERS, params={"personel_ad": f"eq.{personel}"})
        r_tum.raise_for_status()
        tum_gorevler_ham = r_tum.json()
        tum_gorevler = [g for g in tum_gorevler_ham if g.get("deadline", "").startswith(tarih_gun)]
    except Exception as e:
        st.error(f"Görev listesi alınırken bir sorun oluştu. Lütfen sayfayı yenileyin.")
        st.stop()

    toplam_gorev = len(tum_gorevler)
    tamamlanan = sum(1 for g in tum_gorevler if g.get("durum") == "tamamlandi")
    ilerleme = tamamlanan / toplam_gorev if toplam_gorev > 0 else 0

    # --- ARAYÜZ (GÖRSEL ŞÖLEN) ---
    tarih_formatli = datetime.strptime(tarih_gun, "%Y-%m-%d").strftime("%d.%m.%Y")
    st.markdown(f"""
        <div class="welcome-card">
            <h1>Hoş Geldin, {personel}! 👋</h1>
            <p>📅 {tarih_formatli} Tarihli Çalışma Masan</p>
        </div>
    """, unsafe_allow_html=True)

    # Tebrik Mesajı Kontrolü (Butona basıldıktan sonra çalışır)
    if st.session_state.get('goster_tebrik', False):
        st.success("🎉 Tebrikler! Seçilen görevler tamamlandı ve Yöneticiye bilgi verildi.")
        st.balloons()
        st.session_state['goster_tebrik'] = False

    st.markdown(f"**Günlük İlerleme:** {tamamlanan} / {toplam_gorev} Görev Tamamlandı")
    st.progress(ilerleme)

    st.write("---")
    st.markdown("### 📋 Yapılacaklar Listen")

    # Görev Kartları Listeleme
    for g in tum_gorevler:
        task_id = g["id"]
        db_is_tamam = (g.get("durum") == "tamamlandi")
        
        # Ekrandaki anlık seçimi yakalar (Tıklandığı an görseli değiştirmek için)
        is_checked = st.session_state.get(task_id, db_is_tamam)
        
        css_class = "task-card task-completed" if is_checked else "task-card"
        
        with st.container():
            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            col1, col2 = st.columns([0.08, 0.92])
            
            with col1:
                st.checkbox(" ", value=db_is_tamam, key=task_id)
            
            with col2:
                # Kupa ve Üst Çizme Efekti
                if is_checked:
                    st.markdown(f'<div class="task-title"><s style="color:#95a5a6;">{g["is_tanimi"]}</s> &nbsp;🏆</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="task-title">{g["is_tanimi"]}</div>', unsafe_allow_html=True)
                
                saat = g["deadline"].split("T")[1][:5] if "T" in g.get("deadline", "") else "Belirtilmedi"
                st.markdown(f'<div class="task-time">⏰ Hedef Saat: {saat}</div>', unsafe_allow_html=True)
                
                yonetici_notu = g.get("notlar", "")
                if yonetici_notu:
                    st.markdown(f'<div class="task-note">📌 <b>Yönetici Notu:</b> {yonetici_notu}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

    # --- TOPLU KAYDETME BUTONU ---
    st.write("") 
    if st.button("🚀 Seçili Görevleri Tamamla ve Kaydet", use_container_width=True, type="primary"):
        with st.spinner("Sistem güncelleniyor, Yöneticiye bilgi veriliyor..."):
            for g in tum_gorevler:
                task_id = g["id"]
                db_status = g.get("durum")
                ui_status = st.session_state[task_id]
                
                yeni_durum = "tamamlandi" if ui_status else "bekliyor"
                
                # Sadece durumu değişenleri veritabanına yolla
                if db_status != yeni_durum:
                    try:
                        httpx.patch(f"{SUPABASE_URL}?id=eq.{task_id}", headers=HEADERS, json={"durum": yeni_durum})
                    except:
                        pass
            
            st.session_state['goster_tebrik'] = True
            st.rerun() # Ekranı yenile ve balonları uçur

if __name__ == "__main__":
    main()
