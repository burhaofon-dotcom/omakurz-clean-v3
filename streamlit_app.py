import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai
import plotly.graph_objects as go
from datetime import datetime
import time

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="Oma-Kurz-Kompass ULTRA v5.1",
    page_icon="🧭",
    layout="wide"
)

# --- EDLES DESIGN & ENDPUNKTE (CSS) ---
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #2c1d0c 0%, #4a3525 50%, #1f1408 100%);
        border: 2px solid #d4af37;
        padding: 25px;
        border-radius: 12px;
        color: #f4e8c1;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
        margin-bottom: 25px;
    }
    .main-header h1 {
        color: #f9f1df;
        font-family: 'Georgia', serif;
        letter-spacing: 1.5px;
        margin-bottom: 5px;
    }
    .main-header p {
        color: #d4af37;
        font-style: italic;
        font-size: 1.1em;
    }
</style>
""", unsafe_allow_html=True)

# --- SICHERE API-KEY INITIALISIERUNG ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("🚨 Sicherheitsfehler: Kein Gemini API-Key in den Streamlit-Secrets gefunden!")
    st.stop()

# --- MODELL INITIALISIERUNG ---
model = genai.GenerativeModel(
    model_name="gemini-3.6-flash",
    generation_config={
        "temperature": 0.3,
        "max_output_tokens": 3200,
    }
)

# --- SEITENLEISTE: GLOSSAR & PHILOSOPHIE ---
with st.sidebar:
    st.title("🧭 Das Titanen-Quartett + 1")
    st.markdown("""
    * **🛡️ Beate Sander:** Substanz, Bilanzen, Dividenden.
    * **🚀 Ray Kurzweil:** Exponentielles Wachstum & Technologie.
    * **🏰 Charlie Munger:** Wirtschaftlicher Burggraben & Qualität.
    * **🌊 Howard Marks:** Marktzyklen & Risikobewusstsein.
    * **🪐 Max Tegmark:** Systemische Resilienz & Validierung.
    """)
    st.markdown("---")
    st.title("💡 Ticker-Wegweiser")
    st.markdown("""
    * **🇯🇵 Japan (Tokyo):** `.T` *(z.B. Fujifilm: `4901.T`)*
    * **🇬🇧 UK (London):** `.L` *(z.B. Rentokil: `RTO.L`)*
    * **🇺🇸 USA:** Normal *(z.B. Alnylam: `ALNY`)*
    * **🇩🇪 Deutschland:** `.DE` *(z.B. Allianz: `ALV.DE`)*
    """)
    st.markdown("---")
    st.caption("Oma-Kurz-Kompass ULTRA v5.1 (Optimiert mit Jimmy-Caching & Retry)")

# --- HEADER ---
st.markdown("""
<div class="main-header">
    <h1>🧭 OMA-KURZ-KOMPASS ULTRA</h1>
    <p>„Substanz, exponentielle Technologie, Burggräben, Zyklen & Theranos-Nikola-Detektor“</p>
