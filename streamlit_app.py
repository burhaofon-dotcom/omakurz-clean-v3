import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import time

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="Oma-Kurz-Kompass ULTRA v4",
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
    st.caption("Oma-Kurz-Kompass ULTRA v4")

# --- HEADER ---
st.markdown("""
<div class="main-header">
    <h1>🧭 OMA-KURZ-KOMPASS ULTRA</h1>
    <p>„Substanz, exponentielle Technologie, Burggräben, Zyklen & Theranos-Nikola-Detektor“</p>
</div>
""", unsafe_allow_html=True)

col_search, col_space = st.columns([2, 1])
with col_search:
    ticker_input = st.text_input("Aktien-Ticker eingeben (z.B. ALNY, ALV.DE, 4901.T):", "ALNY").upper()
    analyze_btn = st.button("🚀 Kurs aufnehmen & Tiefenanalyse starten", use_container_width=True, type="primary")

if analyze_btn and ticker_input:
    with st.spinner(f"Führe Theranos-Nikola-Detektor aus & durchleuchte {ticker_input} durch die Brille der Titanen..."):
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
            
            pe_ratio = info.get('trailingPE', None)
            debt_to_equity = info.get('debtToEquity', None)
            payout_ratio = info.get('payoutRatio', 0.0)
            market_cap = info.get('marketCap', 0)
            fifty_two_high = info.get('fiftyTwoWeekHigh', 'N/A')
            fifty_two_low = info.get('fiftyTwoWeekLow', 'N/A')
            
            # --- INTELLIGENTER "COMPASS INTEGRITY SCORE" MIT THERANOS-NIKOLA-DETEKTOR ---
            base_score = 50
            
            # 1. Bilanz & Bewertung (Sander/Munger)
            if isinstance(pe_ratio, (int, float)) and pe_ratio > 0:
                if pe_ratio < 15:
                    base_score += 15
                elif pe_ratio < 30:
                    base_score += 5
                else:
                    base_score -= 5 # Milder Malus für Wachstum
            
            # 2. Schulden-Check mit Kontext (Wachstums- vs. Pleiterisiko)
            if isinstance(debt_to_equity, (int, float)):
                if debt_to_equity < 50:
                    base_score += 15
                elif debt_to_equity < 150:
                    base_score += 0
                else:
                    # Theranos-Nikola-Detektor: Hohe Schulden/Verluste sind ok, WENN Marktvalidierung da ist (hohe Marktkapitalisierung)
                    if isinstance(market_cap, (int, float)) and market_cap > 5_000_000_000: # > 5 Mrd. Marktkapitalisierung
                        base_score -= 5  # Kompensation durch institutionelle Marktreife
                    else:
                        base_score -= 25 # Harter Malus für hochverschuldete Small Caps ohne Beweise
            
            # 3. Marktkapitalisierung & Validierungs-Bonus (Schutz vor Luftschlössern)
            if isinstance(market_cap, (int, float)):
                if market_cap > 10_000_000_000: # Über 10 Mrd. USD/EUR Marktwert = etablierter Marktteilnehmer
                    base_score += 20
                elif market_cap > 2_000_000_000:
                    base_score += 10
            
            # 4. Dividenden-Bonus
            if isinstance(payout_ratio, (int, float)) and 0.1 <= payout_ratio <= 0.7:
                base_score += 10
                
            integrity_score = max(15, min(100, base_score))
            
            # --- OBERFLÄCHE: LOGBUCH & METRIKEN ---
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
            
            # Visuelle Integrity-Leiste
            st.progress(integrity_score / 100, text=f"Compass Integrity Score: {integrity_score} Punkte (Inkl. Theranos-Nikola-Detektor & Validierungs-Prüfung)")

            with st.expander("📌 Erweiterte Fundamentaldaten & Kursspanne anzeigen"):
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    st.markdown(f"**Marktkapitalisierung:** {market_cap:,} {currency}" if isinstance(market_cap, (int, float)) else f"**Marktkapitalisierung:** {market_cap}")
                with col_t2:
                    st.markdown(f"**52-Wochen-Spanne:** {fifty_two_low} – {fifty_two_high} {currency}")

            st.markdown("---")
            
            # --- ERWEITERTER KI-PROMPT MIT DETEKTOR-LOGIK ---
            prompt = f"""
            Du bist der 'Oma-Kurz-Kompass ULTRA' - ein neutrales, hochpräzises Analyse-Instrument, das die Weisheit von Beate Sander (Substanz), Ray Kurzweil (Technologie), Charlie Munger (Burggraben & Skepsis), Howard Marks (Zyklen) und Max Tegmark (systemische Resilienz & Validierung) vereint.
            
            WICHTIGER SCHWERPUNKT (Theranos-Nikola-Detektor): 
            Prüfe kritisch, ob es sich um echte, unabhängig verifizierte wissenschaftliche / kommerzielle Meilensteine (z.B. zugelassene Produkte, klinische Phase-3-Erfolge, echte Pharma-Partner und Umsätze) handelt oder ob das Unternehmen zu stark von reinen Marketing-Versprechungen ohne Substanz lebt. Blender müssen entlarvt werden; echte Pioniere mit temporär hohen Investitionen müssen fair bewertet werden.
            
            Analysiere {name} ({ticker_input}) tiefgehend:
            - Währung / Börsenplatz: {currency} (ca. {price_eur:.2f} EUR)
            - KGV: {pe_ratio}
            - Verschuldung (Debt/Equity): {debt_to_equity}%
            - Marktkapitalisierung: {market_cap}
            - Berechneter Compass Integrity Score: {integrity_score}/100
            
            WICHTIG: KEINE direkten Anlageempfehlungen oder Handlungsbefehle ("Kaufen/Verkaufen"). Keine Anlageberatung!
            
            Beantworte das Unternehmen in genau dieser Struktur (verwende exakt diese Überschriften mit Doppelkreuz):
            
            ## 1. Sparten & Geschäftsfelder (Womit wird Geld verdient?)
            [Beschreibe präzise die aktuellen Geschäftssäulen und Segmente.]
            
            ## 2. Der Transformations- & Zukunfts-Faktor (Kurzweil & Tegmark Brücke)
            [Wie wandelt sich das Unternehmen technologisch? Wie hoch ist die systemische Zukunftsfähigkeit und Skalierbarkeit?]
            
            ## 3. Burggraben & Theranos-Detektor (Munger-Skeptiker-Blick)
            [Gibt es unabhängige wissenschaftliche/regulatorische Validierungen (z.B. klinische Phasen, FDA, globale Partner) oder handelt es sich um ungeprüfte Versprechungen? Wie stark ist der echte Burggraben?]
            
            ## 4. Bilanzen, Schulden & Zyklen (Sander & Marks Blick)
            [Analysiere Bilanzstabilität, Verschuldung und wo sich das Unternehmen im makroökonomischen Zyklus befindet.]
            
            ## 5. 36-Monats-Horizont & Gesamtprognose
            [Wie schlägt sich das Unternehmen über die nächsten 3 Jahre im Spannungsfeld aus Substanz, Validierung und exponentiellem Wandel?]
            
            ### STEIN-KLASSE: [Wähle exakt eines dieser Keywords: Dividenden-Falle | Unpolierter Rohstein | Sich entwickelnder Stein | Solider Wert | Geschliffener Brillant]
            ### FAZIT: [Ein sachliches, ausgewogenes Fazit für ein diversifiziertes Depot]
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
                st.success("💎 **Stein-Klasse: Geschliffener Brillant** – Unknackbarer Burggraben & Exponentielles Wachstum")
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
            
            # Fazit separat ausgeben
            if "FAZIT:" in raw_text:
                fazit_text = raw_text.split("FAZIT:")[-1].strip()
                st.markdown("---")
                st.info(f"💡 **FAZIT:** {fazit_text}")
                
            # --- DOWNLOAD-BUTTON ---
            st.markdown("---")
            report_filename = f"Compass_Score_{ticker_input}_{datetime.now().strftime('%Y-%m-%d')}.txt"
            full_report_content = f"OMA-KURZ-KOMPASS ULTRA v4 LOGBUCH\nAktie: {name} ({ticker_input})\nDatum: {datetime.now().strftime('%Y-%m-%d')}\nCompass Integrity Score: {integrity_score}/100\nKurs: {price} {currency} (≈ {price_eur:.2f} EUR)\n\n{raw_text}"
            
            st.download_button(
                label="📥 Analyse-Logbuch mit Compass Integrity Score herunterladen",
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
