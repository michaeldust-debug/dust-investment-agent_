from datetime import date
import pandas as pd
import streamlit as st
from dust_agent.config import SYMBOL_ALIASES
from dust_agent.fmp import FMPClient,FMPError
from dust_agent.metrics import merge_statements,score_company
from dust_agent.scoring import weighted_score,verdict
from dust_agent.ai import qualitative_analysis
from dust_agent.pdf_report import build_pdf

st.set_page_config(page_title="Dust Investment Agent",page_icon="📊",layout="wide")
st.title("Dust Investment Agent")
st.caption("Prototyp: strukturierte Finanzdaten, deterministische Kennzahlen und kompakter PDF-Report")
with st.sidebar:
    st.header("Konfiguration"); model=st.secrets.get("OPENAI_MODEL","gpt-5-mini"); st.write(f"OpenAI-Modell: `{model}`")
raw=st.text_input("Unternehmen, WKN, ISIN oder FMP-Symbol",value="A255F1")
if st.button("Report erstellen",type="primary"):
    ok=st.secrets.get("OPENAI_API_KEY"); fk=st.secrets.get("FMP_API_KEY")
    if not ok or not fk: st.error("OPENAI_API_KEY und FMP_API_KEY müssen in Streamlit Secrets hinterlegt sein."); st.stop()
    symbol=SYMBOL_ALIASES.get(raw.strip().upper(),raw.strip().upper()); c=FMPClient(fk)
    try:
        with st.status("Daten werden geladen und ausgewertet ...",expanded=True) as status:
            profile=c.profile(symbol); quote=c.quote(symbol); income=c.income_statements(symbol); balance=c.balance_sheets(symbol); cashflow=c.cashflows(symbol)
            if not profile and not income: raise FMPError("Keine Daten gefunden. Prüfe Symbol und Tarifabdeckung.")
            df=merge_statements(income,balance,cashflow); scores=score_company(df,quote); total=weighted_score(scores); iv=verdict(total); company=profile.get('companyName') or raw
            analysis=qualitative_analysis(ok,model,company,profile,df.head(5).where(pd.notna(df),None).to_dict(orient='records'),scores)
            isin='DE000A255F11' if symbol=='VH2.DE' else profile.get('isin',''); wkn='A255F1' if symbol=='VH2.DE' else ''
            pdf=build_pdf(company,symbol,isin,wkn,profile,quote,df,scores,total,iv,analysis); status.update(label="Report fertig",state="complete",expanded=False)
        a,b,c3=st.columns(3); a.metric("Dust Investment Score",f"{total:.1f}/100"); b.metric("Investmenturteil",iv); c3.metric("Aktueller Kurs",str(quote.get('price','n. v.')))
        st.dataframe(df,use_container_width=True,hide_index=True); st.markdown(analysis)
        fn=f"DIR_{company.replace(' ','_')}_{isin or symbol}_{date.today().isoformat()}.pdf"; st.download_button("PDF herunterladen",pdf,file_name=fn,mime="application/pdf",type="primary")
    except Exception as e: st.exception(e)
