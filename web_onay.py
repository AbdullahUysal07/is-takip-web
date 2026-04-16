import streamlit as st
import httpx

# --- AYARLAR ---
URL = "https://fxohhhqrhybbqqwqxejc.supabase.co/rest/v1/gorevler"
HEADERS = {
    "apikey": "sb_publishable_Gr83hViFqzpLLHW3Ib-iaQ_cIuQ3fe8",
    "Authorization": "Bearer sb_secret_Wun-Hd6XmwwCWy4N5-yqMQ_Wg0kyeh2",
    "Content-Type": "application/json"
}

st.set_page_config(page_title="sadeceyazilim.com | Onay", page_icon="✅")

st.title("🚀 sadeceyazilim.com")
st.subheader("Personel İş Takip Paneli")

# Linkten gelen ID'yi al (?id=TOKEN)
query_params = st.query_params
token = query_params.get("id")

if token:
    # Veritabanından bu tokene ait işleri çek
    with httpx.Client() as client:
        res = client.get(f"{URL}?magic_token=eq.{token}", headers=HEADERS)
        isler = res.json()

    if isler:
        st.write(f"### Merhaba, {isler[0]['personel_ad']}")
        st.divider()
        
        for is_item in isler:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**Görev:** {is_item['is_tanimi']}")
            with col2:
                if is_item['durum'] == 'bekliyor':
                    if st.button("Onayla", key=is_item['id']):
                        # Durumu güncelle
                        httpx.patch(f"{URL}?id=eq.{is_item['id']}", headers=HEADERS, json={"durum": "tamamlandi"})
                        st.success("Onaylandı!")
                        st.rerun()
                else:
                    st.write("✅ Bitti")
            st.divider()
    else:
        st.error("Üzgünüz, bu linke ait bir görev bulunamadı.")
else:
    st.info("Lütfen size gönderilen özel link üzerinden giriş yapın.")