# -*- coding: utf-8 -*-
"""
Created on Thu May 28 10:38:56 2026

@author: Batur
"""

import streamlit as st
import calendar
import json
import os
from datetime import datetime, timedelta
from PIL import Image

# Sayfa Ayarları
st.set_page_config(page_title="Villa Cennet Rezervasyon Paneli", page_icon="🏡", layout="centered")

# --- VERİ YÖNETİMİ ---
DATA_FILE = "villa_takvim_veri.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

if "takvim_verisi" not in st.session_state:
    st.session_state.takvim_verisi = load_data()

# --- ŞİFRE KORUMASI ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔒 Giriş Yetkisi Gerekli")
        sifre = st.text_input("Lütfen Giriş Şifresini Yazın:", type="password")
        if st.button("Giriş Yap") and sifre == "villacennet48": # Şifreniz
            st.session_state.authenticated = True
            st.rerun()
        elif sifre and sifre != "villacennet48":
            st.error("Hatalı şifre! Lütfen tekrar deneyin.")
        return False
    return True

if check_password():
    
    if os.path.exists("villa.jpeg"):
        image = Image.open("villa.jpeg")
        st.image(image, use_container_width=True)
    
    st.title("🏡 Villa Cennet Rezervasyon Yönetimi")
    st.write("Telefonunuzdan aşağı kaydırarak tüm ayları anlık görebilirsiniz.")
    
    # --- SADECE YIL SEÇİMİ ---
    secili_yil = st.selectbox("Görüntülenecek Yıl Seçin", options=[2026, 2027, 2028], index=0)
    
    # --- REZERVASYON EKLEME PANELİ (Açılır Kutu) ---
    with st.expander("📝 Yeni Rezervasyon Ekle (Tarih Aralığı Seçin)", expanded=False):
        col_tarih1, col_tarih2 = st.columns(2)
        with col_tarih1:
            giris_tarihi = st.date_input("Müşteri Giriş Tarihi", value=datetime.now(), key="ins_start")
        with col_tarih2:
            cikis_tarihi = st.date_input("Müşteri Çıkış Tarihi", value=datetime.now() + timedelta(days=1), key="ins_end")
            
        rez_notu = st.text_input("Rezervasyon Notu (Müşteri Adı, Telefon, Kapora vb.):")
        
        if st.button("💾 Rezervasyonu Otomatik İşle", use_container_width=True):
            if giris_tarihi >= cikis_tarihi:
                st.error("HATA: Çıkış tarihi, giriş tarihinden sonra olmalıdır!")
            else:
                current_date = giris_tarihi
                while current_date <= cikis_tarihi:
                    key = f"{current_date.year}-{current_date.month}-{current_date.day}"
                    
                    if current_date == giris_tarihi:
                        durum = "giris"
                    elif current_date == cikis_tarihi:
                        durum = "cikis"
                    else:
                        durum = "dolu"
                        
                    st.session_state.takvim_verisi[key] = {"status": durum, "note": rez_notu}
                    current_date += timedelta(days=1)
                    
                save_data(st.session_state.takvim_verisi)
                st.success("Rezervasyon başarıyla işlendi ve takvim güncellendi!")
                st.rerun()

    # --- REZERVASYON SİLME PANELİ (Açılır Kutu) ---
    with st.expander("🗑️ Rezervasyon İptal Et / Günleri Boşalt", expanded=False):
        col_sil1, col_sil2 = st.columns(2)
        with col_sil1:
            sil_baslangic = st.date_input("Silinecek Aralık Başlangıcı", value=datetime.now(), key="del_start")
        with col_sil2:
            sil_bitis = st.date_input("Silinecek Aralık Bitişi", value=datetime.now(), key="del_end")
            
        if st.button("❌ Seçili Aralığı Tamamen Boşalt (Müsait Yap)", use_container_width=True):
            current_date = sil_baslangic
            silinen_adet = 0
            while current_date <= sil_bitis:
                key = f"{current_date.year}-{current_date.month}-{current_date.day}"
                if key in st.session_state.takvim_verisi:
                    del st.session_state.takvim_verisi[key]
                    silinen_adet += 1
                current_date += timedelta(days=1)
                
            save_data(st.session_state.takvim_verisi)
            st.warning(f"Seçilen aralıktaki {silinen_adet} günün rezervasyonu temizlendi.")
            st.rerun()

    # --- RENK SKALASI (Sadece bir kez en üstte görünsün) ---
    st.write("---")
    st.markdown("""
    <div style='display: flex; gap: 10px; margin-bottom: 25px; font-size: 12px; justify-content: center;'>
        <span style='background:#f8f9fa; color:black; padding:5px; border-radius:5px; border:1px solid #ddd'>⚪ Müsait</span>
        <span style='background:#ff7979; color:black; padding:5px; border-radius:5px;'>📐 Giriş</span>
        <span style='background:#ff3838; color:white; padding:5px; border-radius:5px;'>🔴 Tam Dolu</span>
        <span style='background:#ffaa44; color:black; padding:5px; border-radius:5px;'>📐 Çıkış</span>
    </div>
    """, unsafe_allow_html=True)

    # --- 🔄 TÜM AYLARI SEKANSSAL OLARAK (ALT ALTA) ÇİZME DÖNGÜSÜ ---
    aylar_tr = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
    gunler = ["Pt", "Sl", "Ça", "Pe", "Cu", "Ct", "Pa"]
    
    for ay_indeks in range(1, 13):
        # Ay Başlığı
        st.subheader(f"📅 {aylar_tr[ay_indeks-1]} {secili_yil}")
        
        # Haftanın Günleri Başlığı (Pzt, Sal...)
        cols_header = st.columns(7)
        for i, g in enumerate(gunler):
            cols_header[i].markdown(f"<center><b style='color:#7f8c8d; font-size:12px;'>{g}</b></center>", unsafe_allow_html=True)
            
        # Takvim Gün Matrisi oluşturma
        cal = calendar.Calendar(firstweekday=0)
        weeks = cal.monthdayscalendar(secili_yil, ay_indeks)
        
        for week in weeks:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day == 0:
                    cols[i].write("")
                else:
                    day_key = f"{secili_yil}-{ay_indeks}-{day}"
                    day_info = st.session_state.takvim_verisi.get(day_key, "bos")
                    
                    if isinstance(day_info, str):
                        status, note = day_info, ""
                    else:
                        status = day_info.get("status", "bos")
                        note = day_info.get("note", "")
                    
                    bg = "#f8f9fa"
                    fg = "#2c3e50"
                    
                    if status == "dolu":
                        bg = "#ff3838"
                        fg = "white"
                    elif status == "giris":
                        bg = "linear-gradient(135deg, #f8f9fa 50%, #ff7979 50%)"
                    elif status == "cikis":
                        bg = "linear-gradient(135deg, #ffaa44 50%, #f8f9fa 50%)"
                        
                    note_marker = "🔹" if note.strip() else ""
                    
                    cell_html = f"""
                    <div style='background: {bg}; color: {fg}; text-align: center; 
                                padding: 6px 0px; border-radius: 8px; font-weight: bold; 
                                border: 1px solid #e1e4e8; min-height: 42px; font-size:13px; line-height:1.2;'>
                        {day}<br><span style='font-size:8px;'>{note_marker}</span>
                    </div>
                    """
                    cols[i].markdown(cell_html, unsafe_allow_html=True)
                    
        # --- O AYA AİT NOTLAR (Hemen takvimin altına listelenir) ---
        _, num_days = calendar.monthrange(secili_yil, ay_indeks)
        aylik_not_var_mi = False
        
        for d in range(1, num_days + 1):
            k = f"{secili_yil}-{ay_indeks}-{d}"
            if k in st.session_state.takvim_verisi:
                info = st.session_state.takvim_verisi[k]
                if isinstance(info, dict) and info.get("note", "").strip():
                    if not aylik_not_var_mi:
                        st.markdown(f"<p style='margin-top:10px; margin-bottom:2px; font-size:12px; font-weight:bold; color:#34495e;'>📋 {aylar_tr[ay_indeks-1]} Notları:</p>", unsafe_allow_html=True)
                        aylik_not_var_mi = True
                    st.markdown(f"<div style='font-size:11px; background:#e8f4f8; padding:4px 8px; border-radius:4px; margin-bottom:2px;'><b>Gün {d}:</b> {info['note']} <i>({info['status'].upper()})</i></div>", unsafe_allow_html=True)
                    
        st.markdown("<br><hr style='margin-top:5px; margin-bottom:15px; border:0; border-top:1px dashed #eee;'><br>", unsafe_allow_html=True)
