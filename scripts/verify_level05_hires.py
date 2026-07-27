#!/usr/bin/env python3
"""Verify provisional Level 05 native 1254px transparent canonical images."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from pathlib import Path

from PIL import Image


ROOT = Path("agent-icons/level-05")
ASSIGNMENTS = ROOT / ".orchestration" / "native-1254" / "assignments"
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
RESERVED = set(GROUPS.values())
PROVISIONAL_NAME = re.compile(
    r"^aachat-ascend-("
    + "|".join(GROUPS.values())
    + r")-unlinked-([a-z]+)\.png$"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def alpha_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    bbox = image.getchannel("A").getbbox()
    if bbox is None:
        raise ValueError("image has no visible pixels")
    return bbox


def expected_bbox(
    bbox: tuple[int, int, int, int], reference_size: tuple[int, int]
) -> tuple[int, int, int, int]:
    width, height = reference_size
    if width != height:
        raise ValueError(f"reference must be square, got {width}x{height}")
    scale = MASTER_SIZE / width
    return tuple(round(value * scale) for value in bbox)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-accepted", type=int)
    parser.add_argument("--require-total", type=int, default=305)
    args = parser.parse_args()

    errors: list[str] = []
    rows: list[dict[str, str]] = []
    assignment_paths = sorted(ASSIGNMENTS.glob("worker-*.csv"))
    if len(assignment_paths) != 5:
        errors.append(f"expected 5 assignment files, found {len(assignment_paths)}")
    for path in assignment_paths:
        with path.open(newline="", encoding="utf-8") as source:
            rows.extend(csv.DictReader(source))

    if len(rows) != args.require_total:
        errors.append(f"expected {args.require_total} assignment rows, found {len(rows)}")

    references = [row["reference_relative_path"] for row in rows]
    if len(references) != len(set(references)):
        errors.append("assignment rows contain duplicate references")

    accepted = [row for row in rows if row["status"] == "accepted"]
    if args.require_accepted is not None and len(accepted) != args.require_accepted:
        errors.append(
            f"expected {args.require_accepted} accepted outputs, found {len(accepted)}"
        )
    invalid_statuses = sorted(
        {row["status"] for row in rows} - {"pending", "accepted"}
    )
    if invalid_statuses:
        errors.append(f"invalid statuses: {', '.join(invalid_statuses)}")

    expected_outputs: set[Path] = set()
    names: set[str] = set()
    for row in rows:
        if row["status"] == "pending":
            populated = [
                field
                for field in (
                    "provisional_filename",
                    "provisional_relative_path",
                    "evolution",
                    "sha256",
                    "visual_qa",
                )
                if row[field]
            ]
            if populated:
                errors.append(
                    f"{row['reference_relative_path']}: pending row has populated "
                    f"fields {', '.join(populated)}"
                )
            continue

        filename = row["provisional_filename"]
        match = PROVISIONAL_NAME.fullmatch(filename)
        if match is None:
            errors.append(f"{filename}: invalid provisional filename")
            continue
        group, evolution = match.groups()
        if group != row["group"]:
            errors.append(f"{filename}: group does not match assignment")
        if evolution != row["evolution"]:
            errors.append(f"{filename}: evolution does not match assignment")
        if evolution in RESERVED:
            errors.append(f"{filename}: evolution is a reserved group word")
        if filename in names:
            errors.append(f"duplicate provisional filename: {filename}")
        names.add(filename)
        if row["visual_qa"] != "pass":
            errors.append(f"{filename}: visual_qa is not pass")

        output = ROOT / row["provisional_relative_path"]
        reference = ROOT / row["reference_relative_path"]
        expected_outputs.add(output)
        if output.name != filename:
            errors.append(f"{output}: filename does not match provisional_filename")
        if not output.exists():
            errors.append(f"{output}: missing output")
            continue
        if not reference.exists():
            errors.append(f"{reference}: missing reference")
            continue
        if sha256(output) != row["sha256"]:
            errors.append(f"{output}: sha256 does not match assignment")

        with Image.open(reference) as source:
            if source.size != (256, 256):
                errors.append(f"{reference}: expected 256x256, got {source.size}")
            reference_image = source.convert("RGBA")
        with Image.open(output) as source:
            if source.size != (MASTER_SIZE, MASTER_SIZE):
                errors.append(
                    f"{output}: expected {MASTER_SIZE}x{MASTER_SIZE}, got {source.size}"
                )
            if source.mode != "RGBA":
                errors.append(f"{output}: expected RGBA, got {source.mode}")
            output_image = source.convert("RGBA")

        corners = (
            output_image.getpixel((0, 0))[3],
            output_image.getpixel((MASTER_SIZE - 1, 0))[3],
            output_image.getpixel((0, MASTER_SIZE - 1))[3],
            output_image.getpixel((MASTER_SIZE - 1, MASTER_SIZE - 1))[3],
        )
        if corners != (0, 0, 0, 0):
            errors.append(f"{output}: corners are not fully transparent")
        try:
            target = expected_bbox(alpha_bbox(reference_image), reference_image.size)
            actual = alpha_bbox(output_image)
            if any(abs(left - right) > 2 for left, right in zip(actual, target)):
                errors.append(
                    f"{output}: subject bbox {actual} does not match expected {target}"
                )
        except ValueError as exc:
            errors.append(f"{output}: {exc}")

    actual_outputs = set(ROOT.rglob("aachat-ascend-*.png"))
    unexpected = actual_outputs - expected_outputs
    missing = expected_outputs - actual_outputs
    if unexpected:
        errors.append(
            "unrecorded provisional outputs: "
            + ", ".join(str(path) for path in sorted(unexpected))
        )
    if missing:
        errors.append(
            "recorded outputs missing from tree: "
            + ", ".join(str(path) for path in sorted(missing))
        )

    if errors:
        raise SystemExit("\n".join(errors))
    print(
        f"verified {len(accepted)} accepted provisional Level 05 images "
        f"across {len(rows)} assignments"
    )


if __name__ == "__main__":
    main()
