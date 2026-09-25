"""Command-line entry points shared by all research phases."""

from __future__ import annotations

import argparse
import logging
from collections.abc import Sequence
from pathlib import Path

LOGGER = logging.getLogger(__name__)

PHASE_COMMANDS = {
    "simplify": 7,
    "track-amendments": 8,
    "analyze": 10,
    "qa": 11,
}


def build_parser() -> argparse.ArgumentParser:
    """Create the top-level command parser without running any pipeline."""
    parser = argparse.ArgumentParser(
        prog="sl-legal-nlp",
        description="Provenance-preserving Sri Lankan legal NLP research pipeline.",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    subparsers = parser.add_subparsers(dest="command")

    extract = subparsers.add_parser("extract", help="Phase 2 PDF extraction")
    extract.add_argument("--config", type=Path, required=True, help="Path to the YAML config")

    align = subparsers.add_parser("align", help="Phase 3 bilingual structural alignment")
    align.add_argument("--config", type=Path, required=True, help="Path to the YAML config")

    annotation = subparsers.add_parser(
        "prepare-annotation", help="Phase 4 blank annotation-task preparation"
    )
    annotation.add_argument("--config", type=Path, required=True, help="Path to the YAML config")

    split = subparsers.add_parser("split", help="Phase 5 grouped split feasibility and creation")
    split.add_argument("--config", type=Path, required=True, help="Path to the YAML config")

    ner = subparsers.add_parser("train-ner", help="Phase 6 NER baseline training")
    ner.add_argument("--config", type=Path, required=True, help="Path to the YAML config")

    for command, phase in PHASE_COMMANDS.items():
        child = subparsers.add_parser(command, help=f"Phase {phase} (not implemented yet)")
        child.add_argument("--config", type=Path, required=True, help="Path to the YAML config")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Parse CLI input and fail safely for phases not implemented yet."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    if args.command == "extract":
        from sri_lankan_legal_nlp.data.extraction import run_extraction

        return run_extraction(args.config)

    if args.command == "align":
        from sri_lankan_legal_nlp.data.alignment import run_alignment

        return run_alignment(args.config)

    if args.command == "prepare-annotation":
        from sri_lankan_legal_nlp.annotation.prepare import prepare_annotation

        return prepare_annotation(args.config)

    if args.command == "split":
        from sri_lankan_legal_nlp.data.splitting import run_splitting

        return run_splitting(args.config)

    if args.command == "train-ner":
        from sri_lankan_legal_nlp.ner.train import run_ner

        return run_ner(args.config)

    phase = PHASE_COMMANDS[args.command]
    LOGGER.error("Phase %s command '%s' is not implemented yet.", phase, args.command)
    parser.error(
        f"Phase {phase} is not implemented yet; no output was created. "
        "Proceed phase by phase from the approved plan."
    )
    return 2
