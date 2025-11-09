"""Error response models."""
from __future__ import annotations

from dataclasses import dataclass
from fastapi import HTTPException
from typing import Any, Dict


@dataclass
class ErrorResponse:
    detail: str
    status_code: int

    @classmethod
    def from_exc(cls, exc: HTTPException) -> "ErrorResponse":
        detail = exc.detail if isinstance(exc.detail, str) else "error"
        return cls(detail=detail, status_code=exc.status_code)

    def model_dump(self) -> Dict[str, Any]:
        return {"detail": self.detail, "status_code": self.status_code}
