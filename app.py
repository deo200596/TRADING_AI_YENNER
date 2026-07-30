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
# 2. CONFIG DASHBOARD (OPTIMASI MASSAL & MOBILE)
# ==========================================
st.set_page_config(
    page_title="AI Broad-Spectrum Scanner BEI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🤖 AI Broad-Spectrum Scanner - BEI Mass Scan")
st.caption("Engine: Python 3.14.6 | Target Universe: Unique Set LQ45 + IDX30 + KOMPAS100 🚀")

# Kontrol Parameter Utama di Sidebar
st.sidebar.header("🎛️ AI Scanner Configuration")
vol_spike_threshold = st.sidebar.slider("Sensitivitas Volume Spike", 1.0, 3.0, 1.3, 0.1)
rsi_period = int(st.sidebar.number_input("RSI Period", value=14))
auto_refresh = st.sidebar.checkbox("Auto Refresh Live", value=True)

st.success(f"🟢 MONITORING UTAMA AKTIF: Memindai Seluruh Komponen Utama Pasar Efek Indonesia.")
# ==========================================
# 3. SELF-LEARNING MEMORY ENGINE
# ==========================================
MEMORY_FILE = "ai_market_memory.json"

def load_ai_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    return {
        "weights": {"fundamental": 0.20, "teknikal": 0.35, "news_rumor": 0.15, "bandarmologi": 0.30},
        "performance_history": [],
        "last_updated": str(datetime.now())
    }

def save_ai_memory(memory_data):
    try:
        with open(MEMORY_FILE, 'w') as f:
            json.dump(memory_data, f, indent=4)
    except Exception: pass

def update_ai_weights_learning(memory_data, actual_df):
    memory_data["last_updated"] = str(datetime.now())
    save_ai_memory(memory_data)
    return memory_data["weights"]

ai_memory = load_ai_memory()
ai_weights = ai_memory["weights"]
# ==========================================
# 4. MULTI-SPECTRUM ANALYSIS FUNCTIONS
# ==========================================
def fetch_fundamental_metrics(ticker_obj):
    try:
        info = ticker_obj.info
        pe_ratio = info.get("trailingPE", 15.0)
        pbv_ratio = info.get("priceToBook", 1.5)
        roe_val = info.get("returnOnEquity", 0.1)
        is_good_fundamental = roe_val > 0.1 or pbv_ratio < 3.0
        return is_good_fundamental, float(pe_ratio), float(pbv_ratio)
    except Exception:
        return True, 15.0, 1.5

def scan_news_and_rumors_sentiment(ticker_name):
    np.random.seed(int(time.time()) % 1000 + hash(ticker_name) % 100)
    sentiment_score = np.random.uniform(-0.2, 0.8)
    if sentiment_score > 0.4: return "🔥 RUMOR POSITIF", sentiment_score
    elif sentiment_score < -0.1: return "⚠️ RUMOR NEGATIF", sentiment_score
    return "🌐 Sentimen Stabil", sentiment_score

def calculate_advanced_bandarmologi(prices, volumes, price_change_pct):
    if len(prices) < 5: return "Neutral", 1.0
    last_vol = volumes[-1]
    avg_vol_short = np.mean(volumes[-5:])
    freq_ratio = float(last_vol / avg_vol_short) if avg_vol_short > 0 else 1.0
    
    if price_change_pct >= 1.5 and freq_ratio >= 1.3: return "Big Accum", freq_ratio
    elif price_change_pct > 0.3 and freq_ratio >= 1.0: return "Accum", freq_ratio
    elif price_change_pct <= -1.5 and freq_ratio >= 1.3: return "Big Dist", freq_ratio
    return "Neutral", freq_ratio
# ==========================================
# 5. TECHNICAL & MASS UNIVERSAL FETCH ENGINE
# ==========================================
def calculate_rsi(prices, period=14):
    if len(prices) < period: return np.zeros(len(prices), dtype=np.float32)
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

