"""Governance enforcement helper."""
from __future__ import annotations

from typing import Dict


def evaluate_guardrails(text: str, consent_scopes: list[str]) -> Dict[str, str | bool]:
    flagged = "telemed" in text.lower() and "ai:telemed" not in consent_scopes
    return {
        "flagged": flagged,
        "reason": "Telemed scope missing" if flagged else "ok",
    }
