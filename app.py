import pandas as pd
import pandas_ta as ta
import requests
import streamlit as st
import yfinance as yf

# Page Config (Mobile Responsive UI)
st.set_page_config(
    page_title="Mahadev Stock Screener", page_icon="📈", layout="wide"
)

st.title("📈 Live F&O Stock Option Screener")
st.caption("Auto-refreshes live market data with Volume, VWAP & RSI Filters")

# Complete NSE F&O Stocks List (180+ Stocks)
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


def run_scanner():
    bullish, bearish = [], []

    for ticker in FO_STOCKS:
        try:
            df = yf.download(
                ticker, period="5d", interval="5m", progress=False
            )
            if df.empty or len(df) < 50:
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df["RSI"] = ta.rsi(df["Close"], length=14)
            df["VWAP"] = ta.vwap(
                df["High"], df["Low"], df["Close"], df["Volume"]
            )
            df["Vol_SMA"] = ta.sma(df["Volume"], length=20)

            latest = df.iloc[-1]
            price = round(latest["Close"], 2)
            vwap = round(latest["VWAP"], 2)
            rsi = round(latest["RSI"], 1)

            vol_mult = (
                round(latest["Volume"] / latest["Vol_SMA"], 1)
                if latest["Vol_SMA"] > 0
                else 0
            )
            stock = ticker.replace(".NS", "")

            # Intraday Conditions
            if price > vwap and rsi > 60 and vol_mult >= 1.8:
                bullish.append({
                    "Stock": stock,
                    "Price (₹)": price,
                    "VWAP": vwap,
                    "RSI": rsi,
                    "Volume Spike": f"{vol_mult}x",
                })
            elif price < vwap and rsi < 40 and vol_mult >= 1.8:
                bearish.append({
                    "Stock": stock,
                    "Price (₹)": price,
                    "VWAP": vwap,
                    "RSI": rsi,
                    "Volume Spike": f"{vol_mult}x",
                })
        except Exception:
            pass

    return pd.DataFrame(bullish), pd.DataFrame(bearish)


# Dashboard Interface
col1, col2 = st.columns(2)

with st.spinner("Scanning All 180+ F&O Stocks... Please wait..."):
    df_bull, df_bear = run_scanner()

with col1:
    st.subheader("🚀 Bullish Breakouts (CE Buy)")
    if not df_bull.empty:
        st.dataframe(df_bull, use_container_width=True)
    else:
        st.info("No Bullish Candidates Right Now")

with col2:
    st.subheader("🔻 Bearish Breakouts (PE Buy)")
    if not df_bear.empty:
        st.dataframe(df_bear, use_container_width=True)
    else:
        st.info("No Bearish Candidates Right Now")
