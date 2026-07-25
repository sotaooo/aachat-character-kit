#!/usr/bin/env python3
"""Verify canonical Level 04 masters and their manifest references."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
import re
from pathlib import Path

from PIL import Image


MASTER_SIZE = 1254
GROUPS = {
    "B01-HUM": "humanoid",
    "B02-FAU": "fauna",
    "B03-FLO": "flora",
    "B04-CUL": "culinary",
    "B05-MEC": "machine",
    "B06-OBJ": "artifact",
    "B07-MAT": "mineral",
    "B08-NAT": "nature",
    "B09-ECH": "echo",
    "B10-ANO": "anomaly",
}
RESERVED_WORDS = set(GROUPS.values())
CANONICAL_NAME = re.compile(
    r"^aachat-forge-(" + "|".join(GROUPS.values()) + r")-([a-z]+(?:-[a-z]+)*)\.png$"
)


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

    errors: list[str] = []
    csv_path = args.root / "manifest.csv"
    json_path = args.root / "manifest.json"
    summary_path = args.root / "summary.json"

    with csv_path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    json_rows = json.loads(json_path.read_text(encoding="utf-8"))
    if rows != json_rows:
        errors.append("manifest.csv and manifest.json differ")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    category_counts = dict(Counter(row["origin_type"] for row in rows))
    if summary.get("level") != "04":
        errors.append("summary.json level is not 04")
    if summary.get("total") != len(rows):
        errors.append("summary.json total does not match manifest rows")
    if summary.get("categories") != category_counts:
        errors.append("summary.json category counts do not match manifest rows")

    outputs = sorted(args.root.rglob("aachat-forge-*.png"))
    temporary_outputs = sorted(args.root.rglob("*-1254.png"))
    references = sorted(args.root.rglob("*-256.png"))

    expected_count = args.require_count if args.require_count is not None else len(rows)
    if len(rows) != expected_count:
        errors.append(f"expected {expected_count} manifest rows, found {len(rows)}")
    if len(outputs) != expected_count:
        errors.append(f"expected {expected_count} canonical outputs, found {len(outputs)}")
    if len(references) != expected_count:
        errors.append(f"expected {expected_count} references, found {len(references)}")
    if temporary_outputs:
        errors.append(f"found {len(temporary_outputs)} obsolete *-1254.png outputs")

    manifest_outputs: set[Path] = set()
    manifest_references: set[Path] = set()
    names: set[str] = set()
    for row in rows:
        output_path = args.root / row["relative_path"]
        reference_path = args.root / row["reference_relative_path"]
        manifest_outputs.add(output_path)
        manifest_references.add(reference_path)

        filename = row["filename"]
        if filename in names:
            errors.append(f"duplicate canonical filename: {filename}")
        names.add(filename)

        match = CANONICAL_NAME.match(filename)
        expected_group = GROUPS.get(row["origin_type"])
        if match is None:
            errors.append(f"{filename}: invalid Level 4 canonical filename")
        else:
            group, identity = match.groups()
            if group != expected_group:
                errors.append(
                    f"{filename}: group {group} does not match {row['origin_type']}"
                )
            reserved = RESERVED_WORDS.intersection(identity.split("-"))
            if reserved:
                errors.append(
                    f"{filename}: identity contains reserved group words "
                    f"{', '.join(sorted(reserved))}"
                )

        if row["asset_status"] != "native-master":
            errors.append(f"{filename}: asset_status is not native-master")
        if row["resolution"] != "1254x1254":
            errors.append(f"{filename}: manifest resolution is not 1254x1254")
        if row["color_mode"] != "RGBA":
            errors.append(f"{filename}: manifest color_mode is not RGBA")

        if not output_path.exists():
            errors.append(f"{output_path}: missing canonical output")
            continue
        if not reference_path.exists():
            errors.append(f"{reference_path}: missing reference")
            continue

        with Image.open(reference_path) as source:
            if source.size != (256, 256):
                errors.append(f"{reference_path}: got {source.size}, expected 256x256")
            reference = source.convert("RGBA")
        with Image.open(output_path) as source:
            if source.mode != "RGBA":
                errors.append(f"{output_path}: got mode {source.mode}, expected RGBA")
            output = source.convert("RGBA")

        if output.size != (MASTER_SIZE, MASTER_SIZE):
            errors.append(f"{output_path}: got {output.size}, expected 1254x1254")

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

    if manifest_outputs != set(outputs):
        errors.append("canonical outputs do not exactly match manifest relative_path values")
    if manifest_references != set(references):
        errors.append(
            "256px references do not exactly match manifest reference_relative_path values"
        )

    if errors:
        raise SystemExit("\n".join(errors))

    print(f"verified {len(outputs)} canonical Level 04 high-resolution images")


if __name__ == "__main__":
    main()
