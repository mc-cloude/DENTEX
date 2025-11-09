from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.shared.utils.auth import AuthenticatedUser

router = APIRouter(prefix="/fitness", tags=["fitness"])


@router.get("/programs")
async def list_programs(user: AuthenticatedUser = Depends()) -> dict:
    return {
        "tier": user.tier if user else "anon",
        "programs": [
            {"name": "Executive Vitality", "focus": "VO2", "tier": "elevate"},
            {"name": "Transcend Peak", "focus": "HRV", "tier": "transcend"},
        ],
    }
