from __future__ import annotations
import json
from openai import OpenAI

def qualitative_analysis(api_key: str, model: str, company_name: str, profile: dict, metrics_rows: list[dict], scores: dict[str, float]) -> str:
    client = OpenAI(api_key=api_key)
    prompt = f"""
Du bist der Dust Investment Agent. Verfasse auf Deutsch eine kompakte, sachliche Aktienanalyse für einen Wirtschaftsprüfer und langfristigen Value-Investor.

Unternehmen: {company_name}
Unternehmensprofil: {json.dumps(profile, ensure_ascii=False, default=str)}
Historische Kennzahlen: {json.dumps(metrics_rows, ensure_ascii=False, default=str)}
Vorläufige Teil-Scores: {json.dumps(scores, ensure_ascii=False)}

Gliedere in Geschäftsmodell, Wettbewerbsvorteile, Finanzqualität und Cashflow, Chancen, Risiken und WP-Red-Flags, Investmentthese sowie drei zu überwachende Kennzahlen.
Keine Zahlen erfinden. Fehlende Informationen als nicht belastbar verfügbar kennzeichnen. Keine individuelle Anlageberatung. Höchstens 1.200 Wörter.
"""
    response = client.responses.create(model=model, input=prompt)
    return response.output_text
