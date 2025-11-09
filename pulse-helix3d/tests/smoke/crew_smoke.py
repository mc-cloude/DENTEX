from __future__ import annotations

from backend.services.ai_agentic_core.orchestrator import AgentOrchestrator


async def test_guardian_scope_check(event_loop):
    orchestrator = AgentOrchestrator()
    payload = {"user": {"scopes": ["ai:coach"]}, "input": {"goal": "improve sleep"}}
    result = await orchestrator.dispatch("planner", payload)
    assert result["endpoint"] == "planner"
