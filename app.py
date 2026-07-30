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

st.title("📈 Live F&O Screener + Sector Tracker + BTST Predictor")
st.caption(
    "Filters: Sector Performance, VWAP, RSI, Volume Spike, NSE Live OI & BTST"
    " Finder"
)

# Sector Indices Mapping
SECTOR_INDICES = {
    "NIFTY BANK": "^NSEBANK",
    "NIFTY IT": "^CNXIT",
    "NIFTY AUTO": "^CNXAUTO",
    "NIFTY PHARMA": "^CNXPHARMA",
    "NIFTY METAL": "^CNXMETAL",
    "NIFTY FMCG": "^CNXFMCG",
    "NIFTY REALTY": "^CNXREALTY",
    "NIFTY ENERGY": "^CNXENERGY",
    "NIFTY INFRA": "^CNXINFRA",
}

# Stock to Sector Mapping (Sample Mapping for Top F&O Stocks)
STOCK_SECTOR_MAP = {
    "SBIN": "NIFTY BANK",
    "HDFCBANK": "NIFTY BANK",
    "ICICIBANK": "NIFTY BANK",
    "AXISBANK": "NIFTY BANK",
    "KOTAKBANK": "NIFTY BANK",
    "BANKBARODA": "NIFTY BANK",
    "PNB": "NIFTY BANK",
    "FEDERALBNK": "NIFTY BANK",
    "TCS": "NIFTY IT",
    "INFY": "NIFTY IT",
    "HCLTECH": "NIFTY IT",
    "TECHM": "NIFTY IT",
    "WIPRO": "NIFTY IT",
    "LTIM": "NIFTY IT",
    "COFORGE": "NIFTY IT",
    "TATAMOTORS": "NIFTY AUTO",
    "M&M": "NIFTY AUTO",
    "MARUTI": "NIFTY AUTO",
    "BAJAJ-AUTO": "NIFTY AUTO",
    "HEROMOTOCO": "NIFTY AUTO",
    "TVSMOTOR": "NIFTY AUTO",
    "EICHERMOT": "NIFTY AUTO",
    "BHARATFORG": "NIFTY AUTO",
    "SUNPHARMA": "NIFTY PHARMA",
    "CIPLA": "NIFTY PHARMA",
    "DRREDDY": "NIFTY PHARMA",
    "DIVISLAB": "NIFTY PHARMA",
    "LUPIN": "NIFTY PHARMA",
    "TATASTEEL": "NIFTY METAL",
    "JINDALSTEL": "NIFTY METAL",
    "HINDALCO": "NIFTY METAL",
    "JSWSTEEL": "NIFTY METAL",
    "VEDL": "NIFTY METAL",
    "SAIL": "NIFTY METAL",
    "NMDC": "NIFTY METAL",
    "COALINDIA": "NIFTY METAL",
    "ITC": "NIFTY FMCG",
    "HINDUNILVR": "NIFTY FMCG",
    "BRITANNIA": "NIFTY FMCG",
    "DABUR": "NIFTY FMCG",
    "GODREJCP": "NIFTY FMCG",
    "TATACONSUM": "NIFTY FMCG",
    "DLF": "NIFTY REALTY",
    "GODREJPROP": "NIFTY REALTY",
    "OBEROIRLTY": "NIFTY REALTY",
    "RELIANCE": "NIFTY ENERGY",
    "BPCL": "NIFTY ENERGY",
    "IOC": "NIFTY ENERGY",
    "ONGC": "NIFTY ENERGY",
    "NTPC": "NIFTY ENERGY",
    "POWERGRID": "NIFTY ENERGY",
    "LT": "NIFTY INFRA",
    "HAL": "NIFTY INFRA",
    "BEL": "NIFTY INFRA",
    "ADANIPORTS": "NIFTY INFRA",
    "BHARTIARTL": "NIFTY INFRA",
}

