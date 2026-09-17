import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai
import plotly.graph_objects as go
import time

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="Oma-Kurz-Kompass ULTRA v5.7",
    page_icon="🧭",
    layout="wide"
)

# --- EDLES DESIGN (CSS) ---
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

# --- MODELL-KANDIDATEN ---
# WICHTIG: gemini-1.5-flash, gemini-1.5-flash-8b und gemini-1.5-pro wurden von Google
# abgeschaltet (Stand 2026) und liefern nur noch "model not found". Aktuelle Nachfolger:
MODEL_CANDIDATES = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro"
]

# Hinweis: Kein globales, fest verdrahtetes 'model'-Objekt mehr nötig - der Fallback
# unten probiert bei Bedarf automatisch alle MODEL_CANDIDATES der Reihe nach durch.

# --- CACHED KI-GENERIERUNG MIT RETRY & MODELL-FALLBACK ---
# (Es gibt nur noch EINE Definition dieser Funktion - die doppelte, die vorher weiter
# unten im Skript stand und diese hier überschrieben hat, wurde entfernt.)
@st.cache_data(ttl=86400, show_spinner=False)
def generate_ki_analysis_cached(prompt_text):
    last_exception = None
    for model_name in MODEL_CANDIDATES:
        try:
            temp_model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 3200,
                }
            )
            response = temp_model.generate_content(prompt_text)
            return response.text
        except Exception as err:
            last_exception = err
            if "429" in str(err):
                time.sleep(5)
            continue

    raise last_exception

# --- SEITENLEISTE ---
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
    * **🇺🇸 USA / REITs:** z.B. `MPW`, `ALNY`
    * **🇩🇪 Deutschland:** `.DE` *(z.B. `GBF.DE`, `ALV.DE`)*
    * **🇯🇵 Japan:** `.T` *(z.B. `4901.T`)*
    * **🇬🇧 UK:** `.L` *(z.B. `RTO.L`)*
    """)
    st.markdown("---")
    st.caption("Oma-Kurz-Kompass ULTRA v5.7 (Vollständige KI-Ausgabe & Stein-Fix)")

# --- HEADER ---
st.markdown("""
<div class="main-header">
    <h1>🧭 OMA-KURZ-KOMPASS ULTRA</h1>
    <p>„Substanz, exponentielle Technologie, Burggräben, Zyklen & Domino-Narrativ-Detektor“</p>
