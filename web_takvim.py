# -*- coding: utf-8 -*-
"""
Created on Thu May 28 10:38:56 2026

@author: Batur
"""

import streamlit as st
import calendar
import json
import os
from datetime import datetime
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
        if st.button("Giriş Yap") and sifre == "batur123":
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
    
    # İŞTE O DEĞİŞEN BAŞLIK:
    st.title("🏡 Villa Cennet Rezervasyon Yönetimi")
    st.write("Telefon ve bilgisayardan anlık müsaitlik yönetim paneli.")
    
    # --- AY / YIL SEÇİMİ ---
    today = datetime.now()
    col_yil, col_ay = st.columns(2)
    
    with col_yil:
        secili_yil = st.selectbox("Yıl Seçin", options=[2026, 2027, 2028], index=0)
    with col_ay:
        aylar_tr = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        secili_ay = st.selectbox("Ay Seçin", options=list(range(1, 13)), format_func=lambda x: aylar_tr[x-1], index=4)

    # --- GÜNCELLEME FORMU ---
    st.subheader("📝 Gün Durumu Güncelle")
    
    _, num_days = calendar.monthrange(secili_yil, secili_ay)
    
    col_gun, col_durum = st.columns([1, 2])
    with col_gun:
        secili_gun = st.number_input("Gün", min_value=1, max_value=num_days, value=1)
    with col_durum:
        durum_secenekleri = {"Müsait (Boş)": "bos", "Giriş Günü (Yarım)": "giris", "Tam Dolu": "dolu", "Çıkış Günü (Yarım)": "cikis"}
        secili_durum_metin = st.selectbox("Durum", options=list(durum_secenekleri.keys()))
        secili_durum = durum_secenekleri[secili_durum_metin]
        
    secili_not = st.text_input("Rezervasyon Notu (Müşteri adı, kapora, telefon vb.):")
    
    key = f"{secili_yil}-{secili_ay}-{secili_gun}"
    
    if st.button("💾 Güncelle ve Kaydet", use_container_width=True):
        if secili_durum == "bos" and not secili_not.strip():
            if key in st.session_state.takvim_verisi:
                del st.session_state.takvim_verisi[key]
        else:
            st.session_state.takvim_verisi[key] = {"status": secili_durum, "note": secili_not}
            
        save_data(st.session_state.takvim_verisi)
        st.success(f"{secili_gun} {aylar_tr[secili_ay-1]} {secili_yil} başarıyla güncellendi!")
        st.rerun()

    # --- TAKVİM GÖRSELLEŞTİRME ---
    st.write("---")
    st.subheader(f"📅 {aylar_tr[secili_ay-1]} {secili_yil} Takvimi")
    
    # HATALI PARAMETRELERİN HEPSİ DOĞRUSUYLA (unsafe_allow_html=True) DEĞİŞTİRİLDİ
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
    for d in range(1, num_days + 1):
        k = f"{secili_yil}-{secili_ay}-{d}"
        if k in st.session_state.takvim_verisi:
            info = st.session_state.takvim_verisi[k]
            if isinstance(info, dict) and info.get("note", "").strip():
                st.info(f"**Gün {d}:** {info['note']} *({info['status'].upper()})*")
                not_bulundu = True
                
    if not not_bulundu:
        st.write("Bu ay için eklenmiş bir rezervasyon notu bulunmuyor.")
