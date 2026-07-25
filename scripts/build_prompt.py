#!/usr/bin/env python3
"""Build a self-contained generation prompt from the single normative spec."""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "references" / "SPEC.md"


def spec_for_level(level: str) -> str:
    """Keep one source file while omitting the other Level from the prompt."""
    text = SPEC.read_text(encoding="utf-8")
    level4 = text.index("## Level 4")
    level5 = text.index("## Level 5")
    review = text.index("## Visual review")
    common = text[:level4]
    selected = text[level4:level5] if level == "4" else text[level5:review]
    return common + selected + text[review:]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("concept", "reference"), required=True)
    parser.add_argument("--level", choices=("4", "5"), required=True)
    parser.add_argument("--brief", required=True)
    parser.add_argument("--lineage")
    parser.add_argument("--transformation")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.level == "4" and (args.lineage or args.transformation):
        parser.error("--lineage/--transformation are only valid for Level 5")
    if bool(args.lineage) != bool(args.transformation):
        parser.error("use --lineage and --transformation together")
    return args


def main() -> None:
    args = parse_args()
    mode = (
        "CONCEPT MODE\nNo character-specific design image is used."
        if args.mode == "concept"
        else (
            "REFERENCE MODE\nUse the supplied source image as design-language "
            "authority. Replace its complete face system with the fixed aachat "
            "LCD. Do not copy text, logos, protected identity, watermarks, or "
            "image artifacts."
        )
    )
    evolution = ""
    if args.lineage:
        evolution = (
            f"\n\nLEVEL 5 LINEAGE\nRetain: {args.lineage}\n"
            f"Transform: {args.transformation}"
        )
    prompt = (
        f"TARGET\nCreate exactly one Level {args.level} aachat character.\n\n"
        f"{mode}\n\nDESIGN BRIEF\n{args.brief}{evolution}\n\n"
        f"{spec_for_level(args.level)}\n"
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(prompt, encoding="utf-8")
    else:
        print(prompt, end="")


if __name__ == "__main__":
    main()
