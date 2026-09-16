import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import time

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
        "max_output_tokens": 3000,
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
      *(z.B. Fujifilm: `4901.T`, Sony: `6758.T`)*
    * **🇬🇧 UK (London):** Kürzel + `.L`  
      *(z.B. Rentokil: `RTO.L`, Shell: `SHEL.L`)*
    * **🇺🇸 USA:** Normales Kürzel  
      *(z.B. Alnylam: `ALNY`, Apple: `AAPL`)*
    * **🇩🇪 Deutschland:** Kürzel + `.DE`  
      *(z.B. Allianz: `ALV.DE`, RWE: `RWE.DE`)*
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
    ticker_input = st.text_input("Aktien-Ticker eingeben (z.B. ALNY, ALV.DE, 4901.T, AAPL):", "ALNY").upper()
    analyze_btn = st.button("🚀 Kurs aufnehmen & Tiefenanalyse starten", use_container_width=True, type="primary")

if analyze_btn and ticker_input:
    with st.spinner(f"Navigiere durch die Weltmärkte, durchleuchte Sparten und analysiere Bilanzen von {ticker_input}..."):
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
            
            # --- AUTOMATISCHE WECHSELKURS-UMRECHNUNG IN EURO ---
            price_eur = price
            if currency != 'EUR' and isinstance(price, (int, float)):
                try:
                    fx_ticker = yf.Ticker(f"{currency}EUR=X")
                    fx_info = fx_ticker.info
                    fx_rate = fx_info.get('currentPrice', fx_info.get('regularMarketPrice', None))
                    if not fx_rate:
                        fx_hist = fx_ticker.history(period="1d")
                        if not fx_hist.empty:
                            fx_rate = fx_hist['Close'].iloc[-1]
                    if fx_rate:
                        price_eur = price * fx_rate
                except Exception:
                    pass
            
            pe_ratio = info.get('trailingPE', 'N/A')
            debt_to_equity = info.get('debtToEquity', 'N/A')
            payout_ratio = info.get('payoutRatio', 0.0)
            market_cap = info.get('marketCap', 'N/A')
            fifty_two_high = info.get('fiftyTwoWeekHigh', 'N/A')
            fifty_two_low = info.get('fiftyTwoWeekLow', 'N/A')
            
            st.markdown(f"## 📊 Schiffslogbuch für **{name}** (`{ticker_input}`)")
            
            # --- METRIK-KARTEN OBEN ---
            m1, m2, m3, m4 = st.columns(4)
            if currency == 'EUR':
                m1.metric("Kurs", f"{price:.2f} EUR")
            else:
                m1.metric("Kurs", f"{price:.2f} {currency}", f"≈ {price_eur:.2f} EUR")
                
            m2.metric("KGV (PE Ratio)", f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else pe_ratio)
            m3.metric("Schulden (Debt/Equity)", f"{debt_to_equity}%" if debt_to_equity != 'N/A' else 'N/A')
            m4.metric("Ausschüttungsquote", f"{payout_ratio * 100:.1f}%" if isinstance(payout_ratio, (int, float)) else "N/A")
            
            # --- ERWEITERTE DATEN-TABELLE ---
            with st.expander("📌 Erweiterte Fundamentaldaten & Kursspanne anzeigen"):
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    st.markdown(f"**Marktkapitalisierung:** {market_cap:,} {currency}" if isinstance(market_cap, (int, float)) else f"**Marktkapitalisierung:** {market_cap}")
                with col_t2:
                    st.markdown(f"**52-Wochen-Spanne:** {fifty_two_low} – {fifty_two_high} {currency}")

            st.markdown("---")
            
            # --- ERWEITERTER PROMPT MIT SPARTEN & TRANSFORMATION ---
            prompt = f"""
            Du bist der 'Oma-Kurz-Kompass' - ein neutraler, analytischer Finanzkompass nach Beate Sander (Substanz, Bilanzen, Diversifikation) und Ray Kurzweil (exponentielles Wachstum, technologische Disruption, Transformation).
            Analysiere {name} ({ticker_input}) tiefgehend anhand der Kennzahlen:
            - Währung / Börsenplatz: {currency} (ca. {price_eur:.2f} EUR)
            - KGV: {pe_ratio}
            - Verschuldung (Debt/Equity): {debt_to_equity}%
            - Ausschüttungsquote: {payout_ratio * 100 if payout_ratio else 'N/A'}%
            
            WICHTIG: Gib KEINE direkten Anlageempfehlungen wie "Kaufen" oder "Finger weg!". Keine Anlageberatung! Formuliere stattdessen objektiv.
            
            Beantworte und bewerte das Unternehmen in genau dieser Struktur (verwende exakt diese Überschriften mit Doppelkreuz):
            
            ## 1. Sparten & Geschäftsfelder (Womit wird Geld verdient?)
            [Beschreibe präzise die aktuellen Geschäftssäulen, Segmente oder medizinischen/technologischen Plattformen des Unternehmens.]
            
            ## 2. Der Transformations-Faktor (Wandel & Evolution)
            [Wie wandelt sich das Unternehmen strukturell? (z.B. alte vs. neue Geschäftsfelder, Diversifikation, Technologiewandel wie Fujifilm von Film zu Medizintechnik oder Alnylam von seltener Genetik zu breiterer RNAi-Pipeline).]
            
            ## 3. Schulden & Stabilität (Sander-Blick)
            [Analysiere Bilanz, Verschuldung und finanzielle Widerstandskraft.]
            
            ## 4. Dividenden-Sicherheit vs. Falle
            [Bewerte die Ausschüttung im Verhältnis zum Cashflow und Geschäftsmodell.]
            
            ## 5. 36-Monats-Horizont (Sander-Kurzweil-Prognose)
            [Wie könnte sich dieses Unternehmen in den nächsten 3 Jahren in einem diversifizierten Depot im Spannungsfeld aus solider Substanz und technologischer Skalierung entwickeln?]
            
            ### STEIN-KLASSE: [Wähle exakt eines dieser Keywords: Dividenden-Falle | Unpolierter Rohstein | Sich entwickelnder Stein | Solider Wert | Geschliffener Brillant]
            ### FAZIT: [Ein sachliches, ausgewogenes Fazit für ein diversifiziertes Depot ohne Handlungsbefehl]
            """
            
            # --- ROBUSTE KI-ABFRAGE MIT RETRY ---
            response = None
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = model.generate_content(prompt)
                    break
                except Exception as api_err:
                    if "429" in str(api_err) and attempt < max_retries - 1:
                        time.sleep(10)
                    else:
                        raise api_err
            
            raw_text = response.text
            
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
            
            # --- TEXT PARSEN UND IN VISUELLE CONTAINER PACKEN ---
            parts = raw_text.split("## ")
            for part in parts:
                if part.startswith("1. Sparten"):
                    with st.container(border=True):
                        st.markdown("### 🧩 1. Sparten & Geschäftsfelder (Womit wird Geld verdient?)")
                        st.markdown(part.replace("1. Sparten & Geschäftsfelder (Womit wird Geld verdient?)", "").strip())
                elif part.startswith("2. Der Transformations"):
                    with st.container(border=True):
                        st.markdown("### 🔄 2. Der Transformations-Faktor (Wandel & Evolution)")
                        st.markdown(part.replace("2. Der Transformations-Faktor (Wandel & Evolution)", "").strip())
                elif part.startswith("3. Schulden"):
                    with st.container(border=True):
                        st.markdown("### 🏛️ 3. Schulden & Stabilität (Sander-Blick)")
                        st.markdown(part.replace("3. Schulden & Stabilität (Sander-Blick)", "").strip())
                elif part.startswith("4. Dividenden"):
                    with st.container(border=True):
                        st.markdown("### 💰 4. Dividenden-Sicherheit vs. Falle")
                        st.markdown(part.replace("4. Dividenden-Sicherheit vs. Falle", "").strip())
                elif part.startswith("5. 36-Monats"):
                    with st.container(border=True):
                        st.markdown("### ⏳ 5. 36-Monats-Horizont (Sander-Kurzweil-Prognose)")
                        st.markdown(part.replace("5. 36-Monats-Horizont (Sander-Kurzweil-Prognose)", "").strip())
            
            # Fazit separat ausgeben
            if "FAZIT:" in raw_text:
                fazit_text = raw_text.split("FAZIT:")[-1].strip()
                st.markdown("---")
                st.info(f"💡 **FAZIT:** {fazit_text}")
                
            # --- DOWNLOAD-BUTTON ---
            st.markdown("---")
            report_filename = f"Kompass_Analyse_{ticker_input}_{datetime.now().strftime('%Y-%m-%d')}.txt"
            full_report_content = f"OMA-KURZ-KOMPASS LOGBUCH\nAktie: {name} ({ticker_input})\nDatum: {datetime.now().strftime('%Y-%m-%d')}\nKurs: {price} {currency} (≈ {price_eur:.2f} EUR)\nKGV: {pe_ratio}\n\n{raw_text}"
            
            st.download_button(
                label="📥 Analyse-Logbuch als Text-Datei herunterladen",
                data=full_report_content,
                file_name=report_filename,
                mime="text/plain",
                use_container_width=True
            )
            
        except Exception as e:
            if "429" in str(e):
                st.warning("⏳ Das API-Limit der kostenlosen Stufe wurde kurzzeitig erreicht. Bitte warte einen Moment (ca. 15–30 Sekunden) und starte die Analyse dann erneut.")
            else:
                st.error(f"Fehler bei der Navigation/Analyse: {str(e)}")
