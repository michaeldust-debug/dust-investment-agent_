import json
from openai import OpenAI

def qualitative_analysis(api_key,model,company_name,profile,metrics_rows,scores):
    client=OpenAI(api_key=api_key)
    prompt=f"""Du bist der Dust Investment Agent. Verfasse auf Deutsch eine kompakte, sachliche Aktienanalyse für einen Wirtschaftsprüfer und langfristigen Value-Investor.
Unternehmen: {company_name}
Profil: {json.dumps(profile,ensure_ascii=False,default=str)}
Kennzahlen: {json.dumps(metrics_rows,ensure_ascii=False,default=str)}
Scores: {json.dumps(scores,ensure_ascii=False)}
Gliedere in Geschäftsmodell, Wettbewerbsvorteile, Finanzqualität, Chancen, Risiken/WP-Red-Flags, Investmentthese und drei zu überwachende Kennzahlen. Keine Zahlen erfinden. Fehlende Informationen als nicht belastbar verfügbar kennzeichnen. Höchstens 1.200 Wörter. Keine individuelle Anlageberatung."""
    r=client.responses.create(model=model,input=prompt)
    return r.output_text
