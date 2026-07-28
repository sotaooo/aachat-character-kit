#!/usr/bin/env python3
"""Verify finalized Level 05 canonical masters and lineage manifests."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from PIL import Image


ROOT = Path("agent-icons/level-05")
LEVEL4_ROOT = Path("agent-icons/level-04")
EXPECTED = 305
FINAL_NAME = re.compile(
    r"^aachat-ascend-"
    r"(humanoid|fauna|flora|culinary|machine|artifact|mineral|nature|echo|anomaly)"
    r"-([a-z]+(?:-[a-z]+)*)-([a-z]+)\.png$"
)
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
CONFIDENCE = {"exact", "high", "provisional", "balanced"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    with (ROOT / "manifest.csv").open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    json_rows = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    summary = json.loads((ROOT / "summary.json").read_text(encoding="utf-8"))
    with (LEVEL4_ROOT / "manifest.csv").open(
        newline="", encoding="utf-8"
    ) as source:
        level4 = {row["relative_path"]: row for row in csv.DictReader(source)}

    errors: list[str] = []
    if len(rows) != EXPECTED:
        errors.append(f"manifest has {len(rows)} rows, expected {EXPECTED}")
    if rows != json_rows:
        errors.append("manifest.csv and manifest.json differ")
    if summary.get("total") != EXPECTED:
        errors.append("summary total is not 305")

    names: set[str] = set()
    paths: set[str] = set()
    parent_counts: Counter[str] = Counter()
    confidence_counts: Counter[str] = Counter()
    expected_files: set[Path] = set()
    for row in rows:
        filename = row["filename"]
        relative_path = row["relative_path"]
        match = FINAL_NAME.fullmatch(filename)
        if match is None:
            errors.append(f"{filename}: invalid final filename")
            continue
        group, parent_name, evolution = match.groups()
        if group != GROUPS.get(row["origin_type"]):
            errors.append(f"{filename}: group/category mismatch")
        if row["evolution"] != evolution:
            errors.append(f"{filename}: evolution mismatch")
        if filename in names or relative_path in paths:
            errors.append(f"{filename}: duplicate manifest identity")
        names.add(filename)
        paths.add(relative_path)
        if Path(relative_path).name != filename:
            errors.append(f"{relative_path}: filename/path mismatch")
        parent = level4.get(row["parent_relative_path"])
        if parent is None:
            errors.append(f"{filename}: missing Level 4 parent")
        else:
            if parent["filename"] != row["parent_filename"]:
                errors.append(f"{filename}: parent filename mismatch")
            expected_parent_name = parent["filename"].removeprefix(
                f"aachat-forge-{group}-"
            ).removesuffix(".png")
            if parent_name != expected_parent_name:
                errors.append(f"{filename}: inherited parent name mismatch")
            if parent["origin_type"] != row["origin_type"]:
                errors.append(f"{filename}: parent category mismatch")
        confidence = row["lineage_confidence"]
        if confidence not in CONFIDENCE:
            errors.append(f"{filename}: invalid lineage confidence")
        confidence_counts[confidence] += 1
        parent_counts[row["parent_relative_path"]] += 1
        if row["asset_status"] != "native-master":
            errors.append(f"{filename}: asset status is not native-master")
        if row["resolution"] != "1254x1254" or row["color_mode"] != "RGBA":
            errors.append(f"{filename}: file contract metadata mismatch")

        path = ROOT / relative_path
        expected_files.add(path)
        if not path.exists():
            errors.append(f"{path}: missing master")
            continue
        with Image.open(path) as image:
            if image.size != (1254, 1254) or image.mode != "RGBA":
                errors.append(f"{path}: invalid image contract")
            corners = (
                image.getpixel((0, 0))[3],
                image.getpixel((1253, 0))[3],
                image.getpixel((0, 1253))[3],
                image.getpixel((1253, 1253))[3],
            )
            if corners != (0, 0, 0, 0):
                errors.append(f"{path}: corners are not transparent")

    actual_files = set(ROOT.rglob("aachat-ascend-*.png"))
    if actual_files != expected_files:
        errors.append("manifest and canonical Level 05 file set differ")
    references = list(ROOT.rglob("aachat-level-05-*-256.png"))
    if references:
        errors.append(f"{len(references)} superseded 256px references remain")
    if list(ROOT.rglob("aachat-ascend-*-unlinked-*.png")):
        errors.append("unlinked provisional filenames remain")
    if summary.get("lineage_confidence") != dict(
        sorted(confidence_counts.items())
    ):
        errors.append("summary lineage confidence counts differ")
    if summary.get("parents_used") != len(parent_counts):
        errors.append("summary parents_used differs")
    if summary.get("max_children_per_parent") != max(parent_counts.values()):
        errors.append("summary max_children_per_parent differs")

    assignment_rows: list[dict[str, str]] = []
    for path in sorted(
        (ROOT / ".orchestration/native-1254/assignments").glob("worker-*.csv")
    ):
        with path.open(newline="", encoding="utf-8") as source:
            assignment_rows.extend(csv.DictReader(source))
    if len(assignment_rows) != EXPECTED:
        errors.append("assignment row count is not 305")
    for row in assignment_rows:
        path = ROOT / row["provisional_relative_path"]
        if not path.exists():
            errors.append(f"{path}: assignment points to missing final master")
        elif sha256(path) != row["sha256"]:
            errors.append(f"{path}: assignment SHA mismatch")

    if errors:
        raise SystemExit("\n".join(errors))
    print(
        f"verified {len(rows)} finalized Level 05 native masters; "
        f"{len(parent_counts)} Level 04 parents used; "
        f"confidence={dict(sorted(confidence_counts.items()))}"
    )


if __name__ == "__main__":
    main()
