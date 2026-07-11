from __future__ import annotations

from datetime import date
import pandas as pd
import streamlit as st

from dust_agent.config import SYMBOL_ALIASES
from dust_agent.fmp import FMPClient, FMPError
from dust_agent.metrics import merge_statements, score_company
from dust_agent.scoring import weighted_score, verdict
from dust_agent.ai import qualitative_analysis
from dust_agent.pdf_report import build_pdf

st.set_page_config(page_title="Dust Investment Agent", page_icon="📊", layout="wide")
st.title("Dust Investment Agent 2.0")
st.caption("Aktienanalyse mit FMP-Daten, OpenAI-Auswertung und PDF-Export")

with st.sidebar:
    st.header("Konfiguration")
    model = st.secrets.get("OPENAI_MODEL", "gpt-5-mini")
    st.write(f"OpenAI-Modell: `{model}`")
    st.info("API-Schlüssel werden nur über Streamlit Secrets gelesen.")

raw_input = st.text_input(
    "Unternehmen, WKN, ISIN oder Ticker",
    value="A255F1",
    help="Für Friedrich Vorwerk: A255F1, DE000A255F11, VH2 oder VH2.DE",
)

if st.button("Report erstellen", type="primary"):
    openai_key = st.secrets.get("OPENAI_API_KEY")
    fmp_key = st.secrets.get("FMP_API_KEY")

    if not openai_key or not fmp_key:
        st.error("Bitte OPENAI_API_KEY und FMP_API_KEY in den Streamlit Secrets hinterlegen.")
        st.stop()

    normalized = raw_input.strip().upper()
    symbol = SYMBOL_ALIASES.get(normalized, normalized)
    client = FMPClient(fmp_key)

    try:
        with st.status("Daten werden geladen ...", expanded=True) as status:
            st.write(f"Verwendetes Symbol: `{symbol}`")
            profile = client.profile(symbol)
            quote = client.quote(symbol)
            income = client.income_statements(symbol, limit=5)
            balance = client.balance_sheets(symbol, limit=5)
            cashflow = client.cashflows(symbol, limit=5)

            if not profile and not income:
                raise FMPError("Keine Daten gefunden. Prüfe das Symbol oder die FMP-Abdeckung deines Tarifs.")

            df = merge_statements(income, balance, cashflow)
            scores = score_company(df, quote)
            total = weighted_score(scores)
            investment_verdict = verdict(total)
            company_name = profile.get("companyName") or profile.get("name") or raw_input

            st.write("Qualitative Analyse wird erstellt ...")
            analysis = qualitative_analysis(
                api_key=openai_key,
                model=model,
                company_name=company_name,
                profile=profile,
                metrics_rows=df.head(5).where(pd.notna(df), None).to_dict(orient="records"),
                scores=scores,
            )

            isin = "DE000A255F11" if symbol == "VH2.DE" else profile.get("isin", "")
            wkn = "A255F1" if symbol == "VH2.DE" else ""
            pdf_bytes = build_pdf(
                company_name=company_name,
                symbol=symbol,
                isin=isin,
                wkn=wkn,
                profile=profile,
                quote=quote,
                df=df,
                scores=scores,
                total_score=total,
                investment_verdict=investment_verdict,
                analysis=analysis,
            )
            status.update(label="Report fertig", state="complete", expanded=False)

        c1, c2, c3 = st.columns(3)
        c1.metric("Dust Investment Score", f"{total:.1f}/100")
        c2.metric("Investmenturteil", investment_verdict)
        price = quote.get("price")
        c3.metric("Aktueller Kurs", f"{price:,.2f}" if isinstance(price, (int, float)) else "nicht verfügbar")

        st.subheader("Historische Finanzdaten")
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.subheader("Qualitative Analyse")
        st.markdown(analysis)

        safe_company = "".join(ch if ch.isalnum() or ch in ("_", "-") else "_" for ch in company_name)
        filename = f"DIR_{safe_company}_{isin or symbol}_{date.today().isoformat()}.pdf"
        st.download_button("PDF herunterladen", data=pdf_bytes, file_name=filename, mime="application/pdf", type="primary")

    except Exception as exc:
        st.error("Die Report-Erstellung ist fehlgeschlagen.")
        st.exception(exc)
