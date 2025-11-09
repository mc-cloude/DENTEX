"""Authentication helpers shared across services."""
from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any, Dict

from fastapi import Request


@dataclass
class OAuthUser:
    access_token: str
    expires_in: int
    token_type: str
    scope: str


@dataclass
class AuthenticatedUser:
    user_id: str
    tenant: str
    tier: str
    scopes: list[str]

    @classmethod
    def from_claims(cls, claims: Dict[str, Any]) -> "AuthenticatedUser":
        return cls(
            user_id=claims.get("sub", "anon"),
            tenant=claims.get("tenant", "unknown"),
            tier=claims.get("tier", "core"),
            scopes=claims.get("scp", []),
        )

    def model_dump(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "tenant": self.tenant,
            "tier": self.tier,
            "scopes": self.scopes,
        }


def decode_jwt(token: str) -> Dict[str, Any]:
    """Decode a JWT without signature verification for local testing."""
    try:
        payload_part = token.split(".")[1]
        padded = payload_part + "=" * (-len(payload_part) % 4)
        decoded = base64.urlsafe_b64decode(padded)
        return json.loads(decoded)
    except Exception as exc:  # pragma: no cover
        raise ValueError("Invalid JWT token") from exc


def build_opa_input(request: Request, user: AuthenticatedUser) -> Dict[str, Any]:
    route_name = request.url.path.strip("/").replace("/", ".") or "root"
    return {
        "route": route_name,
        "method": request.method.lower(),
        "tenant": user.tenant,
        "user": {
            "tier": user.tier,
            "scopes": user.scopes,
        },
        "consent_scopes": user.scopes,
    }
