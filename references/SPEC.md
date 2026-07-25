# aachat Level 4/5 production specification

This file is normative. A production master is a native **1024×1024 RGB PNG**
on an opaque, seamless white background. Never resize, upscale, interpolate,
pad, convert, or remove the background to make a candidate pass.

## Fixed identity

- Exactly one horizontal LCD, about 1.65:1 (28U×17U), physically integrated
  into the head and kept close to front-facing, visible, and unobstructed.
- Deep-black glass with restrained cobalt-blue inner glow.
- Exactly two identical, level white square eyes (5U×5U) with a 5U gap.
- One identical tall black pupil per eye (about 2.2U×3.6U). Both pupils use the
  same slight +0.6U right offset and no vertical offset; never center or mirror.
- No mouth, nose, brows, lashes, cheeks, glasses, extra eyes, symbols, letters,
  icons, or other facial features.

## Composition

- Exactly one original character; full body and every hand, finger, foot, sole,
  extension, ornament, and prop inside frame with comfortable breathing room.
- Front-facing or mild three-quarter pose; LCD remains near frontal.
- Maximum-bright, clean high-key studio lighting with generous fill.
- Request pure white. For visual QA, neutral near-white pixels and a subtle
  contact shadow are acceptable. Reject colored cast, visible gradient, floor
  line, reflection, scenery, vignette, muddy shadow, text, logo, label,
  watermark, grid, or extra character.

## Level 4 — Module Form

- Build the actual character from large, coarse square 3D modules; never apply
  a pixelation filter.
- Keep one module scale across head, LCD housing, body, clothing, limbs, shoes,
  and prop.
- Use stepped contours, broad block faces, hard facets, and crisp rendering.
- Prefer at most three material systems, one dominant motif, at most two
  supporting ideas, and low-to-medium decoration density.

## Level 5 — Ascended Form

- Use premium high-resolution stylized 3D, a strong large silhouette, precise
  sculpting, refined seams, differentiated materials, controlled reflections,
  and selective translucency or emission.
- Do not default to pixels, voxels, coarse cubes, a generic robot, superhero
  armor, repeated gold trim, steampunk gears, or dark-fantasy armor.
- When evolving Level 4, substantially transform at least three of: body
  architecture, silhouette, material system, function, motion, environmental
  effect. Preserve at least two recognizable lineage anchors.

## System visual QA

Reject if any answer is no:

1. Exactly one original character?
2. LCD count, shape, eyes, pupil size/direction, glow, integration, visibility,
   and absence of other facial features all correct?
3. Entire character and every prop safely inside frame?
4. Background visually white and neutral; lighting bright and clean?
5. No text, logo, watermark, scenery, or recognizable existing-IP/brand copy?
6. Target Level grammar clearly present?
7. Design coherent rather than a motif stuck onto a generic mascot?
8. If reference mode, source design language recognizable without copying its
   face, marks, or artifacts?
9. If Level 5 evolution, three transformed axes and two lineage anchors visible?

System QA means the file passes both this visual review and the mechanical
checker. It does not mean a human approved it.

## Prompt contract

Ask the generator for one production-ready, original, full-body aachat
character following every requirement in this file. Treat the supplied brief
as one unified design thesis controlling silhouette, body architecture,
materials, palette, clothing/construction, and any necessary prop. Give the
generator freedom in subordinate details. Ask it to self-correct LCD,
single-character count, framing, background, brightness, Level grammar, and
coherence before output.

For concept mode, state that no character-specific source image is used. For
reference mode, state that the supplied image controls design language while
the fixed aachat LCD replaces the complete original face system. The level
anchor controls rendering/construction only.

