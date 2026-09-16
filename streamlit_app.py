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

# --- SEITENLEISTE: GLOSSAR & TICKER-HILFE ---
with st.sidebar:
    st.title("📚 Der Edelstein-Glossar")
    st.markdown("""
    * **⚠️ Dividenden-Falle:** Hohe Ausschüttungen durch Schulden erkauft.
    * **🪨 Unpolierter Rohstein:** Viel Potenzial, aber hohe Risiken.
    * **🌱 Sich entwickelnder Stein:** Wachsende Substanz, starker Accelerator.
    * **🛡️ Solider Wert:** Stabiler Fels in der Brandung, krisenfester Cashflow.
    * **💎 Geschliffener Brillant:** Unknackbarer Burggraben & exponentielles Wachstum.
    """)
    
    st.markdown("---")
    st.title("💡 Ticker-Wegweiser")
    st.markdown("""
    Manchmal sucht man vergeblich nach den internationalen Kürzeln. Hier sind wichtige Kennungen:
    * **🇯🇵 Japan (Tokyo):** Zahlen + `.T`  
      *(z.B. Sony: `6758.T`, Toyota: `7203.T`, Shin-Etsu: `4063.T`, Nintendo: `7974.T`)*
    * **🇬🇧 UK (London):** Kürzel + `.L`  
      *(z.B. Rentokil: `RTO.L`, Shell: `SHEL.L`)*
    * **🇺🇸 USA:** Normales Kürzel  
      *(z.B. Apple: `AAPL`, Microsoft: `MSFT`)*
    * **🇨🇦 Kanada:** Normales Kürzel  
      *(z.B. Enbridge: `ENB`)*
    """)
    st.markdown("---")
    st.caption("Oma-Kurz-Kompass ULTRA v2")

# --- HEADER & SUCHE ---
st.title("💎 Oma-Kurz-Kompass ULTRA v2")
st.caption("KI-gestützte Bilanz- & Wachstumsanalyse mit internationalem Ticker-Wegweiser & Farb-Design")

st.markdown("---")

col_search, col_space = st.columns([2, 1])
with col_search:
    ticker_input = st.text_input("Aktien-Ticker eingeben (z.B. AAPL, ENB, 6758.T, RTO.L):", "AAPL").upper()
    analyze_btn = st.button("🚀 Analyse starten", use_container_width=True, type="primary")

if analyze_btn and ticker_input:
    with st.spinner(f"Lade internationale Börsendaten & starte KI-Stresstest für {ticker_input}..."):
        try:
            stock = yf.Ticker(ticker_input)
            info = stock.info
            
            name = info.get('longName', ticker_input)
            price = info.get('currentPrice', info.get('regularMarketPrice', 0.0))
            currency = info.get('currency', 'USD')
            
            # --- WÄHRUNGS- & PENCE-KORREKTUR ---
            if currency == 'GBp':
                price = price / 100.0
                currency = 'GBP'
            
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
            
            # --- NEUTRALER PROMPT FÜR DIE KI ---
            prompt = f"""
            Du bist der 'Oma-Kurz-Kompass' - ein neutraler, analytischer Finanzkompass nach Beate Sander (Substanz) und Ray Kurzweil (exponentielles Wachstum).
            Analysiere {name} ({ticker_input}) rein objektiv anhand der Kennzahlen:
            - Währung / Börsenplatz: {currency}
            - KGV: {pe_ratio}
            - Verschuldung (Debt/Equity): {debt_to_equity}%
            - Ausschüttungsquote: {payout_ratio * 100 if payout_ratio else 'N/A'}%
            
            WICHTIG: Gib KEINE direkten Anlageempfehlungen wie "Kaufen" oder "Finger weg!". Keine Anlageberatung! Formuliere stattdessen objektiv, wie sich das Unternehmen in einem breit diversifizierten Depot verhalten könnte.
            
            Bewerte die Aktie prägnant in genau dieser Struktur (verwende exakt diese Überschriften mit Doppelkreuz):
            
            ## 1. Schulden & Stabilität
            [Deine Analyse]
            
            ## 2. Dividenden-Sicherheit vs. Falle
            [Deine Analyse]
            
            ## 3. Zukunftspotenzial / Skalierung (Der Accelerator)
            [Deine Analyse]
            
            ### STEIN-KLASSE: [Wähle exakt eines dieser Keywords: Dividenden-Falle | Unpolierter Rohstein | Sich entwickelnder Stein | Solider Wert | Geschliffener Brillant]
            ### FAZIT: [Ein sachliches, ausgewogenes Fazit für ein diversifiziertes Depot ohne Handlungsbefehl]
            """
            
            response = model.generate_content(prompt)
            raw_text = response.text
            
            # --- TEXT PARSEN UND FARBLICH IN KARTEN / CONTAINER EINBETTEN ---
            # Wir splitten die KI-Antwort nach den Abschnitten, um sie psychologisch ansprechend darzustellen
            parts = raw_text.split("## ")
            
            # --- STEIN-KLASSEN BADGES ---
            if "Geschliffener Brillant" in raw_text:
                st.success("💎 **Stein-Klasse: Geschliffener Brillant** – Unknackbares Geschäftsmodell & Exponentielles Wachstum")
            elif "Solider Wert" in raw_text:
                st.info("🛡️ **Stein-Klasse: Solider Wert** – Fels in der Brandung mit gesunder Substanz")
            elif "Sich entwickelnder Stein" in raw_text:
                st.info("🌱 **Stein-Klasse: Sich entwickelnder Stein** – Wachsendes Potenzial auf dem Weg nach oben")
            elif "Unpolierter Rohstein" in raw_text:
                st.warning("🪨 **Stein-Klasse: Unpolierter Rohstein** – Viel Potenzial, aber noch mit Risiken behaftet")
            elif "Dividenden-Falle" in raw_text:
                st.error("⚠️ **Stein-Klasse: Dividenden-Falle** – Hohe Ausschüttung, aber gefährliche Bilanzen")
                
            st.markdown("---")
            
            # Schöne farbige visuelle Container für die 3 Kernbereiche
            for part in parts:
                if part.startswith("1. Schulden"):
                    with st.container(border=True):
                        st.markdown("### 🏛️ 1. Schulden & Stabilität")
                        st.markdown(part.replace("1. Schulden & Stabilität", "").strip())
                elif part.startswith("2. Dividenden"):
                    with st.container(border=True):
                        st.markdown("### 💰 2. Dividenden-Sicherheit vs. Falle")
                        st.markdown(part.replace("2. Dividenden-Sicherheit vs. Falle", "").strip())
                elif part.startswith("3. Zukunftspotenzial"):
                    with st.container(border=True):
                        st.markdown("### 🚀 3. Zukunftspotenzial / Skalierung (Der Accelerator)")
                        st.markdown(part.replace("3. Zukunftspotenzial / Skalierung (Der Accelerator)", "").strip())
            
            # Fazit separat am Ende ausgeben
            if "FAZIT:" in raw_text:
                fazit_text = raw_text.split("FAZIT:")[-1].strip()
                st.markdown("---")
                st.info(f"💡 **FAZIT:** {fazit_text}")
            
        except Exception as e:
            st.error(f"Fehler bei der Analyse: {str(e)}")
