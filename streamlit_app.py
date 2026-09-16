import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai
from datetime import datetime

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="Oma-Kurz-Kompass ULTRA v2",
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
    st.title("🧭 Der Navigations-Ratgeber")
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
    * **🇯🇵 Japan (Tokyo):** Zahlen + `.T`  
      *(z.B. Sony: `6758.T`, Toyota: `7203.T`)*
    * **🇬🇧 UK (London):** Kürzel + `.L`  
      *(z.B. Rentokil: `RTO.L`, Shell: `SHEL.L`)*
    * **🇺🇸 USA:** Normales Kürzel  
      *(z.B. Apple: `AAPL`)*
    * **🇩🇪 Deutschland:** Kürzel + `.DE`  
      *(z.B. RWE: `RWE.DE`)*
    """)
    st.markdown("---")
    st.caption("Oma-Kurz-Kompass ULTRA v2 - Edition 2026")

# --- HEADER IM HISTORISCHEN ENDPUNKT-LOOK ---
st.markdown("""
<div class="main-header">
    <h1>🧭 OMA-KURZ-KOMPASS ULTRA</h1>
    <p>„Die Entdeckung des weltweiten Wertes – Substanz nach Beate Sander & exponentielles Wachstum nach Ray Kurzweil“</p>
</div>
""", unsafe_allow_html=True)

col_search, col_space = st.columns([2, 1])
with col_search:
    ticker_input = st.text_input("Aktien-Ticker eingeben (z.B. AAPL, RWE.DE, 6758.T, RTO.L):", "AAPL").upper()
    analyze_btn = st.button("🚀 Kurs aufnehmen & Analyse starten", use_container_width=True, type="primary")

if analyze_btn and ticker_input:
    with st.spinner(f"Navigiere durch die Weltmärkte und analysiere Bilanz von {ticker_input}..."):
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
            market_cap = info.get('marketCap', 'N/A')
            fifty_two_high = info.get('fiftyTwoWeekHigh', 'N/A')
            fifty_two_low = info.get('fiftyTwoWeekLow', 'N/A')
            
            st.markdown(f"## 📊 Schiffslogbuch für **{name}** (`{ticker_input}`)")
            
            # --- METRIK-KARTEN OBEN ---
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Kurs", f"{price:.2f} {currency}" if isinstance(price, (int, float)) else "N/A")
            m2.metric("KGV (PE Ratio)", f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else pe_ratio)
            m3.metric("Schulden (Debt/Equity)", f"{debt_to_equity}%" if debt_to_equity != 'N/A' else 'N/A')
            m4.metric("Ausschüttungsquote", f"{payout_ratio * 100:.1f}%" if isinstance(payout_ratio, (int, float)) else "N/A")
            
            # --- ERWEITERTE DATEN-TABELLE (PROFI-LOOK) ---
            with st.expander("📌 Erweiterte Fundamentaldaten & Kursspanne anzeigen"):
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    st.markdown(f"**Marktkapitalisierung:** {market_cap:,} {currency}" if isinstance(market_cap, (int, float)) else f"**Marktkapitalisierung:** {market_cap}")
                with col_t2:
                    st.markdown(f"**52-Wochen-Spanne:** {fifty_two_low} – {fifty_two_high} {currency}")

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
                
            # --- DOWNLOAD-BUTTON FÜR DAS LOGBUCH ---
            st.markdown("---")
            report_filename = f"Kompass_Analyse_{ticker_input}_{datetime.now().strftime('%Y-%m-%d')}.txt"
            full_report_content = f"OMA-KURZ-KOMPASS LOGBUCH\nAktie: {name} ({ticker_input})\nDatum: {datetime.now().strftime('%Y-%m-%d')}\nKurs: {price} {currency}\nKGV: {pe_ratio}\n\n{raw_text}"
            
            st.download_button(
                label="📥 Analyse-Logbuch als Text-Datei herunterladen",
                data=full_report_content,
                file_name=report_filename,
                mime="text/plain",
                use_container_width=True
            )
            
        except Exception as e:
            st.error(f"Fehler bei der Navigation/Analyse: {str(e)}")
