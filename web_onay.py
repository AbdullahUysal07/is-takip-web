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

# --- ÖZEL CSS (KUSURSUZ TASARIM) ---
st.markdown("""
<style>
    .stApp { background-color: #f4f7f6; font-family: 'Inter', sans-serif; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}

    .welcome-card {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        padding: 35px; border-radius: 20px; color: white; text-align: center;
        box-shadow: 0 15px 30px rgba(0,0,0,0.15); margin-bottom: 20px;
    }
    .welcome-card h1 { color: #ffffff !important; font-weight: 800; font-size: 34px; margin-bottom: 5px;}
    .welcome-card p { font-size: 18px; color: #d1d8e0; margin-top: 0;}

    div[data-testid="stCheckbox"] label span p { display: none; }
    div[data-testid="stCheckbox"] { padding-top: 15px; } 
    
    .task-card {
        background: #ffffff; border-radius: 12px; padding: 15px 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04); border-left: 6px solid #3498db;
        transition: all 0.3s ease; margin-bottom: 5px;
    }
    .task-card:hover { transform: translateX(5px); box-shadow: 0 6px 20px rgba(0,0,0,0.08); }
    .task-completed { border-left: 6px solid #2ecc71; background: #f9fdfa; opacity: 0.85; }
    
    .task-title { font-size: 18px; font-weight: 700; color: #2c3e50; margin-bottom: 5px; transition: all 0.2s;}
    .task-time { font-size: 13px; color: #7f8c8d; font-weight: 600; margin-bottom: 5px;}
    .task-note { background-color: #fff8e1; padding: 10px 12px; border-radius: 8px; font-size: 13px; color: #b78a00; border-left: 4px solid #ffc107; margin-top: 15px;}
    
    @keyframes blink { 0% {opacity:1;} 50% {opacity:0;} 100% {opacity:1;} }
    .blink { animation: blink 1s infinite; }

    button[kind="primary"] {
        background: linear-gradient(to right, #11998e, #38ef7d) !important;
        color: white !important; font-weight: bold !important; border: none !important;
        border-radius: 12px !important; padding: 12px !important;
        box-shadow: 0 4px 15px rgba(46, 204, 113, 0.4) !important; transition: all 0.3s ease !important;
        margin-top: 20px !important;
    }
    button[kind="primary"]:hover { transform: scale(1.02) !important; box-shadow: 0 6px 20px rgba(46, 204, 113, 0.6) !important; }
    
    /* Akış Kartları CSS */
    .feed-card {
        background-color: #ffffff; border-left: 4px solid #f39c12;
        padding: 12px; border-radius: 8px; margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .feed-name { font-size: 13px; color: #2c3e50; margin-bottom: 4px; }
    .feed-motto { color: #d35400; font-size: 12px; font-weight: bold; background: #fff3e0; padding: 4px 8px; border-radius: 4px; display: inline-block;}

    .feed-card-ongoing {
        background-color: #ffffff; border-left: 4px solid #3498db;
        padding: 12px; border-radius: 8px; margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .feed-motto-ongoing { color: #2980b9; font-size: 12px; font-weight: bold; background: #ebf5fb; padding: 4px 8px; border-radius: 4px; display: inline-block;}

    .scroll-container { max-height: 400px; overflow-y: auto; padding-right: 10px; }
    .scroll-container::-webkit-scrollbar { width: 6px; }
    .scroll-container::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 4px; }
    .scroll-container::-webkit-scrollbar-thumb { background: #c1c1c1; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

MOTIVASYON_BITEN = [
    "🎉 Harika iş çıkardın {isim}, iyi ki bizimlesin!",
    "🚀 Eline sağlık {isim}, hızına yetişemiyoruz!",
    "👏 Muhteşem bir performans {isim}, tebrikler!",
    "🏆 Bugünün şampiyonlarından biri de sensin {isim}!"
]

MOTIVASYON_DEVAM = [
    "💪 Kolay gelsin {isim}!",
    "🎯 Odaklanma zamanı {isim}, başarılar!",
    "⚡ Tempon harika {isim}, kolay gelsin!",
    "☕ Kahveni al ve harikalar yarat {isim}!"
]

def main():
    query_params = st.query_params
    token = query_params.get("id")

    if not token:
        st.markdown('<div class="welcome-card"><h1>Görev Bulunamadı</h1><p>Lütfen yöneticinizin gönderdiği geçerli bir linke tıklayın.</p></div>', unsafe_allow_html=True)
        st.stop()

    with st.spinner('Verileriniz senkronize ediliyor...'):
        try:
            r = httpx.get(SUPABASE_URL, headers=HEADERS, params={"magic_token": f"eq.{token}"})
            r.raise_for_status()
            ilk_gorev_list = r.json()
        except Exception as e:
            st.error("Veritabanına bağlanılamadı.")
            st.stop()

    if not ilk_gorev_list:
        st.error("Bu link geçersiz veya görev yöneticiniz tarafından silinmiş.")
        st.stop()

    ilk_gorev = ilk_gorev_list[0]
    personel = ilk_gorev["personel_ad"]
    tarih_gun = datetime.now().strftime("%Y-%m-%d")

    # VERİ ÇEKME İŞLEMLERİ
    try:
        r_tum = httpx.get(SUPABASE_URL, headers=HEADERS, params={"personel_ad": f"eq.{personel}"})
        tum_gorevler_ham = r_tum.json()
        
        bugunun_gorevleri = [g for g in tum_gorevler_ham if g.get("deadline", "").startswith(tarih_gun)]
        gelecek_gorevler = [g for g in tum_gorevler_ham if g.get("deadline", "").split("T")[0] > tarih_gun]
        gelecek_gorevler.sort(key=lambda x: x["deadline"])

        r_sirket = httpx.get(SUPABASE_URL, headers=HEADERS, params={"deadline": f"like.{tarih_gun}%"})
        sirket_gunluk = r_sirket.json()
        sirket_biten_gorevler = [g for g in sirket_gunluk if g.get("durum") == "tamamlandi"]
        sirket_devam_eden_gorevler = [g for g in sirket_gunluk if g.get("durum") != "tamamlandi"]
    except Exception as e:
        st.error("Veriler alınırken bir sorun oluştu.")
        st.stop()

    # --- 1. SABİT HOŞGELDİN ALANI ---
    tarih_formatli = datetime.strptime(tarih_gun, "%Y-%m-%d").strftime("%d.%m.%Y")
    st.markdown(f"""
        <div class="welcome-card">
            <h1>Hoş Geldin, {personel}! 👋</h1>
            <p>📅 {tarih_formatli} | FLU DİJİTAL Portal</p>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.get('goster_tebrik', False):
        st.success("🎉 Tebrikler! Seçilen görevler tamamlandı ve Yöneticiye bilgi verildi.")
        st.balloons()
        st.session_state['goster_tebrik'] = False

    toplam_gorev = len(bugunun_gorevleri)
    tamamlanan = sum(1 for g in bugunun_gorevleri if g.get("durum") == "tamamlandi")
    ilerleme = tamamlanan / toplam_gorev if toplam_gorev > 0 else 0

    st.markdown(f"**Günlük Genel Durum:** Bugün atanan {toplam_gorev} görevin {tamamlanan} tanesi tamamlandı. (%{int(ilerleme*100)})")
    st.progress(ilerleme)
    st.write("---")

    # --- 2. SOL MENÜ ---
    with st.sidebar:
        st.markdown("### 🧭 Menü")
        st.write("")
        secim = st.radio(
            "Gideceğiniz sekmeyi seçin:",
            ["📋 Yapılacaklar Listen", "🌐 Canlı Şirket Radarı", "📅 Gelecek Tarihli İşler"]
        )
        st.write("---")
        st.markdown("<div style='text-align:center; color:#95a5a6; font-size:12px;'>FLU DİJİTAL © 2026</div>", unsafe_allow_html=True)

    # --- YARDIMCI FONKSİYON ---
    def gorevleri_ciz(gorev_listesi, liste_baslik, is_gelecek=False):
        st.markdown(f"### {liste_baslik}")
        st.write("")
        
        if not gorev_listesi:
            st.info("Bu listeye ait herhangi bir görev bulunmuyor. 🎉")
            return

        for g in gorev_listesi:
            task_id = g["id"]
            db_is_tamam = (g.get("durum") == "tamamlandi")
            is_checked = st.session_state.get(task_id, db_is_tamam)
            
            deadline_str = g.get("deadline", "")
            hedef_tarih_gun = deadline_str.split("T")[0]
            hedef_saat = deadline_str.split("T")[1][:5] if "T" in deadline_str else ""
            
            tarih_etiketi = f"📅 {datetime.strptime(hedef_tarih_gun, '%Y-%m-%d').strftime('%d.%m.%Y')} | " if is_gelecek else ""
            
            kalan = 0
            try:
                deadline_dt = datetime.strptime(deadline_str, "%Y-%m-%dT%H:%M:%S")
                simdi = datetime.now()
                kalan = (deadline_dt - simdi).total_seconds()
                
                if kalan > 0:
                    gun_fark = int(kalan // 86400)
                    kalan_saat = int((kalan % 86400) // 3600)
                    kalan_dk = int((kalan % 3600) // 60)
                    
                    if is_gelecek and gun_fark > 0:
                        zaman_metni = f"<b>⏳ Kalan: {gun_fark} Gün {kalan_saat} Saat</b>"
                        sure_yuzde = 0.1 
                    else:
                        zaman_metni = f"<b>⏳ Kalan: {kalan_saat} Saat {kalan_dk} Dakika</b>"
                        sure_yuzde = max(0.0, min(1.0, 1.0 - (kalan / 43200))) 
                else:
                    zaman_metni = "<span class='blink' style='color:#e74c3c; font-weight:bold;'>⚠️ Süresi Geçmiş Görev!</span>"
                    sure_yuzde = 1.0
            except:
                zaman_metni = "⏰ Süre Belirtilmedi"
                sure_yuzde = 0.0

            col1, col2 = st.columns([0.08, 0.92])
            with col1:
                st.checkbox(" ", value=db_is_tamam, key=task_id)
            
            with col2:
                yonetici_notu = g.get("notlar", "")
                not_html = f'<div class="task-note">📌 <b>Yönetici Notu:</b> {yonetici_notu}</div>' if yonetici_notu else ''
                
                bar_renk = "#2ecc71" if is_checked else ("#e74c3c" if kalan <= 0 else "#3498db")
                bar_html = f"""
                <div style="width: 100%; background-color: #ecf0f1; border-radius: 4px; height: 6px; margin-top: 10px; overflow: hidden;">
                    <div style="width: {100 if is_checked else (sure_yuzde * 100)}%; background-color: {bar_renk}; height: 100%; border-radius: 4px;"></div>
                </div>
                """

                # Hata yaratan blok düzeltildi. (Değişkenler metne aktarılıp markdown'a öyle basıldı)
                if is_checked:
                    kart_html = f"""
                    <div class="task-card task-completed">
                        <div class="task-title"><s style="color:#95a5a6;">{g['is_tanimi']}</s> &nbsp;🏆</div>
                        <div class="task-time">{tarih_etiketi}⏰ Hedef: {hedef_saat} | <b style="color:#2ecc71;">Görev Tamamlandı!</b></div>
                        {bar_html}
                        {not_html}
                    </div>
                    """
                    st.markdown(kart_html, unsafe_allow_html=True)
                else:
                    kart_html = f"""
                    <div class="task-card">
                        <div class="task-title">{g['is_tanimi']}</div>
                        <div class="task-time">{tarih_etiketi}⏰ Hedef: {hedef_saat} | {zaman_metni}</div>
                        {bar_html}
                        {not_html}
                    </div>
                    """
                    st.markdown(kart_html, unsafe_allow_html=True)
            st.write("")

    # --- 3. İÇERİK DEĞİŞİMİ ---
    if secim == "📋 Yapılacaklar Listen":
        gorevleri_ciz(bugunun_gorevleri, "Bugünün Görevleri")

    elif secim == "📅 Gelecek Tarihli İşler":
        gorevleri_ciz(gelecek_gorevler, "İleri Tarihli Görevlerin", is_gelecek=True)

    elif secim == "🌐 Canlı Şirket Radarı":
        st.markdown("### 🌐 Canlı Şirket Radarı")
        st.markdown("Tüm ekibin bugün üzerindeki çalışma akışı")
        st.write("")
        
        col_biten, col_devam = st.columns(2)
        
        with col_biten:
            st.markdown("##### 🏆 Şampiyonlar")
            if not sirket_biten_gorevler:
                st.info("Henüz görev bitiren yok. İlk sen ol!")
            else:
                html_biten = '<div class="scroll-container">'
                for bg in reversed(sirket_biten_gorevler): 
                    isim_tam = bg['personel_ad']
                    ilk_isim = isim_tam.split()[0]
                    motto = random.choice(MOTIVASYON_BITEN).format(isim=ilk_isim)
                    html_biten += f"""
                    <div class="feed-card">
                        <div class="feed-name"><b>{isim_tam}</b>, <i>{bg['is_tanimi'][:25]}...</i> işini tamamladı!</div>
                        <div class="feed-motto">{motto}</div>
                    </div>"""
                html_biten += '</div>'
                st.markdown(html_biten, unsafe_allow_html=True)

        with col_devam:
            st.markdown("##### ⏳ Sahada Ter Dökenler")
            if not sirket_devam_eden_gorevler:
                st.info("Şu an bekleyen görev yok! 🌟")
            else:
                html_devam = '<div class="scroll-container">'
                for dg in sirket_devam_eden_gorevler:
                    isim_tam = dg['personel_ad']
                    ilk_isim = isim_tam.split()[0]
                    motto = random.choice(MOTIVASYON_DEVAM).format(isim=ilk_isim)
                    html_devam += f"""
                    <div class="feed-card-ongoing">
                        <div class="feed-name"><b>{isim_tam}</b>, <i>{dg['is_tanimi'][:25]}...</i> için çalışıyor.</div>
                        <div class="feed-motto-ongoing">{motto}</div>
                    </div>"""
                html_devam += '</div>'
                st.markdown(html_devam, unsafe_allow_html=True)

    # --- TOPLU KAYDETME BUTONU ---
    if secim in ["📋 Yapılacaklar Listen", "📅 Gelecek Tarihli İşler"]:
        st.write("---")
        if st.button("🚀 Seçili Görevleri Tamamla ve Kaydet", use_container_width=True, type="primary"):
            with st.spinner("Sistem güncelleniyor, Yöneticiye bilgi veriliyor..."):
                tum_kaydedilecekler = bugunun_gorevleri + gelecek_gorevler
                for g in tum_kaydedilecekler:
                    task_id = g["id"]
                    db_status = g.get("durum")
                    ui_status = st.session_state.get(task_id, False)
                    yeni_durum = "tamamlandi" if ui_status else "bekliyor"
                    
                    if db_status != yeni_durum:
                        try:
                            httpx.patch(f"{SUPABASE_URL}?id=eq.{task_id}", headers=HEADERS, json={"durum": yeni_durum})
                        except: pass
                
                st.session_state['goster_tebrik'] = True
                st.rerun()

if __name__ == "__main__":
    main()
