#!/usr/bin/env python3
"""Create the five tracked Level 05 high-resolution worker assignments."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path("agent-icons/level-05")
MANIFEST = ROOT / "manifest.csv"
ORCHESTRATION = ROOT / ".orchestration" / "native-1254"
ASSIGNMENTS = ORCHESTRATION / "assignments"
EXPECTED_COUNT = 305

WORKERS = {
    "worker-01": {"B06-OBJ"},
    "worker-02": {"B02-FAU", "B09-ECH", "B10-ANO"},
    "worker-03": {"B01-HUM", "B03-FLO"},
    "worker-04": {"B04-CUL", "B07-MAT"},
    "worker-05": {"B05-MEC", "B08-NAT"},
}

FIELDS = [
    "origin_type",
    "group",
    "reference_filename",
    "reference_relative_path",
    "provisional_filename",
    "provisional_relative_path",
    "evolution",
    "status",
    "sha256",
    "visual_qa",
]

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


def main() -> None:
    if ORCHESTRATION.exists():
        raise SystemExit(
            f"{ORCHESTRATION} already exists; refusing to overwrite live assignments"
        )

    with MANIFEST.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    if len(rows) != EXPECTED_COUNT:
        raise SystemExit(f"expected {EXPECTED_COUNT} manifest rows, found {len(rows)}")

    assigned_groups = set().union(*WORKERS.values())
    if assigned_groups != set(GROUPS):
        raise SystemExit("worker group partition does not cover each group exactly once")

    by_worker: dict[str, list[dict[str, str]]] = {
        worker: [] for worker in WORKERS
    }
    seen_references: set[str] = set()
    for row in rows:
        origin_type = row["origin_type"]
        worker = next(
            (name for name, groups in WORKERS.items() if origin_type in groups),
            None,
        )
        if worker is None:
            raise SystemExit(f"{row['filename']}: unassigned group {origin_type}")

        reference_relative_path = row["relative_path"]
        reference = ROOT / reference_relative_path
        if not reference.exists():
            raise SystemExit(f"missing reference: {reference}")
        if reference_relative_path in seen_references:
            raise SystemExit(f"duplicate reference: {reference_relative_path}")
        seen_references.add(reference_relative_path)

        by_worker[worker].append(
            {
                "origin_type": origin_type,
                "group": GROUPS[origin_type],
                "reference_filename": row["filename"],
                "reference_relative_path": reference_relative_path,
                "provisional_filename": "",
                "provisional_relative_path": "",
                "evolution": "",
                "status": "pending",
                "sha256": "",
                "visual_qa": "",
            }
        )

    ASSIGNMENTS.mkdir(parents=True)
    counts: dict[str, int] = {}
    for worker, worker_rows in by_worker.items():
        worker_rows.sort(
            key=lambda row: (row["origin_type"], row["reference_relative_path"])
        )
        path = ASSIGNMENTS / f"{worker}.csv"
        with path.open("w", newline="", encoding="utf-8") as target:
            writer = csv.DictWriter(target, fieldnames=FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(worker_rows)
        counts[worker] = len(worker_rows)

    category_counts = Counter(row["origin_type"] for row in rows)
    summary = {
        "contract": "level05-native-1254-rgba-unlinked-v1",
        "total": len(rows),
        "workers": counts,
        "categories": dict(sorted(category_counts.items())),
        "status": "prepared",
    }
    (ORCHESTRATION / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"prepared {len(rows)} references across {len(WORKERS)} workers: {counts}")


if __name__ == "__main__":
    main()
