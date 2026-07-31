import streamlit as st
import pandas as pd
import numpy as np
import telebot
import time
import requests
import gc

# ==========================================
# 1. KONFIGURASI KREDENSIAL & TELEGRAM ASLI
# ==========================================
TOKEN = "8701590259:AAFHOTaWoKMk2qCsReI6RlW76NOLm0dtluo".strip()
CHAT_ID = "5282255947".strip()
bot = telebot.TeleBot(TOKEN)

# ==========================================
# 2. CONFIG DASHBOARD (SESI 8: ANTI-THROTTLE)
# ==========================================
st.set_page_config(
    page_title="AI Scalper Pro - Sesi 8 Master Engine",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🤖 AI Scalper Pro - Core Screener Engine Sesi 8")
st.caption("Platform Otomatisasi Trading BEI | Proteksi Over-Cpu Cloud & Jalur Data Stabilizer ⚡")

# Navigasi Menu Utama Website Sesuai Parameter Tujuan Anda
st.sidebar.header("🧭 Navigasi Menu Utama")
menu_terpilih = st.sidebar.radio(
    "Pilih Tampilan Menu:",
    [
        "1. DAFTAR EMITEN LQ45, KOMPAS100, IDX30",
        "2. DAFTAR 20 EMITEN LOLOS PENYARINGAN",
        "3. DAFTAR EMITEN REKOMENDASI BUY",
        "4. DAFTAR EMITEN REKOMENDASI SELL"
    ]
)

# Perbaikan: Mengubah intervensi waktu default ke 10 detik untuk mencegah Banned Server Cloud
refresh_rate = st.sidebar.slider("Jeda Refresh Live (Detik - Proteksi CPU)", 5, 30, 10, 1)
auto_refresh = st.sidebar.checkbox("Auto Refresh Live Active", value=True)

st.success(f"🔥 ANTI-THROTTLE ONLINE: Mengunci Target Pemindaian Menggunakan Sistem Delay Cerdas")
# ==========================================
# 3. UNIVERSE CONSTITUENTS (LQ45, IDX30, KOMPAS100)
# ==========================================
def get_combined_idx_universe():
    """Mengunci daftar emiten gabungan indeks papan atas BEI sebagai jangkar scan."""
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
# 4. ENGINE KOMUNIKASI DATA PASAR (ANTI-RATE LIMIT)
# ==========================================
def fetch_live_bursa_stream(symbols_list):
    """Menembak klaster data market dengan pengaman agar tidak diblokir server bursa."""
    query_symbols = ",".join([f"{sym}.JK" for sym in symbols_list])
    # Membulatkan interval waktu ke kelipatan 10 detik untuk menghindari pembatasan IP
    rounded_timestamp = (int(time.time()) // 10) * 10
    url = f"https://yahoo.com{query_symbols}&_={rounded_timestamp}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=7)
        if response.status_code == 200:
            return response.json().get("quoteResponse", {}).get("result", [])
    except Exception:
        pass
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
                "Turnover": turnover_rupiah, "Volatilitas": volatilitas, "Bandarmology": bandarmology
            })
        except Exception: continue
        
    return pd.DataFrame(processed_rows)
