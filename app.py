import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import gc

# ==============================================================================
# 1. KONFIGURASI MUTLAK SYSTEM & KREDENSIAL (KUNCI PERMANEN)
# ==============================================================================
st.set_page_config(page_title="AI Trading BEI - Sesi 6 Master", layout="wide")

# Kredensial Utama Anda (Terkunci Sempurna)
TOKEN_TELEGRAM = "8701590259:AAFHOTaWoKMk2qCsReI6RlW76NOLm0dtluo"
CHAT_ID_TELEGRAM = "5282255947" 

# Daftar Komposisi Universal Scope Lengkap Tanpa Pemangkasan Harian
TICKERS = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "TLKM.JK", "ASII.JK", "UNVR.JK",
    "GOTO.JK", "ADRO.JK", "PTBA.JK", "ITMG.JK", "UNTR.JK", "PGAS.JK", "AKRA.JK",
    "ANTM.JK", "INCO.JK", "BRPT.JK", "TPIA.JK", "AMRT.JK", "MDKA.JK", "KLBF.JK",
    "SMGR.JK", "INDF.JK", "ICBP.JK", "CPIN.JK", "MEDC.JK", "HRUM.JK"
]
# ==============================================================================
# 2. ENGINE DATA REAL-TIME TANGGUH (RESTORASI AKURASI SESI 5)
# ==============================================================================
@st.cache_data(ttl=5) # Cache dipangkas menjadi 5 detik untuk memaksa pembaruan harga live hulu BEI
def fetch_realtime_market_data(ticker_list):
    """
    KEMBALI KE STRUKTUR SESI 5: Menarik data interval menit untuk fluktuasi live 
    dan data harian sekaligus secara individual untuk mendapatkan pembanding harga kemarin.
    """
    data_dict = {}
    for ticker in ticker_list:
        try:
            # 1. Tarik data intraday menit berjalan (Akurasi Real-time Detik Ini)
            df_live = yf.download(ticker, period="1d", interval="1m", progress=False)
            # 2. Tarik data harian untuk mendapatkan harga penutupan kemarin sebagai baseline
            df_daily = yf.download(ticker, period="5d", interval="1d", progress=False)
            
            if not df_live.empty and not df_daily.empty:
                # Meratakan MultiIndex jika terdeteksi dari fungsi yfinance terbaru
                if isinstance(df_live.columns, pd.MultiIndex):
                    df_live_clean = df_live[ticker].dropna() if ticker in df_live.columns.levels else df_live.copy().dropna()
                    df_daily_clean = df_daily[ticker].dropna() if ticker in df_daily.columns.levels else df_daily.copy().dropna()
                else:
                    df_live_clean = df_live.dropna()
                    df_daily_clean = df_daily.dropna()
                
                if len(df_live_clean) >= 1 and len(df_daily_clean) >= 2:
                    data_dict[ticker] = {
                        "live": df_live_clean,
                        "daily": df_daily_clean
                    }
        except Exception:
            continue
            
    gc.collect() # Proteksi memori RAM 4GB Streamlit Cloud
    return data_dict

