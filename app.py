from datetime import datetime
import pandas as pd
import pytz
import requests
import streamlit as st
import yfinance as yf

# Page Config
st.set_page_config(
    page_title="Mahadev Stock Screener", page_icon="📈", layout="wide"
)

st.title("📈 Live F&O Stock Screener (Price + Volume + NSE Live OI)")
st.caption(
    "Filters: VWAP, RSI, Volume Spike & NSE Official Live OI Buildup (Long/Short Buildup)"
)

# Top Liquid F&O Stocks List
FO_STOCKS = [
    "BAJAJFINSV.NS",
    "SBIN.NS",
    "RELIANCE.NS",
    "INFY.NS",
    "TATAMOTORS.NS",
    "ICICIBANK.NS",
    "HDFCBANK.NS",
    "BHARTIARTL.NS",
    "TCS.NS",
    "LT.NS",
    "AXISBANK.NS",
    "MARUTI.NS",
    "SUNPHARMA.NS",
    "TITAN.NS",
    "M&M.NS",
    "TATASTEEL.NS",
    "JINDALSTEL.NS",
    "HAL.NS",
    "VEDL.NS",
    "COALINDIA.NS",
]


# Function to get NSE Live OI Data using Session Cookies
def get_nse_oi_data(symbol):
    try:
        session = requests.Session()
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
        }
        # Step 1: Hit NSE Home Page to grab cookies
        session.get("https://www.nseindia.com", headers=headers, timeout=5)

        # Step 2: Hit Option Chain API for the Symbol
        url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"
        response = session.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()
            records = data.get("records", {}).get("data", [])

            total_ce_oi_change = 0
            total_pe_oi_change = 0

            for row in records:
                if "CE" in row:
                    total_ce_oi_change += row["CE"].get(
                        "changeinOpenInterest", 0
                    )
                if "PE" in row:
                    total_pe_oi_change += row["PE"].get(
                        "changeinOpenInterest", 0
                    )

            # Net OI Change
            net_oi_change = total_pe_oi_change - total_ce_oi_change
            return round(net_oi_change, 0)
    except Exception:
        pass
    return None


def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def run_scanner():
    bullish, bearish = [], []
    tz = pytz.timezone("Asia/Kolkata")
    today_date = datetime.now(tz).date()

    for ticker in FO_STOCKS:
        try:
            df = yf.download(
                ticker, period="1d", interval="5m", progress=False
            )
            if df.empty or len(df) < 5:
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            latest_time = df.index[-1].tz_convert(tz)
            if latest_time.date() != today_date:
                continue

            # Price Calculations
            df["RSI"] = calculate_rsi(df["Close"], 14)
            df["VWAP"] = (
                df["Volume"] * (df["High"] + df["Low"] + df["Close"]) / 3
            ).cumsum() / df["Volume"].cumsum()
            df["Vol_SMA"] = df["Volume"].rolling(window=20).mean()

            latest = df.iloc[-1]
            price = round(latest["Close"], 2)
            vwap = round(latest["VWAP"], 2)
            rsi = round(latest["RSI"], 1)
            vol_mult = (
                round(latest["Volume"] / latest["Vol_SMA"], 1)
                if latest["Vol_SMA"] > 0
                else 1.0
            )

            stock = ticker.replace(".NS", "")

            # Fetch NSE Live OI Data
            net_oi_change = get_nse_oi_data(stock)
            oi_status = (
                f"{net_oi_change:,}"
                if net_oi_change is not None
                else "NSE Blocked"
            )

            # Bullish Condition: Price > VWAP, RSI > 60, Vol > 1.5x, Put OI > Call OI (Positive Net OI)
            if price > vwap and rsi > 60 and vol_mult >= 1.5:
                buildup = (
                    "Long Buildup 🚀"
                    if net_oi_change and net_oi_change > 0
                    else "Price Breakout"
                )
                bullish.append({
                    "Stock": stock,
                    "Price (₹)": price,
                    "VWAP": vwap,
                    "RSI": rsi,
                    "Volume": f"{vol_mult}x",
                    "Net OI Change": oi_status,
                    "Signal": buildup,
                })

            # Bearish Condition: Price < VWAP, RSI < 40, Vol > 1.5x, Call OI > Put OI (Negative Net OI)
            elif price < vwap and rsi < 40 and vol_mult >= 1.5:
                buildup = (
                    "Short Buildup 🔻"
                    if net_oi_change and net_oi_change < 0
                    else "Price Breakdown"
                )
                bearish.append({
                    "Stock": stock,
                    "Price (₹)": price,
                    "VWAP": vwap,
                    "RSI": rsi,
                    "Volume": f"{vol_mult}x",
                    "Net OI Change": oi_status,
                    "Signal": buildup,
                })
        except Exception:
            pass

    return pd.DataFrame(bullish), pd.DataFrame(bearish)


# Dashboard Interface
col1, col2 = st.columns(2)

with st.spinner("Fetching Live Market Data + Direct NSE Option Chain..."):
    df_bull, df_bear = run_scanner()

with col1:
    st.subheader("🚀 Bullish CE Opportunities")
    if not df_bull.empty:
        st.dataframe(df_bull, use_container_width=True)
    else:
        st.info("Market Closed / No Live Candidates Right Now")

with col2:
    st.subheader("🔻 Bearish PE Opportunities")
    if not df_bear.empty:
        st.dataframe(df_bear, use_container_width=True)
    else:
        st.info("Market Closed / No Live Candidates Right Now")
