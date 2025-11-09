from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/nutrition", tags=["nutrition"])


@router.get("/plans")
async def nutrition_plans() -> dict:
    return {
        "plans": [
            {"name": "Metabolic Reset", "calories": 1800, "macros": {"protein": 30, "fat": 30, "carb": 40}},
            {"name": "Longevity Mediterranean", "calories": 2100, "macros": {"protein": 25, "fat": 35, "carb": 40}},
        ]
    }
