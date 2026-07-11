from dataclasses import dataclass
from typing import Any
import requests

class FMPError(RuntimeError):
    pass

@dataclass
class FMPClient:
    api_key: str
    base_url: str = "https://financialmodelingprep.com/stable"
    timeout: int = 30

    def _get(self, endpoint: str, **params: Any):
        params["apikey"] = self.api_key
        r = requests.get(f"{self.base_url}/{endpoint.lstrip('/')}" , params=params, timeout=self.timeout)
        r.raise_for_status()
        payload = r.json()
        if isinstance(payload, dict) and (payload.get("Error Message") or payload.get("error")):
            raise FMPError(str(payload.get("Error Message") or payload.get("error")))
        if not isinstance(payload, list):
            raise FMPError(f"Unerwartetes Antwortformat für {endpoint}")
        return payload

    def profile(self, symbol):
        rows=self._get("profile",symbol=symbol); return rows[0] if rows else {}
    def quote(self, symbol):
        rows=self._get("quote",symbol=symbol); return rows[0] if rows else {}
    def income_statements(self,symbol,limit=5):
        return self._get("income-statement",symbol=symbol,period="annual",limit=limit)
    def balance_sheets(self,symbol,limit=5):
        return self._get("balance-sheet-statement",symbol=symbol,period="annual",limit=limit)
    def cashflows(self,symbol,limit=5):
        return self._get("cash-flow-statement",symbol=symbol,period="annual",limit=limit)
