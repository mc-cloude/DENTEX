"""CLI for validating data contracts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft7Validator


def validate(sample_path: Path, schema_path: Path) -> int:
    sample = json.loads(sample_path.read_text())
    schema = json.loads(schema_path.read_text())
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(sample), key=lambda e: e.path)
    if errors:
        for error in errors:
            print(f"Validation error: {list(error.path)} -> {error.message}")
        return 1
    print("Validation passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True)
    parser.add_argument("--schema", required=True)
    args = parser.parse_args()
    return validate(Path(args.src), Path(args.schema))


if __name__ == "__main__":
    raise SystemExit(main())
