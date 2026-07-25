#!/usr/bin/env python3
"""Fit a generated transparent subject to the reference image's normalized bbox."""

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


def scaled_reference_bbox(
    bbox: tuple[int, int, int, int], reference_size: tuple[int, int]
) -> tuple[int, int, int, int]:
    width, height = reference_size
    if width != height:
        raise ValueError(f"reference must be square, got {width}x{height}")

    scale = MASTER_SIZE / width
    left, top, right, bottom = bbox
    return (
        round(left * scale),
        round(top * scale),
        round(right * scale),
        round(bottom * scale),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--generated", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    with Image.open(args.reference) as source:
        reference = source.convert("RGBA")
    with Image.open(args.generated) as source:
        generated = source.convert("RGBA")

    target_bbox = scaled_reference_bbox(alpha_bbox(reference), reference.size)
    generated_bbox = alpha_bbox(generated)
    subject = generated.crop(generated_bbox)

    left, top, right, bottom = target_bbox
    subject = subject.resize((right - left, bottom - top), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (MASTER_SIZE, MASTER_SIZE), (0, 0, 0, 0))
    canvas.alpha_composite(subject, dest=(left, top))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.output, format="PNG", optimize=True)


if __name__ == "__main__":
    main()
