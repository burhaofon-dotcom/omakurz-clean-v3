import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="Oma-Kurz-Kompass ULTRA v2",
    page_icon="💎",
    layout="wide"
)

# --- SICHERE API-KEY INITIALISIERUNG ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("🚨 Sicherheitsfehler: Kein Gemini API-Key in den Streamlit-Secrets gefunden! Bitte hinterlege GEMINI_API_KEY in den Secrets.")
    st.stop()

# --- MODELL AUSWAHL ---
generation_config = {
    "temperature": 0.3,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 2048,
}

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config={
        "temperature": 0.3,
        "max_output_tokens": 2048,
    }


st.title("💎 Oma-Kurz-Kompass ULTRA v2")
st.caption("KI-gestützte Bilanz- & Wachstumsanalyse nach Beate Sander & Ray Kurzweil")

ticker_input = st.text_input("Aktien-Ticker eingeben (z.B. AAPL, MSFT, TSLA, ENB):", "AAPL").upper()

if st.button("🚀 Analyse starten", use_container_width=True):
    with st.spinner(f"Analysiere {ticker_input}..."):
        try:
            stock = yf.Ticker(ticker_input)
            info = stock.info
            
            name = info.get('longName', ticker_input)
            price = info.get('currentPrice', info.get('regularMarketPrice', 0.0))
            currency = info.get('currency', 'USD')
            pe_ratio = info.get('trailingPE', 'N/A')
            debt_to_equity = info.get('debtToEquity', 'N/A')
            payout_ratio = info.get('payoutRatio', 0.0)
            
            prompt = f"""
            Du bist der 'Oma-Kurz-Kompass' - ein gnadenloser Finanzanalyst nach Beate Sander (Substanz) und Ray Kurzweil (exponentielles Wachstum).
            Analysiere {name} ({ticker_input}):
            - KGV: {pe_ratio}
            - Verschuldung (Debt/Equity): {debt_to_equity}%
            - Ausschüttungsquote: {payout_ratio * 100 if payout_ratio else 'N/A'}%
            
            Bewerte die Aktie kurz und prägnant in 3 Abschnitten:
            1. Schulden & Stabilität
            2. Dividenden-Sicherheit vs. Falle
            3. Zukunftspotenzial / Skalierung
            
            Fazit mit 'Härtegrad': [Rohstein / Dividenden-Falle / Solider Wert / Brillant]
            """
            
            response = model.generate_content(prompt)
            
            st.subheader(f"Ergebnis für {name} ({currency} {price})")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"Fehler bei der Analyse: {str(e)}")