</div>
""", unsafe_allow_html=True)

col_search, col_space = st.columns([2, 1])
with col_search:
    ticker_input = st.text_input("Aktien-Ticker eingeben (z.B. ALNY, ALV.DE, 4901.T):", "4901.T").upper()
    analyze_btn = st.button("🚀 Kurs aufnehmen & Tiefenanalyse starten", use_container_width=True, type="primary")

# --- 1. JIMMY-FUNKTION: CACHED YFINANCE ABFRAGE (1 STUNDE TTL) ---
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_stock_data_cached(ticker_symbol):
    stock = yf.Ticker(ticker_symbol)
    info = stock.info or {}
    
    # Historie mit auto_adjust=True für split-bereinigte Kurse
    df_fast = stock.history(period="1y", auto_adjust=True)
    
    return {
        'longName': info.get('longName', ticker_symbol),
        'currentPrice': info.get('currentPrice', info.get('regularMarketPrice', 0.0)),
        'currency': info.get('currency', 'USD'),
        'trailingPE': info.get('trailingPE', None),
        'debtToEquity': info.get('debtToEquity', None),
        'payoutRatio': info.get('payoutRatio', 0.0),
        'marketCap': info.get('marketCap', 0),
        'fiftyTwoWeekHigh': info.get('fiftyTwoWeekHigh', 'N/A'),
        'fiftyTwoWeekLow': info.get('fiftyTwoWeekLow', 'N/A'),
        'df_history': df_fast
    }

# --- CACHED CHART RENDERER MIT AUTO_ADJUST (SPLIT-KORREKTUR) ---
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_chart_history_cached(ticker_symbol, period_choice):
    stock = yf.Ticker(ticker_symbol)
    # auto_adjust=True glättet Aktiensplits sauber heraus
    return stock.history(period=period_choice, auto_adjust=True)

# --- 2. JIMMY-FUNKTION: CACHED KI-GENERIERUNG MIT EXPONENTIAL BACKOFF ---
@st.cache_data(ttl=3600, show_spinner=False)
def generate_ki_analysis_cached(prompt_text):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt_text)
            return response.text
        except Exception as api_err:
            if "429" in str(api_err) and attempt < max_retries - 1:
                time.sleep(10 + (attempt * 10))  # Wartet 10s, dann 20s...
            else:
                raise api_err

if analyze_btn and ticker_input:
    with st.spinner(f"Führe Theranos-Nikola-Detektor aus & durchleuchte {ticker_input}..."):
        try:
            # 1. Daten holen (Cached)
            info = fetch_stock_data_cached(ticker_input)
            
            name = info['longName']
            price = info['currentPrice']
            currency = info['currency']
            
            if currency == 'GBp':
                price = price / 100.0
                currency = 'GBP'
            
            price_eur = price
            if currency != 'EUR' and isinstance(price, (int, float)):
                try:
                    fx_ticker = yf.Ticker(f"{currency}EUR=X")
                    fx_info = fx_ticker.info or {}
                    fx_rate = fx_info.get('currentPrice', fx_info.get('regularMarketPrice', None))
                    if fx_rate:
                        price_eur = price * fx_rate
                except Exception:
                    pass
            
            pe_ratio = info['trailingPE']
            debt_to_equity = info['debtToEquity']
            payout_ratio = info['payoutRatio']
            market_cap = info['marketCap']
            fifty_two_high = info['fiftyTwoWeekHigh']
            fifty_two_low = info['fiftyTwoWeekLow']
            
            # --- COMPASS INTEGRITY SCORE ---
            base_score = 50
            if isinstance(pe_ratio, (int, float)) and pe_ratio > 0:
                if pe_ratio < 15: base_score += 15
                elif pe_ratio < 30: base_score += 5
                else: base_score -= 5
            
            if isinstance(debt_to_equity, (int, float)):
                if debt_to_equity < 50: base_score += 15
                elif debt_to_equity > 150:
                    if isinstance(market_cap, (int, float)) and market_cap > 5_000_000_000:
                        base_score -= 5
                    else:
                        base_score -= 25
            
            if isinstance(market_cap, (int, float)):
                if market_cap > 10_000_000_000: base_score += 20
                elif market_cap > 2_000_000_000: base_score += 10
            
            if isinstance(payout_ratio, (int, float)) and 0.1 <= payout_ratio <= 0.7:
                base_score += 10
                
            integrity_score = max(15, min(100, base_score))
            
            # --- UI METRIKEN ---
            st.markdown(f"## 📊 Schiffslogbuch für **{name}** (`{ticker_input}`)")
            
            col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
            if currency == 'EUR':
                col_m1.metric("Kurs", f"{price:.2f} EUR")
            else:
                col_m1.metric("Kurs", f"{price:.2f} {currency}", f"≈ {price_eur:.2f} EUR")
                
            col_m2.metric("KGV", f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else "N/A")
            col_m3.metric("Schulden (D/E)", f"{debt_to_equity}%" if isinstance(debt_to_equity, (int, float)) else "N/A")
            col_m4.metric("Ausschüttung", f"{payout_ratio * 100:.1f}%" if isinstance(payout_ratio, (int, float)) and payout_ratio else "N/A")
            col_m5.metric("🧭 Integrity Score", f"{integrity_score} / 100")
            
            st.progress(integrity_score / 100, text=f"Compass Integrity Score: {integrity_score} Punkte")

            with st.expander("📌 Erweiterte Fundamentaldaten & Kursspanne anzeigen"):
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    st.markdown(f"**Marktkapitalisierung:** {market_cap:,} {currency}" if isinstance(market_cap, (int, float)) else f"**Marktkapitalisierung:** {market_cap}")
                with col_t2:
                    st.markdown(f"**52-Wochen-Spanne:** {fifty_two_low} – {fifty_two_high} {currency}")
            
            # --- INTERAKTIVER CHART MIT SPLIT-KORREKTUR ---
            df_chart = fetch_chart_history_cached(ticker_input, "1y")
            if not df_chart.empty:
                st.markdown(f"### 📈 Kursverlauf für **{name}**")
                y_col = 'Close' if 'Close' in df_chart.columns else df_chart.columns[0]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_chart.index,
                    y=df_chart[y_col],
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
                    yaxis=dict(showgrid=True, gridcolor="#333333", title=f"Kurs ({currency})"),
                    hovermode="x unified"
                )
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            
            # --- PROMPT ---
            prompt = f"""
            Du bist der 'Oma-Kurz-Kompass ULTRA' - ein neutrales, hochpräzises Analyse-Instrument, das die Weisheit von Beate Sander, Ray Kurzweil, Charlie Munger, Howard Marks und Max Tegmark vereint.
            
            WICHTIGER SCHWERPUNKT (Theranos-Nikola-Detektor): 
            Prüfe kritisch auf echte Validierung vs. Marketing-Hype.
            
            Analysiere {name} ({ticker_input}):
            - Währung: {currency} (ca. {price_eur:.2f} EUR)
            - KGV: {pe_ratio}
            - Verschuldung (Debt/Equity): {debt_to_equity}%
            - Marktkapitalisierung: {market_cap}
            - Score: {integrity_score}/100
            
            KEINE Anlageberatung!
            
            Struktur:
            ## 1. Sparten & Geschäftsfelder (Womit wird Geld verdient?)
            ## 2. Der Transformations- & Zukunfts-Faktor (Kurzweil & Tegmark Brücke)
            ## 3. Burggraben & Theranos-Detektor (Munger-Skeptiker-Blick)
            ## 4. Bilanzen, Schulden & Zyklen (Sander & Marks Blick)
            ## 5. 36-Monats-Horizont & Gesamtprognose
            
            ### STEIN-KLASSE: [Wähle exakt eines: Dividenden-Falle | Unpolierter Rohstein | Sich entwickelnder Stein | Solider Wert | Geschliffener Brillant]
            ### FAZIT: [Sachliches Fazit]
            """
            
            # 2. KI Abfrage (Cached)
            raw_text = generate_ki_analysis_cached(prompt)
            
            if "Geschliffener Brillant" in raw_text:
                st.success("💎 **Stein-Klasse: Geschliffener Brillant**")
            elif "Solider Wert" in raw_text:
                st.info("🛡️ **Stein-Klasse: Solider Wert**")
            elif "Sich entwickelnder Stein" in raw_text:
                st.info("🌱 **Stein-Klasse: Sich entwickelnder Stein**")
            elif "Unpolierter Rohstein" in raw_text:
                st.warning("🪨 **Stein-Klasse: Unpolierter Rohstein**")
            elif "Dividenden-Falle" in raw_text:
                st.error("⚠️ **Stein-Klasse: Dividenden-Falle**")
                
            st.markdown("---")
            
            parts = raw_text.split("## ")
            for part in parts:
                if part.startswith("1. Sparten"):
                    with st.container(border=True):
                        st.markdown("### 🧩 1. Sparten & Geschäftsfelder (Womit wird Geld verdient?)")
                        st.markdown(part.replace("1. Sparten & Geschäftsfelder (Womit wird Geld verdient?)", "").strip())
                elif part.startswith("2. Der Transformations"):
                    with st.container(border=True):
                        st.markdown("### 🚀 2. Der Transformations- & Zukunfts-Faktor (Kurzweil & Tegmark)")
                        st.markdown(part.replace("2. Der Transformations- & Zukunfts-Faktor (Kurzweil & Tegmark)", "").strip())
                elif part.startswith("3. Burggraben"):
                    with st.container(border=True):
                        st.markdown("### 🏰 3. Burggraben & Theranos-Detektor (Munger-Skeptiker-Blick)")
                        st.markdown(part.replace("3. Burggraben & Theranos-Detektor (Munger-Skeptiker-Blick)", "").strip())
                elif part.startswith("4. Bilanzen"):
                    with st.container(border=True):
                        st.markdown("### 🏛️ 4. Bilanzen, Schulden & Zyklen (Sander & Marks)")
                        st.markdown(part.replace("4. Bilanzen, Schulden & Zyklen (Sander & Marks)", "").strip())
                elif part.startswith("5. 36-Monats"):
                    with st.container(border=True):
                        st.markdown("### ⏳ 5. 36-Monats-Horizont & Gesamtprognose")
                        st.markdown(part.replace("5. 36-Monats-Horizont & Gesamtprognose", "").strip())
            
            if "FAZIT:" in raw_text:
                fazit_text = raw_text.split("FAZIT:")[-1].strip()
                st.markdown("---")
                st.info(f"💡 **FAZIT:** {fazit_text}")
                
        except Exception as e:
            if "429" in str(e):
                st.warning("⏳ API-Pause: Sowohl YFinance als auch Gemini bitten um eine kurze Pause. Warte 20-30 Sekunden.")
            else:
                st.error(f"Fehler: {str(e)}")
