from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/clinical", tags=["clinical"])


@router.get("/programs")
async def clinical_programs() -> dict:
    return {
        "programs": [
            {"name": "CardioMetabolic Precision", "duration_weeks": 12, "tier": "transcend"},
            {"name": "Metabolic Guard", "duration_weeks": 8, "tier": "elevate"},
        ]
    }
