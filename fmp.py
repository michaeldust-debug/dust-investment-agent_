from __future__ import annotations
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

    def _get(self, endpoint: str, **params: Any) -> list[dict[str, Any]]:
        params["apikey"] = self.api_key
        response = requests.get(f"{self.base_url}/{endpoint.lstrip('/')}", params=params, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, dict):
            error = payload.get("Error Message") or payload.get("error") or payload.get("message")
            if error:
                raise FMPError(str(error))
            raise FMPError(f"Unerwartetes Antwortformat bei {endpoint}")
        if not isinstance(payload, list):
            raise FMPError(f"Unerwartetes Antwortformat bei {endpoint}")
        return payload

    def profile(self, symbol: str) -> dict[str, Any]:
        rows = self._get("profile", symbol=symbol)
        return rows[0] if rows else {}

    def quote(self, symbol: str) -> dict[str, Any]:
        rows = self._get("quote", symbol=symbol)
        return rows[0] if rows else {}

    def income_statements(self, symbol: str, limit: int = 5) -> list[dict[str, Any]]:
        return self._get("income-statement", symbol=symbol, period="annual", limit=limit)

    def balance_sheets(self, symbol: str, limit: int = 5) -> list[dict[str, Any]]:
        return self._get("balance-sheet-statement", symbol=symbol, period="annual", limit=limit)

    def cashflows(self, symbol: str, limit: int = 5) -> list[dict[str, Any]]:
        return self._get("cash-flow-statement", symbol=symbol, period="annual", limit=limit)
