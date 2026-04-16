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

# --- ÖZEL TASARIM (CSS) ---
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
    
    .task-card {
        background: #ffffff; border-radius: 12px; padding: 15px 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04); border-left: 6px solid #3498db;
        transition: all 0.3s ease; margin-bottom: 5px;
    }
    .task-completed { border-left: 6px solid #2ecc71; background: #f9fdfa; opacity: 0.85; }
    .task-title { font-size: 18px; font-weight: 700; color: #2c3e50; margin-bottom: 5px; }
    
    .feed-card {
        background-color: #ffffff; border-left: 4px solid #f39c12;
        padding: 12px; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .feed-card-ongoing {
        background-color: #ffffff; border-left: 4px solid #3498db;
        padding: 12px; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .scroll-container { max-height: 400px; overflow-y: auto; padding-right: 10px; }
    .task-note { background-color: #fff8e1; padding: 10px; border-radius: 8px; font-size: 13px; color: #b78a00; border-left: 4px solid #ffc107; margin-top: 10px;}
    
    button[kind="primary"] {
        background: linear-gradient(to right, #11998e, #38ef7d) !important;
        color: white !important; font-weight: bold !important; border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

MOTIVASYON_BITEN = ["🎉 Harika iş çıkardın {isim}!", "🚀 Eline sağlık {isim}!", "🏆 Şampiyon sensin {isim}!"]
MOTIVASYON_DEVAM = ["💪 Kolay gelsin {isim}!", "🎯 Başarılar {isim}!", "☕ İyi çalışmalar {isim}!"]

def main():
    query_params = st.query_params
    token = query_params.get("id")

    if not token:
        st.error("Giriş anahtarı bulunamadı.")
        st.stop()

    # VERİLERİ ÇEK
    try:
        r = httpx.get(SUPABASE_URL, headers=HEADERS, params={"magic_token": f"eq.{token}"})
        ilk_list = r.json()
        if not ilk_list: st.stop()
        
        personel = ilk_list[0]["personel_ad"]
        tarih_gun = datetime.now().strftime("%Y-%m-%d")

        r_tum = httpx.get(SUPABASE_URL, headers=HEADERS, params={"personel_ad": f"eq.{personel}"})
        tum_ham = r_tum.json()
        
        # Görev Gruplama
        bugun_list = [g for g in tum_ham if g.get("deadline", "").startswith(tarih_gun)]
        gelecek_list = [g for g in tum_ham if g.get("deadline", "").split("T")[0] > tarih_gun]
        gelecek_list.sort(key=lambda x: x["deadline"])

        # Şirket Radarı Verileri
        r_sirket = httpx.get(SUPABASE_URL, headers=HEADERS, params={"deadline": f"like.{tarih_gun}%"})
        sirket_gunluk = r_sirket.json()
    except:
        st.error("Veri senkronizasyon hatası.")
        st.stop()

    # --- ÜST SABİT ALAN ---
    st.markdown(f'<div class="welcome-card"><h1>Hoş Geldin, {personel}! 👋</h1><p>FLU DİJİTAL Profesyonel Portal</p></div>', unsafe_allow_html=True)

    # Genel İlerleme
    toplam = len(bugun_list)
    tamam = sum(1 for g in bugun_list if g.get("durum") == "tamamlandi")
    ilerleme = tamam / toplam if toplam > 0 else 0
    st.markdown(f"**Günlük Hedef Oranı:** %{int(ilerleme*100)}")
    st.progress(ilerleme)

    # --- SOL MENÜ ---
    with st.sidebar:
        st.markdown("### 🧭 Menü")
        secim = st.radio("Gitmek istediğiniz sekme:", ["📋 Yapılacaklar Listen", "🌐 Canlı Şirket Radarı", "📅 Gelecek Tarihli İşler"])
        st.write("---")
        st.info("FLU DİJİTAL © 2026")

    # --- İÇERİK SEKMELERİ ---

    # 1. SEKME: YAPILACAKLAR
    if secim == "📋 Yapılacaklar Listen":
        st.subheader("Bugünün Görevleri")
        if not bugun_list:
            st.info("Bugün için atanmış bir görev bulunmuyor.")
        else:
            for g in bugun_list:
                tid = g["id"]
                istamam = st.session_state.get(tid, g.get("durum") == "tamamlandi")
                
                c1, c2 = st.columns([0.1, 0.9])
                with c1:
                    st.checkbox(" ", value=istamam, key=tid)
                with c2:
                    card_class = "task-card task-completed" if istamam else "task-card"
                    t_html = f"<s>{g['is_tanimi']}</s> 🏆" if istamam else g['is_tanimi']
                    n_html = f'<div class="task-note">📌 <b>Yönetici Notu:</b> {g["notlar"]}</div>' if g.get("notlar") else ""
                    st.markdown(f'<div class="{card_class}"><div class="task-title">{t_html}</div><small>⏰ Hedef: {g.get("deadline","").split("T")[1][:5]}</small>{n_html}</div>', unsafe_allow_html=True)

    # 2. SEKME: GELECEK İŞLER
    elif secim == "📅 Gelecek Tarihli İşler":
        st.subheader("Gelecek Dönem Planlaması")
        if not gelecek_list:
            st.info("İleri tarihli bir planlama bulunmuyor.")
        else:
            for g in gelecek_list:
                f_tarih = datetime.strptime(g['deadline'].split('T')[0], '%Y-%m-%d').strftime('%d.%m.%Y')
                st.markdown(f'''
                    <div class="task-card">
                        <div class="task-title">{g["is_tanimi"]}</div>
                        <div style="font-size:12px; color:gray;">📅 Tarih: {f_tarih} | ⏰ Saat: {g['deadline'].split('T')[1][:5]}</div>
                    </div>
                ''', unsafe_allow_html=True)

    # 3. SEKME: ŞİRKET RADARI
    elif secim == "🌐 Canlı Şirket Radarı":
        st.subheader("Ekip Dinamiği")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### 🏆 Şampiyonlar")
            bitenler = [g for g in sirket_gunluk if g.get("durum") == "tamamlandi"]
            if not bitenler: st.caption("Henüz tamamlanan iş yok.")
            for b in bitenler:
                m = random.choice(MOTIVASYON_BITEN).format(isim=b['personel_ad'].split()[0])
                st.markdown(f'<div class="feed-card"><b>{b["personel_ad"]}</b> {b["is_tanimi"][:20]}... işini bitirdi!<br><small style="color:#d35400;">{m}</small></div>', unsafe_allow_html=True)
        with c2:
            st.markdown("##### ⏳ Sahada Ter Dökenler")
            devamlar = [g for g in sirket_gunluk if g.get("durum") != "tamamlandi"]
            if not devamlar: st.caption("Aktif bekleyen iş yok.")
            for d in devamlar:
                m = random.choice(MOTIVASYON_DEVAM).format(isim=d['personel_ad'].split()[0])
                st.markdown(f'<div class="feed-card-ongoing"><b>{d["personel_ad"]}</b> {d["is_tanimi"][:20]}... üzerine çalışıyor.<br><small style="color:#2980b9;">{m}</small></div>', unsafe_allow_html=True)

    # --- KAYDET BUTONU ---
    if secim in ["📋 Yapılacaklar Listen", "📅 Gelecek Tarihli İşler"]:
        st.write("---")
        if st.button("🚀 Değişiklikleri Kaydet", use_container_width=True, type="primary"):
            with st.spinner("Güncelleniyor..."):
                for g in (bugun_list + gelecek_list):
                    new_stat = "tamamlandi" if st.session_state.get(g["id"]) else "bekliyor"
                    if g["durum"] != new_stat:
                        httpx.patch(f"{SUPABASE_URL}?id=eq.{g['id']}", headers=HEADERS, json={"durum": new_stat})
                st.session_state['goster_tebrik'] = True
                st.rerun()

if __name__ == "__main__":
    main()
