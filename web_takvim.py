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
        if st.button("Giriş Yap") and sifre == "batur123": # Şifreni buradan değiştirebilirsin
            st.session_state.authenticated = True
            st.rerun()
        elif sifre and sifre != "batur123":
            st.error("Hatalı şifre! Lütfen tekrar deneyin.")
        return False
    return True

if check_password():
    
    if os.path.exists("logo.jpg"):
        image = Image.open("logo.jpg")
        st.image(image, use_container_width=True)
    
    st.title("🏡 Villa Cennet Rezervasyon Yönetimi")
    st.write("Telefon ve bilgisayardan anlık müsaitlik yönetim paneli.")
    
    # --- AY / YIL SEÇİMİ (Takvim Ekranı İçin) ---
    st.write("---")
    col_yil, col_ay = st.columns(2)
    
    with col_yil:
        secili_yil = st.selectbox("Görüntülenecek Yıl", options=[2026, 2027, 2028], index=0)
    with col_ay:
        aylar_tr = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        secili_ay = st.selectbox("Görüntülenecek Ay", options=list(range(1, 13)), format_func=lambda x: aylar_tr[x-1], index=datetime.now().month - 1)

    # --- 🗓️ YENİ AKILLI REZERVASYON FORMU ---
    st.subheader("📅 Yeni Rezervasyon Ekle (Tarih Aralığı)")
    
    col_tarih1, col_tarih2 = st.columns(2)
    with col_tarih1:
        giris_tarihi = st.date_input("Müşteri Giriş Tarihi", value=datetime.now())
    with col_tarih2:
        cikis_tarihi = st.date_input("Müşteri Çıkış Tarihi", value=datetime.now() + timedelta(days=1))
        
    rez_notu = st.text_input("Rezervasyon Notu (Müşteri Adı, Telefon, Kapora vb.):")
    
    if st.button("💾 Rezervasyonu Otomatik İşle", use_container_width=True):
        if giris_tarihi >= cikis_tarihi:
            st.error("HATA: Çıkış tarihi, giriş tarihinden sonra olmalıdır!")
        else:
            # İki tarih arasındaki tüm günleri bulup döngüye alıyoruz
            current_date = giris_tarihi
            while current_date <= cikis_tarihi:
                # Veritabanı anahtarı formatı: "YIL-AY-GÜN" (Örn: "2026-5-28")
                key = f"{current_date.year}-{current_date.month}-{current_date.day}"
                
                # Durum Belirleme Mantığı:
                if current_date == giris_tarihi:
                    durum = "giris"      # İlk gün Giriş Günü
                elif current_date == cikis_tarihi:
                    durum = "cikis"      # Son gün Çıkış Günü
                else:
                    durum = "dolu"       # Aradaki tüm günler Tam Dolu
                    
                st.session_state.takvim_verisi[key] = {"status": durum, "note": rez_notu}
                current_date += timedelta(days=1)
                
            save_data(st.session_state.takvim_verisi)
            st.success(f"{giris_tarihi} ile {cikis_tarihi} arasındaki günler başarıyla dolduruldu!")
            st.rerun()

    # --- 🗑️ HIZLI REZERVASYON İPTALİ (SİLME) ---
    st.subheader("🗑️ Rezervasyon İptal Et / Günleri Boşalt")
    col_sil1, col_sil2 = st.columns(2)
    with col_sil1:
        sil_baslangic = st.date_input("Silinecek Aralık Başlangıcı", value=datetime.now())
    with col_sil2:
        sil_bitis = st.date_input("Silinecek Aralık Bitişi", value=datetime.now())
        
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
        st.warning(f"Seçilen aralıktaki {silinen_adet} günün rezervasyonu silindi ve müsait yapıldı.")
        st.rerun()

    # --- TAKVİM GÖRSELLEŞTİRME ---
    st.write("---")
    st.subheader(f"📅 {aylar_tr[secili_ay-1]} {secili_yil} Takvimi")
    
    st.markdown("""
    <div style='display: flex; gap: 10px; margin-bottom: 15px; font-size: 12px; justify-content: center;'>
        <span style='background:#f8f9fa; color:black; padding:5px; border-radius:5px; border:1px solid #ddd'>⚪ Müsait</span>
        <span style='background:#ff7979; color:black; padding:5px; border-radius:5px;'>📐 Giriş</span>
        <span style='background:#ff3838; color:white; padding:5px; border-radius:5px;'>🔴 Tam Dolu</span>
        <span style='background:#ffaa44; color:black; padding:5px; border-radius:5px;'>📐 Çıkış</span>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(7)
    gunler = ["Pt", "Sl", "Ça", "Pe", "Cu", "Ct", "Pa"]
    for i, g in enumerate(gunler):
        cols[i].markdown(f"<center><b>{g}</b></center>", unsafe_allow_html=True)
        
    cal = calendar.Calendar(firstweekday=0)
    weeks = cal.monthdayscalendar(secili_yil, secili_ay)
    
    for week in weeks:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].write("")
            else:
                day_key = f"{secili_yil}-{secili_ay}-{day}"
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
                            padding: 8px 0px; border-radius: 8px; font-weight: bold; 
                            border: 1px solid #e1e4e8; min-height: 45px; font-size:14px;'>
                    {day}<br><span style='font-size:10px;'>{note_marker}</span>
                </div>
                """
                cols[i].markdown(cell_html, unsafe_allow_html=True)

    # --- SEÇİLİ AYIN TÜM NOTLARI ---
    st.write("---")
    st.subheader("📋 Bu Ayın Rezervasyon Notları")
    not_bulundu = False
    _, num_days = calendar.monthrange(secili_yil, secili_ay)
    for d in range(1, num_days + 1):
        k = f"{secili_yil}-{secili_ay}-{d}"
        if k in st.session_state.takvim_verisi:
            info = st.session_state.takvim_verisi[k]
            if isinstance(info, dict) and info.get("note", "").strip():
                st.info(f"**Gün {d}:** {info['note']} *({info['status'].upper()})*")
                not_bulundu = True
                
    if not not_bulundu:
        st.write("Bu ay için eklenmiş bir rezervasyon notu bulunmuyor.")
