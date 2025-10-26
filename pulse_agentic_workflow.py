"""Agentic workflow orchestration for Pulse inference phases."""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Dict, Optional


INITIAL_PHASE_PATH = Path(__file__).resolve().parent / "HierarchialDet-InitialPhase-Docker" / "process.py"
FINAL_PHASE_PATH = Path(__file__).resolve().parent / "HierarchialDet-FinalPhase-Docker" / "process.py"


def _load_module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(path.stem.replace("-", "_"), path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_hierarchialdet(path: Path):
    module = _load_module(path)
    if not hasattr(module, "Hierarchialdet"):
        raise AttributeError(f"Module {path} does not define Hierarchialdet")
    return module.Hierarchialdet


class PulseAgenticWorkflow:
    """Orchestrates the staged Pulse inference workflow."""

    def __init__(self, initial_path: Path = INITIAL_PHASE_PATH, final_path: Path = FINAL_PHASE_PATH):
        self.initial_cls = _load_hierarchialdet(initial_path) if initial_path.exists() else None
        self.final_cls = _load_hierarchialdet(final_path) if final_path.exists() else None

    def _run_phase(self, runner_cls, args: Dict):
        if runner_cls is None:
            raise RuntimeError("Requested phase is unavailable in the current checkout")
        runner = runner_cls()
        runner.process(args=args)

    def run_initial(self, args: Dict):
        self._run_phase(self.initial_cls, args)

    def run_final(self, args: Dict):
        self._run_phase(self.final_cls, args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Agentic workflow orchestrator for Pulse inference")
    parser.add_argument("--input-volume", type=str, default=None, help="Path to the .mha volume shared across stages")
    parser.add_argument(
        "--input-dir",
        type=str,
        default="/input/images/panoramic-dental-xrays",
        help="Directory to search for .mha volumes when --input-volume is omitted",
    )
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.0,
        help="Detection confidence applied to both inference phases",
    )
    parser.add_argument("--initial-config", type=str, default=None, help="Optional override for the initial phase config")
    parser.add_argument("--initial-weights", type=str, default=None, help="Optional override for the initial phase weights")
    parser.add_argument(
        "--initial-output",
        type=str,
        default="/output/pulse-initial-predictions.json",
        help="Destination file for the initial phase JSON output",
    )
    parser.add_argument(
        "--initial-opts",
        nargs="*",
        default=None,
        help="Optional config overrides passed to the initial phase",
    )
    parser.add_argument("--final-config", type=str, default=None, help="Optional override for the final phase config")
    parser.add_argument("--final-weights", type=str, default=None, help="Optional override for the final phase weights")
    parser.add_argument(
        "--final-output",
        type=str,
        default="/output/pulse-final-predictions.json",
        help="Destination file for the final phase JSON output",
    )
    parser.add_argument(
        "--final-opts",
        nargs="*",
        default=None,
        help="Optional config overrides passed to the final phase",
    )
    parser.add_argument(
        "--final-image-metadata",
        type=str,
        default=None,
        help="Optional metadata JSON passed to the final phase",
    )
    parser.add_argument("--skip-initial", action="store_true", help="Skip running the initial phase")
    parser.add_argument("--skip-final", action="store_true", help="Skip running the final phase")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    orchestrator = PulseAgenticWorkflow()

    shared_kwargs = {
        "input_volume": args.input_volume,
        "input_dir": args.input_dir,
        "confidence_threshold": args.confidence_threshold,
    }

    if not args.skip_initial:
        initial_kwargs = {
            **shared_kwargs,
            "config_file": args.initial_config,
            "model_weights": args.initial_weights,
            "output_file": args.initial_output,
            "opts": args.initial_opts or [],
        }
        orchestrator.run_initial(initial_kwargs)

    if not args.skip_final:
        final_kwargs = {
            **shared_kwargs,
            "config_file": args.final_config,
            "model_weights": args.final_weights,
            "output_file": args.final_output,
            "opts": args.final_opts or [],
            "image_metadata": args.final_image_metadata,
        }
        orchestrator.run_final(final_kwargs)

    return 0


if __name__ == "__main__":
    sys.exit(main())
