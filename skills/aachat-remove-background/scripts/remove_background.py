#!/usr/bin/env python3
"""Create an RGBA candidate from an approved aachat RGB master."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
PRODUCTION = ROOT / "production"
OUTPUT = ROOT / ".work" / "transparent-candidates"
MASTER_SIZE = 1254
MASTER_DIMENSIONS = (MASTER_SIZE, MASTER_SIZE)


def is_under(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("master", type=Path)
    parser.add_argument("--model", default="birefnet-general")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_path = args.master.expanduser().resolve()
    if not source_path.is_file() or not is_under(source_path, PRODUCTION):
        sys.exit("FAIL: input must be an approved file under production/")
    with Image.open(source_path) as opened:
        if (
            opened.format != "PNG"
            or opened.size != MASTER_DIMENSIONS
            or opened.mode != "RGB"
        ):
            sys.exit(
                "FAIL: input must be a native 1254x1254 RGB PNG production master"
            )
        source = opened.copy()

    try:
        from rembg import new_session, remove
    except ImportError:
        sys.exit(
            "FAIL: rembg is not installed; follow the setup command in "
            "skills/aachat-remove-background/SKILL.md"
        )

    relative = source_path.relative_to(PRODUCTION.resolve())
    target = OUTPUT / relative.with_name(f"{source_path.stem}-alpha.png")
    if target.exists():
        sys.exit(f"FAIL: candidate already exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)

    session = new_session(args.model)
    result = remove(source, session=session)
    if not isinstance(result, Image.Image):
        sys.exit("FAIL: rembg did not return a Pillow image")
    if result.size != MASTER_DIMENSIONS:
        sys.exit(f"FAIL: output size changed to {result.size}")
    result = result.convert("RGBA")
    if result.getchannel("A").getextrema() in ((255, 255), (0, 0)):
        sys.exit("FAIL: output is not a usable transparent image")
    result.save(target, "PNG")
    print(f"TRANSPARENT CANDIDATE: {target}")


if __name__ == "__main__":
    main()
