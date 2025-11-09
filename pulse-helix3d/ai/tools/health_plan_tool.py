"""CrewAI tool for health plan generation."""
from __future__ import annotations

from typing import Any, Dict


def build_health_plan(goal: str, tier: str) -> Dict[str, Any]:
    return {
        "goal": goal,
        "tier": tier,
        "blocks": [
            {"name": "HRV Foundations", "duration_days": 14},
            {"name": "VO2 Intervals", "duration_days": 21},
        ],
    }
