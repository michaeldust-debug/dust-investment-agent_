from io import BytesIO
from datetime import date
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak

def money(v,c="EUR"):
    if v is None or pd.isna(v): return "nicht verfügbar"
    v=float(v)
    if abs(v)>=1e9:return f"{v/1e9:.2f} Mrd. {c}".replace('.',',')
    if abs(v)>=1e6:return f"{v/1e6:.1f} Mio. {c}".replace('.',',')
    return f"{v:.2f} {c}".replace('.',',')
def pct(v): return "nicht verfügbar" if v is None or pd.isna(v) else f"{float(v)*100:.1f} %".replace('.',',')

def build_pdf(company_name,symbol,isin,wkn,profile,quote,df,scores,total_score,investment_verdict,analysis):
    b=BytesIO(); doc=SimpleDocTemplate(b,pagesize=A4,rightMargin=18*mm,leftMargin=18*mm,topMargin=18*mm,bottomMargin=18*mm)
    st=getSampleStyleSheet(); story=[Spacer(1,20*mm),Paragraph("DUST INVESTMENT REPORT",st['Title']),Paragraph(company_name,st['Heading1']),Paragraph(f"Symbol: {symbol}<br/>ISIN: {isin or 'nicht verfügbar'}<br/>WKN: {wkn or 'nicht verfügbar'}<br/>Datenstand: {date.today().strftime('%d.%m.%Y')}",st['Heading3']),Spacer(1,12*mm),Paragraph(f"Dust Investment Score: <b>{total_score:.1f}/100</b>",st['Heading1']),Paragraph(f"Analytisches Urteil: <b>{investment_verdict}</b>",st['Heading2']),PageBreak(),Paragraph("Executive Dashboard",st['Heading1'])]
    latest=df.iloc[0] if not df.empty else {}
    data=[["Kennzahl","Wert"],["Aktueller Kurs",money(quote.get('price'),profile.get('currency','EUR'))],["Marktkapitalisierung",money(quote.get('marketCap') or profile.get('marketCap'),profile.get('currency','EUR'))],["KGV",str(quote.get('pe') or 'nicht verfügbar')],["Umsatz letztes GJ",money(latest.get('revenue') if len(df) else None,profile.get('currency','EUR'))],["EBIT-Marge",pct(latest.get('ebit_margin') if len(df) else None)],["Eigenkapitalquote",pct(latest.get('equity_ratio') if len(df) else None)],["Free Cashflow",money(latest.get('free_cash_flow') if len(df) else None,profile.get('currency','EUR'))],["Dust Investment Score",f"{total_score:.1f}/100"],["Urteil",investment_verdict]]
    t=Table(data,colWidths=[75*mm,90*mm]); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#17365D')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.4,colors.grey),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F2F5F8')])]))
    story += [t,Spacer(1,8*mm),Paragraph("Scorecard",st['Heading1'])]
    sr=[["Teilbereich","Punkte / 10"]]+[[k.replace('_',' ').title(),f"{v:.1f}"] for k,v in scores.items()]
    tt=Table(sr,colWidths=[110*mm,55*mm]); tt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#17365D')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.4,colors.grey)])); story += [tt,PageBreak(),Paragraph("Historische Finanzkennzahlen",st['Heading1'])]
    hist=[["GJ","Umsatz","EBIT-Marge","Jahresüberschuss","FCF","EK-Quote"]]
    for _,r in df.head(5).iterrows(): hist.append([str(r.get('date',''))[:4],money(r.get('revenue'),profile.get('currency','EUR')),pct(r.get('ebit_margin')),money(r.get('net_income'),profile.get('currency','EUR')),money(r.get('free_cash_flow'),profile.get('currency','EUR')),pct(r.get('equity_ratio'))])
    ht=Table(hist,repeatRows=1,colWidths=[20*mm,33*mm,25*mm,36*mm,31*mm,25*mm]); ht.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#17365D')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.35,colors.grey),('FONTSIZE',(0,0),(-1,-1),7.5)])); story += [ht,Spacer(1,8*mm),Paragraph("Qualitative Analyse",st['Heading1'])]
    for block in analysis.split('\n'):
        if block.strip(): story += [Paragraph(block.strip(),st['BodyText']),Spacer(1,2*mm)]
    story += [Paragraph("Daten- und Haftungshinweis",st['Heading1']),Paragraph("Automatisch erzeugter Prototyp auf Basis verfügbarer FMP-Daten und qualitativer KI-Auswertung. Originalberichte und aktuelle Marktdaten sind vor einer Anlageentscheidung zu verifizieren. Keine individuelle Anlageberatung.",st['BodyText'])]
    doc.build(story); return b.getvalue()
