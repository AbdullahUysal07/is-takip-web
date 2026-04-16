import streamlit as st
import httpx

st.set_page_config(page_title="Sadece Yazılım | Onay", page_icon="✅")
st.image("https://sadeceyazilim.com/wp-content/uploads/2023/10/sadeceyazilim-logo.png", width=250)
st.title("Personel İş Takip Paneli")

# URL'den ID çekme
query_params = st.query_params
magic_id = query_params.get("id")

SUPABASE_URL = "https://fxohhhqrhybbqqwqxejc.supabase.co/rest/v1/gorevler"
ANON_KEY = "sb_publishable_Gr83hViFqzpLLHW3Ib-iaQ_cIuQ3fe8"
HEADERS = {"apikey": ANON_KEY, "Authorization": f"Base {ANON_KEY}"}

if magic_id:
    try:
        with httpx.Client() as client:
            res = client.get(f"{SUPABASE_URL}?magic_token=eq.{magic_id}", headers=HEADERS)
            isler = res.json()
            
            if isler and len(isler) > 0:
                is_verisi = isler[0]
                st.info(f"Merhaba **{is_verisi['personel_ad']}**, sana atanan bir iş var.")
                st.write(f"📋 **Görev:** {is_verisi['is_tanimi']}")
                
                if is_verisi['durum'] == 'tamamlandi':
                    st.success("✅ Bu işi daha önce onayladınız. Teşekkürler!")
                else:
                    if st.button("İŞİ TAMAMLADIM VE ONAYLIYORUM", type="primary"):
                        update_res = client.patch(
                            f"{SUPABASE_URL}?id=eq.{is_verisi['id']}",
                            headers=HEADERS,
                            json={"durum": "tamamlandi"}
                        )
                        if update_res.status_code == 204:
                            st.balloons()
                            st.success("Harika! İş başarıyla onaylandı.")
                            st.rerun()
            else:
                st.warning("Bu linke ait bir görev bulunamadı veya link hatalı.")
    except Exception as e:
        st.error("Veritabanı bağlantısında bir sorun oluştu.")
else:
    st.info("Lütfen size gönderilen özel link üzerinden giriş yapın.")
