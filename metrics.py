import math
import pandas as pd

def num(v):
    try:
        x=float(v); return x if math.isfinite(x) else None
    except (TypeError,ValueError): return None

def safe_div(a,b):
    a,b=num(a),num(b)
    return None if a is None or b in (None,0) else a/b

def merge_statements(income,balance,cashflow):
    inc={str(r.get("date")):r for r in income if r.get("date")}
    bal={str(r.get("date")):r for r in balance if r.get("date")}
    cf={str(r.get("date")):r for r in cashflow if r.get("date")}
    rows=[]
    for d in sorted(set(inc)|set(bal)|set(cf),reverse=True):
        i,b,c=inc.get(d,{}),bal.get(d,{}),cf.get(d,{})
        revenue=num(i.get("revenue")); ebit=num(i.get("operatingIncome")); ni=num(i.get("netIncome"))
        assets=num(b.get("totalAssets")); equity=num(b.get("totalStockholdersEquity") or b.get("totalEquity"))
        debt=num(b.get("totalDebt")); cash=num(b.get("cashAndCashEquivalents"))
        ocf=num(c.get("operatingCashFlow") or c.get("netCashProvidedByOperatingActivities")); capex=num(c.get("capitalExpenditure")); fcf=num(c.get("freeCashFlow"))
        if fcf is None and ocf is not None and capex is not None: fcf=ocf+capex if capex<0 else ocf-capex
        rows.append({"date":d,"revenue":revenue,"ebit":ebit,"ebit_margin":safe_div(ebit,revenue),"net_income":ni,"eps":num(i.get("eps")),"operating_cash_flow":ocf,"capex":capex,"free_cash_flow":fcf,"total_assets":assets,"equity":equity,"equity_ratio":safe_div(equity,assets),"total_debt":debt,"net_debt":None if debt is None or cash is None else debt-cash,"cash":cash})
    df=pd.DataFrame(rows)
    if not df.empty:
        df["revenue_growth"]=df["revenue"].iloc[::-1].pct_change().iloc[::-1]
        df["net_income_growth"]=df["net_income"].iloc[::-1].pct_change().iloc[::-1]
    return df

def score_company(df,quote):
    s={"business_model":7.0,"moat":6.5,"balance_sheet":5.0,"earnings_quality":5.0,"profitability":5.0,"cashflow":5.0,"growth":5.0,"valuation":5.0,"risk":6.0}
    if df.empty:return s
    x=df.iloc[0]
    if pd.notna(x.get("equity_ratio")): s["balance_sheet"]=max(2,min(9.5,4+float(x["equity_ratio"])*10))
    if pd.notna(x.get("ebit_margin")): s["profitability"]=max(2,min(9.5,4+float(x["ebit_margin"])*20))
    if pd.notna(x.get("free_cash_flow")) and pd.notna(x.get("net_income")) and x.get("net_income")!=0:
        conv=float(x["free_cash_flow"])/float(x["net_income"]); s["cashflow"]=max(2,min(9.5,5+(conv-.7)*3)); s["earnings_quality"]=max(2,min(9.5,5+(conv-.8)*3))
    if pd.notna(x.get("revenue_growth")): s["growth"]=max(2,min(10,5+float(x["revenue_growth"])*20))
    pe=quote.get("pe")
    if pe is not None:
        pe=float(pe); s["valuation"]=8.5 if 0<pe<15 else 7 if pe<22 else 5.5 if pe<30 else 3.5
    return s
