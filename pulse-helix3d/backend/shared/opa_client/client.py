"""Async OPA client with typed decision payloads."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict

import httpx

logger = logging.getLogger(__name__)


@dataclass
class PolicyDecision:
    allow: bool
    reason: str | None = None

    def model_dump(self) -> Dict[str, Any]:
        return {"allow": self.allow, "reason": self.reason}


class OPAAuthorizer:
    def __init__(self, base_url: str, policy_path: str = "v1/data/pulse/allow") -> None:
        self._base_url = base_url.rstrip("/")
        self._policy_path = policy_path

    async def authorize(self, route_name: str, payload: Dict[str, Any]) -> PolicyDecision:
        url = f"{self._base_url}/{self._policy_path}"
        logger.debug("OPA query url=%s route=%s", url, route_name)
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.post(url, json={"input": payload})
                response.raise_for_status()
                result = response.json()
            except Exception as exc:  # pragma: no cover
                logger.error("OPA evaluation failed: %s", exc)
                return PolicyDecision(allow=False, reason="OPA unreachable")
        allow = result.get("result", {}).get("allow", False)
        reason = result.get("result", {}).get("reason")
        return PolicyDecision(allow=allow, reason=reason)
