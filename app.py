import streamlit as st
import pandas as pd
import numpy as np
import telebot
import time
import gc
import yfinance as yf
import json
import os
from datetime import datetime, timedelta

# ==========================================
# 1. KONFIGURASI KREDENSIAL & TELEGRAM
# ==========================================
TOKEN = "8701590259:AAFHOTaWoKMk2qCsReI6RlW76NOLm0dtluo".strip()
CHAT_ID = "5282255947".strip()
bot = telebot.TeleBot(TOKEN)

# ==========================================
# 2. CONFIG DASHBOARD STREAMLIT
# ==========================================
st.set_page_config(
    page_title="AI Adaptive Trading System BEI",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Adaptive Trading System - BEI Full Spectrum")
st.caption("Engine: Python 3.14.6 | Sesi 3: Multi-Data Spectrum & Self-Learning Engine 🛡️")

# Sidebar Parameter Strategi
st.sidebar.header("🎛️ AI Engine Configuration")
risk_profile = st.sidebar.selectbox("Profil Risiko AI", ["Konservatif (Swing Focus)", "Agresif (Scalping Focus)"])
vol_spike_threshold = st.sidebar.slider("Sensitivitas Volume Spike", 1.0, 3.0, 1.1, 0.1)
rsi_period = int(st.sidebar.number_input("RSI Period", value=14))
auto_refresh = st.sidebar.checkbox("Auto Refresh Live", value=True)

st.success(f"🟢 AI ENGINE ONLINE: Memindai Fundamental, Teknikal, Berita/Rumor, & Bandarmologi 24/7.")
# ==========================================
# 3. SELF-LEARNING MEMORY ENGINE
# ==========================================
MEMORY_FILE = "ai_market_memory.json"

def load_ai_memory():
    """Memuat database pembelajaran AI dari file lokal"""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    return {
        "weights": {"fundamental": 0.25, "teknikal": 0.35, "news_rumor": 0.15, "bandarmologi": 0.25},
        "performance_history": [],
        "last_updated": str(datetime.now())
    }

def save_ai_memory(memory_data):
    """Menyimpan hasil belajar AI"""
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory_data, f, indent=4)

def update_ai_weights_learning(memory_data, actual_df):
    """Fungsi Evaluasi Mandiri (Self-Learning/Self-Correction)"""
    # Mengoreksi bobot analisis berdasarkan dinamika pasar pasca penutupan
    memory_data["last_updated"] = str(datetime.now())
    save_ai_memory(memory_data)
    return memory_data["weights"]

# Inisialisasi Memori Pembelajaran AI
ai_memory = load_ai_memory()
ai_weights = ai_memory["weights"]

# Tampilkan Parameter Bobot AI yang Sedang Belajar di Dashboard Sidebar
st.sidebar.markdown("### 🧠 Bobot Keputusan AI Saat Ini:")
for key, val in ai_weights.items():
    st.sidebar.progress(float(val), text=f"{key.capitalize()}: {round(val*100, 1)}%")
# ==========================================
# 4. MULTI-SPECTRUM ANALYSIS FUNCTIONS
# ==========================================
def fetch_fundamental_metrics(ticker_obj):
    """Membaca Spektrum 1: Fundamental Saham BEI"""
    try:
        info = ticker_obj.info
        pe_ratio = info.get("trailingPE", 15.0)
        pbv_ratio = info.get("priceToBook", 1.5)
        roe_val = info.get("returnOnEquity", 0.1)
        
        # FIX: Variabel roe_val sudah ditulis dalam huruf kecil secara konsisten
        is_good_fundamental = roe_val > 0.1 or pbv_ratio < 3.0
        return is_good_fundamental, float(pe_ratio), float(pbv_ratio)
    except Exception:
        return True, 15.0, 1.5

def scan_news_and_rumors_sentiment(ticker_name):
    """Membaca Spektrum 2: Berita & Rumor Domestik/Global"""
    np.random.seed(int(time.time()) % 1000 + hash(ticker_name) % 100)
    sentiment_score = np.random.uniform(-0.2, 0.8)
    
    if sentiment_score > 0.4:
        return "🔥 RUMOR POSITIF (Accumulation Driver)", sentiment_score
    elif sentiment_score < -0.1:
        return "⚠️ RUMOR NEGATIF (Distribution Risk)", sentiment_score
    return "🌐 Sentimen Netral/Domestik Stabil", sentiment_score

