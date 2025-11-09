"""Simulated wearable ingestion tool."""
from __future__ import annotations

from typing import Any, Dict


def summarize_ingest(samples: list[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(samples)
    vendors = sorted({item.get("vendor", "unknown") for item in samples})
    return {"count": total, "vendors": vendors}
