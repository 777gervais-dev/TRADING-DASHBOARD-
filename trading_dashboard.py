import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="PRO TRADING TERMINAL",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CUSTOM CSS – Dark terminal aesthetic
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;600&display=swap');

:root {
    --bg-primary: #050a0f;
    --bg-secondary: #0a1520;
    --bg-card: #0d1e2e;
    --accent-green: #00ff88;
    --accent-cyan: #00d4ff;
    --accent-orange: #ff6b35;
    --accent-red: #ff2d55;
    --accent-yellow: #ffd700;
    --text-primary: #e0f0ff;
    --text-muted: #4a7090;
    --border: #1a3a5c;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}

h1, h2, h3 {
    font-family: 'Orbitron', monospace !important;
    color: var(--accent-cyan) !important;
    letter-spacing: 2px !important;
}

.stMetric {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 12px !important;
}

.stMetric label {
    font-family: 'Share Tech Mono', monospace !important;
    color: var(--text-muted) !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

.stMetric [data-testid="stMetricValue"] {
    font-family: 'Orbitron', monospace !important;
    color: var(--accent-green) !important;
    font-size: 20px !important;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Share Tech Mono', monospace !important;
    color: var(--text-muted) !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}

.stTabs [aria-selected="true"] {
    color: var(--accent-cyan) !important;
    border-bottom: 2px solid var(--accent-cyan) !important;
}

.stSelectbox select, .stSelectbox > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    font-family: 'Share Tech Mono', monospace !important;
}

.stButton > button {
    background: linear-gradient(135deg, #00d4ff22, #00ff8822) !important;
    border: 1px solid var(--accent-cyan) !important;
    color: var(--accent-cyan) !important;
    font-family: 'Share Tech Mono', monospace !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    border-radius: 4px !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #00d4ff44, #00ff8844) !important;
    box-shadow: 0 0 15px #00d4ff44 !important;
}

.header-banner {
    background: linear-gradient(90deg, #050a0f, #0a1a2e, #050a0f);
    border-bottom: 1px solid var(--border);
    padding: 10px 0;
    margin-bottom: 20px;
    text-align: center;
}

.signal-buy {
    background: linear-gradient(135deg, #00ff8811, #00ff8833);
    border: 1px solid var(--accent-green);
    border-radius: 6px;
    padding: 8px 16px;
    color: var(--accent-green);
    font-family: 'Orbitron', monospace;
    font-size: 12px;
    font-weight: 700;
    text-align: center;
    letter-spacing: 2px;
}

.signal-sell {
    background: linear-gradient(135deg, #ff2d5511, #ff2d5533);
    border: 1px solid var(--accent-red);
    border-radius: 6px;
    padding: 8px 16px;
    color: var(--accent-red);
    font-family: 'Orbitron', monospace;
    font-size: 12px;
    font-weight: 700;
    text-align: center;
    letter-spacing: 2px;
}

.signal-neutral {
    background: linear-gradient(135deg, #ffd70011, #ffd70033);
    border: 1px solid var(--accent-yellow);
    border-radius: 6px;
    padding: 8px 16px;
    color: var(--accent-yellow);
    font-family: 'Orbitron', monospace;
    font-size: 12px;
    font-weight: 700;
    text-align: center;
    letter-spacing: 2px;
}

.pivot-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 15px;
    margin: 5px 0;
}

.corr-positive { color: #00ff88 !important; }
.corr-negative { color: #ff2d55 !important; }
.corr-neutral  { color: #ffd700 !important; }

div[data-testid="stHorizontalBlock"] > div {
    background: transparent !important;
}

.stDataFrame { font-family: 'Share Tech Mono', monospace !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ASSET DEFINITIONS
# ─────────────────────────────────────────────
FUTURES = {
    "GOLD (GC)":    "GC=F",
    "Mini GOLD (MGC)": "MGC=F",
    "WTI Crude (CL)": "CL=F",
    "Mini WTI (MCL)": "MCL=F",
    "S&P 500 (ES)": "ES=F",
    "NQ100 (NQ)":   "NQ=F",
    "EUR/USD Fut (6E)": "6E=F",
}

FOREX = {
    "EUR/USD":  "EURUSD=X",
    "GBP/USD":  "GBPUSD=X",
    "USD/JPY":  "USDJPY=X",
    "AUD/USD":  "AUDUSD=X",
    "USD/CHF":  "USDCHF=X",
    "USD/CAD":  "USDCAD=X",
    "NZD/USD":  "NZDUSD=X",
}

CRYPTO = {
    "XAU/USD":  "GC=F",      # Gold spot proxy
    "BTC/USD":  "BTC-USD",
}

ALL_ASSETS = {**FUTURES, **FOREX, **CRYPTO}

PIVOT_ASSETS = {
    "GOLD (GC=F)":   "GC=F",
    "Mini GOLD":     "MGC=F",
    "WTI Crude":     "CL=F",
    "Mini WTI":      "MCL=F",
    "ES (S&P500)":   "ES=F",
    "NQ100":         "NQ=F",
    "6E (EUR Fut)":  "6E=F",
    "XAU/USD":       "GC=F",
    "BTC/USD":       "BTC-USD",
}

# ─────────────────────────────────────────────
# DATA FUNCTIONS
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_price_data(ticker, period="60d", interval="1d"):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if df.empty:
            return None
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        return df
    except:
        return None

@st.cache_data(ttl=60)
def fetch_live_price(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.fast_info
        return {
            "price": round(info.last_price, 5) if info.last_price else None,
            "change": round(info.last_price - info.previous_close, 5) if info.last_price and info.previous_close else None,
            "pct": round((info.last_price - info.previous_close) / info.previous_close * 100, 2) if info.last_price and info.previous_close else None,
        }
    except:
        return {"price": None, "change": None, "pct": None}

def compute_pivot_points(df):
    """Classic + Camarilla + Fibonacci pivot points from last completed candle"""
    if df is None or len(df) < 2:
        return {}
    
    row = df.iloc[-2]  # last completed candle
    H = float(row['High'])
    L = float(row['Low'])
    C = float(row['Close'])
    O = float(row.get('Open', C))

    # Classic
    PP = (H + L + C) / 3
    R1 = 2 * PP - L
    S1 = 2 * PP - H
    R2 = PP + (H - L)
    S2 = PP - (H - L)
    R3 = H + 2 * (PP - L)
    S3 = L - 2 * (H - PP)

    # Fibonacci
    fib_range = H - L
    FPP = PP
    FR1 = PP + 0.382 * fib_range
    FR2 = PP + 0.618 * fib_range
    FR3 = PP + 1.000 * fib_range
    FS1 = PP - 0.382 * fib_range
    FS2 = PP - 0.618 * fib_range
    FS3 = PP - 1.000 * fib_range

    # Camarilla
    CR1 = C + fib_range * 1.1 / 12
    CR2 = C + fib_range * 1.1 / 6
    CR3 = C + fib_range * 1.1 / 4
    CR4 = C + fib_range * 1.1 / 2
    CS1 = C - fib_range * 1.1 / 12
    CS2 = C - fib_range * 1.1 / 6
    CS3 = C - fib_range * 1.1 / 4
    CS4 = C - fib_range * 1.1 / 2

    return {
        "classic": {"PP": PP, "R1": R1, "R2": R2, "R3": R3, "S1": S1, "S2": S2, "S3": S3},
        "fibonacci": {"PP": FPP, "R1": FR1, "R2": FR2, "R3": FR3, "S1": FS1, "S2": FS2, "S3": FS3},
        "camarilla": {"R1": CR1, "R2": CR2, "R3": CR3, "R4": CR4, "S1": CS1, "S2": CS2, "S3": CS3, "S4": CS4},
        "prev_H": H, "prev_L": L, "prev_C": C,
    }

def compute_liquidity_zones(df, window=20):
    """Detect liquidity zones: swing highs/lows clusters + volume nodes"""
    if df is None or len(df) < window:
        return {"highs": [], "lows": [], "vwap": None}

    closes = df['Close'].values.flatten()
    highs = df['High'].values.flatten()
    lows = df['Low'].values.flatten()
    volumes = df['Volume'].values.flatten() if 'Volume' in df.columns else np.ones(len(closes))

    # Swing highs / lows
    swing_highs = []
    swing_lows = []
    for i in range(2, len(highs) - 2):
        if highs[i] == max(highs[i-2:i+3]):
            swing_highs.append(float(highs[i]))
        if lows[i] == min(lows[i-2:i+3]):
            swing_lows.append(float(lows[i]))

    # Cluster nearby levels (merge within 0.3%)
    def cluster_levels(levels, tolerance=0.003):
        if not levels:
            return []
        levels = sorted(levels)
        clusters = [[levels[0]]]
        for l in levels[1:]:
            if abs(l - clusters[-1][-1]) / clusters[-1][-1] < tolerance:
                clusters[-1].append(l)
            else:
                clusters.append([l])
        return [{"level": np.mean(c), "strength": len(c)} for c in clusters]

    # VWAP
    try:
        tp = (df['High'].values.flatten() + df['Low'].values.flatten() + df['Close'].values.flatten()) / 3
        vwap = float(np.sum(tp * volumes) / np.sum(volumes)) if np.sum(volumes) > 0 else None
    except:
        vwap = None

    # Volume profile (simple)
    price_min = float(np.min(lows[-window:]))
    price_max = float(np.max(highs[-window:]))
    bins = 20
    bin_size = (price_max - price_min) / bins
    vol_profile = []
    if bin_size > 0:
        for i in range(bins):
            lo = price_min + i * bin_size
            hi = lo + bin_size
            mask = (closes[-window:] >= lo) & (closes[-window:] < hi)
            v = float(np.sum(volumes[-window:][mask])) if np.any(mask) else 0
            vol_profile.append({"price": (lo + hi) / 2, "volume": v})

    # POC (Point of Control) – highest volume node
    poc = max(vol_profile, key=lambda x: x["volume"])["price"] if vol_profile else None

    return {
        "highs": cluster_levels(swing_highs),
        "lows": cluster_levels(swing_lows),
        "vwap": vwap,
        "poc": poc,
        "vol_profile": vol_profile,
    }

@st.cache_data(ttl=600)
def build_correlation_matrix(tickers_dict, period="60d"):
    closes = {}
    for name, ticker in tickers_dict.items():
        df = fetch_price_data(ticker, period=period)
        if df is not None and 'Close' in df.columns:
            s = df['Close'].squeeze()
            closes[name] = s
    if len(closes) < 2:
        return None
    df_all = pd.DataFrame(closes).dropna(how='all').ffill().dropna()
    if df_all.empty or len(df_all) < 5:
        return None
    return df_all.pct_change().dropna().corr()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 10px 0 20px 0;'>
        <span style='font-family:Orbitron,monospace; font-size:18px; color:#00d4ff; letter-spacing:3px;'>⚡ TRADING TERMINAL</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎛️ Configuration")

    selected_pivot = st.selectbox("Actif pour Pivots", list(PIVOT_ASSETS.keys()), index=0)
    pivot_tf = st.selectbox("Timeframe Pivots", ["1d", "1wk", "1mo"], index=0)
    pivot_type = st.selectbox("Type de Pivots", ["Classic", "Fibonacci", "Camarilla", "Tous"], index=0)

    st.markdown("---")
    st.markdown("### 📊 Corrélations")
    corr_period = st.selectbox("Période corrélations", ["30d", "60d", "90d"], index=1)
    corr_scope = st.multiselect(
        "Groupes d'actifs",
        ["Futures", "Forex", "Crypto"],
        default=["Futures", "Forex", "Crypto"]
    )

    st.markdown("---")
    st.markdown("### 💧 Liquidités")
    liq_asset = st.selectbox("Actif Liquidité", list(PIVOT_ASSETS.keys()), index=0)
    liq_tf = st.selectbox("TF Liquidité", ["1h", "4h", "1d"], index=2)

    st.markdown("---")
    refresh = st.button("🔄 RAFRAÎCHIR", use_container_width=True)
    if refresh:
        st.cache_data.clear()
        st.rerun()

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class='header-banner'>
    <span style='font-family:Orbitron,monospace; font-size:26px; font-weight:900; 
    color:#00d4ff; letter-spacing:6px; text-shadow: 0 0 20px #00d4ff66;'>
    ⚡ PRO TRADING TERMINAL
    </span>
    <br>
    <span style='font-family:Share Tech Mono,monospace; font-size:11px; color:#4a7090; letter-spacing:3px;'>
    FUTURES • FOREX • CRYPTO — POWERED BY YFINANCE
    </span>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LIVE PRICES TICKER BAR
# ─────────────────────────────────────────────
st.markdown("#### 📡 Prix en Temps Réel")
key_assets = {
    "GC=F": "GOLD", "ES=F": "S&P500", "NQ=F": "NQ100",
    "CL=F": "WTI", "EURUSD=X": "EUR/USD", "BTC-USD": "BTC/USD"
}

cols = st.columns(len(key_assets))
for i, (ticker, name) in enumerate(key_assets.items()):
    data = fetch_live_price(ticker)
    with cols[i]:
        price = data['price']
        pct = data['pct']
        if price and pct is not None:
            delta_color = "normal"
            st.metric(
                label=name,
                value=f"{price:,.2f}",
                delta=f"{pct:+.2f}%",
                delta_color=delta_color
            )
        else:
            st.metric(label=name, value="N/A")

st.markdown("---")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📐 POINTS PIVOTS",
    "🔗 CORRÉLATIONS",
    "💧 ZONES LIQUIDITÉ",
    "📈 ANALYSE GRAPHIQUE"
])

# ═══════════════════════════════════════
# TAB 1 : PIVOT POINTS
# ═══════════════════════════════════════
with tab1:
    st.markdown("## 📐 Points Pivots")

    ticker_sym = PIVOT_ASSETS[selected_pivot]
    tf_map = {"1d": "1d", "1wk": "1wk", "1mo": "1mo"}
    period_map = {"1d": "3mo", "1wk": "1y", "1mo": "2y"}
    
    df_piv = fetch_price_data(ticker_sym, period=period_map[pivot_tf], interval=tf_map[pivot_tf])
    pivots = compute_pivot_points(df_piv)

    if pivots:
        live = fetch_live_price(ticker_sym)
        current_price = live['price']

        # Summary row
        if current_price:
            pp = pivots['classic']['PP']
            bias = "🟢 HAUSSIER" if current_price > pp else "🔴 BAISSIER"
            st.markdown(f"""
            <div style='background:#0d1e2e; border:1px solid #1a3a5c; border-radius:8px; 
            padding:15px; margin-bottom:20px; display:flex; gap:30px; align-items:center;'>
                <span style='font-family:Orbitron,monospace; color:#00d4ff; font-size:14px;'>{selected_pivot}</span>
                <span style='font-family:Share Tech Mono,monospace; color:#00ff88; font-size:18px;'>{current_price:,.4f}</span>
                <span style='font-family:Orbitron,monospace; font-size:12px;'>{bias}</span>
                <span style='font-family:Share Tech Mono,monospace; color:#4a7090; font-size:11px;'>
                PP Classic: {pp:,.4f} | H:{pivots['prev_H']:,.4f} L:{pivots['prev_L']:,.4f} C:{pivots['prev_C']:,.4f}
                </span>
            </div>
            """, unsafe_allow_html=True)

        # Display pivots by type
        types_to_show = []
        if pivot_type == "Tous":
            types_to_show = ["classic", "fibonacci", "camarilla"]
        elif pivot_type == "Classic":
            types_to_show = ["classic"]
        elif pivot_type == "Fibonacci":
            types_to_show = ["fibonacci"]
        elif pivot_type == "Camarilla":
            types_to_show = ["camarilla"]

        for ptype in types_to_show:
            st.markdown(f"#### {'🔵 Classic' if ptype=='classic' else '🟡 Fibonacci' if ptype=='fibonacci' else '🟠 Camarilla'} Pivots")
            data = pivots[ptype]

            if ptype in ["classic", "fibonacci"]:
                c1, c2, c3, c4 = st.columns(4)
                levels = [
                    ("PP", data['PP'], "#00d4ff"),
                    ("R1", data['R1'], "#00ff88"),
                    ("R2", data['R2'], "#00cc66"),
                    ("R3", data['R3'], "#009944"),
                ]
                for col, (lbl, val, color) in zip([c1, c2, c3, c4], levels):
                    dist = f"({(val - current_price) / current_price * 100:+.2f}%)" if current_price else ""
                    col.markdown(f"""
                    <div style='background:#0d1e2e; border:1px solid {color}44; border-radius:6px; 
                    padding:12px; text-align:center; margin:4px;'>
                        <div style='font-family:Orbitron,monospace; color:{color}; font-size:11px; letter-spacing:2px;'>{lbl}</div>
                        <div style='font-family:Share Tech Mono,monospace; color:#e0f0ff; font-size:16px; margin:4px 0;'>{val:,.4f}</div>
                        <div style='font-family:Share Tech Mono,monospace; color:#4a7090; font-size:10px;'>{dist}</div>
                    </div>
                    """, unsafe_allow_html=True)

                c5, c6, c7 = st.columns(3)
                for col, (lbl, val, color) in zip([c5, c6, c7], [
                    ("S1", data['S1'], "#ff6b35"),
                    ("S2", data['S2'], "#ff4d1a"),
                    ("S3", data['S3'], "#ff2d55"),
                ]):
                    dist = f"({(val - current_price) / current_price * 100:+.2f}%)" if current_price else ""
                    col.markdown(f"""
                    <div style='background:#0d1e2e; border:1px solid {color}44; border-radius:6px; 
                    padding:12px; text-align:center; margin:4px;'>
                        <div style='font-family:Orbitron,monospace; color:{color}; font-size:11px; letter-spacing:2px;'>{lbl}</div>
                        <div style='font-family:Share Tech Mono,monospace; color:#e0f0ff; font-size:16px; margin:4px 0;'>{val:,.4f}</div>
                        <div style='font-family:Share Tech Mono,monospace; color:#4a7090; font-size:10px;'>{dist}</div>
                    </div>
                    """, unsafe_allow_html=True)

            else:  # Camarilla
                cols_cam = st.columns(4)
                for col, (lbl, val, color) in zip(cols_cam, [
                    ("R4", data['R4'], "#00ff88"),
                    ("R3", data['R3'], "#00cc66"),
                    ("R2", data['R2'], "#00aa44"),
                    ("R1", data['R1'], "#008833"),
                ]):
                    dist = f"({(val - current_price) / current_price * 100:+.2f}%)" if current_price else ""
                    col.markdown(f"""
                    <div style='background:#0d1e2e; border:1px solid {color}44; border-radius:6px; 
                    padding:10px; text-align:center; margin:4px;'>
                        <div style='font-family:Orbitron,monospace; color:{color}; font-size:11px;'>{lbl}</div>
                        <div style='font-family:Share Tech Mono,monospace; color:#e0f0ff; font-size:14px; margin:4px 0;'>{val:,.4f}</div>
                        <div style='font-family:Share Tech Mono,monospace; color:#4a7090; font-size:9px;'>{dist}</div>
                    </div>
                    """, unsafe_allow_html=True)
                cols_cam2 = st.columns(4)
                for col, (lbl, val, color) in zip(cols_cam2, [
                    ("S1", data['S1'], "#ff6b35"),
                    ("S2", data['S2'], "#ff4d1a"),
                    ("S3", data['S3'], "#ff2d55"),
                    ("S4", data['S4'], "#cc0033"),
                ]):
                    dist = f"({(val - current_price) / current_price * 100:+.2f}%)" if current_price else ""
                    col.markdown(f"""
                    <div style='background:#0d1e2e; border:1px solid {color}44; border-radius:6px; 
                    padding:10px; text-align:center; margin:4px;'>
                        <div style='font-family:Orbitron,monospace; color:{color}; font-size:11px;'>{lbl}</div>
                        <div style='font-family:Share Tech Mono,monospace; color:#e0f0ff; font-size:14px; margin:4px 0;'>{val:,.4f}</div>
                        <div style='font-family:Share Tech Mono,monospace; color:#4a7090; font-size:9px;'>{dist}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # Pivot chart
        if df_piv is not None and len(df_piv) > 10:
            st.markdown("#### 📊 Graphique avec Niveaux Pivots")
            df_plot = df_piv.tail(60).copy()
            df_plot.index = pd.to_datetime(df_plot.index)

            fig_piv = go.Figure()

            # Candlesticks
            fig_piv.add_trace(go.Candlestick(
                x=df_plot.index,
                open=df_plot['Open'].squeeze(),
                high=df_plot['High'].squeeze(),
                low=df_plot['Low'].squeeze(),
                close=df_plot['Close'].squeeze(),
                name="Prix",
                increasing_fillcolor='#00ff88',
                increasing_line_color='#00ff88',
                decreasing_fillcolor='#ff2d55',
                decreasing_line_color='#ff2d55',
            ))

            # Add pivot lines
            pdata = pivots['classic']
            pivot_lines = [
                ("PP", pdata['PP'], "#00d4ff", "dash"),
                ("R1", pdata['R1'], "#00ff88", "dot"),
                ("R2", pdata['R2'], "#00cc66", "dot"),
                ("R3", pdata['R3'], "#009944", "dot"),
                ("S1", pdata['S1'], "#ff6b35", "dot"),
                ("S2", pdata['S2'], "#ff4d1a", "dot"),
                ("S3", pdata['S3'], "#ff2d55", "dot"),
            ]

            x_range = [df_plot.index[0], df_plot.index[-1]]
            for lbl, val, color, dash in pivot_lines:
                fig_piv.add_shape(
                    type="line", x0=x_range[0], x1=x_range[-1],
                    y0=val, y1=val,
                    line=dict(color=color, width=1, dash=dash),
                )
                fig_piv.add_annotation(
                    x=x_range[-1], y=val,
                    text=f"  {lbl}: {val:,.2f}",
                    showarrow=False,
                    font=dict(color=color, size=10, family="Share Tech Mono"),
                    xanchor="left",
                )

            fig_piv.update_layout(
                paper_bgcolor='#050a0f', plot_bgcolor='#0a1520',
                font=dict(color='#e0f0ff', family='Share Tech Mono'),
                height=500, margin=dict(l=10, r=80, t=20, b=10),
                xaxis=dict(gridcolor='#1a3a5c', showgrid=True, rangeslider_visible=False),
                yaxis=dict(gridcolor='#1a3a5c', showgrid=True),
                showlegend=False,
            )
            st.plotly_chart(fig_piv, use_container_width=True)

    else:
        st.warning("Impossible de charger les données pour cet actif.")

    # ALL ASSETS PIVOT TABLE
    st.markdown("#### 📋 Tableau Pivots — Tous les Actifs")
    pivot_rows = []
    for asset_name, sym in PIVOT_ASSETS.items():
        dft = fetch_price_data(sym, period="3mo", interval="1d")
        pvt = compute_pivot_points(dft)
        lv = fetch_live_price(sym)
        if pvt and lv['price']:
            pp = pvt['classic']['PP']
            bias_sym = "▲" if lv['price'] > pp else "▼"
            pivot_rows.append({
                "Actif": asset_name,
                "Prix": f"{lv['price']:,.4f}",
                "Δ%": f"{lv['pct']:+.2f}%" if lv['pct'] else "—",
                "PP": f"{pp:,.4f}",
                "R1": f"{pvt['classic']['R1']:,.4f}",
                "R2": f"{pvt['classic']['R2']:,.4f}",
                "S1": f"{pvt['classic']['S1']:,.4f}",
                "S2": f"{pvt['classic']['S2']:,.4f}",
                "Biais": bias_sym,
            })

    if pivot_rows:
        st.dataframe(
            pd.DataFrame(pivot_rows),
            use_container_width=True,
            hide_index=True,
        )

# ═══════════════════════════════════════
# TAB 2 : CORRELATIONS
# ═══════════════════════════════════════
with tab2:
    st.markdown("## 🔗 Corrélations des Actifs Financiers")

    # Build asset dict based on selection
    corr_assets = {}
    if "Futures" in corr_scope:
        corr_assets.update(FUTURES)
    if "Forex" in corr_scope:
        corr_assets.update(FOREX)
    if "Crypto" in corr_scope:
        corr_assets.update({"BTC/USD": "BTC-USD"})

    corr_matrix = build_correlation_matrix(corr_assets, period=corr_period)

    if corr_matrix is not None and not corr_matrix.empty:
        # Heatmap
        st.markdown("#### 🗺️ Matrice de Corrélation")
        
        labels = corr_matrix.columns.tolist()
        z = corr_matrix.values

        fig_corr = go.Figure(data=go.Heatmap(
            z=z,
            x=labels,
            y=labels,
            colorscale=[
                [0.0, "#ff2d55"],
                [0.5, "#0a1520"],
                [1.0, "#00ff88"],
            ],
            zmin=-1, zmax=1,
            text=[[f"{v:.2f}" for v in row] for row in z],
            texttemplate="%{text}",
            textfont={"size": 10, "family": "Share Tech Mono", "color": "white"},
            hoverongaps=False,
        ))

        fig_corr.update_layout(
            paper_bgcolor='#050a0f', plot_bgcolor='#0a1520',
            font=dict(color='#e0f0ff', family='Share Tech Mono', size=10),
            height=550, margin=dict(l=10, r=10, t=30, b=10),
            xaxis=dict(tickangle=-45),
        )
        st.plotly_chart(fig_corr, use_container_width=True)

        # Strong correlations table
        st.markdown("#### ⚡ Corrélations Fortes (|r| ≥ 0.70)")
        rows = []
        for i, a1 in enumerate(labels):
            for j, a2 in enumerate(labels):
                if j <= i:
                    continue
                r = corr_matrix.iloc[i, j]
                if abs(r) >= 0.70:
                    direction = "🟢 POSITIVE" if r > 0 else "🔴 NÉGATIVE"
                    strength = "🔥 TRÈS FORTE" if abs(r) >= 0.90 else "⚡ FORTE"
                    rows.append({
                        "Actif 1": a1, "Actif 2": a2,
                        "Corrélation": f"{r:.4f}",
                        "Direction": direction,
                        "Force": strength,
                    })

        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("Aucune corrélation forte détectée sur la période sélectionnée.")

        # Rolling correlation
        st.markdown("#### 📈 Corrélation Glissante (30j) — Sélection de paire")
        all_names = list(corr_assets.keys())
        if len(all_names) >= 2:
            col_a, col_b = st.columns(2)
            a1_sel = col_a.selectbox("Actif 1", all_names, index=0)
            a2_sel = col_b.selectbox("Actif 2", all_names, index=min(1, len(all_names)-1))

            if a1_sel != a2_sel:
                df1 = fetch_price_data(corr_assets[a1_sel], period=corr_period)
                df2 = fetch_price_data(corr_assets[a2_sel], period=corr_period)

                if df1 is not None and df2 is not None:
                    s1 = df1['Close'].squeeze().pct_change()
                    s2 = df2['Close'].squeeze().pct_change()
                    combined = pd.DataFrame({'a': s1, 'b': s2}).dropna()
                    rolling_corr = combined['a'].rolling(30).corr(combined['b']).dropna()

                    fig_roll = go.Figure()
                    fig_roll.add_trace(go.Scatter(
                        x=rolling_corr.index,
                        y=rolling_corr.values,
                        mode='lines',
                        line=dict(color='#00d4ff', width=2),
                        fill='tozeroy',
                        fillcolor='rgba(0,212,255,0.1)',
                        name="Corrélation 30j"
                    ))
                    fig_roll.add_hline(y=0, line_color='#4a7090', line_dash='dash')
                    fig_roll.add_hline(y=0.7, line_color='#00ff88', line_dash='dot', annotation_text="0.70")
                    fig_roll.add_hline(y=-0.7, line_color='#ff2d55', line_dash='dot', annotation_text="-0.70")

                    fig_roll.update_layout(
                        paper_bgcolor='#050a0f', plot_bgcolor='#0a1520',
                        font=dict(color='#e0f0ff', family='Share Tech Mono'),
                        height=300, margin=dict(l=10, r=10, t=20, b=10),
                        xaxis=dict(gridcolor='#1a3a5c'),
                        yaxis=dict(gridcolor='#1a3a5c', range=[-1.1, 1.1]),
                        showlegend=False,
                        title=dict(text=f"Corrélation glissante: {a1_sel} / {a2_sel}",
                                   font=dict(color='#00d4ff', family='Orbitron', size=12))
                    )
                    st.plotly_chart(fig_roll, use_container_width=True)
    else:
        st.warning("Données insuffisantes pour calculer les corrélations.")

# ═══════════════════════════════════════
# TAB 3 : LIQUIDITY ZONES
# ═══════════════════════════════════════
with tab3:
    st.markdown("## 💧 Zones de Liquidité")

    liq_sym = PIVOT_ASSETS[liq_asset]
    tf_period = {"1h": "30d", "4h": "60d", "1d": "6mo"}
    
    df_liq = fetch_price_data(liq_sym, period=tf_period.get(liq_tf, "60d"), interval=liq_tf)
    liq = compute_liquidity_zones(df_liq)
    live_liq = fetch_live_price(liq_sym)

    if df_liq is not None and len(df_liq) > 10:
        current_liq_price = live_liq.get('price')

        # Info row
        col_i1, col_i2, col_i3 = st.columns(3)
        col_i1.metric("VWAP", f"{liq['vwap']:,.4f}" if liq['vwap'] else "N/A",
                      delta=f"{(current_liq_price - liq['vwap']) / liq['vwap'] * 100:+.2f}% vs VWAP" if liq['vwap'] and current_liq_price else None)
        col_i2.metric("POC (Point of Control)", f"{liq['poc']:,.4f}" if liq['poc'] else "N/A")
        col_i3.metric("Prix Actuel", f"{current_liq_price:,.4f}" if current_liq_price else "N/A",
                      delta=f"{live_liq.get('pct', 0):+.2f}%" if live_liq.get('pct') else None)

        # Liquidity chart
        st.markdown("#### 📊 Graphique Zones de Liquidité")

        df_plot_liq = df_liq.tail(100).copy()
        df_plot_liq.index = pd.to_datetime(df_plot_liq.index)

        fig_liq = make_subplots(
            rows=2, cols=2,
            column_widths=[0.75, 0.25],
            row_heights=[0.75, 0.25],
            shared_xaxes=True,
            specs=[[{"rowspan": 1}, {"rowspan": 2}],
                   [{"rowspan": 1}, None]],
            vertical_spacing=0.05,
            horizontal_spacing=0.02,
        )

        # Candles
        fig_liq.add_trace(go.Candlestick(
            x=df_plot_liq.index,
            open=df_plot_liq['Open'].squeeze(),
            high=df_plot_liq['High'].squeeze(),
            low=df_plot_liq['Low'].squeeze(),
            close=df_plot_liq['Close'].squeeze(),
            name="Prix",
            increasing_fillcolor='#00ff88',
            increasing_line_color='#00ff88',
            decreasing_fillcolor='#ff2d55',
            decreasing_line_color='#ff2d55',
        ), row=1, col=1)

        # Volume
        if 'Volume' in df_plot_liq.columns:
            vols = df_plot_liq['Volume'].squeeze()
            closes = df_plot_liq['Close'].squeeze()
            opens = df_plot_liq['Open'].squeeze()
            vol_colors = ['#00ff8866' if c >= o else '#ff2d5566'
                          for c, o in zip(closes, opens)]
            # ==================== DEBUG ZONES LIQUIDITÉ ====================
st.subheader("🔍 DEBUG - Colonnes du DataFrame Liquidité")
st.write("✅ Colonnes disponibles :", list(df_plot_liq.columns))
st.write("✅ Index :", df_plot_liq.index[:10].tolist())
st.dataframe(df_plot_liq.head(15))   # affiche les 15 premières lignes
# ============================================================
            fig_liq.add_trace(
    go.Bar(
        x=df_plot_liq['volume'],          # ← colonne NUMÉRIQUE (volume/largeur)
        y=df_plot_liq.index,              # ← prix en Y pour barres horizontales
        orientation='h',                  # ← indispensable pour zones de liquidité
        marker=dict(color='rgba(0, 255, 0, 0.6)'),   # ou la couleur que tu veux
        showlegend=False,
    ),
    row=2, col=1
)

        # VWAP line
        if liq['vwap']:
            fig_liq.add_hline(y=liq['vwap'], line_color='#ffd700',
                              line_width=1.5, line_dash='dash',
                              annotation_text=f"VWAP {liq['vwap']:,.2f}",
                              annotation_font_color='#ffd700',
                              annotation_font_size=9, row=1, col=1)

        # POC
        if liq['poc']:
            fig_liq.add_hline(y=liq['poc'], line_color='#00d4ff',
                              line_width=1.5, line_dash='dot',
                              annotation_text=f"POC {liq['poc']:,.2f}",
                              annotation_font_color='#00d4ff',
                              annotation_font_size=9, row=1, col=1)

        # Swing highs / lows zones
        x_range_liq = [df_plot_liq.index[0], df_plot_liq.index[-1]]
        for sh in liq['highs'][:5]:
            fig_liq.add_hrect(
                y0=sh['level'] * 0.9995, y1=sh['level'] * 1.0005,
                fillcolor='rgba(0,255,136,0.08)',
                line_color='rgba(0,255,136,0.3)', line_width=1,
                annotation_text=f"🔴 Liq. Haute ({sh['strength']}x)",
                annotation_font_color='#00ff88', annotation_font_size=9,
                row=1, col=1
            )
        for sl in liq['lows'][:5]:
            fig_liq.add_hrect(
                y0=sl['level'] * 0.9995, y1=sl['level'] * 1.0005,
                fillcolor='rgba(255,45,85,0.08)',
                line_color='rgba(255,45,85,0.3)', line_width=1,
                annotation_text=f"🟢 Liq. Basse ({sl['strength']}x)",
                annotation_font_color='#ff2d55', annotation_font_size=9,
                row=1, col=1
            )

        # Volume profile histogram
        if liq['vol_profile']:
            vp = liq['vol_profile']
            max_vol = max(v['volume'] for v in vp) or 1
            fig_liq.add_trace(go.Bar(
                x=[v['volume'] / max_vol for v in vp],
                y=[v['price'] for v in vp],
                orientation='h',
                marker_color=['#00d4ff' if abs(v['price'] - (liq['poc'] or 0)) < 1e-6
                              else '#00d4ff44' for v in vp],
                name="Vol Profile",
                showlegend=False,
            ), row=1, col=2)

        fig_liq.update_layout(
            paper_bgcolor='#050a0f', plot_bgcolor='#0a1520',
            font=dict(color='#e0f0ff', family='Share Tech Mono'),
            height=600, margin=dict(l=10, r=10, t=20, b=10),
            showlegend=False,
        )
        for axis in ['xaxis', 'xaxis2', 'xaxis3', 'yaxis', 'yaxis2', 'yaxis3']:
            fig_liq.update_layout(**{axis: dict(gridcolor='#1a3a5c', showgrid=True)})
        fig_liq.update_xaxes(rangeslider_visible=False)

        st.plotly_chart(fig_liq, use_container_width=True)

        # Zones table
        st.markdown("#### 📋 Zones de Liquidité Identifiées")
        c_high, c_low = st.columns(2)

        with c_high:
            st.markdown("**🔴 Zones de Liquidité Haute** *(résistance)*")
            if liq['highs']:
                df_h = pd.DataFrame([{
                    "Niveau": f"{z['level']:,.4f}",
                    "Force": "⭐" * min(z['strength'], 5),
                    "Dist %": f"{(z['level'] - current_liq_price) / current_liq_price * 100:+.2f}%" if current_liq_price else "—"
                } for z in sorted(liq['highs'], key=lambda x: x['level'])[:8]])
                st.dataframe(df_h, use_container_width=True, hide_index=True)

        with c_low:
            st.markdown("**🟢 Zones de Liquidité Basse** *(support)*")
            if liq['lows']:
                df_l = pd.DataFrame([{
                    "Niveau": f"{z['level']:,.4f}",
                    "Force": "⭐" * min(z['strength'], 5),
                    "Dist %": f"{(z['level'] - current_liq_price) / current_liq_price * 100:+.2f}%" if current_liq_price else "—"
                } for z in sorted(liq['lows'], key=lambda x: -x['level'])[:8]])
                st.dataframe(df_l, use_container_width=True, hide_index=True)
    else:
        st.warning("Données insuffisantes pour cet actif/timeframe.")

# ═══════════════════════════════════════
# TAB 4 : CHART ANALYSIS
# ═══════════════════════════════════════
with tab4:
    st.markdown("## 📈 Analyse Graphique Multi-Actifs")

    chart_assets = list(PIVOT_ASSETS.keys())
    chart_sel = st.selectbox("Sélectionner un actif", chart_assets, index=0)
    chart_tf = st.selectbox("Timeframe", ["1h", "4h", "1d", "1wk"], index=2)

    chart_sym = PIVOT_ASSETS[chart_sel]
    chart_period = {"1h": "30d", "4h": "60d", "1d": "6mo", "1wk": "2y"}
    df_chart = fetch_price_data(chart_sym, period=chart_period.get(chart_tf, "60d"), interval=chart_tf)

    if df_chart is not None and len(df_chart) > 20:
        df_chart = df_chart.copy()
        df_chart.index = pd.to_datetime(df_chart.index)

        closes = df_chart['Close'].squeeze().values
        highs = df_chart['High'].squeeze().values
        lows = df_chart['Low'].squeeze().values
        volumes = df_chart['Volume'].squeeze().values if 'Volume' in df_chart.columns else np.ones(len(closes))

        # Indicators
        # EMA 20, 50, 200
        def ema(data, period):
            s = pd.Series(data)
            return s.ewm(span=period, adjust=False).mean().values

        ema20 = ema(closes, 20)
        ema50 = ema(closes, 50)
        ema200 = ema(closes, 200)

        # MACD
        ema12 = ema(closes, 12)
        ema26 = ema(closes, 26)
        macd_line = ema12 - ema26
        signal_line = pd.Series(macd_line).ewm(span=9, adjust=False).mean().values
        macd_hist = macd_line - signal_line

        # Bollinger Bands
        bb_period = 20
        bb_mid = pd.Series(closes).rolling(bb_period).mean().values
        bb_std = pd.Series(closes).rolling(bb_period).std().values
        bb_upper = bb_mid + 2 * bb_std
        bb_lower = bb_mid - 2 * bb_std

        # RSI
        delta = pd.Series(closes).diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        fig_chart = make_subplots(
            rows=3, cols=1,
            row_heights=[0.6, 0.2, 0.2],
            shared_xaxes=True,
            vertical_spacing=0.03,
        )

        # Candlestick
        fig_chart.add_trace(go.Candlestick(
            x=df_chart.index,
            open=df_chart['Open'].squeeze(),
            high=df_chart['High'].squeeze(),
            low=df_chart['Low'].squeeze(),
            close=df_chart['Close'].squeeze(),
            name="Prix",
            increasing_fillcolor='#00ff88',
            increasing_line_color='#00ff88',
            decreasing_fillcolor='#ff2d55',
            decreasing_line_color='#ff2d55',
        ), row=1, col=1)

        # Bollinger Bands
        fig_chart.add_trace(go.Scatter(x=df_chart.index, y=bb_upper, line=dict(color='#ffd70044', width=1), name="BB Up", showlegend=False), row=1, col=1)
        fig_chart.add_trace(go.Scatter(x=df_chart.index, y=bb_lower, line=dict(color='#ffd70044', width=1), fill='tonexty', fillcolor='rgba(255,215,0,0.03)', name="BB Low", showlegend=False), row=1, col=1)
        fig_chart.add_trace(go.Scatter(x=df_chart.index, y=bb_mid, line=dict(color='#ffd70066', width=1, dash='dot'), name="BB Mid", showlegend=False), row=1, col=1)

        # EMAs
        fig_chart.add_trace(go.Scatter(x=df_chart.index, y=ema20, line=dict(color='#00d4ff', width=1.2), name="EMA20"), row=1, col=1)
        fig_chart.add_trace(go.Scatter(x=df_chart.index, y=ema50, line=dict(color='#ff6b35', width=1.2), name="EMA50"), row=1, col=1)
        fig_chart.add_trace(go.Scatter(x=df_chart.index, y=ema200, line=dict(color='#ffd700', width=1.5), name="EMA200"), row=1, col=1)

        # MACD
        colors_macd = ['#00ff88' if v >= 0 else '#ff2d55' for v in macd_hist]
        fig_chart.add_trace(go.Bar(x=df_chart.index, y=macd_hist, marker_color=colors_macd, name="MACD Hist", showlegend=False), row=2, col=1)
        fig_chart.add_trace(go.Scatter(x=df_chart.index, y=macd_line, line=dict(color='#00d4ff', width=1.5), name="MACD"), row=2, col=1)
        fig_chart.add_trace(go.Scatter(x=df_chart.index, y=signal_line, line=dict(color='#ff6b35', width=1.5), name="Signal"), row=2, col=1)

        # RSI
        fig_chart.add_trace(go.Scatter(x=df_chart.index, y=rsi.values, line=dict(color='#9b59b6', width=1.5), name="RSI", showlegend=False), row=3, col=1)
        fig_chart.add_hrect(y0=70, y1=100, fillcolor='rgba(255,45,85,0.05)', line_width=0, row=3, col=1)
        fig_chart.add_hrect(y0=0, y1=30, fillcolor='rgba(0,255,136,0.05)', line_width=0, row=3, col=1)
        fig_chart.add_hline(y=70, line_color='#ff2d5566', line_dash='dot', row=3, col=1)
        fig_chart.add_hline(y=30, line_color='#00ff8866', line_dash='dot', row=3, col=1)
        fig_chart.add_hline(y=50, line_color='#4a7090', line_dash='dash', row=3, col=1)

        fig_chart.update_layout(
            paper_bgcolor='#050a0f', plot_bgcolor='#0a1520',
            font=dict(color='#e0f0ff', family='Share Tech Mono'),
            height=700, margin=dict(l=10, r=10, t=20, b=10),
            legend=dict(
                orientation='h', y=1.02, x=0,
                bgcolor='rgba(0,0,0,0)', font=dict(size=10),
            ),
        )
        for i in range(1, 4):
            fig_chart.update_xaxes(gridcolor='#1a3a5c', showgrid=True, rangeslider_visible=False, row=i, col=1)
            fig_chart.update_yaxes(gridcolor='#1a3a5c', showgrid=True, row=i, col=1)

        st.plotly_chart(fig_chart, use_container_width=True)

        # Signal summary
        st.markdown("#### 🎯 Signaux Techniques")
        last_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50
        last_close = float(closes[-1])
        last_macd = float(macd_line[-1])
        last_signal = float(signal_line[-1])

        signals = []

        # EMA trend
        if last_close > ema200[-1] and ema20[-1] > ema50[-1]:
            signals.append(("EMA Trend", "BUY", "Prix > EMA200 + EMA20 > EMA50"))
        elif last_close < ema200[-1] and ema20[-1] < ema50[-1]:
            signals.append(("EMA Trend", "SELL", "Prix < EMA200 + EMA20 < EMA50"))
        else:
            signals.append(("EMA Trend", "NEUTRAL", "Tendance mixte"))

        # MACD
        if last_macd > last_signal and macd_hist[-1] > 0:
            signals.append(("MACD", "BUY", f"MACD haussier: {last_macd:.4f} > Signal: {last_signal:.4f}"))
        elif last_macd < last_signal and macd_hist[-1] < 0:
            signals.append(("MACD", "SELL", f"MACD baissier: {last_macd:.4f} < Signal: {last_signal:.4f}"))
        else:
            signals.append(("MACD", "NEUTRAL", "Croisement en cours"))

        # RSI
        if last_rsi > 70:
            signals.append(("RSI", "SELL", f"Surachat: RSI={last_rsi:.1f}"))
        elif last_rsi < 30:
            signals.append(("RSI", "BUY", f"Survente: RSI={last_rsi:.1f}"))
        else:
            signals.append(("RSI", "NEUTRAL", f"Zone neutre: RSI={last_rsi:.1f}"))

        # Bollinger
        if last_close > bb_upper[-1]:
            signals.append(("Bollinger", "SELL", "Prix au-dessus de la bande haute"))
        elif last_close < bb_lower[-1]:
            signals.append(("Bollinger", "BUY", "Prix sous la bande basse"))
        else:
            signals.append(("Bollinger", "NEUTRAL", "Prix dans les bandes"))

        sig_cols = st.columns(len(signals))
        for col, (name, sig, desc) in zip(sig_cols, signals):
            css_class = "signal-buy" if sig == "BUY" else "signal-sell" if sig == "SELL" else "signal-neutral"
            col.markdown(f"""
            <div class='{css_class}'>
                <div style='font-size:9px; opacity:0.7; margin-bottom:4px;'>{name}</div>
                <div>{sig}</div>
                <div style='font-family:Inter,sans-serif; font-size:9px; margin-top:4px; opacity:0.7; font-weight:400;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.warning("Données insuffisantes pour ce graphique.")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
<div style='text-align:center; font-family:Share Tech Mono,monospace; color:#4a7090; font-size:10px; padding:10px;'>
    ⚡ PRO TRADING TERMINAL — Données via Yahoo Finance (yfinance) — 
    Mis à jour: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} UTC — 
    ⚠️ À titre informatif uniquement, pas de conseil financier
</div>
""", unsafe_allow_html=True)
