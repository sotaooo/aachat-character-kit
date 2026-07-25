#!/usr/bin/env python3
"""Mechanical gates and simple candidate → human approval routing."""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".work"
CANDIDATES = WORK / "candidates"
SYSTEM_APPROVED = WORK / "system-approved"
PRODUCTION = ROOT / "production"
TRANSPARENT_CANDIDATES = WORK / "transparent-candidates"
TRANSPARENT_DERIVATIVES = ROOT / "derivatives" / "transparent"
MANIFEST = PRODUCTION / "manifest.csv"
GROUP_FOLDERS = {
    "humanoid": "B01-HUM__Humanoid",
    "fauna": "B02-FAU__Fauna",
    "flora": "B03-FLO__Flora",
    "culinary": "B04-CUL__Culinary",
    "machine": "B05-MEC__Machine",
    "artifact": "B06-OBJ__Artifact",
    "mineral": "B07-MAT__Mineral",
    "nature": "B08-NAT__Nature",
    "echo": "B09-ECH__Echo",
    "anomaly": "B10-ANO__Anomaly",
}
MASTER_NAME = re.compile(
    rf"aachat-(forge|ascend)-({'|'.join(GROUP_FOLDERS)})-"
    r"([a-z]+(?:-[a-z]+)*)\.png"
)
MANIFEST_FIELDS = ("filename", "relative_path", "resolution", "lineage")


def resolved(path: Path) -> Path:
    return path.expanduser().resolve()


