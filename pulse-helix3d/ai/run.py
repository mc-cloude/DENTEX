"""Utility entrypoint to exercise the CrewAI configuration."""
from __future__ import annotations

import json
from pathlib import Path


def load_config() -> dict:
    config_path = Path(__file__).parent / "crewai_config.yaml"
    return json.loads(json.dumps({"config": config_path.read_text()}))


if __name__ == "__main__":  # pragma: no cover
    print(load_config())