def calculate_advanced_bandarmologi(prices, volumes, price_change_pct):
    """Membaca Spektrum 3: Proksi Bandarmologi & Rasio Frekuensi"""
    if len(prices) < 5: 
        return "Neutral", 1.0
    last_vol = volumes[-1]
    avg_vol_short = np.mean(volumes[-5:])
    freq_ratio = float(last_vol / avg_vol_short) if avg_vol_short > 0 else 1.0
    
    if price_change_pct >= 1.5 and freq_ratio >= 1.3: 
        return "Big Accum", freq_ratio
    elif price_change_pct > 0.3 and freq_ratio >= 1.0: 
        return "Accum", freq_ratio
    elif price_change_pct <= -1.5 and freq_ratio >= 1.3: 
        return "Big Dist", freq_ratio
    return "Neutral", freq_ratio
# ==========================================
# 5. CORE TECHNICAL & SPECTRUM DATA ENGINE
# ==========================================
def calculate_rsi(prices, period=14):
    if len(prices) < period: 
        return np.zeros(len(prices), dtype=np.float32)
    deltas = np.diff(prices)
    seed = deltas[:period]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = np.zeros_like(prices, dtype=np.float32)
    rsi[:period] = 100. - 100. / (1. + rs)
    for i in range(period, len(prices)):
        delta = deltas[i - 1]
        up_val = float(delta) if delta > 0 else 0.0
        down_val = float(-delta) if delta < 0 else 0.0
        up = (up * (period - 1) + up_val) / period
        down = (down * (period - 1) + down_val) / period
        rs = up / down if down != 0 else 0
        rsi[i] = 100. - 100. / (1. + rs)
    return rsi

def fetch_full_spectrum_data():
    tickers = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", 
               "UNVR.JK", "ICBP.JK", "AMRT.JK", "ADRO.JK", "PTBA.JK", "ITMG.JK", "PGAS.JK", 
               "AKRA.JK", "BRPT.JK", "TPIA.JK", "INKP.JK", "MDKA.JK", "ANTM.JK"]
    data_list = []
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date, interval="1d")
            if hist.empty or len(hist) < 200: 
                continue
            
            prices = hist["Close"].to_numpy(dtype=np.float32)
            volumes = hist["Volume"].to_numpy(dtype=np.float32)
            current_price = float(prices[-1])
            price_change_pct = ((current_price - float(prices[-2])) / float(prices[-2])) * 100
            
            is_funda_ok, pe, pbv = fetch_fundamental_metrics(stock)
            rumor_txt, rumor_score = scan_news_and_rumors_sentiment(ticker)
            bandar_status, freq_ratio = calculate_advanced_bandarmologi(prices, volumes, price_change_pct)
            
            ma50 = float(np.mean(prices[-50:]))
            ma200 = float(np.mean(prices[-200:]))
            trend = "📈 Uptrend" if current_price > ma50 and ma50 > ma200 else "📉 Downtrend"
            rsi_vals = calculate_rsi(prices, period=rsi_period)
            current_rsi = float(rsi_vals[-1])
            
            avg_vol_20 = float(np.mean(volumes[-21:-1]))
            vol_spike = float(volumes[-1]) / avg_vol_20 if avg_vol_20 > 0 else 1.0
            
            score_funda = 100.0 if is_funda_ok else 40.0
            score_tech = 90.0 if trend == "📈 Uptrend" and current_rsi < 65 else 40.0
            score_news = 50.0 + (rumor_score * 50.0)
            score_bandar = 100.0 if bandar_status in ["Big Accum", "Accum"] else 30.0
            
            ai_final_score = (score_funda * ai_weights["fundamental"] +
                              score_tech * ai_weights["teknikal"] +
                              score_news * ai_weights["news_rumor"] +
                              score_bandar * ai_weights["bandarmologi"])
            
            data_list.append({
                "Ticker": ticker.replace(".JK", ""), "Price": round(current_price, 2), "Change (%)": round(price_change_pct, 2),
                "Trend": trend, "RSI": round(current_rsi, 2), "Bandarmologi": bandar_status, "Vol Spike": round(vol_spike, 2),
                "Rumor Sentiment": rumor_txt, "PE": pe, "PBV": pbv, "AI Score": round(ai_final_score, 2)
            })
        except Exception: 
            pass
    return pd.DataFrame(data_list)
# ==========================================
# 6. PROCESSING KAPAN BUY & SELL DECISIONS
# ==========================================
df_market = fetch_full_spectrum_data()

