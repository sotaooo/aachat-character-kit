#!/usr/bin/env python3
"""Point the Level 04 manifests at canonical 1254px masters.

Named references map directly from their semantic slug. Candidate-only
references are matched to the remaining canonical outputs by visual distance.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from PIL import Image, ImageChops, ImageStat


ROOT = Path("agent-icons/level-04")
CSV_PATH = ROOT / "manifest.csv"
JSON_PATH = ROOT / "manifest.json"
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
SEMANTIC_REFERENCE = re.compile(
    r"^aachat-level-04-b\d{2}-[a-z]{3}-(?:r\d+-|\d+-)(.+)-256\.png$"
)


def flattened(path: Path) -> Image.Image:
    rgba = Image.open(path).convert("RGBA").resize((128, 128), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", rgba.size, "white")
    canvas.alpha_composite(rgba)
    return canvas.convert("RGB")


def distance(left: Image.Image, right: Image.Image) -> float:
    means = ImageStat.Stat(ImageChops.difference(left, right)).mean
    return sum(means) / (len(means) * 255)


def main() -> None:
    with CSV_PATH.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))

    mappings: dict[str, str] = {}
    for origin_type, group in GROUPS.items():
        category_rows = [row for row in rows if row["origin_type"] == origin_type]
        if not category_rows:
            raise SystemExit(f"manifest has no rows for {origin_type}")

        category_dir = ROOT / Path(category_rows[0]["relative_path"]).parent
        outputs = sorted(category_dir.glob(f"aachat-forge-{group}-*.png"))
        if len(outputs) != len(category_rows):
            raise SystemExit(
                f"{category_dir}: expected {len(category_rows)} canonical outputs, "
                f"found {len(outputs)}"
            )

        unmatched_outputs = {output.name: output for output in outputs}
        candidate_rows: list[dict[str, str]] = []
        for row in category_rows:
            reference_name = row["filename"]
            match = SEMANTIC_REFERENCE.match(reference_name)
            if match:
                output_name = f"aachat-forge-{group}-{match.group(1)}.png"
                if output_name not in unmatched_outputs:
                    raise SystemExit(
                        f"{reference_name}: expected canonical output {output_name}"
                    )
                mappings[reference_name] = output_name
                unmatched_outputs.pop(output_name)
            else:
                candidate_rows.append(row)

        if len(candidate_rows) != len(unmatched_outputs):
            raise SystemExit(
                f"{category_dir}: {len(candidate_rows)} candidate references but "
                f"{len(unmatched_outputs)} unmatched outputs"
            )

        references = {
            row["filename"]: flattened(ROOT / row["relative_path"])
            for row in candidate_rows
        }
        candidates = {
            output_name: flattened(output_path)
            for output_name, output_path in unmatched_outputs.items()
        }
        scored = sorted(
            (
                distance(reference_image, output_image),
                reference_name,
                output_name,
            )
            for reference_name, reference_image in references.items()
            for output_name, output_image in candidates.items()
        )

        assigned_references: set[str] = set()
        assigned_outputs: set[str] = set()
        for score, reference_name, output_name in scored:
            if reference_name in assigned_references or output_name in assigned_outputs:
                continue
            if score > 0.22:
                raise SystemExit(
                    f"{reference_name}: closest remaining visual match is too weak "
                    f"({output_name}, distance={score:.3f})"
                )
            mappings[reference_name] = output_name
            assigned_references.add(reference_name)
            assigned_outputs.add(output_name)
            print(f"{reference_name} -> {output_name} ({score:.3f})")

        if len(assigned_references) != len(candidate_rows):
            raise SystemExit(f"{category_dir}: incomplete candidate matching")

    final_rows: list[dict[str, str]] = []
    for row in rows:
        reference_filename = row["filename"]
        reference_relative_path = row["relative_path"]
        canonical_filename = mappings[reference_filename]
        canonical_relative_path = str(
            Path(reference_relative_path).parent / canonical_filename
        )
        final_rows.append(
            {
                "level": row["level"],
                "origin_type": row["origin_type"],
                "origin_name": row["origin_name"],
                "filename": canonical_filename,
                "relative_path": canonical_relative_path,
                "reference_filename": reference_filename,
                "reference_relative_path": reference_relative_path,
                "source_filename": row["source_filename"],
                "classification_basis": row["classification_basis"],
                "asset_status": "native-master",
                "resolution": "1254x1254",
                "color_mode": "RGBA",
            }
        )

    fieldnames = list(final_rows[0])
    with CSV_PATH.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(final_rows)
    JSON_PATH.write_text(
        json.dumps(final_rows, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"updated {CSV_PATH} and {JSON_PATH} with {len(final_rows)} masters")


if __name__ == "__main__":
    main()
