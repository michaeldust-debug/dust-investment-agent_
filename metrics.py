from __future__ import annotations
from typing import Any
import math
import pandas as pd

def num(value: Any) -> float | None:
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None

def safe_div(a: Any, b: Any) -> float | None:
    a_n, b_n = num(a), num(b)
    if a_n is None or b_n in (None, 0):
        return None
    return a_n / b_n

def merge_statements(income, balance, cashflow) -> pd.DataFrame:
    inc = {str(r.get("date")): r for r in income if r.get("date")}
    bal = {str(r.get("date")): r for r in balance if r.get("date")}
    cf = {str(r.get("date")): r for r in cashflow if r.get("date")}
    dates = sorted(set(inc) | set(bal) | set(cf), reverse=True)
    rows = []
    for dt in dates:
        i, b, c = inc.get(dt, {}), bal.get(dt, {}), cf.get(dt, {})
        revenue = num(i.get("revenue"))
        ebit = num(i.get("operatingIncome"))
        net_income = num(i.get("netIncome"))
        assets = num(b.get("totalAssets"))
        equity = num(b.get("totalStockholdersEquity") or b.get("totalEquity"))
        debt = num(b.get("totalDebt"))
        cash = num(b.get("cashAndCashEquivalents"))
        ocf = num(c.get("operatingCashFlow") or c.get("netCashProvidedByOperatingActivities"))
        capex = num(c.get("capitalExpenditure"))
        fcf = num(c.get("freeCashFlow"))
        if fcf is None and ocf is not None and capex is not None:
            fcf = ocf + capex if capex < 0 else ocf - capex
        rows.append({
            "date": dt,
            "revenue": revenue,
            "ebit": ebit,
            "ebit_margin": safe_div(ebit, revenue),
            "net_income": net_income,
            "eps": num(i.get("eps")),
            "operating_cash_flow": ocf,
            "capex": capex,
            "free_cash_flow": fcf,
            "total_assets": assets,
            "equity": equity,
            "equity_ratio": safe_div(equity, assets),
            "total_debt": debt,
            "cash": cash,
            "net_debt": None if debt is None or cash is None else debt - cash,
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df["revenue_growth"] = df["revenue"].iloc[::-1].pct_change().iloc[::-1]
        df["net_income_growth"] = df["net_income"].iloc[::-1].pct_change().iloc[::-1]
    return df

def score_company(df: pd.DataFrame, quote: dict[str, Any]) -> dict[str, float]:
    scores = {"business_model": 7.0, "moat": 6.5, "balance_sheet": 5.0, "earnings_quality": 5.0, "profitability": 5.0, "cashflow": 5.0, "growth": 5.0, "valuation": 5.0, "risk": 6.0}
    if df.empty:
        return scores
    latest = df.iloc[0]
    eq = latest.get("equity_ratio")
    if pd.notna(eq):
        scores["balance_sheet"] = max(2.0, min(9.5, 4.0 + float(eq) * 10))
    margin = latest.get("ebit_margin")
    if pd.notna(margin):
        scores["profitability"] = max(2.0, min(9.5, 4.0 + float(margin) * 20))
    fcf = latest.get("free_cash_flow")
    ni = latest.get("net_income")
    if pd.notna(fcf) and pd.notna(ni) and ni != 0:
        conversion = float(fcf) / float(ni)
        scores["cashflow"] = max(2.0, min(9.5, 5.0 + (conversion - 0.7) * 3))
        scores["earnings_quality"] = max(2.0, min(9.5, 5.0 + (conversion - 0.8) * 3))
    growth = latest.get("revenue_growth")
    if pd.notna(growth):
        scores["growth"] = max(2.0, min(10.0, 5.0 + float(growth) * 20))
    pe = quote.get("pe")
    if pe is not None:
        pe = float(pe)
        scores["valuation"] = 8.5 if 0 < pe < 15 else 7.0 if pe < 22 else 5.5 if pe < 30 else 3.5
    return scores
