# aachat Level 4/5 production specification

This file is normative. A production master is a native **1254×1254 RGB PNG**
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

<!-- AACHAT_LEVEL_4_START -->
## Level 4 — Module Form

- Build the actual character from large, coarse square 3D modules; never apply
  a pixelation filter.
- Keep one module scale across head, LCD housing, body, clothing, limbs, shoes,
  and prop.
- Use stepped contours, broad block faces, hard facets, and crisp rendering.
- Prefer at most three material systems, one dominant motif, at most two
  supporting ideas, and low-to-medium decoration density.
<!-- AACHAT_LEVEL_4_END -->

<!-- AACHAT_LEVEL_5_START -->
## Level 5 — Ascended Form

- Use premium high-resolution stylized 3D, a strong large silhouette, precise
  sculpting, refined seams, differentiated materials, controlled reflections,
  and selective translucency or emission.
- Do not default to pixels, voxels, coarse cubes, a generic robot, superhero
  armor, repeated gold trim, steampunk gears, or dark-fantasy armor.
- When evolving Level 4, substantially transform at least three of: body
  architecture, silhouette, material system, function, motion, environmental
  effect. Preserve at least two recognizable lineage anchors.
- Use the system-approved Level 4 image as the evolution source.
<!-- AACHAT_LEVEL_5_END -->

<!-- AACHAT_SHARED_AFTER_LEVELS -->
## Visual review

Before recording a system pass, inspect the actual image against the fixed
identity, composition, and target Level above. `REVIEW_CHECKLIST.md` is an
optional reminder. No score, schema, or written QA record is required.

System QA means the agent inspected the image against this specification and
the file passed the mechanical checker. It does not mean a human approved it.

## Prompt contract

Ask the generator for one production-ready, original, full-body aachat
character following every requirement in this file. Treat the supplied brief
as one unified design thesis controlling silhouette, body architecture,
materials, palette, clothing/construction, and any necessary prop. Give the
generator freedom in subordinate details. Ask it to self-correct LCD,
single-character count, framing, background, brightness, Level grammar, and
coherence before output.

For concept mode, state that no external character-specific source image is
used. For reference mode, state that the supplied image controls design
language while the fixed aachat LCD replaces the complete original face
system. The level anchor controls rendering/construction only.
