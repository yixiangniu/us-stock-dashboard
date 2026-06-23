import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(
    page_title="US Stock Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("📈 US Stock Dashboard")
st.write("Track multiple US stocks with price charts and basic fundamentals.")

tickers_input = st.text_input(
    "Enter US stock tickers, separated by commas:",
    value="AAPL, MSFT, NVDA, TSLA"
)

tickers = [
    ticker.strip().upper()
    for ticker in tickers_input.split(",")
    if ticker.strip()
]

period = st.selectbox(
    "Choose time period:",
    [
        "1d",
        "5d",
        "1mo",
        "3mo",
        "6mo",
        "YTD",
        "1y",
        "5y",
        "Max / Since IPO"
    ]
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
    "Max / Since IPO": "1mo",
}

if period == "YTD":
    yf_period = "ytd"
elif period == "Max / Since IPO":
    yf_period = "max"
else:
    yf_period = period
interval = interval_map[period]

if not tickers:
    st.warning("Please enter at least one ticker.")
else:
    st.subheader("Price Comparison")

    price_data = pd.DataFrame()

    for ticker in tickers:
        try:
            data = yf.Ticker(ticker).history(
                period=yf_period,
                interval=interval
            )

            if not data.empty:
                price_data[ticker] = data["Close"]
            else:
                st.warning(f"No price data found for {ticker}.")

        except Exception as e:
            st.error(f"Error loading data for {ticker}.")
            st.code(str(e))

    if not price_data.empty:
        st.line_chart(price_data)

        st.subheader("Performance Summary")

        rows = []

        for ticker in price_data.columns:
            series = price_data[ticker].dropna()

            if len(series) >= 2:
                first_price = series.iloc[0]
                latest_price = series.iloc[-1]
                change = latest_price - first_price
                change_pct = change / first_price * 100

                rows.append({
                    "Ticker": ticker,
                    "First Price": round(first_price, 2),
                    "Latest Price": round(latest_price, 2),
                    "Change": round(change, 2),
                    "Change %": round(change_pct, 2),
                })

        summary_df = pd.DataFrame(rows)
        st.dataframe(summary_df, use_container_width=True)

        st.subheader("Basic Fundamentals")

        fundamentals = []

        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info

                fundamentals.append({
                    "Ticker": ticker,
                    "Company": info.get("shortName", "N/A"),
                    "Market Cap": info.get("marketCap", "N/A"),
                    "Trailing P/E": info.get("trailingPE", "N/A"),
                    "Forward P/E": info.get("forwardPE", "N/A"),
                    "Sector": info.get("sector", "N/A"),
                    "Industry": info.get("industry", "N/A"),
                })

            except Exception as e:
                fundamentals.append({
                    "Ticker": ticker,
                    "Company": "Error",
                    "Market Cap": "N/A",
                    "Trailing P/E": "N/A",
                    "Forward P/E": "N/A",
                    "Sector": "N/A",
                    "Industry": "N/A",
                })

        fundamentals_df = pd.DataFrame(fundamentals)
        st.dataframe(fundamentals_df, use_container_width=True)

st.caption(
    "Data is provided by yfinance/Yahoo Finance and may be delayed, incomplete, "
    "or have different calculation methods from official filings. "
    "This dashboard is for learning and tracking only, not financial advice."
)
