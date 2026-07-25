#!/usr/bin/env python3
"""Mechanical gates and simple candidate → human approval routing."""

from __future__ import annotations

import argparse
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


def resolved(path: Path) -> Path:
    return path.expanduser().resolve()


def is_under(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent.resolve())
        return True
    except ValueError:
        return False


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
    target = SYSTEM_APPROVED / source.name
    move_unique(source, target)
    print(f"SYSTEM QA PASS (NOT HUMAN APPROVAL): {target}")


def command_approve(args: argparse.Namespace) -> None:
    source = resolved(args.image)
    if not is_under(source, SYSTEM_APPROVED):
        raise ValueError("approve accepts only .work/system-approved/")
    if not args.human_approved:
        raise ValueError("explicit human approval is required")
    name = Path(args.name).name
    if name != args.name or not name.lower().endswith(".png"):
        raise ValueError("--name must be a plain .png filename")
    check_master(source)
    target = PRODUCTION / name
    move_unique(source, target)
    print(f"HUMAN-APPROVED PRODUCTION MASTER: {target}")


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
    if not is_under(master_path, PRODUCTION):
        raise ValueError("master must be under production/")
    if not is_under(derivative_path, TRANSPARENT_CANDIDATES):
        raise ValueError("derivative candidate must be under .work/transparent-candidates/")
    if master_path.name != derivative_path.name:
        raise ValueError("master and derivative candidate filenames must match")
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
    target = TRANSPARENT_DERIVATIVES / derivative_path.name
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
    approve.add_argument("--name", required=True)
    approve.add_argument("--human-approved", action="store_true")
    approve.set_defaults(run=command_approve)

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
