from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/community", tags=["community"])


@router.get("/challenges")
async def community_challenges() -> dict:
    return {
        "challenges": [
            {"name": "Desert Sunrise HRV", "type": "hrv", "reward": "tier_badge"},
            {"name": "Corporate Wellness Cup", "type": "steps", "reward": "donation"},
        ]
    }
