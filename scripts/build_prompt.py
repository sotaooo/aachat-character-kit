#!/usr/bin/env python3
"""Build a self-contained generation prompt from the single normative spec."""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "references" / "SPEC.md"
LEVEL_MARKERS = {
    "4": ("<!-- AACHAT_LEVEL_4_START -->", "<!-- AACHAT_LEVEL_4_END -->"),
    "5": ("<!-- AACHAT_LEVEL_5_START -->", "<!-- AACHAT_LEVEL_5_END -->"),
}
SHARED_AFTER_LEVELS = "<!-- AACHAT_SHARED_AFTER_LEVELS -->"


def spec_for_level(level: str) -> str:
    """Keep one source file while omitting the other Level from the prompt."""
    text = SPEC.read_text(encoding="utf-8")
    try:
        level4_start = text.index(LEVEL_MARKERS["4"][0])
        level4_end = text.index(LEVEL_MARKERS["4"][1], level4_start)
        level5_start = text.index(LEVEL_MARKERS["5"][0], level4_end)
        level5_end = text.index(LEVEL_MARKERS["5"][1], level5_start)
        shared_start = text.index(SHARED_AFTER_LEVELS, level5_end)
        if not level4_start < level4_end < level5_start < level5_end < shared_start:
            raise ValueError
        start_marker, end_marker = LEVEL_MARKERS[level]
        selected_start = text.index(start_marker) + len(start_marker)
        selected_end = text.index(end_marker, selected_start)
    except (KeyError, ValueError) as error:
        raise RuntimeError(
            "references/SPEC.md section markers are missing or out of order"
        ) from error
    common = text[:level4_start].rstrip()
    selected = text[selected_start:selected_end].strip()
    shared = text[shared_start + len(SHARED_AFTER_LEVELS) :].lstrip()
    return f"{common}\n\n{selected}\n\n{shared}"


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
