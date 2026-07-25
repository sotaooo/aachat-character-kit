---
name: aachat-remove-background
description: Create, inspect, accept, or reject a transparent 1024×1024 RGBA derivative from a human-approved aachat RGB production master. Use only when a human requests background removal, transparency, a cutout, or a transparent PNG; do not use during master generation or before human approval.
---

# Remove an aachat background

Keep the approved RGB master unchanged. Work only from `production/`, preserve
the canvas, and never resize, crop, recenter, or delete detached details.

## Set up once

This optional derivative workflow supports Python 3.11–3.13. For a new setup,
install Python 3.13; an existing 3.11 or 3.12 also works. Python 3.14 is not
currently supported by `rembg`. RGB master generation does not require this
setup. From the repository root:

```bash
python3.13 -m venv .venv-transparency
.venv-transparency/bin/python -m pip install \
  -r skills/aachat-remove-background/requirements.txt
```

The first run downloads the background-removal model. This optional setup does
not affect RGB master generation.

## Create a candidate

```bash
.venv-transparency/bin/python \
  skills/aachat-remove-background/scripts/remove_background.py \
  production/<stage>/<group-folder>/<master.png>
```

The script preserves the master's stage/group path under ignored
`.work/transparent-candidates/` and adds `-alpha` to the filename. It does not
remove small disconnected components after segmentation.

The default is the same BiRefNet general model used by the legacy production
workflow. If another installed rembg model is more suitable, pass
`--model <name>`; this is optional.

## Inspect at native resolution

```bash
.venv-transparency/bin/python scripts/kit.py transparent-check \
  production/<stage>/<group-folder>/<master.png> \
  .work/transparent-candidates/<stage>/<group-folder>/<master-alpha.png> \
  --preview .work/transparent-preview.png
```

Inspect the 3072×1024 preview: RGB master, light checkerboard, then dark
checkerboard. Compare at 100% zoom. For Level 5, verify smoke, particles, glow,
thin lines, translucent pieces, and detached details. Also check transparent
holes and white edge fringe. Use judgment; no numeric score or report is
required.

If anything is missing, delete only the candidate:

```bash
.venv-transparency/bin/python scripts/kit.py reject \
  .work/transparent-candidates/<stage>/<group-folder>/<master-alpha.png>
```

If it passes:

```bash
.venv-transparency/bin/python scripts/kit.py transparent-pass \
  production/<stage>/<group-folder>/<master.png> \
  .work/transparent-candidates/<stage>/<group-folder>/<master-alpha.png> \
  --visual-pass
```

Only this final command moves the RGBA derivative into
`derivatives/transparent/`. Human approval of the RGB master remains valid;
the derivative requires system visual QA but does not replace the master.