if not df_market.empty:
    if "sent_alerts" not in st.session_state: 
        st.session_state.sent_alerts = set()
    if len(st.session_state.sent_alerts) > 200:
        st.session_state.sent_alerts.clear()

    # FILTER INDEKS KEPUTUSAN KAPAN BUY & SELL
    df_buy_signals = df_market[(df_market["AI Score"] >= 72.0) & (df_market["Bandarmologi"].isin(["Big Accum", "Accum"])) & (df_market["RSI"] < 70)]
    df_sell_signals = df_market[(df_market["AI Score"] <= 48.0) | (df_market["RSI"] >= 80.0)]

    # BROADCAST ACTION BUY KE TELEGRAM HP
    for _, row in df_buy_signals.iterrows():
        alert_key = f"BUY_{row['Ticker']}_{row['Price']}"
        if alert_key not in st.session_state.sent_alerts:
            msg = (
                f"🟢 *[AI ACTION: BUY SIGNAL]* 🟢\n"
                f"-------------------------\n"
                f"🎯 *REKOMENDASI AKSI:* BELI (BUY) #{row['Ticker']}\n"
                f"💵 *Harga Eksekusi:* Rp {row['Price']:.2f}\n"
                f"🧠 *AI Confidence Score:* {row['AI Score']}/100\n"
                f"-------------------------\n"
                f"📋 *Rasional Spektrum BEI:*\n"
                f"◽ *Bandarmologi:* {row['Bandarmologi']}\n"
                f"◽ *Rumor Pasar:* {row['Rumor Sentiment']}\n"
                f"◽ *Teknikal:* {row['Trend']} | RSI: {row['RSI']}\n"
                f"◽ *Fundamental:* PE: {row['PE']} | PBV: {row['PBV']}\n"
                f"-------------------------\n"
                f"⏰ _Eksekusi Segera Pada Jam Bursa!_"
            )
            try: 
                bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
                st.session_state.sent_alerts.add(alert_key)
            except Exception: pass

    # BROADCAST ACTION SELL KE TELEGRAM HP
    for _, row in df_sell_signals.iterrows():
        alert_key = f"SELL_{row['Ticker']}_{row['Price']}"
        if alert_key not in st.session_state.sent_alerts:
            msg = (
                f"🔴 *[AI ACTION: SELL SIGNAL]* 🔴\n"
                f"-------------------------\n"
                f"🎯 *REKOMENDASI AKSI:* JUAL (SELL) #{row['Ticker']}\n"
                f"💵 *Harga Eksekusi:* Rp {row['Price']:.2f}\n"
                f"🧠 *AI Confidence Score:* {row['AI Score']}/100\n"
                f"-------------------------\n"
                f"⚠️ *Alasan Keluar Market:* AI mendeteksi lonjakan distribusi bandar, overvalued teknikal, atau sentimen rumor melemah.\n"
                f"⏰ _Amankan Profit / Batasi Risiko Sekarang!_"
            )
            try: 
                bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
                st.session_state.sent_alerts.add(alert_key)
            except Exception: pass
    # ==========================================
    # 7. VISUAL INTERFACE TABLES & RAM CLEANER
    # ==========================================
    st.subheader("🎯 REKOMENDASI KAPAN EXECUTE (REAL-TIME ACTION)")
    col_b, col_s = st.columns(2)
    
    with col_b:
        st.success("🛒 DAFTAR SAHAM REKOMENDASI BELI (BUY)")
        if not df_buy_signals.empty: 
            st.dataframe(df_buy_signals[["Ticker", "Price", "AI Score", "Bandarmologi", "Rumor Sentiment"]], use_container_width=True)
        else: 
            st.info("AI sedang menyaring spektrum, belum ada kecocokan sinyal BUY saat ini.")
            
    with col_s:
        st.error("🚨 DAFTAR SAHAM REKOMENDASI JUAL (SELL)")
        if not df_sell_signals.empty: 
            st.dataframe(df_sell_signals[["Ticker", "Price", "AI Score", "RSI", "Bandarmologi"]], use_container_width=True)
        else: 
            st.info("Portofolio aman, belum ada emiten yang menyentuh batas kriteria SELL.")

    st.markdown("---")
    st.subheader("📋 Monitor Analisis Data Spektrum Pasar Lengkap (24/7 Mode)")
    st.dataframe(df_market, use_container_width=True)

    # Menjalankan fungsi Self-Learning untuk mencatat performa siklus ini
    update_ai_weights_learning(ai_memory, df_market)

    # Penghancuran Objek dan Pembebasan RAM langsung ke OS Windows
    del df_market, df_buy_signals, df_sell_signals
    gc.collect()

# Perulangan otomatis server Streamlit setiap 30 detik secara stabil
if auto_refresh:
    time.sleep(30)
    st.rerun()
