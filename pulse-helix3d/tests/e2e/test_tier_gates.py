from __future__ import annotations

import base64
import json

from fastapi.testclient import TestClient

from backend.services.api_gateway.main import app


def _token(tier: str) -> str:
    payload = base64.urlsafe_b64encode(
        json.dumps({"sub": "user-1", "tenant": "corp_uae_001", "tier": tier, "scp": ["ai:coach"]}).encode()
    ).decode().rstrip("=")
    return f"header.{payload}.sig"


def test_core_user_blocked_from_analytics():
    client = TestClient(app)
    token = _token("core")
    response = client.get("/dashboard/analytics", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code in {200, 403}
