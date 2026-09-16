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

# --- MODELL INITIALISIERUNG ---
model = genai.GenerativeModel(
    model_name="gemini-3.6-flash",
    generation_config={
        "temperature": 0.3,
        "max_output_tokens": 2048,
    }
)

# --- SEITENLEISTE: GLOSSAR & PHILOSOPHIE ---
with st.sidebar:
    st.title("📚 Der Edelstein-Glossar")
    st.markdown("""
    Hier siehst du die Klassifizierung unserer Anlage-Steine nach Beate Sander & Ray Kurzweil:
    
    * **🪨 Unpolierter Rohstein:**  
      Unternehmen mit viel Potenzial, aber noch Ecken, Kanten oder hohem Risiko. Muss erst geschliffen werden.
      
    * **🌱 Sich entwickelnder Stein:**  
      Wachsende Substanz, die Innovationen skaliert und auf dem Weg zu wahrer Größe ist (Zukunfts-Accelerator).
      
    * **🛡️ Solider Wert:**  
      Stabiler Fels in der Brandung. Solide Bilanzen, krisenfester Cashflow, ideal für langfristigen Aufbau.
      
    * **💎 Geschliffener Brillant:**  
      Die absolute Königsklasse. Unknackbares Geschäftsmodell, starker Burggraben und exponentielles Wachstum.
      
    * **⚠️ Dividenden-Falle:**  
      Vorsicht! Hohe Ausschüttungen, die aber durch Schulden erkauft sind und Innovationen abwürgen.
    """)
    st.markdown("---")
    st.caption("Oma-Kurz-Kompass ULTRA v2")

# --- HEADER & SUCHE ---
st.title("💎 Oma-Kurz-Kompass ULTRA v2")
st.caption("KI-gestützte Bilanz- & Wachstumsanalyse mit Stein-Hierarchie & Glossar")

st.markdown("---")

col_search, col_space = st.columns([2, 1])
with col_search:
    ticker_input = st.text_input("Aktien-Ticker eingeben (z.B. AAPL, MSFT, TSLA, ENB):", "AAPL").upper()
    analyze_btn = st.button("🚀 Analyse starten", use_container_width=True, type="primary")

if analyze_btn and ticker_input:
    with st.spinner(f"Lade Finanzdaten und starte KI-Stresstest für {ticker_input}..."):
        try:
            stock = yf.Ticker(ticker_input)
            info = stock.info
            
            name = info.get('longName', ticker_input)
            price = info.get('currentPrice', info.get('regularMarketPrice', 0.0))
            currency = info.get('currency', 'USD')
            pe_ratio = info.get('trailingPE', 'N/A')
            debt_to_equity = info.get('debtToEquity', 'N/A')
            payout_ratio = info.get('payoutRatio', 0.0)
            
            st.markdown(f"## 📊 Analyse für **{name}** (`{ticker_input}`)")
            
            # --- METRIK-KARTEN OBEN ---
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Kurs", f"{price:.2f} {currency}" if isinstance(price, (int, float)) else "N/A")
            m2.metric("KGV (PE Ratio)", f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else pe_ratio)
            m3.metric("Schulden (Debt/Equity)", f"{debt_to_equity}%" if debt_to_equity != 'N/A' else 'N/A')
            m4.metric("Ausschüttungsquote", f"{payout_ratio * 100:.1f}%" if isinstance(payout_ratio, (int, float)) else "N/A")
            
            st.markdown("---")
            
            # --- PROMPT FÜR DIE KI ---
           prompt = f"""
            Du bist der 'Oma-Kurz-Kompass' - ein neutraler, analytischer Finanzkompass nach Beate Sander (Substanz) und Ray Kurzweil (exponentielles Wachstum).
            Analysiere {name} ({ticker_input}) rein objektiv anhand der Kennzahlen:
            - KGV: {pe_ratio}
            - Verschuldung (Debt/Equity): {debt_to_equity}%
            - Ausschüttungsquote: {payout_ratio * 100 if payout_ratio else 'N/A'}%
            
            WICHTIG: Gib KEINE direkten Anlageempfehlungen wie "Kaufen" oder "Finger weg!". Keine Anlageberatung! Formuliere stattdessen objektiv, wie sich das Unternehmen im Depot verhalten könnte (z.B. bei breiter Streuung, kleinen Tranchen oder für bestimmte Anlegertypen).
            
            Bewerte die Aktie prägnant in genau dieser Struktur:
            
            ### 1. Schulden & Stabilität
            [Deine Analyse]
            
            ### 2. Dividenden-Sicherheit vs. Falle
            [Deine Analyse]
            
            ### 3. Zukunftspotenzial / Skalierung (Der Accelerator)
            [Deine Analyse]
            
            ### STEIN-KLASSE: [Wähle genau eines aus: Geschliffener Brillant | Solider Wert | Sich entwickelnder Stein | Unpolierter Rohstein | Dividenden-Falle]
            ### FAZIT: [Ein sachliches, ausgewogenes Fazit für ein diversifiziertes Depot ohne Handlungsbefehl]
            """
            # --- STEIN-KLASSEN BADGES ---
            if "Geschliffener Brillant" in raw_text:
                st.success("💎 **Stein-Klasse: Geschliffener Brillant** – Unknackbares Geschäftsmodell & Exponentielles Wachstum")
            elif "Solider Wert" in raw_text:
                st.info("🛡️ **Stein-Klasse: Solider Wert** – Fels in der Brandung mit gesunder Substanz")
            elif "Sich entwickelnder Stein" in raw_text:
                st.warning("🌱 **Stein-Klasse: Sich entwickelnder Stein** – Wachsendes Potenzial auf dem Weg nach oben")
            elif "Unpolierter Rohstein" in raw_text:
                st.warning("🪨 **Stein-Klasse: Unpolierter Rohstein** – Viel Potenzial, aber noch mit Risiken behaftet")
            elif "Dividenden-Falle" in raw_text:
                st.error("⚠️ **Stein-Klasse: Dividenden-Falle** – Hohe Ausschüttung, aber gefährliche Bilanzen")
                
            st.markdown("---")
            st.markdown(raw_text)
            
        except Exception as e:
            st.error(f"Fehler bei der Analyse: {str(e)}")
