from __future__ import annotations

import asyncio

from backend.services.ai_agentic_core.orchestrator import AgentOrchestrator


async def test_dsr_delete_flow(event_loop):
    orchestrator = AgentOrchestrator()
    user = type("User", (), {"user_id": "user-1", "scopes": ["ai:coach"], "tier": "transcend", "tenant": "corp"})
    job_id = await orchestrator.start_dsr_job(user, {"reason": "user_request"})
    status = await orchestrator.get_dsr_status(job_id)
    assert status["status"] in {"pending", "completed"}
