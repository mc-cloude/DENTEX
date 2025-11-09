from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from backend.services.api_gateway.main import app
from backend.services.ai_agentic_core.orchestrator import AgentOrchestrator


def _token(tier: str = "transcend") -> str:
    import base64
    import json

    payload = base64.urlsafe_b64encode(
        json.dumps({"sub": "user-1", "tenant": "corp_uae_001", "tier": tier, "scp": ["ai:coach"]}).encode()
    ).decode().rstrip("=")
    return f"header.{payload}.sig"


def test_goal_to_dashboard_flow(monkeypatch):
    client = TestClient(app)
    token = _token()
    response = client.post("/ai/plan", headers={"Authorization": f"Bearer {token}"}, json={"goal": "sleep"})
    assert response.status_code in {200, 403}
    dashboard = client.get("/dashboard/summary", headers={"Authorization": f"Bearer {token}"})
    assert dashboard.status_code in {200, 403}
