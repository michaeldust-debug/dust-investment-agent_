from __future__ import annotations
from io import BytesIO
from datetime import date
from typing import Any
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

def money(value: Any, currency: str = "EUR") -> str:
    if value is None or pd.isna(value):
        return "nicht verfügbar"
    value = float(value)
    if abs(value) >= 1_000_000_000:
        text = f"{value/1_000_000_000:,.2f} Mrd. {currency}"
    elif abs(value) >= 1_000_000:
        text = f"{value/1_000_000:,.1f} Mio. {currency}"
    else:
        text = f"{value:,.2f} {currency}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")

def pct(value: Any) -> str:
    if value is None or pd.isna(value):
        return "nicht verfügbar"
    return f"{float(value) * 100:.1f} %".replace(".", ",")

def build_pdf(company_name, symbol, isin, wkn, profile, quote, df, scores, total_score, investment_verdict, analysis) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm, title=f"Dust Investment Report – {company_name}")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], alignment=TA_CENTER, fontSize=24, leading=30, spaceAfter=12))
    story = [Spacer(1, 28*mm), Paragraph("DUST INVESTMENT REPORT", styles["CoverTitle"]), Paragraph(company_name, styles["Title"]), Spacer(1, 8*mm), Paragraph(f"Symbol: {symbol}<br/>ISIN: {isin or 'nicht verfügbar'}<br/>WKN: {wkn or 'nicht verfügbar'}<br/>Datenstand: {date.today().strftime('%d.%m.%Y')}", styles["Heading3"]), Spacer(1, 25*mm), Paragraph(f"Dust Investment Score: <b>{total_score:.1f}/100</b>", styles["Heading1"]), Paragraph(f"Analytisches Urteil: <b>{investment_verdict}</b>", styles["Heading2"]), PageBreak(), Paragraph("Executive Dashboard", styles["Heading1"])]
    latest = df.iloc[0] if not df.empty else {}
    dashboard = [["Kennzahl", "Wert"], ["Aktueller Kurs", money(quote.get("price"), profile.get("currency", "EUR"))], ["Marktkapitalisierung", money(quote.get("marketCap") or profile.get("marketCap"), profile.get("currency", "EUR"))], ["KGV", str(quote.get("pe") or "nicht verfügbar")], ["Umsatz letztes GJ", money(latest.get("revenue") if len(df) else None, profile.get("currency", "EUR"))], ["EBIT-Marge", pct(latest.get("ebit_margin") if len(df) else None)], ["Eigenkapitalquote", pct(latest.get("equity_ratio") if len(df) else None)], ["Free Cashflow", money(latest.get("free_cash_flow") if len(df) else None, profile.get("currency", "EUR"))], ["Dust Investment Score", f"{total_score:.1f}/100"], ["Urteil", investment_verdict]]
    table = Table(dashboard, colWidths=[75*mm, 90*mm])
    table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#17365D")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("GRID", (0,0), (-1,-1), 0.4, colors.grey), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F2F5F8")]), ("VALIGN", (0,0), (-1,-1), "TOP")]))
    story += [table, Spacer(1, 8*mm), Paragraph("Scorecard", styles["Heading1"])]
    score_rows = [["Teilbereich", "Punkte / 10"]] + [[key.replace("_", " ").title(), f"{value:.1f}"] for key, value in scores.items()]
    score_table = Table(score_rows, colWidths=[110*mm, 55*mm])
    score_table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#17365D")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("GRID", (0,0), (-1,-1), 0.4, colors.grey), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F2F5F8")])]))
    story += [score_table, PageBreak(), Paragraph("Historische Finanzkennzahlen", styles["Heading1"])]
    hist = [["GJ", "Umsatz", "EBIT-Marge", "Jahresüberschuss", "FCF", "EK-Quote"]]
    for _, row in df.head(5).iterrows():
        hist.append([str(row.get("date", ""))[:4], money(row.get("revenue"), profile.get("currency", "EUR")), pct(row.get("ebit_margin")), money(row.get("net_income"), profile.get("currency", "EUR")), money(row.get("free_cash_flow"), profile.get("currency", "EUR")), pct(row.get("equity_ratio"))])
    hist_table = Table(hist, repeatRows=1, colWidths=[18*mm, 34*mm, 25*mm, 36*mm, 30*mm, 25*mm])
    hist_table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#17365D")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("GRID", (0,0), (-1,-1), 0.35, colors.grey), ("FONTSIZE", (0,0), (-1,-1), 7.5), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F2F5F8")])]))
    story += [hist_table, Spacer(1, 8*mm), Paragraph("Qualitative Analyse", styles["Heading1"])]
    for block in analysis.split("\n"):
        if block.strip():
            story.append(Paragraph(block.strip(), styles["BodyText"]))
            story.append(Spacer(1, 2*mm))
    story += [Spacer(1, 6*mm), Paragraph("Daten- und Haftungshinweis", styles["Heading1"]), Paragraph("Dieser automatisch erzeugte Prototyp basiert auf den über FMP verfügbaren Daten und einer qualitativen KI-Auswertung. Er ersetzt weder die Prüfung der Originalberichte noch eine individuelle Anlageberatung. Fehlende Daten werden nicht geschätzt.", styles["BodyText"])]
    doc.build(story)
    return buffer.getvalue()
