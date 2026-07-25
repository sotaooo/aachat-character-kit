---
name: aachat-character-kit
description: Generate, revise, QA, approve, and derive transparent copies of aachat Level 4/5 character images. Use for concept generation without a character-specific reference, reinterpretation or evolution with a supplied reference image, exact aachat LCD construction, Level 4/5 style selection, production-master validation, human approval, rejection, or transparent RGBA derivative review.
---

# aachat Character Kit

Use one short path from request to approved master. Keep generation-tool choices
outside this kit so Codex, aachat, and other agents can follow it unchanged.

## Read first

Always read `references/SPEC.md`. It is the only normative design and image
specification. Do not invent additional fixed ratios, schemas, profiles, or
calibration sets.

## Choose exactly one input mode

- **Concept mode:** no character-specific design image was supplied. Write one
  concrete visual brief from the human request.
- **Reference mode:** a source image was supplied, or an approved Level 4 is
  being evolved into Level 5. Inspect that image and write a short brief of its
  silhouette, palette, materials, construction, and prop relationship. Replace
  its face with the aachat LCD; never paste an LCD over the old face.

Do not silently switch modes. In reference mode, preserve recognizable design
language while removing logos, readable text, protected character identity,
watermarks, and source-image artifacts.

## Select references

Attach only what the image generator needs:

- Concept mode: `references/aachat-lcd-face-master.png` and the target Level
  anchor.
- Reference mode: the supplied source, `references/aachat-lcd-face-master.png`,
  and the target Level anchor.
- Add `references/aachat-master-spec.png` only when the tool accepts another
  reference or an LCD/composition failure needs correction.

The anchors control construction quality, not the new character's design.

## Build and run

Create the complete prompt from the single specification:

```bash
python3 scripts/build_prompt.py \
  --mode concept|reference \
  --level 4|5 \
  --brief "<one concrete visual direction>"
```

For Level 5 evolution, also pass:

```bash
--lineage "<two retained anchors>" \
--transformation "<at least three transformed axes>"
```

The generated prompt is a starting point, not locked wording. When a stronger
prompt or LCD correction is useful, optionally read
`references/PROMPT_GUIDE.md` and adapt its examples to the human request.

Generate one native 1024×1024 result at a time into `.work/candidates/`.
Inspect the actual image after every attempt. Revise the brief or prompt to fix
the observed failure; do not repair a wrong-sized result by resizing, padding,
format conversion, or relabeling.

## Gate and approve

1. Inspect the image against `references/SPEC.md`. Optionally use
   `references/REVIEW_CHECKLIST.md` as a reminder; it requires no score or
   written QA record.
2. If any item fails, run `python3 scripts/kit.py reject <candidate>` or revise
   with a new attempt. The reject command only deletes files under `.work/`.
3. If all visual items pass, run:

   ```bash
   python3 scripts/kit.py system-pass <candidate> --visual-pass
   ```

   This verifies the mechanical contract and moves the file to ignored
   `.work/system-approved/`. A system pass is not human approval.
4. Show that exact file to a human. Do not infer approval from silence.
5. Only after explicit approval, run:

   ```bash
   python3 scripts/kit.py approve <system-approved-file> \
     --name <production-name.png> --human-approved
   ```

   This moves the RGB master into `production/`. Never approve directly from
   `.work/candidates/`.

## Transparent derivatives

When a transparent copy is requested, read and follow
`skills/aachat-remove-background/SKILL.md`. It creates an ignored candidate,
checks it at native resolution, and moves only a visually accepted derivative
into `derivatives/transparent/`. Never replace the RGB master.