def is_under(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def master_location(
    path: Path, parent: Path
) -> tuple[Path, str, str, str, str | None]:
    path = resolved(path)
    try:
        relative = path.relative_to(parent.resolve())
    except ValueError as error:
        raise ValueError(f"file must be under {parent.relative_to(ROOT)}/") from error
    if len(relative.parts) != 3:
        raise ValueError("master path must be <stage>/<group-folder>/<filename>")
    stage_folder, group_folder, filename = relative.parts
    match = MASTER_NAME.fullmatch(filename)
    if not match:
        raise ValueError("filename does not follow references/NAMING.md")
    stage, group, tail = match.groups()
    if stage_folder != stage:
        raise ValueError(f"stage folder must be {stage}/")
    if group_folder != GROUP_FOLDERS[group]:
        raise ValueError(f"group folder must be {GROUP_FOLDERS[group]}/")
    words = tail.split("-")
    if stage == "ascend":
        if len(words) < 2:
            raise ValueError("Level 5 requires an inherited name and one evolution word")
        name = "-".join(words[:-1])
        evolution = words[-1]
    else:
        name = tail
        evolution = None
    if set(words) & set(GROUP_FOLDERS):
        raise ValueError("name and evolution word must not contain a group word")
    return relative, stage, group, name, evolution


def validate_lineage(
    stage: str, group: str, name: str, evolution: str | None, lineage: str
) -> None:
    lineage_name = Path(lineage).name
    if lineage_name != lineage:
        raise ValueError("--lineage must be a plain .png filename")
    if stage == "forge":
        expected = f"aachat-origin-{group}.png"
        if lineage != expected:
            raise ValueError(f"Level 4 lineage must be {expected}")
        return
    expected = f"aachat-forge-{group}-{name}.png"
    if lineage != expected:
        raise ValueError(f"Level 5 lineage must be {expected}")
    if not evolution:
        raise ValueError("Level 5 requires one evolution word")
    parent = PRODUCTION / "forge" / GROUP_FOLDERS[group] / lineage
    if not parent.is_file():
        raise ValueError("approve the Level 4 parent before its Level 5 child")
    if sum(row["lineage"] == lineage for row in manifest_rows()) >= 3:
        raise ValueError("this Level 4 already has three approved Level 5 children")


def level4_path(root: Path, group: str, name: str) -> Path:
    filename = f"aachat-forge-{group}-{name}.png"
    return root / "forge" / GROUP_FOLDERS[group] / filename


def level5_children(root: Path, group: str, name: str) -> list[Path]:
    folder = root / "ascend" / GROUP_FOLDERS[group]
    if not folder.is_dir():
        return []
    prefix = f"aachat-ascend-{group}-{name}-"
    return [
        path
        for path in folder.glob(f"{prefix}*.png")
        if path.name.startswith(prefix)
    ]


def manifest_rows() -> list[dict[str, str]]:
    try:
        with MANIFEST.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            if tuple(reader.fieldnames or ()) != MANIFEST_FIELDS:
                raise ValueError("production/manifest.csv has an unexpected header")
            return list(reader)
    except csv.Error as error:
        raise ValueError("production/manifest.csv is invalid") from error


def record_manifest(relative: Path, lineage: str) -> None:
    rows = manifest_rows()
    if any(
        row["filename"] == relative.name
        or row["relative_path"] == relative.as_posix()
        for row in rows
    ):
        raise ValueError("production/manifest.csv already contains this master")
    with MANIFEST.open("a", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=MANIFEST_FIELDS)
        writer.writerow(
            {
                "filename": relative.name,
                "relative_path": relative.as_posix(),
                "resolution": "1024x1024",
                "lineage": lineage,
            }
        )


def check_master(path: Path) -> None:
    path = resolved(path)
    if not path.is_file():
        raise ValueError(f"file not found: {path}")
    if path.suffix.lower() != ".png":
        raise ValueError("master must have a .png extension")
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        if image.format != "PNG":
            raise ValueError(f"encoded format is {image.format}, expected PNG")
        if image.size != (1024, 1024):
            raise ValueError(f"size is {image.size}, expected (1024, 1024)")
        if image.mode != "RGB":
            raise ValueError(f"mode is {image.mode}, expected RGB")
        pixels = image.load()
        border = []
        for x in range(1024):
            border.extend((pixels[x, 0], pixels[x, 1023]))
        for y in range(1, 1023):
            border.extend((pixels[0, y], pixels[1023, y]))
        tinted = sum(
            1
            for r, g, b in border
            if min(r, g, b) < 250 or max(r, g, b) - min(r, g, b) > 3
        )
        if tinted / len(border) >= 0.01:
            raise ValueError(
                f"outer border is not neutral near-white (requires RGB >= 250 "
                f"with channel spread <= 3; fewer than 1% exceptions allowed; "
                f"{tinted}/{len(border)} suspect pixels)"
            )


def move_unique(source: Path, destination: Path) -> None:
    if destination.exists():
        raise ValueError(f"destination exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(destination))


def command_check(args: argparse.Namespace) -> None:
    check_master(args.image)
    print("MECHANICAL PASS: native 1024x1024 RGB PNG; neutral near-white border.")
    print("Visual QA is still required. Read references/SPEC.md.")


def command_system_pass(args: argparse.Namespace) -> None:
    source = resolved(args.image)
    if not is_under(source, CANDIDATES):
        raise ValueError("system-pass accepts only .work/candidates/")
    if not args.visual_pass:
        raise ValueError("inspect SPEC.md, then provide --visual-pass")
    check_master(source)
    relative, stage, group, name, _ = master_location(source, CANDIDATES)
    if stage == "ascend":
        parents = (
            level4_path(SYSTEM_APPROVED, group, name),
            level4_path(PRODUCTION, group, name),
        )
        if not any(parent.is_file() for parent in parents):
            raise ValueError("system-pass the Level 4 parent before its children")
        existing = level5_children(SYSTEM_APPROVED, group, name)
        existing += level5_children(PRODUCTION, group, name)
        if len(existing) >= 3:
            raise ValueError("this Level 4 already has three accepted Level 5 children")
    target = SYSTEM_APPROVED / relative
    move_unique(source, target)
    print(f"SYSTEM QA PASS (NOT HUMAN APPROVAL): {target}")


def command_approve(args: argparse.Namespace) -> None:
    source = resolved(args.image)
    if not is_under(source, SYSTEM_APPROVED):
        raise ValueError("approve accepts only .work/system-approved/")
    if not args.human_approved:
        raise ValueError("explicit human approval is required")
    check_master(source)
    relative, stage, group, name, evolution = master_location(
        source, SYSTEM_APPROVED
    )
    validate_lineage(stage, group, name, evolution, args.lineage)
    rows = manifest_rows()
    if any(
        row["filename"] == relative.name
        or row["relative_path"] == relative.as_posix()
        for row in rows
    ):
        raise ValueError("production/manifest.csv already contains this master")
    target = PRODUCTION / relative
    move_unique(source, target)
    record_manifest(relative, args.lineage)
    print(f"HUMAN-APPROVED PRODUCTION MASTER: {target}")


def command_family_check(args: argparse.Namespace) -> None:
    parent = resolved(args.level4)
    check_master(parent)
    _, stage, group, name, _ = master_location(parent, PRODUCTION)
    if stage != "forge":
        raise ValueError("family-check requires a production Level 4 master")
    rows = manifest_rows()
    parent_rows = [row for row in rows if row["filename"] == parent.name]
    if len(parent_rows) != 1:
        raise ValueError("Level 4 must have exactly one manifest row")
    parent_row = parent_rows[0]
    expected_parent_path = parent.relative_to(PRODUCTION.resolve()).as_posix()
    if (
        parent_row["relative_path"] != expected_parent_path
        or parent_row["resolution"] != "1024x1024"
        or parent_row["lineage"] != f"aachat-origin-{group}.png"
    ):
        raise ValueError("Level 4 manifest row is inconsistent")
    children = [row for row in rows if row["lineage"] == parent.name]
    if len(children) != 3:
        raise ValueError(f"family has {len(children)} approved Level 5 children, expected 3")
    evolutions = set()
    for row in children:
        child = PRODUCTION / row["relative_path"]
        check_master(child)
        _, child_stage, child_group, child_name, evolution = master_location(
            child, PRODUCTION
        )
        if (
            child_stage != "ascend"
            or child_group != group
            or child_name != name
            or not evolution
            or row["filename"] != child.name
            or row["resolution"] != "1024x1024"
        ):
            raise ValueError(f"invalid family member: {row['filename']}")
        evolutions.add(evolution)
    if len(evolutions) != 3:
        raise ValueError("the three Level 5 children need distinct evolution words")
    print(f"FAMILY PASS: 1 Level 4 + 3 Level 5 children for {parent.name}")


def command_reject(args: argparse.Namespace) -> None:
    source = resolved(args.image)
    if not is_under(source, WORK):
        raise ValueError("reject only deletes files under .work/")
    if not source.is_file():
        raise ValueError(f"file not found: {source}")
    source.unlink()
    print(f"REJECT DELETED: {source}")


def checkerboard(size: tuple[int, int], dark: bool = False) -> Image.Image:
    colors = ((54, 58, 66), (94, 100, 112)) if dark else ((190, 190, 190), (235, 235, 235))
    image = Image.new("RGB", size)
    draw = ImageDraw.Draw(image)
    tile = 32
    for y in range(0, size[1], tile):
        for x in range(0, size[0], tile):
            draw.rectangle(
                (x, y, x + tile - 1, y + tile - 1),
                fill=colors[(x // tile + y // tile) % 2],
            )
    return image


def make_preview(master: Image.Image, derivative: Image.Image, output: Path) -> None:
    panel_size = (1024, 1024)
    panels = [master.copy()]
    for dark in (False, True):
        panel = checkerboard(panel_size, dark=dark)
        panel.paste(derivative, (0, 0), derivative)
        panels.append(panel)
    canvas = Image.new("RGB", (3072, 1024), "white")
    for index, panel in enumerate(panels):
        canvas.paste(panel, (index * 1024, 0))
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, "PNG")


def check_derivative(master_path: Path, derivative_path: Path) -> tuple[Image.Image, Image.Image]:
    check_master(master_path)
    master_relative, _, _, _, _ = master_location(master_path, PRODUCTION)
    if not is_under(derivative_path, TRANSPARENT_CANDIDATES):
        raise ValueError("derivative candidate must be under .work/transparent-candidates/")
    derivative_relative = derivative_path.relative_to(TRANSPARENT_CANDIDATES.resolve())
    expected = master_relative.with_name(f"{master_path.stem}-alpha.png")
    if derivative_relative != expected:
        raise ValueError("transparent candidate path must match its master with -alpha")
    with Image.open(master_path) as opened:
        master = opened.convert("RGB")
    with Image.open(derivative_path) as opened:
        if opened.format != "PNG" or opened.size != (1024, 1024) or opened.mode != "RGBA":
            raise ValueError(
                f"derivative must be 1024x1024 RGBA PNG; got "
                f"{opened.format} {opened.size} {opened.mode}"
            )
        derivative = opened.copy()
    alpha = derivative.getchannel("A")
    extrema = alpha.getextrema()
    if extrema == (255, 255):
        raise ValueError("derivative has no transparent pixels")
    if extrema == (0, 0):
        raise ValueError("derivative is fully transparent")
    return master, derivative


def command_transparent_check(args: argparse.Namespace) -> None:
    master_path = resolved(args.master)
    derivative_path = resolved(args.derivative)
    master, derivative = check_derivative(master_path, derivative_path)
    if args.preview:
        make_preview(master, derivative, resolved(args.preview))
        print(f"PREVIEW: {resolved(args.preview)}")
    print("MECHANICAL DERIVATIVE PASS.")
    print(
        "VISUAL CHECK REQUIRED: compare smoke, particles, glow, thin lines, "
        "translucent pieces, and detached details. Reject the derivative if lost."
    )


def command_transparent_pass(args: argparse.Namespace) -> None:
    master_path = resolved(args.master)
    derivative_path = resolved(args.derivative)
    if not args.visual_pass:
        raise ValueError("inspect the native-resolution preview, then provide --visual-pass")
    check_derivative(master_path, derivative_path)
    relative = derivative_path.relative_to(TRANSPARENT_CANDIDATES.resolve())
    target = TRANSPARENT_DERIVATIVES / relative
    move_unique(derivative_path, target)
    print(f"TRANSPARENT DERIVATIVE PASS: {target}")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    commands = root.add_subparsers(dest="command", required=True)

    check = commands.add_parser("check")
    check.add_argument("image", type=Path)
    check.set_defaults(run=command_check)

    system_pass = commands.add_parser("system-pass")
    system_pass.add_argument("image", type=Path)
    system_pass.add_argument("--visual-pass", action="store_true")
    system_pass.set_defaults(run=command_system_pass)

    approve = commands.add_parser("approve")
    approve.add_argument("image", type=Path)
    approve.add_argument("--lineage", required=True)
    approve.add_argument("--human-approved", action="store_true")
    approve.set_defaults(run=command_approve)

    family_check = commands.add_parser("family-check")
    family_check.add_argument("level4", type=Path)
    family_check.set_defaults(run=command_family_check)

    reject = commands.add_parser("reject")
    reject.add_argument("image", type=Path)
    reject.set_defaults(run=command_reject)

    transparent = commands.add_parser("transparent-check")
    transparent.add_argument("master", type=Path)
    transparent.add_argument("derivative", type=Path)
    transparent.add_argument("--preview", type=Path)
    transparent.set_defaults(run=command_transparent_check)

    transparent_pass = commands.add_parser("transparent-pass")
    transparent_pass.add_argument("master", type=Path)
    transparent_pass.add_argument("derivative", type=Path)
    transparent_pass.add_argument("--visual-pass", action="store_true")
    transparent_pass.set_defaults(run=command_transparent_pass)
    return root


def main() -> None:
    args = parser().parse_args()
    try:
        args.run(args)
    except (OSError, ValueError) as error:
        sys.exit(f"FAIL: {error}")


if __name__ == "__main__":
    main()
