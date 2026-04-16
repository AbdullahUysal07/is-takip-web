# ... (Önceki kodun üst kısımları aynı)

    for g in tum_gorevler:
        task_id = g["id"]
        is_tamam = (g.get("durum") == "tamamlandi")
        deadline_str = g.get("deadline", "")
        
        # Zaman Hesaplamaları
        try:
            deadline_dt = datetime.strptime(deadline_str, "%Y-%m-%dT%H:%M:%S")
            simdi = datetime.now()
            kalan_sure = deadline_dt - simdi
            
            # Kalan süreyi metne çevir (Örn: 2s 15dk)
            if kalan_sure.total_seconds() > 0:
                saat, kalan = divmod(kalan_sure.seconds, 3600)
                dakika, _ = divmod(kalan, 60)
                zaman_metni = f"⏳ Kalan: {saat}s {dakika}dk"
                yuzde = 1.0 - (kalan_sure.total_seconds() / 86400) # 24 saat üzerinden örnek oran
                yuzde = max(0.0, min(1.0, yuzde))
            else:
                zaman_metni = "⚠️ SÜRE DOLDU"
                yuzde = 1.0
        except:
            zaman_metni = "⏰ Süre Belirtilmedi"
            yuzde = 0

        css_class = "task-card task-completed" if is_tamam else "task-card"
        
        with st.container():
            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            col1, col2 = st.columns([0.1, 0.9])
            with col1:
                st.checkbox(" ", value=is_tamam, key=task_id)
            with col2:
                st.markdown(f'<div class="task-title">{g["is_tanimi"]}</div>', unsafe_allow_html=True)
                
                # Saat ve Geri Sayım Yan Yana
                st.markdown(f'<div style="font-size: 13px; color: #7f8c8d;">⏰ {deadline_str.split("T")[1][:5]} | <b>{zaman_metni}</b></div>', unsafe_allow_html=True)
                
                # Minik İlerleme Barı
                bar_rengi = "green" if is_tamam else ("red" if "DOLDU" in zaman_metni else "blue")
                st.progress(yuzde) # Streamlit progress bar
                
                if g.get("notlar"):
                    st.markdown(f'<div class="task-note">📌 <b>Not:</b> {g["notlar"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
