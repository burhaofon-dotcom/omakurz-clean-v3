import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# --- CACHED YFINANCE ABFRAGE MIT AUTO-ADJUST & ROBUSTEM FAST_INFO FALLBACK ---
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_stock_data_cached(ticker_symbol):
    stock = yf.Ticker(ticker_symbol)
    
    # auto_adjust=True bereinigt historische Splits & Ausschüttungen sauber
    df_fast = stock.history(period="1y", auto_adjust=True)
    latest_price = 0.0
    if not df_fast.empty:
        # Dynamisch die richtige Kursspalte ermitteln ('Close' oder Fallback auf die erste Spalte)
        close_col = 'Close' if 'Close' in df_fast.columns else df_fast.columns[0]
        latest_price = float(df_fast[close_col].iloc[-1])

    info = {}
    try:
        info = stock.info or {}
    except Exception:
        info = {}
    
    # FastInfo ist ein Objekt (kein dict). getattr schützt sicher vor AttributeErrors.
    fast_info = getattr(stock, 'fast_info', None)
    
    fast_currency = getattr(fast_info, 'currency', None) if fast_info else None
    fast_last_price = getattr(fast_info, 'last_price', None) if fast_info else None
    fast_market_cap = getattr(fast_info, 'market_cap', 0) if fast_info else 0
    fast_year_high = getattr(fast_info, 'year_high', 'N/A') if fast_info else 'N/A'
    fast_year_low = getattr(fast_info, 'year_low', 'N/A') if fast_info else 'N/A'
    
    currency = info.get('currency') or fast_currency or 'USD'
    price = info.get('currentPrice') or info.get('regularMarketPrice') or fast_last_price or latest_price
    if not price or price == 0.0:
        price = latest_price
        
    if currency == 'GBp':
        price = price / 100.0
        currency = 'GBP'
        
    fx_rate = fetch_fx_rate_cached(currency)
    price_eur = price * fx_rate if isinstance(price, (int, float)) else price

    return {
        'longName': info.get('longName', ticker_symbol),
        'currentPrice': price,
        'currency': currency,
        'price_eur': price_eur,
        'trailingPE': info.get('trailingPE'),
        'debtToEquity': info.get('debtToEquity'),
        'payoutRatio': info.get('payoutRatio', 0.0),
        'marketCap': info.get('marketCap') or fast_market_cap,
        'fiftyTwoWeekHigh': info.get('fiftyTwoWeekHigh', fast_year_high),
        'fiftyTwoWeekLow': info.get('fiftyTwoWeekLow', fast_year_low),
        'df_history': df_fast
    }

# --- CACHED CHART RENDERER MIT SPLIT-KORREKTUR ---
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_chart_history_cached(ticker_symbol, period_choice):
    stock = yf.Ticker(ticker_symbol)
    return stock.history(period=period_choice, auto_adjust=True)

def render_interactive_chart(ticker_symbol, company_name, df_prefetched):
    st.markdown(f"### 📈 Kursverlauf & Marktzyklus für **{company_name}**")
    
    period_choice = st.radio(
        "Zeitraum wählen:",
        ["6m", "1y", "3y", "5y"],
        index=1,
        horizontal=True,
        key=f"chart_period_{ticker_symbol}"
    )
    
    if period_choice == "1y" and not df_prefetched.empty:
        df = df_prefetched
    else:
        df = fetch_chart_history_cached(ticker_symbol, period_choice)
    
    if not df.empty:
        # Dynamisch die richtige Kursspalte ermitteln (Close vs. Adj Close)
        y_col = 'Close' if 'Close' in df.columns else df.columns[0]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[y_col],
            mode='lines',
            name='Schlusskurs',
            line=dict(color='#d4af37', width=2),
            hovertemplate='%{x|%d.%m.%Y}: <b>%{y:.2f}</b>'
        ))
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(20,20,20,0.6)",
            margin=dict(l=10, r=10, t=20, b=10),
            height=350,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#333333", title="Kurs"),
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Keine historischen Kursdaten verfügbar.")