# Complete List of Active F&O Stocks
FO_STOCKS = [
    "AARTIIND.NS",
    "ABB.NS",
    "ABBOTINDIA.NS",
    "ABCAPITAL.NS",
    "ABFRL.NS",
    "ACC.NS",
    "ADANIENT.NS",
    "ADANIPORTS.NS",
    "ALKEM.NS",
    "AMBUJACEM.NS",
    "APOLLOHOSP.NS",
    "APOLLOTYRE.NS",
    "ASHOKLEY.NS",
    "ASIANPAINT.NS",
    "ASTRAL.NS",
    "ATUL.NS",
    "AUBANK.NS",
    "AUROPHARMA.NS",
    "AXISBANK.NS",
    "BAJAJ-AUTO.NS",
    "BAJAJFINSV.NS",
    "BAJFINANCE.NS",
    "BALKRISIND.NS",
    "BALRAMCHIN.NS",
    "BANDHANBNK.NS",
    "BANKBARODA.NS",
    "BATAINDIA.NS",
    "BEL.NS",
    "BERGEPAINT.NS",
    "BHARATFORG.NS",
    "BHARTIARTL.NS",
    "BHEL.NS",
    "BIOCON.NS",
    "BSOFT.NS",
    "BPCL.NS",
    "BRITANNIA.NS",
    "CANBK.NS",
    "CANFINHOME.NS",
    "CHAMBLFERT.NS",
    "CHOLAFIN.NS",
    "CIPLA.NS",
    "COALINDIA.NS",
    "COFORGE.NS",
    "COLPAL.NS",
    "CONCOR.NS",
    "COROMANDEL.NS",
    "CROMPTON.NS",
    "CUB.NS",
    "CUMMINSIND.NS",
    "DABUR.NS",
    "DALBHARAT.NS",
    "DEEPAKNTR.NS",
    "DELHIVERY.NS",
    "DIVISLAB.NS",
    "DIXON.NS",
    "DLF.NS",
    "DRREDDY.NS",
    "EICHERMOT.NS",
    "ESCORTS.NS",
    "EXIDEIND.NS",
    "FEDERALBNK.NS",
    "GAIL.NS",
    "GLENMARK.NS",
    "GMMPFAUDLR.NS",
    "GMRINFRA.NS",
    "GNFC.NS",
    "GODREJCP.NS",
    "GODREJPROP.NS",
    "GRANULES.NS",
    "GRASIM.NS",
    "GUJGASLTD.NS",
    "HAL.NS",
    "HAVELLS.NS",
    "HCLTECH.NS",
    "HDFCBANK.NS",
    "HDFCLIFE.NS",
    "HEROMOTOCO.NS",
    "HINDALCO.NS",
    "HINDCOPPER.NS",
    "HINDPETRO.NS",
    "HINDUNILVR.NS",
    "ICICIBANK.NS",
    "ICICIGI.NS",
    "ICICIPRULI.NS",
    "IDEA.NS",
    "IDFCFIRSTB.NS",
    "IEX.NS",
    "IGL.NS",
    "INDHOTEL.NS",
    "IOC.NS",
    "IRCTC.NS",
    "INDIAMART.NS",
    "INDIGO.NS",
    "INDUSINDBK.NS",
    "INDUSTOWER.NS",
    "INFY.NS",
    "IPCALAB.NS",
    "ITC.NS",
    "JINDALSTEL.NS",
    "JKCEMENT.NS",
    "JSWSTEEL.NS",
    "JUBLFOOD.NS",
    "KOTAKBANK.NS",
    "LALPATHLAB.NS",
    "LAURUSLABS.NS",
    "LICHSGFIN.NS",
    "LTIM.NS",
    "LT.NS",
    "LTTS.NS",
    "LUPIN.NS",
    "M&M.NS",
    "M&MFIN.NS",
    "MANAPPURAM.NS",
    "MARICO.NS",
    "MARUTI.NS",
    "MCDOWELL-N.NS",
    "MCX.NS",
    "METROPOLIS.NS",
    "MFSL.NS",
    "MGL.NS",
    "MOTHERSON.NS",
    "MPHASIS.NS",
    "MRF.NS",
    "MUTHOOTFIN.NS",
    "NATIONALUM.NS",
    "NAVINFLUOR.NS",
    "NESTLEIND.NS",
    "NMDC.NS",
    "NTPC.NS",
    "OBEROIRLTY.NS",
    "OFSS.NS",
    "ONGC.NS",
    "PAGEIND.NS",
    "PERSISTENT.NS",
    "PETRONET.NS",
    "PFC.NS",
    "PIDILITIND.NS",
    "PIIND.NS",
    "PNB.NS",
    "POLYCAB.NS",
    "POWERGRID.NS",
    "PVRINOX.NS",
    "RAMCOCEM.NS",
    "RBLBANK.NS",
    "RECLTD.NS",
    "RELIANCE.NS",
    "SAIL.NS",
    "SBICARD.NS",
    "SBILIFE.NS",
    "SBIN.NS",
    "SHREECEM.NS",
    "SHRIRAMFIN.NS",
    "SIEMENS.NS",
    "SRF.NS",
    "SUNPHARMA.NS",
    "SUNTV.NS",
    "SYNGENE.NS",
    "TATACOMM.NS",
    "TATACONSUM.NS",
    "TATAMOTORS.NS",
    "TATAPOWER.NS",
    "TATASTEEL.NS",
    "TCS.NS",
    "TECHM.NS",
    "TITAN.NS",
    "TORNTPHARM.NS",
    "TRENT.NS",
    "TVSMOTOR.NS",
    "UBL.NS",
    "ULTRACEMCO.NS",
    "UPL.NS",
    "VEDL.NS",
    "VOLTAS.NS",
    "WIPRO.NS",
    "ZEEL.NS",
    "ZYDUSLIFE.NS",
]


