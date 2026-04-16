import streamlit as st
import httpx
from datetime import datetime
import json

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="FlowDesk | Çalışan Portalı", 
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

# --- GELİŞMİŞ CSS VE ANİMASYONLAR ---
st.markdown("""
<style>
    .stApp { background-color: #f4f7f6; font-family: 'Inter', sans-serif; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}

    .welcome-card {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        padding: 35px; border-radius: 20px; color: white; text-align: center;
        box-shadow: 0 15px 30px rgba(0,0,0,0.15); margin-bottom: 20px;
    }
    
    .task-card {
        background: #ffffff; border-radius: 12px; padding: 15px 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04); border-left: 6px solid #3498db;
        transition: all 0.3s ease; margin-bottom: 10px;
    }
    .task-completed { border-left: 6px solid #2ecc71; background: #f9fdfa; opacity: 0.85; }
    
    .task-title { font-size: 18px; font-weight: 700; color: #2c3e50; margin-bottom: 2px; }
    .task-time-info { font-size: 13px; color: #7f8c8d; margin-bottom: 8px; font-weight: 500;}
    
    /* Yanıp Sönen Ünlem ve Yazı */
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0; } 100% { opacity: 1; } }
    .overdue-text { color: #e74c3c; font-weight: bold; }
    .blink-icon { animation: blink 1s linear infinite; color: #e74c3c; font-size: 18px; font-weight: 900; }

    .task-note { 
        background-color: #fff8e1; padding: 10px; border-radius: 8px; 
        font-size: 13px; color: #b78a00; border-left: 4px solid #ffc107; margin-top: 10px;
    }

    /* Checkbox Gizleme */
    div[data-testid="stCheckbox"] label span p { display: none; }
    div[data-testid="stCheckbox"] { padding-top: 20px; }
</style>
""", unsafe_allow_html=True)

def main():
    query_params = st.query_params
    token = query_params.get("id")

    if not token:
        st.markdown('<div class="welcome-card"><h1>Bağlantı Geçersiz</h1><p>Lütfen yöneticinizden gelen linki kontrol edin.</p></div>', unsafe_allow_html=True)
        st.stop()

    # Veri Çekme
    try:
        r = httpx.get(SUPABASE_URL, headers=HEADERS, params={"magic_token": f"eq.{token}"})
        ilk_gorev_list = r.json()
        if not ilk_gorev_list: st.stop()
        
        personel = ilk_gorev_list[0]["personel_ad"]
        tarih_gun = ilk_gorev_list[0]["deadline"].split("T")[0]
        
        r_tum = httpx.get(SUPABASE_URL, headers=HEADERS, params={"personel_ad": f"eq.{personel}"})
        tum_gorevler = [g for g in r_tum.json() if g.get("deadline", "").startswith(tarih_gun)]
    except:
        st.error("Veritabanı hatası.")
        st.stop()

    # Üst Bilgi
    st.markdown(f'<div class="welcome-card"><h1>Hoş Geldin, {personel}! 👋</h1><p>Bugünkü Görev Çizelgen</p></div>', unsafe_allow_html=True)

    # İstatistikler
    tamam = sum(1 for g in tum_gorevler if g.get("durum") == "tamamlandi")
    st.progress(tamam / len(tum_gorevler) if tum_gorevler else 0)

    st.write("---")

    for g in tum_gorevler:
        task_id = g["id"]
        is_tamam = (g.get("durum") == "tamamlandi")
        deadline_raw = g["deadline"] # Örn: 2026-04-16T14:00:00
        
        # Sütun Düzeni
        col1, col2 = st.columns([0.08, 0.92])
        
        with col1:
            st.checkbox(" ", value=is_tamam, key=task_id)
        
        with col2:
            card_class = "task-card task-completed" if is_tamam else "task-card"
            target_h = deadline_raw.split("T")[1][:5]
            
            # JavaScript Geri Sayım Kartı
            unique_id = f"timer_{task_id.replace('-', '')}"
            
            st.markdown(f"""
            <div class="{card_class}">
                <div class="task-title">{"<s>" if is_tamam else ""}{g['is_tanimi']}{"</s> 🏆" if is_tamam else ""}</div>
                <div id="{unique_id}" class="task-time-info">Hesaplanıyor...</div>
                <script>
                    (function() {{
                        const targetDate = new Date("{deadline_raw.replace('T', ' ')}").getTime();
                        const timerElement = document.getElementById("{unique_id}");
                        
                        function update() {{
                            if ("{is_tamam}" === "True") {{
                                timerElement.innerHTML = "⏰ Hedef: {target_h} | <b>Görev Tamamlandı!</b>";
                                return;
                            }}
                            
                            const now = new Date().getTime();
                            const diff = targetDate - now;
                            
                            if (diff <= 0) {{
                                timerElement.innerHTML = "⏰ Hedef: {target_h} | <span class='overdue-text'>Süresi geçmiş görev</span> <span class='blink-icon'>!</span>";
                            }} else {{
                                const h = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                                const m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                                const s = Math.floor((diff % (1000 * 60)) / 1000);
                                timerElement.innerHTML = "⏰ Hedef: {target_h} | <b>⏳ Kalan: " + h + "s " + m + "dk " + s + "sn</b>";
                            }}
                        }}
                        update();
                        if ("{is_tamam}" !== "True") setInterval(update, 1000);
                    }})();
                </script>
                {f'<div class="task-note">📌 <b>Not:</b> {g["notlar"]}</div>' if g.get("notlar") else ""}
            </div>
            """, unsafe_allow_html=True)

    # Kaydet Butonu
    if st.button("🚀 Görevleri Kaydet ve Bilgi Ver", use_container_width=True, type="primary"):
        for g in tum_gorevler:
            tid = g["id"]
            new_status = "tamamlandi" if st.session_state.get(tid) else "bekliyor"
            if g["durum"] != new_status:
                httpx.patch(f"{SUPABASE_URL}?id=eq.{tid}", headers=HEADERS, json={"durum": new_status})
        st.balloons()
        st.rerun()

if __name__ == "__main__":
    main()