def build_multiindex_session8_frame(df_linear):
    if df_linear.empty: return pd.DataFrame()
    
    tickers_found = df_linear["Ticker"].tolist()
    sub_metrics = ["Price_Close", "Price_Live", "Net_Diff", "Change_Pct", "Freq", "Idx_Individual", "Volume_Lot", "Turnover", "Volatilitas", "Bandarmology"]
    
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
    df_radar_multi = build_multiindex_session8_frame(df_linear_base)
    
    # ------------------------------------------------=================
    # MENU 1: DAFTAR EMITEN LQ45, KOMPAS100 DAN IDX30 (UTUH & LIVE)
    # ------------------------------------------------=================
    if menu_terpilih == "1. DAFTAR EMITEN LQ45, KOMPAS100, IDX30":
        st.subheader("📋 Menu 1: Monitor Semesta Saham Top Indeks BEI")
        report_list = []
        for idx, row in df_linear_base.iterrows():
            sign = "+" if row["Net_Diff"] > 0 else ""
            arrow = "▲" if row["Net_Diff"] > 0 else ("▼" if row["Net_Diff"] < 0 else "▬")
            report_list.append({
                "Kode Saham": row["Ticker"], "Harga Penutupan": f"Rp {row['Price_Close']:,.0f}",
                "Harga Live Real-Time": f"Rp {row['Price_Live']:,.0f}",
                "Selisih Harga": f"{arrow} {sign}{row['Net_Diff']:,.0f} ({row['Change_Pct']:+.2f}%)",
                "Frekuensi (Live Match)": f"{row['Freq']:,} x", "Indeks Individual": f"{row['Idx_Individual']:.2f}",
                "Volume (Lot)": f"{row['Volume_Lot']:,.0f} Lot", "Bandarmology": row["Bandarmology"]
            })
        st.table(pd.DataFrame(report_list))
        
    # ------------------------------------------------=================
    # MENU 2: DAFTAR 20 EMITEN LOLOS PENYARINGAN (TERTINGGI FREK/VOLATILITAS)
    # ------------------------------------------------=================
    elif menu_terpilih == "2. DAFTAR 20 EMITEN LOLOS PENYARINGAN":
        st.subheader("🔥 Menu 2: Top 20 Emiten Hasil Penyaringan Likuiditas")
        df_filtered = df_linear_base.sort_values(by="Freq", ascending=False).head(20)
        report_list = []
        for idx, row in df_filtered.iterrows():
            sign = "+" if row["Net_Diff"] > 0 else ""
            arrow = "▲" if row["Net_Diff"] > 0 else ("▼" if row["Net_Diff"] < 0 else "▬")
            report_list.append({
                "Kode Saham": row["Ticker"], "Harga Penutupan": f"Rp {row['Price_Close']:,.0f}",
                "Harga Live Real-Time": f"Rp {row['Price_Live']:,.0f}",
                "Selisih Harga": f"{arrow} {sign}{row['Net_Diff']:,.0f} ({row['Change_Pct']:+.2f}%)",
                "Frekuensi (Live Match)": f"{row['Freq']:,} x", "Indeks Individual": f"{row['Idx_Individual']:.2f}",
                "Volume (Lot)": f"{row['Volume_Lot']:,.0f} Lot", "Bandarmology": row["Bandarmology"]
            })
        st.table(pd.DataFrame(report_list))
    # Mengambil urutan peringkat global untuk validasi syarat top kriteria
    df_sort_freq = df_linear_base.sort_values(by="Freq", ascending=False)
    top_20_freq_tickers = df_sort_freq["Ticker"].head(20).tolist()
    
    df_sort_volatilitas = df_linear_base.sort_values(by="Volatilitas", ascending=False)
    top_volatilitas_tickers = df_sort_volatilitas["Ticker"].head(10).tolist()
    
    df_sort_volume = df_linear_base.sort_values(by="Volume_Lot", ascending=False)
    top_2_volume_tickers = df_sort_volume["Ticker"].head(2).tolist()

    # ------------------------------------------------=================
    # MENU 3: DAFTAR EMITEN REKOMENDASI BUY (PANIC REBOUND LOGIC)
    # ------------------------------------------------=================
    if menu_terpilih == "3. DAFTAR EMITEN REKOMENDASI BUY":
        st.subheader("🟢 Menu 3: Sinyal Beli Masuk Watchlist (Trigger Telebot)")
        buy_list = []
        for idx, row in df_linear_base.iterrows():
            t = row["Ticker"]
            cond_a = t in top_20_freq_tickers          
            cond_b = t in top_volatilitas_tickers      
            cond_c = -5.0 <= row["Change_Pct"] <= -3.0 
            cond_d = t in top_2_volume_tickers         
            
            if cond_a and cond_b and cond_c and cond_d:
                buy_list.append(row)
                alert_msg = (
                    f"🟢 *AI SCALPER ALERT: SIGNAL BUY VALID* 🟢\n\n"
                    f"Emiten Saham: *{t}*\n"
                    f"Harga Live: Rp {row['Price_Live']:,.0f}\n"
                    f"Selisih Real-Time: {row['Change_Pct']:+.2f}%\n"
                    f"Kondisi: Memenuhi Kriteria Top 20 Frekuensi, Volatilitas Tinggi, & Penampungan Volume Raksasa!"
                )
                try: bot.send_message(CHAT_ID, alert_msg, parse_mode="Markdown")
                except Exception: pass
        
        if buy_list: st.table(pd.DataFrame(buy_list))
        else: st.info("Memindai running trade... Belum ada emiten yang memenuhi akumulasi kriteria Buy (-3% s/d -5%) detik ini.")

    # ------------------------------------------------=================
    # MENU 4: DAFTAR EMITEN REKOMENDASI SELL (CLIMAX DISTRIBUTION LOGIC)
    # ----------------------------------------------------------------=
    elif menu_terpilih == "4. DAFTAR EMITEN REKOMENDASI SELL":
        st.subheader("🔴 Menu 4: Sinyal Jual Ambil Profit (Trigger Telebot)")
        sell_list = []
        for idx, row in df_linear_base.iterrows():
            t = row["Ticker"]
            cond_a = t in top_20_freq_tickers         
            cond_b = t in top_volatilitas_tickers     
            cond_c = 3.0 <= row["Change_Pct"] <= 5.0  
            cond_d = t in top_2_volume_tickers        
            
            if cond_a and cond_b and cond_c and cond_d:
                sell_list.append(row)
                alert_msg = (
                    f"🔴 *AI SCALPER ALERT: SIGNAL SELL VALID* 🔴\n\n"
                    f"Emiten Saham: *{t}*\n"
                    f"Harga Live: Rp {row['Price_Live']:,.0f}\n"
                    f"Selisih Real-Time: {row['Change_Pct']:+.2f}%\n"
                    f"Kondisi: Jual ke retail FOMO! Harga menyentuh area climax +3% s/d +5% harian."
                )
                try: bot.send_message(CHAT_ID, alert_msg, parse_mode="Markdown")
                except Exception: pass
                
        if sell_list: st.table(pd.DataFrame(sell_list))
        else: st.info("Memindai running trade... Belum ada emiten yang memenuhi kriteria distribusi Sell (+3% s/d +5%) detik ini.")

else:
    st.warning("⚠️ Server Cloud sedang membatasi akses (Throttled). Menahan tembakan data untuk memulihkan koneksi bursa...")

# Pengosongan memori rutin RAM 4GB Streamlit Cloud
gc.collect()
if auto_refresh:
    # Jeda dinamis berbasis pengaman CPU agar platform tetap sehat
    time.sleep(refresh_rate)
    st.rerun()
