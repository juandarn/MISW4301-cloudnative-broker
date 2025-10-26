from __future__ import annotations
import os
from typing import Any
import requests

def _safe_json(response: requests.Response) -> dict[str, Any]:
    try:
        return response.json()
    except ValueError:
        return {"raw": response.text}

class TrueNativeException(Exception):
    def __init__(self, status_code: int, message: str | None = None, payload: Any | None = None):
        super().__init__(message or f"TrueNative error {status_code}")
        self.status_code = status_code
        self.payload = payload or {}

class TrueNativeCardsClient:
    """
    Cliente HTTP para TrueNative. Requiere:
    - TRUENATIVE_BASE_URL
    - SECRET_TOKEN
    """
    def __init__(self, base_url: str | None = None, secret_token: str | None = None, timeout: int = 10):
        self.base_url = (base_url or os.environ.get("TRUENATIVE_BASE_URL", "")).rstrip("/")
        if not self.base_url:
            raise RuntimeError("TRUENATIVE_BASE_URL is not configured")

        self.secret_token = secret_token or os.environ.get("SECRET_TOKEN")
        if not self.secret_token:
            raise RuntimeError("SECRET_TOKEN is not configured")

        self.timeout = timeout
        self.session = requests.Session()

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.secret_token}",
            "Content-Type": "application/json",
        }

    def register_card(self, card_payload: dict[str, Any], transaction_identifier: str) -> dict[str, Any]:
        url = f"{self.base_url}/native/cards"
        payload = {"card": card_payload, "transactionIdentifier": transaction_identifier}
        response = self.session.post(url, json=payload, headers=self._headers(), timeout=self.timeout)
        if response.status_code == 201:
            return response.json()
        if response.status_code in {400, 401, 403, 409}:
            raise TrueNativeException(response.status_code, response.text, _safe_json(response))
        raise TrueNativeException(response.status_code, "Unexpected error registering card", _safe_json(response))

    def get_card_status(self, ruv: str) -> tuple[int, dict[str, Any]]:
        url = f"{self.base_url}/native/cards/{ruv}"
        response = self.session.get(url, headers=self._headers(), timeout=self.timeout)
        data = _safe_json(response)
        return response.status_code, data
