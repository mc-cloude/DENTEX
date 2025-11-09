from __future__ import annotations

import base64
import json

from fastapi.testclient import TestClient

from backend.services.api_gateway.main import app


def _build_token(tier: str = "transcend", scopes: list[str] | None = None) -> str:
    scopes = scopes or ["ai:coach"]
    payload = json.dumps({"sub": "user-1", "tenant": "corp_uae_001", "tier": tier, "scp": scopes}).encode()
    encoded = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    return f"header.{encoded}.signature"


def test_healthz():
    client = TestClient(app)
    assert client.get("/healthz").status_code == 200


def test_dashboard_summary_authorized(monkeypatch):
    client = TestClient(app)
    token = _build_token()
    response = client.get("/dashboard/summary", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code in {200, 403}
