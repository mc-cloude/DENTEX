from __future__ import annotations

from pathlib import Path


def test_frontend_main_exists():
    main = Path("frontend/lib/main.dart")
    assert main.exists()
    assert "Pulse HELIX3D" in main.read_text()
