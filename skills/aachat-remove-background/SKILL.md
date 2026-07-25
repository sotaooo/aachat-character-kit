---
name: aachat-remove-background
description: Create, inspect, accept, or reject a transparent 1024×1024 RGBA derivative from a human-approved aachat RGB production master. Use only when a human requests background removal, transparency, a cutout, or a transparent PNG; do not use during master generation or before human approval.
---

# Remove an aachat background

Keep the approved RGB master unchanged. Work only from `production/`, preserve
the canvas, and never resize, crop, recenter, or delete detached details.

## Set up once

rembg currently requires Python 3.11–3.13. From the repository root:

```bash
python3 -m venv .venv-transparency
.venv-transparency/bin/python -m pip install \
  -r skills/aachat-remove-background/requirements.txt
```

The first run downloads the background-removal model. This optional setup does
not affect RGB master generation.

## Create a candidate

```bash
.venv-transparency/bin/python \
  skills/aachat-remove-background/scripts/remove_background.py \
  production/<master.png>
```

The script writes the same filename under ignored
`.work/transparent-candidates/`. It does not remove small disconnected
components after segmentation.

The default is the same BiRefNet general model used by the legacy production
workflow. If another installed rembg model is more suitable, pass
`--model <name>`; this is optional.

## Inspect at native resolution

```bash
python3 scripts/kit.py transparent-check \
  production/<master.png> .work/transparent-candidates/<master.png> \
  --preview .work/transparent-preview.png
```

Inspect the 3072×1024 preview: RGB master, light checkerboard, then dark
checkerboard. Compare at 100% zoom. For Level 5, verify smoke, particles, glow,
thin lines, translucent pieces, and detached details. Also check transparent
holes and white edge fringe. Use judgment; no numeric score or report is
required.

If anything is missing, delete only the candidate:

```bash
python3 scripts/kit.py reject .work/transparent-candidates/<master.png>
```

If it passes:

```bash
python3 scripts/kit.py transparent-pass \
  production/<master.png> .work/transparent-candidates/<master.png> \
  --visual-pass
```

Only this final command moves the RGBA derivative into
`derivatives/transparent/`. Human approval of the RGB master remains valid;
the derivative requires system visual QA but does not replace the master.
