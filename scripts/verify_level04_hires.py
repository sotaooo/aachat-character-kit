#!/usr/bin/env python3
"""Verify Level 04 high-resolution siblings against their 256px references."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


MASTER_SIZE = 1254


def alpha_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    bbox = image.getchannel("A").getbbox()
    if bbox is None:
        raise ValueError("image has no visible pixels")
    return bbox


def expected_bbox(
    bbox: tuple[int, int, int, int], reference_size: tuple[int, int]
) -> tuple[int, int, int, int]:
    width, height = reference_size
    scale = MASTER_SIZE / width
    return tuple(round(value * scale) for value in bbox)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=Path("agent-icons/level-04"))
    parser.add_argument("--require-count", type=int)
    args = parser.parse_args()

    outputs = sorted(args.root.rglob("*-1254.png"))
    errors: list[str] = []

    if args.require_count is not None and len(outputs) != args.require_count:
        errors.append(f"expected {args.require_count} outputs, found {len(outputs)}")

    for output_path in outputs:
        reference_path = output_path.with_name(
            output_path.name.removesuffix("-1254.png") + "-256.png"
        )
        if not reference_path.exists():
            errors.append(f"{output_path}: missing reference {reference_path.name}")
            continue

        with Image.open(reference_path) as source:
            reference = source.convert("RGBA")
        with Image.open(output_path) as source:
            output = source.convert("RGBA")

        if output.size != (MASTER_SIZE, MASTER_SIZE):
            errors.append(f"{output_path}: got {output.size}, expected 1254x1254")
        if output.mode != "RGBA":
            errors.append(f"{output_path}: got mode {output.mode}, expected RGBA")

        corners = (
            output.getpixel((0, 0))[3],
            output.getpixel((MASTER_SIZE - 1, 0))[3],
            output.getpixel((0, MASTER_SIZE - 1))[3],
            output.getpixel((MASTER_SIZE - 1, MASTER_SIZE - 1))[3],
        )
        if corners != (0, 0, 0, 0):
            errors.append(f"{output_path}: corners are not fully transparent")

        target = expected_bbox(alpha_bbox(reference), reference.size)
        actual = alpha_bbox(output)
        if any(abs(a - b) > 2 for a, b in zip(actual, target)):
            errors.append(
                f"{output_path}: subject bbox {actual} does not match expected {target}"
            )

    if errors:
        raise SystemExit("\n".join(errors))

    print(f"verified {len(outputs)} Level 04 high-resolution images")


if __name__ == "__main__":
    main()
