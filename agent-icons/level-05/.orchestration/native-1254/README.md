# Level 05 native 1254px provisional canonical run

This directory coordinates the five-worker upgrade of the 305 existing
`*-256.png` references in `agent-icons/level-05`.

## Hard scope

- Work only on the rows in the worker's own assignment CSV.
- Preserve the reference character's design, silhouette, pose, palette, props,
  placement, and margins. This is faithful high-resolution reconstruction, not
  a redesign or a new Level 5 evolution.
- Produce native 1254×1254 RGBA PNGs with transparent backgrounds.
- Keep every 256px reference until the coordinator performs final cleanup.
- Do not edit `manifest.csv`, `manifest.json`, `summary.json`, another worker's
  assignment, Level 4, `production/`, or `derivatives/`.

## Provisional name

Choose one meaningful lowercase ASCII evolution word that describes the
reference and is unique within every group assigned to the worker:

```text
aachat-ascend-{group}-unlinked-{evolution}.png
```

Do not use a number, size, group word, uppercase letter, underscore, space, or
Japanese text. `unlinked` is fixed and must not be changed by a worker.

## One-image workflow

1. Inspect the local 256px reference with `view_image`.
2. Use one built-in imagegen call to reconstruct the exact character at high
   fidelity on a perfectly flat removable chroma-key background. Do not use a
   batch call for distinct characters.
3. Copy the generated source into ignored `tmp/imagegen/`.
4. Remove the flat background with the installed imagegen
   `remove_chroma_key.py` helper using auto-key, soft matte, and despill.
5. Run `scripts/fit_generated_subject.py` with the exact 256px reference so the
   final alpha bbox matches the reference position and margins.
6. Save the final PNG under the same category folder as the reference using the
   provisional filename.
7. Inspect the RGBA image at native resolution on light and dark backgrounds.
   Reject redesign, crop, missing or added details, shadows, floor, scenery,
   text, watermark, chroma fringe, and damaged translucent or detached details.
8. Record an accepted output:

   ```bash
   python3 scripts/record_level05_hires.py \
     --assignment <worker-assignment.csv> \
     --reference '<category/reference-256.png>' \
     --evolution <one-word-evolution> \
     --visual-pass
   ```

9. Verify the current shared contract:

   ```bash
   uv run --with pillow python scripts/verify_level05_hires.py
   ```

## Pilot gate

Each worker initially produces only the first pending row in its assignment,
commits the image and its own updated assignment CSV, pushes the worker branch,
and reports the commit, exact reference, exact output, final prompt, and QA
observations. Do not proceed to the remaining rows until the parent
coordinator sends a follow-up after central pilot review.

