from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any
import requests

@dataclass(frozen=True)
class CosmosResponse:
    raw_text: str
    status: str  # "ok" | "skipped" | "error"

class CosmosClient:
    """
    Generic HTTP client wrapper. If COSMOS_API_URL or COSMOS_API_KEY is missing,
    it safely returns status='skipped' so demos still run (heuristics-only).
    """
    def __init__(self, api_url: Optional[str], api_key: Optional[str], model: str = "reason-2", timeout_s: int = 30):
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.timeout_s = timeout_s

    def infer(self, system: str, user: str) -> CosmosResponse:
        if not self.api_url or not self.api_key:
            return CosmosResponse(raw_text="", status="skipped")

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.0,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            r = requests.post(self.api_url, json=payload, headers=headers, timeout=self.timeout_s)
            r.raise_for_status()
            # Accept either a plain string response or OpenAI-like JSON structures.
            try:
                data = r.json()
                # Common patterns:
                # - { "output_text": "..." }
                # - { "choices": [{"message": {"content": "..."}}] }
                if isinstance(data, dict) and "output_text" in data:
                    return CosmosResponse(raw_text=str(data["output_text"]), status="ok")
                if isinstance(data, dict) and "choices" in data and data["choices"]:
                    content = data["choices"][0].get("message", {}).get("content", "")
                    return CosmosResponse(raw_text=str(content), status="ok")
                # Fallback: stringify JSON
                return CosmosResponse(raw_text=str(data), status="ok")
            except Exception:
                return CosmosResponse(raw_text=r.text, status="ok")
        except Exception as e:
            return CosmosResponse(raw_text=f"{type(e).__name__}: {e}", status="error")