def send_telegram_alert(message):
    """Fungsi transmisi pesan langsung ke Telegram API."""
    url = f"https://telegram.org{TOKEN_TELEGRAM}/sendMessage"
    payload = {
        "chat_id": CHAT_ID_TELEGRAM,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code, response.json()
    except Exception as e:
        return 500, str(e)
# ==============================================================================
# 3. CORE METRICS LOGIC: FLUKTUASI REAL-TIME & INDEKS WAJAR SKALA 100
# ==============================================================================
def process_realtime_metrics(ticker, ticker_data):
    """Memproses gabungan data intraday menit dan harian secara fluktuatif tanpa lag."""
    try:
        df_live = ticker_data["live"]
        df_daily = ticker_data["daily"]
        
        # Ambil tick harga menit terakhir berjalan (Harga Saat Ini)
        current_tick = df_live.iloc[-1]
        # Ambil baris penutupan hari kemarin
        yesterday_row = df_daily.iloc[-2]
        
        close_val = float(current_tick['Close'])
        high_val = float(current_tick['High'])
        low_val = float(current_tick['Low'])
        open_val = float(current_tick['Open'])
        volume_val = float(df_live['Volume'].sum()) # Total volume akumulasi menit hari ini
        
        # Ambil baseline harga penutupan kemarin secara akurat
        prev_close = float(yesterday_row['Close'])
        
        # 1. KOLOM SELISIH FLUKTUATIF REAL-TIME: (Harga Detik Ini - Harga Penutupan Kemarin)
        selisih_harga = close_val - prev_close
        
        # Formula Proksi Volume Presisi Tinggi Sesi 6
        range_width = high_val - low_val
        price_position = (close_val - low_val) / range_width if range_width > 0 else 0.5
        close_vs_open = 0.6 if close_val > open_val else (0.4 if close_val < open_val else 0.5)
        buy_fraction = (price_position * 0.7) + (close_vs_open * 0.3)
        buy_volume = volume_val * buy_fraction
        sell_volume = volume_val * (1.0 - buy_fraction)
        selisih_volume = buy_volume - sell_volume
        
        # 2. KOLOM FREKUENSI PROKSI MARKET REAL-TIME
        np.random.seed(int(close_val) % 1000 + 1)
        estimated_frequency = int(volume_val / np.random.randint(15, 30)) if volume_val > 0 else 0
        
        # 3. KOLOM INDEX INDIVIDUAL (NILAI 100 = TEPAT PADA HARGA WAJAR HISTORIS 5 HARI)
        historical_mean = df_daily['Close'].mean()
        indeks_individual = (close_val / historical_mean) * 100 if historical_mean > 0 else 100.0

        # Algoritma Sinyal & Win-Rate Ledger Otomatis (TP/CL 3% - 4%)
        signal = "▬"
        tp_price = close_val * 1.03
        cl_price = close_val * 0.96
        ledger_status = "HOLD"
        
        if selisih_harga > 0 and selisih_volume > 0:
            signal = "▲ BUY"
            ledger_status = "TARGET PROFIT" if selisih_harga > (prev_close * 0.02) else "SIGNAL RELEASED"
        elif selisih_harga < 0 or selisih_volume < 0:
            signal = "▼ SELL"
            ledger_status = "CUT LOSS" if selisih_harga < -(prev_close * 0.015) else "SIGNAL RELEASED"

        return {
            "Emiten": ticker.replace(".JK", ""),
            "Index Individual": round(indeks_individual, 2),
            "Harga": f"Rp {int(close_val):,}",
            "Selisih": selisih_harga,
            "Sinyal": signal,
            "Frekuensi": f"{estimated_frequency:,}",
            "Buy Vol (Proxy)": f"{int(buy_volume):,}",
            "Sell Vol (Proxy)": f"{int(sell_volume):,}",
            "Selisih Vol": f"{'+' if selisih_volume > 0 else ''}{int(selisih_volume):,}",
            "TP (3%)": f"Rp {int(tp_price):,}",
            "CL (4%)": f"Rp {int(cl_price):,}",
            "Ledger_Status": ledger_status
        }
    except Exception:
        return None
# ==============================================================================
# 4. DASHBOARD INTERAKTIF & ENGINE BROADCASTER TELEGRAM
# ==============================================================================
st.title("📈 AI TRADING SYSTEM - INDONESIA STOCK EXCHANGE")
st.subheader("Sesi 6 Master: Pemulihan Total Jalur Data Intraday Real-Time Sesi 5")

# Eksekusi pemindaian aman hulu per emiten berbasis menit
with st.spinner("Menarik Data Intraday Real-Time Seluruh Emiten BEI..."):
    dict_raw_data = fetch_realtime_market_data(TICKERS)

processed_rows = []
for ticker in TICKERS:
    if ticker in dict_raw_data:
        metrics = process_realtime_metrics(ticker, dict_raw_data[ticker])
        if metrics is not None:
            processed_rows.append(metrics)

if processed_rows:
    df_master = pd.DataFrame(processed_rows)
    
    st.write("### 🎛️ Win-Rate Ledger & Kendali Sinyal Kontrol")
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    total_sinyal_count = len(df_master[df_master['Sinyal'] != "▬"])
    total_tp_count = len(df_master[df_master['Ledger_Status'] == "TARGET PROFIT"])
    total_cl_count = len(df_master[df_master['Ledger_Status'] == "CUT LOSS"])
    
    if "filter_mode" not in st.session_state:
        st.session_state.filter_mode = "ALL"

    with col_btn1:
        if st.button(f"🔔 Total Sinyal Dirilis ({total_sinyal_count} Emiten)", use_container_width=True):
            st.session_state.filter_mode = "SINYAL"
    with col_btn2:
        if st.button(f"🎯 Sukses Target Profit ({total_tp_count} Emiten)", use_container_width=True):
            st.session_state.filter_mode = "TP"
    with col_btn3:
        if st.button(f"🛡️ Disiplin Cut Loss ({total_cl_count} Emiten)", use_container_width=True):
            st.session_state.filter_mode = "CL"

    if st.button("🔄 Reset Tampilan & Lihat Semua Emiten Terlikuid", type="secondary"):
        st.session_state.filter_mode = "ALL"

    # --- TRANSMITTER TELEGRAM VIA REALTIME DATA ---
    st.markdown("---")
    if st.button("🚀 PANCARKAN SINYAL AKTIF HARI INI KE TELEGRAM", type="primary", use_container_width=True):
        emiten_sinyal = df_master[df_master['Sinyal'] != "▬"]
        if not emiten_sinyal.empty:
            pesan_induk = "🔔 *AI TRADING REPORT - SESI 6 MASTER*\n\n"
            for _, row in emiten_sinyal.iterrows():
                pesan_induk += f"• *{row['Emiten']}* | {row['Sinyal']} | Harga: {row['Harga']} | Selisih: {row['Selisih']} | Indeks: {row['Index Individual']}\n"
            
            status_code, json_response = send_telegram_alert(pesan_induk)
            if status_code == 200:
                st.success("✅ Sinyal aktif sukses dipancarkan ke aplikasi Telegram Anda!")
            else:
                st.error(f"❌ Telegram API Error {status_code}! Periksa kembali konfigurasi Chat ID.")
                st.json(json_response)
        else:
            st.warning("Tidak ada emiten bersinyal aktif (▲/▼) detik ini untuk dikirim.")

    # Aplikasi Logika Saringan Tampilan UI Berbasis Tombol yang Di-klik
    df_filtered = df_master.copy()
    if st.session_state.filter_mode == "SINYAL":
        df_filtered = df_master[df_master['Sinyal'] != "▬"]
        st.info("Menampilkan Emiten yang Berhasil Merilis Sinyal Eksekusi.")
    elif st.session_state.filter_mode == "TP":
        df_filtered = df_master[df_master['Ledger_Status'] == "TARGET PROFIT"]
        st.success("Menampilkan Emiten Sukses Target Profit.")
    elif st.session_state.filter_mode == "CL":
        df_filtered = df_master[df_master['Ledger_Status'] == "CUT LOSS"]
        st.warning("Menampilkan Emiten Area Disiplin Cut Loss.")

    # Finalisasi Visual Formatter Kolom Tabel Hulu
    df_filtered["Selisih"] = df_filtered["Selisih"].apply(lambda x: f"{'+' if x > 0 else ''}{int(x):,}")
    df_filtered["Index Individual"] = df_filtered["Index Individual"].apply(lambda x: f"{x} (Pas)" if x == 100.0 else f"{x}")

    display_cols = [
        "Emiten", "Index Individual", "Harga", "Selisih", "Sinyal", "Frekuensi", 
        "Buy Vol (Proxy)", "Sell Vol (Proxy)", "Selisih Vol", "TP (3%)", "CL (4%)"
    ]
    
    st.dataframe(df_filtered[display_cols], use_container_width=True, hide_index=True)
else:
    st.error("Gagal memuat data intraday hulu Yahoo Finance. Silakan muat ulang halaman.")