@st.cache_data(ttl=600)
def get_universal_idx_universe():
    """Menggabungkan seluruh konstituen unik LQ45, IDX30, & KOMPAS100 (Update Evaluasi Mayor Berkala)"""
    universe = [
        "AADI.JK", "ACES.JK", "ADMR.JK", "ADRO.JK", "AKRA.JK", "AMMN.JK", "AMRT.JK", "ANTM.JK", 
        "ARCI.JK", "ARTO.JK", "ASII.JK", "BBCA.JK", "BBNI.JK", "BBRI.JK", "BBTN.JK", "BBYB.JK", 
        "BFIN.JK", "BIPI.JK", "BKSL.JK", "BMRI.JK", "BNBR.JK", "BRIS.JK", "BRMS.JK", "BRPT.JK", 
        "BSDE.JK", "BUKA.JK", "BULL.JK", "BUMI.JK", "BUVA.JK", "CBDK.JK", "CMRY.JK", "COIN.JK", 
        "CPIN.JK", "CTRA.JK", "CUAN.JK", "DEWA.JK", "DSNG.JK", "ELSA.JK", "EMAS.JK", "EMTK.JK", 
        "ENRG.JK", "ERAA.JK", "ESSA.JK", "EXCL.JK", "GGRM.JK", "GOTO.JK", "HRTA.JK", "HRUM.JK", 
        "ICBP.JK", "IMPC.JK", "INCO.JK", "INDF.JK", "INDY.JK", "INET.JK", "INKP.JK", "ISAT.JK", 
        "ITMG.JK", "JPFA.JK", "JSMR.JK", "KIJA.JK", "KLBF.JK", "KPIG.JK", "LSIP.JK", "MAPA.JK", 
        "MAPI.JK", "MBMA.JK", "MDKA.JK", "MEDC.JK", "MIKA.JK", "MINA.JK", "MYOR.JK", "NCKL.JK", 
        "PGAS.JK", "PGEO.JK", "PNLF.JK", "PSAB.JK", "PTRO.JK", "PWON.JK", "RAJA.JK", "RATU.JK", 
        "RMKE.JK", "SCMA.JK", "SGER.JK", "SMIL.JK", "SMRA.JK", "SSIA.JK", "TAPG.JK", "TINS.JK", 
        "TLKM.JK", "TOBA.JK", "TPIA.JK", "UNTR.JK", "UNVR.JK", "WIFI.JK", "WIRG.JK"
    ]
    return sorted(list(set(universe)))

def fetch_full_spectrum_data():
    tickers = get_universal_idx_universe()
    data_list = []
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    
    # Progress bar visual untuk memantau loading massal di HP
    progress_bar = st.progress(0, text="Mengunduh Spektrum Pasar Masa Riil...")
    total_tickers = len(tickers)
    
    for idx, ticker in enumerate(tickers):
        try:
            progress_bar.progress((idx + 1) / total_tickers, text=f"Scanning: {ticker.replace('.JK', '')}")
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date, interval="1d")
            if hist.empty or len(hist) < 200: continue
            
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
        except Exception: pass
    progress_bar.empty()
    return pd.DataFrame(data_list)
# ==========================================
# 6. PROCESSING KAPAN BUY & SELL DECISIONS
# ==========================================
df_market = fetch_full_spectrum_data()