</div>
""", unsafe_allow_html=True)

col_search, col_space = st.columns([2, 1])
with col_search:
    ticker_input = st.text_input("Aktien-Ticker eingeben (z.B. MPW, GBF.DE, ALNY, ALV.DE):", "GBF.DE").upper()
    analyze_btn = st.button("🚀 Kurs aufnehmen & Tiefenanalyse starten", use_container_width=True, type="primary")

# --- 1. ROBUSTE YFINANCE ABFRAGE (24H CACHE / KEINE DOPPEL-CALLS) ---
@st.cache_data(ttl=86400, show_spinner=False)
def fetch_stock_data_cached(ticker_symbol):
    stock = yf.Ticker(ticker_symbol)

    info = {}
    try:
        info = stock.info or {}
    except Exception:
        pass

    fast_info = getattr(stock, 'fast_info', {})

    # Historie nur 1x laden
    df_hist = pd.DataFrame()
    try:
        df_hist = stock.history(period="1y", auto_adjust=True)
    except Exception:
        pass

    # Robuster Kurs-Fallback
    current_p = info.get('currentPrice') or info.get('regularMarketPrice')
    if not current_p and hasattr(fast_info, 'last_price'):
        current_p = fast_info.last_price
    if (not current_p or current_p == 0.0) and not df_hist.empty:
        current_p = float(df_hist['Close'].iloc[-1])
    if not current_p:
        current_p = 0.0

    # 52-Wochen Spanne Fallbacks
    high_52 = info.get('fiftyTwoWeekHigh')
    if (not high_52 or high_52 == 'N/A') and not df_hist.empty:
        high_52 = float(df_hist['Close'].max())

    low_52 = info.get('fiftyTwoWeekLow')
    if (not low_52 or low_52 == 'N/A') and not df_hist.empty:
        low_52 = float(df_hist['Close'].min())

    return {
        'longName': info.get('longName', ticker_symbol),
        'currentPrice': float(current_p),
        'currency': info.get('currency', 'USD'),
        'trailingPE': info.get('trailingPE', None),
        'debtToEquity': info.get('debtToEquity', None),
        'payoutRatio': info.get('payoutRatio', None),
        'marketCap': info.get('marketCap', 0),
        'fiftyTwoWeekHigh': high_52 if high_52 else 'N/A',
        'fiftyTwoWeekLow': low_52 if low_52 else 'N/A',
        'df_history': df_hist
    }

if analyze_btn and ticker_input:
    with st.spinner(f"Führe Domino- & Narrativ-Detektor aus & durchleuchte {ticker_input}..."):
        try:
            info = fetch_stock_data_cached(ticker_input)

            name = info['longName']
            price = info['currentPrice']
            currency = info['currency']

            if currency == 'GBp':
                price = price / 100.0
                currency = 'GBP'

            price_eur = price
            if currency != 'EUR' and isinstance(price, (int, float)) and price > 0:
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

            # --- COMPASS INTEGRITY SCORE (ROBUSTE MATHEMATIK) ---
            base_score = 50

            # 1. KGV / Verluste
            if isinstance(pe_ratio, (int, float)) and pe_ratio > 0:
                if pe_ratio < 15: base_score += 15
                elif pe_ratio < 30: base_score += 5
                else: base_score -= 10
            else:
                base_score -= 15

            # 2. Schulden-Bewertung
            de_actual = None
            if isinstance(debt_to_equity, (int, float)):
                de_actual = debt_to_equity / 100.0 if debt_to_equity > 500 else debt_to_equity
                if de_actual < 50: base_score += 15
                elif de_actual > 150: base_score -= 25
                elif de_actual > 100: base_score -= 10
            else:
                base_score -= 10

            # 3. Marktkapitalisierung
            if isinstance(market_cap, (int, float)) and market_cap > 0:
                if market_cap > 10_000_000_000: base_score += 15
                elif market_cap > 2_000_000_000: base_score += 5
            else:
                base_score -= 5

            # 4. Ausschüttungsquote
            if isinstance(payout_ratio, (int, float)) and 0.1 <= payout_ratio <= 0.7:
                base_score += 10

            # 5. Absturz- & Trend-Detektor
            if isinstance(fifty_two_high, (int, float)) and fifty_two_high > 0 and isinstance(price, (int, float)) and price > 0:
                drop_from_high = ((fifty_two_high - price) / fifty_two_high) * 100
                if drop_from_high > 40:
                    base_score -= 30
                elif drop_from_high > 25:
                    base_score -= 15

            integrity_score = max(10, min(100, base_score))

            # --- UI METRIKEN ---
            st.markdown(f"## 📊 Schiffslogbuch für **{name}** (`{ticker_input}`)")

            col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
            if currency == 'EUR':
                col_m1.metric("Kurs", f"{price:.2f} EUR")
            else:
                col_m1.metric("Kurs", f"{price:.2f} {currency}", f"≈ {price_eur:.2f} EUR")

            col_m2.metric("KGV", f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else "N/A (Verlust)")
            col_m3.metric("Schulden (D/E)", f"{de_actual:.1f}%" if isinstance(de_actual, (int, float)) else "N/A")
            col_m4.metric("Ausschüttung", f"{payout_ratio * 100:.1f}%" if isinstance(payout_ratio, (int, float)) and payout_ratio else "N/A")
            col_m5.metric("🧭 Integrity Score", f"{integrity_score} / 100")

            st.progress(integrity_score / 100, text=f"Compass Integrity Score: {integrity_score} Punkte")

            with st.expander("📌 Erweiterte Fundamentaldaten & Kursspanne anzeigen"):
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    st.markdown(f"**Marktkapitalisierung:** {market_cap:,} {currency}" if isinstance(market_cap, (int, float)) else f"**Marktkapitalisierung:** {market_cap}")
                with col_t2:
                    st.markdown(f"**52-Wochen-Spanne:** {fifty_two_low} – {fifty_two_high} {currency}")

            # --- INTERAKTIVER CHART (CACHED HISTORIE) ---
            df_chart = info['df_history']
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

            # --- STRUKTURIERTER PROMPT (KOMPAKT & AUF DEN PUNKT) ---
            prompt = f"""
            Du bist der 'Oma-Kurz-Kompass ULTRA' (Analyst auf Titanen-Niveau: Sander, Kurzweil, Munger, Marks, Tegmark).

            Analysiere {name} ({ticker_input}):
            - KGV: {pe_ratio if pe_ratio else 'Verlust/Keine Daten'}
            - Schulden D/E: {de_actual if de_actual else 'Unklar'}%
            - Score: {integrity_score}/100

            VERZICHTE komplett auf allgemeine Firmen-Beschreibungen oder Einleitungen! Gehe sofort in die Tiefe.

            Wichtigste Aufgabe:
            - Klumpenrisiken, Gegenpartei-Risiken & Vorstands-Narrative/Fata-Morganas aufdecken.
            - Passen Margen zum KGV? Gab es Zielverfehlungen oder abrupte Restrukturierungen?

            Nutze exakt folgende Abschnitte:
            SECTION_TRANSFORMATION: [Prüfung auf Zukunfts-Hype vs. reale Technologie]
            SECTION_DOMINO: [Burggraben, Klumpenrisiko & Domino-Detektor]
            SECTION_BILANZ: [Schulden, Zyklen & Zinsrisiko]
            SECTION_PROGNOSE: [36-Monats-Ausblick]
            STEIN_KLASSE: [Wähle exakt eine Option aus: Dividenden-Falle | Unpolierter Rohstein | Sich entwickelnder Stein | Solider Wert | Geschliffener Brillant]
            FAZIT: [Kurzer, sachlicher Kernaussage-Satz]
            """

            # KI Abfrage
            raw_text = generate_ki_analysis_cached(prompt)

            # --- STEIN-KLASSE EXTRACTION & DISPLAY ---
            stein_klasse = "Unbekannt"
            if "STEIN_KLASSE:" in raw_text:
                stein_line = [line for line in raw_text.split('\n') if "STEIN_KLASSE:" in line]
                if stein_line:
                    stein_klasse = stein_line[0].replace("STEIN_KLASSE:", "").strip()

            if "Geschliffener Brillant" in stein_klasse:
                st.success(f"💎 **Stein-Klasse: {stein_klasse}**")
            elif "Solider Wert" in stein_klasse:
                st.info(f"🛡️ **Stein-Klasse: {stein_klasse}**")
            elif "Sich entwickelnder Stein" in stein_klasse:
                st.info(f"🌱 **Stein-Klasse: {stein_klasse}**")
            elif "Unpolierter Rohstein" in stein_klasse:
                st.warning(f"🪨 **Stein-Klasse: {stein_klasse}**")
            elif "Dividenden-Falle" in stein_klasse:
                st.error(f"⚠️ **Stein-Klasse: {stein_klasse}**")
            else:
                st.warning(f"🏷️ **Stein-Klasse: {stein_klasse}**")

            st.markdown("---")

            # --- ANZEIGE DER SEKTIONEN ---
            def parse_section(text, tag):
                if tag in text:
                    sub = text.split(tag)[1]
                    for next_tag in ["SECTION_TRANSFORMATION:", "SECTION_DOMINO:", "SECTION_BILANZ:", "SECTION_PROGNOSE:", "STEIN_KLASSE:", "FAZIT:"]:
                        if next_tag != tag and next_tag in sub:
                            sub = sub.split(next_tag)[0]
                    return sub.strip()
                return ""

            sec_trans = parse_section(raw_text, "SECTION_TRANSFORMATION:")
            sec_domino = parse_section(raw_text, "SECTION_DOMINO:")
            sec_bilanz = parse_section(raw_text, "SECTION_BILANZ:")
            sec_prog = parse_section(raw_text, "SECTION_PROGNOSE:")
            fazit_txt = parse_section(raw_text, "FAZIT:")

            if sec_trans:
                with st.container(border=True):
                    st.markdown("### 🚀 1. Transformations- & Zukunfts-Faktor")
                    st.markdown(sec_trans)

            if sec_domino:
                with st.container(border=True):
                    st.markdown("### 🏰 2. Burggraben & Domino-Story-Detektor")
                    st.markdown(sec_domino)

            if sec_bilanz:
                with st.container(border=True):
                    st.markdown("### 🏛️ 3. Bilanzen, Schulden & Zyklen")
                    st.markdown(sec_bilanz)

            if sec_prog:
                with st.container(border=True):
                    st.markdown("### ⏳ 4. 36-Monats-Horizont & Prognose")
                    st.markdown(sec_prog)

            if fazit_txt:
                st.markdown("---")
                st.info(f"💡 **FAZIT:** {fazit_txt}")

        except Exception as e:
            if "429" in str(e):
                st.warning("⏳ API-Pause: Bitte 20 Sekunden warten.")
            else:
                st.error(f"Fehler: {str(e)}")
