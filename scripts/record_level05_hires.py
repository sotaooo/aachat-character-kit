#!/usr/bin/env python3
"""Record one accepted provisional Level 05 canonical image."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from pathlib import Path


ROOT = Path("agent-icons/level-05")
RESERVED = {
    "humanoid",
    "fauna",
    "flora",
    "culinary",
    "machine",
    "artifact",
    "mineral",
    "nature",
    "echo",
    "anomaly",
}
WORD = re.compile(r"^[a-z]+$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assignment", required=True, type=Path)
    parser.add_argument("--reference", required=True)
    parser.add_argument("--evolution", required=True)
    parser.add_argument("--visual-pass", action="store_true")
    args = parser.parse_args()

    if not args.visual_pass:
        raise SystemExit("--visual-pass is required after native-resolution inspection")
    if not WORD.fullmatch(args.evolution):
        raise SystemExit("evolution must be exactly one lowercase ASCII word")
    if args.evolution in RESERVED:
        raise SystemExit("evolution must not be one of the ten reserved group words")

    with args.assignment.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        rows = list(reader)
        fieldnames = reader.fieldnames
    if fieldnames is None:
        raise SystemExit(f"{args.assignment}: missing header")

    matches = [row for row in rows if row["reference_relative_path"] == args.reference]
    if len(matches) != 1:
        raise SystemExit(f"expected one assignment for {args.reference}, found {len(matches)}")
    row = matches[0]
    if row["status"] == "accepted":
        raise SystemExit(f"{args.reference}: already accepted")

    filename = f"aachat-ascend-{row['group']}-unlinked-{args.evolution}.png"
    relative_path = str(Path(args.reference).parent / filename)
    output = ROOT / relative_path
    if not output.exists():
        raise SystemExit(f"missing provisional output: {output}")

    for other in rows:
        if other is row:
            continue
        if other["provisional_filename"] == filename:
            raise SystemExit(f"duplicate provisional filename in assignment: {filename}")

    row.update(
        {
            "provisional_filename": filename,
            "provisional_relative_path": relative_path,
            "evolution": args.evolution,
            "status": "accepted",
            "sha256": sha256(output),
            "visual_qa": "pass",
        }
    )
    with args.assignment.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"recorded {args.reference} -> {relative_path}")


if __name__ == "__main__":
    main()
