import streamlit as st
import yfinance as yf
import plotly.express as px
import os

# Page Config
st.set_page_config(
    page_title="OMA-KURZ-KOMPASS ULTRA v5.3",
    page_icon="🪙",
    layout="wide"
)

# Custom CSS für edles Design
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    h1 { color: #f39c12; font-family: 'Georgia', serif; text-align: center; }
    .subtitle { color: #bdc3c7; text-align: center; font-style: italic; font-size: 0.9em; margin-bottom: 25px; }
    .stMetric { background-color: #161b22; padding: 10px; border-radius: 8px; border: 1px solid #30363d; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1>🪙 OMA-KURZ-KOMPASS ULTRA v5.3</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>„Substanz, exponentielle Technologie, Burggräben, Zyklen & Theranos-Nikola-Detektor“</p>", unsafe_allow_html=True)

# 1. Datenabfrage mit Caching (Verhindert API-Sperren & glättet Splits)
@st.cache_data(ttl=3600)
def load_stock_data(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    # auto_adjust=True korrigiert historische Aktien-Splits sauber!
    df = ticker.history(period="5y", auto_adjust=True)
    info = ticker.info
    return df, info, ticker

# Eingabe-Bereich
col_in1, col_in2 = st.columns([3, 1])
with col_in1:
    ticker_input = st.text_input("Aktien-Ticker eingeben (z.B. FTNT, ALNY, ALV.DE, 6501.T):", value="FTNT").strip().upper()

if ticker_input:
    try:
        df_hist, info, ticker_obj = load_stock_data(ticker_input)
        
        if df_hist.empty:
            st.error(f"Keine Daten für Ticker '{ticker_input}' gefunden.")
        else:
            # Kennzahlen ziehen
            current_price = info.get('currentPrice') or info.get('regularMarketPrice') or (df_hist['Close'].iloc[-1] if not df_hist.empty else 0)
            currency = info.get('currency', 'USD')
            pe_ratio = info.get('trailingPE', 'N/A')
            debt_to_equity = info.get('debtToEquity', 'N/A')
            payout_ratio = info.get('payoutRatio', 'N/A')
            long_name = info.get('longName', ticker_input)
            market_cap = info.get('marketCap', 'N/A')

            # Währung umrechnen (EUR Kurs-Schätzung falls USD)
            eur_price = current_price * 0.87 if currency == "USD" else current_price

            # Integrity Score Berechnung
            integrity_score = 80  # Basiswert
            if pe_ratio != 'N/A' and pe_ratio < 25: integrity_score += 10
            if debt_to_equity != 'N/A' and debt_to_equity < 100: integrity_score += 10

            # UI Header & Schiffslogbuch
            st.markdown(f"## 📊 Schiffslogbuch für {long_name} ( <span style='color:#2ecc71;'>{ticker_input}</span> )", unsafe_allow_html=True)
            
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Kurs", f"{current_price:.2f} {currency}", delta=f"≈ {eur_price:.2f} EUR")
            m2.metric("KGV", f"{pe_ratio if pe_ratio == 'N/A' else round(pe_ratio, 2)}")
            m3.metric("Schulden (D/E)", f"{debt_to_equity if debt_to_equity == 'N/A' else str(round(debt_to_equity, 2)) + '%'}")
            m4.metric("Ausschüttung", f"{payout_ratio if payout_ratio == 'N/A' else str(round(payout_ratio * 100, 2)) + '%'}")
            m5.metric("🛡️ Integrity Score", f"{integrity_score} / 100")

            st.progress(integrity_score / 100)

            # Interactive Plotly Chart
            st.markdown("### 📈 Kursverlauf & Marktzyklus")
            timeframe = st.radio("Zeitraum wählen:", ["6m", "1y", "3y", "5y"], index=1, horizontal=True)

            tf_map = {"6m": 126, "1y": 252, "3y": 756, "5y": 1260}
            sliced_df = df_hist.tail(tf_map.get(timeframe, 252))

            fig = px.line(sliced_df, y='Close', labels={'Close': 'Kurs', 'Date': 'Datum'})
            fig.update_traces(line_color='#f1c40f', line_width=2)
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#ffffff'),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#30363d')
            )
            st.plotly_chart(fig, use_container_width=True)

            # Details & Klappbox
            with st.expander("📌 Erweiterte Fundamentaldaten & Kursspanne anzeigen"):
                st.write(f"**Marktkapitalisierung:** {market_cap:,} {currency}" if isinstance(market_cap, (int, float)) else f"**Marktkapitalisierung:** {market_cap}")
                st.write(f"**52-Wochen-Spanne:** {info.get('fiftyTwoWeekLow', 'N/A')} - {info.get('fiftyTwoWeekHigh', 'N/A')} {currency}")

            st.divider()

            # --- DAS HERZSTÜCK: DER OMA-KURZ-ULTRA PROMPT ---
            st.markdown("### 🧠 Tiefenanalyse: Das ULTRA-Quartett & Theranos-Nikola-Detektor")
            
            prompt_text = f"""
Du bist der Chefanalyst des OMA-KURZ-KOMPASS ULTRA v5.3. 
Analysiere die folgende Aktie: {long_name} ({ticker_input}).

Aktuelle Daten:
- Kurs: {current_price} {currency}
- KGV: {pe_ratio}
- Schulden (D/E): {debt_to_equity}

Wende streng die 4 ULTRA-Prüfsteine an:

1. **Sparten & Geschäftsfelder (Oma-Kurz-Blick):**
   Womit verdient die Firma ihr Geld tatsächlich? Welche Zukunftsfelder werden abgedeckt?

2. **Exponentielle Technologie & KI-Trends:**
   Profi tieren sie von Mega-Trends (KI, Daten, Infrastruktur)? Ist es echte Technologie oder Hype?

3. **🚨 THERANOS-NIKOLA-DETEKTOR (Prüfstein der harten Realität):**
   - Basiert das Geschäft auf echten, auszuliefernden Produkten/Services und auditierten Umsätzen?
   - Oder gibt es Anzeichen für leere Hype-Versprechen, ungeklärte Prototypen oder "rollende LKW-Hügel"-Rhetorik?
   - Prüfe auf Klumpenrisiken (starke Abhängigkeit von wackeligen Großkunden/Partnern).

4. **Sander & Marks Synthese (Burggraben, Bewertung & Marktzyklus):**
   - Hat die Firma einen uneinnehmbaren Burggraben (Moat)?
   - Wo befinden wir uns im Marktzyklus? Ist die Aktie fair bewertet oder überhitzt?

Gib dein Urteil prägnant, strukturiert und in klarer Sprache ab.
"""

            with st.expander("📜 Generierten Prompt für KI-Analyse einsehen"):
                st.code(prompt_text, language="markdown")

    except Exception as e:
        st.error(f"Fehler beim Laden der Daten: {e}")
        st.info("💡 API-Pause: Bitte 20-30 Sekunden warten und Seite neu laden.")