# Function to get Sector Performance
def get_sector_performance():
    sector_data = []
    tz = pytz.timezone("Asia/Kolkata")
    today_date = datetime.now(tz).date()

    for name, symbol in SECTOR_INDICES.items():
        try:
            df = yf.download(
                symbol, period="1d", interval="5m", progress=False
            )
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)

                latest_time = df.index[-1].tz_convert(tz)
                if latest_time.date() == today_date:
                    open_p = df["Open"].iloc[0]
                    curr_p = df["Close"].iloc[-1]
                    p_change = round(((curr_p - open_p) / open_p) * 100, 2)
                    status = (
                        "🟢 Strong"
                        if p_change > 0.5
                        else ("🔴 Weak" if p_change < -0.5 else "⚪ Neutral")
                    )
                    sector_data.append({
                        "Sector": name,
                        "Change (%)": f"{p_change}%",
                        "Status": status,
                        "raw_change": p_change,
                    })
        except Exception:
            pass

    df_sec = pd.DataFrame(sector_data)
    if not df_sec.empty:
        df_sec = df_sec.sort_values(by="raw_change", ascending=False).drop(
            columns=["raw_change"]
        )
    return df_sec


# Function to fetch NSE Live Option Chain Data
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
        session.get("https://www.nseindia.com", headers=headers, timeout=3)
        url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"
        response = session.get(url, headers=headers, timeout=3)

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
    bullish, bearish, btst_list = [], [], []
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

            # Technical Calculations
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

            day_high = df["High"].max()
            day_low = df["Low"].min()

            stock = ticker.replace(".NS", "")
            sector = STOCK_SECTOR_MAP.get(stock, "Others")
            net_oi_change = get_nse_oi_data(stock)
            oi_status = (
                f"{net_oi_change:,}"
                if net_oi_change is not None
                else "NSE Blocked"
            )

            # Intraday Bullish / Bearish Breakouts
            if price > vwap and rsi > 60 and vol_mult >= 1.5:
                bullish.append({
                    "Stock": stock,
                    "Sector": sector,
                    "Price (₹)": price,
                    "VWAP": vwap,
                    "RSI": rsi,
                    "Volume": f"{vol_mult}x",
                    "Net OI Change": oi_status,
                })
            elif price < vwap and rsi < 40 and vol_mult >= 1.5:
                bearish.append({
                    "Stock": stock,
                    "Sector": sector,
                    "Price (₹)": price,
                    "VWAP": vwap,
                    "RSI": rsi,
                    "Volume": f"{vol_mult}x",
                    "Net OI Change": oi_status,
                })

            # BTST / STBT Logic
            if (
                price >= day_high * 0.995
                and price > vwap
                and rsi >= 62
                and vol_mult >= 2.0
            ):
                btst_list.append({
                    "Stock": stock,
                    "Sector": sector,
                    "Type": "BTST (Call Carry 🚀)",
                    "Price (₹)": price,
                    "RSI": rsi,
                    "Volume Spike": f"{vol_mult}x",
                })
            elif (
                price <= day_low * 1.005
                and price < vwap
                and rsi <= 38
                and vol_mult >= 2.0
            ):
                btst_list.append({
                    "Stock": stock,
                    "Sector": sector,
                    "Type": "STBT (Put Carry 🔻)",
                    "Price (₹)": price,
                    "RSI": rsi,
                    "Volume Spike": f"{vol_mult}x",
                })

        except Exception:
            pass

    return (
        pd.DataFrame(bullish),
        pd.DataFrame(bearish),
        pd.DataFrame(btst_list),
    )


# --- DASHBOARD LAYOUT ---

st.subheader("📊 Live Sector Strength Tracker")
with st.spinner("Fetching Live Sector Trends..."):
    df_sectors = get_sector_performance()

if not df_sectors.empty:
    st.dataframe(df_sectors, use_container_width=True, hide_index=True)
else:
    st.info("Market Closed / Sector Trends Unavailable")

st.markdown("---")

col1, col2 = st.columns(2)

with st.spinner("Scanning 180+ F&O Stocks for Live Breakouts & BTST..."):
    df_bull, df_bear, df_btst = run_scanner()

with col1:
    st.subheader("🚀 Bullish Intraday CE")
    if not df_bull.empty:
        st.dataframe(df_bull, use_container_width=True)
    else:
        st.info("No Intraday Bullish Breakout Right Now")

with col2:
    st.subheader("🔻 Bearish Intraday PE")
    if not df_bear.empty:
        st.dataframe(df_bear, use_container_width=True)
    else:
        st.info("No Intraday Bearish Breakdown Right Now")

st.markdown("---")
st.subheader("🌙 BTST / STBT Overnight Suggestions (Best viewed after 2:30 PM)")

if not df_btst.empty:
    st.dataframe(df_btst, use_container_width=True)
else:
    st.info("No BTST/STBT high-probability candidates found right now.")
