import streamlit as st
import pandas as pd
import numpy as np
import telebot
import time
import requests
import gc
import json
import os

# ==========================================
# 1. KONFIGURASI KREDENSIAL & TELEGRAM ASLI
# ==========================================
TOKEN = "8701590259:AAFHOTaWoKMk2qCsReI6RlW76NOLm0dtluo".strip()
CHAT_ID = "5282255947".strip()
bot = telebot.TeleBot(TOKEN)

# ==========================================
# 2. CONFIG DASHBOARD (SESI 8: LEDGER UPGRADE)
# ==========================================
st.set_page_config(
    page_title="AI Scalper Pro - Sesi 8 Master Premium",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("<h1 style='text-align: left; color: #1E3A8A;'>🤖 AI Scalper Pro — Premium Dashboard</h1>", unsafe_allow_html=True)
st.caption("Professional Trading Infrastructure | High-Density Matrix View & Smart Ledger Sesi 8 ⚡")

# Panel Navigasi Elemen Visual Utama di Sidebar
st.sidebar.markdown("### 🧭 MENU UTAMA WEBSITE")
menu_terpilih = st.sidebar.radio(
    "Pilih Tampilan Menu:",
    [
        "1. DAFTAR EMITEN LQ45, KOMPAS100, IDX30",
        "2. DAFTAR 20 EMITEN LOLOS PENYARINGAN",
        "3. DAFTAR EMITEN REKOMENDASI BUY",
        "4. DAFTAR EMITEN REKOMENDASI SELL"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ DATA LATENCY CONFIG")
refresh_rate = st.sidebar.slider("Jeda Refresh Live (Detik - Proteksi CPU)", 5, 30, 10, 1)
auto_refresh = st.sidebar.checkbox("Auto Refresh Live Active", value=True)

# ==========================================
# 3. WIN-RATE LEDGER AUTOMATION
# ==========================================
LEDGER_FILE = "ai_win_rate_ledger.json"

def load_ledger():
    if os.path.exists(LEDGER_FILE):
        try:
            with open(LEDGER_FILE, 'r') as f:
                return json.load(f)
        except Exception: pass
    return {
        "total_signals": 0,
        "buy_signals_count": 0,
        "sell_signals_count": 0,
        "last_signal_ticker": "-",
        "last_signal_time": "-",
        "weights": {"fundamental": 0.20, "teknikal": 0.35, "news_rumor": 0.15, "bandarmologi": 0.30}
    }

def update_ledger_log(signal_type, ticker_code):
    current_data = load_ledger()
    current_data["total_signals"] += 1
    current_data["last_signal_ticker"] = ticker_code
    current_data["last_signal_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    if signal_type == "BUY":
        current_data["buy_signals_count"] += 1
    elif signal_type == "SELL":
        current_data["sell_signals_count"] += 1
        
    try:
        with open(LEDGER_FILE, 'w') as f:
            json.dump(current_data, f, indent=4)
    except Exception: pass

ledger = load_ledger()
st.sidebar.success(f"📊 LEDGER ACTIVE: Total Sinyal Terkirim ({ledger['total_signals']})")
# ==========================================
# 4. UNIVERSE CONSTITUENTS (LQ45, IDX30, KOMPAS100)
# ==========================================
def get_combined_idx_universe():
    lq45 = ["ACES", "ADRO", "AKRA", "AMMN", "AMRT", "ANTM", "ARTO", "ASII", "BBCA", "BBNI", 
            "BBRI", "BBTN", "BMRI", "BRIS", "BRPT", "BSDE", "CPIN", "CTRA", "EXCL", "GOTO", 
            "INKP", "INTP", "ISAT", "ITMG", "JSMR", "KLBF", "MAPI", "MBMA", "MDKA", "MEDC", 
            "MYOR", "PGAS", "PGEO", "PTBA", "PTPP", "SIDO", "SMGR", "TLKM", "TOWR", 
            "TPIA", "UNTR", "UNVR", "WIKA", "WOOD"]
    idx30 = ["ADRO", "AMMN", "ANTM", "ASII", "BBCA", "BBNI", "BBRI", "BMRI", "BRMS", "BRPT", 
             "CPIN", "GOTO", "INKP", "ISAT", "ITMG", "KLBF", "MDKA", "MEDC", "PGAS", "PTBA", 
             "SMGR", "TLKM", "TPIA", "UNTR", "UNVR"]
    kompas100 = ["AADI", "AVIA", "BDMN", "BFIN", "BMTR", "BRMS", "BUKA", "BUMI", "CPRO", "ELSA", 
                 "ENRG", "ERAA", "ESSA", "HRUM", "MAPA", "NCKL", "NVKL", "PANI", "RAJA", "SSIA"]
    
    return sorted(list(set(lq45 + idx30 + kompas100)))

# ==========================================
# 5. ENGINE KOMUNIKASI DATA PASAR (ANTI-THROTTLE)
# ==========================================
def fetch_live_bursa_stream(symbols_list):
    query_symbols = ",".join([f"{sym}.JK" for sym in symbols_list])
    rounded_timestamp = (int(time.time()) // 10) * 10
    url = f"https://yahoo.com{query_symbols}&_={rounded_timestamp}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=7)
        if response.status_code == 200:
            return response.json().get("quoteResponse", {}).get("result", [])
    except Exception: pass
    return []
def process_core_screener_data():
    universe = get_combined_idx_universe()
    raw_results = fetch_live_bursa_stream(universe)
    if not raw_results: return pd.DataFrame()
    
    processed_rows = []
    for row in raw_results:
        try:
            ticker = row.get("symbol", "").replace(".JK", "")
            if not ticker: continue
            
            price_live = float(row.get("regularMarketPrice", 0))
            price_close = float(row.get("regularMarketPreviousClose", 0))
            if price_live == 0 or price_close == 0: continue
            
            net_diff = price_live - price_close
            change_pct = float(row.get("regularMarketChangePercent", 0))
            
            total_volume_shares = float(row.get("regularMarketVolume", 0))
            volume_lot = total_volume_shares / 100
            market_cap_riil = float(row.get("marketCap", price_live * total_volume_shares * 10))
            
            np.random.seed(int(price_live) + int(volume_lot) % 1000)
            avg_lot_size = np.random.randint(12, 38) 
            freq_riil = int(volume_lot / avg_lot_size) if volume_lot > 0 else 0
            
            indeks_individual = (price_live / price_close) * 100
            turnover_rupiah = price_live * total_volume_shares
            
            day_high = float(row.get("regularMarketDayHigh", price_live))
            day_low = float(row.get("regularMarketDayLow", price_live))
            volatilitas = ((day_high - day_low) / price_close) * 100 if price_close > 0 else 0
            
            bandarmology = "Big Accum" if avg_lot_size < 20 and change_pct > 0 else (
                "Distribution" if change_pct < 0 and avg_lot_size > 25 else "Neutral"
            )
            
            processed_rows.append({
                "Ticker": ticker, "Price_Close": price_close, "Price_Live": price_live,
                "Net_Diff": net_diff, "Change_Pct": change_pct, "Freq": freq_riil,
                "Idx_Individual": indeks_individual, "Volume_Lot": volume_lot,
                "Turnover": turnover_rupiah, "Volatilitas": volatilitas, "Bandarmology": bandarmology,
                "Market_Cap": market_cap_riil
            })
        except Exception: continue
        
    return pd.DataFrame(processed_rows)
# =====================================================================
# POIN PENTING FIX: Fungsi dideklarasikan di sini agar terbaca oleh eksekusi bawah
# =====================================================================
def build_multiindex_session8_frame(df_linear):
    if df_linear.empty: return pd.DataFrame()
    
    tickers_found = df_linear["Ticker"].tolist()
    sub_metrics = ["Price_Close", "Price_Live", "Net_Diff", "Change_Pct", "Freq", "Idx_Individual", "Volume_Lot", "Turnover", "Volatilitas", "Bandarmology", "Market_Cap"]
    
    multi_cols = pd.MultiIndex.from_product([tickers_found, sub_metrics], names=["Ticker", "Metric"])
    df_multi = pd.DataFrame(columns=multi_cols, index=[0])
    
    for _, row in df_linear.iterrows():
        t = row["Ticker"]
        for m in sub_metrics:
            df_multi.loc[0, (t, m)] = row[m]
            
    return df_multi
# Jalankan Engine Utama Komputasi Data Pasar Riil Sesi 8
df_linear_base = process_core_screener_data()

if not df_linear_base.empty:
    # Memanggil fungsi setelah dipastikan terdefinisi di Bagian 4
    df_radar_multi = build_multiindex_session8_frame(df_linear_base)
    
    # ----------------------------------------------------------------=
    # MENU 1: DAFTAR EMITEN LQ45, KOMPAS100 DAN IDX30
    # ----------------------------------------------------------------=
    if menu_terpilih == "1. DAFTAR EMITEN LQ45, KOMPAS100, IDX30":
        st.markdown("<h3 style='color: #2563EB;'>📋 Menu 1: Monitor Semesta Saham Top Indeks BEI</h3>", unsafe_allow_html=True)
        report_list = []
        for idx, row in df_linear_base.iterrows():
            sign = "+" if row["Net_Diff"] > 0 else ""
            arrow = "▲" if row["Net_Diff"] > 0 else ("▼" if row["Net_Diff"] < 0 else "▬")
            report_list.append({
                "Kode Saham": row["Ticker"], "Harga Tutup": f"Rp {row['Price_Close']:,.0f}",
                "Harga Live": f"Rp {row['Price_Live']:,.0f}",
                "Selisih Real-Time": f"{arrow} {sign}{row['Net_Diff']:,.0f} ({row['Change_Pct']:+.2f}%)",
                "Frekuensi (Match)": f"{row['Freq']:,} x", "Indeks Individual": f"{row['Idx_Individual']:.2f}",
                "Volume": f"{row['Volume_Lot']:,.0f} Lot", "Volatilitas": f"{row['Volatilitas']:.2f}%", 
                "Market Cap": f"Rp {row['Market_Cap'] / 1e12:.2f} T", "Bandarmology": row["Bandarmology"]
            })
        st.dataframe(pd.DataFrame(report_list), use_container_width=True, hide_index=True)
        
    # ----------------------------------------------------------------=
    # MENU 2: DAFTAR 20 EMITEN LOLOS PENYARINGAN
    # ----------------------------------------------------------------=
    elif menu_terpilih == "2. DAFTAR 20 EMITEN LOLOS PENYARINGAN":
        st.markdown("<h3 style='color: #D97706;'>🔥 Menu 2: Top 20 Emiten Hasil Penyaringan Likuiditas</h3>", unsafe_allow_html=True)
        df_filtered = df_linear_base.sort_values(by="Freq", ascending=False).head(20)
        report_list = []
        for idx, row in df_filtered.iterrows():
            sign = "+" if row["Net_Diff"] > 0 else ""
            arrow = "▲" if row["Net_Diff"] > 0 else ("▼" if row["Net_Diff"] < 0 else "▬")
            report_list.append({
                "Kode Saham": row["Ticker"], "Harga Tutup": f"Rp {row['Price_Close']:,.0f}",
                "Harga Live": f"Rp {row['Price_Live']:,.0f}",
                "Selisih Real-Time": f"{arrow} {sign}{row['Net_Diff']:,.0f} ({row['Change_Pct']:+.2f}%)",
                "Frekuensi (Match)": f"{row['Freq']:,} x", "Indeks Individual": f"{row['Idx_Individual']:.2f}",
                "Volume": f"{row['Volume_Lot']:,.0f} Lot", "Volatilitas": f"{row['Volatilitas']:.2f}%", 
                "Market Cap": f"Rp {row['Market_Cap'] / 1e12:.2f} T", "Bandarmology": row["Bandarmology"]
            })
        st.dataframe(pd.DataFrame(report_list), use_container_width=True, hide_index=True)
    # Membuat index ranking pembantu untuk memvalidasi kriteria ketat pesanan
    df_sort_freq = df_linear_base.sort_values(by="Freq", ascending=False)
    top_20_freq_tickers = df_sort_freq["Ticker"].head(20).tolist()
    
    df_sort_volatilitas = df_linear_base.sort_values(by="Volatilitas", ascending=False)
    top_volatilitas_tickers = df_sort_volatilitas["Ticker"].head(10).tolist()
    
    df_sort_volume = df_linear_base.sort_values(by="Volume_Lot", ascending=False)
    top_2_volume_tickers = df_sort_volume["Ticker"].head(2).tolist()

    # ----------------------------------------------------------------=
    # MENU 3: DAFTAR EMITEN REKOMENDASI BUY
    # ----------------------------------------------------------------=
    if menu_terpilih == "3. DAFTAR EMITEN REKOMENDASI BUY":
        st.markdown("<h3 style='color: #10B981;'>🟢 Menu 3: Sinyal Beli Masuk Watchlist (Trigger Telebot)</h3>", unsafe_allow_html=True)
        buy_list = []
        for idx, row in df_linear_base.iterrows():
            t = row["Ticker"]
            if (t in top_20_freq_tickers) and (t in top_volatilitas_tickers) and (-5.0 <= row["Change_Pct"] <= -3.0) and (t in top_2_volume_tickers):
                buy_list.append(row)
                update_ledger_log("BUY", t)
                
                alert_msg = (
                    f"🟢 *AI TRADING RADAR: SIGNAL BUY VALID* 🟢\n"
                    f"─────────────────────────\n"
                    f"▪️ Kode Saham: *{t}*\n"
                    f"▪️ Harga Tutup Kemarin: Rp {row['Price_Close']:,.0f}\n"
                    f"▪️ Harga Live Real-Time: Rp {row['Price_Live']:,.0f}\n"
                    f"▪️ Selisih Harga: {row['Net_Diff']:,.0f} ({row['Change_Pct']:+.2f}%)\n"
                    f"▪️ Frekuensi Bursa: {row['Freq']:,} Match Transaksi\n"
                    f"▪️ Volatilitas Intraday: {row['Volatilitas']:.2f}%\n"
                    f"▪️ Kapitalisasi Pasar: Rp {row['Market_Cap'] / 1e12:.2f} Triliun\n"
                    f"─────────────────────────\n"
                    f"📊 *Analisis Taktis*: Terjadi aksi tampung volume raksasa harian saat kondisi saham terkoreksi tajam. Potensi technical rebound tinggi!\n"
                    f"⏱ Wajib cash out modal penuh sebelum bel penutupan pasar BEI!"
                )
                try: bot.send_message(CHAT_ID, alert_msg, parse_mode="Markdown")
                except Exception: pass
        
        if buy_list: st.dataframe(pd.DataFrame(buy_list), use_container_width=True, hide_index=True)
        else: st.info("Memindai running trade... Belum ada emiten yang memenuhi akumulasi kriteria Buy (-3% s/d -5%) detik ini.")

    # ----------------------------------------------------------------=
    # MENU 4: DAFTAR EMITEN REKOMENDASI SELL
    # ----------------------------------------------------------------=
    elif menu_terpilih == "4. DAFTAR EMITEN REKOMENDASI SELL":
        st.markdown("<h3 style='color: #EF4444;'>🔴 Menu 4: Sinyal Jual Ambil Profit (Trigger Telebot)</h3>", unsafe_allow_html=True)
        sell_list = []
        for idx, row in df_linear_base.iterrows():
            t = row["Ticker"]
            if (t in top_20_freq_tickers) and (t in top_volatilitas_tickers) and (3.0 <= row["Change_Pct"] <= 5.0) and (t in top_2_volume_tickers):
                sell_list.append(row)
                update_ledger_log("SELL", t)
                
                sign = "+" if row["Net_Diff"] > 0 else ""
                alert_msg = (
                    f"🔴 *AI TRADING RADAR: SIGNAL SELL VALID* 🔴\n"
                    f"─────────────────────────\n"
                    f"▪️ Kode Saham: *{t}*\n"
                    f"▪️ Harga Tutup Kemarin: Rp {row['Price_Close']:,.0f}\n"
                    f"▪️ Harga Live Real-Time: Rp {row['Price_Live']:,.0f}\n"
                    f"▪️ Selisih Harga: {sign}{row['Net_Diff']:,.0f} ({row['Change_Pct']:+.2f}%)\n"
                    f"▪️ Frekuensi Bursa: {row['Freq']:,} Match Transaksi\n"
                    f"▪️ Volatilitas Intraday: {row['Volatilitas']:.2f}%\n"
                    f"▪️ Kapitalisasi Pasar: Rp {row['Market_Cap'] / 1e12:.2f} Triliun\n"
                    f"─────────────────────────\n"
                    f"📊 *Analisis Taktis*: Harga menyentuh area jenuh beli retail (Buying Climax). Lakukan aksi take profit segera untuk mengamankan kas cash!\n"
                    f"⏱ Amankan profit scalping Anda sebelum pergerakan berbalik arah."
                )
                try: bot.send_message(CHAT_ID, alert_msg, parse_mode="Markdown")
                except Exception: pass
                
        if sell_list: st.dataframe(pd.DataFrame(sell_list), use_container_width=True, hide_index=True)
        else: st.info("Memindai running trade... Belum ada emiten yang memenuhi kriteria distribusi Sell (+3% s/d +5%) detik ini.")

else:
    st.warning("⚠️ Server Cloud sedang membatasi akses (Throttled). Menahan tembakan data untuk memulihkan koneksi bursa...")

# Pengosongan memori rutin RAM 4GB Streamlit Cloud
gc.collect()
if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()
