#!/usr/bin/env python3
"""Finalize Level 05 names, manifests, and reference cleanup."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image


ROOT = Path("agent-icons/level-05")
LEVEL4_ROOT = Path("agent-icons/level-04")
ASSIGNMENTS = ROOT / ".orchestration" / "native-1254" / "assignments"
LINEAGE_FILES = (
    Path(".work/orchestration/level05-finalize/lineage-a.tsv"),
    Path(".work/orchestration/level05-finalize/lineage-b.tsv"),
)
EXPECTED = 305
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
VALID_CONFIDENCE = {"exact", "high", "provisional", "balanced"}
TOKEN = re.compile(r"^[a-z]+(?:-[a-z]+)*$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path, delimiter: str = ",") -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source, delimiter=delimiter))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(
            target, fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    manifest_rows = read_csv(ROOT / "manifest.csv")
    assignments: list[dict[str, str]] = []
    assignment_sources: dict[str, Path] = {}
    for path in sorted(ASSIGNMENTS.glob("worker-*.csv")):
        for row in read_csv(path):
            reference = row["reference_relative_path"]
            if reference in assignment_sources:
                raise SystemExit(f"duplicate assignment reference: {reference}")
            assignment_sources[reference] = path
            assignments.append(row)

    lineage: list[dict[str, str]] = []
    for path in LINEAGE_FILES:
        lineage.extend(read_csv(path, delimiter="\t"))

    if not (
        len(manifest_rows) == len(assignments) == len(lineage) == EXPECTED
    ):
        raise SystemExit(
            "expected 305 manifest, assignment, and lineage rows; got "
            f"{len(manifest_rows)}, {len(assignments)}, {len(lineage)}"
        )

    manifest_by_reference = {
        row["relative_path"]: row for row in manifest_rows
    }
    assignment_by_output = {
        row["provisional_relative_path"]: row for row in assignments
    }
    lineage_by_output = {
        row["level05_relative_path"]: row for row in lineage
    }
    if len(manifest_by_reference) != EXPECTED:
        raise SystemExit("manifest reference paths are not unique")
    if len(assignment_by_output) != EXPECTED:
        raise SystemExit("assignment output paths are not unique")
    if len(lineage_by_output) != EXPECTED:
        raise SystemExit("lineage Level 05 paths are not unique")
    if set(assignment_by_output) != set(lineage_by_output):
        raise SystemExit("assignment and lineage Level 05 paths differ")

    level4_rows = read_csv(LEVEL4_ROOT / "manifest.csv")
    level4_by_path = {row["relative_path"]: row for row in level4_rows}
    plans: list[dict[str, object]] = []
    final_names: set[str] = set()
    final_rows: list[dict[str, str]] = []

    for provisional_relative_path in sorted(assignment_by_output):
        assignment = assignment_by_output[provisional_relative_path]
        mapping = lineage_by_output[provisional_relative_path]
        reference_relative_path = assignment["reference_relative_path"]
        reference_row = manifest_by_reference.get(reference_relative_path)
        if reference_row is None:
            raise SystemExit(f"missing manifest reference: {reference_relative_path}")
        parent_relative_path = mapping["level04_relative_path"]
        parent = level4_by_path.get(parent_relative_path)
        if parent is None:
            raise SystemExit(f"missing Level 4 parent: {parent_relative_path}")
        if parent["origin_type"] != assignment["origin_type"]:
            raise SystemExit(
                f"{provisional_relative_path}: parent category mismatch"
            )
        confidence = mapping["confidence"]
        if confidence not in VALID_CONFIDENCE:
            raise SystemExit(
                f"{provisional_relative_path}: invalid confidence {confidence}"
            )
        parent_name = mapping["level04_name"]
        evolution = mapping["level05_evolution"]
        if not TOKEN.fullmatch(parent_name) or not TOKEN.fullmatch(evolution):
            raise SystemExit(
                f"{provisional_relative_path}: invalid parent/evolution token"
            )
        group = GROUPS[assignment["origin_type"]]
        final_filename = (
            f"aachat-ascend-{group}-{parent_name}-{evolution}.png"
        )
        if final_filename in final_names:
            raise SystemExit(f"duplicate final filename: {final_filename}")
        final_names.add(final_filename)
        final_relative_path = str(
            Path(provisional_relative_path).parent / final_filename
        )
        source = ROOT / provisional_relative_path
        target = ROOT / final_relative_path
        reference = ROOT / reference_relative_path
        if not source.exists():
            raise SystemExit(f"missing provisional master: {source}")
        if target.exists() and target != source:
            raise SystemExit(f"final target already exists: {target}")
        if not reference.exists():
            raise SystemExit(f"missing 256px reference: {reference}")
        if sha256(source) != assignment["sha256"]:
            raise SystemExit(f"{source}: assignment SHA mismatch")
        with Image.open(source) as image:
            if image.size != (1254, 1254) or image.mode != "RGBA":
                raise SystemExit(f"{source}: invalid master contract")

        plans.append(
            {
                "source": source,
                "target": target,
                "reference": reference,
                "assignment": assignment,
                "final_filename": final_filename,
                "final_relative_path": final_relative_path,
            }
        )
        final_rows.append(
            {
                "level": "05",
                "origin_type": assignment["origin_type"],
                "origin_name": reference_row["origin_name"],
                "filename": final_filename,
                "relative_path": final_relative_path,
                "parent_filename": parent["filename"],
                "parent_relative_path": parent_relative_path,
                "evolution": evolution,
                "lineage_confidence": confidence,
                "reference_filename": assignment["reference_filename"],
                "reference_relative_path": reference_relative_path,
                "source_filename": reference_row["source_filename"],
                "classification_basis": (
                    "full visual review: Level 05 native master; "
                    f"Level 04 lineage {confidence}"
                ),
                "asset_status": "native-master",
                "resolution": "1254x1254",
                "color_mode": "RGBA",
            }
        )

    # All destructive preconditions have passed. Rename masters first, update
    # assignment provenance, write manifests, then remove superseded references.
    for plan in plans:
        source = plan["source"]
        target = plan["target"]
        assert isinstance(source, Path) and isinstance(target, Path)
        source.rename(target)
        assignment = plan["assignment"]
        assert isinstance(assignment, dict)
        assignment["provisional_filename"] = str(plan["final_filename"])
        assignment["provisional_relative_path"] = str(
            plan["final_relative_path"]
        )

    by_assignment_file: dict[Path, list[dict[str, str]]] = defaultdict(list)
    for row in assignments:
        by_assignment_file[assignment_sources[row["reference_relative_path"]]].append(
            row
        )
    for path, rows in by_assignment_file.items():
        write_csv(path, rows)

    final_rows.sort(key=lambda row: (row["origin_type"], row["relative_path"]))
    write_csv(ROOT / "manifest.csv", final_rows)
    (ROOT / "manifest.json").write_text(
        json.dumps(final_rows, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    confidence_counts = Counter(row["lineage_confidence"] for row in final_rows)
    category_counts = Counter(row["origin_type"] for row in final_rows)
    parent_counts = Counter(row["parent_relative_path"] for row in final_rows)
    summary = {
        "level": "05",
        "total": len(final_rows),
        "categories": dict(sorted(category_counts.items())),
        "asset_status": "native-master",
        "resolution": "1254x1254",
        "color_mode": "RGBA",
        "lineage_confidence": dict(sorted(confidence_counts.items())),
        "parents_used": len(parent_counts),
        "max_children_per_parent": max(parent_counts.values()),
        "references_removed": len(plans),
    }
    (ROOT / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    for plan in plans:
        reference = plan["reference"]
        assert isinstance(reference, Path)
        reference.unlink()

    print(
        f"finalized {len(final_rows)} Level 05 masters, "
        f"removed {len(plans)} references"
    )


if __name__ == "__main__":
    main()
