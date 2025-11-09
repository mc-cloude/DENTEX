from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/labs", tags=["labs"])


@router.get("/partners")
async def lab_partners() -> dict:
    return {
        "partners": [
            {"name": "GCC Precision Labs", "capabilities": ["blood", "genomics"]},
            {"name": "Dubai Longevity Center", "capabilities": ["metabolomics"]},
        ]
    }
