import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def safe_number(value):
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def calculate_model_rating(info, price_series=None):
    """
    Educational valuation model.
    This is a rule-based scoring system, not financial advice.
    """

    score = 50
    reasons = []

    trailing_pe = safe_number(info.get("trailingPE"))
    forward_pe = safe_number(info.get("forwardPE"))
    peg_ratio = safe_number(info.get("pegRatio"))
    profit_margin = safe_number(info.get("profitMargins"))
    revenue_growth = safe_number(info.get("revenueGrowth"))
    debt_to_equity = safe_number(info.get("debtToEquity"))

    # Trailing P/E
    if trailing_pe is not None:
        if trailing_pe < 15:
            score += 12
            reasons.append("Trailing P/E looks relatively low.")
        elif trailing_pe <= 30:
            score += 5
            reasons.append("Trailing P/E looks moderate.")
        else:
            score -= 8
            reasons.append("Trailing P/E looks high.")
    else:
        reasons.append("Trailing P/E is unavailable.")

    # Forward P/E
    if forward_pe is not None:
        if forward_pe < 15:
            score += 12
            reasons.append("Forward P/E looks relatively low.")
        elif forward_pe <= 30:
            score += 5
            reasons.append("Forward P/E looks moderate.")
        else:
            score -= 8
            reasons.append("Forward P/E looks high.")
    else:
        reasons.append("Forward P/E is unavailable.")

    # PEG Ratio
    if peg_ratio is not None:
        if peg_ratio < 1:
            score += 12
            reasons.append("PEG ratio suggests valuation may be attractive relative to growth.")
        elif peg_ratio <= 2:
            score += 5
            reasons.append("PEG ratio looks acceptable.")
        else:
            score -= 8
            reasons.append("PEG ratio looks expensive relative to growth.")
    else:
        reasons.append("PEG ratio is unavailable.")

    # Profit Margin
    if profit_margin is not None:
        if profit_margin > 0.20:
            score += 10
            reasons.append("Profit margin is strong.")
        elif profit_margin > 0.05:
            score += 4
            reasons.append("Profit margin is positive.")
        else:
            score -= 8
            reasons.append("Profit margin is weak or negative.")
    else:
        reasons.append("Profit margin is unavailable.")

    # Revenue Growth
    if revenue_growth is not None:
        if revenue_growth > 0.15:
            score += 10
            reasons.append("Revenue growth is strong.")
        elif revenue_growth > 0:
            score += 4
            reasons.append("Revenue growth is positive.")
        else:
            score -= 8
            reasons.append("Revenue growth is negative or weak.")
    else:
        reasons.append("Revenue growth is unavailable.")

    # Debt to Equity
    if debt_to_equity is not None:
        if debt_to_equity < 50:
            score += 8
            reasons.append("Debt-to-equity looks low.")
        elif debt_to_equity <= 150:
            score += 2
            reasons.append("Debt-to-equity looks manageable.")
        else:
            score -= 8
            reasons.append("Debt-to-equity looks high.")
    else:
        reasons.append("Debt-to-equity is unavailable.")

    # Price momentum
    if price_series is not None and len(price_series.dropna()) >= 2:
        clean_prices = price_series.dropna()
        first_price = clean_prices.iloc[0]
        latest_price = clean_prices.iloc[-1]

        if first_price > 0:
            momentum = (latest_price - first_price) / first_price

            if momentum > 0.10:
                score += 8
                reasons.append("Price momentum is positive.")
            elif momentum >= -0.10:
                score += 2
                reasons.append("Price momentum is relatively stable.")
            else:
                score -= 8
                reasons.append("Price momentum is negative.")

    score = max(0, min(100, score))

    if score >= 70:
        rating = "Buy"
    elif score >= 40:
        rating = "Considering"
    else:
        rating = "Sell"

    return rating, round(score, 1), reasons

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
chart_type = st.selectbox(
    "Choose chart type:",
    ["Line", "Candlestick", "OHLC"]
)

show_volume = st.checkbox("Show Volume", value=True)
show_ma20 = st.checkbox("Show MA20", value=True)
show_ma50 = st.checkbox("Show MA50", value=False)

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
        fig = go.Figure()

for ticker in price_data.columns:
    fig.add_trace(
        go.Scatter(
            x=price_data.index,
            y=price_data[ticker],
            mode="lines",
            name=ticker
        )
    )

fig.update_layout(
    height=600,
    template="plotly_white",
    title="Price Comparison",
    xaxis_title="Date",
    yaxis_title="Price",
    hovermode="x unified",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(fig, use_container_width=True)

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

        st.info(
    "The Buy / Considering / Sell rating is generated by a simple educational rule-based model. "
    "It is not financial advice and should not be used as the only basis for investment decisions."
)

        fundamentals = []

        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info

                price_series = price_data[ticker] if ticker in price_data.columns else None
rating, model_score, reasons = calculate_model_rating(info, price_series)

fundamentals.append({
    "Ticker": ticker,
    "Company": info.get("shortName", "N/A"),
    "Model Rating": rating,
    "Model Score": model_score,
    "Market Cap": info.get("marketCap", "N/A"),
    "Trailing P/E": info.get("trailingPE", "N/A"),
    "Forward P/E": info.get("forwardPE", "N/A"),
    "PEG Ratio": info.get("pegRatio", "N/A"),
    "Profit Margin": info.get("profitMargins", "N/A"),
    "Revenue Growth": info.get("revenueGrowth", "N/A"),
    "Debt to Equity": info.get("debtToEquity", "N/A"),
    "Sector": info.get("sector", "N/A"),
    "Industry": info.get("industry", "N/A"),
    "Model Reasons": " | ".join(reasons[:4]),
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
