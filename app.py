import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(
    page_title="US Stock Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("📈 US Stock Dashboard")
st.write("A simple dashboard for tracking US stock prices and fundamentals.")

ticker = st.text_input("Enter a US stock ticker:", value="AAPL").upper()

period = st.selectbox(
    "Choose time period:",
    ["1d", "5d", "1mo", "3mo", "6mo", "YTD", "1y", "5y"]
)

interval_map = {
    "1d": "5m",
    "5d": "15m",
    "1mo": "1h",
    "3mo": "1d",
    "6mo": "1d",
    "YTD": "1d",
    "1y": "1d",
    "5y": "1wk",
}

yf_period = "ytd" if period == "YTD" else period
interval = interval_map[period]

try:
    stock = yf.Ticker(ticker)
    data = stock.history(period=yf_period, interval=interval)

    if data.empty:
        st.error("No data found. Please check the ticker symbol.")
    else:
        st.subheader(f"{ticker} Price Chart")
        st.line_chart(data["Close"])

        latest_price = data["Close"].iloc[-1]
        first_price = data["Close"].iloc[0]
        change = latest_price - first_price
        change_pct = change / first_price * 100

        col1, col2, col3 = st.columns(3)
        col1.metric("Latest Close", f"${latest_price:.2f}")
        col2.metric("Change", f"${change:.2f}")
        col3.metric("Change %", f"{change_pct:.2f}%")

        st.subheader("Recent Price Data")
        st.dataframe(data.tail(20))

        st.subheader("Basic Fundamentals")
        info = stock.info

        col4, col5, col6 = st.columns(3)
        col4.metric("Market Cap", info.get("marketCap", "N/A"))
        col5.metric("Trailing P/E", info.get("trailingPE", "N/A"))
        col6.metric("Forward P/E", info.get("forwardPE", "N/A"))

        st.caption(
            "Data is provided by yfinance/Yahoo Finance and may be delayed or incomplete. "
            "This dashboard is for learning and tracking only, not financial advice."
        )

except Exception as e:
    st.error("Something went wrong while loading stock data.")
    st.code(str(e))