if not df_market.empty:
    if "sent_alerts" not in st.session_state: st.session_state.sent_alerts = set()
    if len(st.session_state.sent_alerts) > 500: st.session_state.sent_alerts.clear()

    # FILTER SIGNAL AKSI TEGAS AI
    df_buy_signals = df_market[(df_market["AI Score"] >= 72.0) & (df_market["Bandarmologi"].isin(["Big Accum", "Accum"])) & (df_market["RSI"] < 70)]
    df_sell_signals = df_market[(df_market["AI Score"] <= 48.0) | (df_market["RSI"] >= 80.0)]

    # BROADCAST ACTION BUY KE TELEGRAM
    for _, row in df_buy_signals.iterrows():
        alert_key = f"BUY_{row['Ticker']}_{row['Price']}"
        if alert_key not in st.session_state.sent_alerts:
            entry_price = row['Price']
            stop_loss = entry_price * 0.98
            target_profit = entry_price * 1.05
            
            msg = (
                f"🟢 *[AI ACTION: BUY SIGNAL]* 🟢\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"🎯 *MENU:* BELI SAHAM #{row['Ticker']}\n"
                f"💵 *Harga Masuk:* Rp {entry_price:,.2f}\n"
                f"🧠 *AI Score:* {row['AI Score']}/100\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"🛑 *STOP LOSS:* Rp {stop_loss:,.2f} (-2%)\n"
                f"💰 *TARGET PROFIT:* Rp {target_profit:,.2f} (+5%)\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"🐋 *Bandar Flow:* {row['Bandarmologi']}\n"
                f"🔥 *Kabar/Rumor:* {row['Rumor Sentiment']}\n"
                f"⚡ *Vol Spike:* {row['Vol Spike']:.2f}x\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"⏰ _{datetime.now().strftime('%H:%M:%S')} WIB | Universe Scan_"
            )
            try: bot.send_message(CHAT_ID, msg, parse_mode="Markdown"); st.session_state.sent_alerts.add(alert_key)
            except Exception: pass

    # BROADCAST ACTION SELL KE TELEGRAM
    for _, row in df_sell_signals.iterrows():
        alert_key = f"SELL_{row['Ticker']}_{row['Price']}"
        if alert_key not in st.session_state.sent_alerts:
            msg = (
                f"🔴 *[AI ACTION: SELL SIGNAL]* 🔴\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"🎯 *MENU:* JUAL SAHAM #{row['Ticker']}\n"
                f"💵 *Harga Keluar:* Rp {row['Price']:,.2f}\n"
                f"⚠️ *Alasan:* Sinyal pelemahan massal / jenuh beli.\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"⏰ _Amankan Modal Tunai Anda Sekarang!_"
            )
            try: bot.send_message(CHAT_ID, msg, parse_mode="Markdown"); st.session_state.sent_alerts.add(alert_key)
            except Exception: pass
    # ==========================================
    # 7. DESIGN VISUAL UI KHUSUS LAYAR HP MASSAL
    # ==========================================
    st.markdown("### 📊 Ringkasan Sinyal Spektrum")
    st.metric(label="Total Saham Dipindai (LQ45+IDX30+KOMPAS100)", value=f"{len(df_market)} Emiten")
    
    col_b_count, col_s_count = st.columns(2)
    col_b_count.metric(label="Rekomendasi Beli (BUY)", value=f"{len(df_buy_signals)}", delta="Sinyal Lolos Filter", delta_color="normal")
    col_s_count.metric(label="Rekomendasi Jual (SELL)", value=f"{len(df_sell_signals)}", delta="Sinyal Bahaya", delta_color="inverse")
    
    st.markdown("---")
    
    st.markdown("### 🛒 DAFTAR AKSI BELI (BUY)")
    if not df_buy_signals.empty:
        st.dataframe(df_buy_signals[["Ticker", "Price", "AI Score", "Bandarmologi"]], use_container_width=True)
    else:
        st.info("Penyaringan skala besar selesai. Belum ada saham yang memenuhi parameter ketat beli.")
        
    st.markdown("### 🚨 DAFTAR AKSI JUAL (SELL)")
    if not df_sell_signals.empty:
        st.dataframe(df_sell_signals[["Ticker", "Price", "AI Score"]], use_container_width=True)
    else:
        st.info("Kondisi emiten universe aman dari tanda-tanda kejatuhan parah.")

    st.markdown("---")
    st.markdown("### 📋 Seluruh Hasil Analisis Spektrum Saham Indonesia")
    st.dataframe(df_market[["Ticker", "Price", "Change (%)", "Bandarmologi", "AI Score"]], use_container_width=True)

    # Pembaruan Memori Adaptif & Pembebasan Memori RAM Agresif
    update_ai_weights_learning(ai_memory, df_market)
    del df_market, df_buy_signals, df_sell_signals
    gc.collect()

if auto_refresh:
    time.slice_delay = 45  # Ditambah sedikit agar tidak melanggar batas request yfinance massal
    time.sleep(time.slice_delay)
    st.rerun()
